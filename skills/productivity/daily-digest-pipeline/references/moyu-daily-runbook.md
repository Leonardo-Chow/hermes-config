# 摸鱼日报每日生成 Runbook（v4.2，2026-08-26 全流程实测）

> 产品定义、19 板块结构、质量评分细则、数据源端点表见用户自有 skill `moyu-daily-generator`（未 adopt，只读）。本文件是当日全流程实测记录与踩坑。

## 标准流程（全程约 10 分钟）

1. **归档昨日数据**（先归档再采集）：
   ```bash
   cd /tmp/moyu_data && mkdir -p archive_<昨日日期> && mv *.json *.txt *.xml *.html archive_<昨日日期>/
   ```
   ⚠️ aggregate.py 的 `load()` 对缺失文件静默返回空、对残留文件静默复用——不归档会把昨日新闻混进今日日报且无任何报错；误删则板块悄悄变空。归档 + 聚合后逐板块核对条数是唯一防线。

2. **国内四源并行采集**：
   - A股：`qt.gtimg.cn/q=sh000001,sz399001,sz399006,sh000300`（GBK→UTF8 存 `astock_utf8.txt`）；美股 `usDJI,usIXIC,usINX` 同理
   - 微博：`node weibo.js --json` —— **JSON 在 stdout 的 `--- JSON OUTPUT ---` 标记之后**，前面是人读表格，直接 `json.load(sys.stdin)` 会炸。解析：`out.find(marker)` 后取剩余部分
   - 百度/抖音：直接 curl API（端点见 data-sources.md）
   - terminal 工具不支持 `&` 后台并行，用 execute_code 循环 subprocess

3. **RSS 采集**：rss2json 优先，失败走降级（见 SKILL.md）

4. **HN 免 VPN**：Firebase API 被墙；rss2json 的 hnrss 也可能返回空。**直连 `https://hnrss.org/frontpage` XML 可用**（无需 VPN）。item id 从 comments URL 正则 `id=(\d+)` 提取；⚠️ points/score 字段可能缺失——前端渲染直接省略分数，不要显示 "0 pts"

5. **聚合** `python3 aggregate.py` → 打印各板块条数，**任何 0 条板块必须排查**（文件名对不上是常见原因，如 rss_tcv.xml 需复制为 aggregate.py 认的 rss_verge.json）

6. **改 gen_html.py 每日硬编码**（见下方清单）→ 生成 HTML

7. **质量评分 ≥70** 才可上传（国际来源≥5家=15分，4家=10分及格；CNN/NYT/Reuters/AP 历史验证均不稳，4 家是常态，不必硬凑）

8. **刷新封面签名 URL**（get_media_info）→ 上传 IMA 知识库

## rss2json 失败降级实测（2026-08-26）

| 源 | rss2json | 直连 XML→转换 |
|----|----------|---------------|
| MarketWatch | ❌ error | ✅ |
| Yahoo Finance | ❌ error | ✅ (50 items) |
| Variety | ❌ error | ✅ |
| Business Insider | — | ❌ 空（放弃即可） |

财经混源 CNBC+MarketWatch 即达标 ≥2 家。FT/WSJ rss2json 均失败属常态。

## gen_html.py 每日必改清单（漏改 = 昨日内容泄漏上线）

- [ ] 深度观察正文 OBS_01/OBS_02（500-1000字×2 四段式：事件是什么/前因后果/可能带来的影响/未来发展推演；可外置 obs01.py/obs02.py import）
- [ ] 两张 obs_card 卡片标题
- [ ] `ZH` 翻译映射（key=英文标题前 30 字符）
- [ ] `GH_ZH` / `HN_ZH` 中文介绍映射
- [ ] `hot_list()` 内 `NOTES` 热搜简析映射
- [ ] 各板块 `sec-lede` 导语（今日主线概括）
- [ ] footer 版本号与日期
- [ ] 输出路径 out_path 的日期（若硬编码）

自检：`grep 前一日日期 gen_html.py` 应 0 hits 再生成。

## 质量评分实现要点（94/100 实测通过）

用正则从生成后的 HTML 提取验证，不靠目测：
- 板块完整性：8 个 section 标题逐个 in html
- 内容深度：`class="note"` + `class="zh"` 计数 >60 得满分
- 国际来源多样性：从 intl section 提取 `<a href>` 域名去重计数（不能用 `\[来源\]\(URL\)` 格式匹配）
- 链接落地页率：统计以 `.com/` `.org/` 结尾的首页级链接数
- 封面图：`class="cover"` + `res-skb.ima.qq.com` 同时存在
