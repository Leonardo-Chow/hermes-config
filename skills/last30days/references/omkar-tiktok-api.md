# Omar TikTok Scraper API

**Homepage**: https://www.omkar.cloud/tools/tiktok-scraper
**Free Tier**: 100 queries/month, no credit card
**Pricing**: $16/3K, $48/15K, $148/75K queries

## Authentication

```
Header: API-Key: ok_82a...92b
```

## Endpoints

### Video Details
```
GET https://tiktok-scraper.omkar.cloud/tiktok/videos/details
Params: video_url (required) — Full TikTok video URL
```

Returns: video_id, caption, duration, author info, media URLs (HD/watermark-free), stats (views/likes/comments/shares/downloads/saves), audio info, thumbnails.

### User Profile
```
GET https://tiktok-scraper.omkar.cloud/tiktok/users/profile
Params: handle (required) — Username without @
```

Returns: user_id, handle, display_name, bio, avatar URLs, is_verified, stats (following/followers/likes/videos).

### Video Search
```
GET https://tiktok-scraper.omkar.cloud/tiktok/videos/search
Params: search_query (required) — Search keyword
```

Returns: Array of video objects with full details.

### Trending Videos
```
GET https://tiktok-scraper.omkar.cloud/tiktok/videos/trending
Params: None
```

Returns: Array of trending video objects.

### User Videos
```
GET https://tiktok-scraper.omkar.cloud/tiktok/users/videos
Params: handle (required) — Username without @
```

Returns: Array of user's videos.

## Test Results (2026-06-08)

| Endpoint | Status | Notes |
|:---------|:-------|:------|
| video/details | ✅ | Full data with HD download URLs |
| users/profile | ✅ | Verified accounts detected |
| videos/search | ✅ | Returns multiple results |
| videos/trending | ✅ | Global trending feed |
| users/videos | ⏳ | Not tested |

## Parameter Names (Pitfall!)

- `handle` NOT `username` for user endpoints
- `search_query` NOT `keyword` for search
- No `count` parameter — returns all results

## Comparison with Other TikTok Sources

| Feature | Omar API | ScrapeCreators | ScraperAPI | last30days native |
|:--------|:---------|:---------------|:-----------|:------------------|
| Video details | ✅ | ❌ (credits) | ❌ | ❌ |
| User profile | ✅ | ❌ | ❌ | ❌ |
| Search | ✅ | ❌ | ❌ | ❌ |
| Trending | ✅ | ❌ | ❌ | ❌ |
| HD download | ✅ | ❌ | ❌ | ❌ |
| Free tier | 100/mo | 0 (exhausted) | 5000 | N/A |

**Recommendation**: Use Omar API as primary TikTok data source. ScrapeCreators is out of credits. ScraperAPI requires parsing HTML.
