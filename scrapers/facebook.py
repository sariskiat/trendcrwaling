"""Facebook scraper using facebook-scraper. No API key required."""
from __future__ import annotations

import os
from typing import TypedDict

from facebook_scraper import get_posts

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


def _credentials() -> tuple[str, str] | None:
    """Return (email, password) from env vars FB_EMAIL/FB_PASSWORD, or None."""
    email: str = os.getenv("FB_EMAIL", "")
    password: str = os.getenv("FB_PASSWORD", "")
    if email and password:
        return (email, password)
    return None


def scrape_page(page: str, limit: int = 20) -> list[FacebookPost]:
    """Return recent posts from a public Facebook page.

    Args:
        page: Facebook page name as it appears in the URL.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of FacebookPost dicts with keys: text, likes, time, post_url, image_url.

    Raises:
        ValueError: If limit is not positive.
        FacebookScraperError: If the Facebook scraper fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    creds: tuple[str, str] | None = _credentials()
    results: list[FacebookPost] = []
    try:
        for post in get_posts(page, pages=3, credentials=creds):
            results.append(FacebookPost(
                text=post.get("text") or "",
                likes=post.get("likes") or 0,
                time=str(post.get("time") or ""),
                post_url=post.get("post_url") or "",
                image_url=post.get("image") or "",
            ))
            if len(results) >= limit:
                break
    except Exception as exc:
        raise FacebookScraperError(f"Failed to scrape Facebook page '{page}': {exc}") from exc
    return results
