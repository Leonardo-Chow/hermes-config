---
name: hindsight
description: "Hindsight (v0.6.1) — Agent memory system that learns, not just remembers。12.7K ⭐，SOTA 长时记忆基准性能。Docker 服务端 + Python/NPM SDK 客户端。"
version: 1.2.0
author: Hermes Agent
tags: [hindsight, agent-memory, ai-memory, vectorize, python-sdk, docker, podman]
---

# Hindsight Skill

[Hindsight](https://github.com/vectorize-io/hindsight) — 让 AI Agent 拥有真正的学习能力，不仅仅是记住对话历史。对标 RAG 和知识图谱的缺陷，在 LongMemEval 基准测试中达到 SOTA。

## 安装

### 客户端 SDK（Python）

已安装在 uv 虚拟环境 `~/.venvs/hindsight` 中（v0.6.1）：

```bash
source ~/.venvs/hindsight/bin/activate
python -c "from hindsight_client import Hindsight; print('OK')"
```

重新安装/更新：

```bash
uv venv ~/.venvs/hindsight --python 3.12
uv pip install --python ~/.venvs/hindsight/bin/python hindsight-client
```

也可以直接用 `uvx` 运行脚本（不安装）或 `uv run --with hindsight-client` 临时使用。

### 服务端（Docker / Podman 兼容）

本机 Docker 通过 **Podman 5.8.2** 提供（原因：GFW 封锁了 Docker Desktop 和 Colima 的镜像下载），`docker` CLI 已配置通过 Podman Machine 的 Unix socket 连接。详见 `references/podman-setup.md`。

### DeepSeek 配置（本机 LLM）

DeepSeek 是 OpenAI 兼容 API，按如下配置：

```bash
export HINDSIGHT_API_LLM_API_KEY="sk-xxx"               # DeepSeek API Key
export HINDSIGHT_API_LLM_PROVIDER="openai"               # 用 openai provider 兼容
export HINDSIGHT_API_LLM_BASE_URL="https://api.deepseek.com/v1"  # DeepSeek 地址
export HINDSIGHT_API_LLM_MODEL="deepseek-chat"           # DeepSeek 模型名
export HF_ENDPOINT="https://hf-mirror.com"               # ⚠️ 中国必备：HF 镜像
```

### ⚠️ 关键：HuggingFace 镜像（中国用户必备）

Hindsight 启动时会自动下载 embedding 模型 `BAAI/bge-small-en-v1.5`（~130MB），下载自 HuggingFace。在中国网络环境下 HuggingFace 不可达，**必须**设置 `HF_ENDPOINT=https://hf-mirror.com`，否则容器启动后卡死 300 秒然后退出。

**启动命令（完整版）：**

```bash
docker run --rm -d --name hindsight \
  -p 8888:8888 -p 9999:9999 \
  -e HINDSIGHT_API_LLM_API_KEY="sk-xxx" \
  -e HINDSIGHT_API_LLM_PROVIDER="openai" \
  -e HINDSIGHT_API_LLM_BASE_URL="https://api.deepseek.com/v1" \
  -e HINDSIGHT_API_LLM_MODEL="deepseek-chat" \
  -e HF_ENDPOINT="https://hf-mirror.com" \
  -v $HOME/.hindsight-data:/home/hindsight/.pg0 \
  ghcr.io/vectorize-io/hindsight:latest
```

启动后：
- API: http://localhost:8888（首次启动约需 90-120 秒，因下载 embedding 模型）
- UI: http://localhost:9999

### 启动耗时说明

首次启动约 90-120s，因为：
1. DeepSeek 连接验证 ✅（~1s）
2. 内嵌 PostgreSQL 启动 ✅（~3s）
3. 从 HuggingFace 镜像下载 embedding 模型 `bge-small-en-v1.5` ✅（~30-60s，取决于网络）
4. 加载模型到内存 ✅（~15-30s）
5. 服务就绪

在此期间 `curl localhost:8888/health` 会返回空或 `connection reset by peer` —— 这**不是**端口转发问题，只是服务还没就绪。等日志出现 `[WORKER_STATS]` 行就代表 OK。

## 快速上手

### 方式一：Python SDK（快捷方式）

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# 创建记忆库（bank）
client.create_bank(bank_id="my-bank")

# 存储记忆
client.retain(bank_id="my-bank", content="Alice works at Google as a software engineer")
client.retain(bank_id="my-bank", content="Alice lives in San Francisco")

# 搜索记忆
results = client.recall(bank_id="my-bank", query="Where does Alice work?")
print(results)

# 反思：基于记忆生成感知响应
response = client.reflect(bank_id="my-bank", query="Tell me about Alice")
print(response)
```

### 方式二：HTTP API（无需 SDK）

> **⚠️ 批量操作优先用 HTTP API** — Python SDK 的 `retain()` 在批量存入多条时会调用 LLM 逐条分析（~3K tokens/条），容易超时（60s+）。HTTP API 的批量存入快得多（11 条 < 15s）。

```bash
# 健康检查
curl http://localhost:8888/health

# 创建 bank
curl -s -X PUT http://localhost:8888/v1/default/banks/test-bank \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "description": "desc"}'

# 存储记忆（items 里放内容）
curl -s -X POST http://localhost:8888/v1/default/banks/test-bank/memories \
  -H "Content-Type: application/json" \
  -d '{"items": [{"content": "某条记忆内容", "context": "system"}]}'

# 语义召回
curl -s -X POST http://localhost:8888/v1/default/banks/test-bank/memories/recall \
  -H "Content-Type: application/json" \
  -d '{"query": "搜索关键词"}'

# 反思+回答
curl -s -X POST http://localhost:8888/v1/default/banks/test-bank/reflect \
  -H "Content-Type: application/json" \
  -d '{"query": "基于记忆回答的问题"}'

# 开放 API 文档
curl http://localhost:8888/openapi.json | python3 -m json.tool
```

### 批量存入（HTTP API）

当需要一次性存入多条记忆时，HTTP API 比 Python SDK 快得多（SDK 会逐条调用 LLM 分析，批量操作容易超时 60s+）：

```bash
# 多次调用 HTTP API 存入（推荐：每条单独 POST，curl 逐条执行）
curl -s -X POST http://localhost:8888/v1/default/banks/my-bank/memories \
  -H "Content-Type: application/json" \
  -d '{"items":[{"content":"记忆A","tags":["tag1"]}]}'

curl -s -X POST http://localhost:8888/v1/default/banks/my-bank/memories \
  -H "Content-Type: application/json" \
  -d '{"items":[{"content":"记忆B","tags":["tag2"]}]}'
```

Python 循环调用 HTTP API（推荐方式，速度快）：

```python
import requests, json

entries = [
    ("内容1", ["tag1", "tag2"]),
    ("内容2", ["tag3"]),
]

for content, tags in entries:
    resp = requests.post(
        "http://localhost:8888/v1/default/banks/my-bank/memories",
        json={"items": [{"content": content, "tags": tags}]},
    )
    resp.raise_for_status()
```

### 方式三：Hermes 记忆归档工作流

将 Hindsight 作为 Hermes Agent `memory` 的外置归档库——解决 Hermes memory 仅 4000 字符的限制：

**何时归档：** 当 Hermes memory 使用率 > 70% 时，将低频信息迁出到 Hindsight。

**工作流：**

1. **备份 → Hindsight：** 遍历当前 Hermes memory 条目，逐条存入 Hindsight bank（通过 HTTP API，不要用 SDK retain）
2. **清理 Hermes memory：** `memory(action='remove', ...)` 删除已备份的低频条目
3. **保留指针：** 在 Hermes memory 中留一条轻量指针，如 `"Hindsight bank 'hermes-memory-archive' 存有离线记忆，需查时可以让我 recall"`
4. **查询：** 后续需要已归档信息时，用 recall 语义搜索 Hindsight

**建议保留在 Hermes memory 的高频信息：**
- IMA 知识库连接参数（摸鱼日报知识库ID等）
- 定时任务 Job ID
- Audit logging 用法规范
- Hindsight archive bank 指针

**建议迁出的低频信息：**
- 工具详细配置（AutoCLI/Agent-Reach/bb-browser 版本、路径）
- 环境搭建细节（Docker/Podman 参数）
- 一次性安装教程和技能描述
- 已稳定的服务配置（Hindsight 自身的配置）

### 核心 HTTP API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `GET` | `/v1/default/banks` | 列出所有 bank |
| `PUT` | `/v1/default/banks/{bank_id}` | 创建 bank |
| `DELETE` | `/v1/default/banks/{bank_id}` | 删除 bank |
| `POST` | `/v1/default/banks/{bank_id}/memories` | 存储记忆（body: `{"items": [{"content": "..."}]}`） |
| `POST` | `/v1/default/banks/{bank_id}/memories/recall` | 语义召回（body: `{"query": "..."}`） |
| `POST` | `/v1/default/banks/{bank_id}/reflect` | 反思回答（body: `{"query": "..."}`） |
| `GET` | `/v1/default/banks/{bank_id}/memories/list` | 列出记忆（分页） |
| `POST` | `/v1/default/banks/{bank_id}/files/retain` | 文件记忆（上传文件） |
| `GET` | `/v1/default/banks/{bank_id}/graph` | 记忆图谱数据 |

### 存储记忆的字段说明

`items` 数组中的每个对象：

```json
{
  "content": "记忆文本内容",           // 必填
  "context": "system",               // 可选：上下文标签
  "document_id": "conv_123",         // 可选：文档 ID（用于分组）
  "timestamp": "2025-01-15T10:00:00Z", // 可选
  "tags": ["tag1", "tag2"],          // 可选
  "type": "experience"               // 可选：experience（默认）或 world
}
```

## 核心概念

| 概念 | 说明 |
|------|------|
| **Bank** | 记忆库，类似命名空间，不同 Agent/任务使用不同 Bank |
| **Retain** | 存储信息到记忆库 |
| **Recall** | 基于 query 搜索相关记忆 |
| **Reflect** | 结合记忆和上下文生成感知响应 |
| **Bank ID** | 记忆库的唯一标识符 |

## 与其他 Agent 框架集成

```python
from hindsight_client import Hindsight

# 初始化（连接本地 Docker 服务）
client = Hindsight(base_url="http://localhost:8888")

# 在你的 Agent 循环中
def process_message(user_input):
    # 1. 先回忆相关记忆
    memories = client.recall(bank_id="agent-memory", query=user_input)
    
    # 2. 用记忆增强 prompt
    context = f"Relevant memories: {memories}\nUser: {user_input}"
    
    # 3. 处理并存储新信息
    response = llm_call(context)
    client.retain(bank_id="agent-memory", content=f"User said: {user_input}, I responded: {response}")
    
    return response
```

## LLM Wrapper 模式（零代码侵入）

```python
# 用 hindsight 包装你的 LLM 客户端
from hindsight_client.llm_wrapper import wrap_openai
from openai import OpenAI

client = wrap_openai(OpenAI(), base_url="http://localhost:8888")

# 之后正常使用 OpenAI API，记忆自动存储和检索
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What projects have I been working on?"}]
)
```

## LLM 提供商配置

环境变量 `HINDSIGHT_API_LLM_PROVIDER`：

| 值 | 说明 |
|----|------|
| `openai` | OpenAI（默认） |
| `anthropic` | Claude |
| `gemini` | Google Gemini |
| `groq` | Groq |
| `ollama` | 本地 Ollama |
| `lmstudio` | LM Studio |
| `minimax` | MiniMax |

## Pitfalls

- **本机 Docker 由 Podman 提供** — 不是 Docker Desktop。`docker` CLI 通过 `DOCKER_HOST` 连接 Podman socket
- **HF_ENDPOINT 必须设置** — 在中国 = 必设 `https://hf-mirror.com`，否则 embedding 模型下载卡死 300s 然后退出
- **health check 返回空/connection reset ≠ 端口转发问题** — 首次启动需 90-120s 下载 embedding 模型，服务就绪前 health 端点不可用。等日志出现 `[WORKER_STATS]` 或 `📍 Access:` 再测
- **DeepSeek API 配置** — 需要同时设 `HINDSIGHT_API_LLM_BASE_URL` 和 `HINDSIGHT_API_LLM_MODEL`，只改 provider 不够
- **`HINDSIGHT_API_LLM_BASE_URL` 是正确变量名，`OPENAI_BASE_URL` 不被容器内读取**
- **Python 版本要求** — hindsight-client 需要 Python >= 3.10，系统 Python 3.9 不兼容
- 客户端 SDK 没有 CLI 入口，需要通过 Python 脚本或 Hermes Agent 工具调用使用
- 服务端默认使用内置 PostgreSQL（pg0），生产环境建议用外置 PostgreSQL
- HTTP API 的保留端点路径是 `/v1/default/banks/{bank_id}/memories`，body 用 `items` 数组，不是 `documents`
- `items` 里的字段是 `content`（记忆文本），不是 `text`
- 如果想加快首次启动速度，可以预先下载 embedding 模型到本地，挂载到容器的 HuggingFace 缓存路径
- **Podman Port 转发说明** — Podman 在 rootful 模式下通过 gvproxy 转发端口。如果 gvproxy 日志显示连接建立但立即 reset，绝大多数情况下是容器内应用还没完成启动，不是网络问题。`docker logs -f <container>` 是首诊手段
- 可通过 `hindsight-client` npm 包在 Node.js/TypeScript 中使用
- Docker Hub 拉取慢 — 已配置镜像加速 `docker.m.daocloud.io`，详见 `references/podman-setup.md`
- **Python SDK `retain()` 批量操作慢** — 每条记忆都会调用 LLM 分析提取实体（~3K tokens/条）。11 条批量存入曾超时 60s。批量操作请用 HTTP API（curl 或 requests.post），快一个数量级
- **Hermes memory 归档时注意**：SDK 的 `retain()` 慢，但 HTTP API 的 `POST /v1/default/banks/{bank_id}/memories` 在 15s 内完成单条存入，适合用于迁移工作流
- **SDK `recall()` 也可能慢** — 如果 Hindsight 的 LLM provider 响应慢（如 DeepSeek 在高峰期），recall 和 reflect 都会等 LLM 返回。纯语义搜索用 HTTP API 的 `recall` 端点，skip LLM processing
