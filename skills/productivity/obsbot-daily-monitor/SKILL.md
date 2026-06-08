---
name: obsbot-daily-monitor
description: OBSBOT 每日监测工作流 — 搜索 YouTube/Instagram/TikTok/X 上的 OBSBOT 产品视频，创建腾讯文档智能表格。覆盖 10 个产品关键词，7 列结构。
version: 1.0.0
tags: [obsbot, monitoring, daily, youtube, instagram, tiktok, tencent-docs]
---

# OBSBOT 每日监测

每天搜索多平台 OBSBOT 产品相关内容，汇总到腾讯文档智能表格。

**⚠️ 必须搜索全部 10 个产品关键词**（用户 2026-06-01 确认）。不能只搜索 Tiny 3 和 Tiny 2，必须覆盖所有产品线。

## 产品关键词

OBSBOT Tail Air / Tail 2 / Meet SE / Meet 2 / Tiny SE / Tiny 2 / Tiny 2 Lite / Tiny 3 / Tiny 3 Lite / Talent 2

## 平台覆盖 & 工具链

| 平台 | 工具 | 可靠性 | 说明 |
|:-----|:-----|:------|:-----|
| **YouTube** | YouTube Data API | ✅ HIGH | `curl` + API Key 直接搜索，日期过滤精确 |
| **Instagram** | Scrapling StealthyFetcher | ⚠️ MEDIUM | 可爬帖子列表和内容，但拿不到精确日期 |
| **TikTok** | Scrapling search + oembed API | ✅ HIGH | 搜索页获取链接 + oembed API 获取详情 + 视频 ID 解码时间（2026-05-31 验证） |
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

## TikTok 爬取流程

### 额度管理（⚠️ 重要）

**Omar TikTok API（omkar.cloud）每月仅 100 次免费请求，必须合理分配！**

| 用途 | 预算/月 | 说明 |
|:-----|:--------|:-----|
| OBSBOT 竞品监测 | 40 次 | 每周一/三/五，每次约 3-5 个关键视频详情 |
| KOL 资料验证 | 30 次 | 高价值 KOL 的详细资料和视频历史 |
| 应急备用 | 30 次 | 用户临时需求、特殊查询 |

**优先级规则**：
1. **🔴 必须用 Omar API**：获取视频完整数据（含 HD 下载链接）、验证 KOL 资料真实性
2. **🟡 用免费替代**：视频基本信息 → oembed API、批量搜索 → ScraperAPI

### TikTok 数据源优先级

| 优先级 | 方案 | 额度消耗 | 适用场景 |
|:-------|:-----|:---------|:---------|
| 1 | oembed API + 代理 | 免费 | 视频基本信息（标题、作者、封面） |
| 2 | ScraperAPI | 按量计费 | 通用网页抓取 |
| 3 | Omar API | 100次/月 | 视频详情、用户资料、搜索 |
| 4 | Scrapling | 免费 | 搜索页获取链接列表 |

### Omar API 端点

```python
import requests

OMKAR_API_KEY = "YOUR_OMKAR_API_KEY"  # 存 ~/.config/last30days/.env
OMKAR_BASE = "https://tiktok-scraper.omkar.cloud"

def get_tiktok_profile(handle):
    """获取用户资料 - 消耗1次额度"""
    resp = requests.get(
        f"{OMKAR_BASE}/tiktok/users/profile",
        params={"handle": handle},
        headers={"API-Key": OMKAR_API_KEY}
    )
    return resp.json()

def get_video_details(video_url):
    """获取视频详情 - 消耗1次额度"""
    resp = requests.get(
        f"{OMKAR_BASE}/tiktok/videos/details",
        params={"video_url": video_url},
        headers={"API-Key": OMKAR_API_KEY}
    )
    return resp.json()

def search_videos(query):
    """搜索视频 - 消耗1次额度"""
    resp = requests.get(
        f"{OMKAR_BASE}/tiktok/videos/search",
        params={"search_query": query},
        headers={"API-Key": OMKAR_API_KEY}
    )
    return resp.json()
```

### 免费替代方案（优先使用）

