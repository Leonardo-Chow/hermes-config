#!/usr/bin/env python3
"""Upload jasy qualified KOLs to Tencent Docs (with dedup check)."""
import os, json, csv, subprocess, time, datetime

FILE_ID = "DMAtCCxkRdOV"
SHEET_ID = "t00i2h"

# 读取分类结果
with open(os.path.expanduser("~/Downloads/IG_KOL_筛选_jasylifestyle_2026-07-30_部分.csv"), encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

def mc_call(tool, args_dict, timeout=90):
    args_str = json.dumps(args_dict, ensure_ascii=False)
    r = subprocess.run(["mcporter", "call", "tencent-docs", tool, "--args", args_str],
                       capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout), None
    except: return None, "parse error"

# 1. 拉取数据库现有用户名（查重）
existing_users = set()
offset = 0
while True:
    resp, err = None, "retry"
    for attempt in range(5):
        resp, err = mc_call("smartsheet.list_records", {
            "file_id": FILE_ID, "sheet_id": SHEET_ID, "limit": 10, "offset": offset,
            "field_titles": ["ID (用户名)"]})
        if resp: break
        time.sleep(6 * (attempt + 1))
    if err or not resp:
        print("List error:", err); break
    recs = resp.get('records', [])
    for rec in recs:
        for fv in rec.get('field_values', []):
            if fv.get('field') == 'ID (用户名)' and fv.get('text_value'):
                existing_users.add(fv['text_value']['items'][0]['text'])
    total = resp.get('total', 0)
    if offset + len(recs) >= total or len(recs) == 0:
        break
    offset += len(recs)

print(f"数据库现有: {len(existing_users)} 条")

# 2. 构造新记录（去重）
new_rows = [r for r in rows if r['ID'] not in existing_users]
print(f"待新增: {len(new_rows)} (跳过重复: {len(rows) - len(new_rows)})")

if not new_rows:
    print("无新增")
    exit()

today_ms = int(datetime.datetime(2026, 7, 30).timestamp() * 1000)

def text_value(v):
    return {"text_value": {"items": [{"text": str(v), "type": "text"}]}}
def number_value(v):
    return {"number_value": int(v)}
def url_value(v):
    return {"url_value": {"items": [{"text": v, "type": "url", "link": v}]}}
def option_value(v):
    return {"option_value": {"items": [{"text": v}]}}
def string_value(v):
    return {"string_value": str(v)}

records = []
for r in new_rows:
    records.append({"field_values": [
        {"field": "ID (用户名)", **text_value(r['ID'])},
        {"field": "主页链接", **url_value(r['主页链接'])},
        {"field": "粉丝数量", **number_value(r['粉丝数量'])},
        {"field": "Views", **number_value(r['Views'])},
        {"field": "帖子数", **number_value(r['帖子数'])},
        {"field": "账号类别", **option_value(r['一级类目'])},
        {"field": "二级类目", **text_value(r['二级类目'])},
        {"field": "来源博主", **text_value('jasylifestyle')},
        {"field": "添加日期", **string_value(today_ms)},
    ]})

# 3. 分批上传（每批 5 条）
success = 0
failed = 0
for i in range(0, len(records), 5):
    batch = records[i:i+5]
    ok = False
    for attempt in range(5):
        resp, err = mc_call("smartsheet.add_records", {
            "file_id": FILE_ID, "sheet_id": SHEET_ID, "records": batch})
        if not err and (resp.get("error") == "" or not resp.get("error")):
            ok = True
            break
        time.sleep(8 * (attempt + 1))
    if ok:
        success += len(batch)
        print(f"  Batch {i//5+1}: OK ({len(batch)})", flush=True)
    else:
        failed += len(batch)
        print(f"  Batch {i//5+1}: FAIL", flush=True)

print(f"\nDone: {success} added, {failed} failed")
