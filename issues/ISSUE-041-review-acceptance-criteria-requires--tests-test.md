# [ISSUE-041] Review violation: Acceptance criteria requires `tests/test_instagram.py` to cover the scraper contract — specifically sort order by likes desc (fallback created_at desc). The diff adds no changes to this file and the existing `test_scrape_trending_deduplicates` does not assert sort order. A mocked unit test for `scrape_trending` covering sort, dedup, and recency filter is required.

**Type:** AFK
**Source:** Auto-created by reviewer — iteration 1, from ISSUE-043-instagram-global-trending-tracer-bullet.md

## Problem

File: `tests/test_instagram.py` (line 0)

Acceptance criteria requires `tests/test_instagram.py` to cover the scraper contract — specifically sort order by likes desc (fallback created_at desc). The diff adds no changes to this file and the existing `test_scrape_trending_deduplicates` does not assert sort order. A mocked unit test for `scrape_trending` covering sort, dedup, and recency filter is required.

## Acceptance Criteria

- [ ] Violation fixed in `tests/test_instagram.py`
- [ ] `uv run ruff check .` passes
- [ ] `uv run pyright` passes
- [ ] `uv run pytest -x` passes

## Files to Modify

- `tests/test_instagram.py`
