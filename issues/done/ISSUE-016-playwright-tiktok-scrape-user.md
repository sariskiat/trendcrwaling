# [ISSUE-016] Replace tiktokapipy with Playwright for scrape_user + add scrape_tiktok_user MCP tool

**Type:** AFK
**Priority:** tracer-bullet
**Blocked by:** nothing

---

## Summary

Replace the `tiktokapipy` library with a Playwright headless browser scraper for `scrape_user`. Extend `TikTokPost` with `views`, `thumbnail_url`, and `author` fields. Expose `scrape_tiktok_user` as a dedicated MCP tool. Remove the `tiktokapipy` dependency from `pyproject.toml`. This is the thinnest vertical slice that proves the Playwright approach works end-to-end.

---

## Acceptance Criteria

- [ ] `scrapers/tiktok.py` uses Playwright (not `tiktokapipy`) to scrape a TikTok user's posts
- [ ] Cookie authentication via `TT_COOKIES_FILE` env var (Netscape cookies.txt format)
- [ ] `TikTokPost` TypedDict has fields: `url`, `desc`, `likes`, `views`, `thumbnail_url`, `author`
- [ ] `_setup_browser`, `_load_cookies` helpers follow the Instagram scraper pattern
- [ ] Wait strategy: `networkidle` + `wait_for_selector` with 15 s timeout
- [ ] All failures raise `TikTokScraperError` with a descriptive message
- [ ] `scrape_tiktok_user` MCP tool is registered in `mcp_server/server.py` with `username` and `limit` params
- [ ] Existing `analyze_competitor` flow still works (backward compatible — calls `scrape_tiktok` → `scrape_user`)
- [ ] `tiktokapipy` removed from `pyproject.toml` dependencies
- [ ] `tests/test_tiktok.py` rewritten: Playwright mocks replace `TikTokAPI` mocks; covers happy path, limit, invalid limit, error
- [ ] `tests/test_server.py` updated: `TikTokPost` construction includes new fields; new test for `scrape_tiktok_user` MCP tool dispatch
- [ ] **TDD gate:** failing tests written before implementation code

---

## Files to Create / Modify

| File | Action |
|---|---|
| `scrapers/tiktok.py` | Rewrite — remove tiktokapipy, implement Playwright scrape_user |
| `scrapers/__init__.py` | Update — ensure scrape_tiktok still maps to scrape_user |
| `mcp_server/server.py` | Modify — add `scrape_tiktok_user` tool definition + handler |
| `tests/test_tiktok.py` | Rewrite — Playwright mocks, all scrape_user tests |
| `tests/test_server.py` | Modify — update TikTokPost fields, add scrape_tiktok_user dispatch test |
| `pyproject.toml` | Modify — remove tiktokapipy from dependencies |
