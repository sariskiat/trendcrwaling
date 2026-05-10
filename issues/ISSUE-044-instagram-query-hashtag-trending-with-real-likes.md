# [ISSUE-044] Add Instagram query hashtag trending with real likes

## Type
AFK

## Priority
infra

## Blocked by
- Ship Instagram global trending tracer bullet
- Create LLM hashtag generator module

## Why
Mode 2 needs query->hashtags expansion and ranking by real engagement, not placeholder likes.

## Scope (vertical slice)
Generate 10 hashtags from freeform query, scrape IG hashtag pages, include Reels and posts, enrich with detail-page like counts, filter <=10 days, return top 10 in MCP.

## Acceptance Criteria
- MCP tool `instagram_hashtag_trending(query, limit=10)` is available and callable.
- Hashtags are generated via `generate_hashtags(query, platform="instagram")` (10 tags target).
- Scraper includes both `/p/` and `/reel/` URLs.
- For Mode 2 responses, likes come from detail-page scrape and are non-placeholder when available.
- Results are deduped by `post_url`, filtered to <=10 days (when `created_at>0`), and sorted by likes desc.
- User-visible behavior: calling MCP tool with a query returns ranked post JSON.
- TDD gate: failing tests first for hashtag generation wiring, likes enrichment, recency/ranking, and MCP exposure; then green (`uv run pytest tests/test_instagram.py tests/test_hashtag_generator.py tests/test_server.py`).

## Files to Create/Modify
- `scrapers/hashtag_generator.py`
- `scrapers/instagram.py`
- `mcp_server/server.py`
- `tests/test_instagram.py`
- `tests/test_hashtag_generator.py`
- `tests/test_server.py`
