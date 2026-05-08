# [ISSUE-031] Consolidate analyze_image validation + move load_dotenv

**Type:** AFK
**Priority:** warning
**Blocked by:** ISSUE-029

---

## Summary

Two structural issues:

1. `analyze_image` splits validation: URL check in `server.py`, API key check in `image_analysis.py`. Every other tool validates all preconditions in the tool function before calling the scraper. Move `OPENAI_API_KEY` check into the tool function for consistency.

2. `load_dotenv()` runs at import time, polluting `os.environ` during tests. Move into `main()`.

Also: remove unused `import asyncio` and add type annotation to `_HANDLE_RE`.

---

## Acceptance Criteria

- [ ] `OPENAI_API_KEY` check moved from `image_analysis.py` into `analyze_image` tool function in `server.py` (pass api_key as param to `analyze_image_with_vision`)
- [ ] `load_dotenv()` moved from module level into `main()`
- [ ] Unused `import asyncio` removed (or kept only if `__main__` block is retained)
- [ ] `_HANDLE_RE` gets explicit `re.Pattern[str]` type annotation
- [ ] `_validate_limit` docstring gets `Raises:` section
- [ ] Tests updated accordingly
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Review Findings Addressed

- B5: unused `asyncio` import
- W1: split validation on analyze_image
- W2: `load_dotenv()` at import time
- W4: missing type annotation on `_HANDLE_RE`
- W7: `_validate_limit` missing Raises docstring

---

## Files to Modify

| File | Action |
|---|---|
| `mcp_server/server.py` | Move dotenv, remove asyncio, consolidate validation, add annotations |
| `mcp_server/image_analysis.py` | Accept api_key as parameter instead of reading env |
| `tests/test_image_analysis.py` | Update mocks for new signature |
