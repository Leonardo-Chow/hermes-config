# 腾讯文档上传流程

## 完整流程

### 1. 上传文件到 COS
```bash
cd ~/.hermes/skills/tencent-docs && bash import_file.sh /path/to/file.xlsx
```

输出示例：
```
IMPORT_READY
FILE_KEY:temp/u.../import_xxx.xlsx
FILE_NAME:filename.xlsx
FILE_MD5:xxx
TASK_ID:drivetask_xxx
FILE_SIZE:1234
```

### 2. 触发异步导入
```bash
mcporter call "tencent-docs" "manage.async_import" --args '{
  "task_id": "drivetask_xxx",
  "file_size": "1234",
  "file_key": "temp/u.../import_xxx.xlsx",
  "file_name": "filename.xlsx",
  "file_md5": "xxx"
}'
```

### 3. 等待并搜索文件
```bash
sleep 5
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key": "文件名关键词"}'
```

### 4. 移动到目标文件夹
```bash
mcporter call "tencent-docs" "manage.move_file" --args '{
  "file_id": "从search结果获取",
  "target_folder_id": "DnNkcnCRIHGt"
}'
```

### 5. 验证
```bash
mcporter call "tencent-docs" "manage.folder_list" --args '{"folder_id": "DnNkcnCRIHGt"}'
```

## 代理处理策略

mcporter 和 import_file.sh 的代理需求不一致：

| 操作 | 直连 | 代理 |
|------|------|------|
| import_file.sh | ✅ 通常可用 | ✅ 备用 |
| mcporter async_import | ❌ 常超时 | ✅ 通常可用 |
| mcporter search_file | ✅ 通常可用 | ❌ 常超时 |
| mcporter move_file | ❌ 常超时 | ✅ 通常可用 |
| mcporter folder_list | ✅ 通常可用 | ✅ 都可用 |

**策略**：
1. 先尝试直连
2. 遇到 HTTP 405 / 连接超时 → 加代理重试
3. 代理也失败 → 等 3-5 秒后重试

## 代理设置
```bash
export https_proxy=http://127.0.0.1:1082
export http_proxy=http://127.0.0.1:1082
```

## 目标文件夹 ID

| 文件夹 | ID |
|--------|-----|
| OBSBOT/竞品监测 | DnNkcnCRIHGt |
| OBSBOT 根目录 | DjbGtzenXmbX |
