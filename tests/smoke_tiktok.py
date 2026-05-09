"""Live smoke test — hits real TikTok and verifies output shape.

Usage:
    uv run python -m tests.smoke_tiktok mk_suki 3

Requires: TT_COOKIES_FILE env var (optional but recommended).
Exit 0 = pass, Exit 1 = shape mismatch or scrape failure.
"""

from __future__ import annotations

import asyncio
import json
import sys

from scrapers.tiktok import TikTokPost, scrape_user

_REQUIRED_KEYS: set[str] = {"url", "desc", "likes", "views", "thumbnail_url", "author"}


async def _smoke(username: str, limit: int) -> None:
    print(f"[smoke] scrape_user('{username}', {limit})...")
    posts: list[TikTokPost] = await scrape_user(username, limit)

    # --- shape assertions ---
    assert isinstance(posts, list), f"Expected list, got {type(posts)}"
    assert len(posts) > 0, "Got 0 posts — page might be blocked or empty"
    assert len(posts) <= limit, f"Got {len(posts)} posts, expected <= {limit}"

    for i, post in enumerate(posts):
        missing = _REQUIRED_KEYS - set(post.keys())
        assert not missing, f"Post[{i}] missing keys: {missing}"
        assert isinstance(post["url"], str) and post["url"].startswith("http"), (
            f"Post[{i}] bad url: {post['url']}"
        )
        assert isinstance(post["views"], int), f"Post[{i}] views not int"
        assert isinstance(post["likes"], int), f"Post[{i}] likes not int"
        assert isinstance(post["author"], str) and post["author"], (
            f"Post[{i}] author empty"
        )

    print(f"[smoke] PASS — {len(posts)} posts, all shapes valid")
    print(json.dumps(posts[:2], indent=2, ensure_ascii=False))


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: uv run python -m tests.smoke_tiktok <username> <limit>")
        sys.exit(2)

    username = sys.argv[1]
    limit = int(sys.argv[2])
    asyncio.run(_smoke(username, limit))


if __name__ == "__main__":
    main()
