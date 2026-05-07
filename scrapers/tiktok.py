"""TikTok scraper using TikTokPy (tiktokapipy). No API key required."""

from __future__ import annotations

from typing import TypedDict

from tiktokapipy.api import TikTokAPI

__all__ = ["TikTokPost", "scrape_user"]


class TikTokPost(TypedDict):
    """A single TikTok post returned by the scraper."""

    url: str
    desc: str
    likes: int


class TikTokScraperError(Exception):
    """Raised when TikTok scraping fails due to network or library errors."""


async def scrape_user(username: str, limit: int = 20) -> list[TikTokPost]:
    """Return recent posts for a TikTok username.

    Args:
        username: TikTok handle without @.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikTokPost dicts with keys: url, desc, likes.

    Raises:
        ValueError: If limit is not positive.
        TikTokScraperError: If the TikTok API call fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    results: list[TikTokPost] = []
    try:
        async with TikTokAPI() as api:
            user = await api.user(username)
            async for video in user.videos:
                results.append(
                    TikTokPost(
                        url=video.url,
                        desc=video.desc,
                        likes=video.stats.digg_count,
                    )
                )
                if len(results) >= limit:
                    break
    except Exception as exc:
        raise TikTokScraperError(
            f"Failed to scrape TikTok user '{username}': {exc}"
        ) from exc
    return results
