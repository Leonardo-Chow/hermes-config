---
name: python-local-webapp
description: 用纯 Python 标准库 + SQLite 构建零依赖本地网页工具（管理后台、数据库界面、Dashboard）。当用户（尤其非技术小白）要"本地跑一个网页版 XX 系统/工具"、要求零安装双击即用、数据存本地时使用。涵盖 ThreadingHTTPServer 架构、CRUD API、登录认证、操作日志/误操作回调、中文 CSV 导入导出，以及 Python 3.9 与 stdlib http.server 的系列坑。
---

# Python Local Web App (零依赖本地网页工具)

## 何时用
- 用户（通常是非技术小白）说「本地跑一个网页版 X 管理系统 / 工具 / 数据库界面」
- 要求零依赖、零安装、双击即用、数据存本地单文件
- 需要增删改查 + 搜索筛选 + CSV 导入导出 + 统计面板
- 对比结论：GitHub 开源同类项目要么要 Docker/Postgres（小白劝退）、要么偏撮合平台不贴合需求 → 自建轻量版常是最优解（先快速搜一下开源，再决定）

## 用户工作流偏好（重要）
Leonardo 明确要求此类任务：**先说你的设计思路 → 问他的设计思路 → 再开始跑**。
- 动手前先讲清楚：技术选型为什么、字段怎么设计、页面结构、核心交互
- 用 clarify 问他的想法（他可能给新字段/新页面/新模块），确认后再写代码
- 不要闷头做完再汇报——先对齐设计再执行
- 用户连续执行偏好依然适用：对齐之后一路做完，不要中途停下来等确认

## 架构（已验证的骨架）
```
~/项目名/
├─ app.py          # 后端：ThreadingHTTPServer + SQLite（全部标准库）
├─ start.sh        # 一键启动：cd dir + (sleep 1.5 && open http://127.0.0.1:PORT) & + python3 app.py
├─ README.md       # 小白向说明：启动/字段/CSV格式/备份
├─ kol.db          # SQLite 单文件（备份=复制此文件）
└─ webapp/         # 静态前端：index.html / list.html / add.html / login.html / style.css
```

- `HOST = "127.0.0.1"` 仅本机；想局域网访问改 `"0.0.0.0"`（README 写清楚）
- `PORT = int(os.environ.get("KOL_PORT", "8787"))` 支持换端口
- DB：`sqlite3.connect` + `row_factory = sqlite3.Row` + `PRAGMA journal_mode=WAL`（ThreadingHTTPServer 并发访问需要）
- init_db 用 `PRAGMA table_info` 检查缺失列 + `ALTER TABLE ADD COLUMN` 做旧库兼容迁移
- 所有 JSON 响应 `ensure_ascii=False`（中文必加）

## 后端 API 模式
- 列表：`build_where(params)` 拼 WHERE（search 走 LIKE 多字段 OR、精确筛选、数字范围）+ `fetch_kols` 分页
- `clean_row()`：INT/FLOAT 字段统一 `int(float(str(x or 0)))` 兜底，避免空串/None 崩溃
- CPM 类计算字段：后端保存时自动算（若未显式传），导入时也算，保证数据一致
- CSV 导出：`"\ufeff" + csv`（BOM 让 Excel 直接打开不乱码）
- CSV 导入：`HEADER_ALIAS` 字典把中文表头（红人ID/粉丝数量/产品价格…）映射到英文字段，`csv.DictReader` 逐行，重复 username 按 mode skip/overwrite
- 操作日志：`operation_log` 表（ts/action/entity/entity_id/summary/before_json/after_json），增删改都写 before/after 快照 → 实现**误操作回调**（rollback 时按 action 恢复：delete→重插、update→还原 before、create→删除）。回调需验证管理员密码。
- settings 表（key/value）存月度目标、密码、方向指引等

## 登录认证（关键坑）
**必须用 Cookie，不能只靠 Authorization header。**
- 浏览器导航（地址栏/链接跳转）不会自动带 `Authorization: Bearer`，只有 fetch/XHR 会 → 纯 header 认证会导致登录后跳转仍被拦截
- 正确做法：登录成功 `Set-Cookie: kol_session=<token>; Path=/; HttpOnly; SameSite=Lax`，`check_auth` 优先正则从 `Cookie` 头取 token，兼容 Authorization（curl 测试方便）
- 静态页面也要认证：未登录返回 `<meta http-equiv="refresh" content="0;url=/login.html">`
- API 未认证返回 401；前端 `api()` 统一处理 401 → 跳登录页
- 密码存 settings 表，默认 `admin123`，README 写修改命令
- session 存内存 dict（重启失效，本地单机够用）

