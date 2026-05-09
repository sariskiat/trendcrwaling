# [ISSUE-040] Implement Apify Clockworks scraper

## Type
AFK

## Priority
quick-win

## Blocked by
nothing

## Context

Apify Clockworks is a production-grade scraper API with 98% success rate, pay-per-result pricing. Most reliable option.

## Acceptance Criteria

- [ ] `scrapers/tiktok_apify.py` exists with `ApifyTikTokScraper` class and `scrape_user` async function
- [ ] `ApifyTikTokPost` typed dict matches existing `TikTokPost` structure
- [ ] MCP tool `tiktok_user_posts_apify` registered in `mcp_server/server.py`
- [ ] Tool returns JSON string of posts with source provenance (`"source": "apify"`)
- [ ] Tool returns clear error if `APIFY_TOKEN` environment variable not set
- [ ] Failing test first, then implementation passes
- [ ] `.env.example` documents `APIFY_TOKEN` variable

## Files to Create/Modify

| File | Action |
|------|--------|
| `scrapers/tiktok_apify.py` | Create |
| `tests/test_tiktok_apify.py` | Create |
| `mcp_server/server.py` | Add MCP tool |
| `.env.example` | Document APIFY_TOKEN |

## TDD Gate

```python
# test_tiktok_apify.py
async def test_scrape_user_returns_posts_with_source():
    """scrape_user returns ApifyTikTokPost with source=apify"""

async def test_scrape_user_raises_without_api_token():
    """scrape_user raises ConfigurationError if APIFY_TOKEN not set"""
```

## Notes

- Requires paid API token — tool must fail gracefully if not configured
- Follow the pattern from ISSUE-038 (TikTok-Api)
- Independent of other scrapers — can run in parallel with ISSUE-039