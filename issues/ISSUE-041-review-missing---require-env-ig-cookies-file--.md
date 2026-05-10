# [ISSUE-041] Review violation: Missing `_require_env(IG_COOKIES_FILE, ...)` call. Every other cookie-dependent tool (instagram_user_posts, facebook_page_posts, tiktok_user_posts) calls _require_env before dispatching to the scraper. Without it, a missing IG_COOKIES_FILE produces a confusing scraper-level error instead of an actionable MCP error response.

**Type:** AFK
**Source:** Auto-created by reviewer — iteration 1, from ISSUE-043-instagram-global-trending-tracer-bullet.md

## Problem

File: `mcp_server/server.py` (line 96)

Missing `_require_env(IG_COOKIES_FILE, ...)` call. Every other cookie-dependent tool (instagram_user_posts, facebook_page_posts, tiktok_user_posts) calls _require_env before dispatching to the scraper. Without it, a missing IG_COOKIES_FILE produces a confusing scraper-level error instead of an actionable MCP error response.

## Acceptance Criteria

- [ ] Violation fixed in `mcp_server/server.py`
- [ ] `uv run ruff check .` passes
- [ ] `uv run pyright` passes
- [ ] `uv run pytest -x` passes

## Files to Modify

- `mcp_server/server.py`
