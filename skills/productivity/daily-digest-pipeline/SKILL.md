---
name: daily-digest-pipeline
description: 生成每日多平台信息聚合日报时使用。覆盖采集→当日过滤→聚合→HTML→质量评分→知识库上传全管线方法论与踩坑。
---

# 每日信息聚合日报管线

适用于"每天定时采集多平台数据 → 过滤当日内容 → 聚合成中英双语 HTML 报告 → 质量评分 → 上传知识库"这一类任务。具体产品（摸鱼日报 v4.2、bilingual-daily-digest）各自有专属 skill，本 skill 是它们共享的方法论与通用坑。

## 采集层

- terminal 工具不支持 `&` 后台并行；多源并行采集用 execute_code 循环 subprocess，或分批顺序执行
- RSS 优先走 rss2json（`https://api.rss2json.com/v1/api.json?rss_url=<url>`）；**同一天内不同 feed 可能表现不一**：部分返回 error/空 items（限流），部分正常——失败源单独降级，不阻塞整体
- rss2json 失败降级模式（实测有效）：curl 直连 RSS XML → ElementTree 解析 → **转成 rss2json 兼容格式存同名 .json**，让下游聚合脚本零改动：
  ```python
  {'status':'ok','items':[{'title':..., 'link':...(split('?')[0]),
    'pubDate': UTC '%Y-%m-%d %H:%M:%S', 'description':...}]}
  ```
  ⚠️ pubDate 必须转成该 UTC 格式，否则下游 `is_today()` 当日过滤全部失效（旧文泄漏或全部被滤空）
- 直连 XML 时 link 常带跟踪参数，`split('?')[0]` 清洗成干净落地页
- 被墙 API（如 Hacker News Firebase）免 VPN 替代路径优先于要求用户开 VPN；XML 字段缺失（如 score）时前端渲染直接省略该字段，不要显示 "0"

## 聚合层

- 聚合脚本对缺失文件**静默返回空**、对残留文件**静默复用**——两类故障都不报错。防线：① 每日先归档昨日数据文件再采集（防混入旧数据）；② 聚合后打印逐板块条数并核对，任何 0 条必须排查
- 文件名对不上是 0 条的最常见原因（如采集存的 rss_tcv.xml、脚本读的是 rss_verge.json）：对齐命名或复制
- 当日过滤统一用北京时间（UTC+8），兼容 RFC822 与 `%Y-%m-%d %H:%M:%S` 两种 pubDate

## 渲染层（HTML）

- 每日硬编码内容清单（漏改 = 昨日内容泄漏上线）：深度观察正文、卡片标题、翻译映射表、GitHub/HN 中文介绍、热搜简析映射、各板块导语、footer 版本号。自检：`grep 前一日日期 gen_html.py` 应 0 hits 再生成
- 硬编码 key 匹配规则要写清注释（如 ZH 映射 key=英文标题前 30 字符），次日换数据后匹配才不断

## 质量门槛与上传

- 上传前跑可编程评分（板块完整性/封面图/来源多样性/链接落地页率/双语覆盖），低于阈值返工；评分脚本用正则从 HTML 提取验证，不靠目测
- 需签名 URL 的资源（封面图等）每次生成时重新获取——签名会过期，不能复用昨天的 URL
- 国际新闻来源 ≥5 家为优、4 家及格；历史上 CNN/NYT/Reuters/AP 的 RSS 均不稳定，不必硬凑到 5 家

## 相关 skills 与 runbook

- `references/moyu-daily-runbook.md` — 摸鱼日报当日全流程实测记录：采集命令、weibo.js JSON 解析坑、rss2json 降级实测表、gen_html.py 每日必改清单、质量评分实现要点
- `moyu-daily-generator`（用户自有，未 adopt）：中文摸鱼日报 v4.2 产品定义、19 板块结构、质量评分细则、数据源端点表
- `html-data-report` — 批量 docx/数据 → 单文件 Claude 暖色 HTML dashboard（通用报告生成管线，HTML 生成技术栈共享）

---

## 产品变体：中英双语每日深度摘要 — `bilingual-daily-digest`（已合并）

**触发**：「生成中英双语每日深度资讯摘要，产出单文件零依赖 HTML（Claude暖色风），直传 IMA 知识库」

### 核心板块结构（固定，按序号渲染）

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

### 硬性规则（红线，违者重做）

- ⛔ **仅当日内容**：所有英文源按北京时间过滤（rss2json UTC格式+8h；CNBC RFC822解析）。昨日内容一律剔除
- ⛔ **双语排版强制**：`.t-en` 英文标题（衬线加粗）→ `.zh` 中文翻译 → `.desc-en` 英文摘要（斜体小字）
- ⛔ **多源去重**：国际新闻按源轮转配额入选，保证 ≥5 家媒体；标题前40字去重
- ⛔ **HTML标签剥离必须替换为空格**：`re.sub(r"<[^>]+>", " ", s)` 防英文单词粘连
- ⛔ **混源排序用时间戳**：统一转 `timestamp()` 排序，不能用日期字符串（RFC822与标准格式混排会错位）
- ⛔ **CNN World RSS 陈年缓存**：显式排除或按当日过滤剔除
- ⛔ **封面签名 URL 每次重获**：IMA `get_media_info` 签名会过期
- ⛔ **不直接 patch 生成的 HTML**：修生成脚本重建，防重跑覆盖
- ⛔ **财经观察当日无料**：显式替换（AI产业链/政策周期等），不可硬凑

