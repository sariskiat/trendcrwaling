# [ISSUE-017] Add scrape_trending entry point and scrape_tiktok_trending MCP tool

**Type:** AFK
**Priority:** quick-win
**Blocked by:** ISSUE-016

---

## Summary

Add a `scrape_trending(limit)` function to `scrapers/tiktok.py` that navigates TikTok's Explore/trending page and extracts posts using the Playwright infrastructure established in ISSUE-016. Expose it as a dedicated `scrape_tiktok_trending` MCP tool. Export from `scrapers/__init__.py`.

---

## Acceptance Criteria

- [ ] `scrape_trending(limit: int = 20)` added to `scrapers/tiktok.py`
- [ ] Navigates TikTok trending/explore page, extracts `TikTokPost` dicts
- [ ] Reuses `_setup_browser`, `_load_cookies`, and `TikTokScraperError` from ISSUE-016
- [ ] `scrape_tiktok_trending` MCP tool registered in `mcp_server/server.py` with `limit` param
- [ ] `scrape_trending` exported from `scrapers/__init__.py`
- [ ] `tests/test_tiktok.py` — tests for scrape_trending: happy path, limit, error
- [ ] `tests/test_server.py` — test for `scrape_tiktok_trending` MCP tool dispatch
- [ ] **TDD gate:** failing tests written before implementation code

---

## Files to Create / Modify

| File | Action |
|---|---|
| `scrapers/tiktok.py` | Modify — add `scrape_trending` function |
| `scrapers/__init__.py` | Modify — export `scrape_trending` |
| `mcp_server/server.py` | Modify — add `scrape_tiktok_trending` tool definition + handler |
| `tests/test_tiktok.py` | Modify — add scrape_trending tests |
| `tests/test_server.py` | Modify — add scrape_tiktok_trending dispatch test |
