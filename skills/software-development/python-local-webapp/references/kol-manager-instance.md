# 参考实例：KOL 网红管理系统 v3（~/kol-manager）

本技能产出的具体实例，作为同类「零依赖本地网页工具」的起点模板。

## 项目位置
- 路径：`~/kol-manager/`（app.py + start.sh + README.md + kol.db + webapp/）
- 启动：`./start.sh` 或 `python3 app.py --no-browser`，端口 8787
- 登录：默认密码 `admin123`（存 settings 表 admin_password key）
- 当前版本 v3.x：平台字段 + **产品型号下拉联动（13 款 OBSBOT 产品价目表）** + CPM 含产品价 + 登录 + 操作日志/回调 + 方向指引 + 发布需求

## 数据模型（kol 表字段）
```
id INTEGER PK, username(红人ID), name(达人名称), platform(平台),
profile_url(主页), email(邮件), followers(粉丝数量), avg_views(均播),
product_model(产品型号), product_cost(产品价格), cost(合作费用), cpm(CPM),
status(合作状态), next_remind(下次邮件提醒), category(账号类别),
sub_category(二级类目), source(来源博主), added_date(添加日期), notes(备注)
```
- 全部存 TEXT，数值字段读写时 parse/clean
- 其他表：settings(key,value)、operation_log(id,ts,action,entity,entity_id,summary,before_json,after_json)、needs(id,title,content,platform,status,created_at)

## 产品价目表（PRODUCT_PRICES in app.py，13 款）
| 型号 | 成本价 | 型号 | 成本价 |
|---|---|---|---|
| Meet 3 | $199 | Tiny 2 Lite | $179 |
| Talent 2 | $2,099 | Tiny SE | $99 |
| Meet Flip | $99 | Meet 2 | $129 |
| Tiny 3 | $349 | Meet SE | $69 |
| Tiny 3 Lite | $199 | Tail Air | $499 |
| Tiny 2 | $329 | Tail 2 | $1,199 |
| | | Talent | $1,099 |

- 联动：录入/编辑页「产品型号」下拉（文案带价 `Talent 2 ($2099)`）→ 选中自动填产品价格 → 自动算 CPM；后端 `/api/products` 返回 `[{model,cost}]`，前端 `loadProducts()` + `onProductChange()` 实现
- 产品价格仍可手改（折扣/送样场景），改后 CPM 实时重算

## 核心公式
- CPM = (合作费用 cost + 产品价格 product_cost) ÷ (均播 avg_views ÷ 1000)
  - 例：Talent 2（$2099）+ 费用 $2000 + 均播 50万 → CPM = 4099÷500 = $8.20
- 合作状态枚举：待联系 / 已联系 / 合作中 / 已合作
- 平台枚举：YouTube / Instagram / Twitch / X(Twitter) / TikTok / Bilibili / Facebook / 其他

## 页面结构
| 页面 | 路由 | 功能 |
|---|---|---|
| 登录页 | /login.html | 密码 → Set-Cookie kol_session |
| 主页 | / | 月度目标进度条、方向指引卡片、发布需求卡片网格、邮件提醒列表、操作日志弹窗 |
| 红人管理 | /kol.html | 表格 + 平台/状态/类别/来源/粉丝筛选 + 编辑/复制/删除 + CSV 导入导出 |
| 录入红人 | /add.html | 大表单，CPM 前端实时算 |

## API 清单
- POST /api/login {password} → {token} + Set-Cookie；POST /api/logout
- GET /api/dashboard — 聚合：目标/进度/合作状态计数/提醒(带 remind_state: overdue|today|upcoming)/方向/需求数
- GET /api/kols?search&platform&status&category&min_followers&page&page_size&sort&order
- POST /api/kols（创建）、PUT /api/kols/<id>（更新，自动算 CPM）、DELETE /api/kols/<id>、POST /api/kols/<id>/duplicate
- GET /api/kols/export（BOM CSV）、POST /api/kols/import {content, mode}
- GET /api/products — 产品价目表 `{items:[{model,cost}], total}`
- GET /api/logs、POST /api/rollback {log_id, password}
- GET/POST /api/settings（monthly_goal）、POST /api/direction {content}
- GET/POST /api/needs、DELETE /api/needs/<id>

## 认证流程（cookie 方案）
1. login.html POST /api/login → 服务端 Set-Cookie: kol_session=<hex>; Path=/; HttpOnly; SameSite=Lax
2. 前端 api() 不存 localStorage（cookie 自动带），401 时跳 /login.html
3. check_auth：正则从 Cookie 头取 kol_session，兼容 Authorization Bearer（curl 测试用）
4. 静态页未登录返回 meta refresh 到 login

## 邮件提醒逻辑
- 提醒条件：next_remind 非空 且 status IN ('合作中','已合作')
- Dashboard 按 next_remind 排序，remind_state 分色：逾期红 / 今天黄 / 未来绿
- 「发邮件」按钮 = mailto: 链接，正文预填视频进度询问模板（未做真 SMTP 自动发送——用户提过这个选项，若后续接上：SMTP 配置 + 定时任务）

## 操作日志/回调
- 增删改/导入都写 operation_log，带 before_json/after_json 快照
- rollback 需管理员密码验证：
  - create → DELETE 该行
  - update → 用 before 还原
  - delete → 用 before 重插（保留原 id）
  - need 同理
- 回调本身也写一条 rollback 日志

## 待办/可扩展
- 真 SMTP 自动发邮件（用户已询问过）
- 修改密码界面（当前只有 README 里的 sqlite3 命令）
- 平台列表可扩展（小红书/抖音等）
- 局域网访问：HOST 改 0.0.0.0
