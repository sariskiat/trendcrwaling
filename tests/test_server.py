# tests/test_server.py
"""Tests for the MCP server tool handler."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.server import CompetitorAnalysisResult, handle_analyze_competitor
from scrapers.facebook import FacebookPost
from scrapers.instagram import InstagramPost
from scrapers.tiktok import TikTokPost


async def test_analyze_competitor_tiktok_only() -> None:
    mock_posts: list[TikTokPost] = [
        TikTokPost(
            url="https://tiktok.com/v/1",
            desc="Promo",
            likes=1000,
            views=0,
            thumbnail_url="",
            author="mk_suki",
        )
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
    tiktok_posts: list[TikTokPost] = [
        TikTokPost(
            url="t1", desc="d", likes=10, views=0, thumbnail_url="", author="test"
        )
    ]
    ig_posts: list[InstagramPost] = [
        InstagramPost(
            url="i1", caption="c", likes=20, post_url="https://instagram.com/p/1/"
        )
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
        InstagramPost(
            url="i1", caption="c", likes=0, post_url="https://instagram.com/p/1/"
        )
    ]
    mock_scrape: AsyncMock = AsyncMock(return_value=ig_posts)
    with patch("mcp_server.server.scrape_instagram", mock_scrape):
        result: CompetitorAnalysisResult = await handle_analyze_competitor(
            name="test_user", platforms=["instagram"], limit=5
        )
    mock_scrape.assert_awaited_once_with("test_user", 5)
    assert result["instagram"] == ig_posts  # type: ignore[index]


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


async def test_scrape_tiktok_user_tool_dispatch() -> None:
    """scrape_tiktok_user tool calls _scrape_tiktok_user(username, limit)."""
    from mcp_server.server import call_tool

    posts: list[TikTokPost] = [
        TikTokPost(
            url="https://tiktok.com/v/1",
            desc="Test",
            likes=0,
            views=500,
            thumbnail_url="https://img/1.jpg",
            author="testuser",
        )
    ]
    with patch(
        "mcp_server.server._scrape_tiktok_user",
        new_callable=AsyncMock,
        return_value=posts,
    ):
        result = await call_tool(  # type: ignore[assignment]
            "scrape_tiktok_user", {"username": "testuser", "limit": 5}
        )

    assert len(result) == 1  # type: ignore[arg-type]
    assert "testuser" in result[0].text  # type: ignore[index]


async def test_scrape_tiktok_trending_tool_dispatch() -> None:
    """scrape_tiktok_trending tool calls _scrape_tiktok_trending(limit)."""
    from mcp_server.server import call_tool

    posts: list[TikTokPost] = [
        TikTokPost(
            url="https://tiktok.com/v/t1",
            desc="Trending",
            likes=0,
            views=9000,
            thumbnail_url="https://img/t1.jpg",
            author="",
        )
    ]
    with patch(
        "mcp_server.server._scrape_tiktok_trending",
        new_callable=AsyncMock,
        return_value=posts,
    ):
        result = await call_tool(  # type: ignore[assignment]
            "scrape_tiktok_trending", {"limit": 10}
        )

    assert len(result) == 1  # type: ignore[arg-type]
    assert "Trending" in result[0].text  # type: ignore[index]


async def test_scrape_tiktok_hashtag_tool_dispatch() -> None:
    """scrape_tiktok_hashtag tool calls _scrape_tiktok_hashtag(tag, limit)."""
    from mcp_server.server import call_tool

    posts: list[TikTokPost] = [
        TikTokPost(
            url="https://tiktok.com/v/h1",
            desc="Hashtag post",
            likes=0,
            views=3000,
            thumbnail_url="https://img/h1.jpg",
            author="",
        )
    ]
    with patch(
        "mcp_server.server._scrape_tiktok_hashtag",
        new_callable=AsyncMock,
        return_value=posts,
    ):
        result = await call_tool(  # type: ignore[assignment]
            "scrape_tiktok_hashtag", {"tag": "sukiyaki", "limit": 5}
        )

    assert len(result) == 1  # type: ignore[arg-type]
    assert "Hashtag post" in result[0].text  # type: ignore[index]


async def test_call_tool_rejects_invalid_username() -> None:
    """scrape_tiktok_user rejects usernames with special characters."""
    from mcp_server.server import call_tool

    with pytest.raises(ValueError, match="Invalid username"):
        await call_tool("scrape_tiktok_user", {"username": "../../../etc/passwd"})


async def test_call_tool_rejects_invalid_tag() -> None:
    """scrape_tiktok_hashtag rejects tags with special characters."""
    from mcp_server.server import call_tool

    with pytest.raises(ValueError, match="Invalid tag"):
        await call_tool("scrape_tiktok_hashtag", {"tag": "'; DROP TABLE--", "limit": 5})


async def test_call_tool_rejects_excessive_limit() -> None:
    """Tools reject limit > 100."""
    from mcp_server.server import call_tool

    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        await call_tool("scrape_tiktok_trending", {"limit": 999})


async def test_call_tool_rejects_invalid_competitor_name() -> None:
    """analyze_competitor rejects names with path traversal."""
    from mcp_server.server import call_tool

    with pytest.raises(ValueError, match="Invalid name"):
        await call_tool(
            "analyze_competitor", {"name": "../../etc", "platforms": ["tiktok"]}
        )


async def test_call_tool_rejects_invalid_platforms() -> None:
    """analyze_competitor rejects when no valid platforms remain."""
    from mcp_server.server import call_tool

    with pytest.raises(ValueError, match="Invalid name|No valid platforms"):
        await call_tool(
            "analyze_competitor", {"name": "validname", "platforms": ["hackme"]}
        )


async def test_handle_analyze_competitor_validates_name_directly() -> None:
    """handle_analyze_competitor validates input even when called directly."""
    with pytest.raises(ValueError, match="Invalid name"):
        await handle_analyze_competitor(
            name="../../../etc/passwd", platforms=["tiktok"], limit=5
        )
