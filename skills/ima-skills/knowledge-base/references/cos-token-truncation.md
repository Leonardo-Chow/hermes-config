# COS 上传 token 截断问题与解决方案

## 问题描述

`create_media` API 返回的 `cos_credential.token` 长度为 875+ 字符，包含 `+`, `/`, `=` 等特殊符号。当通过 shell 参数传递给 `cos-upload.cjs` 时，会被 shell 截断为 12-15 字符。

**症状**：
- `cos-upload.cjs` 返回 HTTP 403 InvalidAccessKeyId
- 错误信息：`The Access Key Id you provided does not exist in our records`
- 实际上 `create_media` 返回的凭证是有效的

## 解决方案

### 方案一：使用一体化脚本（推荐）

使用 `scripts/upload-to-kb.cjs` 脚本，该脚本在单个 Node.js 进程中完成：
1. 调用 `ima_api.cjs` 创建媒体（通过 `child_process.spawn`，不经过 shell）
2. 在进程内构建 COS 认证头（HMAC-SHA1）
3. 直接通过 `https` 模块上传文件
4. 调用 `ima_api.cjs` 添加知识

```bash
node scripts/upload-to-kb.cjs /path/to/file.pdf <knowledge_base_id> "title"
```

### 方案二：写入临时文件

将凭证写入临时 JSON 文件，修改 `cos-upload.cjs` 以从文件读取凭证：

```bash
# 1. 创建媒体并保存凭证
node ima_api.cjs "openapi/wiki/v1/create_media" '{"file_name":"...","file_size":...}' > /tmp/creds.json

# 2. 修改 cos-upload.cjs 支持 --creds-file 参数
# 3. 使用文件方式调用
node cos-upload.cjs --file /path/to/file.pdf --creds-file /tmp/creds.json
```

## 技术细节

- Token 长度：875 字符
- 截断后长度：12-15 字符
- 特殊字符：`+`, `/`, `=`, `&`
- 根本原因：shell 对特殊字符的转义和截断

## 验证方法

```bash
# 检查 token 长度
node ima_api.cjs "openapi/wiki/v1/create_media" '{"file_name":"test.pdf","file_size":1000}' | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['data']['cos_credential']['token']))"
```

预期输出：`875`（而非 12-15）
