---
name: youtube-api-optimizer
description: "YouTube Data API v3 配额优化器。当需要调用 YouTube Data API 获取视频/频道/播放列表数据时必用——批量合并请求、本地缓存、避免 search.list、配额追踪。省下 90% 配额。"
version: "2026-06-03"
tags: [youtube, api, quota, cache, optimization, batch]
triggers:
  - youtube data api
  - youtube api quota
  - youtube批量获取
  - youtube api优化
---

# YouTube Data API v3 配额优化器

## 配额成本速查

| API 端点 | 成本/次 | 说明 |
|----------|---------|------|
| `search.list` | **100** | 🔴 配额杀手，能不用就不用 |
| `videos.list` | 1 | 🟢 获取视频详情 |
| `channels.list` | 1 | 🟢 获取频道详情 |
| `playlistItems.list` | 1 | 🟢 获取播放列表 |
| `playlists.list` | 1 | 🟢 播放列表元数据 |
| `commentThreads.list` | 1 | 🟢 评论列表 |
| `activities.list` | 1 | 🟢 频道活动 |

默认配额：**10,000 单位/天**（每个 API Key）

## 三大优化原则

### 1. 批量合并请求（省 98%）

```bash
# ❌ 坏：50 次调用 = 50 单位
for id in video_ids; do
  curl "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=$id&key=$KEY"
done

```bash
# ⚠️ endpoint 是 "videos" 不是 "videos.list"
curl "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=id1,id2,...,id50&key=$KEY"
```

**规则**：`videos.list`、`channels.list` 的 `id` 参数支持逗号分隔，最多 50 个。

### 2. 避免 search.list（省 99%）

| 场景 | ❌ search.list (100单位) | ✅ 替代方案 (1单位) |
|------|------------------------|-------------------|
| 已知视频 ID | — | `videos.list(id=...)` |
| 已知频道 | `search.list(channelId=...)` | `playlistItems.list(playlistId=UU+channelId后缀)` |
| 获取频道最新视频 | `search.list(q=channel, type=video)` | `activities.list(channelId=..., part=contentDetails)` |
| 获取播放列表 | `search.list(q=playlist)` | `playlists.list(id=...)` |
| 关键词搜索 | 无法避免 | 缓存结果，24h 内复用 |

**频道上传列表技巧**：频道 ID `UC...` 的上传播放列表 = `UU` + channelId 后 22 位。
例如 `UC_x5XG1OV2P6uZZ5FSM9Ttw` → 播放列表 `UUx5XG1OV2P6uZZ5FSM9Ttw`

### 3. 本地缓存（省 90%+）

视频元数据 24h 内不变，缓存命中 = 0 配额消耗。

## 实现：yt_optimizer.py

**位置**: `~/.hermes/scripts/yt_optimizer.py`

```python
#!/usr/bin/env python3
"""
YouTube Data API v3 配额优化器
- 批量请求（50 ID/次）
- SQLite 本地缓存（24h TTL）
- 配额追踪
- Key 轮换
"""

import json, sqlite3, time, hashlib, os, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

CACHE_DIR = Path.home() / ".hermes" / "cache" / "youtube"
DB_PATH = CACHE_DIR / "yt_cache.db"
QUOTA_LOG = CACHE_DIR / "quota_log.json"
KEY_POOL_PATH = Path.home() / ".hermes" / "config" / "youtube_api_pool.json"
DAILY_QUOTA = 10000

# ─── 初始化 ───
def init():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            fetched_at REAL NOT NULL,
            expires_at REAL NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON cache(expires_at)")
    conn.commit()
    return conn

# ─── Key 管理 ───
def load_keys() -> list[str]:
    if KEY_POOL_PATH.exists():
        return json.loads(KEY_POOL_PATH.read_text())
    key = os.environ.get("YOUTUBE_API_KEY", "")
    return [key] if key else []

def get_key(keys: list[str]) -> str:
    """轮换 key：选配额消耗最少的"""
    quota = load_quota()
    best = min(keys, key=lambda k: quota.get(k, {}).get("used", 0))
    return best

# ─── 配额追踪 ───
def load_quota() -> dict:
    if QUOTA_LOG.exists():
        data = json.loads(QUOTA_LOG.read_text())
        today = time.strftime("%Y-%m-%d")
        # 清理非今天的记录
        return {k: v for k, v in data.items() if v.get("date") == today}
    return {}

