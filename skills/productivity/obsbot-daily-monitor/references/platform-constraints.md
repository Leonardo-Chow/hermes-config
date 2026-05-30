# OBSBOT Daily Monitoring — Platform Constraints & Tool Matrix

## Platform-by-Platform Status (verified 2026-05-29)

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

### TikTok ❌ NOT WORKING
- **Root cause:** X-Bogus anti-bot token mechanism
- **What happens:** Profile page loads (HTTP 200), user info visible (followers, bio), playlists visible, but video grid shows "出错了" (error). SSR `itemList` is empty. All API calls return 0 bytes.
- **Approaches tried (all failed):**
  1. curl + proxy + cookies → HTTP 200, 0 bytes
  2. Scrapling DynamicFetcher + proxy → Page loads, 0 video links
  3. Scrapling StealthyFetcher + proxy → Same
  4. Playwright + cookies + proxy → Detected as headless
  5. bb-browser (real Chrome) + cookie injection → Video grid error
  6. Direct TikTok API calls from browser fetch → Empty response (missing X-Bogus)
- **Alternatives:**
  - NoxInfluencer Brand Monitor (requires brand_id from web UI)
  - Manual check of @obsbot profile
  - NoxInfluencer creator search (finds tagged creators, not today's posts)

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
  ├── Task 2: Instagram Scrapling + X/Twitter web_search
  └── Task 3: Tencent Docs folder lookup + smartsheet creation
```

Total execution time: ~3-5 minutes (YouTube API is fastest, Instagram Scrapling takes 30-60s)
