#!/usr/bin/env python3
"""Fetch IG followers for a given following CSV - parameterized."""
import os, json, re, urllib.request, time, sys

csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.hermes/workspace/ig_following_cheskasuz.csv")
output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/.hermes/workspace/ig_accounts_data.json")

with open(csv_path) as f:
    lines = f.read().strip().split('\n')
usernames = [line.split(',')[0].strip() for line in lines[1:] if line.strip()]
total = len(usernames)
print(f"Total: {total}", flush=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html',
}

def parse_count(s):
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*([KMB]?)', s)
    if not m: return 0
    num = float(m.group(1).replace(',', ''))
    suf = m.group(2)
    if suf == 'K': num *= 1000
    elif suf == 'M': num *= 1000000
    elif suf == 'B': num *= 1000000000
    return int(num)

results = []
for i, username in enumerate(usernames):
    try:
        req = urllib.request.Request(f'https://www.instagram.com/{username}/', headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            chunk = resp.read(50000).decode('utf-8', errors='replace')
        
        og = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', chunk)
        if og:
            desc = og.group(1)
            f_match = re.search(r'([\d,]+[KMB]?)\s*Followers', desc)
            flw_match = re.search(r'([\d,]+[KMB]?)\s*Following', desc)
            p_match = re.search(r'([\d,]+(?:\.\d+)?)\s*Posts', desc)
            results.append({
                'username': username,
                'profile_url': f'https://www.instagram.com/{username}/',
                'followers': parse_count(f_match.group(1)) if f_match else 0,
                'following': parse_count(flw_match.group(1)) if flw_match else 0,
                'posts': int(p_match.group(1).replace(',', '')) if p_match else 0
            })
    except:
        pass

    if (i + 1) % 50 == 0 or (i + 1) == total:
        print(f"  {i+1}/{total}\t({len(results)} found)", flush=True)
        with open(output_path, 'w') as f:
            json.dump(results, f)

    time.sleep(0.3)

with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

high = [r for r in results if r['followers'] >= 50000]
high.sort(key=lambda x: x['followers'], reverse=True)
print(f"\n=== {len(results)}/{total}, >50K: {len(high)} ===")
for r in high:
    print(f"  @{r['username']} - {r['followers']:,}")
