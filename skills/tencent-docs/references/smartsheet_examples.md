# 智能表格（SmartSheet）使用示例

## 完整工作流：创建表格并添加数据

### 步骤 1: 创建智能表格文件

```bash
mcporter call tencent-docs manage.create_file --args '{
  "file_type": "smartsheet",
  "title": "Data Collection"
}'
```

> ⚠️ 中文标题可能报错 400001，先用英文标题创建，再 `rename_file_title` 改中文。

### 步骤 2: 获取工作表 ID

```bash
mcporter call tencent-docs smartsheet.list_tables --args '{
  "file_id": "DlxFgEUUCQOs"
}'
```

### 步骤 3: 删除自动生成的空行

创建 smartsheet 后会自动生成 5 条空记录，必须先删除：

```bash
mcporter call tencent-docs smartsheet.delete_records --args '{
  "file_id": "DlxFgEUUCQOs",
  "sheet_id": "t00i2h",
  "record_ids": ["ryZloS", "rZAFer", "rOlE8X", "rzHwJr", "rwW64k"]
}'
```

### 步骤 4: 添加字段（列）

```bash
mcporter call tencent-docs smartsheet.add_fields --args '{
  "file_id": "DlxFgEUUCQOs",
  "sheet_id": "t00i2h",
  "fields": [
    {"field_title": "名称", "field_type": "text", "property_text": {}},
    {"field_title": "链接", "field_type": "text", "property_text": {}},
    {"field_title": "量级", "field_type": "number", "property_number": {"decimal_places": 1, "use_separate": true}}
  ]
}'
```

> ⚠️ 每个字段**必须包含对应的 property 对象**，否则字段不会被正确创建！

### 步骤 5: 添加记录（行）

```bash
mcporter call tencent-docs smartsheet.add_records --args '{
  "file_id": "DlxFgEUUCQOs",
  "sheet_id": "t00i2h",
  "records": [
    {
      "field_values": [
        {"field": "名称", "text_value": {"items": [{"text": "产品A", "type": "text"}]}},
        {"field": "链接", "text_value": {"items": [{"text": "https://example.com", "type": "text"}]}},
        {"field": "量级", "number_value": 541.6}
      ]
    }
  ]
}'
```

> ⚠️ 记录格式是 `field_values` 数组（不是 `fields` 对象），每个元素包含 `field`（字段标题）和类型化值。

## 字段值格式参考

| 字段类型 | 值格式 | 示例 |
|:---------|:-------|:-----|
| text | `text_value` | `{"text_value": {"items": [{"text": "内容", "type": "text"}]}}` |
| number | `number_value` | `{"number_value": 42}` |
| checkbox | `bool_value` | `{"bool_value": true}` |
| singleSelect | `option_value` | `{"option_value": {"items": [{"text": "选项"}]}}` |
| dateTime | `string_value` | `{"string_value": "1720000000000"}` |

## 完整 Python 示例

```python
import json
import subprocess

def mcporter(tool, **kwargs):
    result = subprocess.run(
        ['mcporter', 'call', 'tencent-docs', tool, '--args', json.dumps(kwargs, ensure_ascii=False)],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(result.stdout) if result.stdout else {}

# 1. 创建表格
resp = mcporter('manage.create_file', file_type='smartsheet', title='YouTube Data')
file_id = resp['file_id']

# 2. 获取 sheet_id
resp = mcporter('smartsheet.list_tables', file_id=file_id)
sheet_id = resp['sheets'][0]['sheet_id']

# 3. 删除空行
resp = mcporter('smartsheet.list_records', file_id=file_id, sheet_id=sheet_id)
empty_ids = [r['record_id'] for r in resp.get('records', []) if not r.get('field_values')]
if empty_ids:
    mcporter('smartsheet.delete_records', file_id=file_id, sheet_id=sheet_id, record_ids=empty_ids)

# 4. 添加字段
fields = [
    {"field_title": "标题", "field_type": "text", "property_text": {}},
    {"field_title": "链接", "field_type": "text", "property_text": {}},
    {"field_title": "播放量", "field_type": "number", "property_number": {"decimal_places": 0, "use_separate": True}},
]
mcporter('smartsheet.add_fields', file_id=file_id, sheet_id=sheet_id, fields=fields)

# 5. 添加记录（分批，每批≤10条）
records = [{
    "field_values": [
        {"field": "标题", "text_value": {"items": [{"text": "Video 1", "type": "text"}]}},
        {"field": "链接", "text_value": {"items": [{"text": "https://youtube.com/watch?v=xxx", "type": "text"}]}},
        {"field": "播放量", "number_value": 10000},
    ]
}]

mcporter('smartsheet.add_records', file_id=file_id, sheet_id=sheet_id, records=records)

# 6. 移动到目标文件夹
mcporter('manage.move_file', file_id=file_id, target_folder_id='DPIZlPqPflSU')
```
