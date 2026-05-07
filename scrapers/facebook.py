"""Facebook scraper using Playwright headless browser. No API key required."""
from __future__ import annotations

import os
from http.cookiejar import MozillaCookieJar
from typing import TypedDict

from playwright.async_api import async_playwright

__all__ = ["FacebookPost", "FacebookScraperError", "scrape_page"]

_POST_SELECTOR = "[data-ad-comet-preview='message']"
_REAL_IMAGE_PATTERN = "scontent"


class FacebookPost(TypedDict):
    """A single Facebook post returned by the scraper."""

    text: str
    likes: int
    time: str
    post_url: str
    image_url: str


class FacebookScraperError(Exception):
    """Raised when Facebook scraping fails due to network or access errors."""


def _cookie_file() -> str | None:
    """Return path to cookies.txt from FB_COOKIES_FILE env var, or None."""
    path: str = os.getenv("FB_COOKIES_FILE", "")
    return path if path else None


def _load_cookies(path: str) -> list[dict[str, str]]:
    """Load a Netscape cookies.txt and convert to Playwright cookie dicts.

    Args:
        path: Path to a Netscape-format cookies.txt file.

    Returns:
        List of dicts with name, value, domain, path keys.
    """
    jar: MozillaCookieJar = MozillaCookieJar(path)
    jar.load(ignore_discard=True, ignore_expires=True)
    return [
        {
            "name": cookie.name,
            "value": cookie.value or "",
            "domain": cookie.domain,
            "path": cookie.path,
        }
        for cookie in jar
    ]


async def scrape_page(page: str, limit: int = 20) -> list[FacebookPost]:
    """Return recent posts from a public Facebook page.

    Args:
        page: Facebook page slug as it appears in the URL (e.g. 'mkrestaurants').
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of FacebookPost dicts with keys: text, likes, time, post_url, image_url.

    Raises:
        ValueError: If limit is not positive.
        FacebookScraperError: If Playwright fails or the page cannot be scraped.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")

    cookie_path: str | None = _cookie_file()

    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 900},
            )
            if cookie_path is not None:
                await ctx.add_cookies(_load_cookies(cookie_path))  # type: ignore[arg-type]
            pg = await ctx.new_page()
            await pg.goto(
                f"https://www.facebook.com/{page}",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            await pg.wait_for_timeout(5000)
            for scroll_y in [800, 1600, 2400]:
                await pg.evaluate(f"window.scrollTo(0, {scroll_y})")
                await pg.wait_for_timeout(1500)

            raw: list[dict[str, str]] = await pg.evaluate(
                f"""() => {{
                    const results = [];
                    const msgs = document.querySelectorAll("{_POST_SELECTOR}");
                    msgs.forEach(msg => {{
                        let container = msg;
                        for (let i = 0; i < 8; i++) container = container.parentElement;

                        const text = msg.innerText || "";

                        const linkEl = container.querySelector("a[href*='/posts/']")
                            || container.querySelector("a[href*='/videos/']")
                            || container.querySelector("a[href*='story_fbid']");
                        const post_url = linkEl ? linkEl.href : "";

                        const imgs = Array.from(container.querySelectorAll("img[src]"));
                        const realImg = imgs.find(i => i.src.includes("{_REAL_IMAGE_PATTERN}"));
                        const image_url = realImg ? realImg.src : "";

                        const abbrEl = container.querySelector("abbr");
                        const time = abbrEl ? (abbrEl.title || abbrEl.innerText || "") : "";

                        results.push({{ text, post_url, image_url, time }});
                    }});
                    return results;
                }}"""
            )

            await browser.close()

            return [
                FacebookPost(
                    text=entry.get("text", ""),
                    likes=0,
                    time=entry.get("time", ""),
                    post_url=entry.get("post_url", ""),
                    image_url=entry.get("image_url", ""),
                )
                for entry in raw[:limit]
            ]

    except FacebookScraperError:
        raise
    except Exception as exc:
        raise FacebookScraperError(
            f"Failed to scrape Facebook page '{page}': {exc}"
        ) from exc
