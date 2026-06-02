---
name: obsbot-competitive-analysis
description: 多平台竞品分析工作流 — 从 YouTube/Reddit/Amazon 等平台数据（docx/xlsx）中提取用户反馈，生成杂志风格 HTML 市场分析报告（含 Chart.js 图表）。当用户要求分析竞品数据、生成市场分析报告、或处理 OBSBOT/竞品的 YouTube 评论/Reddit 讨论/Amazon 评论时使用。也适用于 YouTube 全量视频搜索+KOL 调研（产品竞品分析场景）。
version: 1.1.0
---

# 多平台竞品分析工作流

从 YouTube 评论、Reddit 讨论、Amazon 评论等多平台数据中提取洞察，生成杂志风格 HTML 市场分析报告。

## KOL 视频分析工作流

当用户要求分析某个 YouTube KOL 视频（获取字幕 → 上传腾讯文档 → 生成解析到 IMA），详见 `references/kol-video-analysis-workflow.md`。

核心流程：TranscriptAPI 获取字幕 → `create_smartcanvas_by_mdx` 上传到腾讯文档红人视频文件夹 → 按工作流程格式生成解析 → `import_doc` + `add_knowledge` 上传到 IMA OBSBOT 知识库。

关键 ID：
- OBSBOT 知识库：`mmYXYA4QIUsKj6PikZYHx1HtEhrPFvmysbEUrO4UfvQ=`
- 红人视频文件夹（腾讯文档）：`DNmTBhbgCAky`
- TranscriptAPI Key：存储在 `~/.zshenv`

## 每日监测工作流

当用户要求「每日监测」「今天更新的 OBSBOT 视频」「daily monitor」时，执行每日监测流程。

核心流程：YouTube Data API + web_search 多平台搜索 → 腾讯文档智能表格（7列：更新时间/KOL ID/产品关键词/平台/视频类型/视频简介/视频链接）。

**关键要求**：
- 简介必须完整（含所有链接、折扣码、hashtags、免责声明），不能摘要
- 搜索结果标注置信度（HIGH/MEDIUM/LOW）
- 未检测到的平台必须说明是「确认无内容」还是「检测能力不足」

详见 `references/daily-monitoring-workflow.md`。

## 适用场景

- OBSBOT 产品竞品分析
- OBSBOT 每日多平台内容监测（YouTube/Instagram/TikTok/X）
- 任何产品的多平台用户反馈分析
- 从 docx/xlsx 文件中提取数据生成可视化报告

## 数据提取工具

### docx 文件（Word 文档）
```python
# 使用系统 Python（不是 venv）
python3 -c "
from docx import Document
doc = Document('/path/to/file.docx')
text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
"
```
⚠️ 必须用 `python3`（系统 Python），venv 中可能没有 python-docx。已安装：`pip3 install python-docx`

### xlsx 文件（Excel）
```python
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('/path/to/file.xlsx')
for name in wb.sheetnames:
    ws = wb[name]
    print(f'{name}: {ws.max_row} rows x {ws.max_column} cols')
"
```
⚠️ 已安装：`pip3 install openpyxl`

### Reddit 数据
- 优先用 Tavily Extract：`mcp_tavily_tavily_extract(urls=['https://www.reddit.com/r/xxx/hot/'])`
- 备用：Camoufox 浏览器（curl/API 被封 403）

### YouTube 数据
- YouTube Data API v3（Key 在 memory 中）
- 或从已有的 xlsx 文件中提取

## HTML 报告模板

使用 guizang-ppt-skill 的杂志风格（深色主题 + 衬线标题 + 无衬线正文），配合 Chart.js 生成图表。

### 必须包含的图表类型
1. **柱状图** — 对比数据（如 TOP 10 视频观看量）
2. **环形图/饼图** — 占比分布（如评分分布、竞品提及率）
3. **折线图** — 趋势变化（如发布时间线）
4. **雷达图** — 多维对比（如竞品维度对比）
5. **堆叠柱状图** — 正负面情感对比

