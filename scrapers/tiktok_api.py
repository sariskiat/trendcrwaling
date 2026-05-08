"""TikTok scraper using TikTok-Api library (davidteather)."""

from __future__ import annotations

import os
from typing import TypedDict

from TikTokApi import TikTokApi

from mcp_server.exceptions import ConfigurationError

__all__ = [
    "TikTokApiPost",
    "TikTokApiScraperError",
    "scrape_user",
    "scrape_trending",
    "scrape_hashtag",
]

_MS_TOKEN_ENV: str = "TT_MS_TOKEN"


class TikTokApiPost(TypedDict):
    """A single TikTok post returned by the TikTok-Api scraper."""

    url: str
    desc: str
    likes: int
    views: int
    thumbnail_url: str
    author: str
    source: str


class TikTokApiScraperError(Exception):
    """Raised when TikTok-Api scraping fails."""


def _get_ms_token() -> str:
    """Return the ms_token from TT_MS_TOKEN env var.

    Raises:
        ConfigurationError: If TT_MS_TOKEN is not set.
    """
    token: str = os.getenv(_MS_TOKEN_ENV, "")
    if not token:
        raise ConfigurationError(
            f"{_MS_TOKEN_ENV} environment variable is not set. "
            "Export it to provide your TikTok ms_token for API access."
        )
    return token


async def scrape_user(username: str, limit: int = 20) -> list[TikTokApiPost]:
    """Return recent posts from a public TikTok profile using TikTok-Api.

    Args:
        username: TikTok handle without @.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikTokApiPost dicts with keys: url, desc, likes, views,
        thumbnail_url, author, source.

    Raises:
        ValueError: If limit is not positive.
        ConfigurationError: If TT_MS_TOKEN env var is not set.
        TikTokApiScraperError: If TikTok-Api fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")

    ms_token: str = _get_ms_token()

    posts: list[TikTokApiPost] = []
    try:
        async with TikTokApi() as api:
            await api.create_sessions(
                num_sessions=1, sleep_after=3, ms_tokens=[ms_token]
            )
            user = api.user(username=username)
            count = 0
            async for video in user.videos(count=limit):
                if count >= limit:
                    break

                video_id: str = getattr(video, "id", "")
                desc: str = getattr(video, "desc", "")
                as_dict: dict[str, object] = getattr(video, "as_dict", {})

                # Extract stats from as_dict
                stats: dict[str, int] = as_dict.get("stats", {})  # type: ignore[assignment]
                views: int = stats.get("playCount", 0)
                likes: int = stats.get("diggCount", 0)

                # Extract author from as_dict
                author_info: dict[str, str] = as_dict.get("author", {})  # type: ignore[assignment]
                author: str = author_info.get("uniqueId", username)

                # Extract thumbnail from video.playAddr
                video_info: dict[str, str] = as_dict.get("video", {})  # type: ignore[assignment]
                thumbnail_url: str = video_info.get("playAddr", "")

                # Build URL
                url: str = f"https://www.tiktok.com/@{author}/video/{video_id}"

                posts.append(
                    TikTokApiPost(
                        url=url,
                        desc=desc,
                        likes=likes,
                        views=views,
                        thumbnail_url=thumbnail_url,
                        author=author,
                        source="tiktok-api",
                    )
                )
                count += 1
    except TikTokApiScraperError:
        raise
    except Exception as exc:
        raise TikTokApiScraperError(
            f"Failed to scrape TikTok user '{username}': {exc}"
        ) from exc

    return posts


async def scrape_trending(limit: int = 20) -> list[TikTokApiPost]:
    """Return trending TikTok posts using TikTok-Api.

    Args:
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikTokApiPost dicts with keys: url, desc, likes, views,
        thumbnail_url, author, source.

    Raises:
        ValueError: If limit is not positive.
        ConfigurationError: If TT_MS_TOKEN env var is not set.
        TikTokApiScraperError: If TikTok-Api fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")

    ms_token: str = _get_ms_token()

    posts: list[TikTokApiPost] = []
    try:
        async with TikTokApi() as api:
            await api.create_sessions(
                num_sessions=1, sleep_after=3, ms_tokens=[ms_token]
            )
            count = 0
            async for video in api.trending.videos(count=limit):
                if count >= limit:
                    break

                video_id: str = getattr(video, "id", "")
                desc: str = getattr(video, "desc", "")
                as_dict: dict[str, object] = getattr(video, "as_dict", {})

                # Extract stats from as_dict
                stats: dict[str, int] = as_dict.get("stats", {})  # type: ignore[assignment]
                views: int = stats.get("playCount", 0)
                likes: int = stats.get("diggCount", 0)

                # Extract author from as_dict
                author_info: dict[str, str] = as_dict.get("author", {})  # type: ignore[assignment]
                author: str = author_info.get("uniqueId", "")

                # Extract thumbnail from video.playAddr
                video_info: dict[str, str] = as_dict.get("video", {})  # type: ignore[assignment]
                thumbnail_url: str = video_info.get("playAddr", "")

                # Build URL
                url: str = f"https://www.tiktok.com/@{author}/video/{video_id}"

                posts.append(
                    TikTokApiPost(
                        url=url,
                        desc=desc,
                        likes=likes,
                        views=views,
                        thumbnail_url=thumbnail_url,
                        author=author,
                        source="tiktok-api",
                    )
                )
                count += 1
    except TikTokApiScraperError:
        raise
    except Exception as exc:
        raise TikTokApiScraperError(
            f"Failed to scrape trending TikTok videos: {exc}"
        ) from exc

    return posts


