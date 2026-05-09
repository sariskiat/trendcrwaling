# [ISSUE-028] Update README with tool documentation and planned tools

**Type:** AFK
**Priority:** polish
**Blocked by:** ISSUE-024, ISSUE-025, ISSUE-026, ISSUE-027

---

## Summary

Update `README.md` to document all available MCP tools, their parameters, required env vars, and list planned tools (`instagram_recent_posts`, `facebook_recent_posts`) as future work.

---

## Acceptance Criteria

- [ ] README lists all 6 tools with parameter descriptions
- [ ] README lists required env vars: `TT_COOKIES_FILE`, `IG_COOKIES_FILE`, `FB_COOKIES_FILE`, `OPENAI_API_KEY`
- [ ] README has a "Planned Tools" section listing `instagram_recent_posts` and `facebook_recent_posts`
- [ ] README includes how to run the server (`uv run mcp_server/server.py` or equivalent)
- [ ] **TDD gate:** N/A (documentation only)
- [ ] Quality gates: `uv run pytest` (no regressions)

---

## Out of Scope

- Implementation of planned tools
- Detailed API docs (tool descriptions in MCP are sufficient)

---

## Files to Create / Modify

| File | Action |
|---|---|
| `README.md` | Rewrite with tool docs, env vars, planned tools |