### CSS 变量（深色杂志风格）
```css
:root {
  --bg: #0a0a0f;
  --bg-card: #12121a;
  --text: #e8e6e3;
  --text-dim: #8a8a9a;
  --accent: #00cec9;
  --accent2: #e84393;
  --accent3: #6c5ce7;
  --accent4: #fdcb6e;
  --accent5: #ff6b35;
  --green: #00b894;
  --red: #d63031;
  --serif: 'Noto Serif SC', serif;
  --sans: 'Inter', sans-serif;
  --mono: 'JetBrains Mono', monospace;
}
```

### Chart.js CDN
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
```

### Google Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

## 报告结构模板

```
1. Hero 区 — 产品名 + 核心指标（大数字）
2. 数据概览 — 各平台数据对比（柱状图 + 环形图）
3. 详细分析 — 按平台分节（YouTube/Reddit/Amazon）
   - TOP 视频表格
   - 正面评价卡片（绿色边框）
   - 负面评价卡片（红色边框）
   - 情感分析堆叠图
4. 竞品对比 — 提及频率（环形图）+ 维度对比（雷达图）+ 表格
5. 社区反馈 — Reddit 帖子卡片
6. 核心洞察 — 优势/劣势/建议/竞争格局（4 卡片）
```

## 数据分析流程

### Step 1: 数据提取
- docx → python-docx 提取段落文本
- xlsx → openpyxl 读取表格数据
- 统计：总条数、评分分布、关键词频率

### Step 2: 情感分析
- 正面关键词：tracking, quality, love, amazing, great, recommend
- 负面关键词：issue, problem, firmware, price, unreliable, bug
- 按主题分类：画质、AI功能、音频、价格、软件稳定性

### Step 3: 竞品提取
- 从评论中提取竞品品牌名
- 统计提及频率
- 对比维度：价格、功能、用户口碑

### 参考文件索引

本 skill 的 `references/` 目录包含：
| 文件 | 内容 |
|:-----|:-----|
| `kol-screening-criteria.md` | KOL筛选标准全文解析 |
| `noxinfluencer-kol-discovery-cookbook.md` | NoxInfluencer CLI 搜索命令大全 |
| `verified-kol-patterns-from-v3-session.md` | 2026-05 美洲市场V3已验证的KOL偏好模式 + 搜索参数 + GFW恢复策略 |
| `kol-video-analysis-workflow.md` | KOL 单视频分析流程 |
| `youtube-full-search.md` | YouTube 全量视频搜索 |
| `daily-monitoring-workflow.md` | 每日监测工作流（多平台搜索+智能表格） |
| `competitive-monitoring-sop.md` | OBSBOT 竞品投放监测 SOP（竞品清单、数据字段、用户评论5大维度、竞争洞察） |
| `html-template-guide.md` | HTML 报告模板指南 |
| `obsbot-admin-api.md` | OBSBOT 内部管理系统 API（网红数据、大使列表、批量扫描） |

### Step 4: 报告生成
- 使用 execute_code 一次性生成完整 HTML
- 用 write_file 写入 ~/Documents/ 目录
- 文件名格式：{产品名}-market-analysis-{日期}.html

## KOL 资源开发工作流（美洲市场示例）

当用户要求开发新市场 KOL 资源时，执行以下流程：

### ⚠️ 第一步：判断「找新的」还是「补旧的」

用户可能指定具体 KOL ID（如"找我指定的这几个"），也可能让搜索新的人。**规则**：
- **用户给具体名字** → `Connor McCaskill` / `Davey Gravy` 等 → 只查这几个人的数据并补全，**不要去找同类型**
- **用户给品类要求** → "找Tech/3C类的中腰部博主" → 用 NoxInfluencer 搜索
- **用户给示例但说找相似** → 按品类+量级参数搜索匹配的
- **用户从之前结果里留一部分** → 留下的不要动，其余按场景补充

### 步骤0：产品→场景→品类映射（必须先做）

用户明确纠正过「先思考产品适合的目标人群，然后再去寻找KOL」。在任何搜索前，先分析产品核心卖点 → 对应的使用场景 → YouTube 品类：

```python
# 例：OBSBOT Tiny 3 核心卖点 = AI追踪 + PTZ自动跟拍
target_scenarios = [
    ("🎥 直播/串流",    "走动时AI自动追踪",   ["Livestream", "Streamer"]),        # P0
    ("🏋️ 健身/运动",   "运动中自动跟拍",     ["Sports", "Fitness"]),              # P0
    ("🎵 音乐/录音棚", "多角度无人跟拍",     ["Music", "Studio"]),               # P1
    ("📷 相机/视频教学","AI追踪作为卖点",     ["Camera", "Videography"]),          # P1
    ("🪑 桌搭/工作室", "高颜值摄像头融入Setup",["Content Creator", "Setup"]),     # P1
    ("🎮 游戏直播",    "互动更自由",          ["Gamer", "Game Gear"]),             # P2
    ("💼 远程办公/教育","AI自动构图",         ["Apple", "Productive Tools"]),     # P2
]
# 用场景对应的品类去 NoxInfluencer 搜索

