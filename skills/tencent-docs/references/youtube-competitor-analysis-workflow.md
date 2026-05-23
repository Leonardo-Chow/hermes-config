# YouTube 竞品分析→腾讯文档智能表格 工作流

## 概述

YouTube 竞品分析数据采集、清洗、格式化并上传到腾讯文档智能表格的完整流程。

## 数据格式要求（用户明确要求）

### 1. 网红类型（必须具体）

❌ 错误示例：Tech/Video Production、头部KOL、腰部KOL

✅ 正确分类：
- **Livestream** — 直播内容创作者
- **Camera/Video** — 摄影/视频制作
- **Tutorial/Education** — 教程/教育
- **Product Review** — 产品评测
- **Gaming/Esports** — 游戏/电竞
- **Church Production** — 教堂/礼拜直播
- **Music Production** — 音乐制作
- **Corporate/Business** — 企业/商务
- **Podcast Production** — 播客制作

判断依据：视频标题 + 描述 + 内容分析，不能笼统分类。

### 2. 受众地区（English/中文格式）

必须使用 `English/中文` 格式：
- United States/美国
- United Kingdom/英国
- Germany/欧洲
- France/欧洲
- Sweden/欧洲
- South Korea/韩国
- Japan/日本
- Australia/澳大利亚
- India/印度
- Global/全球（未知地区）

⚠️ 欧洲国家统一用 `Country/欧洲`，不单独写中文国名。

### 3. Pros/Cons（基于真实评论）

- ✅ 从视频评论区提取真实用户反馈
- ✅ 每条 Pros/Cons 精简提炼（≤15字）
- ✅ 每个视频 2-3 条 Pros 和 Cons
- ❌ 不能出现"待分析"
- ❌ 不能基于标题推断，必须来自评论

无内容时用 `——` 代替。

### 4. 结论（详细说明）

每个视频 2-3 句话，包含：
- 创作者定位（谁在做这个内容）
- 受众需求（观众关心什么）
- 视频价值（这个视频解决了什么问题）

### 5. 关键词铺设

从以下来源综合提取：
- 视频标题（主要来源）
- 视频描述区（重要来源）
- Hashtags（如有）
- 限制 8 个最相关关键词

### 6. 场景描述（必须具体）

❌ 错误：视频制作、内容创作、直播

✅ 正确分类：
- Live Event Production — 音乐会、会议、体育赛事
- Church/Worship Streaming — 教堂礼拜
- Tutorial/Education — 教程、指南
- Product Review — 评测、开箱
- Podcast Production — 播客录制
- Gaming/Esports — 游戏直播
- Corporate/Business — 企业会议、研讨会
- Wedding/Event — 婚礼、典礼
- Sports Broadcasting — 体育赛事

## 完整工作流

### Step 1: YouTube 数据采集

```python
# 使用 YouTube Data API v3
API_KEY = "YOUR_YOUTUBE_API_KEY"

# 搜索视频
search_url = f"{BASE}/search?part=snippet&q={query}&type=video&maxResults=50&key={API_KEY}"

# 获取视频统计
videos_url = f"{BASE}/videos?part=statistics,snippet&id={video_ids}&key={API_KEY}"

# 获取频道统计（订阅数）
channels_url = f"{BASE}/channels?part=statistics,snippet&id={channel_ids}&key={API_KEY}"
```

### Step 2: 评论采集（用于 Pros/Cons）

```python
# 获取评论（按相关性排序，取 top 20）
comments_url = f"{BASE}/commentThreads?part=snippet&videoId={video_id}&maxResults=20&order=relevance&key={API_KEY}"
```

评论采集策略：
- 按评论数排序，优先获取评论多的视频
- 每个视频获取 15-20 条热门评论
- 使用 Tavily Extract 作为备选方案（API 超时时）

### Step 3: 数据清洗与格式化

