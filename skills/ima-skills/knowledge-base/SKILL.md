---
name: knowledge-base
description: "IMA 知识库操作 — 上传文件、添加笔记/网页、搜索浏览。文件上传流程含 5 道安全门，需特别注意 COS token 被 shell 截断的问题。"
version: 2.0.0
tags: [ima, knowledge-base, cos, upload, file-management]
---

# Knowledge Base (知识库)

API base path: `openapi/wiki/v1` — 完整数据结构和接口参数详见 `references/api.md`。

## 接口决策表

| 用户意图                                      | 调用接口                                                               | 关键参数                                                                                           |
| --------------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 上传文件到知识库                              | `check_repeated_names` → `create_media` → COS Upload → `add_knowledge` | `media_type`（按扩展名），`knowledge_base_id`，`file_name`，`file_size`                            |
| 上传文件到知识库的某个文件夹                  | 先定位文件夹 → 同上（`folder_id` 传入目标文件夹 ID）                   | 见「文件夹操作」章节                                                                               |
| 添加网页/微信文章到知识库                     | `import_urls`                                                          | `urls`（1-10 个），`knowledge_base_id`，可选 `folder_id`（省略则根目录）                           |
| 添加笔记到知识库                              | `add_knowledge`                                                        | `media_type=11`，`note_info.content_id=<note_id>`，`knowledge_base_id`                             |
| 添加 URL（文件型）到知识库                    | `check_repeated_names` → 下载文件 → 走"上传文件"流程                   | URL 指向 PDF/Word/PPT 等文件时，按文件方式处理                                                     |
| 检查文件名是否重复                            | `check_repeated_names`                                                 | `params[].name`，`params[].media_type`，`knowledge_base_id`，`folder_id`                           |
| 获取知识库信息                                | `get_knowledge_base`                                                   | `ids`（1-20 个，不重复）                                                                           |
| 浏览知识库内容列表 / 浏览文件夹               | `get_knowledge_list`                                                   | `knowledge_base_id`，`cursor`，`limit`(1~50)，可选 `folder_id`                                     |
| 在知识库中搜索（含文件和文件夹）              | `search_knowledge`                                                     | `query`，`knowledge_base_id`，`cursor`                                                             |
| 按关键词查找知识库（用户知道名字但不知道 ID） | `search_knowledge_base`                                                | `query`，`cursor`，`limit`(1~20)                                                                   |
| 查看/了解自己有哪些知识库                     | `search_knowledge_base`（`query` 传空字符串）                          | `query: ""`，`cursor`，`limit`(1~20)                                                               |
| 添加内容但**未指定**目标知识库                | `get_addable_knowledge_base_list` → 展示列表让用户选择                 | `cursor`，`limit`(1~50)                                                                            |
| 查看原文、分析原文、导出原文                  | `get_media_info`                                                       | `media_id`；导出/下载时在 URL 后追加 `response-content-type` + `response-content-disposition` 参数 |

### `search_knowledge_base` vs `get_addable_knowledge_base_list`

| 场景                                             | 使用接口                                       | 原因                               |
| ------------------------------------------------ | ---------------------------------------------- | ---------------------------------- |
| 用户说了知识库名称（如"添加到产品文档库"）       | `search_knowledge_base`                        | 按名称搜索，找到 ID 后继续操作     |
| 用户想浏览/了解某个知识库                        | `search_knowledge_base` → `get_knowledge_base` | 先搜到 ID，再获取详情              |
| 用户想查看自己有哪些知识库（无具体关键词）       | `search_knowledge_base`（`query: ""`）         | 空 query 返回用户的所有知识库列表  |
| 用户要添加内容但**没说添加到哪个知识库**         | `get_addable_knowledge_base_list`              | 列出有权限添加的知识库，让用户选择 |
| 用户说"添加到知识库"但上下文中无法确定哪个知识库 | `get_addable_knowledge_base_list`              | 同上，不要猜测，让用户选择         |

**绝不要**在用户已明确指定知识库名称时调用 `get_addable_knowledge_base_list`。

---

## 写入类工作流

## 内置脚本

知识库目录下提供了以下脚本（位于 `scripts/`）：

