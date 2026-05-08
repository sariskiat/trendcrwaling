"""Tests for the image analysis tool using OpenAI Vision."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


async def test_analyze_image_success() -> None:
    """analyze_image returns text analysis on successful OpenAI response."""
    from mcp_server.server import analyze_image

    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content="A blue sky with clouds"))
    ]

    with (
        patch(
            "mcp_server.image_analysis.AsyncOpenAI",
            return_value=AsyncMock(
                chat=AsyncMock(
                    completions=AsyncMock(create=AsyncMock(return_value=mock_response))
                )
            ),
        ),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
    ):
        result = await analyze_image("https://example.com/image.jpg")

    assert isinstance(result, str)
    assert result == "A blue sky with clouds"


async def test_analyze_image_with_custom_prompt() -> None:
    """analyze_image uses custom prompt when provided."""
    from mcp_server.server import analyze_image

    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(message=AsyncMock(content="Analysis"))]

    with (
        patch(
            "mcp_server.image_analysis.AsyncOpenAI",
            return_value=AsyncMock(
                chat=AsyncMock(
                    completions=AsyncMock(create=AsyncMock(return_value=mock_response))
                )
            ),
        ),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
    ):
        result = await analyze_image(
            "https://example.com/image.jpg", prompt="List all objects"
        )

    assert isinstance(result, str)
    assert result == "Analysis"


async def test_analyze_image_missing_api_key() -> None:
    """analyze_image raises ConfigurationError with actionable message when OPENAI_API_KEY not set."""
    from mcp_server.server import analyze_image, ConfigurationError

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ConfigurationError,
            match="OPENAI_API_KEY environment variable is not set",
        ):
            await analyze_image("https://example.com/image.jpg")


async def test_analyze_image_invalid_url() -> None:
    """analyze_image raises ValidationError for non-http URL."""
    from mcp_server.server import analyze_image, ValidationError

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(ValidationError, match="image_url must start with http"):
            await analyze_image("file:///local/path/image.jpg")


async def test_analyze_image_invalid_url_no_scheme() -> None:
    """analyze_image raises ValidationError for URL without scheme."""
    from mcp_server.server import analyze_image, ValidationError

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with pytest.raises(ValidationError, match="image_url must start with http"):
            await analyze_image("example.com/image.jpg")


async def test_analyze_image_empty_response_raises() -> None:
    """analyze_image raises AnalysisError when OpenAI response content is None or empty."""
    from mcp_server.server import analyze_image, AnalysisError

    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(message=AsyncMock(content=None))]

    with (
        patch(
            "mcp_server.image_analysis.AsyncOpenAI",
            return_value=AsyncMock(
                chat=AsyncMock(
                    completions=AsyncMock(create=AsyncMock(return_value=mock_response))
                )
            ),
        ),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
    ):
        with pytest.raises(AnalysisError):
            await analyze_image("https://example.com/image.jpg")


async def test_analyze_image_empty_choices_raises_analysis_error() -> None:
    """analyze_image raises AnalysisError when choices list is empty (IndexError case)."""
    from mcp_server.server import analyze_image, AnalysisError

    mock_response = AsyncMock()
    mock_response.choices = []  # Empty choices triggers IndexError

    with (
        patch(
            "mcp_server.image_analysis.AsyncOpenAI",
            return_value=AsyncMock(
                chat=AsyncMock(
                    completions=AsyncMock(create=AsyncMock(return_value=mock_response))
                )
            ),
        ),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
    ):
        with pytest.raises(AnalysisError):
            await analyze_image("https://example.com/image.jpg")


async def test_analyze_image_missing_message_raises_analysis_error() -> None:
    """analyze_image raises AnalysisError when message is None (AttributeError case)."""
    from mcp_server.server import analyze_image, AnalysisError

    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=None)
    ]  # None message triggers AttributeError

    with (
        patch(
            "mcp_server.image_analysis.AsyncOpenAI",
            return_value=AsyncMock(
                chat=AsyncMock(
                    completions=AsyncMock(create=AsyncMock(return_value=mock_response))
                )
            ),
        ),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
    ):
        with pytest.raises(AnalysisError):
            await analyze_image("https://example.com/image.jpg")
