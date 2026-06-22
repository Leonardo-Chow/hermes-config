---
name: obsbot-competitor-monitor
description: |
  OBSBOT竞品YouTube上线监测。搜索20款核心竞品在YouTube的上线视频，抓取数据，分析评论区，生成Word报告上传腾讯文档。
  定时任务：周一/三/五自动执行。
  输出格式：Word文档（不要Excel）。
  参考模板：/Users/zhoulong/Downloads/2026-06-12——视频上线监测——上午.docx
user-invocable: true
---

# OBSBOT 竞品上线监测

## ⚠️ 关键执行原则

1. **第一步必须检测日期** — 用 `date` 命令获取今天的实际日期和星期几，不要假设
2. **连续执行，不要停顿** — 搜索→统计→过滤→生成→上传，全程自动，不要中途汇报等确认
3. **日期必须准确** — 根据今天实际日期计算搜索范围，不要假设
4. **API key 不要写在脚本里** — 会被系统截断，用浏览器搜索或直接 curl
5. **时区说明** — YouTube API 返回的是 **UTC 时间**，用户在东八区（UTC+8）。搜索和筛选时以 UTC 时间为准，不需要转换时区。

## ⚠️ 搜索关键词漏检教训（2026-06-05）

**问题**：视频 "EMEET PIXY Wireless: Complete OBS Settings for Live Streaming & Recording" 被漏检
**原因**：搜索词 "EMEET Pixy webcam" 未覆盖此视频，因为标题不含 "webcam"，只含 "OBS"、"Live Streaming"
**解决方案**：每个品牌必须搜索多个关键词变体

| 品牌 | 必须搜索的关键词变体 |
|------|---------------------|
| Logitech Brio 4K | Logitech Brio 4K webcam, Logitech Brio webcam, Logitech Brio review |
| Insta360 Link 2 | Insta360 Link 2 webcam, Insta360 Link 2 4K, Insta360 Link 2c, Insta360 Link 2 Pro |
| Insta360 Wave | Insta360 Wave webcam |
| Elgato Facecam 4K | Elgato Facecam 4K, Elgato Facecam review |
| Elgato Facecam mk2 | Elgato Facecam mk2 |
| Emeet Pixy | Emeet Pixy webcam, EMEET Pixy review, EMEET Pixy PTZ |
| EMEET SmartCam S600 | EMEET S600 webcam, EMEET SmartCam S600 |
| EMEET SmartCam S800 | EMEET S800 webcam, EMEET SmartCam S800 |
| EMEET PIXY Wireless | EMEET PIXY Wireless, EMEET PIXY OBS, EMEET PIXY streaming |
| EMEET S600L | EMEET S600L webcam |
| EMEET SmartCam C960 Ultra | EMEET SmartCam C960 Ultra, EMEET 960C, EMEET C960 |
| Yolocam S3 | Yolocam S3 webcam, YoloLiv YoloCam S3 review |
| Yolocam S7 | Yolocam S7 webcam, YoloLiv YoloCam S7 |
| Hollyland VenusLiv Air | Hollyland VenusLiv Air, Hollyland VenusLiv webcam |
| Hollyland Lyra 4K | Hollyland Lyra 4K webcam, Hollyland Lyra webcam |
| Hollyland Astra P1 | Hollyland Astra P1, Hollyland Astra P1 review, Hollyland Astra P1 PTZ |
| Razer Kiyo | Razer Kiyo webcam, Razer Kiyo V2 webcam, Razer Kiyo review |
| UGREEN 4K Webcam | UGREEN 4K webcam, UGREEN webcam review |
**核心原则**：标题可能不含 "webcam"，但含 "streaming"、"OBS"、"PTZ"、"review"、"camera" 等变体。每个品牌至少 2-3 个变体查询。

## 日期计算规则（严格执行）

| 执行日 | 搜索范围 | 说明 |
|--------|---------|------|
| 周一 | 上周六 ~ 本周一 | 3天 |
| 周三 | 周二 ~ 周三 | 2天 |
| 周五 | 周四 ~ 周五 | 2天 |
| 周四（手动触发） | 周三 ~ 周四 | 2天 |
| 其他日期（手动触发） | 前一天 ~ 当天 | 2天 |

**⚠️ 时区处理**：
- YouTube API 返回的 `publishedAt` 是 UTC 时间（如 `2026-06-03T15:00:00Z`）
- 用户在 UTC+8（北京时间），但搜索筛选时以 UTC 日期为准
- 浏览器显示的 "X小时前"、"1天前" 是基于用户本地时区（UTC+8）的相对时间
- **不需要手动转换时区**，直接用 UTC 日期即可

**计算方法**：
```bash
# 获取今天日期和星期几（本地时间）
TODAY=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%u)  # 1=周一, 2=周二, ..., 7=周日
DAY_NAME=$(date +%A)

echo "今天是: $TODAY ($DAY_NAME, 星期$DAY_OF_WEEK)"

# 根据星期几计算搜索范围（UTC 日期）
case $DAY_OF_WEEK in
    1)  # 周一
        START_DATE=$(date -v-2d -u +%Y-%m-%d)  # 周六 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        ;;
    3)  # 周三
        START_DATE=$(date -v-1d -u +%Y-%m-%d)  # 周二 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        ;;
    5)  # 周五
        START_DATE=$(date -v-1d -u +%Y-%m-%d)  # 周四 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        ;;
    4)  # 周四（手动触发）
        START_DATE=$(date -v-1d -u +%Y-%m-%d)  # 周三 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        ;;
    *)  # 其他日期
        START_DATE=$(date -v-1d -u +%Y-%m-%d)
        END_DATE=$(date -u +%Y-%m-%d)
        ;;
esac

echo "搜索范围: $START_DATE ~ $END_DATE (UTC)"
```

## 核心竞品清单（19款）

⚠️ 每个品牌必须用**多个搜索词**覆盖，避免漏检。标题不含"webcam"的视频也可能相关（如"OBS Settings"、"Live Streaming"、"Review"）。
⚠️ **必须覆盖多语言**：英语、日语、葡萄牙语、西班牙语、法语、德语等。

| 品牌 | 搜索关键词（必须全部搜索） |
|------|-----------|
| Logitech Brio 4K | Logitech Brio 4K webcam, Logitech Brio webcam, Logitech Brio review, Logitech Brio レビュー |
| Elgato Facecam 4K | Elgato Facecam 4K, Elgato Facecam 4K review, Elgato Facecam 4K streaming |
| Elgato Facecam mk2 | Elgato Facecam mk2, Elgato Facecam mk2 review |
| Emeet Pixy | Emeet Pixy webcam, EMEET Pixy review, EMEET Pixy PTZ, EMEET Pixy レビュー |
| EMEET SmartCam S600 | EMEET S600 webcam, EMEET SmartCam S600 review |
| EMEET SmartCam S800 | EMEET S800 webcam, EMEET SmartCam S800 review |
| EMEET PIXY Wireless | EMEET PIXY Wireless, EMEET PIXY Wireless OBS, EMEET PIXY Wireless streaming, EMEET PIXY Wireless review, EMEET PIXY Wireless レビュー, EMEET PIXY Wireless resenha |
| EMEET S600L | EMEET S600L webcam, EMEET S600L review, EMEET S600L 4K, EMEET S600L レビュー |
| EMEET SmartCam C960 Ultra | EMEET SmartCam C960 Ultra, EMEET 960C, EMEET C960, EMEET 960C review, EMEET C960 Ultra |
| Yolocam S3 | Yolocam S3 webcam, YoloLiv YoloCam S3 review, Yolocam S3 streaming, Yolocam S3 レビュー |
| Yolocam S7 | Yolocam S7 webcam, YoloLiv YoloCam S7 review, Yolocam S7 streaming |
| Hollyland VenusLiv Air | Hollyland VenusLiv Air, Hollyland VenusLiv Air review, Hollyland VenusLiv Air streaming |
| Hollyland Lyra 4K | Hollyland Lyra 4K webcam, Hollyland Lyra 4K review |
| Hollyland Astra P1 | Hollyland Astra P1, Hollyland Astra P1 review, Hollyland Astra P1 PTZ |
| Razer Kiyo | Razer Kiyo webcam, Razer Kiyo V2 webcam, Razer Kiyo review, Razer Kiyo V2 review |
| UGREEN 4K Webcam | UGREEN 4K webcam, UGREEN webcam review, UGREEN webcam レビュー, UGREEN webcam resenha |
| Insta360 Link 2 | Insta360 Link 2 webcam, Insta360 Link 2 review, Insta360 Link 2 streaming, Insta360 Link 2c |
| Insta360 Wave | Insta360 Wave webcam, Insta360 Wave speaker |
| Insta360 Link 2 Pro | Insta360 Link 2 Pro webcam, Insta360 Link 2 Pro review, Insta360 Link 2 Pro vs, Insta360 Link 2 Pro unboxing |
| EMEET SmartCam C60E 4K | EMEET C60E, EMEET C60E webcam, EMEET C60E review, EMEET SmartCam C60E |
| EMEET SmartCam C60E 4K | EMEET C60E, EMEET C60E webcam, EMEET C60E review, EMEET SmartCam C60E |

