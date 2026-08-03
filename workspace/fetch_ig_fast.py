#!/usr/bin/env python3
"""Fetch IG followers - concurrent version. 5 parallel workers."""
import os, json, re, urllib.request, time
from concurrent.futures import ThreadPoolExecutor, as_completed

csv_path = os.path.expanduser("~/.hermes/workspace/ig_following_cheskasuz.csv")
output_path = os.path.expanduser("~/.hermes/workspace/ig_accounts_data.json")

with open(csv_path) as f:
    lines = f.read().strip().split('\n')
usernames = [line.split(',')[0].strip() for line in lines[1:] if line.strip()]
total = len(usernames)
print(f"Total accounts: {total}", flush=True)

with open(os.path.expanduser("~/.hermes/cookies/platform_cookies.json")) as f:
    cookie_data = json.load(f)
cookie_str = cookie_data.get("instagram", "")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
    'Cookie': cookie_str,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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

def fetch_account(username):
    try:
        req = urllib.request.Request(f'https://www.instagram.com/{username}/', headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=10) as resp:
            chunk = resp.read(50000).decode('utf-8', errors='replace')
        
        og_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', chunk)
        if og_match:
            desc = og_match.group(1)
            followers = parse_count(desc.split('Followers')[0]) if 'Followers' in desc else 0
            following = parse_count(desc.split('Following')[0].split('Followers')[-1]) if 'Following' in desc else 0
            posts_match = re.search(r'([\d,]+(?:\.\d+)?)\s*Posts', desc)
            posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0
            return username, followers, following, posts
        return username, 0, 0, 0
    except:
        return username, 0, 0, 0

# Split into batches of 50 for saving progress
batch_size = 50
all_results = []

for batch_start in range(0, total, batch_size):
    batch = usernames[batch_start:batch_start + batch_size]
    batch_results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        fut_map = {executor.submit(fetch_account, u): u for u in batch}
        for future in as_completed(fut_map):
            r = future.result()
            if r[1] > 0:
                batch_results.append({
                    'username': r[0], 'profile_url': f'https://www.instagram.com/{r[0]}/',
                    'followers': r[1], 'following': r[2], 'posts': r[3]
                })
    
    all_results.extend(batch_results)
    progress = min(batch_start + batch_size, total)
    print(f"  Batch {batch_start//batch_size + 1}: {progress}/{total} ({len(all_results)} found)", flush=True)
    
    with open(output_path, 'w') as f:
        json.dump(all_results, f)
    
    time.sleep(2)  # 2s pause between batches

high_followers = [r for r in all_results if r['followers'] >= 50000]
high_followers.sort(key=lambda x: x['followers'], reverse=True)

print(f"\n=== RESULTS ===")
print(f"Processed: {len(all_results)}/{total}")
print(f"Followers > 50K: {len(high_followers)}")
for r in high_followers:
    print(f"  @{r['username']} - {r['followers']:,} followers, {r['posts']} posts")
