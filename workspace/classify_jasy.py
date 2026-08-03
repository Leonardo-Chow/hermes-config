#!/usr/bin/env python3
"""Classify jasy accounts - heuristic + known knowledge."""
import json, os, csv

with open('/tmp/jasy_qualified.json') as f:
    qual = json.load(f)

# username -> (一级类目, 二级类目, 依据, 是否过滤)
# 过滤 = 明星/品牌号/官方号
C = {
    'lalalalisa_m': ('Content Creator', 'Music', '歌手LISA', True),
    'kaerukeki': ('Content Creator', 'Lifestyle', '生活方式/日常博主', False),
    'sooyaaa__': ('Content Creator', 'Music', '歌手Rosé', True),
    'littleqqabbiett': ('Content Creator', 'Beauty', '美妆/日常博主', False),
    'siuday__': ('Content Creator', 'Lifestyle', '生活方式博主', False),
    'nicole_pamelaaa': ('Content Creator', 'Beauty', '美妆博主', False),
    'mia_yilin_': ('Content Creator', 'Beauty', '美妆/日常博主', False),
    'leniklum': ('Content Creator', 'Fashion', '模特/名人(Heidi Klum之女)', True),
    'lilbieber': ('Content Creator', 'Music', '名人', True),
    'ufocaller': ('Content Creator', 'Lifestyle', '艺术/生活方式博主', False),
    'jacqisdiary': ('Content Creator', 'Lifestyle', '日常vlog/生活方式博主', False),
    'mingsanhealing': ('Content Creator', 'Lifestyle', '疗愈/健康生活方式', False),
    'louiburke': ('Content Creator', 'Travel', '旅行博主', False),
    'miarose_mcgrath': ('Content Creator', 'Beauty', '美妆博主', False),
    'seed': ('Content Creator', 'Beauty', '护肤品牌号', True),
    'service95bookclub': ('Content Creator', 'Lifestyle', 'Dua Lipa读书俱乐部(名人)', True),
    'fromsabyang': ('Content Creator', 'Fashion', '时尚/美妆博主', False),
    'beautybybanda_': ('Content Creator', 'Beauty', '美妆博主', False),
    'nespresso': ('Content Creator', 'Lifestyle', '咖啡品牌号', True),
    'andyyyen': ('Content Creator', 'Travel', '旅行/摄影博主', False),
    'lena_yewon': ('Content Creator', 'Beauty', '美妆/时尚博主', False),
    'bubble': ('Content Creator', 'Beauty', '护肤品牌号(Bubble)', True),
    'sandydianabang': ('Content Creator', 'Fashion', '时尚/美妆博主', False),
}

rows = []
for q in qual:
    u = q['username']
    cat1, cat2, note, filtered = C.get(u, ('Content Creator', 'Lifestyle', '待确认', False))
    rows.append({**q, '一级类目': cat1, '二级类目': cat2, '分类依据': note, '过滤': filtered})

# 输出
kept = [r for r in rows if not r['过滤']]
dropped = [r for r in rows if r['过滤']]

print(f"=== 保留 {len(kept)} 个有效 KOL ===")
for r in sorted(kept, key=lambda x: x['avg_video_views'], reverse=True):
    print(f"  @{r['username']:<20} | {r['一级类目']:<18} | {r['二级类目']:<10} | {r['followers']:>10,} | {r['avg_video_views']:>10,} | {r['分类依据']}")

print(f"\n=== 过滤 {len(dropped)} 个明星/品牌号 ===")
for r in dropped:
    print(f"  @{r['username']:<20} | {r['分类依据']}")

# 写 CSV
output_path = os.path.expanduser("~/Downloads/IG_KOL_筛选_jasylifestyle_2026-07-30_部分.csv")
with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', '主页链接', '粉丝数量', 'Views', '帖子数', '一级类目', '二级类目', '分类依据', '来源博主'])
    for r in kept:
        writer.writerow([r['username'], r['profile_url'], r['followers'], r['avg_video_views'],
                         r['posts'], r['一级类目'], r['二级类目'], r['分类依据'], 'jasylifestyle'])
print(f"\nCSV: {output_path}")
