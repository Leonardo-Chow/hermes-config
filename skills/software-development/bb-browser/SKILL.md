---
name: bb-browser
description: "bb-browser (BadBoy Browser) — CLI + MCP server that lets AI agents control your real Chrome with full login state. 103 commands across 36 platforms (Twitter, Reddit, Zhihu, B站, GitHub, YouTube, etc.). No API keys, no scraping."
version: 1.0.0
author: Hermes Agent
tags: [bb-browser, browser, automation, chrome, cdp, web]
---

# bb-browser Skill

[bb-browser](https://github.com/epiral/bb-browser) connects to your real Chrome browser so AI agents can access 36+ platforms **using your login state**. No API keys, no scraping, no headless browser detection.

## Status

- **Version:** v0.11.5 (npm global)
- **Install:** `npm install -g bb-browser`
- **Registry:** npmmirror (China mirror)

## Quick Start

```bash
# Update community adapters
bb-browser site update

# See recommended adapters
bb-browser site recommend

# Use a site adapter
bb-browser site zhihu/hot
bb-browser site twitter/search "AI agent"
bb-browser site github search "llm"
bb-browser site arxiv/search "transformer"
```

## Architecture

```
AI Agent ──CLI/MCP──▶ bb-browser CLI ──HTTP──▶ Daemon (127.0.0.1:19824) ──CDP──▶ Your Chrome
```

The daemon needs to be running for `site` commands to work.

## 36 Platforms, 103 Commands

| Category | Platforms |
|----------|-----------|
| 🔍 **Search** | Google, Baidu, Bing, DuckDuckGo, Sogou WeChat |
| 🐦 **Social** | Twitter/X, Reddit, Weibo, Xiaohongshu, Jike, LinkedIn, Hupu |
| 📰 **News** | BBC, Reuters, 36kr, Toutiao, Eastmoney |
| 💻 **Dev** | GitHub, StackOverflow, HackerNews, CSDN, V2EX, Dev.to, npm, PyPI, arXiv |
| 🎬 **Video** | YouTube, Bilibili |
| 🎮 **Entertainment** | Douban, IMDb, Genius, Qidian |
| 📈 **Finance** | Xueqiu, Eastmoney, Yahoo Finance |
| 💼 **Jobs** | BOSS直聘, LinkedIn |
| 📖 **Knowledge** | Wikipedia, Zhihu, Open Library |
| 🛍️ **Shopping** | SMZDM |

## Common Usage

```bash
# Search Twitter
bb-browser site twitter/search "keyword" --json

# Zhihu trending
bb-browser site zhihu/hot

# GitHub search
bb-browser site github search "topic"

# YouTube transcript
bb-browser site youtube/transcript VIDEO_ID

# Stock quotes
bb-browser site xueqiu/hot-stock 5 --jq '.items[] | {name, changePercent}'

# ArXiv papers
bb-browser site arxiv/search "transformer"
```

## Browser Automation Commands

```bash
bb-browser open https://example.com    # Open a URL
bb-browser snapshot -i                 # Get accessibility tree
bb-browser click @3                    # Click element
bb-browser fill @5 "text"              # Fill input
bb-browser eval "document.title"       # Run JS
bb-browser fetch URL --json            # Authenticated fetch
bb-browser screenshot                  # Screenshot
```

## Daemon

```bash
bb-browser daemon                      # Start daemon (needs Chrome running)
bb-browser daemon --host 127.0.0.1     # IPv4 only (fix macOS IPv6)
```

## MCP Setup (for Claude Code / Cursor)

```json
{
  "mcpServers": {
    "bb-browser": {
      "command": "npx",
      "args": ["-y", "bb-browser", "--mcp"]
    }
  }
}
```

## Reddit

See `references/reddit-scraping.md` for complete workflow with Python scripts, filtering patterns, and Tencent Docs upload.

## Amazon Reviews

See `references/amazon-review-scraping.md` for browser-based review extraction (curl blocked by CAPTCHA from China).

```bash
# Navigate to product page
browser_navigate url="https://www.amazon.com/dp/ASIN"

# Extract reviews via JavaScript console
browser_console expression="document.body.innerText.substring(document.body.innerText.indexOf('Top reviews'), document.body.innerText.indexOf('Top reviews') + 8000)"
```

**⚠️ Critical lessons (see reference for details):**
- Always use exact phrase quotes: `"OBSBOT Tiny 2"` not `OBSBOT Tiny 2`
- Search results DON'T include full post body — must fetch via `/comments/POST_ID.json`
- VPN (Shadowrocket) disconnects during long scrapes — add periodic reconnect
- Use 2-3 search queries per product for comprehensive coverage

```bash
# Search posts (returns up to 50 posts per query)
bb-browser site reddit/search "\"keyword\"" --json

# Fetch post body + comments (reddit/post does NOT exist!)
curl -s -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://www.reddit.com/comments/POST_ID.json"
# Returns: [{post_data}, {comments_data}]
# Post body: [0].data.children[0].data.selftext
# Comments: [1].data.children[].data
```

**Filtering patterns:**
```python
# Remove official posts
user_posts = [p for p in posts if p.get('author') != 'OBSBOT-Official']

# Time filter (Unix timestamp)
cutoff = datetime(2026, 1, 28).timestamp()
filtered = [p for p in posts if p.get('created_utc', 0) >= cutoff]

# Product filter (e.g., separate Tiny 3 from Tiny 3 Lite)
tiny3_only = [p for p in posts if 'lite' not in p.get('title', '').lower()]
```

## Pitfalls

- The **daemon must be running** for `site` commands to work
- Chrome must be open with remote debugging enabled
- First run `bb-browser site update` to pull community adapters
- Twitter and other blocked sites need a proxy in China
- Installed via npmmirror npm registry
- **Reddit `reddit/post` does NOT exist** — use `reddit/search` for search, and direct `.json` URL for post body + comments
- **Reddit needs VPN** from China — connect Shadowrocket before accessing Reddit APIs
- **VPN disconnects mid-scrape** — add periodic health check during long scrapes (50+ posts)
- **Reddit search requires exact quotes** — unquoted queries return irrelevant results
- **Search results lack full post body** — must fetch via `/comments/POST_ID.json` to get `selftext`
- **Reddit rate limiting** — add 1.5-2s delay between requests; use 2-3 queries per product for coverage
- **Reddit blocks entirely sometimes** — returns HTML instead of JSON; reconnect VPN and retry
- **Amazon scraping blocked** — CAPTCHA from China; curl returns captcha page. **Solution**: use browser to navigate, then extract reviews via `browser_console` with JS:
  ```javascript
  // After navigating to product page and clicking "Reviews"
  const pageContent = document.body.innerText;
  const reviewStart = pageContent.indexOf('来自美国的热门评论'); // or 'Top reviews from the United States'
  pageContent.substring(reviewStart, reviewStart + 8000);
  ```
- **Script timeout** — split large scraping jobs into per-product runs, not one mega-script
- **bb-browser search returns 0** — usually means VPN dropped. Reconnect VPN (`scutil --nc start "Shadowrocket"`) before retrying
- **Script timeout** — split large scraping jobs into per-product runs (50 posts max per script), not one mega-script covering all products
