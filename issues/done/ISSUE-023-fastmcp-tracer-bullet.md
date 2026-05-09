# [ISSUE-023] Rewrite MCP server with FastMCP — tracer bullet (tiktok_user_posts)

**Type:** AFK
**Priority:** tracer-bullet
**Blocked by:** none

---

## Summary

Replace the raw `mcp.server.Server` + manual dispatch in `mcp_server/server.py` with FastMCP decorator pattern. Implement one tool (`tiktok_user_posts`) end-to-end to prove the architecture: typed params, input validation, MCP `isError` responses, `readOnlyHint` annotation, and JSON output. Remove the old `analyze_competitor` combo tool and the manual `list_tools`/`call_tool` handlers entirely.

---

## Acceptance Criteria

- [ ] `mcp_server/server.py` uses `FastMCP` (from `mcp.server.fastmcp`) — no manual `list_tools`/`call_tool`
- [ ] `tiktok_user_posts(username: str, limit: int = 20)` tool registered via `@mcp.tool()` decorator
- [ ] Invalid username returns MCP error response (isError), not a Python exception
- [ ] Invalid limit returns MCP error response
- [ ] Missing `TT_COOKIES_FILE` returns MCP error response with actionable message
- [ ] Tool has `readOnlyHint=True` annotation
- [ ] Old `analyze_competitor` tool removed
- [ ] Old `list_tools`/`call_tool` handlers removed
- [ ] `tests/test_server.py` updated: tests for `tiktok_user_posts` success, bad-input error, missing-cookies error
- [ ] **TDD gate:** failing test first
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Out of Scope

- Other tools (added in subsequent issues)
- Scraper implementation changes
- `analyze_image` (separate issue)

---

## Files to Create / Modify

| File | Action |
|---|---|
| `mcp_server/server.py` | Rewrite with FastMCP, register `tiktok_user_posts` only |
| `tests/test_server.py` | Rewrite tests for new FastMCP server |
| `pyproject.toml` | Ensure `mcp[cli]` dependency is present for FastMCP |
