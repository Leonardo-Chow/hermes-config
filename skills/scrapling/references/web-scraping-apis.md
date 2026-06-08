# Web Scraping API Services

当浏览器爬取太慢或资源消耗过大时，可以使用 API 化的网页抓取服务。这些服务提供代理池、JS 渲染、反检测等能力。

## ScraperAPI

**用途**：通用网页抓取代理池，支持 JS 渲染、住宅代理、地理位置定位

| 项目 | 详情 |
|:-----|:-----|
| 官网 | https://www.scraperapi.com |
| 文档 | https://docs.scraperapi.com |
| 定价 | 免费 5000 次/月，付费 $49/月起 |
| 特点 | 代理池 + JS 渲染 + 结构化数据 |

### 基本用法

```python
import requests

payload = {
    'api_key': 'YOUR_KEY',
    'url': 'https://example.com',
    'render': 'true',  # 启用 JS 渲染
}
r = requests.get('https://api.scraperapi.com/', params=payload)
print(r.text)
```

### 高级参数

```python
payload = {
    'api_key': 'YOUR_KEY',
    'url': 'https://example.com',
    'render': 'true',
    'country_code': 'us',  # 地理位置
    'premium': 'true',     # 高级代理池
    'session_number': '123',  # 会话保持
    'device_type': 'mobile',  # 设备类型
}
```

### 环境变量配置

```bash
export SCRAPERAPI_API_KEY="your_key"
# 或写入 ~/.config/last30days/.env
```

### 已验证可用场景

- ✅ TikTok 主页抓取（返回完整 HTML，含 og:description 等元数据）
- ✅ 被墙网站抓取（自带代理，无需 VPN）
- ✅ JS 渲染页面（设置 `render=true`）

---

## ScrapeCreators

**用途**：社交媒体专用 API，支持 TikTok、Instagram、X、YouTube 等 27+ 平台

| 项目 | 详情 |
|:-----|:-----|
| 官网 | https://scrapecreators.com |
| 文档 | https://docs.scrapecreators.com |
| 定价 | 免费 100 积分，充值 $100 起（$1/1000 请求） |
| 特点 | 社交媒体专用，结构化数据，评论/字幕/粉丝数据 |

### 支持的平台

| 平台 | 端点示例 | 说明 |
|:-----|:---------|:-----|
| TikTok | `/v1/tiktok/profile/videos` | 个人主页视频列表 |
| TikTok | `/v1/tiktok/video/comments` | 视频评论 |
| TikTok | `/v1/tiktok/search/keyword` | 关键词搜索 |
| Instagram | `/v1/instagram/reels` | Reels 列表 |
| Instagram | `/v1/instagram/post` | 帖子详情 |
| X/Twitter | `/v1/x/tweet` | 推文详情 |
| YouTube | `/v1/youtube/video` | 视频详情 |

### 基本用法

```python
import requests

headers = {
    'x-api-key': 'YOUR_KEY',
    'Content-Type': 'application/json'
}
params = {
    'handle': 'obsbot',
    'count': 10
}
response = requests.get(
    'https://api.scrapecreators.com/v1/tiktok/profile/videos',
    headers=headers,
    params=params
)
data = response.json()
```

### 环境变量配置

```bash
export SCRAPECREATORS_API_KEY="your_key"
# 或写入 ~/.config/last30days/.env
```

### 额度管理

- 免费 100 积分，不需要信用卡
- 余额永不过期
- 每次 API 调用消耗 1 积分
- 额度用完后返回：`{"success": false, "message": "Looks like you're out of credits"}`

---

## 两者对比

| 维度 | ScraperAPI | ScrapeCreators |
|:-----|:-----------|:---------------|
| 定位 | 通用网页抓取 | 社交媒体专用 |
| 输出 | 原始 HTML | 结构化 JSON |
| 代理池 | ✅ 住宅/数据中心 | ❌ |
| JS 渲染 | ✅ | N/A |
| 社交平台 | ❌ 需自己解析 | ✅ 27+ 平台 |
| 评论/字幕 | ❌ | ✅ |
| 免费额度 | 5000 次/月 | 100 次（一次性） |
| 适合场景 | 通用网页、被墙网站 | TikTok/Instagram/X 数据采集 |

---

## 与 last30days Skill 的集成

`last30days` skill 使用 ScrapeCreators 作为 TikTok/Instagram/Threads 的数据源。当 ScrapeCreators 额度用完时：

1. **用 ScraperAPI 替代**：直接抓取 TikTok/Instagram 页面 HTML，自行解析
2. **充值 ScrapeCreators**：https://app.scrapecreators.com
3. **用 Scrapling 爬取**：浏览器爬取 TikTok 搜索页 + oembed API

### last30days 配置文件

```
~/.config/last30days/.env
```

内容示例：
```
SCRAPECREATORS_API_KEY=your_key
SCRAPERAPI_API_KEY=your_key
SETUP_COMPLETE=true
```

---

## Pitfalls

- **Key 混淆**：ScrapeCreators 和 ScraperAPI 是两家不同公司，Key 不通用
- **额度监控**：ScrapeCreators 额度用完会静默失败（返回 0 结果），需检查响应
- **TikTok 反爬**：即使是 API 服务，TikTok 也可能返回空数据或 CAPTCHA
- **代理地区**：ScraperAPI 的 `country_code` 参数影响结果，某些地区可能被封锁
