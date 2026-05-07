# [ISSUE-012] Wire Playwright Instagram scraper into MCP server and remove instagrapi

**Type:** `AFK`
**Priority:** `infra`
**Blocked by:** ISSUE-011
**Blocks:** none
**Module(s):** `mcp_server/`, `scrapers/`

---

## Context

ISSUE-011 rewrites `scrapers/instagram.py` to use Playwright with a new signature: `scrape_user(username, limit)` — no `session_file`. This issue updates all call sites, removes the old instagrapi wiring from the MCP server, and deletes the now-obsolete `setup_ig_session.py`.

## What to build

### 1. Update `mcp_server/server.py`

Remove the `_IG_SESSION_FILE` constant:
```python
# delete this line:
_IG_SESSION_FILE: str = os.getenv("IG_SESSION_FILE", "ig_session.json")
```

Update the `handle_analyze_competitor` call for Instagram:
```python
# before:
results["instagram"] = scrape_instagram(name, _IG_SESSION_FILE, limit)

# after:
results["instagram"] = await scrape_instagram(name, limit)
```

Note: `scrape_instagram` is now `async` (Playwright-based) — add `await`.

### 2. Update `scrapers/__init__.py`

`scrape_instagram` is aliased from `scrapers.instagram.scrape_user`. Verify the alias still resolves correctly after the signature change. No change needed if the alias is a bare name re-export — just confirm it.

### 3. Delete `setup_ig_session.py`

This script was only needed for instagrapi. Delete it.

### 4. Update `tests/test_server.py`

The server test for Instagram calls `scrape_instagram` with the old sync mock. Update it:
- Mock `scrape_instagram` as `AsyncMock` (it is now async)
- Remove any `session_file` argument from the mock call assertion

## Acceptance criteria

- [ ] Failing test written **before** any implementation (TDD — non-negotiable)
- [ ] `mcp_server/server.py` has no reference to `_IG_SESSION_FILE` or `IG_SESSION_FILE`
- [ ] `scrape_instagram` called as `await scrape_instagram(name, limit)` in server
- [ ] `setup_ig_session.py` deleted
- [ ] `tests/test_server.py` mocks `scrape_instagram` as `AsyncMock`
- [ ] `ruff .` passes
- [ ] `black --check .` passes
- [ ] `pytest -x --cov` passes, all tests green

## Out of scope

- The Playwright scraper implementation itself — that is ISSUE-011
- Stories, Reels video download, comments, followers, posting

## Notes

After this issue, `instagrapi` can be removed from `pyproject.toml` dependencies if it is no longer imported anywhere. Run `grep -r "instagrapi" .` to confirm before removing.
