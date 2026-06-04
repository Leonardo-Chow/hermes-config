---
name: platform-cookies-manager
description: |
  平台Cookie管理 — 保存、更新、使用Instagram/X/TikTok/YouTube等平台的登录Cookie，
  用于需要认证的API请求和爬取。
version: 1.0.0
author: Leonardo
metadata:
  hermes:
    tags: [cookies, authentication, Instagram, Twitter, TikTok, YouTube, scraping]
    related_skills: [scrapling, obsbot-daily-launch-monitor]
---

# 平台Cookie管理

管理Instagram/X/TikTok/YouTube等平台的登录Cookie，用于需要认证的API请求和爬取。

## Cookie文件位置

```
~/.hermes/cookies/platform_cookies.json
```

## 文件格式

```json
{
  "instagram": "cookie_string",
  "twitter": "cookie_string",
  "tiktok": "cookie_string",
  "youtube": "cookie_string",
  "updated_at": "YYYY-MM-DD"
}
```

## 使用场景

| 平台 | Cookie用途 | 使用方式 |
|:-----|:-----------|:---------|
| Instagram | 访问用户主页、获取帖子详情 | Scrapling StealthyFetcher + Cookie |
| X/Twitter | 访问推文、获取用户数据 | API请求 + Cookie头 |
| TikTok | oembed API、视频详情 | curl + Cookie头 |
| YouTube | 访问需要登录的视频、评论 | API请求 + Cookie头 |

## 如何获取Cookie

### 浏览器获取方法（推荐）

1. 打开目标平台并登录
2. 按 F12 打开开发者工具
3. 切换到 Console 标签
4. 输入 `document.cookie` 并按回车
5. 复制输出的 Cookie 字符串

### ⚠️ 粘贴限制绕过

某些网站（如 TikTok）会阻止控制台粘贴。解决方案：

**方法1：地址栏执行**
```
javascript:void(document.title=document.cookie)
```
输入后按回车，页面标题会变成 Cookie 内容。

**方法2：Chrome 扩展**
安装 "Allow Right-Click" 扩展，允许在任何网站右键粘贴。

**方法3：最短输入**
在 Console 中手动输入 `document.cookie`（仅14个字符），不需要粘贴。

### Chrome Cookie导出

```bash
# macOS Chrome Cookie数据库
~/Library/Application Support/Google/Chrome/Default/Cookies
```

注意：Chrome Cookie是加密的，需要解密才能使用。

## 使用Cookie的示例

### Instagram (Scrapling)

```python
import json
import sys
sys.path.insert(0, '/Users/zhoulong/.hermes/skills/scrapling/venv/lib/python3.12/site-packages')
from scrapling.fetchers import StealthyFetcher

# 读取Cookie
with open('/Users/zhoulong/.hermes/cookies/platform_cookies.json') as f:
    cookies = json.load(f)

page = StealthyFetcher.fetch(
    'https://www.instagram.com/obsbot/',
    headless=True,
    network_idle=True,
    disable_resources=True,
    proxy='http://127.0.0.1:1082',
    extra_headers={'Cookie': cookies['instagram']}
)
```

### TikTok (curl + oembed)

```bash
# 读取Cookie
COOKIE=$(python3 -c "import json; print(json.load(open('/Users/zhoulong/.hermes/cookies/platform_cookies.json'))['tiktok'])")

# 使用Cookie调用oembed API
curl -s --max-time 8 -x http://127.0.0.1:1082 \
  -H "Cookie: $COOKIE" \
  "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@user/video/VIDEO_ID"
```

### X/Twitter (curl)

```bash
# 读取Cookie
COOKIE=$(python3 -c "import json; print(json.load(open('/Users/zhoulong/.hermes/cookies/platform_cookies.json'))['twitter'])")

# 使用Cookie访问API
curl -s -H "Cookie: $COOKIE" "https://api.x.com/2/tweets/VIDEO_ID"
```

### YouTube (curl)

```bash
# 读取Cookie
COOKIE=$(python3 -c "import json; print(json.load(open('/Users/zhoulong/.hermes/cookies/platform_cookies.json'))['youtube'])")

# 使用Cookie访问API
curl -s -H "Cookie: $COOKIE" "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=VIDEO_ID&key=API_KEY"
```

## Cookie更新

当Cookie过期时，需要重新获取：

1. 打开浏览器登录目标平台
2. 按F12获取新的Cookie
3. 更新 `~/.hermes/cookies/platform_cookies.json` 文件
4. 更新 `updated_at` 字段

## Cookie有效期

| 平台 | 预计有效期 | 过期表现 |
|:-----|:-----------|:---------|
| Instagram | 1-3个月 | 返回登录页面、401错误 |
| X/Twitter | 1-6个月 | 返回403错误、要求重新登录 |
| TikTok | 1-2周 | oembed返回400、页面显示登录 |
| YouTube | 6-12个月 | API返回401、需要重新授权 |

## 已知限制

1. **Cookie加密**：Chrome的Cookie是加密的，无法直接读取
2. **HttpOnly标记**：部分Cookie标记为HttpOnly，JavaScript无法访问
3. **SameSite限制**：跨域请求可能被SameSite策略阻止
4. **IP绑定**：部分平台的Cookie与IP地址绑定，切换VPN后可能失效
5. **浏览器注入失败**（2026-06-02 验证）：浏览器安全策略阻止 `document.cookie` 设置，无法通过 JavaScript 注入 Cookie 到已打开的页面。解决方案：让用户在自己 Chrome 中登录后，通过 Console 执行 `document.cookie` 提取 Cookie 字符串。
6. **TikTok Cookie有效期**：约 1-2 周过期，需用户定期更新
5. **浏览器注入失败**：浏览器安全策略阻止通过 JavaScript 注入 Cookie（`document.cookie` 赋值被拒绝），需要用 curl 带 Cookie 头的方式替代
6. **TikTok CAPTCHA**：即使用 Cookie，Profile 页面仍可能弹出滑块验证，视频网格不渲染

## 安全注意事项

- Cookie文件包含登录凭证，不要提交到Git仓库
- 定期更新Cookie，避免使用过期凭证
- 不要在公共场合分享Cookie
- 使用完毕后及时清理临时文件

## 文件路径

- Cookie文件：`~/.hermes/cookies/platform_cookies.json`
- 记忆存储：memory中记录了Cookie文件位置和更新日期
