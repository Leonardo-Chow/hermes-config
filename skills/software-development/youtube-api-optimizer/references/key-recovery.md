# YouTube API Key 恢复与配置

## Key 池文件格式

`~/.hermes/config/youtube_api_pool.json` 支持两种格式：

```json
// 格式1：数组
["key1", "key2", "key3"]

// 格式2：对象（推荐）
{
  "api_keys": ["key1", "key2", "key3"],
  "current_index": 0,
  "updated_at": "2026-06-03"
}
```

## 从 Git 历史恢复 Key

如果 key 被替换为占位符，可以从 git 历史恢复：

```bash
cd ~/.hermes && git log --all -p -- config/youtube_api_pool.json 2>/dev/null \
  | grep -o 'AIzaSy[a-zA-Z0-9_-]\{33\}' | sort -u
```

## API Endpoint 注意事项

YouTube Data API v3 的 endpoint 是资源名，不是方法名：

| ❌ 错误 | ✅ 正确 |
|---------|---------|
| `videos.list` | `videos` |
| `channels.list` | `channels` |
| `search.list` | `search` |
| `playlistItems.list` | `playlistItems` |

URL 格式：`https://www.googleapis.com.youtube.com/youtube/v3/{resource}?{params}`

## Python urllib vs curl

Python 的 `urllib` 不原生支持 SOCKS5 代理。两种解决方案：

1. **用 curl 子进程**（推荐，零依赖）：`subprocess.run(["curl", "--proxy", "socks5://..."])`
2. **安装 PySocks**：`pip install pysocks` 然后 `urllib` 自动支持

## 代理配置

- 默认代理：`socks5://127.0.0.1:1082`（Shadowrocket）
- 环境变量覆盖：`YT_PROXY=socks5://...`
- GFW 环境下 Google APIs 必须走代理
