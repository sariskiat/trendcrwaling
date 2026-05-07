# [ISSUE-008] Replace `# type: ignore` suppressions with correct types

**Type:** `AFK`
**Priority:** `bug`
**Blocked by:** none
**Blocks:** none
**Module(s):** `scrapers/`, `mcp_server/`

---

## Context

Three `# type: ignore[arg-type]` comments suppress real type errors rather than fixing them. Each one hides a mismatch that the type checker correctly flagged.

## What to build

Fix the three suppressions:

**1. `scrapers/facebook.py` line 89**
```python
await ctx.add_cookies(_load_cookies(cookie_path))  # type: ignore[arg-type]
```
`add_cookies` expects `list[SetCookieParam]` but `_load_cookies` returns `list[dict[str, str]]`.
Fix: change `_load_cookies` return type to `list[SetCookieParam]` and construct `SetCookieParam` objects directly. Import `SetCookieParam` from `playwright.async_api`.

**2. `mcp_server/server.py` line 117**
```python
platforms: list[str] = list(arguments["platforms"])  # type: ignore[arg-type]
```
`arguments` is typed `dict[str, object]` so `arguments["platforms"]` is `object`.
Fix: cast explicitly — `platforms: list[str] = list(cast(list[str], arguments["platforms"]))` — and import `cast` from `typing`.

**3. `mcp_server/server.py` line 118**
```python
limit: int = int(arguments.get("limit", 20))  # type: ignore[arg-type]
```
Same root cause. Fix: `limit: int = int(cast(int | str, arguments.get("limit", 20)))`.

After all three are fixed, no `# type: ignore` should remain in `scrapers/facebook.py` or `mcp_server/server.py`.

## Acceptance criteria

- [ ] Failing test written **before** any implementation (TDD — non-negotiable)
- [ ] Zero `# type: ignore` comments in `scrapers/facebook.py` and `mcp_server/server.py`
- [ ] `ruff .` passes
- [ ] `pytest -x` passes

## Out of scope

Other files are not in scope.

## Notes

`cast()` is the correct tool when you know the runtime type but the static type system does not. It is not a suppression — it is an assertion. If `cast` feels wrong, consider narrowing `arguments` to a `TypedDict` instead.
