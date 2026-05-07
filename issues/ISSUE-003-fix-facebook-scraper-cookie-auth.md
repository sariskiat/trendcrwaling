# [ISSUE-003] Fix facebook-scraper: switch from credentials to browser cookies

**Type:** `human-in-loop`
**Priority:** `bug`
**Blocked by:** `none`
**Blocks:** `none`
**Module(s):** `scrapers/facebook.py`, `tests/test_facebook.py`

---

## Context

ISSUE-002 verification revealed that `facebook-scraper` is broken in both auth modes:

- **Without credentials**: returns 0 posts (Facebook requires login to view page content)
- **With credentials**: `AttributeError: 'NoneType' object has no attribute 'attrs'` — the library's login form parser fails because Facebook changed their login page HTML

The library's `login()` method calls `submit_form()` which searches for a `<form>` element that no longer exists at that URL.

## What to build

### Human step (required first)

Export cookies from a logged-in Facebook browser session to a Netscape-format `cookies.txt` file:

1. Install the browser extension **"Get cookies.txt LOCALLY"** (Chrome/Firefox)
2. Log into Facebook with the throwaway account (`pdrpo@hotmail.com`)
3. Export cookies for `facebook.com` → save as `fb_cookies.txt` in the project root
4. Add `FB_COOKIES_FILE=fb_cookies.txt` to `.env`

### Code changes

1. **`scrapers/facebook.py`** — replace credential-based auth with cookie-file auth:
   - Add `_cookie_file() -> str | None` that reads `FB_COOKIES_FILE` env var
   - In `scrape_page`, call `facebook_scraper.set_cookies(parse_cookie_file(path))` before `get_posts` if a cookie file is set
   - Remove the `credentials` parameter from the `get_posts` call (credentials auth is broken)
   - Update `_credentials()` → remove it entirely (no longer needed)

2. **`tests/test_facebook.py`** — update tests:
   - Remove `test_scrape_page_passes_credentials_when_env_set`
   - Remove `test_scrape_page_passes_no_credentials_when_env_missing`
   - Add `test_scrape_page_uses_cookie_file_when_env_set` — mock `set_cookies` + `parse_cookie_file`
   - Add `test_scrape_page_skips_cookies_when_env_missing`

## Acceptance criteria

- [ ] Human exports `fb_cookies.txt` and sets `FB_COOKIES_FILE` in `.env`
- [ ] Failing tests written **before** implementation (TDD)
- [ ] `scrape_page` uses cookie-based auth when `FB_COOKIES_FILE` is set
- [ ] `scrape_page` runs without cookies when `FB_COOKIES_FILE` is not set
- [ ] `uv run ruff check .` passes
- [ ] `uv run pytest -x` passes
- [ ] Calling `analyze_competitor(name="mk.suki.official", platforms=["facebook"], limit=5)` returns ≥1 real post

## Out of scope

- Not in this issue: switching to a different scraping library
- Not in this issue: Instagram or TikTok

## Notes

`facebook-scraper` exposes `parse_cookie_file(path)` and `set_cookies(cookiejar)` in its public API. These bypass the broken login form entirely — the library just sends cookies directly on every request.

The cookie file is gitignored (contains session tokens). Add `fb_cookies.txt` to `.gitignore`.
