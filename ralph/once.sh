#!/bin/bash
# ralph/once.sh — single AFK run (supervisor in isolated container)
# Usage:
#   bash ralph/once.sh                  # run supervisor on host
#   bash ralph/once.sh --container      # run supervisor in Docker container
#
# Container mode mounts:
#   - repo (rw) at /workspace
#   - ~/.config/github-copilot (ro) for Copilot CLI auth
#   - ~/.gitconfig (ro) so git commits have correct author
#
# Requires: GitHub Copilot CLI, Docker (for --container mode)

set -eo pipefail

# ── Parse flags ────────────────────────────────────────────────────────────────
USE_CONTAINER=false
for arg in "$@"; do
  [[ "$arg" == "--container" ]] && USE_CONTAINER=true
done

# ── Container mode: re-exec this script inside Docker ─────────────────────────
if [[ "$USE_CONTAINER" == true ]]; then
  if ! command -v docker &>/dev/null; then
    echo "Error: Docker not found. Install Docker Desktop or Docker Engine."
    exit 1
  fi

  REPO_ROOT="$(git rev-parse --show-toplevel)"
  IMAGE="ralph-agent"

  # Build image if it doesn't exist yet (or if Dockerfile changed)
  if [[ "$(docker images -q "$IMAGE" 2>/dev/null)" == "" ]]; then
    echo "=== Building $IMAGE image (first run) ==="
    docker build -f "$REPO_ROOT/ralph/Dockerfile.agent" -t "$IMAGE" "$REPO_ROOT"
  fi

  echo "=== Launching supervisor container ==="
  exec docker run --rm \
    --name "ralph-supervisor-$$" \
    -v "$REPO_ROOT:/workspace" \
    -v "$HOME/.config/github-copilot:/root/.config/github-copilot:ro" \
    -v "$HOME/.gitconfig:/root/.gitconfig:ro" \
    -e GITHUB_TOKEN="${GITHUB_TOKEN:-}" \
    -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    -e TT_COOKIES_FILE="${TT_COOKIES_FILE:-}" \
    -e IG_COOKIES_FILE="${IG_COOKIES_FILE:-}" \
    -e FB_COOKIES_FILE="${FB_COOKIES_FILE:-}" \
    -w /workspace \
    "$IMAGE" \
    bash ralph/once.sh
  # ↑ re-runs this script inside the container without --container flag
fi

# ── Host / in-container execution ─────────────────────────────────────────────
if ! command -v copilot &>/dev/null; then
  echo "Error: Copilot CLI not found."
  echo "Install: gh extension install github/gh-copilot"
  exit 1
fi

commits=$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found")

# Classify open issues by their ## Type field
afk_issues=""
hitl_issues=""
for f in issues/*.md; do
  [ -f "$f" ] || continue
  if grep -qi '^## Type' "$f" && grep -qi 'HITL' "$f"; then
    hitl_issues="$hitl_issues\n\n=== $f ===\n$(cat "$f")"
  else
    afk_issues="$afk_issues\n\n=== $f ===\n$(cat "$f")"
  fi
done

afk_issues=${afk_issues:-"No AFK issues found"}
hitl_issues=${hitl_issues:-"No HITL issues found"}

copilot --agent ralph-supervisor \
  --allow-all-tools \
  -p "Previous commits:
$commits

---
AFK ISSUES (implement these):
$afk_issues

---
HITL ISSUES (skip — human required, shown for awareness):
$hitl_issues"
