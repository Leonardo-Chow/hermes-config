#!/usr/bin/env python3
"""
YouTube Data API v3 配额优化器
- 批量请求（50 ID/次 = 1 单位）
- SQLite 本地缓存（24h TTL）
- 配额追踪 + Key 轮换
- 避免 search.list

用法:
  python3 yt_optimizer.py batch-videos vid1 vid2 vid3
  python3 yt_optimizer.py channel-uploads UC_x5XG1OV2P6uZZ5FSM9Ttw
  python3 yt_optimizer.py quota
  python3 yt_optimizer.py cleanup
"""

from __future__ import annotations
import json, sqlite3, time, hashlib, os, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import subprocess

CACHE_DIR = Path.home() / ".hermes" / "cache" / "youtube"
DB_PATH = CACHE_DIR / "yt_cache.db"
QUOTA_LOG = CACHE_DIR / "quota_log.json"
KEY_POOL_PATH = Path.home() / ".hermes" / "config" / "youtube_api_pool.json"
DAILY_QUOTA = 10000
PROXY = os.environ.get("YT_PROXY", "socks5://127.0.0.1:1082")


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
def load_keys() -> list:
    if KEY_POOL_PATH.exists():
        data = json.loads(KEY_POOL_PATH.read_text())
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "api_keys" in data:
            return data["api_keys"]
    key = os.environ.get("YOUTUBE_API_KEY", "")
    return [key] if key else []


def get_key(keys: list) -> str:
    """轮换 key：选配额消耗最少的"""
    quota = load_quota()
    best = min(keys, key=lambda k: quota.get(k, {}).get("used", 0))
    return best


# ─── 配额追踪 ───
def load_quota() -> dict:
    if QUOTA_LOG.exists():
        try:
            data = json.loads(QUOTA_LOG.read_text())
            today = time.strftime("%Y-%m-%d")
            return {k: v for k, v in data.items() if v.get("date") == today}
        except json.JSONDecodeError:
            return {}
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


def make_cache_key(prefix: str, params: dict) -> str:
    raw = f"{prefix}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(raw.encode()).hexdigest()


# ─── 缓存清理 ───
def cleanup(conn: sqlite3.Connection):
    cur = conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
    conn.commit()
    return cur.rowcount


# ─── API 调用 ───
def api_call(endpoint: str, params: dict, cost: int = 1, ttl: int = 86400) -> dict:
    """
    带缓存+配额追踪的 API 调用
    返回: {"data": {...}, "source": "cache"|"api", "cost": 0|N}
    """
    conn = init()
    ck = make_cache_key(endpoint, params)

    # 1. 查缓存
    cached = cache_get(conn, ck)
    if cached:
        conn.close()
        return {"data": cached, "source": "cache", "cost": 0}

    # 2. 检查配额
    keys = load_keys()
    if not keys:
        conn.close()
        raise RuntimeError("No YouTube API keys. Set YOUTUBE_API_KEY or configure ~/.hermes/config/youtube_api_pool.json")

    key = get_key(keys)
    remaining = get_remaining(key)
    if remaining < cost:
        for k in keys:
            if get_remaining(k) >= cost:
                key = k
                break
        else:
            conn.close()
            remaining_all = {k[-6:]: get_remaining(k) for k in keys}
            raise RuntimeError(f"All keys exhausted. Remaining: {remaining_all}")

    # 3. 调用 API（用 curl 支持 SOCKS5 代理）
    from urllib.parse import urlencode
    params["key"] = key
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{urlencode(params, safe=',')}"

    try:
        curl_cmd = ["curl", "-s", "-f", "--max-time", "30"]
        if PROXY:
            curl_cmd += ["--proxy", PROXY]
        curl_cmd += ["-H", "Accept: application/json", url]

        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=35)
        if result.returncode != 0:
            raise RuntimeError(f"curl failed (exit {result.returncode}): {result.stderr[:200]}")
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        conn.close()
        raise RuntimeError(f"Invalid JSON from YouTube API: {result.stdout[:200]}")

    # 4. 缓存 + 记录
    cache_set(conn, ck, data, ttl=ttl)
    track_usage(key, cost)
    conn.close()

    return {"data": data, "source": "api", "cost": cost}


# ─── 批量获取视频（核心优化）───
def batch_videos(video_ids: list, parts: str = "snippet,statistics", ttl: int = 86400) -> list:
    """
    批量获取视频详情，自动分片 50 ID/次
    50 个视频 = 1 单位（不是 50）
    """
    conn = init()
    results = []
    uncached_ids = []

    # 1. 查缓存
    for vid in video_ids:
        ck = make_cache_key("videos.list", {"id": vid, "part": parts})
        cached = cache_get(conn, ck)
        if cached and "items" in cached and cached["items"]:
            results.append(cached["items"][0])
        else:
            uncached_ids.append(vid)

    cache_hits = len(video_ids) - len(uncached_ids)

    # 2. 批量请求未缓存的
    api_calls = 0
    for i in range(0, len(uncached_ids), 50):
        batch = uncached_ids[i:i + 50]
        resp = api_call("videos", {
            "id": ",".join(batch),
            "part": parts,
        }, cost=1, ttl=ttl)

        items = resp["data"].get("items", [])
        results.extend(items)

        # 单独缓存每个视频
        for item in items:
            ck = make_cache_key("videos.list", {"id": item["id"], "part": parts})
            cache_set(conn, ck, {"items": [item]}, ttl=ttl)

        api_calls += 1

    conn.close()

    # 摘要
    total_cost = api_calls * 1
    print(f"[yt_optimizer] {len(video_ids)} videos: {cache_hits} cached, {api_calls} API calls, {total_cost} units", file=sys.stderr)
    return results


