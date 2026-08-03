#!/usr/bin/env python3
"""Fetch IG followers+views - slow/stable with proxy + resume + dual-endpoint."""
import os, json, subprocess, time, sys, random

input_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.hermes/workspace/ig_accounts_data.json")
output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/.hermes/workspace/ig_kol_data.json")

with open(input_path) as f:
    accounts = json.load(f)

# Load existing results to merge (resume support)
existing = {}
if os.path.exists(output_path):
    try:
        with open(output_path) as f:
            for item in json.load(f):
                existing[item['username']] = item
    except:
        pass

usernames = [a['username'] for a in accounts if a['followers'] >= 50000]
print(f"Accounts: {len(usernames)} (already have {len(existing)})", flush=True)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
PROXIES = [None, "http://127.0.0.1:1082"]  # direct first, proxy fallback
results = list(existing.values())
total = len(usernames)

def build_cmd(proxy, username):
    cmd = ["curl", "-s", "--max-time", "12",
           "-H", f"User-Agent: {UA}",
           "-H", "X-IG-App-ID: 936619743392459"]
    if proxy:
        cmd += ["--proxy", proxy]
    cmd.append(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}")
    return cmd

def fetch_one(username):
    for proxy in PROXIES:
        for attempt in range(2):
            try:
                result = subprocess.run(build_cmd(proxy, username), capture_output=True, text=True, timeout=18)
                if len(result.stdout) < 50:
                    time.sleep(4)
                    continue
                data = json.loads(result.stdout)
                user = data.get('data', {}).get('user', {})
                if not user:
                    msg = str(data.get('message', ''))
                    # Rate limited - try next proxy / wait
                    if 'wait' in msg.lower() or 'too many' in msg.lower() or 'limit' in msg.lower():
                        time.sleep(15)
                        continue
                    # Asset/other errors - permanent skip
                    return None
                followers = user.get('edge_followed_by', {}).get('count', 0)
                following = user.get('edge_follow', {}).get('count', 0)
                posts_count = user.get('edge_owner_to_timeline_media', {}).get('count', 0)
                user_id = user.get('id', '')
                media_edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
                video_views = [e['node']['video_view_count'] for e in media_edges
                               if e.get('node', {}).get('__typename') == 'GraphVideo' and e['node'].get('video_view_count')]
                avg_views = int(sum(video_views) / len(video_views)) if video_views else 0
                return {
                    'username': username, 'profile_url': f'https://www.instagram.com/{username}/',
                    'user_id': user_id, 'followers': followers, 'following': following,
                    'posts': posts_count, 'avg_video_views': avg_views,
                    'max_video_views': max(video_views) if video_views else 0,
                    'video_posts_scanned': len(video_views)
                }
            except:
                time.sleep(4)
    return None

t0 = time.time()
for i, username in enumerate(usernames):
    if username in existing:
        continue
    item = fetch_one(username)
    if item:
        results.append(item)
    if (i + 1) % 25 == 0 or (i + 1) == total:
        elapsed = time.time() - t0
        print(f"  {i+1}/{total} ({len(results)} ok, {elapsed:.0f}s)", flush=True)
        with open(output_path, 'w') as f:
            json.dump(results, f)
    time.sleep(3 + random.random() * 2)

with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
qualified = [r for r in results if r['followers'] >= 50000 and r['avg_video_views'] >= 5000]
qualified.sort(key=lambda x: x['avg_video_views'], reverse=True)
print(f"\n=== {len(results)}/{total}, Qualified: {len(qualified)} ===")
for r in qualified:
    print(f"  @{r['username']} | {r['followers']:,} | avg {r['avg_video_views']:,}")
