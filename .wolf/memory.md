# Memory

> Chronological action log. Hooks and AI append to this file automatically.
> Old sessions are consolidated by the daemon weekly.

## Session: 2026-05-10 Harness fix

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| — | Fixed AFK reviewer harness behavior | ralph/afk.sh | Enforced close-on-approval fallback and deduped auto-created review issues | ~900 |

## Session: 2026-05-10 PRD-to-issues

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| — | PRD-to-issues from existing PRD | issues/ISSUE-043..ISSUE-050-*.md | 8 vertical-slice issues with tracer bullet first and explicit DAG blockers | ~2600 |

## Session: 2026-05-08

| 15:05 | ISSUE-030 | mcp_server/image_analysis.py, mcp_server/server.py, tests/test_image_analysis.py, issues/done/ISSUE-030-fix-silent-empty-response.md | Raise ValueError for empty OpenAI response; update docstring and tests | ~80 
| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| - | Grill-me session | — | Shared design concept for MCP rebuild | — |
| - | Wrote PRD | docs/prd-rebuild-mcp-server.md | FastMCP rebuild PRD | ~800 |
| - | Created issues 023-028 | issues/ISSUE-023..028-*.md | 6 vertical-slice issues (DAG) | ~3000 |
| - | Created live smoke test | tests/smoke_tiktok.py | Verifies TikTok scrape output shape | ~400 |
| - | Created MCP integration test | tests/integration_mcp.py | NDJSON stdio, init + tools/list | ~600 |
| - | Created CI workflow | .github/workflows/ci.yml | lint + test + integration on push | ~300 |
| - | Added ruff to dev deps | pyproject.toml | CI lint gate | ~10 |
| - | ISSUE-023 | mcp_server/server.py, tests/test_server.py | Rewrote to FastMCP, tiktok_user_posts tracer bullet | ~1500 |
| - | ISSUE-024 | mcp_server/server.py, tests/test_server.py | Added tiktok_trending + tiktok_hashtag_posts | ~800 |
| - | ISSUE-025 | mcp_server/server.py, tests/test_server.py | Added instagram_user_posts tool | ~500 |
| - | ISSUE-026 | mcp_server/server.py, tests/test_server.py | Added facebook_page_posts tool | ~500 |
| - | ISSUE-027 | mcp_server/image_analysis.py, server.py, tests/test_image_analysis.py, pyproject.toml | Added analyze_image tool with OpenAI Vision | ~800 |
| - | ISSUE-028 | README.md | Documented all 6 tools, env vars, planned tools | ~400 |

## Session: 2026-05-07 20:44

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-07 20:53

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-07 20:53

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-07 20:54

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-07 20:54

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-07 21:22

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 21:23 | Edited ../../.claude/statusline-command.sh | 40→40 lines | ~389 |
| 21:23 | Session end: 1 writes across 1 files (statusline-command.sh) | 3 reads | ~979 tok |

## Session: 2026-05-07 23:00

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-07 PRD-to-issues

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| — | PRD-to-issues | issues/ISSUE-016, ISSUE-017, ISSUE-018 | 3 vertical-slice issues from prd-playwright-tiktok-scraper.md; DAG: 016→{017,018} parallel | ~1900 |

## Session: 2026-05-07 23:54

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 23:56 | Created tests/test_tiktok.py | — | ~1589 |
| 23:57 | Created scrapers/tiktok.py | — | ~1622 |
| 23:57 | Edited tests/test_server.py | modified test_analyze_competitor_tiktok_only() | ~63 |
| 23:57 | Edited tests/test_server.py | modified test_analyze_competitor_all_platforms() | ~52 |
| 23:57 | Edited tests/test_server.py | modified test_analyze_competitor_skips_unselected_platforms() | ~364 |
| 23:57 | Edited mcp_server/server.py | added 1 import(s) | ~56 |
| 23:57 | Edited mcp_server/server.py | modified list_tools() | ~612 |
| 23:57 | Edited mcp_server/server.py | modified call_tool() | ~435 |
| 23:57 | Edited pyproject.toml | 13→12 lines | ~72 |
| 00:29 | Edited tests/test_server.py | added 1 import(s) | ~231 |
| 01:18 | Edited tests/test_server.py | added 1 import(s) | ~103 |
| 01:19 | Edited tests/test_server.py | 2→2 lines | ~35 |
| 01:19 | Edited tests/test_server.py | modified test_scrape_tiktok_user_tool_dispatch() | ~216 |
| 01:19 | Edited tests/test_server.py | 2→2 lines | ~35 |
| 01:19 | Edited tests/test_server.py | modified patch() | ~112 |
| 01:19 | Edited tests/test_server.py | 6→5 lines | ~36 |

