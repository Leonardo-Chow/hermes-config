---
name: tiktok-data-collection
description: |
  TikTok 数据采集工具链 — 多源采集策略、API 端点、额度管理、免费替代方案。
  覆盖 ScrapeCreators、Omar API、ScraperAPI、oembed API、Scrapling 等工具。
  当需要搜索 TikTok 视频、获取用户资料、抓取视频详情时使用。
version: 1.0.0
tags: [tiktok, social-media, scraping, api, obsbot, data-collection]
---

# TikTok 数据采集

多源采集 TikTok 数据的统一工具链。根据场景选择最优方案。

## 数据源优先级（按成本排序）

| 优先级 | 方案 | 成本 | 适用场景 | 额度 |
|:-------|:-----|:-----|:---------|:-----|
| 1 | oembed API + 代理 | 免费 | 视频基本信息（标题、作者、封面） | 无限 |
| 2 | ScraperAPI | 按量计费 | 通用网页抓取、代理池 | 5000/月 |
| 3 | ScrapeCreators | 按量计费 | 用户资料、hashtag 搜索 | 95+ 积分 |
| 4 | Omar API | 按量计费 | 视频详情（含 HD 下载链接） | 100/月 |

**⚠️ 额度宝贵，优先用免费方案！**

## 免费方案：oembed API

最简单、最可靠的免费方案。获取视频基本信息。

```python
import subprocess, json

proxy = 'http://127.0.0.1:1082'  # Shadowrocket

def get_video_info_free(video_url):
    """用 oembed 获取视频基本信息 - 免费，无限次"""
    result = subprocess.run(
        ['curl', '-s', '--max-time', '8', '-x', proxy,
         f'https://www.tiktok.com/oembed?url={video_url}'],
        capture_output=True, text=True, timeout=15)
    return json.loads(result.stdout)

# 返回字段：
# - title: 视频标题
# - author_name: 作者昵称
# - author_url: 作者主页
# - thumbnail_url: 封面图
# - provider_name: "TikTok"
```

**注意**：必须通过代理（Shadowrocket at 127.0.0.1:1082），直连会 connection reset。

## 视频 ID 时间解码

从视频 URL 解码发布时间，无需 API 调用。

```python
from datetime import datetime

def decode_video_time(video_url):
    """从视频 URL 解码发布时间 - 免费"""
    vid_id = video_url.split('/video/')[-1].split('?')[0]
    ts = int(vid_id) >> 32  # Unix timestamp (秒)
    return datetime.fromtimestamp(ts)

# 示例
url = "https://www.tiktok.com/@obsbot/video/7353620611029898538"
dt = decode_video_time(url)
print(dt.strftime('%Y-%m-%d'))  # 发布日期
```

## ScrapeCreators API

覆盖 33+ 平台的统一数据采集 API。

### 认证

```
Header: x-api-key: YOUR_SCRAPECREATORS_API_KEY
配置文件: ~/.config/last30days/.env
```

### TikTok 端点

| 端点 | 方法 | 参数 | 说明 | 消耗 |
|:-----|:-----|:-----|:-----|:-----|
| `/v1/tiktok/profile` | GET | `handle` | 用户资料 | 1 积分 |
| `/v1/tiktok/search/hashtag` | GET | `hashtag`, `count` | hashtag 搜索 | 1 积分 |
| `/v1/tiktok/search/keyword` | GET | `query`, `count` | 关键词搜索 | 1 积分 |
| `/v1/tiktok/profile/videos` | GET | `handle`, `count` | 用户视频列表 | 1 积分 |
| `/v1/tiktok/video/info` | GET | `url` | 视频详情 | 1 积分 |

### 使用示例

```python
import requests

API_KEY = "YOUR_SCRAPECREATORS_API_KEY"
BASE = "https://api.scrapecreators.com"

def get_profile(handle):
    """获取用户资料"""
    resp = requests.get(
        f"{BASE}/v1/tiktok/profile",
        params={"handle": handle},
        headers={"x-api-key": API_KEY}
    )
    return resp.json()

def search_hashtag(hashtag, count=20):
    """hashtag 搜索 - 比关键词搜索更可靠"""
    resp = requests.get(
        f"{BASE}/v1/tiktok/search/hashtag",
        params={"hashtag": hashtag, "count": count},
        headers={"x-api-key": API_KEY}
    )
    return resp.json()
```

### ⚠️ 已知问题

- **关键词搜索返回空**：`/v1/tiktok/search/keyword` 经常返回 0 结果
- **hashtag 搜索更可靠**：用 hashtag 搜索替代关键词搜索
- **积分查询**：API 响应中包含 `credits_remaining` 字段

## Omar API (omkar.cloud)

专注 TikTok 数据的 API，提供 HD 下载链接。

