# Cerebrum

> OpenWolf's learning memory. Updated automatically as the AI learns from interactions.
> Do not edit manually unless correcting an error.
> Last updated: 2026-05-07

## User Preferences

<!-- How the user likes things done. Code style, tools, patterns, communication. -->

## Key Learnings

- **Project:** trendcrwaling
- **TikTok Scraper Pattern:** Replaced tiktokapipy with Playwright. Uses same pattern as Instagram scraper: _COOKIE_ENV, _load_cookies, _setup_browser with networkidle wait, _extract_posts with page.evaluate(), try/finally for browser.close(). TikTokPost now includes views (int), thumbnail_url (str), author (str) fields. Cookie auth via TT_COOKIES_FILE env var.
- **Workflow Convention:** For `/saris-skill:prd-to-issues`, generate numbered markdown issues directly under `issues/` with tracer-bullet first, explicit `Blocked by` DAG, AFK/HITL type, and TDD acceptance criteria.
- **Harness Convention:** AFK harness must enforce issue closure after reviewer APPROVED and must dedupe auto-created review-violation issues to prevent convergence loops.

## Do-Not-Repeat

<!-- Mistakes made and corrected. Each entry prevents the same mistake recurring. -->
<!-- Format: [YYYY-MM-DD] Description of what went wrong and what to do instead. -->
- [2026-05-08] Never interpolate user input into JS f-strings passed to page.evaluate(). Assign user-controlled values in Python after evaluate returns.

## Decision Log

<!-- Significant technical decisions with rationale. Why X was chosen over Y. -->
- [2026-05-07] TikTok scraper: Playwright replaces tiktokapipy. Three entry points (user, trending, hashtag). Auth via TT_COOKIES_FILE env var. MCP gets three dedicated tools instead of one.
