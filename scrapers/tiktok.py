"""TikTok scraper using Playwright headless browser. No API key required."""

from __future__ import annotations

import os
from http.cookiejar import MozillaCookieJar
from typing import TypedDict

from playwright._impl._api_structures import (
    SetCookieParam,  # not re-exported from playwright.async_api
)
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

__all__ = [
    "TikTokPost",
    "TikTokScraperError",
    "scrape_user",
    "scrape_trending",
    "scrape_hashtag",
]

_COOKIE_ENV: str = "TT_COOKIES_FILE"
_HEADLESS_ENV: str = "TT_HEADLESS"  # Set to "false" to run with visible browser
_POST_SELECTOR: str = '[data-e2e="user-post-item"]'
_USER_AGENT: str = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class TikTokPost(TypedDict):
    """A single TikTok post returned by the scraper."""

    url: str
    desc: str
    likes: int
    views: int
    thumbnail_url: str
    author: str


class TikTokScraperError(Exception):
    """Raised when TikTok scraping fails due to network or access errors."""


def _cookie_file() -> str | None:
    """Return path to cookies.txt from TT_COOKIES_FILE env var, or None."""
    path: str = os.getenv(_COOKIE_ENV, "")
    return path if path else None


def _is_headless() -> bool:
    """Return True if headless mode is enabled (default), False for visible browser."""
    val: str = os.getenv(_HEADLESS_ENV, "true").lower()
    return val not in ("false", "0", "no")


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
    url: str,
) -> tuple[Browser, Page]:
    """Launch browser, navigate to the given URL, and return (browser, page).

    Args:
        pw: Active Playwright instance.
        cookie_path: Path to cookies.txt, or None to browse without cookies.
        url: Full TikTok URL to navigate to.

    Returns:
        Tuple of (browser, page) ready for content extraction.
    """
    browser: Browser = await pw.chromium.launch(headless=_is_headless())
    ctx: BrowserContext = await browser.new_context(
        user_agent=_USER_AGENT,
        viewport={"width": 1280, "height": 900},
    )
    if cookie_path is not None:
        await ctx.add_cookies(_load_cookies(cookie_path))
    pg: Page = await ctx.new_page()
    await pg.goto(
        url,
        wait_until="networkidle",
        timeout=30000,
    )
    await pg.wait_for_selector(_POST_SELECTOR, timeout=15000)
    return browser, pg


async def _extract_posts(pg: Page, author: str = "") -> list[dict[str, str]]:
    """Extract raw post data via DOM evaluation.

    Args:
        pg: Playwright page already loaded with content.
        author: Author name to embed in each post entry.

    Returns:
        List of raw post dicts with url, desc, thumbnail_url, views, author keys.
    """
    extract_js: str = f"""() => {{
    const results = [];
    const items = document.querySelectorAll("{_POST_SELECTOR}");
    items.forEach(item => {{
        const link = item.querySelector('a');
        const img = item.querySelector('img');
        const viewsElem = item.querySelector('[data-e2e="video-views"]');
        const url = link ? (link.href || "") : "";
        const desc = img ? (img.alt || "") : "";
        const thumbnail_url = img ? (img.src || "") : "";
        const views_text = viewsElem ? (viewsElem.textContent || "0") : "0";
        const views = parseInt(views_text.replace(/[^0-9]/g, ""), 10) || 0;
        results.push({{ url, desc, thumbnail_url, views: views.toString() }});
    }});
    return results;
}}"""
    raw: list[dict[str, str]] = await pg.evaluate(extract_js)
    for entry in raw:
        entry["author"] = author
    return raw


async def scrape_user(username: str, limit: int = 20) -> list[TikTokPost]:
    """Return recent posts from a public TikTok profile.

    Args:
        username: TikTok handle without @.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikTokPost dicts with keys: url, desc, likes, views, thumbnail_url, author.

    Raises:
        ValueError: If limit is not positive.
        TikTokScraperError: If Playwright fails or the profile cannot be scraped.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    cookie_path: str | None = _cookie_file()
    try:
        async with async_playwright() as pw:
            browser, pg = await _setup_browser(
                pw, cookie_path, f"https://www.tiktok.com/@{username}"
            )
            try:
                raw: list[dict[str, str]] = await _extract_posts(pg, author=username)
                posts: list[TikTokPost] = _raw_to_posts(raw, limit)
            finally:
                await browser.close()
            return posts
    except TikTokScraperError:
        raise
    except Exception as exc:
        raise TikTokScraperError(
            f"Failed to scrape TikTok user '{username}': {exc}"
        ) from exc


def _raw_to_posts(raw: list[dict[str, str]], limit: int) -> list[TikTokPost]:
    """Convert raw DOM dicts to typed TikTokPost list, capped at limit."""
    return [
        TikTokPost(
            url=entry.get("url", ""),
            desc=entry.get("desc", ""),
            likes=0,
            views=int(entry.get("views", "0")) or 0,
            thumbnail_url=entry.get("thumbnail_url", ""),
            author=entry.get("author", ""),
        )
        for entry in raw[:limit]
    ]


async def scrape_trending(limit: int = 20) -> list[TikTokPost]:
    """Return trending TikTok posts.

    Args:
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikTokPost dicts.

    Raises:
        ValueError: If limit is not positive.
        TikTokScraperError: If Playwright fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    cookie_path: str | None = _cookie_file()
    try:
        async with async_playwright() as pw:
            browser, pg = await _setup_browser(
                pw, cookie_path, "https://www.tiktok.com/explore"
            )
            try:
                raw: list[dict[str, str]] = await _extract_posts(pg)
                posts: list[TikTokPost] = _raw_to_posts(raw, limit)
            finally:
                await browser.close()
            return posts
    except TikTokScraperError:
        raise
    except Exception as exc:
        raise TikTokScraperError(f"Failed to scrape TikTok trending: {exc}") from exc


async def scrape_hashtag(tag: str, limit: int = 20) -> list[TikTokPost]:
    """Return TikTok posts for a given hashtag.

    Args:
        tag: Hashtag without #.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikTokPost dicts.

    Raises:
        ValueError: If limit is not positive or tag is empty.
        TikTokScraperError: If Playwright fails.
    """
    if not tag or not tag.strip():
        raise ValueError("tag must not be empty")
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    cookie_path: str | None = _cookie_file()
    try:
        async with async_playwright() as pw:
            browser, pg = await _setup_browser(
                pw, cookie_path, f"https://www.tiktok.com/tag/{tag}"
            )
            try:
                raw: list[dict[str, str]] = await _extract_posts(pg)
                posts: list[TikTokPost] = _raw_to_posts(raw, limit)
            finally:
                await browser.close()
            return posts
    except TikTokScraperError:
        raise
    except Exception as exc:
        raise TikTokScraperError(
            f"Failed to scrape TikTok hashtag '{tag}': {exc}"
        ) from exc
