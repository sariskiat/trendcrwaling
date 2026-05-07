# [ISSUE-000] Title

**Type:** `AFK` | `human-in-loop`
**Priority:** `bug` | `infra` | `tracer-bullet` | `polish`
**Blocked by:** ISSUE-XXX, ISSUE-YYY *(or `none`)*
**Blocks:** ISSUE-XXX, ISSUE-YYY *(or `none`)*
**Module(s):** `agents/` | `graphs/` | `tools/` | `core/` | `connectors/` | `prompts/` | `evaluations/` | `memory/`

---

## Context

Why does this need to exist? Brief background the agent needs to understand scope.

## What to build

Concrete description. Specify inputs, outputs, and observable side effects.
Be specific enough that an AFK agent can pick this up cold.

## Acceptance criteria

- [ ] Failing test written **before** any implementation (TDD — non-negotiable)
- [ ] Implementation makes the test pass
- [ ] `ruff .` passes
- [ ] `black --check .` passes
- [ ] `pytest -x --cov=genai_project_template --cov-fail-under=20` passes
- [ ] Coverage does not decrease from baseline
- [ ] `tests/` still mirrors `src/` exactly
- [ ] *[add feature-specific criteria here]*

## Out of scope

What this issue explicitly does NOT cover. Defines the boundary of done.

- Not in this issue: ...

## Notes

Additional context, links, constraints, or design decisions.
