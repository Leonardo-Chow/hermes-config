#!/usr/bin/env python3
"""Scan OBSBOT netizen IDs + fetch ambassadors.
Usage: python3 scan_netizens.py [start_id] [end_id] [workers] [output_file]
Output: ~/Downloads/obsbot_confirmed_netizens.json
"""
import json, urllib.request, time, sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN_FILE="/tmp/obsbot_token.txt"
PMS = "https://api.obsbot.cn/pms"

def load_token():
    with open(TOKEN_FILE) as f:
        return f.read().strip()

def fetch_one(token, nid, retries=3):
    h = {"Authorization": token, "Accept": "application/json", "dealer-proxy-type": "Remo"}
    for i in range(retries):
        try:
            r = urllib.request.Request(f"{PMS}/v1/netizen/detail/infos?id={nid}", headers=h)
            resp = urllib.request.urlopen(r, timeout=15)
            return json.loads(resp.read().decode())
        except:
            if i < retries - 1: time.sleep(0.3 * (i + 1))
    return None

def fetch_ambassadors(token):
    h = {"Authorization": token, "Accept": "application/json",
         "Content-Type": "application/json", "dealer-proxy-type": "Remo"}
    all_amb, page = [], 1
    while True:
        body = json.dumps({"page_no": page, "page_size": 200}).encode()
        try:
            r = urllib.request.Request(f"{PMS}/v1/netizen/ambassador/program/list",
                                       data=body, headers=h, method="POST")
            resp = urllib.request.urlopen(r, timeout=30)
            d = json.loads(resp.read().decode())
            all_amb.extend(d.get('results', []))
            if page >= d.get('pages', 0): break
            page += 1; time.sleep(0.3)
        except: break
    return all_amb

def merge_ambassadors(confirmed, ambassadors):
    pids = {r['platform_id'].lower() for r in confirmed.values()
            if isinstance(r.get('id'), int) and r.get('platform_id')}
    n = 0
    for a in ambassadors:
        if a.get('url', '').lower() in pids: continue
        plats = a.get('platform_info_list', [])
        yt = tt = ig = ''
        for p in plats:
            if p['platform'] == 'youtube': yt = p.get('link', '')
            elif p['platform'] == 'tiktok': tt = p.get('link', '')
            elif p['platform'] == 'instagram': ig = p.get('link', '')
        confirmed[f"amb_{a['id']}"] = {
            'id': a['id'], 'platform_id': a.get('url', ''),
            'name': a.get('profile_creator_id', ''), 'country': a.get('country', ''),
            'liaison': a.get('colleagues', '') or '', 'contact': '',
            'youtube': yt, 'tiktok': tt, 'instagram': ig,
            'source': 'ambassador', 'category': a.get('category', ''),
        }
        n += 1
    return n

def main():
    start_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end_id = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    output = sys.argv[4] if len(sys.argv) > 4 else os.path.expanduser(
        "~/Downloads/obsbot_confirmed_netizens.json")
    token = load_token()
    existing = {}
    if os.path.exists(output):
        with open(output) as f:
            for r in json.load(f): existing[r['id']] = r
    print(f"Scan {start_id}-{end_id} ({workers}w). Existing: {len(existing)}", flush=True)
    start = time.time()
    scanned = confirmed_n = 0
    for bs in range(start_id, end_id + 1, workers):
        ids = [i for i in range(bs, min(bs + workers, end_id + 1)) if i not in existing]
        if not ids: continue
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for f in as_completed({ex.submit(fetch_one, token, i): i for i in ids}):
                d = f.result(); scanned += 1
                if d and d.get('id') and d.get('communication_state') == 'confirm' and d['id'] not in existing:
                    existing[d['id']] = {'id': d['id'], 'platform_id': d.get('netizen_platform_id', ''),
                        'name': d.get('name', '') or '', 'country': d.get('influence_region', ''),
                        'liaison': d.get('liaison', ''), 'contact': d.get('contact', '')}
                    confirmed_n += 1
        if scanned % 500 < workers:
            print(f"  [{bs}/{end_id}] {confirmed_n} new, {len(existing)} total", flush=True)
            with open(output, 'w') as f: json.dump(list(existing.values()), f, ensure_ascii=False)
    print(f"Phase 1: {len(existing)} confirmed in {(time.time()-start)/60:.1f}min", flush=True)
    print("Phase 2: Ambassadors...", flush=True)
    amb = fetch_ambassadors(token)
    new_amb = merge_ambassadors(existing, amb)
    records = list(existing.values())
    with open(output, 'w') as f: json.dump(records, f, ensure_ascii=False)
    print(f"Done: {len(records)} total in {(time.time()-start)/60:.1f}min -> {output}", flush=True)

if __name__ == "__main__":
    main()
