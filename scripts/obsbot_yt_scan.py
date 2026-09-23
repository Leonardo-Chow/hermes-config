#!/usr/bin/env python3
"""OBSBOT YouTube 上线监测扫描器。

用法:  python3 obsbot_yt_scan.py 2026-09-14 [2026-09-15 ...]
输出:  按真实 publishedAt(UTC) 归组的候选列表，已去黑名单/官方，带时长/播放量/过滤标记。
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

POOL = "/Users/zhoulong/.hermes/config/youtube_api_pool.json"
KEY_FILES = ["/tmp/scan3day.py", "/tmp/weekend_scan.py"]
API_KEY = None


def _valid(k):
    try:
        u = ("https://www.googleapis.com/youtube/v3/videos?part=id"
             f"&id=dQw4w9WgXcQ&key={k}")
        urllib.request.urlopen(u, timeout=15).read()
        return True
    except Exception:  # noqa: BLE001
        return False


try:
    _pool = json.load(open(POOL))
    for _k in _pool.get("api_keys", []):
        if _valid(_k):
            API_KEY = _k
            break
except Exception:  # noqa: BLE001
    pass

if not API_KEY:
    for _f in KEY_FILES:
        try:
            API_KEY = re.search(r"(AIzaSy[A-Za-z0-9_\-]{33})", open(_f).read()).group(1)
            break
        except Exception:  # noqa: BLE001
            continue

if not API_KEY:
    sys.exit("未找到可用 YouTube API key（检查 youtube_api_pool.json）")

KWS = ["OBSBOT", "OBSBOT Tiny 3", "OBSBOT Tiny 3 Lite", "OBSBOT Tiny 2", "OBSBOT Tiny 2 Lite",
       "OBSBOT Tail 2", "OBSBOT Meet Flip", "OBSBOT Meet SE", "OBSBOT Meet 2", "OBSBOT Meet",
       "OBSBOT Talent", "OBSBOT Vox", "OBSBOT review", "OBSBOT unboxing", "OBSBOT webcam"]

BLACKLIST = {"UnboxingMyBuys", "Gadget Theory", "Gadget Savvy", "BrujulaDelUnboxing",
             "Chia Se Thong Tin", "CreatorFinds", "Pickfolio", "Su Lo", "Ha Vu", "SAM"}

# 🔴 已发布台账：曾出现在历史报告里的 video ID 一律不再二次出现（2026-09-20 用户要求）
LEDGER = "/Users/zhoulong/.hermes/config/obsbot_reported_videos.json"


def load_ledger():
    try:
        with open(LEDGER) as f:
            return json.load(f).get("videos", {})
    except Exception:  # noqa: BLE001
        return {}


def mark_reported(vids, date=None, meta=None):
    """把 video ID 写入台账，避免下次报告重复出现。"""
    import datetime
    import os
    data = {"videos": load_ledger()}
    date = date or datetime.date.today().isoformat()
    meta = meta or {}
    added = 0
    for vid in vids:
        if vid not in data["videos"]:
            added += 1
        m = meta.get(vid, {})
        data["videos"][vid] = {"reported": date,
                               "channel": m.get("ch", ""),
                               "title": m.get("title", "")}
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
    return added


def api(path, params):
    params["key"] = API_KEY
    url = f"https://www.googleapis.com/youtube/v3/{path}?" + urllib.parse.urlencode(params)
    err = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as f:
                return json.load(f)
        except Exception as e:  # noqa: BLE001
            err = str(e)
            time.sleep(2)
    return {"error": err}


def datetime_yesterday():
    """默认扫描目标 = 昨天（北京时间早跑前一天 UTC）。"""
    import datetime
    return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


def iso2sec(s):
    if not s:
        return -1
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    if not m:
        return -1
    dd, h, mi, sec = (int(x) if x else 0 for x in m.groups())
    return dd * 86400 + h * 3600 + mi * 60 + sec


def fmt(sec):
    if sec < 0:
        return "?"
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s"


def main(days):
    lo, hi = min(days), max(days)
    ids = set()
    # ⚠️ 不要用 publishedAfter/publishedBefore —— YouTube search 的窗口参数会漏视频
    # （2026-09-15 实测：窗口法只找到 12 条，order=date 全量扫描找到 37 条）。
    # 正确做法：order=date 拉最近 50 条，再用 videos.list 的 publishedAt 客户端过滤。
    for kw in KWS:
        d = api("search", {"part": "snippet", "q": kw, "type": "video",
                           "order": "date", "maxResults": 50})
        for i in d.get("items", []):
            vid = i["id"].get("videoId")
            if vid:
                ids.add(vid)
        time.sleep(0.15)

    print(f"搜索窗口 {lo} ~ {hi} | 命中 {len(ids)} 条 | 拉取详情...")

    rows = []
    idlist = sorted(ids)
    for k in range(0, len(idlist), 50):
        d = api("videos", {"part": "snippet,contentDetails,statistics",
                           "id": ",".join(idlist[k:k + 50])})
        for it in d.get("items", []):
            s = it["snippet"]
            ch = s["channelTitle"]
            title = s["title"]
            if "obsbot" not in title.lower() and "obsbot" not in ch.lower():
                continue
            if ch in BLACKLIST or ch.strip().lower() in ("obsbot", "obsbot official"):
                continue
            pub = s["publishedAt"]
            if pub[:10] not in days:          # 真实发布日期复核
                continue
            rows.append({
                "vid": it["id"], "ch": ch, "title": title,
                "dur": iso2sec(it.get("contentDetails", {}).get("duration")),
                "day": pub[:10], "pub": pub,
                "views": int(it.get("statistics", {}).get("viewCount", 0) or 0),
            })

    rows.sort(key=lambda r: (r["day"], r["ch"]))

    # 🔴 去重：历史报告中已出现过的 video ID 不再二次出现
    ledger = load_ledger()
    dup_rows = [r for r in rows if r["vid"] in ledger]
    rows = [r for r in rows if r["vid"] not in ledger]

    print(f"去黑名单/官方 + 日期复核后: {len(rows) + len(dup_rows)} 条"
          f"（其中 {len(dup_rows)} 条已在历史报告出现过，已排除）\n")
    for r in rows:
        flag = ""
        if r["dur"] > 3600:
            flag += " [>1h]"
        if 0 <= r["dur"] < 60:
            flag += " [<1min]"
        if r["views"] == 0:
            flag += " [0views]"
        print(f"{r['day']} | {r['vid']} | {r['ch'][:32]:32} | {fmt(r['dur']):>10} | "
              f"{r['views']:>7}v | {r['title'][:52]}{flag}")
    print("\n入选候选（通过时长/播放量硬过滤）:")
    for r in rows:
        if 60 <= r["dur"] <= 3600 and r["views"] > 0:
            print(f"  {r['day']} | {r['vid']} | {r['ch']} | {fmt(r['dur'])} | {r['views']}v | {r['title'][:60]}")
    if dup_rows:
        print("\n已排除（历史报告重复）:")
        for r in dup_rows:
            print(f"  {r['day']} | {r['vid']} | {r['ch']} | {r['title'][:55]}")


if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv and argv[0] == "--mark":
        ids = [a for a in argv[1:] if not a.startswith("-")]
        n = mark_reported(ids)
        print(f"台账已更新：新增 {n} 条，总计 {len(load_ledger())} 条")
    else:
        main(argv or [datetime_yesterday()])
