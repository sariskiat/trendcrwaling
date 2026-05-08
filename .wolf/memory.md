# Memory

> Chronological action log. Hooks and AI append to this file automatically.
> Old sessions are consolidated by the daemon weekly.

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
