#!/usr/bin/env python3
"""Classify IG accounts using OBSBOT content category system - v2."""
import os, json, csv
from collections import Counter

data_path = os.path.expanduser("~/.hermes/workspace/ig_kol_data.json")
output_path = os.path.expanduser("~/Downloads/IG_KOL_筛选_cheskasuz_2026-07-30_OBSBOT类目.csv")

with open(data_path) as f:
    accounts = json.load(f)

qualified = [a for a in accounts if a['followers'] >= 50000 and a['avg_video_views'] >= 5000]
qualified.sort(key=lambda x: x['avg_video_views'], reverse=True)
print(f"Total accounts: {len(qualified)}")

# (一级类目, 二级类目, 分类依据)
C = {
    # ===== Content Creator =====
    'patrickstarrr': ('Content Creator', 'Beauty', '美妆博主/ONESIZE创始人'),
    'sephora': ('Content Creator', 'Beauty', '美妆零售品牌号'),
    'nyxcosmetics': ('Content Creator', 'Beauty', '彩妆品牌号'),
    'rarebeauty': ('Content Creator', 'Beauty', '美妆品牌号'),
    'blkcosmeticsph': ('Content Creator', 'Beauty', '菲律宾彩妆品牌号'),
    'pereylierge': ('Content Creator', 'Beauty', '美妆/隐形眼镜博主'),
    'iamsooyounlee': ('Content Creator', 'Beauty', 'Beauty/Fashion博主'),
    'janetrosee': ('Content Creator', 'Beauty', '美妆博主'),
    'sanamiee': ('Content Creator', 'Beauty', '美妆博主'),
    'heillyraices': ('Content Creator', 'Beauty', '美妆博主'),
    '_rosetanaka': ('Content Creator', 'Beauty', '美妆/生活方式博主'),
    'krissyonfire': ('Content Creator', 'Beauty', '美妆博主'),
    'ciara_melle': ('Content Creator', 'Beauty', '美妆博主'),
    'tracie.lovex': ('Content Creator', 'Beauty', '美妆博主'),
    'michellegraviet': ('Content Creator', 'Beauty', '美妆/routines博主'),
    'yulingwu': ('Content Creator', 'Beauty', '美妆/护肤博主'),
    'mara.mcginnis': ('Content Creator', 'Beauty', '美妆博主'),
    'morgansandiego': ('Content Creator', 'Beauty', '美妆生活方式博主'),
    'allthingsjudyy': ('Content Creator', 'Beauty', '美妆博主'),
    'eighthmermaid': ('Content Creator', 'Beauty', '美妆博主'),
    'amayaelizabeth_': ('Content Creator', 'Beauty', '美妆/时尚博主'),
    'rachelkaejenkins': ('Content Creator', 'Beauty', '美妆博主'),
    'cams_florentino': ('Content Creator', 'Beauty', '菲律宾美妆/生活博主'),
    'katrina_dimaranan': ('Content Creator', 'Beauty', '美妆/选美公众人物'),
    'katebartlett': ('Content Creator', 'Beauty', '美妆博主'),
    'sophiacuerquis': ('Content Creator', 'Beauty', '美妆/时尚博主'),
    'itsyuyann': ('Content Creator', 'Beauty', '美妆博主'),
    'gforce_mykag': ('Content Creator', 'Beauty', '牙医+美妆博主'),
    # --- Fashion ---
    'rbonneynola': ('Content Creator', 'Fashion', '环保时尚设计师'),
    'laurenwolfe': ('Content Creator', 'Fashion', 'NYC时尚博主'),
    'abercrombie': ('Content Creator', 'Fashion', '服装品牌号'),
    'amazonfashion': ('Content Creator', 'Fashion', 'Amazon时尚频道'),
    'beis': ('Content Creator', 'Fashion', '箱包品牌号'),
    'warbyparker': ('Content Creator', 'Fashion', '眼镜品牌号'),
    'wearfigs': ('Content Creator', 'Fashion', '医护服饰品牌号'),
    'alysaxliu': ('Content Creator', 'Fashion', '花滑运动员/时尚博主'),
    'need4lspeed': ('Content Creator', 'Fashion', '时尚博主'),
    'kirstendodgen': ('Content Creator', 'Fashion', '时尚/生活博主'),
    'savpalacio': ('Content Creator', 'Fashion', '时尚博主'),
    'missynjohnson': ('Content Creator', 'Fashion', 'Reel creator/时尚生活'),
    # --- Music ---
    'taylorswift': ('Content Creator', 'Music', '歌手Taylor Swift'),
    'arianagrande': ('Content Creator', 'Music', '歌手Ariana Grande'),
    'lalalalisa_m': ('Content Creator', 'Music', '歌手LISA'),
    'sooyaaa__': ('Content Creator', 'Music', '歌手Rosé'),
    'roses_are_rosie': ('Content Creator', 'Music', '歌手Rosé'),
    'lilbieber': ('Content Creator', 'Music', '名人'),
    'jennyhan': ('Content Creator', 'Music', '歌手/名人'),
    'leejung_lee': ('Content Creator', 'Music', '韩国歌手/名人'),
    # --- Lifestyle / other ---
    'chloe.shih': ('Content Creator', 'Lifestyle', 'career/生活博主'),
    'heysandylin': ('Content Creator', 'Lifestyle', '生活方式博主'),
    'zendaya': ('Content Creator', 'Lifestyle', '演员Zendaya'),
    'nespressousa': ('Content Creator', 'Lifestyle', '咖啡品牌号'),
    'operation_niki': ('Content Creator', 'Lifestyle', '生活方式博主'),
    'thejaycee_': ('Content Creator', 'Lifestyle', '生活方式博主'),
    'teresalaucar': ('Content Creator', 'Lifestyle', '生活方式博主'),
    'clockedoutdinks': ('Content Creator', 'Lifestyle', '生活方式博主'),
    'yanaaaaaak': ('Content Creator', 'Lifestyle', '生活方式博主'),
    'agenomicsphd': ('Content Creator', 'Lifestyle', '基因组学博士健康内容'),
    'mijindonp': ('Content Creator', 'Lifestyle', '生活方式博主'),
    'mosseri': ('Content Creator', 'Lifestyle', 'Instagram负责人'),
    'alice.journeyy': ('Content Creator', 'Travel', '旅行博主'),
    'dealcheats': ('Content Creator', 'Earning', '折扣/省钱信息博主'),
    # ===== Setup =====
    'wisteriem': ('Setup', 'Game Setup', 'cozy gaming/桌搭'),
    'cozycornerkai': ('Setup', 'Game Setup', 'cozy living/游戏桌搭'),
    'goldenmirmy': ('Setup', 'Game Setup', 'games/tech/cozy桌搭'),
    # ===== Tech =====
    'logitech': ('Tech', '3C', '键鼠外设品牌号(纯测评)'),
    'samsungmobileusa': ('Tech', '3C', '手机品牌号(纯产品)'),
    'sonyelectronics': ('Tech', '3C', '消费电子品牌号'),
    'amazonhome': ('Tech', 'Hometech', 'Amazon家居频道'),
    'hatchforsleep': ('Tech', 'Hometech', '睡眠科技品牌号'),
    'omniluxled': ('Tech', 'Hometech', '美容光疗品牌号'),
    'girlset': ('Tech', '3C', '电子配件品牌号'),
    # ===== Sports =====
    'f1': ('Sports', '—', 'F1官方赛事号'),
    'rundisney': ('Sports', 'Fitness', 'runDisney跑步赛事官方号'),
    # ===== Entertainment =====
    'waltdisneyworld': ('Entertainment', '—', '迪士尼乐园官方号'),
    'disneycruiseline': ('Entertainment', '—', '迪士尼邮轮官方号'),
    # ===== Live Production =====
    'hankimmel': ('Live Production', 'Podcast', '播客主持人'),
    'sweetnsourpodcast': ('Live Production', 'Podcast', '播客频道'),
}

unclassified = [a['username'] for a in qualified if a['username'] not in C]
print(f"Unclassified: {len(unclassified)}")
if unclassified:
    print(f"  {unclassified}")

rows = []
for a in qualified:
    u = a['username']
    cat1, cat2, note = C.get(u, ('待分类', '待分类', '需人工确认'))
    rows.append({
        'username': u, 'profile_url': a['profile_url'],
        'followers': a['followers'], 'avg_video_views': a['avg_video_views'],
        'posts': a['posts'],
        '一级类目': cat1, '二级类目': cat2, '分类依据': note
    })

# Write CSV
with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', '主页链接', '粉丝数量', 'Views', '帖子数', '一级类目', '二级类目', '分类依据'])
    for r in rows:
        writer.writerow([r['username'], r['profile_url'], r['followers'], r['avg_video_views'],
                         r['posts'], r['一级类目'], r['二级类目'], r['分类依据']])

print(f"\nCSV: {output_path}")
print(f"Total: {len(rows)}")

cat1_counter = Counter(r['一级类目'] for r in rows)
cat2_counter = Counter(r['二级类目'] for r in rows)
print(f"\n一级类目: {dict(cat1_counter)}")
print(f"\n二级类目: {dict(cat2_counter)}")
