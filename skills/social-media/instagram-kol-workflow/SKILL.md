---
name: instagram-kol-workflow
description: Instagram KOL 端到端工作流 —— 竞品博主发现 → 批量粉丝/播放量获取 → 本地管理系统录入跟踪 → 视频内容解析报告。覆盖 IG 搜索页爬取、web_profile_info API、og:description 解析、instaloader/移动端 Feed API、腾讯文档智能表写入、KOL 管理系统、YouTube 字幕获取与 OBSBOT 格式报告生成。
tags: [instagram, kol, koc, influencer, web-profile-info, instaloader, tiktok, youtube, tencent-docs, ima]
---

# Instagram KOL 端到端工作流

本技能统筹 Instagram/KOL 相关的四大核心能力，形成**发现 → 量化 → 管理 → 分析**的完整闭环。原有四个窄技能（`instagram-competitor-kol-discovery`、`instagram-follower-batch-fetch`、`kol-manager-webapp`、`kol-video-analysis`）已合并为本技能的四个标签子章节，保留其独特经验细节。

---

## 1️⃣ 竞品博主发现 — `instagram-competitor-kol-discovery`

**场景**：给自家产品（如 OBSBOT Meet）找竞品在 IG 上的创作者（尤其女性博主），用于对标/合作/竞争情报。

### 核心流程
```
IG 搜索页 → 提取帖子 shortcode → 逐帖 curl 解析作者 → 验证性别/bio → 交付链接清单
```

### 关键步骤与坑点
| 步骤 | 方法 | 关键坑点 |
|------|------|----------|
| 1. 搜索页 | `browser_navigate → instagram.com/explore/search/keyword/?q=<关键词>` | 每次 navigate 掉 session 弹登录框，需 `browser_console` 注入 cookie（`~/.hermes/cookies/platform_cookies.json` 的 instagram 字段） |
| 2. 提取 shortcode | `document.querySelectorAll('a[href^="/p/"]')` | 搜索页 DOM 不暴露作者，必须逐帖抓 |
| 3. 逐帖抓作者 | `curl https://www.instagram.com/p/<code>/` 解析 `og:description` | 格式：`X likes, Y comments - <username> on <date>: "<caption>"`，正则：`-\\s*([A-Za-z0-9_.]+)\\s+on\\s+` |
| 4. 验证性别 | curl 主页 → `og:description` 含 `NAME` | 排除男性/品牌号/聚合号（如 `the_setup_vault`） |

### 交付格式
- 直接列链接 + 粉丝数 + 内容方向，按量级分组（头部 >15万 / 腰部 3-10万 / 小博主 1-2万）
- 标注 #AD 品牌合作帖（说明愿意接同类产品合作）

### 判断要点
- 大博主（>10万粉）竞品帖常为 #AD 合作 → 愿意接单但贵
- 小博主（1-2万粉）自发内容 → 性价比高
- 纯产品测评男性科技号、品牌官方号、聚合号一律排除

---

## 2️⃣ 批量粉丝/播放量获取 — `instagram-follower-batch-fetch`

**场景**：批量从 Instagram 公开主页获取粉丝数、关注数、帖子数、视频播放量，用于筛选 KOL 入库。

### 推荐管道（2026-07-30 实战验证）
```
用户导出关注列表 CSV（DevTools 方法见 references/instagram-following-export.md）
    ↓
web_profile_info API 批量查询（匿名 curl + X-IG-App-ID，~6 分钟/200+ 账号）
    ↓   一次拿到 followers + 最近 12 条视频的 avg_video_views
双重筛选：followers > 50K AND avg_video_views > 5K
    ↓
按 OBSBOT 内容分类体系分类（一级类目 = 内容占比最多；核心排除：纯手机/电脑/键盘/鼠标测评）
    ↓
写入腾讯文档智能表（含查重：list_records field_titles 拉现有 username 比对）
    ↓
输出去重后 CSV（ID/主页链接/粉丝数量/Views/帖子数/一级类目/二级类目/分类依据）
```

### 核心 API：`web_profile_info`（主力，匿名可调）
```bash
curl -s -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
     -H "X-IG-App-ID: 936619743392459" \
     "https://www.instagram.com/api/v1/users/web_profile_info/?username=X"
```
**必须项**：curl（非 urllib）、短 UA、带 `X-IG-App-ID`、**不带 Cookie**（带登录 cookie 时不返回 media edges）、1s 间隔防限流。