## Session: 2026-05-08

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| — | ISSUE-020: gitignore wildcard | .gitignore | fb_cookies.txt → *_cookies.txt; already untracked | ~48 |
| — | ISSUE-021: MCP input validation | mcp_server/server.py, tests/test_server.py | Added _validate_handle, _validate_limit; applied in call_tool for all 4 tools; 5 new tests, 12/12 pass | ~200 |

## Session: 2026-05-08 ISSUE-022

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| — | ISSUE-022: try/finally browser cleanup | scrapers/facebook.py, tests/test_facebook.py | Wrapped _extract_posts in try/finally for browser.close(); added test_scrape_page_closes_browser_on_exception; 8/8 pass | ~150 |

## Session: 2026-05-08 14:55

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-08 14:56

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-08 14:59

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 17:09 | Session end: 16 writes across 5 files (test_tiktok.py, tiktok.py, test_server.py, server.py, pyproject.toml) | 8 reads | ~12721 tok |

## Session: 2026-05-08 17:17

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 17:22 | Created .mcp.json | — | ~100 |
| 17:23 | Created .mcp.json | — | ~48 |
| 18:13 | Session end: 2 writes across 1 files (.mcp.json) | 6 reads | ~1839 tok |
| 18:26 | Session end: 2 writes across 1 files (.mcp.json) | 6 reads | ~1839 tok |
| 18:35 | Session end: 2 writes across 1 files (.mcp.json) | 7 reads | ~1839 tok |
| 18:39 | Session end: 2 writes across 1 files (.mcp.json) | 7 reads | ~1839 tok |
| 18:42 | Edited scrapers/tiktok.py | 1→2 lines | ~34 |
| 18:43 | Edited scrapers/tiktok.py | modified _cookie_file() | ~116 |
| 18:44 | Edited scrapers/tiktok.py | inline fix | ~20 |
| 18:49 | Created docs/prd-tiktok-alternatives.md | — | ~1048 |

## Session: 2026-05-08 18:50

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-08 18:50

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 18:54 | Created issues/ISSUE-038-tiktok-api-scraper-tracer-bullet.md | — | ~456 |
| 18:54 | Created issues/ISSUE-039-tikapi-io-scraper.md | — | ~396 |
| 18:54 | Created issues/ISSUE-040-apify-clockworks-scraper.md | — | ~406 |
| 18:54 | Created issues/ISSUE-041-add-trending-hashtag-to-tiktok-scrapers.md | — | ~488 |
| 18:54 | Created issues/ISSUE-042-tiktok-source-config-and-docs.md | — | ~372 |
| 18:54 | Session end: 5 writes across 5 files (ISSUE-038-tiktok-api-scraper-tracer-bullet.md, ISSUE-039-tikapi-io-scraper.md, ISSUE-040-apify-clockworks-scraper.md, ISSUE-041-add-trending-hashtag-to-tiktok-scrapers.md, ISSUE-042-tiktok-source-config-and-docs.md) | 2 reads | ~4842 tok |
| 19:59 | Edited ralph/once.sh | expanded (+10 lines) | ~208 |
| 20:00 | Session end: 6 writes across 6 files (ISSUE-038-tiktok-api-scraper-tracer-bullet.md, ISSUE-039-tikapi-io-scraper.md, ISSUE-040-apify-clockworks-scraper.md, ISSUE-041-add-trending-hashtag-to-tiktok-scrapers.md, ISSUE-042-tiktok-source-config-and-docs.md) | 9 reads | ~9542 tok |

## Session: 2026-05-08 20:01

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 21:21 | Created tests/test_tiktok_api.py | — | ~1958 |
| 21:22 | Created scrapers/tiktok_api.py | — | ~1069 |
| 21:22 | Edited mcp_server/server.py | added 1 import(s) | ~133 |
| 21:23 | Edited mcp_server/server.py | modified tiktok_hashtag_posts() | ~302 |
| 21:23 | Edited tests/test_server.py | modified test_tiktok_hashtag_posts_missing_cookies() | ~1084 |
| 21:23 | Edited tests/test_server.py | modified test_all_tools_registered() | ~193 |
| 21:25 | Edited scrapers/tiktok_api.py | 6→8 lines | ~68 |
| 21:26 | Created tests/test_tiktok_api.py | — | ~1978 |
| 21:30 | Session end: 8 writes across 4 files (test_tiktok_api.py, tiktok_api.py, server.py, test_server.py) | 14 reads | ~22426 tok |
| 21:33 | Edited ralph/afk.sh | expanded (+36 lines) | ~604 |
| 21:33 | Session end: 9 writes across 5 files (test_tiktok_api.py, tiktok_api.py, server.py, test_server.py, afk.sh) | 18 reads | ~23601 tok |
| 21:34 | Created tests/test_tiktok_tikapi.py | — | ~1597 |
| 21:34 | Created scrapers/tiktok_tikapi.py | — | ~1060 |

