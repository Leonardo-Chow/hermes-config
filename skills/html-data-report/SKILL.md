---
name: html-data-report
description: 批量docx/数据报告分析与可视化：产出单文件Claude暖色HTML dashboard时使用。
tags: []
related_skills: []
---

# HTML 数据分析报告生成 Pipeline

把一批结构相似的报告文档（监测日报、检测周报、导出数据）变成一个**单文件、零外部依赖、浏览器直接打开**的 HTML 数据分析页。

典型触发：「给我分析一下这些数据，做一个 claude 风格的 html 网页数据分析」+ 一批 docx 附件。

---

## Phase 1 — 提取（python-docx）

```python
from docx import Document
doc = Document(path)
paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
tables = [[[c.text.strip() for c in r.cells] for r in t.rows] for t in doc.tables]
```

⚠️ **先验明正身再解析**：打印每个文档的前 5–6 段 + 第一个表头，确认内容与文件名一致。实测出现过两个文件**内容与文件名完全互换**——按文件名归类会把两类数据整体搞反。以内容为准建 filename→identity 映射。

结构规律：这类报告通常是 `编号. 标题` / 链接行 / 元数据行（`键：值 | 键：值`）的段落流，末尾带统计汇总表。用正则按行状态机解析。

## Phase 2 — 结构化 JSON

- 实体抽成 dict：url、title、creator、分类字段、数值指标；中间结果落盘 /tmp/*.json，聚合与生成分离便于重跑。
- 解析完立即打印总量/分组计数 sanity check，与原文档核对。

## Phase 3 — 聚合分析

- **去重口径显式声明**：多份报告时间窗会重叠（8.15-17 与 8.17-18 都含 8.17），按 URL 去重并在页面注明。
- **发布日 ≠ 报告期**：趋势图口径必须全篇一致。「周一补齐周末」型报告按报告期画趋势会出现假峰，改用内容实际发布日。
- 高价值低成本维度：家族归并（单品→品牌）、Counter 排行、均值/中位、语言地区粗判（标题关键词启发式）。
- **所有写进文案的数字先重算**：份额%、均值、峰值日、品牌归属凭印象写极易与图表矛盾（本次实测发生 3 处）。

## Phase 4 — 生成单文件 HTML

- **单一数据源铁律**：所有修正在生成脚本里改后重建输出。绝不直接 patch 输出 HTML——下次重跑脚本会静默覆盖补丁（实测踩坑：直接改了 HTML 三处，重跑脚本全部回退，还得返工）。
- **零依赖图表**（无需 ECharts/CDN）：
  - 环形图 = `conic-gradient` 多段着色 + 内嵌绝对定位圆洞显示总数；
  - 条形图 = div 宽度百分比 + 渐变 track；
  - 折线图 = 内联 `<svg>` polyline + circle 数据点 + text 数值标注。
- Claude 暖色 token（用户点名「Claude 风格」时用这套，覆盖 leonardo-brand 深蓝默认）：

```css
--bg:#FAF9F5; --panel:#FFFFFF; --line:#E8E4DA; --ink:#29261B; --sub:#6E6A5E;
--accent:#D97757; --accent-deep:#B85C3F; --accent-soft:#F7E8E1;
--sage:#7D9273; --slate:#5E718A; --gold:#C0974F;
标题字体: Georgia,"Songti SC","Noto Serif SC",serif
```

- 页面骨架：eyebrow+大标题+meta → 6 张 KPI 卡 → 编号分区（01 趋势折线 / 02 自家分布 / 03 竞品格局环形图 / 04 内容结构 / 05 TOP 榜+语言分布 / 06 编号洞察列表 01–08 / 07 明细表 Tab 切换）→ footer 标注来源与生成时间。
- 明细表放最后用 Tab 切换分组，每行带可点击原文链接。

## Phase 5 — 验证

1. `browser_navigate` 到 `file:///path/output.html`，snapshot 确认结构与表格行数。
2. **重新 navigate 再截图**——patch 过的页面不刷新会截到旧缓存版本，造成「已修复」假象。
3. 截图检查图表错位/文字溢出/色调统一。
4. 文案↔图表一致性终检：板块标题的结论词（「周四见顶」「断层第一」）必须被图中数字支撑；品牌归属逐条对源数据。

## Pitfalls

1. 文件名 ≠ 内容——批量附件先验身份。
2. 修正只进生成脚本，输出文件是一次性产物。
3. 图表数据、callout 文案、板块标题三处必须同一口径。
4. 中文键值行解析注意全角冒号、`|` 分隔两侧空格、百分号。
