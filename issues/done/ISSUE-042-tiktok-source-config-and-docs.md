# [ISSUE-042] Add TIKTOK_SOURCE environment variable and documentation

## Type
AFK

## Priority
polish

## Blocked by
- ISSUE-038: TikTok-Api scraper
- ISSUE-039: TikAPI.io scraper
- ISSUE-040: Apify Clockworks scraper
- ISSUE-041: Trending/hashtag endpoints

## Context

Users need to configure which TikTok source to prefer via environment variable. Documentation needs to explain pricing and trade-offs.

## Acceptance Criteria

- [ ] `TIKTOK_SOURCE` env var documented: `auto` (try free first), `api`, `tikapi`, `apify`
- [ ] `.env.example` updated with all TikTok environment variables
- [ ] `README.md` updated with TikTok sources comparison table (free vs paid, reliability)
- [ ] Each MCP tool docstring explains source and requirements
- [ ] Error messages guide users to set correct environment variable

## Files to Modify

| File | Change |
|------|--------|
| `.env.example` | Add all TikTok env vars |
| `README.md` | Add TikTok sources section |
| `mcp_server/server.py` | Improve docstrings |

## TDD Gate

No new code — documentation and configuration only. Verify:
- [ ] `.env.example` contains all required variables
- [ ] README has comparison table with pricing info

## Notes

- Pricing info:
  - TikTok-Api: Free, may hit rate limits
  - TikAPI.io: Paid, reliable
  - Apify: Pay-per-result, 98% success rate
- This is the final polish issue before the feature is complete