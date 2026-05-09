"""Hashtag generator using OpenAI chat completions."""

from __future__ import annotations

import os

from openai import AsyncOpenAI

__all__ = ["ConfigurationError", "generate_hashtags"]

_PLATFORM_HINTS: dict[str, str] = {
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "facebook": "Facebook",
    "general": "social media",
}

_SYSTEM_TEMPLATE = (
    "You are a social media hashtag expert specialised in {platform}. "
    "Given a topic, return exactly 10 relevant, trending hashtags for {platform}. "
    "Output only the hashtags, one per line, without the # symbol and without any "
    "other text, numbering, or explanation."
)


class ConfigurationError(Exception):
    """Raised when required configuration (e.g. API key) is missing."""


async def generate_hashtags(query: str, platform: str = "general") -> list[str]:
    """Return 10 hashtags for the query, without # prefix.

    Args:
        query: The topic or search query to generate hashtags for.
        platform: Target platform — one of instagram, tiktok, facebook, general.

    Returns:
        List of exactly 10 hashtag strings (no # prefix).

    Raises:
        ConfigurationError: If OPENAI_API_KEY environment variable is not set.
        ValueError: If query is empty or longer than 500 characters.
    """
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ConfigurationError(
            "OPENAI_API_KEY environment variable is not set. "
            "Set it before calling generate_hashtags()."
        )

    if not query or not query.strip():
        raise ValueError("query must not be empty")
    if len(query) > 500:
        raise ValueError(f"query must not exceed 500 characters, got {len(query)}")

    platform_label = _PLATFORM_HINTS.get(platform.lower(), platform)
    system_prompt = _SYSTEM_TEMPLATE.format(platform=platform_label)

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.7,
        max_tokens=200,
    )

    raw_content: str = response.choices[0].message.content or ""
    hashtags: list[str] = []
    for line in raw_content.splitlines():
        tag = line.strip().lstrip("#").strip()
        if tag:
            hashtags.append(tag)

    return hashtags[:10]
