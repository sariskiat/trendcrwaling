# [ISSUE-010] Add `black` and `pytest-cov` to dev dependencies

**Type:** `AFK`
**Priority:** `infra`
**Blocked by:** none
**Blocks:** none
**Module(s):** `pyproject.toml`

---

## Context

The quality gate requires `black --check .` and `pytest -x --cov` to pass, but neither `black` nor `pytest-cov` is in `pyproject.toml`. Both commands fail with "No such file or directory" and "unrecognized arguments" respectively. The gate is broken.

## What to build

In `pyproject.toml`, add both tools to the `[dependency-groups] dev` section:

```toml
[dependency-groups]
dev = [
    "black>=24.0.0",
    "pytest>=9.0.2",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=5.0.0",
]
```

Then run `uv sync` to install them and verify both commands pass:

```bash
uv run black --check .
uv run pytest -x --cov=.
```

If `black --check .` fails on existing files, reformat them first: `uv run black .`

## Acceptance criteria

- [ ] `black` and `pytest-cov` listed in `[dependency-groups] dev`
- [ ] `uv run black --check .` exits 0
- [ ] `uv run pytest -x --cov` exits 0
- [ ] All 18 existing tests still pass

## Out of scope

No source code changes — only tooling and formatting.

## Notes

Run `uv run black .` (auto-format) before `black --check .` (verify) to avoid failing the gate on pre-existing style issues. Commit the reformatted files as a separate chore commit before adding to CI.
