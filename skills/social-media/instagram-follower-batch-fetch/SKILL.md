---
name: instagram-follower-batch-fetch
description: 批量获取 Instagram 账号粉丝数和视频播放量的方法。主力：匿名 web_profile_info API（curl + X-IG-App-ID，一次拿 followers + avg views）；后备：解析 og:description meta tag。含限流处理、OBSBOT 内容分类、腾讯文档智能表写入（查重+去重 CSV）。
---

# Instagram 批量粉丝数获取

批量从 Instagram 公开主页获取粉丝数（followers）、关注数（following）、帖子数（posts），用于筛选 KOL。

## 数据来源

每个 Instagram 公开个人主页的 `<meta property="og:description">` 包含结构化数据：

```html
<meta property="og:description" content="847 Followers, 595 Following, 299 Posts - See Instagram photos and videos from USER" />
```

中文版格式：`"847 粉丝, 595 关注, 299 帖子 - ..."`

## 解析方法

### 粉丝数解析（含 K/M/B 后缀）

```python
import re

def parse_ig_count(s):
    """Parse '43M', '142K', '847', '34K' style numbers."""
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*([KMB]?)', s)
    if not m:
        return 0
    num = float(m.group(1).replace(',', ''))
    suf = m.group(2)
    if suf == 'K': num *= 1000
    elif suf == 'M': num *= 1000000
    elif suf == 'B': num *= 1000000000
    return int(num)

def fetch_account_data(username, cookie_str):
    """Fetch follower/following/posts count for one Instagram account."""
    import subprocess, os, re
    
    tmp_file = f"/tmp/ig_{username}.html"
    subprocess.run([
        "curl", "-s", "--max-time", "10",
        "-H", f"Cookie: {cookie_str}",
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "-o", tmp_file,
        f"https://www.instagram.com/{username}/"
    ], timeout=15)
    
    if not os.path.exists(tmp_file):
        return None
    
    with open(tmp_file, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()
    os.remove(tmp_file)
    
    og_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
    if not og_match:
        return None
    
    desc = og_match.group(1)
    
    # Handle both English and Chinese
    followers = parse_ig_count(desc.split('Followers')[0]) if 'Followers' in desc else \
                parse_ig_count(desc.split('粉丝')[0]) if '粉丝' in desc else 0
    following = parse_ig_count(desc.split('Following')[0].split('Followers')[-1]) if 'Following' in desc else \
                parse_ig_count(desc.split('关注')[0].split('粉丝')[-1]) if '关注' in desc else 0
    posts_match = re.search(r'([\d,]+(?:\.\d+)?)\s*Posts', desc) or \
                  re.search(r'([\d,]+(?:\.\d+)?)\s*帖子', desc)
    posts = int(posts_match.group(1).replace(',', '')) if posts_match else 0
    
    return {
        'username': username,
        'profile_url': f'https://www.instagram.com/{username}/',
        'followers': followers,
        'following': following,
        'posts': posts
    }
```

## ⚠️ 已知陷阱

### 0. ⚠️ 优先用 web_profile_info API（一次拿粉丝+视频播放量，推荐）
`https://www.instagram.com/api/v1/users/web_profile_info/?username=X` **匿名可调**，返回 followers + 最近 12 条帖子的 video_view_count（含视频播放量）。比解析 og:description 强得多——Views 数据一次拿到。

**关键参数（2026-07-30 实战验证）：**
- **必须用 curl**，不能用 urllib（TLS 指纹不同会被 429 限流）
- **User-Agent 不能用 `Chrome/150.0.0.0`**（不存在的版本号导致 Instagram 返回缩短版页面、无 og:description/无 media edges）。用短 UA：`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36`
- 必须带 `X-IG-App-ID: 936619743392459` 头
- **不要带 Cookie**（带登录 cookie 时 API 不返回 media edges，即拿不到 views）
- 1s 间隔可避免限流，200+ 账号约 5-6 分钟跑完（远快于 og:description 方式）
- 限流表现为 body 无 `data.user`；部分账号返回 `Asset asset://laser.provider/...` 错误（业务数据问题，跳过即可，不是限流）

