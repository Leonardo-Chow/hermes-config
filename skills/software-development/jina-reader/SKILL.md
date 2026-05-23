---
name: jina-reader
description: Jina Reader — 将任何 URL 转换为 LLM 友好的 Markdown 格式。通过简单的前缀 https://r.jina.ai/ 实现网页内容提取。
tags: [web-scraping, markdown, llm, content-extraction, jina]
version: 1.0.0
---

# Jina Reader

将任何 URL 转换为 LLM 友好的 Markdown 格式。

## 核心功能

**简单用法：** 在任意 URL 前添加 `https://r.jina.ai/` 前缀，即可获取该页面的干净 Markdown 内容。

```bash
# 原始 URL
https://example.com/article

# Jina Reader 格式
https://r.jina.ai/https://example.com/article
```

## 使用场景

1. **网页内容提取** — 将新闻文章、博客帖子转换为干净的 Markdown
2. **LLM 输入** — 为 AI 模型提供结构化的网页内容
3. **数据采集** — 批量获取网页内容用于分析
4. **内容归档** — 保存网页内容为可读格式

## 使用方法

### 方法 1：直接 curl 请求

```bash
# 获取网页内容
curl -s "https://r.jina.ai/https://www.example.com/article"

# 保存为文件
curl -s "https://r.jina.ai/https://www.example.com/article" > article.md
```

### ⚠️ 已知问题

**当前状态：** Jina Reader 服务在国内访问不稳定，请求经常超时或返回空内容。

**解决方案：**
1. 使用 VPN 代理访问
2. 使用 Camoufox 浏览器作为备用方案
3. 使用 Agent-Reach 的 Jina Reader 通道（已集成）

### 方法 2：Python 请求

```python
import urllib.request

url = "https://r.jina.ai/https://www.example.com/article"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=30)
content = resp.read().decode('utf-8')

print(content)
```

### 方法 3：在 Hermes 中使用

```bash
# 直接使用 terminal 工具
curl -s "https://r.jina.ai/https://techcrunch.com/2026/05/08/cloudflare-says-ai-made-1100-jobs-obsolete-even-as-revenue-hit-a-record-high/"
```

## 输出格式

Jina Reader 返回的 Markdown 包含：

- **标题** — 页面标题
- **正文** — 干净的文本内容，去除广告、导航等干扰
- **图片** — 图片 URL（如果存在）
- **链接** — 相关链接
- **元数据** — 作者、发布时间等

## 优势

| 特性 | 说明 |
|:-----|:-----|
| **无需 API Key** | 免费使用，无需注册 |
| **反爬友好** | 内置反爬机制，成功率更高 |
| **干净输出** | 自动去除广告、导航等干扰 |
| **LLM 优化** | 输出格式专为 AI 模型优化 |
| **支持动态页面** | 可处理 JavaScript 渲染的页面 |

## 限制

- **速率限制**：免费版有请求频率限制
- **页面大小**：超大页面可能被截断
- **登录页面**：无法访问需要登录的页面
- **付费墙**：无法绕过付费墙

## 示例

### 获取新闻文章

```bash
# TechCrunch 文章
curl -s "https://r.jina.ai/https://techcrunch.com/2026/05/08/cloudflare-says-ai-made-1100-jobs-obsolete-even-as-revenue-hit-a-record-high/"

# BBC 新闻
curl -s "https://r.jina.ai/https://www.bbc.com/news/world-us-canada-12345678"
```

### 获取博客帖子

```bash
# 个人博客
curl -s "https://r.jina.ai/https://example.com/blog/my-post"
```

### 获取技术文档

```bash
# GitHub README
curl -s "https://r.jina.ai/https://github.com/jina-ai/reader"
```

## 与其他工具的配合

### 与 Camoufox 配合

```python
# 先用 Camoufox 访问页面，再用 Jina Reader 提取内容
from camoufox.async_api import AsyncCamoufox

async def get_content(url):
    # 先用 Jina Reader 尝试
    jina_url = f"https://r.jina.ai/{url}"
    # 如果失败，再用 Camoufox
    # ...
```

### 与 Agent-Reach 配合

Agent-Reach 的 Jina Reader 通道已集成此功能：

```bash
# 通过 Agent-Reach 使用
agent-reach web read --url "https://example.com/article"
```

## 常见问题

### Q: 为什么某些网站无法获取？

A: 可能原因：
1. 网站有反爬机制
2. 需要登录才能访问
3. 付费墙限制
4. 网站使用了复杂的 JavaScript 渲染

### Q: 如何提高成功率？

A: 建议：
1. 使用 Camoufox 作为备用方案
2. 添加适当的 User-Agent
3. 避免频繁请求同一网站
4. 对于重要网站，使用多种工具组合

### Q: 输出内容不完整怎么办？

A: 解决方案：
1. 检查原始 URL 是否可访问
2. 尝试使用 Camoufox 直接访问
3. 对于超长内容，可能需要分段获取

## 更新日志

- **v1.0.0** (2026-05-09): 初始版本，支持基本 URL 转换功能
