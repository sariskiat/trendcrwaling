"""Tests for the Facebook scraper."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from scrapers.facebook import FacebookPost, FacebookScraperError, scrape_page


def test_scrape_page_returns_structured_posts() -> None:
    mock_posts: list[dict[str, object]] = [
        {"text": "Today's special buffet!", "likes": 150, "time": "2026-05-01 12:00:00"},
        {"text": "Weekend deal", "likes": 80, "time": "2026-04-30 10:00:00"},
    ]

    with patch("scrapers.facebook.get_posts", return_value=iter(mock_posts)):
        result: list[FacebookPost] = scrape_page("mk.suki.official", limit=2)

    assert len(result) == 2
    assert result[0]["text"] == "Today's special buffet!"
    assert result[0]["likes"] == 150
    assert result[0]["time"] == "2026-05-01 12:00:00"


def test_scrape_page_respects_limit() -> None:
    mock_posts: list[dict[str, object]] = [
        {"text": f"Post {i}", "likes": i * 10, "time": "2026-05-01"}
        for i in range(5)
    ]

    with patch("scrapers.facebook.get_posts", return_value=iter(mock_posts)):
        result: list[FacebookPost] = scrape_page("mk.suki.official", limit=2)

    assert len(result) == 2


def test_scrape_page_handles_missing_fields() -> None:
    with patch("scrapers.facebook.get_posts", return_value=iter([{}])):
        result: list[FacebookPost] = scrape_page("mk.suki.official", limit=1)

    assert result[0]["text"] == ""
    assert result[0]["likes"] == 0
    assert result[0]["time"] == ""


def test_scrape_page_raises_on_invalid_limit() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        scrape_page("mk.suki.official", limit=0)


def test_scrape_page_raises_scraper_error_on_failure() -> None:
    with patch("scrapers.facebook.get_posts", side_effect=RuntimeError("blocked")):
        with pytest.raises(FacebookScraperError, match="Failed to scrape Facebook page"):
            scrape_page("mk.suki.official", limit=5)
