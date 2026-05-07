# Project Status

**Phase:** Done
**Feature:** Instagram scraper (Playwright)
**PRD:** docs/prd-playwright-instagram-scraper.md
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
| ISSUE-011 | Replace instagrapi with Playwright in scrapers/instagram.py | ✅ done |
| ISSUE-012 | Wire Playwright Instagram scraper into MCP server | ✅ done |
| ISSUE-013 | Close browser on exception path in scrape_user | ✅ done |
| ISSUE-014 | Add type annotations to module-level constants in scrapers/instagram.py | ✅ done |
| ISSUE-015 | Add BrowserContext type annotation to ctx in _setup_browser | ✅ done |

## DAG

| Issue | Type | Priority | Blocked by |
|---|---|---|---|
| ISSUE-013 | AFK | bug | none |
| ISSUE-014 | AFK | bug | none |
| ISSUE-015 | AFK | bug | none |

## Next Step

All QA issues resolved. Commit, merge PR, and close the feature branch.