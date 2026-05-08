#!/bin/bash
# ralph/afk.sh — batch AFK issue lister for subagent dispatch
# Usage: bash ralph/afk.sh [max_issues]
#
# Lists all unblocked AFK issues from issues/ directory.
# Use this to see what's available, then dispatch each to a fresh
# Copilot Chat subagent via runSubagent (or implement directly).
#
# Primary dispatch mode: Copilot Chat subagents (runSubagent tool)
# Fallback: GitHub Issues with --label copilot (if Copilot agent is enabled)

set -eo pipefail

max=${1:-99}
echo "=== Ralph AFK · scanning issues/ ==="

count=0
for f in issues/ISSUE-*.md; do
  [ -f "$f" ] || continue
  grep -qi 'Type:.*human-in-loop' "$f" && continue
  ((count >= max)) && break

  title=$(head -1 "$f" | sed 's/^#* *//')
  echo "  [$((count + 1))] $title  ($f)"
  ((count++))
done

if [ $count -eq 0 ]; then
  echo "No AFK issues remaining."
else
  echo ""
  echo "$count issues ready for subagent dispatch."
  echo "Dispatch via Copilot Chat: ask the agent to implement each issue."
fi
