# [ISSUE-013] Close browser on exception path in scrape_user

**Type:** `AFK`
**Priority:** `bug`
**Blocked by:** none
**Blocks:** none
**Module(s):** `scrapers/`

---

## Context

In `scrapers/instagram.py`, `scrape_user` calls `await browser.close()` only on the happy path (line 147). If `_extract_posts` raises any exception, both the `except InstagramScraperError` and `except Exception` handlers re-raise without closing the browser, leaking a Chromium process. The `async with async_playwright()` context manager closes the Playwright instance but does NOT close the browser.

## What to build

In `scrapers/instagram.py`, wrap `browser.close()` in a `try/finally` so it executes on all exit paths from the `async with async_playwright()` block.

Current code (lines 144–156):
```python
async with async_playwright() as pw:
    browser, pg = await _setup_browser(pw, cookie_path, username)
    raw: list[dict[str, str]] = await _extract_posts(pg)
    await browser.close()
    return [...]
```

Target pattern:
```python
async with async_playwright() as pw:
    browser, pg = await _setup_browser(pw, cookie_path, username)
    try:
        raw: list[dict[str, str]] = await _extract_posts(pg)
        return [...]
    finally:
        await browser.close()
```

## Acceptance criteria

- [ ] Failing test written **before** any implementation (TDD — non-negotiable)
- [ ] Test verifies `browser.close()` is called even when `_extract_posts` raises
- [ ] Implementation makes the test pass
- [ ] `ruff .` passes
- [ ] `black --check .` passes
- [ ] `pytest -x --cov` passes
- [ ] No new `try` block body exceeds 5 lines

## Out of scope

- Not in this issue: fixing the same pattern in `scrapers/facebook.py` (pre-existing, separate issue if needed)

## Notes

Flagged in PR #1 review comment: https://github.com/sariskiat/trendcrwaling/pull/1#issuecomment-4396246776
