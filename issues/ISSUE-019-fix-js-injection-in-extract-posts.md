# [ISSUE-019] Fix JS injection via author param in _extract_posts

**Type:** AFK
**Priority:** bug
**Blocked by:** nothing

---

## Summary

`_extract_posts()` in `scrapers/tiktok.py` interpolates the `author` parameter directly into a JavaScript string executed by `page.evaluate()`. A crafted username can break out of the JS string and execute arbitrary code in the browser context — which has session cookies loaded.

The same pattern exists in `scrapers/instagram.py` and `scrapers/facebook.py` if they interpolate user input into JS eval strings.

---

## Acceptance Criteria

- [ ] `_extract_posts()` in `scrapers/tiktok.py` does NOT interpolate `author` into the JS string
- [ ] Instead, `author` is assigned in Python after `pg.evaluate()` returns
- [ ] Audit `scrapers/instagram.py` and `scrapers/facebook.py` for the same pattern — fix if found
- [ ] Add a test: username containing `"` and JS code does not cause injection
- [ ] All existing tests still pass
- [ ] **TDD gate:** failing test first

---

## Files to Create / Modify

| File | Action |
|---|---|
| `scrapers/tiktok.py` | Fix `_extract_posts` — remove author from JS, assign in Python |
| `scrapers/instagram.py` | Audit and fix if same pattern exists |
| `scrapers/facebook.py` | Audit and fix if same pattern exists |
| `tests/test_tiktok.py` | Add JS injection regression test |
