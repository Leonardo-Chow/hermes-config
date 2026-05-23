---
name: crawl4ai
description: Crawl4AI — 开源 LLM 友好的网页爬虫和抓取工具。将网页转换为干净的 Markdown 格式，支持深度爬取、LLM 提取、反检测等功能。
tags: [web-scraping, crawler, llm, markdown, playwright, python]
version: 1.0.0
---

# Crawl4AI

🚀🤖 Crawl4AI: Open-source LLM Friendly Web Crawler & Scraper

将网页转换为干净的 LLM 友好 Markdown 格式，适用于 RAG、代理和数据管道。

## 核心功能

| 功能 | 说明 |
|:-----|:-----|
| **LLM 友好输出** | 智能 Markdown，包含标题、表格、代码、引用提示 |
| **快速实践** | 异步浏览器池、缓存、最小跳转 |
| **完全控制** | 会话、代理、Cookie、用户脚本、钩子 |
| **自适应智能** | 学习网站模式，只探索重要内容 |
| **随处部署** | 无密钥、CLI 和 Docker、云友好 |

## 安装

### 基本安装

```bash
# 安装包
pip install -U crawl4ai

# 运行安装后设置
crawl4ai-setup

# 验证安装
crawl4ai-doctor
```

### 浏览器安装（如果遇到问题）

```bash
python -m playwright install --with-deps chromium
```

### 开发安装

```bash
git clone https://github.com/unclecode/crawl4ai.git
cd crawl4ai
pip install -e .

# 安装可选功能
pip install -e ".[all]"  # 安装所有可选功能
```

## 使用方法

### Python API

```python
import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.nbcnews.com/business",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())
```

### ⚠️ 已知问题

**代理配置：** 旧版 `proxy` 参数已弃用，使用 `proxy_config` 替代。

**VPN 使用：** 如果已配置 Shadowrocket VPN，可直接访问被墙网站，无需额外代理配置。

```python
# 直接通过 VPN 访问（推荐）
async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="https://www.google.com")
```

### 命令行界面

```bash
# 基本爬取，输出 Markdown
crwl https://www.nbcnews.com/business -o markdown

# 深度爬取，BFS 策略，最多 10 页
crwl https://docs.crawl4ai.com --deep-crawl bfs --max-pages 10

# 使用 LLM 提取
crwl https://www.example.com/products -q "提取所有产品价格"
```

## 高级用法

### 启发式 Markdown 生成

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.48, 
                threshold_type="fixed", 
                min_word_threshold=0
            )
        ),
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://docs.micronaut.io/4.9.9/guide/",
            config=run_config
        )
        print(f"原始 Markdown 长度: {len(result.markdown.raw_markdown)}")
        print(f"过滤后 Markdown 长度: {len(result.markdown.fit_markdown)}")

if __name__ == "__main__":
    asyncio.run(main())
```

### CSS 选择器提取

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    run_config = CrawlerRunConfig(
        css_selector="article.main-content",
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com/article",
            config=run_config
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())
```

### 代理配置

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig

async def main():
    browser_config = BrowserConfig(
        proxy="http://127.0.0.1:7890",  # ClashX 代理
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://www.google.com")
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())
```

## Docker 部署

```bash
# 拉取并运行最新版本
docker pull unclecode/crawl4ai:latest
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest

# 访问监控面板
# http://localhost:11235/dashboard

# 访问交互式 playground
# http://localhost:11235/playground
```

### Docker API 使用

```python
import requests

# 提交爬取任务
response = requests.post(
    "http://localhost:11235/crawl",
    json={"urls": ["https://example.com"], "priority": 10}
)

if response.status_code == 200:
    print("爬取任务提交成功")
    
if "results" in response.json():
    results = response.json()["results"]
    print("爬取任务完成，结果:")
    for result in results:
        print(result)
else:
    task_id = response.json()["task_id"]
    print(f"爬取任务提交，任务 ID: {task_id}")
    result = requests.get(f"http://localhost:11235/task/{task_id}")
