---
name: tencent-docs-mcp
description: 腾讯文档 MCP 集成 — 通过 mcporter CLI 操作腾讯文档（docs.qq.com），支持创建/编辑/读取智能文档、在线表格、智能表格、PPT、思维导图等。
version: 1.0.0
tags: [tencent, docs, mcp, mcporter, cloud-docs, spreadsheet]
category: productivity
---

# 腾讯文档 MCP

通过 mcporter CLI 调用腾讯文档 MCP API，支持 98 个工具。

## 安装配置

### 1. 下载 Skill

```bash
cd /tmp
curl -L -o tencent-docs.zip "https://cdn.addon.tencentsuite.com/static/tencent-docs.zip"
unzip -o tencent-docs.zip -d tencent-docs-extracted
cp -r /tmp/tencent-docs-extracted/tencent-docs ~/.hermes/skills/
```

### 2. 配置 mcporter

```bash
# 添加 MCP 服务器
mcporter config add tencent-docs https://docs.qq.com/openapi/mcp

# 设置环境变量（在 ~/.hermes/.env）
echo 'TENCENT_DOCS_TOKEN="your_token_here"' >> ~/.hermes/.env
```

### 3. 获取 Token

访问 https://docs.qq.com/scenario/open-claw.html?nlc=1 获取 Token。

### 4. 验证

```bash
mcporter list tencent-docs
```

## 常用操作

### 创建智能文档（推荐）

```bash
mcporter call tencent-docs create_smartcanvas_by_mdx --args '{
  "title": "文档标题",
  "mdx": "# 内容\n\n支持 Markdown 语法"
}'
```

### 创建在线表格

```bash
# 创建表格文件
mcporter call tencent-docs manage.create_file --args '{
  "file_type": "sheet",
  "title": "表格标题",
  "parent_id": "folder_id"  # 可选，指定文件夹
}'

# 获取工作表 ID
mcporter call tencent-docs sheet.get_sheet_info --args '{"file_id": "xxx"}'

# 写入数据
mcporter call tencent-docs sheet.set_range_value --args '{
  "file_id": "xxx",
  "sheet_id": "Sheet1",
  "values": [
    {"row": 0, "col": 0, "value_type": "STRING", "string_value": "表头1"},
    {"row": 0, "col": 1, "value_type": "STRING", "string_value": "表头2"}
  ]
}'
```

### 创建智能表格（SmartSheet）

```bash
# 创建智能表格
mcporter call tencent-docs manage.create_file --args '{
  "file_type": "smartsheet",
  "title": "智能表格标题"
}'

# 添加字段
mcporter call tencent-docs smartsheet.add_fields --args '{
  "file_id": "xxx",
  "sheet_id": "yyy",
  "fields": [
    {"field_title": "名称", "field_type": "text", "property_text": {}},
    {"field_title": "链接", "field_type": "text", "property_text": {}}
  ]
}'

# 添加记录
mcporter call tencent-docs smartsheet.add_records --args '{
  "file_id": "xxx",
  "sheet_id": "yyy",
  "records": [
    {"fields": {"名称": "值1", "链接": "https://..."}}
  ]
}'
```

### 搜索文档

```bash
mcporter call tencent-docs manage.search_file --args '{"search_key": "关键词"}'
```

### 获取文档内容

```bash
mcporter call tencent-docs get_content --args '{"file_id": "xxx"}'
```

### 网页剪藏

```bash
# 剪藏网页
mcporter call tencent-docs scrape_url --args '{"url": "https://example.com"}'

# 查询进度（轮询直到 status=2）
mcporter call tencent-docs scrape_progress --args '{"task_id": "xxx"}'
```

## 文件夹管理

### 查找文件夹

```bash
mcporter call tencent-docs manage.search_file --args '{"search_key": "文件夹名"}'
```

### 查看文件夹内容

```bash
mcporter call tencent-docs manage.folder_list --args '{"folder_id": "xxx"}'
```

### 在指定文件夹创建文档