async def scrape_hashtag(tag: str, limit: int = 20) -> list[TikTokApiPost]:
    """Return TikTok posts for a given hashtag using TikTok-Api.

    Args:
        tag: Hashtag to search for (without #).
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikTokApiPost dicts with keys: url, desc, likes, views,
        thumbnail_url, author, source.

    Raises:
        ValueError: If limit is not positive.
        ConfigurationError: If TT_MS_TOKEN env var is not set.
        TikTokApiScraperError: If TikTok-Api fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")

    ms_token: str = _get_ms_token()

    posts: list[TikTokApiPost] = []
    try:
        async with TikTokApi() as api:
            await api.create_sessions(
                num_sessions=1, sleep_after=3, ms_tokens=[ms_token]
            )
            hashtag = api.hashtag(name=tag)
            count = 0
            async for video in hashtag.videos(count=limit):
                if count >= limit:
                    break

                video_id: str = getattr(video, "id", "")
                desc: str = getattr(video, "desc", "")
                as_dict: dict[str, object] = getattr(video, "as_dict", {})

                # Extract stats from as_dict
                stats: dict[str, int] = as_dict.get("stats", {})  # type: ignore[assignment]
                views: int = stats.get("playCount", 0)
                likes: int = stats.get("diggCount", 0)

                # Extract author from as_dict
                author_info: dict[str, str] = as_dict.get("author", {})  # type: ignore[assignment]
                author: str = author_info.get("uniqueId", "")

                # Extract thumbnail from video.playAddr
                video_info: dict[str, str] = as_dict.get("video", {})  # type: ignore[assignment]
                thumbnail_url: str = video_info.get("playAddr", "")

                # Build URL
                url: str = f"https://www.tiktok.com/@{author}/video/{video_id}"

                posts.append(
                    TikTokApiPost(
                        url=url,
                        desc=desc,
                        likes=likes,
                        views=views,
                        thumbnail_url=thumbnail_url,
                        author=author,
                        source="tiktok-api",
                    )
                )
                count += 1
    except TikTokApiScraperError:
        raise
    except Exception as exc:
        raise TikTokApiScraperError(f"Failed to scrape hashtag '{tag}': {exc}") from exc

    return posts
