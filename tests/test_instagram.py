"""Tests for the Instagram scraper (Playwright-based)."""

from __future__ import annotations

import os
from contextlib import AbstractContextManager
from unittest.mock import AsyncMock, MagicMock, patch
import sys

import pytest

from scrapers.instagram import (
    InstagramPost,
    InstagramScraperError,
    _shortcode_to_timestamp,
    scrape_user,
    scrape_trending,
)

import time


@pytest.mark.asyncio
async def test_scrape_trending_deduplicates():
    """
    Integration: scrape_trending returns deduped posts from #trending and #viral.
    Should not return duplicate post_url, and all posts must be recent (<=10 days old).
    """
    limit = 10
    max_age_days = 10
    posts = await scrape_trending(limit=limit, max_age_days=max_age_days)
    urls = [p["post_url"] for p in posts]
    assert len(urls) == len(set(urls)), "scrape_trending did not deduplicate post_url"
    now = time.time()
    for p in posts:
        assert now - p["created_at"] <= max_age_days * 86400, (
            f"Old post found: {p['created_at']}"
        )
    assert len(posts) <= limit


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


async def test_scrape_user_closes_browser_on_exception() -> None:
    """browser.close must be called even when _extract_posts raises."""
    mock_pw, mock_browser, _, _ = _make_pw_mocks()
    mock_browser.close = AsyncMock()

    with patch(
        "scrapers.instagram._extract_posts",
        new=AsyncMock(side_effect=RuntimeError("DOM exploded")),
    ):
        with _patch_pw(mock_pw):
            with pytest.raises(InstagramScraperError):
                await scrape_user("mk.suki.official", limit=5)

    mock_browser.close.assert_called_once()


def test_shortcode_to_timestamp_known_value() -> None:
    ts = _shortcode_to_timestamp("CnvGmGiLTcD")
    # This post is from early 2023
    assert 1672531200 < ts < 1704067200  # 2023-01-01 to 2024-01-01


def test_shortcode_to_timestamp_returns_zero_on_invalid() -> None:
    assert _shortcode_to_timestamp("") == 0


async def test_scrape_user_result_has_created_at() -> None:
    fake_posts: list[dict[str, str]] = [
        {
            "post_url": "https://www.instagram.com/p/CnvGmGiLTcD/",
            "url": "https://cdn.instagram.com/img/abc.jpg",
            "caption": "test",
        }
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[InstagramPost] = await scrape_user("mk.suki.official", limit=1)

    assert "created_at" in result[0]
    assert result[0]["created_at"] > 0


async def test_scrape_user_created_at_zero_for_malformed_url() -> None:
    fake_posts: list[dict[str, str]] = [
        {"post_url": "https://www.instagram.com/", "url": "", "caption": ""}
    ]
    mock_pw, _, _, _ = _make_pw_mocks(evaluate_posts=fake_posts)

    with _patch_pw(mock_pw):
        result: list[InstagramPost] = await scrape_user("mk.suki.official", limit=1)

    assert result[0]["created_at"] == 0


def test_post_link_selector_includes_reels() -> None:
    from scrapers.instagram import _POST_LINK_SELECTOR

    assert "/reel/" in _POST_LINK_SELECTOR


# ── ISSUE-046: detail-page likes ──────────────────────────────────────────────
from scrapers.instagram import _enrich_posts_with_likes, _scrape_post_likes  # noqa: E402


@pytest.mark.asyncio
async def test_scrape_hashtag_filters_old_posts():
    """
    scrape_hashtag should filter out posts older than max_age_days.
    """
    fake_now = 1700000000
    old_post = {
        "post_url": "https://www.instagram.com/p/OLD/",
        "url": "https://cdn.instagram.com/img/old.jpg",
        "caption": "old post",
        "created_at": fake_now - 20 * 86400,
        "likes": 100,
    }
    new_post = {
        "post_url": "https://www.instagram.com/p/NEW/",
        "url": "https://cdn.instagram.com/img/new.jpg",
        "caption": "new post",
        "created_at": fake_now - 2 * 86400,
        "likes": 200,
    }
    with (
        patch("scrapers.hashtag_generator.generate_hashtags", return_value=["testtag"]),
        patch("scrapers.instagram._scrape_hashtag", return_value=[old_post, new_post]),
        patch(
            "scrapers.instagram._enrich_posts_with_likes",
            side_effect=lambda ctx, posts: posts,
        ),
        patch("time.time", return_value=fake_now),
    ):
        sys.modules["scrapers.instagram"].generate_hashtags = sys.modules[
            "scrapers.hashtag_generator"
        ].generate_hashtags
        from scrapers.instagram import scrape_hashtag

        posts = await scrape_hashtag("test", limit=10, max_age_days=10)
        assert len(posts) == 1
        assert posts[0]["post_url"] == "https://www.instagram.com/p/NEW/"


async def test_scrape_post_likes_returns_integer() -> None:
    mock_ctx = MagicMock()
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.inner_text = AsyncMock(return_value="1,234 likes")
    mock_ctx.new_page = AsyncMock(return_value=mock_page)

    result = await _scrape_post_likes(mock_ctx, "https://www.instagram.com/p/abc123/")
    assert result == 1234


async def test_scrape_post_likes_returns_zero_on_failure() -> None:
    mock_ctx = MagicMock()
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock(side_effect=Exception("not found"))
    mock_ctx.new_page = AsyncMock(return_value=mock_page)

    result = await _scrape_post_likes(mock_ctx, "https://www.instagram.com/p/abc123/")
    assert result == 0


async def test_enrich_posts_with_likes() -> None:
    posts = [
        {"post_url": "https://www.instagram.com/p/A/", "likes": 0},
        {"post_url": "https://www.instagram.com/p/B/", "likes": 0},
    ]

    mock_ctx = MagicMock()

    async def fake_likes(ctx: object, url: str) -> int:
        return 42 if "A" in url else 99

    with patch("scrapers.instagram._scrape_post_likes", side_effect=fake_likes):
        result = await _enrich_posts_with_likes(mock_ctx, posts)

    assert result[0]["likes"] == 42
    assert result[1]["likes"] == 99
