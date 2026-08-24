---
name: instagram-competitor-kol-discovery
description: 在 Instagram 上找发过特定竞品产品的 KOL（如 OBSBOT Meet 竞品 Insta360 Link 2C/2C Pro 的女性博主）。流程：IG 搜索页 → 提取帖子 → 逐帖解析作者 → 验证性别/bio → 直接交付链接清单。
---

# Instagram 竞品产品博主发现

场景：用户要给自家产品找竞品在 IG 上的创作者（尤其女性博主），用于对标/合作/竞争情报。例如 OBSBOT Meet（网络摄像头）→ 竞品 Insta360 Link 2C / Link 2C Pro 的女性博主。

**纯发现型请求：用户只要链接清单 → 直接交付链接 + 粉丝数 + 内容方向，不要跑完整筛选入库 SOP（不建库、不 CSV）。**（完整 SOP 见 `instagram-following-export` skill）

## 流程

```
1. IG 搜索页找帖子：instagram.com/explore/search/keyword/?q=<产品关键词>
2. browser_console 提取帖子 shortcode（a[href^="/p/"]）
3. curl 每个帖子页，og:description 解析作者 username
4. 女性候选 curl 主页验证（og:description 含 NAME）
5. 排除男性/品牌号/聚合号，直接交付链接
```

## 详细步骤

### 1. IG 搜索页
```
browser_navigate → https://www.instagram.com/explore/search/keyword/?q=insta360%20link%202c
```
⚠️ **每次 navigate 到搜索页都会掉 session 弹登录框**：
- navigate → 见 login 弹窗 → browser_console 注入 cookie（`~/.hermes/cookies/platform_cookies.json` 的 instagram 字段，12 条 cookie 字符串）
- 再 navigate 同 URL → 此时已登录
- 等 8-10s 加载（页面有 progressbar）

### 2. 提取帖子 shortcode
```js
document.querySelectorAll('a[href^="/p/"]')  // → ["/p/DGUKFxHIFrI/", ...]
```
搜索页 DOM 不直接暴露作者，必须逐帖抓。

### 3. 逐帖抓作者（curl 匿名即可）
```
curl -s -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
     https://www.instagram.com/p/<code>/
```
og:description 格式：`X likes, Y comments - <username> on <date>: "<caption>"`
正则：`-\s*([A-Za-z0-9_.]+)\s+on\s+`

### 4. 验证性别/bio
curl 主页 → og:description：`X Followers, Y Following, Z Posts - See Instagram photos and videos from <NAME> (@user)`
- NAME 判断性别；排除男性科技测评号
- 排除品牌/聚合号（如 the_setup_vault）
- 性别不确定的标注「待确认」

### 5. 交付格式
- 直接列链接 + 粉丝数 + 内容方向，按量级分组（头部 >15万 / 腰部 3-10万 / 小博主 1-2万）
- 标注 #AD 品牌合作帖（说明愿意接同类产品合作）

## 判断要点

- 大博主（>10万粉）的竞品帖子通常是 #AD 合作帖 → 愿意接同类产品，但贵
- 小博主（1-2万粉）自发内容 → 性价比高
- 纯产品测评的男性科技号、品牌官方号、聚合号一律排除
- Tavily/Google 搜产品名主要返回 YouTube 男性测评 + 官网页，对找 IG 博主帮助有限 → 直接走 IG 搜索页

## 已验证示例（Insta360 Link 2C/2C Pro 女性博主）

| 博主 | 粉丝 | 方向 | 备注 |
|------|------|------|------|
| minibutmighty_ (Kathryn Nash) | 79.4万 | 生活方式 | 发过 Link 2C 帖 |
| studywithemmane_ (Emma) | 45.1万 | Study & Tech | Link 2C Pro 测评 |
| thedesignely (Agatha) | 16.3万 | UI/UX 设计师 | Link 2C 内容 |
| erencmlbl (Eren) | 23.4万 | 大博主 | ⚠️ 性别待确认 |
| audreycaprianni (auds) | 6.3万 | 桌搭 | "my desk setup" Link 2C |
| liyuelatte (Connie) | 3.3万 | Cozy Lifestyle Gamer | Link 2C 视频 |
| byex0si | 3.2万 | 内容创作者 | IG+TikTok Link 2 Pro 开箱 |
| prisciliagoh | 1.3万 | tech 测评 | 东南亚女性 |
| btoiiptimist (brenda toi) | 1.1万 | 创作者 | "Meet the Insta360" 帖 |

完整配方与坑见 `references/competitor-product-discovery.md`。
