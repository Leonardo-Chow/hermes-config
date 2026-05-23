---
name: daily-digest
description: |
  Generate and publish structured daily briefings/digests from multiple online sources.
  Covers parallel data collection from stock APIs, social media hotlists, tech news,
  international news, and entertainment sources — then formats and publishes to
  a knowledge base (IMA). Supports Chinese-language daily briefing formats
  like 摸鱼日报.
homepage: ""
metadata:
  security:
    allowed_domains:
      - qt.gtimg.cn
      - weibo.com
      - www.douyin.com
      - techcrunch.com
      - www.bbc.com
      - www.aceshowbiz.com
      - ima.qq.com
      - push2.eastmoney.com
      - newsapi.org\n      - top.baidu.com
      - api.rss2json.com
      - www.npr.org
      - www.theverge.com
      - feeds.arstechnica.com
      - www.wired.com
      - www.hollywoodreporter.com
      - variety.com
---

# Daily Digest (每日简报/摸鱼日报)

Generate a structured daily briefing from multiple online data sources and publish it to a knowledge base (IMA).

## Trigger Conditions

Load this skill when the user asks to:
- "生成日报" / "摸鱼日报"
- "今日简报" / "daily briefing"
- "搜集今天的热点" / "整理今日新闻"
- Any request involving multi-source data aggregation for a daily summary

## Data Sources & Collection Pattern

Use `delegate_task` or independent parallel terminal calls. The typical 8-section brief requires these sources:

### 1. A-Share Market (A股行情)
```
# Indexes (GBK decode needed)
curl -s 'https://qt.gtimg.cn/q=sh000001,sh000688,sz399001,sz399006' | iconv -f GBK -t UTF-8

# Sector rankings
curl -s 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=10&fs=m:90+t:2&fields=f12,f3'
```
Format: 4 indexes (latest price, change%), top 10 sectors with %.

### 微博热搜 ✅ 可靠
```bash
# 推荐接口（避免403）：
curl -s 'https://weibo.com/ajax/statuses/hot_band' -H 'User-Agent: Mozilla/5.0'
# 旧接口 /ajax/side/hotSearch 经常返回403 Forbidden
```
Extract: `data.realtime[].word` (title), `raw_hot` (heat score). Top 20 entries.

### 3. Baidu Hot Search (百度热搜) ✅ 可靠
```bash
curl -s 'https://top.baidu.com/api/board?tab=realtime' -H 'User-Agent: Mozilla/5.0'
# Extract: data.running[].query + hotScore
```

### 4. Douyin Hot List (抖音热榜)
```
curl -s 'https://www.douyin.com/aweme/v1/web/hot/search/list/' -H 'User-Agent: ...'
```
Extract: `data.word_list[].word` + `hot_value`. Top 20 entries.

### 4. Tech News (科技新闻)
```bash
# TechCrunch (REST API)
curl -s 'https://techcrunch.com/wp-json/wp/v2/posts?per_page=15'

# The Verge
curl -s 'https://www.theverge.com/rss/index.xml'

# Ars Technica
curl -s 'https://feeds.arstechnica.com/arstechnica/index'

# Wired
curl -s 'https://www.wired.com/feed/rss'

# Hacker News (Firebase API)
curl -s 'https://hacker-news.firebaseio.com/v0/topstories.json'

# Chinese tech (ifanr)
curl -s 'https://www.ifanr.com/wp-json/wp/v2/posts?per_page=10'
```
Extract 8-12 headlines from the most recent entries, ideally from 3+ different sources.

### 5. International News (国际新闻)
> ⚠️ **CRITICAL**: Most RSS feeds cannot be fetched directly from this environment. Use the rss2json proxy:
> ```
> https://api.rss2json.com/v1/api.json?rss_url={RSS_URL}
> ```

```bash
# BBC News (via rss2json) ✅ RELIABLE
curl -s 'https://api.rss2json.com/v1/api.json?rss_url=https://feeds.bbci.co.uk/news/rss.xml'

# NPR (via rss2json) ✅ RELIABLE
curl -s 'https://api.rss2json.com/v1/api.json?rss_url=https://feeds.npr.org/1001/rss.xml'

# Al Jazeera (direct) ✅ RELIABLE
curl -s 'https://www.aljazeera.com/xml/rss/all.xml' -H 'User-Agent: Mozilla/5.0'

# CNBC ⚠️ Sometimes 500
curl -s 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114'

# AP News ⚠️ Often times out
curl -s 'https://api.rss2json.com/v1/api.json?rss_url=https://apnews.com/rss/world'

# France 24 ✅ Works with direct request
```

Select 8-12 important stories from 4-7 different sources covering: geopolitics, conflicts, economy, environment, culture, society.

**Fallback strategy**: If a source fails, use delegate_task to try alternative access methods, or supplement from another source.

