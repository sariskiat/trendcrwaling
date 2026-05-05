"""TikTok scraper using TikTokPy (tiktokapipy). No API key required."""
from __future__ import annotations

from tiktokapipy.api import TikTokAPI


async def scrape_user(username: str, limit: int = 20) -> list[dict[str, object]]:
    """Return recent posts for a TikTok username.

    Args:
        username: TikTok handle without @.
        limit: Max number of posts to return.

    Returns:
        List of dicts with keys: url, desc, likes.
    """
    results: list[dict[str, object]] = []
    async with TikTokAPI() as api:
        user = await api.user(username)
        async for video in user.videos:
            results.append({
                "url": video.url,
                "desc": video.desc,
                "likes": video.stats.digg_count,
            })
            if len(results) >= limit:
                break
    return results
