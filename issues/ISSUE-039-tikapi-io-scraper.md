# [ISSUE-039] Implement TikAPI.io scraper

## Type
AFK

## Priority
quick-win

## Blocked by
nothing

## Context

TikAPI.io is a paid managed API service that handles anti-bot internally. Reliable data without managing anti-bot issues.

## Acceptance Criteria

- [ ] `scrapers/tiktok_tikapi.py` exists with `TikApiScraper` class and `scrape_user` async function
- [ ] `TikApiPost` typed dict matches existing `TikTokPost` structure
- [ ] MCP tool `tiktok_user_posts_tikapi` registered in `mcp_server/server.py`
- [ ] Tool returns JSON string of posts with source provenance (`"source": "tikapi"`)
- [ ] Tool returns clear error if `TIKAPI_KEY` environment variable not set
- [ ] Failing test first, then implementation passes
- [ ] `.env.example` documents `TIKAPI_KEY` variable

## Files to Create/Modify

| File | Action |
|------|--------|
| `scrapers/tiktok_tikapi.py` | Create |
| `tests/test_tiktok_tikapi.py` | Create |
| `mcp_server/server.py` | Add MCP tool |
| `.env.example` | Document TIKAPI_KEY |

## TDD Gate

```python
# test_tiktok_tikapi.py
async def test_scrape_user_returns_posts_with_source():
    """scrape_user returns TikApiPost with source=tikapi"""

async def test_scrape_user_raises_without_api_key():
    """scrape_user raises ConfigurationError if TIKAPI_KEY not set"""
```

## Notes

- Requires paid API key — tool must fail gracefully if not configured
- Follow the pattern from ISSUE-038 (TikTok-Api)
- Independent of other scrapers — can run in parallel