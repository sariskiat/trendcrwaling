#!/bin/bash
# ralph/once.sh — single AFK run (Sonnet supervisor + Haiku implementer)
# Usage: bash ralph/once.sh

set -eo pipefail

issues=$(cat issues/*.md 2>/dev/null || echo "No issues found")
commits=$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found")

claude-tildi --agent ralph-supervisor \
  --permission-mode acceptEdits \
  "Previous commits: $commits

Issues: $issues"
