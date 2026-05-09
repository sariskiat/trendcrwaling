# [ISSUE-045] Instagram: Reels selector + shortcode timestamp decode

## Type
AFK

## Priority
infra

## Blocked by
Nothing — parallel with ISSUE-043 and ISSUE-044

## Context

The current Instagram scraper uses `a[href*='/p/']` which misses Reels (`/reel/` URLs). Additionally, no timestamp is available on the profile grid — this issue adds a fast shortcode-based timestamp decoder (no extra HTTP requests) so the 10-day recency filter can work for Instagram.

The Instagram shortcode is a base62-encoded number that includes the creation timestamp as the high bits (Instagram's snowflake-style ID).

## Acceptance Criteria

- [ ] `_POST_LINK_SELECTOR` in `scrapers/instagram.py` updated to `a[href*='/p/'], a[href*='/reel/']`
- [ ] New `_shortcode_to_timestamp(shortcode: str) -> int` function that decodes a post shortcode to a Unix timestamp using base62 decode → right-shift 23 bits → add Instagram epoch (1314220021)
- [ ] `InstagramPost` TypedDict gains `created_at: int` field (Unix timestamp, 0 if decode fails)
- [ ] `scrape_user` populates `created_at` from the shortcode extracted from `post_url`
- [ ] Unit test: `_shortcode_to_timestamp("CnvGmGiLTcD")` returns a timestamp in the expected range (2023 era)
- [ ] All quality gates pass: `ruff .`, `black --check .`, `pytest -x --cov`, pyright

## Files to Modify

| File | Change |
|------|--------|
| `scrapers/instagram.py` | Update selector, add shortcode decoder, add `created_at` to `InstagramPost` |
| `tests/test_instagram.py` | Add selector and shortcode decode tests |

## TDD Gate

```python
def test_shortcode_to_timestamp_known_value():
    ts = _shortcode_to_timestamp("CnvGmGiLTcD")
    # This post is from early 2023
    assert 1672531200 < ts < 1704067200  # 2023-01-01 to 2024-01-01

def test_scrape_user_result_has_created_at(mock_playwright):
    posts = await scrape_user("testuser")
    assert all("created_at" in p for p in posts)
```

## Notes

- Shortcode decode formula: `id = base62_decode(shortcode); ts = (id >> 23) + 1314220021`
- If `post_url` has no shortcode (malformed), set `created_at = 0` (will fail the 10-day filter safely)
