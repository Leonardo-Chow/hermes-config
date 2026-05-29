---
name: scrapling
description: Web scraping with Scrapling - HTTP fetching, stealth browser automation, Cloudflare bypass, spider crawling, MCP server, and adaptive scraping via CLI and Python.
version: 2.0.0
author: D4Vinci (Karim Shoair)
license: BSD-3-Clause
metadata:
  hermes:
    tags: [Web Scraping, Browser, Cloudflare, Stealth, Crawling, Spider, MCP, Adaptive]
    related_skills: [duckduckgo-search, domain-intel, camoufox]
    homepage: https://github.com/D4Vinci/Scrapling
    docs: https://scrapling.readthedocs.io
prerequisites:
  commands: [python3]
  python_version: ">=3.10"
---

# Scrapling v0.4.8+

[Scrapling](https://github.com/D4Vinci/Scrapling) is an adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl. 50k+ GitHub stars.

**Key capabilities:**
- 🔄 **Adaptive Scraping** — Parser learns from website changes, auto-relocates elements
- 🛡️ **Anti-bot Bypass** — Cloudflare Turnstile/Interstitial solving out of the box
- 🕷️ **Spider Framework** — Scrapy-like API with concurrent requests, pause/resume
- 🤖 **MCP Server** — Built-in MCP server for AI-assisted scraping
- ⚡ **High Performance** — Faster than BS4, PyQuery, Selectolax

**This skill is for educational and research purposes only.** Users must comply with local/international data scraping laws and respect website ToS.

## When to Use

- Scraping static HTML pages (faster than browser tools)
- Scraping JS-rendered pages that need a real browser
- Bypassing Cloudflare Turnstile or bot detection
- Crawling multiple pages with a spider
- When the built-in `web_extract` tool does not return the data you need
- When you need adaptive element tracking across page updates

## Installation

**⚠️ Requires Python 3.10+** — macOS system Python (3.9) will NOT work.

### Recommended: Python 3.12 Virtual Environment

```bash
# Create venv with Python 3.12
/opt/homebrew/bin/python3.12 -m venv ~/.hermes/skills/scrapling/venv

# Activate and install (all features)
source ~/.hermes/skills/scrapling/venv/bin/activate
pip install "scrapling[all]>=0.4.8"
scrapling install --force  # Installs Playwright + Camoufox browsers
```

### Alternative installs

```bash
# Minimal (parser only, no fetchers)
pip install scrapling

# With fetchers only
pip install "scrapling[fetchers]"
scrapling install

# With MCP server
pip install "scrapling[ai]"

# With CLI shell
pip install "scrapling[shell]"

# Docker (all features + browsers)
docker pull pyd4vinci/scrapling
```

### Usage (always activate venv first)

```bash
source ~/.hermes/skills/scrapling/venv/bin/activate
python3 your_script.py
```

## Quick Reference

| Approach | Class | Use When |
|----------|-------|----------|
| HTTP | `Fetcher` / `FetcherSession` | Static pages, APIs, fast bulk requests |
| Dynamic | `DynamicFetcher` / `DynamicSession` | JS-rendered content, SPAs |
| Stealth | `StealthyFetcher` / `StealthySession` | Cloudflare, anti-bot protected sites |
| Spider | `Spider` / `CrawlSpider` / `SitemapSpider` | Multi-page crawling with link following |
| Parser | `Selector` | Parse HTML strings directly (no fetching) |

## CLI Usage

### Extract Static Page

```bash
scrapling extract get 'https://example.com' output.md
scrapling extract get 'https://example.com' output.md --css-selector '.content' --impersonate 'chrome'
```

### Extract JS-Rendered Page

```bash
scrapling extract fetch 'https://example.com' output.md --css-selector '.dynamic-content' --network-idle
```

### Extract Cloudflare-Protected Page

```bash
scrapling extract stealthy-fetch 'https://protected-site.com' output.html --solve-cloudflare --block-webrtc --hide-canvas
```

### POST Request

```bash
scrapling extract post 'https://example.com/api' output.json --json '{"query": "search term"}'
```

### CLI Key Options

| Option | Description |
|--------|-------------|
| `-s, --css-selector` | CSS selector to extract specific content |
| `--impersonate` | Browser fingerprint (Chrome, Firefox, Safari) |
| `--timeout` | Timeout: seconds (HTTP) / ms (browser) |
| `--proxy` | Proxy URL `http://user:***@host:port` |
| `--ai-targeted` | Extract main content only, sanitize for AI |
| `--network-idle` | Wait for network idle (browser) |
| `--disable-resources` | Block fonts/images/media (~25% faster) |
| `--solve-cloudflare` | Auto-solve Cloudflare challenges |
| `--block-webrtc` | Prevent WebRTC IP leak |
| `--hide-canvas` | Canvas fingerprint noise |

### Output Formats

- `.md` — Markdown (best for readability)
- `.html` — Raw HTML
- `.txt` — Plain text only
- `.json` / `.jsonl` — JSON

### Escalation Pattern

When unsure, start with `get`. If it fails or returns empty content, escalate to `fetch`, then `stealthy-fetch`.

## Python: HTTP Scraping

### Single Request

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```

### Session (Persistent Cookies)

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com/', stealthy_headers=True)
    links = page.css('a::attr(href)').getall()
```

### POST / PUT / DELETE

```python
page = Fetcher.post('https://api.example.com/data', json={"key": "value"})
page = Fetcher.put('https://api.example.com/item/1', data={"name": "updated"})
page = Fetcher.delete('https://api.example.com/item/1')
```

### With Proxy

```python
page = Fetcher.get('https://example.com', proxy='http://user:pass@proxy:8080')
```

## Python: Dynamic Pages (JS-Rendered)

```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

# One-off request
page = DynamicFetcher.fetch('https://example.com', headless=True, network_idle=True)
data = page.css('.js-loaded-content::text').getall()

# Session (keep browser open)
with DynamicSession(headless=True, disable_resources=True, network_idle=True) as session:
    page = session.fetch('https://example.com')
```

### Wait for Specific Element

```python
page = DynamicFetcher.fetch(
    'https://example.com',
    wait_selector=('.results', 'visible'),
    network_idle=True,
)
```

### Custom Page Automation

```python
from playwright.sync_api import Page
from scrapling.fetchers import DynamicFetcher

def scroll_and_click(page: Page):
    page.mouse.wheel(0, 3000)
    page.wait_for_timeout(1000)
    page.click('button.load-more')
    page.wait_for_selector('.extra-results')

page = DynamicFetcher.fetch('https://example.com', page_action=scroll_and_click)
```

## Python: Stealth Mode (Anti-Bot Bypass)

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

# One-off request
page = StealthyFetcher.fetch(
    'https://protected-site.com',
    headless=True,
    solve_cloudflare=True,
    block_webrtc=True,
    hide_canvas=True,
)

# Session
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page1 = session.fetch('https://protected-site.com/page1')
    page2 = session.fetch('https://protected-site.com/page2')
```

## Python: Spider Framework

### Basic Spider

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 10
    robots_txt_obey = True

    async def parse(self, response: Response):
        for quote in response.css('.quote'):
            yield {
                "text": quote.css('.text::text').get(),
                "author": quote.css('.author::text').get(),
            }

        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

result = QuotesSpider().start()
result.items.to_json("quotes.json")
```

### Multi-Session Spider

```python
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class SmartSpider(Spider):
    name = "smart"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast")
```

### CrawlSpider (Rules-based)

```python
from scrapling.spiders import CrawlSpider, CrawlRule, LinkExtractor

class BlogCrawler(CrawlSpider):
    name = "blog"
    start_urls = ["https://example.com"]

    def rules(self):
        return [
            CrawlRule(LinkExtractor(allow=r"/posts/"), callback=self.parse_post),
            CrawlRule(LinkExtractor(allow=r"/page/\d+/")),  # follow pagination
        ]

    async def parse_post(self, response):
        yield {"title": response.css("h1::text").get()}
```

### Pause/Resume Crawling

```python
spider = QuotesSpider(crawldir="./crawl_checkpoint")
spider.start()  # Ctrl+C to pause, re-run to resume
```

### Development Mode

```python
class MySpider(Spider):
    development_mode = True  # Cache responses, replay on re-run
    # ...
```

## Element Selection

All fetchers return a `Selector` object:

### CSS Selectors

```python
page.css('h1::text').get()              # First h1 text
page.css('a::attr(href)').getall()      # All link hrefs
page.css('.quote .text::text').getall() # Nested selection
```

### XPath

```python
page.xpath('//div[@class="content"]/text()').getall()
page.xpath('//a/@href').getall()
```

### Find Methods (BeautifulSoup-style)

```python
page.find_all('div', class_='quote')
page.find_by_text('Read more', tag='a')
page.find_by_regex(r'\$\d+\.\d{2}')
```

### Similar Elements

```python
first_product = page.css('.product')[0]
all_similar = first_product.find_similar()
```

### Navigation

```python
el = page.css('.target')[0]
el.parent                # Parent element
el.children              # Child elements
el.next_sibling          # Next sibling
el.prev_sibling          # Previous sibling
el.below_elements()      # Elements below
```

### Parse HTML Directly

```python
from scrapling.parser import Selector
page = Selector("<html>...</html>")
```

## Async Support

```python
import asyncio
from scrapling.fetchers import FetcherSession, AsyncStealthySession, AsyncDynamicSession

async with FetcherSession(http3=True) as session:
    page1 = session.get('https://example.com/')
    page2 = session.get('https://example.com/', impersonate='firefox135')

async with AsyncStealthySession(max_pages=2) as session:
    tasks = [session.fetch(url) for url in urls]
    results = await asyncio.gather(*tasks)
    print(session.get_pool_stats())

# Capture XHR/fetch API calls
async with AsyncDynamicSession(capture_xhr=r"https://api\.example\.com/.*") as session:
    page = await session.fetch('https://example.com')
    for xhr in page.captured_xhr:
        print(xhr.url, xhr.status, xhr.body)
```

## MCP Server

Scrapling has a built-in MCP server with 10 tools:

| Tool | Description |
|------|-------------|
| `get` | HTTP GET (single URL) |
| `bulk_get` | HTTP GET (multiple URLs, parallel) |
| `fetch` | Browser fetch (single URL) |
| `bulk_fetch` | Browser fetch (multiple URLs) |
| `stealthy_fetch` | Stealth browser fetch (single URL) |
| `bulk_stealthy_fetch` | Stealth browser fetch (multiple URLs) |
| `open_session` | Create persistent browser session |
| `close_session` | Close persistent session |
| `list_sessions` | List active sessions |
| `screenshot` | Capture page screenshot |

### MCP Installation

```bash
pip install "scrapling[ai]"
scrapling install --force
```

### MCP Usage with Claude/Cursor

Add to your MCP config:

```json
{
  "mcpServers": {
    "scrapling": {
      "command": "scrapling",
      "args": ["mcp"]
    }
  }
}
```

### MCP Key Features

- CSS selector content narrowing (reduces tokens)
- Persistent browser sessions (avoid restart overhead)
- Page screenshots as MCP ImageContent blocks
- `--ai-targeted` flag for AI-optimized extraction

## Proxy Rotation

```python
from scrapling.spiders import Spider
from scrapling.fetchers import ProxyRotator

# Built-in proxy rotator
rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
])

class MySpider(Spider):
    proxy_rotator = rotator
    # ...
```

## Pitfalls

- **Python version**: macOS system Python is 3.9 — **must** use Python 3.10+ venv
- **Browser install required**: run `scrapling install` after pip install — without it, `DynamicFetcher` and `StealthyFetcher` will fail
- **Timeouts**: DynamicFetcher/StealthyFetcher timeout is in **milliseconds** (default 30000), Fetcher timeout is in **seconds**
- **Cloudflare bypass**: `solve_cloudflare=True` adds 5-15 seconds — **only enable when site actually has Cloudflare**. If site has NO Cloudflare challenge, it will error. Use `DynamicFetcher` instead for non-Cloudflare JS sites.
- **Resource usage**: StealthyFetcher runs a real browser — limit concurrent usage
- **disable_resources**: Set `disable_resources=True` to block fonts/images/media/stylesheets for ~25% faster loading
- **GFW blocked sites**: For BBC, CNN, Google etc. from China — VPN **must** be connected first. Scrapling respects system proxy settings when VPN is active.
- **Shadowrocket proxy for Scrapling/Playwright**: Shadowrocket macOS exposes HTTP/SOCKS5 proxy at `127.0.0.1:1082`. Pass `proxy='http://127.0.0.1:1082'` to Fetcher/DynamicFetcher/StealthyFetcher. Verified working for Instagram, Google, BBC. **Does NOT work for TikTok** (see below).
- **TikTok X-Bogus anti-bot (2026-05-29 verified)**: TikTok's video list API requires an `X-Bogus` token generated client-side by TikTok's own JS. Even with proxy + cookies + Playwright, the video grid returns empty. The SSR `itemList` is always empty. Direct API calls return 0 bytes. **Do not attempt TikTok video scraping with Scrapling** — all approaches (DynamicFetcher, StealthyFetcher, Playwright with cookies) fail.
- **Proxy connection failures**: ~5-10% of requests may fail with `ERR_PROXY_CONNECTION_FAILED`. Wrap in try/except, log failures, continue.
- **YouTube likes/comments**: Dynamically loaded via JS, ~50% success rate. Use `aria-label` attributes as fallback.
- **CLI `extract` command**: As of v0.2.99, the CLI only has `install` command. Use Python API instead for older versions. v0.4.8+ has full CLI.
- **Legal**: Always check robots.txt and website ToS. Use `robots_txt_obey = True` on spiders.

## Performance Benchmarks

### Text Extraction Speed (5000 nested elements)

| Library | Time (ms) | vs Scrapling |
|---------|:---------:|:------------:|
| **Scrapling** | **2.02** | **1.0x** |
| Parsel/Scrapy | 2.04 | 1.01x |
| Raw Lxml | 2.54 | 1.26x |
| PyQuery | 24.17 | ~12x |
| Selectolax | 82.63 | ~41x |
| BS4 with Lxml | 1584.31 | ~784x |

## Verified Patterns

### YouTube Video Details (GFW blocked, JS rendered)

```python
from scrapling.fetchers import DynamicFetcher
import re

page = DynamicFetcher.fetch(url, headless=True, network_idle=True, disable_resources=True)

# Channel
channel_links = page.css('a.yt-simple-endpoint::attr(href)').getall()
channel = next(('@' + l.split('/@')[1] for l in channel_links if '/@' in l), 'N/A')

# Views (from full page text)
all_text = ' '.join(page.css('body *::text').getall())
views = (m := re.search(r'([\d,]+)\s*次观看', all_text)) and m.group(1) or 'N/A'

# Description + Hashtags
desc = page.css('meta[name="description"]::attr(content)').get() or 'N/A'
tags = ', '.join(page.css('a[href*="hashtag/"]::text').getall()[:5])
```

### BBC News (GFW blocked, JS rendered)

```python
# Requires VPN connected first!
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://www.bbc.com/news',
    headless=True,
    network_idle=True,
    disable_resources=True,
)
titles = page.css('h2::text').getall()
```

### Reddit (Anti-bot, Camoufox required)

See `references/reddit-scraping.md` — Reddit blocks curl/API/regular browsers. Camoufox (StealthyFetcher) is the only working approach.

### Instagram Profile Posts (GFW, anti-bot)

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://www.instagram.com/brand_handle/',
    headless=True, network_idle=True, disable_resources=True,
    block_webrtc=True, hide_canvas=True,
)
# Post URLs
links = page.css('a[href*="/p/"]::attr(href)').getall() + page.css('a[href*="/reel/"]::attr(href)').getall()
# Post content
texts = page.css('[data-e2e*="desc"]::text').getall()
# Note: exact dates NOT available without login — posts are ordered most-recent-first
```

### TikTok ⚠️ Very Difficult — Anti-Bot Blocks Video Grid

TikTok uses X-Bogus client-side anti-bot tokens. The video grid is loaded via JS API calls that require this token — it cannot be extracted from CLI/automation.

**What works:** Page loads (HTTP 200), profile info visible, relative time markers (e.g., "12h", "2d") in page text, oembed API for individual video metadata.
**What does NOT work:** Video listing, video descriptions, exact timestamps, the `/api/post/item_list/` endpoint (returns empty without X-Bogus).

**For TikTok monitoring:** Use NoxInfluencer Brand Monitor (requires brand_id from web UI), or manual browser checking.

## Support Files

- `references/youtube-scraping.md` — YouTube video scraping patterns
- `references/youtube-comment-scraping.md` — YouTube comment scraping via API (commentThreads endpoint)
- `references/reddit-scraping.md` — Reddit anti-detection scraping
- `scripts/bbc_scraper.py` — BBC News scraper
- `scripts/youtube_scraper.py` — YouTube video scraper

## References

- [Full Documentation](https://scrapling.readthedocs.io)
- [GitHub Repository](https://github.com/D4Vinci/Scrapling)
- [Agent Skill](https://github.com/D4Vinci/Scrapling/tree/main/agent-skill)
- [Discord Community](https://discord.gg/EMgGbDceNQ)

## Guardrails

- Only scrape content you're authorized to access
- Respect robots.txt and ToS
- Add delays (`download_delay`) for large crawls
- Don't bypass paywalls or authentication without permission
- Never scrape personal/sensitive data
