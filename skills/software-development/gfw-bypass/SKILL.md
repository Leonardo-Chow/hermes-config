---
name: gfw-bypass
description: "在中国 GFW 环境下访问被墙网站的策略和工具链。覆盖代理工具信息、备用内容源。VPN 由用户手动开关。"
version: 1.0.0
author: Hermes Agent
tags: [proxy, vpn, gfw, china, network, scraping]
---

# GFW Bypass — 访问被墙内容

当需要访问被墙网站（Google、YouTube、Twitter、经济学人等）时的诊断和解决流程。

## 本机代理环境

### Shadowrocket VPN（主 VPN）⭐
- **已确认可访问:** Google、BBC、CNN、YouTube 等被墙网站
- **由用户手动开关** — 需要时告诉我，我会提示你开启

### 0dcloud VPN（备用 VPN）
- **路径:** `/Applications/0dcloud.app`
- **Bundle ID:** `com.odcloud.app`
- **架构:** 纯 VPN 模式，创建 `utun4` 隧道接口
- **IPC:** Unix socket `/Users/zhoulong/Library/Caches/0dcloud/ipc_99105.sock`
- **⚠️ 不暴露本地代理端口** — 无法通过 `--proxy` 参数使用
- **配置目录:** `~/Library/Application Support/com.odcloud.app/`
- **订阅:** Shadowrocket/Clash 格式，服务器 `47.242.55.240`
- **节点:** AnyTLS 类型，覆盖新加坡/美国/日本/韩国/香港/英国等
- **⚠️ 节点经常不稳定** — 需要用户手动切换

### ClashX Pro（备用代理）
- **端口:** HTTP/SOCKS5 `127.0.0.1:7890`，API `127.0.0.1:9090`
- **节点:** ShadowsocksR/Vmess（nnbin.com），但连接经常 reset
- **API:** `http://127.0.0.1:9090` 返回 `{"hello":"clash"}`

### Clash Verge（已配置 VLESS 节点）⭐
- **内核:** mihomo (Clash.Meta)，支持 VLESS + XTLS-Vision + Reality
- **服务:** `/Library/PrivilegedHelperTools/io.github.clash-verge-rev.clash-verge-rev.service.bundle/`
- **配置:** `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml`
- **端口配置:** `mixed-port: 7897`，API `127.0.0.1:9090`
- **已有节点:** 良心云 VLESS+Reality 集群（香港/新加坡/日本/美国/韩国/台湾/英国）+ 美国主vpn (obsbot)
- **代理组:** 良心云（手动选择）、自动选择（url-test）、故障转移（fallback）

### v2rayN（实际运行的代理客户端）⭐
- **路径:** `/Applications/v2rayN.app`
- **内核:** mihomo，路径 `/Applications/v2rayN.app/Contents/MacOS/bin/mihomo/mihomo`
- **代理端口:** HTTP `127.0.0.1:10808`，SOCKS `127.0.0.1:10809`
- **2026-05-16 确认:** v2rayN 是实际运行的代理客户端，Clash Verge 可能未安装或未启动
- **测试命令:** `curl -s --connect-timeout 10 -x http://127.0.0.1:10808 http://httpbin.org/ip`
- **⚠️ 诊断时优先检查 v2rayN 端口 10808**，而非 Clash Verge 的 7897

## 诊断流程

### Step 1: 检查 VPN 隧道状态
```bash
ifconfig utun4 2>/dev/null | head -5
netstat -rn | grep utun4 | head -5
```
正常应看到 `inet 198.18.0.1` 和路由表条目。

### Step 2: 测试连通性
```bash
# 直接测试（通过 VPN 隧道）
curl -sL --max-time 10 "https://www.google.com" | wc -c

# 通过 ClashX 代理
curl -sL --max-time 10 --proxy http://127.0.0.1:7890 "https://www.google.com" | wc -c

# 通过 SOCKS5
curl -sL --max-time 10 --socks5-hostname 127.0.0.1:7890 "https://www.google.com" | wc -c
```

### Step 3: 检查代理进程
```bash
ps aux | grep -iE "0dcloud|clash|mihomo|sing-box" | grep -v grep
lsof -i -P -n | grep LISTEN | grep -E "7890|7891|7897|1080|9090"
```

### Step 4: ClashX 节点管理
```bash
# 查看当前节点
curl -sL "http://127.0.0.1:9090/proxies" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(k,':',v.get('now','N/A')) for k,v in d.get('proxies',{}).items() if v.get('now')]"

# 切换节点
curl -sL -X PUT "http://127.0.0.1:9090/proxies/Proxy" -H "Content-Type: application/json" -d '{"name":"节点名称"}'
```

