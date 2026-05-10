# [ISSUE-046] Enforce TikTok API three-mode recency contract end-to-end

## Type
AFK

## Priority
infra

## Blocked by
- Ship Instagram global trending tracer bullet

## Why
TikTok mode coverage exists, but this issue locks contract behavior (<=10 days) across scraper, MCP, and tests so all platforms share the same recency guarantee.

## Scope (vertical slice)
Ensure user/trending/hashtag TikTok-Api paths all return only <=10-day posts with consistent shape through MCP tools.

## Acceptance Criteria
- `scrape_user`, `scrape_trending`, `scrape_hashtag` in TikTok-Api path consistently apply `max_age_days=10` filter.
- MCP tools `tiktok_user_posts_api`, `tiktok_trending_api`, `tiktok_hashtag_api` expose consistent contract and return JSON with `created_at`.
- User-visible behavior: all three TikTok-Api mode calls return only recent posts in real smoke run.
- TDD gate: add/adjust failing recency tests first, then green (`uv run pytest tests/test_tiktok_api.py tests/test_server.py`).

## Files to Create/Modify
- `scrapers/tiktok_api.py`
- `mcp_server/server.py`
- `tests/test_tiktok_api.py`
- `tests/test_server.py`
