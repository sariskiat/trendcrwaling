"""Tests for the TikTok scraper."""

from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapers.tiktok import TikTokPost, TikTokScraperError, scrape_user


async def test_scrape_user_returns_structured_posts() -> None:
    mock_video: MagicMock = MagicMock()
    mock_video.url = "https://tiktok.com/@mk_suki/video/123"
    mock_video.desc = "Promo night"
    mock_video.stats.digg_count = 500

    async def _videos() -> AsyncGenerator[MagicMock, None]:
        yield mock_video

    mock_user: MagicMock = MagicMock()
    mock_user.videos = _videos()

    mock_api: MagicMock = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.user = AsyncMock(return_value=mock_user)

    with patch("scrapers.tiktok.TikTokAPI", return_value=mock_api):
        result: list[TikTokPost] = await scrape_user("mk_suki", limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://tiktok.com/@mk_suki/video/123"
    assert result[0]["desc"] == "Promo night"
    assert result[0]["likes"] == 500


async def test_scrape_user_respects_limit() -> None:
    async def _videos() -> AsyncGenerator[MagicMock, None]:
        for i in range(5):
            v: MagicMock = MagicMock()
            v.url = f"https://tiktok.com/video/{i}"
            v.desc = f"Post {i}"
            v.stats.digg_count = i * 100
            yield v

    mock_user: MagicMock = MagicMock()
    mock_user.videos = _videos()

    mock_api: MagicMock = MagicMock()
    mock_api.__aenter__ = AsyncMock(return_value=mock_api)
    mock_api.__aexit__ = AsyncMock(return_value=None)
    mock_api.user = AsyncMock(return_value=mock_user)

    with patch("scrapers.tiktok.TikTokAPI", return_value=mock_api):
        result: list[TikTokPost] = await scrape_user("mk_suki", limit=3)

    assert len(result) == 3


async def test_scrape_user_raises_on_invalid_limit() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        await scrape_user("mk_suki", limit=0)


async def test_scrape_user_raises_scraper_error_on_api_failure() -> None:
    mock_api: MagicMock = MagicMock()
    mock_api.__aenter__ = AsyncMock(side_effect=RuntimeError("network down"))
    mock_api.__aexit__ = AsyncMock(return_value=None)

    with patch("scrapers.tiktok.TikTokAPI", return_value=mock_api):
        with pytest.raises(TikTokScraperError, match="Failed to scrape TikTok user"):
            await scrape_user("mk_suki", limit=5)
