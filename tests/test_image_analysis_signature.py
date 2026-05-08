"""TDD: test that analyze_image_with_vision accepts an `api_key` parameter.

This test should fail before implementation (TypeError) and pass after.
"""

from unittest.mock import AsyncMock, patch


async def test_analyze_image_with_api_key_param() -> None:
    from mcp_server.image_analysis import analyze_image_with_vision

    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(message=AsyncMock(content="Signature OK"))]

    with patch(
        "mcp_server.image_analysis.AsyncOpenAI",
        return_value=AsyncMock(
            chat=AsyncMock(
                completions=AsyncMock(create=AsyncMock(return_value=mock_response))
            )
        ),
    ):
        # Call with explicit api_key parameter (new contract)
        result = await analyze_image_with_vision(
            "https://example.com/image.jpg", "Prompt", "test-key"
        )

    assert result == "Signature OK"
