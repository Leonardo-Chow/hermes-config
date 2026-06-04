# TikTok 抓取策略详解

## 已知限制（2026-06-02 验证）

1. **Profile 页面有 CAPTCHA 滑块**：浏览器自动化无法绕过
2. **搜索页面需要登录**：未登录时显示「登录以搜索热门内容」
3. **Cookie 注入失败**：浏览器安全策略阻止 `document.cookie` 设置
4. **web_search 索引延迟 1-3 天**：新发布的视频不会立即被收录

## 可用方法

### 方法1: oembed API + 代理（最可靠）

```bash
PROXY="http://127.0.0.1:1082"
curl -s --max-time 8 -x $PROXY "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@USER/video/VIDEO_ID"
```

返回：
```json
{
  "version": "1.0",
  "type": "video",
  "title": "视频标题",
  "author_url": "https://www.tiktok.com/@username",
  "author_name": "显示名称",
  "thumbnail_url": "https://..."
}
```

### 方法2: 视频 ID 解码时间

TikTok 视频 ID 是 Snowflake ID，包含发布时间：

```python
import datetime
video_id = "7646458655717526797"
timestamp = int(video_id) >> 32
date = datetime.datetime.fromtimestamp(timestamp).date()
# 输出: 2026-06-02
```

### 方法3: 已知账号扫描

维护 OBSBOT 相关 TikTok 账号列表，定期用 oembed API 检查最新视频。

### 方法4: web_search 间接搜索

```python
web_search('site:tiktok.com OBSBOT 2026-06', limit=10)
```

注意：Tavily 有每日配额限制（keyless ~10次/天）。

## 用户 Cookie 提取方法

当需要用户提供 TikTok Cookie 时：

1. 让用户在 Chrome 中打开 TikTok 并登录
2. 按 F12 打开开发者工具
3. 切换到 Console 标签
4. 输入 `document.cookie` 并回车
5. 复制输出的 Cookie 字符串
6. 保存到 `~/.hermes/cookies/platform_cookies.json`

> **注意**：不要尝试通过浏览器自动化注入 Cookie，浏览器安全策略会阻止。

## OBSBOT 相关 TikTok 账号

| 账号 | 显示名称 | 粉丝数 |
|:-----|:---------|:-------|
| @obsbot | OBSBOT Official | 17.5K |
| @obsbotmy1 | obsbotmy | - |
| @psscreativemedia | PSS Creative Media | 1.8K |
| @mrsmobster | MrsMobster | - |
| @maccagames | MaccaGames | - |
| @brainiacvp | BrainiacVP | - |
| @obsbot.thailand | obsbot-TH | - |
| @obsbotsingapore | Obsbot-SG | - |
