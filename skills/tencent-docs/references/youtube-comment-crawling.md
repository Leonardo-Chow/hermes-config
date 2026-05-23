# YouTube 评论区 & 视频元数据爬取 → 腾讯文档

## 适用场景
用户给出 YouTube 视频链接列表，要求：
- 爬取评论区内容，生成 Word 文档
- 爬取视频标题/简介/Tags，生成 Word 文档
- 上传到腾讯文档指定文件夹

## 核心流程

### 1. 评论区爬取（YouTube Data API v3）

```python
import urllib.request, json

API_KEY = "YOUR_YOUTUBE_API_KEY"

def get_video_comments(video_id, max_results=30):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults={max_results}&key={API_KEY}&order=relevance"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    comments = []
    for item in data.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": snippet.get("authorDisplayName", ""),
            "text": snippet.get("textDisplay", ""),
            "likes": snippet.get("likeCount", 0),
            "published": snippet.get("publishedAt", "")
        })
    return comments
```

### 2. 视频元数据爬取（标题+简介+Tags）

```python
def get_video_details(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={video_id}&key={API_KEY}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    items = data.get("items", [])
    if items:
        snippet = items[0]["snippet"]
        statistics = items[0].get("statistics", {})
        return {
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),  # 完整简介
            "tags": snippet.get("tags", []),  # 标签列表
            "channel": snippet.get("channelTitle", ""),
            "published": snippet.get("publishedAt", ""),
            "viewCount": statistics.get("viewCount", "0"),
            "likeCount": statistics.get("likeCount", "0"),
            "commentCount": statistics.get("commentCount", "0")
        }
```

### 3. Word 文档生成（python-docx）

```python
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
title = doc.add_heading('标题', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 每个视频一个 section
for i, video_id in enumerate(videos):
    doc.add_heading(f'{i+1}. {video_title}', level=2)
    p = doc.add_paragraph()
    p.add_run(f'视频链接：https://www.youtube.com/watch?v={video_id}').italic = True
    
    # 评论列表
    for j, comment in enumerate(comments):
        p = doc.add_paragraph()
        p.add_run(f'评论 {j+1}：').bold = True
        p.add_run(f'{comment["author"]} (👍 {comment["likes"]})')
        doc.add_paragraph(comment["text"])

doc.save(output_path)
```

### 4. 上传到腾讯文档

```bash
# 上传
cd ~/.hermes/skills/tencent-docs && bash import_file.sh /tmp/文件名.docx

# 触发导入
mcporter call tencent-docs manage.async_import --args '{"task_id": "...", "file_size": "...", "file_key": "...", "file_name": "...", "file_md5": "..."}'

# 等待后搜索
sleep 10 && mcporter call tencent-docs manage.search_file --args '{"search_key": "文件名"}'

# 移动到目标文件夹
mcporter call tencent-docs manage.move_file --args '{"file_id": "...", "target_folder_id": "..."}'
```

## ⚠️ 关键陷阱

### 只爬用户指定的链接
用户给出链接列表时，**只爬这些链接**，不要从文档中提取所有视频。用户明确纠正过：
- ❌ 错误：读取文档所有行的案例视频列，爬全部
- ✅ 正确：只爬用户在消息中给出的链接

### 评论数量
- 默认每个视频最多 **30 条**有价值的评论
- 使用 `order=relevance` 获取最相关的评论
- API 配额充足，57个视频约消耗 57 units（videos.list）+ 57 units（commentThreads.list）

### 文件夹位置（OBSBOT/Talent2 调研数据）
| 文件夹 | ID | 用途 |
|--------|-----|------|
| 分析数据 | DLqiAqwhZcbP | 评论区内容文档 |
| 标题数据 | DbDCnThHUaDu | 视频标题/简介/Tags 文档 |
| youtube数据 | DlFhFPwTsGMu | YouTube 原始数据 |

### 简介必须完整
`description` 字段获取的是完整简介，不要截断或总结。用户要求"完整的把简介里面的内容爬下来"。

### python-docx 依赖
```bash
uv pip install python-docx -q
```
系统 Python 无 docx 模块，需先安装。

### 评论区太多时
用户要求："如果某条视频的评论区太多的话，该视频就抓取30条有价值的评论"。使用 `max_results=30` + `order=relevance`。

## YouTube API Key
```
YOUR_YOUTUBE_API_KEY
```
存储在 MEMORY 中，注意配额限制（10,000 units/天）。
