# [ISSUE-015] Add BrowserContext type annotation to ctx in _setup_browser

**Type:** `AFK`
**Priority:** `bug`
**Blocked by:** none
**Blocks:** none
**Module(s):** `scrapers/`

---

## Context

In `scrapers/instagram.py`, `_setup_browser` has `browser: Browser` and `pg: Page` correctly annotated, but `ctx` at line 94 is untyped:

```python
browser: Browser = await pw.chromium.launch(headless=True)
ctx = await browser.new_context(...)   # missing type annotation
pg: Page = await ctx.new_page()
```

`BrowserContext` is the correct type from `playwright.async_api` but is not currently imported. Violates CLAUDE.md hard gate "Every variable is typed."

## What to build

1. Add `BrowserContext` to the import from `playwright.async_api` in `scrapers/instagram.py` (line 12).
2. Annotate `ctx` as `BrowserContext`:
   ```python
   ctx: BrowserContext = await browser.new_context(...)
   ```

No logic changes. No new tests required.

## Acceptance criteria

- [ ] `BrowserContext` imported from `playwright.async_api`
- [ ] `ctx` annotated as `BrowserContext` at line 94
- [ ] `ruff .` passes
- [ ] `black --check .` passes
- [ ] `pytest -x --cov` passes

## Out of scope

- Not in this issue: any other typing fixes in `_setup_browser`

## Notes

Flagged in PR #1 review comment: https://github.com/sariskiat/trendcrwaling/pull/1#issuecomment-4396246776
