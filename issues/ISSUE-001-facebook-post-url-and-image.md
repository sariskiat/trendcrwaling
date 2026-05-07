# [ISSUE-001] Add post_url and image_url to Facebook scraper

**Type:** `AFK`
**Priority:** `tracer-bullet`
**Blocked by:** `none`
**Blocks:** ISSUE-002
**Module(s):** `scrapers/facebook.py`, `tests/test_facebook.py`

---

## Context

`FacebookPost` currently returns only `text`, `likes`, and `time`. The user needs post links and image URLs to reference posts and analyse visual content via the `analyze_competitor` MCP tool. The `facebook-scraper` library already returns both fields (`post_url` and `image` keys) — they just aren't being extracted.

## What to build

### 1. `scrapers/facebook.py`

Add two fields to the `FacebookPost` TypedDict:
- `post_url: str` — the direct URL to the Facebook post (from `post.get("post_url")`)
- `image_url: str` — the main image URL for the post (from `post.get("image")`)

Update `scrape_page` to extract these fields. Both default to `""` if missing (consistent with the existing `text` and `time` defaults).

### 2. `tests/test_facebook.py`

Follow TDD — write failing tests first, then make them pass:

- Update `test_scrape_page_returns_structured_posts` to assert `post_url` and `image_url` are present in the result
- Update `test_scrape_page_handles_missing_fields` to assert both new fields default to `""`
- Add mock post data with `post_url` and `image` keys in all relevant test fixtures

## Acceptance criteria

- [ ] Failing tests written **before** any implementation change (TDD — non-negotiable)
- [ ] `FacebookPost` TypedDict has `post_url: str` and `image_url: str`
- [ ] `scrape_page` extracts `post_url` from `post.get("post_url")`, defaults to `""`
- [ ] `scrape_page` extracts `image_url` from `post.get("image")`, defaults to `""`
- [ ] All existing tests still pass
- [ ] `test_scrape_page_returns_structured_posts` asserts `post_url` and `image_url` values
- [ ] `test_scrape_page_handles_missing_fields` asserts both default to `""`
- [ ] `uv run ruff check .` passes
- [ ] `uv run pytest -x` passes

## Out of scope

- Not in this issue: Instagram or TikTok scrapers
- Not in this issue: Facebook authentication / credentials
- Not in this issue: MCP server code changes (server already passes through whatever `scrape_facebook` returns)
- Not in this issue: Live end-to-end test against real Facebook (that is ISSUE-002)

## Notes

The `facebook-scraper` library returns `post_url` directly. The image key is `"image"` (a single URL string, not `"images"`). Both are confirmed present in `facebook_scraper/extractors.py`.

The MCP server at `mcp_server/server.py` calls `scrape_facebook` which calls `scrape_page` — no server changes are needed; the enriched `FacebookPost` dicts flow through automatically.
