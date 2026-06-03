---
name: obsbot-competitor-monitor
description: |
  OBSBOT竞品YouTube上线监测。搜索18款核心竞品在YouTube的上线视频，抓取数据，分析评论区，生成Excel报告上传腾讯文档。
  定时任务：周一/三/五自动执行。
user-invocable: true
---

# OBSBOT 竞品上线监测

## 核心竞品清单（18款）

| 品牌 | 搜索关键词 |
|------|-----------|
| Logitech Series | Logitech Brio webcam, Logitech C920 webcam, Logitech MX Brio, Logitech C922 |
| Insta360 Link 2 | Insta360 Link 2 webcam |
| Insta360 Link 2c | Insta360 Link 2c |
| Insta360 Wave | Insta360 Wave webcam |
| Insta360 Link 2 Pro | Insta360 Link 2 Pro |
| Elgato Facecam 4K | Elgato Facecam 4K |
| Elgato Facecam mk2 | Elgato Facecam mk2 |
| Emeet Pixy | Emeet Pixy webcam, EMEET Pixy |
| EMEET SmartCam S600 | EMEET S600 webcam |
| EMEET SmartCam S800 | EMEET S800 webcam |
| EMEET PIXY Wireless | EMEET PIXY Wireless |
| EMEET S600L | EMEET S600L webcam |
| Yolocam S3 | Yolocam S3 webcam, YoloLiv YoloCam S3 |
| Yolocam S7 | Yolocam S7 webcam, YoloLiv YoloCam S7 |
| Hollyland VenusLiv Air | Hollyland VenusLiv Air |
| Hollyland Lyra 4K | Hollyland Lyra 4K webcam |
| Razer Kiyo | Razer Kiyo webcam, Razer Kiyo V2 |
| UGREEN 4K Webcam | UGREEN 4K webcam |

## 定时任务时间规则

| 执行日 | 时间范围 | Cron 表达式 |
|--------|---------|-------------|
| 周一 | 上周六 ~ 本周一 | `0 9 * * 1` |
| 周三 | 周二 ~ 周三 | `0 9 * * 3` |
| 周五 | 周四 ~ 周五 | `0 9 * * 5` |

**注意**：根据实际执行日确定搜索时间范围，不要硬编码日期。

## 过滤规则（必须严格执行）

1. **播放量 < 50 且 粉丝数 < 1k** → 直接过滤，不展示
2. **视频时长 < 1 分钟** → 直接过滤（Shorts 除外，Shorts 保留）
3. **是否上评** → 仅在以下情况标记"是"：
   - 评论区明确提到 obsbot/meet/tiny/tail 等关键词
   - 整体舆论明显负面（差评集中）

## 数据字段

| 字段 | 说明 |
|------|------|
| Date | 发布日期 |
| 竞品 | 品牌名 |
| 网红ID | 频道名 |
| 视频链接 | YouTube URL |
| 量级 | KOL/KOC/素人（按播放量：≥10k=KOL，≥1k=KOL，≥100=KOC，<100=素人） |
| Content Type | Review/VS/Shorts/Tutorials/Unboxing/Roundup/Livestream |
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

### Step 1: 搜索竞品视频
**方法 A: curl 直接调用（推荐）**
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=QUERY&type=video&publishedAfter=START&publishedBefore=END&maxResults=50&order=date&key=AIzaSy...aA1Q"
```

**方法 B: 浏览器搜索（备用）**
```python
# 对每个品牌搜索
for brand, query in competitors.items():
    browser_navigate(f'https://www.youtube.com/results?search_query={query}&sp=EgIIAw%3D%3D')
    # 用 browser_console 提取视频ID
