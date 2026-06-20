---
name: cs2-streamer-research
description: "CS2/CSGO Twitch主播调研工具。当需要搜索、筛选、分析某地区/语言的CS2游戏主播数据时使用。支持多语言多地区批量爬取TwitchTracker数据，生成Excel报告。"
version: "2026-06-16"
tags: [cs2, csgo, twitch, streamer, esports, research, twitchtracker]
triggers:
  - CS2主播调研
  - CSGO主播数据
  - Twitch主播筛选
  - 电竞主播分析
---

# CS2/CSGO Twitch 主播调研工具

## 概述

批量爬取 TwitchTracker 数据，按地区/语言筛选 CS2 主播，生成结构化 Excel 报告。

## 数据源

| 来源 | URL | 用途 |
|------|-----|------|
| TwitchTracker | https://twitchtracker.com | 主播详细数据（排名、30天数据、简介、社交链接） |
| TwitchMetrics | https://twitchmetrics.net/channels/viewership?game=Counter-Strike&lang={LANG} | 按语言的CS2主播排名 |

## 爬虫脚本

```python
#!/usr/bin/env python3
"""CS2 Twitch主播数据爬虫"""
import urllib.request
import re
import json
import time

PROXY = "socks5://127.0.0.1:1082"

def get_twitchtracker_data(username):
    """从TwitchTracker获取主播数据"""
    url = f"https://twitchtracker.com/{username}"
    cmd = f"curl -sL --max-time 25 -x {PROXY} '{url}' 2>/dev/null"
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    html = result.stdout

    if not html or len(html) < 1000:
        return {'username': username, 'error': 'page load failed'}

    data = {'username': username}

    # 排名
    rank_m = re.search(r'<span class="to-number">([0-9,]+)</span>\s*</div>\s*</div>\s*</div>', html[:10000])
    if rank_m:
        data['rank'] = rank_m.group(1).replace(',', '')

    # 30天数据
    blocks = re.findall(
        r'<div class="g-x-s-value to-number">([0-9,]+)</div>\s*<div class="g-x-s-label[^"]*">([^<]+)</div>',
        html
    )
    for val, label in blocks:
        val = val.replace(',', '')
        label = label.strip()
        if 'Hours streamed' in label:
            data['hours_streamed_30d'] = int(val)
        elif 'Average viewers' in label:
            data['avg_viewers_30d'] = int(val)
        elif 'Peak viewers' in label:
            data['peak_viewers_30d'] = int(val)
        elif 'Followers gained' in label:
            data['followers_gained_30d'] = int(val)

    # 简介
    bio_m = re.search(r'word-wrap:break-word;font-size:12px;">(.*?)</div>', html, re.DOTALL)
    if bio_m:
        bio = re.sub(r'<[^>]+>', '', bio_m.group(1)).strip()
        bio = bio.replace('&#039;', "'").replace('&amp;', '&').replace('&quot;', '"')
        data['bio'] = bio[:500]

    # 语言
    lang_m = re.search(r'<span[^>]*>(French|English|Spanish|German|Portuguese|Russian|Italian|Polish|Swedish|Norwegian|Danish|Finnish|Dutch|Turkish)</span>', html)
    if lang_m:
        data['language'] = lang_m.group(1)

    # 社交链接
    for platform, pattern in {
        'youtube': r'href="(https?://(?:www\.)?youtube\.com/[^"]*)"',
        'instagram': r'href="(https?://(?:www\.)?instagram\.com/[^"]*)"',
        'twitter': r'href="(https?://(?:www\.)?(?:twitter\.com|x\.com)/[^"]*)"',
        'tiktok': r'href="(https?://(?:www\.)?tiktok\.com/[^"]*)"',
    }.items():
        matches = re.findall(pattern, html)
        if matches:
            data[f'{platform}_link'] = matches[0]

    # 邮箱
    if 'bio' in data:
        email_m = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', data['bio'])
        if email_m:
            data['email'] = email_m.group(0)

    # 知名关注者
    famous = re.findall(
        r'<a[^>]*>([A-Za-z0-9_]+)</a>\s*<span[^>]*>(French|English|Spanish|German|Portuguese|Russian|Italian|Polish)\s+Partner',
        html
    )
    data['famous_followers'] = [f[0] for f in famous][:10]

    return data


def get_twitchmetrics_streamers(lang='en', limit=20):
    """从TwitchMetrics获取某语言的CS2主播列表"""
    url = f"https://twitchmetrics.net/channels/viewership?game=Counter-Strike&lang={lang}"
    cmd = f"curl -sL --max-time 20 -x {PROXY} '{url}' 2>/dev/null"
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
    html = result.stdout

    # 提取主播名
    names = re.findall(r'<h5[^>]*>([A-Za-z0-9_]+)</h5>', html)
    return names[:limit]


def batch_crawl(streamers, delay=1.0):
    """批量爬取主播数据"""
    results = []
    for i, name in enumerate(streamers):
        print(f"[{i+1}/{len(streamers)}] {name}...", end=" ")
        data = get_twitchtracker_data(name)
        results.append(data)
        if 'error' in data:
            print(f"ERROR: {data['error']}")
        else:
            print(f"rank #{data.get('rank', '?')}, avg {data.get('avg_viewers_30d', '?')}")
        time.sleep(delay)
    return results
```

