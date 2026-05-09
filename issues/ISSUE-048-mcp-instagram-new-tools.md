# [ISSUE-048] MCP: Instagram hashtag_trending + global_trending tools

## Type
AFK

## Priority
polish

## Blocked by
- ISSUE-047: Instagram scrape_hashtag + scrape_trending

## Context

Wire the two new Instagram scraper functions into the MCP server as callable tools. Also update the existing `instagram_scrape_user` tool to pass `max_age_days=10`.

## Acceptance Criteria

- [ ] New MCP tool `instagram_hashtag_trending(query: str) -> str` in `mcp_server/server.py`
  - Validates `query` is non-empty, ≤ 500 chars
  - Calls `_scrape_instagram_hashtag(query, limit=10, max_age_days=10)`
  - Returns JSON array of `InstagramPost` dicts
  - Docstring explains: generates 10 hashtags from query, scrapes each, ranks by likes, returns top 10 ≤ 10 days old
- [ ] New MCP tool `instagram_global_trending() -> str`
  - Calls `_scrape_instagram_trending(limit=10, max_age_days=10)`
  - Returns JSON array of `InstagramPost` dicts
  - Docstring explains: scrapes #trending + #viral, deduped, ranked by likes, ≤ 10 days old
- [ ] Existing `instagram_scrape_user` updated to enforce `max_age_days=10` and document it
- [ ] Both new tools use `IG_COOKIES_FILE` env var (via `_require_env`)
- [ ] Unit tests in `tests/test_server.py` for both new tools (mock scraper functions)
- [ ] All quality gates pass: `ruff .`, `black --check .`, `pytest -x --cov`, pyright

## Files to Modify

| File | Change |
|------|--------|
| `mcp_server/server.py` | Add 2 new tools, update `instagram_scrape_user` |
| `tests/test_server.py` | Add tests for both new tools |

## TDD Gate

```python
async def test_instagram_hashtag_trending_validates_empty_query(mcp_client):
    with pytest.raises(ValidationError):
        await mcp_client.call_tool("instagram_hashtag_trending", {"query": ""})

async def test_instagram_global_trending_returns_json(mcp_client, mock_ig_scraper):
    result = await mcp_client.call_tool("instagram_global_trending", {})
    posts = json.loads(result)
    assert isinstance(posts, list)
```
