# [ISSUE-021] Add input validation at MCP tool boundary and URL path sanitization

**Type:** AFK
**Priority:** infra
**Blocked by:** ISSUE-019

---

## Summary

MCP tool handlers in `mcp_server/server.py` pass user-supplied strings directly to scrapers with no validation. Usernames, tags, and page names are interpolated into URLs without sanitization. Add a shared validation function and apply it at the MCP handler level.

---

## Acceptance Criteria

- [ ] Shared `_validate_handle(value, field)` function that enforces `^[A-Za-z0-9_.]{1,64}$`
- [ ] All MCP handlers validate `username`, `tag`, `name` params before dispatching
- [ ] `limit` validated: `1 <= limit <= 100`
- [ ] `platforms` entries validated against `{"tiktok", "instagram", "facebook"}`
- [ ] Scraper functions (`scrape_user`, `scrape_trending`, `scrape_hashtag`, `scrape_page`) also validate their inputs
- [ ] Cookie file path validated with `os.path.realpath()` + `os.path.isfile()` in all three scrapers
- [ ] Tests for invalid handles, excessive limits, path traversal in cookie path
- [ ] **TDD gate:** failing tests first

---

## Files to Create / Modify

| File | Action |
|---|---|
| `mcp_server/server.py` | Add validation before dispatching to scrapers |
| `scrapers/tiktok.py` | Add handle validation, cookie path validation |
| `scrapers/instagram.py` | Add handle validation, cookie path validation |
| `scrapers/facebook.py` | Add handle validation, cookie path validation |
| `tests/test_server.py` | Add tests for invalid inputs |
| `tests/test_tiktok.py` | Add tests for invalid handles |
| `tests/test_instagram.py` | Add tests for invalid handles |
| `tests/test_facebook.py` | Add tests for invalid handles |