## 前端模式
- 单页多文件（index/list/add/login 各一个 html + 共享 style.css），顶部导航切换
- 三个页面共用一个 `api()` 封装（带 cookie/header + 401 跳转 + 错误提取）
- 表单字段 ID 统一：**用一张 `FIELD_IDS` 映射表**（如 `category: "f-category-input"`），saveForm/openForm 都从映射表取 id——否则填了存不进去（字段 ID 不一致 bug）或 saveForm 读 null 崩溃（HTML 漏了某个输入框，FIELDS 列表却包含它）
- **顶层 init JS 一行抛错 = 后续初始化全挂（静默）**：页面底部 `document.getElementById("f-added_date").value=...` 之类顶层语句，若元素不存在（HTML 漏写该字段）抛 TypeError，会中断其后所有 `loadFilters()/loadProducts()` 等初始化，现象是"某下拉/某数据没加载"且 JS 错误只在 console 有 1 条空 message。修复：init 调用包 try/catch，或每个 getElementById 前判空；排查时先 `!!document.getElementById('f-xxx')` 逐个验证表单字段是否齐全。
- **产品目录联动模式**（选择产品→自动带价→自动算 CPM 类指标）：后端 `PRODUCT_PRICES` 字典（型号→价格）+ `GET /api/products` 返回 `[{model,cost}]`；前端 `loadProducts()` 渲染下拉（option 文案带价 `Talent 2 ($2099)`）+ `onProductChange()` 选中后自动填价格输入框再调 `autoCpm()`；后端 save/import 也用同一字典兜底算。改价/加新品只动后端字典一处。
- 数值自动计算（如 CPM）在前端 oninput 实时算 + 后端兜底算
- 空状态/加载中/错误状态都要有

## 已验证的坑（Python 3.9 / stdlib http.server）
1. **Python 3.9 f-string 不能嵌套双引号**：`f"...{', '.join('"%s"' % c ...)}..."` 直接 SyntaxError。改用普通 `%` 拼接或先算好变量再 f-string。
2. **Handler 必须设 `protocol_version = "HTTP/1.1"`**：默认 HTTP/1.0 响应会让 urllib 客户端 RemoteDisconnected。
3. **验证客户端用 curl 或 Node fetch，不要用 Python urllib**：urllib 发的请求头（即使服务端已设 HTTP/1.1）仍会触发 stdlib http.server 连接被关闭（RemoteDisconnected），而 curl、http.client、Node fetch 全部正常。Node fetch（`node -e`）与浏览器 fetch 同源，是前端行为的最佳代理。urllib 报 RemoteDisconnected 时先怀疑 urllib 本身，不是服务端。
4. **TEXT 列排序是字符串序**：`"16.67" < "4.44" < "5.0"`。数值字段排序必须 `ORDER BY CAST("col" AS REAL) DESC`。建 `numeric_sorts = set(INT_FIELDS)|set(FLOAT_FIELDS)` 统一处理。
5. **数字字段存 TEXT**：SQLite 无类型，全部当 TEXT 存，读写时 parse/clean 兜底。
6. **modal 用 browser_click 模拟可能不稳定**：自动化测试时用 browser_console 直接调 `saveForm()` 更可靠；用户真实点击不受影响（首次点击没生效是时序，不是 bug）。
7. **筛选下拉用 `select` + JS 直接赋值再 `loadKols()`**：测试时 browser 点 option 常报 box model 错误，JS 赋值绕过。
8. **给被其他进程调用的脚本加 CLI 参数必须注册进 argparse**：手动 `sys.argv` 读参数不够——argparse 解析到未注册参数直接 error exit，调用方（如 .app 壳）只见进程静默死亡。新参数一律 `ap.add_argument(...)`。典型场景：加 `--root`/`--port` 让服务可被打包进 macOS App 后重定位静态目录。

## 验证清单（交付前）
- [ ] `python3 -c "import ast; ast.parse(open('app.py').read())"` 语法检查
- [ ] curl 全 API 冒烟：未登录 401 → 登录拿 cookie → 带 cookie CRUD/搜索/筛选/排序/导入导出/日志/回调
- [ ] 排序验证：数值字段降序结果正确（TEXT 列 CAST 后）
- [ ] CPM 类计算：手动算一遍期望值对拍
- [ ] 回调：删除→错误密码拒绝→正确密码恢复，数据完整
- [ ] Node fetch 测导入（模拟浏览器 fetch）
- [ ] 浏览器走一遍：登录→主页→列表→录入→搜索筛选→日志
- [ ] README 更新到当前版本号

## 参考
- `references/kol-manager-instance.md` — 本技能产出的实例：KOL 网红管理系统 v3（字段表、API 清单、认证流程、页面结构），作为下一次同类任务的起点模板
