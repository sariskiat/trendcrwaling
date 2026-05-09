# ISSUE-036: Replace Any with ChatCompletion type annotation

**Type:** AFK
**Priority:** polish
**Blocked by:** nothing

## Problem

`mcp_server/image_analysis.py:31` uses `response: Any` which bypasses type safety.

```python
response: Any = await client.chat.completions.create(...)
```

OpenAI's SDK provides `ChatCompletion` type from `openai.types.chat`.

## Acceptance Criteria

- [ ] Import `ChatCompletion` from `openai.types.chat`
- [ ] Annotate `response: ChatCompletion`
- [ ] `pytest` passes
- [ ] `ruff .` passes
- [ ] `pyright` passes (verify no new type errors)

## Files to Modify

- `mcp_server/image_analysis.py` — import and type annotation

## TDD Gate

Existing tests pass; pyright confirms type correctness.