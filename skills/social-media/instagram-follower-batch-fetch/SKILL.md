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

## 帖子级内容获取（单帖 caption + 评论区，2026-08-04 实战验证）

做**内容分析报告**（分析博主合作帖的具体内容/用户反馈）时，主页级数据不够，需要拿到**单帖的 caption 和评论区**。

### 1. 单帖 og:description（匿名可调）

对帖子 URL `https://www.instagram.com/p/{shortcode}/` 或 `/reel/{shortcode}/` 直接 curl（短 UA + X-IG-App-ID，无需 cookie）：

```python
# og:description 格式："{likes} likes, {comments} comments - {username} on {date}: {caption}"
# 例如：222 likes, 21 comments - skavstheworld on August 1, 2026: "A quick tour of the stream room..."
```

**与主页 og:description 的区别**：主页返回 `X Followers, Y Following, Z Posts - See Instagram photos and videos from USER`；单帖返回点赞/评论数 + caption。解析函数要能区分两者。

```python
import re
def parse_post_og(desc):
    m = re.search(r'([\d,]+)\s+likes?,\s*([\d,]+)\s+comments?\s*-\s*(\w+)\s+on\s+([^:]+):\s*&quot;(.*?)&quot;', desc)
    return {'likes': m.group(1), 'comments': m.group(2), 'user': m.group(3), 'date': m.group(4), 'caption': m.group(5)} if m else None
```

**主页链接陷阱**：数据表里"内容链接"有时是博主主页而不是单帖（如 `https://www.instagram.com/audreycaprianni/`），此时 og:description 是粉丝数格式，无 caption——必须标注"需人工确认"，不要硬编。

### 2. 评论 API（需 cookie）

评论是"用户关注点/用户反馈"分析的唯一真实来源（不能编造用户关心什么）。

```python
# shortcode → media_id：Instagram 短码是自定义 base64 字母表
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
def shortcode_to_id(code):
    n = 0
    for c in code:
        n = n * 64 + ALPHABET.index(c)
    return n

# 拉评论（cookie 从 ~/.hermes/cookies/platform_cookies.json 取 instagram 字段）
# GET https://www.instagram.com/api/v1/media/{media_id}/comments/?can_support_threading=true
# 返回 data.comments[].text，取前 ~12 条
```

要点：
- **必须带登录 cookie**（匿名会 403/空），UA 用短 UA + X-IG-App-ID
- 1s 间隔防限流；评论数多时每帖取前 8-12 条即可满足分析
- 评论提取后用于写"用户关注点"列（如"评论区出现 Win11 兼容性吐槽→投放前需确认固件"）

### 3. 单帖指标获取（点赞/评论/互动率，2026-08-04 实战验证）

**场景**：数据表需补"曝光/点赞/评论/互动率"列时。og:description 的 likes/comments 是**旧缓存**，需用 instaloader 拿最新实时值。

**instaloader（GitHub 工具，推荐）**：
```bash
pip3 install --user instaloader   # Python 3.9 环境
```
```python
import instaloader, re, json
L = instaloader.Instaloader(quiet=True,
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    request_timeout=20)
# 注入登录 cookie（从 ~/.hermes/cookies/platform_cookies.json instagram 字段）
ig_cookie = json.load(open('/Users/zhoulong/.hermes/cookies/platform_cookies.json'))['instagram']
for name in ['sessionid','mid','csrftoken','ds_user_id']:
    m = re.search(name + r'=([^;]+)', ig_cookie)
    if m: L.context._session.cookies.set(name, m.group(1), domain='.instagram.com')
L.context._session.headers.update({'X-IG-App-ID': '936619743392459'})

post = instaloader.Post.from_shortcode(L.context, 'DPB1--3CMlj')
likes, comments = post.likes, post.comments   # 实时最新值，比 og 缓存更新
views = post.video_view_count                # 大部分 Reels 返回 None，见下方限制
```
- 每帖间隔 0.8-1s 防限流
- 点赞/评论对大多数帖子都能拿到（哪怕视频 views 缺失）

**⚠️ Reels 曝光（play_count）：instaloader 拿不到，但移动端 Feed API 能拿到（2026-08-04 重大突破）**：
- instaloader 对 Reels（`product_type=clips`）返回 `video_view_count=None`——这是 **instaloader 的限制，不是平台拿不到**
- **移动端 API `https://www.instagram.com/api/v1/feed/user/{user_id}/?count=33`（带 Cookie）返回 `play_count`（Reels 播放量=曝光）**，实测 8 帖中 6 帖拿到（50,497 / 10,788 / 203,427 等），支持 `max_id` 分页且**不走 web_profile_info 的限流池**
- user_id 获取：instaloader `Profile.from_username(...).userid`；限流时用**页面 HTML 正则** `"user_id":(\d+)` 或 `"pk":(\d+)`（`curl https://www.instagram.com/{user}/` 匿名+短UA+X-IG-App-ID）
- 分页：响应 `more_available` + `next_max_id` 游标；实际每页返回 12 条（count=33 被忽略）；时间乱序需全量翻页
- **博主主动隐藏统计的帖子拿不到**：帖子 HTML 含 `view_counts":"false"`（如 thedesignely DTc_ASSjRTJ、feryfer_gg DSG91N3jFs-），instaloader/移动端/页面三路确认全为 None——此时诚实告知"博主隐藏"，互动率回退 followers 口径
- 完整脚本见 `references/ig-mobile-feed-play-count.md`

**⚠️ web_profile_info schema 错误是间歇性的**：
`Asset asset://laser.provider/ig_business_category_subvertical has been deleted` 报错**重试 2-3 次（间隔 2s）可恢复**，不是永久失败也不是限流。之前 skill 写"跳过即可"，实战证明重试更优。

**互动率口径统一（重要）**：
- 表格"账户平均互动率"列是 `(点赞+评论)/粉丝数` 口径
- 帖子级互动率**必须同口径**：`(likes+comments)/followers`，不要在有 views 时混用 views 口径（会导致 jatara 15.69% vs 0.4% 这种不可比数据）
- followers 获取优先级：instaloader Profile.from_username → og:description → web_profile_info

**⚠️ 用户名脏数据核对**：
- 原表 `tudywithemmane_` 实际是 `studywithemmane_`（少个 s），Profile.from_username 报 "does not exist" 时不要放弃——**从单帖 og:description 的 "username on date" 提取真实用户名**，再查 followers
- 大账号互动率低是常态（794K 粉 0.05%），不是数据错误，要在 insights 里解释

### 4. 数据表脏数据核对清单（分析前必查）

| 问题 | 处理 |
|:-----|:-----|
| 产品列与 caption 不符（如标 Facecam 实为 Prompter） | 以实际 caption 为准并修正 |
| 内容是官方号转发 KOC（caption 作者 ≠ 博主 ID） | 标注"官方转发"，互动数据参考价值低 |
| 内容链接是主页而非单帖 | 无法分析，标注"需人工确认" |
| 同一链接重复出现多行 | 去重或合并 |
| 原始表分析列是占位符 "1" | 用真实分析替换（模板补全场景常见） |

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
