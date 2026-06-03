# OBSBOT 竞品投放监测 SOP

> 来源：IMA 笔记「每日竞品监测」(2026.06.02 更新) + 竞品投放情况.xlsx

## 核心目标

1. **竞品推广策略拆解** — 人群特征、内容布局、博主量级、上线节奏
2. **市场反馈洞察** — 用户需求、差异化 OBSBOT 产品推广点

## 核心竞品清单（18款）

| 品牌 | 产品 |
|------|------|
| Logitech | Series |
| Insta360 | Link 2&2c / Wave / Link 2 Pro |
| Elgato | Facecam 4K / Facecam mk2 |
| EMEET | Pixy / PIXY Wireless / SmartCam S600 / SmartCam S800 / S600L |
| YoloLiv | Yolocam S3 / Yolocam S7 |
| Hollyland | VenusLiv Air / Lyra 4K |
| Razer | Kiyo & Kiyo V2 |
| UGREEN | 4K Webcam |

## 日常工作流程

1. **搜索** — 每天在 YouTube 搜索竞品关键词（关键词 List 见 Google Sheet）
2. **筛选** — ✔️ YouTube 长视频（高质量评论 & 真实反馈）；✖️ 官方宣传切片/直播/无相关产品测评
3. **存档** — 按频道体量分类（KOL/KOC/素人）、记录数据（曝光量/点赞量/评论率）、监控评论区舆论风向
4. **上评** — 依据实际数据判断是否需要上评论

## 数据字段规范

`Date` / `竞品` / `网红ID` / `视频链接` / `量级(KOL/KOC/素人)` / `Content Type` / `是否上评` / `曝光量` / `点赞量` / `点赞率` / `评论数` / `评论率` / `互动率` / `Title` / `Comment`

## 用户评论关注主题（5大维度）

1. **硬件与画质** — 传感器大小、暗光控噪、自然虚化、发热问题
2. **AI追踪** — 教学/演示场景、快速移动稳定性、手势控制
3. **软件易用性** — 设置记忆功能（跨机痛点）、手动对焦、场景快捷键
4. **连接性** — USB-C/无线选项、线材设计、HDMI/音频输入
5. **市场定位** — 性价比讨论、垂直场景需求（俯拍/直播销售/VTuber）

## 关键竞争洞察

- **Elgato Facecam 4K**：上线少但互动率高，持续做关键词建设（Best 4K Webcam 等 CTA 视频）
- **Yolocam S3**：12月投放从17→49条大幅增长，画质好评但配套APP差评多
- **Hollyland Lyra 4K**：12月新入局即32条，但发热问题是重灾区
- **Insta360 Link 2**：AI追踪被视为"行业未来"，适合教学/演讲场景

## 标题关键词建设模式

`(Best/Perfect/Advanced) + 产品类别 + 使用场景 + 价格限制 + 年份 + 购买行为 + 特定用户`

---

## 每日竞品监测执行工作流（2026-06-02 验证）

### 完整流程概览

```
1. YouTube Data API 搜索 → 2. 视频统计 → 3. 评论区分析 → 4. 生成 Excel → 5. 上传腾讯文档
```

### Step 1: YouTube Data API 搜索

**⚠️ 2026-06-02 重要更新：直连可用，代理反而不稳定**

```python
import urllib.request, urllib.parse, json

API_KEY=***  # YouTube Data API Key

# 搜索参数：按日期筛选
params = urllib.parse.urlencode({
    'part': 'snippet',
    'q': product_name,  # 如 "Insta360 Link 2"
    'type': 'video',
    'publishedAfter': '2026-06-01T00:00:00Z',  # 昨天
    'publishedBefore': '2026-06-02T23:59:59Z',  # 今天
    'maxResults': 50,
    'order': 'date',
    'key': API_KEY
})
url = f"https://www.googleapis.com/youtube/v3/search?{params}"
```

**⚠️ 关键坑**：
- **直连可用** — YouTube Data API 在中国大陆可直连（无需代理），代理反而会返回 503/超时
- **API Key 截断问题** — 在 terminal heredoc (`<< 'PYEOF'`) 中，API Key `AIzaSy...` 会被系统截断为 `AIza...`，导致 403 错误。**解决方案**：用 curl 直接调用，或写入文件后执行
- 部分请求会 `IncompleteRead` 或 `Remote end closed connection`，需要重试
- 搜索词要精确匹配产品名，避免噪音（如 "Wave" 会匹配旅行视频）
- 每个品牌用多个搜索词覆盖（如 Logitech 用 "Logitech Brio" + "Logitech C920" + "Logitech MX Brio"）

### Step 2: 获取视频统计

```python
# 批量获取统计（最多50个ID）
params = urllib.parse.urlencode({
    'part': 'statistics,contentDetails,snippet',
    'id': ','.join(video_ids),
    'key': API_KEY
})
url = f"https://www.googleapis.com/youtube/v3/videos?{params}"

# 计算互动率
like_rate = (likes / views * 100) if views > 0 else 0
comment_rate = (comments / views * 100) if views > 0 else 0
engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
```

