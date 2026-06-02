# Reddit Scraping Workflow

Complete workflow for searching Reddit posts, fetching comments, filtering, and uploading to Tencent Docs.

## Prerequisites

1. **VPN must be connected** — Reddit is blocked in China
   ```bash
   用户先手动开启 Shadowrocket VPN
   sleep 5
   用户确认 VPN 已连接后再继续
   ```

2. **bb-browser daemon** must be running for `site` commands

## Step 1: Search Posts

**⚠️ CRITICAL: Always use exact phrase quotes!** Without quotes, Reddit search returns irrelevant garbage (cats, Paris rants, etc.).

```bash
# ✅ CORRECT — exact phrase search (returns up to 50 posts)
bb-browser site reddit/search "\"OBSBOT Tiny 2\"" --json

# ✅ CORRECT — direct curl with URL encoding
curl -s -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://www.reddit.com/search.json?q=%22OBSBOT+Tiny+2%22&sort=new&t=all&limit=50"

# ❌ WRONG — unquoted search returns garbage
bb-browser site reddit/search "OBSBOT Tiny 2" --json

# Use multiple search queries per product for comprehensive results:
queries = ['"OBSBOT Tiny 2"', '"OBSBOT Tiny 2 Lite"', 'obsbot tiny2']
```

**Python URL encoding:**
```python
from urllib.parse import quote
encoded = quote('"OBSBOT Tiny 2"')  # %22OBSBOT+Tiny+2%22
url = f'https://www.reddit.com/search.json?q={encoded}&sort=new&t=all&limit=50'
```

**Response format:**
```json
{
  "data": {
    "children": [
      {
        "data": {
          "id": "1rug4uu",
          "title": "...",
          "author": "username",
          "subreddit": "r/OBSBOT_Official",
          "created_utc": 1773586595,
          "num_comments": 6,
          "permalink": "/r/OBSBOT_Official/comments/1rug4uu/...",
          "selftext_preview": "...",
          "score": 5
        }
      }
    ]
  }
}
```

**⚠️ `selftext_preview` is NOT the full post body!** Must fetch via Step 2 to get complete `selftext`.

## Step 2: Fetch Post Body + Comments

**Important:** `reddit/post` does NOT exist. Use direct JSON API to get BOTH the full post body AND comments:

```bash
curl -s -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://www.reddit.com/comments/POST_ID.json"

# Response: [post_listing, comments_listing]
# Post body at: [0].data.children[0].data.selftext
# Comments at: [1].data.children[].data
# Each comment: {author, body, score, created_utc}
```

**Python extraction:**
```python
def get_post_and_comments(post_id):
    """Get BOTH full post body AND comments in one call."""
    url = f'https://www.reddit.com/comments/{post_id}.json'
    result = subprocess.run(
        ['curl', '-s', '-L', '-A', 'Mozilla/5.0 ...', url],
        capture_output=True, text=True, timeout=20
    )
    data = json.loads(result.stdout)
    if isinstance(data, list) and len(data) >= 2:
        post_data = data[0].get('data', {}).get('children', [{}])[0].get('data', {})
        comments = data[1].get('data', {}).get('children', [])
        return post_data, comments
    return {}, []

# Usage:
post_data, comments = get_post_and_comments('1rug4uu')
selftext = post_data.get('selftext', '')  # Full post body
```

## Step 3: Filter Posts

### Filter out official accounts
```python
user_posts = [p for p in posts if p.get('author') != 'OBSBOT-Official']
```

### Filter by time (Unix timestamp)
```python
from datetime import datetime
cutoff = datetime(2026, 1, 28).timestamp()  # 1738022400
filtered = [p for p in posts if p.get('created_utc', 0) >= cutoff]
```

### Filter by topic (e.g., separate Tiny 3 from Tiny 3 Lite)
```python
tiny3_only = [p for p in posts if 'lite' not in p.get('title', '').lower()]
tiny3_lite = [p for p in posts if 'lite' in p.get('title', '').lower()]
```

## Step 4: Format for Tencent Docs

```markdown
# Product Name - Reddit User Discussions

**Generated:** 2026-05-13 13:08
**Time Range:** 2026-01-28 to present
**Filter:** User posts only (excluded official posts)

---

## Post Title
- **Author:** u/username
- **Date:** 2026-04-15
- **URL:** https://www.reddit.com/comments/POST_ID

### Comments (N user comments)

**u/commenter** (X pts):
> Comment body text here

---
```

## Step 5: Upload to Tencent Docs

```bash
# Create smart document (title max 36 chars!)
mcporter call tencent-docs create_smartcanvas_by_mdx \
  title="Short Title Here" \
  mdx="$(cat /tmp/file.md)"

# Move to target folder
mcporter call tencent-docs manage.move_file \
  file_id="Dxxxxxxxx" \
  target_folder_id="FOLDER_ID"

# Verify
mcporter call tencent-docs manage.folder_list folder_id="FOLDER_ID"
```

## Complete Python Script (Production-Ready)

**Key differences from basic script:**
- Fetches full post body (`selftext`) via comments endpoint
- Uses URL encoding for search queries
- Includes multiple search queries per product
- Filters by author, time, and deduplicates
- Rate limiting 1.5s between requests

