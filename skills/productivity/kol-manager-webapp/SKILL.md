---
name: kol-manager-webapp
description: KOL 网红管理系统（~/kol-manager）—— 本地零依赖 Python 标准库 + SQLite 单文件网页应用。当用户提到 KOL 管理系统、网红管理、录入红人、CPM、产品价格联动、环形进度、操作日志回调、GitHub 自动备份、登录页、Claude 风格 UI 时加载。也适用于"本地零依赖网页应用"这类任务（http.server + sqlite3 + 原生前端）。
---

# KOL 网红管理系统（本地零依赖网页应用）

用户 Leonardo 的本地网红管理工具，位于 `~/kol-manager`。技术栈：**纯 Python 标准库**（`http.server` + `sqlite3` + `subprocess`），零第三方依赖，SQLite 单文件 `kol.db`，前端原生 HTML/CSS/JS（Claude 风格设计）。

## 快速操作

```bash
cd ~/kol-manager && ./start.sh          # 启动（自动开浏览器）
cd ~/kol-manager && python3 app.py --no-browser   # 后台/无浏览器启动
# 登录：用户名 admin / 密码 admin123（存在 settings 表 admin_username/admin_password）
# 停止：Ctrl+C；数据自动保存 + 自动备份推送
```

- 端口 8787（`KOL_PORT=9000` 可换）；局域网访问需把 `HOST` 改为 `0.0.0.0`
- 结构：`app.py`（后端全部逻辑）、`webapp/`（index.html 主页 / kol.html 红人管理 / add.html 录入 / login.html / style.css）、`backup.sh`、`kol.db`、`start.sh`
- 可复用的"本地零依赖网页应用"通用模式见 `references/local-webapp-pattern.md`（骨架/后端要点/前端要点/3.9 陷阱/常见坑）

## 数据模型（kol 表字段，顺序即 CSV 导出表头）

`username(红人ID) name platform profile_url email followers avg_views product_model product_cost cost cpm status next_remind category sub_category source added_date notes`

- 数值字段 `INT_FIELDS`：followers/avg_views/product_cost/cost；`FLOAT_FIELDS`：cpm
- 合作状态六态：**建联中 / 已报价 / 价格不合理 / 确认合作 / 已完成代付款 / 合作结束**（`STATUS_LIST`）
  - Dashboard 映射：完成=已完成代付款+合作结束；确认合作=cooperating；已报价=quoted；建联/未定=建联中+价格不合理
  - 邮件提醒只看 `status='确认合作'` 且有 next_remind
- 平台 `PLATFORM_LIST`：YouTube/Instagram/Twitch/X(Twitter)/TikTok/Bilibili/Facebook/其他
- 产品价格表 `PRODUCT_PRICES`（13 款 OBSBOT）：Meet 3=$199, Talent 2=$2099, Meet Flip=$99, Tiny 3=$349, Tiny 3 Lite=$199, Tiny 2=$329, Tiny 2 Lite=$179, Tiny SE=$99, Meet 2=$129, Meet SE=$69, Tail Air=$499, Tail 2=$1199, Talent=$1099
- **CPM = (cost + product_cost) ÷ (avg_views ÷ 1000)**，选产品型号自动带出价格再算
- 其他表：`settings`(monthly_goal/admin_password/admin_username/monthly_direction)、`operation_log`、`needs`(发布需求)

## 核心功能

1. **主页 Dashboard**：环形进度（SVG donut，`.ring-fg` stroke-dashoffset，周长 CIRC=326.73）+ 分布统计 + 方向指引 + 发布需求卡片 + 邮件提醒（逾期红/今天黄/未来绿，mailto 预填模板）
2. **红人管理**：搜索/筛选（平台/状态/类别/粉丝范围）/排序（数值字段 CAST 排序）/编辑/复制/删除/CSV 导入导出（中英表头 HEADER_ALIAS 映射）
3. **操作日志 + 回调**：所有增删改写 `operation_log`（before/after JSON 快照），`/api/rollback` 需管理员密码，支持 kol/need 的 create/update/delete 反向恢复
4. **登录认证**：用户名+密码 → Set-Cookie `kol_session`（HttpOnly），cookie 优先、Authorization header 兼容

