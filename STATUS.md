# Project Status

**Phase:** Done
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
| ISSUE-005 | Verify Playwright scraper returns real posts | ✅ done |
| ISSUE-006 | Remove `Any` type from test_facebook.py | ✅ done |
| ISSUE-007 | Split `scrape_page` — exceeds 30-line limit | ✅ done |
| ISSUE-008 | Replace `type: ignore` suppressions with correct types | ✅ done |
| ISSUE-009 | `FacebookPost` missing required fields in test_server.py | ✅ done |
| ISSUE-010 | Add `black` and `pytest-cov` to dev dependencies | ✅ done |

## Next Step

All QA issues resolved. Commit and close the branch.
