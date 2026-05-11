# [ISSUE-041] Review violation: Real OpenAI API key hardcoded in source: 'sk-proj-NIALUUAhRa1ZKtkL7pSXDhJgOZtJHlCBSvzQ50-...' committed to repository. Must be replaced with a placeholder such as 'test-key'.

**Type:** AFK
**Source:** Auto-created by reviewer — iteration 4, from ISSUE-047-create-llm-hashtag-generator-module.md

## Problem

File: `tests/test_hashtag_generator.py` (line 51)

Real OpenAI API key hardcoded in source: 'sk-proj-NIALUUAhRa1ZKtkL7pSXDhJgOZtJHlCBSvzQ50-...' committed to repository. Must be replaced with a placeholder such as 'test-key'.

## Acceptance Criteria

- [ ] Violation fixed in `tests/test_hashtag_generator.py`
- [ ] `uv run ruff check .` passes
- [ ] `uv run pyright` passes
- [ ] `uv run pytest -x` passes

## Files to Modify

- `tests/test_hashtag_generator.py`