```python
# 1. 网红类型判断
def determine_creator_type(title, description, scene):
    # 基于标题关键词判断
    if 'livestream' in title_lower or 'live stream' in title_lower:
        return 'Livestream'
    if 'review' in title_lower or 'unboxing' in title_lower:
        return 'Product Review'
    # ... 详见上方分类表

# 2. 受众地区格式化
def format_region(country_code):
    mapping = {
        'US': 'United States/美国',
        'GB': 'United Kingdom/英国',
        'DE': 'Germany/欧洲',
        'FR': 'France/欧洲',
        # ...
    }
    return mapping.get(country_code, 'Global/全球')

# 3. Pros/Cons 提取（基于评论）
def extract_pros_cons(comments):
    # 分析评论情感
    # 正面关键词 → Pros
    # 负面关键词 → Cons
    # 无明确反馈 → '——'
```

### Step 4: 上传到腾讯文档

```python
import subprocess
import json

FILE_ID = "DREtBbXZad2VHVm13"  # 目标表格
SHEET_ID = "t00i2h"  # 工作表 ID

# 清空旧数据
records = list_records(FILE_ID, SHEET_ID)
delete_records(FILE_ID, SHEET_ID, [r['record_id'] for r in records])

# 上传新数据（每批 50 条）
for i in range(0, len(new_records), 50):
    batch = new_records[i:i+50]
    subprocess.run([
        "mcporter", "call", "tencent-docs", "smartsheet.add_records",
        "--args", json.dumps({
            "file_id": FILE_ID,
            "sheet_id": SHEET_ID,
            "records": batch
        })
    ])
```

## 表格结构（13 列）

| 列名 | 类型 | 说明 |
|------|------|------|
| 网红ID | text | 频道名称 |
| 渠道链接 | text | YouTube 频道 URL |
| 网红类型 | text | Livestream/Camera/Tutorial 等 |
| 受众地区 | text | United States/美国 格式 |
| 量级(k) | number | 订阅数（千） |
| 案例视频 | text | 视频 URL |
| 点赞量 | number | 视频点赞数 |
| 评论数 | number | 视频评论数 |
| 关键词铺设 | text | 逗号分隔的关键词 |
| 场景 | text | 具体场景分类 |
| Pros | text | 用户认可的功能点 |
| Cons | text | 用户不认可的功能点 |
| 结论 | text | 2-3 句详细分析 |

## Pitfalls

- **YouTube API 超时**：使用 Tavily Extract 作为备选
- **评论为空**：用 `——` 代替，不能写"待分析"
- **网红类型笼统**：必须基于视频内容具体分类
- **受众地区格式**：必须 "English/中文"，欧洲统一 "Country/欧洲"
- **关键词过多**：限制 8 个最相关的
- **场景泛化**：必须具体，不能写"视频制作"

## 数据采集方式（2026-05-20 更新）

### 视频元数据采集

**首选：TranscriptAPI**（无需 VPN，国内直连）
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=json&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: HermesAgent/0.11.0"
```
返回：title, author_name, author_url, language, transcript

**备选：YouTube Data API v3**
```bash
curl -s "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=VIDEO_ID&key=$API_KEY"
```

### 评论区采集

**首选：浏览器 DOM 提取**（最可靠）
```javascript
// 需要先滚动到评论区触发懒加载，然后执行：
const comments = [];
document.querySelectorAll('ytd-comment-thread-renderer').forEach((el, i) => {
    if (i < 10) {
        const author = el.querySelector('#author-text')?.textContent?.trim() || '';
        const text = el.querySelector('#content-text')?.textContent?.trim() || '';
        const likes = el.querySelector('#vote-count-middle')?.textContent?.trim() || '';
        if (text) comments.push({ author, text, likes });
    }
});
JSON.stringify(comments);
```
⚠️ 需要 VPN 访问 YouTube
⚠️ 页面需要先滚动 2-3 次触发评论区懒加载

**备选：YouTube Data API v3**
```bash
curl -s "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=VIDEO_ID&maxResults=20&order=relevance&key=$API_KEY"
```

### 批量处理策略

当需要处理 20+ 个视频时：
1. 用 TranscriptAPI 批量获取标题（无需 VPN，速度快）
2. 用浏览器逐个获取评论（需要 VPN，每个视频约 30 秒）
3. 用 delegate_task 并行处理（最多 3 个并发）

### 批量评论爬取→Word文档（2026-05-21 新增）

当用户要求"爬取所有视频评论并生成文档"时，使用此流程：

```python
import urllib.request
import json
import time
from docx import Document

