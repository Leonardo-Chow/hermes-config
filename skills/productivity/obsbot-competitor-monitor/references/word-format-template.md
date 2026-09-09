# Word 文档格式参考

## 参考模板文件

`/Users/zhoulong/Downloads/2026-06-12——视频上线监测——上午.docx`

这是 OBSBOT 自己的上线监测报告格式，竞品监测报告应参照此格式。

## 格式要点

1. **标题**：居中，Heading 0，"竞品视频上线监测"
2. **日期信息**：Normal 样式，3 行（日期、搜索范围、数据来源）
3. **全平台搜索结果**：Heading 1
4. **各平台**：加粗段落，如 "YouTube（N条）"
5. **每个视频**：编号段落 + 博主/链接/竞品/类型/发布时间/播放量等详情
6. **统计汇总**：Heading 1 + 表格（平台数量、竞品覆盖情况、过滤说明）

## 表格样式

- 使用 `Table Grid` 样式
- 表头行加粗
- 列宽适中，不要太窄

## 字体

- 默认字体：微软雅黑
- 默认字号：10pt
- 标题字号：16pt（Heading 0）
- 章节标题：12pt（Heading 1）

## 精确版式（2026-09-08 由 9-07 报告逆向得出，python-docx 复刻成功）

文件名：`YYYY-MM-DD——竞品检测报告——时间范围（M.D-M.D）.docx`，存 Downloads。

**顶部**：
- 居中加粗 16pt：`竞品视频上线监测`
- 3 行 Normal：`日期：2026年9月8日（周二）` / `搜索范围：9月7日（周一）~ 9月8日（周二）UTC` / `数据来源：YouTube Data API`

**每条视频 = 7 行块**（Normal 10pt，编号连续）：
1. `N. <完整视频标题>`
2. `博主：<channelTitle>`
3. `链接：https://www.youtube.com/watch?v=<id>`
4. `竞品：<品牌> | 量级：KOL/KOC | 类型：YTB Shorts/Dedicated Video/Tutorials/Comparison | 时长：M:SS`
5. `发布时间：YYYY-MM-DD`
6. `播放量：1,250 | 点赞：27 | 评论：0 | 互动率：2.16%`（千分位逗号；互动率=(点赞+评论)/播放量）
7. 空行

**统计汇总（Heading 1 后接 5 张 Table Grid 表，表头加粗 9pt）**：
1. 平台数量：平台/数量（YouTube、TikTok、Instagram、X/Twitter、合计）
2. Content Type：YTB Shorts / YTB Dedicated Video / YTB Tutorials / YTB Comparison 计数
3. 竞品覆盖：`竞品/状态`，格式 `有新视频（N条）`
4. 量级：KOL/KOC 计数
5. 过滤说明：表头 `频道/视频/原因`，逐行列出被过滤项（mention-only、>1h 直播、黑名单、批量频道、AI/带货、非监测型号等），每行给出具体原因
