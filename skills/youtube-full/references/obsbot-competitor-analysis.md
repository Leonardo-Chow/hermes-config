# OBSBOT Competitor Analysis Workflow Reference

## Overview

This workflow analyzes YouTube videos for OBSBOT competitors (ATEM Mini Extreme, RODECaster Video, ATEM Mini Pro, etc.) and generates structured analysis reports for Talent 2 product launch strategy.

## Data Sources

| Source | Tool | Purpose |
|:-------|:-----|:--------|
| YouTube video titles/tags | TranscriptAPI | Get video metadata |
| YouTube comments | Browser + JS extraction | User feedback analysis |
| Competitor docs | Tencent Docs `get_content` | Existing research data |
| Template format | Tencent Docs `get_content` | Output format reference |

## Template Structure (from Talent 2 youtube数据分析)

```
|网红ID|渠道链接|网红类型|受众地区|量级（k）|案例视频|关键词铺设（Keywords / Hashtags）|场景|Pros|Cons|结论|
```

### Column Details

1. **网红ID**: Creator name/handle
2. **渠道链接**: YouTube channel URL
3. **网红类型**: Product Review / Tutorial/Education / Livestream / Church Production / Music Production / Podcast Production
4. **受众地区**: Country/Region (e.g., "United States/美国", "France/欧洲")
5. **量级（k）**: Subscriber count in thousands
6. **案例视频**: Specific video URL used for analysis
7. **关键词铺设**: ✅标题: [title] + ✅标签: [tags/hashtags]
8. **场景**: Use case category
9. **Pros**: ✅ User-recognized features (with emoji bullets)
10. **Cons**: ❌ User complaints (with emoji bullets)
11. **结论**: Structured analysis with:
    - 目标人群画像 ✅
    - 主推场景（关键词）✅
    - 可解决的用户痛点 ✅
    - 未满足的用户痛点 ⚠️
    - 主推功能 ✅

## Writing Style Rules

- Use ✅ and ❌ emoji for Pros/Cons bullets
- Use 🎯 for target audience, 🎬 for scenarios, 🔥 for core pain points
- Bold key terms with **text**
- Include specific user quotes from comments when relevant
- Compare with competitors explicitly
- Structure conclusions with numbered sections
- Use tables for structured data

## Key File Locations

- Template: `DquLvjLfcIqQ` (Talent 2 youtube数据分析)
- ATEM Mini Extreme: `DnRZguRDXifQ`
- RODECaster Video: `DUuQNTwdMIMK`
- ATEM Mini Pro: `DGrETsTcAWRN`
- Talent2调研数据 folder: `DPIZlPqPflSU`

## Workflow Steps

1. Read template document to understand format
2. Read competitor analysis documents for existing data
3. Extract video URLs from competitor docs
4. Get video titles/tags via TranscriptAPI
5. Get comments via browser (scroll + JS extraction)
6. Create analysis document matching template style
7. Move to Talent2调研数据 folder