用户历史偏好模式（已验证保留的KOL样本）和更多已验证的 NoxInfluencer 搜索参数见 `references/verified-kol-patterns-from-v3-session.md`。
```

### 数据源准备
1. **已合作 KOL 表** — `Tiny 3 & Lite KOL(1).xlsx`（或更新的版本），用于排除已合作博主
2. **已有模板** — `Leonardo的 KOL资源开发.xlsx`，包含了部分已筛选的 KOL
3. **KOL筛选标准** — IMA 笔记「KOL筛选标准」，搜索关键词定位。详见 `references/kol-screening-criteria.md`

### 排除规则
- 用 `openpyxl` 读取已合作表的「网红ID」列（B列），生成排除列表：`python3 -c "import openpyxl; ..."`
- 同时排除模板中已有的 KOL（以免重复）
- 逐一验证候选 KOL 在排除列表中：`python3 -c 'print("✅" if name.lower() not in kols else "⛔")'`

### ⚠️ 关键偏好：KOL 量级选择
- **用户明确要求中腰部以下** — 不要全选头部/顶部博主
- 按筛选标准量级定义（近期10个视频均播）：
  - 🥈 **Mid-tier（腰部）**：10k ≤ views < 30k — **首选**
  - 🥉 **Nano（尾部）**：views < 10k — **首选**
  - 🥇 **Lower Macro（中下部）**：30k ≤ views < 50k — **少量**
  - 🏆 **Elite / Upper Macro**（views ≥ 50k）— **不要选**
- **粉丝数 >3k** — 太低的不考虑
- **近3个月活跃** — `--published_within_days 90` 过滤

### KOL 搜索策略（从中国网络环境）

| 方法 | 效果 | 说明 |
|:-----|:-----|:-----|
| **Noxinfluencer CLI** | ⭐ **首选** | CLI搜索最精准，支持关键词/国家/粉丝量/均播/活跃度多维过滤。4000配额/月 |
| **Noxinfluencer 网页版** | ⭐ 备用 | 筛选标准推荐，含多个OBSBOT账号（见 `references/kol-screening-criteria.md`） |
| **YouTube Data API** | ⚠️ 需要VPN | 可搜索特定品类频道，配额有限 |
| **web_search + FeedSpot** | ⚠️ 辅助 | 可找到频道目录站，但GFW下结果有限 |
| **delegate_task** | ⚠️ 容易超时 | 大范围搜索容易600s超时，适合窄范围搜索 |
| **web_extract** | ❌ GFW阻断 | 多数KOL目录站被墙 |
| **知识 + 验证** | ⭐ 备用 | 利用对YouTube创作者生态的了解 + 定向搜索验证 |

### NoxInfluencer 搜索参数详解

详细搜索命令和已验证的频道名单见 `references/noxinfluencer-kol-discovery-cookbook.md`。

```bash
# 基础搜索命令
noxinfluencer creator search --platform youtube \
  --country '[US,CA]' \           # 国家：US=美国, CA=加拿大, MX=墨西哥
  --keywords '[关键词]' \          # 搜索关键词（shell引号数组）
  --avg_view_min 3000 \            # 最低均播
  --avg_view_max 50000 \           # 最高均播
  --follower_min 3000 \            # 最低粉丝
  --follower_max 150000 \          # 最高粉丝
  --published_within_days 90 \     # 最近90天内发布过视频
  --page_size 20 \                 # 每页数量（最多20）
  --lang zh                        # 中文输出
