---
name: python-stdlib-webapp
description: 用 Python 标准库（http.server + sqlite3）构建零依赖本地网页应用（如 KOL 网红管理系统）。覆盖架构蓝图、cookie 认证、操作日志/回调、CSV 导入导出、关键坑位。当用户要求"本地跑一个网页版 XX 系统/工具"、要零依赖双击即用时使用。
---

# Python Stdlib Web App（零依赖本地网页应用）

用纯 Python 标准库（http.server + sqlite3 + csv + json）构建本地网页管理系统。**零 pip 依赖**，双击启动，数据存 SQLite 单文件。这是为小白用户搭建内部工具的首选路线（不装 Docker/Node/Postgres）。

## 何时用
- 用户要"本地网页版管理系统/工具"（KOL 管理、数据录入、看板、CRM…）
- 用户是小白，不想装任何环境；或数据敏感，要纯本地存储
- 单机单人使用，无需多用户并发
- 可参考成品：`~/kol-manager`（KOL 网红管理系统 v3.1，见 references/kol-manager.md）

## 工作流铁律（用户偏好，2026-08 明确要求）
1. **先讲设计思路**（技术选型、字段设计、功能范围、为什么这么选）
2. **问用户的设计思路**（他最常打开做什么、数据从哪来、字段缺不缺、界面偏好）
3. **对齐后再开跑** —— 不要一上来就闷头写代码。用户原话："你先说一下你的涉及思路，然后问一下我的涉及思路，最后再开始跑"

## 架构蓝图
```
kol-manager/
├─ app.py      # ThreadingHTTPServer + Handler(BaseHTTPRequestHandler)
├─ webapp/     # 静态 HTML/CSS/JS（index.html 主页 / 列表页 / 录入页 / login.html / style.css）
├─ kol.db      # SQLite 单文件（运行时生成）
└─ start.sh    # 一键启动：cd + open 浏览器 + python3 app.py
```
- `init_db()`：CREATE TABLE IF NOT EXISTS + **PRAGMA table_info 检查缺失列后 ALTER TABLE ADD COLUMN**（兼容旧库升级）
- settings 表（key/value）：月度目标、方向指引、管理员密码等
- 静态文件：`_serve_static()` 按路径返回，注意 `os.path.normpath` + 防 `..` 穿越
- 前端 API 调用统一封装 `api(url, opts)`，401 时跳 login

## 认证：Cookie 优于 Authorization header（关键教训）
- 用 `Authorization: Bearer` 时，**浏览器地址栏导航/刷新页面不会带 header**，只有 fetch 会带 → 页面跳转永远被弹回登录页
- 正确做法：登录成功 `Set-Cookie: kol_session=<token>; Path=/; HttpOnly; SameSite=Lax`，`check_auth()` 优先解析 Cookie、兼容 Authorization（双通道）
- 服务端 session 存内存 dict `{token: timestamp}`；登出时 Set-Cookie 清空
- 静态页面也要在 do_GET 里校验，未登录返回 `<meta http-equiv="refresh" content="0;url=/login.html">`

## 操作日志 + 回调（误操作恢复）
- operation_log 表：ts / action / entity / entity_id / summary / before_json / after_json
- 增删改、导入、回调都写日志；update 存 before+after 快照，delete 存 before，create 存 after
- rollback API：**必须验证管理员密码**（存 settings）→ create 则删行 / update 则还原 before / delete 则按原 id 重插
- 前端"操作日志"弹窗每条可回调，回调需输密码弹窗

## CSV 导入导出
- 导出：`csv.writer` + **`\ufeff` BOM 前缀**（Excel 打开中文不乱码）；`Content-Disposition: attachment`
- 导入：`csv.DictReader` 读内容，**表头中英文别名映射表**（如 红人ID/username → username）；username 查重，skip/overwrite 两模式
- 数字清洗：`parse_int` 处理 "1.2万"、"250,000"、"$500" 等

