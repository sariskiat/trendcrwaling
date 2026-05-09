# [ISSUE-038] Implement TikTok-Api scraper (tracer bullet)

## Type
AFK

## Priority
tracer-bullet

## Blocked by
nothing

## Context

This is the **tracer bullet** — the thinnest complete vertical slice through all layers. It validates the pattern before implementing the paid alternatives.

TikTok-Api (davidteather) is a free unofficial API wrapper. It may hit rate limits but worth trying first.

## Acceptance Criteria

- [ ] `scrapers/tiktok_api.py` exists with `TikTokApiScraper` class and `scrape_user` async function
- [ ] `TikTokApiPost` typed dict matches existing `TikTokPost` structure (url, desc, thumbnail_url, views, author, likes)
- [ ] MCP tool `tiktok_user_posts_api` registered in `mcp_server/server.py`
- [ ] Tool returns JSON string of posts with source provenance (`"source": "tiktok-api"`)
- [ ] Tool returns clear error if library not installed or ms_token missing
- [ ] Failing test first, then implementation passes
- [ ] `pyproject.toml` updated with `TikTokApi` dependency

## Files to Create/Modify

| File | Action |
|------|--------|
| `scrapers/tiktok_api.py` | Create |
| `tests/test_tiktok_api.py` | Create |
| `mcp_server/server.py` | Add MCP tool |
| `pyproject.toml` | Add TikTokApi dependency |

## TDD Gate

```python
# test_tiktok_api.py
async def test_scrape_user_returns_posts_with_source():
    """scrape_user returns TikTokApiPost with source=tiktok-api"""
    # Mock TikTokApi calls
    # Assert posts returned with correct structure
    # Assert source field = "tiktok-api"
```

## Notes

- Keep existing Playwright scraper as fallback
- This is free — no API key required, but ms_token optional
- Pattern established here will be replicated for TikAPI and Apify