```

### Step 2: 获取视频统计
```bash
curl -s "https://www.googleapis.com/youtube/v3/videos?part=statistics,contentDetails,snippet&id=VIDEO_IDS&key=AIzaSy...aA1Q"
```

### Step 3: 过滤
- 删除播放量<50且粉丝<1k的视频
- 删除时长<1分钟的视频（Shorts除外）

### Step 4: 评论区分析
对高互动视频（播放≥500 且 评论≥3），用浏览器提取评论：
```javascript
// browser_console 执行
const comments = [];
document.querySelectorAll('ytd-comment-thread-renderer').forEach((el, i) => {
    if (i < 20) {
        const author = el.querySelector('#author-text')?.textContent?.trim() || '';
        const text = el.querySelector('#content-text')?.textContent?.trim() || '';
        if (text) comments.push({ author, text });
    }
});
// 检查 OBSBOT 关键词
const obsbotKeywords = ['obsbot', 'meet 2', 'meet se', 'tiny 2', 'tiny 3', 'tail 2', 'tail air'];
```

### Step 5: 生成 Excel
```python
import openpyxl
# 按日期+品牌排序
# 表头：Date, 竞品, 网红ID, 视频链接, 量级, Content Type, 是否上评, 曝光量, 点赞量, 点赞率, 评论数, 评论率, 互动率, Title, Comment
```

### Step 6: 上传腾讯文档
```bash
cd ~/.hermes/skills/tencent-docs && bash import_file.sh /path/to/excel.xlsx
# 然后调用 manage.async_import
# 然后调用 manage.move_file 移动到 DnNkcnCRIHGt（竞品监测文件夹）
```

## 文件命名规则

`{当天日期}——竞品检测报告——时间范围（{起始日期}-{结束日期}）`

示例：`2026-06-02——竞品检测报告——时间范围（5.30-6.2）`

## 保存位置

腾讯文档：云盘 → OBSBOT → 竞品监测
文件夹 ID：`DnNkcnCRIHGt`

## 已知陷阱（Pitfalls）

### 🔴 YouTube API 配额优化（推荐）

使用 `~/.hermes/scripts/yt_optimizer.py` 自动缓存 + 批量请求：

```python
import sys
sys.path.insert(0, str(Path.home() / '.hermes' / 'scripts'))
from yt_optimizer import api_call, batch_videos

# 搜索（24h 缓存，重复执行 = 0 单位）
result = api_call("search", {
    "q": "Logitech Brio webcam",
    "type": "video", "part": "snippet",
    "publishedAfter": START, "publishedBefore": END,
    "maxResults": "50", "order": "date",
}, cost=100, ttl=86400)

# 批量获取视频详情（50个 = 1 单位）
video_ids = [item["id"]["videoId"] for item in result["data"]["items"]]
details = batch_videos(video_ids)
```

**配额节省**：18品牌搜索 = 1800单位首次，24h内缓存=0。批量详情 = 1单位/50视频。

### 🔴 YouTube API Key 在 Python heredoc 中被截断
系统会将 `AIzaSy...` 开头的 API key 截断为 `***`。不要在 Python 脚本中硬编码 API key。

**解决方案**：
1. 用 `curl` 直接调用 API（推荐）：
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=QUERY&type=video&publishedAfter=START&publishedBefore=END&maxResults=50&order=date&key=YOUR_YOUTUBE_API_KEY"
```
2. 或用浏览器搜索 YouTube（browser_navigate + browser_console）

### 🔴 YouTube API 直连可用，不需要代理
YouTube Data API v3 可以直连访问，不需要走代理。但 mcporter 调用腾讯文档需要代理。

### 🔴 mcporter 调用腾讯文档需要代理
```bash
export https_proxy=http://127.0.0.1:1082
export http_proxy=http://127.0.0.1:1082
```

### 🔴 浏览器搜索 YouTube 的 JS 选择器
```javascript
// 提取视频标题和链接
const videos = [];
document.querySelectorAll('a#video-title').forEach((el, i) => {
    if (i < 15) {
        const href = el.href || '';
        const title = el.textContent?.trim()?.substring(0, 80) || '';
        const videoId = href.split('v=')[1]?.split('&')[0] || '';
        videos.push({ title, url: href, videoId });
    }
});

// 从视频页面获取统计
const title = document.querySelector('h1.ytd-watch-metadata yt-formatted-string')?.textContent?.trim() || '';
const channel = document.querySelector('#channel-name a')?.textContent?.trim() || '';
const views = document.querySelector('#info-container span:first-child')?.textContent?.trim() || '';
const likes = document.querySelector('#top-level-buttons-computed button:first-child')?.textContent?.trim() || '';
```

### 🔴 评论区提取 JS 代码
```javascript
const comments = [];
document.querySelectorAll('ytd-comment-thread-renderer').forEach((el, i) => {
    if (i < 20) {
        const author = el.querySelector('#author-text')?.textContent?.trim() || '';
        const text = el.querySelector('#content-text')?.textContent?.trim() || '';
        if (text) comments.push({ author, text });
    }
});

// 检查 OBSBOT 关键词
const obsbotKeywords = ['obsbot', 'meet 2', 'meet se', 'tiny 2', 'tiny 3', 'tail 2', 'tail air'];
const obsbotMentions = comments.filter(c => {
    const lower = c.text.toLowerCase();
    return obsbotKeywords.some(kw => lower.includes(kw));
});
```

## 注意事项

1. YouTube API 直连可用（不需要代理）
2. mcporter 调用腾讯文档需要代理（export https_proxy=http://127.0.0.1:1082）
3. API 配额限制：10,000 单位/天，每次搜索约 100 单位
4. 评论区分析用浏览器（browser_navigate + browser_console）
5. 每个品牌单独搜索，避免漏掉
6. 搜索结果中可能包含不相关视频（如摩托车骑行视频），需要人工过滤
