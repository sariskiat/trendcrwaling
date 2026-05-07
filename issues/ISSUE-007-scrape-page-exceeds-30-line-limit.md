# [ISSUE-007] Split `scrape_page` — exceeds 30-line function limit

**Type:** `AFK`
**Priority:** `bug`
**Blocked by:** none
**Blocks:** none
**Module(s):** `scrapers/`

---

## Context

`scrape_page` in `scrapers/facebook.py` (lines 58–147) is 90 lines — three times the 30-line max. The function does browser setup, scrolling, DOM extraction, and result mapping in a single body.

## What to build

Refactor `scrapers/facebook.py` by extracting two private helpers. The public interface (`scrape_page` signature and return type) must not change.

Suggested split:

1. `async def _setup_browser(pw, cookie_path)` — launches browser, creates context, injects cookies if present. Returns `(browser, page)`.
2. `async def _extract_posts(page) -> list[dict[str, str]]` — scrolls the page and evaluates the DOM extraction JS. Returns the raw list of dicts.

`scrape_page` then becomes: validate limit → get cookie path → call `_setup_browser` → call `_extract_posts` → map to `FacebookPost` → close browser. Each function must stay under 30 lines.

All three functions must be fully type-annotated. Private helpers are `_prefixed` and not added to `__all__`.

## Acceptance criteria

- [ ] Failing test written **before** any implementation (TDD — non-negotiable)
- [ ] `scrape_page`, `_setup_browser`, `_extract_posts` each under 30 lines
- [ ] Public interface (`scrape_page` signature, `__all__`) unchanged
- [ ] `ruff .` passes
- [ ] `pytest -x` passes (existing tests must all still pass)

## Out of scope

No changes to test mocking strategy — existing mock structure in `test_facebook.py` should still work without modification.

## Notes

The existing tests mock `async_playwright` at the module level, so extraction into private helpers is transparent to them as long as the helpers are called from within the same `async_playwright` context manager.
