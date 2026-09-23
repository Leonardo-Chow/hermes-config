---
name: obsbot-daily-launch-monitor
description: |
  OBSBOT 每日上线资源检测 — 自动搜索 YouTube/TikTok/Instagram/X 四平台，
  覆盖10个产品关键词，按日期范围筛选，生成质检报告到 ~/Downloads。
version: 1.3.0
author: Leonardo
metadata:
  hermes:
    tags: [OBSBOT, YouTube, TikTok, Instagram, Twitter, monitoring, daily-report]
    related_skills: [tencent-docs, youtube-full, scrapling, noxinfluencer, platform-cookies-manager, leonardo-brand]
---

# OBSBOT 每日上线资源检测

自动搜索 OBSBOT 产品在 YouTube/TikTok/Instagram/X 四平台的上线内容，生成质检报告到 `~/Downloads`。

## 触发条件

当用户提到以下关键词时使用此 skill：
- **「开始今天的」/「开始今天的检测」/「再做一次今天的检测」/「开始啊」** —— 用户日常最常用的触发语，**不带任何其他上下文**。含义固定为：跑一次 OBSBOT 每日上线监测，产出 docx 到 `~/Downloads`。**不要反问要做什么，直接执行。**
- OBSBOT 上线资源
- OBSBOT 每日监测
- OBSBOT 视频检测
- OBSBOT 内容监控

### 日常执行路径（2026-09 起的实际做法，照此做即可）

```bash
# 1) 确认今天日期
date "+%Y-%m-%d %H:%M %Z (%A)"
# 2) 目标 = 前一天 UTC（报告文件名用今天的 CST 日期）
TARGET=$(date -v-1d "+%Y-%m-%d")
# 3) 跑现成扫描脚本（已封装全部搜索+过滤逻辑）
python3 ~/.hermes/scripts/obsbot_yt_scan.py "$TARGET"
#    周一补齐周末：python3 ~/.hermes/scripts/obsbot_yt_scan.py <周五> <周六> <周日>
# 4) 用脚本输出的「入选候选」做人工质检（AI配音/主题偏离/测试流），生成 docx
```

**日期映射铁律**：报告文件名 = 执行当天的 CST 日期；内容覆盖 **前一天 UTC 全天**（周一覆盖上周五~周日 3 天）。
例：9/18 执行 → 文件名 `2026-09-18-视频上线监测.docx` → 内容是 9/17 UTC 的视频。
不要在文件名里写 UTC 日期，用户按 CST 日期归档。

## 产品关键词（10个）

> ⚠️ **必须搜索全部 10 个关键词**，遗漏任何一个都是质量事故。用户原话：「这些关键词都要去检索，不是只检索tiny3和tiny2」

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

### Step 0: 检查日期和星期（必须第一步执行）

> ⚠️ **必须第一步执行**：确认今天的日期和星期，避免用错日期导致数据错误。

```bash
# 获取今天的日期和星期
TODAY=$(date +%Y-%m-%d)
WEEKDAY=$(date +%u)  # 1=Monday, 7=Sunday
WEEKDAY_NAME=$(date +%A)

echo "今天：$TODAY ($WEEKDAY_NAME)"
```

**日期规则**：
- 周一（WEEKDAY=1）：搜索周五、周六、周日三天
- 周二至周五（WEEKDAY=2-5）：搜索当天
- 周六日（WEEKDAY=6-7）：定时任务不执行，手动执行时搜索当天

### Step 1: 检查 VPN 状态

```bash
scutil --nc status "Shadowrocket" 2>/dev/null | head -2
```

如果断开，重新连接：
```bash
scutil --nc start "Shadowrocket" 2>&1; sleep 3
```

### Step 2: YouTube 搜索

> **配额管理**：使用 API 池轮换 + yt_optimizer.py 批量优化。
> - 配置文件：`~/.hermes/config/youtube_api_pool.json`
> - 管理脚本：`~/.hermes/scripts/youtube_api_pool.py`
> - 优化器：`~/.hermes/scripts/yt_optimizer.py`（批量请求、本地缓存、配额追踪）

