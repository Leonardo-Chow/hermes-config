# mcporter 智能表格批量上传工作流

## 概述

通过 `mcporter` CLI 调用腾讯文档 MCP 工具，完成智能表格的创建、字段定义、数据上传全流程。

## 完整流程（Python + mcporter）

### 步骤 1: 创建智能表格

```python
import json
import subprocess

result = subprocess.run(
    ["mcporter", "call", "tencent-docs", "manage.create_file",
     "--args", json.dumps({
         "title": "数据表标题",
         "file_type": "smartsheet"
     })],
    capture_output=True, text=True
)

# 解析结果
json_start = result.stdout.find('{')
create_result = json.loads(result.stdout[json_start:])
file_id = create_result.get("file_id")
```

### 步骤 2: 获取 sheet_id

```python
result = subprocess.run(
    ["mcporter", "call", "tencent-docs", "smartsheet.list_tables",
     "--args", json.dumps({"file_id": file_id})],
    capture_output=True, text=True
)

tables_result = json.loads(result.stdout[result.stdout.find('{'):])
sheet_id = tables_result["sheets"][0]["sheet_id"]
```

### 步骤 3: 添加字段

```python
fields = [
    {
        "field_title": "名称",
        "field_type": "text",
        "property_text": {}
    },
    {
        "field_title": "数量",
        "field_type": "number",
        "property_number": {"decimal_places": 0, "use_separate": True}
    },
    {
        "field_title": "类型",
        "field_type": "singleSelect",
        "property_single_select": {
            "options": [
                {"text": "A类", "style": "3"},
                {"text": "B类", "style": "4"}
            ]
        }
    },
    {
        "field_title": "链接",
        "field_type": "text",  # 用 text 而非 url，避免超链接格式问题
        "property_text": {}
    }
]

result = subprocess.run(
    ["mcporter", "call", "tencent-docs", "smartsheet.add_fields",
     "--args", json.dumps({
         "file_id": file_id,
         "sheet_id": sheet_id,
         "fields": fields
     })],
    capture_output=True, text=True
)
```

### 步骤 4: 批量上传记录

```python
# 构建记录
records = []
for item in data:
    record = {
        "field_values": [
            {"field": "名称", "text_value": {"items": [{"text": item["name"], "type": "text"}]}},
            {"field": "数量", "number_value": item["count"]},
            {"field": "类型", "option_value": {"items": [{"text": item["type"]}]}},
            {"field": "链接", "text_value": {"items": [{"text": item["url"], "type": "text"}]}}
        ]
    }
    records.append(record)

# 分批上传（每批 50 条）
batch_size = 50
for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    result = subprocess.run(
        ["mcporter", "call", "tencent-docs", "smartsheet.add_records",
         "--args", json.dumps({
             "file_id": file_id,
             "sheet_id": sheet_id,
             "records": batch
         })],
        capture_output=True, text=True
    )
    add_result = json.loads(result.stdout[result.stdout.find('{'):])
    if add_result.get("error"):
        print(f"批次 {i//batch_size + 1} 失败: {add_result['error']}")
```

### 步骤 5: 清理默认数据

```python
# 删除默认空行
result = subprocess.run(
    ["mcporter", "call", "tencent-docs", "smartsheet.list_records",
     "--args", json.dumps({
         "file_id": file_id,
         "sheet_id": sheet_id,
         "field_titles": ["第一个字段名"],
         "limit": 100
     })],
    capture_output=True, text=True
)

records_result = json.loads(result.stdout[result.stdout.find('{'):})
empty_records = []
for r in records_result.get("records", []):
    # 检查第一个字段是否为空
    field_values = r.get("field_values", [])
    first_field_value = ""
    for fv in field_values:
        if fv.get("field") == "第一个字段名":
            items = fv.get("text_value", {}).get("items", [])
            first_field_value = items[0].get("text", "") if items else ""
            break
    
    if not first_field_value:
        empty_records.append(r.get("record_id"))

if empty_records:
    subprocess.run(
        ["mcporter", "call", "tencent-docs", "smartsheet.delete_records",
         "--args", json.dumps({
             "file_id": file_id,
             "sheet_id": sheet_id,
             "record_ids": empty_records
         })],
        capture_output=True, text=True
    )

# 删除默认字段（单选、数字、日期、图片、文本）
result = subprocess.run(
    ["mcporter", "call", "tencent-docs", "smartsheet.list_fields",
     "--args", json.dumps({"file_id": file_id, "sheet_id": sheet_id})],
    capture_output=True, text=True
)

fields_result = json.loads(result.stdout[result.stdout.find('{'):])
our_fields = {"字段1", "字段2", ...}  # 你创建的字段名
default_fields = [f for f in fields_result.get("fields", []) 
                  if f.get("field_title") not in our_fields]

if default_fields:
    subprocess.run(
        ["mcporter", "call", "tencent-docs", "smartsheet.delete_fields",
         "--args", json.dumps({
             "file_id": file_id,
             "sheet_id": sheet_id,
             "field_ids": [f["field_id"] for f in default_fields]
         })],
        capture_output=True, text=True
    )
```

### 步骤 6: 移动到目标文件夹

```python
subprocess.run(
    ["mcporter", "call", "tencent-docs", "manage.move_file",
     "--args", json.dumps({
         "file_id": file_id,
         "target_folder_id": "目标文件夹ID"
     })],
    capture_output=True, text=True
)
```

## Pitfalls

- **mcporter auth**: 首次使用需 `mcporter auth tencent-docs`
- **工具名格式**: 使用点号分隔 `manage.create_file`，不是空格
- **URL 字段类型**: 用户可能不要超链接格式，用 `text` 类型更安全
- **批量大小**: 每批最多 50 条记录，超过可能超时
- **默认数据**: 新建表格会自动生成 5 个默认字段和 5 条空行，必须清理
- **JSON 解析**: mcporter 输出可能包含额外文本，用 `result.stdout.find('{')` 定位 JSON 起始位置