```python
import json, subprocess, time
from datetime import datetime
from urllib.parse import quote

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

def search_reddit(query, limit=50):
    """Search Reddit with URL encoding."""
    try:
        encoded = quote(query)
        url = f'https://www.reddit.com/search.json?q={encoded}&sort=new&t=all&limit={limit}'
        result = subprocess.run(['curl', '-s', '-L', '-A', UA, url], 
                              capture_output=True, text=True, timeout=20)
        data = json.loads(result.stdout)
        return [p['data'] for p in data.get('data', {}).get('children', [])]
    except Exception as e:
        print(f'Search error: {e}')
    return []

def get_post_and_comments(post_id):
    """Get BOTH full post body AND comments."""
    try:
        url = f'https://www.reddit.com/comments/{post_id}.json'
        result = subprocess.run(['curl', '-s', '-L', '-A', UA, url],
                              capture_output=True, text=True, timeout=20)
        data = json.loads(result.stdout)
        if isinstance(data, list) and len(data) >= 2:
            post_data = data[0].get('data', {}).get('children', [{}])[0].get('data', {})
            comments = data[1].get('data', {}).get('children', [])
            return post_data, comments
    except Exception as e:
        print(f'Get post error: {e}')
    return {}, []

def format_post(post_data, comments):
    """Format post with full body + filtered comments."""
    lines = []
    title = post_data.get('title', 'N/A')
    author = post_data.get('author', 'N/A')
    date = datetime.fromtimestamp(post_data.get('created_utc', 0)).strftime('%Y-%m-%d')
    url = f"https://www.reddit.com{post_data.get('permalink', '')}"
    selftext = post_data.get('selftext', '')
    
    lines.append(f"## {title}")
    lines.append(f"- **Author:** u/{author}")
    lines.append(f"- **Date:** {date}")
    lines.append(f"- **URL:** {url}")
    lines.append(f"- **Score:** {post_data.get('score', 0)} | **Comments:** {post_data.get('num_comments', 0)}")
    lines.append("")
    
    # Post body (CRITICAL - must fetch from post_data, not search results)
    if selftext and selftext not in ['[removed]', '[deleted]'] and len(selftext) > 10:
        lines.append("### Post Content")
        lines.append(selftext[:2000])
        lines.append("")
    
    # Comments (filter official accounts)
    user_comments = [c['data'] for c in comments 
                     if c.get('data', {}).get('author') not in 
                     ['OBSBOT-Official', 'Insta360_Support', 'AutoModerator']]
    if user_comments:
        lines.append(f"### User Comments ({len(user_comments)})")
        lines.append("")
        for c in user_comments[:10]:
            body = c.get('body', '')[:500].replace('\n', '\n> ')
            if body and body not in ['[removed]', '[deleted]']:
                lines.append(f"**u/{c.get('author', 'N/A')}** ({c.get('score', 0)} pts):")
                lines.append(f"> {body}")
                lines.append("")
    lines.append("---\n")
    return '\n'.join(lines)

def fetch_and_save(queries, product_name, filename, cutoff_date='2025-01-01'):
    """Main workflow: search → deduplicate → fetch → format → save."""
    cutoff = datetime.strptime(cutoff_date, '%Y-%m-%d').timestamp()
    all_posts = {}
    
    for q in queries:
        print(f'  Searching: {q}')
        posts = search_reddit(q)
        for p in posts:
            pid = p.get('id', '').replace('t3_', '')
            if pid and p.get('created_utc', 0) >= cutoff:
                if pid not in all_posts:
                    all_posts[pid] = p
        time.sleep(2)
    
    user_posts = {k: v for k, v in all_posts.items() 
                  if v.get('author') not in ['OBSBOT-Official', 'Insta360_Support']}
    print(f'  Total user posts: {len(user_posts)}')
    
    content = f"# {product_name} - Reddit User Discussions\n\n"
    content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    content += f"**Filter:** User posts only\n\n---\n\n"
    
    count = 0
    for pid, post_info in user_posts.items():
        print(f'    Fetching: {post_info.get("title", "")[:40]}...')
        post_data, comments = get_post_and_comments(pid)
        if post_data:
            content += format_post(post_data, comments)
            count += 1
        time.sleep(1.5)  # Rate limiting!
    
    with open(filename, 'w') as f:
        f.write(content)
    print(f'  Saved {count} posts to {filename}')
    return count

# Usage example:
fetch_and_save(
    ['"OBSBOT Tiny 2"', '"OBSBOT Tiny 2 Lite"', 'obsbot tiny2'],
    "OBSBOT Tiny 2", '/tmp/obsbot_tiny2_reddit.md', '2024-01-01'
)
```

## Pitfalls

1. **VPN disconnected mid-scrape** — Shadowrocket disconnects during long scrapes (50+ posts). Ask user to reconnect if this happens. Run between batches of ~20 posts.

2. **Unquoted search returns garbage** — Reddit search without quotes (`"..."`) returns completely irrelevant results. ALWAYS use exact phrase quotes: `'"OBSBOT Tiny 2"'`.

