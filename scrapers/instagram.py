"""Instagram scraper using Playwright headless browser. No API key required."""

from __future__ import annotations

import os
from http.cookiejar import MozillaCookieJar
from typing import TypedDict

from playwright._impl._api_structures import (
    SetCookieParam,  # not re-exported from playwright.async_api
)
from playwright.async_api import Browser, Page, Playwright, async_playwright

__all__ = ["InstagramPost", "InstagramScraperError", "scrape_user"]

_COOKIE_ENV = "IG_COOKIES_FILE"
_POST_LINK_SELECTOR = "a[href*='/p/']"
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_EXTRACT_JS: str = f"""() => {{
    const results = [];
    const links = document.querySelectorAll("{_POST_LINK_SELECTOR}");
    links.forEach(link => {{
        const post_url = link.href || "";
        const img = link.querySelector("img");
        const url = img ? (img.src || "") : "";
        const caption = img ? (img.alt || "") : "";
        results.push({{ post_url, url, caption }});
    }});
    return results;
}}"""


class InstagramPost(TypedDict):
    """A single Instagram post returned by the scraper."""

    url: str
    caption: str
    likes: int
    post_url: str


class InstagramScraperError(Exception):
    """Raised when Instagram scraping fails due to network or access errors."""


def _cookie_file() -> str | None:
    """Return path to cookies.txt from IG_COOKIES_FILE env var, or None."""
    path: str = os.getenv(_COOKIE_ENV, "")
    return path if path else None


def _load_cookies(path: str) -> list[SetCookieParam]:
    """Load a Netscape cookies.txt and convert to Playwright cookie dicts.

    Args:
        path: Path to a Netscape-format cookies.txt file.

    Returns:
        List of SetCookieParam with name, value, domain, path keys.
    """
    jar: MozillaCookieJar = MozillaCookieJar(path)
    jar.load(ignore_discard=True, ignore_expires=True)
    return [
        SetCookieParam(
            name=cookie.name,
            value=cookie.value or "",
            domain=cookie.domain,
            path=cookie.path,
        )
        for cookie in jar
    ]


async def _setup_browser(
    pw: Playwright,
    cookie_path: str | None,
    username: str,
) -> tuple[Browser, Page]:
    """Launch browser, navigate to the profile page, and return (browser, page).

    Args:
        pw: Active Playwright instance.
        cookie_path: Path to cookies.txt, or None to browse without cookies.
        username: Instagram username as it appears in the URL.

    Returns:
        Tuple of (browser, page) ready for content extraction.
    """
    browser: Browser = await pw.chromium.launch(headless=True)
    ctx = await browser.new_context(
        user_agent=_USER_AGENT,
        viewport={"width": 1280, "height": 900},
    )
    if cookie_path is not None:
        await ctx.add_cookies(_load_cookies(cookie_path))
    pg: Page = await ctx.new_page()
    await pg.goto(
        f"https://www.instagram.com/{username}/",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    await pg.wait_for_timeout(5000)
    return browser, pg


async def _extract_posts(pg: Page) -> list[dict[str, str]]:
    """Scroll the page and extract raw post data via DOM evaluation.

    Args:
        pg: Playwright page already loaded with content.

    Returns:
        List of raw post dicts with post_url, url, caption keys.
    """
    for scroll_y in [800, 1600, 2400]:
        await pg.evaluate(f"window.scrollTo(0, {scroll_y})")
        await pg.wait_for_timeout(1500)
    raw: list[dict[str, str]] = await pg.evaluate(_EXTRACT_JS)
    return raw


async def scrape_user(username: str, limit: int = 20) -> list[InstagramPost]:
    """Return recent posts from a public Instagram profile.

    Args:
        username: Instagram handle without @.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of InstagramPost dicts with keys: url, caption, likes, post_url.

    Raises:
        ValueError: If limit is not positive.
        InstagramScraperError: If Playwright fails or the profile cannot be scraped.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    cookie_path: str | None = _cookie_file()
    try:
        async with async_playwright() as pw:
            browser, pg = await _setup_browser(pw, cookie_path, username)
            raw: list[dict[str, str]] = await _extract_posts(pg)
            await browser.close()
            return [
                InstagramPost(
                    url=entry.get("url", ""),
                    caption=entry.get("caption", ""),
                    likes=0,
                    post_url=entry.get("post_url", ""),
                )
                for entry in raw[:limit]
            ]
    except InstagramScraperError:
        raise
    except Exception as exc:
        raise InstagramScraperError(
            f"Failed to scrape Instagram user '{username}': {exc}"
        ) from exc
