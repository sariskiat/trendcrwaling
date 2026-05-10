# [ISSUE-043] Ship Instagram global trending tracer bullet

## Type
AFK

## Priority
tracer-bullet

## Blocked by
nothing

## Why
Deliver the thinnest complete end-to-end slice for the new 3-mode architecture: scrape -> rank/filter -> MCP tool -> user-visible response.

## Scope (vertical slice)
Implement Instagram global trending from `#trending` + `#viral`, dedupe by `post_url`, enforce <=10 days, and return JSON through MCP.

## Acceptance Criteria
- Given valid `IG_COOKIES_FILE`, MCP tool `instagram_global_trending(limit)` returns up to `limit` posts with keys `post_url`, `url`, `caption`, `likes`, `created_at`.
- Returned posts are deduplicated by `post_url` and sorted by likes desc (fallback created_at desc).
- All returned posts satisfy `now - created_at <= 864000` when `created_at > 0`.
- User-visible behavior: tool appears in MCP tool list and can be called directly with a real query.
- TDD gate: start with failing tests for scraper + MCP endpoint, then implement until tests pass (`uv run pytest tests/test_instagram.py tests/test_server.py`).

## Files to Create/Modify
- `scrapers/instagram.py`
- `mcp_server/server.py`
- `tests/test_instagram.py`
- `tests/test_server.py`
