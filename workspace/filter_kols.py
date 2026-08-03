#!/usr/bin/env python3
"""Filter out celebrities/brand accounts, keep real KOLs."""
import os, csv, json

input_path = os.path.expanduser("~/Downloads/IG_KOL_筛选_cheskasuz_2026-07-30_OBSBOT类目.csv")
output_path = os.path.expanduser("~/Downloads/IG_KOL_筛选_cheskasuz_2026-07-30_有效KOL.csv")

with open(input_path, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# 过滤规则：分类依据含以下关键词视为明星/品牌号/官方号
FILTER_KEYWORDS = ['品牌号', '官方号', '官方赛事号', '频道', '负责人', '歌手', '演员',
                   '名人', '公众人物', '选美']

def is_filtered(row):
    note = row.get('分类依据', '')
    return any(kw in note for kw in FILTER_KEYWORDS)

kept = []
filtered = []
for r in rows:
    if is_filtered(r):
        filtered.append(r)
    else:
        kept.append(r)

print(f"Total: {len(rows)}, Kept: {len(kept)}, Filtered: {len(filtered)}")

# Write kept CSV
with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', '主页链接', '粉丝数量', 'Views', '帖子数', '一级类目', '二级类目', '分类依据'])
    for r in kept:
        writer.writerow([r['ID'], r['主页链接'], r['粉丝数量'], r['Views'], r['帖子数'],
                         r['一级类目'], r['二级类目'], r['分类依据']])

print(f"\nKept CSV: {output_path}")

# Summary
from collections import Counter
cat1 = Counter(r['一级类目'] for r in kept)
cat2 = Counter(r['二级类目'] for r in kept)
print(f"\n一级类目: {dict(cat1)}")
print(f"二级类目: {dict(cat2)}")

print("\n=== 保留的博主 ===")
for r in kept:
    print(f"  @{r['ID']:<20} | {r['一级类目']:<18} | {r['二级类目']:<12} | {r['粉丝数量']:>10} | {r['分类依据']}")

print("\n=== 过滤掉的（明星/品牌号） ===")
for r in filtered:
    print(f"  @{r['ID']:<20} | {r['一级类目']:<18} | {r['二级类目']:<12} | {r['分类依据']}")

# Save filtered usernames for later Tencent Docs cleanup
with open('/tmp/filtered_usernames.json', 'w') as f:
    json.dump([r['ID'] for r in filtered], f)
with open('/tmp/kept_usernames.json', 'w') as f:
    json.dump([r['ID'] for r in kept], f)
