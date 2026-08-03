#!/usr/bin/env python3
"""Generate final CSV from ig_kol_data.json with consistent categorization."""
import os, json, csv

input_path = os.path.expanduser("~/.hermes/workspace/ig_kol_data.json")
output_path = os.path.expanduser("~/Downloads/IG_KOL_筛选_cheskasuz_2026-07-30.csv")

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

with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', '主页链接', '粉丝数量', 'Views', '帖子数', '账号类别', '来源博主'])
    for a in qualified:
        writer.writerow([
            a['username'],
            a['profile_url'],
            a['followers'],
            a['avg_video_views'],
            a['posts'],
            categorize(a['username']),
            'cheskasuz'
        ])

print(f"CSV written: {output_path}")
print(f"Records: {len(qualified)}")

# Category summary
cats = {}
for a in qualified:
    c = categorize(a['username'])
    cats[c] = cats.get(c, 0) + 1
print(f"Categories: {cats}")

# Check taylorswift
for a in qualified[:5]:
    print(f"  @{a['username']} -> {categorize(a['username'])}")
