#!/bin/bash
# ralph/review.sh — parallel Opus review (fresh session, two independent agents)
# Usage: bash ralph/review.sh
# Run in a NEW terminal session after ralph completes — never at the end of an AFK run.
# NOTE: TILDI env vars must be set (run: source ~/Downloads/claude-start.sh first)

set -eo pipefail

# Verify TILDI environment is configured
if [ -z "$ANTHROPIC_BASE_URL" ] || [ -z "$TILDI_VIRTUAL_KEY" ]; then
  echo "Error: TILDI environment not configured."
  echo "Run: source ~/Downloads/claude-start.sh"
  exit 1
fi

diff=$(git diff main...HEAD 2>/dev/null || git diff HEAD~5...HEAD)

echo "=== Spawning two Opus reviewers in parallel ==="

# Agent 1: review-protocol (tests, integration, structure)
claude --agent ralph-reviewer \
  --print \
  "Review the following diff for review-protocol compliance — tests first, then integration, then structure:

$diff" &

PID1=$!

# Agent 2: code-standards (types, naming, modules, docstrings)
claude --agent ralph-reviewer \
  --print \
  "Review the following diff for code-standards compliance — types, error handling, naming, module design, enums, immutability, docstrings:

$diff" &

PID2=$!

wait $PID1 $PID2
echo "=== Review complete ==="
