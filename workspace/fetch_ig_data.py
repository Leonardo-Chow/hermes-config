#!/usr/bin/env python3
"""Fetch Instagram follower/following/posts counts for a list of usernames."""

import os
import json
import subprocess
import re
import time
import csv
import sys

CSV_PATH = os.path.expanduser("~/.hermes/workspace/ig_following_cheskasuz.csv")
OUTPUT_PATH = os.path.expanduser("~/.hermes/workspace/ig_accounts_data.json")
COOKIE_PATH = os.path.expanduser("~/.hermes/cookies/platform_cookies.json")
BATCH_SIZE = 50
DELAY = 0.3  # seconds between requests

# Load cookies
with open(COOKIE_PATH) as f:
    cookie_data = json.load(f)
cookie_str = cookie_data.get("instagram", "")
if not cookie_str:
    print("ERROR: No Instagram cookie found in platform_cookies.json")
    sys.exit(1)
print(f"Cookie loaded (len={len(cookie_str)})")

# Read usernames from CSV
usernames = []
with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        usernames.append(row['username'].strip())

print(f"Total usernames to process: {len(usernames)}")

def parse_count(text):
    """Parse a count string like '43M', '142K', '847' into an integer."""
    text = text.strip().replace(',', '')
    if not text:
        return 0
    if text.upper().endswith('M'):
        return int(float(text[:-1]) * 1_000_000)
    elif text.upper().endswith('K'):
        return int(float(text[:-1]) * 1_000)
    elif text.upper().endswith('B'):
        return int(float(text[:-1]) * 1_000_000_000)
    else:
        return int(text) if text else 0

def parse_og_description(og_text):
    """Parse og:description like '847 Followers, 595 Following, 299 Posts'"""
    if not og_text:
        return None
    # Pattern: "X Followers, Y Following, Z Posts - See Instagram photos..."
    pattern = r'([\d.,]+[KkMmBb]?)\s*Followers?,\s*([\d.,]+[KkMmBb]?)\s*Following?,\s*([\d.,]+[KkMmBb]?)\s*Posts?'
    m = re.search(pattern, og_text, re.IGNORECASE)
    if m:
        followers = parse_count(m.group(1))
        following = parse_count(m.group(2))
        posts = parse_count(m.group(3))
        return followers, following, posts
    return None

def fetch_profile(username):
    """Fetch Instagram profile and parse counts."""
    url = f"https://www.instagram.com/{username}/"
    try:
        result = subprocess.run([
            "curl", "-s", "--max-time", "10",
            "-H", f"Cookie: {cookie_str}",
            "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            url
        ], capture_output=True, text=True, timeout=15)
        html = result.stdout
        
        # Check for og:description
        og_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
        if og_match:
            parsed = parse_og_description(og_match.group(1))
            if parsed:
                followers, following, posts = parsed
                return {
                    "username": username,
                    "profile_url": url,
                    "followers": followers,
                    "following": following,
                    "posts": posts
                }
        
        # Check if it's a private/not-found account
        if '"is_private":true' in html:
            return {
                "username": username,
                "profile_url": url,
                "followers": None,
                "following": None,
                "posts": None,
                "error": "private"
            }
        
        if 'This page is not available' in html or 'The link you followed may be broken' in html:
            return {
                "username": username,
                "profile_url": url,
                "followers": None,
                "following": None,
                "posts": None,
                "error": "not_found"
            }
        
        # Try to extract from JSON-LD or window._sharedData
        # Also check if we got a login wall
        if 'login' in html.lower() and ('Log In' in html or 'log in' in html):
            return {
                "username": username,
                "profile_url": url,
                "followers": None,
                "following": None,
                "posts": None,
                "error": "login_required"
            }
        
        return {
            "username": username,
            "profile_url": url,
            "followers": None,
            "following": None,
            "posts": None,
            "error": "parse_failed"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "username": username,
            "profile_url": url,
            "followers": None,
            "following": None,
            "posts": None,
            "error": "timeout"
        }
    except Exception as e:
        return {
            "username": username,
            "profile_url": url,
            "followers": None,
            "following": None,
            "posts": None,
            "error": str(e)
        }

# Main loop - process in batches
all_results = []
total = len(usernames)

# Load existing results if any (resume support)
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH) as f:
        all_results = json.load(f)
    processed = {r["username"] for r in all_results}
    print(f"Found existing results with {len(processed)} usernames")
else:
    processed = set()

start_time = time.time()

for i, username in enumerate(usernames):
    if username in processed:
        continue
    
    result = fetch_profile(username)
    all_results.append(result)
    
    # Progress
    done = i + 1
    elapsed = time.time() - start_time
    rate = done / elapsed if elapsed > 0 else 0
    remaining = (total - done) / rate if rate > 0 else 0
    
    status = result.get("error", "ok") if result.get("followers") is None else f"ok({result['followers']}f)"
    print(f"[{done}/{total}] {username:30s} -> {status:20s}  ({rate:.1f}/s, {remaining:.0f}s remaining)")
    
    # Save after each batch
    if (done) % BATCH_SIZE == 0 or done == total:
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"  -> Saved {len(all_results)} results to {OUTPUT_PATH}")
    
    time.sleep(DELAY)

# Final save
with open(OUTPUT_PATH, 'w') as f:
    json.dump(all_results, f, indent=2)

elapsed = time.time() - start_time
print(f"\n{'='*60}")
print(f"Completed! {len(all_results)} results in {elapsed:.0f}s ({len(all_results)/elapsed:.1f}/s)")

# Summary
ok_count = sum(1 for r in all_results if r.get("followers") is not None)
error_count = sum(1 for r in all_results if r.get("followers") is None)
print(f"Successful: {ok_count}, Errors: {error_count}")
if error_count > 0:
    error_types = {}
    for r in all_results:
        if r.get("followers") is None:
            e = r.get("error", "unknown")
            error_types[e] = error_types.get(e, 0) + 1
    for etype, ecount in sorted(error_types.items(), key=lambda x: -x[1]):
        print(f"  {etype}: {ecount}")
print(f"Results saved to: {OUTPUT_PATH}")
