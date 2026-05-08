"""Tests for the TikTok-Api library scraper."""

from __future__ import annotations

import os
from contextlib import AbstractContextManager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server.exceptions import ConfigurationError
from scrapers.tiktok_api import (
    TikTokApiPost,
    TikTokApiScraperError,
    scrape_user,
    scrape_trending,
    scrape_hashtag,
)


def _make_api_mocks(
    videos: list[dict[str, Any]] | None = None,
) -> tuple[MagicMock, MagicMock, MagicMock]:
    """Return (mock_api, mock_user, mock_video_iter) wired together.

    Args:
        videos: List of video dicts with id, desc, as_dict keys.
    """
    videos = videos or []

    mock_api = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.create_sessions = AsyncMock()

    mock_user = MagicMock()
    mock_api.user = MagicMock(return_value=mock_user)

    # Create async iterator for videos
    async def _video_gen() -> object:
        for v in videos:
            mock_video = MagicMock()
            mock_video.id = v.get("id", "123")
            mock_video.desc = v.get("desc", "")
            mock_video.as_dict = v.get("as_dict", {})
            yield mock_video

    mock_user.videos = MagicMock(return_value=_video_gen())

    return mock_api, mock_user, mock_user.videos


def _patch_tiktok_api(mock_api: MagicMock) -> AbstractContextManager[MagicMock]:
    """Patch TikTokApi import to return mock_api."""
    return patch("scrapers.tiktok_api.TikTokApi", return_value=mock_api)


