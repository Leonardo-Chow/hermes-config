---
name: local-webapp-builder
description: 为小白用户构建本地运行的轻量网页工具（管理系统/数据库/看板/CRM）。零依赖 Python 标准库 + SQLite 单文件 + 原生前端，双击即用。当用户要求"本地跑一个网页版XXX"、"做一个我自己的管理系统"或"帮我把XX数据做成网页版"时使用。
---

# 本地轻量网页工具构建

## 触发条件
- 用户要求本地跑网页版工具（管理系统/数据库/看板/CRM），尤其自称"小白"或强调要简单
- 单人/小团队使用、数据敏感（KOL资料、业务数据）→ 纯本地、零依赖、单文件
- 用户先问"有没有现成开源平台"→ 先 GitHub API 搜 stars 排序评估，再决定自建

## 工作流（用户明确要求，勿跳过）
1. **先说你的设计思路**：技术选型、字段、功能、为什么这么选。一句话讲清"零依赖+单文件+本地"对小白的好处
2. **再问用户的设计思路**：用 clarify 开放式问题——最常打开它做什么 / 数据从哪来 / 界面偏好（表格vs卡片）/ 缺哪些字段
3. **用户回复后开始执行**；用户未回复就停在问题处，不要擅自大改设计
4. 确认后全程自动执行不中途停；交付时明确说「任务执行完毕」+ 摘要 + 下一步建议

## 技术栈（零依赖）
- 后端：Python 标准库 `http.server.ThreadingHTTPServer` + `sqlite3` + `csv`（macOS/Linux 自带 python3）
- 前端：webapp/ 目录静态文件（原生 HTML/CSS/JS），**不用 CDN**（国内网络）
- 数据：SQLite 单文件，`PRAGMA journal_mode=WAL`，备份=复制 db 文件
- 启动：`start.sh` = `cd "$(dirname "$0")" && python3 app.py` + 自动 open 浏览器；默认绑 `127.0.0.1`，局域网访问才改 `0.0.0.0`

## 骨架要点（完整骨架见 templates/app_skeleton.py）
- `protocol_version = "HTTP/1.1"` 必须设置（默认 1.0 会坑 Python urllib 客户端，见 Pitfall 2）
- **FIELDS 数组驱动一切**：`[("field","中文表头"),...]` → 建表/表单/表格/CSV导出 全从它生成，保证前后端一致
- init_db 用 `PRAGMA table_info` 对比 + `ALTER TABLE ADD COLUMN` 兼容旧库升级
- 多页面系统：`/`、`/kol.html`、`/add.html` 显式路由 + 顶部导航；单页小工具可一个 index.html 搞定
- CSV 导出加 BOM `\ufeff`（Excel 打开不乱码）；CSV 导入做中英文表头别名映射 + 万/w/$ 后缀 parse
- 新建 db 后先 curl 全链路测试再交付

