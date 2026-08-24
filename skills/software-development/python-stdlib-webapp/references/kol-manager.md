# KOL 网红管理系统（~/kol-manager）— 参考实现

零依赖 Python + SQLite 本地网页应用成品。路径 `~/kol-manager`，端口 8787，启动：`./start.sh` 或 `python3 app.py --no-browser`。
登录：用户名 `admin` / 密码 `admin123`（存 settings 表 `admin_username` / `admin_password`）。**密码提示已从登录页删除**（用户要求）。

## 版本沿革（用户需求驱动）
- v1.0: 基础 KOL 表格增删改查 + 搜索筛选 + CSV 导入导出
- v2.0: 主页 Dashboard（月度目标进度条 + 邮件提醒联动）、独立录入页、合作状态/CPM/费用字段
- v3.0: 平台下拉 + 产品价格联动 CPM + 登录认证 + 操作日志/回调 + 方向指引/发布需求模块
- v3.1: UI 全面重做为 Claude 风格（用户否决深蓝科技风后）
- v3.2: **环形进度 SVG**（含邮件提醒三色分段环）+ 所有选项改 datalist 自由输入 + 合作状态六态 + 登录用户名+密码 + **GitHub 私有仓库自动备份**
- v3.3: **产品上市日期**（填后自动算提醒 = 上市前 14 天，修正 toISOString 时区差一天）+ 侧边栏 **CPM 计算器**
- v3.4: **合作日期/上线视频链接/视频Views/点赞/评论** 字段 + 表格横向滑动布局（overflow-x + min-width:1280px + sticky 表头）+ **当月合作筛选视图**（侧边栏「🤝 当月合作」→ `/kol.html?status=确认合作` 复用列表页编辑视频数据）+ **本月 Views 总量达标环**（SUM(video_views) WHERE 确认合作 ÷ monthly_views_goal，可改目标）

## 数据表
- **kol**: id, username(红人ID), name, platform, profile_url, email, followers, avg_views, product_model, product_launch(上市日期), product_cost, cost, cpm, status, deal_date(合作日期), video_url, video_views, video_likes, video_comments, next_remind, category, sub_category, source, added_date, notes
- **settings**: monthly_goal, monthly_views_goal(默认1000000), monthly_direction, admin_username, admin_password
- **operation_log**: ts, action(create/update/delete/import/rollback), entity, entity_id, summary, before_json, after_json
- **needs**: title, content, platform, status(待发布/已发布/已完成), created_at

## 合作状态六态（v3.2 取代旧四态 待联系/已联系/合作中/已合作）
`建联中 → 已报价 → 价格不合理 → 确认合作 → 已完成代付款 → 合作结束`
Dashboard 映射：
- 完成（done_total/done_month/progress）= `已完成代付款` + `合作结束`
- 确认合作（cooperating）= `确认合作`；已报价（quoted）= `已报价`
- 推进中（contacted）= `已报价` + `确认合作`；建联/未定（pending）= `建联中` + `价格不合理`
- **邮件提醒只对 `确认合作`**（需跟进视频进度），其他状态即使有 next_remind 也不进提醒列表

## 关键公式
- **CPM = (合作费用 + 产品价格) ÷ (均播 ÷ 1000)**，自动算可手改
- 产品型号（datalist 建议 + 自由输入）→ 选中自动填 product_cost → 自动算 CPM
  PRODUCT_PRICES = {Meet 3:199, Talent 2:2099, Meet Flip:99, Tiny 3:349, Tiny 3 Lite:199, Tiny 2:329, Tiny 2 Lite:179, Tiny SE:99, Meet 2:129, Meet SE:69, Tail Air:499, Tail 2:1199, Talent:1099}
- 月度进度 = 状态 `已完成代付款`+`合作结束` 红人数 ÷ monthly_goal（环形图）
- **Views 达标环** = SUM(video_views) WHERE status='确认合作' ÷ monthly_views_goal（settings，默认 100 万，弹窗可改 → POST /api/settings）
- **上市日期 → 提醒** = product_launch − 14 天 → next_remind（前端 autoRemind()，本地时区计算，勿用 toISOString）

## 当月合作（确认合作）筛选视图
- 侧边栏「🤝 当月合作」= `/kol.html?status=确认合作` → handleStatusParam() 轮询等筛选下拉加载后锁定状态、改标题为「当月合作（确认合作）」、高亮侧边栏
- 在该视图直接点 ✏️ 编辑填 video_url/video_views/video_likes/video_comments/deal_date
- 主页「🤝 当月合作」卡片板 + Views 达标环都读同一份数据，改一处全联动

## API 一览（除 login 外全部需认证；login 需 username+password）
- POST /api/login, /api/logout, /api/kols, /api/kols/import, /api/settings, /api/direction, /api/needs, /api/rollback, /api/kols/{id}/duplicate
- GET /api/dashboard, /api/kols(+筛选/排序/分页), /api/kols/{id}, /api/kols/export, /api/filters, /api/products, /api/needs, /api/logs, /api/stats, /api/settings
- PUT /api/kols/{id}（自动重算 CPM）, DELETE /api/kols/{id}, /api/needs/{id}

## 邮件提醒联动（v3.2 更新）
- 状态「确认合作」+ next_remind 有值 → 主页提醒列表按日期排序
- remind_state: overdue(逾期红) / today(今天黄) / upcoming(未来绿)
- 主页右侧新增**邮件提醒三色环形**：逾期红段 → 今天黄段 → 未来绿段，中心=需跟进数(逾期+今天)
- 「发邮件」= mailto: 打开邮件客户端 + 预填进度询问模板（未接真 SMTP）

## Claude 风格 UI 配方（style.css）
```
--bg:#FAF9F5  --bg-sidebar:#F5F4ED  --surface:#FFFFFF
--border:#E8E6DD  --text:#3D3929  --text-secondary:#7A7568
--accent:#D97757  --accent-dark:#C14B2A  --accent-light:#FAF1EC
--success:#3A7D5C  --danger:#B3452E  --warning:#B5811F  --info:#5A7D9A
--serif: Georgia,'Source Serif 4',serif（标题/大数字）
--sans: -apple-system,'Inter','PingFang SC'（正文）
```
布局：`.app{display:flex}` → 左侧 `.sidebar`（224px, sticky, logo+导航+底部退出）+ `.main`（page-bar 标题区 + content）。状态标签用胶囊形 `border-radius:999px`，卡片 `border-radius:10px`，`box-shadow:0 1px 3px rgba(61,57,41,.06)`。避免 emoji 堆砌、紫渐变、冷蓝科技感。

## GitHub 自动备份（v3.2）
- 私有仓库 `Leonardo-Chow/KOL-Manager`；每次写操作后 `auto_backup()` 异步跑 `backup.sh` 自动 commit+push
- 写权限 PAT 从 `~/.hermes` remote URL 提取（gh CLI token 只读 403，不能建仓/push）
- `.gitignore` 排除 `*.db-shm`/`*.db-wal`；`.backup.lock` 防并发

## 用户偏好备注
- 设计先行：先讲设计思路 → 问用户想法 → 再写代码
- 任务要连续执行不要停；做完全量测试再汇报
- 误操作恢复（回调）是用户明确要的能力，操作日志是标配
- 用户对环形图要求"正的"——rotate 只能加在圆弧上，文字必须正立
- 登录要用户名+密码双字段，不要显示默认密码提示
