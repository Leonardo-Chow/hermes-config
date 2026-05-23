---
name: youtube-scraping
description: YouTube 视频数据抓取经验总结 — 使用 YouTube Data API、yt-dlp、curl、Camoufox 提取视频详情和评论
tags: [youtube, api, scraping, data-collection, comments]
version: 2.0.0
---

# YouTube 视频数据抓取经验

## 触发条件
- 需要批量获取 YouTube 视频详情（博主、浏览量、点赞、评论等）
- 需要收集特定品牌/产品的 YouTube 视频数据
- 需要获取视频评论区内容

## ⭐ 首选方案：YouTube Data API v3（2026-05-10 重大发现）

**实战经验**：批量抓取 35 个 OBSBOT 视频，YouTube Data API 成功率 100%，远超 yt-dlp (40%)、curl (部分)、Scrapling (0%)。

### 为什么选 YouTube Data API

| 对比项 | YouTube Data API | yt-dlp | curl + regex | Camoufox |
|--------|:----------------:|:------:|:------------:|:--------:|
| 成功率 | **100%** | 40% | 部分 | 部分 |
| 速度 | **<2秒/批** | 5-30秒/个 | 2秒/个 | 10秒/个 |
| 浏览量 | ✅ | ✅ | ✅ | ✅ |
| 点赞数 | ✅ | ✅ | ✅ | ✅ |
| 评论数 | ✅ | ✅ | ❌ | ❌ |
| 评论内容 | ✅ | ❌ | ❌ | ❌ |
| 粉丝数 | ✅ | ✅ | ❌ | ❌ |
| 稳定性 | **极高** | 受VPN影响 | 高 | 中 |
| 依赖 | API Key | Python | curl | Python 3.10+ |

### 使用方法

```python
from googleapiclient.discovery import build

API_KEY = 'YOUR_API_KEY'
youtube = build('youtube', 'v3', developerKey=API_KEY)

# 1. 获取视频统计信息（批量，最多50个/次）
video_ids = ['video_id_1', 'video_id_2', ...]
request = youtube.videos().list(
    part='statistics,snippet',
    id=','.join(video_ids)
)
response = request.execute()

for item in response['items']:
    stats = item['statistics']
    snippet = item['snippet']
    print(f"标题: {snippet['title']}")
    print(f"频道: {snippet['channelTitle']}")
    print(f"频道ID: {snippet['channelId']}")
    print(f"浏览量: {stats.get('viewCount', 0)}")
    print(f"点赞: {stats.get('likeCount', 0)}")
    print(f"评论: {stats.get('commentCount', 0)}")

# 2. 获取频道粉丝数（批量，最多50个/次）
channel_ids = ['channel_id_1', 'channel_id_2', ...]
request = youtube.channels().list(
    part='statistics,snippet',
    id=','.join(channel_ids)
)
response = request.execute()

for item in response['items']:
    stats = item['statistics']
    print(f"频道: {snippet['title']}")
    print(f"粉丝: {stats.get('subscriberCount', 0)}")
    print(f"隐藏粉丝: {stats.get('hiddenSubscriberCount', False)}")

# 3. 获取视频评论（每视频最多20条）
request = youtube.commentThreads().list(
    part='snippet',
    videoId='VIDEO_ID',
    maxResults=20,
    order='relevance',  # 或 'time'
    textFormat='plainText'
)
response = request.execute()

for item in response['items']:
    snippet = item['snippet']['topLevelComment']['snippet']
    print(f"作者: {snippet['authorDisplayName']}")
    print(f"评论: {snippet['textDisplay']}")
    print(f"点赞: {snippet['likeCount']}")
    print(f"日期: {snippet['publishedAt'][:10]}")
```

### API Key 获取步骤
1. 打开 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目或选择现有项目
3. 启用 **YouTube Data API v3**
4. 创建 **API Key**
5. 复制 Key 使用

### 实战数据（35个视频）

| 指标 | 数量 | 成功率 |
|------|:----:|:------:|
| 视频统计 | 35/35 | 100% |
| 评论数 | 31/35 | 89% |
| 点赞数 | 34/35 | 97% |
| 频道粉丝 | 29/29 | 100% |
| 评论内容 | 353条 | 100% |

### 关键字段映射

**videos().list(part='statistics,snippet')** 返回：

