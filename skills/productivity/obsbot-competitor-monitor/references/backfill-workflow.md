# 竞品投放数据回填工作流（→ Google Sheets 总表）

**触发**：用户说「把 X 号到今天的竞品写入到表格」「回填数据」等。

**目标**：把每日监测报告里**已收录**的视频，按总表格式整理成可直接粘贴（或 API 写入）的数据。

---

## 步骤

### Step 1 从 seen 库取收录记录

```python
import json
seen = json.load(open(f'{BASE}/seen_videos.json'))
targets = {k: v for k, v in seen.items()
           if v.get('status') == 'included' and v.get('first_seen') in (日期列表, )}
```

⚠️ **first_seen 格式不统一**：早期记录经格式化为 `2026-09-23`，`report_builder.py` 写入的是 `DATE_CN[:10]` = **中文格式** `2026年9月24日`。查询时两种都要匹配。

### Step 2 用 videos.list 取详情（不受 search 配额限制）

```python
# 50 个 ID/批，1 配额单位/批
GET https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id=<id1,id2,...>&key=***
```
- 走代理 `http://127.0.0.1:1082`
- ISO8601 duration 需正则转秒：`PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?`
- 个别视频可能查不到（已删除/私享）→ 从历史备份 `details_*_prev.json` 兜底
- **曝光量 = `statistics.viewCount`（必抓）**、点赞 = `likeCount`、评论 = `commentCount`

### Step 2b 取频道订阅数（判量级用）

```
GET https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id=<ch1,ch2,...>&key=<API_KEY>
```
- 50 个 ID/批；走代理 `http://127.0.0.1:1082`
- 订阅数取 `statistics.subscriberCount`；若 `hiddenSubscriberCount=true` 需人工判定
- 脚本：`~/obsbot_monitor/backfill_subs.py`

### Step 3 竞品名映射（对齐表格）

### Step 3 竞品名映射（对齐表格）

先按标题/频道正则匹配（顺序敏感，**具体在前**）：`yolocam s7` → `yolocam s3` → `c960` → `venusliv` → `astra` → `link 2 pro` → `link 2c` → `insta360 wave` → `c60e` → `s600l` → `smartcam s600` → `smartcam s800` → `pixy wireless` → `pixy` → `kiyo` → `lyra` → `facecam` → `ugreen` → 最后 `logitech|brio|c920|c922` → `Logitech Series`。

⚠️ **约 15% 的条目标题不含品牌名**（品牌词只出现在描述里，如「I Got a New 4K Webcam」「The Webcam Upgrade I Didn't Know I Needed」）→ 需**从 `desc_start` 或原始报告配置人工补映射**，不要留空或瞎猜。

**命名要点**：
- Logitech 全部型号 → `Logitech Series`
- `EMEET C60E` → `EMEET SmartCam C60E 4K`（表内实际用名）
- `Insta360 Link 2C` → `Insta360 Link 2&2c`
- `Razer Kiyo V2 Pro` → `Razer Kiyo&Kiyo V2`

### Step 4 计算派生字段

| 字段 | 公式 | 格式 |
|------|------|------|
| **量级** | 按频道订阅数 | <1000 `素人` / 1000-13000 `KOC` / >13000 `KOL` |
| **Content Type** | 官方标准判定，**去掉 YTB 前缀** | `Shorts`/`Dedicated`/`Comparison`/`Tutorials`/`Round-up`/`Integration` |
| 点赞率 | 点赞 / 曝光 | 1 位小数 + `%` |
| 评论率 | 评论 / 曝光 | 1 位小数 + `%` |
| 互动率 | (点赞+评论) / 曝光 | 整数 + `%` |

⚠️ 时长边界：**<180s 才是 Shorts**，182s 就是长视频。
⚠️ Content Type 填带 `YTB ` 前缀的值会因不在下拉选项内被判无效（用户明确指出过）。

### Step 5 「是否上评」判定

| 条件 | 是否上评 |
|------|---------|
| 评论数 ≤ 10 | **否** |
| 评论数 > 10 但仅夸赞 / 纯表情 / 无实质互动 | **否**（无效评论） |
| 评论数 > 10 且有实质讨论（提问/批评/问题/对比/建议） | **是** |

抓评论：`commentThreads.list`（1 单位/次，`maxResults=100`、`order=relevance`、`textFormat=plainText`）
脚本：`~/obsbot_monitor/backfill_comments.py`

### Step 6 去重（必做）

```python
# 导出表格 CSV 后正则提取已有 video ID
re.search(r'[?&]v=([\w-]+)|/shorts/([\w-]+)|youtu\.be/([\w-]+)', link)
```
剔除与表格重复的条目。实测 65 条中有 5 条已被团队手工填入。

### Step 7 生成 TSV（列对齐 15 列）

```
Date | 竞品 | 网红ID | 视频链接 | 量级 | Content Type | 是否上评 | 曝光量 | 点赞量 | 点赞率 | 评论数 | 评论率 | 互动率 | Title | Comment
```
- **仅 `Comment` 列留空**，其余全部填写
- `csv.writer(f, delimiter='\t')`，UTF-8；另存一份 UTF-8-BOM 的 CSV 供 Excel
- 输出到 `~/Downloads/竞品投放数据_回填_<范围>.tsv`

### Step 8 交付

**方式 A（当前）**：交付本地 TSV，告知用户用 **「仅粘贴值」`Cmd+Shift+V`** 从第一个空行 A 列粘贴 —— 保留目标列下拉验证与字体格式。

**方式 B（待 Google 凭证）**：Sheets API `values.append` + `copyPaste` 复制上一行格式以保留下拉验证。

---

## 陷阱清单

1. **Content Type 前缀**：判定用官方标准 `YTB xxx`，但表内取值**无前缀**。
2. **Logitech 一律 `Logitech Series`**：Brio 4K / C920 / C922 / MX Brio 全部归入。
3. **seen 库 first_seen 两种格式**：`2026-09-23` 与 `2026年9月24日`。
4. **表内已有数据**：团队会手工录入（实测已有 1502 个视频 ID），不去重就会重复。
5. **Date 取视频实际发布日期**（`publishedAt` → `9.28`），不是报告生成日期 —— 4 天窗口的报告横跨多个日期。
6. **量级必须填**（2026-09-28 追加要求），按订阅数判定，不要凭播放量/主观感觉。
7. **曝光量必须抓**（2026-09-28 追加要求），= `statistics.viewCount`。
8. **写入需 Google OAuth**：目前未配置（缺 `google_token.json` + `google_client_secret.json`），只能出本地文件让用户粘贴。
9. **时长 180s 是硬边界**：182s 的教程视频算长视频（Tutorials），不是 Shorts。