```python
import subprocess, json, time
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
def fetch_one(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    r = subprocess.run(["curl","-s","--max-time","10","-H",f"User-Agent: {UA}",
                        "-H","X-IG-App-ID: 936619743392459", url],
                       capture_output=True, text=True, timeout=15)
    data = json.loads(r.stdout)
    user = data.get('data', {}).get('user', {})
    if not user: return None  # 限流或资产错误
    edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
    views = [e['node']['video_view_count'] for e in edges
             if e.get('node', {}).get('__typename') == 'GraphVideo'
             and e['node'].get('video_view_count')]
    return {'username': username,
            'followers': user.get('edge_followed_by', {}).get('count', 0),
            'posts': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
            'avg_video_views': sum(views)//len(views) if views else 0,
            'max_video_views': max(views) if views else 0}
```

### 1. Rate Limiting
Instagram 对短时间内大量请求返回空白/非标准页面。

**解决方法：**
- 每请求间隔 ≥1 秒
- 或使用 Tavily MCP / Jina Reader 等第三方搜索工具替代
- web_profile_info API 匿名 + curl + 1s 间隔实测不触发限流

### 2. IncompleteRead / 响应截断（urllib 和 -o 组合）
Python urllib 可能因响应过大（~600K-650K）触发 `IncompleteRead`。**更隐蔽的坑：`curl -s -o <tmpfile>` 与 `capture_output=True` 组合会导致文件截断**（619KB vs 652KB，og:description 丢失）。

### 3. Cookie 过期
`~/.hermes/cookies/platform_cookies.json` 中的 Instagram cookie 会过期。更新方式：
- 用户在 Chrome 登录 Instagram 后，用 EditThisCookie 扩展导出
- 或运行 bb-browser 的 Instagram 适配器

### 4. 请求返回空
某些账号可能返回空 HTML（length=0），原因：
- 账号不存在/已改名
- 网络问题导致 curl 中断
- Instagram 限流该 IP

### 5. 中文 vs 英文
og:description 的 label 取决于用户语言设置：
- 英文：`X Followers, Y Following, Z Posts`
- 中文：`X 粉丝, Y 关注, Z 帖子`

## 完整批量处理脚本

参考文件 `scripts/batch_fetch_ig.py`，包含：
- 从 CSV 读取 usernames
- 逐条查询 og:description
- 断点续传（每 100 条保存）
- 过滤 >50K 粉丝的账号

## 推荐管道（2026-07-30 实战验证版）

```
用户导出关注列表 CSV（DevTools 方法见 instagram-following-export skill）
    ↓
web_profile_info API 批量查询（匿名 curl + X-IG-App-ID，~6 分钟/200+ 账号）
    ↓   一次拿到 followers + 最近 12 条视频的 avg_video_views
双重筛选：followers > 50K AND avg_video_views > 5K
    ↓
按 OBSBOT 内容分类体系分类（见文末，一级类目=内容占比最多）
    ↓
写入腾讯文档智能表（含查重：list_records field_titles 拉现有 username 比对）
    ↓
输出去重后 CSV（ID/主页链接/粉丝数量/Views/帖子数/一级类目/二级类目/分类依据）
```

## 腾讯文档智能表写入（mcporter 实战要点）

记录格式**按字段标题**（非 field_id），`field_values` 数组：
```json
{"field_values": [
  {"field": "ID (用户名)", "text_value": {"items": [{"text": "taylorswift", "type": "text"}]}},
  {"field": "主页链接", "url_value": {"items": [{"text": "https://...", "type": "url", "link": "https://..."}]}},
  {"field": "粉丝数量", "number_value": 273562840},
  {"field": "账号类别", "option_value": {"items": [{"text": "Content Creator"}]}},
  {"field": "添加日期", "string_value": "1785340800000"}   // 毫秒时间戳字符串
]}
```

**关键坑：**
- **url 字段**必须用 `url_value`（`text_value` 报 `Smartsheet invalid url value`）
- **dateTime** 用 `string_value`（毫秒时间戳字符串）
- **singleSelect** 用 `option_value`；新选项需先 `update_fields` 加到字段 options
- **mcporter 调用必须用参数列表（argv list）**，不要 `shell=True` + `$(cat file)`（会解析失败）；JSON 直接作为 `--args` 的单个 argv 元素即可
- **每批 ≤5 条**（10 条时返回 JSON 过大偶发解析失败）；失败批次**带重试**（网络波动常见，`tencent-docs appears offline` 重试即可）
- **查重**：`list_records` 加 `field_titles` 参数减少输出量（全字段输出可能截断），分页拉取后与待写入 username 比对
- `list_records` 输出大时 JSON 解析偶发失败 → 加 retry-with-backoff

## OBSBOT 内容分类体系