#### 获取当前 API Key

```bash
API_KEY=$(python3 ~/.hermes/scripts/youtube_api_pool.py current)
```

#### 搜索所有产品关键词

> ⚠️ **时区处理**：YouTube API 返回 UTC 时间，用户在北京时间（UTC+8）。搜索时需要扩大范围以覆盖北京时间当天所有视频。
> 
> **搜索范围**：前一天 UTC 00:00 ~ 当天 UTC 15:59
> 
> 这样可以覆盖：
> - 北京时间前一天 08:00 ~ 当天 23:59
> - 捕获北京时间晚上发布的视频（UTC 时间为前一天）

```bash
DATE="2026-06-05"  # 北京时间日期

# 计算 UTC 时间范围
YESTERDAY=$(date -v-1d -j -f "%Y-%m-%d" "$DATE" +%Y-%m-%d)
UTC_START="${YESTERDAY}T00:00:00Z"  # 前一天 UTC 00:00
UTC_END="${DATE}T15:59:59Z"         # 当天 UTC 15:59

for kw in "OBSBOT" "OBSBOT+Tiny+3" "OBSBOT+Tiny+2" "OBSBOT+Tail+2" "OBSBOT+Meet+2" "OBSBOT+Talent" "OBSBOT+webcam" "OBSBOT+Tiny+3+Lite" "OBSBOT+Tiny+2+Lite" "OBSBOT+Meet+SE" "OBSBOT+Tail+Air" "OBSBOT+Tiny+SE"; do
  curl -s --max-time 12 "https://www.googleapis.com/youtube/v3/search?part=snippet&q=${kw}&type=video&publishedAfter=${UTC_START}&publishedBefore=${UTC_END}&maxResults=20&key=$API_KEY"
done
```

#### 批量获取视频详情（省 98% 配额）

```python
from yt_optimizer import batch_videos

# 批量获取 50 个视频 = 1 单位（不是 50）
videos = batch_videos(["vid1", "vid2", ..., "vid50"])
```

#### API 池轮换（配额用完时）

```bash
python3 ~/.hermes/scripts/youtube_api_pool.py rotate  # 切换到下一个 Key
python3 ~/.hermes/scripts/youtube_api_pool.py list     # 查看所有 Key
python3 ~/.hermes/scripts/youtube_api_pool.py add NEW_KEY  # 添加新 Key
```

#### 配额检查

```bash
python3 ~/.hermes/scripts/yt_optimizer.py quota  # 查看配额报告
```

### Step 3: TikTok 搜索（多策略交叉验证）

> ⚠️ **核心教训**：web_search 索引延迟 1-3 天，新发布的视频不会被收录。必须多策略交叉验证。
> 
> **2026-06-01 教训**：仅靠 web_search 漏掉了 @psscreativemedia 的视频（6月2日凌晨发布）。原因是搜索引擎索引延迟。

#### 策略1: ScrapeCreators hashtag 搜索（推荐，最可靠）

```python
import requests

API_KEY = "YOUR_SCRAPECREATORS_API_KEY"
BASE = "https://api.scrapecreators.com"

def search_tiktok_hashtag(hashtag, count=20):
    """hashtag 搜索 - 比关键词搜索更可靠"""
    resp = requests.get(
        f"{BASE}/v1/tiktok/search/hashtag",
        params={"hashtag": hashtag, "count": count},
        headers={"x-api-key": API_KEY}
    )
    return resp.json()

# 搜索 OBSBOT 相关 hashtags
for tag in ["obsbot", "obsbot_tiny3", "obsbot_tail2", "obsbot_meet2"]:
    results = search_tiktok_hashtag(tag)
    # 处理结果...
```

**已知问题**：关键词搜索返回空，hashtag 搜索更可靠。

#### 策略2: oembed API 验证已知视频（免费，无限次）

```bash
PROXY="http://127.0.0.1:1082"
curl -s --max-time 8 -x $PROXY "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@USER/video/VIDEO_ID"
```

