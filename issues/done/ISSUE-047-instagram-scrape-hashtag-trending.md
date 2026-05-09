# [ISSUE-047] Instagram: scrape_hashtag + scrape_trending

## Type
AFK

## Priority
infra

## Blocked by
- ISSUE-044: Hashtag generator module
- ISSUE-046: Instagram detail-page likes scraper (needs `_enrich_posts_with_likes`)

## Context

Add `scrape_hashtag` and `scrape_trending` to `scrapers/instagram.py`. These are the Mode 2 and Mode 3 entry points for Instagram.

- `scrape_hashtag(query, limit=10, max_age_days=10)` — generates 10 hashtags from `query` via `hashtag_generator`, scrapes ~10 posts per hashtag, enriches with real likes, filters by age, ranks by likes, returns top `limit`.
- `scrape_trending(limit=10, max_age_days=10)` — scrapes `#trending` and `#viral`, deduplicates by `post_url`, enriches with real likes, filters by age, ranks by likes, returns top `limit`.

## Acceptance Criteria

- [ ] `scrape_hashtag(query: str, limit: int = 10, max_age_days: int = 10) -> list[InstagramPost]` added
- [ ] `scrape_trending(limit: int = 10, max_age_days: int = 10) -> list[InstagramPost]` added
- [ ] Both use `_enrich_posts_with_likes` for real like counts
- [ ] Both filter posts where `time.time() - created_at > max_age_days * 86400`
- [ ] `scrape_trending` deduplicates by `post_url` before ranking
- [ ] `scrape_trending` seeds from `["trending", "viral"]` (no `#` — added internally when building URL)
- [ ] Instagram hashtag URL pattern: `https://www.instagram.com/explore/tags/{hashtag}/`
- [ ] Returns fewer than `limit` posts if filter leaves fewer (no error)
- [ ] All exports added to `__all__`
- [ ] Unit tests for both functions with mocked Playwright and mocked hashtag generator
- [ ] All quality gates pass: `ruff .`, `black --check .`, `pytest -x --cov`, pyright

## Files to Modify

| File | Change |
|------|--------|
| `scrapers/instagram.py` | Add `scrape_hashtag`, `scrape_trending` |
| `tests/test_instagram.py` | Add tests for both new functions |

## TDD Gate

```python
async def test_scrape_trending_deduplicates(mock_playwright, mock_hashtag_gen):
    # both #trending and #viral return same post_url
    result = await scrape_trending(limit=10)
    assert len([p for p in result if p["post_url"] == "https://..."]) == 1

async def test_scrape_hashtag_filters_old_posts(mock_playwright, mock_hashtag_gen):
    # mock returns 1 old post (>10 days) + 1 recent post
    result = await scrape_hashtag("summer", limit=10)
    assert len(result) == 1  # only recent post passes
```
