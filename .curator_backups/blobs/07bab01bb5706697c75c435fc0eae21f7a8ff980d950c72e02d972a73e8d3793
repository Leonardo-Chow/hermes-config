# KOL 视频分析工作流

当需要分析 OBSBOT KOL 合作视频时，执行以下流程。

## 流程概览

### 完整流程（腾讯文档+IMA）

```
YouTube 视频 URL
  → 获取字幕（youtube-transcript-api 或 TranscriptAPI）
  → 获取视频元数据（curl 从页面源码提取）
  → 上传字幕到腾讯文档（OBSBOT → 红人视频）
  → 按工作流程格式生成视频解析
  → 上传解析到 IMA OBSBOT 知识库
```

### 简化流程（本地 Word 文档）

用户有时只需要本地 Word 文档，不走腾讯文档+IMA流程：

1. 获取字幕（见下方）
2. 获取视频元数据（curl）
3. 读取参考文档 `~/Downloads/KOL & 产品营销视频对接 (1).docx` 学习语言风格（⚠️必须是(1)版本，243MB，不是旧版218MB）
4. 分析字幕内容，提取 OBSBOT 产品亮点
5. 用 `templates/doc_generator.py` 生成 Word 文档到 `~/Downloads/`
6. 文件名格式：`KOL优秀视频解析_{产品名}.docx` 或 `KOL优秀视频解析_{产品名}_{竞品名}.docx`

## 获取 YouTube 字幕

### 方案A：youtube-transcript-api（推荐，免费）

```python
import os
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1082'  # GFW环境下必须

from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['en', 'zh-Hans', 'zh-Hant', 'ja', 'ko'])

full_text = ""
for entry in transcript:
    m, s = int(entry.start // 60), int(entry.start % 60)
    full_text += f"[{m:02d}:{s:02d}] {entry.text}\n"
```

## 常见陷阱

### ⚠️ 格式必须匹配 (1) 文档
最常见的错误是使用bullet list（•）和冗余的层级嵌套。模板文档使用**普通段落排列**，不要用 `List Bullet` 样式。

### ⚠️ 标题不要加博主名和产品名
格式为 `视频：简短标签`，不是 `视频1：博主名 & 产品名 - 原视频✔️`。标签应简洁描述视频类型（如"竞品横评""深度测评""多机播客搭建"）。

### ⚠️ 总结必须用要点形式
总结分析必须使用「适用人群/核心价值/不足/结论」固定结构，不要写成大段文字。

### ⚠️ 不要过度解读视频形式
描述视频内容时如实陈述即可，不要把类比手法（如拳击比赛用语）当做视频的主题大肆渲染。

### ⚠️ execute_code 每次需重装依赖
`youtube-transcript-api` 和 `PySocks` 在 execute_code 环境中不会持久，每次新会话都需要 `pip install`。安装命令：
```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api", "PySocks"])
```

- API v1.2.4 已废弃 `get_transcript()` 和 `list_transcripts()`，必须用实例方法 `api.fetch()`

### 方案B：TranscriptAPI（付费，更稳定）

```bash
export TRANSCRIPT_API_KEY=***  # 从 ~/.zshenv 加载

curl -s "https://transcriptapi.com/api/v2/youtube/transcript\
?video_url=VIDEO_URL&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANS...EY" \
  -H "User-Agent: HermesAgent/0.11.0"
```

**⚠️ 注意**：`format=text` 时 `transcript` 字段是**字符串**（不是数组），格式为：
```
[0.32s] Hey chicos, gracias por estar una vez
[1.68s] más en este canal.
```

## YouTube 元数据快速提取（curl）

无需浏览器或 API Key，直接从页面源码提取：

```bash
VIDEO_URL="https://www.youtube.com/watch?v=VIDEO_ID"
curl -s "$VIDEO_URL" | grep -o '"title":"[^"]*"' | head -1            # 视频标题
curl -s "$VIDEO_URL" | grep -o '"ownerChannelName":"[^"]*"' | head -1  # 频道名
curl -s "$VIDEO_URL" | grep -o '"publishDate":"[^"]*"' | head -1       # 上传日期（ISO格式）
curl -s "$VIDEO_URL" | grep -o '"lengthSeconds":"[^"]*"' | head -1     # 时长（秒）
```

