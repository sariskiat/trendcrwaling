# PRD — Replace tiktokapipy with Playwright for TikTok Scraping

**Status:** Approved  
**Date:** 2026-05-07  
**Origin:** grill-me session (2026-05-07)

---

## Problem Statement

The TikTok scraper (`scrapers/tiktok.py`) depends on `tiktokapipy`, a third-party wrapper around TikTok's unofficial API. This library breaks frequently when TikTok changes endpoints, has stale maintenance, and offers no cookie-based auth — making it unreliable for production scraping. The Facebook and Instagram scrapers have already migrated to Playwright; TikTok is the last platform still on a library wrapper.

Without this change, the `analyze_competitor` MCP tool silently fails or returns stale data for TikTok, undermining the whole competitive research workflow.

---

## Solution

Replace the `tiktokapipy` dependency with a Playwright headless browser scraper that:

- Navigates TikTok pages directly in a real browser context
- Authenticates via a Netscape cookies.txt file (`TT_COOKIES_FILE` env var)
- Extracts post data from rendered DOM elements
- Exposes three entry points: user posts, trending posts, and hashtag posts
- Follows the same patterns established in `scrapers/instagram.py` and `scrapers/facebook.py`

---

## User Stories

1. **As a trend researcher**, I can scrape a TikTok user's recent posts so that I can analyse competitor content strategy.

2. **As a trend researcher**, I can scrape TikTok trending posts so that I can discover what content themes are performing well right now.

3. **As a trend researcher**, I can scrape posts for a specific TikTok hashtag so that I can track campaign or topic performance.

4. **As a trend researcher**, I get a clear error message when TikTok scraping fails so that I know what went wrong and can act on it.

5. **As a Claude MCP user**, I can call `scrape_tiktok_user`, `scrape_tiktok_trending`, or `scrape_tiktok_hashtag` tools so that I get structured TikTok data directly in my conversation.

---

## Out of Scope

- Video download or media storage
- Posting or scheduling content to TikTok
- Proxy rotation or IP management
- Analytics dashboards or aggregation
- Login via username/password (cookies only)
- Rate limiting or retry logic
- Scraping comments or follower lists

---

## Implementation Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Scraper engine** | Playwright headless | Consistent with Facebook and Instagram scrapers; renders JS-heavy TikTok pages |
| **Authentication** | `TT_COOKIES_FILE` env var (Netscape cookies.txt) | Same pattern as `IG_COOKIES_FILE` and `FB_COOKIES_FILE`; no credentials in code |
| **Entry points** | `scrape_user(username, limit)`, `scrape_trending(limit)`, `scrape_hashtag(tag, limit)` | Covers the three scraping dimensions agreed in grill-me |
| **Post fields** | `url`, `desc`, `likes`, `views`, `thumbnail_url`, `author` | Extends existing `TikTokPost` TypedDict with `views`, `thumbnail_url`, `author` |
| **MCP tools** | `scrape_tiktok_user`, `scrape_tiktok_trending`, `scrape_tiktok_hashtag` | One tool per entry point; granular control for Claude |
| **Wait strategy** | `networkidle` + `wait_for_selector` with 15s timeout | Balances page-load reliability with reasonable timeout |
| **Error handling** | All failures raise `TikTokScraperError` with descriptive message | Single exception type, consistent with Instagram/Facebook scrapers |

---

## Proposed Modules

| File | Change |
|---|---|
| `scrapers/tiktok.py` | Rewrite: remove `tiktokapipy`, implement Playwright scraper with `scrape_user`, `scrape_trending`, `scrape_hashtag` |
| `scrapers/__init__.py` | Export `scrape_trending` and `scrape_hashtag` alongside existing `scrape_tiktok` |
| `mcp_server/server.py` | Add `scrape_tiktok_user`, `scrape_tiktok_trending`, `scrape_tiktok_hashtag` tool definitions and handlers |
| `tests/test_tiktok.py` | Rewrite: replace `tiktokapipy` mocks with Playwright mocks; add tests for all three entry points |
| `tests/test_server.py` | Add tests for new MCP tool dispatch |
| `pyproject.toml` | Remove `tiktokapipy` dependency (Playwright already present) |
