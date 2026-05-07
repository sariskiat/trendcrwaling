"""Facebook scraper using Playwright headless browser. No API key required."""
from __future__ import annotations

import os
from http.cookiejar import MozillaCookieJar
from typing import TypedDict

from playwright.async_api import async_playwright

__all__ = ["FacebookPost", "FacebookScraperError", "scrape_page"]


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
        page: Facebook page name as it appears in the URL.
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
            context = await browser.new_context()
            if cookie_path is not None:
                await context.add_cookies(_load_cookies(cookie_path))  # type: ignore[arg-type]
            pg = await context.new_page()
            await pg.goto(f"https://www.facebook.com/{page}")
            await pg.wait_for_selector("article", timeout=15000)
            articles = await pg.query_selector_all("article")
            results: list[FacebookPost] = []
            for article in articles[:limit]:
                text: str = (await article.inner_text()) or ""
                link_el = await article.query_selector("a[href*='/posts/']")
                post_url: str = (
                    (await link_el.get_attribute("href")) if link_el is not None else ""
                ) or ""
                img_el = await article.query_selector("img")
                image_url: str = (
                    (await img_el.get_attribute("src")) if img_el is not None else ""
                ) or ""
                results.append(
                    FacebookPost(
                        text=text,
                        likes=0,
                        time="",
                        post_url=post_url,
                        image_url=image_url,
                    )
                )
            await browser.close()
            return results
    except FacebookScraperError:
        raise
    except Exception as exc:
        raise FacebookScraperError(
            f"Failed to scrape Facebook page '{page}': {exc}"
        ) from exc
