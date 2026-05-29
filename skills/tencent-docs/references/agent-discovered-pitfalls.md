# Agent-Discovered Pitfalls (from tencent-docs-mcp sessions)

> These pitfalls were discovered through extensive agent-created sessions using
> mcporter CLI for Tencent Docs. Merged here for discoverability.

## mcporter Parameter Format Issues

### sheet.set_range_value MUST use key=value format
```bash
# ✅ Correct
mcporter call tencent-docs sheet.set_range_value file_id="Dxxx" sheet_id="BB08J2" values='[{...}]'

# ❌ Wrong (returns "missing required parameters")
mcporter call tencent-docs sheet.set_range_value --args '{"file_id":"Dxxx","sheet_id":"BB08J2","values":[...]}'
```

### Shell JSON escaping for large payloads
When passing `values` with Chinese/special characters, shell `'[...]'` format gets truncated.
**Reliable approach**: Write JSON to temp file, use Python subprocess:
```python
import json, subprocess
values_str = json.dumps(values, ensure_ascii=False)
result = subprocess.run(
    ["mcporter", "call", "tencent-docs", "sheet.set_range_value",
     "file_id=xxx", "sheet_id=BB08J2", f"values={values_str}"],
    capture_output=True, text=True, timeout=60
)
```

## file_id vs URL ID

- `manage.search_file` returns `file_id` (e.g., `DdEOtHMKgqEv`)
- URL contains different ID (e.g., `DRGRFT3RITUtncUV2`)
- **Both work**: URL ID for `sheet.*` operations, search file_id for `manage.*` operations
- When in doubt, use the `file_id` from `search_file`

## get_content Limitations

- **~27K character truncation**: Large tables get truncated
- **Markdown table parsing**: Cells containing `|` (e.g., video titles "Webcam | Review") cause column misalignment
- **Robust parsing strategy**: Use known-format fields (URL, date) as anchors, parse from right to left
- Do NOT rely on `get_content` to verify large data writes — trust `set_range_value` success response instead

## sheet.get_range_value Does NOT Exist

This tool is not registered. Use `get_content file_id=xxx` to read entire sheet content.

## clear_range_all Boundary Errors

`start_row`/`end_row` beyond actual row count → `operation out of sheet boundary`.
Check `sheet.get_sheet_info` → `row_count` before clearing.

## Batch Write Performance

- Max 100 cells per `set_range_value` call
- 1000 cells ≈ 10 batches
- Row auto-expansion beyond default 200 rows

## SmartSheet vs Sheet (DO NOT MIX)

| Operation | Sheet | SmartSheet |
|-----------|-------|------------|
| Get info | `sheet.get_sheet_info` | `smartsheet.list_tables` |
| Read data | `get_content` | `smartsheet.list_records` |
| Write data | `sheet.set_range_value` | `smartsheet.add_records` |
| Clear data | `sheet.clear_range_all` | `smartsheet.delete_records` |

**Detection**: `sheet.get_sheet_info` returns `sheets` array → Sheet; `smartsheet.list_tables` returns `sheets` → SmartSheet.

## Title Length Limit

`create_smartcanvas_by_mdx` title max **36 characters**. Use `manage.create_file` for longer titles.

## MDX Content Size

Truncate `mdx` parameter to ~30KB (`head -c 30000`). Larger content may timeout.

## Moving Documents to Folders

`manage.move_file` uses `target_folder_id` (NOT `parent_id`).
Workflow: `create_smartcanvas_by_mdx` → get `file_id` → `manage.move_file` to target folder.

## File Import (Word/Excel)

User preference: Reports should use Word documents, not Excel.
`import_file.sh` → `manage.async_import` → poll until complete.
Word docs generated with python-docx, organized by sections with tables.

## mcporter Token Expiry

`mcporter` tokens can expire after periods of inactivity, causing `manage.*` and `sheet.*` tools to fail with:
```
mcporter] tencent-docs appears offline (fetch failed).
[TypeError: fetch failed]
Client network socket disconnected before secure TLS connection was established
```

**Diagnosis**: `curl https://docs.qq.com` returns `200` (Tencent Docs itself is reachable), but mcporter calls fail with fetch/TLS errors.

**Fix**: Re-authenticate:
```bash
mcporter auth tencent-docs
```
This re-establishes the session token. No config changes needed.

**Prevention**: If mcporter has been idle for more than a few hours in the session, re-auth before file upload/import operations.

## Nested Folder Navigation

For deeply nested folders (e.g., obsbot → youtube → 油管分析):
1. `manage.search_file search_key="obsbot"` → find top-level folder
2. `manage.folder_list folder_id="top-level-id"` → view subfolders
3. Find target subfolder ID, then operate

Use `is_folder` field to distinguish folders from files.
