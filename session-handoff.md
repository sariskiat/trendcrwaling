# Session Handoff — ISSUE-048: Expose complete Instagram/Facebook mode tools in MCP
Date: 2026-05-12

## Rounds

### Round 1 — Review

**Reviewer:** claude-sonnet-4-6

**Gates checked:** hard-gates, implementation-philosophy, code-standards

**Defects found and fixed before approval:**

1. **Hard Gate 1 — Missing type annotations on `posts`, `deduped`, `sorted_posts` in 4 new tools.** All four new tools (`instagram_global_trending`, `instagram_hashtag_trending`, `facebook_hashtag_trending`, `facebook_global_trending`) used bare `posts = await ...` with no explicit type annotation. Fixed to `posts: list[InstagramPost] = ...` / `list[FacebookPost]` matching the established pattern in all TikTok tools.

2. **Code Standards — Deferred local import in `instagram_global_trending`.** The function used `from scrapers.instagram import scrape_trending` inside the function body instead of a module-level aliased import matching the project convention (`_scrape_*` prefix). Fixed by adding `scrape_trending as _scrape_instagram_trending` to the top-level `scrapers.instagram` import block and updating the call site.

3. **Test — Mock path broken after import fix.** The existing `test_instagram_global_trending_tool` patched `scrapers.instagram.scrape_trending` (the deferred-import lookup path), which no longer works once the import was promoted to module level. Fixed mock path to `mcp_server.server._scrape_instagram_trending`.

4. **Documentation — Stale docstring in test.** `test_all_tools_registered` docstring said "18 MCP tools" but the expected set contains 20. Fixed to "20".

**Result:** All 4 defects fixed. 183 tests pass. `bash init.sh` green.

**Decision:** APPROVED

## What Was Accomplished

ISSUE-048 is complete. All 6 required MCP tools (`instagram_user_posts`, `instagram_hashtag_trending`, `instagram_global_trending`, `facebook_page_posts`, `facebook_hashtag_trending`, `facebook_global_trending`) are registered in `mcp_server/server.py` with:

- Full input validation via `_validate_handle`, `_validate_limit`, `_require_env`
- Explicit type annotations on all local variables (`posts`, `deduped`, `sorted_posts`)
- Deduplication by `post_url`
- Sorting by likes desc with `created_at` fallback
- Recency filtering via `max_age_days=10`
- Return value as `json.dumps(..., ensure_ascii=False, indent=2)`

All 183 tests pass. The tool registration smoke test (`test_all_tools_registered`) now verifies all 20 MCP tools by name.
