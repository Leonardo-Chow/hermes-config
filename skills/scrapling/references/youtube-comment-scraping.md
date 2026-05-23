# YouTube Comment Scraping via API

## Overview

YouTube comments can be scraped via the Data API v3 `commentThreads` endpoint. This is more reliable than browser scraping for comments.

**API Key:** See memory for YouTube Data API v3 key.

## Python Pattern

```python
import json
import requests
import time

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://www.googleapis.com/youtube/v3"

def get_video_comments(video_id, max_comments=100):
    """获取视频评论（按相关性排序）"""
    comments = []
    page_token = None
    
    while len(comments) < max_comments:
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(100, max_comments - len(comments)),
            "order": "relevance",  # 按相关性排序（热门评论优先）
            "textFormat": "plainText",
            "key": API_KEY
        }
        if page_token:
            params["pageToken"] = page_token
        
        try:
            response = requests.get(f"{BASE_URL}/commentThreads", params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    top_comment = snippet.get("topLevelComment", {}).get("snippet", {})
                    
                    comments.append({
                        "comment_id": item.get("id", ""),
                        "video_id": video_id,
                        "author": top_comment.get("authorDisplayName", ""),
                        "text": top_comment.get("textDisplay", ""),
                        "like_count": top_comment.get("likeCount", 0),
                        "published_at": top_comment.get("publishedAt", ""),
                        "reply_count": snippet.get("totalReplyCount", 0),
                    })
                
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
            elif response.status_code == 403:
                error_msg = response.json().get("error", {}).get("message", "")
                if "commentsDisabled" in str(response.json()):
                    return comments, "comments_disabled"
                elif "quotaExceeded" in error_msg:
                    return comments, "quota_exceeded"
                break
            elif response.status_code == 404:
                return comments, "not_found"
            else:
                return comments, f"error_{response.status_code}"
        except Exception as e:
            return comments, "exception"
        
        time.sleep(0.05)  # API 限流保护
    
    return comments, "success"
```

## Batch Processing Pattern

```python
# 批量获取多个视频的评论
all_comments = []
video_stats = []
quota_exceeded = False

for i, video in enumerate(videos):
    video_id = video.get("video_id")
    
    if quota_exceeded:
        continue
    
    comments, status = get_video_comments(video_id, max_comments=100)
    
    if status == "quota_exceeded":
        quota_exceeded = True
    
    all_comments.extend(comments)
    video_stats.append({
        "video_id": video_id,
        "comment_count": len(comments),
        "status": status
    })
    
    # 每 10 个视频保存一次中间结果
    if (i + 1) % 10 == 0:
        with open("/tmp/comments_progress.json", "w") as f:
            json.dump({"total_comments": len(all_comments), "comments": all_comments}, f)
    
    time.sleep(0.1)
```

## Data Cleaning

```python
import re

def clean_comments(comments):
    """清洗评论数据"""
    cleaned = []
    for c in comments:
        text = c.get("text", "").strip()
        
        # 跳过空评论
        if not text:
            continue
        
        # 跳过过短评论（< 3 字符）
        if len(text) < 3:
            continue
        
        # 跳过纯表情/符号
        text_no_emoji = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', '', text)
        text_no_symbols = re.sub(r'[^\w\s]', '', text_no_emoji).strip()
        if len(text_no_symbols) < 2:
            continue
        
        # 清洗文本
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > 500:
            text = text[:500] + "..."
        
        c["text"] = text
        cleaned.append(c)
    
    return cleaned
```

## Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| `success` | 正常获取 | 继续 |
| `comments_disabled` | 评论已禁用 | 跳过该视频 |
| `quota_exceeded` | API 配额超限 | 停止所有请求 |
| `not_found` | 视频不存在 | 跳过 |
| `error_403` | 其他 403 错误 | 记录并跳过 |
| `exception` | 网络异常 | 重试或跳过 |

## Pitfalls

- **配额限制**: YouTube API 每日配额有限（默认 10,000 units），每个 commentThreads 请求消耗 1 unit
- **评论禁用**: 部分视频禁用评论，返回 403
- **reply_count**: 只返回顶级评论数，不包含回复内容；获取回复需要额外请求
- **排序**: `order=relevance` 返回热门评论，`order=time` 返回最新评论
- **textDisplay vs textOriginal**: `textDisplay` 包含 HTML 格式，`textOriginal` 是纯文本
