"""Public scraper interface — one function per platform."""
from __future__ import annotations

from scrapers.facebook import FacebookPost, scrape_page as scrape_facebook
from scrapers.instagram import InstagramPost, scrape_user as scrape_instagram
from scrapers.tiktok import TikTokPost, scrape_user as scrape_tiktok

__all__ = [
    "scrape_tiktok",
    "scrape_instagram",
    "scrape_facebook",
    "TikTokPost",
    "InstagramPost",
    "FacebookPost",
]