```

**关键筛选参数**：
- `--avg_view_min` / `--avg_view_max` — 按均播过滤量级（核心参数）
- `--follower_min` / `--follower_max` — 按粉丝数过滤
- `--published_within_days` — 确保活跃度（建议90天）
- `--keywords` — 按内容标签搜索，支持多关键词
- `--country` — 目标市场国家代码
- `--follower_countries` — 受众国家占比

**分品类关键词策略**：
| 品类 | 关键词 | 建议均播范围 |
|:-----|:-------|:------------|
| Tech/3C | `[webcam review,tech gadget,3C,camera review]` | 5k-50k |
| Camera/Videography | `[camera review,photography tutorial,videography,film]` | 3k-50k |
| Desk Setup/PC Build | `[desk setup,gaming setup,PC build,home office]` | 3k-50k |
| Livestream/Gamer | `[streaming setup,gaming gear,live stream,PTZ camera]` | 3k-50k |
| Music/Studio | `[music production,studio setup,guitar tutorial]` | 3k-50k |
| Content Creator | `[productive tools,setup tour,workspace]` | 3k-50k |
| Sports/Fitness | `[fitness,yoga,workout,gym,home gym]` | 3k-50k |
| Apple/Accessories | `[apple accessories,mac setup,iphone accessories]` | 3k-50k |
| Mexico (Spanish) | `[tecnologia,camara web,streaming,reseña]` | 3k-50k |

### 价格估算

| 量级 | 均播范围 | 建议价格 |
|:-----|:---------|:---------|
| 🥉 Nano | <10k | $60 - $200 |
| 🥈 Mid-tier | 10k-30k | $200 - $500 |
| 🥇 Lower Macro | 30k-50k | $500 - $900 |
| 🥇 Upper Macro | 50k-100k | $900 - $2,000 （慎选）|
| 🏆 Elite | ≥100k | $2,000+ （用户要求不选）|

### 后续步骤：联系信息
- **不要在当前流程中获取联系方式** — 用户明确表示「可以先不获取联系方式，后面我自己去弄」
- 后续操作：NoxInfluencer 中可以用 `creator contacts` 获取邮箱

### 品类覆盖要求

不要全是一种类型，按 KOL筛选标准的网红类型分类覆盖：

| 优先级 | 品类 | 与产品匹配度 |
|:-------|:-----|:------------|
| P0 | Camera / Tech / 3C / Gadget Review | 直接评测摄像头产品 |
| P1 | PC Build / Desk Setup / Livestream | 可用作工作室/直播设备 |
| P2 | Content Creator / Apple / Game Gear | 内容创作生态设备 |
| P3 | Music / Art / DIY / Sports / Entertainment | 场景化使用案例 |

### 模板填写规范（16列）

| 列号 | 字段 | 填写规范 |
|:----:|:-----|:---------|
| 1 | 产品 | 固定为 `Tiny 3& Tiny 3 Lite` |
| 2 | KOL ID | 频道名称（非Handle） |
| 3 | 邮箱 | 公开邮箱或 @频道名推测 |
| 4 | 频道链接 | YouTube 频道 URL |
| 5 | 受众国家 | 按筛选标准：美国/加拿大/墨西哥 |
| 6 | 粉丝量（k） | 如 `7.1M`, `136k` |
| 7 | 量级（k）（视频均播） | 按近期10个视频均播估算 |
| 8 | 互动率 | 百分比估算 |
| 9 | 网红类型-一级类目 | Tech / Camera / Livestream / Gamer / Content Creator / Apple / Sports / Entertainment |
| 10 | 网红类型-二级类目 | 按筛选标准中的二级类目填写 |
| 11 | 视频形式&内容 | 简述频道内容方向 |
| 12 | 合作平台 | `youtube` |
| 13 | 建议合作价格 | 按量级估算（Nano $50-200 / Mid-tier $200-500 / Macro $500-1000 / Elite $1000+） |
| 14 | 是否建议合作及理由 | 必须填写2-3句推荐理由 |
| 15 | 筛选时间 | `YYYY-MM-DD` |
| 16 | @审核人员 | 留空（用户负责审核） |

### Excel 生成脚本
```python
# 用 openpyxl 生成格式化的 Excel 文件
# 模板格式：标题行（合并A1:P1）+ 表头行（蓝色背景白字）+ 数据行
# 冻结窗格 A3，启用自动筛选
```

### 腾讯文档 上传工作流

KOL 资源表生成后，上传到腾讯文档云盘 OBSBOT 文件夹：

```bash
# Step 1: 上传到 COS
cd ~/.hermes/skills/tencent-docs
bash import_file.sh "/path/to/Leonardo的 KOL资源开发_XX.xlsx"
# 输出：IMPORT_READY, FILE_KEY, FILE_NAME, FILE_MD5, TASK_ID, FILE_SIZE

