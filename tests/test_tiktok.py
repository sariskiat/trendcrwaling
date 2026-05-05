"""Tests for TikTok scraper."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapers.tiktok import scrape_user


async def test_scrape_user_returns_structured_posts() -> None:
    """Test scrape_user returns properly structured post dicts."""
    mock_video = MagicMock()
    mock_video.url = "https://tiktok.com/@mk_suki/video/123"
    mock_video.desc = "Promo night"
    mock_video.stats.digg_count = 500

    async def _videos() -> object:
        yield mock_video

    mock_user = MagicMock()
    mock_user.videos = _videos()

    mock_api = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.user = AsyncMock(return_value=mock_user)

    with patch("scrapers.tiktok.TikTokAPI", return_value=mock_api):
        result: list[dict[str, object]] = await scrape_user("mk_suki", limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://tiktok.com/@mk_suki/video/123"
    assert result[0]["desc"] == "Promo night"
    assert result[0]["likes"] == 500


async def test_scrape_user_respects_limit() -> None:
    """Test scrape_user stops collecting posts after reaching limit."""
    async def _videos() -> object:
        for i in range(5):
            v = MagicMock()
            v.url = f"https://tiktok.com/video/{i}"
            v.desc = f"Post {i}"
            v.stats.digg_count = i * 100
            yield v

    mock_user = MagicMock()
    mock_user.videos = _videos()

    mock_api = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.user = AsyncMock(return_value=mock_user)

    with patch("scrapers.tiktok.TikTokAPI", return_value=mock_api):
        result: list[dict[str, object]] = await scrape_user("mk_suki", limit=3)

    assert len(result) == 3
