#!/bin/bash
# ralph/afk.sh — Multi-agent AFK pipeline
#
# Three isolated containers per iteration:
#   1. Supervisor  (GPT-4o)       — picks issue, writes brief to ralph-state/brief.json
#   2. Implementor (GPT-4.1)      — TDD + real integration tests + commit (own container)
#   3. Reviewer    (Claude Sonnet) — /review-protocol + /code-standards gate
#
# On NEEDS_REVISION: auto-creates ISSUE files per violation, increments convergence counter.
# After --convergence-limit consecutive non-APPROVED reviews: logs and exits 1 for human.
#
# Usage: bash ralph/afk.sh <max_iterations> [--convergence-limit N]
#   Default convergence limit: 3

set -eo pipefail

# ── Args ──────────────────────────────────────────────────────────────────────

if [ -z "$1" ]; then
  echo "Usage: $0 <max_iterations> [--convergence-limit N]"
  exit 1
fi

MAX_ITER="$1"
CONVERGENCE_LIMIT=3
shift

while [[ $# -gt 0 ]]; do
  case $1 in
    --convergence-limit) CONVERGENCE_LIMIT="$2"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT="$(pwd)"
STATE_DIR="$REPO_ROOT/ralph-state"
BRIEF_FILE="$STATE_DIR/brief.json"
VIOLATIONS_FILE="$STATE_DIR/violations.json"
REVIEW_LOG="$STATE_DIR/review-log.md"
CONVERGENCE_FILE="$STATE_DIR/convergence-failures.md"

mkdir -p "$STATE_DIR"

# ── Container runner ──────────────────────────────────────────────────────────
# All three agents use the ralph-agent Docker image via copilot CLI.
# The repo is bind-mounted at /workspace so agents share the same filesystem.

run_agent() {
  local agent="$1"
  local prompt="$2"

  # Resolve token: prefer explicit COPILOT_GITHUB_TOKEN, then extract from
  # ~/.config/github-copilot/apps.json (the copilot CLI's own OAuth token —
  # different app/quota from the gh CLI token returned by `gh auth token`)
  local _token="${COPILOT_GITHUB_TOKEN:-$(python3 -c \
    "import json,os; d=json.load(open(os.path.expanduser('~/.config/github-copilot/apps.json'))); print(list(d.values())[0]['oauth_token'])" \
    2>/dev/null || gh auth token 2>/dev/null || true)}"

  local -a args=(
    run --rm
    -v "$REPO_ROOT:/workspace"
    -w /workspace
    -e "COPILOT_GITHUB_TOKEN=${_token}"
  )

  # Mount .env for scraper secrets — clean whitespace from key names (docker --env-file is strict)
  if [[ -f "$REPO_ROOT/.env" ]]; then
    local _envtmp
    _envtmp=$(mktemp)
    sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d; s/^[[:space:]]*//; s/[[:space:]]*=/=/' \
      "$REPO_ROOT/.env" > "$_envtmp"
    args+=(--env-file "$_envtmp")
    trap "rm -f '$_envtmp'" RETURN
  fi

  args+=(ralph-agent copilot --agent "$agent" --allow-all-tools -p "$prompt")

  docker "${args[@]}"
}

# ── Issue counter helper ───────────────────────────────────────────────────────
# Returns the next available ISSUE-NNN number (3-digit, zero-padded).

next_issue_number() {
  local max=0 n
  for f in "$REPO_ROOT"/issues/*.md "$REPO_ROOT"/issues/done/*.md; do
    [[ -f "$f" ]] || continue
    n=$(basename "$f" | grep -oE '^ISSUE-[0-9]+' | grep -oE '[0-9]+' || true)
    [[ -n "$n" && "$n" -gt "$max" ]] && max="$n"
  done
  printf '%03d' $((max + 1))
}

# ── Main loop ─────────────────────────────────────────────────────────────────

CONVERGENCE_COUNT=0

echo "━━━ RALPH — AFK Pipeline ━━━"
echo "  Max iterations:    $MAX_ITER"
echo "  Convergence limit: $CONVERGENCE_LIMIT"
echo "  State dir:         $STATE_DIR"
echo ""

for ((i=1; i<=MAX_ITER; i++)); do
  echo ""
  echo "━━━ Iteration $i / $MAX_ITER ━━━"
  date

  # ── Pre-check: any AFK issues left? ─────────────────────────────────────────
  ISSUE_COUNT=$(ls "$REPO_ROOT"/issues/*.md 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$ISSUE_COUNT" -eq 0 ]]; then
    echo "✓ No issues remaining — backlog empty."
    exit 0
  fi

  # ── Stage 1: Supervisor ──────────────────────────────────────────────────────
  echo ""
  echo "[ 1/3 ] Supervisor (GPT-4o) — /hardgate → brief..."

  COMMITS=$(git -C "$REPO_ROOT" log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null \
    || echo "No commits found")
  ISSUES_BODY=$(cat "$REPO_ROOT"/issues/*.md 2>/dev/null || echo "No issues found")
  PROMPT_BODY=$(cat "$REPO_ROOT/ralph/prompt.md")

  SUPERVISOR_PROMPT="# CONTEXT

## Open Issues

$ISSUES_BODY

## Recent Commits (last 5)

$COMMITS

## AFK Protocol

$PROMPT_BODY

---

# YOUR TASK

1. Apply /hardgate to every open issue. Reject issues missing: (a) acceptance criteria, (b) a concrete file to modify, or (c) a testable outcome.
2. Pick exactly ONE AFK-safe issue that passes /hardgate.
3. Write the JSON brief to \`/workspace/ralph-state/brief.json\`.
4. Print BRIEF_WRITTEN or NO_MORE_TASKS."

  rm -f "$BRIEF_FILE"
  SUPERVISOR_OUT=$(run_agent "ralph-supervisor" "$SUPERVISOR_PROMPT" 2>&1) || true
  echo "$SUPERVISOR_OUT"

  if echo "$SUPERVISOR_OUT" | grep -q "NO_MORE_TASKS"; then
    echo ""
    echo "✓ Supervisor: no more tasks. Pipeline complete after $i iterations."
    exit 0
  fi

  if ! echo "$SUPERVISOR_OUT" | grep -q "BRIEF_WRITTEN"; then
    echo "⚠ Supervisor did not confirm BRIEF_WRITTEN — skipping iteration."
    continue
  fi

  if [[ ! -f "$BRIEF_FILE" ]]; then
    echo "✗ BRIEF_WRITTEN claimed but $BRIEF_FILE missing — skipping iteration."
    continue
  fi

  ISSUE_FILE=$(python3 -c \
    "import json; d=json.load(open('$BRIEF_FILE')); print(d.get('issue_file','?'))" \
    2>/dev/null || echo "unknown")
  echo "  Brief: $ISSUE_FILE"

  # ── Stage 2: Implementor (own container) ─────────────────────────────────────
  echo ""
  echo "[ 2/3 ] Implementor (GPT-4.1) — TDD + real integration tests + commit..."

  IMPLEMENTOR_PROMPT="# YOUR TASK

Read \`/workspace/ralph-state/brief.json\` and execute the full TDD workflow:

1. Read the brief (issue_file, files, test_file, first_failing_test, acceptance_criteria).
2. Write a FAILING real integration test in test_file. Run it — confirm red before continuing.
   - NO mocks, NO @patch, NO MagicMock. Fire real API calls / launch real browsers.
3. Implement until the test passes.
4. Run all quality gates (must all be green before commit):
   - uv run ruff check .
   - uv run ruff format --check .
   - uv run pyright
   - uv run pytest -x
5. git commit with: what changed, why, key decisions, files changed.

Do NOT move the issue file to done/ — the reviewer handles that after approval.

Print DONE: <issue_file> or FAILED: <reason>."

  # Snapshot the current HEAD so we can diff everything the implementor commits
  PRE_IMPL_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo "")

  rm -f "$VIOLATIONS_FILE"
  IMPL_OUT=$(run_agent "ralph-implementor" "$IMPLEMENTOR_PROMPT" 2>&1) || true
  echo "$IMPL_OUT"

  if echo "$IMPL_OUT" | grep -q "hit your rate limit\|rate limit.*reset\|Rate limit"; then
    RESET_MSG=$(echo "$IMPL_OUT" | grep -oE 'reset in [^.]+' | head -1 || echo "unknown time")
    echo ""
    echo "━━━ RATE LIMITED ━━━"
    echo "  Implementor hit a Copilot Premium rate limit ($RESET_MSG)."
    echo "  Pipeline paused — rerun after the quota resets."
    echo "  Log: ralph-state/pipeline-run.log"
    exit 2
  fi

  if echo "$IMPL_OUT" | grep -q "^FAILED:"; then
    FAIL_REASON=$(echo "$IMPL_OUT" | grep "^FAILED:" | head -1)
    echo "⚠ Implementor: $FAIL_REASON — skipping review, continuing to next iteration."
    continue
  fi

  if ! echo "$IMPL_OUT" | grep -q "^DONE:"; then
    echo "⚠ Implementor produced no DONE/FAILED signal — skipping review."
    continue
  fi

  # ── Stage 3: Reviewer ────────────────────────────────────────────────────────
  echo ""
  echo "[ 3/3 ] Reviewer (Claude Sonnet) — /review-protocol + /code-standards..."

  # Write diff to a file — captures ALL commits the implementor made (pre-impl SHA → current HEAD)
  DIFF_FILE="$STATE_DIR/diff.txt"
  if [[ -n "$PRE_IMPL_SHA" ]] && git -C "$REPO_ROOT" rev-parse HEAD &>/dev/null; then
    git -C "$REPO_ROOT" diff "${PRE_IMPL_SHA}"...HEAD > "$DIFF_FILE" 2>/dev/null \
      || git -C "$REPO_ROOT" show HEAD > "$DIFF_FILE" 2>/dev/null \
      || echo "(no diff available)" > "$DIFF_FILE"
  else
    echo "(no diff available)" > "$DIFF_FILE"
  fi

  REVIEWER_PROMPT="# YOUR TASK

Review the git diff for this iteration. The diff has been written to the file:
  /workspace/ralph-state/diff.txt

Read that file first, then apply review-protocol and code-standards checks.

## Pass 1 — Review Protocol

- Test-first: was a failing test written before implementation? (look at commit order)
- Coverage: new functions/methods have corresponding tests?
- Integration: fits existing module patterns and error handling?
- Structure: functions ≤ 30 lines, single responsibility, no dead code?

## Pass 2 — Code Standards

- Types: all signatures annotated, no bare Any, no # type: ignore without justification
- Error handling: no bare except, specific exception types, no silent swallowing
- Naming: snake_case vars/functions, PascalCase classes
- Module design: no circular imports, no logic in __init__.py
- Immutability: prefer tuple/frozenset for constants, no mutable defaults
- Docstrings: public functions/classes documented
- Security: no secrets hardcoded, no user input interpolated into JS/SQL/shell

## Required output

1. Write \`/workspace/ralph-state/violations.json\`:
{
  \"verdict\": \"APPROVED\" | \"NEEDS_REVISION\" | \"BLOCKED\",
  \"violations\": [
    { \"file\": \"<file>\", \"line\": <line or 0>, \"severity\": \"FAIL\" | \"WARN\", \"description\": \"<what>\" }
  ]
}

2. If the verdict is APPROVED, move the issue to done and commit:
```
mv issues/<issue_file> issues/done/<issue_file>
git add -A
git commit -m "chore: close <issue_file> — approved"
```
The issue_file is in /workspace/ralph-state/brief.json under the key `issue_file`.

3. Print exactly one of:
   VERDICT: APPROVED
   VERDICT: NEEDS_REVISION
   VERDICT: BLOCKED"

  REVIEW_OUT=$(run_agent "ralph-reviewer" "$REVIEWER_PROMPT" 2>&1) || true
  echo "$REVIEW_OUT"

  VERDICT=$(echo "$REVIEW_OUT" | grep "^VERDICT:" | head -1 | awk '{print $2}')

  # Append to persistent review log
  {
    echo ""
    echo "## Iteration $i — $(date '+%Y-%m-%d %H:%M') — $ISSUE_FILE"
    echo ""
    echo "**Verdict:** $VERDICT"
    echo ""
    echo "$REVIEW_OUT"
    echo ""
    echo "---"
  } >> "$REVIEW_LOG"

  # ── Decision on verdict ───────────────────────────────────────────────────────
  case "$VERDICT" in
    APPROVED)
      echo "✓ APPROVED — resetting convergence counter."
      CONVERGENCE_COUNT=0
      ;;

    NEEDS_REVISION|BLOCKED)
      CONVERGENCE_COUNT=$((CONVERGENCE_COUNT + 1))
      echo "✗ $VERDICT (convergence: $CONVERGENCE_COUNT / $CONVERGENCE_LIMIT)"

      # Auto-create issue files for each FAIL violation
      if [[ -f "$VIOLATIONS_FILE" ]]; then
        while IFS='|' read -r vfile vline vdesc; do
          [[ -z "$vdesc" ]] && continue
          NUM=$(next_issue_number)
          SLUG=$(echo "$vdesc" \
            | tr '[:upper:]' '[:lower:]' \
            | sed 's/[^a-z0-9]/-/g' \
            | sed 's/-\+/-/g' \
            | cut -c1-40 \
            | sed 's/-$//')
          IPATH="$REPO_ROOT/issues/ISSUE-${NUM}-review-${SLUG}.md"
          cat > "$IPATH" <<ISSUE_EOF
# [ISSUE-${NUM}] Review violation: $vdesc

**Type:** AFK
**Source:** Auto-created by reviewer — iteration $i, from $ISSUE_FILE

## Problem

File: \`$vfile\` (line $vline)

$vdesc

## Acceptance Criteria

- [ ] Violation fixed in \`$vfile\`
- [ ] \`uv run ruff check .\` passes
- [ ] \`uv run pyright\` passes
- [ ] \`uv run pytest -x\` passes

## Files to Modify

- \`$vfile\`
ISSUE_EOF
          echo "  Created: $(basename "$IPATH")"
        done < <(python3 - <<PYEOF
import json, sys
try:
    d = json.load(open('$VIOLATIONS_FILE'))
    for v in d.get('violations', []):
        if v.get('severity') == 'FAIL':
            f = v.get('file', '?')
            l = v.get('line', 0)
            desc = v.get('description', '?').replace('|', '-')
            print(f"{f}|{l}|{desc}")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
PYEOF
)
      fi

      # Convergence failure: raise for human
      if [[ $CONVERGENCE_COUNT -ge $CONVERGENCE_LIMIT ]]; then
        echo ""
        echo "━━━ CONVERGENCE FAILURE ━━━"
        echo "  $CONVERGENCE_COUNT consecutive non-APPROVED reviews — raising for human."
        {
          echo "# Convergence Failure — $(date '+%Y-%m-%d %H:%M')"
          echo ""
          echo "Pipeline stopped after **$CONVERGENCE_COUNT** consecutive non-APPROVED reviews."
          echo ""
          echo "## Last Issue"
          echo ""
          echo "$ISSUE_FILE"
          echo ""
          echo "## Open Violations"
          echo ""
          [[ -f "$VIOLATIONS_FILE" ]] && python3 -c \
            "import json; d=json.load(open('$VIOLATIONS_FILE')); [print(f\"- [{v['severity']}] {v['file']}:{v['line']} — {v['description']}\") for v in d.get('violations',[])]" \
            2>/dev/null || echo "(could not parse violations.json)"
          echo ""
          echo "## Review Log"
          echo ""
          echo "See: \`ralph-state/review-log.md\`"
        } > "$CONVERGENCE_FILE"
        echo "  → ralph-state/convergence-failures.md"
        exit 1
      fi
      ;;

    *)
      echo "⚠ Unrecognised verdict '$VERDICT' — continuing."
      ;;
  esac

done

echo ""
echo "━━━ AFK pipeline done — $MAX_ITER iterations completed ━━━"