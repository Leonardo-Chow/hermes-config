# YouTube 评论深度爬取 + 分析

当需要对指定视频列表进行深度评论分析（而非仅检查 OBSBOT 提及）时，使用此流程。

## API 端点

```
GET https://www.googleapis.com/youtube/v3/commentThreads
参数：
  videoId=VIDEO_ID
  part=snippet
  maxResults=100（最大值）
  order=relevance（按相关性排序，top-level comments）
  textFormat=plainText
  pageToken=NEXT_PAGE_TOKEN（分页）
```

每次调用消耗 **1 单位配额**。每个视频最多 500 条评论 = 5 次调用。

## 分页逻辑

```python
comments = []
page_token = None
while len(comments) < max_comments:
    params = {"videoId": video_id, "part": "snippet", "maxResults": "100",
              "order": "relevance", "textFormat": "plainText"}
    if page_token:
        params["pageToken"] = page_token
    data = api_call("commentThreads", params)
    items = data.get("items", [])
    if not items:
        break
    for item in items:
        s = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "id": item["id"],
            "author": s.get("authorDisplayName", ""),
            "text": s.get("textDisplay", ""),
            "likes": s.get("likeCount", 0),
            "published": s.get("publishedAt", ""),
            "reply_count": item["snippet"].get("totalReplyCount", 0),
        })
    page_token = data.get("nextPageToken")
    if not page_token:
        break
```

## SOCKS5 代理

YouTube API 在中国大陆被墙，必须走代理。

**⚠️ 关键发现**：`requests` 库直接设置 `session.proxies` 时 SOCKS5 代理可能报 `Connection refused`。**用环境变量更可靠**：

```bash
# 推荐方式：环境变量
HTTPS_PROXY=socks5h://127.0.0.1:1082 HTTP_PROXY=socks5h://127.0.0.1:1082 python3 script.py

# 或在 Python 中设置
import os
os.environ["HTTPS_PROXY"] = "socks5h://127.0.0.1:1082"
os.environ["HTTP_PROXY"] = "socks5h://127.0.0.1:1082"
```

需要 `pip3 install requests[socks]`（PySocks + urllib3 socks 支持）。

## 评论情感过滤（精准甄别）

### 核心问题

关键词匹配会产生大量误判。必须区分：
- ✅ **真实吐槽/问题**：用户明确表达产品不满
- ❌ **误判**：正面评价中包含负面词、购买意向、纯互动、音乐/演出评论

### 强负面词（直接命中 = 吐槽）

```
doesn't work, don't work, not working, won't work
broken, broke, failed, failure, defective, dead
terrible, horrible, awful, worst, trash, garbage, junk, scam
waste of, rip off, regret buying, regret getting
disappointed with, disappointing, very disappointed
frustrating, frustrated with, annoying
return it, send it back, money back, refund
overheating, overheats, too hot
disconnect constantly, keeps disconnecting, drops connection
major latency, huge lag, unacceptable lag
doesn't track, can't track, tracking fails, tracking issue
crashes constantly, keeps crashing, freezes
not worth the price, waste of money
stopped working, quit working, broke after
poor quality, bad quality, low quality
software is terrible, app is terrible, software is buggy
```

中文强负面：
```
严重延迟, 严重卡顿, 经常断连, 发热严重, 噪音很大
不好用, 没法用, 无法使用, 质量差, 后悔买了, 退货
```

### 必须排除的模式（不是吐槽）

```python
EXCLUDE_PATTERNS = [
    # 纯正面
    r"\bi love\b", r"\bamazing\b", r"\bawesome\b", r"\bfantastic\b",
    r"\bgreat camera\b", r"\bgreat review\b", r"\bgreat video\b",
    r"\bexcellent\b", r"\bperfect\b", r"\blove the\b", r"\blove this\b",
    r"\bthank you\b", r"\bthanks for\b", r"\bkeep up\b", r"\bgood job\b",
    # 购买意向
    r"\bwant to buy\b", r"\bgoing to buy\b", r"\bplanning to\b",
    r"\bi need this\b", r"\bgrabbing one\b", r"\bgetting one\b",
    # 误判保护
    r"\bhard pass\b",           # "hard pass" on competitor = 正面
    r"\bcan't wait\b",          # 兴奋 = 正面
    r"\bwell worth\b",          # 值得 = 正面
    r"\bto bad i got\b",        # 后悔买竞品 = 不是吐槽 OBSBOT
    r"\bthey don't get more\b", # 说 OBSBOT 应该更火 = 正面
    # 音乐/演出视频的评论（通常与产品无关）
    r"\bpremiere\b", r"\bpremier\b",
    r"\bmix\b", r"\bset\b", r"\bdj\b",
    r"\bmelodic techno\b", r"\bprogressive house\b",
]
```

### 判定逻辑

```python
def is_real_complaint(text):
    text_lower = text.lower().strip()
    if len(text_lower) < 20:        # 过短评论无意义
        return False, 0, []
    if len(re.sub(r'[^a-zA-Z\u4e00-\u9fff]', '', text_lower)) < 8:  # 纯符号/表情
        return False, 0, []

    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, text_lower):
            return False, 0, []

    strong_hits = [kw for kw in STRONG_NEGATIVE if kw.lower() in text_lower]
    if strong_hits:
        return True, len(strong_hits) * 2, strong_hits

    return False, 0, []
```

