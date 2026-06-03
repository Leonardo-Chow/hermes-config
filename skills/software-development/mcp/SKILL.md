---
name: mcp
description: "Model Context Protocol (MCP) — LLM 应用与外部工具/数据源的标准化连接协议。当需要构建 MCP Server（暴露工具/资源/提示）、MCP Client（连接已有 Server）、或配置 Hermes 的 MCP 集成时使用。"
version: "2026-06-03"
tags: [mcp, protocol, llm, tools, server, client, stdio, sse, streamable-http]
triggers:
  - mcp server
  - mcp client
  - model context protocol
  - mcp tools
  - mcp integration
---

# Model Context Protocol (MCP)

官网: [modelcontextprotocol.io](https://modelcontextprotocol.io)
GitHub: [github.com/modelcontextprotocol](https://github.com/modelcontextprotocol) (47.6k followers)
Spec: [specification/2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)

## 核心概念

MCP 是 LLM 应用与外部数据源/工具之间的**标准化连接协议**，类似 USB-C 之于设备。它将「提供上下文」与「LLM 交互」分离。

```
LLM 应用 (Host) ←→ MCP Client ←→ MCP Server ←→ 外部工具/数据
```

### 三大原语 (Primitives)

| 原语 | 控制方 | 描述 | 类比 |
|------|--------|------|------|
| **Tools** | Model 控制 | LLM 调用的函数（有副作用） | POST endpoint |
| **Resources** | Application 控制 | 提供给 LLM 的数据（无副作用） | GET endpoint |
| **Prompts** | User 控制 | 用户选择的交互模板 | Slash commands |

### 传输方式 (Transports)

| Transport | 场景 | 说明 |
|-----------|------|------|
| **stdio** | 本地进程 | Client 启动 Server 子进程，通过 stdin/stdout 通信 |
| **Streamable HTTP** | 远程/网络 | HTTP POST + SSE 流式响应，推荐的新标准 |
| **SSE** (已废弃) | 旧版远程 | 被 Streamable HTTP 取代 |

### 生命周期

```
Client → initialize (能力协商) → initialized 通知
Client ↔ Server 正常通信 (请求/响应/通知)
Client/Server → shutdown (关闭连接)
```

## SDK 官方支持

| 语言 | 包名 | 安装 |
|------|------|------|
| **Python** | `mcp` | `pip install "mcp[cli]"` |
| **TypeScript** | `@modelcontextprotocol/server` | `npm install @modelcontextprotocol/server` |
| **Java** | `io.modelcontextprotocol:sdk` | Maven Central |
| **Kotlin** | `io.modelcontextprotocol:kotlin-sdk` | Maven Central |
| **Go** | `github.com/modelcontextprotocol/go-sdk` | `go get` |
| **C#** | `ModelContextProtocol` | NuGet |
| **Rust** | `mcp-core` / `mcp-server` | crates.io |
| **Ruby** | `mcp` | RubyGems |
| **PHP** | `mcp/sdk` | Composer |
| **Swift** | `mcp-swift-sdk` | SPM |

---

## Python SDK (重点)

### 安装

```bash
# 推荐 uv
uv init mcp-server-demo && cd mcp-server-demo
uv add "mcp[cli]"

# 或 pip
pip install "mcp[cli]"
```

### 快速开始 — FastMCP

```python
from mcp.server.fastmcp import FastMCP

# 创建 MCP Server
mcp = FastMCP("Demo")

# 定义 Tool（LLM 可调用的函数）
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# 定义 Resource（提供数据给 LLM）
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# 定义 Prompt（用户可选的模板）
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

# 运行
if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # HTTP 模式
    # mcp.run(transport="stdio")          # stdio 模式
```

### Tools（工具）详解

```python
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

mcp = FastMCP("Tool Examples")

# 基础 Tool
@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# 异步 Tool + 进度上报
@mcp.tool()
async def long_task(task_name: str, ctx: Context[ServerSession, None], steps: int = 5) -> str:
    """Execute a task with progress updates."""
    await ctx.info(f"Starting: {task_name}")
    for i in range(steps):
        progress = (i + 1) / steps
        await ctx.report_progress(progress=progress, total=1.0, message=f"Step {i+1}/{steps}")
    return f"Task '{task_name}' completed"

# 结构化输出（自动 JSON Schema）
class WeatherData(BaseModel):
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage")
    condition: str

@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Get weather for a city - returns structured data."""
    return WeatherData(temperature=22.5, humidity=45.0, condition="sunny")

# 禁用结构化输出
@mcp.tool(structured_output=False)
def raw_tool() -> str:
    """Returns plain text only."""
    return "raw result"

# 直接返回 CallToolResult（完全控制）
from mcp.types import CallToolResult, TextContent

@mcp.tool()
def advanced_tool(message: str) -> CallToolResult:
    """Full control including _meta field."""
    return CallToolResult(
        content=[TextContent(type="text", text=f"Processed: {message}")],
        structuredContent={"result": "success"},
        _meta={"hidden": "data for client only"},
    )
```

### Resources（资源）详解

```python
@mcp.resource("file://documents/{name}")
def read_document(name: str) -> str:
    """Read a document by name."""
    return f"Content of {name}"

@mcp.resource("config://settings")
def get_settings() -> str:
    """Get application settings (static resource)."""
    return '{"theme": "dark", "language": "en"}'
```

### Prompts（提示模板）

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt(title="Code Review")
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

@mcp.prompt(title="Debug Assistant")
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]
```

### Lifespan（生命周期管理）

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

class Database:
    @classmethod
    async def connect(cls) -> "Database":
        return cls()
    async def disconnect(self) -> None:
        pass
    def query(self) -> str:
        return "Query result"

@dataclass
class AppContext:
    db: Database

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()

mcp = FastMCP("My App", lifespan=app_lifespan)

@mcp.tool()
def query_db(ctx: Context[ServerSession, AppContext]) -> str:
    db = ctx.request_context.lifespan_context.db
    return db.query()
```

### 运行 Server

```bash
# 开发模式（带 Inspector UI）
uv run mcp dev server.py

# 直接运行 stdio
uv run mcp run server.py --transport stdio

# HTTP 模式
uv run server.py  # 如果代码里 mcp.run(transport="streamable-http")

# Claude Desktop 集成
uv run mcp install server.py
```

---

## MCP Client（客户端）

### stdio 连接

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
    env={"KEY": "value"},
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 列出可用工具
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"Tool: {t.name} - {t.description}")

            # 调用工具
            result = await session.call_tool("add", arguments={"a": 5, "b": 3})
            print(result.content[0].text)  # "8"

            # 列出资源
            resources = await session.list_resources()
            content = await session.read_resource("greeting://World")

            # 列出/获取 Prompt
            prompts = await session.list_prompts()
            prompt = await session.get_prompt("greet_user", {"name": "Alice"})