## 关键坑位（全部踩过）
1. **Python 3.9 f-string 不能嵌套同引号**：`f"...{', '.join('"%s"' % c for c in cols)}..."` 报 `SyntaxError: f-string: unterminated string`。修复：先拼 `col_str = ", ".join('"%s"' % c for c in cols)` 再 `%` 格式化。**3.9 里写 f-string 表达式内部不要用双引号字符串字面量。**
2. **BaseHTTPRequestHandler 默认 HTTP/1.0**：urllib/Node fetch 用 HTTP/1.1 keep-alive 请求时服务端无响应 → 客户端 `RemoteDisconnected`，而 curl 正常。修复：`protocol_version = "HTTP/1.1"`（urllib 仍可能失败是 Python urllib 特有 header 问题，**浏览器/Node fetch 不受影响**，别被它误导）。
3. **TEXT 字段排序按字符串**：`ORDER BY "cpm"` 会把 "16.67" 排在 "4.44" 前面。修复：数值字段用 `CAST("col" AS REAL)` 排序（INT/FLOAT 字段集合）。
4. **表单字段 id 映射 bug**：前端 `saveForm()` 用 FIELDS 数组遍历 `getElementById("f-" + f)`，但 platform/status 的输入框 id 带 `-input` 后缀（`f-platform-input`）→ 保存时取到 null。修复：统一 FIELD_IDS 映射表，或保证 input id 与字段名严格一致。**录入页漏掉任一字段的 input 会导致底部初始化 JS 抛异常、后续 loadXxx 全部不执行**（症状：下拉没数据）——加字段时必须同步检查 HTML 表单。
5. **`toISOString()` 时区差一天（中国时区）**：`new Date("2026-09-15T00:00:00").toISOString().slice(0,10)` 返回 `2026-09-14`（UTC+8 偏移）。做「上市日期 − 14 天 → 提醒日期」这类计算时，**不要用 toISOString**。正确：拆 `launch.split("-")` → `new Date(y, m-1, d)`（本地时区）→ `setDate(getDate()-14)` → 用 `getFullYear()/getMonth()+1/getDate()` 拼 `YYYY-MM-DD`（补零）。踩过：上市 09-15 算出提醒 08-31，实际应为 09-01。
6. **表格列多了别硬挤**：字段一多（20+ 列）用户要求「滑动查看、注意排版」，**且后续又反馈"太拥挤了"→ 方案要升级**：
   - v1：`.table-wrap{overflow-x:auto}` + `table{min-width:1280px}` + thead th `position:sticky; top:0`
   - **v2（用户嫌挤后）**：`table{min-width:2000px}`（列空间 +56%）、单元格 `padding:13px 18px`（别 10px 12px）、表头 `padding:14px 18px`、cell `max-width:320px`、`line-height:1.6`；**首列/末列也 sticky**（`td.sticky-col{position:sticky; left:0}`、`td.sticky-col-r{position:sticky; right:0; box-shadow:-4px 0 8px}`，表头同加，z-index 表头>单元格），横向滑动时红人ID/操作按钮始终可见；美化滚动条（`scrollbar-width:thin` + `::-webkit-scrollbar{height:10px}` + 圆角 thumb）
   - 验证：`wrap.scrollWidth > wrap.clientWidth` 且 `wrap.scrollLeft` 可改；sticky 列滑动后 `getBoundingClientRect().left` 仍 ≈ 容器左缘
   - 加列后记得同步 `colspan` 数值（列数变化容易漏）
   - 并列的卡片网格（如当月合作 deal-card）同样放大：padding 18-20px、gap 16px、minmax(320px,1fr)

## UI 风格（用户偏好）
- **个人/内部工具类 Web UI：默认 Claude 风格**（用户 2026-08 明确否定了深蓝科技风）——奶油底 `#FAF9F5`、橙棕主色 `#D97757`、衬线标题（Georgia/Source Serif）、左侧边栏 + 内容区、胶囊标签、柔和阴影
- 不要用 leonardo-brand 的深蓝科技主题做个人工具 UI（那是正式对外产物用的）
- 细节见 references/kol-manager.md 的 UI 部分

## SVG 环形进度（donut）——踩坑教训
用户要"环形显示更直观"，第一版把 `rotate(-90deg)` 加在整个 `<svg>` 上 → **中间百分比文字也跟着旋转，用户说"歪的"**。
- 正确做法：`rotate(-90deg)` 只加在**进度圆弧 circle** 上（`.ring-fg { transform: rotate(-90deg); transform-origin: 50% 50%; }`），让进度从 12 点起顺时针增长；SVG 整体和 `<text>` 保持正立。
- 半径 r=52 的圆周长 ≈ 326.73，`stroke-dasharray="326.73"` + `stroke-dashoffset = 326.73*(1-pct/100)`。
- **三色分段环**（如邮件提醒：逾期红/今天黄/未来绿）：多个 circle 叠放，各设 `stroke-dasharray="len 326.73"`；后续段用**负 offset** 位移起点：`segToday.offset = -CIRC*overdue/total`、`segFuture.offset = -CIRC*(overdue+today)/total`。中心大字 + 旁边图例统计。
- 双环布局：`.ring-cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}` 两个 `.ring-card` 并排。
- **达标看板环（数据来自聚合）**：如「本月 Views 总量达标」——`actual = SUM(video_views) WHERE status='确认合作'`、`goal` 存 settings（`monthly_views_goal`，默认 100 万），环形显示 `actual/goal`。目标可改：单独弹窗 + `POST /api/settings`；前端 `state.viewsGoal` 缓存，改完 `loadDashboard()` 重绘。中心文字 `fmtShort`（万/亿缩写）。三个环卡片用 `minmax(340px,1fr)` 自适应排布。