3. **Missing post body** — Search results only have `selftext_preview` (truncated). Must fetch full `selftext` via `/comments/POST_ID.json` endpoint. **USER CORRECTION:** Documents with only URLs and no post body content are considered incomplete/broken. Always include post body.

4. **bb-browser returns 0 posts** — Usually VPN issue or rate limiting. Use curl directly as fallback with URL encoding (`urllib.parse.quote()`).

5. **Title length > 36 chars** — Tencent Docs `create_smartcanvas_by_mdx` rejects titles over 36 characters. Shorten titles.

6. **Rate limiting** — Add 1.5-2s delay between Reddit API calls. After ~50 requests, may get 429s. Reconnect VPN and retry.

7. **Official posts mixed in** — Always filter by author not in `['OBSBOT-Official', 'Insta360_Support', 'AutoModerator']`.

8. **Time filter** — Use Unix timestamp comparison, not string dates. `datetime.strptime('2026-01-28', '%Y-%m-%d').timestamp()`

9. **Multiple queries needed** — Single search query misses many posts. Use 2-3 variations per product: `['"OBSBOT Tiny 2"', '"OBSBOT Tiny 2 Lite"', 'obsbot tiny2']`.

10. **Deduplication** — Multiple queries return overlapping results. Use post ID as key to deduplicate.

11. **Large file upload** — For very long markdown files (>30KB), truncate with `head -c 30000` before passing to `mdx` parameter.

12. **Script timeout** — Python scripts with 600s timeout fail for large batches (6 products). Split into per-product runs (~1-3 min each) instead of one mega-script.

13. **Reddit blocks entirely** — Reddit sometimes returns HTML (CAPTCHA/blocked page) instead of JSON. Detect by checking if response starts with `{`. If blocked, reconnect VPN and retry.

14. **Amazon scraping blocked** — Amazon returns CAPTCHA for direct curl/browser access from China. Use alternative sources: Best Buy reviews, tech review sites (TechRadar, Tom's Guide, Trusted Reviews), or Reddit discussions instead.

15. **Comprehensive scraping expected** — User expects maximum post coverage. Don't stop at first search; use multiple queries, multiple keywords, ensure `selftext` inclusion. Quality gate: every post must have body content if available.

## Reddit JSON API Endpoints

| Endpoint | Description |
|----------|-------------|
| `https://www.reddit.com/search.json?q=QUERY&sort=new&t=year&limit=50` | Search posts |
| `https://www.reddit.com/comments/POST_ID.json` | Get post + comments |
| `https://www.reddit.com/r/SUBREDDIT/comments/POST_ID.json` | Get post from specific subreddit |

## Tencent Docs Folder Structure (OBSBOT example)

```
obsbot/
├── Amazon/ (folder_id: DKQjkLCCkwLR)
│   ├── OBSBOT Tiny3 Amazon Reviews
│   ├── OBSBOT Tiny 2 Amazon Reviews
│   ├── Insta360 Link 2 Pro Amazon Reviews
│   ├── Insta360 Link 2 Amazon Reviews
│   ├── OBSBOT Tiny 3 Lite Amazon Reviews
│   └── Insta360 Link 2C Reviews
└── Reddit/ (folder_id: DnDseMiuEfDq)
    ├── OBSBOT Tiny 3 Reddit Discussions
    ├── Tiny 3 Lite Reddit Discussions
    ├── OBSBOT Tiny 2 Reddit Discussions
    ├── Tiny 3 Comparisons Reddit
    ├── Insta360 Link 2 Pro Reddit
    └── Insta360 Link 2C Pro Reddit
```

## Amazon Scraping via Browser

Amazon blocks direct access from China (CAPTCHA). When user asks to scrape Amazon reviews:

### Primary: Use amazon-review-scraper skill (Woot endpoint)
```bash
python3 ~/.hermes/skills/productivity/amazon-review-scraper/scripts/amazon_review_scraper.py {ASIN} --mode max
```

### Fallback: Browser direct extraction
When Woot endpoint returns empty, use browser tool:

```bash
# 1. Navigate to product page
browser_navigate url="https://www.amazon.com/dp/{ASIN}"

# 2. Scroll to reviews section
browser_click ref=e15  # "Reviews" link in page nav
browser_scroll direction=down

# 3. Extract reviews via JavaScript
browser_console expression="""
const pc = document.body.innerText;
const rs = pc.indexOf('来自美国的热门评论');
if (rs > -1) pc.substring(rs, rs + 8000);
else { const ci = pc.indexOf('Amazon Customer'); ci > -1 ? pc.substring(ci, ci + 8000) : 'No reviews'; }
"""

# 4. Repeat scrolling + extraction for more reviews
browser_scroll direction=down
# Re-run console expression with different offset
```

**Key notes:**
- Amazon auto-detects language, reviews section may show as "来自美国的热门评论" (Chinese)
- Each scroll loads ~8 more reviews
- "查看更多评论" button may need clicking
- Parse review text manually: stars, title, author, date, body
- **USER FEEDBACK:** User confirmed VPN is working; Amazon CAPTCHA is the issue, not VPN. Always try browser approach first before giving up.
