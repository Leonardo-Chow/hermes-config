---
name: tavily-python
description: "Tavily Python SDK — AI 优化的搜索+提取+爬取+研究 API。当需要高质量网页搜索、URL 内容提取、网站爬取地图、AI 研究报告时使用。需要 API Key。"
version: "0.7.24"
---

# Tavily Python SDK

Tavily 是专为 AI Agent 设计的搜索与内容获取平台，提供搜索、提取、爬取、网站地图、研究报告五大功能。

> ⚠️ **需要 API Key**：免费版每月 1000 次调用。注册地址：https://app.tavily.com

## 安装

```bash
pip3 install -U tavily-python
```

## API Key 配置

```bash
# 环境变量（推荐）
export TAVILY_API_KEY="YOUR_TAVILY_API_KEY"

# 或代码中直接传入
client = TavilyClient(api_key="YOUR_TAVILY_API_KEY")
```

> ⚠️ **当前 API Key 已配置**：`YOUR_TAVILY_API_KEY`

## MCP Server 配置

Tavily 提供远程 MCP Server，已配置到 `~/.hermes/config.yaml`：

```yaml
mcp_servers:
  tavily:
    url: "https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>"
    timeout: 180
    connect_timeout: 60
```

重启 Hermes 后，Tavily 的搜索、提取、爬取、地图工具将自动注册为 `mcp_tavily_*` 工具。

## CLI 暂无

### 1. Search — 网页搜索
```python
from tavily import TavilyClient

client = TavilyClient(api_key="tvly-YOUR_API_KEY")

# 基本搜索
response = client.search("Who is Leo Messi?")

# 精确匹配
response = client.search('"John Smith" CEO', exact_match=True)

# 获取 RAG 上下文
context = client.get_search_context("What happened during Burning Man floods?")

# 快速问答
answer = client.qna_search("Who is Leo Messi?")
```

### 2. Extract — URL 内容提取
```python
# 批量提取（最多 20 个 URL）
urls = [
    "https://en.wikipedia.org/wiki/AI",
    "https://en.wikipedia.org/wiki/ML",
]
response = client.extract(urls=urls, include_images=True)

for result in response["results"]:
    print(f"URL: {result['url']}")
    print(f"Content: {result['raw_content']}")
    print(f"Images: {result['images']}")
```

### 3. Crawl — 网站爬取（需邀请）
```python
response = client.crawl(
    url="https://example.com",
    max_depth=3,
    limit=50,
    instructions="Find all pages about citrus fruits"
)
```

### 4. Map — 网站地图
```python
response = client.map(
    url="https://example.com",
    max_depth=2,
    limit=30,
    instructions="Find pages about citrus fruits"
)
```

### 5. Research — AI 研究报告
```python
# 异步研究报告
response = client.research(
    input="Research latest developments in AI",
    model="pro",
    citation_format="apa"
)
request_id = response["request_id"]
result = client.get_research(request_id)

# 流式输出
stream = client.research(input="Research AI", stream=True)
for chunk in stream:
    print(chunk.decode('utf-8'))
```

## CLI 暂无

Tavily 仅提供 Python SDK，无独立 CLI。需通过 Python 脚本调用。

## 与其他工具对比

| 特性 | Tavily | Web Forager | Crawl4AI | Jina Reader |
|:-----|:--------|:------------|:---------|:------------|
| 搜索 | ✅ AI 优化 | ✅ DDG | ❌ | ❌ |
| 新闻搜索 | ✅ | ✅ | ❌ | ❌ |
| 内容提取 | ✅ 批量 | ✅ 单页 | ✅ | ✅ |
| 网站爬取 | ✅ 需邀请 | ❌ | ✅ | ❌ |
| AI 研究 | ✅ | ❌ | ❌ | ❌ |
| 开源 | ❌ | ✅ | ✅ | ❌ |
| 免费 | 1000/月 | ✅ 无限制 | ✅ | 有限制 |
| 需要 API Key | ✅ | ❌ | ❌ | ✅ |

## 适用场景

- **高质量搜索**：Tavily 搜索结果比 DDG 更精准，适合需要高质量结果的场景
- **批量提取**：一次提取 20 个 URL，适合摸鱼日报多源采集
- **AI 研究报告**：自动生成带引用的研究报告
- **RAG 应用**：`get_search_context()` 一行代码生成 RAG 上下文

## 注意事项

- 需要 API Key，免费版 1000 次/月
- Crawl 功能需要邀请才能使用
- 与 Web Forager / Crawl4AI 互补使用，非替代关系