## 过滤规则（必须严格执行）

### 过滤1：官方账号排除
- ❌ 排除竞品官方频道发布的视频（如 `Hollyland FAQ`、`Insta360`、`YoloLiv Tech` 等官号）
- 判断方法：频道名包含品牌名 + "FAQ"/"Official"/"Tech"/"Tutorials" 等后缀
- ⚠️ **Insta360India** 是官方频道 → 排除（2026-06-18 纠正）

### 过滤2：非 webcam 内容排除
- 标题必须与 webcam 直接相关，排除以下：
  - ❌ 运动相机、全景相机、无人机（如 Insta360 X5、Insta360 Luna、Insta360 Ace Pro）
  - ❌ 麦克风、采集卡、NAS、Hub 等非摄像头产品
  - ❌ 纯品牌选购指南（如「Insta360 全系列選購指南」）
  - ❌ 游戏直播内容（如 FORZA HORIZON 6 + webcam 组合，但无产品测评）
  - ❌ **YoloBox Extreme**（直播切换器）≠ Yolocam S3/S7（摄像头）→ 产品类型不同，排除（2026-06-18 纠正）
- ✅ 保留：标题包含 webcam/facecam/camera + streaming/review/unboxing/comparison 等关键词

### 过滤3：游戏直播排除
- ❌ 排除纯游戏直播内容，没有讲解 webcam 产品
- 判断：标题含游戏名（FORZA、VALORANT、COD 等）且无 webcam 测评内容

### 过滤3b：非评测内容排除（2026-06-22 新增）
- ❌ **Studio Tour** → 排除（设备展示非摄像头评测）
- ❌ **How-to/Tutorial** → 排除（连接教程、设置教程等非评测内容）
- ❌ **Livestream without webcam review** → 排除（纯直播无摄像头产品讲解）
- ❌ **Spam/Irrelevant** → 排除（标题与摄像头完全无关的内容）

### 过滤4：低质量视频排除
- 播放量 < 50 **且** 时长 < 1分钟 → 直接过滤
- ⚠️ 巴西创作者常见模式：15-30秒 "直播" 片段，播放量 20-30（见 Pitfall 21）
- ⚠️ **标题拼写错误 + 播放量 0** → 疑似垃圾内容，直接过滤（2026-06-18 纠正）

### 过滤5：Roundup/合集视频过滤（2026-06-18 新增）
- ❌ **小频道的 Top N 合集视频** → 排除（如 "Top 5 Best Webcams 2026" by 小频道）
- ✅ **大频道的 Top N 合集视频** → 保留（如 Think Media、Linus Tech Tips 等知名频道）
- 判断标准：
  - 播放量 ≥ 1000 的 Roundup 视频 → 保留
  - 播放量 < 1000 的 Roundup 视频 → 排除
  - 知名频道（订阅 ≥ 100K）的 Roundup 视频 → 保留，无论播放量
- ⚠️ Roundup 视频的 Content Type 标记为 "Roundup"

### 过滤6：赞助视频识别
- 如果视频页面显示「包含付费宣传内容」（Contains paid promotion）标签，在 Content Type 后加 "/Sponsored"
- 检测方法：`document.querySelector('a[href*="paid_promotion"]')` 或页面上出现 `包含付费宣传内容` 文字
- 赞助视频的评论区可信度较低，但不影响是否上评判断

### 过滤7：是否上评判断
- 仅在以下情况标记"是"：
  - 评论区明确提到 obsbot/meet/tiny/tail 等关键词
  - 视频 hashtags 包含 obsbot 相关标签（如 `#streamwithobsbot`）
  - 整体舆论明显负面（差评集中）
- ⚠️ 注意：用户取消 OBSBOT 订单转选竞品 = 负面信号，需标记上评

### 过滤8：标题提到 OBSBOT 但不是竞品专门评测（2026-06-22 新增）
- ❌ 标题提到 OBSBOT 产品（如 "OBSBOT Tiny 3 Lite vs Insta360 Link 2 Pro"）但视频不是专门讲竞品 → 排除
- ❌ 标题提到 OBSBOT 产品（如 "This is the SMALLEST Webcam: OBSBOT Tiny 3"）但视频是讲 OBSBOT 而非竞品 → 排除
- ✅ 标题提到 OBSBOT 但视频是竞品评测（如 "Is Insta360 Link 2 Pro Better Than OBSBOT?"）→ 保留
- 判断标准：视频主要讲的是竞品还是 OBSBOT？如果 OBSBOT 只是对比对象，保留；如果 OBSBOT 是主角，排除

### 用户纠正案例（2026-06-03）
- 「裝備魔 JBTVHK」的「Insta360 全系列選購指南」→ ❌ 排除（不是专门讲 webcam）
- 「FORZA HORIZON 6 E WEBCAM EMEET PIXY 4K」→ ❌ 排除（纯游戏内容）
- 「Hollyland FAQ」频道的所有视频 → ❌ 排除（官方账号）

### 用户纠正案例（2026-06-18）
- TechTrends「15 Smartest Innovations」→ ❌ 排除（小频道 Roundup，播放量 < 1000）
- best picks today「Best Webcam for Content Creators」→ ❌ 排除（小频道 Roundup）
- Tech Techify「Top 5 Best 4K Webcams 2026」→ ❌ 排除（小频道 Roundup）
- WeShootFilms「Yolobox Extreme」→ ❌ 排除（YoloBox ≠ Yolocam，产品类型不同）
- PhotoJoseph「YoloBox Extreme」→ ❌ 排除（YoloBox ≠ Yolocam）
- Kay Tomas「Razer Kiyo wettings」→ ❌ 排除（标题拼写错误 + 播放量 0）
- Immortals TRYN「Razer Kiyo combo」→ ❌ 排除（越南语，非目标市场）

### 用户纠正案例（2026-06-22）
- Santiago Santiago「NEW Apartment Studio Tour 2026」→ ❌ 排除（Studio Tour 非摄像头评测）
- Sean Simz Tech「How to connect Logitech Brio 100 to PC」→ ❌ 排除（How-to 教程非评测）
- WeShootFilms「WeShootFilms is live!」→ ❌ 排除（纯直播无摄像头评测内容）
- Atius Dade Studio「Hollyland Venusliv Air - Crippling Software」→ ❌ 排除（垃圾内容）
- Charmain Hilliard「Razer Kiyo Pro Webcam」→ ❌ 排除（0播放，垃圾内容）

