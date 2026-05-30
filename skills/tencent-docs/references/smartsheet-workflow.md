# Smartsheet Workflow (Smart Sheet / 智能表格)

## Complete Workflow: Create + Configure + Populate

### Step 1: Create Smartsheet

```bash
mcporter call 'tencent-docs' 'manage.create_file' --args '{"title":"Sheet Title","file_type":"smartsheet"}'
```

Response: `{"file_id": "DrxpgbTwcPEw", "url": "https://docs.qq.com/smartsheet/..."}`

### Step 2: Get Sheet ID

```bash
mcporter call 'tencent-docs' 'smartsheet.list_tables' --args '{"file_id":"FILE_ID"}'
```

**Pitfall:** Response format is `{"sheets": [{"sheet_id": "t00i2h", "title": "智能表1"}]}` — NO `data` wrapper. Access `resp['sheets'][0]['sheet_id']` directly.

### Step 3: Delete Default Fields

New smartsheets come with 5 default fields (单选, 数字, 日期, 图片, 文本). Delete them before adding custom fields:

```bash
# List existing fields
mcporter call 'tencent-docs' 'smartsheet.list_fields' --args '{"file_id":"FID","sheet_id":"SID"}'

# Delete each field
mcporter call 'tencent-docs' 'smartsheet.delete_fields' --args '{"file_id":"FID","sheet_id":"SID","field_ids":["f0JNov"]}'
```

**Pitfall:** Response format for list_fields is `{"fields": [...]}` — NO `data` wrapper.

### Step 4: Add Custom Fields

```bash
mcporter call 'tencent-docs' 'smartsheet.add_fields' --args '{
  "file_id": "FID",
  "sheet_id": "SID",
  "fields": [
    {"field_title": "Column Name", "field_type": "text", "property_text": {}}
  ]
}'
```

**User preference:** Use `text` type for ALL fields including links/URLs. User explicitly said "视频链接不要用超链接". Do NOT use `url` field type.

### Step 5: Delete Default Empty Records

New smartsheets come with 5 empty records. Delete them:

```bash
# List records
mcporter call 'tencent-docs' 'smartsheet.list_records' --args '{"file_id":"FID","sheet_id":"SID"}'

# Delete empty records
mcporter call 'tencent-docs' 'smartsheet.delete_records' --args '{"file_id":"FID","sheet_id":"SID","record_ids":["ra8ZtR","rb2XyZ"]}'
```

### Step 6: Add Records

```bash
mcporter call 'tencent-docs' 'smartsheet.add_records' --args '{
  "file_id": "FID",
  "sheet_id": "SID",
  "records": [
    {
      "field_values": [
        {"field": "Column Name", "text_value": {"items": [{"text": "Value", "type": "text"}]}}
      ]
    }
  ]
}'
```

**Important:** Use `ensure_ascii=False` in Python `json.dumps` for Chinese content.

### Step 7: Rename Sheet Tab (Optional)

```bash
mcporter call 'tencent-docs' 'smartsheet.rename_table' --args '{"file_id":"FID","sheet_id":"SID","title":"New Tab Name"}'
```

### Step 8: Move to Target Folder

```bash
mcporter call 'tencent-docs' 'manage.move_file' --args '{"file_id":"FID","target_folder_id":"FOLDER_ID"}'
```

### Step 9: Rename File Title (Optional)

```bash
mcporter call 'tencent-docs' 'manage.rename_file_title' --args '{"file_id":"FID","title":"New Title"}'
```

## Field Types

| Type | property | Use Case |
|------|----------|----------|
| `text` | `property_text: {}` | General text, URLs, descriptions |
| `number` | `property_number: {}` | Numeric values |
| `date` | `property_date: {}` | Dates |
| `select` | `property_select: {"options": [...]}` | Single choice |
| `url` | `property_url: {}` | **AVOID** — user prefers text type for links |

## Pitfalls

1. **Response format varies** — `list_tables`, `list_fields`, `list_records` return data at top level (no `data` wrapper)
2. **Default content cleanup** — Always delete default fields AND default empty records before populating
3. **Chinese content** — Use `ensure_ascii=False` in json.dumps
4. **Field IDs are dynamic** — After deleting and re-adding fields, IDs change. Always re-list fields to get current IDs
5. **Text type for links** — User explicitly prefers text type over url type for video/link fields
