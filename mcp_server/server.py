# mcp_server/server.py
"""MCP stdio server exposing analyze_competitor to Claude."""
from __future__ import annotations

import asyncio
import json
import os
from typing import TypedDict

from dotenv import load_dotenv
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from scrapers import FacebookPost, InstagramPost, TikTokPost
from scrapers import scrape_facebook, scrape_instagram, scrape_tiktok

load_dotenv()

__all__ = ["CompetitorAnalysisResult", "handle_analyze_competitor", "UnknownToolError"]

_IG_SESSION_FILE: str = os.getenv("IG_SESSION_FILE", "ig_session.json")

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
        results["instagram"] = scrape_instagram(name, _IG_SESSION_FILE, limit)
    if "facebook" in platforms:
        results["facebook"] = scrape_facebook(name, limit)
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
                        "items": {"type": "string", "enum": ["tiktok", "instagram", "facebook"]},
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
        )
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
    if name != "analyze_competitor":
        raise UnknownToolError(f"Unknown tool: {name}")

    competitor_name: str = str(arguments["name"])
    platforms: list[str] = list(arguments["platforms"])  # type: ignore[arg-type]
    limit: int = int(arguments.get("limit", 20))  # type: ignore[arg-type]

    result: CompetitorAnalysisResult = await handle_analyze_competitor(
        competitor_name, platforms, limit
    )
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def main() -> None:
    """Run the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
