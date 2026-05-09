# mcp_server/server.py
"""MCP stdio server using FastMCP decorator pattern."""

from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Final

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from mcp_server.exceptions import (
    MCPServerError,
    ValidationError,
    ConfigurationError,
    AnalysisError,
)
from mcp_server.image_analysis import analyze_image_with_vision
from scrapers.tiktok import TikTokPost, scrape_user as _scrape_tiktok_user
from scrapers.tiktok import scrape_trending as _scrape_tiktok_trending
from scrapers.tiktok import scrape_hashtag as _scrape_tiktok_hashtag
from scrapers.tiktok_api import TikTokApiPost, scrape_user as _scrape_tiktok_api_user
from scrapers.tiktok_api import scrape_trending as _scrape_tiktok_api_trending
from scrapers.tiktok_api import scrape_hashtag as _scrape_tiktok_api_hashtag
from scrapers.tiktok_tikapi import TikApiPost, scrape_user as _scrape_tikapi_user
from scrapers.tiktok_tikapi import scrape_trending as _scrape_tikapi_trending
from scrapers.tiktok_tikapi import scrape_hashtag as _scrape_tikapi_hashtag
from scrapers.tiktok_apify import ApifyTikTokPost, scrape_user as _scrape_apify_user
from scrapers.tiktok_apify import scrape_trending as _scrape_apify_trending
from scrapers.tiktok_apify import scrape_hashtag as _scrape_apify_hashtag
from scrapers.instagram import InstagramPost, scrape_user as _scrape_instagram_user
from scrapers.facebook import FacebookPost, scrape_page as _scrape_facebook_page

__all__ = [
    "mcp",
    "MCPServerError",
    "ValidationError",
    "ConfigurationError",
    "AnalysisError",
]

_HANDLE_RE: re.Pattern[str] = re.compile(r"^[A-Za-z0-9_.]{1,64}$")

TT_COOKIES_FILE: Final[str] = "TT_COOKIES_FILE"
IG_COOKIES_FILE: Final[str] = "IG_COOKIES_FILE"
FB_COOKIES_FILE: Final[str] = "FB_COOKIES_FILE"


def _require_env(name: str, label: str) -> str:
    """Return the env var `name` or raise ConfigurationError with actionable message."""
    value = os.getenv(name, "")
    if not value:
        raise ConfigurationError(
            f"{name} environment variable is not set. Export it to {label}"
        )
    return value


def _validate_handle(value: str, field: str) -> str:
    """Validate a social media handle/username.

    Raises ValidationError if the value doesn't match the allowed pattern.
    """
    if not _HANDLE_RE.match(value):
        raise ValidationError(
            f"Invalid {field}: must be 1-64 alphanumeric/underscore/dot characters"
        )
    return value


def _validate_limit(value: int) -> int:
    """Validate limit is within acceptable range.

    Raises:
        ValidationError: If `value` is not between 1 and 100 inclusive.
    """
    if not 1 <= value <= 100:
        raise ValidationError(f"limit must be between 1 and 100, got {value}")
    return value


