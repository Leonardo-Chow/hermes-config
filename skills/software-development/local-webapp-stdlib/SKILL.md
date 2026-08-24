---
name: local-webapp-stdlib
description: 零依赖本地 Web 管理系统开发（Python 标准库 http.server + SQLite + 原生 HTML/JS/CSS）。当用户要求「本地跑一个网页版管理系统/工具」（如 KOL 管理、数据管理、后台面板），或要求在已有轻量系统上加功能时使用。涵盖：零依赖架构、登录认证、操作日志+回调、SVG 环形图、CSV 导入导出、GitHub 自动备份等可复用模式与关键坑。
---

# 零依赖本地 Web 管理系统（Python 标准库 + SQLite）

## 何时使用
- 用户要求「在本地跑一个网页版 XX 系统」，强调小白友好/双击即用/数据本地保存
- 已有 `~/kol-manager` 系统的迭代需求（见 references/kol-manager.md）
- 需要单文件数据库、无 pip 依赖、局域网可访问的后台工具

## 架构模板（已验证可工作）
- **后端**：`ThreadingHTTPServer` + `BaseHTTPRequestHandler`，`sqlite3` 单文件（WAL 模式），`protocol_version = "HTTP/1.1"`
- **前端**：纯原生 HTML/CSS/JS，无 CDN、无框架，静态文件由 handler 服务
- **字段/表结构**：定义 `FIELDS` 列表驱动增删改查/导出，`ALTER TABLE ADD COLUMN` 做旧库兼容
- **认证**：登录发 token → `Set-Cookie: kol_session=<token>; Path=/; HttpOnly; SameSite=Lax`；服务端 `check_auth` 解析 Cookie（也兼容 Authorization header）
- **操作日志+回调**：`operation_log` 表存 before/after JSON，rollback 按 action 恢复；回调需管理员密码
- **目录**：`app.py` + `webapp/`（index/kol/add/login.html + style.css）+ `start.sh` + `backup.sh` + `kol.db`

## 关键坑（都实际踩过）
1. **Python 3.9 f-string 不能嵌套同引号**：`f"INSERT ... ({', '.join('"%s"' % c for c in cols)})"` 报 `SyntaxError: f-string: unterminated string`。改用 `%` 拼接：`"INSERT INTO kol (%s) VALUES (%s)" % (col_str, ph_str)`
2. **默认 protocol_version 是 HTTP/1.0**：urllib 请求会 `RemoteDisconnected`（但 curl / Node fetch 正常）。必须设 `protocol_version = "HTTP/1.1"`
3. **浏览器导航不自动带 Authorization header**：页面跳转（非 fetch）会 401 卡在登录页。改用 **Cookie 认证**（浏览器导航和 fetch 都自动带）
4. **JS 日期时区坑**：`new Date("2026-09-15T00:00:00").toISOString()` 在中国时区少一天。解析日期要用 `fmtLocalDate(d)`（getFullYear/getMonth/getDate 手动拼），不要用 toISOString().slice()
5. **SVG 环形图要「正」**：`rotate(-90deg)` 加在整个 `<svg>` 上会让文字也转歪。只加在圆弧 `<circle>` 上 + `transform-origin: 50% 50%`，文字保持正立
6. **下拉改自由输入**：用户要「所有选项可手动更改」→ 用 `<input list="xx-suggest">` + `<datalist>` 替代 `<select>`，既有建议又能输入任意值
7. **CSV 中文表头**：HEADER_ALIAS 映射表（中文名→字段名），导出带 BOM `\ufeff` 让 Excel 不乱码；导入支持 skip/overwrite 模式
8. **SQLite WAL 文件**：`*.db-shm`/`*.db-wal` 要加进 .gitignore，别提交
9. **进程"假活"诊断**：`ps aux | grep app.py` 显示进程在、但 curl 返回 `HTTP 000`（连接失败）→ 进程卡死（hang 住）。直接 `kill <pid>` 重启，别信 ps。排查顺序：curl 探活 → ps 确认 → kill → 重启
10. **Python urllib 不可用作浏览器等价测试**：urllib 有自身 header/keep-alive 坑（RemoteDisconnected）。测浏览器行为用 `node -e "fetch(...)"` 或 curl，不要用 urllib 的失败断言"前端坏了"

