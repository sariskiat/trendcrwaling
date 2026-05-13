#!/usr/bin/env bash
set -euo pipefail

echo "=== ruff ==="
uv run ruff check .

echo "=== pyright ==="
uv run pyright || echo "⚠ pyright warnings (non-blocking)"

echo "=== pytest ==="
uv run pytest

echo ""
echo "=== Environment green ==="
echo ""
cat STATUS.md
