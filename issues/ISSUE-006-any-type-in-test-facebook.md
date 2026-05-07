# [ISSUE-006] Remove `Any` type from test_facebook.py

**Type:** `AFK`
**Priority:** `bug`
**Blocked by:** none
**Blocks:** none
**Module(s):** `tests/`

---

## Context

`Any` is banned by the coding standards. It appears in `tests/test_facebook.py` in the helper `_evaluate_side_effect`, hiding real type information from the type checker.

## What to build

In `tests/test_facebook.py`:

- Line 5: remove `from typing import Any`
- Line 37: change `def _evaluate_side_effect(js: Any) -> Any:` to use `object` for the parameter and `list[dict[str, str]] | None` for the return type

Exact change:
```python
# before
def _evaluate_side_effect(js: Any) -> Any:

# after
def _evaluate_side_effect(js: object) -> list[dict[str, str]] | None:
```

The function body already returns either `None` or `posts` (a `list[dict[str, str]]`), so the return type is accurate.

## Acceptance criteria

- [ ] Failing test written **before** any implementation (TDD — non-negotiable)
- [ ] Implementation makes the test pass
- [ ] `ruff .` passes
- [ ] `pytest -x` passes
- [ ] No `Any` import or annotation remains in `tests/test_facebook.py`

## Out of scope

No other files need changing for this issue.

## Notes

`object` is the correct replacement for `Any` on input parameters — it accepts everything but preserves type safety. For the return value, the union `list[dict[str, str]] | None` matches the actual branches.
