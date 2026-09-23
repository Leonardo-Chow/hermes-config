#!/usr/bin/env python3
"""
摸鱼日报质量评分脚本 v2.0
每次生成日报后、上传前必须执行。低于 70 分立即返工。
"""

import re
import sys

def evaluate_daily_report(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    score = 0
    details = []
    
    # 1. 板块完整性 (15分)
    required_sections = [
        '指数与全球财经', '国内热搜', '科技热点', 'AI 动态', 
        '国际视野', '娱乐圈', '开源 & 技术社区', '每日精选'
    ]
    present = sum(1 for s in required_sections if s in html)
    pts = 15 if present == len(required_sections) else max(0, 15 - (len(required_sections) - present) * 2)
    score += pts
    details.append(f'板块完整性: {present}/{len(required_sections)} = {pts}分')
    
    # 2. 内容深度 (20分)
    notes = len(re.findall(r'class="note"', html))
    zh_trans = len(re.findall(r'class="zh"', html))
    if (notes + zh_trans) > 60:
        pts = 20
    elif (notes + zh_trans) > 30:
        pts = 10
    else:
        pts = 5
    score += pts
    details.append(f'内容深度: notes={notes}, zh={zh_trans} = {pts}分')
    
    # 3. 封面图片 (10分)
    has_cover = 'class="cover"' in html and 'res-skb.ima.qq.com' in html
    pts = 10 if has_cover else 0
    score += pts
    details.append(f'封面图: {pts}分')
    
    # 4. 热搜质量 (10分)
    hot_ok = all(k in html for k in ['微博热搜', '百度热搜', '抖音热榜'])
    pts = 8 if hot_ok else 5
    score += pts
    details.append(f'热搜三平台: {pts}分')
    
    # 5. 国际双语覆盖 (10分)
    pts = 10 if zh_trans >= 12 else 6
    score += pts
    details.append(f'国际双语覆盖: {pts}分')
    
    # 6. 国际来源多样性 (15分)
    intl_sec = html.split('id="intl"')[1].split('</section>')[0] if 'id="intl"' in html else ''
    links = re.findall(r'<a href="(https?://[^"]+)"', intl_sec)
    domains = set()
    for u in links:
        m = re.search(r'https?://(?:www\.)?([^/]+)', u)
        if m: domains.add(m.group(1))
    n_src = len(domains)
    if n_src >= 5: pts = 15
    elif n_src >= 4: pts = 10
    elif n_src >= 3: pts = 5
    else: pts = 0
    score += pts
    details.append(f'国际来源 {n_src}家: {pts}分')
    
    # 7. 链接可直达性 (15分)
    bad = sum(1 for u in re.findall(r'href="(https?://[^"]+)"', html) if u.endswith('.com/') or u.endswith('.org/'))
    if bad <= 2: pts = 15
    elif bad < 10: pts = 8
    else: pts = 0
    score += pts
    details.append(f'首页级链接数={bad}: {pts}分')
    
    # 8. 数据源多样性 (5分)
    src_count = len(re.findall(r'(?:CNBC|MarketWatch|TechCrunch|Ars|Verge|BBC|NPR|Al Jazeera|France|Variety|THR|GitHub|Hacker)', html.split('<footer>')[1] if '<footer>' in html else html))
    if src_count >= 7: pts = 5
    elif src_count >= 5: pts = 3
    elif src_count >= 3: pts = 1
    else: pts = 0
    score += pts
    details.append(f'Footer数据源: {src_count}个 = {pts}分')
    
    # 双语完整性检查
    lis = re.findall(r"<li>.*?</li>", html, re.S)
    total_bi = sum(1 for li in lis if "t-en" in li)
    miss_zh = sum(1 for li in lis if "t-en" in li and 'class="zh"' not in li)
    
    print(f'=== 质量评分报告 ===')
    for d in details:
        print(f'  {d}')
    print(f'双语条数: {total_bi}, 缺中文: {miss_zh} {"✅" if miss_zh==0 else "❌"}')
    print(f'总分: {score}/100 {"✅ 合格" if score >= 70 else "❌ 需返工"}')
    
    return score, miss_zh == 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        evaluate_daily_report(sys.argv[1])
    else:
        print('Usage: python quality-check.py <html_file>')