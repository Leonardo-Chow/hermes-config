# OBSBOT 每日上线 SOP 输出格式

## 格式规则（用户确认）

1. **链接用纯文本 URL**：不要用 `[链接](URL)` 格式，直接写 `https://...`
2. **每条视频独立列出**：用加粗编号 + 标题作为独立条目，不要放在表格行里
3. **过滤官方账号**：@obsbot、@OBSBOT_Official、@obsbotmy、@obsbot_us 等
4. **Part 1 必须全面**：列出所有找到的内容
5. **Part 2 必须附带链接**：每条视频都要有链接
6. **Part 2 必须有质检**：视频内容质检 + 描述区质检（每项打勾或打叉）

---

## 报告结构（两部分 + 排除说明）

```markdown
## MM月DD日（周X）

### 全平台搜索结果

#### YouTube（N条）

**1. 视频标题**
- 博主：频道名
- 链接：https://www.youtube.com/watch?v=xxx
- 产品：Tiny 3
- 类型：Dedicated Video

**2. 视频标题**
- 博主：频道名
- 链接：https://www.youtube.com/watch?v=xxx
- 产品：Tiny 2 Lite
- 类型：Integration Video

#### TikTok（N条）

**1. 视频标题**
- 博主：@username
- 链接：https://www.tiktok.com/@user/video/xxx

#### Instagram（N条）

**1. 帖子标题**
- 博主：@username
- 链接：https://www.instagram.com/p/xxx

#### X/Twitter（N条）

**1. 帖子内容**
- 账号：@username
- 链接：https://x.com/user/status/xxx

---

### 符合 SOP 要求的视频

**1. 视频标题**
- 博主：频道名
- 链接：https://www.youtube.com/watch?v=xxx
- 产品：Tiny 3
- 类型：Dedicated Video
- 视频内容质检：
  - ☑️ 常规产品测评
  - ☑️ 原画直出演示
  - ☑️ 特殊主题：无
- 描述区质检：
  - ☑️ 官网链接：有
  - ☑️ 亚马逊链接：有
  - ☑️ 折扣信息：有（折扣码）
  - ☑️ 标签：有（#obsbot 等）

---

## ⚠️ 排除说明

**1. 视频标题**
- 平台：YTB
- 原因：品牌大使直播中使用，非专门产品测评
```

---

## 过滤规则

**必须过滤的内容：**
- OBSBOT 官方账号（@obsbot、@OBSBOT_Official、@obsbotmy、@obsbot_us、@obsbot.my 等）
- 纯官方宣传素材切片

**Part 2 排除标准：**
- 只挂购买链接未展示产品
- 品牌大使直播中使用（非专门测评）
- 仅描述中提到使用但无产品展示
- 抽奖/活动宣传（非产品测评）

---

## 视频类型判断

| 场景 | 类型 |
|:-----|:-----|
| 整期评测 OBSBOT 产品 | Dedicated Video |
| 视频中使用但非主推 | Integration Video |
| YouTube Shorts 竖屏 | YTB Shorts |
| TikTok 视频 | TT video |
| Instagram Reels | INS reel |
| Instagram 图文帖 | INS post |
| X/Twitter 帖子 | X post |
| 品牌大使使用展示 | Integration（品牌大使） |
