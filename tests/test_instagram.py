"""Tests for the Instagram scraper (Playwright-based)."""

from __future__ import annotations

import os
from contextlib import AbstractContextManager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapers.instagram import InstagramPost, InstagramScraperError, scrape_user


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
    return patch("scrapers.instagram.async_playwright", return_value=cm)


async def test_scrape_user_returns_structured_posts() -> None:
    fake_posts: list[dict[str, str]] = [
        {
            "post_url": "https://www.instagram.com/p/ABC123/",
            "url": "https://cdn.instagram.com/img/abc.jpg",
            "caption": "Suki special night!",
        }
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[InstagramPost] = await scrape_user("mk.suki.official", limit=1)

    assert len(result) == 1
    assert result[0]["post_url"] == "https://www.instagram.com/p/ABC123/"
    assert result[0]["url"] == "https://cdn.instagram.com/img/abc.jpg"
    assert result[0]["caption"] == "Suki special night!"
    assert result[0]["likes"] == 0


async def test_scrape_user_respects_limit() -> None:
    fake_posts: list[dict[str, str]] = [
        {"post_url": f"https://www.instagram.com/p/{i}/", "url": "", "caption": ""}
        for i in range(5)
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[InstagramPost] = await scrape_user("mk.suki.official", limit=3)

    assert len(result) == 3


async def test_scrape_user_handles_missing_fields() -> None:
    fake_posts: list[dict[str, str]] = [{"post_url": "", "url": "", "caption": ""}]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[InstagramPost] = await scrape_user("mk.suki.official", limit=1)

    assert result[0]["post_url"] == ""
    assert result[0]["url"] == ""
    assert result[0]["caption"] == ""
    assert result[0]["likes"] == 0


async def test_scrape_user_raises_on_invalid_limit() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        await scrape_user("mk.suki.official", limit=0)


async def test_scrape_user_raises_scraper_error_on_playwright_failure() -> None:
    mock_pw = MagicMock()
    mock_pw.chromium.launch = AsyncMock(side_effect=RuntimeError("browser crashed"))

    with _patch_pw(mock_pw):
        with pytest.raises(
            InstagramScraperError, match="Failed to scrape Instagram user"
        ):
            await scrape_user("mk.suki.official", limit=5)


async def test_scrape_user_injects_cookies_when_env_set() -> None:
    mock_pw, _, mock_context, _ = _make_pw_mocks()
    fake_cookies: list[dict[str, str]] = [
        {
            "name": "sessionid",
            "value": "abc123",
            "domain": ".instagram.com",
            "path": "/",
        },
    ]

    with patch.dict(os.environ, {"IG_COOKIES_FILE": "ig_cookies.txt"}):
        with patch(
            "scrapers.instagram._load_cookies", return_value=fake_cookies
        ) as mock_load:
            with _patch_pw(mock_pw):
                await scrape_user("mk.suki.official", limit=5)

    mock_load.assert_called_once_with("ig_cookies.txt")
    mock_context.add_cookies.assert_called_once_with(fake_cookies)


async def test_scrape_user_skips_cookies_when_env_missing() -> None:
    mock_pw, _, mock_context, _ = _make_pw_mocks()

    with patch.dict(os.environ, {}, clear=True):
        with _patch_pw(mock_pw):
            await scrape_user("mk.suki.official", limit=5)

    mock_context.add_cookies.assert_not_called()
