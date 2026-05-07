#!/usr/bin/env bash
# loop.sh — run Ralph in a continuous AFK loop until the backlog is empty
#
# Prerequisites:
#   1. once.sh calibration passed cleanly
#   2. Issues populated in issues/ by prd-to-issues skill
#   3. Feature branch checked out (never develop or main)
#
# The loop:
#   - Each iteration: Ralph picks one AFK issue, implements it with TDD,
#     runs quality gates, commits, and reports done.
#   - Loop continues until no AFK issues with resolved blockers remain.
#   - Each iteration runs in a fresh claude invocation (preserves smart zone).
#
# Usage: ./scripts/loop.sh [--project /path/to/project] [--max-iterations N]

set -euo pipefail

# ── STATUS.md helper ──────────────────────────────────────────────────────────

update_next_step() {
  local status_file="$PROJECT_ROOT/STATUS.md"
  local next_step="$1"
  [[ -f "$status_file" ]] || return
  python3 - "$status_file" "$next_step" <<'PYEOF'
import sys, re
path, step = sys.argv[1], sys.argv[2]
content = open(path).read()
content = re.sub(
  r'(## Next Step\n\n?).*',
  f'## Next Step\n\n{step}',
  content,
  flags=re.DOTALL
)
open(path, 'w').write(content)
PYEOF
}

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
MAX_ITERATIONS="${MAX_ITERATIONS:-20}"   # safety ceiling — prevent runaway loops

RALPH_PROMPT="$SKILLS_ROOT/prompts/ralph.md"
ISSUES_DIR="$PROJECT_ROOT/issues"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --project) PROJECT_ROOT="$2"; shift 2 ;;
    --max-iterations) MAX_ITERATIONS="$2"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# ── Pre-flight checks ─────────────────────────────────────────────────────────

echo "━━━ RALPH — AFK loop (loop.sh) ━━━"
echo ""

if ! git -C "$PROJECT_ROOT" rev-parse --git-dir > /dev/null 2>&1; then
  echo "✗ Not a git repository: $PROJECT_ROOT"
  exit 1
fi

if [[ ! -f "$RALPH_PROMPT" ]]; then
  echo "✗ Ralph prompt not found: $RALPH_PROMPT"
  exit 1
fi

if [[ ! -d "$ISSUES_DIR" ]]; then
  echo "✗ Issues directory not found: $ISSUES_DIR"
  echo "  Run prd-to-issues skill first."
  exit 1
fi

CURRENT_BRANCH=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" == "develop" || "$CURRENT_BRANCH" == "main" ]]; then
  echo "✗ On protected branch: $CURRENT_BRANCH"
  echo "  Ralph must never commit to develop or main."
  echo "  Create a feature branch: git checkout -b feature/your-feature"
  exit 1
fi

echo "✓ Project root:    $PROJECT_ROOT"
echo "✓ Branch:          $CURRENT_BRANCH"
echo "✓ Max iterations:  $MAX_ITERATIONS"
echo ""
echo "⚠ You are about to start an AFK loop."
echo "  Ralph will implement issues autonomously until the backlog is empty."
echo "  Have you run once.sh and confirmed calibration? (y/N)"
read -r CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "Aborted. Run once.sh first."
  exit 0
fi

# ── Loop ─────────────────────────────────────────────────────────────────────

ITERATION=0
START_TIME=$(date +%s)

while true; do
  ITERATION=$((ITERATION + 1))

  # Safety ceiling
  if [[ $ITERATION -gt $MAX_ITERATIONS ]]; then
    echo ""
    echo "━━━ Max iterations ($MAX_ITERATIONS) reached — stopping ━━━"
    echo "Review completed work before continuing."
    break
  fi

  echo ""
  echo "━━━ Iteration $ITERATION / $MAX_ITERATIONS ━━━"
  date

  # Check for available AFK issues before each iteration
  AFK_ISSUES=$(grep -rl "Type:.*AFK" "$ISSUES_DIR" 2>/dev/null || true)
  if [[ -z "$AFK_ISSUES" ]]; then
    echo ""
    echo "✓ No AFK issues remaining — backlog empty."
    echo "  Human review phase: clear context, load prompts/reviewer.md, review fresh."
    break
  fi

  AFK_COUNT=$(echo "$AFK_ISSUES" | wc -l | tr -d ' ')
  echo "  AFK issues remaining: $AFK_COUNT"

  # Fresh context each iteration — preserves smart zone
  RECENT_COMMITS=$(git -C "$PROJECT_ROOT" log --oneline -5 2>/dev/null || echo "(no commits yet)")
  ALL_ISSUES=$(cat "$ISSUES_DIR"/*.md 2>/dev/null || echo "(no issue files found)")

  ITERATION_CONTEXT="$(cat <<CONTEXT
# Iteration $ITERATION

# Current Backlog

$ALL_ISSUES

---

# Recent Commits (last 5)

$RECENT_COMMITS

---

# Ralph Instructions

$(cat "$RALPH_PROMPT")

---

# This iteration

Pick exactly ONE AFK issue with no unresolved blockers.
Implement it completely: failing test → implement → quality gates → commit.
When done, output a one-line summary: "DONE: [issue slug] — [commit message]"
If no AFK issues are available or all remaining are blocked, output: "BLOCKED: [reason]"
CONTEXT
)"

  # Run Ralph for this iteration
  RESULT=$(claude --allowedTools "Bash,Read,Write,Edit" \
    --model claude-sonnet-4-6 \
    --print "$ITERATION_CONTEXT" 2>&1)

  echo "$RESULT"

  # Check if Ralph reported blocked or no work available
  if echo "$RESULT" | grep -q "^BLOCKED:"; then
    echo ""
    echo "━━━ Ralph is blocked — stopping loop ━━━"
    echo "Review blocking issues. Some may need human-in-loop resolution."
    break
  fi

  # Brief pause between iterations — avoids rate limiting
  sleep 5

done

# ── Summary ───────────────────────────────────────────────────────────────────

END_TIME=$(date +%s)
ELAPSED=$(( (END_TIME - START_TIME) / 60 ))

echo ""
echo "━━━ Loop complete ━━━"
echo "  Iterations:  $ITERATION"
echo "  Elapsed:     ~${ELAPSED}m"
echo "  Branch:      $CURRENT_BRANCH"
echo ""
echo "Next steps (inner QA loop):"
echo "  1. Clear this context"
echo "  2. Open a fresh session"
echo "  3. Load: prompts/reviewer.md"
echo "  4. Review the branch — gray box: interfaces + tests only"
echo "  5. QA findings → new issues → ralph picks them up"

update_next_step "AFK loop complete. Clear context → open fresh session → load \`prompts/reviewer.md\` → Review phase: gray box review of interfaces and tests."