## 输出格式（2026-06-12 更新）

### 输出格式：Word 文档（必须，不要 Excel）

⚠️ **用户明确要求：不要用 Excel 生成，只用 Word**（2026-06-18 纠正）

**参考模板**：`/Users/zhoulong/Downloads/2026-06-12——视频上线监测——上午.docx`
下载文件夹中有格式参考文档，首次执行时应读取学习格式。

报告结构：

```
竞品视频上线监测（标题，居中，Heading 0）

日期：YYYY年M月D日（周X）
搜索范围：M月D日（周X）~ M月D日（周X）

全平台搜索结果（Heading 1）

YouTube（N条）（加粗）
1. 视频标题
博主：频道名
链接：URL
竞品：品牌名
类型：Review / Unboxing / Roundup / VS / Tutorials
发布时间：YYYY-MM-DD
播放量：N | 点赞：N | 评论：N | 互动率：N%

2. ...

TikTok（0条）（加粗）
今日无新帖。

Instagram（0条）（加粗）
今日无新帖。

X/Twitter（0条）（加粗）
今日无新帖。

统计汇总（Heading 1）

[平台数量表格]
| 平台 | 数量 |
| YouTube | N |
| TikTok | 0 |
| Instagram | 0 |
| 合计 | N |

竞品覆盖情况（加粗）
| 竞品 | 状态 |
| 品牌A | ✅ 有新视频（N条） |
| 品牌B | 无新视频 |
...

过滤说明（加粗）
| 过滤项 | 原因 |
|--------|------|
| 视频标题 | 过滤原因 |
...
```

**Word 生成代码模板**（python-docx）：
```python
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
style = doc.styles['Normal']
style.font.name = '微软雅黑'
style.font.size = Pt(10)

# 标题
title = doc.add_heading('竞品视频上线监测', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 日期信息
doc.add_paragraph('日期：YYYY年M月D日（周X）')
doc.add_paragraph('搜索范围：M月D日（周X）~ M月D日（周X）')

# 全平台搜索结果
doc.add_paragraph('')
p = doc.add_paragraph('全平台搜索结果')
for run in p.runs:
    run.bold = True
    run.font.size = Pt(12)

# YouTube 部分 - 每个视频一段
doc.add_paragraph('')
p = doc.add_paragraph(f'YouTube（{count}条）')
for run in p.runs:
    run.bold = True

for item in videos:
    doc.add_paragraph(f'{idx}. {item["Title"]}')
    doc.add_paragraph(f'博主：{item["网红ID"]}')
    doc.add_paragraph(f'链接：{item["视频链接"]}')
    doc.add_paragraph(f'竞品：{item["竞品"]}')
    doc.add_paragraph(f'类型：{item["Content Type"]}')
    doc.add_paragraph(f'发布时间：{item["Date"]}')
    doc.add_paragraph(f'播放量：{item["曝光量"]:,} | 点赞：{item["点赞量"]:,} | 评论：{item["评论数"]:,} | 互动率：{item["互动率"]}%')
    doc.add_paragraph('')

# 统计汇总表格
table = doc.add_table(rows=N, cols=2)
table.style = 'Table Grid'
```

### 文件命名规则

`{当天日期}——视频上线监测——上午/下午`

示例：`2026-06-12——视频上线监测——上午`

### 保存位置

腾讯文档：云盘 → OBSBOT → 竞品监测
文件夹 ID：`DnNkcnCRIHGt`

### 关键质量要求

1. **必须覆盖全平台**：YouTube、TikTok、Instagram、X/Twitter
2. **每个视频必须有质检**：视频内容质检 + 描述区质检
3. **必须有统计汇总**：产品覆盖情况表 + 过滤说明表
4. **必须说明过滤原因**：哪些内容被过滤了，为什么
5. **链接必须真实有效**：不能用占位符

## 数据字段

| 字段 | 说明 |
|------|------|
| Date | 发布日期（YYYY-MM-DD） |
| 竞品 | 品牌名 |
| 网红ID | 频道名 |
| 视频链接 | YouTube URL |
| 量级 | KOL/KOC/素人（按播放量：≥10k=KOL，≥1k=KOL，≥100=KOC，<100=素人） |
| Content Type | Review/VS/Shorts/Tutorials/Unboxing/Roundup/Livestream/Sponsored |
| 是否上评 | 是/空（仅评论提到obsbot或舆论差时=是） |
| 曝光量 | 播放量 |
| 点赞量 | 点赞数 |
| 点赞率 | 点赞/播放 % |
| 评论数 | 评论数 |
| 评论率 | 评论/播放 % |
| 互动率 | (点赞+评论)/播放 % |
| Title | 视频标题 |
| Comment | 评论区分析（OBSBOT提及、舆论导向） |

## 执行流程

### Step 0: 确定日期范围 + VPN 检查（第一步必须执行）

**⚠️ 先检查 VPN 连接状态**（Shadowrocket 长任务会断开）：
```bash
# 检查 VPN 状态，断开则重连
VPN_STATUS=$(scutil --nc status "Shadowrocket" 2>&1 | head -1)
if [ "$VPN_STATUS" != "Connected" ]; then
    echo "VPN 断开，正在重连..."
    scutil --nc start "Shadowrocket"
    sleep 3
fi
# 验证代理可用
curl -s --connect-timeout 5 --proxy http://127.0.0.1:1082 "https://www.youtube.com" -o /dev/null -w "%{http_code}"
```

```bash
# 获取今天是周几
DAY_OF_WEEK=$(date +%u)  # 1=Mon, 7=Sun
TODAY=$(date +%Y-%m-%d)
DAY_NAME=$(date +%A)
START_DISPLAY=$(date -v-2d +%m.%d)  # 用于文件名（零填充）
END_DISPLAY=$(date +%m.%d)

echo "今天是: $TODAY ($DAY_NAME)"

# 计算搜索范围（UTC 日期，用于 yt-dlp 上传日期过滤）
case $DAY_OF_WEEK in
    1)  # 周一
        START_DATE=$(date -v-2d -u +%Y-%m-%d)  # 周六 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        START_DISPLAY=$(date -v-2d +%m.%d)
        ;;
    3)  # 周三
        START_DATE=$(date -v-1d -u +%Y-%m-%d)  # 周二 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        START_DISPLAY=$(date -v-1d +%m.%d)
        ;;
    5)  # 周五
        START_DATE=$(date -v-1d -u +%Y-%m-%d)  # 周四 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        START_DISPLAY=$(date -v-1d +%m.%d)
        ;;
    *)  # 其他日期（手动触发）
        START_DATE=$(date -v-1d -u +%Y-%m-%d)
        END_DATE=$(date -u +%Y-%m-%d)
        START_DISPLAY=$(date -v-1d +%m.%d)
        ;;
esac

echo "搜索范围(UTC): $START_DATE ~ $END_DATE"
echo "文件名: ${TODAY}——竞品检测报告——时间范围（${START_DISPLAY}-${END_DISPLAY}）"
```

### Step 1: 搜索竞品视频

**推荐搜索策略（优先级排序）**：
1. **YouTube Data API**（最快最准，需有效 API Key）
2. **yt-dlp `ytsearch`**（无需 API Key，按相关性排序，需后过滤日期）
3. **浏览器搜索**（最可靠但最慢，可能触发 bot 检测）
4. **Exa MCP**（补充搜索，日期索引有延迟）

