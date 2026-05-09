# [ISSUE-033] Add custom exception hierarchy

**Type:** AFK
**Priority:** warning
**Blocked by:** ISSUE-029

---

## Summary

All error paths raise raw `ValueError`. Callers cannot distinguish "invalid handle" from "missing env var" from "empty OpenAI response" by type — only by string matching. Define a base `MCPServerError` with subtypes.

Note: FastMCP catches exceptions and wraps them as `isError=True`. Custom exceptions should inherit from both the base and `ValueError` to maintain FastMCP compatibility.

---

## Acceptance Criteria

- [ ] Base `MCPServerError(ValueError)` defined
- [ ] `ValidationError(MCPServerError)` for handle/limit/URL validation
- [ ] `ConfigurationError(MCPServerError)` for missing env vars
- [ ] `AnalysisError(MCPServerError)` for empty OpenAI responses
- [ ] All `raise ValueError(...)` calls replaced with appropriate subtypes
- [ ] Tests updated to match on specific exception types (still passes `ValueError` isinstance check)
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Review Findings Addressed

- W6: no custom app exception hierarchy

---

## Files to Modify

| File | Action |
|---|---|
| `mcp_server/server.py` | Define exceptions, use in tool functions |
| `mcp_server/image_analysis.py` | Use `ConfigurationError`, `AnalysisError` |
| `tests/test_server.py` | Optionally tighten exception type assertions |
| `tests/test_image_analysis.py` | Optionally tighten exception type assertions |
