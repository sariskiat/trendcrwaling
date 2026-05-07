# tests/test_server.py
"""Tests for the MCP server tool handler."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch


from mcp_server.server import CompetitorAnalysisResult, handle_analyze_competitor
from scrapers.facebook import FacebookPost
from scrapers.instagram import InstagramPost
from scrapers.tiktok import TikTokPost


async def test_analyze_competitor_tiktok_only() -> None:
    mock_posts: list[TikTokPost] = [
        TikTokPost(url="https://tiktok.com/v/1", desc="Promo", likes=1000)
    ]
    with patch(
        "mcp_server.server.scrape_tiktok",
        new_callable=AsyncMock,
        return_value=mock_posts,
    ):
        result: CompetitorAnalysisResult = await handle_analyze_competitor(
            name="mk_suki", platforms=["tiktok"], limit=5
        )

    assert "tiktok" in result
    assert len(result["tiktok"]) == 1
    assert "instagram" not in result
    assert "facebook" not in result


async def test_analyze_competitor_all_platforms() -> None:
    tiktok_posts: list[TikTokPost] = [TikTokPost(url="t1", desc="d", likes=10)]
    ig_posts: list[InstagramPost] = [
        InstagramPost(url="i1", caption="c", likes=20, post_url="https://instagram.com/p/1/")
    ]
    fb_posts: list[FacebookPost] = [
        FacebookPost(text="f1", likes=30, time="2026-05-01", post_url="", image_url="")
    ]

    with (
        patch(
            "mcp_server.server.scrape_tiktok",
            new_callable=AsyncMock,
            return_value=tiktok_posts,
        ),
        patch(
            "mcp_server.server.scrape_instagram",
            new_callable=AsyncMock,
            return_value=ig_posts,
        ),
        patch("mcp_server.server.scrape_facebook", return_value=fb_posts),
    ):
        result: CompetitorAnalysisResult = await handle_analyze_competitor(
            name="barbegon", platforms=["tiktok", "instagram", "facebook"], limit=5
        )

    assert "tiktok" in result
    assert "instagram" in result
    assert "facebook" in result


async def test_analyze_competitor_instagram_awaited_without_session_file() -> None:
    """scrape_instagram must be awaited with (name, limit) — no session_file arg."""
    ig_posts: list[InstagramPost] = [
        InstagramPost(url="i1", caption="c", likes=0, post_url="https://instagram.com/p/1/")
    ]
    mock_scrape: AsyncMock = AsyncMock(return_value=ig_posts)
    with patch("mcp_server.server.scrape_instagram", mock_scrape):
        result: CompetitorAnalysisResult = await handle_analyze_competitor(
            name="test_user", platforms=["instagram"], limit=5
        )
    mock_scrape.assert_awaited_once_with("test_user", 5)
    assert result["instagram"] == ig_posts


async def test_analyze_competitor_skips_unselected_platforms() -> None:
    fb_posts: list[FacebookPost] = [
        FacebookPost(
            text="fb post", likes=5, time="2026-05-01", post_url="", image_url=""
        )
    ]

    with patch("mcp_server.server.scrape_facebook", return_value=fb_posts):
        result: CompetitorAnalysisResult = await handle_analyze_competitor(
            name="barbegon", platforms=["facebook"], limit=5
        )

    assert "facebook" in result
    assert "tiktok" not in result
    assert "instagram" not in result
