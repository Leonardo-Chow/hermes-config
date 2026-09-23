import json, re, time, urllib.parse, urllib.request

API_KEY = re.search(r"(AIzaSy[A-Za-z0-9_\-]{33})",
                    open("/Users/zhoulong/.hermes/scripts/obsbot_yt_scan.py").read())
POOL = "/Users/zhoulong/.hermes/config/youtube_api_pool.json"
API_KEY = json.load(open(POOL))["api_keys"][0]

KWS = ["OBSBOT", "OBSBOT webcam", "OBSBOT camera", "OBSBOT unboxing",
       "OBSBOT Tiny", "OBSBOT Meet", "OBSBOT Tiny 3", "OBSBOT Tail 2",
       "OBSBOT Meet Flip", "OBSBOT Meet SE", "OBSBOT review", "OBSBOT Vox",
       "OBSBOT Talent", "OBSBOT Tiny 2 Lite"]
DAY = "2026-09-14"


def api(path, params):
    params["key"] = API_KEY
    url = f"https://www.googleapis.com/youtube/v3/{path}?" + urllib.parse.urlencode(params)
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as f:
                return json.load(f)
        except Exception:
            time.sleep(2)
    return {}


ids = {}
for kw in KWS:
    d = api("search", {"part": "snippet", "q": kw, "type": "video", "order": "date",
                       "publishedAfter": f"{DAY}T00:00:00Z",
                       "publishedBefore": f"{DAY}T23:59:59Z", "maxResults": 50})
    for i in d.get("items", []):
        vid = i["id"].get("videoId")
        if vid:
            ids.setdefault(vid, i["snippet"]["title"])
    time.sleep(0.15)

print(f"窗口 {DAY} | 命中 {len(ids)} 条")

# 拉详情，检查 title + description
extra = []
idlist = sorted(ids)
for k in range(0, len(idlist), 50):
    d = api("videos", {"part": "snippet,contentDetails,statistics",
                       "id": ",".join(idlist[k:k + 50])})
    for it in d.get("items", []):
        s = it["snippet"]
        blob = (s["title"] + " " + s.get("description", "")).lower()
        ch = s["channelTitle"].lower()
        if "obsbot" not in blob and "obsbot" not in ch:
            continue
        extra.append({
            "vid": it["id"], "ch": s["channelTitle"], "title": s["title"],
            "pub": s["publishedAt"][:16],
            "dur": it["contentDetails"].get("duration"),
            "views": it["statistics"].get("viewCount", "?"),
            "intitle": "obsbot" in s["title"].lower() or "obsbot" in ch,
        })

print(f"含 OBSBOT（含描述区）: {len(extra)}\n")
for r in sorted(extra, key=lambda x: not x["intitle"]):
    mark = "" if r["intitle"] else "  <-- 仅描述区"
    print(f"{r['pub']} | {r['vid']} | {r['ch'][:28]:28} | {r['dur']:>9} | {r['views']:>7}v | {r['title'][:50]}{mark}")