# ISSUES

Local issue files from `issues/` are provided at start of context. Parse them to understand the open issues.

You will work on AFK-safe issues only, not HITL ones.

You've also been passed a file containing the last few commits. Review these to understand what work has been done.

If all AFK tasks are complete, output <promise>NO MORE TASKS</promise>.

# AFK vs HITL CRITERIA

**AFK-safe** (you may work on these unsupervised):
- Implementation of a well-scoped vertical-slice issue
- Automated test suite execution
- Linting / formatting / type checking
- Database migration execution (not design)
- Dependency updates with test gate

**Human-in-loop** (skip these — leave them for the human):
- Alignment / grill-me sessions
- PRD review and approval
- Kanban issue review
- Prototype / architecture selection
- QA / manual testing
- Code review
- Any decision requiring business intent or taste

**Decision rule:** If the task requires taste, business judgement, or creative input → skip it (HITL). If the task is deterministic, has a clear acceptance criterion, and can be verified by a quality gate → do it (AFK-safe).

# TASK SELECTION

Pick the next AFK-safe task. Prioritize in this order:

1. Critical bugfixes
2. Development infrastructure

Getting development infrastructure like tests, types, and dev scripts ready is an important precursor to building features.

3. Tracer bullets for new features

Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early.

TL;DR - build a tiny, end-to-end slice of the feature first, then expand it out.

4. Polish and quick wins
5. Refactors

# EXPLORATION

Explore the repo.

# IMPLEMENTATION

Write a failing test first, then implement until the test passes.

# FEEDBACK LOOPS

Before committing, run the feedback loops:

- `uv run pytest` to run the tests
- `uv run pyright` to run the type checker

# COMMIT

Make a git commit. The commit message must:

1. Include key decisions made
2. Include files changed
3. Blockers or notes for next iteration

# THE ISSUE

If the task is complete, move the issue file to `issues/done/`.

If the task is not complete, add a note to the issue file with what was done.

# FINAL RULES

ONLY WORK ON A SINGLE TASK.