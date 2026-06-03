---
name: obsbot-daily-launch-monitor
description: |
  OBSBOT 每日上线资源检测 — 自动搜索 YouTube/TikTok/Instagram/X 四平台，
  覆盖10个产品关键词，按日期范围筛选，生成质检报告并上传腾讯文档。
version: 1.0.0
author: Leonardo
metadata:
  hermes:
    tags: [OBSBOT, YouTube, TikTok, Instagram, Twitter, monitoring, daily-report]
    related_skills: [tencent-docs, youtube-full, scrapling, noxinfluencer]
---

# OBSBOT 每日上线资源检测

自动搜索 OBSBOT 产品在 YouTube/TikTok/Instagram/X 四平台的上线内容，生成质检报告并上传腾讯文档。

## 触发条件

当用户提到以下关键词时使用此 skill：
- OBSBOT 上线资源
- OBSBOT 每日监测
- OBSBOT 视频检测
- OBSBOT 内容监控

## 产品关键词（10个）

```
OBSBOT Tail Air
OBSBOT Tail 2
OBSBOT Meet SE
OBSBOT Meet 2
OBSBOT Tiny SE
OBSBOT Tiny 2
OBSBOT Tiny 2 Lite
OBSBOT Tiny 3
OBSBOT Tiny 3 Lite
OBSBOT Talent 2
```

## 搜索平台（4个）

| 平台 | 搜索方式 | 备注 |
|:-----|:---------|:-----|
| YouTube | YouTube Data API v3 | 主力，API Key: YOUR_YOUTUBE_API_KEY |
| TikTok | oembed API + web_search | Profile 有 CAPTCHA，用 oembed 验证 |
| Instagram | web_search | 无法直接爬取，用搜索引擎间接获取 |
| X/Twitter | web_search | 无法直接爬取，用搜索引擎间接获取 |

## 完整流程

### Step 1: 检查 VPN 状态

```bash
scutil --nc status "Shadowrocket" 2>/dev/null | head -2
```

如果断开，重新连接：
```bash
scutil --nc start "Shadowrocket" 2>&1; sleep 3
```

### Step 2: YouTube 搜索

#### 方式1: YouTube Data API（推荐）

> **配额优化**：使用 `~/.hermes/scripts/yt_optimizer.py`，10 关键词搜索 = 1000 单位首次，24h 内缓存 = 0 单位。下午执行 = 完全省配额。

```python
import sys
sys.path.insert(0, str(Path.home() / '.hermes' / 'scripts'))
from yt_optimizer import api_call, batch_videos

products = ["OBSBOT Tiny 3", "OBSBOT Tail 2", "OBSBOT Meet 2", ...]

for product in products:
    # 搜索（带 24h 缓存，同天下午 = 0 单位）
    result = api_call("search", {
        "q": product,
        "type": "video", "part": "snippet",
        "publishedAfter": "2026-06-03T00:00:00Z",
        "publishedBefore": "2026-06-03T23:59:59Z",
        "maxResults": "20", "order": "date",
    }, cost=100, ttl=86400)

# 批量获取视频详情（50个 = 1 单位）
all_ids = [...]  # 从搜索结果收集
details = batch_videos(all_ids)
```

**配额对比**：
- 传统方式：10 × 100 = 1000 单位/次，每天 2 次 = 2000 单位
- 优化方式：上午 1000 单位，下午 0 单位（缓存），共 1000 单位/天
- 3 Key 轮换 = 30,000 单位/天，优化后剩余 29,000 单位

#### 方式2: 浏览器搜索（API 配额用完时）

```python
browser_navigate("https://www.youtube.com/results?search_query=OBSBOT+Tiny+3")
# 获取搜索结果中的视频ID
```

#### 获取视频详情

```bash
curl -s --max-time 12 "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=$VIDEO_ID&key=$API_KEY"
```

返回字段：
- title: 视频标题
- channelTitle: 频道名
- description: 描述区全文
- tags: 标签列表

### Step 3: TikTok 搜索（必须用多策略交叉验证）

> ⚠️ **重要教训**：web_search 索引有延迟，新发布的视频（1-3天内）不会被收录。必须用多种方式交叉验证，否则会漏掉视频。

#### 策略1: web_search 间接搜索（覆盖历史视频）

```python
# 搜索所有产品关键词，不能只搜热门产品
for product in ["OBSBOT", "Tiny 3", "Tiny 2", "Tail 2", "Meet 2", "Talent", "Tiny 3 Lite", "Tiny 2 Lite", "Meet SE", "Tiny SE", "Tail Air"]:
    web_search(f'site:tiktok.com "{product}" 2026', limit=10)
    web_search(f'tiktok "{product}" review unboxing 2026', limit=10)
```

