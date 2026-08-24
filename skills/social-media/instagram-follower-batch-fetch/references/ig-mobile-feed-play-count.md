# IG Reels 曝光（play_count）获取 — 移动端 Feed API

2026-08-04 实战验证。**核心结论：instaloader 拿不到 Reels 播放量，但移动端 Feed API 能拿到。**

## 为什么 instaloader 不行

- Reels（`product_type=clips`）→ `post.video_view_count = None`（instaloader 只读 GraphVideo 的 video_view_count，Reels 不返回）
- `web_profile_info` 只返回最近 12 条帖子，目标帖子常在更早位置
- `web_profile_info` 翻页会被限流（`Please wait a few minutes before you try again`）
- 单帖页面 HTML 对大部分帖子没有 play_count（但隐藏统计的帖子有 `view_counts":"false"` 标记）

## 移动端 Feed API（能拿到 play_count）

```
GET https://www.instagram.com/api/v1/feed/user/{user_id}/?count=33[&max_id={cursor}]
Headers:
  User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
  X-IG-App-ID: 936619743392459
  Cookie: <platform_cookies.json instagram 字段>
```

响应 `items[]` 每项包含：
- `code` = shortcode
- `play_count` = Reels 播放量（**这就是曝光**）
- `like_count` / `comment_count`
- `media_type`（2=视频，1=图片）
- `taken_at` = Unix 时间戳

分页：`more_available: true` → 用 `next_max_id` 作为下一个 `max_id`。**每页实际返回 12 条**（count=33 被忽略），时间乱序（不是严格倒序），不能按日期猜页码，必须全量翻页。

## user_id 获取（两种方式）

```python
# 方式 1：instaloader（快速，但连续调用会 Read timeout）
import instaloader, re, json
L = instaloader.Instaloader(quiet=True, user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", request_timeout=15)
# 注入 cookie（见主 SKILL.md）
uid = instaloader.Profile.from_username(L.context, 'thehippiehacker').userid

# 方式 2：页面 HTML 正则（限流时备用，匿名可调）
# curl https://www.instagram.com/{username}/  + 短UA + X-IG-App-ID
m = re.search(r'"user_id":(\d+)', html) or re.search(r'"id":"(\d+)"', html) \
    or re.search(r'profilePage_(\d+)', html) or re.search(r'"pk":(\d+)', html)
```

## 完整工作脚本

```python
import json, subprocess, time, re, os

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
COOKIE = json.load(open('/Users/zhoulong/.hermes/cookies/platform_cookies.json'))['instagram']

def get_user_id_html(username):
    r = subprocess.run(["curl", "-s", "--max-time", "15", "-H", f"User-Agent: {UA}",
                        "-H", "X-IG-App-ID: 936619743392459",
                        f"https://www.instagram.com/{username}/"],
                       capture_output=True, text=True, timeout=20)
    m = re.search(r'"user_id":(\d+)', r.stdout) or re.search(r'"id":"(\d+)"', r.stdout) \
        or re.search(r'profilePage_(\d+)', r.stdout) or re.search(r'"pk":(\d+)', r.stdout)
    return m.group(1) if m else None

def feed_page(user_id, max_id=None):
    url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/?count=33"
    if max_id: url += f"&max_id={max_id}"
    r = subprocess.run(["curl", "-s", "--max-time", "12", "-H", f"User-Agent: {UA}",
                        "-H", "X-IG-App-ID: 936619743392459", "-H", f"Cookie: {COOKIE}", url],
                       capture_output=True, text=True, timeout=18)
    try: return json.loads(r.stdout)
    except: return None

def find_post(username, target_sc, max_pages=150):
    uid = get_user_id_html(username)
    if not uid: return {'error': 'cannot get user id'}
    cursor = None
    for page in range(1, max_pages + 1):
        d = feed_page(uid, cursor)
        if not d or 'items' not in d:
            return {'error': f'page {page} failed'}
        for it in d['items']:
            if it.get('code') == target_sc:
                return {'views': it.get('play_count') or it.get('view_count'),
                        'likes': it.get('like_count'), 'comments': it.get('comment_count'),
                        'page': page}
        if not d.get('more_available'):
            return {'error': f'not found after {page} pages (end)'}
        cursor = d.get('next_max_id')
        time.sleep(0.5)   # 防限流
    return {'error': f'not found within {max_pages} pages'}
```

## 关键坑

1. **后台跑 + process wait 会误杀**：分页循环在 60s wait 超时后进程被终止且可能不保存进度。**改前台跑 + timeout=500**，或每次找到即写盘（断点续跑 JSON）。
2. **断点续跑**：进度存 `/tmp/mobile_progress.json`，重跑时跳过已有 views/error 的条目（注意：旧的 error 记录也会被 skip 逻辑当"完成"，清空进度文件再跑）。
3. **限流特征**：`feed_page` 返回 dict 无 `items`（如 `{'message': 'Please wait a few minutes...'}`）→ 等 2-3 分钟重试。
4. **时间乱序**：feed 返回不是严格倒序，翻页时打印日期范围辅助定位但不要据此提前结束。
5. **博主隐藏统计**：帖子 HTML 含 `view_counts":"false"` 时（如 thedesignely DTc_ASSjRTJ、feryfer_gg DSG91N3jFs-），三路 API（instaloader/移动端/页面）全是 None —— 这是平台隐私设置，**无法绕过**，诚实标注"博主隐藏"，互动率回退 followers 口径。

## 互动率口径

- 有 views：`(likes+comments)/views`（真实曝光口径）
- 无 views（博主隐藏）：`(likes+comments)/followers`（与"账户平均互动率"列同口径，可比）
- 数值格式：4 位小数（0.0047），与表内列格式一致
