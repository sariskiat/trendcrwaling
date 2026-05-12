# [ISSUE-048] Expose complete Instagram/Facebook mode tools in MCP

## Type
AFK

## Priority
infra

## Blocked by
- ISSUE-044
- ISSUE-045
- ISSUE-046

## Why
After per-platform logic is implemented, MCP must present a coherent, discoverable cross-platform API surface.

## Scope (vertical slice)
Add/finalize MCP tool registrations and handlers for all missing IG/FB mode endpoints and verify real response contract consistency.

## Acceptance Criteria
- MCP tool list includes: `instagram_user_posts`, `instagram_hashtag_trending`, `instagram_global_trending`, `facebook_page_posts`, `facebook_hashtag_trending`, `facebook_global_trending`.
- Each tool validates inputs, maps to scraper function, and returns JSON payloads with recency fields where defined.
- User-visible behavior: tools are discoverable in list and callable with expected arguments.
- TDD gate: failing tool-registration and dispatch tests first, then green (`uv run pytest tests/test_server.py`).

## Files to Create/Modify
- `mcp_server/server.py`
- `tests/test_server.py`
