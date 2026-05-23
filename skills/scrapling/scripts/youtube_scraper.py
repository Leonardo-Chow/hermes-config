#!/usr/bin/env python3
"""
YouTube 视频批量抓取脚本（使用 Scrapling）
用法：python3 scripts/youtube_scraper.py input.json output.json [--limit N]
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

# 激活虚拟环境
VENV_PATH = Path(__file__).parent.parent / "venv"
sys.path.insert(0, str(VENV_PATH / "lib"))

from scrapling.fetchers import DynamicFetcher


def extract_youtube_video(url):
    """提取单个 YouTube 视频的详细信息"""
    page = DynamicFetcher.fetch(url, headless=True, network_idle=True, disable_resources=True)
    
    # 获取所有文本
    all_text = page.css('body *::text').getall()
    full_text = ' '.join(all_text)
    
    # 提取博主名称
    channel = 'N/A'
    channel_links = page.css('a.yt-simple-endpoint::attr(href)').getall()
    for link in channel_links:
        if '/@' in link:
            channel = '@' + link.split('/@')[1]
            break
    
    # 提取描述
    description = 'N/A'
    desc_meta = page.css('meta[name="description"]::attr(content)').get()
    if desc_meta:
        description = desc_meta[:200]
    
    # 提取浏览量
    views = 'N/A'
    view_match = re.search(r'([\d,]+)\s*次观看', full_text)
    if view_match:
        views = view_match.group(1)
    else:
        view_match = re.search(r'([\d,]+)\s*views', full_text, re.IGNORECASE)
        if view_match:
            views = view_match.group(1)
    
    # 提取点赞数
    likes = 'N/A'
    like_labels = page.css('[aria-label*="like"]::attr(aria-label)').getall()
    for label in like_labels:
        like_match = re.search(r'([\d,.]+)', label)
        if like_match:
            likes = like_match.group(1)
            break
    
    # 提取评论数
    comments = 'N/A'
    comment_match = re.search(r'([\d,.]+)\s*(?:条评论|comments)', full_text, re.IGNORECASE)
    if comment_match:
        comments = comment_match.group(1)
    
    # 提取 hashtags
    hashtags = ''
    hashtag_elems = page.css('a[href*="hashtag/"]::text').getall()
    if hashtag_elems:
        hashtags = ', '.join(list(set(hashtag_elems[:5])))
    
    return {
        'channel': channel,
        'views': views,
        'likes': likes,
        'comments': comments,
        'description': description,
        'hashtags': hashtags
    }


def main():
    parser = argparse.ArgumentParser(description='YouTube 视频批量抓取')
    parser.add_argument('input', help='输入 JSON 文件（包含视频列表）')
    parser.add_argument('output', help='输出 JSON 文件')
    parser.add_argument('--limit', type=int, default=50, help='最多抓取视频数')
    parser.add_argument('--delay', type=int, default=3, help='请求间隔（秒）')
    args = parser.parse_args()
    
    # 读取输入
    with open(args.input, 'r', encoding='utf-8') as f:
        videos = json.load(f)[:args.limit]
    
    print(f"📺 开始抓取 {len(videos)} 个视频\n")
    
    results = []
    for i, video in enumerate(videos, 1):
        url = video.get('url', '')
        title = video.get('title', '').replace(' - YouTube', '').strip()
        
        print(f"{i}. {title[:40]}...", end="")
        
        try:
            details = extract_youtube_video(url)
            results.append({
                'title': title[:80],
                'url': url,
                **details
            })
            print(f" ✅ {details['channel']} | {details['views']}次观看")
        except Exception as e:
            print(f" ❌ {str(e)[:30]}")
            results.append({
                'title': title[:80],
                'url': url,
                'channel': 'N/A',
                'views': 'N/A',
                'likes': 'N/A',
                'comments': 'N/A',
                'description': '',
                'hashtags': ''
            })
        
        time.sleep(args.delay)
        
        # 每 10 个视频保存一次
        if i % 10 == 0:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 最终保存
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！共抓取 {len(results)} 个视频")
    print(f"💾 保存到 {args.output}")


if __name__ == '__main__':
    main()
