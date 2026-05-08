#!/bin/bash
# ralph/review.sh — review Copilot PRs
# Usage: bash ralph/review.sh
# Lists open Copilot PRs and requests review on each.

set -eo pipefail

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "=== Ralph Review · repo: $REPO ==="

# List PRs created by copilot
prs=$(gh pr list --repo "$REPO" --author "copilot" --state open --json number,title,url -q '.[] | "#\(.number) \(.title) → \(.url)"')

if [ -z "$prs" ]; then
  echo "No open Copilot PRs found."
  exit 0
fi

echo "Open Copilot PRs:"
echo "$prs"
echo ""

# Show diff for each PR
while IFS= read -r line; do
  pr_num=$(echo "$line" | grep -oE '#[0-9]+' | tr -d '#')
  echo "--- PR #$pr_num ---"
  gh pr diff "$pr_num" --repo "$REPO" | head -100
  echo "...(truncated, run 'gh pr diff $pr_num' for full diff)"
  echo ""
done <<< "$prs"
echo "=== Review complete ==="