| 字段路径 | 说明 | 类型 |
|----------|------|------|
| `snippet.title` | 视频标题 | string |
| `snippet.channelTitle` | 频道名 | string |
| `snippet.channelId` | 频道ID | string |
| `snippet.publishedAt` | 发布时间 | string |
| `statistics.viewCount` | 浏览量 | string→int |
| `statistics.likeCount` | 点赞数 | string→int |
| `statistics.commentCount` | 评论数 | string→int |

**channels().list(part='statistics,snippet')** 返回：

| 字段路径 | 说明 | 类型 |
|----------|------|------|
| `snippet.title` | 频道名 | string |
| `statistics.subscriberCount` | 粉丝数 | string→int |
| `statistics.hiddenSubscriberCount` | 是否隐藏粉丝 | bool |
| `statistics.videoCount` | 视频数 | string→int |

**commentThreads().list(part='snippet')** 返回：

| 字段路径 | 说明 | 类型 |
|----------|------|------|
| `snippet.topLevelComment.snippet.authorDisplayName` | 评论作者 | string |
| `snippet.topLevelComment.snippet.textDisplay` | 评论内容 | string |
| `snippet.topLevelComment.snippet.likeCount` | 评论点赞 | int |
| `snippet.topLevelComment.snippet.publishedAt` | 发布时间 | string |

### 批量评论抓取脚本（纯 curl，无需 googleapiclient）

当需要抓取大量视频的全部评论时，用 curl + subprocess 直接调 API，避免依赖 googleapiclient：

```python
import json, subprocess, re, time

API_KEY = "YOUR_KEY"
MAX_COMMENTS_PER_VIDEO = 200

def fetch_comments(video_id):
    comments = []
    page_token = ""
    while len(comments) < MAX_COMMENTS_PER_VIDEO:
        batch = min(100, MAX_COMMENTS_PER_VIDEO - len(comments))
        url = (f"https://www.googleapis.com/youtube/v3/commentThreads?"
               f"part=snippet&videoId={video_id}&maxResults={batch}&order=time&key={API_KEY}")
        if page_token:
            url += f"&pageToken={page_token}"
        result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        
        if "error" in data:
            reason = data["error"].get("errors", [{}])[0].get("reason", "")
            if reason in ("commentsDisabled", "forbidden"):
                return None  # 评论已关闭
            break
        
        for item in data.get("items", []):
            s = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": s.get("authorDisplayName", ""),
                "text": s.get("textDisplay", ""),
                "likes": s.get("likeCount", 0),
                "published_at": s.get("publishedAt", ""),
                "reply_count": item["snippet"].get("totalReplyCount", 0),
            })
        
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break
        time.sleep(0.1)
    return comments
```

**批量处理要点：**
- 视频间间隔 0.15s，避免触发限流
- `commentsDisabled` 返回 None（区分于空列表）
- `order=time` 按时间排序，`order=relevance` 按相关性排序
- 每视频上限 200 条评论已够分析，无需全量
- HTML 实体需 `html.unescape()` + 正则去标签

### YouTube Search API

批量搜索关键词获取视频列表（无需已知视频 ID）：

```python
import urllib.parse

def search_videos(query, max_results=50, page_token=""):
    encoded = urllib.parse.quote(query)
    url = (f"https://www.googleapis.com/youtube/v3/search?"
           f"part=snippet&q={encoded}&type=video&maxResults={max_results}"
           f"&order=relevance&key={API_KEY}")
    if page_token:
        url += f"&pageToken={page_token}"
    data = api_get(url)
    
    results = []
    for item in data.get("items", []):
        results.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel_name": item["snippet"]["channelTitle"],
            "channel_id": item["snippet"]["channelId"],
            "published_at": item["snippet"]["publishedAt"],
        })
    return results, data.get("nextPageToken", "")
```

**搜索策略**：同一产品用多个关键词搜索（如 `OBSBOT Tiny 3`、`OBSBOT Tiny 3 review`、`OBSBOT Tiny 3 Lite`），去重合并，通常可覆盖 90%+ 的相关视频。每个关键词最多获取 100 个结果（2 页）。

### 批量产品搜索策略（2026-05-16 验证）

当需要采集某产品从上市以来的**所有** YouTube 视频时，使用多关键词搜索 + 去重 + 清洗流程：

