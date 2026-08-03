#!/usr/bin/env python3
"""
Batch fetch Instagram follower counts from a CSV list of usernames.
Usage:
  1. Place CSV with 'username,profile_url' in current dir
  2. Update csv_path below
  3. Run: python3 batch_fetch_ig.py

Produces ig_accounts_data.json
"""
import os, json, re, subprocess, time

csv_path = "ig_following_export.csv"
output_path = "ig_accounts_data.json"

with open(csv_path) as f:
    lines = f.read().strip().split('\n')
usernames = [line.split(',')[0].strip() for line in lines[1:] if line.strip()]

print(f"Total: {len(usernames)}", flush=True)

# Read cookies
cookie_file = os.path.expanduser("~/.hermes/cookies/platform_cookies.json")
if not os.path.exists(cookie_file):
    print(f"ERROR: {cookie_file} not found!")
    exit(1)

with open(cookie_file) as f:
    cookie_data = json.load(f)
cookie_str = cookie_data.get("instagram", "")
if not cookie_str:
    print("ERROR: No Instagram cookies found!")
    exit(1)

results = []
total = len(usernames)
tmp_dir = "/tmp/ig_batch"
os.makedirs(tmp_dir, exist_ok=True)

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
    tmp_file = os.path.join(tmp_dir, f"{username}.html")
    try:
        subprocess.run([
            "curl", "-s", "--max-time", "10",
            "-H", f"Cookie: {cookie_str}",
            "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            "-o", tmp_file,
            f"https://www.instagram.com/{username}/"
        ], check=False, timeout=15)

        if os.path.exists(tmp_file) and os.path.getsize(tmp_file) > 500:
            with open(tmp_file, 'r', encoding='utf-8', errors='replace') as f:
                html = f.read()
            os.remove(tmp_file)

            og_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
            if og_match:
                desc = og_match.group(1)
                followers = parse_count(desc.split('Followers')[0]) if 'Followers' in desc else \
                            parse_count(desc.split('粉丝')[0]) if '粉丝' in desc else 0
                following = parse_count(desc.split('Following')[0].split('Followers')[-1]) if 'Following' in desc else \
                            parse_count(desc.split('关注')[0].split('粉丝')[-1]) if '关注' in desc else 0
                posts_match = re.search(r'([\d,]+(?:\.\d+)?)\s*Posts', desc) or \
                              re.search(r'([\d,]+(?:\.\d+)?)\s*帖子', desc)
                posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0

                results.append({
                    'username': username,
                    'profile_url': f'https://www.instagram.com/{username}/',
                    'followers': followers,
                    'following': following,
                    'posts': posts
                })
    except:
        pass

    if (i + 1) % 25 == 0:
        print(f"  {i+1}/{total} ({len(results)} found)", flush=True)

    if (i + 1) % 100 == 0 or i == total - 1:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

    time.sleep(0.5)  # ⚠️ Rate limiting protection

# Cleanup
for f in os.listdir(tmp_dir):
    os.remove(os.path.join(tmp_dir, f))
os.rmdir(tmp_dir)

with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

high = [r for r in results if r['followers'] >= 50000]
high.sort(key=lambda x: x['followers'], reverse=True)

print(f"\n=== RESULTS ===")
print(f"Processed: {len(results)}/{total}")
print(f"Followers > 50K: {len(high)}")
for r in high:
    print(f"  @{r['username']} - {r['followers']:,}")
