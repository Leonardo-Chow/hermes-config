# 竞品产品博主发现 — 完整配方（2026-07-30 实战）

场景：OBSBOT 产品线（如 Meet 网络摄像头）找竞品（Insta360 Link 2C / Link 2C Pro / Logitech Brio / Razer Kiyo 等）的 IG 女性博主。

## 步骤

### 1. IG 搜索页
```
browser_navigate → https://www.instagram.com/explore/search/keyword/?q=<产品关键词 URL 编码>
```
⚠️ 每次 navigate 到搜索页都会掉 session 弹登录框。流程：
- navigate → 若见 login 弹窗 → browser_console 注入 cookie（platform_cookies.json 的 instagram 字段，12 条）
- 再 navigate 一次同 URL（此时已登录）
- 等 8-10s 让结果加载（页面有 progressbar）

### 2. 提取帖子 shortcode
```js
document.querySelectorAll('a[href^="/p/"]')  // 拿 /p/<code>/ 列表
```
搜索页 DOM 不直接暴露作者，必须逐帖抓取。

### 3. 逐帖抓作者（curl 匿名即可，无需登录）
```
curl -s -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
     https://www.instagram.com/p/<code>/
```
og:description 格式：`X likes, Y comments - <username> on <date>: "<caption>"`
正则：`-\s*([A-Za-z0-9_.]+)\s+on\s+`

### 4. 验证性别/bio（curl 主页 og:description）
`X Followers, Y Following, Z Posts - See Instagram photos and videos from <NAME> (@user)`
- NAME 判断性别；排除男性科技测评号（willhallfilms、techwithbashir、thehippiehacker、devdoesreviews 等）
- 排除品牌/聚合号（the_setup_vault 等）
- 性别不确定的单独标注「待确认」（如 erencmlbl，名字中性）

### 5. 交付
- 直接列链接 + 粉丝数 + 内容方向，按量级分组（头部>15万 / 腰部3-10万 / 小博主1-2万）
- 标注哪些是 #AD 合作帖（说明愿意接同类产品合作）

## 已验证清单（Insta360 Link 2C/2C Pro 女性博主）

| 博主 | 粉丝 | 内容方向 | 备注 |
|------|------|---------|------|
| minibutmighty_ (Kathryn Nash) | 79.4万 | 生活方式大博主 | 发过 Link 2C 帖子 |
| studywithemmane_ (Emma) | 45.1万 | Study & Tech | 发过 Link 2C Pro 测评 |
| thedesignely (Agatha) | 16.3万 | UI/UX 设计师 | 发过 Link 2C 内容 |
| erencmlbl (Eren) | 23.4万 | 大博主 | ⚠️ 性别待确认 |
| audreycaprianni (auds) | 6.3万 | 桌搭 | "my desk setup" Link 2C 帖 |
| liyuelatte (Connie) | 3.3万 | Cozy Lifestyle Gamer | 发过 Link 2C 视频 |
| byex0si | 3.2万 | 内容创作者 | IG+TikTok 都发过 Link 2 Pro 开箱 |
| prisciliagoh | 1.3万 | tech 测评 | 东南亚女性 |
| btoiiptimist (brenda toi) | 1.1万 | 创作者 | "Meet the Insta360" 帖 |

## 坑
- Tavily 搜 "insta360 link 2c" 主要返回 YouTube 男性测评 + 品牌官网页，对找 IG 博主帮助有限 → 直接走 IG 搜索页
- 搜索页结果有时不渲染作者链接（JS 懒加载），逐帖 curl 更可靠
- 帖子页 curl 偶尔空响应（限流/负载），重试即可；21 个帖子约 85s（execute_code 循环）
- 搜索关键词用产品全名（"insta360 link 2c pro"）会漏掉只写 "link 2c" 的帖子，可搜两个变体并集