API_KEY = "YOUR_YOUTUBE_API_KEY"

def get_video_comments(video_id, max_results=10):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults={max_results}&key={API_KEY}&order=relevance"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    return [{"author": i["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
             "text": i["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
             "likes": i["snippet"]["topLevelComment"]["snippet"]["likeCount"]}
            for i in data.get("items", [])]

def get_video_title(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={API_KEY}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    return data["items"][0]["snippet"]["title"] if data.get("items") else "Unknown"

# 批量处理 57 个视频（2026-05-21 实测，~73秒完成）
for video_id in video_list:
    title = get_video_title(video_id)
    comments = get_video_comments(video_id, max_results=10)
    # 写入 docx...
    time.sleep(0.1)  # 避免 API 限流
```

**上传到腾讯文档**：python-docx 生成 .docx → `import_file.sh` → `manage.async_import` → `manage.move_file`

**关键 Pitfalls**：
- YouTube Data API 的 `commentThreads` 端点在国内可直连，无需 VPN
- 404 错误通常意味着视频已删除或设为私有，跳过即可
- 每个视频取 top 10-20 条热门评论即可（`order=relevance`）
- 57 个视频批量处理约 73 秒，每个视频间隔 0.1s 避免限流
- python-docx 需要安装：`uv pip install python-docx`

**区分表格中的链接列（重要，用户多次纠正）**：
腾讯文档的竞品分析表格通常有两个链接列：
- `渠道链接` — YouTube 频道主页 URL（**不需要爬评论**）
- `案例视频` — 具体视频 URL（**需要爬评论**）
用户明确说过"只需要爬取案例视频列"，不要混淆两列。不要爬渠道链接！

**用户指定视频列表时的处理**：
当用户直接贴出视频链接列表时，只处理这些链接，不要从文档中读取其他视频。
用户可能会说"重新给我弄，只抓这几个视频"——此时忽略之前的数据，只处理用户新给的列表。

**评论数量**：
默认抓取10条评论，但用户可能要求更多（如30条）。当用户说"评论区太多的话抓取30条有价值的评论"时：
- 使用 `max_results=30`
- 使用 `order=relevance`（按相关性排序，获取最有价值的评论）
- 如果评论少于30条，有多少返回多少

**上传目标文件夹**：
竞品分析相关文档的文件夹结构：
- `DPIZlPqPflSU` — Talent2 调研数据（父文件夹）
- `DLqiAqwhZcbP` — 分析数据（子文件夹，存放评论汇总文档）
- `DlFhFPwTsGMu` — youtube数据（子文件夹）

用户说"上传到分析数据文件夹"时，使用 `DLqiAqwhZcbP`。

## 表格创建 vs 更新

**更新已有表格**：直接用 `smartsheet.update_records`
**创建新表格**：参考 SKILL.md 中的「Smartsheet 从零创建工作流」

## 相关文件

- `/tmp/atem_cleaned.json` — 原始视频数据
- `/tmp/atem_comments.json` — 评论数据
- `/tmp/atem_keywords.json` — 关键词和场景分析
- `/tmp/atem_final.json` — 最终格式化数据
- `/tmp/all_comments.json` — 三个竞品的评论汇总（2026-05-20）
- `/tmp/video_links.json` — 视频链接汇总（2026-05-20）
- `/tmp/all_competitor_data.json` — 三个竞品完整数据（2026-05-20）
