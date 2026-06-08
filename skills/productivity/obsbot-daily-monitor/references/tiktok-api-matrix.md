# TikTok 数据源矩阵

## 可用 API 对比

| 服务 | 端点 | 免费额度 | 认证方式 | 数据丰富度 |
|:-----|:-----|:---------|:---------|:-----------|
| Omar API | tiktok-scraper.omkar.cloud | 100次/月 | `API-Key` header | ⭐⭐⭐⭐⭐ (30+字段，含HD下载链接) |
| ScrapeCreators | api.scrapecreators.com | 100次(首充) | `x-api-key` header | ⭐⭐⭐⭐⭐ (全平台覆盖) |
| ScraperAPI | api.scraperapi.com | 5000次/月 | `api_key` query param | ⭐⭐⭐ (通用抓取，需自行解析) |
| oembed API | tiktok.com/oembed | 无限 | 无需认证(需代理) | ⭐⭐ (仅标题/作者/封面) |

## 端点速查

### Omar API (优先用于详情查询)
```
GET /tiktok/users/profile?handle={username}
GET /tiktok/videos/details?video_url={url}
GET /tiktok/videos/search?search_query={keyword}
GET /tiktok/videos/trending
```
- 参数名注意：`handle` 不是 `username`，`search_query` 不是 `keyword`
- 返回完整 JSON，含视频下载链接(HD/无水印)、统计数据、音频信息

### ScrapeCreators (优先用于搜索和批量)
```
GET /v1/tiktok/profile?handle={username}
GET /v1/tiktok/search/keyword?keyword={keyword}&count={n}
GET /v1/tiktok/profile/videos?handle={username}&count={n}
GET /v1/tiktok/video?video_url={url}
```
- 支持 30+ 平台(TikTok/Instagram/YouTube/Twitter/Reddit/GitHub...)
- credits_remaining 字段显示剩余额度

### oembed API (免费兜底)
```bash
curl -s -x socks5h://127.0.0.1:1082 "https://www.tiktok.com/oembed?url={video_url}"
```
- 返回：title, author_name, thumbnail_url
- 必须走代理(GFW)，直连会 connection reset

### 视频ID时间解码 (免费)
```python
vid_id = video_url.split('/video/')[-1]
timestamp = int(vid_id) >> 32  # Unix timestamp (秒)
```

## 额度分配策略

### Omar API (100次/月)
| 用途 | 预算 | 说明 |
|:-----|:-----|:-----|
| 竞品监测 | 40次 | 周一/三/五，每次3-5个关键视频 |
| KOL验证 | 30次 | 高价值KOL资料 |
| 应急备用 | 30次 | 临时需求 |

### ScrapeCreators (按充值)
- 优先用于：搜索、批量抓取、非TikTok平台
- 避免用于：单个视频详情(用Omar更划算)

## 额度管理脚本
```bash
# 检查 Omar 额度
python3 ~/.hermes/scripts/omkar_usage.py

# 记录使用
python3 ~/.hermes/scripts/omkar_usage.py add 3 "竞品监测"
```

## 优先级规则
1. 免费方案优先：oembed + 视频ID解码
2. 批量搜索：ScraperAPI 或 Scrapling
3. 详情查询：Omar API (消耗额度)
4. 多平台需求：ScrapeCreators (消耗额度)