```python
import subprocess, json
from datetime import datetime

proxy = 'http://127.0.0.1:1082'  # Shadowrocket

# oembed API - 免费，获取视频基本信息
def get_video_info_free(video_url):
    """用 oembed 获取基本信息 - 免费"""
    result = subprocess.run(
        ['curl', '-s', '--max-time', '8', '-x', proxy,
         f'https://www.tiktok.com/oembed?url={video_url}'],
        capture_output=True, text=True, timeout=15)
    return json.loads(result.stdout)

# 视频 ID 解码时间 - 免费
def decode_video_time(video_url):
    """从视频 URL 解码发布时间 - 免费"""
    vid_id = video_url.split('/video/')[-1]
    ts = int(vid_id) >> 32  # Unix timestamp (秒)
    return datetime.fromtimestamp(ts)
```

### 搜索页爬取（免费）

```python
from scrapling.fetchers import StealthyFetcher

# 搜索页获取视频链接 - 免费
def search_tiktok_links(keyword):
    """搜索页获取视频链接 - 免费"""
    page = StealthyFetcher.fetch(
        f'https://www.tiktok.com/search?q={keyword}',
        headless=True, network_idle=True, disable_resources=True,
        proxy=proxy, block_webrtc=True, hide_canvas=True
    )
    return page.css('a[href*="/video/"]::attr(href)').getall()
```

### 额度追踪文件

```bash
# 追踪文件位置
~/.hermes/config/omkar_usage.txt

# 格式：日期: 使用次数 (用途)
2026-06-08: 5 (初始测试)
2026-06-09: 3 (OBSBOT竞品监测)
```

**注意**：VPN 必须连接（Shadowrocket at 127.0.0.1:1082），否则 Scrapling 和 oembed API 都会超时。已知 OBSBOT TikTok 账号：`@obsbot`（17.5K粉丝）、`@obsbot_us`、`@obsbot.my`。标签：`#obsbot`、`#obsbot_tiny3lite`。

## YouTube 批量搜索脚本

用 Python 脚本批量搜索比逐个 curl 更可靠（避免 VPN 断连导致部分关键词超时）：

```python
#!/usr/bin/env python3
import json, urllib.request, urllib.parse

API_KEY=*** = "YYYY-MM-DD"
keywords = ["OBSBOT", "OBSBOT Tiny 3", "OBSBOT Tiny 3 Lite", "OBSBOT Tiny 2",
    "OBSBOT Tiny 2 Lite", "OBSBOT Tiny SE", "OBSBOT Tail 2", "OBSBOT Tail Air",
    "OBSBOT Meet 2", "OBSBOT Meet SE", "OBSBOT Talent 2", "OBSBOT webcam",
    "OBSBOT camera", "OBSBOT unboxing", "OBSBOT review", "OBSBOT streaming"]

all_videos = {}
for kw in keywords:
    params = urllib.parse.urlencode({
        'part': 'snippet', 'q': kw, 'type': 'video',
        'publishedAfter': f'{DATE}T00:00:00Z',
        'publishedBefore': f'{DATE}T23:59:59Z',
        'maxResults': 20, 'key': API_KEY
    })
    url = f"https://www.googleapis.com/youtube/v3/search?{params}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url), timeout=15) as resp:
            data = json.loads(resp.read().decode())
            for item in data.get('items', []):
                vid = item['id']['videoId']
                if vid not in all_videos:
                    s = item['snippet']
                    all_videos[vid] = {
                        'id': vid, 'title': s['title'], 'channel': s['channelTitle'],
                        'published': s['publishedAt'], 'desc': s.get('description','')[:300],
                        'url': f'https://youtube.com/watch?v={vid}', 'keyword': kw
                    }
    except Exception as e:
        print(f"[{kw}] ERROR: {e}")

# 过滤 OBSBOT 相关
obsbot_related = [v for v in all_videos.values() if any(
    k in v['title'].lower() or k in v['desc'].lower()
    for k in ['obsbot', 'tiny 3', 'tiny 2', 'tail 2', 'tail air', 'meet 2', 'meet se', 'talent 2']
)]
```

**关键坑**：VPN 长任务会断，部分关键词会 IncompleteRead 或 SSL EOF。脚本会跳过失败的关键词继续执行，最后汇总所有成功的结果。

## SOP 工作流（IMA 笔记：OBSBOT每日上线SOP）

IMA 笔记链接：https://ima.qq.com/note/share/_AweMLuM8wuZLJgQaVVlNg

每日执行 3 步：

### Step 1 社交媒体检索
- 覆盖 4 平台：YouTube / Instagram / TikTok / X
- 10 个产品关键词
- 视频类型：YTB Dedicated / Integration / Shorts / TT video / INS reel / INS post / X post
- ❌ 无效视频：只挂购买链接未展示产品 / 纯官方宣传素材切片

