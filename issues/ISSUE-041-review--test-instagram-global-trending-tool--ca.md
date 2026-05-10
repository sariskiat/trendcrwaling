# [ISSUE-041] Review violation: `test_instagram_global_trending_tool` calls the real `instagram_global_trending` function with no mock of `scrape_trending`. This makes the test dependent on live Instagram credentials and network, so it will hang or fail in CI. The test must patch `scrapers.instagram.scrape_trending` (or the import path used in server.py) with an AsyncMock that returns controlled fixture data.

**Type:** AFK
**Source:** Auto-created by reviewer — iteration 1, from ISSUE-043-instagram-global-trending-tracer-bullet.md

## Problem

File: `tests/test_server.py` (line 2159)

`test_instagram_global_trending_tool` calls the real `instagram_global_trending` function with no mock of `scrape_trending`. This makes the test dependent on live Instagram credentials and network, so it will hang or fail in CI. The test must patch `scrapers.instagram.scrape_trending` (or the import path used in server.py) with an AsyncMock that returns controlled fixture data.

## Acceptance Criteria

- [ ] Violation fixed in `tests/test_server.py`
- [ ] `uv run ruff check .` passes
- [ ] `uv run pyright` passes
- [ ] `uv run pytest -x` passes

## Files to Modify

- `tests/test_server.py`