## Session: 2026-05-08 21:35

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 21:35 | Created tests/test_tiktok_tikapi.py | — | ~1684 |
| 21:36 | Edited mcp_server/server.py | added 1 import(s) | ~157 |
| 21:36 | Edited mcp_server/server.py | modified tiktok_user_posts_api() | ~306 |
| 21:37 | Edited tests/test_server.py | modified test_tiktok_user_posts_api_config_error_propagates() | ~953 |
| 21:37 | Edited tests/test_server.py | modified test_all_tools_registered() | ~203 |
| 21:41 | Created tests/test_tiktok_apify.py | — | ~1312 |
| 21:42 | Created scrapers/tiktok_apify.py | — | ~1037 |
| 21:42 | Edited mcp_server/server.py | added 1 import(s) | ~48 |
| 21:42 | Edited mcp_server/server.py | modified tiktok_user_posts_tikapi() | ~271 |
| 21:43 | Edited tests/test_server.py | modified test_tiktok_user_posts_apify_success() | ~361 |
| 21:44 | Edited tests/test_server.py | modified test_all_tools_registered() | ~131 |
| 21:46 | Edited scrapers/tiktok_apify.py | 11→14 lines | ~185 |
| 21:47 | Edited tests/test_tiktok_api.py | 5→7 lines | ~40 |
| 21:48 | Edited tests/test_tiktok_api.py | modified _make_trending_mocks() | ~2485 |
| 21:48 | Edited scrapers/tiktok_api.py | 5→7 lines | ~37 |
| 21:49 | Edited scrapers/tiktok_api.py | modified scrape_trending() | ~1508 |
| 21:49 | Edited tests/test_tiktok_tikapi.py | 5→7 lines | ~39 |
| 21:50 | Edited tests/test_tiktok_tikapi.py | modified test_scrape_trending_raises_not_implemented() | ~268 |
| 21:50 | Edited scrapers/tiktok_tikapi.py | 5→7 lines | ~35 |
| 21:50 | Edited scrapers/tiktok_tikapi.py | modified scrape_trending() | ~407 |
| 21:51 | Edited tests/test_tiktok_tikapi.py | modified test_scrape_trending_raises_not_implemented() | ~247 |
| 21:51 | Edited tests/test_tiktok_apify.py | 5→7 lines | ~42 |
| 21:52 | Edited tests/test_tiktok_apify.py | modified test_scrape_user_wraps_http_errors() | ~456 |
| 21:52 | Edited scrapers/tiktok_apify.py | 5→7 lines | ~38 |
| 21:53 | Edited scrapers/tiktok_apify.py | modified scrape_trending() | ~412 |
| 21:53 | Edited mcp_server/server.py | added 6 import(s) | ~265 |
| 21:54 | Edited mcp_server/server.py | modified tiktok_user_posts_apify() | ~1030 |
| 21:54 | Edited tests/test_server.py | modified test_all_tools_registered() | ~268 |
| 22:00 | ISSUE-041 | scrapers/tiktok_api.py, tiktok_tikapi.py, tiktok_apify.py, tests/test_tiktok_api.py, test_tiktok_tikapi.py, test_tiktok_apify.py, mcp_server/server.py, tests/test_server.py | Added scrape_trending/scrape_hashtag to all 3 TikTok scrapers (TikTok-Api functional, TikAPI/Apify raise NotImplementedError); 6 new MCP tools; 10 new tests; all gates pass | ~3500 |
| 21:56 | Edited tests/test_server.py | modified test_tiktok_trending_api_success() | ~2149 |
| 21:57 | Edited tests/test_server.py | modified test_all_tools_registered() | ~39 |
| 22:00 | Edited README.md | expanded (+14 lines) | ~204 |
| 22:00 | Edited README.md | 8→12 lines | ~198 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_user_posts() | ~152 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_trending() | ~122 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_hashtag_posts() | ~129 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_user_posts_api() | ~115 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_user_posts_tikapi() | ~122 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_user_posts_apify() | ~125 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_trending_api() | ~109 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_trending_tikapi() | ~156 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_trending_apify() | ~157 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_hashtag_api() | ~113 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_hashtag_tikapi() | ~160 |
| 22:01 | Edited mcp_server/server.py | modified tiktok_hashtag_apify() | ~161 |
| 22:03 | Session end: 44 writes across 9 files (test_tiktok_tikapi.py, server.py, test_server.py, test_tiktok_apify.py, tiktok_apify.py) | 17 reads | ~46456 tok |
| 22:06 | Session end: 44 writes across 9 files (test_tiktok_tikapi.py, server.py, test_server.py, test_tiktok_apify.py, tiktok_apify.py) | 18 reads | ~46456 tok |
| 22:06 | Session end: 44 writes across 9 files (test_tiktok_tikapi.py, server.py, test_server.py, test_tiktok_apify.py, tiktok_apify.py) | 18 reads | ~46456 tok |
| 22:06 | Session end: 44 writes across 9 files (test_tiktok_tikapi.py, server.py, test_server.py, test_tiktok_apify.py, tiktok_apify.py) | 18 reads | ~46456 tok |

