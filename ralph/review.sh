#!/bin/bash
# ralph/review.sh — review open PRs for current branch or all open PRs
# Usage: bash ralph/review.sh [pr_number]
#   No args: reviews all open PRs
#   With arg: reviews that specific PR

set -eo pipefail

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "=== Ralph Review · repo: $REPO ==="

if [ -n "$1" ]; then
  # Review a specific PR
  prs=$(gh pr view "$1" --repo "$REPO" --json number,title,url -q '"#\(.number) \(.title) → \(.url)"')
else
  # Review all open PRs
  prs=$(gh pr list --repo "$REPO" --state open --json number,title,url -q '.[] | "#\(.number) \(.title) → \(.url)"')
fi

if [ -z "$prs" ]; then
  echo "No open PRs found."
  exit 0
fi

echo "Open PRs:"
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