**🎯 最佳组合策略（2026-06-08 验证，2026-06-22 更新）**：
1. **Phase 1**：yt-dlp `ytsearch8` 搜索全部品牌（~60秒，300+个视频），用 ThreadPoolExecutor 并行获取详情（~160秒）→ 过滤日期范围。**预期命中率**：2天窗口约 0.4%（1-2个视频），3天窗口约 1-2%。⚠️ **风险**：批量并行详情获取可能触发 YouTube 全局 bot 检测（Pitfall 27），导致全部失败。
2. **Phase 2**：如果 Phase 1 结果为空、过少、**或详情获取因 bot 检测全部失败**，用浏览器搜索（`sp=EgIIAw%3D%3D` 日期排序）补充 → 3 个 subagent 各搜索 6-7 个品牌（~540秒）。**预期命中率**：2天窗口约 7-10 个视频，3天窗口约 6-15 个视频。
3. **Phase 3**：对补充搜索到的视频用浏览器获取详情（yt-dlp 可能仍被封锁）。每个 subagent 处理 7 个视频（~200秒）。

这种组合策略比纯浏览器搜索快 3x，比纯 yt-dlp 不会漏掉低播放量的新视频。

> 📖 **完整混合搜索流程 + 代码模板**：详见 `references/hybrid-search-strategy.md`

#### 方式 A: yt-dlp 搜索（推荐，无需 API Key）

⚠️ **前提**：确保 VPN 代理可用（见 Step 0）

```bash
# 搜索单个品牌（返回 JSON 格式）
export https_proxy=http://127.0.0.1:1082
yt-dlp --flat-playlist --no-warnings \
  --print '{"title":"%(title)s","channel":"%(channel)s","views":"%(view_count)s","id":"%(id)s","duration":"%(duration)s"}' \
  "ytsearch10:BRAND+QUERY"

# 批量搜索所有品牌（用 execute_code）
# 搜索结果按相关性排序，需后续用 upload_date 过滤
```

⚠️ **yt-dlp 搜索结果按相关性排序**，不是按日期。需要用 Step 2 获取 `upload_date` 后过滤日期范围。

#### 方式 B: 浏览器搜索

```
对每个品牌执行：
1. browser_navigate 到 YouTube 搜索页：
   https://www.youtube.com/results?search_query=BRAND+QUERY&sp=EgIIAw%3D%3D
   （sp=EgIIAw%3D%3D = 按上传日期排序）

2. browser_console 提取视频数据：
   const vidList = [];
   document.querySelectorAll('ytd-video-renderer').forEach((el, i) => {
       if (i < 15) {
           const titleEl = el.querySelector('#video-title');
           const channelEl = el.querySelector('#channel-name a');
           const metaSpans = el.querySelectorAll('#metadata-line span');
           let views = '', date = '';
           metaSpans.forEach(s => {
               const t = s.textContent.trim();
               if (t.includes('次观看') || t.includes('views')) views = t;
               if (t.includes('前') || t.includes('ago')) date = t;
           });
           if (titleEl) {
               vidList.push({
                   title: titleEl.textContent.trim().substring(0, 80),
                   channel: channelEl?.textContent.trim() || '',
                   views: views,
                   date: date,
                   videoId: titleEl.href?.split('v=')[1]?.split('&')[0] || ''
               });
           }
       }
   });
   JSON.stringify(vidList, null, 2);

3. 从搜索结果中筛选日期范围内的视频
   - "X小时前" = 今天（可信）
   - "1天前" = 可能是昨天或前天，**必须验证实际日期**（见 Pitfall 20）
   - "2天前" = 基本确定超出 2 天范围，可排除
   - "X天前" = 需要计算是否在范围内
   - ⚠️ **关键**：浏览器相对日期不可靠，必须通过 description 中的绝对日期或 yt-dlp 验证
```

### Step 2: 获取视频详情

**方式 A: yt-dlp（推荐，无需 API Key）**
```bash
# 获取单个视频详情
export https_proxy=http://127.0.0.1:1082
yt-dlp --no-warnings --no-download \
  --print '%(id)s|||%(upload_date)s|||%(view_count)s|||%(like_count)s|||%(comment_count)s|||%(duration)s|||%(channel)s|||%(title)s' \
  'https://www.youtube.com/watch?v=VIDEO_ID'

# ⚠️ 注意：每个视频约 5-10 秒。批量处理时：
# - execute_code 超时 300 秒，最多处理 ~50 个视频
# - 超过 50 个视频需分批或用 YouTube Data API
# - upload_date 格式：YYYYMMDD（如 20260604）
```

**方式 B: YouTube Data API（批量，需有效 Key）**
```bash
# 批量获取 50 个视频详情（1 单位配额）
curl -s --proxy http://127.0.0.1:1082 \
  "https://www.googleapis.com/youtube/v3/videos?part=statistics,contentDetails,snippet&id=ID1,ID2,...&key=API_KEY"
```

**方式 C: 浏览器（最慢，适合少量视频，yt-dlp 失败时的唯一选择）**

⚠️ **何时使用**：当 yt-dlp 报 `Requested format is not available`（新视频 <48h）或 bot 检测错误时，必须用浏览器获取详情。用 `delegate_task` 批量处理，每个 subagent 最多 7 个视频。

对每个视频，用 browser_navigate 访问视频页面，browser_console 提取：
```javascript
const title = document.querySelector('h1.ytd-watch-metadata yt-formatted-string')?.textContent?.trim();
const channel = document.querySelector('#channel-name a')?.textContent?.trim();
const views = document.querySelector('#info-container span:first-child')?.textContent?.trim();
const likes = document.querySelector('like-button-view-model button')?.getAttribute('aria-label') || document.querySelector('#top-level-buttons-computed button:first-child')?.textContent?.trim();
const date = document.querySelector('#info-container span:nth-child(3)')?.textContent?.trim();
const duration = document.querySelector('.ytp-time-duration')?.textContent?.trim();
// 以下字段用于过滤6（赞助视频）和过滤7（OBSBOT提及）判定
const paidPromotion = !!document.querySelector('a[href*="paid_promotion"]');
const hashtags = Array.from(document.querySelectorAll('a[href*="hashtag"]')).map(el => el.textContent.trim().toLowerCase()).join(',');
const actualDate = (document.querySelector('#description-inner')?.textContent?.match(/(\d{4})年(\d{1,2})月(\d{1,2})日/) || []).slice(1,4).join('-') || 'unknown';
const description = document.querySelector('#description-inner')?.textContent?.trim().substring(0, 500);
```

⚠️ **注意**：YouTube 页面结构可能变化。如果上述选择器失效，用 `document.querySelectorAll('[class*="ytd-watch"]')` 探索可用元素。

### Step 3: 过滤
- 删除播放量<50且时长<1分钟的视频
- 解析时长：从搜索结果的 heading 文本中提取（如 "8分钟12秒钟"）

### Step 4: 评论区分析
对高互动视频（播放≥500 且 评论≥3），用浏览器提取评论：

**4a. 先检查视频 hashtags（在视频描述区）：**
```javascript
// 检查 hashtags 是否包含 obsbot 相关标签
const hashtags = [];
document.querySelectorAll('a[href*="hashtag"]').forEach(el => {
    hashtags.push(el.textContent.trim().toLowerCase());
});
const obsbotHashtags = hashtags.filter(h => h.includes('obsbot') || h.includes('meet') || h.includes('tiny'));
```

**4b. 再检查评论区：**
```javascript
const comments = [];
document.querySelectorAll('ytd-comment-thread-renderer').forEach((el, i) => {
    if (i < 30) {
        const author = el.querySelector('#author-text')?.textContent?.trim() || '';
        const text = el.querySelector('#content-text')?.textContent?.trim() || '';
        if (text) comments.push({ author, text: text.substring(0, 300) });
    }
});

// OBSBOT 关键词匹配
const obsbotKeywords = ['obsbot', 'meet 2', 'meet se', 'tiny 2', 'tiny 3', 'tail 2', 'tail air'];
const obsbotMentions = comments.filter(c => {
    const lower = c.text.toLowerCase();
    return obsbotKeywords.some(kw => lower.includes(kw));
});
```