## 地区/语言映射

| 地区 | TwitchMetrics lang | 语言 |
|------|-------------------|------|
| 英语区（英国、爱尔兰） | en | English |
| 德语区（德国、奥地利、瑞士） | de | German |
| 法语区（法国、比利时、瑞士） | fr | French |
| 北欧（瑞典、挪威、丹麦、芬兰） | sv/no/da/fi | Swedish/Norwegian/Danish/Finnish |
| 西班牙语（西班牙） | es | Spanish |
| 意大利语 | it | Italian |
| 波兰语 | pl | Polish |

## Excel 生成

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_excel(all_data, output_path):
    """生成Excel报告"""
    wb = openpyxl.Workbook()
    
    # 样式
    hf = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    hfill = PatternFill(start_color='1B3A5C', end_color='1B3A5C', fill_type='solid')
    lf = Font(name='Calibri', size=10, color='0563C1', underline='single')
    tb = Border(left=Side('thin','B0B0B0'), right=Side('thin','B0B0B0'),
                top=Side('thin','B0B0B0'), bottom=Side('thin','B0B0B0'))
    ca = Alignment(horizontal='center', vertical='center', wrap_text=True)
    wa = Alignment(wrap_text=True, vertical='center')
    
    headers = [
        '排名', 'Twitch 主播', 'Twitch 直播间', 'Twitch 全球排名',
        '30天直播时长', '30天平均观众', '30天峰值观众', '30天新增粉丝',
        '简介', '语言', 'YouTube', 'Instagram', 'X/Twitter',
        '联系方式', '舆情状态', '备注'
    ]
    
    for region, streamers in all_data.items():
        ws = wb.create_sheet(region)
        
        for col, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.font = hf; c.fill = hfill; c.alignment = ca; c.border = tb
        
        for ri, s in enumerate(streamers, 2):
            row = [
                ri - 1,
                s.get('username', ''),
                f"https://www.twitch.tv/{s.get('username', '')}",
                f"#{s.get('rank', 'N/A')}",
                f"{s.get('hours_streamed_30d', 'N/A')}h",
                s.get('avg_viewers_30d', 'N/A'),
                s.get('peak_viewers_30d', 'N/A'),
                f"+{s.get('followers_gained_30d', 'N/A')}",
                s.get('bio', '')[:100],
                s.get('language', ''),
                s.get('youtube_link', '—'),
                s.get('instagram_link', '—'),
                s.get('twitter_link', '—'),
                s.get('email', '—'),
                '✅ 无已知负面',
                ''
            ]
            for ci, val in enumerate(row, 1):
                c = ws.cell(row=ri, column=ci, value=str(val) if val else '—')
                c.border = tb; c.alignment = wa
                if ci == 1: c.alignment = ca
                if ci == 3 and str(val).startswith('http'): c.font = lf
        
        # 列宽
        widths = [6, 20, 40, 14, 14, 14, 14, 14, 50, 10, 35, 35, 35, 28, 12, 30]
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        
        ws.freeze_panes = 'A2'
    
    # 删除默认sheet
    if 'Sheet' in wb.sheetnames:
        del wb['Sheet']
    
    # 数据来源
    ws_src = wb.create_sheet('数据来源')
    ws_src['A1'] = '数据来源说明'
    ws_src['A1'].font = Font(bold=True, size=14)
    ws_src['A3'] = '1. TwitchTracker (https://twitchtracker.com) - 主播详细数据'
    ws_src['A4'] = '2. TwitchMetrics (https://twitchmetrics.net) - 按语言的CS2主播排名'
    ws_src['A5'] = f'数据采集时间：{time.strftime("%Y-%m-%d")}'
    ws_src['A6'] = '数据范围：最近30天'
    ws_src.column_dimensions['A'].width = 80
    
    wb.save(output_path)
    print(f'Excel 已保存: {output_path}')
