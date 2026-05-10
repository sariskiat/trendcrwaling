# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-09T08:15:36.564Z
> Files: 83 tracked | Anatomy hits: 0 | Misses: 0

## ../../.claude/

- `statusline-command.sh` — Claude Code status line — shows token usage prominently (Matt Poccock style). (~389 tok)

## ./

- `.coverage` (~14199 tok)
- `.gitignore` — Git ignore rules (~82 tok)
- `.mcp.json` (~98 tok)
- `.python-version` (~2 tok)
- `CLAUDE.md` — OpenWolf (~120 tok)
- `fb_cookies.txt` — Netscape HTTP Cookie File (~189 tok)
- `login_error.html` — เกิดข้อผิดพลาด (~11001 tok)
- `main.py` — main (~26 tok)
- `pyproject.toml` — Add your description here (~119 tok)
- `pyrightconfig.json` (~28 tok)
- `README.md` — Project documentation (~908 tok)
- `STATUS.md` — Project Status (~405 tok)

## .claude/

- `settings.json` (~563 tok)
- `settings.local.json` (~864 tok)

## .claude/hooks/

- `guard_rm.py` — PreToolUse hook: blocks rm commands targeting paths outside the repo. (~212 tok)

## .claude/rules/

- `openwolf.md` (~313 tok)

## .pytest_cache/

- `.gitignore` — Git ignore rules (~10 tok)
- `CACHEDIR.TAG` (~51 tok)
- `README.md` — Project documentation (~76 tok)

## .pytest_cache/v/cache/

- `lastfailed` (~1 tok)
- `nodeids` (~573 tok)

## .ruff_cache/

- `.gitignore` — Git ignore rules (~10 tok)
- `CACHEDIR.TAG` (~12 tok)

## .ruff_cache/0.15.5/

- `11320122088085669201` (~24 tok)
- `11804482675482816010` (~31 tok)
- `11959544369576891989` (~30 tok)
- `15391937647139450588` (~60 tok)
- `4798576694490546382` (~48 tok)

## docs/

- `prd-social-allthree-modes.md` — PRD — Social All-Three: 3 Modes x 3 Platforms (~1300 tok)
- `prd-facebook-scraper-live.md` — PRD — Facebook Scraper: Live Data via MCP (~709 tok)
- `prd-playwright-facebook-scraper.md` — PRD — Replace facebook-scraper with Playwright (~761 tok)
- `prd-playwright-instagram-scraper.md` — PRD — Replace instagrapi with Playwright for Instagram Scraping (~938 tok)
- `prd-playwright-tiktok-scraper.md` — PRD — Replace tiktokapipy with Playwright for TikTok Scraping (~900 tok)
- `prd-tiktok-alternatives.md` — PRD — TikTok Scraping Alternatives (~983 tok)

## issues/

