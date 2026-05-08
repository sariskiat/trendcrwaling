#!/bin/bash
# ralph/afk.sh — batch AFK run via GitHub Copilot coding agent
# Usage: bash ralph/afk.sh [max_issues]
#
# Creates GitHub Issues for all unblocked AFK issues and assigns Copilot.
# Copilot works on them in parallel — no polling, just fire-and-forget.

set -eo pipefail

max=${1:-99}
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "=== Ralph AFK (Copilot) · repo: $REPO · max: $max ==="

created=0
for f in issues/ISSUE-*.md; do
  [ -f "$f" ] || continue
  grep -qi 'Type:.*human-in-loop' "$f" && continue
  ((created >= max)) && break

  title=$(head -1 "$f" | sed 's/^#* *//')
  body=$(cat "$f")

  if [ -f ralph/prompt.md ]; then
    body="$body

---

## Implementation Instructions

$(cat ralph/prompt.md)"
  fi

  echo "Creating: $title"
  gh_url=$(gh issue create \
    --repo "$REPO" \
    --title "$title" \
    --body "$body" \
    --label "copilot" 2>&1)

  issue_number=$(echo "$gh_url" | grep -oE '[0-9]+$')
  gh issue edit "$issue_number" --repo "$REPO" --add-assignee "copilot"

  echo "  → #$issue_number assigned to Copilot"
  mv "$f" issues/done/
  ((created++))
done

if [ $created -eq 0 ]; then
  echo "No AFK issues remaining."
else
  echo "Dispatched $created issues to Copilot. Check PRs on GitHub."
fi
