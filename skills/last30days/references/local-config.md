# last30days Local Configuration (Leonardo's Setup)

## Python Path
```bash
PYTHON=/opt/homebrew/bin/python3.12
```

## Config File
Location: `~/.config/last30days/.env`

```env
SCRAPECREATORS_API_KEY=<key>
SCRAPERAPI_API_KEY=<key>
OMKAR_API_KEY=<key>
SETUP_COMPLETE=true
```

## Data Source Status (2026-06-08)

| Source | Status | Notes |
|--------|--------|-------|
| YouTube | ✅ Working | yt-dlp installed, best coverage |
| Reddit | ❌ 403 Blocked | JSON API blocked by anti-bot |
| TikTok | ⚠️ Via Omar API | ScrapeCreators credits exhausted |
| Instagram | ❌ Credits out | ScrapeCreators credits exhausted |
| Threads | ❌ Credits out | ScrapeCreators credits exhausted |
| X/Twitter | ❌ Not authed | Need browser login at x.com |
| Hacker News | ✅ Working | Free, no auth needed |
| GitHub | ✅ Working | Free, no auth needed |
| Polymarket | ✅ Working | Free, no auth needed |

## Omar TikTok Scraper API (Alternative)

When ScrapeCreators credits are exhausted, use Omar API directly:

### Endpoints
- Video details: `GET /tiktok/videos/details?video_url=<url>`
- User profile: `GET /tiktok/users/profile?handle=<handle>`
- Video search: `GET /tiktok/videos/search?search_query=<query>`
- Trending: `GET /tiktok/videos/trending`
- User videos: `GET /tiktok/users/videos?handle=<handle>`

### Auth
```bash
-H "API-Key: YOUR_OMKAR_API_KEY"
```

### Base URL
`https://tiktok-scraper.omkar.cloud`

### Pricing
- Free: 100 queries/month
- $16: 3K queries/month
- $48: 15K queries/month

## ScraperAPI (General Web Scraping)

For scraping any website with proxy rotation and JS rendering:

```bash
curl "http://api.scraperapi.com?api_key=$SCRAPERAPI_API_KEY&url=https://example.com&render=true"
```

Works for TikTok profile pages when API access is unavailable.

## Known Pitfalls

1. **ScrapeCreators credits**: 100 free credits, then PAYG. Check balance before large runs.
2. **Reddit 403**: Public JSON API is blocked. Use ScraperAPI proxy or browser cookies.
3. **X/Twitter auth**: Must login in Safari/Firefox, then skill reads cookies.
4. **Safari cookies**: "Permission denied reading Cookies.binarycookies" — need Full Disk Access for Terminal in System Settings > Privacy & Security.
5. **Named-entity topics**: Must pass `--plan` JSON or use `--auto-resolve`. Without it, engine runs deterministic fallback (weaker).
