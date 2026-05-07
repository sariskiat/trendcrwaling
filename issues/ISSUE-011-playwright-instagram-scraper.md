# [ISSUE-011] Replace instagrapi with Playwright in scrapers/instagram.py

**Type:** `AFK`
**Priority:** `tracer-bullet`
**Blocked by:** none
**Blocks:** ISSUE-012
**Module(s):** `scrapers/`

---

## Context

The Instagram scraper currently uses instagrapi with a session JSON file. The session flow is unreliable — sessions expire and Instagram triggers checkpoints. The solution is to replace instagrapi entirely with Playwright headless Chromium, following the same pattern as `scrapers/facebook.py`.

## What to build

Rewrite `scrapers/instagram.py` in place. Do not touch `mcp_server/server.py` or `setup_ig_session.py` in this issue.

### Schema change

Add `post_url: str` to `InstagramPost`:

```python
class InstagramPost(TypedDict):
    url: str        # thumbnail / first image CDN URL
    caption: str
    likes: int      # return 0 if hidden
    post_url: str   # e.g. https://www.instagram.com/p/ABC123/
```

### New function signature

```python
async def scrape_user(username: str, limit: int = 20) -> list[InstagramPost]:
```

Drop `session_file` parameter entirely. Cookies are loaded from `IG_COOKIES_FILE` env var (Netscape cookies.txt format), same as `FB_COOKIES_FILE` in the Facebook scraper.

### Implementation structure (mirror facebook.py)

Extract three private helpers — each must stay under 30 lines:

1. `_cookie_file() -> str | None` — reads `IG_COOKIES_FILE` env var
2. `async _setup_browser(pw, cookie_path, username) -> tuple[Browser, Page]` — launches Chromium, injects cookies if present, navigates to `https://www.instagram.com/{username}/`, waits for load
3. `async _extract_posts(pg) -> list[dict[str, str]]` — scrolls the page, evaluates DOM JS to extract post thumbnails and links

`scrape_user` orchestrates: validate limit → cookie path → `async_playwright()` → `_setup_browser` → `_extract_posts` → map to `InstagramPost` → close browser. Must raise `InstagramScraperError` on any failure (wrap in `except Exception`).

### DOM extraction target

Instagram profile grids render `<article>` or `<a href="/p/...">` elements. Extract:
- `post_url`: `href` from `a[href*="/p/"]` links in the grid
- `url`: `src` from the `img` inside each post link
- `caption`: `alt` attribute on the `img` (Instagram puts the caption there for accessibility)
- `likes`: `0` (not visible in grid view)

### Auth

```python
_COOKIE_ENV = "IG_COOKIES_FILE"
```

If `IG_COOKIES_FILE` is not set, attempt to scrape without cookies (may fail — that is acceptable; `InstagramScraperError` will be raised).

### Rewrite tests/test_instagram.py

Replace instagrapi mocks with Playwright mocks using the exact same helper pattern as `tests/test_facebook.py`:

- `_make_pw_mocks(evaluate_posts)` — returns `(mock_pw, mock_browser, mock_context, mock_page)` wired for async
- `_patch_pw(mock_pw)` — patches `scrapers.instagram.async_playwright`

Required tests (TDD — write failing test first for each):
- `test_scrape_user_returns_structured_posts` — happy path, all fields populated
- `test_scrape_user_respects_limit`
- `test_scrape_user_handles_missing_fields` — empty strings, 0 likes
- `test_scrape_user_raises_on_invalid_limit` — `limit=0` raises `ValueError`
- `test_scrape_user_raises_scraper_error_on_playwright_failure`
- `test_scrape_user_injects_cookies_when_env_set`
- `test_scrape_user_skips_cookies_when_env_missing`

## Acceptance criteria

- [ ] Failing test written **before** any implementation (TDD — non-negotiable)
- [ ] Implementation makes the test pass
- [ ] `InstagramPost` has `url`, `caption`, `likes`, `post_url` — all typed
- [ ] `scrape_user(username, limit)` — no `session_file` parameter
- [ ] `_setup_browser`, `_extract_posts`, `scrape_user` each under 30 lines
- [ ] No `Any` annotations, no `type: ignore`
- [ ] Auth reads from `IG_COOKIES_FILE` env var via `_cookie_file()` helper
- [ ] `InstagramScraperError` raised on Playwright failure
- [ ] `ruff .` passes
- [ ] `black --check .` passes
- [ ] `pytest -x --cov` passes, all 7 new tests green

## Out of scope

- MCP server wiring — that is ISSUE-012
- Deleting `setup_ig_session.py` — that is ISSUE-012
- Stories, Reels video download, comments, followers, posting

## Notes

Follow `scrapers/facebook.py` exactly as the reference implementation. The `_EXTRACT_JS` constant pattern (module-level f-string built from selector constants) keeps `_extract_posts` short. Use `SetCookieParam` from `playwright._impl._api_structures` for the cookie type (not re-exported from `playwright.async_api` — see facebook.py for the import pattern).
