#!/bin/bash
# ralph/test.sh — smoke test to verify Copilot CLI + ralph agents work
# Usage: bash ralph/test.sh
# Runs easy tasks to confirm the setup is operational before a real AFK run.

set -eo pipefail

PASS=0
FAIL=0

ok()   { echo "  ✓ $1"; PASS=$((PASS+1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL+1)); }

echo ""
echo "━━━ Ralph / Copilot CLI — smoke tests ━━━"
echo ""

# ── 1. Copilot CLI available ──────────────────────────────────────────────────
echo "[ 1/5 ] Copilot CLI available"
if command -v copilot &>/dev/null; then
  ok "copilot found at $(command -v copilot)"
else
  fail "copilot not found — install: gh extension install github/gh-copilot"
fi

# ── 2. Authenticated ──────────────────────────────────────────────────────────
echo ""
echo "[ 2/5 ] Copilot CLI authenticated"
if copilot --version &>/dev/null 2>&1; then
  ok "copilot --version succeeded"
else
  fail "copilot --version failed — run: gh auth login"
fi

# ── 3. Git repo present ───────────────────────────────────────────────────────
echo ""
echo "[ 3/5 ] Git repository"
if git rev-parse --git-dir &>/dev/null 2>&1; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  ok "git repo detected (branch: $BRANCH)"
else
  fail "not inside a git repository"
fi

# ── 4. Agent files present ────────────────────────────────────────────────────
echo ""
echo "[ 4/5 ] Agent definition files"

SUPERVISOR=".github/agents/ralph-supervisor.agent.md"
REVIEWER=".github/agents/ralph-reviewer.agent.md"

if [[ -f "$SUPERVISOR" ]]; then
  ok "$SUPERVISOR"
else
  fail "$SUPERVISOR — not found"
fi

if [[ -f "$REVIEWER" ]]; then
  ok "$REVIEWER"
else
  fail "$REVIEWER — not found"
fi

# ── 5. Live CLI call — trivial prompt ─────────────────────────────────────────
echo ""
echo "[ 5/5 ] Live Copilot CLI call (trivial prompt)"
echo "        Sending: 'Reply with exactly: RALPH_OK'"
echo ""

RESPONSE=$(copilot --allow-all-tools -p "Reply with exactly the word: RALPH_OK" 2>&1 || true)

echo "        Response: $RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "RALPH_OK"; then
  ok "got expected token RALPH_OK in response"
else
  fail "unexpected response (see above) — check authentication or model availability"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Tests passed:  $PASS"
echo "  Tests failed:  $FAIL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [[ $FAIL -eq 0 ]]; then
  echo "✅ All checks passed. ralph/once.sh is ready to run."
  exit 0
else
  echo "❌ $FAIL check(s) failed. Fix the issues above before running ralph."
  exit 1
fi