### Step 3: 评论区 OBSBOT 提及检测

**方法 A: 浏览器提取（推荐，最可靠）**

```javascript
// 在 YouTube 视频页面执行
const comments = [];
document.querySelectorAll('ytd-comment-thread-renderer').forEach((el, i) => {
    if (i < 20) {
        const author = el.querySelector('#author-text')?.textContent?.trim() || '';
        const text = el.querySelector('#content-text')?.textContent?.trim() || '';
        const likes = el.querySelector('#vote-count-middle')?.textContent?.trim() || '0';
        if (text) comments.push({ author, text, likes });
    }
});

// OBSBOT 关键词检测
const obsbotKeywords = ['obsbot', 'meet 2', 'meet se', 'tiny 2', 'tiny 3', 'tail 2', 'tail air'];
const obsbotMentions = comments.filter(c => {
    const lower = c.text.toLowerCase();
    return obsbotKeywords.some(kw => lower.includes(kw));
});
```

**操作步骤**：
1. `browser_navigate` 到视频 URL
2. `browser_scroll` 下滑 2-3 次触发评论加载
3. `browser_console` 执行上述 JS 提取评论
4. 分析 OBSBOT 提及和舆论导向

**方法 B: YouTube Data API（备用）**

```bash
curl -s "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=VIDEO_ID&maxResults=20&order=relevance&key=$API_KEY"
```

⚠️ API 不稳定，部分视频禁用评论 API

### Step 4: 视频类型分类逻辑

```python
def classify_video_type(title, duration_str):
    title_lower = title.lower()
    
    # Shorts 检测（duration < 60s）
    if duration_str:
        import re
        match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if match:
            total_seconds = int(match.group(1) or 0)*3600 + int(match.group(2) or 0)*60 + int(match.group(3) or 0)
            if total_seconds <= 60:
                return 'Shorts'
    
    # 按标题关键词分类
    if any(kw in title_lower for kw in ['vs', 'versus', 'comparison']):
        return 'VS'
    elif any(kw in title_lower for kw in ['review', 'reseña', 'resenha']):
        return 'Review'
    elif any(kw in title_lower for kw in ['tutorial', 'how to', 'guide', 'setup']):
        return 'Tutorials'
    elif any(kw in title_lower for kw in ['unboxing', 'unbox']):
        return 'Unboxing'
    elif any(kw in title_lower for kw in ['best', 'top', 'roundup']):
        return 'Roundup'
    elif any(kw in title_lower for kw in ['live', 'streaming', 'stream']):
        return 'Livestream'
    else:
        return 'Review'  # 默认
```

### Step 5: 创作者量级分类

```python
def classify_creator_tier(views, likes, comments):
    if views >= 10000:
        return 'KOL'
    elif views >= 1000:
        return 'KOL'
    elif views >= 100:
        return 'KOC'
    else:
        return '素人'
```

### Step 6: Excel 生成格式

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side

headers = [
    'Date', '竞品', '网红ID', '视频链接', '量级', 'Content Type', 
    '是否上评', '曝光量', '点赞量', '点赞率', '评论数', '评论率', 
    '互动率', 'Title', 'Comment'
]

# 样式
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(bold=True, size=11, color="FFFFFF")
thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                     top=Side(style='thin'), bottom=Side(style='thin'))

# "是否上评" 判断逻辑
should_comment = '是' if views >= 100 and comments_count >= 2 else ''
```

### Step 7: 上传腾讯文档

```bash
# 文件夹结构：云盘 → OBSBOT (DjbGtzenXmbX) → 竞品监测 (DnNkcnCRIHGt)

# 1. 上传到 COS
cd ~/.hermes/skills/tencent-docs
bash import_file.sh "/Users/zhoulong/Downloads/2026-06-02-竞品检测.xlsx"

# 2. 触发异步导入
mcporter call "tencent-docs" "manage.async_import" --args '{"task_id": "...", ...}'

# 3. 搜索获取 file_id
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key": "竞品检测"}'

# 4. 移动到竞品监测文件夹
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id": "...", "target_folder_id": "DnNkcnCRIHGt"}'
```

**关键文件夹 ID**：
- OBSBOT 文件夹：`DjbGtzenXmbX`
- 竞品监测子文件夹：`DnNkcnCRIHGt`

### 常见陷阱

| 陷阱 | 解决方案 |
|------|---------|
| YouTube API `IncompleteRead` | 直连重试即可，不要用代理 |
| YouTube API 403 错误 | 检查 API Key 是否被 heredoc 截断，用 curl 直接调用 |
| 代理返回 503/超时 | 移除代理设置，YouTube API 可直连 |
| 搜索结果含无关视频 | 检查标题关键词，过滤非 webcam 相关内容 |
| 评论区未加载 | 浏览器下滑 2-3 次触发懒加载 |
| `manage.import_progress` 返回 405 | 用 `manage.search_file` 替代验证 |
| mcporter 连接超时 | 设置代理或重新 `mcporter auth tencent-docs` |
| 中文标题创建失败 | 先英文创建，再 `manage.rename_file_title` 改中文 |