- **`scripts/upload-to-kb.cjs`** — 统一文件上传脚本。内部执行 create_media → COS 上传 → add_knowledge 全流程，绕开 shell 参数截断问题。用法：`node scripts/upload-to-kb.cjs <文件路径> <知识库ID>`
- **`scripts/cos-upload.cjs`** — COS 上传脚本（仅上传步骤，需手动完成前置和后续步骤）。⚠️ 不要通过 shell 传 `--token`！
- **`scripts/preflight-check.cjs`** — 文件类型检查脚本
- **`scripts/weibo.js`** — 微博热搜获取脚本（基于微博公开API `weibo.com/ajax/side/hotSearch`）。用法：`node scripts/weibo.js [数量] [--json]`
- **`scripts/reddit.js`** — Reddit 热门内容获取脚本（通过 Tavily Extract 解析 Reddit 页面）。用法：`node scripts/reddit.js [数量] [--json]`

> **路径注意：** `ima_api.cjs` 位于 `~/.hermes/skills/ima-skills/ima_api.cjs`，不在当前工作目录。调用时需使用完整路径：`node ~/.hermes/skills/ima-skills/ima_api.cjs`

### ⛔ COS Token 截断（已知坑）
`cos_credential.token` 长度 875+ 字符，传给 shell 脚本时会被截断 → HTTP 403 InvalidAccessKeyId。
**使用 `scripts/upload-file-to-kb.cjs` 一体化脚本**，用 Node.js spawn + 内置 https 绕开 shell 参数传递：
```bash
node scripts/upload-file-to-kb.cjs /path/to/file.pdf <knowledge_base_id> "title"
```

以下 5 条规则**仅**在上传文件到知识库时适用。搜索、浏览、获取信息等读取操作不受影响。

```
GATE 1 [TYPE CHECK]
  Run preflight-check.cjs FIRST. pass=false → reject immediately.
  NEVER ask "do you still want to try?" for unsupported types.
  Video files, Bilibili/YouTube URLs, file:// URLs → tell user to use IMA desktop client.

GATE 2 [NAMING]
  add_knowledge title MUST equal file_name (with extension).
  NEVER rename, shorten, translate, or modify the original filename.
  Example: file is "音频.mp3" → title="音频.mp3", file_name="音频.mp3"

GATE 3 [DUPLICATES]
  Call check_repeated_names BEFORE create_media for ALL file uploads.
  is_repeated=true → ask user: keep both (append timestamp) or cancel.
  "Replace" is NOT supported.
  Timestamp format: {name}_YYYYMMDDHHmmss.{ext}

GATE 4 [UPLOAD EXIT]
  cos-upload.cjs non-zero exit → STOP immediately.
  Do NOT call add_knowledge. Report error to user.

GATE 5 [COS TOKEN TRUNCATION]
  NEVER pass cos_credential.token as a shell argument to cos-upload.cjs.
  The token is 800-900 chars with special chars (+, /, =, etc.) —
  shell WILL truncate it (length becomes 12-15 chars instead of 875).
  SYMPTOM: COS returns HTTP 403 "InvalidAccessKeyId" / "Access Key Id does not exist"
    even though create_media returned code=0 with valid credentials.
  FIX option A: Use the unified script `scripts/upload-to-kb.cjs` which:
    a) Calls ima_api.cjs via child_process.spawn() (no shell) to create_media
    b) Builds COS auth header (HMAC-SHA1) in-process and PUTs directly via https
    c) Calls ima_api.cjs via spawn() for add_knowledge
    All within a single Node.js process; credentials passed as JS variables, NOT CLI args.
  FIX option B: Write credentials to a temp .json file, read it from cos-upload.cjs
    (modified to accept --creds-file instead of --token).
  DEFAULT: Use option A (scripts/upload-to-kb.cjs) — it's the proven approach.
```

### 上传文件到知识库

完整流程：前置检查 → 重名检查 → 创建媒体 → COS 上传 → COS 验证 → 添加知识。

