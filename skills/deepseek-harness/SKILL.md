---
name: deepseek-harness
description: 安装配置 DeepSeek Harness (dsh) 与 OpenRouter provider 凭证。
---

# DeepSeek Harness (dsh)

DeepSeek 官方开源 Agent Harness（npm 包 `@deepseek-ai/dsh`），架构 "Everything is a Plugin"，基于 Cordis。

## 安装

```bash
npm install -g @deepseek-ai/dsh   # 需要 Node.js
dsh --version                      # 2026-08 装的是 0.1.1-rc.2
```

## 运行

```bash
dsh web --no-open        # Web UI @ http://127.0.0.1:3080
dsh web                  # 同上并自动开浏览器
dsh plugin --profile <p> add <pkg>   # 装插件
dsh --profile headless "任务"        # 单任务模式：输出结果即退出
```

## 配置自定义 provider（如 OpenRouter）

`~/.dsh/settings.yaml`（热加载，改完下一条请求生效，无需重启）：

```yaml
agent-default-model:            # 覆盖默认模型（默认 deepseek-official/deepseek-v4-flash）
  provider: openrouter
  model: stealth/ox-alpha
llm-pi-ai:
  providers:
    openrouter:                 # key 即路由 ID（永久，改名需新建）
      displayName: OpenRouter
      apiKeyEnv: OPENROUTER_API_KEY   # 凭证引用名（POSIX 标识符）
      api: openai-completions           # 手写路由必须声明协议
      baseURL: https://openrouter.ai/api/v1
      defaultInput: [text, image]       # 兜底模态；单模型用 models[].input
      models:
        - id: stealth/ox-alpha
          name: Ox Alpha
          contextWindow: 1048576        # 从 /api/v1/models 查
          maxTokens: 131072
```

`~/.dsh/.credentials.yaml`（chmod 600 必须；version 行必须有）：

```yaml
version: 1
refs:
  OPENROUTER_API_KEY: sk-or-v1-xxxx
```

也可不落盘：`export OPENROUTER_API_KEY=…`（refs > env > .env 分层）。

## 本地客户端（自建）

`~/deepseek-harness-client/` — 零依赖 Python 代理 + 单页前端，DeepSeek 官方品牌（鲸鱼 logo #4D6BFE）。

```bash
~/deepseek-harness-client/start.sh   # 自动拉起 dsh + 客户端 @ http://127.0.0.1:8799
```

架构：浏览器 → server.py(:8799, 同源反代绕 CORS) → dsh(:3080) 的原生 RPC `POST /api/<method>`。
RPC 格式：`{"type":"client-request","rpcId":"x","method":"session.list","payload":{}}`。
已验证方法：session.list/create/history/prompt/cancel/selectModel/models、llm.models/providers。
前端渲染规则：`assistant/message` 事件是权威版（丢弃流式累积块防重复）；`turn/end` reason=error 时显示失败提示。

## 原生桌面 App（自建）

`~/Desktop/DeepSeek Harness.app` — Swift + WKWebView 原生壳，双击自动编排：拉起 dsh(:3080) → 拉起内置 server.py(:8799) → 加载界面。Dock 图标为 DeepSeek 鲸鱼。

- Swift 源码：/tmp/ds_harness_app/main.swift（swiftc 编译，Cocoa+WebKit，~90KB 二进制）
- 构建要点：Resources 内打包 server.py + public/ 整目录 + AppIcon.icns + loading.html；server.py 用 `--root` 指定静态目录
- `--root` 必须注册进 argparse（手动 sys.argv 解析会被 argparse 的未知参数报错杀死）
- codesign ad-hoc（`-s -`）+ xattr -dr com.apple.quarantine 免 Gatekeeper 弹窗
- WKWebView navigationDelegate 拦截非 127.0.0.1 域名转交系统浏览器；外部链接经 uiDelegate createWebViewWith 打开

## Pitfalls

- **验证别靠 Web UI**：SPA 在自动化浏览器里点两下就白屏。用 `dsh --profile headless "Reply with exactly: OK"` 端到端验证最可靠（走同一 provider+凭证+模型链路）。
- macOS 无 `timeout` 命令；headless 直接给足 terminal timeout 即可。
- `dsh --dump-config` 只显示静态组合树，用户 settings 层是运行时按 provider 合并的——看不到自己加的路由不代表没生效。
- reasoning 模型网关拒 `developer` role 时加 `compat.supportsDeveloperRole: false`。
- 凭证文件缺 `version: 1` 会报 "pre-release flat layout"。
- 配置错误会在写入时被 validate 拒绝（settings-rejected）；外部编辑出错则保留最后好值并告警。
- **urllib 调 dsh RPC 会被断连**（RemoteDisconnected，原因不明），必须用 `http.client` + `Connection: close`。
- stealth/ox-alpha 走 OpenRouter 共享池，偶发上游限流（429/空响应）；dsh 自动重试 5 次，客户端需渲染 turn/end error。