async def test_scrape_user_returns_posts_with_source() -> None:
    """scrape_user returns TikTokApiPost with all fields including source provenance."""
    fake_videos: list[dict[str, Any]] = [
        {
            "id": "7234567890",
            "desc": "Test video description",
            "as_dict": {
                "video": {"playAddr": "https://video.tiktok.com/123.mp4"},
                "author": {"uniqueId": "testuser"},
                "stats": {"playCount": 10000, "diggCount": 500},
            },
        }
    ]
    mock_api, _, _ = _make_api_mocks(videos=fake_videos)

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            result: list[TikTokApiPost] = await scrape_user("testuser", limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://www.tiktok.com/@testuser/video/7234567890"
    assert result[0]["desc"] == "Test video description"
    assert result[0]["views"] == 10000
    assert result[0]["likes"] == 500
    assert result[0]["author"] == "testuser"
    assert result[0]["source"] == "tiktok-api"


async def test_scrape_user_raises_configuration_error_without_token() -> None:
    """scrape_user raises ConfigurationError if TT_MS_TOKEN env var is not set."""
    mock_api, _, _ = _make_api_mocks()

    with patch.dict(os.environ, {}, clear=True):
        with _patch_tiktok_api(mock_api):
            with pytest.raises(ConfigurationError, match="TT_MS_TOKEN"):
                await scrape_user("testuser", limit=5)


async def test_scrape_user_respects_limit() -> None:
    """scrape_user respects the limit parameter."""
    fake_videos: list[dict[str, Any]] = [
        {
            "id": f"{i}",
            "desc": f"Video {i}",
            "as_dict": {
                "video": {"playAddr": f"https://video.tiktok.com/{i}.mp4"},
                "author": {"uniqueId": "testuser"},
                "stats": {"playCount": i * 1000, "diggCount": i * 10},
            },
        }
        for i in range(5)
    ]
    mock_api, _, _ = _make_api_mocks(videos=fake_videos)

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            result: list[TikTokApiPost] = await scrape_user("testuser", limit=3)

    assert len(result) == 3


async def test_scrape_user_raises_on_invalid_limit() -> None:
    """scrape_user raises ValueError if limit <= 0."""
    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with pytest.raises(ValueError, match="limit must be positive"):
            await scrape_user("testuser", limit=0)


async def test_scrape_user_wraps_library_errors() -> None:
    """scrape_user wraps TikTokApi exceptions in TikTokApiScraperError."""
    mock_api = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.create_sessions = AsyncMock(side_effect=RuntimeError("API failure"))

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            with pytest.raises(TikTokApiScraperError, match="Failed to scrape"):
                await scrape_user("testuser", limit=5)


async def test_scrape_user_passes_ms_token_to_sessions() -> None:
    """scrape_user passes ms_tokens to create_sessions when available."""
    mock_api, _, _ = _make_api_mocks()

    with patch.dict(os.environ, {"TT_MS_TOKEN": "my-secret-token"}):
        with _patch_tiktok_api(mock_api):
            await scrape_user("testuser", limit=1)

    mock_api.create_sessions.assert_called_once()
    call_kwargs = mock_api.create_sessions.call_args[1]
    assert call_kwargs.get("ms_tokens") == ["my-secret-token"]


async def test_scrape_user_generates_correct_url() -> None:
    """scrape_user generates correct TikTok URL from video id and author."""
    fake_videos: list[dict[str, Any]] = [
        {
            "id": "999888777",
            "desc": "URL test",
            "as_dict": {
                "video": {"playAddr": "https://video.tiktok.com/999.mp4"},
                "author": {"uniqueId": "sukiyaki_lover"},
                "stats": {"playCount": 100, "diggCount": 5},
            },
        }
    ]
    mock_api, _, _ = _make_api_mocks(videos=fake_videos)

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            result: list[TikTokApiPost] = await scrape_user("sukiyaki_lover", limit=1)

    assert result[0]["url"] == "https://www.tiktok.com/@sukiyaki_lover/video/999888777"


async def test_scrape_user_handles_missing_thumbnail() -> None:
    """scrape_user handles missing thumbnail gracefully with empty string."""
    fake_videos: list[dict[str, Any]] = [
        {
            "id": "123",
            "desc": "No thumbnail",
            "as_dict": {
                "video": {},  # No playAddr
                "author": {"uniqueId": "testuser"},
                "stats": {"playCount": 100, "diggCount": 5},
            },
        }
    ]
    mock_api, _, _ = _make_api_mocks(videos=fake_videos)

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            result: list[TikTokApiPost] = await scrape_user("testuser", limit=1)

    assert result[0]["thumbnail_url"] == ""


def _make_trending_mocks(
    videos: list[dict[str, Any]] | None = None,
) -> tuple[MagicMock, MagicMock]:
    """Return (mock_api, mock_trending) wired together for trending videos.

    Args:
        videos: List of video dicts with id, desc, as_dict keys.
    """
    videos = videos or []

    mock_api = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.create_sessions = AsyncMock()

    mock_trending = MagicMock()
    mock_api.trending = mock_trending

    # Create async iterator for videos
    async def _video_gen() -> object:
        for v in videos:
            mock_video = MagicMock()
            mock_video.id = v.get("id", "123")
            mock_video.desc = v.get("desc", "")
            mock_video.as_dict = v.get("as_dict", {})
            yield mock_video

    mock_trending.videos = MagicMock(return_value=_video_gen())

    return mock_api, mock_trending


def _make_hashtag_mocks(
    videos: list[dict[str, Any]] | None = None,
) -> tuple[MagicMock, MagicMock, MagicMock]:
    """Return (mock_api, mock_hashtag, mock_tag) wired together for hashtag videos.

    Args:
        videos: List of video dicts with id, desc, as_dict keys.
    """
    videos = videos or []

    mock_api = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.create_sessions = AsyncMock()

    mock_tag = MagicMock()
    mock_api.hashtag = MagicMock(return_value=mock_tag)

    # Create async iterator for videos
    async def _video_gen() -> object:
        for v in videos:
            mock_video = MagicMock()
            mock_video.id = v.get("id", "123")
            mock_video.desc = v.get("desc", "")
            mock_video.as_dict = v.get("as_dict", {})
            yield mock_video

    mock_tag.videos = MagicMock(return_value=_video_gen())

    return mock_api, mock_tag, mock_api.hashtag


# ============== scrape_trending tests ==============


async def test_scrape_trending_returns_posts_with_source() -> None:
    """scrape_trending returns TikTokApiPost with all fields including source provenance."""
    fake_videos: list[dict[str, Any]] = [
        {
            "id": "7234567890",
            "desc": "Trending video description",
            "as_dict": {
                "video": {"playAddr": "https://video.tiktok.com/123.mp4"},
                "author": {"uniqueId": "trendinguser"},
                "stats": {"playCount": 50000, "diggCount": 2000},
            },
        }
    ]
    mock_api, _ = _make_trending_mocks(videos=fake_videos)

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            result: list[TikTokApiPost] = await scrape_trending(limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://www.tiktok.com/@trendinguser/video/7234567890"
    assert result[0]["desc"] == "Trending video description"
    assert result[0]["views"] == 50000
    assert result[0]["likes"] == 2000
    assert result[0]["author"] == "trendinguser"
    assert result[0]["source"] == "tiktok-api"


async def test_scrape_trending_raises_configuration_error_without_token() -> None:
    """scrape_trending raises ConfigurationError if TT_MS_TOKEN env var is not set."""
    mock_api, _ = _make_trending_mocks()

    with patch.dict(os.environ, {}, clear=True):
        with _patch_tiktok_api(mock_api):
            with pytest.raises(ConfigurationError, match="TT_MS_TOKEN"):
                await scrape_trending(limit=5)


async def test_scrape_trending_respects_limit() -> None:
    """scrape_trending respects the limit parameter."""
    fake_videos: list[dict[str, Any]] = [
        {
            "id": f"{i}",
            "desc": f"Trending Video {i}",
            "as_dict": {
                "video": {"playAddr": f"https://video.tiktok.com/{i}.mp4"},
                "author": {"uniqueId": "trendinguser"},
                "stats": {"playCount": i * 1000, "diggCount": i * 10},
            },
        }
        for i in range(5)
    ]
    mock_api, _ = _make_trending_mocks(videos=fake_videos)

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            result: list[TikTokApiPost] = await scrape_trending(limit=3)

    assert len(result) == 3


async def test_scrape_trending_raises_on_invalid_limit() -> None:
    """scrape_trending raises ValueError if limit <= 0."""
    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with pytest.raises(ValueError, match="limit must be positive"):
            await scrape_trending(limit=0)


async def test_scrape_trending_wraps_library_errors() -> None:
    """scrape_trending wraps TikTokApi exceptions in TikTokApiScraperError."""
    mock_api = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.create_sessions = AsyncMock(side_effect=RuntimeError("API failure"))

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            with pytest.raises(
                TikTokApiScraperError, match="Failed to scrape trending"
            ):
                await scrape_trending(limit=5)


# ============== scrape_hashtag tests ==============


async def test_scrape_hashtag_returns_posts_with_source() -> None:
    """scrape_hashtag returns TikTokApiPost with all fields including source provenance."""
    fake_videos: list[dict[str, Any]] = [
        {
            "id": "7234567890",
            "desc": "Hashtag video description",
            "as_dict": {
                "video": {"playAddr": "https://video.tiktok.com/123.mp4"},
                "author": {"uniqueId": "hashtaguser"},
                "stats": {"playCount": 30000, "diggCount": 1500},
            },
        }
    ]
    mock_api, _, _ = _make_hashtag_mocks(videos=fake_videos)

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            result: list[TikTokApiPost] = await scrape_hashtag("dance", limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://www.tiktok.com/@hashtaguser/video/7234567890"
    assert result[0]["desc"] == "Hashtag video description"
    assert result[0]["views"] == 30000
    assert result[0]["likes"] == 1500
    assert result[0]["author"] == "hashtaguser"
    assert result[0]["source"] == "tiktok-api"


async def test_scrape_hashtag_raises_configuration_error_without_token() -> None:
    """scrape_hashtag raises ConfigurationError if TT_MS_TOKEN env var is not set."""
    mock_api, _, _ = _make_hashtag_mocks()

    with patch.dict(os.environ, {}, clear=True):
        with _patch_tiktok_api(mock_api):
            with pytest.raises(ConfigurationError, match="TT_MS_TOKEN"):
                await scrape_hashtag("dance", limit=5)


async def test_scrape_hashtag_respects_limit() -> None:
    """scrape_hashtag respects the limit parameter."""
    fake_videos: list[dict[str, Any]] = [
        {
            "id": f"{i}",
            "desc": f"Hashtag Video {i}",
            "as_dict": {
                "video": {"playAddr": f"https://video.tiktok.com/{i}.mp4"},
                "author": {"uniqueId": "hashtaguser"},
                "stats": {"playCount": i * 1000, "diggCount": i * 10},
            },
        }
        for i in range(5)
    ]
    mock_api, _, _ = _make_hashtag_mocks(videos=fake_videos)

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            result: list[TikTokApiPost] = await scrape_hashtag("dance", limit=3)

    assert len(result) == 3


async def test_scrape_hashtag_raises_on_invalid_limit() -> None:
    """scrape_hashtag raises ValueError if limit <= 0."""
    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with pytest.raises(ValueError, match="limit must be positive"):
            await scrape_hashtag("dance", limit=0)


async def test_scrape_hashtag_wraps_library_errors() -> None:
    """scrape_hashtag wraps TikTokApi exceptions in TikTokApiScraperError."""
    mock_api = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.create_sessions = AsyncMock(side_effect=RuntimeError("API failure"))

    with patch.dict(os.environ, {"TT_MS_TOKEN": "test-token"}):
        with _patch_tiktok_api(mock_api):
            with pytest.raises(TikTokApiScraperError, match="Failed to scrape hashtag"):
                await scrape_hashtag("dance", limit=5)
