# [ISSUE-050] Run HITL credentialed smoke and close loop

## Type
human-in-loop

## Priority
polish

## Blocked by
- ISSUE-049

## Why
Final verification requires real credentials and human confirmation that all three platforms and modes behave in production.

## Scope (vertical slice)
Run real MCP calls with valid cookies/API keys for 3x3 mode matrix, verify recency/ranking expectations, and file blockers for any failing mode.

## Acceptance Criteria
- Human operator executes real smoke calls for all target tools with valid env credentials.
- For each mode/platform, record pass/fail and attach one sample response shape.
- Any failing mode creates a new blocked issue immediately (AFK if code-fixable, HITL if credential/access-bound).
- User-visible behavior: final run report shows which modes are production-ready.
- TDD gate: no merge/close until automated test suite is green before HITL smoke execution (`uv run pytest`).

## Files to Create/Modify
- `mcp_server/server.py`
- `scrapers/instagram.py`
- `scrapers/facebook.py`
- `scrapers/tiktok_api.py`
- `tests/test_server.py`
- `tests/test_instagram.py`
- `tests/test_facebook.py`
- `tests/test_tiktok_api.py`
