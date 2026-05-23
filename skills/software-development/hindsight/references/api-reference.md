# Hindsight HTTP API Reference

Base URL: `http://localhost:8888`

## Health & Monitoring

```bash
# 健康检查
curl http://localhost:8888/health
# → {"status":"healthy","database":"connected"}

# 版本信息
curl http://localhost:8888/version

# Prometheus 指标
curl http://localhost:8888/metrics

# OpenAPI 规范（全端点文档）
curl http://localhost:8888/openapi.json
```

## Bank 管理

### 创建 Bank

```bash
curl -X PUT http://localhost:8888/v1/default/banks/my-bank \
  -H "Content-Type: application/json" \
  -d '{"name": "My Bank", "description": "..."}'
```

### 列出 Banks

```bash
curl http://localhost:8888/v1/default/banks
```

### 删除 Bank

```bash
curl -X DELETE http://localhost:8888/v1/default/banks/my-bank
```

### 更新 Bank 配置

```bash
curl -X PATCH http://localhost:8888/v1/default/banks/my-bank/config \
  -H "Content-Type: application/json" \
  -d '{"skepticism": 5, "literalism": 3, "empathy": 4}'
```

Disposition 参数说明：
- `skepticism` (1-10): 怀疑度，越高越需要证据
- `literalism` (1-10): 字面理解程度
- `empathy` (1-10): 共情能力

## 记忆存储与检索

### 存储记忆（Retain）

```bash
curl -X POST http://localhost:8888/v1/default/banks/my-bank/memories \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"content": "Alice works at Google as a software engineer", "context": "work"},
      {"content": "She lives in San Francisco", "context": "personal"}
    ],
    "async": false
  }'
```

`async=true` 会异步处理，立即返回 `operation_id`。`async=false`（默认）等待处理完成再返回。

### 语义召回（Recall）

```bash
curl -X POST http://localhost:8888/v1/default/banks/my-bank/memories/recall \
  -H "Content-Type: application/json" \
  -d '{"query": "Where does Alice work?", "k": 5}'
```

参数：
- `query` (必填): 搜索查询
- `k` (可选, 默认5): 返回结果数
- `type` (可选): 过滤类型 (`experience` / `world`)
- `min_relevance` (可选, 默认0.0): 最低相关性阈值

返回包含：
- `results`: 匹配的记忆单元（含 entities 自动提取）
- `entities`: 提取的实体图谱

### 列出记忆

```bash
curl "http://localhost:8888/v1/default/banks/my-bank/memories/list?limit=20&offset=0"
```

### 反思（Reflect）

基于已有记忆，结合 LLM 生成上下文感知的回复：

```bash
curl -X POST http://localhost:8888/v1/default/banks/my-bank/reflect \
  -H "Content-Type: application/json" \
  -d '{"query": "What do you know about Alice?"}'
```

### 文件记忆

```bash
curl -X POST http://localhost:8888/v1/default/banks/my-bank/files/retain \
  -F "file=@document.pdf" \
  -F "metadata={\"type\": \"report\"};type=application/json"
```

### 记忆图谱

```bash
curl "http://localhost:8888/v1/default/banks/my-bank/graph?type=experience&limit=100"
```

## 后台操作

### 异步操作状态查询

```bash
curl http://localhost:8888/v1/default/banks/my-bank/operations/{operation_id}
```

### 重试失败操作

```bash
curl -X POST http://localhost:8888/v1/default/banks/my-bank/operations/{operation_id}/retry
```

### 触发记忆合并

```bash
curl -X POST http://localhost:8888/v1/default/banks/my-bank/consolidate
```

## 高级功能

### 心智模型管理

```bash
# 创建心智模型
curl -X POST http://localhost:8888/v1/default/banks/my-bank/mental-models \
  -H "Content-Type: application/json" \
  -d '{"name": "user_preferences", "description": "User preferences pattern"}'

# 刷新心智模型
curl -X POST http://localhost:8888/v1/default/banks/my-bank/mental-models/{id}/refresh
```

### 指令管理

```bash
curl -X POST http://localhost:8888/v1/default/banks/my-bank/directives \
  -H "Content-Type: application/json" \
  -d '{"text": "Always respond in Chinese", "type": "system"}'
```

### Webhook 管理

```bash
curl -X POST http://localhost:8888/v1/default/banks/my-bank/webhooks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/webhook", "events": ["memory.created"]}'
```

## 环境变量参考

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HINDSIGHT_API_LLM_API_KEY` | — | LLM API Key（**必填**）|
| `HINDSIGHT_API_LLM_PROVIDER` | `openai` | LLM 提供商 |
| `HINDSIGHT_API_LLM_BASE_URL` | `https://api.openai.com/v1` | 自定义 API 地址 |
| `HINDSIGHT_API_LLM_MODEL` | `gpt-4o-mini` | 使用的模型 |
| `HINDSIGHT_API_HOST` | `0.0.0.0` | API 监听地址 |
| `HINDSIGHT_API_PORT` | `8888` | API 端口 |
| `HINDSIGHT_API_WORKERS` | `1` | 工作进程数 |
| `HINDSIGHT_ENABLE_API` | `true` | 启用 API 服务 |
| `HINDSIGHT_ENABLE_CP` | `true` | 启用控制面板 |
| `HINDSIGHT_CP_HOSTNAME` | `0.0.0.0` | 控制面板监听地址 |
| `HINDSIGHT_CP_PORT` | `9999` | 控制面板端口 |
| `HF_ENDPOINT` | `https://huggingface.co` | 🌐 HuggingFace 端点（中国必设为 `https://hf-mirror.com`） |
| `HINDSIGHT_API_DATABASE_URL` | 内嵌 pg0 | 外置 PostgreSQL 连接串 |
| `HINDSIGHT_API_HEALTH_URL` | `http://localhost:8888/health` | 健康检查地址 |

## MCP 集成

Hindsight 内置 MCP 服务器，位于 `/mcp` 端点。任何 MCP 客户端可直接连接：

```
Endpoint: http://localhost:8888/mcp
```
