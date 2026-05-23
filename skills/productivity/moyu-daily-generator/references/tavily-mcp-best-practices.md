# Tavily MCP 工具最佳实践

## 概述

Tavily MCP 是主力数据采集工具，提供搜索、提取、爬取、研究四大功能。

## 工具列表

| 工具 | 功能 | 适用场景 |
|------|------|----------|
| `mcp_tavily_tavily_search` | 网络搜索 | 获取实时信息、新闻、趋势 |
| `mcp_tavily_tavily_extract` | URL 内容提取 | 提取网页全文、Reddit 页面 |
| `mcp_tavily_tavily_crawl` | 网站爬取 | 深度爬取、批量抓取 |
| `mcp_tavily_tavily_map` | 网站映射 | 获取网站结构、URL 列表 |
| `mcp_tavily_tavily_research` | 综合研究 | 生成研究报告、多源整合 |

## 最佳实践

### 1. 搜索（tavily_search）

```python
# 基础搜索
result = tavily_search(
    query="2026年5月 AI 新闻",
    max_results=10,
    search_depth="basic"  # basic 或 advanced
)

# 时间范围过滤
result = tavily_search(
    query="breaking news today",
    time_range="day",  # day, week, month, year
    max_results=5
)

# 话题过滤
result = tavily_search(
    query="AI news",
    topic="news",  # general, news, finance, tech
    max_results=10
)
```

**技巧**：
- `search_depth="advanced"` 返回更详细的内容，但耗时更长
- `time_range="day"` 获取最新 24 小时内容
- `topic="news"` 专注新闻搜索

### 2. 提取（tavily_extract）

```python
# 提取单个 URL
result = tavily_extract(
    urls=["https://www.reddit.com/r/all/hot/"],
    format="markdown"
)

# 提取多个 URL
result = tavily_extract(
    urls=[
        "https://www.reddit.com/r/all/hot/",
        "https://news.ycombinator.com/"
    ],
    format="markdown"
)
```

**适用场景**：
- Reddit 热门内容（r/all/hot）
- Hacker News 首页
- 新闻文章全文
- 需要登录态的页面（Tavily 代理访问）

### 3. 爬取（tavily_crawl）

```python
# 爬取网站
result = tavily_crawl(
    url="https://example.com",
    max_depth=2,  # 爬取深度
    limit=20      # 最大页面数
)
```

**适用场景**：
- 批量抓取文章列表
- 获取网站所有页面

### 4. 映射（tavily_map）

```python
# 映射网站结构
result = tavily_map(
    url="https://example.com",
    max_depth=2,
    limit=50
)
```

**适用场景**：
- 获取网站所有 URL
- 分析网站结构

### 5. 研究（tavily_research）

```python
# 综合研究
result = tavily_research(
    input="2026年5月中国A股市场最新动态和热点板块",
    model="mini"  # mini 或 default
)
```

**适用场景**：
- 深度研究报告
- 多源信息整合
- 需要引用来源的分析

## 场景选择指南

| 需求 | 推荐工具 | 原因 |
|------|----------|------|
| 获取最新新闻 | `tavily_search` | 快速、实时 |
| 提取 Reddit 热门 | `tavily_extract` | 无需登录、结构化 |
| 获取文章全文 | `tavily_extract` | 绕过付费墙、提取正文 |
| 批量抓取内容 | `tavily_crawl` | 深度爬取、自动翻页 |
| 生成研究报告 | `tavily_research` | 多源整合、自动引用 |

## 注意事项

1. **响应时间**：advanced 搜索比 basic 慢 2-3 倍
2. **内容长度**：extract 返回完整页面，可能很长
3. **解析成本**：返回的是原始内容，需要自行解析
4. **API 限制**：注意 API 调用次数限制

## 与其他工具对比

| 工具 | 优势 | 劣势 |
|------|------|------|
| Tavily MCP | 高质量、结构化、无需登录 | 需要 API Key |
| AutoCLI | 极速、零依赖 | 部分站点需 Chrome 扩展 |
| curl + API | 直接、可控 | 需要处理反爬 |
| Camoufox | 反检测、成功率高 | 配置复杂 |

## Reddit 热门获取示例

```python
# 获取 Reddit 热门内容
result = tavily_extract(
    urls=["https://www.reddit.com/r/all/hot/"],
    format="markdown"
)

# 解析 Trending 话题
# 格式：## 标题\n...r/板块名...🔗[查看](链接)

# 解析 Hot 帖子
# 格式：[标题](链接)...r/板块名...•时间
```
