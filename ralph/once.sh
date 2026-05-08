#!/bin/bash
# ralph/once.sh — single AFK run via GitHub Copilot coding agent
# Usage: bash ralph/once.sh
#
# Picks the highest-priority unblocked issue from issues/,
# creates a GitHub Issue, assigns Copilot, and waits for the PR.

set -eo pipefail

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "=== Ralph (Copilot) · repo: $REPO ==="

# --- 1. SELECT: pick the first unblocked AFK issue file ---
issue_file=""
for f in issues/ISSUE-*.md; do
  [ -f "$f" ] || continue
  # skip HITL issues
  grep -qi 'Type:.*human-in-loop' "$f" && continue
  issue_file="$f"
  break
done

if [ -z "$issue_file" ]; then
  echo "No AFK issues remaining."
  exit 0
fi

title=$(head -1 "$issue_file" | sed 's/^#* *//')
echo "Selected: $title"

# --- 2. CREATE GitHub Issue with full body ---
body=$(cat "$issue_file")

# Append implementation context from prompt.md
if [ -f ralph/prompt.md ]; then
  body="$body

---

## Implementation Instructions

$(cat ralph/prompt.md)"
fi

gh_issue_url=$(gh issue create \
  --repo "$REPO" \
  --title "$title" \
  --body "$body" \
  --label "copilot" 2>&1)

echo "Created: $gh_issue_url"

# --- 3. ASSIGN Copilot coding agent ---
issue_number=$(echo "$gh_issue_url" | grep -oE '[0-9]+$')
gh issue edit "$issue_number" --repo "$REPO" --add-assignee "copilot"

echo "Assigned Copilot to issue #$issue_number. It will open a PR autonomously."
echo "Track: $gh_issue_url"

# --- 4. WAIT for PR (poll every 60s, max 30 min) ---
echo "Waiting for Copilot PR..."
for ((i=1; i<=30; i++)); do
  pr_url=$(gh pr list --repo "$REPO" \
    --search "$issue_number" \
    --json url -q '.[0].url // empty' 2>/dev/null || true)
  if [ -n "$pr_url" ]; then
    echo "PR opened: $pr_url"
    # Move issue to done
    mv "$issue_file" issues/done/
    echo "Moved $issue_file → issues/done/"
    exit 0
  fi
  echo "  [$i/30] No PR yet, waiting 60s..."
  sleep 60
done

echo "Timeout — no PR after 30 min. Check GitHub manually."
exit 1
