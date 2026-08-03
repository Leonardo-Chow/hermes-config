#!/usr/bin/env python3
"""Fetch Instagram follower counts - MINIMAL."""
import os, json, re, time, http.client

csv_path = os.path.expanduser("~/.hermes/workspace/ig_following_cheskasuz.csv")
output_path = os.path.expanduser("~/.hermes/workspace/ig_accounts_data.json")

with open(csv_path) as f:
    lines = f.read().strip().split('\n')
usernames = [line.split(',')[0].strip() for line in lines[1:] if line.strip()]
print(f"Total: {len(usernames)}", flush=True)

results = []
total = len(usernames)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def parse_count(s):
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*([KMB]?)', s)
    if not m: return 0
    num = float(m.group(1).replace(',', ''))
    suf = m.group(2)
    if suf == 'K': num *= 1000
    elif suf == 'M': num *= 1000000
    elif suf == 'B': num *= 1000000000
    return int(num)

for i, username in enumerate(usernames):
    conn = http.client.HTTPSConnection("www.instagram.com", timeout=10)
    conn.request("GET", f"/{username}/", headers={"User-Agent": UA})
    resp = conn.getresponse()
    html = resp.read().decode("utf-8", errors="replace")
    conn.close()
    
    if len(html) > 500:
        og_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
        if og_match:
            desc = og_match.group(1)
            followers = parse_count(desc.split('Followers')[0]) if 'Followers' in desc else 0
            # Extract following count - text between 'Followers, ' and ' Following'
            following_match = re.search(r'([\d,]+[KMB]?)\s*Following', desc)
            following = parse_count(following_match.group(1)) if following_match else 0
            posts_match = re.search(r'([\d,]+(?:\.\d+)?)\s*Posts', desc)
            posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0
            results.append({'username': username, 'profile_url': f'https://www.instagram.com/{username}/', 'followers': followers, 'following': following, 'posts': posts})

    if (i + 1) % 50 == 0:
        print(f"  {i+1}/{total} ({len(results)} found)", flush=True)
    if (i + 1) % 100 == 0 or (i + 1) == total:
        with open(output_path, 'w') as f: json.dump(results, f, indent=2)
    time.sleep(0.3)

with open(output_path, 'w') as f: json.dump(results, f, indent=2)
high = [r for r in results if r['followers'] >= 50000]
high.sort(key=lambda x: x['followers'], reverse=True)
print(f"\n=== {len(results)}/{total}, >50K: {len(high)} ===")
for r in high:
    print(f"  @{r['username']} - {r['followers']:,}")
