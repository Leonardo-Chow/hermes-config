#!/usr/bin/env python3
"""Upload records to Tencent Docs smartsheet - reliable argv method."""
import json, subprocess, time

FILE_ID = "DMAtCCxkRdOV"
SHEET_ID = "t00i2h"

with open("/Users/zhoulong/.hermes/workspace/ig_records.json") as f:
    records = json.load(f)

def mc_call(tool, args_dict, timeout=90):
    args_str = json.dumps(args_dict, ensure_ascii=False)
    r = subprocess.run(["mcporter", "call", "tencent-docs", tool, "--args", args_str],
                       capture_output=True, text=True, timeout=timeout)
    if not r.stdout.strip():
        return None, f"empty stdout (rc={r.returncode}): {r.stderr[:200]}"
    try:
        return json.loads(r.stdout), None
    except Exception as e:
        return None, f"parse error: {r.stdout[:200]}"

BATCH = 5  # 每批 5 条，避免输出过大
success = 0
failed = 0
for i in range(0, len(records), BATCH):
    batch = records[i:i+BATCH]
    resp, err = mc_call("smartsheet.add_records", {
        "file_id": FILE_ID, "sheet_id": SHEET_ID, "records": batch
    })
    if err:
        failed += len(batch)
        print(f"  Batch {i//BATCH+1}: FAIL - {err}", flush=True)
    elif resp.get("error") == "" or not resp.get("error"):
        success += len(batch)
        print(f"  Batch {i//BATCH+1}: OK ({len(batch)})", flush=True)
    else:
        failed += len(batch)
        print(f"  Batch {i//BATCH+1}: FAIL - {resp.get('error')}", flush=True)
    time.sleep(0.8)

print(f"\nDone: {success} success, {failed} failed")

# Verify
resp, err = mc_call("smartsheet.list_records", {
    "file_id": FILE_ID, "sheet_id": SHEET_ID, "limit": 1, "field_titles": ["ID (用户名)"]})
print(f"Table total now: {resp.get('total') if resp else 'ERR'}")
