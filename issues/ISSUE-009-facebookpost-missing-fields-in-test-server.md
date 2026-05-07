# [ISSUE-009] `FacebookPost` constructed without required fields in test_server.py

**Type:** `AFK`
**Priority:** `bug`
**Blocked by:** none
**Blocks:** none
**Module(s):** `tests/`

---

## Context

`FacebookPost` is a `TypedDict` with five required keys: `text`, `likes`, `time`, `post_url`, `image_url`. In `tests/test_server.py` line 32 and line 49, `FacebookPost` is constructed without `post_url` and `image_url`. TypedDict does not enforce fields at runtime so the tests pass, but the objects are structurally invalid and the type checker would flag them.

## What to build

In `tests/test_server.py`:

- Line 32: add `post_url=""` and `image_url=""` to the `FacebookPost(...)` constructor.
- Line 49: same — add `post_url=""` and `image_url=""`.

Exact fix for line 32:
```python
# before
fb_posts: list[FacebookPost] = [FacebookPost(text="f1", likes=30, time="2026-05-01")]

# after
fb_posts: list[FacebookPost] = [
    FacebookPost(text="f1", likes=30, time="2026-05-01", post_url="", image_url="")
]
```

Same pattern for line 49.

## Acceptance criteria

- [ ] Failing test written **before** any implementation (TDD — non-negotiable)
- [ ] All `FacebookPost` constructors in `tests/test_server.py` include all five required fields
- [ ] `ruff .` passes
- [ ] `pytest -x` passes

## Out of scope

No other test files are affected. `FacebookPost` definition itself does not change.

## Notes

If `post_url` and `image_url` are genuinely optional, change `FacebookPost` to `TypedDict` with `total=False` for those fields (or use a `Required`/`NotRequired` mix). But that is a separate design decision — for now, populate the fields with empty strings.
