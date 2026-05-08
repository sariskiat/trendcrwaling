"""Tests for the TikTok scraper (Playwright-based)."""

from __future__ import annotations

import os
from contextlib import AbstractContextManager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapers.tiktok import (
    TikTokPost,
    TikTokScraperError,
    scrape_user,
    scrape_trending,
    scrape_hashtag,
)


def _make_pw_mocks(
    evaluate_posts: list[dict[str, str]] | None = None,
) -> tuple[MagicMock, AsyncMock, AsyncMock, AsyncMock]:
    """Return (mock_pw, mock_browser, mock_context, mock_page) wired together.

    Args:
        evaluate_posts: What pg.evaluate() returns for the post-extraction call.
    """
    posts: list[dict[str, str]] = evaluate_posts or []

    mock_pw = MagicMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()

    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.add_cookies = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value=posts)

    return mock_pw, mock_browser, mock_context, mock_page


def _patch_pw(mock_pw: MagicMock) -> AbstractContextManager[MagicMock]:
    """Patch async_playwright to return mock_pw via its async context manager."""
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=mock_pw)
    cm.__aexit__ = AsyncMock(return_value=False)
    return patch("scrapers.tiktok.async_playwright", return_value=cm)


async def test_scrape_user_returns_structured_posts() -> None:
    """scrape_user returns TikTokPost with all fields including views, thumbnail_url, author."""
    fake_posts: list[dict[str, str]] = [
        {
            "url": "https://tiktok.com/@mk_suki/video/123",
            "desc": "Promo night",
            "thumbnail_url": "https://img.tiktok.com/thumb/123.jpg",
            "views": "10000",
            "author": "mk_suki",
        }
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[TikTokPost] = await scrape_user("mk_suki", limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://tiktok.com/@mk_suki/video/123"
    assert result[0]["desc"] == "Promo night"
    assert result[0]["thumbnail_url"] == "https://img.tiktok.com/thumb/123.jpg"
    assert result[0]["views"] == 10000
    assert result[0]["author"] == "mk_suki"
    assert result[0]["likes"] == 0


async def test_scrape_user_respects_limit() -> None:
    """scrape_user respects the limit parameter."""
    fake_posts: list[dict[str, str]] = [
        {
            "url": f"https://tiktok.com/video/{i}",
            "desc": f"Post {i}",
            "thumbnail_url": f"https://img.tt/{i}.jpg",
            "views": f"{i * 1000}",
            "author": "mk_suki",
        }
        for i in range(5)
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[TikTokPost] = await scrape_user("mk_suki", limit=3)

    assert len(result) == 3


async def test_scrape_user_raises_on_invalid_limit() -> None:
    """scrape_user raises ValueError if limit <= 0."""
    with pytest.raises(ValueError, match="limit must be positive"):
        await scrape_user("mk_suki", limit=0)


async def test_scrape_user_raises_scraper_error_on_failure() -> None:
    """scrape_user wraps all exceptions (except TikTokScraperError) in TikTokScraperError."""
    mock_pw = MagicMock()
    mock_pw.chromium.launch = AsyncMock(side_effect=RuntimeError("browser crash"))

    with _patch_pw(mock_pw):
        with pytest.raises(TikTokScraperError, match="Failed to scrape TikTok user"):
            await scrape_user("mk_suki", limit=5)


async def test_scrape_user_injects_cookies_when_env_set() -> None:
    """scrape_user loads and injects cookies from TT_COOKIES_FILE env var."""
    mock_pw, _, mock_context, _ = _make_pw_mocks()
    fake_cookies: list[dict[str, str]] = [
        {
            "name": "sessionid",
            "value": "abc123",
            "domain": ".tiktok.com",
            "path": "/",
        },
    ]

    with patch.dict(os.environ, {"TT_COOKIES_FILE": "tt_cookies.txt"}):
        with patch(
            "scrapers.tiktok._load_cookies", return_value=fake_cookies
        ) as mock_load:
            with _patch_pw(mock_pw):
                await scrape_user("mk_suki", limit=5)

    mock_load.assert_called_once_with("tt_cookies.txt")
    mock_context.add_cookies.assert_called_once_with(fake_cookies)


async def test_scrape_user_skips_cookies_when_env_missing() -> None:
    """scrape_user skips add_cookies if TT_COOKIES_FILE is not set."""
    mock_pw, _, mock_context, _ = _make_pw_mocks()

    with patch.dict(os.environ, {}, clear=True):
        with _patch_pw(mock_pw):
            await scrape_user("mk_suki", limit=5)

    mock_context.add_cookies.assert_not_called()


async def test_scrape_user_closes_browser_on_exception() -> None:
    """browser.close must be called even when _extract_posts raises."""
    mock_pw, mock_browser, _, _ = _make_pw_mocks()
    mock_browser.close = AsyncMock()

    with patch(
        "scrapers.tiktok._extract_posts",
        new=AsyncMock(side_effect=RuntimeError("DOM exploded")),
    ):
        with _patch_pw(mock_pw):
            with pytest.raises(TikTokScraperError):
                await scrape_user("mk_suki", limit=5)

    mock_browser.close.assert_called_once()


# --- scrape_trending tests (ISSUE-017) ---


async def test_scrape_trending_returns_posts() -> None:
    """scrape_trending returns TikTokPost list from explore page."""
    fake_posts: list[dict[str, str]] = [
        {
            "url": "https://tiktok.com/video/t1",
            "desc": "Trending post",
            "thumbnail_url": "https://img.tt/t1.jpg",
            "views": "50000",
            "author": "",
        }
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[TikTokPost] = await scrape_trending(limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://tiktok.com/video/t1"
    assert result[0]["views"] == 50000


async def test_scrape_trending_respects_limit() -> None:
    """scrape_trending caps results at limit."""
    fake_posts: list[dict[str, str]] = [
        {
            "url": f"https://tiktok.com/video/{i}",
            "desc": f"Trend {i}",
            "thumbnail_url": "",
            "views": "100",
            "author": "",
        }
        for i in range(5)
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[TikTokPost] = await scrape_trending(limit=2)

    assert len(result) == 2


async def test_scrape_trending_raises_on_invalid_limit() -> None:
    """scrape_trending raises ValueError if limit <= 0."""
    with pytest.raises(ValueError, match="limit must be positive"):
        await scrape_trending(limit=0)


async def test_scrape_trending_raises_scraper_error_on_failure() -> None:
    """scrape_trending wraps exceptions in TikTokScraperError."""
    mock_pw = MagicMock()
    mock_pw.chromium.launch = AsyncMock(side_effect=RuntimeError("network down"))

    with _patch_pw(mock_pw):
        with pytest.raises(
            TikTokScraperError, match="Failed to scrape TikTok trending"
        ):
            await scrape_trending(limit=5)


# --- scrape_hashtag tests (ISSUE-018) ---


async def test_scrape_hashtag_returns_posts() -> None:
    """scrape_hashtag returns TikTokPost list from /tag/{tag} page."""
    fake_posts: list[dict[str, str]] = [
        {
            "url": "https://tiktok.com/video/h1",
            "desc": "Hashtag post",
            "thumbnail_url": "https://img.tt/h1.jpg",
            "views": "8000",
            "author": "",
        }
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[TikTokPost] = await scrape_hashtag("sukiyaki", limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://tiktok.com/video/h1"
    assert result[0]["views"] == 8000


async def test_scrape_hashtag_respects_limit() -> None:
    """scrape_hashtag caps results at limit."""
    fake_posts: list[dict[str, str]] = [
        {
            "url": f"https://tiktok.com/video/{i}",
            "desc": f"Tag {i}",
            "thumbnail_url": "",
            "views": "200",
            "author": "",
        }
        for i in range(5)
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[TikTokPost] = await scrape_hashtag("sukiyaki", limit=3)

    assert len(result) == 3


async def test_scrape_hashtag_raises_on_invalid_limit() -> None:
    """scrape_hashtag raises ValueError if limit <= 0."""
    with pytest.raises(ValueError, match="limit must be positive"):
        await scrape_hashtag("sukiyaki", limit=0)


async def test_scrape_hashtag_raises_on_empty_tag() -> None:
    """scrape_hashtag raises ValueError if tag is empty."""
    with pytest.raises(ValueError, match="tag must not be empty"):
        await scrape_hashtag("", limit=5)


async def test_scrape_hashtag_raises_scraper_error_on_failure() -> None:
    """scrape_hashtag wraps exceptions in TikTokScraperError."""
    mock_pw = MagicMock()
    mock_pw.chromium.launch = AsyncMock(side_effect=RuntimeError("timeout"))

    with _patch_pw(mock_pw):
        with pytest.raises(TikTokScraperError, match="Failed to scrape TikTok hashtag"):
            await scrape_hashtag("sukiyaki", limit=5)