### Step 2 内容质检

详细质检要求见 `references/quality-check-requirements.md`。

每条视频检查：
1. **视频内容**：是否原画直出、是否特殊主题（榜单/对比/教程/特殊场景/展会采访）
2. **描述区**：官网链接、亚马逊链接、渠道链接、标签、折扣信息（每项打勾或打叉）

### Step 3 输出上线资源报告（两部分结构）

报告必须包含两部分，不能只输出筛选结果：

**Part 1：全平台搜索结果（所有第三方 OBSBOT 相关内容）**
- 列出当日搜索到的**所有** OBSBOT 相关内容
- **必须过滤 OBSBOT 官方账号**（@obsbot、@OBSBOT_Official、@obsbotmy、@obsbot_us 等）
- 按平台分组：YTB / TT / INS / X
- 每条包含：博主、标题、链接、发布时间、简介

**Part 2：符合 SOP 要求的视频**\n- 从 Part 1 中筛选出符合要求的视频\n- 筛选标准：视频必须包含完整的产品测评内容\n- ❌ 排除：只挂购买链接未展示产品 / 纯官方宣传素材切片 / 品牌大使直播中使用（非专门测评）/ 仅描述中提到但无产品展示\n- 按平台分组，每条标注产品、视频类型、简析\n- **⚠️ Part 2 必须附带链接**（用户明确要求 2026-05-31）

**⚠️ 腾讯文档 smartcanvas 中链接必须用纯文本 URL**（用户 2026-06-01 确认）。不要用 `[链接](URL)` 格式，直接写 `https://...`。

**⚠️ 每条视频必须单独列出**（用户 2026-06-01 确认）。不要把多条视频放在表格的一行里，每条视频用加粗编号 + 标题作为独立条目。

**⚠️ 多工具交叉验证**（用户 2026-06-01 确认）。不能只用一种工具搜索，需要用 YouTube API + web_search + 浏览器搜索等多种方式交叉验证，确保不遗漏任何视频。

**⚠️ 必须全面**（用户 2026-06-01 确认）。所有视频链接都要写出来，不能只输出筛选后的结果，Part 1 必列所有找到的内容。

**排除说明**：在报告末尾列出被排除的视频及原因

格式示例（每条视频独立列出，链接用纯文本 URL）：
```
## 5月30日（周六）

### 全平台搜索结果

#### YouTube（6条）

**1. OBSBOT Tiny 3 + Vox SE Review - Best webcam yet?**
- 博主：LevelUP Gaming & Tech
- 链接：https://www.youtube.com/watch?v=1wA3SztU7Zs
- 产品：Tiny 3
- 类型：Dedicated Video

**2. OBSBOT Tiny 3 Lite et micro VOX SE**
- 博主：GUILLAUME++
- 链接：https://www.youtube.com/watch?v=OBZjBTIfrEI
- 产品：Tiny 3 Lite
- 类型：Dedicated Video

#### TikTok（1条）

**1. Is this the smartest webcam ever? OBSBOT Tiny 3 Unboxing!**
- 博主：@mrsmobster
- 链接：https://www.tiktok.com/@mrsmobster/video/7645867491847130381

#### Instagram（0条）

今日无新帖。

#### X/Twitter（1条）

**1. 使用 OBSBOT AI 追尾摄像头录制播客**
- 账号：@SCHOOLLIVEBAR

---

### 符合 SOP 要求的视频

**1. OBSBOT Tiny 3 + Vox SE Review - Best webcam yet?**
- 博主：LevelUP Gaming & Tech
- 链接：https://www.youtube.com/watch?v=1wA3SztU7Zs
- 产品：Tiny 3
- 类型：Dedicated Video
- 视频内容质检：
  - ☑️ 常规产品测评
  - ☑️ 原画直出演示
  - ☑️ 特殊主题：无
- 描述区质检：
  - ☑️ 官网链接：有
  - ☑️ 亚马逊链接：有
  - ☑️ 折扣信息：有（DERMO505，5% off）
  - ☑️ 标签：有（#obsbot #obsbot_Tiny3 等）
```

已合作红人需标记对应小伙伴名字（参考 KOL资源交接表）。

详细输出格式模板见 `references/sop-output-format.md`。
产品覆盖情况表格式见 `references/product-coverage-table.md`。

## 腾讯文档上传