```python
import json, requests, time

API_KEY = "YOUR_KEY"
BASE_URL = "https://www.googleapis.com/youtube/v3"

# 1. 确定产品上市日期（用 web_search 查找）
LAUNCH_DATE = "2026-01-13T00:00:00Z"

# 2. 多关键词搜索（15 个关键词，覆盖不同角度）
SEARCH_QUERIES = [
    "Product Name",
    "Product Name review",
    "Product Name unboxing",
    "Product Name test",
    "Product Name vs",
    "Product Name comparison",
    "Product Name hands on",
    "Product Name first look",
    "Product Name demo",
    "Product Name sample",
    "Product Name footage",
    "Product Name setup",
    "Product Name tutorial",
    "Product Name 4K",
    "Product Name AI",
]

def search_videos(query, max_results=50, page_token=None):
    params = {
        "part": "snippet", "q": query, "type": "video",
        "publishedAfter": LAUNCH_DATE, "maxResults": max_results,
        "order": "date", "key": API_KEY
    }
    if page_token:
        params["pageToken"] = page_token
    response = requests.get(f"{BASE_URL}/search", params=params)
    return response.json() if response.status_code == 200 else None

def get_video_details(video_ids):
    params = {"part": "snippet,statistics,contentDetails", "id": ",".join(video_ids), "key": API_KEY}
    response = requests.get(f"{BASE_URL}/videos", params=params)
    return response.json() if response.status_code == 200 else None

# 3. 收集所有唯一视频 ID
all_video_ids = set()
for query in SEARCH_QUERIES:
    result = search_videos(query, max_results=50)
    if result and "items" in result:
        for item in result["items"]:
            all_video_ids.add(item["id"]["videoId"])
    time.sleep(0.1)  # API 限流

# 4. 批量获取详情（50 个/批）
detailed_videos = []
video_list = list(all_video_ids)
for i in range(0, len(video_list), 50):
    batch = video_list[i:i+50]
    details = get_video_details(batch)
    if details and "items" in details:
        for item in details["items"]:
            detailed_videos.append({
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "published": item["snippet"]["publishedAt"],
                "tags": item["snippet"].get("tags", []),
                "description": item["snippet"].get("description", ""),
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "like_count": int(item["statistics"].get("likeCount", 0)),
                "comment_count": int(item["statistics"].get("commentCount", 0)),
                "duration": item["contentDetails"].get("duration", ""),
                "url": f"https://www.youtube.com/watch?v={item['id']}"
            })
    time.sleep(0.2)
```

**实测数据（Insta360 Link 2 Pro）**：15 个关键词 → 242 个原始视频 → 133 个清洗后视频

### 数据清洗和分类

搜索结果包含大量不相关视频（如只提到竞品而非目标产品），必须清洗：

```python
# 相关性过滤
cleaned = []
for v in videos:
    title_lower = v["title"].lower()
    desc_lower = v["description"].lower()[:500]
    
    # 标题和描述中都没有目标产品名 → 不相关
    if "product name" not in title_lower and "product name" not in desc_lower:
        continue
    
    # 竞品单独视频（标题含竞品名但不含目标产品名）
    if "competitor" in title_lower and "product name" not in title_lower:
        continue
    
    cleaned.append(v)

# 视频类型分类
for v in cleaned:
    title_lower = v["title"].lower()
    if any(kw in title_lower for kw in ["review", "评测", "hands on", "in-depth"]):
        v["video_type"] = "评测"
    elif any(kw in title_lower for kw in ["unboxing", "开箱", "first look"]):
        v["video_type"] = "开箱"
    elif any(kw in title_lower for kw in ["vs", "versus", "comparison", "对比"]):
        v["video_type"] = "对比"
    elif any(kw in title_lower for kw in ["test", "测试", "sample", "footage", "demo"]):
        v["video_type"] = "测试"
    elif any(kw in title_lower for kw in ["setup", "tutorial", "教程", "how to"]):
        v["video_type"] = "教程"
    elif any(kw in title_lower for kw in ["tips", "tricks", "技巧"]):
        v["video_type"] = "技巧"
    elif v["channel"] == "Official Channel":
        v["video_type"] = "官方"
    else:
        v["video_type"] = "其他"
```

**清洗效果（Insta360 Link 2 Pro 实测）**：
- 原始: 242 个 → 清洗后: 133 个（移除 109 个不相关视频）
- 主要移除原因：只提到 Flow 2 Pro 而非 Link 2 Pro 的视频

### 统计分析维度

批量采集后生成以下统计：

