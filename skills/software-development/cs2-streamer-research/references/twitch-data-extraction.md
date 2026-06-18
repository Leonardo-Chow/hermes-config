# Twitch 数据提取参考

## TwitchTracker 数据提取

### 30天数据

```python
# 排名
rank_m = re.search(r'<span class="to-number">([0-9,]+)</span>\s*</div>\s*</div>\s*</div>', html[:10000])

# 30天数据（直播时长、平均观众、峰值、新增粉丝）
blocks = re.findall(
    r'<div class="g-x-s-value to-number">([0-9,]+)</div>\s*<div class="g-x-s-label[^"]*">([^<]+)</div>',
    html
)
# labels: "Hours streamed", "Average viewers", "Peak viewers", "Followers gained"
```

### 简介

```python
bio_m = re.search(r'word-wrap:break-word;font-size:12px;">(.*?)</div>', html, re.DOTALL)
# 需要清理 HTML entities: &#039; → ' &amp; → &
```

### 语言

```python
lang_m = re.search(r'<span[^>]*>(French|English|Spanish|German|Portuguese|Russian|Italian|Polish|Swedish|Norwegian|Danish|Finnish|Dutch|Turkish)</span>', html)
```

### 社交链接

```python
# YouTube, Instagram, Twitter/X, TikTok
links = re.findall(r'href="(https?://(?:www\.)?(?:youtube\.com|instagram\.com|twitter\.com|x\.com|tiktok\.com)/[^"]*)"', html)
```

### 粉丝量（不在HTML中）

TwitchTracker 的 follower count 通过 JavaScript 动态加载，curl 无法获取。必须使用 Twitch GQL API。

## TwitchMetrics 数据提取

### 主播名

```python
# HTML 结构: <h5 class="mr-2 mb-0">STREAMER_NAME</h5>
names = re.findall(r'<h5 class="mr-2 mb-0">([A-Za-z0-9_]+)</h5>', html)
```

### 观看时长

```python
# 页面中的 viewer hours 数字
viewer_hours = re.findall(r'>([0-9,]+)\s*<.*?viewer hours', html, re.DOTALL)
```

### 各语言 URL

| 语言 | URL |
|------|-----|
| English | `https://twitchmetrics.net/channels/viewership?game=Counter-Strike&lang=en` |
| German | `?lang=de` |
| French | `?lang=fr` |
| Swedish | `?lang=sv` |
| Spanish | `?lang=es` |
| Italian | `?lang=it` |
| Polish | `?lang=pl` |

## Twitch GQL API

### 获取粉丝量

```bash
# 必须写入文件再发送（不能 inline）
echo '{"query": "query { user(login: \"USERNAME\") { followers { totalCount } } }"}' > /tmp/q.json
curl -s -X POST 'https://gql.twitch.tv/gql' \
  -H 'Client-ID: kimne78kx3ncx6brgo4mv6wki5h1ko' \
  -H 'Content-Type: application/json' \
  -d @/tmp/q.json
```

### 限流策略

- 每次请求间隔 0.3-0.5 秒
- 约 50 次请求后会触发限流
- 限流后等待 10-15 秒再重试
- 最终成功率约 95%+（140 个主播中约 139 个可获取）

## 实际数据示例（2026-06-16）

| 主播 | 排名 | 30天平均观众 | 30天峰值 | 30天直播时长 | 粉丝量 |
|------|------|-------------|---------|-------------|--------|
| CroissantStrike | #221 | 3,209 | 30,092 | — | 234,663 |
| KRL_STREAM | #1,546 | 900 | 4,052 | 197h | 132,383 |
| shoxieJESUSS | #2,603 | 952 | 2,828 | 76h | 287,507 |
| ESLCS | #17 | 10,836 | — | — | 6,747,091 |
| ohnePixel | #8 | 43,750 | — | — | 2,907,411 |
| IzakOOO | #216 | 4,455 | — | — | 2,010,876 |
