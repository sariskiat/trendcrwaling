# [ISSUE-032] Add scraper exception propagation tests

**Type:** AFK
**Priority:** warning
**Blocked by:** none

---

## Summary

No tests cover what happens when a scraper raises an exception (e.g. `TikTokScraperError`, `PlaywrightError`, network timeout). Currently tool functions have no try/except — exceptions propagate raw. Add at least one test per scraper verifying the behavior.

Also add a tool-registration smoke test verifying all 6 tools are registered on the `mcp` object.

---

## Acceptance Criteria

- [ ] Test: `tiktok_user_posts` when scraper raises `TikTokScraperError` → exception propagates
- [ ] Test: `instagram_user_posts` when scraper raises `InstagramScraperError` → exception propagates
- [ ] Test: `facebook_page_posts` when scraper raises `FacebookScraperError` → exception propagates
- [ ] Test: `analyze_image` when OpenAI raises → exception propagates
- [ ] Test: smoke test verifying all 6 tools registered on `mcp` object
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Review Findings Addressed

- W3: no scraper exception tests
- N3: add tool-registration smoke test

---

## Files to Modify

| File | Action |
|---|---|
| `tests/test_server.py` | Add scraper error tests + registration smoke test |
