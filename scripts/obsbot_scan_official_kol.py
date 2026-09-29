#!/usr/bin/env python3
"""按官方 KOL brief 指纹检索合作视频。

三层检索：
  L1 直接搜指纹串（折扣码 / 官方 hashtag）
  L2 关键词搜 + 描述区指纹匹配（含本地化品牌名）
  L3 汇总去重、去台账、输出
用法: python3 obsbot_scan_official_kol.py [起始日 结束日]
"""
import re
import sys
import time

sys.path.insert(0, "/Users/zhoulong/.hermes/scripts")
import obsbot_yt_scan as s  # noqa: E402

# L1 指纹串（直接搜索）
FINGERPRINTS = [
    "269YUS10",                     # brief 案例折扣码
    "#streamwithobsbot", "#obsbotambassador", "#obsbotecosystem", "#obsbotreview",
    "obsbot discount code", "obsbot prime day", "obsbot tiny 2 lite code",
    "obsbot.com rfsn",
]

# L2 关键词（产品维度，覆盖 brief 涉及产品）
KWS = ["OBSBOT Tiny 2 Lite", "OBSBOT Tiny 3", "OBSBOT Meet Flip", "OBSBOT Tail 2",
       "OBSBOT Talent 2", "OBSBOT Meet SE", "OBSBOT Meet 2", "OBSBOT", "옵스봇"]


def gather(day_lo, day_hi):
    ids = set()
    for q in FINGERPRINTS + KWS:
        for attempt in range(3):
            d = s.api("search", {"part": "snippet", "q": q, "type": "video",
                                 "order": "date", "maxResults": 50})
            items = d.get("items")
            if items is not None:
                break
            time.sleep(3)
        else:
            print(f"  ⚠️ 搜索失败: {q}")
            continue
        for i in items:
            v = i["id"].get("videoId")
            if v:
                ids.add(v)
        time.sleep(0.2)
    print(f"L1+L2 命中 {len(ids)} 个 vid，拉详情...")

    rows = []
    idlist = sorted(ids)
    for k in range(0, len(idlist), 50):
        d = s.api("videos", {"part": "snippet,contentDetails,statistics,liveStreamingDetails",
                             "id": ",".join(idlist[k:k + 50])})
        for it in d.get("items", []):
            sn = it["snippet"]
            ch, title = sn["channelTitle"], sn["title"]
            desc = sn.get("description", "") or ""
            pub = sn["publishedAt"]
            if not (day_lo <= pub[:10] <= day_hi):
                continue
            if ch in s.BLACKLIST or ch.strip().lower() in ("obsbot", "obsbot official"):
                continue
            blob = f"{title} {ch} {desc}"
            if not s.match_brand(blob):
                continue
            in_title = bool(s.match_brand(title) or s.match_brand(ch))
            sigs = s.sponsor_signals(desc)
            # 折扣码单独提取（brief 形态）
            codes = re.findall(r"[Cc]ode[:\s]*([A-Z0-9]{6,10})\b", desc)
            rows.append({
                "vid": it["id"], "ch": ch, "title": title, "desc": desc,
                "day": pub[:10],
                "dur": s.iso2sec(it.get("contentDetails", {}).get("duration")),
                "views": int(it.get("statistics", {}).get("viewCount", 0) or 0),
                "in_title": in_title, "sigs": sigs[:3], "codes": codes[:2],
                "logged": it["id"] in s.load_ledger(),
            })
    return rows


def main(lo, hi):
    rows = gather(lo, hi)
    off = [r for r in rows if (not r["in_title"]) and r["sigs"] and not r["logged"]]
    off.sort(key=lambda r: -r["views"])
    print(f"\n🔴 官方合作/植入型·未收录: {len(off)}\n")
    for r in off:
        ok = 60 <= r["dur"] <= 3600 and r["views"] > 0
        print(f"{'✅' if ok else '❌'} {r['day']} | {r['vid']} | {r['ch'][:26]:26} | {s.fmt(r['dur']):>9} | {r['views']:>7}v")
        print(f"     T: {r['title'][:78]}")
        print(f"     信号={r['sigs']} 折扣码={r['codes']}")
    # 带折扣码的视频单独列（最强指纹）
    withcode = [r for r in rows if r["codes"] and not r["logged"]]
    print(f"\n💥 描述区含折扣码的视频（最强官方合作指纹）: {len(withcode)}")
    for r in withcode:
        print(f"   {r['day']} | {r['vid']} | {r['ch'][:28]:28} | {r['views']:>7}v | 码={r['codes']} | {r['title'][:48]}")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0] if a else "2026-09-01", a[1] if len(a) > 1 else "2026-09-29")
