# [ISSUE-050] MCP: Facebook hashtag_trending + global_trending tools

## Type
AFK

## Priority
polish

## Blocked by
- ISSUE-049: Facebook timestamp parse + scrape_hashtag + scrape_trending

## Context

Wire the two new Facebook scraper functions into the MCP server. Also update the existing `facebook_scrape_page` tool to populate and pass `max_age_days=10`.

## Acceptance Criteria

- [ ] New MCP tool `facebook_hashtag_trending(query: str) -> str` in `mcp_server/server.py`
  - Validates `query` is non-empty, ≤ 500 chars
  - Calls `_scrape_facebook_hashtag(query, limit=10, max_age_days=10)`
  - Returns JSON array of `FacebookPost` dicts
  - Docstring explains: generates 10 hashtags from query, scrapes each, ranks by likes/recency, returns top 10 ≤ 10 days old
- [ ] New MCP tool `facebook_global_trending() -> str`
  - Calls `_scrape_facebook_trending(limit=10, max_age_days=10)`
  - Returns JSON array of `FacebookPost` dicts
  - Docstring explains: scrapes #trending + #viral Facebook pages, deduped, ≤ 10 days old
- [ ] Existing `facebook_scrape_page` updated to enforce `max_age_days=10` and document it
- [ ] Both new tools use `FB_COOKIES_FILE` env var (via `_require_env`)
- [ ] Unit tests in `tests/test_server.py` for both new tools (mock scraper functions)
- [ ] All quality gates pass: `ruff .`, `black --check .`, `pytest -x --cov`, pyright

## Files to Modify

| File | Change |
|------|--------|
| `mcp_server/server.py` | Add 2 new tools, update `facebook_scrape_page` |
| `tests/test_server.py` | Add tests for both new tools |

## TDD Gate

```python
async def test_facebook_hashtag_trending_validates_empty_query(mcp_client):
    with pytest.raises(ValidationError):
        await mcp_client.call_tool("facebook_hashtag_trending", {"query": ""})

async def test_facebook_global_trending_returns_json(mcp_client, mock_fb_scraper):
    result = await mcp_client.call_tool("facebook_global_trending", {})
    posts = json.loads(result)
    assert isinstance(posts, list)
```
