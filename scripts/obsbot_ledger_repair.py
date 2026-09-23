#!/usr/bin/env python3
"""台账修复：补登遗漏 ID + 修正日期标签错位。"""
import json

LEDGER = "/Users/zhoulong/.hermes/config/obsbot_reported_videos.json"

# 1) 我的 09-08 报告遗漏的 2 条（该报告覆盖 9/7 UTC）
MISSED = {
    "x-3elITbt-Q": ("2026-09-08", "TechBoost"),
    "xkkv7J-WgaA": ("2026-09-08", "KHO CÔNG NGHỆ"),
}

# 2) 早期报告（9/01~9/04，非本周期）补登
EARLY = {
    "2026-09-01": ["qZ2rT4Un99I", "MmP4jB4M2hE", "NfbMYo0xIlo", "0KZAoMUm7Qg",
                   "dJLHs7Z3R9Y", "6DdObPK18kw"],
    "2026-09-02": ["pliTo7sq-g8", "j4dJdUpITv0", "6CyazugeOy8"],
    "2026-09-03": ["qhWsuAKw7PY", "tUBl2Dc9na0", "H7AXoDa9qWU", "ChKFwc0fbJk",
                   "1aR4H7yaYVo", "kHXMTUnAM1g"],
    "2026-09-04": ["AzRaTFpwN1g", "oE0_2G_5cdc", "Uy1H-w2Aw1E", "360wkV_SNuU",
                   "4fBLWZZGJ6Q", "qQ_55nzW418"],
}

# 3) 日期标签错位修正：这 12 条实际出自「2026-09-07」报告，原先误标为 2026-09-08
RELABEL_0707 = ["Kqs8eLx_VdY", "WOGmo6ftWLc", "3quEv6z3lfk", "EJ7yWeMvi5g", "J19g-Sx9tkU",
                "m0pP2bsRYgI", "ZGimzokE3zk", "EPd2qohhkbA", "nsONJC5nb08", "xASCp223CTA",
                "Y7xYNbc-6h8", "cmyINPEfUps"]

data = json.load(open(LEDGER))
vids = data["videos"]
added = relabeled = 0

for vid, (date, ch) in MISSED.items():
    if vid not in vids:
        vids[vid] = {"reported": date, "channel": ch, "title": ""}
        added += 1

for date, ids in EARLY.items():
    for vid in ids:
        if vid not in vids:
            vids[vid] = {"reported": date, "channel": "", "title": ""}
            added += 1

for vid in RELABEL_0707:
    if vid in vids and vids[vid].get("reported") != "2026-09-07":
        vids[vid]["reported"] = "2026-09-07"
        relabeled += 1

data["videos"] = vids
json.dump(data, open(LEDGER, "w"), ensure_ascii=False, indent=1, sort_keys=True)
print(f"补登 {added} 条 | 修正日期标签 {relabeled} 条 | 台账总计 {len(vids)} 条")
