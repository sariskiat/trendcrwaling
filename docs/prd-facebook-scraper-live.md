# PRD — Facebook Scraper: Live Data via MCP

**Status:** `approved`
**Date:** 2026-05-06
**Grill session:** 2026-05-06
**Author:** saris

> **After all issues from this PRD are closed — delete this file.**
> Doc rot is a production risk. Old PRDs mislead future agents. (#14)

---

## Problem Statement

The `analyze_competitor` MCP tool exists and is registered with Claude, but calling it returns nothing useful — all scrapers mock their dependencies, so no real data is ever fetched. When Claude tries to research a competitor Thai buffet (e.g. MK Suki), it gets empty results or errors instead of actual posts.

## Solution

Update the Facebook scraper so it fetches real posts from public Facebook pages and returns them with enough data (text, likes, date, post link, and image URL) for Claude to perform content and visual analysis.

The `analyze_competitor` MCP tool already wires the scraper to Claude — no server changes needed. Only `scrapers/facebook.py` and its tests need updating.

## User Stories

- As Claude, I can call `analyze_competitor(name="mk.suki.official", platforms=["facebook"])` and receive a list of real posts with text, likes, date, post URL, and image URL so that I can analyse what content is performing well for this competitor.
- As Claude, I can see the direct link to each post so that I can reference it during analysis.
- As Claude, I can see the main image URL for each post so that I can describe the visual content.

## Out of Scope

- Not in this PRD: Instagram scraping (needs throwaway account session file)
- Not in this PRD: TikTok scraping (needs Playwright browsers installed)
- Not in this PRD: Facebook authentication/credentials — public pages only
- Not in this PRD: CLI runner or test script
- Not in this PRD: Scheduled runs or persistent storage
- Deferred: Scraping multiple competitors in one call

## Implementation Decisions

| Decision | Choice made | Reason |
|---|---|---|
| Data fields | Add `post_url` and `image_url` to `FacebookPost` | User needs link + image for content analysis |
| Field source | `post_url` from `post.get("post_url")`, `image_url` from `post.get("image")` | These keys are confirmed in `facebook-scraper`'s extractor output |
| Missing fields | Default to `""` (empty string) | Consistent with existing `text` and `time` defaults |
| Credentials | None — unauthenticated first | MK Suki is a public page; add creds only if blocked |
| Test approach | TDD — failing test first, then implementation | Per project rules |

## Proposed Modules

| Module path | Action | Notes |
|---|---|---|
| `scrapers/facebook.py` | modify | Add `post_url: str` and `image_url: str` to `FacebookPost`; extract from `get_posts` output |
| `tests/test_facebook.py` | modify | Add tests asserting `post_url` and `image_url` are populated; update existing mock data |
