# OBSBOT Daily Monitoring — Platform Constraints & Tool Matrix

## Platform-by-Platform Status (verified 2026-05-31)

### YouTube ✅ FULLY WORKING
- **Tool:** YouTube Data API (`curl` + API Key)
- **API Key:** `YOUR_YOUTUBE_API_KEY`
- **Capabilities:** Search by keyword, date filter (`publishedAfter`/`publishedBefore`), full snippet (title, description, tags), video statistics, channel info
- **Reliability:** HIGH — direct API, no scraping needed
- **Rate limits:** 10,000 quota units/day (sufficient for daily monitoring)

### Instagram ⚠️ PARTIALLY WORKING
- **Tool:** Scrapling StealthyFetcher + Shadowrocket proxy
- **Proxy:** `http://127.0.0.1:1082`
- **Capabilities:** Scrape @obsbot profile page — post links (`/p/`, `/reel/`), post content text, hashtags, tagged accounts
- **Limitations:**
  - Cannot get exact post dates from public profile (posts are ordered newest-first but no timestamp)
  - Cannot get engagement metrics (likes/comments) without login
  - Instagram Stories not accessible
- **Workaround for dates:** Scrape individual post URLs via `web_extract` or oembed API
- **Reliability:** MEDIUM — works for content, fails for dates

### TikTok ✅ WORKING (search + oembed approach)
- **Verified:** 2026-05-31
- **What works:**
  1. **Search page via Scrapling**: `StealthyFetcher.fetch('https://www.tiktok.com/search?q=KEYWORD', proxy='http://127.0.0.1:1082')` → `a[href*="/video/"]::attr(href)` returns video links
  2. **oembed API via proxy**: `curl -s -x http://127.0.0.1:1082 "https://www.tiktok.com/oembed?url=VIDEO_URL"` → returns title, author, thumbnail. Direct access (no proxy) gets connection reset.
  3. **Video ID → timestamp**: `int(video_id) >> 32` gives Unix timestamp (seconds) for precise publish date filtering
  4. **web_search indirect**: `site:tiktok.com OBSBOT` discovers video links via search engine indexing
- **What does NOT work:** Profile page scraping triggers CAPTCHA slider puzzle for most accounts. SSR `itemList` is always empty.
- **Workflow:** web_search for links → oembed API for metadata → video ID decode for date → filter today's content
- **Reliability:** HIGH for content discovery; profile scraping still blocked
- **Known accounts:** `@obsbot` (17.5K), `@obsbot_us`, `@obsbot.my`, `@obsbot_official` (PH)
- **Key hashtags:** `#obsbot`, `#obsbot_tiny3lite`, `#obsbot_tiny3`

### X/Twitter ⚠️ NOT CONFIGURED
- **Tools available:**
  - `xurl` CLI — needs `xurl auth apps add` (register X App first)
  - `twitter` CLI (agent-reach) — needs browser login to x.com first
  - `web_search` — works but index delay is 1-3 days
- **Current status:** xurl has no apps registered, twitter CLI has no cookies
- **Action needed:** User must register xurl App or log into x.com in Chrome

## Proxy Configuration

| Proxy | Address | Protocol | Source |
|-------|---------|----------|--------|
| Shadowrocket (primary) | `127.0.0.1:1082` | HTTP + SOCKS5 | macOS system tunnel (utun4) |
| v2rayN | `127.0.0.1:10808` / `10809` | HTTP / SOCKS5 | Backup |
| ClashX Pro | `127.0.0.1:7890` | HTTP | Unstable, avoid |

## NoxInfluencer Brand Monitor

- **Status:** Not configured for OBSBOT (brand_id not obtained)
- **Blocking:** Need user to visit noxinfluencer.com → Brand Monitor → search "OBSBOT" → copy brand_id
- **Command:** `noxinfluencer brand-monitor add <brand_id> --force`
- **See:** `noxinfluencer skill references/brand-monitor-setup.md` for full details

## Parallel Execution Strategy

```
delegate_task (3 parallel):
  ├── Task 1: YouTube API search + full descriptions
  ├── Task 2: TikTok search+oembed + Instagram Scrapling
  └── Task 3: X/Twitter web_search + Tencent Docs setup
```

Total execution time: ~3-5 minutes (YouTube API is fastest, TikTok oembed is fast, Instagram Scrapling takes 30-60s)
