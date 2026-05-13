## Startup Workflow

At the start of every session, in order:
1. Read this file
2. Read `STATUS.md` — find the Next Step
3. Run `bash init.sh` to confirm the environment is green
4. Pick the next unblocked AFK issue and begin — do not wait for instructions

## End of Session

Before ending any session:
1. Update `STATUS.md` — set Next Step to the next unblocked AFK issue
2. Move any completed issue file to `issues/done/`
3. Commit with: `type(scope): description` (under 72 chars)

## Memory — MemPalace-First Rule

MemPalace contains pre-indexed project context (530 drawers). It exists to replace file exploration.

**Before spawning any Explore agent or reading files for context:**
1. Query `mempalace_search` with the topic first.
2. If results are returned (distance < 1.0), use them as the exploration result — do NOT also run Explore.
3. Only fall back to file tools / Explore agent if mempalace returns 0 useful results.

This applies to: orientation, issue planning, architecture questions.
Do NOT run both MemPalace + Explore for the same topic.
