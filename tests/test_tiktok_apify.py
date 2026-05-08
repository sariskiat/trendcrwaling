"""Tests for the Apify Clockworks TikTok scraper."""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server.exceptions import ConfigurationError
from scrapers.tiktok_apify import (
    ApifyTikTokPost,
    ApifyTikTokScraperError,
    scrape_user,
    scrape_trending,
    scrape_hashtag,
)


def _make_client_mock(
    response_data: list[dict[str, Any]] | None = None,
    raise_error: Exception | None = None,
) -> MagicMock:
    """Create a mocked httpx.AsyncClient context manager.

    Args:
        response_data: The JSON data to return from the response.
        raise_error: An exception to raise when making the request.

    Returns:
        A MagicMock configured as an async context manager that returns a client.
    """
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    if raise_error:
        mock_client.post = AsyncMock(side_effect=raise_error)
    else:
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value=response_data or [])
        mock_response.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)

    return mock_client


async def test_scrape_user_returns_posts_with_source() -> None:
    """scrape_user returns ApifyTikTokPost with all fields including source provenance."""
    fake_response: list[dict[str, Any]] = [
        {
            "id": "7234567890",
            "text": "Test video description",
            "video": {"playAddr": "https://video.tiktok.com/123.mp4"},
            "authorName": "testuser",
            "playCount": 10000,
            "diggCount": 500,
        }
    ]

    mock_client = _make_client_mock(response_data=fake_response)

    with patch.dict(os.environ, {"APIFY_TOKEN": "test-apify-token"}):
        with patch("scrapers.tiktok_apify.httpx.AsyncClient", return_value=mock_client):
            result: list[ApifyTikTokPost] = await scrape_user("testuser", limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://www.tiktok.com/@testuser/video/7234567890"
    assert result[0]["desc"] == "Test video description"
    assert result[0]["views"] == 10000
    assert result[0]["likes"] == 500
    assert result[0]["author"] == "testuser"
    assert result[0]["source"] == "apify"


async def test_scrape_user_raises_configuration_error_without_api_token() -> None:
    """scrape_user raises ConfigurationError if APIFY_TOKEN env var is not set."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ConfigurationError, match="APIFY_TOKEN"):
            await scrape_user("testuser", limit=5)


async def test_scrape_user_respects_limit() -> None:
    """scrape_user respects the limit parameter."""
    fake_response: list[dict[str, Any]] = [
        {
            "id": f"{i}",
            "text": f"Video {i}",
            "video": {"playAddr": f"https://video.tiktok.com/{i}.mp4"},
            "authorName": "testuser",
            "playCount": i * 1000,
            "diggCount": i * 10,
        }
        for i in range(5)
    ]

    mock_client = _make_client_mock(response_data=fake_response)

    with patch.dict(os.environ, {"APIFY_TOKEN": "test-apify-token"}):
        with patch("scrapers.tiktok_apify.httpx.AsyncClient", return_value=mock_client):
            result: list[ApifyTikTokPost] = await scrape_user("testuser", limit=3)

    assert len(result) == 3


async def test_scrape_user_raises_on_invalid_limit() -> None:
    """scrape_user raises ValueError if limit <= 0."""
    with patch.dict(os.environ, {"APIFY_TOKEN": "test-apify-token"}):
        with pytest.raises(ValueError, match="limit must be positive"):
            await scrape_user("testuser", limit=0)


async def test_scrape_user_wraps_http_errors() -> None:
    """scrape_user wraps HTTP exceptions in ApifyTikTokScraperError."""
    import httpx

    http_error = httpx.HTTPStatusError(
        "404 Not Found",
        request=httpx.Request("POST", "https://api.apify.io/v2/acts/"),
        response=httpx.Response(404),
    )

    mock_client = _make_client_mock(raise_error=http_error)

    with patch.dict(os.environ, {"APIFY_TOKEN": "test-apify-token"}):
        with patch("scrapers.tiktok_apify.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(ApifyTikTokScraperError, match="Failed to scrape"):
                await scrape_user("testuser", limit=5)


# ============== scrape_trending tests ==============


async def test_scrape_trending_raises_not_implemented() -> None:
    """scrape_trending raises NotImplementedError as Apify Clockworks scraper does not support trending."""
    with patch.dict(os.environ, {"APIFY_TOKEN": "test-apify-token"}):
        with pytest.raises(
            NotImplementedError,
            match="Apify Clockworks scraper does not support trending",
        ):
            await scrape_trending(limit=5)


# ============== scrape_hashtag tests ==============


async def test_scrape_hashtag_raises_not_implemented() -> None:
    """scrape_hashtag raises NotImplementedError as Apify Clockworks scraper does not support hashtag."""
    with patch.dict(os.environ, {"APIFY_TOKEN": "test-apify-token"}):
        with pytest.raises(
            NotImplementedError,
            match="Apify Clockworks scraper does not support hashtag",
        ):
            await scrape_hashtag("dance", limit=5)
