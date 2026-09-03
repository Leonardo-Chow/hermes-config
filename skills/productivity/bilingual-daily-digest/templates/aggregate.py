#!/usr/bin/env python3
"""
摸鱼日报 v4.2 聚合：全球财经 + 双语板块 + 当日过滤
经过 6+ 次重跑验证的稳定版本（2026-08-25 ~ 2026-09-02）
"""
import json, re, os, html as ihtml, urllib.parse, datetime, email.utils, subprocess
from datetime import date

os.chdir(os.path.dirname(os.path.abspath(__file__)))
TODAY = date.today().strftime("%Y-%m-%d")

def load(fn):
    try:
        with open(fn) as f: return json.load(f)
    except Exception:
        try:
            with open(fn) as f: txt = f.read()
            idx = min([i for i in (txt.find("{"), txt.find("[")) if i >= 0])
            obj, _ = json.JSONDecoder().raw_decode(txt[idx:])
            return obj
        except Exception: return None

def bj_time(dstr):
    dstr = (dstr or "").strip()
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", dstr):
            dt = datetime.datetime.strptime(dstr, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
        else:
            dt = email.utils.parsedate_to_datetime(dstr)
        return dt + datetime.timedelta(hours=8)
    except Exception: return None

def is_today(dstr):
    t = bj_time(dstr)
    return bool(t and t.date().isoformat() == TODAY)

def bj_fmt(t):
    return t.strftime("%m-%d %H:%M") if t else ""

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = ihtml.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def rss_items_ts(fn, src, n=5):
    d = load(fn); res = []
    if d and d.get("status") == "ok":
        for it in d.get("items", []):
            if not is_today(it.get("pubDate","")): continue
            ts = bj_time(it.get("pubDate",""))
            desc = clean(it.get("description",""))[:160]
            res.append({"title": clean(it.get("title","")), "url": it.get("link",""),
                        "desc": desc, "source": src, "date": bj_fmt(ts), "ts": ts.timestamp()})
    return res[:n]

out = {"date": TODAY}

# 热搜
baidu = load("baidu.json"); items = []
if baidu:
    for card in baidu.get("data", {}).get("cards", []):
        for c in card.get("content", [])[:8]:
            items.append({"title": c.get("word",""), "url": c.get("url") or c.get("appUrl",""),
                          "hot": int(float(c.get("hotScore",0)))})
out["baidu"] = items[:8]

dy = load("douyin.json"); items = []
if dy:
    for w in dy.get("data", {}).get("word_list", [])[:8]:
        items.append({"title": w.get("word",""), "url": "https://www.douyin.com/hot", "hot": w.get("hot_value",0)})
out["douyin"] = items

wb = load("weibo.json")
if isinstance(wb, list):
    out["weibo"] = []
    for x in wb[:8]:
        t = x.get("title") or x.get("word","")
        u = x.get("url","") or f"https://s.weibo.com/weibo?q=%23{urllib.parse.quote(t)}%23"
        out["weibo"].append({"title": t, "url": u, "hot": x.get("hot") or x.get("num",0)})

# A 股 (parts[3]=price, parts[31]=chg, parts[32]=pct)
try:
    txt = open("astock_utf8.txt").read()
    for m in re.finditer(r'v_([^=]+)="([^"]+)"', txt):
        code, vals = m.groups()
        parts = vals.split("~")
        if len(parts) >= 33:
            name = parts[1]
            try:
                price = float(parts[3]) if parts[3] else 0
                chg = float(parts[31]) if len(parts) > 31 and parts[31] else 0
                pct = float(parts[32]) if len(parts) > 32 and parts[32] else 0
            except Exception: continue
            if name in ["上证指数","深证成指","创业板指","沪深300"]:
                out.setdefault("astock", []).append({"name": name, "price": price, "chg": chg, "pct": pct})
except Exception as e: print("astock:", e); out["astock"] = []

# 美股 (同字段位置)
try:
    txt = open("usstock_utf8.txt").read()
    for m in re.finditer(r'v_([^=]+)="([^"]+)"', txt):
        code, vals = m.groups()
        parts = vals.split("~")
        if len(parts) >= 33:
            name = parts[1]
            try:
                price = float(parts[3]) if parts[3] else 0
                chg = float(parts[31]) if len(parts) > 31 and parts[31] else 0
                pct = float(parts[32]) if len(parts) > 32 and parts[32] else 0
            except Exception: continue
            if name in ["道琼斯","纳斯达克","标普500"]:
                out.setdefault("global_idx", []).append({"name": name, "price": price, "chg": chg, "pct": pct})
except Exception as e: print("usstock:", e); out["global_idx"] = []

# 财经英语
fin = []
try:
    import xml.etree.ElementTree as ET
    tree = ET.parse("cnbc_raw.xml")
    for it in tree.getroot().findall(".//item"):
        pd = it.findtext("pubDate","")
        ts = bj_time(pd)
        if ts and is_today(pd):
            fin.append({"title": clean(it.findtext("title","")), "url": it.findtext("link",""),
                        "desc": clean(it.findtext("description",""))[:150], "source": "CNBC",
                        "date": bj_fmt(ts), "ts": ts.timestamp()})
except Exception: pass

for fn, src in [("rss_ft.json","FT"), ("rss_wsj.json","WSJ"), ("rss_bi.json","Insider"),
                ("rss_mw.json","MarketWatch"), ("rss_yf.json","Yahoo Finance")]:
    for it in rss_items_ts(fn, src): fin.append(it)
seen, dedup = set(), []
for it in fin:
    k = it["title"][:40].lower()
    if k not in seen: seen.add(k); dedup.append(it)
out["finance_en"] = sorted(dedup, key=lambda x: -x["ts"])[:10]
out["fin_sources"] = sorted(set(x["source"] for x in dedup))

# 科技英语
tech = []
for fn, src in [("rss_tc.json","TechCrunch"), ("rss_verge.json","The Verge"),
                ("rss_ars.json","Ars Technica"), ("rss_wired.json","Wired"),
                ("rss_ifanr.json","爱范儿")]:
    for it in rss_items_ts(fn, src): tech.append(it)
out["tech_en"] = sorted(tech, key=lambda x: -x["ts"])[:10]

# AI 英语
ai = []
for fn, src in [("rss_tcai.json","TechCrunch AI")]:
    for it in rss_items_ts(fn, src): ai.append(it)
for it in tech:
    if any(k in it["title"].lower() for k in ["ai","llm","gpt","claude","anthropic","openai","stable","diffusion","llama"]):
        if not any(it["title"][:30] == x["title"][:30] for x in ai):
            ai.append(it)
out["ai_en"] = sorted(ai, key=lambda x: -x["ts"])[:6]

# 国际
intl = []
for fn, src in [("rss_bbc.json","BBC"), ("rss_npr.json","NPR"),
                ("rss_aj.json","Al Jazeera"), ("rss_f24.json","France 24"),
                ("rss_cnn.json","CNN"), ("rss_nyt.json","NYT")]:
    for it in rss_items_ts(fn, src): intl.append(it)
out["intl_en"] = sorted(intl, key=lambda x: -x["ts"])[:12]
out["intl_sources"] = sorted(set(x["source"] for x in intl))

# 娱乐
ent = []
for fn, src in [("rss_thr.json","THR"), ("rss_variety.json","Variety")]:
    for it in rss_items_ts(fn, src): ent.append(it)
out["ent_intl_en"] = sorted(ent, key=lambda x: -x["ts"])[:8]

# GitHub
gh = load("github.json")
out["github"] = [{"name": r["full_name"], "desc": (r.get("description") or "")[:100],
                  "stars": r["stargazers_count"], "url": r["html_url"]} for r in gh.get("items", [])[:5]] if gh else []
gha = load("github_aiagent.json")
out["github_aiagent"] = [{"name": r["full_name"], "desc": (r.get("description") or "")[:110],
                          "stars": r["stargazers_count"], "url": r["html_url"]} for r in gha.get("items", [])[:4]] if gha else []

# HN
hn = []
for line in open("hn_items.jsonl"):
    try:
        d = json.loads(line)
        hn.append({"title": d.get("title",""), "url": d.get("url") or f"https://news.ycombinator.com/item?id={d['id']}",
                   "score": d.get("score",0), "id": d["id"]})
    except Exception: pass
out["hn"] = hn[:8]

with open("moyu_data.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print(f"日期: {TODAY}")
for k in ["baidu","douyin","weibo","astock","global_idx","finance_en","tech_en","ai_en","intl_en","ent_intl_en","github","github_aiagent","hn"]:
    print(f"{k}: {len(out.get(k, []))} 条")
print("财经来源:", out["fin_sources"])
print("国际来源:", out["intl_sources"])