```bash
mcporter call tencent-docs manage.create_file --args '{
  "file_type": "sheet",
  "title": "文档标题",
  "parent_id": "目标文件夹ID"
}'
```

## 文档类型

| 类型 | doc_type | 推荐度 | 说明 |
|------|----------|:------:|------|
| 智能文档 | smartcanvas | ⭐⭐⭐ | MDX 格式，排版美观 |
| 在线表格 | sheet | ⭐⭐⭐ | Excel 操作 |
| 智能表格 | smartsheet | ⭐⭐⭐ | 高级结构化表格 |
| PPT | slide | ⭐⭐⭐ | 演示文稿 |
| 思维导图 | mind | ⭐⭐⭐ | 知识图谱 |
| 流程图 | flowchart | ⭐⭐⭐ | 流程展示 |
| Word | doc | ⭐⭐ | 传统格式 |
| 收集表 | form | ⭐⭐ | 表单收集 |

## 完整工作流：创建表格 → 写入数据 → 设置样式

```bash
# 1. 创建表格（指定文件夹）
mcporter call tencent-docs manage.create_file file_type=sheet title="标题_$(date +%Y-%m-%d)" parent_id="文件夹node_id"

# 2. 获取工作表 ID
mcporter call tencent-docs sheet.get_sheet_info file_id=DTQCXotnuSKK
# 返回 sheet_id: "BB08J2"

# 3. 清空现有数据
mcporter call tencent-docs sheet.clear_range_all file_id=xxx sheet_id=BB08J2 start_row=0 end_row=40 start_col=0 end_col=11

# 4. 批量写入数据（Python 构造 payload）
python3 -c "
import json, subprocess
values = []
# 表头
for col, h in enumerate(['列1','列2']):
    values.append({'row':0, 'col':col, 'value_type':'STRING', 'string_value':h})
# 数据行
for row_idx, item in enumerate(data, 1):
    for col_idx, h in enumerate(headers):
        values.append({'row':row_idx, 'col':col_idx, 'value_type':'STRING', 'string_value':str(item.get(h,''))})

cmd = ['mcporter','call','tencent-docs','sheet.set_range_value',
       f'file_id=xxx', f'sheet_id=BB08J2',
       f'values={json.dumps(values, ensure_ascii=False)}']
subprocess.run(cmd, capture_output=True, text=True, timeout=90)
"

# 5. 设置表头加粗
for col in {0..10}; do
    mcporter call tencent-docs sheet.set_cell_style file_id=xxx sheet_id=BB08J2 row=0 col=$col bold=true
done
```

### mcporter 配置带 Token
```bash
mcporter config add tencent-docs "https://docs.qq.com/openapi/mcp" \
    --header "Authorization=$TENCENT_TOKEN" \
    --transport http \
    --scope home
```

## 在线表格（Sheet）vs 智能表格（SmartSheet）

⚠️ **两者 API 完全不同**，不要混用：

| 操作 | 在线表格 (sheet) | 智能表格 (smartsheet) |
|------|:---:|:---:|
| 获取信息 | `sheet.get_sheet_info` | `smartsheet.list_tables` |
| 读取数据 | `get_content`（返回 Markdown 表格） | `smartsheet.list_records` |
| 写入数据 | `sheet.set_range_value` | `smartsheet.add_records` |
| 清空数据 | `sheet.clear_range_all` | `smartsheet.delete_records` |
| file_id | 用 `search_file` 返回的 `file_id` | 同左 |

**判断方法**：`sheet.get_sheet_info` 返回 `sheets` 数组 → 在线表格；`smartsheet.list_tables` 返回 `sheets` 数组 → 智能表格。

## Pitfalls

