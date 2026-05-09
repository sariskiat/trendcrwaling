# [ISSUE-024] Add remaining TikTok tools to FastMCP server

**Type:** AFK
**Priority:** infra
**Blocked by:** ISSUE-023

---

## Summary

Register `tiktok_trending` and `tiktok_hashtag_posts` tools on the FastMCP server. Same pattern as `tiktok_user_posts`: typed params, validation, MCP error responses, `readOnlyHint=True`.

---

## Acceptance Criteria

- [ ] `tiktok_trending(limit: int = 20)` tool registered and working
- [ ] `tiktok_hashtag_posts(tag: str, limit: int = 20)` tool registered and working
- [ ] Invalid `tag` returns MCP error response
- [ ] Invalid `limit` returns MCP error response
- [ ] Missing `TT_COOKIES_FILE` returns MCP error response with actionable message
- [ ] Both tools annotated `readOnlyHint=True`
- [ ] Tests: success case + bad-input error + missing-cookies error for each tool
- [ ] **TDD gate:** failing test first
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Out of Scope

- Instagram/Facebook tools (separate issues)
- Scraper implementation changes

---

## Files to Create / Modify

| File | Action |
|---|---|
| `mcp_server/server.py` | Add `tiktok_trending`, `tiktok_hashtag_posts` tools |
| `tests/test_server.py` | Add tests for both tools |
