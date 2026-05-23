# Agent-Reach Install Details

Installed on 2026-05-08 by Hermes Agent (DeepSeek V4 Flash).

## Version

- Agent-Reach v1.4.0 (installed via `pip install -e .` from cloned repo)
- Installed at: `/Users/zhoulong/.hermes/hermes-agent/venv/bin/agent-reach`

## Network Workarounds (China GFW)

GitHub blocked → use `gh-proxy.com` prefix:
```
git clone --depth 1 https://gh-proxy.com/https://github.com/Panniantong/agent-reach.git
```

PyPI blocked → use Tsinghua mirror:
```
python3 -m pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
python3 -m pip install <pkg> -i https://pypi.tuna.tsinghua.edu.cn/simple
```

npm blocked → use npmmirror:
```
npm config set registry https://registry.npmmirror.com
npm install -g mcporter
```

## Installation Steps (from scratch)

```bash
# 1. Clone repo via mirror
cd /tmp
rm -rf agent-reach
git clone --depth 1 https://gh-proxy.com/https://github.com/Panniantong/agent-reach.git

# 2. Install via pip with Tsinghua mirror
cd agent-reach
python3 -m pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. Run auto-install for infrastructure
agent-reach install --env=auto

# 4. Install optional channels
agent-reach install --channels=twitter,weibo,xiaohongshu,reddit,douyin
```

## Failed Channels & Fixes

### Weibo — `git+https://github.com/Panniantong/mcp-server-weibo.git` timed out
Fix: Manual install via mirror (not through agent-reach)
```bash
cd /tmp
git clone --depth 1 https://gh-proxy.com/https://github.com/Panniantong/mcp-server-weibo.git
python3 -m pip install /tmp/mcp-server-weibo -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**IMPORTANT:** `agent-reach configure` does NOT have a `weibo-cookies` key. Weibo cookies must be set via the `WEIBO_COOKIE` environment variable in `~/.hermes/.env`:
```bash
cat >> ~/.hermes/.env << 'EOF'
WEIBO_COOKIE=SUBP=xxx;SCF=xxx;SUB=xxx;...
EOF
```
The mcp-server-weibo crawler reads this env var at startup via `os.getenv("WEIBO_COOKIE")`. If not set, it falls back to generating visitor cookies (limited functionality).

## Python Version Pitfall (macOS)

The system `python3` on macOS resolves to `/usr/bin/python3` which is **Python 3.9.6** — many modern tools require >= 3.10.
The hermes venv Python is at `/Users/zhoulong/.hermes/hermes-agent/venv/bin/python3` (Python 3.11.15).
**Always use the full venv path** or activate the venv before running pip installs:
```bash
# WRONG — uses system Python 3.9.6:
pip install agent-reach     # fails with "requires Python >=3.10"

# RIGHT — uses hermes venv Python 3.11:
/Users/zhoulong/.hermes/hermes-agent/venv/bin/python3 -m pip install agent-reach
# Or:
source /Users/zhoulong/.hermes/hermes-agent/venv/bin/activate
pip install agent-reach
```
Also affects which Python's site-packages `mcp-server-weibo` and `douyin-mcp-server` end up in.

## Authentication Required Channels

| Channel | Tool | Auth Method |
|---------|------|-------------|
| Twitter/X | `twitter` CLI v0.8.5 | `agent-reach configure twitter-cookies "<header-string>"` |
| Xiaohongshu | `xhs` CLI v0.6.4 | `agent-reach configure xhs-cookies "<header-string>"` |
| Weibo | mcp-server-weibo v1.0.7 | `WEIBO_COOKIE` env var in `~/.hermes/.env` (NOT agent-reach configure) |
| Reddit | `rdt` CLI v0.4.1 | `rdt login` (terminal-based browser auth) |

**Valid `agent-reach configure` keys:** `proxy`, `github-token`, `groq-key`, `twitter-cookies`, `youtube-cookies`, `xhs-cookies`

**Cookie export:** Use Cookie-Editor Chrome extension on the target site → **Export → Header String** → paste as the value