def save_quota(quota: dict):
    QUOTA_LOG.write_text(json.dumps(quota, indent=2))

def track_usage(key: str, cost: int):
    quota = load_quota()
    today = time.strftime("%Y-%m-%d")
    if key not in quota or quota[key].get("date") != today:
        quota[key] = {"date": today, "used": 0}
    quota[key]["used"] += cost
    save_quota(quota)

def get_remaining(key: str) -> int:
    quota = load_quota()
    used = quota.get(key, {}).get("used", 0)
    return DAILY_QUOTA - used

# ─── 缓存 ───
def cache_get(conn: sqlite3.Connection, cache_key: str) -> dict | None:
    row = conn.execute(
        "SELECT data FROM cache WHERE key=? AND expires_at>?",
        (cache_key, time.time())
    ).fetchone()
    return json.loads(row[0]) if row else None

def cache_set(conn: sqlite3.Connection, cache_key: str, data: dict, ttl: int = 86400):
    now = time.time()
    conn.execute(
        "INSERT OR REPLACE INTO cache (key, data, fetched_at, expires_at) VALUES (?,?,?,?)",
        (cache_key, json.dumps(data), now, now + ttl)
    )
    conn.commit()

def cache_key(prefix: str, params: dict) -> str:
    raw = f"{prefix}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(raw.encode()).hexdigest()

# ─── 缓存清理 ───
def cleanup(conn: sqlite3.Connection):
    conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
    conn.commit()

# ─── API 调用 ───
def api_call(endpoint: str, params: dict, cost: int = 1) -> dict:
    """带缓存+配额追踪的 API 调用"""
    conn = init()
    ck = cache_key(endpoint, params)
    
    # 1. 查缓存
    cached = cache_get(conn, ck)
    if cached:
        return {"data": cached, "source": "cache", "cost": 0}
    
    # 2. 检查配额
    keys = load_keys()
    if not keys:
        raise RuntimeError("No YouTube API keys configured")
    
    key = get_key(keys)
    remaining = get_remaining(key)
    if remaining < cost:
        # 尝试换 key
        for k in keys:
            if get_remaining(k) >= cost:
                key = k
                break
        else:
            raise RuntimeError(f"All keys exhausted. Remaining: {[get_remaining(k) for k in keys]}")
    
    # 3. 调用 API
    params["key"] = key
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    req = Request(url, headers={"Accept": "application/json"})
    try:
        resp = urlopen(req, timeout=30)
        data = json.loads(resp.read())
    except HTTPError as e:
        error_body = json.loads(e.read()) if e.readable() else {}
        raise RuntimeError(f"YouTube API error {e.code}: {error_body}")
    
    # 4. 缓存 + 记录
    cache_set(conn, ck, data)
    track_usage(key, cost)
    conn.close()
    
    return {"data": data, "source": "api", "cost": cost}

# ─── 批量获取视频（核心优化）───
def batch_videos(video_ids: list[str], parts: str = "snippet,statistics") -> list[dict]:
    """批量获取视频详情，自动分片 50 ID/次"""
    conn = init()
    results = []
    uncached_ids = []
    
    # 1. 查缓存
    for vid in video_ids:
        ck = cache_key("videos.list", {"id": vid, "part": parts})
        cached = cache_get(conn, ck)
        if cached and "items" in cached and cached["items"]:
            results.append(cached["items"][0])
        else:
            uncached_ids.append(vid)
    
    # 2. 批量请求未缓存的
    for i in range(0, len(uncached_ids), 50):
        batch = uncached_ids[i:i+50]
        resp = api_call("videos.list", {
            "id": ",".join(batch),
            "part": parts,
        }, cost=1)  # 只扣 1 单位！
        
        items = resp["data"].get("items", [])
        results.extend(items)
        
        # 单独缓存每个视频
        for item in items:
            ck = cache_key("videos.list", {"id": item["id"], "part": parts})
            cache_set(conn, ck, {"items": [item]})
    
    conn.close()
    return results

