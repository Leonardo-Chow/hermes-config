# Cross-Platform KOL Research Workflow

## 概述

从已有 KOL 名单出发，跨 YouTube/Instagram/X/TikTok/Google 搜索补充信息的完整流程。

## 搜索查询模板

```
# YouTube 频道
"FirstName LastName YouTube channel"
"FirstName LastName filmmaker"
"site:youtube.com FirstName LastName"

# 社交媒体
"FirstName LastName Instagram"
"FirstName LastName Twitter OR X.com"

# 任职机构/纸媒
"FirstName LastName company affiliation"
"FirstName LastName cinematographer photographer publication"
"FirstName LastName DP gaffer studio"
```

## 并行分批策略

### delegate_task 分 3 路

每路 ~18 人，各自搜索 + 写 JSON：

```json
// /tmp/kol_batchN.json 格式
[
  {
    "first_name": "Matti",
    "last_name": "Haapoja",
    "youtube_url": "https://www.youtube.com/@MattiHaapoja",
    "subscriber_count": "~1.2M",
    "instagram": "@mattihaapoja",
    "twitter_x": "@mattihaapoja",
    "tiktok": null,
    "affiliation": "TravelFeels (Founder), Finnish filmmaker",
    "notes_update": "芬兰知名旅行电影制作人"
  }
]
```

### 超时处理

1. 第一次超时 → 检查 /tmp/kol_batchN.json 是否有部分数据
2. 第二次超时 → 放弃该批次的委托，用 training knowledge 补全
3. Training knowledge 覆盖率：头部创作者 ~90%，中腰部 ~50%，专业 DP/Gaffer ~10%

## Tavily 配额预算

| 任务规模 | 预估搜索次数 | 配额消耗 | 策略 |
|:---------|:-------------|:---------|:-----|
| 10 人 | 30-50 | 可承受 | 全部用 Tavily |
| 20 人 | 60-100 | 超限 | Tavily 头部 + knowledge 中腰部 |
| 55 人 | 165-275 | 远超限 | Tavily 仅用于最有价值的 5-8 人 |

## Excel 输出模板

```python
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# 样式定义
header_font = Font(bold=True, color="FFFFFF", size=11)
header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
found_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")     # 绿色
not_found_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid") # 橙色

# 列结构
headers = [
    "First name", "Last name", "Type", "ROI",
    "YouTube Channel", "YouTube Subscribers",
    "Instagram", "X/Twitter", "TikTok",
    "Affiliation / Employment",
    "Notes"
]

# 条件高亮
for col in [5, 6, 7, 8, 9, 10]:  # Channel, Sub, IG, X, TikTok, Affiliation
    if cell.value:
        cell.fill = found_fill
    else:
        cell.fill = not_found_fill
```

## 已知 KOL 参考数据（2026-06-04 验证）

### Batch 1 头部创作者

| 姓名 | YouTube | Subs | Instagram | Affiliation |
|:-----|:--------|:-----|:----------|:------------|
| Marques Brownlee (MKBHD) | @mkbhd | ~19M | @mkbhd | MKBHD Studios / Studio 1A |
| Justine Ezarik (iJustine) | @ijustine | ~7M | @ijustine | iJustine Inc. |
| Justin Brown (PrimalVideo) | @PrimalVideo | ~4M | @primalvideo | Primal Video (Founder) |
| Martijn Doolaard | @MartijnDoolaard | ~1.5M | @martijndoolaard | Author & Filmmaker |
| Jesse Driftwood | @JesseDriftwood | ~1M | @jessedriftwood | Independent |
| Bharat Bala | @virtualbharat | ~500K | @bharatbala | Virtual Bharat (Founder) |
| Damien Bernal | @DamienBernal | 268K | @damienbernal | Independent |
| Daniel Aucoin | @DanielAucoinFineArt | 261K | @danielaucoin | Fine Art Photography |
| Hugh Brownstone | @HughBrownstone | ~200K | @hughbrownstone | OneBrownStar |
| Matthew Allard | @Newsshooter | ~200K | @matthewallard | Newsshooter (Editor & Co-Owner) |

### Batch 3 头部创作者

| 姓名 | YouTube | Subs | Instagram | Affiliation |
|:-----|:--------|:-----|:----------|:------------|
| Casey Neistat | @caseyneistat | ~12.5M | @caseyneistat | 368 / Beme (CNN) |
| Peter McKinnon | @PeterMcKinnon | ~8-9M | @petermckinnon | — |
| Tony & Chelsea Northrup | @TonyNorthrup | ~2M | @chelseanorthrup | Northrup Photography |
| Gregory Austin McConnell | @AustinMcConnell | ~1.5M | @austinmcconnell | — |
| Isabel Paige | @IsabelPaige | ~1.5M | @isabelpaige_ | — |
| Manny Ortiz | @MannyOrtiz | ~1M | @mannyortizphoto | — |
| Paul Ripke | @PaulRipke | ~500K | @paulripke | — |

### Batch 2 中腰部

| 姓名 | YouTube | Subs | Instagram | Affiliation |
|:-----|:--------|:-----|:----------|:------------|
| Matti Haapoja | @MattiHaapoja | ~1.2M | @mattihaapoja | TravelFeels (Founder) |
| Brandon Li | @BrandonLi | ~1.2M | @brandonli | Independent filmmaker |
| Faruk Korkmaz | @iPhoneDo | ~500K | @farukkorkmaz | iPhoneDo (Turkish tech) |

### 数据稀疏群体（需手动验证）

专业 DP/灯光师类，公开社交媒体信息极少：
- Richard Götze, Anthony Gugliotta, Arnulfur Hakonarson, Fred Johnny Hammerø
- Zach Hellmuth, Ben Johnson, Tom Keller, Boram Kim, Minjae Kim
- Lera Kogan, Michel Koschorrek, Kyrre Kristoffersen, Philip Lemoine
- Stephanie Liao, Charles Liu, Jamie Mills, Nikita Miroshnikov
- Takeshi Nakasu, Mirko Peek, Helmut Prein

**建议**：这些人的信息可通过 LinkedIn 或行业数据库（如 IMDb Pro、Cinematography Database）补充。