**4c. 负面信号识别：**
- 用户说"cancelled the order"（取消订单）转选竞品 → 负面
- 用户说"returned"/"sent back"/"refund" → 负面
- 用户说"overheating"/"broke"/"defective" → 负面
- 用户说"better alternative"/"switched to" → 负面

**4d. 结果记录到 Comment 字段：**
- 有 OBSBOT 提及：记录具体评论内容 + 正面/负面判断
- 无 OBSBOT 提及：留空或写"无"

### Step 5: 生成 Word 文档（不要用 Excel）
```python
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 按日期+品牌排序
# 结构：标题 → 日期信息 → 全平台搜索结果（YouTube/TikTok/Instagram/X）→ 统计汇总（表格）
# 参考模板：/Users/zhoulong/Downloads/2026-06-12——视频上线监测——上午.docx
```

### Step 6: 上传腾讯文档
```bash
# 上传 Word 文档（不要用 Excel）
cd ~/.hermes/skills/tencent-docs && bash import_file.sh /path/to/report.docx

# 触发导入
mcporter call "tencent-docs" "manage.async_import" --args '{...}'

# 等待 5 秒后搜索文件
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key": "TITLE"}'

# 移动到目标文件夹
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id": "ID", "target_folder_id": "DnNkcnCRIHGt"}'
```

⚠️ **import_file.sh 成功后的验证**：当 `import_file.sh` + `manage.async_import` 均成功时，**不需要用 `sheet.get_range_value` 逐单元格验证数据**。xlsx 文件已作为整体导入，数据完整。只需用 `manage.search_file` 确认文件存在 + `manage.move_file` 移动到目标文件夹即可。不要尝试用 `sheet.get_cell_value` 或 `sheet.get_range_value` 读取单元格——这些工具在 mcporter 中可能未注册（-32601 错误）。

## 上传腾讯文档（替代方案）

> 📖 **完整上传工作流 + mcporter 工具参考**：详见 `references/tencent-docs-sheet-upload.md`

当 `import_file.sh` 上传 xlsx 文件失败（"upload_failed - curl 上传文件失败"）时，使用以下替代方案：

```bash
# 1. 创建新 Sheet
mcporter call "tencent-docs" "manage.create_file" --args '{"title": "2026-06-05——竞品检测报告——时间范围（6.4-6.5）", "file_type": "sheet"}'
# 获取 file_id

# 2. 移动到目标文件夹
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id": "FILE_ID", "target_folder_id": "DnNkcnCRIHGt"}'

# 3. 获取 sheet_id
mcporter call "tencent-docs" "sheet.get_sheet_info" --args '{"file_id": "FILE_ID"}'

# 4. 用 set_range_value 批量写入数据（比逐个 set_cell_value 快 10x）
mcporter call "tencent-docs" "sheet.set_range_value" --args '{"file_id": "FILE_ID", "sheet_id": "SHEET_ID", "values": [["Date", "竞品", ...], ["2026-06-05", "Logitech", ...]]}'
```

⚠️ **注意**：
- `import_file.sh` 可能需要代理（`export https_proxy=http://127.0.0.1:1082`）
- `mcporter` 有时直连成功，有时需要代理，先尝试直连
- `sheet.set_cell_value` 逐个调用会超时（>300s），必须用 `sheet.set_range_value` 批量写入
- 数据格式：所有值都是字符串类型，数字也要用 `"1356"` 而非 `1356`

## 文件命名规则

`{当天日期}——竞品检测报告——时间范围（{起始日期}-{结束日期}）`

⚠️ 日期范围使用 `date +%m.%d` 格式（零填充）：
- ✅ `2026-06-08——竞品检测报告——时间范围（06.06-06.08）`
- ❌ `2026-06-08——竞品检测报告——时间范围（6.6-6.8）`

## 保存位置

腾讯文档：云盘 → OBSBOT → 竞品监测
文件夹 ID：`DnNkcnCRIHGt`

## 参考模板

Word 文档格式参考：`/Users/zhoulong/Downloads/2026-06-12——视频上线监测——上午.docx`
首次执行时应读取学习格式结构。

## 评论区深度分析（YouTube API）

当需要对指定视频列表进行深度评论爬取+分析（而非仅检查 OBSBOT 提及）时，使用 YouTube Data API `commentThreads.list` 端点。

**详细流程**：`references/youtube-comment-scraping.md`，包含：
- API 分页逻辑
- SOCKS5 代理配置（环境变量方式更可靠）
- 评论情感过滤（精准甄别真实吐槽 vs 误判）
- 用户关心点分类（13 类）+ 应用场景分类（11 类）
- Word 文档生成模板（python-docx 样式表格）
- 配额估算

**⚠️ 关键 Pitfall**：YouTube 视频评论中真实吐槽极少（<1%）。音乐/演出类视频的评论几乎全部与产品无关。必须用强负面词 + 排除模式双重过滤，不能用宽泛关键词匹配。

## 已知陷阱

> 📖 **OBSBOT 提及模式库**：详见 `references/obsbot-mention-patterns.md`，包含 hashtags 检查方法、评论区关键词列表、负面信号识别等。

### Pitfall 1: API Key 截断
YouTube API key (`AIzaSy...aA1Q`) 在 shell heredoc/变量中会被系统截断为 `***`。
**解决方案**：
- **方式 A**：用浏览器搜索方式，不要在脚本中写 API key
- **方式 B**：将 API key 存入 `~/.config/youtube/api_key` 文件，脚本中用 `$(cat ~/.config/youtube/api_key)` 读取
- **方式 C**：直接用 `curl` 命令行调用（不经过 Python heredoc）

### Pitfall 1b: YouTube API 直连可用，代理反而失败（2026-06-09 验证）
YouTube Data API 在中国大陆可以**直连访问**（`unset https_proxy http_proxy`），不需要代理。
- ✅ 直连：`curl -s "https://www.googleapis.com/youtube/v3/..."` — 成功
- ❌ 代理：`curl -s --proxy http://127.0.0.1:1082 "https://www.googleapis.com/youtube/v3/..."` — 返回 503 或超时

但 **YouTube 网页版**（browser_navigate）需要代理才能访问。API 和网页版的网络路径不同。

### Pitfall 1c: 视频链接必须是真实 URL，不能用占位符（2026-06-09 用户纠正）
**用户反馈**："视频链接有问题，点不开是怎么回事"
**原因**：脚本中使用了 `REPLACE_ME_1` 等占位符，没有替换为真实的 YouTube 视频 ID。
**解决方案**：
- 从浏览器搜索结果中提取的 `videoId` 必须直接用于构建 URL：`https://www.youtube.com/watch?v={videoId}`
- 生成 Excel 前必须验证所有 URL 格式正确（包含 11 位 video ID）
- 不要先写占位符再替换，直接用真实数据构建

### Pitfall 2: 代理不稳定
- `import_file.sh` 有时需要代理，有时不需要
- `mcporter` 调用也类似
- **策略**：先尝试直连，失败后加代理重试

### Pitfall 3: 日期判断
- 搜索结果中的 "X小时前"、"X天前" 需要根据当前时间推算
- 不要只看 "最新" 标签，要看具体时间

### Pitfall 4: 不要中途停顿（最高优先级）
用户明确要求连续执行（2026-06-03 多次强调）：
- "开始啊，不要等我的指令！！说了很多次了"
- "继续，不要停"
- "不要一步一停，自己继续执行走"

正确做法：搜索→统计→过滤→生成→上传→最终汇报，全程自动。
错误做法：每完成一步就汇报等待确认、生成中间结果后询问是否继续、做一半就停下来。

