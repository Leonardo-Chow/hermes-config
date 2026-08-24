# 实战案例：KOL 网红管理系统 v2.0（2026-08-03 建成）

部署位置：`~/kol-manager/`（app.py + webapp/{index,kol,add}.html + style.css + start.sh + README.md + kol.db）
端口：8787。启动：`./start.sh`（自动开浏览器）或 `python3 app.py`。

## 需求（来自用户口述）
1. 主页面：本月应合作多少红人 + 实际完成进度；邮件提醒（达成合作后定时发邮件问视频制作进度），与下次提醒时间联动
2. 数据手动录入，专门的录入页面，录入后统一在红人里可查
3. 红人管理表格：红人ID、主页、邮件、粉丝数量、均播、CPM、合作状态、合作费用、下次邮件提醒时间

## 数据库字段（FIELDS 顺序 = 表格列顺序）
username(红人ID), name(达人名称), profile_url(主页), email(邮件), followers(粉丝数量),
avg_views(均播), cpm(CPM), status(合作状态), cost(合作费用), next_remind(下次邮件提醒),
category(账号类别), sub_category(二级类目), source(来源博主), added_date(添加日期), notes(备注)

- INT_FIELDS = {followers, avg_views, cost}；FLOAT_FIELDS = {cpm}
- STATUS_LIST = ["待联系", "已联系", "合作中", "已合作"]
- settings 表存 monthly_goal（月度目标，默认 10）

## 核心业务逻辑
- **CPM 自动计算**：`cpm = cost / (avg_views / 1000)`，round 2 位；前端 autoCpm() 实时算，后端 normalize_values/calc_cpm 兜底（导入时若 cpm 为空也自动算）
- **Dashboard 进度**：`progress = done_total / monthly_goal * 100`；done_total = status='已合作' 的总数；done_month = 已合作且 added_date LIKE 'YYYY-MM%'
- **邮件提醒联动**：`next_remind != '' AND status IN ('合作中','已合作')` 按日期升序；remind_state = overdue(<今天) / today(==今天) / upcoming(>今天)；主页逾期标红🔴、今天标黄🟡、未来绿🟢
- **发邮件**：`mailto:` 链接预填主题+正文模板（进度询问：脚本/拍摄/剪辑/已完成 + 预计出片时间），点按钮打开邮件客户端——零配置方案，优于真 SMTP（用户没配时别硬上 SMTP）
- **录入页校验**：状态为合作中/已合作时必须填 next_remind（否则 toast 拦截提示）

## 三页面结构
- `/` Dashboard：统计卡片（目标/已合作/合作中/待跟进提醒）+ 进度条 + 提醒列表 + 红人库概览；编辑目标弹窗 → POST /api/settings
- `/kol.html` 红人管理：搜索(全文本字段 LIKE) + 筛选(状态/类别/来源/粉丝范围) + 13 列排序表格 + 编辑/复制/删除 + CSV 导入导出；支持 `?edit=<id>` URL 参数从主页跳转打开编辑
- `/add.html` 录入页：独立大表单，保存后自动填最近 category/source 方便连续录入

## API 一览
GET  /api/dashboard（目标/进度/提醒+counts/总粉丝）、/api/kols（分页搜索筛选排序）、/api/kols/<id>、/api/stats、/api/filters、/api/reminders、/api/settings、/api/kols/export
POST /api/kols、/api/kols/import（skip|overwrite）、/api/kols/<id>/duplicate、/api/settings
PUT  /api/kols/<id>（不传 cpm 但传 cost/avg_views 时自动重算）、DELETE /api/kols/<id>

## CSV 导入表头别名（中文/英文都认）
红人ID/用户名/username, 主页/profile_url, 邮件/email, 粉丝数量/followers, 均播/avg_views,
CPM/cpm, 合作状态/status, 合作费用/cost, 下次邮件提醒/next_remind, 账号类别/category,
二级类目/sub_category, 来源博主/source, 添加日期/added_date, 备注/notes

## 踩坑记录（本次实际遇到）
- 3 处 f-string 嵌套双引号 SyntaxError（api_create/api_duplicate/api_import 三处 INSERT）→ 全部改 `%` 拼接
- urllib 测 POST /api/kols/import 报 RemoteDisconnected，curl/Node fetch 正常 → 设 protocol_version="HTTP/1.1" 后 curl 通过；urllib 的 header 行为仍不可靠，验证一律用 curl/Node
- add.html 表单漏了 added_date 输入框（FIELDS 里有）→ 保存报 null 错误
- kol.html 保存后 category/source 为空 → 前端 saveForm 读 `f-category` 但 input 实际 id 是 `f-category-input`（datalist 后缀）→ FIELD_IDS 映射修复
- cpm 按 TEXT 字符串排序错乱（16.67 < 4.44）→ `ORDER BY CAST("cpm" AS REAL) DESC`
- Dashboard 总粉丝显示 "-" → api_dashboard 漏返回 total_followers
