"""Tests for the Instagram scraper."""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from scrapers.instagram import InstagramPost, InstagramScraperError, scrape_user


def test_scrape_user_returns_structured_posts(tmp_path: Any) -> None:
    session_file: str = str(tmp_path / "session.json")

    mock_media: MagicMock = MagicMock()
    mock_media.thumbnail_url = "https://instagram.com/p/abc/media.jpg"
    mock_media.caption_text = "Barbegon special night"
    mock_media.like_count = 320

    mock_client: MagicMock = MagicMock()
    mock_client.user_id_from_username.return_value = "99999"
    mock_client.user_medias.return_value = [mock_media]

    with patch("scrapers.instagram.Client", return_value=mock_client):
        result: list[InstagramPost] = scrape_user("barbegon", session_file, limit=1)

    assert len(result) == 1
    assert result[0]["url"] == "https://instagram.com/p/abc/media.jpg"
    assert result[0]["caption"] == "Barbegon special night"
    assert result[0]["likes"] == 320
    mock_client.load_settings.assert_called_once_with(session_file)


def test_scrape_user_passes_limit_to_api(tmp_path: Any) -> None:
    session_file: str = str(tmp_path / "session.json")

    mock_client: MagicMock = MagicMock()
    mock_client.user_id_from_username.return_value = "99999"
    mock_client.user_medias.return_value = []

    with patch("scrapers.instagram.Client", return_value=mock_client):
        scrape_user("barbegon", session_file, limit=7)

    mock_client.user_medias.assert_called_once_with("99999", amount=7)


def test_scrape_user_raises_on_invalid_limit(tmp_path: Any) -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        scrape_user("barbegon", str(tmp_path / "s.json"), limit=0)


def test_scrape_user_raises_scraper_error_on_api_failure(tmp_path: Any) -> None:
    session_file: str = str(tmp_path / "session.json")

    mock_client: MagicMock = MagicMock()
    mock_client.load_settings.side_effect = RuntimeError("session expired")

    with patch("scrapers.instagram.Client", return_value=mock_client):
        with pytest.raises(InstagramScraperError, match="Failed to scrape Instagram user"):
            scrape_user("barbegon", session_file, limit=5)