返回：author_name, title, thumbnail_url。用于验证视频是否存在及获取标题。

#### 策略3: 视频 ID 解码时间（判断发布日期）

```python
import datetime
timestamp = int(video_id) >> 32
date = datetime.datetime.fromtimestamp(timestamp).date()
```

#### 策略4: 已知账号扫描

已知 OBSBOT TikTok 账号（定期检查最新视频）：
- @obsbot（OBSBOT Official，17.5K 粉丝）
- @obsbotmy1（obsbotmy）
- @psscreativemedia（PSS Creative Media）
- @mrsmobster（MrsMobster）
- @maccagames（MaccaGames）
- @brainiacvp（BrainiacVP）
- @obsbot.thailand
- @obsbotsingapore

#### 策略5: web_search 间接搜索（补充）

```python
web_search('site:tiktok.com OBSBOT 2026-06', limit=10)
web_search('tiktok OBSBOT Tiny 3 review 2026', limit=10)
```

注意：Tavily 有每日配额限制（keyless ~10次/天），优先用于其他平台搜索。

#### 策略6: Omar API（视频详情+HD下载链接）

```python
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
```

**额度**：100 次/月，用于高价值视频详情获取。

#### 策略7: Cookie 认证（需要用户登录态）

Cookie 保存在 `~/.hermes/cookies/platform_cookies.json`。有效期 1-2 周。

> **浏览器 Cookie 注入失败**：浏览器安全策略阻止 `document.cookie` 设置。解决方案：让用户在自己 Chrome 中登录后提取 Cookie。

### Step 4: Instagram 搜索

> ⚠️ **重要**：必须搜索所有产品关键词变体，不能只搜通用关键词。2026-06-17 漏掉了 @farmsim25builds 的帖子。

```python
# 必须搜索的关键词变体
search_queries = [
    'site:instagram.com OBSBOT June 2026',
    'site:instagram.com OBSBOT Tiny 3 2026',
    'site:instagram.com OBSBOT Tiny 2 2026',
    'site:instagram.com OBSBOT Tail 2 2026',
    'site:instagram.com OBSBOT Meet 2 2026',
    'site:instagram.com OBSBOT Meet SE 2026',
    'site:instagram.com OBSBOT Tail Air 2026',
    'site:instagram.com OBSBOT Talent 2026',
    'instagram OBSBOT webcam June 2026',
    'instagram OBSBOT camera June 2026',
    'instagram.com/p obsbot 2026-06',
    'instagram.com/reel obsbot 2026-06',
    'instagram OBSBOT code discount 2026',
    'instagram OBSBOT ambassador 2026',
    'instagram OBSBOT affiliate 2026',
    'instagram OBSBOT brand ambassador 2026',
    'instagram OBSBOT giveaway 2026',
    'instagram OBSBOT promo code 2026',
    'instagram OBSBOT social media collaboration 2026',
    'instagram OBSBOT 社媒合作 2026',
]
```

### Step 5: X/Twitter 搜索

> ⚠️ **重要**：必须搜索所有产品关键词变体，不能只搜通用关键词。2026-06-11 漏掉了 @applejackeroni 的推文。

```python
# 必须搜索的关键词变体
search_queries = [
    'site:x.com OBSBOT 2026-06-12',
    'site:x.com OBSBOT 2026-06-11',
    'site:x.com OBSBOT June 2026',
    'site:x.com OBSBOT Tiny 3 2026',
    'site:x.com OBSBOT Tiny 2 2026',
    'site:x.com OBSBOT Tail 2 2026',
    'site:x.com OBSBOT Meet 2 2026',
    'site:x.com OBSBOT Meet SE 2026',
    'site:x.com OBSBOT Tail Air 2026',
    'site:x.com OBSBOT Talent 2026',
    'twitter OBSBOT camera June 2026',
    'twitter OBSBOT webcam June 2026',
    'OBSBOT giveaway twitter June 2026',
    'OBSBOT ambassador twitter June 2026',
    'OBSBOT affiliate twitter June 2026',
    'OBSBOT brand ambassador twitter 2026',
    'OBSBOT promo code twitter 2026',
]
```

