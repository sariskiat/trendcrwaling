# tests/test_server.py
"""Tests for the FastMCP-based MCP server."""

from __future__ import annotations

import json
import time
from unittest.mock import AsyncMock, patch

import pytest

from scrapers.tiktok import TikTokPost


async def test_tiktok_user_posts_success() -> None:
    """tiktok_user_posts returns JSON string with post data on success."""
    from mcp_server.server import tiktok_user_posts

    mock_posts: list[TikTokPost] = [
        TikTokPost(
            url="https://tiktok.com/v/1",
            desc="Test post",
            likes=1000,
            views=5000,
            thumbnail_url="https://img.jpg",
            author="testuser",
        )
    ]
    with (
        patch(
            "mcp_server.server._scrape_tiktok_user",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await tiktok_user_posts("testuser", limit=20)

    # Result should be a JSON string
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["author"] == "testuser"
    assert parsed[0]["likes"] == 1000


async def test_tiktok_user_posts_invalid_username() -> None:
    """tiktok_user_posts raises ValidationError for invalid username."""
    from mcp_server.server import tiktok_user_posts, ValidationError

    with patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="Invalid username"):
            await tiktok_user_posts("../../../etc/passwd", limit=20)


@pytest.mark.asyncio
async def test_instagram_global_trending_tool():
    """
    Integration: MCP tool instagram_global_trending(limit) returns deduped, recent, sorted posts.
    - Returns up to `limit` posts with keys post_url, url, caption, likes, created_at
    - Deduped by post_url, sorted by likes desc (fallback created_at desc)
    - All posts: now - created_at <= 864000 when created_at > 0
    - Tool is registered and callable via MCP
    """
    from mcp_server.server import instagram_global_trending
    from scrapers.instagram import InstagramPost
    import time

    limit = 7
    now = int(time.time())
    mock_posts: list[InstagramPost] = [
        InstagramPost(
            url="https://cdn.instagram.com/img1.jpg",
            caption="Recent post 1",
            likes=500,
            post_url="https://www.instagram.com/p/POST001/",
            created_at=now - 86400,  # 1 day ago
        ),
        InstagramPost(
            url="https://cdn.instagram.com/img2.jpg",
            caption="Recent post 2",
            likes=300,
            post_url="https://www.instagram.com/p/POST002/",
            created_at=now - 172800,  # 2 days ago
        ),
    ]
    with (
        patch(
            "mcp_server.server._scrape_instagram_trending",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"IG_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await instagram_global_trending(limit)

    assert isinstance(result, str), "Tool should return a JSON string"
    posts = json.loads(result)
    assert isinstance(posts, list)
    assert len(posts) <= limit
    post_urls = set()
    last_likes = None
    last_created = None
    for post in posts:
        assert set(post.keys()) >= {"post_url", "url", "caption", "likes", "created_at"}
        assert post["post_url"] not in post_urls, "Duplicate post_url found"
        post_urls.add(post["post_url"])
        if post["created_at"] > 0:
            assert now - post["created_at"] <= 864000, (
                f"Old post found: {post['created_at']}"
            )
        if last_likes is not None:
            assert post["likes"] <= last_likes or (
                post["likes"] == last_likes and post["created_at"] <= last_created
            ), "Posts not sorted by likes desc, fallback created_at desc"
        last_likes = post["likes"]
        last_created = post["created_at"]
    # Tool should appear in MCP tool list
    from mcp_server.server import mcp

    tools = await mcp.list_tools()
    # Print tool names for debug
    print([getattr(t, "name", t) for t in tools])
    assert any(
        getattr(t, "name", None) == "instagram_global_trending" for t in tools
    ), "Tool not registered in MCP"


@pytest.mark.asyncio
async def test_instagram_hashtag_trending_success() -> None:
    """
    Integration: MCP tool instagram_hashtag_trending(query, limit) returns deduped, recent, sorted posts.
    - Returns JSON string with deduped posts by post_url
    - Includes /p/ and /reel/ URLs
    - Sorted by likes desc
    - All posts: now - created_at <= 864000 when created_at > 0
    """
    from mcp_server.server import instagram_hashtag_trending
    from scrapers.instagram import InstagramPost

    query = "cats"
    limit = 7
    now = int(time.time())
    mock_posts: list[InstagramPost] = [
        InstagramPost(
            url="https://cdn.instagram.com/img1.jpg",
            caption="Recent /p/ post",
            likes=500,
            post_url="https://www.instagram.com/p/POST001/",
            created_at=now - 86400,
        ),
        InstagramPost(
            url="https://cdn.instagram.com/img2.jpg",
            caption="Recent /reel/ post",
            likes=300,
            post_url="https://www.instagram.com/reel/REEL001/",
            created_at=now - 172800,
        ),
    ]
    with (
        patch(
            "mcp_server.server._scrape_instagram_hashtag",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"IG_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await instagram_hashtag_trending(query, limit)

    assert isinstance(result, str), "Tool should return a JSON string"
    posts = json.loads(result)
    assert isinstance(posts, list)
    assert len(posts) <= limit
    post_urls = set()
    last_likes = None
    last_created = None
    for post in posts:
        assert set(post.keys()) >= {"post_url", "url", "caption", "likes", "created_at"}
        assert post["post_url"] not in post_urls, "Duplicate post_url found"
        post_urls.add(post["post_url"])
        if post["created_at"] > 0:
            assert now - post["created_at"] <= 864000, (
                f"Old post found: {post['created_at']}"
            )
        if last_likes is not None:
            assert post["likes"] <= last_likes or (
                post["likes"] == last_likes and post["created_at"] <= last_created
            ), "Posts not sorted by likes desc, fallback created_at desc"
        last_likes = post["likes"]
        last_created = post["created_at"]
    # Verify /p/ and /reel/ URLs are present
    urls = [p["post_url"] for p in posts]
    assert any("/p/" in u for u in urls), "No /p/ URLs found"
    assert any("/reel/" in u for u in urls), "No /reel/ URLs found"


@pytest.mark.asyncio
async def test_instagram_hashtag_trending_missing_cookies() -> None:
    """instagram_hashtag_trending raises ConfigurationError with actionable message when IG_COOKIES_FILE not set."""
    from mcp_server.server import instagram_hashtag_trending, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="IG_COOKIES_FILE environment variable is not set"
        ):
            await instagram_hashtag_trending("cats", limit=10)


@pytest.mark.asyncio
async def test_instagram_hashtag_trending_invalid_limit() -> None:
    """instagram_hashtag_trending raises ValidationError for limit=0 or limit>100."""
    from mcp_server.server import instagram_hashtag_trending, ValidationError

    with patch.dict("os.environ", {"IG_COOKIES_FILE": "/path/to/cookies.txt"}):
        # Test limit=0
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await instagram_hashtag_trending("cats", limit=0)
        # Test limit=999
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await instagram_hashtag_trending("cats", limit=999)


async def test_tiktok_user_posts_invalid_limit_zero() -> None:
    """tiktok_user_posts raises ValidationError for limit < 1."""
    from mcp_server.server import tiktok_user_posts, ValidationError

    with patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await tiktok_user_posts("validuser", limit=0)


async def test_tiktok_user_posts_invalid_limit_too_high() -> None:
    """tiktok_user_posts raises ValidationError for limit > 100."""
    from mcp_server.server import tiktok_user_posts, ValidationError

    with patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await tiktok_user_posts("validuser", limit=999)


async def test_tiktok_user_posts_missing_cookies() -> None:
    """tiktok_user_posts raises ConfigurationError with actionable message when TT_COOKIES_FILE not set."""
    from mcp_server.server import tiktok_user_posts, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="TT_COOKIES_FILE environment variable is not set"
        ):
            await tiktok_user_posts("validuser", limit=20)


async def test_instagram_global_trending_tool_requires_ig_cookies():
    """instagram_global_trending raises ConfigurationError with actionable message when IG_COOKIES_FILE not set."""
    from mcp_server.server import instagram_global_trending, ConfigurationError

    # IG_COOKIES_FILE not set
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="IG_COOKIES_FILE environment variable is not set"
        ):
            await instagram_global_trending(5)


# Tests for tiktok_trending
async def test_tiktok_trending_success() -> None:
    """tiktok_trending returns JSON string with trending post data on success."""
    from mcp_server.server import tiktok_trending

    mock_posts: list[TikTokPost] = [
        TikTokPost(
            url="https://tiktok.com/v/trending1",
            desc="Trending post 1",
            likes=50000,
            views=250000,
            thumbnail_url="https://img.jpg",
            author="trendinguser1",
        ),
        TikTokPost(
            url="https://tiktok.com/v/trending2",
            desc="Trending post 2",
            likes=45000,
            views=230000,
            thumbnail_url="https://img2.jpg",
            author="trendinguser2",
        ),
    ]
    with (
        patch(
            "mcp_server.server._scrape_tiktok_trending",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await tiktok_trending(limit=20)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["author"] == "trendinguser1"
    assert parsed[1]["likes"] == 45000


async def test_tiktok_trending_invalid_limit_zero() -> None:
    """tiktok_trending raises ValidationError for limit < 1."""
    from mcp_server.server import tiktok_trending, ValidationError

    with patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await tiktok_trending(limit=0)


async def test_tiktok_trending_invalid_limit_too_high() -> None:
    """tiktok_trending raises ValidationError for limit > 100."""
    from mcp_server.server import tiktok_trending, ValidationError

    with patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await tiktok_trending(limit=200)


async def test_tiktok_trending_missing_cookies() -> None:
    """tiktok_trending raises ConfigurationError with actionable message when TT_COOKIES_FILE not set."""
    from mcp_server.server import tiktok_trending, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="TT_COOKIES_FILE environment variable is not set"
        ):
            await tiktok_trending(limit=20)


# Tests for tiktok_hashtag_posts
async def test_tiktok_hashtag_posts_success() -> None:
    """tiktok_hashtag_posts returns JSON string with hashtag post data on success."""
    from mcp_server.server import tiktok_hashtag_posts

    mock_posts: list[TikTokPost] = [
        TikTokPost(
            url="https://tiktok.com/v/hashtag1",
            desc="Post with hashtag",
            likes=5000,
            views=25000,
            thumbnail_url="https://img.jpg",
            author="hashtaguserl",
        )
    ]
    with (
        patch(
            "mcp_server.server._scrape_tiktok_hashtag",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await tiktok_hashtag_posts(tag="trending", limit=20)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["author"] == "hashtaguserl"
    assert parsed[0]["likes"] == 5000


async def test_tiktok_hashtag_posts_invalid_tag() -> None:
    """tiktok_hashtag_posts raises ValidationError for invalid tag."""
    from mcp_server.server import tiktok_hashtag_posts, ValidationError

    with patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="Invalid tag"):
            await tiktok_hashtag_posts(tag="../../etc/passwd", limit=20)


async def test_tiktok_hashtag_posts_invalid_limit_zero() -> None:
    """tiktok_hashtag_posts raises ValidationError for limit < 1."""
    from mcp_server.server import tiktok_hashtag_posts, ValidationError

    with patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await tiktok_hashtag_posts(tag="trending", limit=0)


async def test_tiktok_hashtag_posts_invalid_limit_too_high() -> None:
    """tiktok_hashtag_posts raises ValidationError for limit > 100."""
    from mcp_server.server import tiktok_hashtag_posts, ValidationError

    with patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await tiktok_hashtag_posts(tag="trending", limit=500)


async def test_tiktok_hashtag_posts_missing_cookies() -> None:
    """tiktok_hashtag_posts raises ConfigurationError with actionable message when TT_COOKIES_FILE not set."""
    from mcp_server.server import tiktok_hashtag_posts, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="TT_COOKIES_FILE environment variable is not set"
        ):
            await tiktok_hashtag_posts(tag="trending", limit=20)


# Tests for tiktok_user_posts_api
async def test_tiktok_user_posts_api_success() -> None:
    """tiktok_user_posts_api returns JSON string with post data including source provenance."""
    from mcp_server.server import tiktok_user_posts_api
    from scrapers.tiktok_api import TikTokApiPost

    mock_posts: list[TikTokApiPost] = [
        TikTokApiPost(
            url="https://tiktok.com/@testuser/video/123",
            desc="API post",
            likes=1000,
            views=5000,
            thumbnail_url="https://img.jpg",
            author="testuser",
            source="tiktok-api",
            created_at=int(time.time()) - (1 * 86400),
        )
    ]
    with patch(
        "mcp_server.server._scrape_tiktok_api_user",
        new_callable=AsyncMock,
        return_value=mock_posts,
    ):
        result = await tiktok_user_posts_api("testuser", limit=20)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["author"] == "testuser"
    assert parsed[0]["likes"] == 1000
    assert parsed[0]["source"] == "tiktok-api"


async def test_tiktok_user_posts_api_invalid_username() -> None:
    """tiktok_user_posts_api raises ValidationError for invalid username."""
    from mcp_server.server import tiktok_user_posts_api, ValidationError

    with pytest.raises(ValidationError, match="Invalid username"):
        await tiktok_user_posts_api("../../../etc/passwd", limit=20)


async def test_tiktok_user_posts_api_invalid_limit_zero() -> None:
    """tiktok_user_posts_api raises ValidationError for limit < 1."""
    from mcp_server.server import tiktok_user_posts_api, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_user_posts_api("validuser", limit=0)


async def test_tiktok_user_posts_api_invalid_limit_too_high() -> None:
    """tiktok_user_posts_api raises ValidationError for limit > 100."""
    from mcp_server.server import tiktok_user_posts_api, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_user_posts_api("validuser", limit=999)


async def test_tiktok_user_posts_api_scraper_error_propagates() -> None:
    """tiktok_user_posts_api propagates TikTokApiScraperError from scraper."""
    from mcp_server.server import tiktok_user_posts_api
    from scrapers.tiktok_api import TikTokApiScraperError

    with patch(
        "mcp_server.server._scrape_tiktok_api_user",
        new_callable=AsyncMock,
        side_effect=TikTokApiScraperError("API failed"),
    ):
        with pytest.raises(TikTokApiScraperError, match="API failed"):
            await tiktok_user_posts_api("testuser", limit=20)


async def test_tiktok_user_posts_api_config_error_propagates() -> None:
    """tiktok_user_posts_api propagates ConfigurationError when TT_MS_TOKEN missing."""
    from mcp_server.server import tiktok_user_posts_api, ConfigurationError

    with patch(
        "mcp_server.server._scrape_tiktok_api_user",
        new_callable=AsyncMock,
        side_effect=ConfigurationError("TT_MS_TOKEN not set"),
    ):
        with pytest.raises(ConfigurationError, match="TT_MS_TOKEN"):
            await tiktok_user_posts_api("testuser", limit=20)


# Tests for tiktok_user_posts_tikapi
async def test_tiktok_user_posts_tikapi_success() -> None:
    """tiktok_user_posts_tikapi returns JSON string with post data including source provenance."""
    from mcp_server.server import tiktok_user_posts_tikapi
    from scrapers.tiktok_tikapi import TikApiPost

    mock_posts: list[TikApiPost] = [
        TikApiPost(
            url="https://tiktok.com/@testuser/video/123",
            desc="TikAPI post",
            likes=1000,
            views=5000,
            thumbnail_url="https://img.jpg",
            author="testuser",
            source="tikapi",
        )
    ]
    with patch(
        "mcp_server.server._scrape_tikapi_user",
        new_callable=AsyncMock,
        return_value=mock_posts,
    ):
        result = await tiktok_user_posts_tikapi("testuser", limit=20)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["author"] == "testuser"
    assert parsed[0]["likes"] == 1000
    assert parsed[0]["source"] == "tikapi"


async def test_tiktok_user_posts_tikapi_invalid_username() -> None:
    """tiktok_user_posts_tikapi raises ValidationError for invalid username."""
    from mcp_server.server import tiktok_user_posts_tikapi, ValidationError

    with pytest.raises(ValidationError, match="Invalid username"):
        await tiktok_user_posts_tikapi("../../../etc/passwd", limit=20)


async def test_tiktok_user_posts_tikapi_invalid_limit_zero() -> None:
    """tiktok_user_posts_tikapi raises ValidationError for limit < 1."""
    from mcp_server.server import tiktok_user_posts_tikapi, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_user_posts_tikapi("validuser", limit=0)


async def test_tiktok_user_posts_tikapi_invalid_limit_too_high() -> None:
    """tiktok_user_posts_tikapi raises ValidationError for limit > 100."""
    from mcp_server.server import tiktok_user_posts_tikapi, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_user_posts_tikapi("validuser", limit=999)


async def test_tiktok_user_posts_tikapi_config_error_propagates() -> None:
    """tiktok_user_posts_tikapi propagates ConfigurationError when TIKAPI_KEY missing."""
    from mcp_server.server import tiktok_user_posts_tikapi, ConfigurationError

    with patch(
        "mcp_server.server._scrape_tikapi_user",
        new_callable=AsyncMock,
        side_effect=ConfigurationError("TIKAPI_KEY environment variable is not set"),
    ):
        with pytest.raises(ConfigurationError, match="TIKAPI_KEY"):
            await tiktok_user_posts_tikapi("testuser", limit=20)


# Tests for tiktok_user_posts_apify
async def test_tiktok_user_posts_apify_success() -> None:
    """tiktok_user_posts_apify returns JSON string with post data including source provenance."""
    from mcp_server.server import tiktok_user_posts_apify
    from scrapers.tiktok_apify import ApifyTikTokPost

    mock_posts: list[ApifyTikTokPost] = [
        ApifyTikTokPost(
            url="https://tiktok.com/@testuser/video/123",
            desc="Apify post",
            likes=1000,
            views=5000,
            thumbnail_url="https://img.jpg",
            author="testuser",
            source="apify",
        )
    ]
    with patch(
        "mcp_server.server._scrape_apify_user",
        new_callable=AsyncMock,
        return_value=mock_posts,
    ):
        result = await tiktok_user_posts_apify("testuser", limit=20)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["author"] == "testuser"
    assert parsed[0]["likes"] == 1000
    assert parsed[0]["source"] == "apify"


# Tests for tiktok_trending_api
async def test_tiktok_trending_api_success() -> None:
    """tiktok_trending_api returns JSON string with trending post data including source provenance."""
    from mcp_server.server import tiktok_trending_api
    from scrapers.tiktok_api import TikTokApiPost

    mock_posts: list[TikTokApiPost] = [
        TikTokApiPost(
            url="https://tiktok.com/v/trending1",
            desc="Trending post 1",
            likes=50000,
            views=250000,
            thumbnail_url="https://img.jpg",
            author="trendinguser1",
            source="tiktok-api",
            created_at=int(time.time()) - (1 * 86400),
        )
    ]
    with patch(
        "mcp_server.server._scrape_tiktok_api_trending",
        new_callable=AsyncMock,
        return_value=mock_posts,
    ):
        result = await tiktok_trending_api(limit=20)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["author"] == "trendinguser1"
    assert parsed[0]["source"] == "tiktok-api"


async def test_tiktok_trending_api_invalid_limit_zero() -> None:
    """tiktok_trending_api raises ValidationError for limit < 1."""
    from mcp_server.server import tiktok_trending_api, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_trending_api(limit=0)


async def test_tiktok_trending_api_invalid_limit_too_high() -> None:
    """tiktok_trending_api raises ValidationError for limit > 100."""
    from mcp_server.server import tiktok_trending_api, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_trending_api(limit=200)


# Tests for tiktok_trending_tikapi
async def test_tiktok_trending_tikapi_raises_not_implemented() -> None:
    """tiktok_trending_tikapi raises NotImplementedError as TikAPI.io does not support trending."""
    from mcp_server.server import tiktok_trending_tikapi

    with pytest.raises(NotImplementedError, match="TikAPI.io does not provide"):
        await tiktok_trending_tikapi(limit=5)


async def test_tiktok_trending_tikapi_invalid_limit() -> None:
    """tiktok_trending_tikapi raises ValidationError for invalid limit."""
    from mcp_server.server import tiktok_trending_tikapi, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_trending_tikapi(limit=0)


# Tests for tiktok_trending_apify
async def test_tiktok_trending_apify_raises_not_implemented() -> None:
    """tiktok_trending_apify raises NotImplementedError as Apify Clockworks does not support trending."""
    from mcp_server.server import tiktok_trending_apify

    with pytest.raises(
        NotImplementedError, match="Apify Clockworks scraper does not support"
    ):
        await tiktok_trending_apify(limit=5)


async def test_tiktok_trending_apify_invalid_limit() -> None:
    """tiktok_trending_apify raises ValidationError for invalid limit."""
    from mcp_server.server import tiktok_trending_apify, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_trending_apify(limit=0)


# Tests for tiktok_hashtag_api
async def test_tiktok_hashtag_api_success() -> None:
    """tiktok_hashtag_api returns JSON string with hashtag post data including source provenance."""
    from mcp_server.server import tiktok_hashtag_api
    from scrapers.tiktok_api import TikTokApiPost

    mock_posts: list[TikTokApiPost] = [
        TikTokApiPost(
            url="https://tiktok.com/v/hashtag1",
            desc="Hashtag post 1",
            likes=30000,
            views=150000,
            thumbnail_url="https://img.jpg",
            author="hashtaguser1",
            source="tiktok-api",
            created_at=int(time.time()) - (1 * 86400),
        )
    ]
    with patch(
        "mcp_server.server._scrape_tiktok_api_hashtag",
        new_callable=AsyncMock,
        return_value=mock_posts,
    ):
        result = await tiktok_hashtag_api("dance", limit=20)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["author"] == "hashtaguser1"
    assert parsed[0]["source"] == "tiktok-api"


async def test_tiktok_hashtag_api_invalid_tag() -> None:
    """tiktok_hashtag_api raises ValidationError for invalid tag."""
    from mcp_server.server import tiktok_hashtag_api, ValidationError

    with pytest.raises(ValidationError, match="Invalid tag"):
        await tiktok_hashtag_api("../../../etc/passwd", limit=20)


async def test_tiktok_hashtag_api_invalid_limit_zero() -> None:
    """tiktok_hashtag_api raises ValidationError for limit < 1."""
    from mcp_server.server import tiktok_hashtag_api, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_hashtag_api("dance", limit=0)


async def test_tiktok_hashtag_api_invalid_limit_too_high() -> None:
    """tiktok_hashtag_api raises ValidationError for limit > 100."""
    from mcp_server.server import tiktok_hashtag_api, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_hashtag_api("dance", limit=200)


# Tests for tiktok_hashtag_tikapi
async def test_tiktok_hashtag_tikapi_raises_not_implemented() -> None:
    """tiktok_hashtag_tikapi raises NotImplementedError as TikAPI.io does not support hashtag."""
    from mcp_server.server import tiktok_hashtag_tikapi

    with pytest.raises(NotImplementedError, match="TikAPI.io does not provide"):
        await tiktok_hashtag_tikapi("dance", limit=5)


async def test_tiktok_hashtag_tikapi_invalid_tag() -> None:
    """tiktok_hashtag_tikapi raises ValidationError for invalid tag."""
    from mcp_server.server import tiktok_hashtag_tikapi, ValidationError

    with pytest.raises(ValidationError, match="Invalid tag"):
        await tiktok_hashtag_tikapi("../../../etc/passwd", limit=20)


async def test_tiktok_hashtag_tikapi_invalid_limit() -> None:
    """tiktok_hashtag_tikapi raises ValidationError for invalid limit."""
    from mcp_server.server import tiktok_hashtag_tikapi, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_hashtag_tikapi("dance", limit=0)


# Tests for tiktok_hashtag_apify
async def test_tiktok_hashtag_apify_raises_not_implemented() -> None:
    """tiktok_hashtag_apify raises NotImplementedError as Apify Clockworks does not support hashtag."""
    from mcp_server.server import tiktok_hashtag_apify

    with pytest.raises(
        NotImplementedError, match="Apify Clockworks scraper does not support"
    ):
        await tiktok_hashtag_apify("dance", limit=5)


async def test_tiktok_hashtag_apify_invalid_tag() -> None:
    """tiktok_hashtag_apify raises ValidationError for invalid tag."""
    from mcp_server.server import tiktok_hashtag_apify, ValidationError

    with pytest.raises(ValidationError, match="Invalid tag"):
        await tiktok_hashtag_apify("../../../etc/passwd", limit=20)


async def test_tiktok_hashtag_apify_invalid_limit() -> None:
    """tiktok_hashtag_apify raises ValidationError for invalid limit."""
    from mcp_server.server import tiktok_hashtag_apify, ValidationError

    with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
        await tiktok_hashtag_apify("dance", limit=0)


# Tests for instagram_user_posts
async def test_instagram_user_posts_success() -> None:
    """instagram_user_posts returns JSON string with post data on success."""
    from mcp_server.server import instagram_user_posts
    from scrapers.instagram import InstagramPost

    mock_posts: list[InstagramPost] = [
        InstagramPost(
            url="https://instagram.com/img1.jpg",
            caption="Test post",
            likes=1000,
            post_url="https://instagram.com/p/abc123",
        )
    ]
    with (
        patch(
            "mcp_server.server._scrape_instagram_user",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"IG_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await instagram_user_posts("testuser", limit=20)

    # Result should be a JSON string
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["caption"] == "Test post"
    assert parsed[0]["likes"] == 1000


async def test_instagram_user_posts_invalid_username() -> None:
    """instagram_user_posts raises ValidationError for invalid username."""
    from mcp_server.server import instagram_user_posts, ValidationError

    with patch.dict("os.environ", {"IG_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="Invalid username"):
            await instagram_user_posts("../../../etc/passwd", limit=20)


async def test_instagram_user_posts_invalid_limit_zero() -> None:
    """instagram_user_posts raises ValidationError for limit < 1."""
    from mcp_server.server import instagram_user_posts, ValidationError

    with patch.dict("os.environ", {"IG_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await instagram_user_posts("validuser", limit=0)


async def test_instagram_user_posts_invalid_limit_too_high() -> None:
    """instagram_user_posts raises ValidationError for limit > 100."""
    from mcp_server.server import instagram_user_posts, ValidationError

    with patch.dict("os.environ", {"IG_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await instagram_user_posts("validuser", limit=999)


async def test_instagram_user_posts_missing_cookies() -> None:
    """instagram_user_posts raises ConfigurationError with actionable message when IG_COOKIES_FILE not set."""
    from mcp_server.server import instagram_user_posts, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="IG_COOKIES_FILE environment variable is not set"
        ):
            await instagram_user_posts("validuser", limit=20)


# Tests for facebook_page_posts
async def test_facebook_page_posts_success() -> None:
    """facebook_page_posts returns JSON string with post data on success."""
    from mcp_server.server import facebook_page_posts
    from scrapers.facebook import FacebookPost

    mock_posts: list[FacebookPost] = [
        FacebookPost(
            text="Test post",
            likes=500,
            time="2025-01-15",
            post_url="https://facebook.com/posts/abc123",
            image_url="https://scontent.xx.fbcdn.net/img.jpg",
        )
    ]
    with (
        patch(
            "mcp_server.server._scrape_facebook_page",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await facebook_page_posts("testpage", limit=20)

    # Result should be a JSON string
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["text"] == "Test post"
    assert parsed[0]["likes"] == 500


async def test_facebook_page_posts_invalid_page_name() -> None:
    """facebook_page_posts raises ValidationError for invalid page name."""
    from mcp_server.server import facebook_page_posts, ValidationError

    with patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="Invalid page_name"):
            await facebook_page_posts("../../../etc/passwd", limit=20)


async def test_facebook_page_posts_invalid_limit_zero() -> None:
    """facebook_page_posts raises ValidationError for limit < 1."""
    from mcp_server.server import facebook_page_posts, ValidationError

    with patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await facebook_page_posts("validpage", limit=0)


async def test_facebook_page_posts_invalid_limit_too_high() -> None:
    """facebook_page_posts raises ValidationError for limit > 100."""
    from mcp_server.server import facebook_page_posts, ValidationError

    with patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await facebook_page_posts("validpage", limit=999)


async def test_facebook_page_posts_missing_cookies() -> None:
    """facebook_page_posts raises ConfigurationError with actionable message when FB_COOKIES_FILE not set."""
    from mcp_server.server import facebook_page_posts, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="FB_COOKIES_FILE environment variable is not set"
        ):
            await facebook_page_posts("validpage", limit=20)


# Tests for scraper exception propagation
async def test_tiktok_user_posts_scraper_error_propagates() -> None:
    """tiktok_user_posts propagates TikTokScraperError from scraper."""
    from mcp_server.server import tiktok_user_posts
    from scrapers.tiktok import TikTokScraperError

    with (
        patch(
            "mcp_server.server._scrape_tiktok_user",
            new_callable=AsyncMock,
            side_effect=TikTokScraperError("Browser failed"),
        ),
        patch.dict("os.environ", {"TT_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        with pytest.raises(TikTokScraperError, match="Browser failed"):
            await tiktok_user_posts("testuser", limit=20)


async def test_instagram_user_posts_scraper_error_propagates() -> None:
    """instagram_user_posts propagates InstagramScraperError from scraper."""
    from mcp_server.server import instagram_user_posts
    from scrapers.instagram import InstagramScraperError

    with (
        patch(
            "mcp_server.server._scrape_instagram_user",
            new_callable=AsyncMock,
            side_effect=InstagramScraperError("Login required"),
        ),
        patch.dict("os.environ", {"IG_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        with pytest.raises(InstagramScraperError, match="Login required"):
            await instagram_user_posts("testuser", limit=20)


async def test_facebook_page_posts_scraper_error_propagates() -> None:
    """facebook_page_posts propagates FacebookScraperError from scraper."""
    from mcp_server.server import facebook_page_posts
    from scrapers.facebook import FacebookScraperError

    with (
        patch(
            "mcp_server.server._scrape_facebook_page",
            new_callable=AsyncMock,
            side_effect=FacebookScraperError("Page not found"),
        ),
        patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        with pytest.raises(FacebookScraperError, match="Page not found"):
            await facebook_page_posts("testpage", limit=20)


async def test_analyze_image_openai_error_propagates() -> None:
    """analyze_image propagates OpenAI API errors."""
    from mcp_server.server import analyze_image
    from openai import APIConnectionError
    import httpx

    error = APIConnectionError(
        message="Connection refused",
        request=httpx.Request("GET", "https://api.openai.com"),
    )

    with (
        patch(
            "mcp_server.image_analysis.AsyncOpenAI",
            side_effect=error,
        ),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
    ):
        with pytest.raises(APIConnectionError):
            await analyze_image("https://example.com/image.jpg")


# Tests for custom exception hierarchy
def test_exception_hierarchy_exists() -> None:
    """Custom exception classes exist with correct inheritance."""
    from mcp_server.exceptions import (
        AnalysisError,
        ConfigurationError,
        MCPServerError,
        ValidationError,
    )

    # All inherit from MCPServerError, which inherits from ValueError
    assert issubclass(MCPServerError, ValueError)
    assert issubclass(ValidationError, MCPServerError)
    assert issubclass(ConfigurationError, MCPServerError)
    assert issubclass(AnalysisError, MCPServerError)


def test_validation_error_is_value_error() -> None:
    """ValidationError is a ValueError for FastMCP compatibility."""
    from mcp_server.exceptions import ValidationError

    exc = ValidationError("test message")
    assert isinstance(exc, ValueError)
    assert str(exc) == "test message"


def test_configuration_error_is_value_error() -> None:
    """ConfigurationError is a ValueError for FastMCP compatibility."""
    from mcp_server.exceptions import ConfigurationError

    exc = ConfigurationError("missing var")
    assert isinstance(exc, ValueError)
    assert str(exc) == "missing var"


def test_analysis_error_is_value_error() -> None:
    """AnalysisError is a ValueError for FastMCP compatibility."""
    from mcp_server.exceptions import AnalysisError

    exc = AnalysisError("empty response")
    assert isinstance(exc, ValueError)
    assert str(exc) == "empty response"


# Smoke test for tool registration
def test_all_tools_registered() -> None:
    """All 20 MCP tools are registered on the mcp object."""
    from mcp_server.server import mcp

    expected_tools: set[str] = {
        "tiktok_user_posts",
        "tiktok_trending",
        "tiktok_hashtag_posts",
        "tiktok_user_posts_api",
        "tiktok_user_posts_tikapi",
        "tiktok_user_posts_apify",
        "tiktok_trending_api",
        "tiktok_trending_tikapi",
        "tiktok_trending_apify",
        "tiktok_hashtag_api",
        "tiktok_hashtag_tikapi",
        "tiktok_hashtag_apify",
        "instagram_user_posts",
        "instagram_global_trending",
        "instagram_hashtag_trending",
        "generate_hashtags_tool",
        "facebook_page_posts",
        "facebook_hashtag_trending",
        "facebook_global_trending",
        "analyze_image",
    }

    registered_tools: set[str] = set(mcp._tool_manager._tools.keys())

    assert expected_tools == registered_tools, (
        f"Missing tools: {expected_tools - registered_tools}, "
        f"Extra tools: {registered_tools - expected_tools}"
    )


# Tests for facebook_hashtag_trending
async def test_facebook_hashtag_trending_success() -> None:
    """facebook_hashtag_trending returns JSON string with post data on success."""
    from mcp_server.server import facebook_hashtag_trending
    from scrapers.facebook import FacebookPost

    now = int(time.time())
    mock_posts: list[FacebookPost] = [
        FacebookPost(
            text="Summer vibes post",
            likes=800,
            time="May 7, 2026 at 3:00 PM",
            post_url="https://www.facebook.com/posts/summer001",
            image_url="https://scontent.example.com/img1.jpg",
            created_at=now - 86400,
        ),
        FacebookPost(
            text="Beach vibes post",
            likes=400,
            time="May 6, 2026 at 12:00 PM",
            post_url="https://www.facebook.com/posts/beach001",
            image_url="https://scontent.example.com/img2.jpg",
            created_at=now - 172800,
        ),
    ]
    with (
        patch(
            "mcp_server.server._scrape_facebook_hashtag",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await facebook_hashtag_trending("summer vibes", limit=10)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) <= 10
    assert all("post_url" in p for p in parsed)
    assert all("created_at" in p for p in parsed)
    likes = [p["likes"] for p in parsed]
    assert likes == sorted(likes, reverse=True)


async def test_facebook_hashtag_trending_missing_cookies() -> None:
    """facebook_hashtag_trending raises ConfigurationError when FB_COOKIES_FILE not set."""
    from mcp_server.server import facebook_hashtag_trending, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="FB_COOKIES_FILE environment variable is not set"
        ):
            await facebook_hashtag_trending("summer", limit=10)


async def test_facebook_hashtag_trending_invalid_limit() -> None:
    """facebook_hashtag_trending raises ValidationError for out-of-range limit."""
    from mcp_server.server import facebook_hashtag_trending, ValidationError

    with patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await facebook_hashtag_trending("summer", limit=0)
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await facebook_hashtag_trending("summer", limit=999)


# Tests for facebook_global_trending
async def test_facebook_global_trending_success() -> None:
    """facebook_global_trending returns deduped, sorted posts as JSON string."""
    from mcp_server.server import facebook_global_trending
    from scrapers.facebook import FacebookPost

    now = int(time.time())
    mock_posts: list[FacebookPost] = [
        FacebookPost(
            text="Viral post",
            likes=5000,
            time="May 7, 2026 at 3:00 PM",
            post_url="https://www.facebook.com/posts/viral001",
            image_url="https://scontent.example.com/viral.jpg",
            created_at=now - 86400,
        ),
        FacebookPost(
            text="Trending post",
            likes=3000,
            time="May 6, 2026 at 12:00 PM",
            post_url="https://www.facebook.com/posts/trending001",
            image_url="https://scontent.example.com/trending.jpg",
            created_at=now - 172800,
        ),
    ]
    with (
        patch(
            "mcp_server.server._scrape_facebook_trending",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await facebook_global_trending(limit=10)

    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) <= 10
    post_urls = [p["post_url"] for p in parsed]
    assert len(post_urls) == len(set(post_urls)), "Duplicate post_url found"
    likes = [p["likes"] for p in parsed]
    assert likes == sorted(likes, reverse=True)


async def test_facebook_global_trending_missing_cookies() -> None:
    """facebook_global_trending raises ConfigurationError when FB_COOKIES_FILE not set."""
    from mcp_server.server import facebook_global_trending, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError, match="FB_COOKIES_FILE environment variable is not set"
        ):
            await facebook_global_trending(limit=10)


async def test_facebook_global_trending_invalid_limit() -> None:
    """facebook_global_trending raises ValidationError for out-of-range limit."""
    from mcp_server.server import facebook_global_trending, ValidationError

    with patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}):
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await facebook_global_trending(limit=0)
        with pytest.raises(ValidationError, match="limit must be between 1 and 100"):
            await facebook_global_trending(limit=999)


async def test_facebook_page_posts_response_includes_created_at() -> None:
    """facebook_page_posts JSON response always includes created_at for every post."""
    from mcp_server.server import facebook_page_posts
    from scrapers.facebook import FacebookPost

    now = int(time.time())
    mock_posts: list[FacebookPost] = [
        FacebookPost(
            text="Post with timestamp",
            likes=100,
            time="May 7, 2026 at 3:00 PM",
            post_url="https://facebook.com/posts/ts001",
            image_url="",
            created_at=now - 3600,
        ),
        FacebookPost(
            text="Post with no timestamp",
            likes=0,
            time="",
            post_url="https://facebook.com/posts/ts002",
            image_url="",
            created_at=0,
        ),
    ]
    with (
        patch(
            "mcp_server.server._scrape_facebook_page",
            new_callable=AsyncMock,
            return_value=mock_posts,
        ),
        patch.dict("os.environ", {"FB_COOKIES_FILE": "/path/to/cookies.txt"}),
    ):
        result = await facebook_page_posts("testpage", limit=20)

    parsed = json.loads(result)
    assert all("created_at" in p for p in parsed), (
        "All posts in facebook_page_posts response must include created_at"
    )


def test_analyze_image_docstring_lists_correct_exceptions() -> None:
    """analyze_image docstring Raises section lists ValidationError, ConfigurationError, AnalysisError."""
    from mcp_server.server import analyze_image

    docstring = analyze_image.__doc__
    assert docstring is not None, "analyze_image should have a docstring"

    # Check that Raises section lists the correct exception types
    assert "ValidationError" in docstring, "Docstring should list ValidationError"
    assert "ConfigurationError" in docstring, "Docstring should list ConfigurationError"
    assert "AnalysisError" in docstring, "Docstring should list AnalysisError"

    # Verify the old incorrect ValueError is not in Raises section
    # (ValueError might still be mentioned as parent class, but not as a raised type)
    raises_section = (
        docstring.split("Raises:")[1].split("\n\n")[0] if "Raises:" in docstring else ""
    )
    assert "ValueError:" not in raises_section, (
        "Raises section should not list ValueError as exception type"
    )