## 常见问题

### VPN 隧道已建立但无法访问
- **症状:** `utun4` 存在，`curl` 连接超时或 SSL_ERROR_SYSCALL
- **原因:** VPN 节点本身不可用或被封
- **解决:** 在 0dcloud App 里切换节点，然后重新测试

### ClashX 代理 Connection reset
- **症状:** `curl --proxy` 返回 `Recv failure: Connection reset by peer`
- **原因:** ShadowsocksR/Vmess 节点过期或被封
- **解决:** 在 ClashX 菜单切换节点，或更新订阅

### git push/pull 失败 — 使用 SOCKS5 代理
- **症状:** `git push` 返回 `LibreSSL SSL_connect: SSL_ERROR_SYSCALL` 或 `CONNECT tunnel failed, response 503`
- **解决:** 为 git 配置 SOCKS5 代理（Shadowrocket 本地端口 1082 支持 SOCKS5）：
  ```bash
  cd <repo>
  git config http.proxy socks5://127.0.0.1:1082
  git config https.proxy socks5://127.0.0.1:1082
  git push origin main
  ```
- **⚠️ 优先级:** git 操作默认使用 `socks5://127.0.0.1:1082`，不要用 `http://127.0.0.1:1082`
- **用户需确保 Shadowrocket 已手动开启**

### git push 代理回退策略（2026-06-08 更新）

当 `socks5://127.0.0.1:1082` 不可用时，按序尝试其他代理端口。

**⚠️ 关键经验：SOCKS5 优先于 HTTP 代理**

Shadowrocket HTTP 代理（1082 端口）对 git push 返回 `503 CONNECT tunnel failed`，但同端口的 SOCKS5 协议正常工作。始终使用 `socks5://` 前缀：

```bash
# ✅ 推荐：SOCKS5（稳定）
git config http.proxy socks5://127.0.0.1:1082
git config https.proxy socks5://127.0.0.1:1082

# ❌ 不推荐：HTTP 代理（返回 503）
# git config http.proxy http://127.0.0.1:1082
```

回退顺序：
1. `socks5://127.0.0.1:1082`（Shadowrocket SOCKS5）
2. `socks5://127.0.0.1:10808`（v2rayN SOCKS5）
3. `http://127.0.0.1:7890`（ClashX Pro HTTP）

**清理代理配置**（推送后必须执行）：
```bash
git config --unset http.proxy
git config --unset https.proxy
```
```bash
# 1. Shadowrocket (1082)
git config http.proxy socks5://127.0.0.1:1082 && git config https.proxy socks5://127.0.0.1:1082 && git push origin main

# 2. v2rayN (10808)
git config http.proxy socks5://127.0.0.1:10808 && git config https.proxy socks5://127.0.0.1:10808 && git push origin main

# 3. ClashX Pro (7890)
git config http.proxy http://127.0.0.1:7890 && git config https.proxy http://127.0.0.1:7890 && git push origin main

# 全部失败：清理代理配置，commit 已本地保存
git config --unset http.proxy && git config --unset https.proxy
```

**⚠️ 关键 pitfall：** 推送失败后**必须**清理 git proxy config（`--unset`），否则后续所有 git 操作（包括非 GitHub 的本地操作）都会走失败的代理而超时。

### 订阅服务器 504
- **症状:** 订阅链接返回 `504 Gateway Time-out`
- **原因:** 订阅服务器 `47.242.55.240` 宕机
- **解决:** 等待恢复，或使用其他订阅源

### npm 源替代 curl|bash 安装脚本（2026-08-24 验证）

GFW 会掐断 `curl -fsSL https://xxx/install | bash` 类官方安装脚本（对 github.com 直接 `SSL_ERROR_SYSCALL`），且当时本机所有代理端口（7890/10808）均不通。但 **registry.npmjs.org 在国内通常直连可达** —— 若工具有 npm 发行版，跳过安装脚本直接用 npm：

```bash
# 例：OpenCode CLI 官方 curl|bash 安装失败后
npm view opencode-ai version        # 先确认 npm 可达 + 拿版本号
npm install -g opencode-ai@latest   # ✅ 成功，约 1m 装完
```

**注意区分桌面版与 CLI 版**：`OpenCode.app` 桌面应用（/Applications）不含独立 CLI 二进制，CLI 必须单独 `npm i -g opencode-ai`。装完用 `which -a <cmd>` 确认可执行文件位置。

### Homebrew 镜像加速（已验证可用）

当 `brew install` 卡在下载环节（GFW 阻断），用中科大镜像：

