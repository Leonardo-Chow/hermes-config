# OBSBOT/Insta360 产品竞品监控 — 文件夹结构和文档格式

## 腾讯文档文件夹结构

| 文件夹 | ID | 用途 |
|--------|-----|------|
| OBSBOT | `DjbGtzenXmbX` | 顶层文件夹 |
| OBSBOT/Youtube | `DHtSaueQJaKb` | YouTube 视频数据+评论 |
| OBSBOT/油管分析 | `DlkJNZtuHMPF` | YouTube 评论 Word 文档 |
| OBSBOT/Amazon | `DKQjkLCCkwLR` | Amazon 评论文档 |

## 产品 ASIN 映射

| 产品 | Amazon ASIN |
|------|-------------|
| OBSBOT Tiny 3 | `B0G636CXQM` |
| Insta360 Link 2C | `B0DDTGY8FG` |
| Insta360 Link 2C Pro | `B0G3SSQMJQ` |

## 文档格式标准

### YouTube 评论 Word 文档
- 标题居中：`{品牌} {产品} YouTube 视频评论分析报告`
- 信息区：日期 + 视频数 + 评论总数 + 有评论视频数
- 📊 视频总览表格（Light Grid Accent 1 样式，7列）
- 📝 按视频分节：🎬标题h2 + 频道+评论数 + 蓝色链接 + 评论列表
- 每条评论：@作者加粗 + (👍N, 日期)灰色 + 正文9pt

### Amazon 评论 Word 文档
- 标题：`{品牌} {产品} - Amazon Customer Reviews`
- 📊 Rating Breakdown 表格（5→1星含数量百分比）
- 按地区分组（🇺🇸 US / 🌍 Other Countries）
- 每条：星级+作者+日期+✓Verified+标题加粗+正文+👍有用票数

### Reddit 讨论 Word 文档
- 每个帖子：标题h2 + u/author | r/sub | Score | Comments | date
- 蓝色URL链接 + Post Content + User Comments（限15条/帖）

## ⚠️ 关键 Pitfalls

- **不要重新搜索YouTube**：用户表格里已有视频链接，用 get_content 直接读取
- **Reddit 不要用 curl/API/浏览器**：全部被封(403)，只能用 Camoufox Scrapling
- **表格解析**：标题含 `|` 导致列错位，从 URL 端反向解析
- **sheet.set_range_value** 必须用 key=value 格式，--args 会报错
