"""Instagram scraper using Playwright headless browser. No API key required."""

from __future__ import annotations

import asyncio
import os
import re
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
    "InstagramPost",
    "InstagramScraperError",
    "_enrich_posts_with_likes",
    "_scrape_post_likes",
    "_shortcode_to_timestamp",
    "scrape_user",
]

_COOKIE_ENV: str = "IG_COOKIES_FILE"
_POST_LINK_SELECTOR: str = "a[href*='/p/'], a[href*='/reel/']"
_USER_AGENT: str = (
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
    created_at: int  # Unix timestamp; 0 if not decodable


class InstagramScraperError(Exception):
    """Raised when Instagram scraping fails due to network or access errors."""


_BASE64URL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
_INSTAGRAM_EPOCH = 1314220021


def _shortcode_to_timestamp(shortcode: str) -> int:
    """Decode an Instagram shortcode to a Unix timestamp.

    Uses base62 decode → right-shift 23 bits → add Instagram epoch.

    Args:
        shortcode: The shortcode portion of an Instagram post URL
            (e.g. "CnvGmGiLTcD" from /p/CnvGmGiLTcD/).

    Returns:
        Unix timestamp (int), or 0 if decode fails.
    """
    if not shortcode:
        return 0
    try:
        num = 0
        for char in shortcode:
            idx = _BASE64URL_CHARS.index(char)
            num = num * 64 + idx
        # Instagram IDs store timestamp in ms: (id >> 23) gives ms since epoch
        return int((num >> 23) / 1000 + _INSTAGRAM_EPOCH)
    except (ValueError, OverflowError):
        return 0


def _extract_shortcode(post_url: str) -> str:
    """Extract shortcode from an Instagram post or reel URL.

    Args:
        post_url: Full post URL like https://www.instagram.com/p/ABC123/ or /reel/...

    Returns:
        Shortcode string, or empty string if not found.
    """
    for prefix in ("/p/", "/reel/"):
        if prefix in post_url:
            after = post_url.split(prefix, 1)[1]
            return after.split("/")[0]
    return ""


_LIKES_SELECTOR = "section span"
_LIKES_SEMAPHORE_LIMIT = 5


async def _scrape_post_likes(ctx: BrowserContext, post_url: str) -> int:
    """Navigate to a post detail page and extract the like count.

    Args:
        ctx: An active Playwright BrowserContext.
        post_url: Full URL to the Instagram post.

    Returns:
        Like count as integer, or 0 if not found or parse fails.
    """
    pg: Page = await ctx.new_page()
    try:
        await pg.goto(post_url, wait_until="domcontentloaded", timeout=30000)
        await pg.wait_for_selector(_LIKES_SELECTOR, timeout=10000)
        text: str = await pg.inner_text(_LIKES_SELECTOR)
        digits = re.sub(r"[^\d]", "", text.split(" ")[0])
        return int(digits) if digits else 0
    except Exception:
        return 0
    finally:
        await pg.close()


async def _enrich_posts_with_likes(
    ctx: BrowserContext,
    posts: list[dict],  # type: ignore[type-arg]
) -> list[dict]:  # type: ignore[type-arg]
    """Fetch like counts for each post concurrently (up to 5 at a time).

    Args:
        ctx: An active Playwright BrowserContext.
        posts: List of post dicts with at least a 'post_url' key.

    Returns:
        Same list with 'likes' field updated.
    """
    sem = asyncio.Semaphore(_LIKES_SEMAPHORE_LIMIT)

    async def _fetch(post: dict) -> dict:  # type: ignore[type-arg]
        async with sem:
            post["likes"] = await _scrape_post_likes(ctx, post.get("post_url", ""))
            return post

    return list(await asyncio.gather(*(_fetch(p) for p in posts)))


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
    ctx: BrowserContext = await browser.new_context(
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
            try:
                raw: list[dict[str, str]] = await _extract_posts(pg)
                posts: list[InstagramPost] = [
                    InstagramPost(
                        url=entry.get("url", ""),
                        caption=entry.get("caption", ""),
                        likes=0,
                        post_url=entry.get("post_url", ""),
                        created_at=_shortcode_to_timestamp(
                            _extract_shortcode(entry.get("post_url", ""))
                        ),
                    )
                    for entry in raw[:limit]
                ]
            finally:
                await browser.close()
            return posts
    except InstagramScraperError:
        raise
    except Exception as exc:
        raise InstagramScraperError(
            f"Failed to scrape Instagram user '{username}': {exc}"
        ) from exc
