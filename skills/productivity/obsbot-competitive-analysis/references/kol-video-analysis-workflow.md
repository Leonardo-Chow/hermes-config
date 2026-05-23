# KOL 视频分析工作流

当需要分析 OBSBOT KOL 合作视频时，执行以下完整流程。

## 流程概览

```
YouTube 视频 URL
  → TranscriptAPI 获取字幕
  → 上传字幕到腾讯文档（OBSBOT → 红人视频）
  → 按工作流程格式生成视频解析
  → 上传解析到 IMA OBSBOT 知识库
```

## Step 1: 获取 YouTube 字幕

```bash
export TRANSCRIPT_API_KEY="sk_..."  # 从 ~/.zshenv 加载

curl -s "https://transcriptapi.com/api/v2/youtube/transcript\
?video_url=VIDEO_URL&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: HermesAgent/0.11.0"
```

**⚠️ 注意**：`format=text` 时 `transcript` 字段是**字符串**（不是数组），格式为：
```
[0.32s] Hey chicos, gracias por estar una vez
[1.68s] más en este canal.
```

**保存字幕**：写入 `/tmp/transcript_text.txt`，格式：
```markdown
# {视频标题}

视频链接: {url}
频道: {频道名} ({频道链接})
语言: {语言代码}

---

{字幕内容}
```

## Step 2: 上传字幕到腾讯文档

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

## Step 3: 按工作流程格式生成视频解析

解析必须包含以下结构（参考 IMA OBSBOT 知识库中已有格式）：

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

### 关键字段说明

| 字段 | 来源 | 说明 |
|:-----|:-----|:-----|
| 博主类型 | 视频内容/频道介绍 | 具体化，如 Livestream/Camera/Tutorial |
| 红人量级 | 播放量判断 | 头部(>100K均播)/中腰部(10-100K)/尾部(<10K) |
| 视频内容 | 字幕分析 | 分点详细描述，不要只写标题 |
| 视频亮点 | 综合分析 | 从营销角度分析，含可复用的经验 |

## Step 4: 上传解析到 IMA OBSBOT 知识库

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
