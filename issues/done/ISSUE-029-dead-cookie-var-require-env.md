# [ISSUE-029] Extract _require_env helper, remove dead cookie_file variable

**Type:** AFK
**Priority:** blocker
**Blocked by:** none

---

## Summary

The `cookie_file` variable is assigned from `os.getenv()` in 5 tool functions but never passed to the scraper — the scraper reads the env var itself. The assignment is dead code. Additionally, the cookie-check boilerplate is duplicated 5 times (~20 lines), pushing `server.py` over the 200-line module limit (currently 224).

Extract a `_require_env(name: str, label: str) -> str` helper to DRY the pattern and bring the module under 200 lines.

---

## Acceptance Criteria

- [ ] `_require_env()` helper extracted in `mcp_server/server.py`
- [ ] Dead `cookie_file` variable removed from all 5 tools — use inline `_require_env()` call
- [ ] Env var names are `Final[str]` module-level constants (not repeated string literals)
- [ ] `server.py` is under 200 lines
- [ ] All existing tests still pass
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Review Findings Addressed

- B1: dead `cookie_file` variable
- B3: 224-line module over 200 cap
- W5: repeated env var string literals
- N1: extract `_require_env()` helper

---

## Files to Modify

| File | Action |
|---|---|
| `mcp_server/server.py` | Extract helper, replace boilerplate, add constants |
