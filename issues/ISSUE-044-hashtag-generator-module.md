# [ISSUE-044] Hashtag generator module

## Type
AFK

## Priority
infra

## Blocked by
Nothing — parallel with ISSUE-043 and ISSUE-045

## Context

Mode 2 (query hashtag trending) across all three platforms requires converting a freeform user query into 10 platform-relevant hashtags. This module calls OpenAI using the existing `OPENAI_API_KEY` and returns a ranked list of hashtags.

## Acceptance Criteria

- [ ] New file `scrapers/hashtag_generator.py` created
- [ ] `generate_hashtags(query: str, platform: str = "general") -> list[str]` function that calls OpenAI chat completions
- [ ] Returns exactly 10 hashtags (without `#` prefix — callers add `#` themselves)
- [ ] Raises `ConfigurationError` if `OPENAI_API_KEY` is not set
- [ ] Raises `ValueError` if `query` is empty or longer than 500 characters
- [ ] Uses `gpt-4o-mini` model (cheapest capable model) with a system prompt tailored per platform
- [ ] Unit tests in `tests/test_hashtag_generator.py` using mocked OpenAI response
- [ ] All quality gates pass: `ruff .`, `black --check .`, `pytest -x --cov`, pyright

## Files to Create/Modify

| File | Change |
|------|--------|
| `scrapers/hashtag_generator.py` | **NEW** |
| `tests/test_hashtag_generator.py` | **NEW** |

## TDD Gate

Write a failing test first:
```python
def test_generate_hashtags_returns_10(mock_openai):
    result = generate_hashtags("summer fashion", platform="instagram")
    assert len(result) == 10
    assert all(not h.startswith("#") for h in result)

def test_generate_hashtags_raises_on_empty_query():
    with pytest.raises(ValueError):
        generate_hashtags("")
```

## Interface

```python
async def generate_hashtags(query: str, platform: str = "general") -> list[str]:
    """Return 10 hashtags for the query, without # prefix."""
```