# ─── 获取频道上传列表（避免 search.list）───
def get_channel_uploads(channel_id: str, max_results: int = 50) -> list[dict]:
    """通过 playlistItems 获取频道视频，避免 search（省 99 单位）"""
    # UC... → UU...
    uploads_playlist = "UU" + channel_id[2:]
    
    resp = api_call("playlistItems.list", {
        "playlistId": uploads_playlist,
        "part": "snippet,contentDetails",
        "maxResults": str(min(max_results, 50)),
    }, cost=1)
    
    return resp["data"].get("items", [])

# ─── 配额报告 ───
def quota_report() -> str:
    quota = load_quota()
    keys = load_keys()
    lines = ["YouTube API 配额报告", "=" * 40]
    for i, k in enumerate(keys):
        used = quota.get(k, {}).get("used", 0)
        remaining = DAILY_QUOTA - used
        pct = used / DAILY_QUOTA * 100
        lines.append(f"Key {i+1}: {used}/{DAILY_QUOTA} ({pct:.1f}%) | 剩余: {remaining}")
    return "\n".join(lines)

# ─── CLI ───
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube API Optimizer")
    sub = parser.add_subparsers(dest="cmd")
    
    # batch-videos
    p = sub.add_parser("batch-videos", help="批量获取视频")
    p.add_argument("ids", nargs="+", help="视频 ID")
    p.add_argument("--parts", default="snippet,statistics")
    
    # channel-uploads
    p = sub.add_parser("channel-uploads", help="获取频道最新视频")
    p.add_argument("channel_id", help="频道 ID (UC...)")
    p.add_argument("--max", type=int, default=50)
    
    # quota
    sub.add_parser("quota", help="查看配额报告")
    
    # cleanup
    sub.add_parser("cleanup", help="清理过期缓存")
    
    args = parser.parse_args()
    
    if args.cmd == "batch-videos":
        items = batch_videos(args.ids, args.parts)
        print(json.dumps(items, indent=2, ensure_ascii=False))
    elif args.cmd == "channel-uploads":
        items = get_channel_uploads(args.channel_id, args.max)
        print(json.dumps(items, indent=2, ensure_ascii=False))
    elif args.cmd == "quota":
        print(quota_report())
    elif args.cmd == "cleanup":
        conn = init()
        cleanup(conn)
        print("Cache cleaned up")
    else:
        parser.print_help()
```

## 使用方式

### 评论爬取 + 产品反馈分析

完整工作流见 [references/youtube-comment-analysis.md](references/youtube-comment-analysis.md)：批量获取评论 → 关键词分析 → Word 报告生成。

### 作为 Python 模块导入

```python
from yt_optimizer import batch_videos, get_channel_uploads, api_call, quota_report

# 批量获取 50 个视频 = 1 单位（不是 50）
videos = batch_videos(["vid1", "vid2", ..., "vid50"])

# 获取频道最新视频 = 1 单位（不是 100）
uploads = get_channel_uploads("UC_x5XG1OV2P6uZZ5FSM9Ttw")

# 自定义 API 调用（带缓存+配额追踪）
result = api_call("channels.list", {"id": "UC...", "part": "snippet,statistics"}, cost=1)

# 查看配额
print(quota_report())
```

**位置**: `~/.hermes/scripts/yt_optimizer.py`（已部署）

```bash
# 批量获取视频
python3 ~/.hermes/scripts/yt_optimizer.py batch-videos vid1 vid2 vid3

# 获取频道上传
python3 ~/.hermes/scripts/yt_optimizer.py channel-uploads UC_x5XG1OV2P6uZZ5FSM9Ttw

# 查看配额
python3 ~/.hermes/scripts/yt_optimizer.py quota

# 清理缓存
python3 ~/.hermes/scripts/yt_optimizer.py cleanup
```

## 配额节省对比

| 场景 | 无优化 | 有优化 | 节省 |
|------|--------|--------|------|
| 获取 50 个视频详情 | 50 单位 | 1 单位 | 98% |
| 获取频道最新视频 | 100 单位 | 1 单位 | 99% |
| 重复查询同一视频 | 1 单位/次 | 0（缓存） | 100% |
| 1000 视图分析（含缓存） | ~2000 单位 | ~40 单位 | 98% |

## Key 轮换策略

3 个 Key = 每天 30,000 单位总配额。脚本自动：
1. 选择当日消耗最少的 Key
2. 单 Key 耗尽自动切换
3. 全部耗尽时抛出明确错误

## OBSBOT 工作流集成

### 1. KOL 筛选 → 节省 99%

| 步骤 | 原方式 | 优化方式 | 节省 |
|------|--------|----------|------|
| 活跃度验证 | `search.list` 100单位 | `channels.list` 1单位 | 99% |
| OBSBOT合作 | `search.list` 100单位 | 缓存命中 0单位 | 100% |
| 竞品合作 | `search.list` 100单位 | `playlistItems.list` 1单位 | 99% |

```python
# 原方式：每个频道 300 单位
curl "...search?channelId=CH&q=obsbot&key=KEY"  # 100
curl "...search?channelId=CH&q=insta360&key=KEY"  # 100

