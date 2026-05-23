# YouTube Data API v3 实战代码模式

## 环境准备

```bash
pip install google-api-python-client
```

## 完整批量采集脚本

```python
import json
from googleapiclient.discovery import build

API_KEY = 'YOUR_API_KEY'
youtube = build('youtube', 'v3', developerKey=API_KEY)

# === 1. 搜索视频 ===
request = youtube.search().list(
    part='snippet',
    q='OBSBOT review 2026',
    type='video',
    maxResults=50,
    order='relevance'
)
response = request.execute()

video_ids = [item['id']['videoId'] for item in response['items']]

# === 2. 批量获取视频统计（最多50个/次）===
all_video_data = {}

for i in range(0, len(video_ids), 50):
    batch = video_ids[i:i+50]
    request = youtube.videos().list(
        part='statistics,snippet',
        id=','.join(batch)
    )
    response = request.execute()
    
    for item in response.get('items', []):
        video_id = item['id']
        stats = item['statistics']
        snippet = item['snippet']
        
        all_video_data[video_id] = {
            'title': snippet['title'],
            'channel': snippet['channelTitle'],
            'channel_id': snippet['channelId'],
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments': int(stats.get('commentCount', 0)),
            'published': snippet['publishedAt']
        }

# === 3. 批量获取频道粉丝数 ===
channel_ids = list(set(v['channel_id'] for v in all_video_data.values()))
channel_data = {}

for i in range(0, len(channel_ids), 50):
    batch = channel_ids[i:i+50]
    request = youtube.channels().list(
        part='statistics,snippet',
        id=','.join(batch)
    )
    response = request.execute()
    
    for item in response.get('items', []):
        channel_id = item['id']
        stats = item['statistics']
        snippet = item['snippet']
        
        channel_data[channel_id] = {
            'name': snippet['title'],
            'subscribers': int(stats.get('subscriberCount', 0)),
            'hidden_subscribers': stats.get('hiddenSubscriberCount', False)
        }

# === 4. 获取每个视频的评论 ===
all_comments = {}

for video_id in video_ids:
    try:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=20,
            order='relevance',
            textFormat='plainText'
        )
        response = request.execute()
        
        comments = []
        for item in response.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'author': snippet['authorDisplayName'],
                'text': snippet['textDisplay'],
                'likes': snippet['likeCount'],
                'published': snippet['publishedAt'][:10]
            })
        
        all_comments[video_id] = comments
    except Exception as e:
        all_comments[video_id] = []  # 评论可能被禁用

# === 5. 合并数据并保存 ===
# 参考 tencent-docs skill 保存到腾讯文档
```

## 粉丝数格式化

```python
def format_subscribers(count):
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count/1_000:.1f}K"
    else:
        return str(count)
```

## 视频 ID 提取

```python
def extract_video_id(url):
    if 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    return None
```

## 错误处理

- **评论禁用**：部分视频返回空列表，需 try-except
- **隐藏粉丝**：`hiddenSubscriberCount=True` 时无法获取
- **配额超限**：每天 10,000 单位，批量操作省配额
- **无效视频ID**：搜索结果可能包含无效ID，需过滤

## 腾讯文档保存（Word 文档）

```python
import subprocess, json

# 创建文档
result = subprocess.run([
    'mcporter', 'call', 'tencent-docs', 'manage.create_file',
    'file_type=doc', 'title=文档标题', 'parent_id=文件夹ID'
], capture_output=True, text=True)
file_id = json.loads(result.stdout)['file_id']

# 写入内容（分批，每批约5000字符）
content = "Markdown内容..."
batch_size = 5000
current_index = 1

for i in range(0, len(content), batch_size):
    batch = content[i:i+batch_size]
    result = subprocess.run([
        'mcporter', 'call', 'tencent-docs', 'doc.insert_markdown',
        f'file_id={file_id}',
        f'index={current_index}',
        f'markdown={batch}'
    ], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        current_index = response.get('last_index', current_index)
```

## 实战经验

1. **YouTube Data API 是最佳方案**：100% 成功率，远超其他工具
2. **批量操作省配额**：videos.list 和 channels.list 支持最多 50 个 ID
3. **评论需要逐个获取**：commentThreads 不支持批量
4. **分批写入大文档**：腾讯文档 API 有大小限制，需分批
5. **使用 index 参数**：doc.insert_markdown 用 index 不是 pos
