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
- `bilingual-daily-digest`：双语深度摘要变体
