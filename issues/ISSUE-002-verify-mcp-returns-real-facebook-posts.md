# [ISSUE-002] Verify MCP tool returns real Facebook posts

**Type:** `human-in-loop`
**Priority:** `polish`
**Blocked by:** ISSUE-001
**Blocks:** `none`
**Module(s):** `mcp_server/server.py` (read-only verification)

---

## Context

After ISSUE-001 lands, the scraper code is correct but has never been run against a real Facebook page. This issue verifies the full path: Claude → MCP → `scrape_page` → Facebook → real posts back to Claude.

## What to build

No code to write. Human must:

1. Restart Claude Code (or reload MCP servers) so the updated `FacebookPost` schema is active
2. Ask Claude to call `analyze_competitor` with:
   - `name`: `"mk.suki.official"`
   - `platforms`: `["facebook"]`
   - `limit`: `5`
3. Confirm the response contains real posts with non-empty `text`, `likes > 0`, a valid `post_url`, and a non-empty `image_url`

If any field is consistently empty, investigate whether `facebook-scraper` is returning that field for this page and open a follow-up bug.

## Acceptance criteria

- [ ] Claude returns at least 1 real post from `mk.suki.official`
- [ ] At least one post has non-empty `text`
- [ ] At least one post has `likes > 0`
- [ ] At least one post has a non-empty `post_url` (starts with `https://`)
- [ ] At least one post has a non-empty `image_url`
- [ ] No `FacebookScraperError` is raised (or if it is, the error message is understood and triaged)

## Out of scope

- Not in this issue: Instagram or TikTok verification
- Not in this issue: Fixing authentication issues (if blocked, that is a separate bug)
- Not in this issue: Code changes

## Notes

If `facebook-scraper` gets blocked on `mk.suki.official` without credentials, the next step is to set `FB_EMAIL` and `FB_PASSWORD` in `.env` with a throwaway Facebook account. Do not use a real personal account.