```

## 特性详情

### 📝 Markdown 生成

- **干净 Markdown**：生成干净、结构化的 Markdown，格式准确
- **Fit Markdown**：基于启发式过滤，去除噪声和无关部分
- **引用和参考**：将页面链接转换为编号参考列表
- **自定义策略**：用户可创建自己的 Markdown 生成策略
- **BM25 算法**：使用 BM25 过滤提取核心信息

### 📊 结构化数据提取

- **LLM 驱动提取**：支持所有 LLM（开源和商业）进行结构化数据提取
- **分块策略**：实现基于主题、正则、句子级别的分块
- **余弦相似度**：基于用户查询找到相关内容块
- **CSS 提取**：使用 XPath 和 CSS 选择器快速提取
- **模式定义**：定义自定义模式提取结构化 JSON

### 🌐 浏览器集成

- **托管浏览器**：使用用户自己的浏览器，完全控制
- **远程浏览器控制**：连接 Chrome DevTools Protocol
- **浏览器配置文件**：创建和管理持久化配置文件
- **会话管理**：保存和复用浏览器状态
- **代理支持**：无缝连接带认证的代理
- **多浏览器支持**：兼容 Chromium、Firefox、WebKit

### 🔎 爬取和抓取

- **媒体支持**：提取图片、音频、视频
- **动态爬取**：执行 JS 等待异步内容
- **截图**：捕获页面截图用于调试
- **原始数据爬取**：直接处理原始 HTML 或本地文件
- **链接提取**：提取内部、外部链接和 iframe 内容
- **可自定义钩子**：在每一步定义钩子自定义行为
- **缓存**：缓存数据提高速度
- **元数据提取**：检索结构化元数据
- **iframe 提取**：从嵌入 iframe 提取内容
- **懒加载处理**：等待图片完全加载
- **全页扫描**：模拟滚动加载所有动态内容

## 与其他工具的对比

| 特性 | Crawl4AI | Jina Reader | Firecrawl |
|:-----|:---------|:------------|:----------|
| 开源 | ✅ | ❌ | ❌ |
| 免费使用 | ✅ | 有限制 | 付费 |
| LLM 提取 | ✅ | ❌ | ✅ |
| 深度爬取 | ✅ | ❌ | ✅ |
| 反检测 | ✅ | ❌ | ✅ |
| Docker 部署 | ✅ | ❌ | ✅ |
| CLI 支持 | ✅ | ❌ | ❌ |

## 使用场景

1. **RAG 数据管道** — 将网页转换为 LLM 友好的 Markdown
2. **数据采集** — 批量获取网页内容用于分析
3. **内容归档** — 保存网页内容为可读格式
4. **竞争分析** — 抓取竞争对手网站信息
5. **新闻聚合** — 从多个新闻网站获取内容
6. **研究数据收集** — 学术研究数据采集

## 常见问题

### Q: 如何绕过反爬机制？

A: Crawl4AI 内置反检测功能：
- 自动 3 级反爬检测
- 代理升级
- 用户代理轮换
- Cookie 和会话管理

### Q: 如何处理 JavaScript 渲染的页面？

A: Crawl4AI 使用 Playwright 浏览器，自动处理 JavaScript 渲染。

### Q: 如何提高爬取速度？

A: 建议：
1. 启用缓存：`cache_mode=CacheMode.ENABLED`
2. 使用 CSS 选择器限制范围
3. 并发爬取多个 URL

### Q: 如何提取特定内容？

A: 使用 CSS 选择器或 LLM 提取：
- CSS 选择器：快速、准确
- LLM 提取：灵活、智能

## 更新日志

- **v0.8.6** (2026-05-09): 安全热修复 — 替换 `litellm` 为 `unclecode-litellm`
- **v0.8.5** (2026-05-08): 反爬检测、Shadow DOM、60+ Bug 修复
- **v0.8.0** (2026-05-07): 崩溃恢复、预取模式
- **v0.7.8** (2026-05-06): 稳定性和 Bug 修复

## 相关链接

- [GitHub 仓库](https://github.com/unclecode/crawl4ai)
- [文档网站](https://docs.crawl4ai.com/)
- [Discord 社区](https://discord.gg/jP8KfhDhyN)
- [PyPI 包](https://pypi.org/project/crawl4ai/)
