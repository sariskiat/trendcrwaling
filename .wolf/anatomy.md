# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-05-07T18:19:22.401Z
> Files: 69 tracked | Anatomy hits: 0 | Misses: 0

## ../../.claude/

- `statusline-command.sh` — Claude Code status line — shows token usage prominently (Matt Poccock style). (~389 tok)

## ./

- `.coverage` (~14199 tok)
- `.gitignore` — Git ignore rules (~48 tok)
- `.mcp.json` (~59 tok)
- `.python-version` (~2 tok)
- `CLAUDE.md` — OpenWolf (~120 tok)
- `fb_cookies.txt` — Netscape HTTP Cookie File (~189 tok)
- `login_error.html` — เกิดข้อผิดพลาด (~11001 tok)
- `main.py` — main (~26 tok)
- `pyproject.toml` — Add your description here (~119 tok)
- `pyrightconfig.json` (~28 tok)
- `README.md` — Project documentation (~0 tok)
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

- `prd-facebook-scraper-live.md` — PRD — Facebook Scraper: Live Data via MCP (~709 tok)
- `prd-playwright-facebook-scraper.md` — PRD — Replace facebook-scraper with Playwright (~761 tok)
- `prd-playwright-instagram-scraper.md` — PRD — Replace instagrapi with Playwright for Instagram Scraping (~938 tok)
- `prd-playwright-tiktok-scraper.md` — PRD — Replace tiktokapipy with Playwright for TikTok Scraping (~900 tok)

## issues/

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

## mcp_server/

- `__init__.py` — MCP server exposing Sukishi trend research tools. (~16 tok)
- `server.py` — MCP stdio server exposing analyze_competitor to Claude. (~1633 tok)

## prompts/

- `ralph.md` — Ralph — AFK Implementation Agent (~1002 tok)
- `reviewer.md` — Reviewer — Code Review Agent (~964 tok)

## scrapers/

- `__init__.py` — Public scraper interface — one function per platform. (~132 tok)
- `facebook.py` — Facebook scraper using Playwright headless browser. No API key required. (~1632 tok)
- `instagram.py` — Instagram scraper using Playwright headless browser. No API key required. (~1503 tok)
- `tiktok.py` — TikTok scraper using Playwright headless browser. No API key required. (~1622 tok)

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
- `test_server.py` — Tests for the MCP server tool handler. (~1249 tok)
- `test_tiktok.py` — Tests for the TikTok scraper (Playwright-based). (~1589 tok)