- **file_id vs URL ID**：`search_file` 返回的 `file_id`（如 `DdEOtHMKgqEv`）与 URL 中的 ID（如 `DRGRFT3RITUtncUV2`）**不同**。API 调用必须用 `search_file` 返回的 `file_id`，不能用 URL 中的 ID。
- **get_content 字符截断**：`get_content` 对大表格有 ~27K 字符截断限制。超过此限制的数据不会返回。解决方案：对于超大表格，无法用 `get_content` 验证写入，需信任 `set_range_value` 的成功响应。
- **sheet.get_range_value 未注册**：此工具不存在！只能用 `get_content` 读取整个表格内容。
- **clear_range_all 边界错误**：`start_row`/`end_row` 超出实际行数会报 `operation out of sheet boundary`。确保范围在 `sheet.get_sheet_info` 返回的 `row_count` 内。
- **行数自动扩展**：`set_range_value` 写入超过默认 200 行时，腾讯文档会自动扩展行数。
- **mcporter 参数格式**：有两种传递参数方式：`--args '{"key":"val"}'` 或直接 `key=value`。**⚠️ `sheet.set_range_value` 必须用 `key=value` 格式，`--args` 格式会报 missing parameters 错误！** 示例：
  ```bash
  # ✅ 正确
  mcporter call tencent-docs sheet.set_range_value file_id="Dxxx" sheet_id="BB08J2" values='[{"row":0,"col":0,"value_type":"STRING","string_value":"test"}]'
  # ❌ 错误（会报 missing required parameters）
  mcporter call tencent-docs sheet.set_range_value --args '{"file_id":"Dxxx","sheet_id":"BB08J2","values":[...]}'
  ```
- **读取表格内容**：`sheet.get_range_value` 工具未注册！用 `get_content file_id=xxx` 读取整个表格内容来验证写入是否成功
- **字段格式错误**：SmartSheet 的 `add_fields` 需要完整的字段定义，包括 `property_text: {}` 等
- **URL 字段类型**：SmartSheet 的 `url` 类型字段可能报错，改用 `text` 类型存储链接
- **记录为空**：`smartsheet.list_records` 返回的 `field_values` 可能为空，尝试指定 `field_titles` 或 `field_ids`
- **批量写入**：使用 `sheet.set_range_value` 批量写入，每批最多 100 个单元格
- **文件夹 ID**：从 URL 中提取 node_id，或用 `manage.search_file` 搜索
- **表头样式**：写入数据后需单独设置样式，批量设置用循环
- **标题长度限制**：`create_smartcanvas_by_mdx` 的 `title` 参数最长 **36 个字符**，超长会报错 `title length exceeds 36 characters`。解决：缩短标题，或用 `manage.create_file` 创建后单独写入内容
- **文件内容大小**：`mdx` 参数建议截断到 30KB 以内（`head -c 30000`），超大内容可能超时或失败
- **移动文档到文件夹**：`manage.move_file` 参数为 `file_id` + `target_folder_id`（不是 `parent_id`）。创建文档后如需放入指定文件夹，先 `create_smartcanvas_by_mdx` 获得 `file_id`，再 `manage.move_file` 移动
- **批量删除文件**：`manage.delete_file` 接受 `file_id` 参数，可用于清理测试/重复文件。批量删除时逐个调用，注意超时风险（60s），分批处理。清理文件夹示例：
  ```bash
  for file_id in Dxxx Dyyy Dzzz; do
    mcporter call tencent-docs manage.delete_file file_id="$file_id" 2>&1 | head -2
  done
  ```
- **mcporter JSON 转义**：通过 shell 传递含中文/特殊字符的 JSON 时，`values='[...]'` 格式容易被 shell 截断（`unexpected EOF`）。**可靠方案**：先用 Python 写 JSON 到临时文件，再用 `subprocess.run(["mcporter", ...])` 调用，避免 shell 转义：
  ```python
  import json, subprocess
  with open("/tmp/batch.json", "w") as f:
      json.dump(values, f, ensure_ascii=False)
  values_str = json.dumps(values, ensure_ascii=False)
  result = subprocess.run(
      ["mcporter", "call", "tencent-docs", "sheet.set_range_value",
       "file_id=xxx", "sheet_id=BB08J2", f"values={values_str}"],
      capture_output=True, text=True, timeout=60
  )
  ```
