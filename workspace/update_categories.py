#!/usr/bin/env python3
"""Update category fields for all records in Tencent Docs smartsheet."""
import os, json, subprocess, time

FILE_ID = "DMAtCCxkRdOV"
SHEET_ID = "t00i2h"

# Load classification
with open("/Users/zhoulong/.hermes/workspace/classify_obsbot.py") as f:
    pass  # classification is in the script; load from CSV instead

import csv
rows = []
with open(os.path.expanduser("~/Downloads/IG_KOL_筛选_cheskasuz_2026-07-30_OBSBOT类目.csv"), encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# username -> (cat1, cat2)
CLASS = {r['ID']: (r['一级类目'], r['二级类目']) for r in rows}

# Load existing records to map username -> record_id
def mc_call(tool, args_dict, timeout=90):
    args_str = json.dumps(args_dict, ensure_ascii=False)
    r = subprocess.run(["mcporter", "call", "tencent-docs", tool, "--args", args_str],
                       capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(r.stdout), None
    except Exception:
        return None, "parse error"

# Get all records with IDs
all_recs = {}
offset = 0
while True:
    resp, err = None, "retry"
    for attempt in range(5):
        resp, err = mc_call("smartsheet.list_records", {
            "file_id": FILE_ID, "sheet_id": SHEET_ID, "limit": 10, "offset": offset,
            "field_titles": ["ID (用户名)"]})
        if resp:
            break
        time.sleep(6 * (attempt + 1))
    if err or not resp:
        print("List error:", err); break
    recs = resp.get('records', [])
    for rec in recs:
        for fv in rec.get('field_values', []):
            if fv.get('field') == 'ID (用户名)' and fv.get('text_value'):
                uname = fv['text_value']['items'][0]['text']
                all_recs[uname] = rec['record_id']
    total = resp.get('total', 0)
    if offset + len(recs) >= total or len(recs) == 0:
        break
    offset += len(recs)

print(f"Records in table: {len(all_recs)}")
print(f"Classifications: {len(CLASS)}")

# Update each record
success = 0
failed = 0
for uname, rid in all_recs.items():
    if uname not in CLASS:
        print(f"  No class for @{uname}")
        continue
    cat1, cat2 = CLASS[uname]
    update = {
        "field_values": [
            {"field": "账号类别", "option_value": {"items": [{"text": cat1}]}},
            {"field": "二级类目", "text_value": {"items": [{"text": cat2, "type": "text"}]}},
        ]
    }
    ok = False
    for attempt in range(4):
        resp, err = mc_call("smartsheet.update_records", {
            "file_id": FILE_ID, "sheet_id": SHEET_ID,
            "records": [{"record_id": rid, **update}]})
        if not err and (resp.get("error") == "" or not resp.get("error")):
            ok = True
            break
        time.sleep(6 * (attempt + 1))
    if ok:
        success += 1
    else:
        failed += 1
        print(f"  FAIL @{uname}")

    if (success + failed) % 10 == 0:
        print(f"  Progress: {success + failed}/{len(all_recs)} ({success} ok)", flush=True)

print(f"\nDone: {success} updated, {failed} failed")