asyncio.run(main())
```

### Streamable HTTP 连接

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client("http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

asyncio.run(main())
```

---

## TypeScript SDK

```bash
# Server
npm install @modelcontextprotocol/server

# Client
npm install @modelcontextprotocol/client

# Middleware（Express/Hono/Node.js HTTP）
npm install @modelcontextprotocol/node
npm install @modelcontextprotocol/express
npm install @modelcontextprotocol/hono
```

```typescript
import { Server } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import { z } from "zod";

const server = new Server({ name: "demo", version: "1.0.0" });

server.tool("add", { a: z.number(), b: z.number() }, async ({ a, b }) => ({
  content: [{ type: "text", text: String(a + b) }],
}));

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## 高级特性

### 结构化输出

Tools 可返回结构化数据（Pydantic/TypedDict/dict），自动生成 `outputSchema`：

```python
class UserData(BaseModel):
    name: str
    age: int
    email: str | None = None

@mcp.tool()
def get_user(user_id: str) -> UserData:
    return UserData(name="Alice", age=30)
```

支持的返回类型：Pydantic BaseModel、TypedDict、dataclass、`dict[str, T]`、原始类型（自动包装为 `{"result": value}`）。

### OAuth 认证

```python
from mcp.client.auth import OAuthClientProvider, TokenStorage

oauth = OAuthClientProvider(
    server_url="http://localhost:8001",
    client_metadata=OAuthClientMetadata(
        redirect_uris=[AnyUrl("http://localhost:3000/callback")],
        grant_types=["authorization_code", "refresh_token"],
    ),
    storage=InMemoryTokenStorage(),
    redirect_handler=handle_redirect,
    callback_handler=handle_callback,
)
```

### 分页

```python
@server.list_resources()
async def list_resources_paginated(request: types.ListResourcesRequest) -> types.ListResourcesResult:
    cursor = request.params.cursor
    start = 0 if cursor is None else int(cursor)
    page_items = [/* ... */]
    next_cursor = str(start + 10) if start + 10 < len(ITEMS) else None
    return types.ListResourcesResult(resources=page_items, nextCursor=next_cursor)
```

### Context 注入（进度/日志）

```python
@mcp.tool()
async def process(data: str, ctx: Context[ServerSession, None]) -> str:
    await ctx.info("Processing started")
    await ctx.debug("Debug message")
    await ctx.report_progress(progress=0.5, total=1.0)
    await ctx.warning("Low confidence")
    return "done"
```

---

## Hermes Agent MCP 集成

Hermes 已内置 MCP Client 支持。配置文件位于 `~/.hermes/config.yaml`：

```yaml
mcp:
  servers:
    tavily:
      transport: stdio
      command: "npx"
      args: ["-y", "tavily-mcp@latest"]
      env:
        TAVILY_API_KEY: "***"
    filesystem:
      transport: stdio
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

详见 `native-mcp` skill。

---

## ⚠️ Pitfalls

1. **Python >= 3.10** — FastMCP 需要 3.10+（type hints 语法）
2. **async 必须** — 所有 MCP API 都是异步的
3. **stdio vs HTTP** — stdio 适合本地单用户，HTTP 适合多用户/远程
4. **SSE 已废弃** — 新项目用 Streamable HTTP，不要用 SSE
5. **Tool 描述很重要** — LLM 通过 description 决定调用哪个 tool，写清楚
6. **Resource URI 模板** — 用 `{param}` 语法，不是 `:param`
7. **结构化输出验证** — 返回类型必须有类型注解，无注解类不会生成 schema
8. **CallToolResult 必须完整** — 不能 Optional/Union，空结果用 `CallToolResult(content=[])`
9. **CORS** — 浏览器客户端需要配置 CORS，`allow_origins=["*"]`
10. **Inspector 调试** — `npx -y @modelcontextprotocol/inspector` 可视化调试 Server