**推荐方式：create_smartcanvas_by_mdx**（智能文档，Markdown 格式，排版美观）

```bash
mcporter call tencent-docs create_smartcanvas_by_mdx --args '{"title": "OBSBOT上线资源报告_YYYY-MM-DD", "mdx": "报告内容..."}'
# 返回 file_id 和 url
mcporter call tencent-docs manage.move_file --args '{"file_id": "FILE_ID", "target_folder_id": "DjbGtzenXmbX"}'
```

**⚠️ 不推荐 import_file.sh + Word 文档**：import_file.sh 上传 .docx 后，manage.search_file 可能搜不到导入的文件（已知坑）。用 create_smartcanvas_by_mdx 更可靠，Markdown 表格直接渲染。

**文件夹**：OBSBOT（ID: DjbGtzenXmbX）

## 腾讯文档表格（KOL 筛选用）

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

## KOL 筛选工作流

除了每日内容监测，此 skill 也覆盖 KOL 筛选任务。

### 筛选标准（用户确认）

1. **不要大博主** — 中腰部/nano 为主（粉丝 <200K，均播 <50K）
2. **账号真实有效** — YouTube API 验证 3 个月内有更新
3. **筛掉 OBSBOT 合作过的** — YouTube API 搜索频道内 "obsbot" 相关视频
4. **重点关注竞品合作过的** — 搜索 "insta360 link" OR "elgato facecam" OR "logitech brio" 等
5. **不获取邮箱** — 暂不需要联系方式
6. **去重** — 与已有筛选结果对比，排除重复

### KOL 筛选流程

```
Step 1: NoxInfluencer 多品类搜索（5 品类并行）
  - Tech 3C / Camera / Livestream / Apple / Desk Setup
  - 过滤: avg_view_min=3000, avg_view_max=50000, follower_max=200000, published_within_days=90
  - 注意: search 结果不含 channel_url，需逐个调 creator profile 获取

Step 2: YouTube API 验证（3 项检查）
  - 活跃度: search(channelId, order=date) → 最近视频是否在 90 天内
  - OBSBOT 合作: search(channelId, q="obsbot") → 检查标题是否含 OBSBOT 关键词
  - 竞品合作: search(channelId, q="insta360 OR elgato OR logitech webcam") → 标记

Step 3: 去重 + 排除
  - 排除昨天已筛选的 KOL（按 nickname 匹配）
  - 排除品牌官方号（Hikvision、Nikon 等）
  - 排除 OBSBOT 已合作的

Step 4: 生成腾讯文档智能表格
  - 15 列：产品/KOL ID/频道链接/受众国家/粉丝量K/均播k/互动率/一级类目/二级类目/视频形式/平台/合作价格/建议理由/筛选时间/竞品合作
  - 合作价格估算: <$30K粉=$100-200, $30-80K=$200-400, $80-150K=$400-700, >$150K=$700-1200
```

### NoxInfluencer KOL 筛选命令

```bash
# 多品类搜索（示例：Tech 3C）
noxinfluencer creator search --platform youtube \
  --keywords '[webcam review,4K webcam,PTZ camera]' \
  --country '[US,CA,UK]' \
  --avg_view_min 3000 --avg_view_max 50000 \
  --follower_min 5000 --follower_max 200000 \
  --published_within_days 90 --page_size 10 --lang en

# 获取频道 URL（search 结果不含 channel_url）
noxinfluencer creator profile <creator_id> --json

# shell_quote 必须！creator_id 含特殊字符
from hermes_tools import terminal, shell_quote
r = terminal(f'noxinfluencer creator profile {shell_quote(cid)} --json', timeout=30)
```

### YouTube API 验证命令

```bash
# 检查最近视频（活跃度）
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CHANNEL_ID&type=video&maxResults=1&order=date&key=API_KEY"

# 搜索频道内 OBSBOT 内容
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CHANNEL_ID&q=obsbot&type=video&maxResults=5&order=date&key=API_KEY"

# 搜索频道内竞品内容
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CHANNEL_ID&q=insta360+OR+elgato+webcam&type=video&maxResults=5&order=date&key=API_KEY"
```
## 已知限制

