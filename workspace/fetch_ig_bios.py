#!/usr/bin/env python3
"""Fetch IG bios for qualified accounts via web_profile_info API."""
import os, json, subprocess, time

input_path = os.path.expanduser("~/.hermes/workspace/ig_kol_data.json")
output_path = os.path.expanduser("~/.hermes/workspace/ig_kol_bios.json")

with open(input_path) as f:
    accounts = json.load(f)

qualified = [a for a in accounts if a['followers'] >= 50000 and a['avg_video_views'] >= 5000]
print(f"Accounts to fetch bios: {len(qualified)}", flush=True)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
results = []

for i, a in enumerate(qualified):
    username = a['username']
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    try:
        result = subprocess.run([
            "curl", "-s", "--max-time", "10",
            "-H", f"User-Agent: {UA}",
            "-H", "X-IG-App-ID: 936619743392459",
            url
        ], capture_output=True, text=True, timeout=15)
        
        if len(result.stdout) > 50:
            data = json.loads(result.stdout)
            user = data.get('data', {}).get('user', {})
            if user:
                bio = user.get('biography', '')
                full_name = user.get('full_name', '')
                category = user.get('category_name', '') or user.get('business_category_name', '')
                is_verified = user.get('is_verified', False)
                is_business = user.get('is_business_account', False)
                results.append({
                    'username': username,
                    'full_name': full_name,
                    'bio': bio,
                    'category': category,
                    'is_verified': is_verified,
                    'is_business': is_business,
                    'followers': a['followers'],
                    'avg_video_views': a['avg_video_views']
                })
                print(f"  [{i+1}] @{username}: {full_name[:30]} | {category} | {bio[:50]}", flush=True)
            else:
                print(f"  [{i+1}] @{username}: no user data", flush=True)
    except Exception as e:
        print(f"  [{i+1}] @{username}: ERROR {type(e).__name__}", flush=True)
    
    if (i + 1) % 20 == 0 or (i + 1) == len(qualified):
        with open(output_path, 'w') as f:
            json.dump(results, f, ensure_ascii=False)
    
    time.sleep(1.2)

with open(output_path, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nDone: {len(results)}/{len(qualified)}")
