# PRD — Replace facebook-scraper with Playwright

**Status:** `approved`
**Date:** 2026-05-07
**Grill session:** 2026-05-07
**Author:** saris

> **After all issues from this PRD are closed — delete this file.**

---

## Problem Statement

`facebook-scraper` is dead. Facebook's mobile site no longer serves simple HTML with `<article>` elements — it now returns the same React-rendered page as the desktop site. The library's login form parser fails with `AttributeError: 'NoneType' object has no attribute 'attrs'`, and even cookie-based auth returns 0 posts. Claude cannot research competitor Thai buffets via the MCP tool because no real Facebook data is ever returned.

## Solution

Replace `facebook-scraper` entirely with Playwright. Playwright drives a real headless Chromium browser, injects saved session cookies, navigates to the Facebook page, and extracts posts from the rendered DOM. The `FacebookPost` schema and `FacebookScraperError` exception stay unchanged — the MCP server contract is unaffected.

## User Stories

- As Claude, I can call `analyze_competitor(name="mkrestaurants", platforms=["facebook"])` and receive real posts with text, likes, time, post URL, and image URL so that I can analyse what content is performing well for MK Restaurant.
- As Claude, I receive a clear `FacebookScraperError` if the cookies are expired or the page is blocked, so I know to inform the user rather than returning silent empty results.

## Out of Scope

- Not in this PRD: Instagram or TikTok scrapers
- Not in this PRD: Credentials-based login (email + password flow)
- Not in this PRD: Headed (visible) browser mode
- Not in this PRD: Caching or storing results
- Not in this PRD: Scraping pages other than the public feed

## Implementation Decisions

| Decision | Choice made | Reason |
|---|---|---|
| Library | Playwright (already installed for TikTok) | facebook-scraper is broken; Playwright handles React-rendered pages |
| Auth | Inject cookies from `FB_COOKIES_FILE` env var | Login form parser is broken; cookies bypass it entirely |
| Browser mode | Headless async | Matches TikTok scraper pattern; MCP server is already async |
| Target URL | `https://www.facebook.com/{page}` | Confirmed slug for MK Restaurant is `mkrestaurants` |
| Output schema | `FacebookPost` TypedDict unchanged | MCP contract stays stable; no downstream changes needed |
| Error handling | Raise `FacebookScraperError` | Same pattern as existing code; MCP surfaces it to Claude |
| Cleanup | Remove `facebook-scraper` from `pyproject.toml` | Dead dependency |

## Proposed Modules

| Module path | Action | Notes |
|---|---|---|
| `scrapers/facebook.py` | rewrite | Replace all `facebook_scraper` imports with async Playwright; keep `FacebookPost`, `FacebookScraperError`, `scrape_page` public API unchanged |
| `tests/test_facebook.py` | rewrite | Mock Playwright `Page` and `Browser` objects instead of `get_posts`; same behaviours under test |
| `pyproject.toml` | modify | Remove `facebook-scraper` dependency; Playwright already listed |
