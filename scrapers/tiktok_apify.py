"""TikTok scraper using Apify Clockworks API."""

from __future__ import annotations

import os
from typing import TypedDict

import httpx

from mcp_server.exceptions import ConfigurationError

__all__ = [
    "ApifyTikTokPost",
    "ApifyTikTokScraperError",
    "scrape_user",
]

_API_TOKEN_ENV: str = "APIFY_TOKEN"
_BASE_URL: str = (
    "https://api.apify.com/v2/acts/clockworks~tiktok-profile-scraper/run-sync-get-dataset-items"
)


class ApifyTikTokPost(TypedDict):
    """A single TikTok post returned by the Apify Clockworks scraper."""

    url: str
    desc: str
    likes: int
    views: int
    thumbnail_url: str
    author: str
    source: str


class ApifyTikTokScraperError(Exception):
    """Raised when Apify Clockworks scraping fails."""


def _get_api_token() -> str:
    """Return the API token from APIFY_TOKEN env var.

    Raises:
        ConfigurationError: If APIFY_TOKEN is not set.
    """
    token: str = os.getenv(_API_TOKEN_ENV, "")
    if not token:
        raise ConfigurationError(
            f"{_API_TOKEN_ENV} environment variable is not set. "
            "Export it to provide your Apify API token for access."
        )
    return token


async def scrape_user(username: str, limit: int = 20) -> list[ApifyTikTokPost]:
    """Return recent posts from a public TikTok profile using Apify Clockworks.

    Args:
        username: TikTok handle without @.
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of ApifyTikTokPost dicts with keys: url, desc, likes, views,
        thumbnail_url, author, source.

    Raises:
        ValueError: If limit is not positive.
        ConfigurationError: If APIFY_TOKEN env var is not set.
        ApifyTikTokScraperError: If Apify API request fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")

    api_token: str = _get_api_token()

    posts: list[ApifyTikTokPost] = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{_BASE_URL}?token={api_token}",
                json={"username": username, "resultsLimit": limit},
                timeout=60.0,
            )
            response.raise_for_status()
            data: list[dict[str, object]] = response.json()

        for raw_post in data[:limit]:
            post_id: str = str(raw_post.get("id", ""))
            desc: str = str(raw_post.get("text", ""))

            video_info: dict[str, str] = raw_post.get("video", {})  # type: ignore[assignment]
            thumbnail_url: str = video_info.get("playAddr", "")

            author: str = str(raw_post.get("authorName", username))

            views_raw: object = raw_post.get("playCount", 0)
            views: int = int(views_raw) if isinstance(views_raw, int) else 0

            likes_raw: object = raw_post.get("diggCount", 0)
            likes: int = int(likes_raw) if isinstance(likes_raw, int) else 0

            post_url: str = f"https://www.tiktok.com/@{author}/video/{post_id}"

            posts.append(
                ApifyTikTokPost(
                    url=post_url,
                    desc=desc,
                    likes=likes,
                    views=views,
                    thumbnail_url=thumbnail_url,
                    author=author,
                    source="apify",
                )
            )
    except ApifyTikTokScraperError:
        raise
    except httpx.HTTPStatusError as exc:
        raise ApifyTikTokScraperError(
            f"Failed to scrape TikTok user '{username}': HTTP {exc.response.status_code}"
        ) from exc
    except Exception as exc:
        raise ApifyTikTokScraperError(
            f"Failed to scrape TikTok user '{username}': {exc}"
        ) from exc

    return posts
