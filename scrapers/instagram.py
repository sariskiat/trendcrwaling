"""Instagram scraper using Instagrapi. Requires a saved session file from a throwaway account."""

from __future__ import annotations

from typing import TypedDict

from instagrapi import Client

__all__ = ["InstagramPost", "InstagramScraperError", "scrape_user"]


class InstagramPost(TypedDict):
    """A single Instagram post returned by the scraper."""

    url: str
    caption: str
    likes: int


class InstagramScraperError(Exception):
    """Raised when Instagram scraping fails due to session or network errors."""


def scrape_user(
    username: str, session_file: str, limit: int = 20
) -> list[InstagramPost]:
    """Return recent posts for an Instagram username.

    Args:
        username: Instagram handle without @.
        session_file: Path to saved Instagrapi session JSON (throwaway account).
        limit: Max number of posts to return. Must be positive.

    Returns:
        List of InstagramPost dicts with keys: url, caption, likes.

    Raises:
        ValueError: If limit is not positive.
        InstagramScraperError: If the Instagrapi call fails.
    """
    if limit <= 0:
        raise ValueError(f"limit must be positive, got {limit}")
    try:
        cl: Client = Client()
        cl.load_settings(session_file)
        user_id: str = cl.user_id_from_username(username)
        medias = cl.user_medias(user_id, amount=limit)
        return [
            InstagramPost(
                url=str(m.thumbnail_url),
                caption=m.caption_text,
                likes=m.like_count,
            )
            for m in medias
        ]
    except Exception as exc:
        raise InstagramScraperError(
            f"Failed to scrape Instagram user '{username}': {exc}"
        ) from exc
