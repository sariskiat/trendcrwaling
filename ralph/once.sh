#!/bin/bash
# ralph/once.sh — show next AFK issue for subagent dispatch
# Usage: bash ralph/once.sh
#
# Picks the highest-priority unblocked issue from issues/
# and prints it for dispatch to a Copilot Chat subagent.
#
# Primary dispatch mode: Copilot Chat subagents (runSubagent tool)
# The parent agent reads the issue, sends it to runSubagent, then
# moves the file to issues/done/ on completion.

set -eo pipefail

echo "=== Ralph (single) · scanning issues/ ==="

# --- 1. SELECT: pick the first unblocked AFK issue file ---
issue_file=""
for f in issues/ISSUE-*.md; do
  [ -f "$f" ] || continue
  grep -qi 'Type:.*human-in-loop' "$f" && continue
  issue_file="$f"
  break
done

if [ -z "$issue_file" ]; then
  echo "No AFK issues remaining."
  exit 0
fi

title=$(head -1 "$issue_file" | sed 's/^#* *//')
echo "Next issue: $title"
echo "File: $issue_file"
echo ""
echo "--- Issue body ---"
cat "$issue_file"
echo ""
echo "--- End ---"
echo ""
echo "Dispatch this to a subagent, then move to issues/done/ when complete."
