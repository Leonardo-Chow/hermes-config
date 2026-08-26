---
name: bilingual-daily-digest
description: 生成中英双语每日深度摘要(HTML/Claude暖色)→IMA知识库，含全球财经、双语板块、深度观察双核。
tags: [daily-digest, bilingual, html-report, ima, deep-analysis]
---

# Bilingual Daily Digest Generator

生成**中英双语每日深度资讯摘要**，产出单文件零依赖 HTML（Claude暖色风），直传 IMA 知识库（HTML media_type=20）。

## 适用场景
- 每日早报/摸鱼日报/内部情报简报
- 需要中英双语对照、仅当日内容、多源去重、深度分析的场景
- 产出需直接在浏览器打开、无需部署、可离线阅读

---

## 核心板块结构（固定，按序号渲染）

| 序号 | 板块 | 关键要求 |
|------|------|----------|
| 01 | **指数与全球财经** | A股4指数+美股3指数卡片；全球财经新闻≥3家来源（CNBC直连XML+FT+BI），仅当日 |
| 02 | **国内热搜·三平台** | 微博/百度/抖音，每条含中文简析（关键词→简析映射表） |
| 03 | **科技热点** | TechCrunch/Ars Technica/The Verge，**双语：英文标题在上→中文翻译在下→英文摘要** |
| 04 | **AI 动态** | 同双语要求，TechCrunch AI为主源，去重 |
| 05 | **国际视野** | BBC/NPR/Al Jazeera/France 24/NYT/CNN ≥5家，**双语+轮转配额**防单源垄断 |
| 06 | **娱乐圈** | 国内/海外两栏；海外英文条目做双语 |
| 07 | **开源 & 技术社区** | GitHub总榜 + **AI Agent专区**（q=ai agent created:>7天 sort=stars） + HN，**每条含中文介绍** |
| 08 | **深度观察·双核** | **每条500-1000字，四段式**：事件是什么→前因后果→可能影响→未来发展推演<br>• 01：地缘/科技/社会大事件<br>• 02：财经宏观深度（当日无重大财经则降级替换） |

---

## 硬性规则（红线，违者重做）

- ⛔ **仅当日内容**：所有英文源按北京时间过滤（rss2json UTC格式+8h；CNBC RFC822解析）。昨日内容一律剔除
- ⛔ **双语排版强制**：`.t-en` 英文标题（衬线加粗）→ `.zh` 中文翻译 → `.desc-en` 英文摘要（斜体小字）
- ⛔ **多源去重**：国际新闻按源轮转配额入选，保证 ≥5 家媒体；标题前40字去重
- ⛔ **HTML标签剥离必须替换为空格**：`re.sub(r"<[^>]+>", " ", s)` 防英文单词粘连
- ⛔ **混源排序用时间戳**：统一转 `timestamp()` 排序，不能用日期字符串（RFC822与标准格式混排会错位）
- ⛔ **CNN World RSS 陈年缓存**：显式排除或按当日过滤剔除
- ⛔ **封面签名 URL 每次重获**：IMA `get_media_info` 签名会过期
- ⛔ **不直接 patch 生成的 HTML**：修生成脚本重建，防重跑覆盖
- ⛔ **财经观察当日无料**：显式替换（AI产业链/政策周期等），不可硬凑

---

## 采集源与解析要点

### 数据源清单
| 类别 | 源 | 方式 | 关键字段 |
|------|------|------|----------|
| 百度热搜 | `top.baidu.com/api/board?tab=realtime` | JSON | `word` `url` `hotScore`(原始值/10000显示万) |
| 抖音热榜 | `douyin.com/aweme/v1/web/hot/search/list/` | JSON | `word` `hot_value` |
| 微博热搜 | `weibo.js` (Node) | JSON | `title` `hot` `url`(补全搜索链接) |
| A股行情 | `qt.gtimg.cn/q=sh000001,sz399001,sz399006,sh000300` | GBK文本 | 字段3现价 31涨跌 32涨跌幅 |
| 美股指数 | `qt.gtimg.cn/q=usDJI,usIXIC,usINX` | GBK文本 | 同上 |
| CNBC财经 | 直连XML `search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114` | XML解析 | RFC822 pubDate |
| FT/WSJ/BI | `api.rss2json.com/v1/api.json?rss_url=<RSS>` | JSON | UTC标准格式 `YYYY-MM-DD HH:MM:SS` |
| 科技/AI/国际/娱乐 | 同上 rss2json | JSON | 同上 |
| GitHub总榜 | `api.github.com/search/repositories?q=created:>7天前&sort=stars` | JSON | `full_name` `description` `stargazers_count` |
| GitHub AI Agent | `q=ai+agent+created:>7天前&sort=stars` | JSON | 同上 |
| Hacker News | `hacker-news.firebaseio.com/v0/topstories.json` + item API | JSON | `title` `url` `score` |

