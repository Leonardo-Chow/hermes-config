# KOL 网红管理系统 v3.x — 演进实录

实战系统：`~/kol-manager`（本地，端口 8787，默认 admin/admin123）。
GitHub 私有仓库：`Leonardo-Chow/KOL-Manager`（每次写操作自动 commit+push）。

## 最终字段（FIELDS 顺序）
username, name, platform, profile_url, email, followers, avg_views,
product_model, product_launch, product_cost, cost, cpm, status,
deal_date, video_url, video_views, video_likes, video_comments,
next_remind, category, sub_category, source, added_date, notes

## 业务常量
- 合作状态六态：建联中 / 已报价 / 价格不合理 / 确认合作 / 已完成代付款 / 合作结束
- 平台：YouTube / Instagram / Twitch / X(Twitter) / TikTok / Bilibili / Facebook / 其他（可自由输入）
- 产品价格表（选择产品自动带出成本价）：
  Meet 3=$199, Talent 2=$2099, Meet Flip=$99, Tiny 3=$349, Tiny 3 Lite=$199,
  Tiny 2=$329, Tiny 2 Lite=$179, Tiny SE=$99, Meet 2=$129, Meet SE=$69,
  Tail Air=$499, Tail 2=$1199, Talent=$1099
- CPM 公式：CPM = (合作费用 cost + 产品价格 product_cost) ÷ (均播 avg_views ÷ 1000)，后端兜底自动算

## Dashboard 聚合映射（关键！）
- 完成 done = status IN ('已完成代付款','合作结束') → 完成进度环形
- 合作中 cooperating = status='确认合作'（需跟进视频）
- 已报价 quoted = status='已报价'
- 建联/未定 pending = status IN ('建联中','价格不合理')
- 邮件提醒 reminders = status='确认合作' AND next_remind != ''（按日期排序，overdue/today/upcoming）
- Views 达标 = SUM(video_views) WHERE status='确认合作' ÷ monthly_views_goal（settings 可改，默认 1000000）
- 当月合作 deals = 确认合作红人完整列表（含 video_url/video_views/video_likes/video_comments）

## 页面结构
- login.html：用户名+密码（admin_username / admin_password 存 settings）
- index.html：侧边栏（导航 + CPM 计算器 + 操作日志/退出）+ 统计卡 + 3 个环形卡（完成进度 / 邮件提醒三色分段 / Views 达标）+ 当月合作看板（确认合作红人卡片：Views/点赞/评论/看视频/填数据）+ 方向指引 + 发布需求 + 邮件提醒列表 + 红人库概览
- kol.html：21 列可横向滑动表格（min-width 1280px, overflow-x auto, thead sticky）+ 筛选/排序/编辑弹窗
- add.html：录入大表单，上市日期→自动提醒（提前14天，本地日期计算）

## 后端 API
/api/login（POST, username+password, Set-Cookie）、/api/logout、/api/dashboard（含 deals/views_progress）、
/api/kols CRUD + /api/kols/export + /api/kols/import、/api/kols/<id>/duplicate、
/api/products（产品表）、/api/needs CRUD、/api/logs、/api/rollback（需管理员密码）、
/api/direction、/api/settings（monthly_goal / monthly_views_goal / admin_username）、/api/filters

## 操作日志 + 回调
- operation_log 表：ts/action(entity)/entity_id/summary/before_json/after_json
- 回调：create→删除该行；update→按 before 还原；delete→按 before 恢复（带 id）
- 回调必须校验管理员密码（verify_password）；回调本身也记一条 rollback 日志

## 验证要点（实测通过）
- 日期联动：上市 2026-09-15 → 提醒 2026-09-01（-14 天，本地日期；toISOString 会差一天）
- CPM：Talent 2 场景 $2000+$2099÷50万=$8.20；Tiny 3 Lite $500+$199÷10万=$6.99
- Views 达标环形：改目标 100万→150万，环形 75%→50%
- 三色邮件环：overdue/today/future 三个 circle，dasharray 按比例 + 负 offset 错开
