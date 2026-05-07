# [ISSUE-014] Add type annotations to module-level constants in scrapers/instagram.py

**Type:** `AFK`
**Priority:** `bug`
**Blocked by:** none
**Blocks:** none
**Module(s):** `scrapers/`

---

## Context

In `scrapers/instagram.py`, three module-level constants lack explicit `str` type annotations, violating the CLAUDE.md hard gate "Every variable is typed." The fourth constant `_EXTRACT_JS` on line 23 is correctly annotated as `str`, making the omission inconsistent.

Untyped constants (lines 16–22):
```python
_COOKIE_ENV = "IG_COOKIES_FILE"
_POST_LINK_SELECTOR = "a[href*='/p/']"
_USER_AGENT = (
    "Mozilla/5.0 ..."
)
```

## What to build

In `scrapers/instagram.py`, add `: str` annotations to `_COOKIE_ENV`, `_POST_LINK_SELECTOR`, and `_USER_AGENT`:

```python
_COOKIE_ENV: str = "IG_COOKIES_FILE"
_POST_LINK_SELECTOR: str = "a[href*='/p/']"
_USER_AGENT: str = (
    "Mozilla/5.0 ..."
)
```

No logic changes. No new tests required — existing tests provide sufficient coverage of these constants.

## Acceptance criteria

- [ ] `_COOKIE_ENV`, `_POST_LINK_SELECTOR`, `_USER_AGENT` each have `: str` annotation
- [ ] `ruff .` passes
- [ ] `black --check .` passes
- [ ] `pytest -x --cov` passes

## Out of scope

- Not in this issue: fixing the same pattern in `scrapers/facebook.py`

## Notes

Flagged in PR #1 review comment: https://github.com/sariskiat/trendcrwaling/pull/1#issuecomment-4396246776
