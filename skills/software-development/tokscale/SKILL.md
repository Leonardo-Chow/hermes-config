---
name: tokscale
description: "Tokscale (v2.1.0) — 跨 AI 编码 Agent 的 Token 用量追踪 CLI + TUI 工具。支持 Hermes Agent、Claude Code、OpenCode、Codex、Cursor、Gemini CLI 等 20+ 平台。内置实时定价、交互式 TUI、排行榜和 3D 贡献图。"
version: 1.0.0
author: Hermes Agent
tags: [tokscale, token-usage, ai-agents, analytics, monitoring, npm, cli, tui]
---

# Tokscale Skill

[Tokscale](https://github.com/junhoyeo/tokscale) — 追踪所有 AI 编码 Agent 的 Token 用量，原生支持 **Hermes Agent**！2.7K ⭐ Rust 核心 CLI。

支持 20+ 平台：Hermes Agent、Claude Code、OpenCode、Codex CLI、Cursor IDE、Gemini CLI、Amp、Kimi CLI、Qwen CLI、Roo Code、Goose 等。

## 安装

已全局安装（v2.1.0），npm registry 使用 npmmirror 镜像。

```bash
tokscale --version   # 验证
```

也可直接运行不用安装：`npx tokscale@latest`

## 快速使用

```bash
# 启动交互式 TUI（默认模式）
tokscale

# 轻量表格模式
tokscale --light

# 查看 Hermes Agent 用量
tokscale --client hermes

# 今日用量
tokscale --today

# JSON 输出（程序化使用）
tokscale --json --today
```

## 常用命令

| 命令 | 用途 |
|------|------|
| `tokscale` | 启动交互式 TUI（6 个视图：总览/模型/日/时/统计/Agent） |
| `tokscale --light` | 轻量表格模式，适合快速查看 |
| `tokscale models` | 模型用量报告 |
| `tokscale monthly` | 月度用量报告 |
| `tokscale hourly` | 小时级用量报告 |
| `tokscale clients` | 查看本地 Agent 数据位置和会话数 |
| `tokscale graph` | 导出贡献图数据（JSON） |
| `tokscale wrapped` | 生成年度回顾图 |

## 筛选选项

```bash
# 按平台筛选
tokscale -c hermes
tokscale -c claude,opencode

# 按时间筛选
tokscale --today
tokscale --week
tokscale --month
tokscale --since 2025-01-01 --until 2025-03-01
tokscale --year 2025
```

## 查看定价

```bash
tokscale pricing claude-sonnet-4-20250514
tokscale pricing gpt-4o
```

## 社交功能

```bash
# 登录（浏览器 GitHub OAuth）
tokscale login

# 提交用量到排行榜
tokscale submit

# 查看个人信息
tokscale whoami

# 登出
tokscale logout
```

## 对 Hermes Agent 的支持

Tokscale 原生支持 Hermes Agent，数据来源：

- `$HERMES_HOME/state.db`（如果设置了环境变量）
- 默认：`~/.hermes/state.db`

直接运行即可看到 Hermes Agent 的使用数据。

## 配置

配置文件：`~/.config/tokscale/settings.json`

```json
{
  "theme": "blue",
  "refresh": 5
}
```

环境变量：`TOKSCALE_HOME` 可覆盖数据目录。

## Pitfalls

- **GitHub/raw 被墙** — npm 安装需用镜像：`npm install -g tokscale --registry https://registry.npmmirror.com`
- TUI 模式依赖终端支持，SSH 或 headless 环境用 `--light` 替代
- 首次启动会扫描本地所有 Agent 数据，大项目可能需要几秒
- 原生 Rust 模块（`@tokscale/core`）通过 npm 预编译，无需本地 Rust 工具链
- 价格数据来自 LiteLLM，每小时缓存一次
- `tokscale submit` 需要先 `tokscale login`
- Cursor IDE 数据需要额外同步：`tokscale cursor sync`
