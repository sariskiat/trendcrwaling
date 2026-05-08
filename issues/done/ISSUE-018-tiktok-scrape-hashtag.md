# [ISSUE-018] Add scrape_hashtag entry point and scrape_tiktok_hashtag MCP tool

**Type:** AFK
**Priority:** quick-win
**Blocked by:** ISSUE-016

---

## Summary

Add a `scrape_hashtag(tag, limit)` function to `scrapers/tiktok.py` that navigates TikTok's hashtag page (`/tag/{tag}`) and extracts posts using the Playwright infrastructure established in ISSUE-016. Expose it as a dedicated `scrape_tiktok_hashtag` MCP tool. Export from `scrapers/__init__.py`.

---

## Acceptance Criteria

- [ ] `scrape_hashtag(tag: str, limit: int = 20)` added to `scrapers/tiktok.py`
- [ ] Navigates `https://www.tiktok.com/tag/{tag}`, extracts `TikTokPost` dicts
- [ ] Reuses `_setup_browser`, `_load_cookies`, and `TikTokScraperError` from ISSUE-016
- [ ] `scrape_tiktok_hashtag` MCP tool registered in `mcp_server/server.py` with `tag` and `limit` params
- [ ] `scrape_hashtag` exported from `scrapers/__init__.py`
- [ ] `tests/test_tiktok.py` — tests for scrape_hashtag: happy path, limit, error, empty tag validation
- [ ] `tests/test_server.py` — test for `scrape_tiktok_hashtag` MCP tool dispatch
- [ ] **TDD gate:** failing tests written before implementation code

---

## Files to Create / Modify

| File | Action |
|---|---|
| `scrapers/tiktok.py` | Modify — add `scrape_hashtag` function |
| `scrapers/__init__.py` | Modify — export `scrape_hashtag` |
| `mcp_server/server.py` | Modify — add `scrape_tiktok_hashtag` tool definition + handler |
| `tests/test_tiktok.py` | Modify — add scrape_hashtag tests |
| `tests/test_server.py` | Modify — add scrape_tiktok_hashtag dispatch test |
