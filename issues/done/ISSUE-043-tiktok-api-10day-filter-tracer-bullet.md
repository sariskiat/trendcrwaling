# [ISSUE-043] TikTok API 10-day recency filter — tracer bullet

## Type
AFK

## Priority
tracer-bullet

## Blocked by
Nothing — first vertical slice

## Context

TikTok API scraper (`scrapers/tiktok_api.py`) already returns `created_at: int` (Unix timestamp) on every post. This issue enforces a 10-day recency filter end-to-end: scraper → MCP tools.

This is the tracer bullet for the Social All-Three PRD — the thinnest complete vertical slice that proves the age-filter pattern works and is testable.

## Acceptance Criteria

- [ ] `TikTokApiPost` retains `created_at: int` field (already exists — verify, do not remove)
- [ ] `scrape_user`, `scrape_trending`, `scrape_hashtag` in `tiktok_api.py` all drop posts where `time.time() - created_at > 864_000` (10 days) before returning
- [ ] Each function accepts an optional `max_age_days: int = 10` parameter so the filter is configurable
- [ ] MCP tools `tiktok_api_scrape_user`, `tiktok_api_scrape_trending`, `tiktok_api_scrape_hashtag` in `server.py` pass `max_age_days=10` and document the filter in their docstrings
- [ ] Unit test in `tests/test_tiktok_api.py`: posts older than 10 days are filtered out; posts within 10 days are retained
- [ ] All quality gates pass: `ruff .`, `black --check .`, `pytest -x --cov`, pyright

## Files to Modify

| File | Change |
|------|--------|
| `scrapers/tiktok_api.py` | Add `max_age_days` param + filter logic to all three functions |
| `mcp_server/server.py` | Pass `max_age_days=10`, update docstrings |
| `tests/test_tiktok_api.py` | Add filter tests |

## TDD Gate

Write a failing test first:
```python
def test_scrape_user_filters_old_posts():
    old_post = TikTokApiPost(..., created_at=int(time.time()) - 90*86400)
    recent_post = TikTokApiPost(..., created_at=int(time.time()) - 3*86400)
    # mock API to return [old_post, recent_post]
    # assert result == [recent_post]
```
