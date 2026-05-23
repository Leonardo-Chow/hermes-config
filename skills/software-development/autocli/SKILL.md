---
name: autocli
description: "AutoCLI — blazing fast Rust CLI for fetching data from 55+ websites (Twitter/X, Reddit, YouTube, Bilibili, Zhihu, Xiaohongshu, Weibo, etc.) with a single command. 4.7MB binary, zero deps."
version: 1.0.0
author: Hermes Agent
tags: [autocli, scraping, web, data-fetch, cli, rust]
---

# AutoCLI Skill

[AutoCLI](https://github.com/nashsu/AutoCLI) is a Rust-based CLI tool that turns websites into command-line interfaces. It can fetch data from **55+ sites** (Twitter/X, Reddit, YouTube, HackerNews, Bilibili, Zhihu, Xiaohongshu, Weibo, etc.) with a single command.

## Installation

Already installed at `~/.local/bin/autocli` (v0.3.8).
Verify: `autocli --version`

## Quick Start

```bash
# List all available sites/commands
autocli --help

# Get help for a specific site
autocli hackernews --help

# Fetch data (table format is default)
autocli hackernews top --limit 10

# JSON output (most useful for programmatic use)
autocli hackernews top --limit 5 --format json

# Markdown output
autocli hackernews top --limit 5 --format md
```

## Key Sites & Commands

### Tech & News
| Site | Example | Description |
|------|---------|-------------|
| HackerNews | `autocli hackernews top --limit 10` | Top stories |
| Dev.to | `autocli devto top --limit 10` | Popular dev articles |
| Lobsters | `autocli lobsters recent --limit 10` | Tech link aggregation |
| V2EX | `autocli v2ex hot --limit 10` | Chinese tech community |
| Reuters | `autocli reuters` | Latest news |
| BBC | `autocli bbc` | BBC news |
| Bloomberg | `autocli bloomberg` | Financial news |
| ArXiv | `autocli arxiv search "llm"` | Academic papers |

### Chinese Platforms
| Site | Example | Description |
|------|---------|-------------|
| Weibo | `autocli weibo hot --limit 20` | Weibo trending |
| Zhihu | `autocli zhihu hot --limit 20` | Zhihu trending |
| Bilibili | `autocli bilibili hot --limit 20` | Bilibili trending |
| Xiaohongshu | `autocli xiaohongshu search "美食"` | XHS search |
| Jike | `autocli jike` | Jike (即刻) |
| Douban | `autocli douban` | Douban |
| Xueqiu | `autocli xueqiu search "茅台"` | Stock discussions |
| SMZDM | `autocli smzdm` | What to buy |
| SBCN (Linux.do) | `autocli linux-do` | Linux.do |
| 36Kr / Sina Finance | `autocli sinafinance` | Financial news |

### Social Media & Video
| Site | Example | Notes |
|------|---------|-------|
| Twitter/X | `autocli twitter search "rust lang" --limit 10` | Requires browser session |
| Reddit | `autocli reddit hot --limit 10` | |
| YouTube | `autocli youtube search "rust tutorial" --limit 10` | |
| TikTok | `autocli tiktok` | |
| Instagram | `autocli instagram` | |
| Medium | `autocli medium` | |
| Substack | `autocli substack` | |
| Steam | `autocli steam` | Game store/search |

### Productivity & Tools
| Command | Example | Description |
|---------|---------|-------------|
| gh | `autocli gh repos list` | GitHub CLI passthrough |
| docker | `autocli docker ps` | Docker passthrough |
| kubectl | `autocli kubectl get pods` | Kubernetes passthrough |
| obsidian | `autocli obsidian` | Obsidian vault management |
| readwise | `autocli readwise` | Readwise highlights |
| gws | `autocli gws` | Google Workspace passthrough |

### AI & Auto-Discovery Commands
| Command | Description |
|---------|-------------|
| `autocli explore <url>` | Analyze a website's API surface |
| `autocli generate <url>` | Auto-generate adapter for any website |
| `autocli search <url>` | Search for existing adapters on autocli.ai |
| `autocli cascade <endpoint>` | Auto-detect auth strategy |
| `autocli auth` | Authenticate with autocli.ai |
| `autocli read <url>` | Extract main article content (Readability) |

## Format Options

```bash
autocli <site> <command> --format <format>
```
Formats: `table` (default), `json`, `yaml`, `csv`, `md`

## Tips for Use with Hermes Agent

1. **JSON format + jq** for data extraction:
   ```bash
   autocli hackernews top --limit 5 --format json | python3 -m json.tool
   ```

2. **Fetch content for daily reports/newsletters** — use autocli to grab trending topics from multiple platforms in parallel via `delegate_task`.

3. **Mix with terminal tool** — most autocli commands complete in 1-5 seconds, perfect for real-time data fetching.

4. **Browser-required sites** (Twitter, Bilibili, Zhihu, Xiaohongshu, etc.) need the Chrome extension + `autocli daemon` running. Public API sites (HackerNews, Dev.to, Reuters, etc.) work without any setup.

5. **Passthrough mode** — `autocli gh`, `autocli docker`, `autocli kubectl` wrap existing CLI tools. Make sure the underlying tool is installed separately.

## Pitfalls

- **GitHub is blocked in China** — always use `gh-proxy.com` mirror prefix for downloading the binary (direct `curl -fsSL https://raw.githubusercontent.com/.../install.sh | sh` will time out)
- **npm is slow in China** — if using `npx skills add`, switch npm registry first: `npm config set registry https://registry.npmmirror.com`
- The user is on **macOS Apple Silicon** (`aarch64-apple-darwin`) — download the correct binary arch
- Binary at `~/.local/bin/autocli` — ensure `~/.local/bin` is in PATH
- Some sites (Twitter, Weibo, Xiaohongshu) require a browser login session via the Chrome extension + `autocli daemon`
- Public API sites (HackerNews, Dev.to, Reuters, BBC, etc.) work without any setup
- `autocli doctor` runs diagnostics if a command fails
- Browser-required sites need the Chrome extension loaded — see github releases for `autocli-chrome-extension.zip`
- Use `--format json` for programmatic data extraction

## Reference Files

- `references/installation-guide.md` — Full install transcript with mirror workarounds and per-platform binary names
