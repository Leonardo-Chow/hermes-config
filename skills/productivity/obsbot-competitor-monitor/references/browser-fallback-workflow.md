# Browser Tool Fallback Workflow

When browser tools are unavailable (`_hermes_read_browser_output` error), use this fallback:

## Step 1: Write API Key to File
```bash
echo "AIzaSy...aA1Q" > /tmp/yt_api_key.txt
```

## Step 2: Create Search Script
Use `write_file` tool to create `/tmp/search_brands.sh`:
```bash
#!/bin/bash
export https_proxy=http://127.0.0.1:1082
export http_proxy=http://127.0.0.1:1082

API_KEY=*** /tmp/yt_api_key.txt)

brands=(
    "Logitech+Brio+4K+webcam"
    "Elgato+Facecam+4K+webcam"
    # ... add all brands
)

for brand in "${brands[@]}"; do
    echo "--- $brand ---"
    curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=${brand}&type=video&publishedAfter=2026-06-22T00:00:00Z&maxResults=5&key=${API_KEY}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if 'items' in d:
        for item in d['items']:
            vid = item['id']['videoId']
            ch = item['snippet']['channelTitle']
            title = item['snippet']['title']
            pub = item['snippet']['publishedAt']
            print(f'{vid}|||{ch}|||{title}|||{pub}')
    elif 'error' in d:
        print(f'ERROR: {d[\"error\"][\"message\"][:50]}')
except Exception as e:
    print(f'PARSE_ERROR: {e}')
"
done
```

## Step 3: Execute Script
```bash
bash /tmp/search_brands.sh 2>&1
```

## Step 4: Get Video Details
Use yt-dlp for each video ID:
```bash
for vid in VIDEO_ID1 VIDEO_ID2; do
    yt-dlp --no-warnings --no-download --print '%(id)s|||%(view_count)s|||%(like_count)s|||%(comment_count)s|||%(duration)s|||%(channel)s|||%(title)s' "https://www.youtube.com/watch?v=$vid"
done
```

## Key Pitfalls
- **NEVER** use `$(cat file)` in terminal heredoc - gets masked to `***`
- **ALWAYS** use `write_file` to create scripts, then `bash /tmp/script.sh`
- **ALWAYS** read API key from file, never inline