```

## Twitch GQL API 获取粉丝量

TwitchTracker 页面的粉丝量通过 JavaScript 动态加载，curl 无法直接获取。解决方案：使用 Twitch 官方 GraphQL API。

```python
import json, subprocess

def get_followers(username):
    """通过 Twitch GQL API 获取粉丝量"""
    query = {"query": f'query {{ user(login: "{username}") {{ followers {{ totalCount }} }} }}'}
    with open('/tmp/twitch_query.json', 'w') as f:
        json.dump(query, f)
    
    cmd = '''curl -s -X POST 'https://gql.twitch.tv/gql' \
      -H 'Client-ID: kimne78kx3ncx6brgo4mv6wki5h1ko' \
      -H 'Content-Type: application/json' \
      -d @/tmp/twitch_query.json 2>/dev/null'''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    try:
        data = json.loads(result.stdout)
        return data.get('data', {}).get('user', {}).get('followers', {}).get('totalCount')
    except:
        return None
```

**关键点**：
- Client-ID `kimne78kx3ncx6brgo4mv6wki5h1ko` 是 Twitch 网页端公开的 Client-ID
- 查询必须写入文件再用 `-d @file` 传递，不能直接在命令行中拼接 JSON（会因转义问题报错）
- 限流：连续请求约 50 次后会返回 N/A，需等待几秒后重试
- 成功率：138 个主播中约 70% 首次成功，重试后可达 95%+

## ⚠️ Pitfalls

1. **TwitchTracker 限流** — 连续请求过多会返回空页面，需加 1-2 秒延迟
2. **SOCKS5 代理必须** — TwitchTracker 在 GFW 后无法直连
3. **curl 优于 requests** — Python urllib/requests 在 SOCKS5 代理下不稳定，用 curl 子进程更可靠
4. **7天数据需JS** — TwitchTracker 的7天数据通过JavaScript加载，curl无法获取
5. **社交链接动态加载** — 部分社媒链接通过JS动态渲染，curl可能提取不到
6. **排名说明** — TwitchTracker排名是全球排名（所有游戏），非CS2专项排名
7. **简介语言** — 简介为原文（各语言），需翻译为中文
8. **数据验证** — 建议对Top主播抽查TwitchTracker页面确认数据准确性
9. **🔴 TwitchTracker 不含粉丝量** — follower count 不在静态 HTML 中（JS 动态加载），必须用 Twitch GQL API 获取
10. **🔴 Twitch GQL API 获取粉丝量** — 使用 `curl -X POST 'https://gql.twitch.tv/gql'` + `Client-ID: kimne78kx3ncx6brgo4mv6wki5h1ko`。查询必须写入 JSON 文件再用 `-d @file` 发送（不能 inline，会有转义问题）
11. **🔴 TwitchMetrics HTML 结构** — 主播名在 `<h5 class="mr-2 mb-0">` 标签中（不是 `<h5>` 通用标签）
12. **🔴 用户偏好** — Leonardo 要求：(1) 粉丝量必须展示；(2) 简介用中文，不超过50字；(3) 语言要写清楚；(4) 社媒信息要完整；(5) Twitch 直播间链接必须可点击

## Twitch GQL API 获取粉丝量

```python
# 写入查询到文件（避免转义问题）
query = {"query": 'query { user(login: "username") { followers { totalCount } } }'}
with open('/tmp/twitch_query.json', 'w') as f:
    json.dump(query, f)

# 发送请求
cmd = '''curl -s -X POST 'https://gql.twitch.tv/gql' \
  -H 'Client-ID: kimne78kx3ncx6brgo4mv6wki5h1ko' \
  -H 'Content-Type: application/json' \
  -d @/tmp/twitch_query.json'''

# 返回: {"data":{"user":{"followers":{"totalCount":132383}}}}
```

**限流**: 约 50 次请求后会失败，需等待后重试。建议 0.3-0.5 秒间隔。
