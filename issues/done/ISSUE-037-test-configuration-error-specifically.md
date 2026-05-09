# ISSUE-037: Update _require_env test to validate ConfigurationError

**Type:** AFK
**Priority:** polish
**Blocked by:** nothing

## Problem

`tests/test_require_env_helper.py:26` expects `ValueError` but `_require_env` raises `ConfigurationError`. While `ConfigurationError` inherits from `ValueError` (so the test passes), the test should validate the *specific* exception type to properly test the new exception hierarchy.

```python
# Current: matches ValueError (base class)
with pytest.raises(ValueError, match="..."):

# Should be: matches ConfigurationError (specific type)
from mcp_server.exceptions import ConfigurationError
with pytest.raises(ConfigurationError, match="..."):
```

## Acceptance Criteria

- [ ] Test imports `ConfigurationError` from `mcp_server.exceptions`
- [ ] Test uses `pytest.raises(ConfigurationError, ...)`
- [ ] `pytest` passes
- [ ] `ruff .` passes

## Files to Modify

- `tests/test_require_env_helper.py`

## TDD Gate

Test fails if `_require_env` raises a different exception type (not `ConfigurationError`).