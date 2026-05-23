#!/usr/bin/env python3

"""
BBC 新闻抓取脚本（使用 Scrapling）
用法：python3 scripts/bbc_scraper.py [--limit N] [--output FILE]
"""

import argparse
import json
import sys
from pathlib import Path

# 添加虚拟环境路径
VENV_PATH = Path(__file__).parent.parent / "venv" / "lib"
sys.path.insert(0, str(VENV_PATH))

from scrapling.fetchers import DynamicFetcher


def fetch_bbc_news(limit=10, output_file=None):
    """抓取 BBC 新闻"""
    
    print("=== 🛡️ 用 Scrapling 抓取 BBC ===\n")
    
    try:
        # 抓取 BBC News
        page = DynamicFetcher.fetch(
            'https://www.bbc.com/news',
            headless=True,
            network_idle=True,
            disable_resources=True,
        )
        
        print(f"✅ 页面抓取成功！\n")
        
        # 提取标题
        h2_titles = page.css('h2::text').getall()
        h3_titles = page.css('h3::text').getall()
        
        # 合并并去重
        all_titles = h2_titles + h3_titles
        seen = set()
        unique_titles = []
        for t in all_titles:
            t = t.strip()
            if t and len(t) > 10 and t not in seen:
                seen.add(t)
                unique_titles.append(t)
        
        # 提取新闻链接
        all_links = page.css('a::attr(href)').getall()
        news_links = list(set([l for l in all_links if '/news/articles' in l]))
        
        # 配对标题和链接
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
        
        # 输出结果
        print(f"📰 BBC 新闻 TOP {len(news_list)}\n")
        print("═" * 70)
        
        for item in news_list:
            print(f"\n{item['rank']}. {item['title']}")
            if item['link']:
                print(f"   🔗 {item['link']}")
        
        print("\n" + "═" * 70)
        print(f"\n📊 共找到 {len(news_list)} 条新闻")
        
        # 保存到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(news_list, f, ensure_ascii=False, indent=2)
            print(f"\n💾 数据已保存到: {output_file}")
        
        return news_list
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    parser = argparse.ArgumentParser(description='BBC 新闻抓取脚本')
    parser.add_argument('--limit', type=int, default=10, help='抓取新闻数量（默认10）')
    parser.add_argument('--output', type=str, help='输出文件路径（JSON格式）')
    
    args = parser.parse_args()
    
    news = fetch_bbc_news(limit=args.limit, output_file=args.output)
    
    if news:
        print(f"\n✅ 抓取完成！共 {len(news)} 条新闻")
    else:
        print(f"\n❌ 抓取失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