#### 策略2: oembed API 验证已知视频（最可靠）

```bash
# 对已知视频ID用oembed验证，带Cookie效果更好
COOKIE=$(python3 -c "import json; print(json.load(open('/Users/zhoulong/.hermes/cookies/platform_cookies.json'))['tiktok'])")
curl -s --max-time 8 -x http://127.0.0.1:1082 \
  -H "Cookie: $COOKIE" \
  "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@USER/video/VIDEO_ID"
```

#### 策略3: 已知账号定期扫描

维护一个 OBSBOT 相关 TikTok 账号列表，定期检查最新视频：

```
@obsbot (OBSBOT Official, 17.5K粉丝)
@obsbotmy1 (obsbotmy)
@psscreativemedia (PSS Creative Media)
@mrsmobster (MrsMobster)
@maccagames (MaccaGames)
@brainiacvp (BrainiacVP)
@obsbot.thailand
@obsbotmy
@obsbotsingapore
```

#### 策略4: 视频 ID 解码时间

```python
import datetime
timestamp = int(video_id) >> 32
date = datetime.datetime.fromtimestamp(timestamp).date()
```

#### 策略5: Cookie 认证搜索（需要用户登录态）

当以上策略都无法覆盖最新视频时，需要用户提供 TikTok Cookie：
- 保存位置：`~/.hermes/cookies/platform_cookies.json`
- 使用方式：curl 带 Cookie 头访问 TikTok API
- Cookie 有效期：1-2 周，过期后需用户重新获取

#### 方式3: 已知账号逐个检查

已知 OBSBOT 相关 TikTok 账号：
- @obsbot（OBSBOT Official，17.5K 粉丝）
- @obsbotmy1（obsbotmy）
- @psscreativemedia（PSS Creative Media）
- @mrsmobster（MrsMobster）
- @maccagames（MaccaGames）
- @brainiacvp（Brainiacvp）
- @cestlabby
- @stephskiii

对每个账号，用 oembed API 验证最新视频。

#### 方式4: web_search 间接搜索（补充）

```python
web_search('site:tiktok.com OBSBOT 2026-05', limit=20)
web_search('tiktok OBSBOT Tiny 3 review May 2026', limit=10)
```

注意：web_search 结果可能遗漏最新视频，仅作为补充。

#### 方式5: 用户提供 Cookie 登录浏览器

如果用户提供了 TikTok Cookie，可以：
1. 保存到 ~/.hermes/cookies/platform_cookies.json
2. 用浏览器访问 TikTok 搜索页面
3. 但 Cookie 注入可能被浏览器安全策略阻止

### Step 4: Instagram 搜索

```python
web_search('site:instagram.com OBSBOT May 2026', limit=10)
web_search('instagram OBSBOT Tiny 3 2026', limit=10)
web_search('instagram.com/p obsbot 2026-05', limit=10)
```

### Step 5: X/Twitter 搜索

```python
web_search('site:x.com OBSBOT 2026-05-30', limit=10)
web_search('x.com OBSBOT Tiny 3 2026', limit=10)
web_search('twitter OBSBOT camera May 2026', limit=10)
```

### Step 6: 去重与筛选

1. 按 video_id / post_url 去重
2. 过滤官方账号（@obsbot, @OBSBOT_Official 等）
3. 按日期分组
4. 确认是否为 OBSBOT 产品相关（标题或描述中包含产品关键词）

### Step 7: 质检（SOP 要求）

> ⚠️ **用户明确要求**：每条符合SOP的视频都要附带质检详情，用 ☑️/☒ 标记每个检查项。

#### 视频内容质检

| 检查项 | 说明 | 标记 |
|:-------|:-----|:-----|
| 原画直出 | 视频是否展示产品实际画面 | ☑️/☒ |
| 特殊主题 | 榜单/对比/OBS教程/多机搭建/特殊场景 | 需标记 |
| 常规测评 | 产品测评/工作流展示/desk setup | 不用标记 |
| 非合作视频 | 博主自发测评，根据体量判断 | 自行判断 |
| 展会/采访 | 特殊活动视频 | 需标记 |

#### 描述区质检

| 检查项 | 说明 | 标记 |
|:-------|:-----|:-----|
| 官网链接 | obsbot.com | ☑️/☒ |
| 亚马逊链接 | amazon.com/de/co.uk 等 | ☑️/☒ |
| 渠道链接 | 经销商链接 | ☑️/☒ |
| 标签 | #obsbot 等 hashtags | ☑️/☒ |
| 折扣信息 | discount code / coupon | ☑️/☒ |

