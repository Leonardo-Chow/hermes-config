#!/usr/bin/env python3
"""Prepare Tencent Docs smartsheet records - CORRECT format."""
import os, json, datetime

input_path = os.path.expanduser("~/.hermes/workspace/ig_kol_data.json")
output_path = os.path.expanduser("~/.hermes/workspace/ig_records.json")

with open(input_path) as f:
    accounts = json.load(f)

qualified = [a for a in accounts if a['followers'] >= 50000 and a['avg_video_views'] >= 5000]
qualified.sort(key=lambda x: x['avg_video_views'], reverse=True)

CATEGORIES = {
    '美妆护肤': ['beauty', 'skin', 'glow', 'hair', 'makeup', 'cosmetic', 'skincare', 'nuface', 'serum', 'lash',
               'k18', 'drunk', 'elephant', 'lemi', 'fenty', 'haus', 'refy', 'merit', 'summerfriday', 'innisfree',
               'lawless', 'skinfix', 'pereylierge', 'beekman', 'wander_beauty', 'florence', 'youthtothepeople',
               'rarebeauty', 'sephora', 'nyx', 'blkcosmetics', 'kate', 'sophia', 'allthingsjudy',
               'mara', 'michelle', 'goldenmir', 'eighthmermaid', 'blk'],
    '时尚穿搭': ['fashion', 'style', 'boutique', 'bag', 'cloth', 'naadam', 'lululemon', 'alo', 'baggu', 'florencebymillsfashion',
               'abercrombie', 'amazonfashion', 'beis', 'warby', 'savpalacio', 'laurenwolfe', 'alysaxliu', 'need4lspeed',
               'kirsten', 'missyn', 'katebartlett', 'sophiacuerquis'],
    '数码科技': ['keyboard', 'tech', 'epomaker', 'yunzii', 'lofree', 'logitech', 'sandisk', 'sony', 'samsung',
               'insta360', 'osumekeys', 'gantri', 'mosseri', 'amazonhome'],
    '健身健康': ['fit', 'gym', 'health', 'wellness', 'yoga', 'bala', 'protein', 'bloomsupps', 'nurse', 'medic',
               'running', 'run', 'wearfigs', 'agenomics'],
    '美食': ['food', 'cook', 'recipe', 'chef', 'coffee', 'nespresso'],
    '宠物': ['pet', 'dog', 'cat', 'fable', 'openfarm'],
    '家居生活': ['home', 'cozy', 'furniture', 'cozey', 'branchfurniture', 'hommey', 'hatch', 'sleep', 'thirtyyears',
               'mynuface', 'omnilux', 'caliray', 'cozycorner'],
    '旅行': ['travel', 'trip', 'wander', 'journey', 'alice.journeyy'],
    '音乐娱乐': ['music', 'podcast', 'entertainment', 'sweetnsour', 'f1', 'disney', 'rundisney', 'waltdisney',
               'operation', 'himmel', 'clockedout'],
    '名人明星': ['taylor', 'lalalalisa', 'sooyaaa', 'roses_are_rosie', 'jennierubyjane', 'arianagrande', 'jennyhan',
               'zendaya', 'lilbieber', 'leejung', 'katrina', 'iamsooyoun', 'savpalacio', 'alysaxliu', 'need4lspeed'],
}

def categorize(username):
    uname = username.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in uname:
                return cat
    return '生活日常'

def text_value(v):
    return {"text_value": {"items": [{"text": str(v), "type": "text"}]}}

def number_value(v):
    return {"number_value": v}

def url_value(v):
    return {"url_value": {"items": [{"text": v, "type": "url", "link": v}]}}

def option_value(v):
    return {"option_value": {"items": [{"text": v}]}}

def string_value(v):
    return {"string_value": str(v)}

today_ms = int(datetime.datetime(2026, 7, 30).timestamp() * 1000)

records = []
for a in qualified:
    records.append({
        "field_values": [
            {"field": "ID (用户名)", **text_value(a['username'])},
            {"field": "主页链接", **url_value(a['profile_url'])},
            {"field": "粉丝数量", **number_value(a['followers'])},
            {"field": "Views", **number_value(a['avg_video_views'])},
            {"field": "帖子数", **number_value(a['posts'])},
            {"field": "账号类别", **option_value(categorize(a['username']))},
            {"field": "来源博主", **text_value('cheskasuz')},
            {"field": "添加日期", **string_value(today_ms)},
        ]
    })

with open(output_path, 'w') as f:
    json.dump(records, f, ensure_ascii=False)

print(f"Prepared {len(records)} records -> {output_path}")
# Print first record for verification
print(json.dumps(records[0], ensure_ascii=False)[:600])
