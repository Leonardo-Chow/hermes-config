#!/usr/bin/env python3
"""Categorize IG accounts and generate final CSV."""
import os, json, re, csv

input_path = os.path.expanduser("~/.hermes/workspace/ig_kol_data.json")
output_path = os.path.expanduser("~/.hermes/workspace/ig_final.csv")

with open(input_path) as f:
    accounts = json.load(f)

# Category keywords
CATEGORIES = {
    '美妆护肤': ['beauty', 'skin', 'glow', 'hair', 'makeup', 'cosmetic', 'skincare', 'nuface', 'serum', 'lash',
               'k18', 'drunk', 'elephant', 'lemi', 'fenty', 'haus', 'refy', 'merit', 'summerfriday', 'innisfree',
               'lawless', 'skinfix', 'pereylierge', 'beekman', 'wander_beauty', 'florence', 'youthtothepeople'],
    '时尚穿搭': ['fashion', 'style', 'boutique', 'bag', 'cloth', 'naadam', 'lululemon', 'alo', 'baggu', 'florencebymillsfashion'],
    '数码科技': ['keyboard', 'tech', 'epomaker', 'yunzii', 'lofree', 'logitech', 'sandisk', 'sony', 'samsung',
               'insta360', 'osumekeys', 'gantri', 'lofree'],
    '健身健康': ['fit', 'gym', 'health', 'wellness', 'yoga', 'bala', 'protein', 'bloomsupps', 'nurse', 'medic',
               'running', 'run'],
    '美食': ['food', 'cook', 'recipe', 'chef', 'coffee', 'nespresso'],
    '宠物': ['pet', 'dog', 'cat', 'fable', 'openfarm'],
    '家居生活': ['home', 'cozy', 'furniture', 'cozey', 'branchfurniture', 'hommey', 'hatch', 'sleep', 'thirtyyears',
               'mynuface', 'omnilux', 'caliray'],
    '旅行': ['travel', 'trip', 'wander', 'journey'],
    '母婴': ['baby', 'kid', 'mom', 'mama'],
    '音乐娱乐': ['music', 'podcast', 'entertainment', 'sweetnsour', 'f1', 'disney', 'rundisney', 'waltdisney'],
    '名人明星': ['zendaya', 'lalalalisa', 'sooyaaa', 'roses_are_rosie', 'jennierubyjane', 'taislourenco', 'katrina_dimaranan'],
}

def categorize(username):
    uname = username.lower()
    # Check exact celebrity names first
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in uname:
                return cat
    return '生活日常'

# Filter qualified
qualified = [a for a in accounts if a['followers'] >= 50000 and a['avg_video_views'] >= 5000]
qualified.sort(key=lambda x: x['avg_video_views'], reverse=True)

print(f"Qualified: {len(qualified)}")

# Write CSV
with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['username', 'profile_url', 'followers', 'avg_views', 'max_views', 'posts', 'category'])
    for a in qualified:
        writer.writerow([
            a['username'],
            a['profile_url'],
            a['followers'],
            a['avg_video_views'],
            a['max_video_views'],
            a['posts'],
            categorize(a['username'])
        ])

print(f"CSV written: {output_path}")
# Preview
for a in qualified[:20]:
    print(f"  @{a['username']} | {a['followers']:,} | {a['avg_video_views']:,} views | {categorize(a['username'])}")
