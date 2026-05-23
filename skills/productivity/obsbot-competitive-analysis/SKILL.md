---
name: obsbot-competitive-analysis
description: 多平台竞品分析工作流 — 从 YouTube/Reddit/Amazon 等平台数据（docx/xlsx）中提取用户反馈，生成杂志风格 HTML 市场分析报告（含 Chart.js 图表）。当用户要求分析竞品数据、生成市场分析报告、或处理 OBSBOT/竞品的 YouTube 评论/Reddit 讨论/Amazon 评论时使用。也适用于 YouTube 全量视频搜索+KOL 调研（产品竞品分析场景）。
version: 1.0.0
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

## 适用场景

- OBSBOT 产品竞品分析
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

### Step 4: 报告生成
- 使用 execute_code 一次性生成完整 HTML
- 用 write_file 写入 ~/Documents/ 目录
- 文件名格式：{产品名}-market-analysis-{日期}.html

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
在中国大陆环境下，YouTube Data API 调用需要 VPN 连接（Shadowrocket）。调用前先检查 VPN 状态：`scutil --nc status "Shadowrocket"`。如果断开，先连接：`scutil --nc start "Shadowrocket"`。

### ⚠️ 用户期望持续推进
不要中途停下汇报「X/Y 完成」然后等待指令。遇到失败应尝试其他方法继续，直到所有数据获取完毕。生成文档前必须自检：文字覆盖率≥95%、关键板块全部存在。

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
