"""Tests for the TikAPI.io scraper."""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server.exceptions import ConfigurationError
from scrapers.tiktok_tikapi import (
    TikApiPost,
    TikApiScraperError,
    scrape_user,
    scrape_trending,
    scrape_hashtag,
)


def _make_client_mock(
    response_data: dict[str, Any] | None = None,
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
        mock_client.get = AsyncMock(side_effect=raise_error)
    else:
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value=response_data or {})
        mock_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)

    return mock_client


async def test_scrape_user_returns_posts_with_source() -> None:
    """scrape_user returns TikApiPost with all fields including source provenance."""
    fake_response: dict[str, Any] = {
        "posts": [
            {
                "id": "7234567890",
                "desc": "Test video description",
                "video": {"playAddr": "https://video.tiktok.com/123.mp4"},
                "author": {"uniqueId": "testuser"},
                "stats": {"playCount": 10000, "diggCount": 500},
            }
        ]
    }

    mock_client = _make_client_mock(response_data=fake_response)

    with patch.dict(os.environ, {"TIKAPI_KEY": "test-api-key"}):
        with patch(
            "scrapers.tiktok_tikapi.httpx.AsyncClient", return_value=mock_client
        ):
            result: list[TikApiPost] = await scrape_user("testuser", limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://www.tiktok.com/@testuser/video/7234567890"
    assert result[0]["desc"] == "Test video description"
    assert result[0]["views"] == 10000
    assert result[0]["likes"] == 500
    assert result[0]["author"] == "testuser"
    assert result[0]["source"] == "tikapi"


async def test_scrape_user_raises_configuration_error_without_api_key() -> None:
    """scrape_user raises ConfigurationError if TIKAPI_KEY env var is not set."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ConfigurationError, match="TIKAPI_KEY"):
            await scrape_user("testuser", limit=5)


async def test_scrape_user_respects_limit() -> None:
    """scrape_user respects the limit parameter."""
    fake_response: dict[str, Any] = {
        "posts": [
            {
                "id": f"{i}",
                "desc": f"Video {i}",
                "video": {"playAddr": f"https://video.tiktok.com/{i}.mp4"},
                "author": {"uniqueId": "testuser"},
                "stats": {"playCount": i * 1000, "diggCount": i * 10},
            }
            for i in range(5)
        ]
    }

    mock_client = _make_client_mock(response_data=fake_response)

    with patch.dict(os.environ, {"TIKAPI_KEY": "test-api-key"}):
        with patch(
            "scrapers.tiktok_tikapi.httpx.AsyncClient", return_value=mock_client
        ):
            result: list[TikApiPost] = await scrape_user("testuser", limit=3)

    assert len(result) == 3


async def test_scrape_user_raises_on_invalid_limit() -> None:
    """scrape_user raises ValueError if limit <= 0."""
    with patch.dict(os.environ, {"TIKAPI_KEY": "test-api-key"}):
        with pytest.raises(ValueError, match="limit must be positive"):
            await scrape_user("testuser", limit=0)


async def test_scrape_user_wraps_http_errors() -> None:
    """scrape_user wraps HTTP exceptions in TikApiScraperError."""
    import httpx

    http_error = httpx.HTTPStatusError(
        "404 Not Found",
        request=httpx.Request("GET", "https://api.tikapi.io/user/test/posts"),
        response=httpx.Response(404),
    )

    mock_client = _make_client_mock(raise_error=http_error)

    with patch.dict(os.environ, {"TIKAPI_KEY": "test-api-key"}):
        with patch(
            "scrapers.tiktok_tikapi.httpx.AsyncClient", return_value=mock_client
        ):
            with pytest.raises(TikApiScraperError, match="Failed to scrape"):
                await scrape_user("testuser", limit=5)


async def test_scrape_user_handles_empty_response() -> None:
    """scrape_user handles empty posts list gracefully."""
    fake_response: dict[str, Any] = {"posts": []}

    mock_client = _make_client_mock(response_data=fake_response)

    with patch.dict(os.environ, {"TIKAPI_KEY": "test-api-key"}):
        with patch(
            "scrapers.tiktok_tikapi.httpx.AsyncClient", return_value=mock_client
        ):
            result: list[TikApiPost] = await scrape_user("testuser", limit=5)

    assert result == []


async def test_scrape_user_handles_missing_thumbnail() -> None:
    """scrape_user handles missing thumbnail gracefully with empty string."""
    fake_response: dict[str, Any] = {
        "posts": [
            {
                "id": "123",
                "desc": "No thumbnail",
                "video": {},  # No playAddr
                "author": {"uniqueId": "testuser"},
                "stats": {"playCount": 100, "diggCount": 5},
            }
        ]
    }

    mock_client = _make_client_mock(response_data=fake_response)

    with patch.dict(os.environ, {"TIKAPI_KEY": "test-api-key"}):
        with patch(
            "scrapers.tiktok_tikapi.httpx.AsyncClient", return_value=mock_client
        ):
            result: list[TikApiPost] = await scrape_user("testuser", limit=1)

    assert result[0]["thumbnail_url"] == ""


# ============== scrape_trending tests ==============


async def test_scrape_trending_raises_not_implemented() -> None:
    """scrape_trending raises NotImplementedError as TikAPI.io does not have a documented trending endpoint."""
    with patch.dict(os.environ, {"TIKAPI_KEY": "test-api-key"}):
        with pytest.raises(
            NotImplementedError,
            match="TikAPI.io does not provide a documented trending endpoint",
        ):
            await scrape_trending(limit=5)


# ============== scrape_hashtag tests ==============


async def test_scrape_hashtag_raises_not_implemented() -> None:
    """scrape_hashtag raises NotImplementedError as TikAPI.io does not have a documented hashtag endpoint."""
    with patch.dict(os.environ, {"TIKAPI_KEY": "test-api-key"}):
        with pytest.raises(
            NotImplementedError,
            match="TikAPI.io does not provide a documented hashtag endpoint",
        ):
            await scrape_hashtag("dance", limit=5)
