# Instagram Scraping with Scrapling

## Verified Working (2026-05-29)

Instagram @obsbot profile successfully scraped using StealthyFetcher with Shadowrocket proxy.

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://www.instagram.com/obsbot/',
    headless=True,
    network_idle=True,
    disable_resources=True,
    proxy='http://127.0.0.1:1082',  # Shadowrocket
    block_webrtc=True,
    hide_canvas=True,
)

# Extract post links
links = page.css('a[href*="/p/"]::attr(href)').getall()
links += page.css('a[href*="/reel/"]::attr(href)').getall()

# Extract text content
texts = page.css('article *::text').getall()
```

## What Works
- Profile page scraping (12 posts visible)
- Post URLs, bio, follower count, descriptions
- Hashtag page (#obsbot top posts with play counts)

## What Doesn't Work
- Exact post dates (not shown on public profile)
- Engagement metrics (likes/comments need login)
- Individual post pages (login wall)

## TikTok Comparison
Same approach tried for TikTok — page loads but video grid fails (X-Bogus anti-bot). TikTok video list scraping is a hard constraint.
