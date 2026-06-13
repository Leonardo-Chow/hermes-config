---
name: kol-video-analysis
description: "KOL优秀视频解析 — 分析KOL视频内容，提取产品亮点，生成结构化Word文档。适用于OBSBOT及类似品牌的产品营销视频分析。"
platforms: [linux, macos, windows]
triggers:
  - "视频解析"
  - "KOL视频分析"
  - "优秀视频"
  - "video analysis"
  - "KOL review"
---

# KOL优秀视频解析

## When to use

当用户要求分析KOL视频、创建视频解析文档、提取产品亮点时使用。典型场景：
- 分析YouTube/TikTok/B站KOL的产品评测视频
- 提取视频中OBSBOT（或其他品牌）产品的展示亮点
- 生成模仿内部文档风格的结构化Word文档

## 前置条件

- YouTube视频字幕获取能力（参考 `youtube-content` skill）
- python-docx（`pip install python-docx`）
- 参考文档（用户提供的风格模板）

## 工作流程

### 1. 读取参考文档，分析语言风格

```python
from docx import Document
doc = Document(reference_doc_path)

# 提取段落和表格
paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
```

**分析要点**：
- Emoji使用习惯（如✅前缀）
- 标点符号偏好（中文/英文标点比例）
- 常用词汇（博主、视频、产品、功能、场景、推荐等）
- 文档结构（链接→标题→概述→时间→亮点分析）
- 语气特征（专业但不生硬，营销文案风格）

### 2. 获取视频字幕并分析

```python
import os
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1082'

from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['en', 'zh-Hans', 'zh-Hant'])
```

**分析框架**：
- 视频主题和目标受众
- 产品展示的时间点和方式
- 博主对产品的评价（正面/中性/负面）
- 功能演示的完整性
- 与竞品的对比（如有）

### 3. 提取产品亮点

**OBSBOT产品亮点维度**：
- **兼容性**：官方支持的设备/平台列表
- **易用性**：连接、设置、操作的简便程度
- **AI功能**：追踪、手势控制、自动构图
- **画质**：传感器、分辨率、低光表现
- **音频**：内置麦克风、降噪、音频模式
- **设计**：体积、材质、安装方式
- **软件**：OBSBOT Studio功能、固件更新

### 4. 生成Word文档

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 标题
title = doc.add_heading('KOL优秀视频解析', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 视频基本信息（使用✅前缀）
doc.add_heading('视频基本信息', level=1)
p = doc.add_paragraph()
p.add_run('✅视频链接：').bold = True
p.add_run(video_url)
# ... 其他字段

# 核心亮点分析
doc.add_heading('核心亮点分析', level=1)
# 按维度分节，每节2-3句话

# 博主优秀之处
doc.add_heading('博主优秀之处', level=1)
# 分析博主的表达技巧和内容策略

# 截图建议（表格形式）
doc.add_heading('截图建议', level=1)
table = doc.add_table(rows=N, cols=3)
table.style = 'Table Grid'
# 列：时间点 | 截图内容 | 截图目的

# 总结
doc.add_heading('总结', level=1)
```

### 5. 文档结构模板

```
KOL优秀视频解析
├── 视频基本信息
│   ├── ✅视频链接
│   ├── ✅视频标题
│   ├── ✅博主
│   ├── ✅视频概述（2-3句话，侧重产品展示角度）
│   ├── ✅上线时间
│   ├── ✅观看次数
│   └── ✅视频时长
├── 核心亮点分析（3-6个维度，每个2-3句话）
├── 博主优秀之处（4-5个方面）
├── 截图建议（表格：时间点 | 内容 | 目的）
└── 总结（1段话）
```

## 语言风格要求

- **模仿参考文档**：必须读取用户提供的参考文档，分析并模仿其语言风格
- **避免AI语气**：不使用"首先/其次/最后"、"综上所述"、"值得注意的是"等AI常见词汇
- **使用KOL术语**：博主、视频、产品、功能、场景、推荐、认可、侧重、讲解
- **专业但不生硬**：用✅标记关键信息，保持营销文案的温度

## Pitfalls

- **不要重新搜索YouTube**：用户提供了视频链接，直接使用，不要自行搜索
- **语言风格必须模仿**：先读参考文档再写，不能凭空创造风格
- **截图建议要具体**：必须包含时间点、截图内容、截图目的三列
- **产品亮点要客观**：基于视频实际内容，不要过度夸大
- **VPN/代理**：获取YouTube字幕需要代理，确保PySocks已安装

## 相关技能

- `youtube-content`：YouTube字幕获取和格式化
- `obsbot-kol-screening`：KOL筛选（本技能侧重视频分析，非KOL筛选）
- `leonardo-brand`：品牌设计系统（文档视觉风格参考）
