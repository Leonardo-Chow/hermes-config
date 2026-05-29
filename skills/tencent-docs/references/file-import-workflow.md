# 腾讯文档文件导入工作流

将本地文件（PDF、DOCX、XLSX 等）上传到腾讯文档云盘。

## 流程（4 步）

### 步骤 1：计算文件信息 + 预导入

```bash
# 使用内置脚本（推荐，自动完成 MD5 计算 + pre_import + curl 上传）
cd ~/.hermes/skills/tencent-docs
bash import_file.sh /path/to/file.pdf
```

脚本输出：
```
IMPORT_READY
FILE_KEY:1d826b940b2c4c63865f032d6b50ff87
FILE_NAME:report.pdf
FILE_MD5:02f61ad3721805383b76e623fdd6d0b9
TASK_ID:drivetask_xxx
FILE_SIZE:8567
```

### 步骤 2：触发异步导入

```bash
mcporter call tencent-docs manage.async_import \
    task_id="drivetask_xxx" \
    file_size=8567 \
    file_key="1d826b940b2c4c63865f032d6b50ff87" \
    file_name="report.pdf" \
    file_md5="02f61ad3721805383b76e623fdd6d0b9"
```

### 步骤 3：轮询导入进度

```bash
# 每 3-5 秒轮询一次，直到 progress=100
mcporter call tencent-docs manage.import_progress task_id="drivetask_xxx"
```

返回：
```json
{
  "file_id": "DCqaAObEatEl",
  "file_name": "report",
  "file_url": "https://docs.qq.com/pdf/DRENxYUFPYkVhdEVs",
  "progress": 100
}
```

### 步骤 4：移动到目标文件夹（可选）

```bash
mcporter call tencent-docs manage.move_file \
    file_id="DCqaAObEatEl" \
    target_folder_id="DHtSaueQJaKb"
```

## 手动分步执行

```bash
# 1. 计算 MD5 和文件大小
MD5=$(md5 -q /path/to/file.pdf)
SIZE=$(stat -f%z /path/to/file.pdf)

# 2. 预导入获取上传链接
mcporter call tencent-docs manage.pre_import \
    file_md5="$MD5" \
    file_name="report.pdf" \
    file_size=$SIZE

# 3. 上传到 COS（使用返回的 upload_url）
curl -X PUT -T /path/to/file.pdf \
    -H "Content-Type: application/octet-stream" \
    "<upload_url>"

# 4. 触发导入
mcporter call tencent-docs manage.async_import ...

# 5. 轮询进度
mcporter call tencent-docs manage.import_progress task_id="xxx"
```

## 常见文件类型对应的腾讯文档格式

| 本地格式 | 导入后格式 | file_url 前缀 |
|----------|-----------|---------------|
| .pdf | PDF | docs.qq.com/pdf/ |
| .docx | Word | docs.qq.com/doc/ |
| .xlsx | Sheet | docs.qq.com/sheet/ |
| .pptx | Slide | docs.qq.com/slide/ |
| .csv | Sheet | docs.qq.com/sheet/ |

## Pitfalls

- **签名错误**：不要手动构造 curl 上传命令，使用 `import_file.sh` 脚本自动处理签名
- **导入超时**：大文件导入可能需要较长时间，轮询间隔 3-5 秒
- **文件夹移动**：导入后文件默认在根目录，需要 `manage.move_file` 移动到目标文件夹
- **file_key 格式**：file_key 是预导入返回的，不是文件路径
- **VPN 导致 docs.qq.com 不可达**：Shadowrocket VPN 开启后 `mcporter call tencent-docs` 报 `fetch failed / ECONNRESET`，即使 `curl https://docs.qq.com` 正常。根因是 VPN 路由导致 mcporter 的 TLS 连接中断。解决：先关 VPN（`scutil --nc stop Shadowrocket`），再 `mcporter auth tencent-docs` 重刷 token，然后重试操作。
- **mcporter token 过期**：当 `manage.pre_import` 返回 `tencent-docs appears offline (fetch failed)` 但网络正常时，通常是 mcporter 的 token 已过期。执行 `mcporter auth tencent-docs` 即可恢复。无需重启或重新配置。