### Step 6: 日期验证与筛选（⚠️ 所有平台必须执行）

> ⚠️ **核心教训（2026-06-10）**：不能只靠搜索引擎返回的"X天前"来判断日期。必须验证每条视频的实际发布日期，超出范围的坚决排除。
> 
> 用户原话：「很多都是好几天前就上架了，注意时间我只要指定日期范围内上架的视频」

#### 平台级日期验证方法

| 平台 | 验证方法 | 精度 |
|:-----|:---------|:-----|
| YouTube | `snippet.publishedAt`（API 直接返回 ISO 日期） | 精确到秒 |
| TikTok | 视频 ID 解码：`int(video_id) >> 32` → Unix 时间戳 | 精确到秒 |
| Instagram | 搜索结果中的日期元数据，或帖子 URL 中的日期编码 | 天级 |
| X/Twitter | 搜索结果中的 `created_at` 字段 | 精确到秒 |

#### TikTok 视频 ID 解码（必须对每条视频执行）

```python
import datetime

def decode_tiktok_date(video_id):
    """从 TikTok 视频 ID 提取精确发布时间"""
    timestamp = int(video_id) >> 32
    return datetime.datetime.fromtimestamp(timestamp)

# 示例
video_id = "7513089494989898989"
dt = decode_tiktok_date(video_id)
print(f"发布时间: {dt}")  # 精确到秒
print(f"日期: {dt.date()}")
```

#### 浏览器"X天前"换算

浏览器显示"3 days ago"需要换算为实际日期：
```python
from datetime import datetime, timedelta
actual_date = datetime.now() - timedelta(days=3)
```

**判断规则**：`actual_date` 必须在搜索日期范围内，否则排除。

#### 去重与筛选流程

1. 按 video_id / post_url 去重
2. **日期验证**（必须第一步）：对每条视频验证实际发布日期，排除超出范围的
3. 过滤官方账号（@obsbot, @OBSBOT_Official 等）
4. 过滤日韩东南亚博主、<1分钟视频、纯直播
5. 按日期分组
6. 确认是否为 OBSBOT 产品相关（标题或描述中包含产品关键词）

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

- **🔴 历史去重（2026-09-20 用户明确要求）：前面报告里出现过的 video / 链接，绝不在后续报告中二次出现。**
  - 台账文件：`~/.hermes/config/obsbot_reported_videos.json`（结构 `{"videos": {"<videoId>": {"reported": "YYYY-MM-DD", ...}}}`）
  - 扫描脚本 `obsbot_yt_scan.py` **已内置**：加载台账 → 命中历史 ID 的行自动剔除，并在输出末尾单列「已排除（历史报告重复）」。
  - **每期报告生成后必须登记**：
    ```bash
    python3 ~/.hermes/scripts/obsbot_yt_scan.py --mark <vid1> <vid2> ...
    ```
  - 判据以 **video ID** 为准（同一链接）；同一标题出现在不同频道属重传，人工判断是否剔除。
  - ⚠️ 已知历史事故：Talent 2 发布期有 4 条视频在 9/15 与 9/16 两期报告中重复出现，用户因此提出此要求。
- **账号黑名单（2026-09-07/09-11/09-20 用户逐条要求，直接过滤这些账号的所有视频）**：
  `UnboxingMyBuys`、`Gadget Theory`、`Gadget Savvy`、`BrujulaDelUnboxing`、`Chia Se Thong Tin`、`CreatorFinds`、`Pickfolio`、`Su Lo`、`Ha Vu`、`SAM`