#### 排除规则

- 过滤官方账号（@obsbot、@OBSBOT_Official 等）
- 故障展示/非产品测评 → 排除
- 仅设备列表提及（非主要使用）→ 排除
- 竞品评测（可能对比OBSBOT但不是主产品）→ 排除

### Step 8: 生成报告

报告格式（腾讯文档 smartcanvas）：

```markdown
# OBSBOT 上线资源报告

日期范围：YYYY年MM月DD日 - MM月DD日

---

## 搜索覆盖范围

### 产品关键词（10个）
1. OBSBOT Tail Air
2. OBSBOT Tail 2
...

### 平台覆盖
- YouTube
- TikTok
- Instagram
- X/Twitter

---

## MM月DD日（周X）

### 全平台搜索结果

#### YouTube（N条）

**1. 视频标题**
- 博主：频道名
- 链接：https://www.youtube.com/watch?v=VIDEO_ID
- 产品：产品名
- 类型：Dedicated Video / Integration Video / Shorts

#### TikTok（N条）
...

#### Instagram（N条）
...

#### X/Twitter（N条）
...

---

### 符合 SOP 要求的视频

**1. 视频标题**
- 博主：频道名
- 链接：https://www.youtube.com/watch?v=VIDEO_ID
- 产品：产品名
- 类型：Dedicated Video
- 视频内容质检：
  - ☑️ 常规产品测评
  - ☑️ 原画直出演示
  - ☑️ 特殊主题：无
- 描述区质检：
  - ☑️ 官网链接：有
  - ☑️ 亚马逊链接：有
  - ☑️ 折扣信息：有（XXX，X% off）
  - ☑️ 标签：有（#obsbot 等）

---

## 统计汇总

| 日期 | YTB | TT | INS | X | 合计 |
|:-----|:----|:---|:----|:---|:-----|
| MM/DD | N | N | N | N | N |

---

## 产品覆盖情况

| 产品 | 状态 |
|:-----|:-----|
| OBSBOT Tail Air | ✅ 有新视频 / 无新视频 |
| OBSBOT Tail 2 | ... |
```

### Step 9: 上传腾讯文档

```bash
# 创建 smartcanvas
mcporter call tencent-docs create_smartcanvas_by_mdx --args '{"title": "OBSBOT上线资源报告_YYYY-MM-DD", "mdx": "报告内容..."}'

# 移动到 OBSBOT 文件夹
mcporter call tencent-docs manage.move_file --args '{"file_id": "FILE_ID", "target_folder_id": "DjbGtzenXmbX"}'
```

## 格式规范（用户明确要求，违反任何一条都是质量事故）

1. **链接格式**：纯文本 URL，不用 Markdown 超链接 `[链接](URL)`。用户 2026-06-01 纠正，原话："链接不要用超链接"
2. **视频标题**：每条视频单独一行展示，格式为 `**1. 视频标题**`。用户 2026-06-01 纠正，原话："所有的视频要单列一条：视频标题"
3. **质检标记**：☑️ 表示通过，☒ 表示未通过/无
4. **过滤官方**：排除 @obsbot、@OBSBOT_Official 等官方账号。用户 2026-06-01 纠正，原话："过滤掉关于OBSBOT官方的内容"
5. **搜索覆盖**：必须搜索全部 10 个产品关键词，不能只搜部分。用户 2026-06-01 纠正，原话："这些关键词都要去检索，不是只检索tiny3和tiny2"
6. **交叉验证**：用多个工具交叉验证视频，确保不遗漏。用户 2026-06-01 纠正，原话："你需要用多个工具去交叉验证视频"
7. **去重逻辑**：上午呈现的内容下午不要重复呈现，只呈现新内容
8. **文件命名**：`YYYY-MM-DD——视频上线监测——上午` 或 `YYYY-MM-DD——视频上线监测——下午`

## 质检标准（SOP 要求）

### 视频内容质检

每条符合 SOP 的视频必须检查：

| 检查项 | 说明 | 标记 |
|:-------|:-----|:-----|
| 原画直出 | 视频是否展示产品实际画面 | ☑️/☒ |
| 特殊主题 | 榜单/对比/OBS教程/多机搭建/特殊场景（播客/体育/直播）| 需标记 |
| 常规测评 | 产品测评/工作流展示/desk setup/小工具推荐 | 不用标记 |
| 非合作视频 | 博主自发测评，根据体量/价值判断 | 自行判断 |
| 展会/采访 | 特殊活动视频 | 需标记 |

