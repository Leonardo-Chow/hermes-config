# KOL 网红管理系统实例（~/kol-manager）

零依赖本地 Web 管理系统 v3.2+，按此 skill 架构实现。本文件记录实例特有细节，供迭代时快速还原。

## 基本信息
- 位置：`~/kol-manager`（app.py + webapp/ + start.sh + backup.sh + run_daemon.sh + kol.db）
- 端口 8787，登录 admin / admin123（settings 表 admin_username / admin_password）
- GitHub 私有仓库：`Leonardo-Chow/KOL-Manager`（自动备份，backup.sh 从 ~/.hermes remote 提取写权限 PAT）
- **守护方式**：launchd 服务 `com.kolmanager.app`（开机自启 + 崩溃自动重启）
  - 管理：`launchctl unload|load ~/Library/LaunchAgents/com.kolmanager.app.plist`
  - 日志：`~/kol-manager/logs/daemon.log` / `daemon.err.log`
  - 手动启动（临时）：`python3 app.py`（`--no-browser` 不自动开浏览器）
- **局域网**：HOST=0.0.0.0，本机 `http://127.0.0.1:8787`，局域网 `http://<ip>:8787`（`ipconfig getifaddr en0` 查 IP）

## 数据字段（FIELDS）
username(红人ID), name, platform, profile_url, email, followers, avg_views, product_model, product_launch, product_cost, cost, cpm, status, deal_date(合作日期), video_url(上线视频链接), video_views, video_likes, video_comments, next_remind, category, sub_category, source, added_date, notes

## 产品价格表（PRODUCT_PRICES，13款）
Meet 3:$199 / Talent 2:$2099 / Meet Flip:$99 / Tiny 3:$349 / Tiny 3 Lite:$199 / Tiny 2:$329 / Tiny 2 Lite:$179 / Tiny SE:$99 / Meet 2:$129 / Meet SE:$69 / Tail Air:$499 / Tail 2:$1199 / Talent:$1099

## CPM 公式
CPM = (合作费用 cost + 产品价格 product_cost) ÷ (均播 avg_views ÷ 1000)
- 填 product_model 自动带出成本价并算 CPM
- 前端 autoCpm() 实时算，后端 normalize_values/calc_cpm 兜底（含导入时）
- 侧边栏有独立 CPM 计算器（calcCpmSide()）

## 上市日期 → 提醒日期联动
- product_launch 填日期 → next_remind 自动 = 上市前 14 天（前端 autoRemind()）
- 时区坑：必须用 fmtLocalDate() 手动拼日期（getFullYear/getMonth/getDate），toISOString 在中国时区会少一天

## 合作状态机（六态）
建联中 / 已报价 / 价格不合理 / 确认合作 / 已完成代付款 / 合作结束
- Dashboard 映射：完成=已完成代付款+合作结束；确认合作=cooperating；已报价=quoted；建联/未定=建联中+价格不合理
- 邮件提醒只针对「确认合作」且 next_remind 非空
- 状态字段是可输入 datalist（用户要求所有选项可手动改）

## 当月合作（确认合作）
- 侧边栏导航「🤝 当月合作」→ `kol.html?status=确认合作`
- kol.html 的 handleStatusParam() 读 URL 参数：自动锁定状态筛选、改页面标题、高亮侧边栏该项
- 主页「当月合作」卡片只显示 status=确认合作 的红人（dashboard 返回 deals 列表）
- **Views 达标看板**：settings 表 `monthly_views_goal`（默认 1000000），环形显示 SUM(video_views of 确认合作) ÷ 目标
- 数据只存一份（红人表），主页看板/环形都从 dashboard API 聚合——不要建独立的数据表，避免两处不同步

## 页面结构
- login.html：用户名+密码（用户明确要求双字段、删密码提示）
- index.html：主页 — 统计卡片、三 SVG 环形图（完成进度 + 邮件提醒三色分段 + Views达标）、当月合作卡片、方向指引、发布需求卡片、邮件提醒列表、操作日志弹窗
- kol.html：红人管理表格（21列含上市日期/合作日期/视频数据）+ 工具栏筛选 + 编辑弹窗 + CSV 导入导出；**宽表格横向滑动 + 首列/末列 sticky**
- add.html：录入页大表单
- 侧边栏底部内嵌 CPM 计算器（合作费用+产品价格+均播 → 实时 CPM）

## 关键实现细节
- 操作日志：operation_log 表（ts/action/entity/entity_id/summary/before_json/after_json），回调需管理员密码，支持 create/update/delete 三类 rollback
- 发布需求：needs 表（title/content/platform/status/created_at）
- 认证：Set-Cookie kol_session，HttpOnly，服务端 check_auth 解析 Cookie（兼容 Bearer header）
- CSV：HEADER_ALIAS 中英映射，导出带 BOM，导入 skip/overwrite
- auto_backup()：写操作后异步线程跑 backup.sh；锁文件 .backup.lock 防并发

## 部署相关
- .gitignore：*.db-shm / *.db-wal / .backup.lock / __pycache__ / .DS_Store
- git remote 内嵌 PAT（从 ~/.hermes remote URL 提取），备份脚本每次 push 前重建 remote
- launchd plist：`~/kol-manager/com.kolmanager.app.plist`（源）→ `~/Library/LaunchAgents/`（生效）