mcp = FastMCP("sukishi-trend-research")


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_user_posts(username: str, limit: int = 20) -> str:
    """Scrape recent TikTok posts for a given username using Playwright.

    Free, but requires browser cookies exported from TikTok.
    Uses headless Chrome/Playwright to scrape posts.

    Requires TT_COOKIES_FILE environment variable pointing to a
    Netscape-format cookies.txt file exported from your browser.

    Returns structured post data (URLs, captions, likes, views, thumbnails).
    """
    _validate_handle(username, "username")
    _validate_limit(limit)

    _require_env(TT_COOKIES_FILE, "a path containing your TikTok cookies.txt file.")

    posts: list[TikTokPost] = await _scrape_tiktok_user(username, limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_trending(limit: int = 20) -> str:
    """Scrape trending TikTok posts using Playwright.

    Free, but requires browser cookies exported from TikTok.
    Uses headless Chrome/Playwright to scrape trending posts.

    Requires TT_COOKIES_FILE environment variable pointing to a
    Netscape-format cookies.txt file exported from your browser.
    """
    _validate_limit(limit)

    _require_env(TT_COOKIES_FILE, "a path containing your TikTok cookies.txt file.")

    posts: list[TikTokPost] = await _scrape_tiktok_trending(limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_hashtag_posts(tag: str, limit: int = 20) -> str:
    """Scrape TikTok posts for a given hashtag using Playwright.

    Free, but requires browser cookies exported from TikTok.
    Uses headless Chrome/Playwright to scrape hashtag posts.

    Requires TT_COOKIES_FILE environment variable pointing to a
    Netscape-format cookies.txt file exported from your browser.
    """
    _validate_handle(tag, "tag")
    _validate_limit(limit)

    _require_env(TT_COOKIES_FILE, "a path containing your TikTok cookies.txt file.")

    posts: list[TikTokPost] = await _scrape_tiktok_hashtag(tag, limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_user_posts_api(
    username: str, limit: int = 20, days_back: int | None = None, timeout: int = 300
) -> str:
    """Scrape TikTok posts for a user using TikTok-Api library (free, unofficial).

    Uses the davidteather/TikTokApi library. Free but may hit rate limits.
    Set TIKTOK_SOURCE=api to use this source.

    Requires TT_MS_TOKEN environment variable to be set.

    Returns posts ≤ 10 days old.

    Args:
        username: TikTok handle without @.
        limit: Max number of posts to return.
        days_back: Only return posts from last N days. None = no filter.
        timeout: Request timeout in seconds. Default 300 (5 minutes).
    """
    _validate_handle(username, "username")
    _validate_limit(limit)

    posts: list[TikTokApiPost] = await _scrape_tiktok_api_user(
        username, limit, days_back, timeout, max_age_days=10
    )
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_user_posts_tikapi(username: str, limit: int = 20) -> str:
    """Scrape TikTok posts for a user using TikAPI.io managed API (paid).

    Reliable managed API service. Set TIKTOK_SOURCE=tikapi to use this source.

    Requires TIKAPI_KEY environment variable (get one at tikapi.io).
    Pricing: Pay-per-request based on TikAPI.io pricing tiers.
    """
    _validate_handle(username, "username")
    _validate_limit(limit)

    posts: list[TikApiPost] = await _scrape_tikapi_user(username, limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_user_posts_apify(username: str, limit: int = 20) -> str:
    """Scrape TikTok posts for a user using Apify Clockworks managed API (pay-per-result).

    98% success rate. Set TIKTOK_SOURCE=apify to use this source.

    Requires APIFY_TOKEN environment variable (get one at apify.com).
    Pricing: Pay-per-result based on Apify Clockworks actor pricing.
    """
    _validate_handle(username, "username")
    _validate_limit(limit)

    posts: list[ApifyTikTokPost] = await _scrape_apify_user(username, limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_trending_api(
    limit: int = 20, days_back: int | None = None, timeout: int = 300
) -> str:
    """Scrape trending TikTok posts using TikTok-Api library (free, unofficial).

    Uses the davidteather/TikTokApi library. Free but may hit rate limits.
    Set TIKTOK_SOURCE=api to use this source.

    Requires TT_MS_TOKEN environment variable to be set.

    Returns posts ≤ 10 days old.

    Args:
        limit: Max number of posts to return.
        days_back: Only return posts from last N days. None = no filter.
        timeout: Request timeout in seconds. Default 300 (5 minutes).
    """
    _validate_limit(limit)

    posts: list[TikTokApiPost] = await _scrape_tiktok_api_trending(
        limit, days_back, timeout, max_age_days=10
    )
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_trending_tikapi(limit: int = 20) -> str:
    """Scrape trending TikTok posts using TikAPI.io managed API (paid).

    Reliable managed API service. Set TIKTOK_SOURCE=tikapi to use this source.

    Requires TIKAPI_KEY environment variable (get one at tikapi.io).
    Pricing: Pay-per-request based on TikAPI.io pricing tiers.

    Note: This endpoint is not implemented as TikAPI.io does not provide
    a documented trending endpoint. Raises NotImplementedError.
    """
    _validate_limit(limit)

    posts: list[TikApiPost] = await _scrape_tikapi_trending(limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_trending_apify(limit: int = 20) -> str:
    """Scrape trending TikTok posts using Apify Clockworks managed API (pay-per-result).

    98% success rate. Set TIKTOK_SOURCE=apify to use this source.

    Requires APIFY_TOKEN environment variable (get one at apify.com).
    Pricing: Pay-per-result based on Apify Clockworks actor pricing.

    Note: This endpoint is not implemented as Apify Clockworks does not provide
    a trending actor. Raises NotImplementedError.
    """
    _validate_limit(limit)

    posts: list[ApifyTikTokPost] = await _scrape_apify_trending(limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_hashtag_api(
    tag: str, limit: int = 20, days_back: int | None = None, timeout: int = 300
) -> str:
    """Scrape TikTok posts for a hashtag using TikTok-Api library (free, unofficial).

    Uses the davidteather/TikTokApi library. Free but may hit rate limits.
    Set TIKTOK_SOURCE=api to use this source.

    Requires TT_MS_TOKEN environment variable to be set.

    Returns posts ≤ 10 days old.

    Args:
        tag: Hashtag to search for (without #).
        limit: Max number of posts to return.
        days_back: Only return posts from last N days. None = no filter.
        timeout: Request timeout in seconds. Default 300 (5 minutes).
    """
    _validate_handle(tag, "tag")
    _validate_limit(limit)

    posts: list[TikTokApiPost] = await _scrape_tiktok_api_hashtag(
        tag, limit, days_back, timeout, max_age_days=10
    )
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_hashtag_tikapi(tag: str, limit: int = 20) -> str:
    """Scrape TikTok posts for a hashtag using TikAPI.io managed API (paid).

    Reliable managed API service. Set TIKTOK_SOURCE=tikapi to use this source.

    Requires TIKAPI_KEY environment variable (get one at tikapi.io).
    Pricing: Pay-per-request based on TikAPI.io pricing tiers.

    Note: This endpoint is not implemented as TikAPI.io does not provide
    a documented hashtag endpoint. Raises NotImplementedError.
    """
    _validate_handle(tag, "tag")
    _validate_limit(limit)

    posts: list[TikApiPost] = await _scrape_tikapi_hashtag(tag, limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def tiktok_hashtag_apify(tag: str, limit: int = 20) -> str:
    """Scrape TikTok posts for a hashtag using Apify Clockworks managed API (pay-per-result).

    98% success rate. Set TIKTOK_SOURCE=apify to use this source.

    Requires APIFY_TOKEN environment variable (get one at apify.com).
    Pricing: Pay-per-result based on Apify Clockworks actor pricing.

    Note: This endpoint is not implemented as Apify Clockworks does not provide
    a hashtag actor. Raises NotImplementedError.
    """
    _validate_handle(tag, "tag")
    _validate_limit(limit)

    posts: list[ApifyTikTokPost] = await _scrape_apify_hashtag(tag, limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def instagram_user_posts(username: str, limit: int = 20) -> str:
    """Scrape Instagram posts for a given user."""
    _validate_handle(username, "username")
    _validate_limit(limit)

    _require_env(IG_COOKIES_FILE, "a path containing your Instagram cookies.txt file.")

    posts: list[InstagramPost] = await _scrape_instagram_user(username, limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def facebook_page_posts(page_name: str, limit: int = 20) -> str:
    """Scrape Facebook posts from a public page."""
    _validate_handle(page_name, "page_name")
    _validate_limit(limit)

    _require_env(FB_COOKIES_FILE, "a path containing your Facebook cookies.txt file.")

    posts: list[FacebookPost] = await _scrape_facebook_page(page_name, limit)
    return json.dumps(posts, ensure_ascii=False, indent=2)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
async def analyze_image(
    image_url: str, prompt: str = "Describe this image in detail"
) -> str:
    """Analyze an image using OpenAI Vision API.

    Args:
        image_url: URL of the image to analyze.
        prompt: What to analyze about the image.

    Returns:
        Text description/analysis of the image.

    Raises:
        ValidationError: If `image_url` does not start with http:// or https://.
        ConfigurationError: If `OPENAI_API_KEY` environment variable is not set.
        AnalysisError: If the OpenAI Vision API returns an empty response.
    """
    if not image_url.startswith(("http://", "https://")):
        raise ValidationError("image_url must start with http:// or https://")

    api_key = _require_env("OPENAI_API_KEY", "your OpenAI API key for Vision")
    return await analyze_image_with_vision(image_url, prompt, api_key)


async def main() -> None:
    """Run the MCP server over stdio."""
    load_dotenv()
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
