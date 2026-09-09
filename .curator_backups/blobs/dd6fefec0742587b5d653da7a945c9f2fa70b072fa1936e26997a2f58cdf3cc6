# 腾讯文档 Sheet 上传工作流

## 文件夹结构

```
OBSBOT (DjbGtzenXmbX)
├── 红人筛选 (DTmwKKobNEvK)
├── 竞品监测 (DnNkcnCRIHGt) ← 目标文件夹
├── 项目调研 (DabFzUGHaTCO)
├── 红人视频 (DNmTBhbgCAky)
└── 每日监测 (DumZsGZJrwsf)
```

## 上传方式优先级

### 方式 1: import_file.sh（推荐，保留 Excel 格式）

```bash
# 先尝试直连
cd ~/.hermes/skills/tencent-docs && bash import_file.sh /path/to/file.xlsx

# 失败则加代理
https_proxy=http://127.0.0.1:1082 http_proxy=http://127.0.0.1:1082 \
  cd ~/.hermes/skills/tencent-docs && bash import_file.sh /path/to/file.xlsx
```

成功后会输出：
```
FILE_KEY:temp/u144115264377710403/import_XXX.xlsx
FILE_NAME:2026-06-08——竞品检测报告——时间范围（6.6-6.8）.xlsx
FILE_MD5:xxx
TASK_ID:drivetask_xxx
FILE_SIZE:9013
```

然后执行：
```bash
mcporter call "tencent-docs" "manage.async_import" --args '{"task_id":"...","file_size":"...","file_key":"...","file_name":"...","file_md5":"..."}'
sleep 5
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key":"TITLE"}'
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id":"...","target_folder_id":"DnNkcnCRIHGt"}'
```

### 方式 2: 直接创建 Sheet（降级方案，COS 上传失败时）

```bash
# 1. 创建 Sheet
mcporter call "tencent-docs" "manage.create_file" --args '{"title":"TITLE","file_type":"sheet"}'
# → 返回 file_id

# 2. 移动到目标文件夹
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id":"ID","target_folder_id":"DnNkcnCRIHGt"}'

# 3. 获取 sheet_id
mcporter call "tencent-docs" "sheet.get_sheet_info" --args '{"file_id":"ID"}'
# → 返回 sheets[0].sheet_id

# 4. 批量写入数据
mcporter call "tencent-docs" "sheet.set_range_value" --args '{"file_id":"ID","sheet_id":"SID","values":[["Date","竞品",...],["2026-06-08","Logitech",...]]}'
```

## 关键 Pitfall

1. **set_range_value 必须用二维数组**，第一行是表头
2. **所有值都是字符串类型**，数字也要用 `"1356"` 而非 `1356`
3. **mcporter 代理行为不一致**：
   - `manage.create_file` 通常直连成功
   - `manage.move_file` 有时需要代理
   - `sheet.set_range_value` 通常直连成功
   - 策略：先尝试直连，失败后加代理重试
4. **set_cell_value 逐个调用会超时**（>300s），必须用 set_range_value 批量写入
5. **文件名格式**：`{日期}——竞品检测报告——时间范围（{起始}-{结束}）`

## mcporter 工具名称参考

| 操作 | 工具名 | 参数 |
|------|--------|------|
| 创建文件 | `manage.create_file` | `title`, `file_type` |
| 移动文件 | `manage.move_file` | `file_id`, `target_folder_id` |
| 搜索文件 | `manage.search_file` | `search_key` |
| 列出文件夹 | `manage.folder_list` | `folder_id` |
| 获取表信息 | `sheet.get_sheet_info` | `file_id` |
| 批量写入 | `sheet.set_range_value` | `file_id`, `sheet_id`, `values` |
| 单元格写入 | `sheet.set_cell_value` | `file_id`, `sheet_id`, `row`, `col`, `value_type`, `string_value` |
