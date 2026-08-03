#!/usr/bin/env python3
"""Debug: test first account"""
import http.client, ssl, re, json, os, time

with open(os.path.expanduser("~/.hermes/cookies/platform_cookies.json")) as f:
    cookie_data = json.load(f)
cookie_str = cookie_data.get("instagram", "")
print(f"Cookie len: {len(cookie_str)}", flush=True)

username = "ptclsn"
t0 = time.time()
try:
    ctx = ssl.create_default_context()
    conn = http.client.HTTPSConnection("www.instagram.com", timeout=10, context=ctx)
    conn.request("GET", f"/{username}/", headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
    })
    resp = conn.getresponse()
    chunks = []
    while True:
        chunk = resp.read(65536)
        if not chunk: break
        chunks.append(chunk)
    html = b''.join(chunks).decode("utf-8", errors="replace")
    conn.close()
    print(f"HTTP: {resp.status}, len: {len(html)}, time: {time.time()-t0:.1f}s", flush=True)
    
    og = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
    print(f"OG: {og is not None}", flush=True)
    if og: print(f"Followers: {og.group(1)[:60]}", flush=True)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e} (after {time.time()-t0:.1f}s)", flush=True)