- **TikTok**：X-Bogus 反爬机制，无法通过任何 CLI/无头浏览器方案获取视频列表。已验证方案：curl+proxy（空响应）、Scrapling DynamicFetcher（视频不渲染）、Playwright+Cookie（被检测）、bb-browser 真实 Chrome（API 返回空）。替代方案：NoxInfluencer Brand Monitor（需 brand_id）或手动确认。
- **TikTok Cookie 提供也不行** — 用户提供了完整 TikTok Cookie，Playwright 设置后仍被反爬检测。X-Bogus 令牌由页面 JS 生成，无法通过外部注入绕过。
- **Instagram**：Scrapling StealthyFetcher + proxy `http://127.0.0.1:1082` 可爬帖子列表和内容，但无法获取精确发布日期。
- **X/Twitter**：xurl 未配置时只能依赖 web_search（索引延迟 1-3 天）。xurl 需要注册 App（`xurl auth apps add`）。twitter CLI 需要浏览器登录态。
- **简介完整性**：YouTube API 返回完整 description；Instagram 只能获取页面可见文本。
- **TikTok VPN 依赖**：Scrapling 必须通过 Shadowrocket 代理（127.0.0.1:1082），VPN 断开会导致超时

## KOL 筛选工作流

当用户要求筛选 KOL 时，使用 NoxInfluencer + YouTube API 的两阶段流程：

### 阶段一：NoxInfluencer 搜索
- 按品类并行搜索（Tech 3C / Camera / Livestream / Apple / Gamer / Desk Setup / Podcast / Productivity）
- 筛选条件：`avg_view_min 3000, avg_view_max 50000, follower_min 5000, follower_max 200000, published_within_days 90`
- 每个品类搜 10-15 个，去重后合并

### 阶段二：YouTube API 三重验证
对每个候选人执行：
1. **获取频道 ID** — `creator profile <id>` 获取 channel_url
2. **活跃度验证** — YouTube API 搜索最新视频，>90 天未更新直接筛掉
3. **OBSBOT 合作检查** — YouTube API 搜索频道内 OBSBOT 相关视频，有则筛掉
4. **竞品合作检查** — YouTube API 搜索频道内竞品视频（Insta360/Elgato/Logitech），有则标记为优先

### 关键要求
- ❌ 不找大博主（Top 级别）
- ❌ 超过 3 个月没更新的筛掉
- ❌ 与 OBSBOT 合作过的筛掉
- ⭐ 重点关注竞品合作过但 OBSBOT 没合作过的
- ⏭️ 暂不获取邮箱
- 📊 排除之前已筛选的所有 KOL（建立 exclusion set）

### 输出
生成腾讯文档智能表格到 OBSBOT → 每日监测 文件夹（ID: DumZsGZJrwsf）

## ⚠️ 用户偏好

**连续执行，不要一步一停** — 用户明确要求：搜索→验证→生成表格，全程自动执行，不要中途停下来等确认。遇到错误（VPN断、API超时）自动重试，最终汇报结果。

## 并行策略

用 `delegate_task` 3 路并行：
1. YouTube API 搜索 + 完整简介获取
2. Instagram Scrapling 爬取
3. X/Twitter web_search + TikTok 尝试

总耗时约 3-5 分钟。

## 多轮搜索确保无遗漏

用户明确要求（2026-05-31）：**必须多次检测确保没有遗漏。**

**⚠️ 多工具交叉验证**（用户 2026-06-01 确认）。不能只用一种工具搜索，需要用 YouTube API + web_search + 浏览器搜索等多种方式交叉验证，确保不遗漏任何视频。用户明确说"你已经漏了很多视频和内容"。

**⚠️ 必须全面**（用户 2026-06-01 确认）。所有视频链接都要写出来，不能只输出筛选后的结果，Part 1 必须列出所有找到的内容。用户明确说"所有的视频链接都要写出来，必须要全面"。

**⚠️ 多工具交叉验证**（用户 2026-06-01 确认）。不能只用一种工具搜索，需要用多种方式交叉验证：
1. YouTube Data API 搜索
2. 浏览器直接搜索 YouTube（`browser_navigate` 到 YouTube 搜索页）
3. web_search 搜索 `site:youtube.com OBSBOT`
4. TikTok oembed API 验证
5. Instagram/X web_search

执行策略：
1. **第一轮**：13 个产品关键词直接搜索（OBSBOT Tiny 3, OBSBOT Tail 2, ...）
2. **第二轮**：变体关键词补充搜索（Tiny 3 webcam, Tail 2 camera, OBSBOT unboxing, OBSBOT review, ...）
3. **第三轮**：品牌大使/联盟关键词（OBSBOT brand ambassador, OBSBOT affiliate）
4. **去重**：按 video ID 去重，汇总所有轮次的结果

