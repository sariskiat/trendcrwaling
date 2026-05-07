# [ISSUE-004] Replace facebook-scraper with Playwright

**Type:** `AFK`
**Priority:** `tracer-bullet`
**Blocked by:** `none`
**Blocks:** ISSUE-005
**Module(s):** `scrapers/facebook.py`, `tests/test_facebook.py`, `pyproject.toml`

---

## Context

`facebook-scraper` is dead — Facebook's mobile site no longer returns parseable HTML. Playwright drives a real headless Chromium browser, injects saved session cookies, and extracts posts from the React-rendered DOM. The public API (`FacebookPost`, `FacebookScraperError`, `scrape_page`) stays unchanged so the MCP server needs no edits.

## What to build

### `pyproject.toml`
Remove `facebook-scraper` from dependencies. Playwright is already listed.

### `scrapers/facebook.py`
Rewrite using `playwright.async_api`. Keep the same public surface:
- `FacebookPost` TypedDict — unchanged fields: `text`, `likes`, `time`, `post_url`, `image_url`
- `FacebookScraperError` — unchanged
- `scrape_page(page: str, limit: int = 20) -> list[FacebookPost]` — now `async`

Implementation shape:
1. Read `FB_COOKIES_FILE` env var; if set, load the Netscape cookies.txt and convert to Playwright cookie dicts
2. Launch headless Chromium via `async_playwright`
3. Inject cookies into browser context
4. Navigate to `https://www.facebook.com/{page}`
5. Wait for post elements to appear in the DOM
6. Extract up to `limit` posts: text, like count, timestamp, post URL, image URL
7. Return `list[FacebookPost]`; raise `FacebookScraperError` on any failure

Cookie format note: Netscape cookies.txt rows → Playwright expects `{"name": ..., "value": ..., "domain": ..., "path": ...}` dicts. Parse manually or use `http.cookiejar`.

### `tests/test_facebook.py`
Rewrite tests to mock Playwright. Use `unittest.mock.AsyncMock` and `MagicMock` for:
- `async_playwright()` context manager
- `browser.new_context()` → mock context
- `context.add_cookies()` 
- `context.new_page()` → mock page
- `page.goto()`, `page.query_selector_all()`, element `.inner_text()`, `.get_attribute()`

Keep the same test scenarios:
- Returns structured posts with all fields populated
- Respects `limit`
- Handles missing/empty fields with defaults
- Raises `ValueError` on `limit <= 0`
- Raises `FacebookScraperError` on Playwright failure
- Injects cookies when `FB_COOKIES_FILE` is set
- Skips cookies when `FB_COOKIES_FILE` is not set

## Acceptance criteria

- [ ] Failing tests written **before** any implementation (TDD — non-negotiable)
- [ ] `facebook-scraper` removed from `pyproject.toml`
- [ ] `scrapers/facebook.py` imports only from `playwright.async_api`, stdlib, and typing
- [ ] `scrape_page` is `async def`
- [ ] Cookie injection tested: `add_cookies` called when `FB_COOKIES_FILE` set, skipped when not
- [ ] `FacebookScraperError` raised on any Playwright exception
- [ ] All existing test scenarios pass with Playwright mocks
- [ ] `uv run ruff check .` passes
- [ ] `uv run pytest -x` passes

## Out of scope

- Not in this issue: credentials-based login (email/password)
- Not in this issue: headed browser mode
- Not in this issue: caching results
- Not in this issue: Instagram or TikTok
- Not in this issue: live verification against real Facebook (that is ISSUE-005)

## Notes

`scrape_page` becomes `async` — the MCP server already calls it with `await scrape_facebook(...)` so no server changes needed. Check `mcp_server/server.py` line ~56 to confirm the existing `await` is in place.

For DOM selectors: Facebook's post structure is dynamic. A robust starting point is `[data-pagelet="FeedUnit"]` or `article` — but confirm by inspecting the live page. The implementation must handle selector misses gracefully (raise `FacebookScraperError`, not crash).