## Session: 2026-05-08 22:08

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 13:54 | Edited .mcp.json | inline fix | ~75 |
| 13:54 | Session end: 1 writes across 1 files (.mcp.json) | 1 reads | ~123 tok |
| 13:58 | Session end: 1 writes across 1 files (.mcp.json) | 3 reads | ~5135 tok |
| 14:04 | Edited .mcp.json | inline fix | ~98 |
| 14:04 | Session end: 2 writes across 1 files (.mcp.json) | 3 reads | ~5260 tok |
| 14:08 | Edited scrapers/tiktok_api.py | 3→3 lines | ~50 |
| 14:08 | Edited scrapers/tiktok_api.py | modified TikTokApiPost() | ~72 |
| 14:11 | Edited scrapers/tiktok_api.py | 31→35 lines | ~445 |
| 14:12 | Edited scrapers/tiktok_api.py | 31→35 lines | ~444 |
| 14:14 | Session end: 6 writes across 2 files (.mcp.json, tiktok_api.py) | 3 reads | ~6337 tok |
| 14:16 | Edited scrapers/tiktok_api.py | added 1 import(s) | ~43 |
| 14:17 | Edited scrapers/tiktok_api.py | modified scrape_user() | ~268 |
| 14:19 | Created scrapers/tiktok_api.py | — | ~2137 |
| 14:21 | Edited mcp_server/server.py | modified tiktok_user_posts_api() | ~242 |
| 14:21 | Edited mcp_server/server.py | modified tiktok_trending_api() | ~206 |
| 14:21 | Edited mcp_server/server.py | modified tiktok_hashtag_api() | ~238 |
| 14:24 | Edited scrapers/tiktok_api.py | 3→3 lines | ~46 |
| 14:25 | Session end: 13 writes across 3 files (.mcp.json, tiktok_api.py, server.py) | 4 reads | ~13491 tok |
| 14:26 | Session end: 13 writes across 3 files (.mcp.json, tiktok_api.py, server.py) | 4 reads | ~13491 tok |

## Session: 2026-05-09 14:28

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 14:34 | Edited .gitignore | expanded (+8 lines) | ~82 |
| 14:35 | Session end: 1 writes across 1 files (.gitignore) | 6 reads | ~5167 tok |

## Session: 2026-05-09 14:43

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
| 14:53 | Edited scrapers/tiktok_api.py | 21→22 lines | ~135 |
| 14:53 | Edited scrapers/tiktok_api.py | modified scrape_user() | ~507 |
| 14:53 | Edited scrapers/tiktok_api.py | modified scrape_trending() | ~460 |
| 14:53 | Edited scrapers/tiktok_api.py | modified scrape_hashtag() | ~482 |
| 14:54 | Edited mcp_server/server.py | modified tiktok_user_posts_api() | ~270 |
| 14:54 | Edited mcp_server/server.py | modified tiktok_trending_api() | ~234 |
| 14:54 | Edited mcp_server/server.py | modified tiktok_hashtag_api() | ~266 |
| 14:56 | Session end: 7 writes across 2 files (tiktok_api.py, server.py) | 3 reads | ~4588 tok |
| 14:58 | Edited scrapers/tiktok_api.py | modified _extract_post() | ~188 |
| 14:59 | Session end: 8 writes across 2 files (tiktok_api.py, server.py) | 4 reads | ~9357 tok |
| 15:13 | Session end: 8 writes across 2 files (tiktok_api.py, server.py) | 4 reads | ~9357 tok |
| 15:15 | Edited scrapers/tiktok_api.py | modified videos() | ~159 |
| 15:15 | Edited scrapers/tiktok_api.py | modified videos() | ~138 |
| 15:15 | Edited scrapers/tiktok_api.py | modified videos() | ~149 |
| 15:15 | Edited scrapers/tiktok_api.py | 300() → seconds() | ~213 |
| 15:15 | Edited scrapers/tiktok_api.py | 300() → seconds() | ~188 |
| 15:15 | Edited scrapers/tiktok_api.py | 300() → seconds() | ~208 |

## Session: 2026-05-09 15:27

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-09 15:39

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|

## Session: 2026-05-09 15:39

| Time | Action | File(s) | Outcome | ~Tokens |
|------|--------|---------|---------|--------|