- 过滤官方账号（@obsbot、@OBSBOT_Official 等）
- 时长 > 1 小时（直播回放）→ 排除。**⚠️ 判据要查 API 字段，不能只看时长数字**（2026-09-18 修正）：`snippet.liveBroadcastContent == "none"` 且无 `liveStreamingDetails` 的即为常规长视频，**即便 1h00m32s 这种刚过线也应保留**（案例：GAMINGTREND 的 Talent 2 真人实时演示被误判）；只有确属直播回放（有 `liveStreamingDetails`）才排除。
- **< 1 分钟（Shorts）→ 排除**（2026-09-15 用户确认「保持现状」：即使某日全部 OBSBOT 内容均为 Shorts，也照常输出「暂无」，不收录）
- AI 配音视频（批量 Top5 榜单、无真人出镜、廉价感）→ 排除
- 故障展示/非产品测评 → 排除
- 仅设备列表提及（非主要使用）→ 排除
- 竞品评测（可能对比OBSBOT但不是主产品）→ 排除
- **日韩东南亚博主谨慎过滤**：日本、韩国、泰国、越南、马来西亚、菲律宾等地区博主 → 排除（内容以当地语言为主，对欧美市场参考价值低）。**但印尼/俄语博主如果是KOL自发评测/开箱/对比等有价值内容，应保留**（2026-06-17 教训：DIMAS俄语Tiny3 Lite评测被误过滤）
  - **⚠️ 实际执行口径（2026-09-11 ~ 09-18 连续 7 天日报实践校准）**：用户**从未**因为地区语言否决过条目 —— 泰语（The Digital STM）、越南语（Roo Setup）、印尼语（KAMARANA）、日语、土耳其语（Mustafa Güney）、繁体中文（WINYEDA）等真实评测/开箱均被正常收录且无异议。用户的做法是**逐号加黑名单**（7 个账号里就有一个越南语号 `Chia Se Thong Tin`），而不是按地区一刀切。
  - **因此默认策略**：只要是真的产品评测/开箱/对比（非 gear 清单提及、非 AI 配音、非测试流），**无论地区语言一律保留**；发现低质账号由用户指认后写入上方黑名单。不要把「地区」当过滤主力。
- **视频时长不到1分钟** → 排除（太短无法展示产品特性）
- **纯直播类型（没有讲解）** → 排除（只有画面没有产品介绍/评测内容）
- **视频质量差** → 排除（画质差、内容浅、制作粗糙、剪辑混乱等）
- **日期必须确认**：必须确认是当天发布的视频，昨天的不算

#### 视频质量判断标准

| 标准 | 说明 |
|:-----|:-----|
| 画质 | 至少 720p，画面清晰不模糊 |
| 内容深度 | 有实际产品展示和讲解，不是简单开箱 |
| 剪辑质量 | 剪辑流畅，不是拼凑感强 |
| 音频质量 | 声音清晰，无杂音 |
| 整体观感 | 专业感强，不是业余随意拍摄 |

#### 日期验证方法

1. **YouTube**：用 publishedAt 字段验证
2. **TikTok**：用视频 ID 解码验证（`int(video_id) >> 32`）
3. **Instagram/X**：用搜索结果中的日期信息验证

#### 日韩东南亚地区识别方法

| 标志 | 说明 |
|:-----|:-----|
| 语言 | 日语、韩语、泰语、越南语、印尼语、马来语、菲律宾语 |
| 地区标签 | #indonesia #malaysia #thailand #vietnam #japan #korea #philippines |
| 购买链接 | shopee.co.id / shopee.co.th / lazada.co.id / tokopedia.com / blibli.com |
| 频道名 | 包含当地语言字符或地区标识 |

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

### Step 9: 输出到本地（**不再上传腾讯文档**）

> **2026-09-11 用户明确要求**：视频上线监测不再上传腾讯文档，只生成 docx 到 `~/Downloads` 即可。
> 腾讯文档相关流程（smartcanvas / manage.create_file / move_file）仅历史参考，日常执行跳过。

```bash
# 生成 docx（python-docx）
python3 gen_report.py
# 输出：~/Downloads/YYYY-MM-DD-视频上线监测.docx
```

生成后确认文件存在即可，无需任何上传/移动操作。

### Step 10: 登记台账（必做，否则下期重复）

报告定稿后，把本期收录的**全部** video ID 写入去重台账：