### 6. Entertainment (娱乐八卦)
```bash
# Hollywood Reporter
curl -s 'https://www.hollywoodreporter.com/wp-json/wp/v2/posts?per_page=10'

# Variety
curl -s 'https://variety.com/feed/'

# AceShowbiz (sometimes 404)
curl -s 'https://www.aceshowbiz.com/rss/latest_news.xml'
```
Select 2-4 gossip/celebrity stories.

## Content Structure (10-Section Format — Chinese 摸鱼日报)

Follow this exact structure — established through iterative user feedback:

```\n# YYYY年M月D日 · 摸鱼日报\n\n---\n\n## 1️⃣ 今日信息差 💻\n5 information gaps with type tags. Bilingual titles (中文 + *English*)\n\n## 2️⃣ A股行情速览 📊\n4 indexes table + Top 8 sectors\n\n## 3️⃣ 🔥 微博热搜精选\n6-8 selected items with rank + title + heat score\n\n## 4️⃣ 🔍 百度热搜精选\n6-8 selected items (新增来源)\n\n## 5️⃣ 📱 抖音热榜精选\n6-8 selected items with rank + title + heat value\n\n## 6️⃣ 💻 科技热点速递\n2 重磅(detailed, bilingual) + quick-hit table (each with link)\n\n## 7️⃣ 🤖 全球AI发展\n1 big story with competitive landscape table + other AI news\n\n## 8️⃣ 🕵️ 娱乐圈八卦侦探\n3+ entertainment stories (MUST NOT be omitted!)\n\n## 9️⃣ 🌍 国际新闻 · 中英双语\n12-15 items from 7+ sources. English title ON TOP, Chinese below.\nGrouped into 4 categories: 冲突/政治/经济/环境 (2+ each)\n\n## 🔟 ⭐ 每日精选\nA NEW story not covered above. Deep 3-dimension analysis + real image.\n```

End with:
```
> 📊 **数据概览**: source count summary
> 📅 **生成时间**: YYYY-MM-DD HH:MM
```

## Publishing to IMA

After generating the Markdown content:

1. **Create note**: `import_doc` with title="YYYY年M月D日 · 摸鱼日报", content_format=1
2. **Refresh cover image**: `get_media_info` for the cover image media_id to get a fresh signed URL
3. **Add to KB**: `add_knowledge` with media_type=11, note_info.content_id=<note_id>

See `ima-skills` skill → `references/daily-digest-pattern.md` for exact API call templates.

## Parallel Collection Strategy

Use `delegate_task` with `max_concurrent_children=3` to parallelize independent data sources:

```
Batch 1: A股 data, 微博热搜, 抖音热榜
Batch 2: Tech news, 国际新闻, 娱乐新闻
```

Each sub-agent task should:
- Return raw collected text (not formatted)
- Have its own timeout (20-30s per source)
- Handle failures gracefully (return empty string if source unavailable)

## Traps & Pitfalls

- **Source APIs can be flaky**: Weibo `/ajax/side/hotSearch` returns 403 (use `/ajax/statuses/hot_band` instead). Stock API needs GBK decode. Douyin API requires `Referer: https://www.douyin.com/` header.
- **RSS direct fetch fails silently**: Most RSS feeds return empty when fetched directly. **Always use rss2json proxy** (`https://api.rss2json.com/v1/api.json?rss_url=...`) for BBC, NPR, etc.
- **Cover image URL expires**: IMA signed URLs are time-limited. Always call `get_media_info` before publishing to refresh.
- **import_doc creates NEW note**: Does NOT update an existing daily note. Each day gets a new note.
- **Content size**: Very long digests may hit IMA content size limits. Strategy: generate in parts (Part 1: finance+social, Part 2: tech+AI, Part 3: intl+entertainment), then merge and upload as one. Remove duplicate headers/images when merging.
- **delegate_task concurrency**: Default max is 3 concurrent children. Batch accordingly (Batch 1: stocks+weibo+douyin, Batch 2: tech+intl+entertainment).
- **Format fidelity**: The 摸鱼日报 has a specific format. Don't invent new sections unless explicitly asked. Include ALL sections even if some have sparse data — especially 娱乐八卦 which is frequently forgotten.
- **NewsAPI.org**: Demo key is rate-limited and unreliable. Do not depend on it. Prefer direct RSS + rss2json.
- **International news quality**: Each sub-category needs 2+ items. User is very strict about this — don't cut corners even if data collection is slow.
- **每日精选 image**: Must be a REAL image URL, not a placeholder. Extract og:image from NPR articles (most reliable). See `moyu-daily-generator` skill → `references/finding-images.md`.
- **Bilingual international news**: English title ON TOP, Chinese below. Not the reverse. Confirmed through user correction.
- **Zhihu hot search**: Extremely difficult to scrape (403/captcha). Document as unavailable rather than wasting time on it.