## "下拉建议 + 自由输入"（用户要求选项可手动更改）
用户：所有数据和选项要求可以手动更改。把 `<select>` 换成 `<input list="xxx-suggest">` + `<datalist>`：
- 平台/状态/产品型号全部如此；`<option value="预设值"></option>` 只做建议，用户可输入任意新值（如自定义平台「小红书」）
- 产品型号联动不变：`oninput="onProductChange()"` 匹配 `PRODUCTS[model]` 自动填价 → 算 CPM；`loadProducts()` 改为填充 datalist 的 `innerHTML` 而非 select 选项
- 后端不用改：TEXT 字段天然接受任意字符串，筛选器从 DB DISTINCT 取现有值

## 侧边栏内嵌小工具（如 CPM 计算器）
用户要在主页左侧放计算器（"CPM 计算逻辑和我前面告诉你的一样"）。做法：**侧边栏底部（操作日志/退出登录上方）放一个紧凑工具卡片**，比新开页面简单：
- `.sidebar-footer` 内插 `.cpm-box`：标题 + 3 个 `<input type=number>`（费用/产品价/均播）+ 结果 `<b>` + 公式说明小字
- 纯前端即时计算：`oninput="calcXxx()"`，结果 `(cost+prod)/(views/1000)` 保留 2 位；输入不全显示 `—`
- 侧边栏窄（224px），输入框全宽即可，别放表格
- 同款逻辑在录入页/编辑弹窗已有（autoCpm），复用公式，别改口径

## 日期联动：上市日期 → 自动提醒日期（提前 N 天）
用户：录入产品上市日期，自动设邮件提醒 = 上市前 2 周。做法：
- 表单加 `<input type="date" id="f-product_launch" onchange="autoRemind()">`；`autoRemind()` 算出提醒日期填入 `#f-next_remind`
- **日期计算严禁 toISOString**（坑 5）：拆 parts → `new Date(y,m-1,d)` → `setDate(getDate()-14)` → 手动拼 `YYYY-MM-DD`
- 提示用户：填完上市日期 toast「已自动设提醒: 上市前 2 周 <日期>」
- 业务字段（deal_date 合作日期 / video_url 视频链接 / video_views / video_likes / video_comments）一并加入 FIELDS + CSV 映射 + 表格列 + 编辑弹窗，用于当月合作看板的数据源（见下）

## 筛选视图 vs 独立页面（单数据源多入口）
用户要「当月合作（确认合作）」独立填写页。**判断：不建独立页，用 URL 参数筛选复用列表页**——视频数据本质是红人属性，独立页=复制数据、改一处另一处不同步。方案：
- 侧边栏入口 `href="/kol.html?status=确认合作"`
- 列表页 `handleStatusParam()`：读 URL `status` 参数 → **轮询等筛选下拉 `options.length>1`（loadFilters 异步填充）** → `sel.value=st` → 改标题/副标题提示该视图用途 → `loadKols()`
- 高亮侧边栏对应项：匹配 `a.getAttribute("href").includes("status=")`
- 数据只有一份，主页看板/列表/筛选视图天然一致（实测：改 video_views → Views 达标环自动重算）
- 多个入口（侧边栏各页共享同一 nav）都指向同一 URL 筛选，`active` class 由当前 URL 决定

## GitHub 自动备份（数据防丢失）
用户要求"上传 GitHub 防丢失，数据实时上传"。方案：
- **私有仓库**（`gh repo create --private`；用户数据不能进 public）
- `backup.sh`：`git add -A` → 有变更才 commit（`auto-backup: <ts>`）→ push；**防并发锁** `.backup.lock`（10 秒内重复调用直接跳过，合并连续写操作）
- `.gitignore` 必须排除 `*.db-shm` / `*.db-wal`（SQLite WAL 临时文件，每次运行都变，会污染提交）
- app.py 写操作后调 `auto_backup()`：`threading.Thread(target=..., daemon=True)` 异步跑 backup.sh，**不阻塞请求**；`KOL_BACKUP=0` 环境变量可关
- **验证闭环**：git clone 远端 → 打开 kol.db 查最新数据存在（别只看 commit 存在）
- 踩坑：gh CLI 的 token 可能是**只读的**（`gh repo create` 403、push 403）；恢复办法——从其他仓库的 remote URL 里捞**内嵌的写权限 PAT**：`git -C ~/.hermes remote get-url origin`（格式 `https://Leonardo-Chow:<PAT>@github.com/...`），用它建仓+push；backup.sh 每次自动提取该 PAT 拼 remote

## 验证清单
- 语法：`python3 -c "import ast; ast.parse(open('app.py').read())"`
- 全链路：curl 登录拿 cookie → 带 cookie 访问 API/页面 → 增删改 → 日志 → 回调（错误密码拒绝/正确密码恢复）→ 导出含 BOM
- 浏览器：登录跳转、各页面渲染、表单保存、搜索筛选
