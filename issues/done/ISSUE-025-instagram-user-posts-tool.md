# [ISSUE-025] Add instagram_user_posts tool to FastMCP server

**Type:** AFK
**Priority:** infra
**Blocked by:** ISSUE-023

---

## Summary

Register `instagram_user_posts` tool on the FastMCP server. Wraps `scrapers.instagram.scrape_user()`. Typed params, validation, MCP error responses, `readOnlyHint=True`.

---

## Acceptance Criteria

- [ ] `instagram_user_posts(username: str, limit: int = 20)` tool registered and working
- [ ] Invalid `username` returns MCP error response
- [ ] Invalid `limit` returns MCP error response
- [ ] Missing `IG_COOKIES_FILE` returns MCP error response with actionable message
- [ ] Tool annotated `readOnlyHint=True`
- [ ] Tests: success case + bad-input error + missing-cookies error
- [ ] **TDD gate:** failing test first
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Out of Scope

- `instagram_recent_posts` (scraper doesn't exist yet)
- Scraper implementation changes

---

## Files to Create / Modify

| File | Action |
|---|---|
| `mcp_server/server.py` | Add `instagram_user_posts` tool |
| `tests/test_server.py` | Add tests for instagram tool |
