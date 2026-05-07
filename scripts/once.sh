#!/usr/bin/env bash
# once.sh — run Ralph exactly once for AFK calibration
#
# Run this BEFORE loop.sh. Watch the agent complete one issue.
# Verify: correct issue selection, TDD order, quality gates, commit format.
# Only after a clean calibration run should you use loop.sh.
#
# Usage: ./scripts/once.sh [--project /path/to/project]

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
PROJECT_ROOT="${1:-$(pwd)}"

RALPH_PROMPT="$SKILLS_ROOT/prompts/ralph.md"
ISSUES_DIR="$PROJECT_ROOT/issues"
ISSUE_TEMPLATE="$SKILLS_ROOT/templates/issue.md"

# ── Pre-flight checks ─────────────────────────────────────────────────────────

echo "━━━ RALPH — calibration run (once.sh) ━━━"
echo ""

# 1. Verify we're inside a git repo
if ! git -C "$PROJECT_ROOT" rev-parse --git-dir > /dev/null 2>&1; then
  echo "✗ Not a git repository: $PROJECT_ROOT"
  echo "  Run from your project root or pass the path: ./scripts/once.sh /path/to/project"
  exit 1
fi

# 2. Verify ralph.md exists
if [[ ! -f "$RALPH_PROMPT" ]]; then
  echo "✗ Ralph prompt not found: $RALPH_PROMPT"
  exit 1
fi

# 3. Verify issues directory exists and has AFK issues
if [[ ! -d "$ISSUES_DIR" ]]; then
  echo "✗ Issues directory not found: $ISSUES_DIR"
  echo "  Run prd-to-issues skill first to populate the backlog."
  exit 1
fi

AFK_ISSUES=$(grep -rl "Type:.*AFK" "$ISSUES_DIR" 2>/dev/null || true)
if [[ -z "$AFK_ISSUES" ]]; then
  echo "✗ No AFK issues found in $ISSUES_DIR"
  echo "  All issues may be human-in-loop or backlog may be empty."
  exit 0
fi

AFK_COUNT=$(echo "$AFK_ISSUES" | wc -l | tr -d ' ')
echo "✓ Project root:  $PROJECT_ROOT"
echo "✓ Ralph prompt:  $RALPH_PROMPT"
echo "✓ AFK issues:    $AFK_COUNT available"
echo ""

# 4. Verify current branch is not develop or main
CURRENT_BRANCH=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" == "develop" || "$CURRENT_BRANCH" == "main" ]]; then
  echo "✗ Currently on protected branch: $CURRENT_BRANCH"
  echo "  Ralph must never commit directly to develop or main."
  echo "  Create a feature branch first: git checkout -b feature/your-feature"
  exit 1
fi
echo "✓ Branch:        $CURRENT_BRANCH"

# 5. Warn if uncommitted changes exist
if ! git -C "$PROJECT_ROOT" diff --quiet || ! git -C "$PROJECT_ROOT" diff --cached --quiet; then
  echo "⚠ Uncommitted changes detected. Ralph will work on top of these."
  echo "  Consider committing or stashing before running Ralph."
  echo ""
fi

# ── Build context ─────────────────────────────────────────────────────────────

echo "━━━ Building context ━━━"
echo ""

# Recent commits — gives Ralph awareness of what's already been done
RECENT_COMMITS=$(git -C "$PROJECT_ROOT" log --oneline -5 2>/dev/null || echo "(no commits yet)")

# All issue files — Ralph selects the highest-priority AFK issue with no blockers
ALL_ISSUES=$(cat "$ISSUES_DIR"/*.md 2>/dev/null || echo "(no issue files found)")

# Full prompt context: issues + recent commits + ralph instructions
FULL_CONTEXT="$(cat <<CONTEXT
# Current Backlog

$ALL_ISSUES

---

# Recent Commits (last 5)

$RECENT_COMMITS

---

# Ralph Instructions

$(cat "$RALPH_PROMPT")

---

# THIS IS A CALIBRATION RUN

Complete exactly ONE issue then stop. Do not loop.
After completing the issue, output a one-paragraph summary:
- Which issue you picked and why (priority + no blockers)
- What test you wrote first (confirm it failed before implementing)
- Which quality gates you ran and their results
- Your exact commit message
CONTEXT
)"

# ── Run ───────────────────────────────────────────────────────────────────────

echo "Starting Ralph (calibration — one issue only)..."
echo "Watch for: correct issue selection → failing test first → quality gates → commit"
echo ""

claude --allowedTools "Bash,Read,Write,Edit" \
  --model claude-sonnet-4-6 \
  --print "$FULL_CONTEXT"

echo ""
echo "━━━ Calibration run complete ━━━"
echo ""
echo "Review the output above. Verify:"
echo "  □ Ralph picked the highest-priority AFK issue with no unresolved blockers"
echo "  □ Failing test was written and confirmed failing before any implementation"
echo "  □ ruff + black + pytest all passed before commit"
echo "  □ Commit message follows: type(scope): description (under 72 chars)"
echo ""
echo "If all checks pass → run loop.sh to start the full AFK loop."
echo "If anything is wrong → fix the issue file or ralph.md before proceeding."

update_next_step "Calibration passed. Run \`./scripts/loop.sh\` to start the full AFK loop, or move to Review phase if no more AFK issues remain."
