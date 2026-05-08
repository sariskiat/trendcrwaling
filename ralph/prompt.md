# Implementation Instructions

You are implementing a feature for the trendcrwaling project. Follow these rules strictly.

# WORKFLOW

1. **TDD first** — write failing tests before implementation code
2. **Implement** — make the tests pass
3. **Quality gates** — all must pass before marking complete:
   - `uv run ruff check .` → clean
   - `uv run black --check .` → clean
   - `uv run pytest -x --cov` → all pass, coverage must not decrease

# PATTERNS TO FOLLOW

- Follow the existing scraper patterns in `scrapers/instagram.py` and `scrapers/facebook.py`
- Use Playwright headless browser for scraping
- Cookie auth via env var (Netscape cookies.txt format)
- All failures raise a platform-specific `ScraperError`
- Use `try/finally` to always close the browser
- TypedDict for post data structures
- MCP tools go in `mcp_server/server.py`

# FILES

- Scrapers: `scrapers/`
- Tests: `tests/`
- MCP server: `mcp_server/server.py`
- Dependencies: `pyproject.toml`

# RULES

- Never write code before the failing test exists
- Never leave quality gates red
- One vertical slice at a time — data → logic → API → tests
- ONLY WORK ON A SINGLE TASK PER LOOP ITERATION.