**阈值**：仅 `strong_hits` 命中时才算吐槽。弱负面词（wish/hope/need/lack）单独出现不算。

### 实际效果（693条评论测试）

| 版本 | 筛出吐槽 | 问题 |
|------|---------|------|
| v1（宽泛关键词） | 75条 | 大量误判（"I love how..."、音乐评论） |
| v2（加排除模式） | 2条 | 排除太严 |
| v3（强负面词 + 精确排除） | 1-2条 | 最精准，只有真实吐槽 |

**结论**：YouTube 视频评论中真实吐槽非常少（<1%），大部分是正面评价或中性讨论。宁可漏掉弱吐槽，也不要误判正面评论。

## 用户关心点分类

```python
CONCERN_KEYWORDS = {
    "画质/图像质量": ["image quality","4k","1080p","sharp","blur","blurry","grain","noise","color","exposure","low light","hdr"],
    "AI Tracking/追踪": ["tracking","track","follow","auto track","gesture","lose track","lost track"],
    "云台/稳定/转动": ["gimbal","stabiliz","pan","tilt","rotate","smooth","shake","jitter","drift"],
    "兼容性": ["compatible","work with","zoom","teams","meet","obs","streamlabs","discord"],
    "安装/设置": ["install","setup","mount","clamp","tripod","instruction","manual"],
    "连接/接口": ["connect","usb","hdmi","wireless","wifi","bluetooth","dongle","disconnect","lag","latency"],
    "软件/App": ["software","app","firmware","update","bug","crash","freeze","error"],
    "价格/性价比": ["price","expensive","cheap","value","worth","budget","overprice"],
    "售后/客服": ["support","service","warranty","return","refund","repair"],
    "音频/麦克风": ["audio","microphone","mic","sound","noise cancel","voice"],
    "对焦/变焦": ["focus","autofocus","zoom","bokeh"],
    "散热/噪音": ["heat","hot","warm","fan","noise","noisy","buzzing"],
    "竞品对比": ["insta360","logitech","elgato","dji","meet","tiny","compared","better than","alternative"],
}
```

## 应用场景分类

```python
SCENARIO_KEYWORDS = {
    "直播/推流": ["stream","streaming","live stream","obs","streamlabs","twitch"],
    "视频会议": ["zoom","teams","meet","skype","conference","call"],
    "视频录制/内容创作": ["record","recording","content","youtube video","tutorial","vlog","podcast"],
    "音乐/演出": ["music","concert","performance","stage","band","guitar","piano","dj"],
    "摄影/摄像": ["photo","photography","camera","filming","cinema"],
    "教育/教学": ["teach","teaching","class","lecture","education"],
    "电商/带货": ["ecommerce","product","sell","shop","review","unboxing"],
    "游戏": ["game","gaming","esports"],
    "播客": ["podcast"],
    "教堂/宗教": ["church","worship","sermon"],
    "运动/健身": ["sport","fitness","workout","yoga"],
}
```

## Word 文档生成（python-docx）

### 依赖

`pip3 install python-docx`（已安装）

### 表格样式

```python
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.enum.table import WD_TABLE_ALIGNMENT

def set_cell_shading(cell, color_hex):
    """设置单元格背景色"""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def set_table_style(table, header_color="2B579A", stripe_color="F2F6FC"):
    """蓝色表头 + 斑马纹"""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell in table.rows[0].cells:
        set_cell_shading(cell, header_color)
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.bold = True
                run.font.size = Pt(9)
    for row_idx in range(1, len(table.rows)):
        if row_idx % 2 == 0:
            for cell in table.rows[row_idx].cells:
                set_cell_shading(cell, stripe_color)
        for cell in table.rows[row_idx].cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(8.5)
```

### 用户格式要求

- **来源 URL 用纯文本**，不要超链接。直接写 `https://www.youtube.com/watch?v=VIDEO_ID`
- **表格列**：序号、评论内容、涉及领域、用户关心点、应用场景、严重度、点赞、评论者、来源视频、来源URL
- **封面**：标题 + 副标题 + 日期 + 统计摘要
- **目录**：7 章结构
- **斑马纹表格**：不同章节用不同表头颜色区分（蓝/红/橙/绿/紫）

### 报告结构

```
封面
目录
一、评论总览（表格：指标/Tail 2/Tail Air）
二、视频列表（表格：标题/频道/日期/播放量/评论数/来源URL）
三、用户关注点统计（表格：关注点/Tail 2/Tail Air/总计/占比）
四、⚠️ 用户吐槽/问题汇总（重点）
   - Tail 2 问题评论表格（含：用户关心点、应用场景列）
   - Tail Air 问题评论表格（含：用户关心点、应用场景列）
   - 问题热点汇总（表格：类别/次数/典型摘录）
   - 应用场景分布（表格：场景/问题数）
五、各关注点详细评论（按关注点分组，每个最多15条）
六、高赞评论 Top 20
七、关键发现与建议
```

## 配额估算

| 操作 | 14个视频 | 说明 |
|------|---------|------|
| videos.list（批量） | 1 单位 | 14个ID一次请求 |
| commentThreads.list | ~70 单位 | 每视频约5次分页 |
| **总计** | ~71 单位 | 占每日配额 0.7% |