### 备选：`og:description` 解析（后备）
- 解析 `<meta property="og:description" content="847 Followers, 595 Following, 299 Posts - ..." />`
- 中英双语格式兼容（Followers/粉丝、Following/关注、Posts/帖子）
- K/M/B 后缀数字解析函数见原 skill

### 进阶：单帖 caption + 评论区 + 实时指标
| 数据 | 方法 | 关键点 |
|------|------|--------|
| 单帖 caption | curl 帖子 URL 解析 `og:description` | 格式含 likes/comments/username/date/caption，区分主页 og 格式 |
| 评论区 | `GET /api/v1/media/{media_id}/comments/` **需登录 cookie** | shortcode → media_id 自定义 base64 转换；1s 间隔取前 8-12 条 |
| 实时点赞/评论 | `instaloader.Post.from_shortcode()` | 每帖 0.8-1s 间隔；Reels 视频 views 拿不到 |
| **Reels 曝光/播放量** | **移动端 Feed API 突破** `GET /api/v1/feed/user/{user_id}/?count=33` | **实测 8 帖中 6 帖拿到 play_count**，不走 web_profile_info 限流池；博主隐藏统计时三路确认全为 None |

### 腾讯文档智能表写入要点
- 记录格式按**字段标题**（非 field_id），`field_values` 数组
- **url 字段必须用 `url_value`**（`text_value` 报错）
- **dateTime 用 `string_value`（毫秒时间戳字符串）**
- **singleSelect 用 `option_value`**；新选项需先 `update_fields` 加到字段 options
- mcporter 调用用参数列表（argv list），**不要 `shell=True` + `$(cat file)`**
- 每批 ≤5 条；失败批次带重试；查重用 `list_records` + `field_titles` 参数

### OBSBOT 内容分类体系（一级类目 = 渠道占比最多）
| 一级 | 二级示例 | 核心排除 |
|------|----------|----------|
| Tech | Hometech / Gadget Review / VR / 3C / Drone / PC Build | 纯手机/电脑/键盘/鼠标测评 → **无效类型** |
| Livestream | Tips / Device / Tutorial / Scene | 非"在直播平台开播" |
| Camera | Photography / Videography / Filmmaker / Camera Settings | |
| Gamer | Game Streamer / Game Gear / Game Recording(FPS) / Gaming PC | |
| Content Creator | Productive Tools / Beauty / Lifestyle / Travel / Fashion / Art | |
| Setup | Desk Setup / Game Setup | OBSBOT 重点品类 |
| Apple | Apple Accessories / Apple News | |
| Live Production | Church / Wedding / DJ / Podcast / Education / Sports | 配合官网 Solution 页面 |
| Entertainment | Reaction / Comedy / ASMR / Cosplay | |
| Sports | Billiards / Basketball / Fitness / Yoga | |
| Social Profession | Teacher / Coach / Esports Team | |

---

## 3️⃣ KOL 本地管理系统 — `kol-manager-webapp`

**位置**：`~/kol-manager` — 零依赖 Python 标准库 + SQLite 单文件网页应用（Claude 风格 UI）。

### 快速操作
```bash
cd ~/kol-manager && ./start.sh          # 启动（自动开浏览器）
cd ~/kol-manager && python3 app.py --no-browser   # 后台启动
# 登录：admin / admin123（settings 表 admin_username/admin_password）
```

### 数据模型（kol 表字段，顺序即 CSV 导出表头）
`username name platform profile_url email followers avg_views product_model product_cost cost cpm status next_remind category sub_category source added_date notes`

- 数值：followers/avg_views/product_cost/cost (INT)；cpm (FLOAT)
- 合作状态六态：**建联中 / 已报价 / 价格不合理 / 确认合作 / 已完成代付款 / 合作结束**
- CPM = (cost + product_cost) ÷ (avg_views ÷ 1000)，选产品型号自动带出价格再算
- 产品价格表 `PRODUCT_PRICES`（13 款 OBSBOT）：Meet 3=$199, Talent 2=$2099, Meet Flip=$99, Tiny 3=$349, Tiny 3 Lite=$199, Tiny 2=$329, Tiny 2 Lite=$179, Tiny SE=$99, Meet 2=$129, Meet SE=$69, Tail Air=$499, Tail 2=$1199, Talent=$1099

