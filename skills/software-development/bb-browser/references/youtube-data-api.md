# YouTube Data API v3 Workflow

Complete workflow for searching YouTube videos, getting stats, and uploading to Tencent Docs.

## Prerequisites

- YouTube Data API Key (stored in memory)
- `curl` and `python3` available

## Step 1: Search Videos

```bash
# Search with date filter
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=QUERY&type=video&maxResults=50&publishedAfter=2024-08-01T00:00:00Z&order=date&key=API_KEY"

# Response: items[].id.videoId, items[].snippet.{title, channelId, channelTitle, publishedAt, description}
# Pagination: nextPageToken
```

## Step 2: Get Video Statistics

```bash
# Batch up to 50 video IDs
curl -s "https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id=id1,id2,id3&key=API_KEY"

# Response: items[].statistics.{viewCount, likeCount, commentCount}
# Response: items[].snippet.tags[]
```

## Step 3: Get Channel Statistics

```bash
# Batch up to 50 channel IDs
curl -s "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=id1,id2&key=API_KEY"

# Response: items[].statistics.{subscriberCount, hiddenSubscriberCount}
```

## Step 4: Generate CSV and Upload

```python
# CSV format: 博主名称,博主粉丝量,视频标题,观看次数,点赞量,评论数量,发布日期,产品型号,Tags,视频链接
# Upload to Tencent Docs sheet using sheet.set_range_value (key=value format, NOT --args)
```

## Pitfalls

- **Rate limiting**: Add 0.5s delay between API calls
- **Batch limits**: Videos/Channels API accepts max 50 IDs per call
- **Hidden subscribers**: Some channels hide subscriber count (`hiddenSubscriberCount: true`)
- **Search relevance**: YouTube search may return irrelevant results; filter by title keywords after fetching
- **Pagination**: Search returns max 50 per page; use `nextPageToken` for more (up to ~500 total)
- **Tencent Docs upload**: Use `key=value` format for `sheet.set_range_value`, NOT `--args`
- **Date format**: `publishedAfter` must be RFC 3339 format: `2024-08-01T00:00:00Z`
