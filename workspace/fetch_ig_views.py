#!/usr/bin/env python3
"""Fetch IG followers + views - FAST anonymous API (curl, 1s delay)."""
import os, json, subprocess, time, sys

input_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.hermes/workspace/ig_accounts_data.json")
output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/.hermes/workspace/ig_kol_data.json")

with open(input_path) as f:
    accounts = json.load(f)

# Load existing results to merge
existing = {}
if os.path.exists(output_path):
    try:
        with open(output_path) as f:
            for item in json.load(f):
                existing[item['username']] = item
    except:
        pass

usernames = [a['username'] for a in accounts if a['followers'] >= 50000]
print(f"Accounts to process (>=50K followers): {len(usernames)} (already have {len(existing)})", flush=True)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
results = list(existing.values())
total = len(usernames)

def fetch_one(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    for attempt in range(3):
        try:
            cmd = [
                "curl", "-s", "--max-time", "10",
                "--proxy", "http://127.0.0.1:1082",
                "-H", f"User-Agent: {UA}",
                "-H", "X-IG-App-ID: 936619743392459",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if len(result.stdout) < 50:
                time.sleep(5)
                continue
            data = json.loads(result.stdout)
            user = data.get('data', {}).get('user', {})
            if not user:
                # Asset error / other - skip permanently
                return None
            followers = user.get('edge_followed_by', {}).get('count', 0)
            following = user.get('edge_follow', {}).get('count', 0)
            posts_count = user.get('edge_owner_to_timeline_media', {}).get('count', 0)
            user_id = user.get('id', '')
            
            media_edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
            video_views = []
            for e in media_edges:
                node = e.get('node', {})
                if node.get('__typename') == 'GraphVideo' and node.get('video_view_count'):
                    video_views.append(node['video_view_count'])
            
            avg_views = int(sum(video_views) / len(video_views)) if video_views else 0
            max_views = max(video_views) if video_views else 0
            
            return {
                'username': username,
                'profile_url': f'https://www.instagram.com/{username}/',
                'user_id': user_id,
                'followers': followers,
                'following': following,
                'posts': posts_count,
                'avg_video_views': avg_views,
                'max_video_views': max_views,
                'video_posts_scanned': len(video_views)
            }
        except:
            time.sleep(5)
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
        print(f"  {i+1}/{total} ({len(results)} ok, {elapsed:.0f}s elapsed)", flush=True)
        with open(output_path, 'w') as f:
            json.dump(results, f)
    
    time.sleep(1.0)

with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

qualified = [r for r in results if r['followers'] >= 50000 and r['avg_video_views'] >= 5000]
qualified.sort(key=lambda x: x['avg_video_views'], reverse=True)

print(f"\n=== RESULTS ({time.time()-t0:.0f}s total) ===")
print(f"Fetched: {len(results)}/{total}")
print(f"Qualified (followers>=50K AND avg_views>=5K): {len(qualified)}")
for r in qualified:
    print(f"  @{r['username']} | {r['followers']:,} followers | avg {r['avg_video_views']:,} views")