## 宽表格布局（用户偏好：不要挤，能滑就滑）
列数多（>14 列）的表格**默认用横向滑动布局**，不要硬塞：
- 容器 `.table-wrap { overflow-x: auto; }`，表 `min-width: 2000px`（列多时每列空间才够）
- 单元格 padding 至少 `13px 18px`，行高 `line-height: 1.6`，不要 10px 12px 那种挤法
- **首列 + 末列 sticky 固定**：`td.sticky-col { position: sticky; left: 0 }`（ID/红人ID 列）、`td.sticky-col-r { position: sticky; right: 0 }`（操作列），滑动时始终可见——用户明确好评
- 表头 `thead th { position: sticky; top: 0; z-index: 2 }` 固定
- 美化滚动条：`scrollbar-width: thin` + `::-webkit-scrollbar` 圆角滑块
- sticky 列的斑马纹/悬停背景要单独补（`tr:nth-child(even) td.sticky-col` 等），否则滚动时背景错位
- 用户原话（2026-08）：「既然可以滑动查看，就不要弄的太拥挤」——布局优先宽松，不追求一屏看全

## 局域网访问（同一 WiFi 另一台设备）
- `HOST = "0.0.0.0"` 监听所有网卡（默认 127.0.0.1 只能本机）
- 本机 IP：`ipconfig getifaddr en0`（macOS）
- `open_browser()` 里用 `http://127.0.0.1:{PORT}`（HOST 改 0.0.0.0 后不能直接用 HOST 拼 URL）
- macOS 防火墙关闭时无需放行端口；开启时需放行 python
- 启动横幅打印本机 + 局域网两个地址，方便用户转发

## launchd 守护（开机自启 + 崩溃自动重启，macOS）
长跑服务不要只靠 `start.sh`（会卡死无人管）。用 launchd：
- 守护脚本 `run_daemon.sh`：`exec /usr/bin/python3 app.py --no-browser`
- plist（放 `~/Library/LaunchAgents/com.<name>.app.plist`）：
  - `RunAtLoad=true` 开机自启
  - `KeepAlive` 字典 `{SuccessfulExit: false}` + `ThrottleInterval: 3` → 崩溃 3 秒后自动拉起
  - `StandardOutPath/StandardErrorPath` 指向 `logs/daemon.log` / `daemon.err.log`
- 命令：`launchctl load|unload ~/Library/LaunchAgents/com.<name>.app.plist`；`launchctl list | grep <name>` 看状态
- **验证崩溃自动重启**：`kill -9 $(pgrep -f "app.py")` → 等 5s → 新 PID 出现 + curl 200
- 服务卡死不再需要手动发现——launchd 自动拉起（2026-08 配置后用户再没报"系统怎么关了"）

## Claude 暖色 UI 风格（用户偏好，2026-08 确认）
用户对 Web 应用 UI 明确偏好 **Claude 风格**（Warm Humanist），不是深蓝科技：
- 背景 `#FAF9F5` 奶油白、侧边栏 `#F5F4ED`、卡片 `#FFFFFF`
- 主色橙棕 `#D97757`（深 `#C14B2A`）、文字暖黑 `#3D3929`、次要 `#7A7568`
- 成功 `#3A7D5C`、危险 `#B3452E`、警告 `#B5811F`、信息 `#5A7D9A`
- 标题衬线体（Georgia/Source Serif），正文无衬线；左侧边栏布局；胶囊标签；柔和阴影；圆角 6-14px
- 进度/统计用 **SVG 环形图**（三色分段：红逾期/黄今天/绿未来，从 12 点顺时针）
- 底部导航区可内嵌小工具（如 CPM 计算器）

## GitHub 自动备份
- `backup.sh`：git add -A → commit（时间戳）→ push；`.backup.lock` 防并发（10s 内合并连续操作）
- `app.py` 写操作后 `threading.Thread(target=auto_backup)` 异步触发，不阻塞请求
- **token 权限坑**：gh CLI 的 token 可能只有只读权限（创建仓库/推送都 403）。解决：从另一个有写权限仓库的 remote URL 里提取内嵌 PAT：
  ```bash
  git -C ~/.hermes remote get-url origin | sed -E 's|https://Leonardo-Chow:([^@]+)@.*|\1|'
  ```
  然后用 `https://Leonardo-Chow:<PAT>@github.com/<user>/<repo>.git` 作为 remote
- 仓库要建 **private**（数据含邮箱等敏感信息）

## 验证清单（交付前）
- curl 测 API：登录(错/对密码)、CRUD、搜索筛选、CSV 导入导出、回调
- 浏览器实测每页（登录→主页→列表→录入），检查 console 无 JS 错误
- 有异步备份时：写一条数据 → 等几秒 → GitHub API 查最新 commit 确认推送成功
- `python3 -c "import ast; ast.parse(open('app.py').read())"` 验证语法

## 支持文件
- `references/kol-manager.md` — KOL 管理系统实例细节（字段、产品目录、状态机、repo 信息）