```bash
# ── Step 1: preflight-check.cjs ← ⛔ GATE 1 ──
# 有扩展名时自动推断；无扩展名时需传 --content-type
PREFLIGHT=$(node .claude/skills/ima-skill/knowledge-base/scripts/preflight-check.cjs \
  --file "/path/to/report.pdf")
echo "$PREFLIGHT"
# pass=false → 终止，将 reason 展示给用户。NEVER ask "want to try?"

# ── Step 2: Extract fields ──
FILE_NAME=$(echo "$PREFLIGHT" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(d.file_name)")
FILE_EXT=$(echo "$PREFLIGHT" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(d.file_ext)")
FILE_SIZE=$(echo "$PREFLIGHT" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(String(d.file_size))")
MEDIA_TYPE=$(echo "$PREFLIGHT" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(String(d.media_type))")
CONTENT_TYPE=$(echo "$PREFLIGHT" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(d.content_type)")

# ── Step 3: check_repeated_names ← ⛔ GATE 3 ──
# MANDATORY for ALL file uploads (media_type 1/3/4/5/7/9/13/14/15).
# is_repeated=true → ask user: keep both (append _YYYYMMDDHHmmss) or cancel.
ima_api "openapi/wiki/v1/check_repeated_names" "{
  \"params\": [{\"name\": \"$FILE_NAME\", \"media_type\": $MEDIA_TYPE}],
  \"knowledge_base_id\": \"<kb_id>\"
}"
# folder_id is optional — omit for root, include for subfolder

# ── Step 4: create_media ──
CREATE_MEDIA_RESP=$(ima_api "openapi/wiki/v1/create_media" "{
  \"file_name\": \"$FILE_NAME\",
  \"file_size\": $FILE_SIZE,
  \"content_type\": \"$CONTENT_TYPE\",
  \"knowledge_base_id\": \"<kb_id>\",
  \"file_ext\": \"$FILE_EXT\"
}")
# Extract media_id, url, and cos_credential fields. code≠0 → terminate.

# ── Step 5: Upload to COS ← ⛔ GATE 5 (use unified script to avoid token truncation) ──
# ⚠️ DO NOT pass --token via shell! Use scripts/upload-to-kb.cjs instead.
# This script handles create_media → COS upload → add_knowledge in one process.
# See: scripts/upload-to-kb.cjs for setup instructions.

# ── Step 6: add_knowledge ← ⛔ GATE 2 (title = file_name) ──
# add_knowledge will verify the file was uploaded — no separate verify step needed.
ima_api "openapi/wiki/v1/add_knowledge" "{
  \"media_type\": $MEDIA_TYPE,
  \"media_id\": \"<media_id>\",
  \"title\": \"$FILE_NAME\",
  \"knowledge_base_id\": \"<kb_id>\",
  \"file_info\": {
    \"cos_key\": \"<cos_credential.cos_key>\",
    \"file_size\": $FILE_SIZE,
    \"file_name\": \"$FILE_NAME\"
  }
}"
```

#### 批量上传时的重复处理

可一次性检查所有文件名（最多 2000 个）：

```bash
# ⛔ GATE 3 — batch check
ima_api "openapi/wiki/v1/check_repeated_names" '{
  "params": [
    {"name": "report.pdf", "media_type": 1},
    {"name": "slides.pptx", "media_type": 4},
    {"name": "data.xlsx", "media_type": 5}
  ],
  "knowledge_base_id": "<kb_id>",
  "folder_id": "<folder_id>"
}'
# 根目录时省略 folder_id。
# is_repeated=true → "以下文件已存在同名：report.pdf。是否保留两者？（不支持替换）"
# 保留两者 → append _YYYYMMDDHHmmss；取消 → remove from upload list
```

### 添加网页/微信文章到知识库

```bash
# 无需 GATE 3-5（非文件上传）
# 添加到根目录（不传 folder_id）
ima_api "openapi/wiki/v1/import_urls" '{
  "knowledge_base_id": "<kb_id>",
  "urls": [
    "https://example.com/article",
    "https://mp.weixin.qq.com/s/xxxxx"
  ]
}'

# 添加到指定文件夹
ima_api "openapi/wiki/v1/import_urls" '{
  "knowledge_base_id": "<kb_id>",
  "folder_id": "<folder_id>",
  "urls": ["https://example.com/article"]
}'
# 返回 results 映射：{ "<url>": { url, ret_code, media_id } }
```

### 添加笔记到知识库