```python
from collections import Counter

# 1. 按类型统计
type_stats = {}
for v in cleaned:
    t = v["video_type"]
    if t not in type_stats:
        type_stats[t] = {"count": 0, "views": 0}
    type_stats[t]["count"] += 1
    type_stats[t]["views"] += v["view_count"]

# 2. 按月度统计（观察热度趋势）
monthly_stats = {}
for v in cleaned:
    month = v["published"][:7]  # YYYY-MM
    if month not in monthly_stats:
        monthly_stats[month] = {"count": 0, "views": 0}
    monthly_stats[month]["count"] += 1
    monthly_stats[month]["views"] += v["view_count"]

# 3. 按频道统计（找头部 KOL）
channel_stats = {}
for v in cleaned:
    ch = v["channel"]
    if ch not in channel_stats:
        channel_stats[ch] = {"count": 0, "views": 0, "top_video": None}
    channel_stats[ch]["count"] += 1
    channel_stats[ch]["views"] += v["view_count"]
    if channel_stats[ch]["top_video"] is None or v["view_count"] > channel_stats[ch]["top_video"]["view_count"]:
        channel_stats[ch]["top_video"] = v
```

### 输出格式

生成三种格式的报告：
1. **Markdown 报告** — 包含统计概览、TOP 20 视频、月度趋势、按类型分组的视频列表
2. **CSV 数据** — 完整视频列表（视频ID、标题、频道、日期、观看、点赞、评论、类型、URL）
3. **JSON 数据** — 完整结构化数据（含 tags、description）

```python
import csv

# CSV 输出
with open("output.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["视频ID", "标题", "频道", "发布日期", "观看次数", "点赞数", "评论数", "视频类型", "URL"])
    for v in sorted(cleaned, key=lambda x: x["view_count"], reverse=True):
        writer.writerow([v["video_id"], v["title"], v["channel"], v["published"][:10],
                        v["view_count"], v["like_count"], v["comment_count"], v["video_type"], v["url"]])
```

**⚠️ CSV 编码注意**：使用 `utf-8-sig`（带 BOM）确保 Excel 正确识别中文。

### 搜索策略要点

- **15 个关键词**可覆盖 90%+ 相关视频（实测 242 个原始结果）
- `publishedAfter` 参数限制为上市日期后的视频
- `order=date` 按时间排序，获取最新视频
- 每个关键词最多 50 个结果（API 限制）
- API 限流：搜索间隔 0.1s，详情获取间隔 0.2s

### 大规模评论抓取 — 并行处理

当需要抓取 100+ 视频的评论时，串行处理太慢（每个视频 2-10 秒）。用后台并行进程加速：

```python
# 1. 准备抓取脚本 fetch_comments.py（接受 start_index, end_index, output_file 参数）
# 2. 分 3 路并行
from hermes_tools import terminal

# 启动后台进程
terminal("python3 fetch_comments.py 0 46 /tmp/batch1.json 50", background=True, notify_on_complete=True, timeout=600)
terminal("python3 fetch_comments.py 46 92 /tmp/batch2.json 50", background=True, notify_on_complete=True, timeout=600)
terminal("python3 fetch_comments.py 92 136 /tmp/batch3.json 50", background=True, notify_on_complete=True, timeout=600)

# 3. 等待完成
process.poll(session_id="proc_xxx")  # 或 process.wait()
```

**关键参数**：
- 每视频评论上限设为 50（而非 200），平衡数据量和速度
- 136 个视频分 3 路，每路约 45 个，总耗时从 15 分钟降到 3 分钟
- 每路设 `timeout=600`（10 分钟），避免无限挂起
- 每个 API 调用加 `--connect-timeout 10`，避免网络卡死

### 数据清洗工作流

```python
# 1. 搜索 + 去重
all_videos = {}
for query in queries:
    results, _ = search_videos(query, 50)
    for v in results:
        if v["video_id"] not in all_videos:
            all_videos[v["video_id"]] = v

# 2. 批量获取视频详情（50个/批）
detailed = []
for i in range(0, len(video_ids), 50):
    detailed.extend(get_video_details(video_ids[i:i+50]))

# 3. 批量获取频道粉丝
subs = get_channel_subscribers(channel_ids)

# 4. 清洗：粉丝≥1K、点赞>0、评论>0
filtered = [v for v in detailed if v["subscribers"] >= 1000 and v["likes"] > 0 and v["comments"] > 0]

# 5. 按产品分类（根据标题关键词）
for v in filtered:
    if "lite" in v["title"].lower():
        v["product"] = "Product Lite"
    else:
        v["product"] = "Product"
```

### 批量评论抓取 + Word 文档上传流程（2026-05-14 验证）

当用户要求"爬出所有评论并生成Word文档上传腾讯文档"时：