- `ISSUE-043-instagram-global-trending-tracer-bullet.md` — [ISSUE-043] Ship Instagram global trending tracer bullet (~360 tok)
- `ISSUE-044-instagram-query-hashtag-trending-with-real-likes.md` — [ISSUE-044] Add Instagram query hashtag trending with real likes (~410 tok)
- `ISSUE-045-facebook-three-modes-with-recency.md` — [ISSUE-045] Implement Facebook three modes with 10-day recency (~395 tok)
- `ISSUE-046-tiktok-api-three-modes-recency-contract.md` — [ISSUE-046] Enforce TikTok API three-mode recency contract end-to-end (~320 tok)
- `ISSUE-047-create-llm-hashtag-generator-module.md` — [ISSUE-047] Create reusable LLM hashtag generator module (~300 tok)
- `ISSUE-048-expose-complete-instagram-facebook-mode-tools.md` — [ISSUE-048] Expose complete Instagram/Facebook mode tools in MCP (~280 tok)
- `ISSUE-049-automate-afk-hitl-classification-and-post-ship-smoke.md` — [ISSUE-049] Automate AFK/HITL classification and post-ship smoke blocking (~300 tok)
- `ISSUE-050-run-hitl-credentialed-smoke-and-close-loop.md` — [ISSUE-050] Run HITL credentialed smoke and close loop (~300 tok)
- `ISSUE-001-facebook-post-url-and-image.md` — [ISSUE-001] Add post_url and image_url to Facebook scraper (~671 tok)
- `ISSUE-002-verify-mcp-returns-real-facebook-posts.md` — [ISSUE-002] Verify MCP tool returns real Facebook posts (~453 tok)
- `ISSUE-003-fix-facebook-scraper-cookie-auth.md` — [ISSUE-003] Fix facebook-scraper: switch from credentials to browser cookies (~725 tok)
- `ISSUE-004-playwright-facebook-scraper.md` — [ISSUE-004] Replace facebook-scraper with Playwright (~923 tok)
- `ISSUE-005-verify-playwright-facebook-live.md` — [ISSUE-005] Verify Playwright scraper returns real Facebook posts (~390 tok)
- `ISSUE-006-any-type-in-test-facebook.md` — [ISSUE-006] Remove `Any` type from test_facebook.py (~353 tok)
- `ISSUE-007-scrape-page-exceeds-30-line-limit.md` — [ISSUE-007] Split `scrape_page` — exceeds 30-line function limit (~464 tok)
- `ISSUE-008-type-ignore-suppressions.md` — [ISSUE-008] Replace `# type: ignore` suppressions with correct types (~501 tok)
- `ISSUE-009-facebookpost-missing-fields-in-test-server.md` — [ISSUE-009] `FacebookPost` constructed without required fields in test_server.py (~416 tok)
- `ISSUE-010-add-black-and-pytest-cov-dev-deps.md` — [ISSUE-010] Add `black` and `pytest-cov` to dev dependencies (~346 tok)
- `ISSUE-011-playwright-instagram-scraper.md` — [ISSUE-011] Replace instagrapi with Playwright in scrapers/instagram.py (~1136 tok)
- `ISSUE-012-wire-instagram-playwright-to-mcp.md` — [ISSUE-012] Wire Playwright Instagram scraper into MCP server and remove instagrapi (~606 tok)
- `ISSUE-013-close-browser-on-exception-path.md` — [ISSUE-013] Close browser on exception path in scrape_user (~469 tok)
- `ISSUE-014-type-annotate-module-constants.md` — [ISSUE-014] Add type annotations to module-level constants in scrapers/instagram.py (~354 tok)
- `ISSUE-015-type-annotate-ctx-in-setup-browser.md` — [ISSUE-015] Add BrowserContext type annotation to ctx in _setup_browser (~340 tok)
- `ISSUE-016-playwright-tiktok-scrape-user.md` — [ISSUE-016] Replace tiktokapipy with Playwright for scrape_user + add scrape_tiktok_user MCP tool (~923 tok)
- `ISSUE-017-tiktok-scrape-trending.md` — [ISSUE-017] Add scrape_trending entry point and scrape_tiktok_trending MCP tool (~500 tok)
- `ISSUE-018-tiktok-scrape-hashtag.md` — [ISSUE-018] Add scrape_hashtag entry point and scrape_tiktok_hashtag MCP tool (~500 tok)
- `ISSUE-038-tiktok-api-scraper-tracer-bullet.md` — [ISSUE-038] Implement TikTok-Api scraper (tracer bullet) (~428 tok)
- `ISSUE-039-tikapi-io-scraper.md` — [ISSUE-039] Implement TikAPI.io scraper (~372 tok)
- `ISSUE-040-apify-clockworks-scraper.md` — [ISSUE-040] Implement Apify Clockworks scraper (~381 tok)
- `ISSUE-041-add-trending-hashtag-to-tiktok-scrapers.md` — [ISSUE-041] Add trending and hashtag endpoints to TikTok scrapers (~457 tok)
- `ISSUE-042-tiktok-source-config-and-docs.md` — [ISSUE-042] Add TIKTOK_SOURCE environment variable and documentation (~349 tok)

## mcp_server/

- `__init__.py` — MCP server exposing Sukishi trend research tools. (~16 tok)
- `server.py` — MCP stdio server using FastMCP decorator pattern. (~4039 tok)

## prompts/

- `ralph.md` — Ralph — AFK Implementation Agent (~1002 tok)
- `reviewer.md` — Reviewer — Code Review Agent (~964 tok)

## ralph/

- `afk.sh` — ralph/afk.sh — looped AFK run with parallel Opus reviewers each iteration (~604 tok)
- `once.sh` — ralph/once.sh — single AFK run (Sonnet supervisor + Haiku implementer) (~208 tok)

## scrapers/

- `__init__.py` — Public scraper interface — one function per platform. (~132 tok)
- `facebook.py` — Facebook scraper using Playwright headless browser. No API key required. (~1632 tok)
- `instagram.py` — Instagram scraper using Playwright headless browser. No API key required. (~1503 tok)
- `tiktok_api.py` — TikTok scraper using TikTok-Api library (davidteather). (~2306 tok)
- `tiktok_apify.py` — TikTok scraper using Apify Clockworks API. (~1504 tok)
- `tiktok_tikapi.py` — TikTok scraper using TikAPI.io REST API. (~1476 tok)
- `tiktok.py` — TikTok scraper using Playwright headless browser. No API key required. (~2416 tok)

## scripts/

- `loop.sh` — loop.sh — run Ralph in a continuous AFK loop until the backlog is empty (~1688 tok)
- `once.sh` — once.sh — run Ralph exactly once for AFK calibration (~1474 tok)

## templates/

- `issue.md` — [ISSUE-000] Title (~296 tok)
- `prd.md` — PRD — [Feature Name] (~397 tok)
- `PULL_REQUEST_TEMPLATE.md` — Type (~293 tok)

## tests/

- `__init__.py` — Tests for trendcrwaling. (~9 tok)
- `test_facebook.py` — Tests for the Facebook scraper (Playwright-based). (~1491 tok)
- `test_instagram.py` — Tests for the Instagram scraper (Playwright-based). (~1628 tok)
- `test_server.py` — Tests for the FastMCP-based MCP server. (~10000 tok)
- `test_tiktok_api.py` — Tests for the TikTok-Api library scraper. (~4463 tok)
- `test_tiktok_apify.py` — Tests for the Apify Clockworks TikTok scraper. (~1565 tok)
- `test_tiktok_tikapi.py` — Tests for the TikAPI.io scraper. (~1990 tok)
- `test_tiktok.py` — Tests for the TikTok scraper (Playwright-based). (~1589 tok)