- **get_content 返回的 Markdown 表格解析**：`get_content` 返回 pipe-delimited Markdown 表格，但视频标题等字段可能包含 `|` 字符，导致 naive split 错位。**解决方案**：从右往左锚定解析——URL（`https://youtube.com/watch?v=...`）和日期（`YYYY-MM-DD`）格式固定，先提取它们，再用数字列（观看/点赞/评论）作为锚点反向定位标题边界。详见 `references/markdown-table-parsing.md`
- **file_id 不一致**：`manage.search_file` 返回的 `file_id`（如 `DdEOtHMKgqEv`）与 URL 中的 ID（如 `DRGRFT3RITUtncUV2`）不同。**两种都可以用**：URL ID 可直接传给 `sheet.*` 操作，search 返回的 ID 用于 `manage.*` 操作
- **嵌套文件夹导航**：当需要找到深层嵌套的文件夹（如 obsbot → youtube → 油管分析），需逐层搜索：
  1. `manage.search_file search_key="obsbot"` 找到顶层文件夹
  2. `manage.folder_list folder_id="顶层ID"` 查看子文件夹
  3. 找到目标子文件夹 ID 后再操作
  注意：`search_file` 返回的 `is_folder` 字段可区分文件夹和文件
- **搜索返回的 file_id 与 URL ID 不同**：`manage.search_file` 返回的 `file_id`（如 `DdEOtHMKgqEv`）和 URL 中的 ID（如 `DRGRFT3RITUtncUV2`）是不同的！API 调用（如 `sheet.get_sheet_info`、`sheet.set_range_value`）必须使用 **search_file 返回的 file_id**，URL ID 只用于 `get_content`。
- **get_content 字符截断**：`get_content` API 返回内容有约 **27K 字符上限**，大表格会截断。验证数据完整性时不要依赖 `get_content`，改用确认写入批次全部返回 `"error": ""` 即可。
- **普通表格 vs 智能表格判断**：用 `sheet.get_sheet_info` 判断是否为普通表格（返回 `sheets` 数组非空），`smartsheet.list_tables` 判断是否为智能表格。不要混用 API。
- **Markdown 表格解析陷阱**：`get_content` 返回的 Markdown 表格中，单元格内容如果包含 `|`（如视频标题 "Webcam | Review"），会导致列错位。解析策略：用已知格式字段（URL、日期）作为锚点从右往左解析，数字列（粉丝量、点赞、评论）作为辅助锚点。
- **文件导入 Word 文档**：用户明确要求报告类数据用 Word 文档而非 Excel。`import_file.sh` 上传 → `manage.async_import` 触发导入 → 等待完成。Word 文档用 python-docx 生成，按章节组织，每节含信息表格+数据表格，标注清晰。
- **Sheet 批量写入性能**：每批 100 个单元格，1000 个单元格约需 10 批。Python 脚本中用 `subprocess.run` 调用 mcporter，设置合理 timeout（60s）
- **移动文档到文件夹**：`manage.move_file` 参数为 `file_id` + `target_folder_id`（不是 `parent_id`）。创建文档后如需放入指定文件夹，先 `create_smartcanvas_by_mdx` 获得 `file_id`，再 `manage.move_file` 移动
## 参考文档

- Skill 目录：`~/.hermes/skills/tencent-docs/`
- 官方文档：`~/.hermes/skills/tencent-docs/references/`
- Markdown 表格解析（含 | 字段）：`references/markdown-table-parsing.md`
- Excel/Word 生成与上传：`references/excel-word-generation.md`
- Markdown 表格解析（含 `|` 的标题字段）：`references/markdown-table-parsing.md`
- OBSBOT/Insta360 竞品监控工作流：`references/obsbot-insta360-workflow.md`
- Markdown 表格解析（含 `|` 的标题字段）：`references/markdown-table-parsing.md`
- **健壮型锚定解析**（推荐，处理所有特殊字符）：`references/robust-markdown-table-parsing.md`
