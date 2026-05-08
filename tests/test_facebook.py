"""Tests for the Facebook scraper (Playwright-based)."""

from __future__ import annotations

import os
from contextlib import AbstractContextManager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapers.facebook import FacebookPost, FacebookScraperError, scrape_page


def _make_pw_mocks(
    evaluate_posts: list[dict[str, str]] | None = None,
) -> tuple[MagicMock, AsyncMock, AsyncMock, AsyncMock]:
    """Return (mock_pw, mock_browser, mock_context, mock_page) wired together.

    Args:
        evaluate_posts: What pg.evaluate() returns for the post-extraction call.
            Scroll calls (window.scrollTo) return None automatically.
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
    mock_page.wait_for_timeout = AsyncMock()

    def _evaluate_side_effect(js: object) -> list[dict[str, str]] | None:
        if isinstance(js, str) and "scrollTo" in js:
            return None
        return posts

    mock_page.evaluate = AsyncMock(side_effect=_evaluate_side_effect)
    return mock_pw, mock_browser, mock_context, mock_page


def _patch_pw(mock_pw: MagicMock) -> AbstractContextManager[MagicMock]:
    """Patch async_playwright to return mock_pw via its async context manager."""
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=mock_pw)
    cm.__aexit__ = AsyncMock(return_value=False)
    return patch("scrapers.facebook.async_playwright", return_value=cm)


async def test_scrape_page_returns_structured_posts() -> None:
    fake_posts: list[dict[str, str]] = [
        {
            "text": "Today's special buffet!",
            "post_url": "https://www.facebook.com/mkrestaurants/posts/123",
            "image_url": "https://scontent.example.com/img.jpg",
            "time": "2026-05-01",
        }
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[FacebookPost] = await scrape_page("mkrestaurants", limit=1)

    assert len(result) == 1
    assert result[0]["text"] == "Today's special buffet!"
    assert result[0]["post_url"] == "https://www.facebook.com/mkrestaurants/posts/123"
    assert result[0]["image_url"] == "https://scontent.example.com/img.jpg"
    assert result[0]["time"] == "2026-05-01"
    assert result[0]["likes"] == 0


async def test_scrape_page_respects_limit() -> None:
    fake_posts: list[dict[str, str]] = [
        {"text": f"Post {i}", "post_url": "", "image_url": "", "time": ""}
        for i in range(5)
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[FacebookPost] = await scrape_page("mkrestaurants", limit=3)

    assert len(result) == 3


async def test_scrape_page_handles_missing_fields() -> None:
    fake_posts: list[dict[str, str]] = [
        {"text": "", "post_url": "", "image_url": "", "time": ""}
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[FacebookPost] = await scrape_page("mkrestaurants", limit=1)

    assert result[0]["text"] == ""
    assert result[0]["likes"] == 0
    assert result[0]["time"] == ""
    assert result[0]["post_url"] == ""
    assert result[0]["image_url"] == ""


async def test_scrape_page_raises_on_invalid_limit() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        await scrape_page("mkrestaurants", limit=0)


async def test_scrape_page_raises_scraper_error_on_playwright_failure() -> None:
    mock_pw = MagicMock()
    mock_pw.chromium.launch = AsyncMock(side_effect=RuntimeError("browser crashed"))

    with _patch_pw(mock_pw):
        with pytest.raises(
            FacebookScraperError, match="Failed to scrape Facebook page"
        ):
            await scrape_page("mkrestaurants", limit=5)


async def test_scrape_page_injects_cookies_when_env_set() -> None:
    mock_pw, _, mock_context, _ = _make_pw_mocks()
    fake_cookies: list[dict[str, str]] = [
        {"name": "c_user", "value": "123", "domain": ".facebook.com", "path": "/"},
    ]

    with patch.dict(os.environ, {"FB_COOKIES_FILE": "fb_cookies.txt"}):
        with patch(
            "scrapers.facebook._load_cookies", return_value=fake_cookies
        ) as mock_load:
            with _patch_pw(mock_pw):
                await scrape_page("mkrestaurants", limit=5)

    mock_load.assert_called_once_with("fb_cookies.txt")
    mock_context.add_cookies.assert_called_once_with(fake_cookies)


async def test_scrape_page_skips_cookies_when_env_missing() -> None:
    mock_pw, _, mock_context, _ = _make_pw_mocks()

    with patch.dict(os.environ, {}, clear=True):
        with _patch_pw(mock_pw):
            await scrape_page("mkrestaurants", limit=5)

    mock_context.add_cookies.assert_not_called()


async def test_scrape_page_closes_browser_on_exception() -> None:
    """browser.close must be called even when _extract_posts raises."""
    mock_pw, mock_browser, _, _ = _make_pw_mocks()
    mock_browser.close = AsyncMock()

    with patch(
        "scrapers.facebook._extract_posts",
        new=AsyncMock(side_effect=RuntimeError("DOM exploded")),
    ):
        with _patch_pw(mock_pw):
            with pytest.raises(FacebookScraperError):
                await scrape_page("mkrestaurants", limit=5)

    mock_browser.close.assert_called_once()