```bash
ima_api "openapi/wiki/v1/add_knowledge" '{
  "media_type": 11,
  "note_info": { "content_id": "<note_id>" },
  "title": "笔记标题",
  "knowledge_base_id": "<kb_id>"
}'
```

### 添加 URL 到知识库（自动检测文件型 URL）

URL 可能指向网页或可下载文件。检测逻辑 → see `references/api.md §URL Type Detection`。

**文件型 URL 处理流程**：

```bash
# 1. 探测 URL 类型
CONTENT_TYPE=$(curl -sI -L "<url>" | grep -i "^content-type:" | tail -1 | awk '{print $2}' | tr -d '\r')

# 2. 下载到临时目录
TEMP_DIR=$(mktemp -d)
curl -sL -o "$TEMP_DIR/paper.pdf" "<url>"

# 3. preflight-check.cjs ← ⛔ GATE 1
PREFLIGHT=$(node .claude/skills/ima-skill/knowledge-base/scripts/preflight-check.cjs \
  --file "$TEMP_DIR/paper.pdf" --content-type "$CONTENT_TYPE")
# pass=false → terminate

# 4. Follow "上传文件到知识库" workflow (Steps 3-7 with all gates)

# 5. Clean up
rm -rf "$TEMP_DIR"
```

**文件名推断**（优先级）：Content-Disposition header → URL path → last URL segment + Content-Type extension

---

---

## 文件夹操作

知识库内容以文件夹层级组织。`folder_id` 始终以 `folder_` 前缀开头。

**核心规则**：

- 操作根目录时 **省略 `folder_id` 字段**，不要传该参数
- **不要将 `knowledge_base_id` 作为 `folder_id` 传入**
- `get_knowledge_list` 返回的 `current_path`（`FolderInfo[]`）= 面包屑

### 定位文件夹（用户只给了名称）

```bash
# 方法 1：搜索（推荐）
ima_api "openapi/wiki/v1/search_knowledge" '{
  "query": "文件夹名称",
  "knowledge_base_id": "<kb_id>",
  "cursor": ""
}'
# 从 info_list 找匹配文件夹，取 media_id 作为 folder_id

# 方法 2：逐级浏览
ima_api "openapi/wiki/v1/get_knowledge_list" '{
  "knowledge_base_id": "<kb_id>",
  "cursor": "",
  "limit": 50
}'
```

---

## 查询类工作流（无安全门限制）

### 获取知识库信息

```bash
ima_api "openapi/wiki/v1/get_knowledge_base" '{"ids": ["<kb_id>"]}'
```

### 浏览知识库内容

```bash
# 根目录
ima_api "openapi/wiki/v1/get_knowledge_list" '{"knowledge_base_id": "<kb_id>", "cursor": "", "limit": 20}'

# 指定文件夹
ima_api "openapi/wiki/v1/get_knowledge_list" '{"knowledge_base_id": "<kb_id>", "folder_id": "<folder_id>", "cursor": "", "limit": 20}'
# 翻页：用 next_cursor，is_end=true 时停止
```
注意：`get_knowledge_list` 返回的 key 是 `knowledge_list`（不是 `info_list`），其中包含 `title`、`media_id`、`media_type` 等字段。

### 搜索知识库内容 / 搜索知识库列表

```bash
ima_api "openapi/wiki/v1/search_knowledge" '{"query": "关键词", "knowledge_base_id": "<kb_id>", "cursor": ""}'

# 搜索知识库列表（按名称）
ima_api "openapi/wiki/v1/search_knowledge_base" '{"query": "关键词", "cursor": "", "limit": 20}'

# 查看所有知识库
ima_api "openapi/wiki/v1/search_knowledge_base" '{"query": "", "cursor": "", "limit": 20}'
```

### 获取可添加的知识库列表

**仅当用户未指定目标知识库时使用**。

```bash
ima_api "openapi/wiki/v1/get_addable_knowledge_base_list" '{"cursor": "", "limit": 20}'
```

### 获取媒体原文内容

```bash
RESPONSE=$(ima_api "openapi/wiki/v1/get_media_info" '{"media_id": "<media_id>"}')
```

**处理分支**：