# Step 2: 触发异步导入
mcporter call "tencent-docs" "manage.async_import" --args '{"task_id": "<TASK_ID>", "file_size": "<FILE_SIZE>", "file_key": "<FILE_KEY>", "file_name": "<FILE_NAME>", "file_md5": "<FILE_MD5>"}'

# Step 3: 等待导入完成（15秒）
sleep 15

# Step 4: 搜索找到 file_id
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key": "文件名关键词"}'
# 记录返回的 file_id

# Step 5: 移动到 OBSBOT 文件夹 (DjbGtzenXmbX)
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id": "<file_id>", "target_folder_id": "DjbGtzenXmbX"}'

# Step 6: 验证
mcporter call "tencent-docs" "manage.folder_list" --args '{"folder_id": "DjbGtzenXmbX"}'
```

⚠️ **注意**：`manage.import_progress` 已知返回 405，替代方案是用 `manage.search_file` 确认。

## 常见陷阱

### ⚠️ 系统 Python vs venv
python-docx 和 openpyxl 安装在系统 Python 3.9 中（`~/Library/Python/3.9/lib/python/site-packages/`），不在 Hermes venv 中。必须用 `python3` 而非 venv 的 python。

### ⚠️ Excel 中文编码
openpyxl 读取中文内容时默认 UTF-8，一般不需要额外处理。但如果遇到乱码，检查文件编码。

### ⚠️ docx 中的表格
python-docx 的 `doc.paragraphs` 只提取段落文本，不包含表格内容。如需提取表格：
```python
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)
```

### ⚠️ Chart.js 深色主题
必须设置 `Chart.defaults.color = '#8a8a9a'` 和 `Chart.defaults.borderColor = '#2a2a3a'`，否则图表文字在深色背景上看不见。

### ⚠️ 文件存放路径
报告存放在 `~/Documents/` 目录，文件名加日期区分版本。不要覆盖旧文件。

### ⚠️ YouTube Data API 需要 VPN
在中国大陆环境下，YouTube Data API 调用需要 VPN。如需使用，先让用户手动开启 Shadowrocket。

### ⚠️ 多平台搜索的置信度差异
YouTube Data API 返回 HIGH 置信度结果。但 Instagram/TikTok/X 的 web_search 结果置信度仅为 MEDIUM/LOW：
- 搜索引擎对当天帖子索引延迟（几小时到几天）
- web_extract 被所有社交平台的登录墙拦截
- NoxInfluencer 可查 tagged 创作者但无法确认当天是否发了相关内容
- 第一次搜索可能遗漏 Instagram 内容（已验证），必须用多种查询变体重试
- 搜索结果为「未检测到」≠「确认无内容」，必须向用户说明检测能力限制

### ⚠️ 用户期望持续推进
不要中途停下汇报「X/Y 完成」然后等待指令。遇到失败应尝试其他方法继续，直到所有数据获取完毕。生成文档前必须自检：文字覆盖率≥95%、关键板块全部存在。

### 🔑 关键工作流修正（2026-05-28 美洲市场V3经验）

#### 步骤0：产品→场景→品类映射（必须先做）

在搜索任何 KOL 之前，**先分析产品目标使用场景**，再映射到 YouTube 内容品类。用户明确纠正过「先思考tiny3适合的目标人群，然后再去寻找KOL」：

```python
# 例：OBSBOT Tiny 3 核心卖点 = AI追踪 + PTZ自动跟拍
target_scenarios = [
    ("🎥 直播/串流", "走动时自动追踪", ["Livestream", "Streamer"]),
    ("🏋️ 健身/运动", "运动中自动跟拍", ["Sports", "Fitness"]),
    ("🎵 音乐/录音棚", "多机位无人跟拍", ["Music", "Studio"]),
    ("📷 相机/视频教学", "AI追踪作为卖点", ["Camera", "Videography"]),
    ("🪑 桌搭/工作室", "高颜值摄像头融入Setup", ["Content Creator", "Setup"]),
    ("🎮 游戏直播", "互动更自由", ["Gamer", "Game Gear"]),
    ("💼 远程办公/教育", "AI自动构图", ["Apple", "Productive Tools"]),
]
# 用这些场景对应的品类去 NoxInfluencer 搜索
```

#### 多版本迭代模式

用户可能会经历多轮筛选。V1→V2→V3迭代常见：
- **V1** 偏大（容易选头部博主）→ 用户会要求缩小
- **V2** 用中腰部但品类不够匹配 → **V3** 按场景精细化
- 每一版生成**新文件**（标注版本号 `_V3_`），不覆盖旧版
- 用户留下哪些就保留，剩下重新按场景补充

#### 中腰部/Nano 严格参数（用户已验证）

用户从 V2 的 39 个里只保留了 12 个，其余要求全部重找。已验证的偏好特征：
```
粉丝范围: 34k ~ 137k，中位数 ~70k
均播范围: 2k ~ 38k，中位数 ~15k
❌ Elite（均播≥50k或粉丝≥150k）不要选
✅ Mid-tier（均播10k-30k）/ Nano（均播<10k）首选
✅ Lower Macro（均播30k-50k）可少量
```

#### NoxInfluencer GFW 故障恢复

NoxInfluencer API (`skill.noxinfluencer.com`) 有时被 GFW 阻断：
```
Error: Request failed: fetch failed
noxinfluencer doctor → server_reachable = fail
```
**恢复策略**：先 `noxinfluencer doctor` 确认 → 不通则用缓存数据（之前搜索结果 / `references/noxinfluencer-kol-discovery-cookbook.md` 已验证名单）→ 尝试 Shadowrocket VPN 后再试

#### mcporter 授权过期修复

Tencent Docs 上传报 `TLS connection` / `fetch failed` 时：
```bash
mcporter auth tencent-docs
```
重新授权即可，不需要手动刷新 token。

#### 联系方式留空（用户偏好）

搜索/筛选阶段**不要**获取联系方式（`creator contacts`）。用户明确说「可以先不获取联系方式，后面我自己去弄」。

### ⚠️ 网红类型必须按实际内容分类
用户明确要求：网红类型分为 Livestream/Camera/Review/Tutorial/Podcast/Church 等实际类型，**不要用 KOL 量级**（头部KOL/腰部KOL/素人）。

### ⚠️ 受众地区必须带英文名
格式：`English Name/中文名`。欧洲国家统一标注为 `Germany/欧洲`, `France/欧洲` 等。

### ⚠️ Pros/Cons 必须基于评论区真实内容
先获取视频评论（YouTube API commentThreads，按 relevance 排序），从评论中提取用户反馈。不能仅靠标题/描述推断。

### ⚠️ 腾讯文档批量上传批次大小
每批 ≤10 条记录。50 条会导致 mcporter 输出截断（20K 字符限制），JSON 解析失败。用 `write_file` + `$(cat /tmp/file.json)` 传递大 JSON。

### ⚠️ manage.create_file 中文标题报错
先用英文标题创建，再用 `manage.rename_file_title` 改为中文。
