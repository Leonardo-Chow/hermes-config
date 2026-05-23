---
name: market-analysis-report
description: 生成数据驱动的市场分析报告（HTML 深色杂志风格），含 Chart.js 图表（折线/柱状/饼图/雷达图）、真实数据采集、多源并行分析。当用户要求生成市场报告、行业分析、竞品分析、数据可视化报告时使用。
version: 1.0.0
---

# 市场分析报告生成器

生成**单文件 HTML** 市场分析报告，深色杂志风格（参考 guizang-ppt-skill 电子杂志风），含 Chart.js 交互式图表。

## 触发条件

- 用户要求「市场分析报告」「行业报告」「竞品分析」「数据可视化报告」
- 用户提到「market analysis」「industry report」
- 需要将多源数据整合为可视化报告

## 工作流

### Step 1 · 需求澄清

1. **主题**：分析什么市场/行业？
2. **数据维度**：市场规模、增长趋势、竞争格局、融资、技术趋势？
3. **时间范围**：历史数据 + 预测到哪年？
4. **输出格式**：HTML 单文件（默认）还是 PDF？

### Step 2 · 数据采集（delegate_task 并行）

使用 `delegate_task` 并行采集，典型分组：
- **任务 1**（web）：市场规模、融资、行业报告
- **任务 2**（terminal）：GitHub API、公开数据接口

**数据源优先级**：
1. Tavily Search/Research — 搜索行业报告、新闻
2. GitHub API — 开源项目数据（stars/forks/contributors）
3. 公开 API — 行业特定数据
4. web_extract — 提取报告/文章内容

**输出格式**：写入 `/tmp/market_data.json`，结构化 JSON。

### Step 3 · 生成 HTML 报告

使用 `write_file` 生成单文件 HTML，包含：
- Chart.js CDN：`https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js`
- Google Fonts：`Noto Serif SC`（标题）+ `Inter`（正文）+ `JetBrains Mono`（数据）
- 深色主题 CSS（参考 guizang-ppt-skill 杂志风）

### Step 4 · 质量检查

- 用 `browser_navigate` 打开 HTML 验证渲染
- 用 `browser_vision` 截图检查图表是否正常
- 确认数据准确性

## 图表类型指南

| 数据类型 | 推荐图表 | Chart.js type |
|:---------|:---------|:--------------|
| 时间序列（市场规模、增长） | 折线图 + 柱状图组合 | `line` + `bar` |
| 占比分布（市场份额、应用场景） | 环形图 | `doughnut` |
| 对比排名（公司融资、项目星标） | 横向柱状图 | `bar` + `indexAxis: 'y'` |
| 多维度对比（公司能力矩阵） | 雷达图 | `radar` |
| 增长率对比（CAGR） | 纵向柱状图 | `bar` |

## HTML 模板结构

```
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>报告标题</title>
  <script src="Chart.js CDN"></script>
  <link href="Google Fonts">
  <style>:root { CSS variables } ... </style>
</head>
<body>
  <!-- Hero: 标题 + 核心指标 -->
  <!-- Sections: 每个板块含图表 + 表格 + 分析 -->
  <!-- Footer: 数据来源 + 生成时间 -->
  <script>// Chart.js 实例</script>
</body>
</html>
```

## 深色主题配色方案

```css
:root {
  --bg: #0a0a0f;           /* 主背景 */
  --bg-card: #12121a;      /* 卡片背景 */
  --bg-highlight: #1a1a2e; /* 悬停高亮 */
  --text: #e8e6e3;         /* 主文字 */
  --text-dim: #8a8a9a;     /* 辅助文字 */
  --accent: #ff6b35;       /* 主强调色（橙） */
  --accent2: #e84393;      /* 次强调色（粉） */
  --accent3: #00cec9;      /* 第三色（青） */
  --accent4: #6c5ce7;      /* 第四色（紫） */
  --accent5: #fdcb6e;      /* 第五色（黄） */
  --border: #2a2a3a;       /* 边框 */
}
```

## 注意事项

- **数据必须真实** — 所有数据必须有来源标注，不要编造数据
- **图表交互** — Chart.js 默认支持 hover 显示数值，确保启用
- **单文件** — 所有 CSS/JS 内联，不依赖外部文件（除 CDN）
- **中文优先** — 报告主体用中文，技术术语保留英文
- **响应式** — 使用 CSS Grid + `@media` 适配移动端
- **GitHub 下载超时** — 如需下载模板文件，先连 VPN 再用 `curl -sL` 逐文件下载
