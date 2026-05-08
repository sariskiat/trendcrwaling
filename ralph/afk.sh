#!/bin/bash
# ralph/afk.sh — looped AFK run (Sonnet supervisor + Haiku implementer)
# Usage: bash ralph/afk.sh <iterations>
# NOTE: Run this in a shell where TILDI env vars are already set
#       (i.e., after running: source ~/Downloads/claude-start.sh)

set -eo pipefail

if [ -z "$1" ]; then
  echo "Usage: $0 <iterations>"
  exit 1
fi

# Verify TILDI environment is configured
if [ -z "$ANTHROPIC_BASE_URL" ] || [ -z "$TILDI_VIRTUAL_KEY" ]; then
  echo "Error: TILDI environment not configured."
  echo "Run: source ~/Downloads/claude-start.sh"
  echo "Then: bash ralph/afk.sh <iterations>"
  exit 1
fi

for ((i=1; i<=$1; i++)); do
  echo "=== Iteration $i/$1 ==="

  issues=$(cat issues/*.md 2>/dev/null || echo "No issues found")
  commits=$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found")

  result=$(claude --agent ralph-supervisor \
    --print \
    "Previous commits: $commits

Issues: $issues")

  echo "$result"

  if [[ "$result" == *"<promise>NO MORE TASKS</promise>"* ]]; then
    echo "Ralph complete after $i iterations."
    exit 0
  fi
done
