#!/bin/bash
# ralph/once.sh — single AFK run (Sonnet supervisor + Haiku implementer)
# Usage: bash ralph/once.sh
# NOTE: Run this in a shell where TILDI env vars are already set
#       (i.e., after running: source ~/Downloads/claude-start.sh)

set -eo pipefail

# Verify TILDI environment is configured
if [ -z "$ANTHROPIC_BASE_URL" ] || [ -z "$TILDI_VIRTUAL_KEY" ]; then
  echo "Error: TILDI environment not configured."
  echo "Run: source ~/Downloads/claude-start.sh"
  echo "Then: bash ralph/once.sh"
  exit 1
fi

issues=$(cat issues/*.md 2>/dev/null || echo "No issues found")
commits=$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found")

claude --agent ralph-supervisor \
  --print \
  "Previous commits: $commits

Issues: $issues"
