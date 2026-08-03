#!/usr/bin/env python3
"""Retry failed batches with backoff."""
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
        return None, f"empty stdout (rc={r.returncode}): {r.stderr[:150]}"
    try:
        return json.loads(r.stdout), None
    except Exception as e:
        return None, f"parse error: {r.stdout[:150]}"

# Failed batches: 2, 5, 11, 13, 15 (0-indexed: 1, 4, 10, 12, 14)
BATCH = 5
failed_batches = [1, 4, 10, 12, 14]
success = 0
failed = 0

for bi in failed_batches:
    start = bi * BATCH
    batch = records[start:start+BATCH]
    # Retry up to 5 times with backoff
    ok = False
    for attempt in range(5):
        resp, err = mc_call("smartsheet.add_records", {
            "file_id": FILE_ID, "sheet_id": SHEET_ID, "records": batch
        })
        if not err and (resp.get("error") == "" or not resp.get("error")):
            success += len(batch)
            print(f"  Batch {bi+1}: OK on attempt {attempt+1} ({len(batch)})", flush=True)
            ok = True
            break
        print(f"  Batch {bi+1}: attempt {attempt+1} failed - {err or resp.get('error')}", flush=True)
        time.sleep(10 * (attempt + 1))
    if not ok:
        failed += len(batch)
        print(f"  Batch {bi+1}: GAVE UP", flush=True)

print(f"\nRetry done: {success} success, {failed} failed")

# Final verify
for attempt in range(3):
    resp, err = mc_call("smartsheet.list_records", {
        "file_id": FILE_ID, "sheet_id": SHEET_ID, "limit": 1, "field_titles": ["ID (用户名)"]})
    if resp:
        print(f"Table total now: {resp.get('total')}")
        break
    time.sleep(5)
