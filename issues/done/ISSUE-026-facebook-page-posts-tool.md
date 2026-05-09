# [ISSUE-026] Add facebook_page_posts tool to FastMCP server

**Type:** AFK
**Priority:** infra
**Blocked by:** ISSUE-023

---

## Summary

Register `facebook_page_posts` tool on the FastMCP server. Wraps `scrapers.facebook.scrape_page()`. Typed params, validation, MCP error responses, `readOnlyHint=True`.

---

## Acceptance Criteria

- [ ] `facebook_page_posts(page_name: str, limit: int = 20)` tool registered and working
- [ ] Invalid `page_name` returns MCP error response
- [ ] Invalid `limit` returns MCP error response
- [ ] Missing `FB_COOKIES_FILE` returns MCP error response with actionable message
- [ ] Tool annotated `readOnlyHint=True`
- [ ] Tests: success case + bad-input error + missing-cookies error
- [ ] **TDD gate:** failing test first
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Out of Scope

- `facebook_recent_posts` (scraper doesn't exist yet)
- Scraper implementation changes

---

## Files to Create / Modify

| File | Action |
|---|---|
| `mcp_server/server.py` | Add `facebook_page_posts` tool |
| `tests/test_server.py` | Add tests for facebook tool |
