# TwitchTracker 数据爬取

## 概述

TwitchTracker 提供主播的详细直播数据（排名、观看时长、平均观众、峰值等）。可通过 curl + 正则表达式提取，无需 JavaScript 渲染。

## URL 格式

```
https://twitchtracker.com/{username}
```

## HTML 结构（关键数据）

### 排名

```html
<div class="rank-badge r2">
    <span>RANK</span>
    <span class="crown"></span>
    <span class="to-number">1546</span>
</div>
```

### 30 天性能数据

```html
<div id="performance-panel" class="g-x-l g-x-l-4">
    <div class="g-x-s-block">
        <div class="g-x-s-value to-number">197</div>
        <div class="g-x-s-label color-live">Hours streamed</div>
    </div>
    <div class="g-x-s-block">
        <div class="g-x-s-value to-number">900</div>
        <div class="g-x-s-label color-viewers">Average viewers</div>
    </div>
    <div class="g-x-s-block">
        <div class="g-x-s-value to-number">4052</div>
        <div class="g-x-s-label color-viewersMax">Peak viewers</div>
    </div>
    <div class="g-x-s-block">
        <div class="g-x-s-value to-number">281</div>
        <div class="g-x-s-label color-followers">Followers gained</div>
    </div>
</div>
```

### 简介

```html
<div style="word-wrap:break-word;font-size:12px;">简介内容...</div>
```

## Python 爬虫模板

```python
import re
import json
import time

def get_twitchtracker_data(username):
    """用 curl 爬取 TwitchTracker 数据"""
    result = terminal(f"curl -sL --max-time 20 -x socks5://127.0.0.1:1082 'https://twitchtracker.com/{username}' 2>/dev/null", timeout=25)
    html = result['output']
    
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
        bio = bio.replace('&#039;', "'").replace('&amp;', '&')
        data['bio'] = bio[:500]
    
    # 语言
    lang_m = re.search(r'<span[^>]*>(French|English|Spanish|German|Portuguese|Russian)</span>', html)
    if lang_m:
        data['language'] = lang_m.group(1)
    
    # 社交链接
    for platform, pattern in [
        ('youtube', r'href="(https?://(?:www\.)?youtube\.com/[^"]*)"'),
        ('instagram', r'href="(https?://(?:www\.)?instagram\.com/[^"]*)"'),
        ('twitter', r'href="(https?://(?:www\.)?(?:twitter\.com|x\.com)/[^"]*)"'),
        ('tiktok', r'href="(https?://(?:www\.)?tiktok\.com/[^"]*)"'),
    ]:
        matches = re.findall(pattern, html)
        if matches:
            data[f'{platform}_link'] = matches[0]
    
    # 邮箱（从简介提取）
    if 'bio' in data:
        email_m = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', data['bio'])
        if email_m:
            data['email'] = email_m.group(0)
    
    return data
```

## 注意事项

1. **频率限制**：连续请求过快会返回空页面。建议间隔 0.5-1.5 秒，失败后等 2 秒重试
2. **7 天数据**：需 JavaScript 交互（点击 "7 DAYS" 按钮），curl 无法获取
3. **邮箱保护**：TwitchTracker 使用 Cloudflare email protection，简介中的邮箱可能被编码
4. **社交链接**：部分社交链接通过 JavaScript 动态加载，curl 可能无法提取
5. **代理**：在中国大陆需要 SOCKS5 代理才能访问