### Pitfall 5: mcporter 代理切换
mcporter 有时直连成功，有时需要代理。如果遇到 HTTP 405 或连接超时：
1. 先尝试不加代理
2. 失败后 `export https_proxy=http://127.0.0.1:1082` 再试
3. 两种都失败则等待几秒后重试
4. 详细工具参考：`references/tencent-docs-sheet-upload.md`

### Pitfall 6: 内容相关性判断不精确
用户纠正（2026-06-03）：仅提到品牌但与 webcam 无关的视频必须排除。
- 「Insta360 全系列選購指南」→ ❌ 排除
- 「Insta360 Mic Pro Review」→ ❌ 排除（麦克风不是 webcam）
- 「FORZA HORIZON 6 E WEBCAM EMEET PIXY 4K」→ ❌ 排除（纯游戏）
- 「Insta360 Link 2 Pro Review」→ ✅ 保留

### Pitfall 7: 评论区分析必须检查 hashtags
用户纠正（2026-06-03）：视频 hashtags 可能包含 `#streamwithobsbot` 等标签，即使评论区没有提到 OBSBOT，hashtags 中有也算提及。检查顺序：先 hashtags → 再评论区。

### Pitfall 8: COS 上传失败的降级方案
`import_file.sh` 的 COS 上传可能失败（`ERROR:upload_failed - curl 上传文件失败`），尤其在网络不稳定时。
**降级方案**：直接创建腾讯文档 smartsheet 并写入数据（详见 `references/tencent-docs-sheet-upload.md`）

### Pitfall 9: VPN (Shadowrocket) 长任务自动断开
Shadowrocket VPN 在长时间执行（>5分钟）时会自动断开。
**修复**：`scutil --nc start "Shadowrocket"` + `sleep 3`
**预防**：在每个主要步骤前检查代理可用性。

⚠️ **execute_code 沙箱中的 VPN 断开**：当 yt-dlp 搜索阶段（~75秒）完成后，进入详情获取阶段时 VPN 可能已断开。症状：所有 yt-dlp 调用返回 `Unable to connect to proxy`。此时必须在 terminal 中重连 VPN，然后重新执行详情获取脚本。

⚠️ **VPN 状态检测不可靠**：`scutil --nc status "Shadowrocket"` 可能返回中间状态（如 "Disconnecting"）。**可靠方法**：直接用 curl 测试代理连通性：
```bash
curl -s --connect-timeout 5 --proxy http://127.0.0.1:1082 "https://www.youtube.com" -o /dev/null -w "%{http_code}"
# 返回 200 = 连接正常，其他 = 需要重连
```
不要依赖 `scutil` 的状态文本判断。

⚠️ **execute_code 内不需要 import openai**：yt-dlp 搜索和 curl 调用只用 `subprocess`、`json`、`datetime`、`concurrent.futures`。不要导入未使用的模块。

### Pitfall 10: yt-dlp 逐个获取详情超时
yt-dlp `--print` 逐个获取视频元数据约 5-10 秒/个。192 个视频需 ~30 分钟，会超过 `execute_code` 的 300 秒超时。
**解决方案**：先用 yt-dlp 搜索获取列表，再用 YouTube Data API 批量获取详情。

### Pitfall 11: Exa 搜索日期索引延迟
Exa MCP 的日期索引对非常新的内容（<48小时）有延迟。作为补充搜索源，不作为唯一搜索源。

### Pitfall 12: yt-dlp 并行获取详情（ThreadPoolExecutor）
yt-dlp 逐个获取视频详情约 5-10 秒/个，242 个视频串行需要 20+ 分钟。使用 `ThreadPoolExecutor(max_workers=8)` 并行处理可在 ~80 秒内完成全部 242 个视频。
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(get_video_date, vid_id): vid_id for vid_id in video_ids}
    for future in as_completed(futures):
        result = future.result()
```
⚠️ **注意**：并行度不要超过 8，否则可能触发 YouTube 限流。每次调用需重新设置 `https_proxy` 环境变量。

### Pitfall 13: 浏览器搜索 subagent 品牌数量控制
用 delegate_task 做浏览器搜索时，受 `max_concurrent_children=3` 限制，最多同时运行 3 个 subagent。
- ✅ 推荐：3 个 subagent，各搜索 8 个品牌（24 品牌全覆盖，~220-325秒完成）
- ⚠️ 可行：2 个 subagent，各搜索 9 个品牌（但并发利用率低）
- ❌ 避免：4+ 个 subagent（超过 max_concurrent_children 限制会报错）
- ❌ 避免：1 个 subagent 搜索全部 18+ 个品牌（会超时 600 秒）

每次搜索 ~30-40 秒，8 个品牌 ~240-320 秒，在 600 秒超时内安全完成。

### Pitfall 14: Excel 生成必须用 terminal 而非 execute_code
`openpyxl` 在 execute_code 的沙箱环境中不可用（`ModuleNotFoundError`）。必须：
1. 用 `write_file` 写 Python 脚本到 `/tmp/gen_report.py`
2. 用 `terminal` 执行 `python3 /tmp/gen_report.py`

### Pitfall 15: 文件名日期格式一致性
文件名中的日期范围必须使用一致的格式：`{MM.DD}-{MM.DD}`（零填充）。
- ✅ `2026-06-08——竞品检测报告——时间范围（06.06-06.08）`
- ❌ `2026-06-08——竞品检测报告——时间范围（6.6-6.8）`
计算时用 `date +%m.%d` 而非手动拼接。

### Pitfall 17: yt-dlp 对新视频报 "Requested format is not available"（2026-06-12 验证）
yt-dlp 对最近上传（<48小时）的视频可能报 `Requested format is not available` 错误，即使使用 `--skip-download` 和 `--cookies-from-browser chrome`。这与 Pitfall 1（bot 检测）不同——是格式解析问题。

**触发条件**：视频上传不足 48 小时，YouTube 尚未完成所有格式的转码。
**症状**：
- `yt-dlp --skip-download --print ...` → `ERROR: Requested format is not available`
- `yt-dlp --dump-json` → 同样错误
- 不加 `--cookies-from-browser` 会先报 bot 检测错误

**解决方案**：用浏览器获取视频详情（见 Step 2 方式 C）。
```javascript
// 在视频页面的 browser_console 中执行
JSON.stringify({
  title: document.querySelector('h1.ytd-watch-metadata yt-formatted-string')?.textContent?.trim(),
  channel: document.querySelector('#channel-name a')?.textContent?.trim(),
  views: document.querySelector('#info-container span:first-child')?.textContent?.trim(),
  likes: document.querySelector('like-button-view-model button')?.getAttribute('aria-label'),
  date: document.querySelector('#info-container span:nth-child(3)')?.textContent?.trim(),
  duration: document.querySelector('.ytp-time-duration')?.textContent?.trim(),
  // ⚠️ 关键：从 description 提取实际发布日期（比相对日期可靠）
  actualDate: (document.querySelector('#description-inner')?.textContent?.match(/(\d{4})年(\d{1,2})月(\d{1,2})日/) || []).slice(1,4).join('-') || 'unknown',
  paidPromotion: !!document.querySelector('a[href*="paid_promotion"]'),
  hashtags: Array.from(document.querySelectorAll('a[href*="hashtag"]')).map(el => el.textContent.trim().toLowerCase()).join(','),
  description: document.querySelector('#description-inner')?.textContent?.trim().substring(0, 500)
});
```

⚠️ 用 `delegate_task` 批量获取详情时，每个 subagent 最多处理 **7 个视频**（每次 ~30 秒），避免超时。

⚠️ **如果 delegate_task 返回 HTTP 429（模型 API 限流）**：不要重试子代理，改用直接浏览器操作（browser_navigate + browser_console 逐个访问），每个视频 ~10 秒。见 Pitfall 22。

### Pitfall 19: yt-dlp `--skip-unavailable-formats` 不存在（2026-06-15 验证）
yt-dlp **没有** `--skip-unavailable-formats` 选项。如果在 yt-dlp 命令中添加此参数，所有调用都会失败：
```
yt-dlp: error: no such option: --skip-unavailable-formats
```
**症状**：333 个视频全部返回 `status=failed`，error 包含 "no such option"。
**解决方案**：不要使用此参数。正确的 yt-dlp 详情获取命令为：
```bash
yt-dlp --no-warnings --no-download \
  --print '%(id)s|||%(upload_date)s|||%(view_count)s|||%(like_count)s|||%(comment_count)s|||%(duration)s|||%(channel)s|||%(title)s' \
  'https://www.youtube.com/watch?v=VIDEO_ID'