1. **从腾讯文档表格读取视频列表**（不是从YouTube搜索！）
   - `mcporter call tencent-docs get_content file_id=xxx` 获取表格内容
   - 解析 Markdown 表格提取视频URL（从右往左锚定URL列）
   - ⚠️ 用户明确纠正：视频链接已在表格中，不要重新搜索YouTube

2. **YouTube API 批量抓取评论**
   - 每视频上限500条，`order=time` 按时间排序
   - 视频间间隔0.15s，每10个视频打印进度
   - `commentsDisabled` 返回 None（区分于空列表）

3. **python-docx 生成 Word 文档**
   - 标题居中，包含产品名+日期+视频数+评论总数
   - 📊 视频总览表格（Light Grid Accent 1 样式）
   - 📝 按视频分节的评论详情（作者加粗、日期灰色、正文9pt）
   - 蓝色链接可点击

4. **上传腾讯文档**
   - `import_file.sh` → `manage.async_import` → `manage.import_progress` → `manage.move_file`
   - 目标文件夹：OBSBOT YouTube（DHtSaueQJaKb）

**实测数据**：79个Tiny3视频+32个Lite视频，总耗时约5分钟

### 限制与注意
- **配额**：每天 10,000 单位（videos.list 约 1 单位/次，commentThreads.list 约 1 单位/次）
- **评论禁用**：部分视频禁用评论，API 返回空列表
- **隐藏粉丝**：`hiddenSubscriberCount=true` 时不显示粉丝数
- **批量限制**：每次最多查询 50 个视频/频道

### ⚠️ Pitfall: 视频 ID 提取
```python
# 从 URL 提取 video_id
url = "https://www.youtube.com/watch?v=VIDEO_ID"
video_id = url.split('v=')[1].split('&')[0]
```

---

## 备用方案：curl + 正则提取（快速但有限）

当没有 API Key 时，可用 curl 获取部分数据（点赞、浏览量），但**无法获取评论**。

### 使用方法

```python
import subprocess, re

url = "https://www.youtube.com/watch?v=VIDEO_ID"
result = subprocess.run(['curl', '-s', '-L', '--max-time', '20', url],
                       capture_output=True, text=True, timeout=25)
html = result.stdout

# 点赞
likes_match = re.search(r'"likeCount":"(\d+)"', html)
likes = int(likes_match.group(1)) if likes_match else 0

# 浏览量
views_match = re.search(r'"viewCount":"(\d+)"', html)
views = int(views_match.group(1)) if views_match else 0
```

### 局限性
- 评论需要 JavaScript 渲染，curl 无法获取
- 描述和标签需要完整页面解析

---

## 备用方案：Camoufox 反检测浏览器

当 curl 无法提取时，Camoufox 可补充数据。

```python
from scrapling import StealthyFetcher
import re

fetcher = StealthyFetcher()
page = fetcher.fetch("VIDEO_URL")
text = page.get_all_text()

# 点赞
like_match = re.search(r'([\d,.]+)\n[Ll]ikes?', text)
likes = int(like_match.group(1).replace(",", "")) if like_match else 0
```

需要 Python 3.10+ 虚拟环境：`~/.hermes/skills/scrapling/venv/`

---

## 备用方案：yt-dlp（不稳定）

**⚠️ 不推荐**：n challenge 失败率约 60%，受 VPN 稳定性影响大。

```bash
yt-dlp --dump-json --no-download --socket-timeout 15 "VIDEO_URL"
```

---

## 评论收集完整流程

### 1. 获取视频列表
搜索关键词获取视频 ID 列表。

### 2. 批量获取视频统计
```python
# 每批最多 50 个
for i in range(0, len(video_ids), 50):
    batch = video_ids[i:i+50]
    request = youtube.videos().list(part='statistics,snippet', id=','.join(batch))
```

### 3. 批量获取频道粉丝
```python
# 提取唯一频道 ID
channel_ids = list(set(video['snippet']['channelId'] for video in all_videos))

# 每批最多 50 个
for i in range(0, len(channel_ids), 50):
    batch = channel_ids[i:i+50]
    request = youtube.channels().list(part='statistics,snippet', id=','.join(batch))
```

### 4. 获取每个视频的评论
```python
for video_id in video_ids:
    try:
        request = youtube.commentThreads().list(
            part='snippet', videoId=video_id,
            maxResults=20, order='relevance', textFormat='plainText'
        )
        response = request.execute()
        # 处理评论...
    except Exception as e:
        # 评论可能被禁用
        pass
```

### 5. 从腾讯文档表格获取视频列表（而非搜索）
当用户已提供腾讯文档表格（含视频链接）时，**直接从表格读取视频列表，不要重新搜索 YouTube**。用户明确纠正过这一点。

