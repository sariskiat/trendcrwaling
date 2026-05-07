#!/usr/bin/env python3
"""PreToolUse hook: blocks rm commands targeting paths outside the repo."""

import json
import re
import sys

REPO_ROOT = "/Users/saris.kia.adm/Desktop/search-engine-api"

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")

if re.search(r"\brm\b", cmd):
    abs_paths = re.findall(r"/[^\s'\";&|>]+", cmd)
    outside = [p for p in abs_paths if not p.startswith(REPO_ROOT)]
    if outside:
        print(
            json.dumps(
                {
                    "continue": False,
                    "stopReason": f"Blocked: rm targeting path outside repo: {', '.join(outside)}",
                }
            )
        )
        sys.exit(0)

print(json.dumps({"continue": True}))
