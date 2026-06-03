# yt_optimizer.py endpoint 修复

## Bug

脚本 `~/.hermes/scripts/yt_optimizer.py` 的 `api_call` 函数中，endpoint 参数直接拼入 URL：

```python
# ❌ 错误：endpoint = "videos.list" → URL 变成 /youtube/v3/videos.list?...
url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{urlencode(params, safe=',')}"
```

YouTube Data API v3 的 URL endpoint 是**资源名**，不是方法名：

| ❌ 错误 | ✅ 正确 |
|---------|---------|
| `videos.list` | `videos` |
| `channels.list` | `channels` |
| `search.list` | `search` |
| `playlistItems.list` | `playlistItems` |

## 修复

在 `api_call` 函数中添加资源名提取：

```python
# 在构建 URL 前
resource = endpoint.split('.')[0] if '.' in endpoint else endpoint
url = f"https://www.googleapis.com/youtube/v3/{resource}?{urlencode(params, safe=',')}"
```

或统一使用资源名调用：

```python
api_call("videos", {...})      # ✅
api_call("videos.list", {...}) # ✅ 也能工作（自动提取）
```
