# YouTube Data API 批量视频详情获取

## 问题
YouTube Data API 的 `search` 端点只返回 snippet（不含完整 description），需要二次调用 `videos` 端点获取详情。

## 方案：Python 脚本写到文件再执行

由于 Hermes terminal 会 redact API key，必须用 Python 脚本获取 key 并调用 API。

### 脚本模板

```python
import subprocess, json

def get_key():
    r = subprocess.run(['python3', '/Users/zhoulong/.hermes/scripts/youtube_api_pool.py', 'current'], capture_output=True, text=True)
    return r.stdout.strip()

k = get_key()

# Step 1: 搜索获取视频ID
all_vids = set()
keywords = ["OBSBOT", "OBSBOT+Tiny+3", ...]

for kw in keywords:
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&q=" + kw + "&type=video&publishedAfter=" + UTC_START + "&publishedBefore=" + UTC_END + "&maxResults=20&key=" + k
    r = subprocess.run(['curl', '-s', '--max-time', '12', url], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        for i in d.get('items', []):
            all_vids.add(i['id']['videoId'])
    except:
        pass

# Step 2: 获取视频详情
for vid in all_vids:
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=" + vid + "&key=" + k
    r = subprocess.run(['curl', '-s', '--max-time', '12', url], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        items = d.get('items', [])
        if items:
            s = items[0]['snippet']
            desc = s.get('description', '')
            # 分析 description 中的 OBSBOT 关键词、官网链接、亚马逊链接、折扣码等
    except:
        pass
```

## 关键字段分析

从 description 中提取：
- `obsbot.com` → 官网链接
- `amazon` → 亚马逊链接
- `code/discount/coupon` → 折扣信息
- `#` → 标签/hashtags
- `obsbot/tiny/meet/tail/talent` → OBSBOT 相关性判断

## 输出格式

每个视频输出：
```
视频标题（截断80字符）
  CH: 频道名
  AT: 发布时间
  OFF:Y/N AMZ:Y/N DISC:Y/N TAG:Y/N
  DC: 描述前250字符
```

## 性能优化

- YouTube API 配额：每次 search 约 100 单位，每次 videos 约 1 单位
- 批量获取：`videos` 端点支持逗号分隔的多个 ID（最多 50 个）
- 去重：用 `set()` 存储视频 ID，避免重复查询
