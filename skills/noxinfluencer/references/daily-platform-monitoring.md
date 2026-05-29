# Daily Platform Monitoring Workflow

## Overview

Daily monitoring of OBSBOT (or similar brand) content across YouTube, Instagram, TikTok, and X/Twitter. Each platform has different scraping characteristics and limitations.

## Platform-by-Platform Approach

### YouTube ✅ Reliable

**Tool:** YouTube Data API (key: stored in user memory)
**Method:** Direct API calls, no scraping needed

```bash
# Search for brand videos from today
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=OBSBOT&type=video&publishedAfter=2026-05-29T00:00:00Z&publishedBefore=2026-05-29T23:59:59Z&maxResults=20&key=API_KEY"

# Get FULL descriptions (including links, promo codes, tags, disclaimers)
curl -s "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=VIDEO_ID1,VIDEO_ID2,VIDEO_ID3&key=API_KEY"
```

**Tips:**
- Use multiple search queries (product name, brand name, "review", etc.) for coverage
- The `snippet.description` field contains the FULL video description — every word, link, tag, promo code
- Can batch up to 50 video IDs in one `videos?part=snippet` call
- `publishedAfter/publishedBefore` filters work reliably for date filtering
- If date filter returns nothing, search without dates and manually check `publishedAt`

### Instagram ⚠️ Medium Reliability

**Tool:** Scrapling StealthyFetcher (headless + anti-detection)
**Method:** Scrape @brand profile page

```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch(
    'https://www.instagram.com/brand_handle/',
    headless=True, network_idle=True, disable_resources=True,
    block_webrtc=True, hide_canvas=True,
)
```

**What works:**
- Post URLs (`/p/...` and `/reel/...`)
- Post content/caption (truncated)
- Product mentions from content
- Hashtag top posts

**Limitations:**
- **No exact post dates** without login — Instagram hides dates on public profiles
- Posts are ordered most-recent-first but dates unknown
- `web_extract` is blocked by Instagram's login wall
- Engagement metrics (likes/comments) not available without login

**Workaround for dates:**
- Use web_search with post URL to find date references in search snippets
- Cross-reference with other sources (Facebook mirror, partner accounts)

### TikTok ❌ Very Difficult

**Tool:** None reliable from CLI/automation
**Root cause:** TikTok's X-Bogus anti-bot token system

**What was tried (all failed for video listing):**
1. **curl + proxy** — Gets page HTML but video grid is empty (SSR `itemList: []`)
2. **Scrapling DynamicFetcher + proxy** — Page loads (HTTP 200) but video grid doesn't render in DOM
3. **Playwright + cookies + proxy** — Cookies set, page loads, but video grid still empty. Modal overlays block interaction
4. **TikTok API (`/api/post/item_list/`)** — Returns HTTP 200 with 0 bytes. Requires X-Bogus token generated client-side
5. **TikTok oembed API** — Works for individual video metadata but not for listing videos

**What partially works:**
- Scrapling gets relative time markers (e.g., "12h", "2d") from the page text
- TikTok oembed API returns video title and author for known video IDs
- NoxInfluencer `creator search` returns tagged creators (not today's specific posts)

**For reliable TikTok monitoring, need:**
- NoxInfluencer Brand Monitor with brand_id from web UI
- Or manual checking of @brand TikTok account
- Or TikTok Business API (requires business account)

**Proxy for TikTok:**
```python
# Shadowrocket proxy for GFW bypass
proxy = "http://127.0.0.1:1082"
page = DynamicFetcher.fetch(url, proxy=proxy, ...)
```

### X/Twitter ⚠️ Needs Configuration

**Tools available but not configured:**
1. **xurl CLI** — Requires `xurl auth apps add` (register X App for API access)
2. **twitter CLI (agent-reach)** — Requires browser login to x.com for cookie extraction
3. **web_search** — Returns indexed results but real-time indexing is delayed

**Current state:** Neither xurl nor twitter CLI is configured. Web search found no today-dated OBSBOT content on X.

**To configure xurl:**
```bash
xurl auth apps add  # Register X App with Client ID/Secret
xurl search "OBSBOT" -n 20  # Search tweets
```

**To configure twitter CLI:**
1. Log into x.com in Chrome
2. `twitter search "OBSBOT"` — auto-extracts cookies from Chrome

## Shadowrocket Proxy Details

- **Address:** `127.0.0.1:1082` (HTTP and SOCKS5 on same port)
- **Process:** Shadowrocket macOS (`MacPacketTunnel`)
- **External IP:** Changes per VPN exit node
- **Works with:** curl, Scrapling Fetcher, Playwright (with `proxy={"server": "http://127.0.0.1:1082"}`)
- **Does NOT work with:** Scrapling DynamicFetcher for TikTok (anti-bot detection)

## Tencent Docs Smart Sheet Workflow

For daily monitoring output, create/update smartsheet in Tencent Docs:

```python
# 1. Create smartsheet
mcporter call 'tencent-docs' 'manage.create_file' --args '{"title": "Daily Monitor YYYY-MM-DD", "file_type": "smartsheet"}'

# 2. Get sheet_id
mcporter call 'tencent-docs' 'smartsheet.list_tables' --args '{"file_id": "FILE_ID"}'

# 3. Delete default fields, add custom fields
mcporter call 'tencent-docs' 'smartsheet.delete_fields' --args '{"file_id": "F", "sheet_id": "S", "field_ids": ["ID"]}'
mcporter call 'tencent-docs' 'smartsheet.add_fields' --args '{"file_id": "F", "sheet_id": "S", "fields": [...]}'

# 4. Add records (batch)
mcporter call 'tencent-docs' 'smartsheet.add_records' --args '{"file_id": "F", "sheet_id": "S", "records": [...]}'

# 5. Move to target folder
mcporter call 'tencent-docs' 'manage.move_file' --args '{"file_id": "F", "target_folder_id": "FOLDER_ID"}'
```

**Field type for links:** Use `text` type, not `url` type (user preference).