```bash
# 安装 JDK/工具类
HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles brew install openjdk@21

# 先 fetch 再 install（避免超时）
HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles brew fetch openjdk@21
brew install openjdk@21
```

**已验证可用：** `openjdk@21` (191MB bottle) 通过中科大镜像成功下载。
**注意：** 仅 `brew install` 可用此方式，`brew update` 需换国内 Git 镜像或连 Shadowrocket。

**brew 下载队列卡死处理：**
当 `brew` 下载被 SIGTERM 中断后，后续安装会卡在 `download_queue.rb` 报错：
```
Error: SIGTERM
/opt/homebrew/Library/Homebrew/download_queue.rb:184:in 'Kernel#sleep'
```
**解决：** 删除锁定文件后重试
```bash
rm -f ~/Library/Caches/Homebrew/downloads/*.incomplete
rm -f ~/Library/Caches/Homebrew/downloads/*.downloading  
rm -f /opt/homebrew/Library/Locks/*
```

### pip3 安装替代方案

当 `brew install` 反复超时时，用 `pip3 install` 代替（网络路径不同，有时更快）：

```bash
pip3 install mitmproxy       # ✅ 已验证成功（Mitmproxy 9.0.1）
pip3 install frida-tools     # Frida 脚本工具
```

注意：pip 安装的 CLI 工具在 `~/Library/Python/3.9/bin/` 下，不在 PATH 中。

### 直接下载 GitHub Release

大型工具（如 JADX、APKTool、Frida gadget）可直接从 GitHub Releases 下载（需要用户先手动开启 VPN）。

```bash
# 下载 JADX
curl -sL "https://github.com/skylot/jadx/releases/download/v1.5.1/jadx-1.5.1.zip" -o /tmp/jadx.zip

# 下载 Frida Gadget
curl -sL "https://github.com/frida/frida/releases/download/16.7.19/frida-gadget-16.7.19-android-arm64.so.xz" -o /tmp/frida-gadget.so.xz
```

## 备用内容获取策略

当代理全部不可用时的降级方案：

| 被墙站点 | 降级方案 |
|----------|---------|
| BBC | CNN（Camoufox 可直接访问，无需代理）|
| 经济学人 | BBC Business / Reuters 中文 / 第一财经 |
| YouTube | 无直接替代，搜索相关内容的中文报道 |
| Twitter/X | 微博热搜 / 知乎讨论 |
| Google News | 百度新闻 / 今日头条 |
| GitHub | gh-proxy.com 镜像 |

### 🛡️ Scrapling — 反检测爬虫

Scrapling 是反检测浏览器爬虫，支持 JS 渲染和 Cloudflare 绕过。**被墙网站需要先让用户开启 VPN**。

```bash
# 激活 Scrapling 虚拟环境
source ~/.hermes/skills/scrapling/venv/bin/activate

# 抓取 BBC（需 VPN）
python3 ~/.hermes/skills/scrapling/scripts/bbc_scraper.py --limit 10 --output bbc.json
```

**适用场景：** 抓取被墙的 JS 渲染网站（BBC、CNN 等）
**详见：** `scrapling` skill

### ⚠️ BBC 完全被墙（2026-05 确认）

BBC 网站在**无代理情况下**完全无法访问，包括：
- `www.bbc.com/news` — 返回空内容
- `www.bbc.com/zhongwen/simp` — 返回空内容
- BBC RSS (`feeds.bbci.co.uk`) — 返回空内容
- BBC API — 返回空内容

**解决方案：** 让用户手动开启 VPN 后即可正常访问 BBC。

### ⚠️ CNN 可直接访问（2026-05 确认）

CNN (`www.cnn.com`) 在中国大陆可以**直接访问**，无需代理：
- Camoufox 浏览器可正常加载
- 文章全文可获取
- 图片 CDN (`media.cnn.com`) 可访问
- 适合生成 PDF 归档

### ClashX 代理诊断（详细流程）

```bash
# 1. 检查 ClashX 是否运行
ps aux | grep -i clash | grep -v grep

# 2. 检查代理端口是否监听
lsof -i :7890 2>/dev/null | head -3

# 3. 检查 API 是否响应
curl -s http://127.0.0.1:9090 2>/dev/null
# 正常返回: {"hello":"clash"}

# 4. 查看当前代理组和节点
curl -s http://127.0.0.1:9090/proxies/Proxy 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2)[:1000])"

# 5. 测试代理连通性
curl -x http://127.0.0.1:7890 -s --max-time 10 "https://www.google.com" | head -20
# 空返回 = 代理不通

# 6. 切换节点（如果当前节点不可用）
curl -s -X PUT http://127.0.0.1:9090/proxies/Proxy \
  -d '{"name":"c美国1 VIP1 网址:nnbin.com"}' \
  -H "Content-Type: application/json"
```

