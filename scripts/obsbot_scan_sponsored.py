#!/usr/bin/env python3
"""补漏扫描：识别「描述区提及 OBSBOT」的视频，区分赞助植入 vs 单纯 gear 清单。

判定逻辑：
  A) 标题/频道含 obsbot            → 主内容（原流程已覆盖）
  B) 描述含 obsbot + 赞助信号词     → 赞助植入（**之前漏掉**，应收录）
  C) 描述含 obsbot + 无赞助信号     → gear 清单/设备列表，排除
用法: python3 obsbot_scan_sponsored.py 2026-09-27 [更多日期...]
"""
import re
import sys
import time

sys.path.insert(0, "/Users/zhoulong/.hermes/scripts")
import obsbot_yt_scan as s  # noqa: E402

SPONSOR_SIGNALS = [
    r"sponsored", r"sponsor", r"thanks to", r"thank you to", r"provided by",
    r"#ad\b", r"\bad\b\s*[-:|]", r"promo code", r"discount code", r"use code",
    r"rfsn=", r"obsbot\.com/store", r"obsbot\.com/[a-z]{2}/store", r"affiliate",
    r"品牌合作", r"赞助", r"推广", r"优惠码",
]


def main(days):
    lo, hi = min(days), max(days)
    ledger = s.load_ledger()
    ids = set()
    for kw in s.KWS:
        d = s.api("search", {"part": "snippet", "q": kw, "type": "video",
                             "order": "date", "maxResults": 50})
        for i in d.get("items", []):
            vid = i["id"].get("videoId")
            if vid:
                ids.add(vid)
        time.sleep(0.15)

    rows = []
    idlist = sorted(ids)
    for k in range(0, len(idlist), 50):
        d = s.api("videos", {"part": "snippet,contentDetails,statistics,liveStreamingDetails",
                             "id": ",".join(idlist[k:k + 50])})
        for it in d.get("items", []):
            sn = it["snippet"]
            ch = sn["channelTitle"]
            title = sn["title"]
            desc = sn.get("description", "") or ""
            blob = f"{title} {ch} {desc}".lower()
            if "obsbot" not in blob:
                continue
            pub = sn["publishedAt"]
            if pub[:10] not in days:
                continue
            if ch in s.BLACKLIST or ch.strip().lower() in ("obsbot", "obsbot official"):
                continue

            in_title = "obsbot" in title.lower() or "obsbot" in ch.lower()
            signal = [p for p in SPONSOR_SIGNALS if re.search(p, blob)]
            rows.append({
                "vid": it["id"], "ch": ch, "title": title, "day": pub[:10],
                "dur": s.iso2sec(it.get("contentDetails", {}).get("duration")),
                "views": int(it.get("statistics", {}).get("viewCount", 0) or 0),
                "was_live": bool(it.get("liveStreamingDetails")),
                "in_title": in_title,
                "signals": signal[:3],
                "logged": it["id"] in ledger,
            })

    rows.sort(key=lambda r: (r["day"], -r["views"]))
    main_rows = [r for r in rows if r["in_title"] and not r["logged"]]
    spons_rows = [r for r in rows if not r["in_title"] and r["signals"] and not r["logged"]]
    gear_rows = [r for r in rows if not r["in_title"] and not r["signals"]]

    print(f"窗口 {lo} ~ {hi} | OBSBOT 相关 {len(rows)} 条（已去黑名单/台账）\n")
    print(f"A) 主内容·未收录: {len(main_rows)}")
    for r in main_rows:
        print(f"   {r['day']} | {r['vid']} | {r['ch'][:28]:28} | {s.fmt(r['dur']):>9} | {r['views']:>7}v | {r['title'][:52]}")
    print(f"\nB) 🔴 赞助植入·未收录（之前漏掉的类型）: {len(spons_rows)}")
    for r in spons_rows:
        ok = 60 <= r["dur"] <= 3600 and r["views"] > 0
        print(f"   {'✅' if ok else '❌过滤'} {r['day']} | {r['vid']} | {r['ch'][:26]:26} | {s.fmt(r['dur']):>9} | {r['views']:>7}v | "
              f"{r['title'][:42]} | 信号={r['signals']}")
    print(f"\nC) 描述区 gear 清单（正确排除）: {len(gear_rows)}")
    for r in gear_rows[:8]:
        print(f"   {r['day']} | {r['ch'][:28]:28} | {r['views']:>7}v | {r['title'][:50]}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["2026-09-27"])