### 解析坑点速查
| 问题 | 症状 | 修复 |
|------|------|------|
| weibo.js/reddit.js 输出带横幅/多段JSON | `json.load` 报错 | `json.JSONDecoder().raw_decode` 取首文档 |
| reddit 数据在 `trending` 键 | 取不到列表 | `rd.get("trending") or rd.get("items")` |
| CNN 返回3月旧文 | rss2json缓存 | 按北京时间过滤当日 + 建议排除该源 |
| 英文单词粘连 | `re.sub(r"<[^>]+>", "", s)` | 改为替换空格：`re.sub(r"<[^>]+>", " ", s)` |
| 混源排序错位 | 字符串比较 RFC822 vs 标准格式 | 统一 `bj_time()` → `timestamp()` 排序 |
| HTML 标签残留 | 描述含 `<p>` `<a>` | 同单词粘连修复，再 `re.sub(r"\s+", " ", s)` |

---

## 生成流程

### Phase 1 — 采集并落盘 JSON
```bash
# 并行采集所有源 → /tmp/moyu_data/*.json
# 运行 aggregate.py 聚合 → moyu_data.json
```
中间产物落盘，便于重跑调试。

### Phase 2 — 生成 HTML
```python
# gen_html.py 读取 moyu_data.json + obs_templates.py + cover_url.txt
# 产出单文件 moyu_daily_YYYY-MM-DD.html
```
- 双语模板见 `references/deep-observation-templates.md`（OBS_01_GEO / OBS_02_FIN）
- Claude 暖色 token 见 `html-data-report` skill
- 浮动热度 li 需 `display:flow-root` 防重叠

### Phase 3 — 质量验证
```bash
# 1. browser_navigate file:///path/report.html
# 2. 再次 browser_navigate 同URL（刷新缓存）
# 3. browser_vision 截图查重叠/溢出/封面
# 4. 发现问题 → 改 gen_html.py → 重跑 → 回第1步
```

### Phase 4 — 上传 IMA
```bash
node ~/.hermes/skills/ima-skills/knowledge-base/scripts/upload-to-kb.cjs \
  /path/report.html <kb_id> "摸鱼日报 | YYYY-MM-DD 星期X · 深度观察版v4.x"
```
- `upload-to-kb.cjs` 需预置 `html:20, htm:20, epub:21` 映射
- IMA 无删除接口，重做时标题带版本后缀区分

---

## 深度观察模板

见 `references/deep-observation-templates.md`：
- **OBS_01_GEO**：地缘/科技/社会大事件
- **OBS_02_FIN**：财经宏观深度（含A股板块映射）

**质量自检清单**（每次生成前核对）：
- [ ] 两条观察分属不同赛道
- [ ] 每条含四个 `<strong>` 小标题段落
- [ ] ≥3个具体数据点（价格/时间/机构/百分比）
- [ ] 因果链条显式（无"可能/大概/或许"）
- [ ] 未来推演给出3个可观测信号+时间窗口
- [ ] 财经观察含A股板块映射（核心/卫星/规避）
- [ ] 字数500-1000字（不含HTML标签）
- [ ] 当日无重大财经时已替换

---

## 常见报错速查

| 报错 | 原因 | 修复 |
|------|------|------|
| `invalid media_type` | upload-to-kb.cjs 缺 20/21 | 补 MEDIA_TYPES/CONTENT_TYPES 映射 |
| `skill auth failed (200002)` | api_key 被误覆盖/过期 | 恢复 `~/.config/ima/api_key` |
| `fetch failed` | GFW无代理 | `https_proxy=http://127.0.0.1:1082` |
| CNN 返回旧文 | rss2json缓存 | 按北京时间过滤当日 + 排除该源 |
| 英文单词粘连 | HTML剥离用空串 | 标签替换为空格 |
| 排序错位 | 字符串比较两种日期格式 | 统一转 timestamp 排序 |
| 封面破图 | 签名URL过期 | 每次生成前重新 `get_media_info` |

---

## 关联技能与参考文件

- `html-data-report` — Claude暖色HTML生成规范（零依赖图表、Phase 1-5验证）
- `references/deep-observation-templates.md` — 深度观察双核模板（OBS_01_GEO/OBS_02_FIN）
- `ima-skills` — IMA知识库操作（官方1.1.9+本地增强，见 `references/ima-local-enhancements.md`）
- `leonardo-brand` — 统一品牌设计系统（深蓝为主，暖色仅用于日报/报告类）

---

## 版本历史

- v4.0 (2026-08-25)：首个HTML版，双语雏形
- v4.1 (2026-08-25)：用户9条反馈落地（全球财经、删Reddit、双语板块、GitHub介绍、娱乐分栏）
- v4.2 (2026-08-25)：深度观察升级为双核模式（各500-1000字四段式），财经观察强制A股映射