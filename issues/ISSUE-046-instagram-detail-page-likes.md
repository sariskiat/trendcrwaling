# [ISSUE-046] Instagram: detail-page likes scraper

## Type
AFK

## Priority
infra

## Blocked by
- ISSUE-045: Instagram Reels selector + shortcode timestamp (needs updated `InstagramPost` shape)

## Context

Instagram hides like counts on profile grid views — they are only visible on each post's detail page. Mode 2 (hashtag trending) and Mode 3 (global trending) rank posts by likes, so real like counts must be scraped. This issue adds a `_scrape_post_likes(page, post_url) -> int` helper that navigates to a post detail page and extracts the like count.

## Acceptance Criteria

- [ ] New async helper `_scrape_post_likes(ctx: BrowserContext, post_url: str) -> int` in `scrapers/instagram.py`
- [ ] Navigates to `post_url`, waits for like count element to appear, extracts and parses the number
- [ ] Returns `0` if like count is not found or fails to parse (graceful degradation)
- [ ] New async `_enrich_posts_with_likes(ctx: BrowserContext, posts: list[dict]) -> list[dict]` that calls `_scrape_post_likes` for each post concurrently (up to 5 at a time via `asyncio.gather` with semaphore)
- [ ] `scrape_hashtag` and `scrape_trending` (to be added in ISSUE-047) will call `_enrich_posts_with_likes`
- [ ] `scrape_user` does NOT call it (Mode 1 keeps `likes=0`)
- [ ] Unit test: mock page returns known like HTML → assert parsed integer returned
- [ ] All quality gates pass: `ruff .`, `black --check .`, `pytest -x --cov`, pyright

## Files to Modify

| File | Change |
|------|--------|
| `scrapers/instagram.py` | Add `_scrape_post_likes`, `_enrich_posts_with_likes` |
| `tests/test_instagram.py` | Add like-scraping unit tests |

## TDD Gate

```python
async def test_scrape_post_likes_returns_integer(mock_page):
    mock_page.inner_text.return_value = "1,234 likes"
    result = await _scrape_post_likes(mock_ctx, "https://www.instagram.com/p/abc123/")
    assert result == 1234

async def test_scrape_post_likes_returns_zero_on_failure(mock_page):
    mock_page.inner_text.side_effect = Exception("not found")
    result = await _scrape_post_likes(mock_ctx, "https://www.instagram.com/p/abc123/")
    assert result == 0
```

## Notes

- Instagram like count selector: `section span` containing "likes" or the `aria-label` on the like button — inspect current HTML to confirm exact selector before hardcoding
- Semaphore limit of 5 concurrent detail-page requests to avoid rate limiting
