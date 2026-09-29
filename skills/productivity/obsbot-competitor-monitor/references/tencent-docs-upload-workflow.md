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

## 代理处理策略（2026-09-28 实测修正）

| 操作 | 直连 | 代理 |
|------|------|------|
| import_file.sh（COS 上传） | ✅ 可用 | ✅ 备用 |
| mcporter async_import | ✅ **成功** | ❌ **405 SSE error** |
| mcporter search_file | ✅ 可用（偶发超时） | ❌ 常超时 |
| mcporter move_file | ✅ 可用 | ✅ 备用 |
| mcporter folder_list | ✅ 可用 | ✅ 都可用 |

**⚠️ 关键教训（2026-09-28 实测）**：

1. **`async_import` 必须直连** —— 加 `https_proxy` 反而返回 `405 (SSE error: Non-200 status code)`。本文件此前写反了，曾据此误判为「token 过期」并做出错误操作。
2. **遇 405 先去掉代理直连重试**，不要立刻跑 `mcporter auth`。
3. 🔴 **绝对不要跑 `mcporter auth tencent-docs --reset`** —— 它会清掉缓存凭证并触发完整 OAuth 流程（需用户在浏览器扫码），期间所有 mcporter 调用全部失效。用户明确批评过这个操作（「按照之前的方法弄就行了，不要你去弄新的」）。只有直连+代理都长期失败、且确认 token 真过期时才走 auth（且不加 `--reset`）。
4. **限流特征**：429 / 405 / i/o timeout 交替出现 = 服务端限流窗口未过。间隔 60s+ 重试，不要换方案（本次连续重试 4 轮后恢复）。
5. `import_file.sh` 的 COS 上传本身不依赖 MCP token，所以它成功 ≠ mcporter 可用，两者独立判断。

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

## 常见故障（2026-09-08 实测）

### HTTP 405 on async_import = mcporter OAuth token 过期
- **症状**：`import_file.sh` 可能仍成功（它用自己的 COS token），但 mcporter 的 `manage.async_import` 报 405（SSE error）
- **修复**：`mcporter auth tencent-docs` → 会打开浏览器授权页 → **请用户扫码/登录确认**（用户之前做过，属于既有流程的一部分，直接请用户操作，不要自己翻凭证文件）
- ⚠️ **不要用 `--reset`** 除非确认要完整重授权：`--reset` 会清掉缓存的 refresh token 并触发完整 OAuth（需用户扫码），且 credentials.json 会被改写
- ⚠️ 连续多次 auth 会触发 **429 限流**（SSE error: Non-200 status code (429)）→ 等 60 秒再重试
- 405/429 时不要怀疑传输层/配置，先等 + 走标准 auth 流程

### 完整 OAuth 时浏览器授权 URL 拿不到
- 管道缓冲导致 `mcporter auth` 的 stdout 不可见时，可读 `~/.mcporter/credentials.json` 的 clientInfo（client_id / redirect_uris 端口 / state）+ codeVerifier 用 S256 推导 code_challenge，拼出 `https://docs.qq.com/scenario/open-claw.html?authType=2&...` 用 `open` 打开
- 这只在万不得已时用；首选是让 mcporter 自己打开浏览器