### 生成流程

**Phase 1 — 采集并落盘 JSON**
```bash
# 并行采集所有源 → /tmp/moyu_data/*.json
# 运行 aggregate.py 聚合 → moyu_data.json
```
中间产物落盘，便于重跑调试。

**Phase 2 — 生成 HTML**
```python
# gen_html.py 读取 moyu_data.json + obs_templates.py + cover_url.txt
# 产出单文件 moyu_daily_YYYY-MM-DD.html
```
- 双语模板见 `references/deep-observation-templates.md`（OBS_01_GEO / OBS_02_FIN）
- Claude 暖色 token 见 `html-data-report` skill
- 浮动热度 li 需 `display:flow-root` 防重叠

**Phase 3 — 质量验证**
```bash
# 1. browser_navigate file:///path/report.html
# 2. 再次 browser_navigate 同URL（刷新缓存）
# 3. browser_vision 截图查重叠/溢出/封面
# 4. 发现问题 → 改 gen_html.py → 重跑 → 回第1步
```

**Phase 4 — 上传 IMA**
```bash
node ~/.hermes/skills/ima-skills/knowledge-base/scripts/upload-to-kb.cjs \
  /path/report.html <kb_id> "摸鱼日报 | YYYY-MM-DD 星期X · 深度观察版v4.x"
```
- `upload-to-kb.cjs` 需预置 `html:20, htm:20, epub:21` 映射
- IMA 无删除接口，重做时标题带版本后缀区分

### 关键技术细节（从 bilingual-daily-digest 吸收）

#### 1. ZH 字典三层 fallback 翻译匹配（必读）
```python
def zh_for(en_title):
    def norm(s):
        for a, b in [("\u2019","'"), ("\u2018","'"), ("\u201c",'"'), ("\u201d",'"'), ("'","'"), ("&apos;","'")]:
            s = s.replace(a, b)
        return s
    t_norm = norm(en_title)
    k = norm(en_title[:30])
    if k in ZH: return ZH[k]
    # 第一层：归一化后前缀匹配
    for pref, tr in ZH.items():
        p = norm(pref).lstrip("'\"")[:25]
        t = t_norm.lstrip("'\"")
        if t.startswith(p): return tr
    # 第二层：ZH 表 key 也归一化查
    ZH_norm = {norm(k).lstrip("'\""): v for k, v in ZH.items()}
    if k in ZH_norm: return ZH_norm[k]
    return ""
```
**验证脚本**（生成后必跑）：
```python
import re
lis = re.findall(r"<li>.*?</li>", html_txt, re.S)
total_bi = sum(1 for li in lis if "t-en" in li)
miss_zh  = sum(1 for li in lis if "t-en" in li and 'class="zh"' not in li)
assert miss_zh == 0, f"双语缺译 {miss_zh} 条，需补 ZH 字典"
```

#### 2. ZH 字典 value 不能含 ASCII 双引号
写翻译时若想引用术语（如 `"AI 原生"`），直接用 ASCII `"` 会让 Python 把字符串切断。两种解法：
- 改成中文「」：`「AI 原生」`
- 改成单引号：`'AI 原生'`

#### 3. 娱乐/瓜类深度观察的「原文照录」模板
当用户在当周明确说「要某瓜」「想看 XX 原文」「照录出来」时，按此模式做（用 `grid-column:1/-1` 占满整行作为第三条观察）。

#### 4. 微博热搜必须用 weibo.js
直接 `curl 'weibo.com/ajax/statuses/hot_band'` 99% 概率只返回 21 字节的 stub JSON。**强制**走 `node ~/.hermes/skills/ima-skills/scripts/weibo.js --json` + `raw_decode` 取首文档。

#### 5. 9:30 前 A 股指数涨跌幅显示 0 是腾讯 API 正常行为
`qt.gtimg.cn` 集合竞价阶段字段 4 (pct) 显示 `0.00`，不是解析 bug。等 9:35 后或当日 10:00 触发时再采集。

#### 6. 字段位置：A 股和美股完全相同
`v_xxx="...~price~prev_close~...~chg~pct~..."` 都是：`parts[3]`=当前价、`parts[31]`=涨跌额、`parts[32]`=涨跌幅（%）

### 已知踩坑速查（v4.2 实测沉淀）

| 报错 | 原因 | 修复 |
|------|------|------|
| `invalid media_type` | upload-to-kb.cjs 缺 20/21 | 补 MEDIA_TYPES/CONTENT_TYPES 映射 |
| `skill auth failed (200002)` | api_key 被误覆盖/过期 | 恢复 `~/.config/ima/api_key` |
| `fetch failed` | GFW无代理 | `https_proxy=http://127.0.0.1:1082` |
| CNN 返回旧文 | rss2json缓存 | 按北京时间过滤当日 + 排除该源 |
| 英文单词粘连 | HTML剥离用空串 | 标签替换为空格 |
| 排序错位 | 字符串比较两种日期格式 | 统一转 timestamp 排序 |
| 封面破图 | 签名URL过期 | 每次生成前重新 `get_media_info` |
