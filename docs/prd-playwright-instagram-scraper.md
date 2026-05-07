# PRD — Replace instagrapi with Playwright for Instagram Scraping

**Status:** `approved`
**Date:** 2026-05-07
**Grill session:** 2026-05-07
**Author:** saris

> **After all issues from this PRD are closed — delete this file.**
> Doc rot is a production risk. Old PRDs mislead future agents. (#14)

---

## Problem Statement

The Instagram scraper uses instagrapi, which requires a one-time manual login and a saved session JSON file (`ig_session.json`). The session flow is unreliable — sessions expire, Instagram triggers checkpoints or 2FA, and the setup script (`setup_ig_session.py`) does not handle these cases. As a result, the MCP tool cannot reliably return real Instagram posts for competitor research.

## Solution

Replace instagrapi entirely with Playwright headless Chromium, following the same pattern used for the Facebook scraper. Playwright navigates the public Instagram profile grid at `instagram.com/{username}/`, injects cookies from a Netscape `cookies.txt` file (exported from a logged-in browser session), scrolls to load posts, and extracts post data from the DOM. No passwords, no session JSON, no instagrapi.

## User Stories

- As Claude, I can call `analyze_competitor(name="mk_suki", platforms=["instagram"])` and receive a list of recent Instagram posts with image URL, caption, post URL, and like count so that I can analyse competitor content.
- As a developer, I can set `IG_COOKIES_FILE=/path/to/cookies.txt` and have the scraper authenticate without any additional setup step so that onboarding is consistent with the Facebook scraper.
- As Claude, I receive an `InstagramScraperError` when Instagram blocks the request or no posts are found so that I can report the failure clearly rather than silently returning nothing.

## Out of Scope

- Not in this PRD: Instagram Stories
- Not in this PRD: Reels video download (Reels are scraped as image posts — thumbnail + post URL only)
- Not in this PRD: Comment scraping
- Not in this PRD: Follower/following counts
- Not in this PRD: Posting or any write operations
- Not in this PRD: Pagination beyond the `limit` parameter
- Deferred to future work: Like count extraction (return `0` if Instagram hides it)

## Implementation Decisions

| Decision | Choice made | Reason |
|---|---|---|
| Auth mechanism | `IG_COOKIES_FILE` env var → Netscape cookies.txt | Consistent with `FB_COOKIES_FILE`; no passwords stored; works with exported browser sessions |
| Scraping target | Profile grid at `instagram.com/{username}/` | Simplest public surface; contains image thumbnails, post URLs, captions |
| Reel handling | Treat same as image posts | No special casing needed — thumbnail + post URL available in grid |
| Function signature | `scrape_user(username: str, limit: int) -> list[InstagramPost]` | Drop `session_file` param; cookies come from env var |
| Error behaviour | Raise `InstagramScraperError` | Consistent with existing contract; MCP server surfaces the error |
| `likes` when hidden | Return `0` | Instagram hides counts — consistent with Facebook scraper behaviour |

## Proposed Modules

| Module path | Action | Notes |
|---|---|---|
| `scrapers/instagram.py` | rewrite | Replace instagrapi implementation with Playwright; same structure as `scrapers/facebook.py` |
| `scrapers/__init__.py` | modify | Update `scrape_instagram` alias — remove `session_file` from the re-export call site if needed |
| `mcp_server/server.py` | modify | Remove `_IG_SESSION_FILE` constant; update `scrape_instagram` call to `scrape_instagram(name, limit)` |
| `setup_ig_session.py` | delete | No longer needed — replaced by browser cookie export |
| `tests/test_instagram.py` | rewrite | Replace instagrapi mocks with Playwright mocks matching the Facebook test pattern |