**常见问题：**
- ClashX 运行但代理不通 → 节点被封，需要切换
- 所有节点都不通 → 订阅过期，需要更新
- API 返回正常但 curl 代理超时 → 检查系统代理设置

### ⚠️ 国内网站反爬升级案例

**千度热播 / LMI Live（qiandurebo.com）— 2026-05 确认：**
- 旧版：PHP 页面，curl 可直接获取 FLV 直播源
- 新版：Vue.js SPA + CloudFront CDN + AES 加密 API
- 反爬：JS 挑战页 + 浏览器指纹检测 + 假内容蜜罐（注入「草履虫科普」文本）
- 结论：所有自动化方案均失效，DouyinLiveRecorder 的千度热播集成已失效
- 详见：`android-reverse-engineering` skill 的 `references/lmi-live-app-analysis.md`

### ⚠️ 存档服务也被墙

以下存档服务在中国大陆也无法访问：
- archive.today (archive.ph) — 超时
- Wayback Machine (web.archive.org) — 超时
- Google Cache (webcache.googleusercontent.com) — 超时
- 12ft.io — 超时

### ⚠️ MiMo 联网搜索的限制

MiMo 的 `web_search` 工具是**模拟的**，不是真实的联网搜索：
- ❌ 无法获取被墙网站的真实内容
- ❌ 无法绕过付费墙
- ❌ 无法访问存档服务
- ✅ 可以生成**仿写文章**（BBC/Reuters/Economist 风格）

当需要英文财经新闻全文时，可以让 MiMo 生成仿写文章，然后生成 PDF。

## ⛔ VPN 节点切换规则

**绝对禁止**：Agent 不要操作 VPN、不要切换节点、不要连接/断开 VPN。

**规则**：
- 被墙网站无法访问时，**提示用户手动开启 VPN**
- 不由我执行任何 VPN 操作命令
- 用户手动操作后告诉我，我再继续

## MiMo 联网搜索（模拟搜索，非真实抓取）

当 VPN 完全不可用且用户接受 AI 生成内容时，可用 MiMo API 的 `tools` 参数触发模拟联网搜索。

**⚠️ 关键限制：**
- ❌ 无法获取被墙网站的真实内容
- ❌ 无法绕过付费墙
- ❌ 无法访问 archive.today、Wayback Machine 等存档服务
- ✅ 可以生成**高质量仿写文章**（BBC/Reuters/Economist 风格）

**推荐工作流：** 不使用 `tools` 参数，直接让 MiMo 生成仿写文章（500-900字），然后用 Playwright 生成 PDF。

```python
# 正确：直接生成仿写文章（不触发 web_search）
payload = {
    'model': 'mimo-v2.5-pro',
    'messages': [{'role': 'user', 'content': '请生成 BBC Business 风格的财经新闻（500字+），主题：...'}]
    # 不包含 tools 参数
}
```

API 端点: `https://token-plan-cn.xiaomimimo.com/v1/chat/completions`
API Key: 从 `~/.hermes/auth.json` 的 `credential_pool.xiaomi[0].access_token` 读取

**详见：** 本 skill 的 `references/mimo-web-search.md`（原 `mimo-web-search` skill 完整内容）

## 订阅链接故障排除

### "客户端版本太旧" 错误
- **症状**：订阅链接返回 base64 编码的提示信息，解码后显示"客户端版本太旧了"
- **原因**：订阅服务器检测到 Shadowrocket 版本过低，拒绝返回节点列表
- **解决**：
  1. 打开 App Store 检查 Shadowrocket 更新
  2. 或联系 VPN 服务商获取新的订阅链接
- **检测命令**：
  ```bash
  # 解码订阅内容查看是否为错误提示
  curl -s "http://47.242.55.240/link/9Yinklz3hNqvzVeB?list=shadowrocket" | base64 -d
  ```

### 订阅服务器 504
- **症状**：订阅链接返回 `504 Gateway Time-out`
- **原因**：订阅服务器 `47.242.55.240` 宕机
- **解决**：等待恢复，或使用其他订阅源

## 添加 VLESS 节点到 Clash Verge

详见 `references/clash-verge-vless-config.md`，包含 vless:// 链接解析、节点格式（Reality/普通TLS）、Python 配置脚本。

**⚠️ 关键 Pitfall：** 永远不要用 sed 编辑 Clash Verge 的 YAML 配置（含 emoji/Unicode 会破坏文件）。必须用 Python。

## 用户需操作事项

当需要访问被墙网站时，我会提示你手动开启 VPN。开启后告诉我即可。
