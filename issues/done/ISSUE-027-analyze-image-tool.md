# [ISSUE-027] Add analyze_image tool with OpenAI Vision

**Type:** AFK
**Priority:** infra
**Blocked by:** ISSUE-023

---

## Summary

Create `mcp_server/image_analysis.py` wrapping OpenAI Vision API. Register `analyze_image` tool on the FastMCP server. Takes any image URL, returns a text description/analysis. Requires `OPENAI_API_KEY` env var.

---

## Acceptance Criteria

- [ ] `mcp_server/image_analysis.py` created with async function calling OpenAI Vision
- [ ] `analyze_image(image_url: str, prompt: str = "Describe this image in detail")` tool registered
- [ ] Missing `OPENAI_API_KEY` returns MCP error response with actionable message
- [ ] Invalid/unreachable URL returns MCP error response
- [ ] Tool annotated `readOnlyHint=True`
- [ ] `openai` added to `pyproject.toml` dependencies
- [ ] Tests: success case (mocked OpenAI), missing-key error, bad-url error
- [ ] **TDD gate:** failing test first
- [ ] Quality gates: `uv run pytest`, `uv run ruff check .`, `uv run pyright`

---

## Out of Scope

- Auto-triggering on scrape results
- Image caching or storage
- Multiple images in one call

---

## Files to Create / Modify

| File | Action |
|---|---|
| `mcp_server/image_analysis.py` | Create — OpenAI Vision wrapper |
| `mcp_server/server.py` | Register `analyze_image` tool |
| `tests/test_image_analysis.py` | Create — tests for image analysis |
| `pyproject.toml` | Add `openai` dependency |
