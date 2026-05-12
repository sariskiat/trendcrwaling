# [ISSUE-045] Implement Facebook three modes with 10-day recency

## Type
AFK

## Priority
infra

## Blocked by
- ISSUE-043
- ISSUE-047

## Why
Facebook currently lacks a complete, tested three-mode surface with strict recency guarantees.

## Scope (vertical slice)
Implement/finish Mode 1 page posts, Mode 2 query hashtag trending, and Mode 3 global trending for Facebook with `created_at` parsing from `<abbr>`, 10-day filtering, ranking, and MCP tools.

## Acceptance Criteria
- MCP tools exist and are callable: `facebook_page_posts`, `facebook_hashtag_trending`, `facebook_global_trending`.
- All tool responses include `created_at` and filter out posts older than 10 days when timestamp parse succeeds.
- Mode 2 uses generated hashtags from freeform query and ranks top results by likes desc then recency.
- Mode 3 uses seeds `#trending` and `#viral`, dedupes by `post_url`, returns top `limit`.
- User-visible behavior: three Facebook modes are discoverable in tool list and return structured JSON.
- TDD gate: failing tests first for timestamp parse/recency filter/mode tools, then green (`uv run pytest tests/test_facebook.py tests/test_hashtag_generator.py tests/test_server.py`).

## Files to Create/Modify
- `scrapers/facebook.py`
- `scrapers/hashtag_generator.py`
- `mcp_server/server.py`
- `tests/test_facebook.py`
- `tests/test_hashtag_generator.py`
- `tests/test_server.py`