```
⚠️ 不要添加任何额外的格式相关参数（如 `--skip-unavailable-formats`、`-f best` 等），`--print` 模式不需要选择格式。

### Pitfall 20: 浏览器相对日期不可靠，必须验证实际日期（2026-06-15 验证，2026-06-17 强化）
浏览器显示的 "X小时前"、"X天前" 是基于用户本地时区（UTC+8）的相对时间，**不能直接用于日期过滤**。

**实测案例（2026-06-17）**：
- 浏览器显示 "1天前"（今天 6月17日 UTC+8）→ 以为是 6月16日
- 实际页面 description 显示 "2026年6月15日" → 超出搜索范围！
- 原因：视频在 6月15日 UTC+8 晚间上传，从 6月17日看确实是"1天多前"

**可靠验证方法**（按优先级）：
1. **浏览器 description 中的绝对日期**：`document.querySelector('#description-inner')` 通常包含 "YYYY年M月D日" 格式的发布日期
2. **yt-dlp `upload_date`**：UTC 日期，最准确（但新视频 <48h 可能报错）
3. **浏览器相对时间**：仅用于初筛（"X小时前"=今天，其他都需要验证）

**关键规则**：
- ⚠️ "1天前" 可能是昨天也可能是前天，必须验证
- ⚠️ "2天前" 基本确定超出 2 天搜索范围，可直接排除
- ⚠️ "X小时前" 基本确定是今天，可保留
- **从 description 提取日期的 JS**：
```javascript
const desc = document.querySelector('#description-inner')?.textContent || '';
const dateMatch = desc.match(/(\d{4})年(\d{1,2})月(\d{1,2})日/);
const actualDate = dateMatch ? `${dateMatch[1]}-${dateMatch[2].padStart(2,'0')}-${dateMatch[3].padStart(2,'0')}` : 'unknown';
```

### Pitfall 18: execute_code 沙箱中 yt-dlp 和代理均不可用（2026-06-12 验证）
在 `execute_code` 沙箱中，`subprocess` 调用 yt-dlp 即使设置了 `https_proxy` 环境变量也会返回 0 结果。原因：
1. 沙箱可能没有 yt-dlp 二进制文件
2. 沙箱的网络环境不走系统代理

**症状**：`execute_code` 中 yt-dlp 搜索/详情获取返回 0 个结果，但同样的命令在 `terminal` 中正常工作。

**解决方案**：
- Phase 1 搜索：用 `execute_code`（yt-dlp 搜索确实能在 execute_code 中工作——2026-06-08 验证）
- Phase 1 详情获取：**必须用 `terminal`**（写 Python 脚本到 `/tmp/`，用 `terminal` 执行）
- Phase 2 浏览器搜索：用 `delegate_task` + browser tools
- Phase 2 详情获取：用 `delegate_task` + browser tools（当 yt-dlp 失败时）

⚠️ 如果 Phase 1 的详情获取在 `execute_code` 中返回 0 结果，不要反复重试——立即切换到 `terminal` 执行。

### Pitfall 21: 巴西创作者超短视频模式（2026-06-17 发现）
巴西 YouTube 创作者（尤其是 EMEET/Hollyland 相关搜索）经常发布**超短直播/短视频**（15-30秒），播放量 20-30 次。

**典型特征**：
- 时长 15-30 秒（远低于 1 分钟）
- 播放量 20-30（低于 50）
- 频道名为葡萄牙语（如 "Peterson Camilo"、"Oppa Lec"）
- 标题含品牌名但无实质内容
- 通常标记为 "直播时间：X小时前"

**处理**：按过滤规则4（播放<50 且 时长<1分钟）直接排除。不需要逐个访问确认。

### Pitfall 22: delegate_task 子代理 HTTP 429 限流（2026-06-17 验证）
当模型 API 触发速率限制时，所有 delegate_task 子代理都会返回 "HTTP 429: Too many requests"。

**症状**：
- 3 个子代理全部在 50-60 秒内失败
- 每个子代理只完成了 6-11 次 API 调用就终止
- 错误信息：`API call failed after 3 retries: HTTP 429: Too many requests`

**解决方案**：
1. **不要重试 delegate_task** — 如果 3 个子代理都 429，重试也会 429
2. **改用直接浏览器操作** — 用 browser_navigate + browser_console 逐个访问视频页面
3. **批量处理策略** — 每个视频页面 ~10 秒，10 个视频 ~100 秒，在单个会话内完成
4. **降级到最少数据** — 如果时间紧迫，只获取标题、频道、播放量、日期即可，跳过评论分析

### Pitfall 24: 浏览器子代理获取视频详情会超时，用 yt-dlp 替代（2026-06-18 验证）
用 `delegate_task` + browser tools 批量获取视频详情（views/likes/comments/duration）时，子代理容易超时（600秒限制，44次API调用后仍未完成）。

**症状**：子代理执行 600 秒后 timeout，返回 `Subagent timed out after 600.0s`

**原因**：每个视频需要 browser_navigate + browser_console + 多次 browser_scroll，单个视频 ~30-60 秒，8 个视频 ~240-480 秒，加上 API 延迟容易超时。

**解决方案**：用 yt-dlp 在 terminal 中批量获取详情，每个视频 ~5 秒，8 个视频 ~40 秒：
```python
import subprocess, json, os
os.environ['https_proxy'] = 'http://127.0.0.1:1082'

for vid in video_ids:
    r = subprocess.run(
        ['yt-dlp', '--no-warnings', '--no-download',
         '--print', '%(id)s|||%(view_count)s|||%(like_count)s|||%(comment_count)s|||%(duration)s|||%(channel)s|||%(title)s',
         f'https://www.youtube.com/watch?v={vid}'],
        capture_output=True, text=True, timeout=30
    )
    # 解析 r.stdout
```

⚠️ **注意**：yt-dlp 对 <48小时的新视频可能报 "Requested format is not available"（见 Pitfall 17），此时必须用浏览器。但对于大多数视频，yt-dlp 是更快更可靠的方案。

**最佳策略**：
1. 先用 yt-dlp 批量获取所有视频详情（~40秒）
2. 对 yt-dlp 失败的视频（新视频 <48h），再用浏览器单独获取

### Pitfall 25: YoloBox Extreme ≠ Yolocam S3/S7（2026-06-18 纠正）
**问题**：搜索 "Yolocam S3/S7" 时，YouTube 返回大量关于 "YoloBox Extreme" 的视频。
**原因**：YoloBox 和 Yolocam 都是 YoloLiv 品牌，但产品类型完全不同：
- **YoloBox Extreme** = 直播切换器（live streaming switcher）
- **Yolocam S3/S7** = 摄像头（webcam）

**解决方案**：
- 搜索结果中标题包含 "YoloBox" 但不含 "Yolocam" → 排除
- 标题同时包含 "YoloBox" 和 "Yolocam" → 保留（可能是对比视频）
- 标题只包含 "Yolocam" → 保留

**判断代码**：
```python
title_lower = title.lower()
if 'yolobox' in title_lower and 'yolocam' not in title_lower:
    return False  # 排除
