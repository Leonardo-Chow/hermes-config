# SmartSheet 创建与数据填充陷阱

## 陷阱1：默认字段必须逐个删除

创建 smartsheet 后会自动生成 5 个默认字段：单选(singleSelect)、数字(number)、日期(dateTime)、图片(image)、文本(text)。

**问题：** 批量删除 `delete_fields` 传入多个 field_id 时，可能部分失败（返回 code:55 错误）。

**解决：** 逐个删除每个字段，不要批量删除：
```python
for f in fields:
    subprocess.run(['mcporter', 'call', 'tencent-docs', 'smartsheet.delete_fields', '--args', 
        json.dumps({"file_id": file_id, "sheet_id": sheet_id, "field_ids": [f['field_id']]})])
```

**⚠️ "文本"字段特别顽固：** 即使批量删除成功，有时仍会残留一个"文本"字段。添加自定义字段后必须再次检查并删除。

## 陷阱2：add_fields 参数格式

**错误格式：**
```json
{"field_name": "网红ID", "field_type": "text"}  // ❌ field_name 会报 "field title cannot be empty"
```

**正确格式：**
```json
{"field_title": "网红ID", "field_type": "text", "property_text": {}}  // ✅
```

必须包含 `property_text`（或对应的 property 类型），否则字段创建可能失败。

## 陷阱3：创建时自动生成空记录

`manage.create_file` 创建 smartsheet 时会自动生成 5 条空记录（field_values 为空数组）。

**必须在添加数据后删除这些空记录：**
```python
records = list_records(file_id, sheet_id)
empty_ids = [r['record_id'] for r in records if not r.get('field_values')]
if empty_ids:
    delete_records(file_id, sheet_id, empty_ids)
```

## 陷阱4：field_value 正确格式

**错误格式：**
```json
{"field": "网红ID", "value": "Zebra Zone"}  // ❌ 不支持
```

**正确格式（文本）：**
```json
{"field": "网红ID", "text_value": {"items": [{"text": "Zebra Zone", "type": "text"}]}}
```

**正确格式（数字）：**
```json
{"field": "量级（k）", "number_value": 541.6}
```

**正确格式（超链接）：**
```json
{"field": "链接", "url_value": {"items": [{"text": "显示文字", "type": "url", "link": "https://..."}]}}
```

## 陷阱5：批量记录数量限制

每批 `add_records` 不要超过 10 条记录。mcporter 输出会被截断到 20K 字符，导致 JSON 解析失败。

对于大量记录（如 27 条），分 3 批添加（10+10+7）。

## 陷阱6：空值处理

某些字段可能为空（如 Pros、Cons）。不能传空字符串，必须传默认值：
```python
{"field": "Pros", "text_value": {"items": [{"text": r['Pros'] if r['Pros'] else "——", "type": "text"}]}}
```

## 陷阱7：add_records 批量超时（2026-05-29 验证）

**批量添加（即使是 3 条/批）在记录字段较多（14 列）时经常超时（30s limit）。**

**唯一可靠方案：逐条添加，timeout 设 60s：**
```python
added = 0
for rec in records:
    payload = json.dumps({"file_id": file_id, "sheet_id": sheet_id, "records": [rec]}, ensure_ascii=False)
    for attempt in range(3):  # 最多重试 3 次
        try:
            r = subprocess.run(['mcporter','call','tencent-docs','smartsheet.add_records','--args',payload],
                             capture_output=True, text=True, timeout=60)
            if json.loads(r.stdout).get('records'):
                added += 1
                break
        except: pass
        time.sleep(2)
    time.sleep(0.3)  # 每条间隔 0.3s
```

**关键参数**：
- timeout=60（不是 30）
- 每条间隔 0.3s
- 失败重试 3 次，间隔 2s
- 36 条记录（14 列）总耗时约 3-4 分钟

## 完整创建流程（Python 示例）

```python
import subprocess, json, time

def create_smartsheet_with_data(title, records_data, folder_id):
    """创建智能表格并填充数据"""
    
    # 1. 创建表格
    r = subprocess.run(['mcporter','call','tencent-docs','manage.create_file','--args',
        json.dumps({"title": title, "file_type": "smartsheet"})], capture_output=True, text=True, timeout=30)
    file_id = json.loads(r.stdout)['file_id']
    
    # 2. 获取 sheet_id
    r = subprocess.run(['mcporter','call','tencent-docs','smartsheet.list_tables','--args',
        json.dumps({"file_id": file_id})], capture_output=True, text=True, timeout=30)
    sheet_id = json.loads(r.stdout)['sheets'][0]['sheet_id']
    
    # 3. 删除默认字段（逐个）
    r = subprocess.run(['mcporter','call','tencent-docs','smartsheet.list_fields','--args',
        json.dumps({"file_id": file_id, "sheet_id": sheet_id})], capture_output=True, text=True, timeout=30)
    for f in json.loads(r.stdout)['fields']:
        subprocess.run(['mcporter','call','tencent-docs','smartsheet.delete_fields','--args',
            json.dumps({"file_id": file_id, "sheet_id": sheet_id, "field_ids": [f['field_id']]})],
            capture_output=True, text=True, timeout=30)
        time.sleep(0.2)
    
    # 4. 添加自定义字段
    fields = [...]  # 你的字段定义
    subprocess.run(['mcporter','call','tencent-docs','smartsheet.add_fields','--args',
        json.dumps({"file_id": file_id, "sheet_id": sheet_id, "fields": fields})],
        capture_output=True, text=True, timeout=30)
    
    # 5. 逐条添加记录（可靠方案）
    added = 0
    for rec in records_data:
        payload = json.dumps({"file_id": file_id, "sheet_id": sheet_id, "records": [rec]}, ensure_ascii=False)
        for attempt in range(3):
            try:
                r = subprocess.run(['mcporter','call','tencent-docs','smartsheet.add_records','--args',payload],
                                 capture_output=True, text=True, timeout=60)
                if json.loads(r.stdout).get('records'):
                    added += 1
                    break
            except: pass
            time.sleep(2)
        time.sleep(0.3)
    
    # 6. 删除默认空记录
    r = subprocess.run(['mcporter','call','tencent-docs','smartsheet.list_records','--args',
        json.dumps({"file_id": file_id, "sheet_id": sheet_id})], capture_output=True, text=True, timeout=30)
    empty_ids = [r['record_id'] for r in json.loads(r.stdout)['records'] if not r.get('field_values')]
    if empty_ids:
        subprocess.run(['mcporter','call','tencent-docs','smartsheet.delete_records','--args',
            json.dumps({"file_id": file_id, "sheet_id": sheet_id, "record_ids": empty_ids})],
            capture_output=True, text=True, timeout=30)
    
    # 7. 移动到目标文件夹
    subprocess.run(['mcporter','call','tencent-docs','manage.move_file','--args',
        json.dumps({"file_id": file_id, "target_folder_id": folder_id})],
        capture_output=True, text=True, timeout=30)
    
    return file_id
```

## 自检清单

创建完成后必须执行：
- [ ] 字段数 = 预期数量（不多不少）
- [ ] 没有默认残留字段（单选、数字、日期、图片、文本）
- [ ] 记录数 = 预期数量
- [ ] 每条记录的 field_values 不为空
- [ ] 第一条记录包含所有预期字段
- [ ] 没有重复记录（检查 KOL ID 等唯一字段）
