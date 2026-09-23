#!/usr/bin/env python3
"""已发布视频台账 —— 记录所有曾出现在「视频上线监测」报告中的 video ID，
供 obsbot_yt_scan.py 去重，避免同一视频/链接二次出现。

结构: {"videos": {"<videoId>": {"reported": "YYYY-MM-DD", "channel": "...", "title": "..."}}}
"""
import json
import os

LEDGER = "/Users/zhoulong/.hermes/config/obsbot_reported_videos.json"

# 2026-09-08 ~ 2026-09-20 各期报告已收录的 video ID
BACKFILL = {
    "2026-09-08": ["Kqs8eLx_VdY", "WOGmo6ftWLc", "3quEv6z3lfk", "EJ7yWeMvi5g", "J19g-Sx9tkU",
                   "m0pP2bsRYgI", "ZGimzokE3zk", "EPd2qohhkbA", "nsONJC5nb08", "xASCp223CTA",
                   "Y7xYNbc-6h8", "cmyINPEfUps"],
    "2026-09-09": ["lAPBm36epfI", "lFVQtNDgxO4", "z20DMGCVgS4"],
    "2026-09-10": ["lccucxgE0Y0"],
    "2026-09-11": ["BGY1gguXrW8"],
    "2026-09-14": ["APN1CbKqTz0", "mX7fz3GmVFA", "JOBg0CeUqP0", "rN0_7fi12ZM", "AHChGsRqhrY",
                   "u-xIjSfuufo", "E5jnDU-X5Sc", "Opgx8LPmnjo"],
    "2026-09-15": ["n7KTKeDB8ZI", "owkofRNOSSU", "2Bp5hbQyYN8", "oH0L5Tx1BsE"],
    "2026-09-16": ["39IIaM8V5lc", "DoDUNmT6VOc", "xyBD0iDKzjk", "3yy9SeqzZFw", "6AcHVpxkUjg",
                   "_HxtoxOgE5w", "g5JPq5HI-2I", "7Sc_WfNujcc", "h9KlCNKd0YE", "tXQoBTslgY8"],
    "2026-09-17": ["XOxQpCLywoc", "kT20pCqWWIk", "cuatPtqwdKk", "y54myxrs1vk", "GQ3VDXEKJI4",
                   "Ro6K8ID0EpQ", "mrXXy1tZFfg", "rbb31LitbDY", "cCpqOFiJXDc"],
    "2026-09-18": ["jHrwNtdjbXg", "QMkFKrVQl50", "mnmJt8rh7fc", "nVqXE8DeSJc", "c-53Ys4N-RE",
                   "LpOQVx_G92c", "qAJ2j_lnQ98"],
    "2026-09-20": ["8Z98NDpsDRE", "c167n76Kvjg", "Grs1fLUq4NU", "MNvWHxF9zYs", "OY3rdS_E_Ow"],
}


def load():
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            return json.load(f)
    return {"videos": {}}


def save(data):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)


if __name__ == "__main__":
    data = load()
    added = 0
    for date, ids in BACKFILL.items():
        for vid in ids:
            if vid not in data["videos"]:
                data["videos"][vid] = {"reported": date, "channel": "", "title": ""}
                added += 1
    save(data)
    print(f"台账已写入 {LEDGER}")
    print(f"新增 {added} 条，总计 {len(data['videos'])} 条已发布视频 ID")
