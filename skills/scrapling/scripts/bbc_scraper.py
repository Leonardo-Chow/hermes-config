#!/usr/bin/env python3

"""
BBC News scraper using Scrapling (dynamic mode).
Requires: VPN connected, scrapling venv activated.

Usage:
    source ~/.hermes/skills/scrapling/venv/bin/activate
    python3 scripts/bbc_scraper.py [--limit N] [--output FILE]
"""

import argparse
import json
import sys
from pathlib import Path

from scrapling.fetchers import DynamicFetcher


def fetch_bbc_news(limit=10, output_file=None):
    """Fetch BBC News headlines with links."""
    
    print("=== Scrapling BBC Fetcher ===\n")
    
    try:
        page = DynamicFetcher.fetch(
            'https://www.bbc.com/news',
            headless=True,
            network_idle=True,
            disable_resources=True,
        )
        
        print(f"Page fetched successfully\n")
        
        # Extract titles
        h2_titles = page.css('h2::text').getall()
        h3_titles = page.css('h3::text').getall()
        
        # Deduplicate
        seen = set()
        unique_titles = []
        for t in h2_titles + h3_titles:
            t = t.strip()
            if t and len(t) > 10 and t not in seen:
                seen.add(t)
                unique_titles.append(t)
        
        # Extract article links
        all_links = page.css('a::attr(href)').getall()
        news_links = list(set([l for l in all_links if '/news/articles' in l]))
        
        # Pair titles with links
        news_list = []
        for i, title in enumerate(unique_titles[:limit]):
            link = ""
            if i < len(news_links):
                link = f"https://www.bbc.com{news_links[i]}"
            news_list.append({
                'rank': i + 1,
                'title': title,
                'link': link
            })
        
        # Output
        print(f"BBC News TOP {len(news_list)}\n")
        print("=" * 70)
        for item in news_list:
            print(f"\n{item['rank']}. {item['title']}")
            if item['link']:
                print(f"   {item['link']}")
        print("\n" + "=" * 70)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(news_list, f, ensure_ascii=False, indent=2)
            print(f"\nSaved to: {output_file}")
        
        return news_list
        
    except Exception as e:
        print(f"Fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    parser = argparse.ArgumentParser(description='BBC News scraper')
    parser.add_argument('--limit', type=int, default=10, help='Number of articles')
    parser.add_argument('--output', type=str, help='Output JSON file path')
    args = parser.parse_args()
    
    news = fetch_bbc_news(limit=args.limit, output_file=args.output)
    if not news:
        sys.exit(1)


if __name__ == '__main__':
    main()
