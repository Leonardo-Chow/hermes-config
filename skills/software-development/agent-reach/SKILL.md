---
name: agent-reach
description: "Agent-Reach — give your AI agent eyes to see the internet. Read & search Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu, Weibo, WeChat — one CLI, zero API fees. 19k+ stars."
version: 1.0.0
author: Hermes Agent
tags: [agent-reach, scraping, web, social-media, cli]
---

# Agent-Reach Skill

[Agent-Reach](https://github.com/Panniantong/Agent-Reach) gives AI agents access to 16+ internet platforms. It's an installer + doctor + config tool — after setup, agents call upstream tools directly (yt-dlp, gh CLI, Jina Reader, mcporter, etc.).

## Status

Installed at `/Users/zhoulong/.hermes/hermes-agent/venv/bin/agent-reach` (v1.4.0)

### ✅ Active Channels (9/16)
| Channel | Tool | Status |
|---------|------|--------|
| 📄 **任意网页** | Jina Reader (`curl https://r.jina.ai/URL`) | ✅ |
| 📺 **YouTube** | yt-dlp | ✅ |
| 📡 **RSS/Atom** | feedparser | ✅ |
| 🔍 **全网语义搜索** | mcporter + Exa MCP | ✅ |
| 💬 **微信公众号** | Exa search | ✅ |
| 📺 **B站** | yt-dlp + B站 API | ✅ |
| 🐦 **Twitter/X** | `twitter` CLI (cookie saved, needs proxy) | ✅ |
| 🗨️ **V2EX** | 公开 API | ✅ |
| 📖 **Reddit** | `rdt` CLI (LeonardoChow1) | ✅ |

### ✅ Optional Channels (Installed)
| Channel | Tool | Auth Required |
|---------|------|:-------------:|
| 📕 **小红书** | `xhs` CLI v0.6.4 | ✅ Cookie 已配 |
| 🐦 **微博** | mcp-server-weibo v1.0.7 | ✅ Cookie 已配 (WEIBO_COOKIE env) |
| 🎵 **抖音** | yt-dlp + Tavily | 需 cookies (yt-dlp)，搜索可用 |

### ❌ Available but not configured
| Channel | Setup |
|---------|-------|
| 📈 **雪球** | `agent-reach install --channels=xueqiu` |
| 💼 **LinkedIn** | `agent-reach install --channels=linkedin` |
| 🎙️ **小宇宙** | `agent-reach install --channels=xiaoyuzhou` |

## Key Commands

```bash
agent-reach doctor                              # Health check
agent-reach install --env=auto                  # Auto-configure
agent-reach install --channels=all              # Install all channels
agent-reach install --channels=twitter,weibo    # Specific channels
agent-reach configure twitter-cookies "..."     # Set Twitter cookies (Header String)
agent-reach configure xhs-cookies "..."         # Set Xiaohongshu cookies
agent-reach configure proxy "http://..."        # Set HTTP proxy
```

**Valid `configure` keys:** `proxy`, `github-token`, `groq-key`, `twitter-cookies`, `youtube-cookies`, `xhs-cookies`

**Weibo cookies** are NOT set via `agent-reach configure`. Instead, set the `WEIBO_COOKIE` env var:
```bash
cat >> ~/.hermes/.env << 'EOF'
WEIBO_COOKIE=SUBP=xxx;SCF=xxx;SUB=xxx;...
EOF
```

## Usage Patterns

### Read any webpage
```bash
curl https://r.jina.ai/URL
```

### YouTube subtitles
```bash
yt-dlp --dump-json URL | python3 -c ...
```

### GitHub repos
```bash
gh repo view owner/repo
gh search repos "keyword"
```

### Search the web
Uses Exa (free, no API key) via mcporter MCP.

## Pitfalls

- **macOS Python version trap** — system `python3` is 3.9.6. Agent-Reach requires >= 3.10. Always use the hermes venv python: `/Users/zhoulong/.hermes/hermes-agent/venv/bin/python3 -m pip install ...`
- **yt-dlp installed but doctor reports "not installed"** — yt-dlp lives in the hermes venv but `agent-reach doctor` checks `PATH`. Fix: `ln -sf /Users/zhoulong/.hermes/hermes-agent/venv/bin/yt-dlp ~/.local/bin/yt-dlp`. Verify with `which yt-dlp`. If `~/.local/bin` isn't in PATH, add it to `~/.zshrc`.
- **Exa not configured** — if doctor shows "mcporter已装但Exa未配置", run: `mcporter config add exa https://mcp.exa.ai/mcp`
- **GitHub is blocked in China** — use `gh-proxy.com` prefix on all GitHub URLs for cloning/downloading
- **PyPI is slow in China** — always use `-i https://pypi.tuna.tsinghua.edu.cn/simple` for pip installs
- **npm is slow in China** — `npm config set registry https://registry.npmmirror.com` first
- **`agent-reach configure` has NO `weibo-cookies` key** — Weibo cookies go in `WEIBO_COOKIE` env var
- Cookie-based auth (Twitter, XHS) needs Cookie-Editor Chrome extension → Export → Header String
- Use dedicated secondary accounts for cookie-based platforms (封号风险)
- V2EX may need proxy in China
- **抖音 (Douyin) 实际状态** — `douyin-mcp-server` 因 mcp 依赖冲突无法安装（pip 报 ResolutionImpossible）。替代方案：1) yt-dlp 支持抖音但需要 cookies（`yt-dlp --dump-json URL`，无 cookies 报 "Fresh cookies needed"）；2) Tavily 搜索可找到抖音内容；3) Jina Reader 可读取抖音页面结构但无法获取动态加载的视频列表；4) 直接 curl 抖音返回 JS 混淆代码（反爬虫机制）。完整功能需配置 cookies。
- **`pipx` might not be available** — fall back to `python3 -m pip install` directly

## Reference Files

- `references/install-details.md` — Full install transcript with mirror workarounds and channel fixes
