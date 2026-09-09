# COS Import Workaround for Tencent Docs

## Problem

`mcporter call tencent-docs doc.insert_markdown` consistently fails with:
```
MCP error -32603: Tool "insert_markdown" is missing required parameters: [idx]
```

This happens even when `idx` is correctly provided. May be mcporter 0.10.1 bug.

## Solution: COS Import

```bash
# Step 1: Upload to COS
cd ~/.hermes/skills/tencent-docs
bash import_file.sh "/path/to/file.docx"

# Step 2: Trigger async import
mcporter call "tencent-docs" "manage.async_import" --args '{"task_id": "<TASK_ID>", "file_size": "<FILE_SIZE>", "file_key": "<FILE_KEY>", "file_name": "<FILE_NAME>", "file_md5": "<FILE_MD5>"}'

# Step 3: Wait (15 seconds)
sleep 15

# Step 4: Search for file
mcporter call tencent-docs manage.search_file --args '{"search_key": "filename"}'

# Step 5: Move to folder
mcporter call tencent-docs manage.move_file --args '{"file_id": "<file_id>", "target_folder_id": "DumZsGZJrwsf"}'
```

Supported: .docx, .xlsx, .md
