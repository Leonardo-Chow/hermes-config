#!/usr/bin/env python3
"""Delete filtered (celebrity/brand) records from Tencent Docs smartsheet."""
import os, json, subprocess, time

FILE_ID = "DMAtCCxkRdOV"
SHEET_ID = "t00i2h"

with open('/tmp/filtered_usernames.json') as f:
    filtered_usernames = set(json.load(f))

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

# Find records to delete
to_delete = []
for uname, rid in all_recs.items():
    if uname in filtered_usernames:
        to_delete.append((uname, rid))

print(f"To delete: {len(to_delete)}")

# Delete in batches of 20
deleted = 0
for i in range(0, len(to_delete), 20):
    batch = to_delete[i:i+20]
    ids = [rid for _, rid in batch]
    ok = False
    for attempt in range(5):
        resp, err = mc_call("smartsheet.delete_records", {
            "file_id": FILE_ID, "sheet_id": SHEET_ID, "record_ids": ids})
        if not err and (resp.get("error") == "" or not resp.get("error")):
            ok = True
            break
        time.sleep(8 * (attempt + 1))
    if ok:
        deleted += len(batch)
        print(f"  Deleted batch {i//20+1}: {len(batch)} records ({[u for u,_ in batch]})", flush=True)
    else:
        print(f"  FAIL batch {i//20+1}: {[u for u,_ in batch]}", flush=True)

print(f"\nDeleted: {deleted}/{len(to_delete)}")