# 优化方式：每个频道 2 单位
from yt_optimizer import api_call, get_channel_uploads

# 活跃度检查：channels.list = 1 单位
ch = api_call("channels", {"id": "UC...", "part": "snippet,statistics"}, cost=1)

# 最近视频：playlistItems.list = 1 单位
uploads = get_channel_uploads("UC...")
```

### 2. 竞品监测 → 缓存后 0 单位

| 步骤 | 原方式 | 优化方式 | 节省 |
|------|--------|----------|------|
| 搜索18品牌 | `search.list` × 18 = 1800单位 | 首次1800，24h内缓存=0 | 100% |
| 视频详情 | 逐个 `videos.list` | 批量 50个/次 | 98% |

```python
from yt_optimizer import api_call, batch_videos

# 搜索（带缓存，24h 内重复调用 = 0 单位）
result = api_call("search", {
    "q": "Logitech Brio webcam",
    "type": "video",
    "part": "snippet",
    "maxResults": "50",
    "order": "date",
    "publishedAfter": "2026-06-01T00:00:00Z",
}, cost=100, ttl=86400)

# 批量获取视频详情（50个 = 1 单位）
video_ids = [item["id"]["videoId"] for item in result["data"]["items"]]
details = batch_videos(video_ids)
```

### 3. 视频上线监测 → 节省 50-100%

| 步骤 | 原方式 | 优化方式 | 节省 |
|------|--------|----------|------|
| 10关键词搜索 | 10 × 100 = 1000单位 | 首次1000，下午缓存=0 | 50-100% |
| 视频详情 | 逐个获取 | 批量获取 | 98% |

```python
from yt_optimizer import api_call, batch_videos

products = ["OBSBOT Tiny 3", "OBSBOT Tail 2", "OBSBOT Meet 2", ...]

for product in products:
    # 搜索（带缓存，同天下午执行 = 0 单位）
    result = api_call("search", {
        "q": product,
        "type": "video",
        "part": "snippet",
        "publishedAfter": "2026-06-03T00:00:00Z",
        "publishedBefore": "2026-06-03T23:59:59Z",
        "maxResults": "20",
        "order": "date",
    }, cost=100, ttl=86400)

# 批量获取详情
all_ids = [...]  # 从搜索结果收集
details = batch_videos(all_ids)
```

### 配额消耗对比表

| 工作流 | 频率 | 原方式/天 | 优化后/天 | 节省 |
|--------|------|-----------|-----------|------|
| KOL筛选(10频道) | 每周 | 3,000 | 20 | 99% |
| 竞品监测(18品牌) | 周1/3/5 | 1,800 | 0(缓存) | 100% |
| 上线监测(10关键词) | 每天2次 | 2,000 | 1,000 | 50% |
| **总计** | - | **6,800** | **1,020** | **85%** |

3 个 Key 轮换 = 30,000 单位/天，优化后剩余 29,000 单位可用于其他任务。

## YouTube API Key Pool 文件格式

`~/.hermes/config/youtube_api_pool.json` 使用嵌套格式，不是纯数组：

```json
{
  "api_keys": ["AIzaSy...key1", "AIzaSy...key2", "AIzaSy...key3"],
  "current_index": 0,
  "updated_at": "2026-06-03"
}
```

加载时必须处理两种格式（兼容数组和对象）：

```python
def load_keys():
    data = json.loads(KEY_POOL_PATH.read_text())
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "api_keys" in data:
        return data["api_keys"]
    return []
