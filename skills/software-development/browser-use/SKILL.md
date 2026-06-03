---
name: browser-use
description: "browser-use — AI 浏览器自动化框架。通过自然语言任务描述驱动 Agent 控制浏览器完成网页操作（搜索、点击、填写表单、抓取数据等）。支持多 LLM 后端、自定义工具、真实浏览器 Profile 复用。当需要 AI 自动操作浏览器完成复杂网页任务时使用。"
version: "2026-06-03"
tags: [browser, automation, ai-agent, scraping, playwright, chromium]
triggers:
  - browser-use
  - browser automation agent
  - AI browser task
  - automated web task
---

# browser-use — AI 浏览器自动化框架

GitHub: [browser-use/browser-use](https://github.com/browser-use/browser-use) (96.8k ⭐)
Docs: [docs.browser-use.com](https://docs.browser-use.com)

## 核心概念

browser-use 让 LLM Agent 控制浏览器完成自然语言任务。Agent 观察页面 DOM + 截图，决定下一步操作（点击、输入、滚动、导航等），循环直到任务完成。

```
用户任务 → Agent(LLM) → 观察页面状态 → 决定操作 → 执行 → 循环
```

## 安装

```bash
# Python >= 3.11
uv init && uv add browser-use && uv sync

# 如果没有 Chromium
uvx browser-use install
```

## 快速开始

```python
from browser_use import Agent, Browser, ChatGoogle
import asyncio

async def main():
    browser = Browser()
    agent = Agent(
        task="Go to google.com and search for 'browser-use github'",
        llm=ChatGoogle(model='gemini-3-flash-preview'),
        browser=browser,
    )
    await agent.run()

asyncio.run(main())
```

## 核心类

### Agent

```python
from browser_use import Agent

agent = Agent(
    task: str,                           # 必填：自然语言任务描述
    llm: BaseChatModel,                  # 必填：LLM 实例
    browser: Browser | None = None,      # 浏览器实例（可选，默认自动创建）
    browser_session: BrowserSession = None,  # 同 browser 参数
    browser_profile: BrowserProfile = None,  # 浏览器配置
    tools: Tools | None = None,          # 自定义工具
    controller: Tools | None = None,     # 同 tools 参数（别名）
    sensitive_data: dict | None = None,  # 敏感数据（密码等，不会发给LLM）
    initial_actions: list[dict] | None = None,  # 首次执行的操作列表
    # AgentSettings 参数：
    use_vision: bool | 'auto' = True,    # 是否用截图辅助 LLM
    vision_detail_level: 'auto'|'low'|'high' = 'auto',
    max_failures: int = 5,               # 最大连续失败次数
    max_actions_per_step: int = 5,       # 每步最大操作数
    use_thinking: bool = True,           # 是否启用思维链
    use_judge: bool = True,              # 是否启用 judge 评估
    generate_gif: bool | str = False,    # 是否生成操作 GIF
    override_system_message: str = None, # 覆盖系统提示
    extend_system_message: str = None,   # 扩展系统提示
    max_history_items: int = None,       # 最大历史条目数
    step_timeout: int = 180,             # 每步超时（秒）
    enable_planning: bool = True,        # 是否启用规划
    calculate_cost: bool = False,        # 是否计算 token 成本
)
```

### Agent.run() 返回值

```python
history = await agent.run(max_steps: int = 100)

# AgentHistoryList 属性：
history.is_done()          # 是否完成
history.final_result()     # 最终结果文本
history.urls()             # 访问过的 URL 列表
history.errors()           # 错误列表
history.model_actions()    # 所有执行的操作
history.model_thoughts()   # 所有思考过程
history.extracted_content() # 提取的内容
history.usage()            # token 用量统计
```

### Browser / BrowserSession

```python
from browser_use import Browser, BrowserSession, BrowserProfile

# 简单启动
browser = Browser()

# 使用真实 Chrome Profile（保留登录态）
browser = Browser.from_system_chrome(profile_directory='/path/to/profile')

# 自定义配置
profile = BrowserProfile(
    headless: bool = False,            # 是否无头模式
    disable_security: bool = False,    # 禁用同源策略
    extra_chromium_args: list = [],    # 额外 Chrome 参数
    chrome_instance_path: str = None,  # Chrome 可执行文件路径
    user_data_dir: str = None,         # 用户数据目录
    proxy: ProxySettings = None,       # 代理设置
    wait_between_actions: float = 0.5, # 操作间隔
    keep_alive: bool = False,          # 关闭后保持浏览器
)
browser = Browser(browser_profile=profile)

# 使用云端浏览器
browser = Browser(use_cloud=True)
```

### LLM 提供商

```python
from browser_use import (
    ChatBrowserUse,     # browser-use 官方模型（推荐，最快最准）
    ChatGoogle,         # Google Gemini
    ChatAnthropic,      # Anthropic Claude
    ChatOpenAI,         # OpenAI GPT
    ChatDeepSeek,       # DeepSeek
    ChatOllama,         # Ollama 本地模型
    ChatGroq,           # Groq
    ChatMistral,        # Mistral
    ChatAzureOpenAI,    # Azure OpenAI
    ChatOpenRouter,     # OpenRouter
    ChatLiteLLM,        # LiteLLM
)

# 官方模型（推荐）
llm = ChatBrowserUse()
# Pricing: Input $0.20/M, Cached $0.02/M, Output $2.00/M

# Google Gemini
llm = ChatGoogle(model='gemini-3-flash-preview')

# Anthropic Claude
llm = ChatAnthropic(model='claude-sonnet-4-6')

# DeepSeek
llm = ChatDeepSeek(model='deepseek-chat')

# Ollama 本地
llm = ChatOllama(model='llama3')
```

### 自定义工具 (Tools)

```python
from browser_use import Tools
from pydantic import BaseModel

tools = Tools()

@tools.action(description='搜索数据库中的用户')
def search_user(name: str) -> str:
    # 自定义逻辑
    return f"Found user: {name}"

@tools.action(description='保存数据到文件')
def save_data(filename: str, content: str) -> str:
    with open(filename, 'w') as f:
        f.write(content)
    return f"Saved to {filename}"

# 带 context 的工具（需要注入外部数据）
class MyContext(BaseModel):
    db_connection: Any
    api_key: str

tools = Tools[MyContext]()

@tools.action(description='查询数据库')
def query_db(query: str, context: MyContext) -> str:
    return context.db_connection.execute(query)

agent = Agent(
    task="...",
    llm=llm,
    tools=tools,
    # context=MyContext(...)  # 传入上下文
)
```

### 敏感数据

```python
# 密码等敏感数据不会发送给 LLM，只在操作时注入
agent = Agent(
    task="Login to my account",
    llm=llm,
    sensitive_data={
        'username': 'myuser',
        'password': 'mypassword',
        # 或按域名限定
        'example.com': {
            'username': 'user',
            'password': 'pass',
        }
    },
)
```

## CLI 命令

```bash
# 快速浏览器操作
browser-use open https://example.com   # 打开 URL
browser-use state                       # 查看可点击元素
browser-use click 5                     # 点击第5个元素
browser-use type "Hello"               # 输入文本
browser-use screenshot page.png         # 截图
browser-use close                       # 关闭浏览器
```

## 模板快速启动

```bash
# 生成模板文件
uvx browser-use init --template default     # 最简模板
uvx browser-use init --template advanced    # 完整配置
uvx browser-use init --template tools       # 自定义工具示例

# 指定输出路径
uvx browser-use init --template default --output my_agent.py
```

## 进阶用法

### 复用已有浏览器登录态

```python
from browser_use import Agent, Browser, ChatGoogle

# 列出本机 Chrome profiles
profiles = Browser.list_chrome_profiles()
for p in profiles:
    print(f"{p['name']}: {p['directory']}")

# 使用指定 profile
browser = Browser.from_system_chrome(profile_directory=profiles[0]['directory'])
agent = Agent(
    task="Go to github.com and check my notifications",
    llm=ChatGoogle(model='gemini-3-flash-preview'),
    browser=browser,
)
```

### 代理设置

```python
from browser_use import BrowserProfile, ProxySettings

profile = BrowserProfile(
    proxy=ProxySettings(
        server='http://127.0.0.1:1082',
        username='user',  # 可选
        password='pass',  # 可选
    )
)
browser = Browser(browser_profile=profile)
```

### 多标签页操作

```python
# Agent 会自动管理标签页
agent = Agent(
    task="Open 3 product pages and compare prices",
    llm=llm,
    browser=browser,
)
```

### 消息压缩（长任务）

```python
from browser_use.agent.views import MessageCompactionSettings

agent = Agent(
    task="...",
    llm=llm,
    message_compaction=MessageCompactionSettings(
        enabled=True,
        compact_every_n_steps=25,  # 每25步压缩一次
        keep_last_items=6,         # 保留最近6条
    ),
)
```

## 环境变量

```bash
# LLM API Keys
BROWSER_USE_API_KEY=***      # browser-use 云 API
GOOGLE_API_KEY=***           # Google Gemini
ANTHROPIC_API_KEY=***        # Anthropic
OPENAI_API_KEY=***           # OpenAI

# 调试
BROWSER_USE_DEBUG_LOG_FILE=/tmp/debug.log
BROWSER_USE_INFO_LOG_FILE=/tmp/info.log
BROWSER_USE_ACTION_TIMEOUT_S=180  # 操作超时（秒）
```

## ⚠️ Pitfalls

1. **Python >= 3.11 必须** — 低版本不支持
2. **async/await 必须** — 所有 API 都是异步的，必须在 `asyncio.run()` 中调用
3. **Chrome 内存** — headless Chrome 吃内存，生产环境用 Cloud 或限制并发
4. **CAPTCHA** — 开源版无法处理验证码，需要 Browser Use Cloud 的反检测浏览器
5. **GFW 环境** — 在中国大陆需要代理才能访问 Google 等被墙网站；`proxy` 参数设置代理
6. **ChatBrowserUse 需要 API Key** — 官方模型需要在 cloud.browser-use.com 注册获取
7. **真实 Profile 冲突** — 使用 `from_system_chrome()` 时，确保该 Chrome profile 没有被其他实例占用
8. **vision 模式** — `use_vision=True` 会发送截图给 LLM，增加 token 消耗；设为 `'auto'` 按需发送
9. **max_steps** — 默认 100 步，复杂任务可能不够，需要调高
10. **操作间隔** — `wait_between_actions` 默认 0.5s，太快可能导致页面未加载完成
