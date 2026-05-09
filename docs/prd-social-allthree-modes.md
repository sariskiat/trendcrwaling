# PRD — Social All-Three: 3 Modes × 3 Platforms

## Problem Statement

The MCP server today only supports TikTok with three scraping modes (user, trending, hashtag). Instagram and Facebook scrapers exist but only expose a single mode each (user posts, page posts respectively). There is no unified approach to:

1. Fetching the latest posts from a specific account (all platforms)
2. Finding trending posts for a topic from generated hashtags (all platforms)
3. Surfacing globally trending posts without a specific query (all platforms)

Additionally, no platform enforces a recency filter — stale posts from months ago can pollute results. The `once.sh` loop cannot distinguish AFK-safe issues from HITL issues that need human credentials, causing wasted supervisor cycles.

## Solution (High-Level)

Extend all three platforms (TikTok, Instagram, Facebook) to support three modes each, with a strict 10-day recency filter and engagement ranking. Add an LLM-powered hashtag generator for Mode 2. Update the ralph supervisor loop to classify issues by type and fire a real smoke query after each shipped feature, creating a new blocker issue automatically if the real call fails.

## User Stories

1. **User posts (Mode 1):** As an MCP caller I can request the 10 latest posts from a specific Instagram/Facebook/TikTok account, and receive only posts published within the last 10 days.
2. **Query hashtag trending (Mode 2):** As an MCP caller I can pass a freeform query string and receive the top 10 posts (by likes) ≤ 10 days old, sourced from 10 LLM-generated hashtags scraped across all three platforms.
3. **Global trending (Mode 3):** As an MCP caller I can request globally trending posts per platform and receive the top 10 posts ≤ 10 days old from `#trending` ∪ `#viral` (deduped).
4. **Recency guarantee:** As an MCP caller I always receive posts no older than 10 days; if fewer than 10 pass the filter the tool returns however many exist (0–10).
5. **Reels included:** As an MCP caller, Instagram results include both regular posts (`/p/`) and Reels (`/reel/`).
6. **Real likes for Instagram:** As an MCP caller, Instagram posts returned from hashtag/trending modes carry real like counts (scraped from each post's detail page), not zeroes.
7. **AFK/HITL classification:** As a developer running `ralph/once.sh`, the supervisor receives pre-classified AFK and HITL issue lists so it never attempts human-action tasks autonomously.
8. **Post-ship smoke test:** As a developer, after each issue is shipped the supervisor fires a real query and automatically creates a new blocker issue (AFK or HITL) if the call fails, without retrying.

## Implementation Decisions

- **TikTok source:** `tiktok_api.py` only (has `created_at` unix timestamp for reliable age filter). Playwright TikTok scraper (`tiktok.py`) is not modified.
- **Age filter:** `time.time() - created_at ≤ 864_000` (10 days in seconds). All Post TypedDicts gain a `created_at: int` (unix ts) field. Where timestamp is unavailable, best-effort parsing is used.
- **Instagram timestamp:** Derived from the post shortcode (encodes creation epoch) — no extra HTTP requests.
- **Instagram likes:** Visit each post's detail page to read the real like count (Mode 2 and 3 require this for ranking). Mode 1 (user posts) can keep `likes=0` unless already on detail page.
- **Hashtag generation:** OpenAI (`OPENAI_API_KEY`) generates 10 hashtags from a freeform query. Scrape ~10 posts per hashtag (~100 raw), rank by likes descending, return top 10.
- **Global trending seed:** `#trending` ∪ `#viral` — scrape both, dedup by `post_url`, rank by likes, return top 10.
- **MCP tool shape:** Separate tools per platform per mode (Option A), consistent with existing pattern.
- **Facebook hashtag:** Facebook hashtag pages are in scope (FB does support public hashtag discovery).
- **Engagement metric:** Likes only. Where likes unavailable (IG Mode 1), fall back to recency order.
- **Instagram selector:** `a[href*='/p/'], a[href*='/reel/']` — includes both posts and Reels.
- **`ralph/once.sh`:** Pre-classifies open issues by `## Type` field before invoking supervisor.
- **`ralph/prompt.md`:** Step 5b VERIFY — supervisor fires real smoke call post-commit; on block creates new issue file (AFK or HITL), does not retry.

## Out of Scope

- Stories (Instagram, Facebook) as a separate content format
- Comments, shares, or saves as ranking signals
- Retry logic beyond what already exists
- Result caching
- TikTok Playwright scraper (`scrapers/tiktok.py`) modifications
- Pagination beyond 10 results
- Rate limiting / backoff logic
- Multi-hashtag union for Mode 2 (only 1 LLM-chosen hashtag per scrape call — 10 hashtags × 10 posts)

## Proposed Modules

| File | Action |
|------|--------|
| `scrapers/hashtag_generator.py` | **NEW** — `generate_hashtags(query: str) -> list[str]` via OpenAI |
| `scrapers/instagram.py` | MODIFY — add `scrape_hashtag`, `scrape_trending`; update selector for Reels; add shortcode timestamp decode; add detail-page like scraping |
| `scrapers/facebook.py` | MODIFY — add `scrape_hashtag`, `scrape_trending`; enforce 10-day filter via `<abbr>` timestamp parse |
| `scrapers/tiktok_api.py` | MODIFY — enforce 10-day filter on all three functions |
| `mcp_server/server.py` | MODIFY — add/update MCP tools: `instagram_hashtag_trending`, `instagram_global_trending`, `facebook_hashtag_trending`, `facebook_global_trending`, updated user/page tools with recency filter |
| `ralph/once.sh` | MODIFY — pre-classify AFK vs HITL before supervisor call ✅ done |
| `ralph/prompt.md` | MODIFY — Step 5b VERIFY + blocker issue creation rules ✅ done |
| `tests/test_instagram.py` | MODIFY — tests for new functions and timestamp decode |
| `tests/test_facebook.py` | MODIFY — tests for new functions and timestamp parse |
| `tests/test_hashtag_generator.py` | **NEW** — unit tests for hashtag generation |
