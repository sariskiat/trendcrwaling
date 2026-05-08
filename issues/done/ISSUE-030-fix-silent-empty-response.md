# [ISSUE-030] Fix silent empty response in image_analysis.py

**Type:** AFK
**Priority:** blocker
**Blocked by:** none

---

## Summary

`analyze_image_with_vision()` returns `response.choices[0].message.content or ""` — if OpenAI returns `None` content (refusals, empty responses), the caller gets an empty string with no error indication. This is a silent sentinel that masks failures.

Replace with explicit check and raise `ValueError` on empty/None content.

---

## Acceptance Criteria

- [ ] `or ""` replaced with explicit None/empty check that raises `ValueError`
- [ ] `analyze_image` docstring in `server.py` updated with `Raises:` section documenting both ValueError cases (bad URL + missing API key + empty response)
- [ ] Test added: mock OpenAI returning None content → verify ValueError raised
- [ ] Type annotations added to `api_key`, `client`, `response` variables in `image_analysis.py`
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Review Findings Addressed

- B2: `or ""` masking failures
- B4: `analyze_image` docstring missing Raises
- W4: missing type annotations in image_analysis.py

---

## Files to Modify

| File | Action |
|---|---|
| `mcp_server/image_analysis.py` | Fix empty response handling, add type annotations |
| `mcp_server/server.py` | Update `analyze_image` docstring Raises section |
| `tests/test_image_analysis.py` | Add test for None/empty OpenAI response |