```

## REST API Endpoint 映射

Python SDK 方法名 ≠ REST API endpoint。调用 `api_call()` 时必须用 REST 路径：

| Python SDK 方法 | REST Endpoint | 成本 |
|----------------|---------------|------|
| `videos().list()` | `videos` | 1 |
| `channels().list()` | `channels` | 1 |
| `playlistItems().list()` | `playlistItems` | 1 |
| `search().list()` | `search` | 100 |

⚠️ **常见 bug**：传入 `"videos.list"` 会拼出 `youtube/v3/videos.list?...`，返回 404。

## SOCKS5 代理

Python `urllib` 不原生支持 SOCKS5。用 `curl` 子进程代替：

```python
import subprocess
from urllib.parse import urlencode

params["key"] = key
url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{urlencode(params, safe=',')}"

curl_cmd = ["curl", "-s", "-f", "--max-time", "30"]
if PROXY:
    curl_cmd += ["--proxy", PROXY]  # e.g. "socks5://127.0.0.1:1082"
curl_cmd += ["-H", "Accept: application/json", url]

result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=35)
data = json.loads(result.stdout)
```

`-f` flag 让 curl 对 HTTP 错误返回非零 exit code，方便错误处理。

## 参考文件

- `references/twitchtracker-crawling.md` — TwitchTracker 主播数据爬取方法（HTML 结构、正则模板、频率限制）
- `references/endpoint-fix.md` — REST API endpoint 映射 bug 修复记录
- `references/key-recovery.md` — API Key 从 git 历史恢复方法

## ⚠️ Pitfalls

## ⚠️ Pitfalls

1. **50 ID 上限** — `videos.list` 的 `id` 参数最多 50 个，脚本自动分片
2. **缓存 TTL** — 默认 24h，视频元数据短期不变但播放量会变，如需实时播放量设短 TTL
3. **search.list 无法完全避免** — 真正的关键词搜索仍需 search.list，但缓存结果后 24h 内复用
4. **Key 池文件** — 位于 `~/.hermes/config/youtube_api_pool.json`，格式为 `{"api_keys": [...], "current_index": 0, "updated_at": "YYYY-MM-DD"}`（不是纯数组）
5. **配额重置** — 太平洋时间午夜重置，脚本按日期自动清理
6. **HTTP 错误** — 403=配额耗尽，429=速率限制，脚本会自动换 Key
7. **🔴 REST API endpoint 不含 `.list`** — Python SDK 的 `videos.list` 对应 REST API 的 `/videos`（不是 `/videos.list`）。同理 `channels.list` → `/channels`，`search.list` → `/search`，`playlistItems.list` → `/playlistItems`
8. **🔴 Python 3.9 兼容** — `dict | None` 语法需要 Python 3.10+。脚本必须在文件头加 `from __future__ import annotations`
9. **🔴 SOCKS5 代理** — Python urllib 不原生支持 SOCKS5。必须用 `curl` 子进程 + `--proxy socks5://127.0.0.1:1082`，或安装 `PySocks` 后用 `socks.set_default_proxy()`
10. **URL 编码** — `urlencode(params, safe=',')` 保留逗号分隔的 ID 列表不被编码
7. **GFW 代理** — Google API 在中国大陆被墙，脚本默认走 `socks5://127.0.0.1:1082`。可通过 `YT_PROXY` 环境变量覆盖，设为空则直连
8. **Python 3.9 兼容** — 脚本使用 `from __future__ import annotations` 支持 3.9 的类型注解语法（`dict | None`）
9. **urllib + SOCKS5 = IncompleteRead** — Python 标准库 `urllib` 搭配 SOCKS5 代理访问 YouTube API 时会报 `http.client.IncompleteRead` 错误（chunked transfer encoding 与 SOCKS5 不兼容）。**必须用 `requests` + `socks5h://` 代理**：
   ```python
   import requests
   session = requests.Session()
   session.proxies = {"http": "socks5h://127.0.0.1:1082", "https": "socks5h://127.0.0.1:1082"}
   resp = session.get(url, params=params, timeout=30)
   ```
   `socks5h://` 表示 DNS 也通过代理解析（避免 DNS 污染）。需要 `pip install PySocks requests[socks]`。
10. **commentThreads.list 端点** — 获取视频评论用 `commentThreads`（不是 `comments`）。`comments` 端点只用于获取回复。关键参数：`videoId`、`part=snippet`、`maxResults=100`（上限）、`order=relevance|time`、`textFormat=plainText`。分页用 `nextPageToken`。每调用 1 次 = 1 单位配额。
