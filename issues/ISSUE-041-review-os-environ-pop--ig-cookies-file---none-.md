# [ISSUE-041] Review violation: os.environ.pop('IG_COOKIES_FILE', None) mutates global env without cleanup. If IG_COOKIES_FILE is set in the environment, it is permanently removed for all subsequent tests in the session. Must use `with patch.dict('os.environ', {}, clear=True):` (the same pattern as test_tiktok_user_posts_missing_cookies on line 126).

**Type:** AFK
**Source:** Auto-created by reviewer — iteration 2, from ISSUE-041-review-missing---require-env-ig-cookies-file--.md

## Problem

File: `tests/test_server.py` (line 138)

os.environ.pop('IG_COOKIES_FILE', None) mutates global env without cleanup. If IG_COOKIES_FILE is set in the environment, it is permanently removed for all subsequent tests in the session. Must use `with patch.dict('os.environ', {}, clear=True):` (the same pattern as test_tiktok_user_posts_missing_cookies on line 126).

## Acceptance Criteria

- [ ] Violation fixed in `tests/test_server.py`
- [ ] `uv run ruff check .` passes
- [ ] `uv run pyright` passes
- [ ] `uv run pytest -x` passes

## Files to Modify

- `tests/test_server.py`