```bash
python3 ~/.hermes/scripts/obsbot_yt_scan.py --mark <vid1> <vid2> <vid3> ...
# 输出：台账已更新：新增 N 条，总计 M 条
```

- 台账：`~/.hermes/config/obsbot_reported_videos.json`
- 下一期扫描时这些 ID 会自动被排除，并在「已排除（历史报告重复）」段落中显示。
- **忘记登记 = 下期必然重复出现**（用户已因此纠正过一次）。

### Step 11: 自检（用户要求「自检一下」时，或每周例行一次）

```bash
python3 ~/.hermes/scripts/obsbot_audit.py          # 默认 2026-09-05 ~ 昨天
python3 ~/.hermes/scripts/obsbot_audit.py 2026-07-01 2026-09-22   # 指定区间
```

检查 5 项并以退出码反映结论（0=通过）：

| # | 检查项 | 不合格含义 |
|:-:|:---|:---|
| 1 | 跨报告重复 | 同一 video ID 出现在多期报告 → 违反用户去重要求 |
| 2 | 未登记台账 | 报告里有 ID 但台账没登记 → 下期必重复 |
| 3 | 台账冗余 | 台账有 ID 但报告里找不到 → 早期清理残留 |
| 4 | UTC 日期缺口 | 某天完全没被任何报告覆盖 → 漏采 |
| 5 | 覆盖天数统计 | 参考值 |

**修复工具**：
- `obsbot_ledger_backfill.py` — 按报告文档全量回填台账（新增报告目录后重跑）
- `obsbot_ledger_repair.py` — 补登遗漏 + 修正日期标签错位
- 发现重复条目时：从**较晚**那期报告删除（较早那期为首次收录）

**历史案例（2026-09-23 自检）**：
- 发现并修复 4 条跨期重复（9/15 vs 9/16，Talent 2 发布期抢跑造成）
- 发现台账漏登 23 条 + 全量回填 311 条（7 月起的历史报告未纳管）→ 台账 90 → 401 条
- 发现 2 条 7 月重复（hkOAfFghvDs、bqiyTynGJRs）并清除

## 格式规范（用户明确要求，违反任何一条都是质量事故）

1. **链接格式**：纯文本 URL，不用 Markdown 超链接 `[链接](URL)`。用户 2026-06-01 纠正，原话："链接不要用超链接"
2. **视频标题**：每条视频单独一行展示，格式为 `**1. 视频标题**`。用户 2026-06-01 纠正，原话："所有的视频要单列一条：视频标题"
3. **质检标记**：☑️ 表示通过，☒ 表示未通过/无
4. **过滤官方**：排除 @obsbot、@OBSBOT_Official 等官方账号。用户 2026-06-01 纠正，原话："过滤掉关于OBSBOT官方的内容"
5. **搜索覆盖**：必须搜索全部 10 个产品关键词，不能只搜部分。用户 2026-06-01 纠正，原话："这些关键词都要去检索，不是只检索tiny3和tiny2"
6. **交叉验证**：用多个工具交叉验证视频，确保不遗漏。用户 2026-06-01 纠正，原话："你需要用多个工具去交叉验证视频"
7. **去重逻辑**：上午呈现的内容下午不要重复呈现，只呈现新内容
8. **文件命名**：`YYYY-MM-DD——视频上线监测——上午` 或 `YYYY-MM-DD——视频上线监测——下午`

## 视觉规范

报告上传到腾讯文档时，使用 `leonardo-brand` skill 的视觉规范：
- 链接用纯文本 URL（不用 Markdown 超链接）
- 视频标题用 `**1. 标题**` 格式单列
- 质检项用 ☑️/☒ 标记

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

## TikTok 已知限制（2026-06-02 验证）

1. **Profile 页面有 CAPTCHA 滑块**：浏览器自动化无法绕过
2. **搜索页面需要登录**：未登录时显示「登录以搜索热门内容」
3. **Cookie 注入失败**：浏览器安全策略阻止 `document.cookie` 设置
4. **oembed API 可用**：通过代理可获取单个视频详情
5. **视频 ID 解码可用**：可从 ID 提取精确发布时间
6. **web_search 索引延迟 1-3 天**：新发布的视频不会立即被收录

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

