---
name: obsbot-daily-monitor
description: OBSBOT 每日监测工作流 — 搜索 YouTube/Instagram/TikTok/X 上的 OBSBOT 产品视频，创建腾讯文档智能表格。覆盖 10 个产品关键词，7 列结构。
version: 1.0.0
tags: [obsbot, monitoring, daily, youtube, instagram, tiktok, tencent-docs]
---

# OBSBOT 每日监测

每天搜索多平台 OBSBOT 产品相关内容，汇总到腾讯文档智能表格。

## 产品关键词

OBSBOT Tail Air / Tail 2 / Meet SE / Meet 2 / Tiny SE / Tiny 2 / Tiny 2 Lite / Tiny 3 / Tiny 3 Lite / Talent 2

## 平台覆盖 & 工具链

| 平台 | 工具 | 可靠性 | 说明 |
|:-----|:-----|:------|:-----|
| **YouTube** | YouTube Data API | ✅ HIGH | `curl` + API Key 直接搜索，日期过滤精确 |
| **Instagram** | Scrapling StealthyFetcher | ⚠️ MEDIUM | 可爬帖子列表和内容，但拿不到精确日期 |
| **TikTok** | ❌ 不可用 | ❌ | X-Bogus 反爬机制，所有方案均失败（2026-05-29 验证） |
| **X/Twitter** | web_search / xurl | ⚠️ LOW | web_search 索引延迟大；xurl 需注册 App |

## YouTube 搜索流程

```bash
# API Key: YOUR_YOUTUBE_API_KEY
# 搜索每个关键词
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=OBSBOT+Tiny+3&type=video&publishedAfter=YYYY-MM-DDT00:00:00Z&publishedBefore=YYYY-MM-DDT23:59:59Z&maxResults=20&key=API_KEY"

# 获取完整视频详情（含完整 description）
curl -s "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=VIDEO_IDS&key=API_KEY"
```

## Instagram 爬取流程

```python
# Scrapling StealthyFetcher + proxy
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch(
    'https://www.instagram.com/obsbot/',
    headless=True, network_idle=True, disable_resources=True,
    proxy='http://127.0.0.1:1082',  # Shadowrocket
    block_webrtc=True, hide_canvas=True,
)
# 提取帖子链接和内容
links = page.css('a[href*="/p/"]::attr(href)').getall()
links += page.css('a[href*="/reel/"]::attr(href)').getall()
```

## 腾讯文档表格

- **文件夹**：OBSBOT → 每日监测（ID: DumZsGZJrwsf）
- **表格类型**：smartsheet
- **7 列**：更新时间 / KOL ID / 产品关键词 / 平台 / 视频类型 / 视频简介 / 视频链接
- **视频类型**：YTB Dedicated Video / YTB Integration Video / YTB Shorts / TT video / INS reel / INS post / X post
- **简介要求**：完整内容，含营销链接、折扣码、Tags、免责声明

## 腾讯文档操作命令

```bash
# 创建智能表格
mcporter call 'tencent-docs' 'manage.create_file' --args '{"title":"OBSBOT Daily Monitor YYYY-MM-DD","file_type":"smartsheet"}'

# 获取 sheet_id
mcporter call 'tencent-docs' 'smartsheet.list_tables' --args '{"file_id":"FILE_ID"}'

# 添加字段
mcporter call 'tencent-docs' 'smartsheet.add_fields' --args '{"file_id":"FID","sheet_id":"SID","fields":[...]}'

# 添加记录
mcporter call 'tencent-docs' 'smartsheet.add_records' --args '{"file_id":"FID","sheet_id":"SID","records":[...]}'

# 移动到目标文件夹
mcporter call 'tencent-docs' 'manage.move_file' --args '{"file_id":"FID","target_folder_id":"DumZsGZJrwsf"}'
```

## 视频类型判断规则

| 场景 | 类型 |
|:-----|:-----|
| 整期视频评测 OBSBOT 产品 | YTB Dedicated Video |
| 视频中使用 OBSBOT 但非主推 | YTB Integration Video |
| YouTube Shorts 竖屏视频 | YTB Shorts |
| TikTok 视频 | TT video |
| Instagram Reels | INS reel |
| Instagram 图文帖 | INS post |
| X/Twitter 帖子 | X post |

## 已知限制

- **TikTok**：X-Bogus 反爬机制，无法通过任何 CLI/无头浏览器方案获取视频列表
- **Instagram**：Scrapling 可爬内容但无法获取精确发布日期
- **X/Twitter**：xurl 未配置时只能依赖 web_search（索引延迟 1-3 天）
- **简介完整性**：YouTube API 返回完整 description；Instagram 只能获取页面可见文本

## 并行策略

用 `delegate_task` 3 路并行：
1. YouTube API 搜索 + 完整简介获取
2. Instagram Scrapling 爬取
3. X/Twitter web_search + TikTok 尝试

总耗时约 3-5 分钟。
