# Reddit Scraping with Camoufox/Scrapling

## Problem
Reddit aggressively blocks automated access:
- **curl/requests**: Returns 403 Blocked (even with realistic User-Agent)
- **Reddit JSON API** (`/search.json`, `/.json`): Returns empty responses or 403
- **Browser automation** (Playwright/Puppeteer): Detected and blocked
- **web_extract** (DuckDuckGo backend): Cannot extract Reddit content

## Solution: Camoufox (Scrapling StealthyFetcher)
Camoufox's anti-detection fingerprinting bypasses Reddit's bot detection.

```python
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
page = fetcher.fetch('https://www.reddit.com/r/SUBREDDIT/comments/ID/TITLE/')
text = page.get_all_text()
```

## Limitations
- **Slow**: ~15-20 seconds per page (includes retries and redirects)
- **No structured data**: Returns plain text, not JSON. Comments need manual parsing
- **JavaScript comments**: Reddit loads comments via JS; Scrapling gets the initial render only
- **Rate limiting**: Needs 2-3 second delay between requests
- **Timeouts**: Some pages timeout on first attempt, auto-retry works

## Parsing Scraped Reddit Text
The scraped text follows a pattern:
```
Post title : r/Subreddit
u/author • Xmo ago
Post content text...
Read more
Share
u/commenter1 (X pts)
Comment text...
u/commenter2
Comment text...
```

Key parsing rules:
- Skip lines containing: 'Sign Up', 'Log In', 'Open menu', 'Promoted', 'navyfederal', 'shopify'
- Comment authors match: `u/username` followed by `•` or newline
- Scores match: `N pts` or `N points`
- Post content is between the author line and "Read more"

## Alternative: Reddit Search API (partial data)
The search API sometimes works for getting post metadata (titles, scores, selftext) even when individual post pages are blocked:
```bash
curl -s -A "Mozilla/5.0" "https://www.reddit.com/search.json?q=QUERY&sort=relevance&t=all&limit=100"
```
This returns: title, author, subreddit, score, num_comments, selftext, permalink
But NOT comments, and may be blocked intermittently.

## Recommended Workflow
1. Use search.json API to get post list and metadata (fast, may work)
2. Use Camoufox to scrape top N most relevant posts (slow but reliable)
3. Parse plain text to extract post content and comments
4. Generate Word doc with python-docx

## Tested: 2026-05-14
- 74 posts found via search API
- 6 posts successfully scraped with full content via Camoufox
- Total time: ~2 minutes for 6 posts
