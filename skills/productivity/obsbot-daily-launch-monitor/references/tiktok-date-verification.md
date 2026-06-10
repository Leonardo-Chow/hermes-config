# TikTok 日期验证策略

## 核心原则

**所有 TikTok 视频必须通过 ID 解码验证发布日期**，不能只靠搜索引擎返回的"X天前"。

## 视频 ID 解码

TikTok 视频 ID 是一个 64 位整数，其中高 32 位是 Unix 时间戳：

```python
import datetime

def decode_tiktok_date(video_id):
    """从 TikTok 视频 ID 提取精确发布时间"""
    timestamp = int(video_id) >> 32
    return datetime.datetime.fromtimestamp(timestamp)

# 示例
video_id = "7513089494989898989"
dt = decode_tiktok_date(video_id)
print(f"发布时间: {dt}")  # 精确到秒
```

## 数据源优先级

| 优先级 | 数据源 | 日期可靠性 | 说明 |
|:-------|:-------|:-----------|:-----|
| 1 | ScrapeCreators hashtag | 有日期字段 | 最可靠，hashtag 比 keyword 搜索更好 |
| 2 | oembed API | 无日期字段 | 需配合 ID 解码获取日期 |
| 3 | Omar API | 有日期字段 | 100次/月，HD下载 |
| 4 | web_search | 不可靠 | 索引延迟 1-3 天，"X天前"需换算 |

## 浏览器"X天前"换算

```python
from datetime import datetime, timedelta

def parse_relative_date(text):
    """解析 '3 days ago', '1 week ago' 等相对日期"""
    if "day" in text:
        days = int(text.split()[0])
        return datetime.now() - timedelta(days=days)
    elif "week" in text:
        weeks = int(text.split()[0])
        return datetime.now() - timedelta(weeks=weeks)
    elif "hour" in text:
        hours = int(text.split()[0])
        return datetime.now() - timedelta(hours=hours)
    return None
```

## 2026-06-10 教训

- web_search 返回的视频显示"3 days ago"、"5 days ago"，但这些不是今天的内容
- 通过 ID 解码发现实际发布日期为 6月3日-6月7日，超出搜索范围
- 正确做法：先 ID 解码，再判断是否在日期范围内

## 已知 OBSBOT TikTok 账号

- @obsbot（OBSBOT Official，17.5K 粉丝）
- @obsbotmy1（obsbotmy）
- @psscreativemedia（PSS Creative Media）
- @mrsmobster（MrsMobster）
- @maccagames（MaccaGames）
- @brainiacvp（BrainiacVP）
- @obsbot.thailand
- @obsbotsingapore
- @gabyxhd
- @clemoeevents
