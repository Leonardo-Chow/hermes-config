#!/usr/bin/env python3
"""
TikTok OBSBOT content discovery via search page + oembed API + video ID timestamp decode.

Usage: python3 scripts/tiktok_oembed_search.py [date] [keyword]
  date: YYYY-MM-DD (default: today)
  keyword: search term (default: OBSBOT)

Requires: VPN connected (Shadowrocket at 127.0.0.1:1082)
"""
import sys, json, subprocess
from datetime import datetime, date

# Config
PROXY = "http://127.0.0.1:1082"
SEARCH_KEYWORDS = ["OBSBOT", "obsbot tiny 3", "obsbot tail 2", "obsbot meet 2"]

def search_tiktok(keyword):
    """Get video links from TikTok search page via Scrapling."""
    # Use Scrapling StealthyFetcher
    script = f"""
import sys
sys.path.insert(0, '/Users/zhoulong/.hermes/skills/scrapling/venv/lib/python3.12/site-packages')
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch(
    'https://www.tiktok.com/search?q={keyword}',
    headless=True, network_idle=True, disable_resources=True,
    proxy='{PROXY}', block_webrtc=True, hide_canvas=True
)
links = page.css('a[href*="/video/"]::attr(href)').getall()
for l in links: print(l)
"""
    result = subprocess.run(
        ['/Users/zhoulong/.hermes/skills/scrapling/venv/bin/python3', '-c', script],
        capture_output=True, text=True, timeout=120
    )
    return [l.strip() for l in result.stdout.strip().split('\n') if '/video/' in l]

def get_video_meta(url):
    """Get video metadata via oembed API (must use proxy)."""
    result = subprocess.run(
        ['curl', '-s', '--max-time', '8', '-x', PROXY,
         f'https://www.tiktok.com/oembed?url={url}'],
        capture_output=True, text=True, timeout=15
    )
    try:
        data = json.loads(result.stdout)
        return {'author': data.get('author_name', 'N/A'), 'title': data.get('title', 'N/A')[:100]}
    except:
        return None

def decode_video_date(video_url):
    """Extract publish date from TikTok video ID."""
    try:
        vid_id = video_url.split('/video/')[-1].split('?')[0]
        ts = int(vid_id) >> 32
        return datetime.fromtimestamp(ts).date()
    except:
        return None

def main():
    target_date = date.today()
    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    
    keywords = [sys.argv[2]] if len(sys.argv) > 2 else SEARCH_KEYWORDS
    
    print(f"Searching TikTok for date: {target_date}")
    print(f"Keywords: {keywords}")
    print("=" * 60)
    
    all_videos = {}
    
    for kw in keywords:
        print(f"\nSearching: {kw}")
        try:
            links = search_tiktok(kw)
            print(f"  Found {len(links)} video links")
            
            for url in links:
                vid_id = url.split('/video/')[-1].split('?')[0]
                if vid_id in all_videos:
                    continue
                
                pub_date = decode_video_date(url)
                meta = get_video_meta(url)
                
                all_videos[vid_id] = {
                    'url': url,
                    'date': str(pub_date) if pub_date else 'unknown',
                    'author': meta['author'] if meta else 'unknown',
                    'title': meta['title'] if meta else 'unknown',
                    'keyword': kw,
                    'is_today': pub_date == target_date if pub_date else False
                }
        except Exception as e:
            print(f"  Error: {e}")
    
    # Filter today's videos
    today_videos = {k: v for k, v in all_videos.items() if v['is_today']}
    
    print(f"\n{'='*60}")
    print(f"Total unique videos: {len(all_videos)}")
    print(f"Today's videos: {len(today_videos)}")
    
    if today_videos:
        print(f"\n=== {target_date} TikTok Videos ===")
        for vid_id, info in today_videos.items():
            print(f"\n@{info['author']}: {info['title']}")
            print(f"  URL: {info['url']}")
    
    # Save results
    output = {'date': str(target_date), 'all': list(all_videos.values()), 'today': list(today_videos.values())}
    with open('/tmp/tiktok_results.json', 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to /tmp/tiktok_results.json")

if __name__ == '__main__':
    main()