### 核心功能
1. **主页 Dashboard**：SVG 环形进度（三色分段：逾期红/今天黄/未来绿）+ 分布统计 + 邮件提醒（mailto 预填模板）
2. **红人管理**：搜索/筛选/排序/编辑/复制/删除/CSV 导入导出（中英表头 `HEADER_ALIAS` 映射）
3. **操作日志 + 回调**：增删改写 `operation_log`（before/after JSON 快照），`/api/rollback` 需管理员密码
4. **登录认证**：Cookie 优先、Authorization header 兼容

### GitHub 自动备份（私有仓库 `Leonardo-Chow/KOL-Manager`）
- 每次写操作后 `auto_backup()` 异步调 `backup.sh`
- **关键坑**：gh CLI token 只有只读权限 → **写权限 PAT 内嵌在 git remote URL 里**（`https://Leonardo-Chow:ghp_xxx@github.com/...`），`backup.sh` 提取复用
- `.gitignore` 必须忽略 `*.db-shm` `*.db-wal`

### 修改字段/加新功能的五处同步
1. `app.py` 的 `FIELDS` 元组
2. `HEADER_ALIAS`（CSV 中英表头映射）
3. `webapp/kol.html` 和 `add.html` 的 JS `FIELDS` 数组 + HTML 表单 `<input id="f-xxx">`
4. `init_db()` 的 `ALTER TABLE` 兼容旧库
5. 筛选字段加入 `build_where`/`api_filters`

### UI 规范（用户明确偏好）
- **Claude 风格**：奶油底 `#FAF9F5`、橙棕主色 `#D97757`、暖黑文字 `#3D3929`、衬线标题 Georgia、左侧边栏、胶囊标签、柔和阴影
- **拒绝深蓝科技主题**（leonardo-brand 仅用于报告/PPT/PDF）

---

## 4️⃣ KOL 视频解析报告 — `kol-video-analysis`

**场景**：解析 YouTube KOL 营销视频，生成符合 OBSBOT 内部文档格式的 Word 报告。

### 核心流程
1. **读取参考文档（必须首先执行）**：`~/Downloads/KOL & 产品营销视频对接 (1).docx`（243MB，必须是 (1) 版本）
2. **获取视频数据**：
   - 字幕：`youtube-transcript-api`（需代理 + PySocks）首选；失败改 `yt-dlp --cookies-from-browser chrome --proxy socks5://... --remote-components ejs:github --write-auto-subs --sub-lang en --sub-format vtt --skip-download`
   - 视频信息：`yt-dlp --print "%(upload_date)s|%(duration)s|%(view_count)s|%(channel)s"`（配合 cookies/proxy/remote-components）最可靠
3. **语言风格**：简洁、每句话有信息量、用"博主展示了/认为/形容"、**禁止** 首先/其次/最后/总之/综上所述/值得注意的是/这是一个优秀的
4. **截图建议**：嵌入正文段落末尾 `(截图建议：MM:SS，简短描述)`，多个用分号分隔
5. **输出**：生成 Word 到 `~/Downloads/`，文件名全新命名，`open` 打开供确认

### 常见错误
- ❌ 不先读参考文档就开始写
- ❌ 截图建议单独放最后
- ❌ 使用 bullet list
- ❌ 出现 AI 套话
- ❌ `youtube_transcript_api` 报 `RequestBlocked` 时不切换备选方案
- ❌ yt-dlp 不加 `--remote-components ejs:github` 导致 n challenge 失败

---

## 🔗 关联技能与参考文件

| 技能/文件 | 用途 |
|-----------|------|
| `references/competitor-product-discovery.md` | 竞品产品博主发现完整配方 |
| `references/ig-mobile-feed-play-count.md` | 移动端 Feed API 获取 Reels play_count 完整脚本 |
| `references/cookie-injection.md` | Cookie 注入详细流程 |
| `scripts/batch_fetch_ig.py` | 批量查询脚本（CSV 读取、断点续传、过滤 >50K） |
| `references/local-webapp-pattern.md` | 本地零依赖网页应用通用模式 |
| `references/kol-manager-v3.md` | KOL 管理系统 v3.x 演进细节 |
| `references/format-template.md` | KOL 视频解析 Word 格式模板 |
| `references/youtube-info-extraction.md` | YouTube 信息提取方法对比 |
| `tencent-docs` | 腾讯文档智能表操作（上传/查重/移动） |
| `ima-skills` | IMA 知识库操作（HTML media_type=20） |
| `leonardo-brand` | 统一品牌设计系统（报告类用深蓝，网页工具用 Claude 风格） |

---

## 📋 版本历史
- v1.0 (2026-09-22)：创建统一技能，合并原四个窄技能