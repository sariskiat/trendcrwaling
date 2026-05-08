"""OpenAI Vision API wrapper for image analysis."""

from __future__ import annotations

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from mcp_server.exceptions import AnalysisError


async def analyze_image_with_vision(
    image_url: str,
    prompt: str = "Describe this image in detail",
    api_key: str = "",
) -> str:
    """Analyze an image using OpenAI Vision API.

    Args:
        image_url: URL of the image to analyze.
        prompt: Text prompt for the analysis.
        api_key: OpenAI API key to use for the request.

    Returns:
        Text description/analysis from the model.

    Raises:
        AnalysisError: If the model returns an empty response.
    """
    client: AsyncOpenAI = AsyncOpenAI(api_key=api_key)
    response: ChatCompletion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=1024,
    )

    # Extract content safely and raise if it's missing or empty.
    try:
        content = response.choices[0].message.content
    except (IndexError, AttributeError):
        content = None

    if not content:
        raise AnalysisError("OpenAI returned empty response content")

    return content
