"""Facebook scraper using Playwright headless browser. No API key required."""

from __future__ import annotations

import os
import time as _time
from datetime import datetime
from http.cookiejar import MozillaCookieJar
from typing import TypedDict

from playwright._impl._api_structures import (
    SetCookieParam,  # not re-exported from playwright.async_api
)
from playwright.async_api import (
    Browser,
    Page,
    Playwright,
    async_playwright,
)

from scrapers.hashtag_generator import generate_hashtags

__all__ = [
    "FacebookPost",
    "FacebookScraperError",
    "_parse_facebook_time",
    "scrape_hashtag",
    "scrape_page",
    "scrape_trending",
]

_POST_SELECTOR = "[data-ad-comet-preview='message']"
_REAL_IMAGE_PATTERN = "scontent"
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_EXTRACT_JS: str = f"""() => {{
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


class FacebookPost(TypedDict):
    """A single Facebook post returned by the scraper."""

    text: str
    likes: int
    time: str
    post_url: str
    image_url: str
    created_at: int  # Unix timestamp; 0 if unparseable


class FacebookScraperError(Exception):
    """Raised when Facebook scraping fails due to network or access errors."""


_FB_TIME_FORMATS = [
    "%B %-d, %Y at %I:%M %p",  # "May 7, 2026 at 3:00 PM"
    "%B %d, %Y at %I:%M %p",  # "May 07, 2026 at 3:00 PM"
    "%B %-d, %Y",  # "May 7, 2026"
    "%B %d, %Y",  # "May 07, 2026"
]


def _parse_facebook_time(time_str: str) -> int:
    """Parse a Facebook-style time string to a Unix timestamp.

    Args:
        time_str: String like "May 7, 2026 at 3:00 PM" from <abbr title="...">.

    Returns:
        Unix timestamp as int, or 0 if parsing fails.
    """
    if not time_str or not time_str.strip():
        return 0
    for fmt in _FB_TIME_FORMATS:
        try:
            dt = datetime.strptime(time_str.strip(), fmt)
            return int(dt.timestamp())
        except ValueError:
            continue
    return 0


def _cookie_file() -> str | None:
    """Return path to cookies.txt from FB_COOKIES_FILE env var, or None."""
    path: str = os.getenv("FB_COOKIES_FILE", "")
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
    page_slug: str,
) -> tuple[Browser, Page]:
    """Launch browser, navigate to the page, and return (browser, page).

    Args:
        pw: Active Playwright instance.
        cookie_path: Path to cookies.txt, or None to browse without cookies.
        page_slug: Facebook page name as it appears in the URL.

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
        f"https://www.facebook.com/{page_slug}",
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
        List of raw post dicts with text, post_url, image_url, time keys.
    """
    for scroll_y in [800, 1600, 2400]:
        await pg.evaluate(f"window.scrollTo(0, {scroll_y})")
        await pg.wait_for_timeout(1500)
    raw: list[dict[str, str]] = await pg.evaluate(_EXTRACT_JS)
    return raw


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
            browser, pg = await _setup_browser(pw, cookie_path, page)
            try:
                raw: list[dict[str, str]] = await _extract_posts(pg)
                posts: list[FacebookPost] = [
                    FacebookPost(
                        text=entry.get("text", ""),
                        likes=0,
                        time=entry.get("time", ""),
                        post_url=entry.get("post_url", ""),
                        image_url=entry.get("image_url", ""),
                        created_at=_parse_facebook_time(entry.get("time", "")),
                    )
                    for entry in raw[:limit]
                ]
            finally:
                await browser.close()
            return posts
    except FacebookScraperError:
        raise
    except Exception as exc:
        raise FacebookScraperError(
            f"Failed to scrape Facebook page '{page}': {exc}"
        ) from exc


_TRENDING_SEEDS = ["trending", "viral"]
_HASHTAG_POSTS_PER_TAG = 10


async def scrape_hashtag(
    query: str,
    limit: int = 10,
    max_age_days: int = 10,
) -> list[FacebookPost]:
    """Scrape trending posts for a topic across generated hashtags.

    Generates 10 hashtags from query, scrapes each hashtag page, filters
    by age, ranks by likes (or recency if likes unavailable), returns top limit.

    Args:
        query: Freeform user query to generate hashtags from.
        limit: Maximum number of posts to return.
        max_age_days: Exclude posts older than this many days.

    Returns:
        List of FacebookPost dicts, sorted by likes descending.
    """
    hashtags = await generate_hashtags(query, platform="facebook")
    cutoff = _time.time() - max_age_days * 86400
    seen: set[str] = set()
    posts: list[FacebookPost] = []
    for tag in hashtags:
        try:
            slug = f"hashtag/{tag}/"
            batch = await scrape_page(slug, limit=_HASHTAG_POSTS_PER_TAG)
            for p in batch:
                url = p["post_url"]
                if url in seen:
                    continue
                seen.add(url)
                if p["created_at"] > 0 and p["created_at"] < cutoff:
                    continue
                posts.append(p)
        except Exception:
            continue
    posts.sort(key=lambda p: (p["likes"], p["created_at"]), reverse=True)
    return posts[:limit]


async def scrape_trending(
    limit: int = 10,
    max_age_days: int = 10,
) -> list[FacebookPost]:
    """Scrape globally trending Facebook posts from #trending and #viral.

    Deduplicates by post_url, filters by age, ranks by likes/recency.

    Args:
        limit: Maximum number of posts to return.
        max_age_days: Exclude posts older than this many days.

    Returns:
        List of FacebookPost dicts, sorted by likes descending.
    """
    cutoff = _time.time() - max_age_days * 86400
    seen: set[str] = set()
    posts: list[FacebookPost] = []
    for seed in _TRENDING_SEEDS:
        try:
            slug = f"hashtag/{seed}/"
            batch = await scrape_page(slug, limit=_HASHTAG_POSTS_PER_TAG)
            for p in batch:
                url = p["post_url"]
                if url in seen:
                    continue
                seen.add(url)
                if p["created_at"] > 0 and p["created_at"] < cutoff:
                    continue
                posts.append(p)
        except Exception:
            continue
    posts.sort(key=lambda p: (p["likes"], p["created_at"]), reverse=True)
    return posts[:limit]