### 描述区质检

| 检查项 | 说明 | 标记 |
|:-------|:-----|:-----|
| 官网链接 | obsbot.com | ☑️/☒ |
| 亚马逊链接 | amazon.com/de/co.uk 等 | ☑️/☒ |
| 渠道链接 | 经销商链接（如 pqs.com.tw） | ☑️/☒ |
| 标签 | #obsbot 等 hashtags（1-2个也算符合） | ☑️/☒ |
| 折扣信息 | discount code / coupon | ☑️/☒ |

> 有些博主喜欢用短链，不确定链接是否正确可以直接点开查看。
> 有些博主喜欢用1-2个标签，例如只选择#obsbot；#obsbot_tiny3lite，这些也属于符合视频信息完善。

## TikTok 抓取方法（2026-06-01 验证可用）

Profile 页面有 CAPTCHA 滑块阻断，但以下方法可用：

### 方法1: oembed API + 代理（推荐）
```bash
curl -s --max-time 8 -x http://127.0.0.1:1082 "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@USER/video/VIDEO_ID"
```
返回：author_name, title, thumbnail_url 等

### 方法2: 搜索页面 Scrapling
```python
page = StealthyFetcher.fetch('https://www.tiktok.com/search?q=OBSBOT', proxy='http://127.0.0.1:1082', ...)
video_links = page.css('a[href*="/video/"]::attr(href)').getall()
```

### 方法3: 视频 ID 解码时间
```python
import datetime
timestamp = int(video_id) >> 32
date = datetime.datetime.fromtimestamp(timestamp).date()
```
用于判断视频是否为当天发布。

### 方法4: Cookie 认证（用户提供的 Cookie）
Cookie 保存在 `references/cookies.md` 中，可用于 Scrapling 或 Playwright 带 Cookie 访问。

## 已知限制

1. **YouTube API 配额**：每天 100 次搜索，配额用完后用浏览器搜索
2. **TikTok 搜索延迟**：web_search 索引有 1-3 天延迟，新发布的视频不会立即被收录。必须用 oembed API + 已知账号列表 + Cookie 认证 多策略交叉验证
3. **TikTok CAPTCHA**：Profile 页面有滑块验证，浏览器自动化无法绕过
4. **Instagram/X**：无法直接爬取，用 web_search 间接获取
5. **VPN 稳定性**：长任务中 VPN 可能断开，需定期检查
6. **Cookie 有效期**：TikTok Cookie 约 1-2 周过期，需用户定期更新

## 定时任务（用户 2026-06-02 要求）

- **上午任务**：工作日 10:00 执行
- **下午任务**：工作日 18:00 执行，只呈现下午新发布的内容（与上午去重）
- **周一特殊处理**：搜索范围覆盖周五、周六、周日三天
- **周二至周五**：正常搜索当天
- **去重逻辑**：下午任务读取上午已发布的视频ID列表，排除后只输出新增

## 常见陷阱（2026-06-01 教训）

1. **不能只搜热门产品**：用户明确要求搜索全部 10 个产品关键词，遗漏任何一个都是质量事故
2. **TikTok 视频必须用多策略**：仅靠 web_search 会漏掉最近 1-3 天的视频
3. **链接格式**：腾讯文档 smartcanvas 中用纯文本 URL，不用 `[链接](URL)` 超链接格式
4. **视频标题单列**：每条视频必须单独一行展示标题，不要合并到表格中
5. **质检必须带标记**：每条符合 SOP 的视频都要 ☑️/☒ 逐项标记，不能省略
6. **YouTube API 配额**：每天 100 次搜索，10 个关键词 × 多轮 = 很容易用完。配额用完后用浏览器搜索或等待次日重置
7. **用户愤怒信号**："做啊"、"继续做"、"立刻马上" = 停止解释，直接执行。不要再问确认问题

## 输出位置

- 腾讯文档：云盘 → OBSBOT 文件夹
- 文件夹 ID：DjbGtzenXmbX

## 示例调用

```
用户：帮我做一下5月30日到6月1日的OBSBOT上线资源检测

Agent：
1. 检查 VPN 状态
2. 搜索 YouTube（10个产品关键词 × 3天）
3. 搜索 TikTok（web_search + oembed）
4. 搜索 Instagram（web_search）
5. 搜索 X/Twitter（web_search）
6. 去重筛选，过滤官方账号
7. 质检（视频内容 + 描述区）
8. 生成报告上传腾讯文档
9. 返回文档链接
```
