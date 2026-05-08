# mcp_server/server.py
"""MCP stdio server exposing analyze_competitor to Claude."""

from __future__ import annotations

import asyncio
import json
import re
from typing import TypedDict, cast

from dotenv import load_dotenv
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from scrapers import FacebookPost, InstagramPost, TikTokPost
from scrapers import scrape_facebook, scrape_instagram, scrape_tiktok
from scrapers.tiktok import scrape_user as _scrape_tiktok_user
from scrapers.tiktok import scrape_trending as _scrape_tiktok_trending
from scrapers.tiktok import scrape_hashtag as _scrape_tiktok_hashtag

load_dotenv()

__all__ = ["CompetitorAnalysisResult", "handle_analyze_competitor", "UnknownToolError"]

_HANDLE_RE = re.compile(r"^[A-Za-z0-9_.]{1,64}$")
_VALID_PLATFORMS = {"tiktok", "instagram", "facebook"}


def _validate_handle(value: str, field: str) -> str:
    """Validate a social media handle/tag/page name.

    Raises ValueError if the value doesn't match the allowed pattern.
    """
    if not _HANDLE_RE.match(value):
        raise ValueError(
            f"Invalid {field}: must be 1-64 alphanumeric/underscore/dot characters"
        )
    return value


def _validate_limit(value: int) -> int:
    """Validate limit is within acceptable range."""
    if not 1 <= value <= 100:
        raise ValueError(f"limit must be between 1 and 100, got {value}")
    return value


app: Server = Server("sukishi-trend-research")


class CompetitorAnalysisResult(TypedDict, total=False):
    """Scraped posts keyed by platform name."""

    tiktok: list[TikTokPost]
    instagram: list[InstagramPost]
    facebook: list[FacebookPost]


class UnknownToolError(Exception):
    """Raised when an unrecognised MCP tool name is called."""


async def handle_analyze_competitor(
    name: str,
    platforms: list[str],
    limit: int = 20,
) -> CompetitorAnalysisResult:
    """Scrape competitor posts across specified platforms.

    Args:
        name: Competitor handle / page name (e.g. 'mk_suki').
        platforms: Subset of ['tiktok', 'instagram', 'facebook'].
        limit: Max posts per platform.

    Returns:
        CompetitorAnalysisResult keyed by platform with typed post lists.
    """
    results: CompetitorAnalysisResult = {}
    if "tiktok" in platforms:
        results["tiktok"] = await scrape_tiktok(name, limit)
    if "instagram" in platforms:
        results["instagram"] = await scrape_instagram(name, limit)
    if "facebook" in platforms:
        results["facebook"] = await scrape_facebook(name, limit)
    return results


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Return all tools this MCP server exposes."""
    return [
        types.Tool(
            name="analyze_competitor",
            description=(
                "Scrape recent posts from a competitor Thai buffet restaurant on TikTok, "
                "Instagram, and/or Facebook. Returns structured post data (URLs, captions, "
                "likes) for visual and content analysis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Competitor handle or page name (e.g. 'mk_suki')",
                    },
                    "platforms": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["tiktok", "instagram", "facebook"],
                        },
                        "description": "Platforms to scrape",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Max posts per platform",
                    },
                },
                "required": ["name", "platforms"],
            },
        ),
        types.Tool(
            name="scrape_tiktok_user",
            description="Scrape recent TikTok posts for a given username. Returns structured post data (URLs, captions, likes, views, thumbnails).",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "TikTok handle without @",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Max posts to return",
                    },
                },
                "required": ["username"],
            },
        ),
        types.Tool(
            name="scrape_tiktok_trending",
            description="Scrape trending TikTok posts from the Explore page. Returns structured post data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Max posts to return",
                    },
                },
            },
        ),
        types.Tool(
            name="scrape_tiktok_hashtag",
            description="Scrape TikTok posts for a specific hashtag. Returns structured post data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Hashtag without # (e.g. 'sukiyaki')",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Max posts to return",
                    },
                },
                "required": ["tag"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, object]) -> list[types.TextContent]:
    """Dispatch a tool call to the correct handler.

    Args:
        name: Tool name from the MCP request.
        arguments: Tool arguments from the MCP request.

    Returns:
        List containing a single TextContent with JSON result.

    Raises:
        UnknownToolError: If the tool name is not recognised.
    """
    if name not in {
        "analyze_competitor",
        "scrape_tiktok_user",
        "scrape_tiktok_trending",
        "scrape_tiktok_hashtag",
    }:
        raise UnknownToolError(f"Unknown tool: {name}")

    if name == "analyze_competitor":
        competitor_name: str = _validate_handle(str(arguments["name"]), "name")
        platforms: list[str] = [
            p for p in cast(list[str], arguments["platforms"]) if p in _VALID_PLATFORMS
        ]
        if not platforms:
            raise ValueError("No valid platforms specified")
        limit: int = _validate_limit(int(cast(int | str, arguments.get("limit", 20))))

        result: CompetitorAnalysisResult = await handle_analyze_competitor(
            competitor_name, platforms, limit
        )
        return [
            types.TextContent(
                type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]

    if name == "scrape_tiktok_user":
        username: str = _validate_handle(str(arguments["username"]), "username")
        limit: int = _validate_limit(int(cast(int | str, arguments.get("limit", 20))))
        posts: list[TikTokPost] = await _scrape_tiktok_user(username, limit)
        return [
            types.TextContent(
                type="text", text=json.dumps(posts, ensure_ascii=False, indent=2)
            )
        ]

    if name == "scrape_tiktok_trending":
        limit: int = _validate_limit(int(cast(int | str, arguments.get("limit", 20))))
        posts: list[TikTokPost] = await _scrape_tiktok_trending(limit)
        return [
            types.TextContent(
                type="text", text=json.dumps(posts, ensure_ascii=False, indent=2)
            )
        ]

    if name == "scrape_tiktok_hashtag":
        tag: str = _validate_handle(str(arguments["tag"]), "tag")
        limit: int = _validate_limit(int(cast(int | str, arguments.get("limit", 20))))
        posts: list[TikTokPost] = await _scrape_tiktok_hashtag(tag, limit)
        return [
            types.TextContent(
                type="text", text=json.dumps(posts, ensure_ascii=False, indent=2)
            )
        ]

    raise UnknownToolError(f"Unknown tool: {name}")


async def main() -> None:
    """Run the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
