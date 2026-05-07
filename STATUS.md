# Project Status

**Phase:** Implement → Verify
**Feature:** Facebook scraper (Playwright)
**PRD:** docs/prd-playwright-facebook-scraper.md
**Updated:** 2026-05-07

## Issues

| Issue | Title | Status |
|---|---|---|
| ISSUE-001 | Add post_url and image_url to FacebookPost | ✅ done |
| ISSUE-002 | Verify MCP returns real Facebook posts | ✅ done (root cause → ISSUE-004) |
| ISSUE-003 | Fix facebook-scraper cookie auth | ✅ done (superseded by ISSUE-004) |
| ISSUE-004 | Replace facebook-scraper with Playwright | ✅ done |
| ISSUE-005 | Verify Playwright scraper returns real posts | 🔄 in-progress — awaiting MCP reload |

## Next Step

Reload MCP servers in Claude Code, then call `analyze_competitor(name="mkrestaurants", platforms=["facebook"], limit=5)` to complete ISSUE-005 verification.