筛选出合格博主后按此体系分类。**一级类目 = 渠道占比最多的内容；二级类目 = 渠道较为分散的内容。核心排除规则：纯手机/电脑/键盘/鼠标测评不计入有效类型。**

| 一级类目 | 二级类目 | 要点 |
|:--------|:---------|:-----|
| Tech | Hometech / Gadget Review / VR / 3C / Drone / PC Build | Hometech=智能家居(灯/锁/音箱/监控/扫地机/割草机)；Gadget=小配件(支架/收纳/充电器)；3C=手机/耳机/平板/笔记本/手表；Drone=DJI/Autel/Skydio；PC Build=装机/配件/性能测试 |
| Livestream | Tips / Device / Tutorial / Scene | 指内容结合直播主题的渠道，非"在直播平台开播"。平台 Twitch/Kick/YT/IG/TT；APP VMIX/OBS/restream/Streamyard/ecamm；设备 Talent/Yolobox/Atem mini/Stream deck |
| Camera | Photography / Videography / Filmmaker / Camera Settings | DSLR 品牌 Sony/Nikon/Canon/Fujifilm/Olympus/Blackmagic；摄影/视频拍摄剪辑/电影化叙事/相机参数 |
| Gamer | Game Streamer / Game Gear / Game Recording(FPS) / Game Recording / Gaming PC / Game Only | Streamer=游戏主播(如Tenz)；Gear=键鼠/电竞椅/手柄/耳机/氛围灯；FPS=Valorant/COD/Fortnite/CS2/Free Fire 主画面+主播小框；Game Only=纯游戏片段 |
| Content Creator | Productive Tools / Earning / Draw / Art / Music / Dance / Instrument / DIY / Home Mom / Study Vlog / Online Education / Animal / Fashion / Beauty / Lifestyle / Family / Travel | Productive Tools=Notion/Todoist/Trello/Obsidian 教程(露脸/手部)；Earning=赚钱方法；Draw/Art=绘画/手工艺；DIY=手工家居改造；Home Mom=亲子vlog；Study Vlog=学习记录；Online Education=线上教学 |
| Setup | Desk Setup / Game Setup | Desk=科技感桌搭；Game=游戏风桌搭（OBSBOT 重点品类） |
| Apple | Apple Accessories / Apple News | 苹果配件(Mac mini/MacBook/iPhone)；苹果资讯(新品/功能迭代) |
| Live Production (*Solution*) | Church / Wedding / DJ / Music / Interview / Podcast / Healthcare / Concert / Education / Cooking / Sports / Equestrian / Construction | 配合官网 Solution 页面特需场景，线下组织/网站/素人，内容单一集中于单一场景 |
| Entertainment | Reaction / Comedy / Spoof / ASMR / Cosplay / Magic / Anime / Commentary | Reaction=实时观看反应评论(露脸) |
| Sports | Billiards / Baseball / Basketball / Soccer / Table Soccer / Tennis / Football / Skateboard / Roller-Skating / Yoga / Fitness / Darts / Golf | 球类/健身教学、集锦、战术分析 |
| Social Profession | Teacher / Player / Coach / Worker / Groups / Club / Organization / Community / Esports Team | 老师/选手/教练/电竞团队（BA/EWC 项目） |

**分类实操要点：**
- 品牌官方号（Sephora/NYX/Logitech/Samsung）归入对应一级类目但营销价值低，仅作渠道参考
- 纯键鼠/手机/电脑测评品牌号 → Tech 3C 但按排除规则标记**无效类型**
- 明星艺人 → Content Creator: Music；美妆博主（IG 关注列表大头）→ Content Creator: Beauty
- 桌搭类（cozy gaming）→ Setup: Game Setup；播客 → Live Production: Podcast
- 分类依据要记录（bio/品牌认知），不能只给类目名
- CPM 定价品类（Tech/Apple/Gamer/Desk Setup/Livestream/Game Recording/Content Creator/Camera）与此表一致

## 腾讯文档数据库结构

推荐字段（smartsheet 类型）：

| 字段 | 类型 | 说明 |
|------|------|------|
| ID (用户名) | text | Instagram 用户名 |
| 主页链接 | url | 主页 URL |
| 粉丝数量 | number | followers 计数值 |
| Views | number | 平均播放量（需补充数据） |
| 帖子数 | number | posts 计数 |
| 账号类别 | singleSelect | Lifestyle/Beauty/Fashion/Tech 等 |
| 来源博主 | text | 从哪个 KOL 的关注列表导出的 |
| 添加日期 | dateTime | 入库日期 |
