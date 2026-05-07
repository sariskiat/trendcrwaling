# PRD — [Feature Name]

**Status:** `draft` | `approved` | `done`
**Date:** YYYY-MM-DD
**Grill session:** [date or link]
**Author:** [name]

> **After all issues from this PRD are closed — delete this file.**
> Doc rot is a production risk. Old PRDs mislead future agents. (#14)

---

## Problem Statement

What pain does this solve? Who experiences it? What breaks today without this?

## Solution

High-level description of the approach. This is a **destination document** — what we are building, not how to build it step by step.

## User Stories

Each story must be concrete and testable. These define what "done" looks like.

- As a **[user]**, I can **[action]** so that **[value]**.
- As a **[user]**, I can **[action]** so that **[value]**.
- As a **[user]**, I can **[action]** so that **[value]**.

## Out of Scope

Explicit exclusions. This is as important as the user stories — it gives agents a definition of done by boundary.

- Not in this PRD: ...
- Not in this PRD: ...
- Deferred to future work: ...

## Implementation Decisions

Design choices resolved during the Grill Me session. Agents read this to understand constraints — they do not re-litigate these decisions.

| Decision | Choice made | Reason |
|---|---|---|
| Data model | ... | ... |
| API shape | ... | ... |
| Storage | ... | ... |

## Proposed Modules

Which files/services will be created or modified. Agents use this as the starting point for exploration.

| Module path | Action | Notes |
|---|---|---|
| `agents/...` | create | ... |
| `graphs/...` | modify | ... |
| `tools/...` | create | ... |
