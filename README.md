# Sukishi Trend Research — MCP Server

MCP server for scraping social media posts from TikTok, Instagram, and Facebook, plus image analysis via OpenAI Vision.

## Quick Start

```bash
uv run python -m mcp_server.server
```

## TikTok Scraping Sources

This project supports multiple TikTok scraping backends:

| Source | Type | Cost | Reliability | Requirements |
|--------|------|------|-------------|--------------|
| TikTok-Api | Unofficial API | Free | May hit rate limits | `TT_MS_TOKEN` env var |
| TikAPI.io | Managed API | Paid | Reliable | `TIKAPI_KEY` env var |
| Apify Clockworks | Managed API | Pay-per-result | 98% success rate | `APIFY_TOKEN` env var |
| Playwright | Headless browser | Free | Requires cookies | `TT_COOKIES_FILE` env var |

Set `TIKTOK_SOURCE=auto` (default) to try TikTok-Api first, then fall back to others.
Set `TIKTOK_SOURCE=api`, `TIKTOK_SOURCE=tikapi`, or `TIKTOK_SOURCE=apify` to use a specific source.

## Available Tools

### `tiktok_user_posts`
Scrape recent TikTok posts for a given username.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `username` | `str` | required | TikTok handle without @ |
| `limit` | `int` | `20` | Max posts to return (1-100) |

### `tiktok_trending`
Scrape trending TikTok posts from the Explore page.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `20` | Max posts to return (1-100) |

### `tiktok_hashtag_posts`
Scrape TikTok posts for a given hashtag.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tag` | `str` | required | Hashtag without # (e.g. `sukiyaki`) |
| `limit` | `int` | `20` | Max posts to return (1-100) |

### `instagram_user_posts`
Scrape Instagram posts for a given user.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `username` | `str` | required | Instagram username |
| `limit` | `int` | `20` | Max posts to return (1-100) |

### `facebook_page_posts`
Scrape Facebook posts from a public page.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page_name` | `str` | required | Facebook page name/slug |
| `limit` | `int` | `20` | Max posts to return (1-100) |

### `analyze_image`
Analyze an image using OpenAI Vision API.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_url` | `str` | required | URL of the image (http/https) |
| `prompt` | `str` | `"Describe this image in detail"` | What to analyze |

## Required Environment Variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `TIKTOK_SOURCE` | TikTok tools | Source selection: `auto` (default), `api`, `tikapi`, `apify` |
| `TT_COOKIES_FILE` | TikTok tools (Playwright) | Path to TikTok Netscape cookies.txt |
| `TT_MS_TOKEN` | TikTok tools (TikTok-Api) | TikTok ms_token for unofficial API |
| `TIKAPI_KEY` | TikTok tools (TikAPI.io) | API key from tikapi.io |
| `APIFY_TOKEN` | TikTok tools (Apify) | API token from apify.com |
| `IG_COOKIES_FILE` | Instagram tool | Path to Instagram Netscape cookies.txt |
| `FB_COOKIES_FILE` | Facebook tool | Path to Facebook Netscape cookies.txt |
| `OPENAI_API_KEY` | `analyze_image` | OpenAI API key for Vision |

## Planned Tools

- `instagram_recent_posts` — scrape recent/explore Instagram posts
- `facebook_recent_posts` — scrape recent public Facebook posts

## Development

```bash
uv run pytest              # run tests
uv run ruff check .        # lint
uv run pyright             # type check
```
