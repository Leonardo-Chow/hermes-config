# YouTube 频道信息抓取技术方案

## 方法对比

| 方法 | 速度 | 稳定性 | 适用场景 |
|:-----|:-----|:-------|:---------|
| curl + 页面解析 | ⚡ 最快（~5s/频道） | ✅ 稳定 | 批量获取频道描述 |
| Tavily 搜索 | 🔶 较快 | ⚠️ 有日限额 | 少量查询、需要搜索结果 |
| yt-dlp | 🐢 最慢（易超时） | ❌ 不稳定 | 单个频道详细信息 |
| YouTube Data API | ⚡ 快 | ✅ 稳定 | 需要结构化数据（需 API Key） |

## 推荐方案：curl + YouTube 页面解析

### 原理
YouTube 频道页面 HTML 中嵌入了 `channelMetadataRenderer` JSON 对象，包含频道名称、描述、关键词等信息。

### 实现

```bash
# 获取频道页面并解析元数据
curl -s "https://www.youtube.com/channel/CHANNEL_ID" \
  | grep -o '"channelMetadataRenderer":{[^}]*}' \
  | head -1
```

### 更完整的解析（Python）

```python
import subprocess
import json
import re

def get_channel_info(channel_id):
    """获取 YouTube 频道信息"""
    url = f"https://www.youtube.com/channel/{channel_id}"
    
    # 使用 curl 抓取页面
    result = subprocess.run(
        ['curl', '-s', '-L', url],
        capture_output=True, text=True, timeout=30
    )
    
    html = result.stdout
    
    # 方法1：从 meta 标签提取
    title_match = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    desc_match = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    
    # 方法2：从嵌入 JSON 提取
    metadata_match = re.search(r'"channelMetadataRenderer":\s*(\{[^}]+\})', html)
    
    info = {
        'title': title_match.group(1) if title_match else '',
        'description': desc_match.group(1) if desc_match else '',
        'keywords': []
    }
    
    if metadata_match:
        try:
            metadata = json.loads(metadata_match.group(1))
            info['title'] = metadata.get('title', info['title'])
            info['description'] = metadata.get('description', info['description'])
            info['keywords'] = metadata.get('keywords', '').split(',') if metadata.get('keywords') else []
        except json.JSONDecodeError:
            pass
    
    return info

# 使用示例
channels = [
    'UC5lDVbmgb-sAcx2fjwy3KQA',  # Booredatwork.com
    'UCSLeoz5odIGS2GdlbHbCAUg',  # Matthew Encina
]

for ch_id in channels:
    info = get_channel_info(ch_id)
    print(f"Title: {info['title']}")
    print(f"Description: {info['description'][:200]}")
    print(f"Keywords: {info['keywords'][:5]}")
    print("---")
```

### 使用 Jina Reader（更稳定）

```bash
# 通过 Jina Reader 获取，返回 Markdown 格式
curl -s "https://r.jina.ai/https://www.youtube.com/channel/CHANNEL_ID" \
  | head -100
```

## 并行处理方案

### 使用 delegate_task 分路并行

```python
# 将频道列表分成 3 组，每组 6-7 个
# 每组用一个 subagent 并行处理
delegate_task(tasks=[
    {"goal": "获取频道信息：频道1、频道2...", "toolsets": ["terminal"]},
    {"goal": "获取频道信息：频道3、频道4...", "toolsets": ["terminal"]},
    {"goal": "获取频道信息：频道5、频道6...", "toolsets": ["terminal"]},
])
```

### 批量处理脚本

```python
import subprocess
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_channel(channel_id):
    """并行获取单个频道信息"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', f'https://www.youtube.com/channel/{channel_id}'],
            capture_output=True, text=True, timeout=30
        )
        
        title_match = re.search(r'<meta property="og:title" content="([^"]*)"', result.stdout)
        desc_match = re.search(r'<meta property="og:description" content="([^"]*)"', result.stdout)
        
        return {
            'channel_id': channel_id,
            'title': title_match.group(1) if title_match else '',
            'description': desc_match.group(1) if desc_match else '',
            'success': True
        }
    except Exception as e:
        return {
            'channel_id': channel_id,
            'error': str(e),
            'success': False
        }

# 并行获取
channels = ['UC5lDVbmgb-sAcx2fjwy3KQA', 'UCSLeoz5odIGS2GdlbHbCAUg', ...]

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(fetch_channel, ch): ch for ch in channels}
    results = {}
    for future in as_completed(futures):
        result = future.result()
        results[result['channel_id']] = result
```

## 常见问题

### Q: curl 返回空内容？
A: YouTube 可能检测到爬虫，尝试：
1. 添加 User-Agent：`curl -A "Mozilla/5.0..." ...`
2. 使用代理：`curl -x http://127.0.0.1:1082 ...`
3. 使用 Jina Reader 作为备用

### Q: Tavily 日限额用完了？
A: 直接用 curl 方案，不依赖 Tavily。

### Q: yt-dlp 超时？
A: yt-dlp 会下载视频元数据，非常慢。批量获取频道描述时不要用 yt-dlp。

### Q: 需要获取频道的最新视频？
A: 使用 YouTube Data API（需要 API Key），或用 yt-dlp 但只获取最新 1 个视频：
```bash
yt-dlp --dump-json --playlist-items 1 "https://www.youtube.com/channel/CHANNEL_ID/videos"
```
