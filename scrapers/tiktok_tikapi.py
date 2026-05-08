"""TikTok scraper using TikAPI.io REST API."""

from __future__ import annotations

import os
from typing import TypedDict

import httpx

from mcp_server.exceptions import ConfigurationError

__all__ = [
    "TikApiPost",
    "TikApiScraperError",
    "scrape_user",
    "scrape_trending",
    "scrape_hashtag",
]

_API_KEY_ENV: str = "TIKAPI_KEY"
_BASE_URL: str = "https://api.tikapi.io/user"


class TikApiPost(TypedDict):
    """A single TikTok post returned by the TikAPI.io scraper."""

    url: str
    desc: str
    likes: int
    views: int
    thumbnail_url: str
    author: str
    source: str


class TikApiScraperError(Exception):
    """Raised when TikAPI.io scraping fails."""


def _get_api_key() -> str:
    """Return the API key from TIKAPI_KEY env var.

    Raises:
        ConfigurationError: If TIKAPI_KEY is not set.
    """
    key: str = os.getenv(_API_KEY_ENV, "")
    if not key:
        raise ConfigurationError(
            f"{_API_KEY_ENV} environment variable is not set. "
            "Export it to provide your TikAPI.io API key for access."
        )
    return key


async def scrape_user(username: str, limit: int = 20) -> list[TikApiPost]:
    """Return recent posts from a public TikTok profile using TikAPI.io.

    Args:
        username: TikTok handle without @.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikApiPost dicts with keys: url, desc, likes, views,
        thumbnail_url, author, source.

    Raises:
        ValueError: If limit is not positive.
        ConfigurationError: If TIKAPI_KEY env var is not set.
        TikApiScraperError: If TikAPI.io request fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")

    api_key: str = _get_api_key()
    url: str = f"{_BASE_URL}/{username}/posts"

    posts: list[TikApiPost] = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"X-API-KEY": api_key},
                params={"count": limit},
            )
            response.raise_for_status()
            data: dict[str, list[dict[str, object]]] = response.json()

        raw_posts: list[dict[str, object]] = data.get("posts", [])
        for raw_post in raw_posts[:limit]:
            post_id: str = str(raw_post.get("id", ""))
            desc: str = str(raw_post.get("desc", ""))

            video_info: dict[str, str] = raw_post.get("video", {})  # type: ignore[assignment]
            thumbnail_url: str = video_info.get("playAddr", "")

            author_info: dict[str, str] = raw_post.get("author", {})  # type: ignore[assignment]
            author: str = author_info.get("uniqueId", username)

            stats: dict[str, int] = raw_post.get("stats", {})  # type: ignore[assignment]
            views: int = stats.get("playCount", 0)
            likes: int = stats.get("diggCount", 0)

            post_url: str = f"https://www.tiktok.com/@{author}/video/{post_id}"

            posts.append(
                TikApiPost(
                    url=post_url,
                    desc=desc,
                    likes=likes,
                    views=views,
                    thumbnail_url=thumbnail_url,
                    author=author,
                    source="tikapi",
                )
            )
    except TikApiScraperError:
        raise
    except httpx.HTTPStatusError as exc:
        raise TikApiScraperError(
            f"Failed to scrape TikTok user '{username}': HTTP {exc.response.status_code}"
        ) from exc
    except Exception as exc:
        raise TikApiScraperError(
            f"Failed to scrape TikTok user '{username}': {exc}"
        ) from exc

    return posts


async def scrape_trending(limit: int = 20) -> list[TikApiPost]:
    """Return trending TikTok posts using TikAPI.io.

    Args:
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikApiPost dicts with keys: url, desc, likes, views,
        thumbnail_url, author, source.

    Raises:
        NotImplementedError: TikAPI.io does not provide a documented trending endpoint.
    """
    raise NotImplementedError(
        "TikAPI.io does not provide a documented trending endpoint. "
        "Use the TikTok-Api scraper (scrapers.tiktok_api) or the Playwright "
        "scraper (scrapers.tiktok) for trending videos."
    )


async def scrape_hashtag(tag: str, limit: int = 20) -> list[TikApiPost]:
    """Return TikTok posts for a given hashtag using TikAPI.io.

    Args:
        tag: Hashtag to search for (without #).
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of TikApiPost dicts with keys: url, desc, likes, views,
        thumbnail_url, author, source.

    Raises:
        NotImplementedError: TikAPI.io does not provide a documented hashtag endpoint.
    """
    raise NotImplementedError(
        f"TikAPI.io does not provide a documented hashtag endpoint. "
        f"Use the TikTok-Api scraper (scrapers.tiktok_api) or the Playwright "
        f"scraper (scrapers.tiktok) for hashtag '{tag}' videos."
    )