**⚠️ GFW 环境**：这些 curl 命令需要代理。youtube-transcript-api 的代理设置不影响 curl，需单独设置：
```bash
export HTTPS_PROXY=socks5h://127.0.0.1:1082
# 或
curl -x socks5h://127.0.0.1:1082 -s "$VIDEO_URL" | grep ...
```

## 上传字幕到腾讯文档（完整流程）

```bash
# 创建智能文档
mcporter call tencent-docs create_smartcanvas_by_mdx --args '{
  "title": "OBSBOT Tiny 3 - {博主名} 字幕",
  "mdx": "{字幕内容}"
}'

# 移动到红人视频文件夹（ID: DNmTBhbgCAky）
mcporter call tencent-docs manage.move_file --args '{
  "file_id": "{file_id}",
  "target_folder_id": "DNmTBhbgCAky"
}'
```

## 视频解析文档结构

解析必须包含以下结构（参考 IMA OBSBOT 知识库中已有格式）：

### 标准结构（用于腾讯文档/IMA上传）

```markdown
视频{编号}：{博主名} & {产品名}

视频基础信息 @{负责人}
视频链接：{YouTube URL}
视频标题：{完整标题}
博主类型：{类型，如科技/直播/教会内容创作者}
红人量级：{头部/中腰部/尾部}
博主所在地区：{国家城市}
上线时间：{日期}

视频概述：
{2-3 句概述视频内容和博主风格}

视频内容：
一、{主题1}
{详细内容}

二、{主题2}
{详细内容}
...

视频亮点/复盘：
1. {亮点1标题}
   {详细分析}

2. {亮点2标题}
   {详细分析}
   ...
```

### 简化结构（用于本地 Word 文档）

参考 `templates/doc_generator.py`，严格要求以下格式（匹配 `KOL & 产品营销视频对接 (1).docx`）：

1. **标题行** — `视频：简短标签`（如"竞品横评""深度测评"），不加博主名和产品名
2. **视频基本信息** — ✅标记的链接、标题、概述、上线时间、博主
3. **内容章节** — 用加粗小标题分隔（如"价格对比""做工设计""OBSBOT核心功能"），下设普通段落形式的要点，不用bullet list
4. **博主视频优秀之处** — 从营销角度分析博主的内容创作手法，每个点用一句话描述
5. **截图建议** — 表格形式，含时间点、截图内容、建议用途
6. **总结分析** — 固定结构：适用人群/核心价值/不足/结论，要点形式

## 上传解析到 IMA OBSBOT 知识库

```bash
# 创建笔记
node ima_api.cjs "openapi/note/v1/import_doc" '{
  "title": "视频{编号}：{博主名} & {产品名}",
  "content": "{解析内容}",
  "content_format": 1
}'

# 添加到 OBSBOT 知识库（ID: mmYXYA4QIUsKj6PikZYHx1HtEhrPFvmysbEUrO4UfvQ=）
node ima_api.cjs "openapi/wiki/v1/add_knowledge" '{
  "media_type": 11,
  "note_info": {"content_id": "{note_id}"},
  "title": "视频{编号}：{博主名} & {产品名}",
  "knowledge_base_id": "mmYXYA4QIUsKj6PikZYHx1HtEhrPFvmysbEUrO4UfvQ="
}'
```

## 关键 ID

| 资源 | ID |
|:-----|:---|
| OBSBOT 知识库 | `mmYXYA4QIUsKj6PikZYHx1HtEhrPFvmysbEUrO4UfvQ=` |
| 红人视频文件夹（腾讯文档） | `DNmTBhbgCAky` |
| OBSBOT Youtube 文件夹（腾讯文档） | `DHtSaueQJaKb` |
| TranscriptAPI Key | 存储在 `~/.zshenv` |

## 已分析视频列表

视频 1-14 的解析已在 OBSBOT 知识库"工作流程"笔记中。新视频从 15 开始编号。
