---
name: repomix
description: "Repomix (v1.14.0) — 将整个仓库打包为一个 AI 友好型文件（XML/Markdown/JSON/Plain），适合喂给 Claude、ChatGPT、DeepSeek 等 LLM。支持本地仓库、远程仓库、文件过滤、代码压缩、Token 统计。"
version: 1.0.0
author: Hermes Agent
tags: [repomix, repo-packing, llm, codebase, ai, npm]
---

# Repomix Skill

[Repomix](https://github.com/yamadashy/repomix) — 把整个仓库打包成一个 AI 能吃的文件，24.5K ⭐ 的 TypeScript 工具。

## 安装

已全局安装（v1.14.0），npm registry 使用 npmmirror 镜像。

```bash
repomix --version   # 验证
```

## 快速使用

```bash
# 基本用法：打包当前目录
repomix

# 指定输出格式
repomix --style markdown -o output.md
repomix --style json -o output.json
repomix --style xml -o output.xml       # 默认格式
repomix --style plain -o output.txt

# 输出到 stdout（适合管道操作）
repomix --stdout --style markdown

# 复制到剪贴板
repomix --copy
```

## 远程仓库（无需 clone）

```bash
# GitHub URL 或 user/repo 格式
repomix --remote yamadashy/repomix
repomix --remote https://github.com/facebook/react
repomix --remote facebook/react --remote-branch main
```

## 文件过滤

```bash
# 只包含特定文件
repomix --include "src/**/*.ts,*.md"

# 排除特定文件（除 .gitignore 外额外排除）
repomix -i "*.test.js,docs/**"

# 禁用默认忽略模式（会包含 node_modules 等）
repomix --no-default-patterns

# 不使用 .gitignore
repomix --no-gitignore
```

## 代码压缩（Tree-sitter 解析）

提取类、函数、接口等核心结构，去掉实现细节：

```bash
repomix --compress
```

## Token 统计

```bash
# 查看文件树+Token数
repomix --token-count-tree

# 显示 token 超过 100 的文件
repomix --token-count-tree 100

# 指定编码方式
repomix --token-count-encoding cl100k_base   # GPT-3.5/4
repomix --token-count-encoding o200k_base    # GPT-4o（默认）
```

## 其他实用选项

```bash
# 去除注释
repomix --remove-comments --remove-empty-lines

# 添加自定义说明头
repomix --header-text "Review this codebase for bugs"

# 拆分大输出
repomix --split-output 500kb

# 包含 Git diff 和提交历史
repomix --include-diffs --include-logs --include-logs-count 30

# 显示行号
repomix --output-show-line-numbers

# 生成技能格式（实验性）
repomix --skill-generate my-skill
```

## 配置方式

创建配置文件 `repomix.config.json`：

```json
{
  "output": {
    "style": "markdown",
    "filePath": "repomix-output.md",
    "removeComments": true,
    "removeEmptyLines": true
  },
  "include": ["src/**/*.ts"],
  "ignore": ["*.test.ts", "dist/**"]
}
```

```bash
# 初始化默认配置
repomix --init

# 使用自定义配置
repomix -c my-config.json
```

## 常用场景

| 场景 | 命令 |
|------|------|
| 给 Claude 送代码 | `repomix --stdout --style markdown` |
| 快速远程仓库分析 | `repomix --remote user/repo --compress --stdout` |
| 代码审查 + 历史 | `repomix --include-diffs --include-logs` |
| 最小化输出 | `repomix --compress --no-file-summary --stdout` |
| 大项目分片 | `repomix --split-output 1mb -o output.xml` |
| 找大文件 | `repomix --top-files-len 20` |
| 安全扫描 | `repomix --no-security-check`（跳过敏感信息扫描） |

## MCP 模式

以 Model Context Protocol 服务器运行，集成到 AI 工具链：

```bash
repomix --mcp
```

## Pitfalls

- **GitHub raw 被墙** — `npm install -g repomix` 需要用 npmmirror 镜像：`npm install -g repomix --registry https://registry.npmmirror.com`
- 大项目（>100MB）输出会很大，建议用 `--compress` 和 `--include` 缩小范围
- `--copy` 依赖系统剪贴板，headless 环境不可用
- `--remote` 会克隆远程仓库到临时目录，首次使用需要下载
- `--split-output` 是等分拆文件，不是按目录拆分
- Token 统计只是估算（基于 tiktoken），不是精确值
- `--mcp` 模式是实验性功能
