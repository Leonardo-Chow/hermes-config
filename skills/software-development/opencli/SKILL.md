---
name: opencli
description: "OpenCLI — 把任意网站变成 CLI 命令 + AI Agent 浏览器自动化。当需要抓取国内平台（小红书/B站/知乎/抖音/微博）、社交平台（Twitter/Reddit/LinkedIn）、或用已登录 Chrome 操作任何网页时使用。触发词：opencli、CLI抓取、浏览器自动化、小红书/B站/知乎/抖音/微博数据。"
---

# OpenCLI — 网站 → CLI + Browser Agent

> 来源: https://github.com/jackwener/opencli
> 安装: `npm install -g @jackwener/opencli` (Node >= 20)

## 核心概念

OpenCLI 有三大能力：

| 能力 | 说明 | 命令示例 |
|------|------|---------|
| **Adapter 命令** | 内置 100+ 网站适配器，一行命令取数据 | `opencli bilibili hot` |
| **Browser 驱动** | 通过已登录 Chrome 操作任意网页 | `opencli browser work open <url>` |
| **External CLI** | 统一入口管理本地工具 | `opencli gh pr list` |

## 5 种数据策略

| Strategy | 是否需要 Chrome | 说明 |
|----------|----------------|------|
| `PUBLIC` | ❌ | 纯 HTTP，无需登录 |
| `COOKIE` | ✅ 需登录 + 扩展 | 从已登录 Chrome 捕获 Cookie |
| `INTERCEPT` | ✅ | 拦截页面签名请求 |
| `UI` | ✅ | 完整 DOM 交互 |
| `LOCAL` | ❌ | 本地/开发端点 |

---

## 安装与配置

```bash
# 安装
npm install -g @jackwener/opencli

# 安装 Chrome 扩展（二选一）
# A. Chrome Web Store 搜索 "OpenCLI"
# B. 从 GitHub Releases 下载 zip，chrome://extensions 开发者模式加载

# 验证
opencli doctor

# 列出所有可用命令
opencli list
```

---

## 内置适配器（高频使用）

### 🇨🇳 国内平台

| 平台 | 命令 | 热门子命令 |
|------|------|-----------|
| **小红书** | `opencli xiaohongshu` | `search` `note` `comments` `feed` `user` `download` `publish` `notifications` `creator-notes` `creator-stats` |
| **B站** | `opencli bilibili` | `hot` `search` `history` `feed` `ranking` `download` `comments` `dynamic` `favorite` `following` `video` `user-videos` `subtitle` `summary` |
| **知乎** | `opencli zhihu` | `hot` `search` `question` `download` `follow` `like` `favorite` `comment` `answer` |
| **抖音** | `opencli douyin` | 见完整列表 |
| **微博** | `opencli weibo` | 见完整列表 |
| **1688** | `opencli 1688` | 下载商品图片/视频 |
| **微信公众号** | `opencli weixin` | 文章 Markdown 导出 |

### 🌍 国际平台

| 平台 | 命令 | 热门子命令 |
|------|------|-----------|
| **Twitter/X** | `opencli twitter` | `trending` `search` `timeline` `tweets` `bookmarks` `post` `download` `profile` `like` `follow` `notifications` `thread` |
| **Reddit** | `opencli reddit` | `hot` `frontpage` `popular` `search` `subreddit` `read` `user` `upvote` `save` `comment` |
| **LinkedIn** | `opencli linkedin` | `connect` `inbox` `jobs` `search` `timeline` `profile` `posts` `analytics` |
| **Amazon** | `opencli amazon` | `bestsellers` `search` `product` `offer` `new-releases` |
| **HackerNews** | `opencli hackernews` | `top` `new` `best` `ask` `show` `jobs` `search` |

### 🤖 AI 工具

| 平台 | 命令 | 子命令 |
|------|------|--------|
| **Claude** | `opencli claude` | `ask` `send` `new` `status` `read` `history` |
| **Gemini** | `opencli gemini` | `new` `ask` `image` `deep-research` |
| **NotebookLM** | `opencli notebooklm` | `list` `open` `get` `summary` `source-list` |

### 🖥 桌面应用（Electron via CDP）

Cursor / Trae CN / Codex / ChatGPT App / ChatWise / Discord / 豆包

### 🔧 CLI Hub

`gh` · `docker` · `vercel` · `obsidian` · `lark-cli` · `ntn`(Notion) · `tg` · `discord` · `wx`

---

## 常用命令速查

### 数据抓取

```bash
# 热榜
opencli bilibili hot --limit 10 -f json
opencli zhihu hot --limit 10 -f json
opencli hackernews top --limit 10 -f json
opencli xiaohongshu feed --limit 10

# 搜索
opencli xiaohongshu search "AI Agent" --limit 20
opencli bilibili search "机器学习" --limit 10
opencli zhihu search "LLM" --limit 10
opencli twitter search "openai" --limit 20

# 详情
opencli bilibili video BV1xxx
opencli xiaohongshu note <note_id>
opencli zhihu question <question_id>
opencli twitter tweets <username> --limit 20
```

