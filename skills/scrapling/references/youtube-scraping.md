# YouTube Scraping with Scrapling

## Overview

YouTube is a dynamic JS-rendered site that requires `DynamicFetcher` for scraping. Key challenges:
- Content loads via JavaScript (can't use HTTP fetcher)
- Likes/comments are dynamically loaded (may need scrolling)
- VPN required from China (youtube.com is blocked by GFW)

## Verified CSS Selectors (2026-05-10)

### Video Page Elements

| Element | Selector | Notes |
|---------|----------|-------|
| **Channel name** | `a.yt-simple-endpoint::attr(href)` | Look for `/@username` pattern |
| **View count** | `span.view-count::text` | Returns "11,156次观看" |
| **Description** | `meta[name="description"]::attr(content)` | Meta tag, reliable |
| **Hashtags** | `a[href*="hashtag/"]::text` | Returns list of hashtags |
| **Video title** | `meta[property="og:title"]::attr(content)` | Meta tag |

### Extraction Pattern

```python
from scrapling.fetchers import DynamicFetcher
import re

def extract_youtube_video(url):
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, disable_resources=True)
    
    # Channel name (from link)
    channel = 'N/A'
    channel_links = page.css('a.yt-simple-endpoint::attr(href)').getall()
    for link in channel_links:
        if '/@' in link:
            channel = '@' + link.split('/@')[1]
            break
    
    # View count
    views = 'N/A'
    all_text = page.css('body *::text').getall()
    full_text = ' '.join(all_text)
    view_match = re.search(r'([\d,]+)\s*次观看', full_text)
    if view_match:
        views = view_match.group(1)
    
    # Description (from meta)
    description = page.css('meta[name="description"]::attr(content)').get() or 'N/A'
    
    # Hashtags
    hashtags = ', '.join(page.css('a[href*="hashtag/"]::text').getall()[:5])
    
    return {
        'channel': channel,
        'views': views,
        'description': description[:200],
        'hashtags': hashtags
    }
```

## Known Limitations

### Likes and Comments
- **Problem**: Likes and comments are loaded via JavaScript after initial page load
- **Current workaround**: Can extract from `aria-label` attributes if available
- **Best effort**: `page.css('[aria-label*="like"]::attr(aria-label)')` may return labels like "1,234 likes this video"
- **Alternative**: Search page text for patterns like `([\d,.]+)\s*(?:likes|赞)`

### Proxy Connection Issues
- YouTube may fail with `ERR_PROXY_CONNECTION_FAILED` on some requests
- **Workaround**: Retry the request or skip that video
- **Pattern**: ~5-10% of requests may fail due to proxy issues

## Batch Processing Best Practices

1. **Rate limiting**: Add 3-5 second delay between requests to avoid rate limits
2. **Error handling**: Wrap each request in try/except, continue on failure
3. **Progress tracking**: Print progress for each video (user feedback)
4. **Save intermediate results**: Save to JSON after each batch in case of failure

```python
import time
import json

for i, video in enumerate(videos, 1):
    try:
        result = extract_youtube_video(video['url'])
        video_details.append(result)
        print(f"{i}. ✅ {result['channel']} | {result['views']}次观看")
    except Exception as e:
        print(f"{i}. ❌ {str(e)[:30]}")
        video_details.append({'channel': 'N/A', 'views': 'N/A', ...})
    
    time.sleep(3)  # Rate limiting
    
    # Save every 10 videos
    if i % 10 == 0:
        with open('/tmp/progress.json', 'w') as f:
            json.dump(video_details, f)
```

## Complete Example Script

See `scripts/youtube_scraper.py` for a complete batch scraping script.

## Integration with Tencent Docs

After scraping, data can be uploaded to Tencent Docs using the `tencent-docs` skill:

```python
# 1. Create sheet in target folder
mcporter call tencent-docs manage.create_file --args '{
  "file_type": "sheet",
  "title": "YouTube Video Data",
  "parent_id": "folder_id"
}'

# 2. Get sheet_id
mcporter call tencent-docs sheet.get_sheet_info --args '{"file_id": "xxx"}'

# 3. Write data using sheet.set_range_value
```
