#!/usr/bin/env python3
"""OBSBOT 视频上线监测 —— 全量自检（闭环反馈）

检查项：
  1. 跨报告重复（同一 video ID 出现在多期报告）
  2. 报告条目是否全部登记入台账（漏登记 → 下期必重复）
  3. 台账是否有多余条目（报告里找不到）
  4. UTC 日期覆盖连续性（有无断档）
用法: python3 obsbot_audit.py [起始日期 YYYY-MM-DD] [结束日期 YYYY-MM-DD]
"""
import datetime
import glob
import json
import os
import re
import sys
from collections import defaultdict

from docx import Document

DOWN = "/Users/zhoulong/Downloads"
LEDGER = "/Users/zhoulong/.hermes/config/obsbot_reported_videos.json"


def main(start, end):
    ledger = json.load(open(LEDGER)).get("videos", {})
    doc_ids = set()
    dup = defaultdict(list)
    covered = set()
    n_entries = 0
    n_docs = 0

    for p in sorted(glob.glob(f"{DOWN}/2026-*-视频上线监测.docx")):
        n_docs += 1
        rdate = os.path.basename(p)[:10]
        paras = [x.text.strip() for x in Document(p).paragraphs if x.text.strip()]
        for i, t in enumerate(paras):
            m = re.match(r"^(\d{4})/(\d{2})/(\d{2})（", t)
            if m:
                covered.add(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
            if re.match(r"^\d+\.\s", t) and i + 1 < len(paras):
                u = re.search(r"v=([A-Za-z0-9_\-]+)", paras[i + 1])
                if u:
                    n_entries += 1
                    doc_ids.add(u.group(1))
                    dup[u.group(1)].append(rdate)

    dupes = {v: ds for v, ds in dup.items() if len(ds) > 1}
    missing = doc_ids - set(ledger)
    redundant = set(ledger) - doc_ids

    # 日期覆盖连续性
    gaps = []
    d = datetime.date.fromisoformat(start)
    end_d = datetime.date.fromisoformat(end)
    while d <= end_d:
        if d.isoformat() not in covered:
            gaps.append(d.isoformat())
        d += datetime.timedelta(days=1)

    ok = not (dupes or missing or gaps)
    print("╔══════════════ OBSBOT 监测自检 ══════════════")
    print(f"║ 报告文档数        : {n_docs}")
    print(f"║ 收录条目总数      : {n_entries}")
    print(f"║ 唯一 video ID     : {len(doc_ids)}")
    print(f"║ 台账条数          : {len(ledger)}")
    print(f"║ 跨报告重复        : {len(dupes)} {'✅' if not dupes else '❌ ' + str(dupes)}")
    print(f"║ 未登记台账        : {len(missing)} {'✅' if not missing else '❌ ' + str(sorted(missing))}")
    print(f"║ 台账冗余          : {len(redundant)} {'✅' if not redundant else '⚠️ ' + str(len(redundant)) + ' 条'}")
    print(f"║ {start}~{end} 日期缺口: {len(gaps)} {'✅' if not gaps else '❌ ' + str(gaps)}")
    print(f"║ 覆盖天数          : {len(covered)}")
    print(f"╚══════════════════════════════════════════════")
    print("结论:", "✅ 全部通过" if ok else "❌ 存在问题，见上")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    s = a[0] if len(a) > 0 else "2026-09-05"
    # 默认截止 = 昨天（今天的目标 UTC 日尚未完整）
    e = a[1] if len(a) > 1 else (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    sys.exit(main(s, e))