### 认证

```
Header: API-Key: YOUR_OMKAR_API_KEY
配置文件: ~/.config/last30days/.env
额度: 100 次/月（免费）
```

### 端点

| 端点 | 参数 | 说明 | 消耗 |
|:-----|:-----|:-----|:-----|
| `/tiktok/users/profile` | `handle` | 用户资料 | 1 次 |
| `/tiktok/videos/details` | `video_url` | 视频详情（含下载链接） | 1 次 |
| `/tiktok/videos/search` | `search_query` | 搜索视频 | 1 次 |
| `/tiktok/videos/trending` | 无 | 热门推荐 | 1 次 |

### 使用示例

```python
import requests

OMKAR_KEY = "YOUR_OMKAR_API_KEY"
OMKAR_BASE = "https://tiktok-scraper.omkar.cloud"

def get_video_details(video_url):
    """获取视频详情 - 含 HD 无水印下载链接"""
    resp = requests.get(
        f"{OMKAR_BASE}/tiktok/videos/details",
        params={"video_url": video_url},
        headers={"API-Key": OMKAR_KEY}
    )
    return resp.json()

# 返回字段：
# - media.video_url: 标清视频
# - media.hd_video_url: 高清无水印视频
# - stats.views/likes/comments/shares: 统计数据
# - author.handle/display_name: 作者信息
```

### ⚠️ 额度管理

每月仅 100 次免费请求，必须合理分配：

| 用途 | 预算/月 | 说明 |
|:-----|:--------|:-----|
| 竞品监测 | 40 次 | 关键视频详情 |
| KOL 验证 | 30 次 | 高价值 KOL 资料 |
| 应急备用 | 30 次 | 临时需求 |

额度追踪脚本：`~/.hermes/scripts/omkar_usage.py`

```bash
python3 ~/.hermes/scripts/omkar_usage.py        # 查看状态
python3 ~/.hermes/scripts/omkar_usage.py check 5 # 检查额度
python3 ~/.hermes/scripts/omkar_usage.py add 3 "用途" # 记录使用
```

## ScraperAPI

通用网页抓取代理池，可抓取 TikTok 页面。

```python
import requests

SCRAPER_KEY = "15cc5a7041e63c43224b37aea4a74e26"

def scrape_tiktok_page(url):
    """用 ScraperAPI 抓取 TikTok 页面"""
    resp = requests.get(
        "https://api.scraperapi.com/",
        params={
            "api_key": SCRAPER_KEY,
            "url": url,
            "render": "true"  # 启用 JS 渲染
        }
    )
    return resp.text
```

## Scrapling 搜索页爬取

用反检测浏览器爬取 TikTok 搜索页，获取视频链接列表。

```python
from scrapling.fetchers import StealthyFetcher

proxy = 'http://127.0.0.1:1082'

def search_tiktok_links(keyword):
    """搜索页获取视频链接 - 免费"""
    page = StealthyFetcher.fetch(
        f'https://www.tiktok.com/search?q={keyword}',
        headless=True, network_idle=True, disable_resources=True,
        proxy=proxy, block_webrtc=True, hide_canvas=True
    )
    return page.css('a[href*="/video/"]::attr(href)').getall()
```

## 场景选择指南

| 场景 | 推荐方案 | 原因 |
|:-----|:---------|:-----|
| 获取视频基本信息 | oembed API | 免费、可靠 |
| 搜索特定 hashtag | ScrapeCreators | hashtag 搜索稳定 |
| 获取用户资料 | ScrapeCreators | 数据丰富 |
| 获取视频下载链接 | Omar API | 提供 HD 无水印 |
| 批量抓取页面 | ScraperAPI | 代理池、JS 渲染 |
| 搜索页链接列表 | Scrapling | 免费、反检测 |

## 配置文件位置

```
~/.config/last30days/.env
├── SCRAPECREATORS_API_KEY
├── SCRAPERAPI_API_KEY
├── OMKAR_API_KEY
└── SETUP_COMPLETE=true
```

## 已知限制

1. **TikTok 反爬**：X-Bogus 机制，Profile 页面有 CAPTCHA
2. **关键词搜索不可靠**：ScrapeCreators 的 keyword 搜索经常返回空
3. **hashtag 搜索更稳定**：优先用 hashtag 搜索
4. **VPN 依赖**：oembed API 和 Scrapling 需要代理
5. **额度限制**：Omar API 100次/月，ScrapeCreators 按积分计费

## 相关 Skill

- `obsbot-daily-monitor` — OBSBOT 每日监测（已集成 TikTok 数据源）
- `obsbot-competitor-monitor` — OBSBOT 竞品监测（已集成 TikTok 数据源）
- `last30days` — 跨平台研究工具（~/.hermes/skills/last30days/）
