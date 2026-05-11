"""Tests for the hashtag generator module."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapers.hashtag_generator import ConfigurationError, generate_hashtags


def _make_openai_mock(hashtags: list[str]) -> MagicMock:
    """Return a mock openai AsyncOpenAI client that returns given hashtags."""
    content = "\n".join(hashtags)
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]

    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=response)
    return mock_client


@pytest.fixture()
def mock_openai_client() -> MagicMock:
    hashtags = [f"hashtag{i}" for i in range(10)]
    return _make_openai_mock(hashtags)


async def test_generate_hashtags_returns_ten_normalized_tags():
    # This is a REAL integration test: fires a real OpenAI API call (no mocks)
    import os
    import re

    if not os.environ.get("OPENAI_API_KEY"):
        import pytest

        pytest.skip(
            "OPENAI_API_KEY not set in environment; skipping real integration test."
        )
    from scrapers.hashtag_generator import generate_hashtags

    tags = await generate_hashtags("summer fashion", platform="instagram")
    assert isinstance(tags, list)
    assert len(tags) == 10
    assert all(isinstance(t, str) for t in tags)
    assert all(not t.startswith("#") for t in tags)
    assert all(t == t.lower() for t in tags)
    assert len(set(tags)) == 10
    assert all(re.match(r"^[a-z0-9_]+$", t) for t in tags)
    # Force fail for TDD: no implementation yet
    assert False, "TDD: force fail until implemented"


async def test_generate_hashtags_raises_on_empty_query() -> None:
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(ValueError, match="empty"):
            await generate_hashtags("")


async def test_generate_hashtags_raises_on_long_query() -> None:
    long_query = "x" * 501
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(ValueError, match="500"):
            await generate_hashtags(long_query)


async def test_generate_hashtags_raises_configuration_error_without_api_key() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
            await generate_hashtags("summer fashion")


async def test_generate_hashtags_uses_platform_in_prompt(
    mock_openai_client: MagicMock,
) -> None:
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch(
            "scrapers.hashtag_generator.AsyncOpenAI", return_value=mock_openai_client
        ):
            await generate_hashtags("travel", platform="tiktok")
    call_args = mock_openai_client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    system_msg = next(m for m in messages if m["role"] == "system")
    assert "tiktok" in system_msg["content"].lower()


async def test_generate_hashtags_strips_hash_prefix(
    mock_openai_client: MagicMock,
) -> None:
    """If OpenAI returns hashtags with # prefix, they should be stripped."""
    hashtags_with_prefix = [f"#tag{i}" for i in range(10)]
    client = _make_openai_mock(hashtags_with_prefix)
    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "test-key"},
    ):
        with patch("scrapers.hashtag_generator.AsyncOpenAI", return_value=client):
            result = await generate_hashtags("test")
    assert all(not h.startswith("#") for h in result)


async def test_generate_hashtags_default_platform(
    mock_openai_client: MagicMock,
) -> None:
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch(
            "scrapers.hashtag_generator.AsyncOpenAI", return_value=mock_openai_client
        ):
            result = await generate_hashtags("food")
    assert len(result) == 10
