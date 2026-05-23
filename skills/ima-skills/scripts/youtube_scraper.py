#!/usr/bin/env python3

"""
YouTube 视频详情提取脚本（使用 Scrapling）
用法：python3 scripts/youtube_scraper.py [--limit N]
"""

import json
import re
from scrapling.fetchers import DynamicFetcher
from playwright.sync_api import Page


def deep_scroll(page: Page):
    """深度滚动触发点赞和评论加载"""
    page.wait_for_timeout(3000)
    page.mouse.wheel(0, 500)
    page.wait_for_timeout(2000)
    for _ in range(8):
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(1500)


def extract_video_data(url):
    """提取视频完整数据"""
    try:
        page = DynamicFetcher.fetch(
            url, 
            headless=True, 
            network_idle=True, 
            disable_resources=True,
            page_action=deep_scroll
        )
        
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
        view_text = page.css('span.view-count::text').get()
        if view_text:
            views = view_text.replace('次观看', '').replace('views', '').strip()
        
        # 提取点赞数
        likes = 'N/A'
        like_labels = page.css('[aria-label*="like this video"]::attr(aria-label)').getall()
        for label in like_labels:
            like_match = re.search(r'([\d,.]+)', label)
            if like_match:
                likes = like_match.group(1)
                break
        
        # 提取评论数
        comments = 'N/A'
        all_text = page.css('body *::text').getall()
        full_text = ' '.join(all_text)
        
        comment_patterns = [
            r'([\d,.]+)\s*条评论',
            r'([\d,.]+)\s*Comments',
            r'([\d,.]+)\s*comments',
        ]
        
        for pattern in comment_patterns:
            comment_match = re.search(pattern, full_text, re.IGNORECASE)
            if comment_match:
                comments = comment_match.group(1)
                break
        
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
            'description': description[:150],
            'hashtags': hashtags
        }
        
    except Exception as e:
        return {
            'channel': 'N/A',
            'views': 'N/A',
            'likes': 'N/A',
            'comments': 'N/A',
            'description': '',
            'hashtags': ''
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='YouTube 视频详情提取脚本')
    parser.add_argument('--limit', type=int, default=35, help='提取视频数量')
    args = parser.parse_args()
    
    # 读取视频数据
    with open('/tmp/obsbot_videos.json', 'r') as f:
        videos = json.load(f)
    
    videos = videos[:args.limit]
    print(f"📺 开始提取 {len(videos)} 个视频的详情\n")
    
    video_details = []
    
    for i, video in enumerate(videos, 1):
        url = video['url']
        title = video['title'].replace(' - YouTube', '').strip()
        
        print(f"{i}. {title[:40]}...", end="")
        
        result = extract_video_data(url)
        result['title'] = title[:80]
        result['url'] = url
        
        video_details.append(result)
        
        print(f" ✅ {result['channel']} | {result['views']}次观看 | 👍{result['likes']} | 💬{result['comments']}")
    
    # 保存结果
    with open('/tmp/obsbot_final_details.json', 'w', encoding='utf-8') as f:
        json.dump(video_details, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 已获取 {len(video_details)} 个视频的详情")
    print(f"💾 保存到 /tmp/obsbot_final_details.json")


if __name__ == '__main__':
    main()