# ─── 获取频道上传列表（避免 search.list）───
def get_channel_uploads(channel_id: str, max_results: int = 50) -> list:
    """
    通过 playlistItems 获取频道视频，避免 search.list（省 99 单位）
    UC... → UU... 自动转换
    """
    if not channel_id.startswith("UC"):
        raise ValueError(f"Channel ID must start with UC, got: {channel_id}")

    uploads_playlist = "UU" + channel_id[2:]

    resp = api_call("playlistItems", {
        "playlistId": uploads_playlist,
        "part": "snippet,contentDetails",
        "maxResults": str(min(max_results, 50)),
    }, cost=1)

    return resp["data"].get("items", [])


# ─── 获取频道详情 ───
def get_channel(channel_id: str, parts: str = "snippet,statistics") -> dict:
    """获取频道详情 = 1 单位"""
    resp = api_call("channels", {
        "id": channel_id,
        "part": parts,
    }, cost=1)
    items = resp["data"].get("items", [])
    return items[0] if items else {}


# ─── 搜索（带缓存，仅必要时使用）───
def search_videos(query: str, max_results: int = 20, ttl: int = 86400) -> list:
    """
    关键词搜索 = 100 单位/次，结果会被缓存
    ⚠️ 配额杀手，仅在无替代方案时使用
    """
    resp = api_call("search", {
        "q": query,
        "type": "video",
        "part": "snippet",
        "maxResults": str(min(max_results, 50)),
        "order": "viewCount",
    }, cost=100, ttl=ttl)

    print(f"[yt_optimizer] ⚠️ search.list cost 100 units! Consider caching.", file=sys.stderr)
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
        lines.append(f"Key {i+1} (...{k[-6:]}): {used}/{DAILY_QUOTA} ({pct:.1f}%) | 剩余: {remaining}")
    return "\n".join(lines)


# ─── CLI ───
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Data API v3 配额优化器")
    sub = parser.add_subparsers(dest="cmd")

    # batch-videos
    p = sub.add_parser("batch-videos", help="批量获取视频详情（50 ID/次 = 1 单位）")
    p.add_argument("ids", nargs="+", help="视频 ID")
    p.add_argument("--parts", default="snippet,statistics", help="API part 参数")
    p.add_argument("--ttl", type=int, default=86400, help="缓存 TTL（秒）")
    p.add_argument("--json", action="store_true", help="输出 JSON")

    # channel-uploads
    p = sub.add_parser("channel-uploads", help="获取频道最新视频（1 单位，非 100）")
    p.add_argument("channel_id", help="频道 ID (UC...)")
    p.add_argument("--max", type=int, default=50, help="最大结果数")
    p.add_argument("--json", action="store_true", help="输出 JSON")

    # channel
    p = sub.add_parser("channel", help="获取频道详情")
    p.add_argument("channel_id", help="频道 ID (UC...)")
    p.add_argument("--parts", default="snippet,statistics")

    # search (with warning)
    p = sub.add_parser("search", help="⚠️ 关键词搜索（100 单位/次！）")
    p.add_argument("query", help="搜索关键词")
    p.add_argument("--max", type=int, default=20)
    p.add_argument("--ttl", type=int, default=86400)

    # quota
    sub.add_parser("quota", help="查看配额报告")

    # cleanup
    sub.add_parser("cleanup", help="清理过期缓存")

    args = parser.parse_args()

    if args.cmd == "batch-videos":
        items = batch_videos(args.ids, args.parts, args.ttl)
        if args.json:
            print(json.dumps(items, indent=2, ensure_ascii=False))
        else:
            for v in items:
                title = v.get("snippet", {}).get("title", "?")
                vid = v.get("id", "?")
                views = v.get("statistics", {}).get("viewCount", "?")
                print(f"  {vid} | {views:>12} views | {title}")

    elif args.cmd == "channel-uploads":
        items = get_channel_uploads(args.channel_id, args.max)
        if args.json:
            print(json.dumps(items, indent=2, ensure_ascii=False))
        else:
            for item in items:
                title = item.get("snippet", {}).get("title", "?")
                vid = item.get("contentDetails", {}).get("videoId", "?")
                pub = item.get("snippet", {}).get("publishedAt", "?")[:10]
                print(f"  {vid} | {pub} | {title}")

    elif args.cmd == "channel":
        ch = get_channel(args.channel_id, args.parts)
        print(json.dumps(ch, indent=2, ensure_ascii=False))

    elif args.cmd == "search":
        items = search_videos(args.query, args.max, args.ttl)
        print(json.dumps(items, indent=2, ensure_ascii=False))

    elif args.cmd == "quota":
        print(quota_report())

    elif args.cmd == "cleanup":
        conn = init()
        count = cleanup(conn)
        conn.close()
        print(f"Cleaned up {count} expired cache entries")

    else:
        parser.print_help()