## 常见陷阱

### 格式规范（违反任何一条都是质量事故）

1. **链接格式**：纯文本 URL，不用 `[链接](URL)` 超链接。用户原话：「链接不要用超链接」
2. **视频标题单列**：每条视频单独一行 `**1. 视频标题**`，不要合并到表格。用户原话：「所有的视频要单列一条：视频标题」
3. **过滤官方**：排除 @obsbot、@OBSBOT_Official 等官方账号。用户原话：「过滤掉关于OBSBOT官方的内容」
4. **搜索覆盖**：必须搜索全部 10 个产品关键词。用户原话：「这些关键词都要去检索，不是只检索tiny3和tiny2」
5. **交叉验证**：用多个工具交叉验证视频。用户原话：「你需要用多个工具去交叉验证视频」
6. **质检必须带标记**：每条符合 SOP 的视频都要 ☑️/☒ 逐项标记

### 执行陷阱

6.4 **直接用现成扫描脚本**：`~/.hermes/scripts/obsbot_yt_scan.py` 已封装「10 关键词 × N 天搜索 → 去黑名单/官方 → publishedAt 复核 → 时长/播放量硬过滤」全流程。
   ```bash
   python3 ~/.hermes/scripts/obsbot_yt_scan.py 2026-09-14            # 单日
   python3 ~/.hermes/scripts/obsbot_yt_scan.py 2026-09-11 2026-09-12 2026-09-13   # 周一补齐周末
   ```
   输出末段「入选候选」即通过硬过滤的清单，再人工判断 AI 配音/主题偏离即可。

6.5 **API key 来源**：优先读 `~/.hermes/config/youtube_api_pool.json`（脚本已内置，逐个验活）。**不要**把 key 字面量写进 write_file 的脚本——掩码机制会吞掉字面量导致 `SyntaxError: unterminated string literal`；`/tmp` 下的临时脚本也会被系统清理，不要作为 key 来源长期依赖。

6.6 **🔴 绝不用 `publishedAfter`/`publishedBefore` 搜索**（2026-09-15 实测重大坑）：YouTube search 的日期窗口参数会**大量漏视频** —— 同一窗口下窗口法只找到 12 条，改用 `order=date` 拉最近 50 条 + 客户端按 `publishedAt` 过滤则找到 37 条（漏了 Talent 2 发布日的一批新片）。
   - **正确做法**：每个关键词只发一次 `order=date, maxResults=50`（不带日期窗口），拿到 vid 后用 `videos.list` 的 `snippet.publishedAt` 在客户端按目标日期过滤。
   - 副作用：单关键词命中数上升（15 关键词 ≈ 443 条），但 `videos.list` 批量查详情可承受。
   - 判据：标题或频道名含 `obsbot` 才算候选；**仅描述区出现**的绝大多数是 gear 清单/设备列表提及（实测 Mac669、Frohnix、Aoki TV、English Sermons 全是 gear list）→ 排除。

6.7 **`P0D` 时长会崩溃**：直播/预告的 duration 可能是 `P0D` 或不含 `PT` 前缀，`re.match(r"PT(...)")` 返回 None 抛 `AttributeError`。正则写成 `r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"` 并判空。

