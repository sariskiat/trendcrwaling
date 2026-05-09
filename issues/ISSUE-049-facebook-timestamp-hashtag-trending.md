# [ISSUE-049] Facebook: timestamp parse + scrape_hashtag + scrape_trending

## Type
AFK

## Priority
infra

## Blocked by
- ISSUE-044: Hashtag generator module

## Context

Facebook has `<abbr title="May 7, 2026 at 3:00 PM">` elements that give a parseable timestamp. This issue adds timestamp parsing to existing posts, adds `scrape_hashtag`, and adds `scrape_trending` to `scrapers/facebook.py`.

Facebook hashtag URL: `https://www.facebook.com/hashtag/{hashtag}/`
Global trending seeds: `["trending", "viral"]` (same pattern as Instagram)

## Acceptance Criteria

- [ ] `FacebookPost` TypedDict gains `created_at: int` field (Unix timestamp, 0 if unparseable)
- [ ] `_parse_facebook_time(time_str: str) -> int` function that parses strings like `"May 7, 2026 at 3:00 PM"` to Unix timestamp; returns 0 on failure
- [ ] `scrape_page` updated to populate `created_at` from existing `time` field via `_parse_facebook_time`
- [ ] New `scrape_hashtag(query: str, limit: int = 10, max_age_days: int = 10) -> list[FacebookPost]`
  - Generates 10 hashtags from `query` via `hashtag_generator`
  - Scrapes each hashtag page (~10 posts each)
  - Filters by `max_age_days`, ranks by `likes` (currently `0` on FB too — rank by recency if likes unavailable)
  - Returns top `limit`
- [ ] New `scrape_trending(limit: int = 10, max_age_days: int = 10) -> list[FacebookPost]`
  - Scrapes `#trending` and `#viral` Facebook hashtag pages
  - Deduplicates by `post_url`, filters by age, ranks by likes/recency
  - Returns top `limit`
- [ ] All exports added to `__all__`
- [ ] Unit tests for `_parse_facebook_time`, `scrape_hashtag`, `scrape_trending`
- [ ] All quality gates pass: `ruff .`, `black --check .`, `pytest -x --cov`, pyright

## Files to Modify

| File | Change |
|------|--------|
| `scrapers/facebook.py` | Add `created_at` field, `_parse_facebook_time`, `scrape_hashtag`, `scrape_trending` |
| `tests/test_facebook.py` | Tests for all new functions |

## TDD Gate

```python
def test_parse_facebook_time_known_value():
    ts = _parse_facebook_time("May 7, 2026 at 3:00 PM")
    assert ts == 1746622800  # or close — verify with datetime.fromisoformat

def test_parse_facebook_time_returns_zero_on_garbage():
    assert _parse_facebook_time("just now") == 0

async def test_scrape_trending_deduplicates(mock_playwright, mock_hashtag_gen):
    result = await scrape_trending(limit=10)
    urls = [p["post_url"] for p in result]
    assert len(urls) == len(set(urls))
```

## Notes

- Facebook time string format: `"%B %-d, %Y at %I:%M %p"` (locale-aware — handle edge cases)
- Facebook hashtag pages may require auth cookies — use existing `FB_COOKIES_FILE` env var
- If FB hashtag page is blocked, scraper should raise `FacebookScraperError` (supervisor will create a blocker issue via VERIFY step)
