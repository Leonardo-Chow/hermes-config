# Daily Digest · Data Sources & API Diagnostics

> Verified working/not-working state as of 2026-05-08 session.

## ✅ RELIABLE (work consistently)

| Source | Endpoint | Method | Notes |
|:-------|:---------|:-------|:------|
| 腾讯股票 | `qt.gtimg.cn/q=sh000001,...` | GET | GBK decode needed |
| 东方财富板块 | `push2.eastmoney.com/api/qt/clist/get?...` | GET | 行业+概念板块 |
| 微博热搜 | `weibo.com/ajax/statuses/hot_band` | GET + UA | `/ajax/side/hotSearch` returns 403 |
| 抖音热榜 | `douyin.com/aweme/v1/web/hot/search/list/` | GET + Referer | Must set `Referer: douyin.com` |
| BBC (via rss2json) | `api.rss2json.com/v1/api.json?rss_url=feeds.bbci.co.uk/...` | GET | ✅ Always works |
| NPR (via rss2json) | `api.rss2json.com/v1/api.json?rss_url=feeds.npr.org/1001/...` | GET | ✅ Always works |
| Al Jazeera (direct) | `www.aljazeera.com/xml/rss/all.xml` | GET + UA | ✅ Direct RSS works |
| TechCrunch | `techcrunch.com/wp-json/wp/v2/posts?per_page=15` | GET | REST API, reliable |
| The Verge | `www.theverge.com/rss/index.xml` | GET | Atom format |
| Ars Technica | `feeds.arstechnica.com/arstechnica/index` | GET | RSS |
| Wired | `www.wired.com/feed/rss` | GET | RSS |
| HN | `hacker-news.firebaseio.com/v0/topstories.json` | GET | Firebase API |
| Hollywood Reporter | `www.hollywoodreporter.com/wp-json/wp/v2/posts?per_page=10` | GET | REST API |
| Variety | `variety.com/feed/` | GET | RSS |
| 爱范儿 ifanr | `www.ifanr.com/wp-json/wp/v2/posts?per_page=10` | GET | Chinese tech |

## ⚠️ UNRELIABLE (use fallback)

| Source | Issue |
|:-------|:------|
| Reuters | All endpoints time out (RSS, direct, rss2json) |
| AP News | rss2json times out; direct RSS fails |
| CNBC | RSS returns HTTP 500 |
| NewsAPI.org | Demo key rate-limited to ~1 request/day |
| 36氪 | SSR/CSR rendered page, can't scrape; API returns old data |
| AceShowbiz RSS | Sometimes 404 |

## Strategy

1. Try the reliable sources first (BBC, NPR, Al Jazeera for international; TechCrunch + Verge + Ars for tech)
2. Use `delegate_task` with `max_concurrent_children=3` to parallelize
3. If a source fails, try via subagent (different UA/cookie strategy) or skip and get extra from a reliable source
4. For international diversity: use BBC (UK) + NPR (US) + Al Jazeera (Qatar) + France 24 (France) as the core 4
