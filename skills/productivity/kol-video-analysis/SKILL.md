---
name: kol-video-analysis
description: 解析KOL营销视频，生成符合OBSBOT内部文档格式的视频分析报告。
---

# KOL视频解析

## 触发条件

用户要求分析、解析某个YouTube视频的KOL内容，或者要求"写一个KOL优秀视频解析"。

## 核心流程

### 1. 读取参考文档（必须首先执行）

**每次必须首先读取** `~/Downloads/KOL & 产品营销视频对接 (1).docx`，学习其格式、语言风格和层级结构。这是唯一权威的格式参考，不要凭记忆或猜测。

关键格式特征：
- 标题格式：`视频：简短标签`（如"视频：深度测评"、"视频：竞品横评"）
- ✅视频链接/标题/概述/上线时间/博主
- 概述一句话说清视频侧重什么、博主认可度、适用场景
- 正文用小标题 + 普通段落，**不用bullet list**
- 子要点直接用独立段落，不要用符号引导
- 截图建议**嵌入正文段落内**，格式：`(截图建议：时间点，描述)`，不要单独放最后
- 总结格式：适用人群/核心价值/不足/结论

### 2. 获取视频数据

**依赖安装**：每次在新的 sandbox 中运行前，先安装依赖：
```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api", "PySocks", "python-docx", "-q"])
```

**字幕获取（首选方案）**：
```python
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1082'
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1082'
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['en', 'zh-Hans', 'zh-Hant'])
```

**字幕获取（备选方案）**：当 `youtube_transcript_api` 返回 `RequestBlocked` 时，改用 yt-dlp + Chrome cookies：
```bash
yt-dlp --cookies-from-browser chrome --proxy socks5://127.0.0.1:1082 \
  --write-auto-subs --sub-lang en --sub-format vtt --skip-download \
  --ignore-no-formats-error -o "/tmp/vt_%(id)s" "URL"
```
VTT 字幕含重复时间戳，需解析清理：按 `\n\n` 分割 cue block，提取时间戳和文本，去重后保存。

**视频信息提取**：
- 标题/博主：`curl -s "URL" | grep` 从页面 HTML 提取（优先）
- oembed API 备选：`curl "https://www.youtube.com/oembed?url=URL&format=json"`
- 上线时间：同上，curl 提取 `publishDate`
- 不要用浏览器打开YouTube页面

### 3. 语言风格

- 简洁，每句话有信息量
- 用"博主展示了""博主认为""博主形容"等自然描述
- **禁止使用**：首先/其次/最后/总之/综上所述/值得注意的是/这是一个优秀的/这个视频具有
- 不写大段评价性文字，用事实和博主原话说话
- 涉及对比时，客观描述双方优劣，不偏袒

### 4. 截图建议

- 嵌入正文对应段落末尾，格式：`(截图建议：MM:SS，简短描述)`
- 可以有多个截图建议，用分号分隔
- 不要在文档末尾单独建表格

### 5. 输出

- 生成Word文档，保存到 `~/Downloads/`
- 文件名使用全新命名，不要重复使用之前的文件名
- 用 `open` 命令打开文档供用户确认

## 常见错误

- ❌ 不先读参考文档就开始写
- ❌ 截图建议单独放最后
- ❌ 使用bullet list
- ❌ 出现AI套话（首先/其次/总之等）
- ❌ 大段评价性总结
- ❌ 文件名与之前重复
- ❌ `youtube_transcript_api` 报 `RequestBlocked` 时不切换备选方案；应立即改用 `yt-dlp --cookies-from-browser chrome`
- ❌ 不先装依赖就直接运行（每次 sandbox 都是全新环境）
