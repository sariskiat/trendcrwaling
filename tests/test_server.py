# tests/test_server.py
"""Tests for the FastMCP-based MCP server."""

from __future__ import annotations

import json
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
    """All 21 MCP tools are registered on the mcp object."""
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
        "facebook_page_posts",
        "analyze_image",
    }

    registered_tools: set[str] = set(mcp._tool_manager._tools.keys())

    assert expected_tools == registered_tools, (
        f"Missing tools: {expected_tools - registered_tools}, "
        f"Extra tools: {registered_tools - expected_tools}"
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
    assert (
        "ValueError:" not in raises_section
    ), "Raises section should not list ValueError as exception type"