| 条件                                                    | 处理                                                              |
| ------------------------------------------------------- | ----------------------------------------------------------------- |
| `media_type=11` 且 `notebook_ext_info.notebook_id` 存在 | 将 `notebook_id` 作为 `note_id` 调用 notes 模块 `get_doc_content` |
| `url_info.url` 非空                                     | 用 `url` + `headers`（如有）请求原文                              |
| `url_info` 为空，或请求失败，或 `code≠0`                | 提示用户「请使用ima客户端查看原文」                               |

**强制下载并指定文件名**：当需要将 `url_info.url` 返回的链接作为下载链接（而非在线预览）时，可在 URL 后追加以下查询参数：

```
response-content-type=application/octet-stream&response-content-disposition=attachment;filename="<desired_filename>"
```

示例：用户要求"导出"或"下载"某个知识库文件时，将 `get_media_info` 返回的 `url` 拼接上述参数，即可让浏览器/客户端以指定文件名下载，而非在线打开。

---

## 分页

所有列表/搜索接口使用**游标分页**：首次 `cursor: ""`，检查 `is_end`，用 `next_cursor` 翻页，`is_end=true` 停止。

## 响应处理

统一结构 `{ "code": 0, "msg": "...", "data": { ... } }`。`code=0` 成功；`code≠0` 直接展示 `msg` 给用户。

## 用户体验

- **隐藏内部 ID**：面向用户展示中**永远不要暴露** `knowledge_base_id`、`media_id`、`folder_id`。使用知识库名称、文件标题、文件夹名称。
- **精简进度**：不要逐步暴露内部操作（"正在创建媒体…正在上传 COS…"）。只报告：
  - 上传文件：`"正在上传 report.pdf…"` → `"已添加到知识库「产品文档库」✓"`
  - 添加网页：`"正在添加…"` → `"已添加到「产品文档库」✓"`
  - 失败时展示 `msg`
- **批量操作**：汇总结果，如 `"3 个文件已添加到「产品文档库」，1 个失败（data.xlsx: 文件大小超限）"`
- **格式化展示**：请参考 IMA 主技能 `SKILL.md` 的「格式化展示」章节

## 注意事项

- `get_knowledge_base` 接受 1-20 个 ID；单个 ID 也需包装为数组
- **文件夹是知识条目的一种**：返回结果中同时包含文件和文件夹
- 文件扩展名必须正确提取，用于 `media_type` 检测和 `file_ext` 字段（无点号，如 `pdf`）
- COS 上传时 `--content-type` 应传入文件的实际 MIME 类型，非 `application/octet-stream`
- 当用户提供 URL 添加到知识库时，必须先检测是否文件型 URL → see `references/api.md §URL Type Detection`
- MediaType 枚举和文件大小限制 → see `references/api.md §MediaType` and `§文件大小限制`
- **COS token 截断是常见陷阱**：`cos_credential.token` 值 875+ 字符，含特殊符号。绝对不能通过 shell 参数传递。使用 `scripts/upload-to-kb.cjs` 统一脚本（create_media → COS 上传 → add_knowledge 单进程完成）。
- **IMA 作为外部 Memory**：当 Hermes 内置 memory（4KB）不够用时，可将低频信息存储到 IMA 知识库。详见 `references/external-memory.md`。
- **Hermes Memory/Skills 同步**：将 Hermes memory 和 skills 清单导出为笔记上传到知识库，用于每日备份和跨实例恢复。详见 `references/hermes-memory-sync.md`。
- **Google Docs 爬取**：公开 Google Docs 可通过 `mobilebasic` URL 爬取全文内容，再用 `import_doc` + `add_knowledge` 创建笔记。详见 `references/google-docs-scraping.md`。
- **大内容写入**：当内容 >10KB 时，不要通过 shell 传递 JSON（会被截断），使用 Node.js 脚本直接调用 `ima_api.cjs`。详见 `references/google-docs-scraping.md#大内容处理`。
- **常用知识库 ID**：OBSBOT知识库 `mmYXYA4QIUsKj6PikZYHx1HtEhrPFvmysbEUrO4UfvQ=`、OBSBOT社媒监控 `EmO3hjd7GDxTm3Oc5TaTJac-Lzutinhil9N4_SOxdVI=`。完整列表见 `references/common-knowledge-base-ids.md`。
