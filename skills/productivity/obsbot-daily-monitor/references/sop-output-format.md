# OBSBOT 每日上线 SOP 输出格式

## 报告结构（两部分）

报告必须包含两部分，不能只输出筛选结果。

---

## Part 1：全平台搜索结果

列出当日搜索到的**所有**第三方 OBSBOT 相关内容（已过滤官方账号）。

```markdown
## 📋 MM.DD OBSBOT 上线资源报告

---

## Part 1：全平台搜索结果

以下为今日所有第三方 OBSBOT 相关内容（已过滤官方账号）：

### YouTube（N条）

| # | 博主 | 视频标题 | 链接 | 发布时间 | 简介 |
|:--|:-----|:---------|:-----|:---------|:-----|
| 1 | MasteriTech | OBSBOT Tiny 2 Lite: ... | [链接](https://youtube.com/watch?v=xxx) | 21:00 | 远程医疗测评 |

### TikTok（N条）

| # | 博主 | 视频标题 | 链接 | 简介 |
|:--|:-----|:---------|:-----|:-----|
| 1 | @mrsmobster | OBSBOT Tiny 3 Unboxing! | [链接](https://www.tiktok.com/@user/video/xxx) | 开箱测评 |

### Instagram（N条）

今日无第三方新帖。

### X/Twitter（N条）

| # | 账号 | 内容 | 链接 |
|:--|:-----|:-----|:-----|
| 1 | @StreamElements | TwitchCon 抽奖 | [链接](https://x.com/user/status/xxx) |
```

---

## Part 2：符合 SOP 要求的视频

从 Part 1 中筛选出符合要求的视频。

```markdown\n---\n\n## Part 2：符合 SOP 要求的视频\n\n> 筛选标准：视频必须包含完整的产品测评内容，排除纯链接/官方素材切片/仅使用展示\n\n### YouTube（N条）\n\n| 博主 | 视频 | 链接 | 产品 | 视频类型 | 简析 |\n|:-----|:-----|:-----|:-----|:---------|:-----|\n| MasteriTech | OBSBOT Tiny 2 Lite | [链接](https://youtube.com/watch?v=xxx) | Tiny 2 Lite | Dedicated Video | 远程医疗场景专项测评 |\n\n### TikTok（N条）\n\n| 博主 | 视频 | 链接 | 产品 | 简析 |\n|:-----|:-----|:-----|:-----|:-----|\n| @mrsmobster | OBSBOT Tiny 3 Unboxing | [链接](https://www.tiktok.com/@user/video/xxx) | Tiny 3 | 开箱测评 |\n\n### Instagram（N条）\n\n今日无新帖。\n\n### X/Twitter（N条）\n\n今日无产品测评类内容。\n```\n\n**⚠️ Part 2 必须附带链接**（用户明确要求 2026-05-31）。不能只有视频标题没有链接。

---

## 排除说明

```markdown
---

## ⚠️ 排除说明

| 排除项 | 平台 | 原因 |
|:-------|:-----|:-----|
| KidSmoove | YTB | 品牌大使直播中使用，非专门产品测评 |
| wizhunt | YTB | 骑行直播，仅描述中提到使用 Tiny 2，无产品展示 |
| @StreamElements | X | 抽奖活动，非产品测评 |
```

---

## 过滤规则

**必须过滤的内容：**
- OBSBOT 官方账号（@obsbot、@OBSBOT_Official、@obsbotmy、@obsbot_us、@obsbot.my、@obsbot_official 等）
- 纯官方宣传素材切片

**Part 2 排除标准：**
- 只挂购买链接未展示产品
- 品牌大使直播中使用（非专门测评）
- 仅描述中提到使用但无产品展示
- 抽奖/活动宣传（非产品测评）

---

## 视频类型判断

| 场景 | 类型 | 说明 |
|:-----|:-----|:-----|
| 整期评测 OBSBOT 产品 | Dedicated Video | 完整产品测评 |
| 视频中使用但非主推 | Integration Video | 产品在视频中出现 |
| YouTube Shorts 竖屏 | YTB Shorts | <60s 竖屏视频 |
| TikTok 视频 | TT video | TikTok 平台 |
| Instagram Reels | INS reel | Instagram 短视频 |
| Instagram 图文帖 | INS post | Instagram 图文 |
| X/Twitter 帖子 | X post | 推文 |
| 品牌大使使用展示 | Integration（品牌大使） | 标记已合作红人 |

---

## 质检要点

1. **链接验证**：确保所有链接指向视频落地页，不是首页
2. **标签检查**：#obsbot、#obsbot_tiny3lite 等标签是否完整
3. **折扣信息**：是否有折扣码、购买链接
4. **已合作红人**：需标记对应小伙伴名字（参考 KOL资源交接表）
5. **官方账号过滤**：确认已过滤所有 OBSBOT 官方账号
6. **两部分完整性**：Part 1 列出所有结果，Part 2 列出筛选结果
