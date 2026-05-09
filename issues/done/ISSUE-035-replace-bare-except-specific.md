# ISSUE-035: Replace bare except with specific exception handling

**Type:** AFK
**Priority:** polish
**Blocked by:** nothing

## Problem

`mcp_server/image_analysis.py:46-49` catches bare `Exception` which swallows `IndexError`, `AttributeError`, and any other exception type without distinction.

```python
try:
    content = response.choices[0].message.content
except Exception:
    content = None
```

## Acceptance Criteria

- [ ] Catch specific exceptions: `(IndexError, AttributeError)`
- [ ] `pytest` passes
- [ ] `ruff .` passes
- [ ] `pyright` passes

## Files to Modify

- `mcp_server/image_analysis.py` — line 46-49

## TDD Gate

Existing test for empty OpenAI response should still pass after the change.