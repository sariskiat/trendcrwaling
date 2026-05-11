# [ISSUE-047] Create reusable LLM hashtag generator module

## Type
AFK

## Priority
quick-win

## Blocked by
nothing

## Why
Mode 2 on multiple platforms depends on one shared query->hashtag component.

## Scope (vertical slice)
Implement `generate_hashtags(query: str, platform: str) -> list[str]` with OpenAI-backed generation, validation/normalization, and user-visible failures through MCP callers.

## Acceptance Criteria
- `generate_hashtags` returns exactly 10 normalized hashtags for a valid query (no `#`, lowercase, unique).
- Missing `OPENAI_API_KEY` raises actionable configuration error text.
- Empty/invalid LLM output is handled with deterministic fallback behavior or explicit error.
- User-visible behavior: when called through IG/FB Mode 2 tools, hashtags drive scraping inputs.
- TDD gate: tests first for success, normalization, and error paths, then green (`uv run pytest tests/test_hashtag_generator.py`).

## Files to Create/Modify
- `scrapers/hashtag_generator.py`
- `tests/test_hashtag_generator.py`
- `mcp_server/server.py`