### 下载

```bash
# 小红书图片/视频
opencli xiaohongshu download "https://www.xiaohongshu.com/..." --output ./xhs

# B站视频（需 yt-dlp）
opencli bilibili download BV1xxx --output ./bilibili

# Twitter 媒体
opencli twitter download <username> --limit 20 --output ./twitter

# 1688 商品图
opencli 1688 download <item_id> --output ./1688-downloads

# 知乎文章（Markdown）
opencli zhihu download <article_url> --output ./zhihu

# 微信公众号文章
opencli weixin download <article_url> --output ./weixin
```

### 输出格式

```bash
-f json    # 管道给 jq 或 LLM
-f csv     # 电子表格
-f md      # Markdown 表格
-f yaml    # YAML
-f table   # 默认终端表格
```

---

## Browser 驱动（任意网页操作）

当没有内置适配器时，用 `opencli browser` 直接操控已登录的 Chrome：

```bash
# 打开页面
opencli browser work open "https://example.com"

# 查看页面状态（DOM 快照）
opencli browser work state

# 点击元素
opencli browser work click "按钮文字"
opencli browser work click "@ref_id"    # state 返回的 ref

# 输入文字
opencli browser work type "搜索框" "关键词"
opencli browser work fill "表单字段" "值"

# 提取数据
opencli browser work extract "selector"
opencli browser work get text "h1"

# 绑定已打开的标签页（保持登录态）
opencli browser gmail bind
opencli browser gmail state
opencli browser gmail click "Search"

# 截图
opencli browser work screenshot

# 网络拦截
opencli browser work network
```

### Session 管理

```bash
# 同一流程用同一 session name
opencli browser my-task open <url>
opencli browser my-task state
opencli browser my-task click "..."
opencli browser my-task close    # 完成后释放

# 绑定现有标签（不夺取控制权）
opencli browser <session> bind
opencli browser <session> unbind
```

---

## Adapter 开发（给新网站写适配器）

```bash
# 初始化
opencli browser init <site>/<command>

# 调试（前台 + trace）
opencli browser <session> open <url> --trace on --keep-tab true --window foreground

# 验证
opencli browser verify <site>/<command>
```

### 策略选择优先级

```
PUBLIC_API（最稳）→ COOKIE_API → UI_SELECTOR → DOM_STATE → PAGE_FETCH → INTERCEPT（最易漂）
```

---

## AutoFix（适配器自修复）

当命令失败时自动诊断修复：

```bash
# 失败类型
SELECTOR      # DOM 变了 → 重新定位元素
EMPTY_RESULT  # API 响应变了 → 检查是否平台反爬
API_ERROR     # 端点迁移 → 找新端点
PAGE_CHANGED  # 页面结构变了 → 更新解析逻辑
```

**安全边界**：
- `AUTH_REQUIRED` (exit 77) → 停止，让用户登录
- `BROWSER_CONNECT` (exit 69) → 停止，让用户运行 `opencli doctor`
- 最多 3 轮修复，失败则报告

---

## Sitemap（站点知识图谱）

为 Agent 提供站点导航知识，避免盲点：

```bash
# 站点知识存储
~/.opencli/sites/<site>/sitemap/
  SITE.md                 # 站点概览
  pages/<page-id>.md      # 页面状态签名
  workflows/<task-id>.md  # 任务路径（最佳 + 降级）
  pitfalls.md             # 已知坑点
```

---

## 与现有工具链的关系

| 场景 | 推荐工具 |
|------|---------|
| 国内平台热榜/搜索 | **OpenCLI** > AutoCLI（OpenCLI 用已登录 Chrome，更稳） |
| Twitter/Reddit 数据 | **OpenCLI**（需要登录态的用 COOKIE 策略） |
| 小红书/知乎下载 | **OpenCLI** download 命令 |
| 需要认证的网页操作 | **OpenCLI browser** > bb-browser（同一个 Chrome 实例） |
| 无需登录的快速抓取 | AutoCLI / Tavily（更快，不需要 Chrome） |
| B站视频下载 | **OpenCLI** `bilibili download`（底层 yt-dlp） |

---

## ⚠️ 注意事项

1. **需要 Chrome 打开 + 扩展安装** — `opencli doctor` 必须通过
2. **被墙站点需要代理** — Twitter 等需要 VPN
3. **Cookie 时效** — 登录过期需重新在 Chrome 登录
4. **反爬风险** — 高频调用可能触发平台风控
5. **Node >= 20** — 必须检查版本
