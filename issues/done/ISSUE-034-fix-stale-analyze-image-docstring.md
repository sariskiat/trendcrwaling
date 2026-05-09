# ISSUE-034: Fix stale analyze_image docstring

**Type:** AFK
**Priority:** bug
**Blocked by:** nothing

## Problem

Docstring in `mcp_server/server.py:155-157` claims `ValueError` is raised but the function now raises:
- `ValidationError` for invalid `image_url`
- `ConfigurationError` for missing `OPENAI_API_KEY`
- `AnalysisError` for empty OpenAI response

This is user-facing documentation that will mislead callers.

## Acceptance Criteria

- [ ] Docstring `Raises:` section lists `ValidationError`, `ConfigurationError`, `AnalysisError` with correct descriptions
- [ ] `pytest` passes
- [ ] `ruff .` passes
- [ ] `pyright` passes

## Files to Modify

- `mcp_server/server.py` — update `analyze_image` docstring

## TDD Gate

Read the docstring, verify it matches actual exception types raised in the function body.