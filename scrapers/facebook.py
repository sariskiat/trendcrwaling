"""Facebook scraper using facebook-scraper. No API key required."""
from __future__ import annotations

from typing import TypedDict

from facebook_scraper import get_posts

__all__ = ["FacebookPost", "FacebookScraperError", "scrape_page"]


class FacebookPost(TypedDict):
    """A single Facebook post returned by the scraper."""

    text: str
    likes: int
    time: str


class FacebookScraperError(Exception):
    """Raised when Facebook scraping fails due to network or access errors."""


def scrape_page(page: str, limit: int = 20) -> list[FacebookPost]:
    """Return recent posts from a public Facebook page.

    Args:
        page: Facebook page name as it appears in the URL.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of FacebookPost dicts with keys: text, likes, time.

    Raises:
        ValueError: If limit is not positive.
        FacebookScraperError: If the Facebook scraper fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    results: list[FacebookPost] = []
    try:
        for post in get_posts(page, pages=3):
            results.append(FacebookPost(
                text=post.get("text") or "",
                likes=post.get("likes") or 0,
                time=str(post.get("time") or ""),
            ))
            if len(results) >= limit:
                break
    except Exception as exc:
        raise FacebookScraperError(f"Failed to scrape Facebook page '{page}': {exc}") from exc
    return results