7. **YouTube API 配额**：使用 API 池轮换（`youtube_api_pool.py`），配额用完时 rotate
8. **TikTok 必须多策略**：仅靠 web_search 会漏掉最近 1-3 天的视频
9. **Tavily 配额限制**：keyless tier ~10 次/天，优先用于 Instagram/X 搜索
10. **delegate_task 超时**：子任务经常超时，优先用 terminal 直接执行 API 调用
11. **VPN 掉线 → YouTube API 全线不可达**（2026-09-17 实测）：`googleapis.com` 返回 000，脚本报「未找到可用 API key」——**这不是 key 失效，是链路断了**。快速判据：
    ```bash
    for h in www.baidu.com www.google.com www.googleapis.com api.github.com; do
      echo "$h -> $(curl -s -o /dev/null -w '%{http_code}' --max-time 8 https://$h)"; done
    scutil --proxy   # HTTPEnable/HTTPSEnable/SOCKSEnable 是否为 0
    ```
    baidu/github 通 + google 000 + 无系统代理 → **VPN 掉了，必须让用户手动开**（用户规则：我不操作 VPN、不切节点）。
    **降级方案**（VPN 未恢复时先交付部分结果）：Tavily MCP 走服务端，不受本地链路影响 —— `tavily_search(time_range="day")` 找线索，`tavily_extract` 抓具体 YouTube 视频页拿播放量/章节；但**无法**系统枚举关键词、拿不到可靠 publishedAt，只能算临时补丁，VPN 恢复后必须用 API 重跑。
12. **smartcanvas API 故障**：`create_smartcanvas_by_mdx` 可能返回 RPC 错误，fallback 到 doc 类型 + `doc.insert_markdown`

### 日期与时间陷阱

16. **所有平台必须日期验证**：不能只靠搜索引擎返回的"X天前"。YouTube 用 `publishedAt`，TikTok 用 ID 解码，INS/X 用搜索元数据。超出范围坚决排除。用户原话：「很多都是好几天前就上架了，注意时间我只要指定日期范围内上架的视频」
17. **YouTube API 返回 UTC**：北京时间 00:00 = UTC 前一天 16:00，必须用 UTC 范围搜索否则漏视频
18. **TikTok web_search 索引延迟 1-3 天**：新发布的视频不会被收录，必须用 oembed + ID 解码交叉验证

### 用户行为信号

19. **「做啊」「继续做」「立刻马上」** = 停止解释，直接执行
20. **「不要废话」「开始啊」** = 跳过确认，立即行动
21. **用户纠正格式/风格/日期** = 立即更新 skill，不要重复犯错

## 输出位置

- **本地：`~/Downloads/YYYY-MM-DD-视频上线监测.docx`**（当前唯一输出，2026-09-11 起）
- ~~腾讯文档：云盘 → OBSBOT → 每日监测 文件夹（已停用）~~
  - 历史参考：OBSBOT 文件夹 ID `DjbGtzenXmbX` / 每日监测 ID `DumZsGZJrwsf`

### 当前实际 docx 格式（2026-09 起，简单纯文本段落，不要用表格）

```
2026/09/18 上线情况

2026/09/17（周四 UTC / 09/18 北京时间早）

1. Talent 2-Tom Buck
https://www.youtube.com/watch?v=jHrwNtdjbXg
Can The OBSBOT Talent 2 Replace An Entire Podcast Studio?

2. Meet SE-Roo Setup
https://www.youtube.com/watch?v=mnmJt8rh7fc
Webcam OBSBOT Meet SE ...

INS
暂无

TT
暂无

X
暂无

搜索关键词
OBSBOT / OBSBOT Tiny 3 / ... / OBSBOT webcam
```

**要点**：
- 条目标题行 = `序号. 产品-频道名`（产品用 Tail 2 / Tiny 3 / Meet SE / Talent 2 这类短名；**不加** -KOL自发/-KOC自发 等后缀）
- 紧跟一行**纯文本 URL**（不要 Markdown 超链接）
- 再一行**视频原始标题**（去掉表情符号和 #hashtag 尾巴更清爽）
- 当天无合格视频就写「暂无」（**不要**为了凑数放进 Shorts）
- 末尾固定三平台 `INS / TT / X` 各写「暂无」+ 「搜索关键词」全文列出
- python-docx 生成后**必须回读校验**再汇报

### 报告交付后的汇报格式（用户偏好）

用表格列入选清单（序号/产品/频道/订阅/时长/播放）→ 过滤明细 → 「情报观察」3-5 条（大号动向、campaign 标题复用、区域分布、展会/新品节点）。用户重视情报解读，不只是罗列链接。

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
8. 生成 docx 报告到 ~/Downloads（不上传腾讯文档）
9. 返回本地文件路径
```