## GitHub 自动备份（重要）

- 私有仓库 `Leonardo-Chow/KOL-Manager`，每次写操作（create/update/delete/import/rollback/needs/settings）后 `auto_backup()` 异步调 `backup.sh`
- **关键坑**：`gh auth` 的 token 只有只读权限（创建仓库/推送均 403，"Resource not accessible by personal access token"）；**写权限 PAT 内嵌在 `~/.hermes` 的 git remote URL 里**（`https://Leonardo-Chow:ghp_xxx@github.com/...`）。`backup.sh` 用 `git -C ~/.hermes remote get-url origin | sed -E 's|https://Leonardo-Chow:([^@]+)@.*|\1|'` 提取复用。不要用 gh CLI 创建/推送。
- 建新仓库流程：先提取旧 PAT → `curl -X POST https://api.github.com/user/repos` 建 private 仓库 → `git remote add origin https://Leonardo-Chow:${PAT}@github.com/...` → push
- `.gitignore` 必须忽略 `*.db-shm` `*.db-wal`（SQLite WAL 临时文件，否则每次都在变导致备份刷屏）

## 修改字段/加新功能的步骤

加字段要五处同步，漏一处就出 bug：
1. `app.py` 的 `FIELDS` 元组（位置=导出表头顺序）
2. `HEADER_ALIAS`（CSV 中英表头映射）
3. `webapp/kol.html` 和 `add.html` 的 JS `FIELDS` 数组 + HTML 表单 `<input id="f-xxx">`
4. `init_db()` 有 ALTER TABLE 兼容旧库，无需手动迁移
5. 需要可筛选就在 `build_where`/`api_filters` 加对应字段

## Pitfalls（踩过的坑）

- **Python 3.9 f-string 不能嵌套同引号**：`f"...{', '.join('"%s"' % c ...)}..."` 会 SyntaxError "f-string: unterminated string"（3.12 才放开）。用 `"%s" % (...)` 拼接或引号错开。
- **http.server 必须设 `protocol_version = "HTTP/1.1"`**：默认 HTTP/1.0 会导致 Python `urllib`/`http.client` 客户端 RemoteDisconnected（curl/Node fetch 正常）。class 里加 `protocol_version = "HTTP/1.1"`。
- **页面导航认证必须用 cookie**：`Authorization` header 只在 fetch 时带上，浏览器地址栏导航/刷新不带 header → 已登录也会被 401 踢回登录页。登录接口 `Set-Cookie`，`check_auth()` 先查 Cookie 再兼容 header。
- **下拉可手动输入用 datalist**：`<input list="xxx-suggest">` + `<datalist>`，用户要求"所有数据可手动更改"，不要用死 `<select>`。产品/平台/状态全部 input+datalist。
- **HTML 表单缺 id 会静默炸掉页面 JS**：页面底部初始化代码 `document.getElementById("f-xxx").value=...` 若元素不存在抛 TypeError，后续 loadFilters/loadProducts 全不执行（表现为下拉是空的）。改表单后检查每个 FIELDS 都有对应 input。
- **`urllib` 发 JSON 的坑**：Python 3.9 urllib 对该服务发送带 body 的 POST 偶尔 RemoteDisconnected，curl/Node fetch 正常 → 测试优先用 curl/Node，别用 urllib 判断服务端 bug。
- **筛选值包含空格/中文**：URL 参数用 `urllib.parse`，前端 `qs()` 用 `URLSearchParams`。
- **状态/字段文案改版后要全局搜旧词**：改六态时残留的"合作中/已合作/待联系"文案会误导（用 search_files 全目录搜）。

## UI 规范（用户明确偏好）

- **Claude 风格**：奶油底 `#FAF9F5`、橙棕主色 `#D97757`（hover `#C14B2A`）、暖黑文字 `#3D3929`、衬线标题（Georgia/Source Serif）、左侧边栏布局、胶囊标签、柔和阴影。
- 用户明确拒绝深蓝科技主题（leonardo-brand 的默认暗色系只用于报告/PPT/PDF，网页应用用 Claude 风格）。
- 参考 skill：`web-design-engineer`（设计流程/避免俗套）、`leonardo-brand`（品牌色板，网页 UI 例外）。
