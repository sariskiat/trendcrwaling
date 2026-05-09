# [ISSUE-041] Add trending and hashtag endpoints to TikTok scrapers

## Type
AFK

## Priority
quick-win

## Blocked by
- ISSUE-038: TikTok-Api scraper
- ISSUE-039: TikAPI.io scraper
- ISSUE-040: Apify Clockworks scraper

## Context

Each TikTok scraper currently only supports `scrape_user`. Add `scrape_trending` and `scrape_hashtag` to match the existing Playwright scraper capabilities.

## Acceptance Criteria

- [ ] Each scraper module has `scrape_trending(limit)` async function
- [ ] Each scraper module has `scrape_hashtag(tag, limit)` async function
- [ ] MCP tools registered: `tiktok_trending_api`, `tiktok_trending_tikapi`, `tiktok_trending_apify`
- [ ] MCP tools registered: `tiktok_hashtag_api`, `tiktok_hashtag_tikapi`, `tiktok_hashtag_apify`
- [ ] All new functions have failing tests first, then pass
- [ ] Source provenance included in all responses

## Files to Modify

| File | Change |
|------|--------|
| `scrapers/tiktok_api.py` | Add scrape_trending, scrape_hashtag |
| `scrapers/tiktok_tikapi.py` | Add scrape_trending, scrape_hashtag |
| `scrapers/tiktok_apify.py` | Add scrape_trending, scrape_hashtag |
| `tests/test_tiktok_api.py` | Add tests for new functions |
| `tests/test_tiktok_tikapi.py` | Add tests for new functions |
| `tests/test_tiktok_apify.py` | Add tests for new functions |
| `mcp_server/server.py` | Add 6 new MCP tools |

## TDD Gate

```python
# For each scraper test file
async def test_scrape_trending_returns_posts_with_source():
    """scrape_trending returns posts with correct source"""

async def test_scrape_hashtag_returns_posts_with_source():
    """scrape_hashtag returns posts with correct source"""
```

## Notes

- Follow existing patterns from `scrapers/tiktok.py` for function signatures
- Some APIs may not support trending/hashtag — check documentation for each