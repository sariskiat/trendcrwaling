# [ISSUE-005] Verify Playwright scraper returns real Facebook posts

**Type:** `human-in-loop`
**Priority:** `polish`
**Blocked by:** ISSUE-004
**Blocks:** `none`
**Module(s):** `mcp_server/server.py` (read-only verification)

---

## Context

After ISSUE-004 lands, the Playwright scraper is implemented and unit-tested with mocks. This issue verifies the full live path: Claude → MCP → Playwright → real Facebook page → real posts back to Claude.

## What to do

No code to write. Human must:

1. Ensure `FB_COOKIES_FILE=fb_cookies.txt` is set in `.env` and the file exists
2. Restart Claude Code (or reload MCP servers) so the updated `scrape_page` is active
3. Ask Claude to call `analyze_competitor` with:
   - `name`: `"mkrestaurants"`
   - `platforms`: `["facebook"]`
   - `limit`: `5`
4. Confirm the response contains real posts

If cookies have expired: export fresh cookies from the browser and replace `fb_cookies.txt`.

## Acceptance criteria

- [ ] Claude returns at least 1 real post from `mkrestaurants`
- [ ] At least one post has non-empty `text`
- [ ] At least one post has `likes >= 0`
- [ ] At least one post has a non-empty `post_url` starting with `https://`
- [ ] No `FacebookScraperError` raised (or if it is, the message clearly explains why)

## Out of scope

- Not in this issue: Instagram or TikTok
- Not in this issue: code changes

## Notes

If the Playwright scraper times out waiting for DOM elements, the CSS selectors in `scrape_page` may need adjusting — open a follow-up bug issue with the specific selector that failed.