```

### Pitfall 27: yt-dlp 批量并行请求触发 YouTube 全局 bot 检测（2026-06-22 验证）

**问题**：yt-dlp 在批量并行请求（300+视频）时，YouTube 会检测到异常模式并**全局封锁后续所有请求**，包括单个请求也会失败。

**症状**：
- Phase 1 搜索成功获取 300+ 视频 ID（yt-dlp `ytsearch` 仍可用）
- Phase 2 详情获取阶段：所有 307 个视频全部返回 `Sign in to confirm you're not a bot`
- 单独测试单个视频（如 dQw4w9WgXcQ）用 `--dump-json` 仍可工作，但批量请求全部被拦截
- 加 `--cookies-from-browser chrome` 后变成 `No video formats found`（Pitfall 23）

**原因**：YouTube 对同一 IP 的短时间大量请求触发反爬封锁。封锁是临时的（可能持续 10-30 分钟），但在任务执行窗口内无法恢复。

**解决方案**：不要重试 yt-dlp，立即切换到浏览器搜索（Phase 2）：
1. 用 `delegate_task` 3 路并行浏览器搜索（每路 6-7 个品牌）
2. 浏览器搜索用 `sp=EgIIAw%3D%3D` 按日期排序，~540 秒完成全部 19 品牌
3. 对搜索到的视频用浏览器获取详情（而非 yt-dlp）

**与 Pitfall 23 的区别**：
- Pitfall 23：bot 检测 → 加 cookies → 格式错误（单个视频的连锁反应）
- Pitfall 27：批量并行 → 全局封锁 → 所有后续请求失败（整个会话级影响）

**预防**：如果 Phase 1 搜索阶段完成后发现详情获取全部失败，不要尝试 `--dump-json`、加 cookies、减少并行度等重试——直接跳到浏览器方案。

### Pitfall 26: 小频道 Roundup 视频过滤（2026-06-18 新增）
**问题**：小频道（播放量低）的 "Top 5/10 Best Webcams" 合集视频，竞品只是列表中的一个，不是专门讲该竞品。
**用户反馈**：这类视频不被视为 "竞品投放"，不应纳入报告。

**解决方案**：
- 播放量 < 1000 的 Roundup/Top N 视频 → 排除
- 播放量 ≥ 1000 的 Roundup 视频 → 保留
- 知名频道（订阅 ≥ 100K）的 Roundup 视频 → 保留

**判断代码**：
```python
title_lower = title.lower()
is_roundup = any(kw in title_lower for kw in ['top 5', 'top 10', 'top n', 'best of', 'roundup'])
if is_roundup and views < 1000:
    return False  # 排除小频道 Roundup
```

### Pitfall 27: 标题提到 OBSBOT 但不是竞品评测（2026-06-22 新增）
**问题**：搜索竞品时，YouTube 返回的视频标题可能提到 OBSBOT 产品，但视频本身不是讲竞品。
**案例**：
- "OBSBOT Tiny 3 Lite vs Insta360 Link 2 Pro" by Tech4Dads → 视频主要讲 OBSBOT，不是专门讲 Insta360
- "This is the SMALLEST Webcam: OBSBOT Tiny 3" by Paula Mads → 视频讲 OBSBOT，不是讲 Insta360 Link 2 Pro
- "Webcam OBSBOT MEET SE a melhor webcam para Streaming?" by The Computer FOOL → 视频讲 OBSBOT，不是讲 EMEET S800

**解决方案**：
- 标题以 OBSBOT 产品为主角 → 排除（不是竞品评测）
- 标题以竞品为主角，OBSBOT 只是对比对象 → 保留
- 判断标准：标题中竞品品牌名出现在前面，OBSBOT 出现在后面 → 通常是竞品评测

**判断代码**：
```python
title_lower = title.lower()
obsbot_products = ['obsbot', 'tiny 2', 'tiny 3', 'meet 2', 'meet se', 'tail air', 'tail 2']
competitor_brands = ['insta360', 'elgato', 'emeet', 'logitech', 'hollyland', 'razer', 'ugreen', 'yolocam']

# 检查标题是否以 OBSBOT 产品为主角
has_obsbot = any(p in title_lower for p in obsbot_products)
has_competitor = any(b in title_lower for b in competitor_brands)

if has_obsbot and has_competitor:
    # 两者都有，判断谁是主角
    # 如果 OBSBOT 出现在标题前面，可能是 OBSBOT 评测
    obsbot_pos = min([title_lower.find(p) for p in obsbot_products if p in title_lower])
    competitor_pos = min([title_lower.find(b) for b in competitor_brands if b in title_lower])
    if obsbot_pos < competitor_pos:
        return False  # OBSBOT 是主角，排除
```

### Pitfall 23: yt-dlp bot 检测后再用 cookies 会触发格式错误（2026-06-17 验证）
当 yt-dlp 不带 cookies 报 "Sign in to confirm you're not a bot" 错误后，加上 `--cookies-from-browser chrome` 会变成 "Requested format is not available" 错误。

**原因链**：不带 cookies → bot 检测拦截 → 带 cookies → 绕过 bot 检测 → 但新视频 <48h 格式未转码 → 格式错误

**正确处理**：
1. yt-dlp 不带 cookies 报 bot 检测 → 不要加 cookies 重试
2. 直接跳到浏览器获取详情（Pitfall 17 的解决方案）
3. 对于新视频 <48h，浏览器是唯一可靠方案

### Pitfall 16: TikTok 数据源额度限制

**Omar TikTok API（omkar.cloud）每月仅 100 次免费请求，必须合理分配！**

| 用途 | 预算/月 | 说明 |
|:-----|:--------|:-----|
| OBSBOT 竞品监测 | 40 次 | 每周一/三/五，每次约 3-5 个关键视频详情 |
| KOL 资料验证 | 30 次 | 高价值 KOL 的详细资料和视频历史 |
| 应急备用 | 30 次 | 用户临时需求、特殊查询 |

**优先级规则**：
1. **🔴 必须用 Omar API**：获取视频完整数据（含 HD 下载链接）、验证 KOL 资料真实性
2. **🟡 用免费替代**：视频基本信息 → oembed API、批量搜索 → ScraperAPI

**额度管理脚本**：
```bash
# 检查额度
python3 ~/.hermes/scripts/omkar_usage.py check

# 记录使用
python3 ~/.hermes/scripts/omkar_usage.py add 3 "竞品监测"
```

**免费替代方案（优先使用）**：
```python
import subprocess, json

proxy = 'http://127.0.0.1:1082'  # Shadowrocket

# oembed API - 免费
def get_video_info_free(video_url):
    result = subprocess.run(
        ['curl', '-s', '--max-time', '8', '-x', proxy,
         f'https://www.tiktok.com/oembed?url={video_url}'],
        capture_output=True, text=True, timeout=15)
    return json.loads(result.stdout)

# 视频 ID 解码时间 - 免费
def decode_video_time(video_url):
    vid_id = video_url.split('/video/')[-1]
    ts = int(vid_id) >> 32
    return datetime.fromtimestamp(ts)
```

**Omar API 端点**：
- 用户资料：`GET /tiktok/users/profile?handle=obsbot`（消耗1次）
- 视频详情：`GET /tiktok/videos/details?video_url=...`（消耗1次）
- 视频搜索：`GET /tiktok/videos/search?search_query=...`（消耗1次）
- 热门推荐：`GET /tiktok/videos/trending`（消耗1次）

**API Key**：`YOUR_OMKAR_API_KEY`，存 `~/.config/last30days/.env`
