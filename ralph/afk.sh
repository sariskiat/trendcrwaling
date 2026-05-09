#!/bin/bash
# ralph/afk.sh — looped AFK run with parallel reviewers each iteration
# Usage:
#   bash ralph/afk.sh <iterations>               # run on host
#   bash ralph/afk.sh <iterations> --container   # each iteration in Docker
#
# Requires: GitHub Copilot CLI, Docker (for --container mode)
# Models: gpt-4.1 (supervisor) + gpt-5-mini (reviewers)

set -eo pipefail

if [ -z "$1" ]; then
  echo "Usage: $0 <iterations> [--container]"
  exit 1
fi

ITERATIONS="$1"
USE_CONTAINER=false
for arg in "$@"; do
  [[ "$arg" == "--container" ]] && USE_CONTAINER=true
done

# Verify Copilot CLI is available
if ! command -v copilot &>/dev/null; then
  echo "Error: Copilot CLI not found."
  echo "Install: gh extension install github/gh-copilot"
  exit 1
fi

# Build Docker image once before the loop if container mode requested
if [[ "$USE_CONTAINER" == true ]]; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  IMAGE="ralph-agent"
  if [[ "$(docker images -q "$IMAGE" 2>/dev/null)" == "" ]]; then
    echo "=== Building $IMAGE image ==="
    docker build -f "$REPO_ROOT/ralph/Dockerfile.agent" -t "$IMAGE" "$REPO_ROOT"
  fi
fi

for ((i=1; i<=ITERATIONS; i++)); do
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  ITERATION $i/$ITERATIONS                                    ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""

  # --- Phase 1: Supervisor (delegates to once.sh) ---
  echo "=== Phase 1: Ralph Supervisor ==="

  ONCE_FLAGS=""
  [[ "$USE_CONTAINER" == true ]] && ONCE_FLAGS="--container"

  result=$(bash ralph/once.sh $ONCE_FLAGS 2>&1)
  echo "$result"

  if [[ "$result" == *"<promise>NO MORE TASKS</promise>"* ]]; then
    echo ""
    echo "✅ Ralph complete after $i iterations."
    exit 0
  fi

  # --- Phase 2: Parallel Reviewers (claude-sonnet-4-5) ---
  echo ""
  echo "=== Phase 2: Parallel Reviewers ==="

  diff=$(git diff main...HEAD 2>/dev/null)
  if [ -z "$diff" ]; then
    diff=$(git diff HEAD~1...HEAD 2>/dev/null || echo "(no diff available)")
  fi

  # Agent 1: review-protocol (tests, integration, structure)
  copilot --agent ralph-reviewer \
    --model gpt-5-mini \
    --allow-all-tools \
    -p "Review the following diff for review-protocol compliance — tests first, then integration, then structure:

$diff" &
  PID1=$!

  # Agent 2: code-standards (types, naming, modules, docstrings)
  copilot --agent ralph-reviewer \
    --model gpt-5-mini \
    --allow-all-tools \
    -p "Review the following diff for code-standards compliance — types, error handling, naming, module design, enums, immutability, docstrings:

$diff" &
  PID2=$!

  wait $PID1 $PID2
  echo "=== Review complete ==="
done

echo ""
echo "⏸️  Completed $1 iterations. Run again to continue."
