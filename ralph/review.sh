#!/bin/bash
# ralph/review.sh — parallel review (fresh session, two independent agents)
# Usage: bash ralph/review.sh
# Run in a NEW terminal session after ralph completes — never at the end of an AFK run.
# Requires: GitHub Copilot CLI (gh extension install github/gh-copilot)

set -eo pipefail

# Verify Copilot CLI is available
if ! command -v copilot &>/dev/null; then
  echo "Error: Copilot CLI not found."
  echo "Install: gh extension install github/gh-copilot"
  exit 1
fi

diff=$(git diff main...HEAD 2>/dev/null)
if [ -z "$diff" ]; then
  diff=$(git diff HEAD~5...HEAD 2>/dev/null || echo "(no diff available)")
fi

echo "=== Spawning two reviewers in parallel (claude-sonnet-4-5) ==="

# Agent 1: review-protocol (tests, integration, structure)
copilot --agent ralph-reviewer \
  --allow-all-tools \
  -p "Review the following diff for review-protocol compliance — tests first, then integration, then structure:

$diff" &

PID1=$!

# Agent 2: code-standards (types, naming, modules, docstrings)
copilot --agent ralph-reviewer \
  --allow-all-tools \
  -p "Review the following diff for code-standards compliance — types, error handling, naming, module design, enums, immutability, docstrings:

$diff" &

PID2=$!

wait $PID1 $PID2
echo "=== Review complete ==="
