# PRD — TikTok Scraping Alternatives

## Problem Statement

The current TikTok Playwright scraper is blocked by TikTok's aggressive anti-bot protection. Even with valid cookies and non-headless mode, the scraper times out waiting for post selectors. Users cannot retrieve TikTok data through the MCP tools, breaking the trend research workflow for TikTok content.

**Who experiences this:** Researchers using the MCP trend tools who need TikTok data alongside Facebook and Instagram.

**What breaks today:**
- `tiktok_user_posts` MCP tool returns timeout errors
- `tiktok_trending` MCP tool returns timeout errors
- `tiktok_hashtag_posts` MCP tool returns timeout errors

## Solution (High-Level)

Implement three TikTok data retrieval alternatives with different trade-offs:

1. **TikTok-Api (Python)** — Free unofficial API wrapper, may still hit rate limits but worth trying first
2. **TikAPI.io** — Paid managed API service, handles anti-bot internally
3. **Apify Clockworks** — Production-grade scraper API with 98% success rate, pay-per-result

The MCP server will expose all three as separate tools, allowing users to choose based on their needs (free vs reliable, self-hosted vs managed).

## User Stories

1. **As a researcher**, I can retrieve TikTok user posts using the free TikTok-Api library so that I can analyze competitor content without paying for API services.

2. **As a researcher**, I can retrieve TikTok trending posts via TikAPI.io so that I get reliable data without managing anti-bot issues myself.

3. **As a researcher**, I can retrieve TikTok hashtag posts via Apify so that I get production-grade reliability with pay-per-result pricing.

4. **As a researcher**, I can see which TikTok data source was used in the response so that I understand the data provenance and reliability.

5. **As a researcher**, I can configure which TikTok source to prefer (via environment variable) so that I control cost vs reliability trade-offs.

## Implementation Decisions

1. **Keep existing Playwright scraper** — Add `TT_HEADLESS` env var support (already done), leave as fallback option
2. **Three new scraper modules** — One per alternative, not a single abstraction layer
3. **Separate MCP tools per source** — `tiktok_user_posts_api`, `tiktok_user_posts_apify`, etc. OR single tool with `source` parameter
4. **Configuration via environment variables** — `TIKTOK_API_KEY`, `TIKAPI_KEY`, `APIFY_TOKEN` for respective services
5. **Fail gracefully** — If a paid service has no API key configured, the tool returns a helpful error message

## Out of Scope

- Unified caching layer across TikTok sources
- Automatic failover between sources (user chooses explicitly)
- TikTok video downloading (only metadata retrieval)
- TikTok comment scraping (future consideration)
- TikTok live stream data
- OAuth authentication for user-specific TikTok data

## Proposed Modules

### New Files

| File | Purpose |
|------|---------|
| `scrapers/tiktok_api.py` | TikTok-Api (davidteather) implementation |
| `scrapers/tiktok_tikapi.py` | TikAPI.io implementation |
| `scrapers/tiktok_apify.py` | Apify Clockworks integration |

### Modified Files

| File | Change |
|------|--------|
| `mcp_server/server.py` | Add new TikTok MCP tools for each source |
| `.env.example` | Document new environment variables |
| `pyproject.toml` | Add `TikTokApi` dependency (already added) |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `TIKTOK_API_KEY` | Optional: ms_token for TikTok-Api library |
| `TIKAPI_KEY` | Required for TikAPI.io integration |
| `APIFY_TOKEN` | Required for Apify integration |
| `TIKTOK_SOURCE` | Default source: `auto` (try free first), `api`, `tikapi`, `apify` |

## Success Criteria

- [ ] All three TikTok alternatives return real post data
- [ ] MCP tools expose each source
- [ ] Clear error messages when API keys missing
- [ ] Documentation updated with pricing/trade-offs