YouTube API 部分关键词会因 VPN 断连返回 IncompleteRead，脚本会跳过失败关键词继续执行。需要跑两轮脚本确保覆盖。

## 腾讯文档编辑（更新已有文档）

当需要更新已创建的智能文档（如添加链接列）时，使用 smartcanvas 编辑工具：

```bash
# 1. 搜索锚点
mcporter call tencent-docs smartcanvas.find --args '{"file_id": "FILE_ID", "query": "要查找的文本"}'
# 返回 blocks[].id

# 2. 删除旧内容
mcporter call tencent-docs smartcanvas.edit --args '{"file_id": "FILE_ID", "action": "DELETE", "id": "BLOCK_ID"}'

# 3. 在锚点后插入新内容
mcporter call tencent-docs smartcanvas.edit --args '{"file_id": "FILE_ID", "action": "INSERT_AFTER", "id": "ANCHOR_ID", "content": "新内容..."}'
```

**⚠️ 已知坑**：
- 搜索返回多个同名块时，需要根据上下文判断删除哪个（如 Part 1 和 Part 2 都有"TikTok（1条）"标题）
- 表格内容在 get_content 中被提取为纯文本，Markdown 链接 `[文本](URL)` 显示为"文本"
- 推荐直接用 `create_smartcanvas_by_mdx` 一次性创建完整内容，避免后续编辑

## ⚠️ YouTube API 配额耗尽

YouTube Data API 每日配额限制 100 次搜索。当返回 `429 Quota exceeded` 时：

** fallback 策略**：
1. **浏览器搜索**：`browser_navigate` 到 YouTube 搜索页，用 `browser_snapshot` 提取结果
2. **web_search**：搜索 `site:youtube.com OBSBOT Tiny 3 2026`
3. **已知视频 ID 验证**：用 `videos?part=snippet&id=VIDEO_ID` 获取详情（不消耗搜索配额）

**配额管理**：
- 每次搜索消耗 100 单位，每日上限 10,000 单位
- 批量搜索 16 个关键词 = 1,600 单位
- 多日报告（3天）需要 3 轮搜索 = 4,800 单位
- 建议：优先搜索核心关键词（OBSBOT + 10个产品名），变体关键词用 fallback 策略

## OBSBOT Admin System API（确认网红管理）

详细的 API 端点、认证方式、数据结构见 `references/obsbot-admin-api.md`。

### 核心要点

- **API 域名**: `https://api.obsbot.cn`（UMS = 用户管理, PMS = 网红/产品管理）
- **认证**: JWT token 作为 `Authorization` header（无 Bearer 前缀）+ `dealer-proxy-type: Remo`
- **用户**: leonardo@obsbot.com（周龙），Role=2（Market Admin）

### ⚠️ 关键 Pitfall

**`/v1/netizen/infos-filtering` 返回 500** — 这是唯一的批量列表接口，服务端 bug，所有参数组合都返回 500。浏览器上下文调也一样。

**替代方案**: `scripts/scan_netizens.py` — 逐 ID 扫描 + 大使数据合并。扫描 ID 1-20000，约 20 分钟可获取 ~1,572 条确认网红 + ~398 条独立大使 = ~1,970 条唯一记录。

### 数据计数说明

| 数据源 | 总数 | 说明 |
|--------|------|------|
| `v2/confirmed/statistics` → `all_total_infos.total` | **2,385** | 唯一确认网红数 |
| `v2/confirmed/views/distribution` → sum | **2,860** | 平台级条目（一个网红多个平台） |
| 品牌大使列表 | **599** | 独立数据集，与网红列表部分重叠 |

以 2,385 为确认网红总数。2,860 含重复平台条目。

### 文件夹

- **OBSBOT**: DjbGtzenXmbX

## ⚠️ 关键约束

**VPN 稳定性是首要约束。** Shadowrocket 长时间任务会断开，需要定期检查连接状态。YouTube API 和 TikTok Scrapling 都依赖 VPN。遇到 VPN 断开时先重连再继续。

详见 `references/platform-constraints.md` 获取每个平台的详细状态和工具矩阵。
详见 `references/tiktok-api-matrix.md` 获取 TikTok 多 API 对比、端点速查、额度分配策略。
详见 `references/last30days-setup.md` 获取 last30days 深度研究工具的安装、配置、pitfall。
