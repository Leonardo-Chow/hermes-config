"""
摸鱼日报质量评分脚本（v2.0 — 2026-05-19 更新）
评分标准：满分100分，低于70分需返工
"""
import re

def evaluate_daily_report(report_content: str) -> dict:
    score = 0
    details = {}
    
    # 1. 板块完整性 (15分)
    required = ['今日金句', '信息差', 'A股', '微博热搜', '百度热搜', '抖音热榜',
                'Reddit', '全球市场', 'GitHub', 'AI Agent Skill', '科技热点', 'AI发展',
                '娱乐圈', '国际新闻', '每日精选', '数据概览']
    present = sum(1 for s in required if s in report_content)
    s1 = (present / len(required)) * 15
    score += s1
    details['板块完整性'] = f"{present}/{len(required)} = {s1:.1f}/15"
    
    # 2. 内容深度 (20分)
    analysis = report_content.count('简析') + report_content.count('分析') + \
               report_content.count('📝') + report_content.count('简介')
    s2 = 20 if analysis >= 20 else (12 if analysis >= 10 else 5)
    score += s2
    details['内容深度'] = f"{analysis} 处 = {s2}/20"
    
    # 3. 封面图片 (10分) — 必须有 ima.qq.com(正常) 或 placehold.co(IMA降级) 图片
    has_cover = '![' in report_content and ('ima.qq.com' in report_content or 'placehold.co' in report_content)
    s3 = 10 if has_cover else 0
    score += s3
    details['封面图片'] = f"{'✅' if has_cover else '❌'} = {s3}/10"
    
    # 4. 热搜质量 (10分)
    hot = ['微博热搜', '百度热搜', '抖音热榜', 'Reddit']
    hot_present = sum(1 for s in hot if s in report_content)
    s4 = (hot_present / 4) * 10
    score += s4
    details['热搜质量'] = f"{hot_present}/4 平台 = {s4:.1f}/10"
    
    # 5. 国际新闻 (10分)
    intl_cats = ['冲突与安全', '政治与外交', '经济与商业', '环境']
    intl_present = sum(1 for c in intl_cats if c in report_content)
    s5 = (intl_present / 4) * 10
    score += s5
    details['国际新闻'] = f"{intl_present}/4 类别 = {s5:.1f}/10"
    
    # 6. 信息来源多样性 (15分) — 国际新闻≥5个不同媒体
    # ⚠️ 注意：链接格式是 [BBC](url) 不是 [来源](url)
    intl_start = report_content.find('国际新闻')
    if intl_start >= 0:
        intl_section = report_content[intl_start:]
        intl_links = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', intl_section)
        intl_domains = set()
        skip = {'s.weibo.com', 'www.baidu.com', 'www.douyin.com'}
        for label, url in intl_links:
            m = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if m and m.group(1) not in skip:
                intl_domains.add(m.group(1))
        unique_intl = len(intl_domains)
    else:
        unique_intl = 0
    s6 = 15 if unique_intl >= 5 else (10 if unique_intl >= 4 else (5 if unique_intl >= 3 else 0))
    score += s6
    details['信息来源多样性'] = f"{unique_intl} 个媒体 = {s6}/15"
    
    # 7. 链接可直达性 (15分) — 链接应指向文章页而非首页
    all_links = re.findall(r'\[.*?\]\((https?://[^)]+)\)', report_content)
    homepage = sum(1 for url in all_links if re.match(r'https?://[^/]+/?$', url))
    total = len(all_links)
    if total > 0:
        ratio = (total - homepage) / total
        s7 = int(ratio * 15)
    else:
        s7 = 0
    score += s7
    details['链接可直达性'] = f"{total - homepage}/{total} 直达 = {s7}/15"
    
    # 8. 数据源多样性 (5分)
    source_links = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', report_content)
    domains = set()
    for label, url in source_links:
        m = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if m and m.group(1) not in skip:
            domains.add(m.group(1))
    unique = len(domains)
    s8 = 5 if unique >= 7 else (3 if unique >= 5 else (1 if unique >= 3 else 0))
    score += s8
    details['数据源多样性'] = f"{unique} 个域名 = {s8}/5"
    
    # 评级
    if score >= 90: rating = "⭐ 优秀"
    elif score >= 80: rating = "✅ 良好"
    elif score >= 70: rating = "⚠️ 合格"
    else: rating = "❌ 不合格，需返工"
    
    return {'score': score, 'rating': rating, 'details': details}


if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/moyu_daily.md'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    result = evaluate_daily_report(content)
    for k, v in result['details'].items():
        print(f"{k}: {v}")
    print(f"\n总分: {result['score']:.1f}/100 — {result['rating']}")
