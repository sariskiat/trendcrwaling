# [ISSUE-049] Automate AFK/HITL classification and post-ship smoke blocking

## Type
AFK

## Priority
infra

## Blocked by
- Expose complete Instagram/Facebook mode tools in MCP

## Why
The supervisor loop must avoid HITL tasks and immediately create blocker issues when real calls fail.

## Scope (vertical slice)
Finalize supervisor flow so `ralph/once.sh` pre-classifies AFK/HITL and `ralph/prompt.md` enforces post-ship real smoke query with blocker issue creation.

## Acceptance Criteria
- `ralph/once.sh` produces explicit AFK and HITL issue sets before supervisor task pick.
- After ship, supervisor executes one real smoke call for the changed tool.
- On smoke failure, supervisor creates a new blocker issue file with type AFK or HITL and does not retry in same run.
- User-visible behavior: running `bash ralph/once.sh` shows classification + verify step outcome.
- TDD gate: failing script/prompt behavior checks first (shell-level assertions), then green (`uv run pytest tests/smoke_tiktok.py` plus script verification command in CI/job notes).

## Files to Create/Modify
- `ralph/once.sh`
- `ralph/prompt.md`