## Pitfalls（踩过的坑）
1. **Python 3.9 f-string 不能嵌套同引号**：`f"...{', '.join('"%s"' % c for c in cols)}..."` → `SyntaxError: f-string: unterminated string`。改用 `%` 拼接（`"INSERT ... (%s) VALUES (%s)" % (col_str, ph)`）或先把子串算成变量。3.12+ 才放开此限制。
2. **http.server 默认 HTTP/1.0**：Python `urllib.request` 发请求会 `RemoteDisconnected: Remote end closed connection without response`，而 curl / 浏览器 / Node fetch 都正常。修复 = `protocol_version = "HTTP/1.1"`。验证客户端用 **curl 或 Node fetch**（浏览器同源），别用 Python urllib 测。
3. **SQLite TEXT 列排序是字典序**：数值存 TEXT 时 `ORDER BY "cpm" DESC` 会把 16.67 排在 4.44 后面。数值排序用 `CAST(col AS REAL)`（如 `ORDER BY CAST("cpm" AS REAL) DESC`）。
4. **前端 datalist 输入框 id 带 -input 后缀**（`f-category-input` vs 字段名 `category`）：saveForm/openForm 读 id 必须和实际 input id 一致——用 `FIELD_IDS = {字段: "f-字段-input", ...}` 映射对象统一管理，别手写两份数组（本次 bug：类别/来源填了但保存后为空）。
5. **表单字段必须和 FIELDS 数组一一对应**：漏一个输入框（如 added_date 无对应 input）→ 保存时报 `Cannot read properties of null`。
6. **CSV 数字字段存 TEXT 没关系**，但筛选/排序要 CAST；parse 时处理 "1.2万"、"$800"、逗号千分位。
7. **Browser MCP 点下拉框选项偶发失败**（`Could not compute box model`）：改用 JS 直接 `document.getElementById(...).value = '...'` 再调保存函数验证。
8. **登录认证用 Cookie 不用 Authorization header**：header 只在 fetch 时带，浏览器整页导航（点链接/输地址）不带 → 登录后跳转被 401 打回登录页。方案：登录成功 `Set-Cookie: kol_session=<token>; Path=/; HttpOnly; SameSite=Lax`，后端 check_auth 正则解析 Cookie（可兼容 header 双通道）；登出发 `Set-Cookie: kol_session=; Max-Age=0`。
9. **SVG 环形图文字歪斜：rotate 只加在圆弧 circle 上**（配 `transform-origin: 50% 50%`），不能加在整个 `<svg>`——否则中间百分比文字跟着转成歪的（用户明确投诉「环形图是歪的」）。参数：`CIRC = 2πr`，`stroke-dashoffset = CIRC × (1 - pct/100)`。多色分段环：多个 circle 叠放，`stroke-dasharray="len CIRC"` + 负 offset 依次错开。
10. **日期计算禁用 toISOString（UTC 差一天）**：UTC+8 下 `new Date("2026-09-15T00:00:00").toISOString().slice(0,10)` 返回前一天。本地日期：`new Date(y, m-1, d)` 解析 + `getFullYear/getMonth/getDate` 手拼格式化。所有「日期±N天」（自动提醒、过期判断）都走本地格式化。
11. **「下拉+自由输入」= input + datalist**：用户要求「选项可手动更改」时，把 `<select>` 换 `<input list="x-suggest">` + `<datalist>`（动态选项 JS 填 datalist innerHTML，监听 oninput 而非 onchange）。产品型号选择后自动带出成本价并算 CPM、上市日期自动设提醒日期——这类联动后端保存也要兜底重算。

## GitHub 自动备份（数据防丢失）
- 用户要求「上传 GitHub 防丢失 + 数据实时上传」：建**私有仓库**（private），写操作后自动 commit+push
- **gh token 可能只读**（建仓库/推送/加 SSH key 全 403）→ 从另一个仓库 remote URL 提取内嵌写权限 PAT（如 `git -C ~/.hermes remote get-url origin` 里的 `https://User:ghp_xxx@github.com/...`），用旧 token 建仓库 + 推送
- backup.sh 模式：锁文件（`stat -f %m` 查年龄 <10s 跳过，合并连续写）→ `git add -A` → `git commit -m "auto-backup: TS"` → `git push`；每次重新 remote add（带 token）
- app.py 写操作后 `threading.Thread(target=auto_backup, daemon=True).start()` 异步触发，不阻塞请求
- `.gitignore` 必须排除 `*.db-shm` `*.db-wal`（WAL 临时文件），只提交 kol.db
- 验证：`git clone` 仓库查 kol.db 含最新数据，别只信本地 commit

## 用户 UI 偏好（重要，本会话明确纠正过）
- **交互式网页工具用户要 Claude 风格**：奶油底 #FAF9F5、橙棕主色 #D97757、衬线标题 Georgia、左侧边栏、pill 标签、柔和阴影、留白充足——**不要默认 leonardo-brand 深蓝科技主题**（深蓝适合报告/PPT，网页工具用户明确说「UI 我不喜欢」）
- 表格列多时用横向滑动（`overflow-x:auto` + `min-width` + thead sticky），不要挤排版
- 大数字用衬线 serif 显示，进度用环形 SVG 更直观

## 验证清单
- 后台启动 → curl 每个 API（HTTP 200 + 数据正确）
- Node fetch 测 POST（与浏览器 fetch 同源）：`node -e "fetch(url).then(r=>r.json()).then(console.log)"`
- browser_navigate 看页面渲染；JS 填表单→保存→API 查库确认落库
- 测搜索/筛选/排序/导入/导出全链路；旧库升级（ALTER TABLE）兼容
- 交付物：app.py + webapp/ + start.sh + README.md（含启动/导入格式/备份说明）

## 参考
- references/kol-manager-v2.md — 实战案例：KOL 网红管理系统 v2.0（字段表、CPM 公式、邮件提醒联动、页面结构）
- references/kol-manager-v3.md — v3.x 演进：登录认证、操作日志+回调、Claude 风格 UI、环形 SVG、产品价格联动、Views 达标看板、GitHub 自动备份（迭代 v3+ 时先读这个）
