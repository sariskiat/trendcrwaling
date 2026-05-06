"""Tests for the Facebook scraper."""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from scrapers.facebook import FacebookPost, FacebookScraperError, scrape_page


def test_scrape_page_returns_structured_posts() -> None:
    mock_posts: list[dict[str, object]] = [
        {
            "text": "Today's special buffet!",
            "likes": 150,
            "time": "2026-05-01 12:00:00",
            "post_url": "https://www.facebook.com/mk.suki.official/posts/123",
            "image": "https://example.com/img1.jpg",
        },
        {
            "text": "Weekend deal",
            "likes": 80,
            "time": "2026-04-30 10:00:00",
            "post_url": "https://www.facebook.com/mk.suki.official/posts/456",
            "image": "https://example.com/img2.jpg",
        },
    ]

    with patch("scrapers.facebook.get_posts", return_value=iter(mock_posts)):
        result: list[FacebookPost] = scrape_page("mk.suki.official", limit=2)

    assert len(result) == 2
    assert result[0]["text"] == "Today's special buffet!"
    assert result[0]["likes"] == 150
    assert result[0]["time"] == "2026-05-01 12:00:00"
    assert result[0]["post_url"] == "https://www.facebook.com/mk.suki.official/posts/123"
    assert result[0]["image_url"] == "https://example.com/img1.jpg"


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
    assert result[0]["post_url"] == ""
    assert result[0]["image_url"] == ""


def test_scrape_page_raises_on_invalid_limit() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        scrape_page("mk.suki.official", limit=0)


def test_scrape_page_raises_scraper_error_on_failure() -> None:
    with patch("scrapers.facebook.get_posts", side_effect=RuntimeError("blocked")):
        with pytest.raises(FacebookScraperError, match="Failed to scrape Facebook page"):
            scrape_page("mk.suki.official", limit=5)


def test_scrape_page_uses_cookie_file_when_env_set() -> None:
    fake_cookiejar: object = object()
    with patch.dict(os.environ, {"FB_COOKIES_FILE": "fb_cookies.txt"}):
        with patch("scrapers.facebook.parse_cookie_file", return_value=fake_cookiejar) as mock_parse:
            with patch("scrapers.facebook.set_cookies") as mock_set:
                with patch("scrapers.facebook.get_posts", return_value=iter([])) as mock_get:
                    scrape_page("barbegon", limit=5)
    mock_parse.assert_called_once_with("fb_cookies.txt")
    mock_set.assert_called_once_with(fake_cookiejar)
    mock_get.assert_called_once_with("barbegon", pages=3)


def test_scrape_page_skips_cookies_when_env_missing() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with patch("scrapers.facebook.set_cookies") as mock_set:
            with patch("scrapers.facebook.get_posts", return_value=iter([])) as mock_get:
                scrape_page("barbegon", limit=5)
    mock_set.assert_not_called()
    mock_get.assert_called_once_with("barbegon", pages=3)
