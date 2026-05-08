# [ISSUE-022] Add try/finally for browser cleanup in Facebook scraper

**Type:** AFK
**Priority:** quick-win
**Blocked by:** nothing

---

## Summary

`scrapers/facebook.py` does not use `try/finally` to ensure `browser.close()` is called when `_extract_posts` raises an exception. TikTok and Instagram scrapers already have this pattern.

---

## Acceptance Criteria

- [ ] `scrape_page()` in `scrapers/facebook.py` wraps `_extract_posts` in `try/finally` with `browser.close()` in the finally block
- [ ] Add test: `browser.close()` is called even when `_extract_posts` raises
- [ ] All existing tests still pass
- [ ] **TDD gate:** failing test first

---

## Files to Create / Modify

| File | Action |
|---|---|
| `scrapers/facebook.py` | Add try/finally around _extract_posts |
| `tests/test_facebook.py` | Add browser-close-on-exception test |
