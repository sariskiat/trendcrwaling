"""Public scraper interface — one function per platform."""

from __future__ import annotations

from scrapers.facebook import FacebookPost, scrape_page as scrape_facebook
from scrapers.instagram import InstagramPost, scrape_user as scrape_instagram
from scrapers.tiktok import TikTokPost, scrape_user as scrape_tiktok
from scrapers.tiktok import scrape_hashtag as scrape_tiktok_hashtag
from scrapers.tiktok import scrape_trending as scrape_tiktok_trending

__all__ = [
    "scrape_tiktok",
    "scrape_tiktok_trending",
    "scrape_tiktok_hashtag",
    "scrape_instagram",
    "scrape_facebook",
    "TikTokPost",
    "InstagramPost",
    "FacebookPost",
]
