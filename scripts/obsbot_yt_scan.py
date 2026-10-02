#!/usr/bin/env python3
"""OBSBOT YouTube 上线监测扫描器。

用法:  python3 obsbot_yt_scan.py 2026-09-14 [2026-09-15 ...]
输出:  按真实 publishedAt(UTC) 归组的候选列表，已去黑名单/官方，带时长/播放量/过滤标记。
"""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

POOL = "/Users/zhoulong/.hermes/config/youtube_api_pool.json"
API_KEY = None

# 多 key 轮换：全部载入，遇 429/403（配额耗尽）自动切下一个
_KEY_LIST = []
_KEY_IDX = 0
try:
    _KEY_LIST = [k for k in json.load(open(POOL)).get("api_keys", []) if k]
except Exception:  # noqa: BLE001
    pass
if not _KEY_LIST:
    _KEY_LIST = [k for k in [API_KEY] if k]
if not _KEY_LIST:
    sys.exit("未找到 YouTube API key（检查 youtube_api_pool.json）")
API_KEY = _KEY_LIST[0]

KWS = ["OBSBOT", "OBSBOT Tiny 3", "OBSBOT Tiny 3 Lite", "OBSBOT Tiny 2", "OBSBOT Tiny 2 Lite",
       "OBSBOT Tail 2", "OBSBOT Tail Air", "OBSBOT Meet Flip", "OBSBOT Meet SE", "OBSBOT Meet 2",
       "OBSBOT Meet", "OBSBOT Talent", "OBSBOT Vox", "OBSBOT Tiny SE", "OBSBOT One",
       "OBSBOT review", "OBSBOT unboxing", "OBSBOT webcam"]

BLACKLIST = {"UnboxingMyBuys", "Gadget Theory", "Gadget Savvy", "BrujulaDelUnboxing",
             "Chia Se Thong Tin", "CreatorFinds", "Pickfolio", "Su Lo", "Ha Vu", "SAM",
             "Khanh Trang", "Nhi An", "DealKompass"}

# 品牌名匹配：英文 + 本地化（韩/日/俄/泰/越南/印尼等平台的转写）
BRAND_NAMES = [r"obsbot", r"옵스봇", r"オプスボット", r"オブスボット", r"обсбот", r"оббсбот"]

# 赞助植入信号词（描述区出现这些 = 品牌合作/植入，应收录；单纯 gear 清单则排除）
# 2026-09-29 依据「官方 KOL 合作 brief」补全指纹
SPONSOR_SIGNALS = [
    # 通用赞助措辞
    r"sponsored", r"sponsor", r"thanks to", r"thank you to", r"provided by",
    r"#ad\b", r"品牌合作", r"赞助", r"推广",
    # 官方 Hashtag 体系（brief 规定）
    r"#streamwithobsbot", r"#obsbotecosystem", r"#obsbotreview", r"#obsbotambassador",
    r"#obsbot[a-z0-9]+",
    # 联盟/折扣链接（brief 规定的链接格式）
    r"rfsn=", r"utm_source=refersion", r"maas_adg_", r"ref_=aa_maas",
    r"obsbot\.com/store", r"obsbot\.com/[a-z]{2}/store", r"obsbot\.com/[a-z0-9\-]+-4k-webcam",
    r"affiliate",
    # CTA / 折扣码措辞（⚠️ 不要用 r"%\s*off" 或裸 code 形态 —— 任何长描述都会误报，2026-09-29 踩坑）
    r"discount code", r"promo code", r"use code", r"coupon code",
    r"shop the deals", r"prime day deal", r"优惠码", r"折扣码",
]


def match_brand(text):
    """返回命中的品牌名写法，未命中返回 None。"""
    low = text.lower()
    for p in BRAND_NAMES:
        if re.search(p, low):
            return p
    return None


def sponsor_signals(text):
    return [p for p in SPONSOR_SIGNALS if re.search(p, text, re.I)]

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
    """调用 YouTube API；遇 429（搜索配额耗尽）自动轮换 key 重试。"""
    global _KEY_LIST, _KEY_IDX
    err = None
    for attempt in range(len(_KEY_LIST) * 2):
        params["key"] = _KEY_LIST[_KEY_IDX]
        url = f"https://www.googleapis.com/youtube/v3/{path}?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=20) as f:
                return json.load(f)
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
            if e.code in (429, 403):          # 配额耗尽 → 换下一个 key
                _KEY_IDX = (_KEY_IDX + 1) % len(_KEY_LIST)
                continue
            time.sleep(1)
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
        d = api("videos", {"part": "snippet,contentDetails,statistics,liveStreamingDetails",
                           "id": ",".join(idlist[k:k + 50])})
        for it in d.get("items", []):
            s = it["snippet"]
            ch = s["channelTitle"]
            title = s["title"]
            desc = s.get("description", "") or ""
            in_title = bool(match_brand(title) or match_brand(ch))
            sigs = sponsor_signals(desc)
            # 官方大使计划标记（#obsbotambassador）：属官方合作，**豁免 <1min 过滤**（2026-09-29 用户要求）
            # ⚠️ 标签可能出现在标题里，不能只查描述区（2026-10-01 踩坑）
            _alltext = f"{title} {desc}"
            is_ambassador = bool(re.search(r"#obsbotambassador|obsbot\s*ambassador", _alltext, re.I))
            is_paid = bool(re.search(r"#paidpartner|#paid\s*partnership|paid partnership", _alltext, re.I))
            if not in_title and not sigs:
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
                "was_live": bool(it.get("liveStreamingDetails")),
                "kind": "主内容" if in_title else "赞助植入",
                "ambassador": is_ambassador,
                "paid": is_paid,
                "signals": sigs[:2],
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
            flag += " [>1h直播回放]" if r["was_live"] else " [>1h非直播·需人工判断]"
        if 0 <= r["dur"] < 60:
            flag += " [<1min]"
        if r["views"] == 0:
            flag += " [0views]"
        print(f"{r['day']} | {r['vid']} | {r['ch'][:32]:32} | {fmt(r['dur']):>10} | "
              f"{r['views']:>7}v | {r['title'][:52]}{flag}")
    print("\n入选候选（时长/播放量硬过滤）:")
    for r in rows:
        # >1h 只排除「直播回放」；非直播的长视频标注出来交人工判断（规则本意是过滤直播回放）
        if r["dur"] > 3600:
            if not r["was_live"]:
                print(f"  ⚠️需人工判断(>1h非直播) | {r['day']} | {r['vid']} | {r['ch']} | {fmt(r['dur'])} | {r['views']}v | {r['title'][:60]}")
            continue
        if r["views"] <= 0:
            continue
        # 官方大使（#obsbotambassador）豁免 <1min 过滤
        if r["dur"] < 60 and not (r.get("ambassador") or r.get("paid")):
            continue
        tag = "  【大使】" if r.get("ambassador") else ("  【paidpartner】" if r.get("paid") else ("  【赞助植入】" if r.get("kind") == "赞助植入" else ""))
        print(f"  {r['day']} | {r['vid']} | {r['ch']} | {fmt(r['dur'])} | {r['views']}v | {r['title'][:55]}{tag}")
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
