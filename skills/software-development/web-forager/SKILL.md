---
name: web-forager
description: "Web Forager — 开源搜索+抓取工具包（DuckDuckGo搜索 + 新闻搜索 + 网页抓取转Markdown）。适合AI Agent联网检索。当用户需要搜索网页、搜索新闻、抓取网页内容时使用。"
version: "3.0.1"
---

# Web Forager

开源的 AI Agent 搜索与抓取工具包，支持 DuckDuckGo 搜索、新闻搜索、网页抓取转 Markdown。

## 核心功能

| 功能 | 说明 |
|:-----|:-----|
| `search` | DuckDuckGo 网页搜索（Brave 后备） |
| `news` | DuckDuckGo 新闻搜索，带日期排序和来源归属 |
| `fetch` | 网页抓取转 Markdown/JSON（trafilatura + Jina Reader 后备） |
| `serve` | MCP Server 模式（STDIO） |

## 安装

```bash
pip3 install -U web-forager
```

## CLI 用法

### 搜索
```bash
web-forager search "查询内容" --max-results 5 --safesearch moderate
web-forager search "查询内容" --output-format text  # LLM 友好文本输出
```

### 新闻搜索
```bash
web-forager news "查询内容" --max-results 10
web-forager news "AI" --output-format text
```

### 网页抓取
```bash
web-forager fetch "https://example.com" --format markdown
web-forager fetch "https://example.com" --format json --max-length 2000
web-forager fetch "https://example.com" --with-images  # 包含图片 alt 文本
```

### 版本
```bash
web-forager version
```

## MCP Server

```bash
web-forager serve
web-forager serve --debug
```

## Python API

```python
from web_forager import WebForager
```

## 与其他工具对比

| 特性 | Web Forager | Crawl4AI | Jina Reader |
|:-----|:------------|:---------|:------------|
| 搜索 | ✅ DuckDuckGo+Brave | ❌ | ❌ |
| 新闻搜索 | ✅ | ❌ | ❌ |
| 网页抓取 | ✅ trafilatura | ✅ Playwright | ✅ API |
| MCP Server | ✅ | ❌ | ❌ |
| CLI | ✅ | ✅ | ❌ |
| Agent Skills | ✅ 5个 | ❌ | ❌ |
| 离线/免费 | ✅ | ✅ | 有限制 |

## 适用场景

- **摸鱼日报**：news 搜索获取各领域最新新闻
- **快速调研**：search 搜索 + fetch 抓取详情
- **联网检索**：作为 AI Agent 的搜索后端

## 注意事项

- DuckDuckGo 搜索可能触发频率限制，会自动 fallback 到 Brave
- urllib3 版本警告可忽略（不影响功能）
- fetch 使用 trafilatura 提取，复杂页面可能不完整（可配合 Crawl4AI 补充）