```python
# 用 mcporter get_content 获取表格内容
result = subprocess.run(["mcporter", "call", "tencent-docs", "get_content", f"file_id={file_id}"],
                       capture_output=True, text=True, timeout=60)
content = json.loads(result.stdout)["content"]
```

**⚠️ Pitfall: Markdown 表格解析** — `get_content` 返回的 `|` 分隔表格中，视频标题常含 `|`、`&`、特殊字符，导致 naive split 列错位。**解决方案：从右往左锚定解析**：
1. 用正则提取 URL（`https://youtube.com/watch?v=xxx`）— 格式固定
2. URL 左边是日期（`YYYY-MM-DD`）— 格式固定
3. 日期左边依次是评论数、点赞、观看 — 都是纯数字
4. 用这些已知格式字段作为锚点反向定位标题和博主

```python
def parse_sheet_videos(content):
    videos = []
    for line in content.split('\n'):
        if not line.startswith('|') or line.startswith('|序号') or line.startswith('|----'):
            continue
        url_match = re.search(r'(https?://youtube\.com/watch\?[^\s|]+)', line)
        if not url_match:
            continue
        url = url_match.group(1)
        vid_id = extract_video_id(url)
        parts = [p.strip() for p in line.split('|')]
        parts = [p for p in parts if p]
        # 从右往左找日期锚点
        for i, p in enumerate(parts):
            if re.match(r'\d{4}-\d{2}-\d{2}', p):
                date_idx = i
                comment_count = parts[date_idx - 1]
                likes = parts[date_idx - 2]
                views = parts[date_idx - 3]
                break
        channel = parts[1]
        title = parts[3]  # 可能含特殊字符，需验证
        videos.append({...})
    return videos
```

### 6. 生成 Word 评论报告并上传腾讯文档

**⚠️ execute_code sandbox 没有 python-docx** — 必须用 `terminal` 执行 docx 生成脚本。

完整流程：
1. 用 YouTube API 批量抓取评论 → 保存为 JSON
2. 用 `terminal` 运行 python-docx 脚本生成 .docx
3. 用 `import_file.sh` 上传 → `manage.async_import` → 轮询 `import_progress`
4. 用 `manage.move_file` 移到目标文件夹

**Word 文档结构**（参考 2026-05-14 实战）：
- 标题：OBSBOT {产品名} YouTube 视频评论分析报告
- 统计概要：视频数量、评论总数、有评论视频数
- 📊 视频总览表格（序号/博主/标题/观看/点赞/评论/日期）
- 📝 评论详情（按视频分节，每条评论含 @作者、👍点赞、日期、正文）
- 链接用蓝色 RGBColor(0, 102, 204)

```python
# 关键：表格样式用 'Light Grid Accent 1'，评论作者加粗，日期灰色
from docx.shared import RGBColor
run.font.color.rgb = RGBColor(0, 102, 204)  # 链接蓝色
run.font.color.rgb = RGBColor(128, 128, 128)  # 日期灰色
```

---

## ⚠️ Pitfall: VPN 稳定性（用户明确反馈）

- **绝对不要乱切换 VPN 节点**，这是网络错误的根本原因
- 保持 VPN 连接稳定，不做多余操作
- 如需切换节点，**必须从已有节点列表里选择**
- Shadowrocket 节点切换只能通过 GUI 操作
- yt-dlp 失败率 > 50% 时，说明 VPN 不稳定，应停止并用已有数据

---

- **Python 语法错误**：`sum(len(v['comments'] for v in ... if v['comments'])` 缺少闭合括号 → 正确写法：`sum(len(v['comments']) for v in ... if v['comments'])`
- **execute_code sandbox 无 python-docx**：sandbox 环境没有第三方包，docx 生成必须用 `terminal` 工具执行
- **表格解析列错位**：Tencent Docs 的 markdown 表格中标题含 `|` 时 split 会错位，必须从右往左锚定解析

## 工具链

| 工具 | 用途 | 推荐度 |
|------|------|:------:|
| **YouTube Data API v3** | 视频统计、频道信息、评论 | ⭐⭐⭐⭐⭐ |
| curl + regex | 快速获取点赞、浏览量 | ⭐⭐⭐ |
| Camoufox | 反检测抓取 | ⭐⭐ |
| yt-dlp | 完整元数据 | ⭐ |
| 腾讯文档 MCP | 存储数据 | ⭐⭐⭐⭐ |
