---
name: git-secrets-audit
description: git 提交/推送前的密钥与 PII 泄露审计。扫描已跟踪+已暂存+未跟踪文件中的真实 API Key、密码、邮箱、手机号，检查仓库可见性，处理 .gitignore 遗漏。当用户要求"检查 GitHub 有没有泄露"、"上传前安全审查"、或每次 git push 前执行。
version: 1.0.0
tags: [git, security, secrets, api-key, audit, github, pii]
---

# Git 密钥与 PII 泄露审计

在 `git commit` / `git push` 之前执行的安全扫描。适用于 `~/.hermes` 配置仓库及任何工作仓库。

## 触发条件
- 用户要求"上传/更新到 github"时（**先扫描再提交**）
- 用户要求"检查 github 有没有 api 泄露"
- 每日复盘的安全审查环节

## 核心命令（按序执行）

### 1. 一键扫描（推荐 — 用脚本覆盖三层文件）

```bash
python3 ~/.hermes/scripts/git_pre_commit_scan.py --exit
```

> 脚本位于本 skill 的 `scripts/git_pre_commit_scan.py`，也可直接调用 skill 内路径 `~/.hermes/skills/software-development/git-secrets-audit/scripts/git_pre_commit_scan.py`。它检查三类文件并覆盖常见密钥格式 + PII，是日常巡检的首选工具。

脚本检查三类文件：
- **已跟踪**（`git ls-files`）
- **已暂存**（`git diff --cached --name-only`）— `git add -A` 后新文件靠这层兜底
- **未跟踪**（`git ls-files --others --exclude-standard`）

覆盖的密钥格式：`AIzaSy*`(YouTube)、`sk-*`、`ghp_/gho_/ghu_/ghs_`(GitHub)、`tvly-*`(Tavily)、`ok_*`(Omar)、`IL6v*`(ScrapeCreators)、32位hex(ScraperAPI/ScrapeCreators)
PII：邮箱、中国手机号。

### 2. 手动严格扫描（脚本不可用时）

```bash
cd ~/.hermes && git ls-files | xargs grep -nE 'AIzaSy[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|tvly-[A-Za-z0-9]{20,}|ok_[A-Za-z0-9]{20,}|IL6v[A-Za-z0-9]{20,}' 2>/dev/null

# 已暂存文件也要扫（新增文件在暂存区）
git diff --cached --name-only | xargs grep -nE 'AIzaSy|sk-|tvly-|ok_|IL6v' 2>/dev/null

# 未跟踪文件（git add -A 会带上它们）
git ls-files --others --exclude-standard | xargs grep -nE 'AIzaSy|sk-|tvly-|ok_|IL6v' 2>/dev/null
```

### 3. 仓库可见性（必须验证，不能假设）

```bash
gh repo view Leonardo-Chow/hermes-config --json isPrivate -q '.isPrivate'
# 必须返回 true。返回 false = 🔴 立即处理
```

**⚠️ 2026-08-03 教训**：用户要求"改成私人仓库"后，`gh repo edit --visibility private` 曾返回 403（token 缺 repo scope）。复盘表里一直标记"未修复"，但**每日必须重新验证**——仓库实际仍为 public。验证命令失败/返回 false 时，直接引导用户手动操作：
1. 打开 https://github.com/<owner>/<repo>/settings
2. Danger Zone → Change visibility → Make private
3. 输入仓库名确认

**403 处理**：`gh auth refresh -s repo`（交互式，需浏览器）；非交互环境无法刷新，提示用户手动。

## 判断标准（真实 Key vs 占位符）

| 匹配 | 处理 |
|:-----|:-----|
| 字符串含 `...`（如 `AIzaSy...aA1Q`） | ✅ 掩码/占位符，安全 |
| 完整 39+ 字符无 `...` | 🔴 真实 Key，替换为占位符 |
| 文档/注释中的模式引用 | ⚠️ 人工判断 |
| `@im.wechat` 后缀 | ✅ webhook ID 误报，非邮箱 |

**🔴 显示层掩码陷阱（2026-08-24 实战教训）**：Hermes 工具输出会对真实密钥做二次掩码（如把文件里的完整 key 显示成 `AIzaSy...aA1Q`）。因此**扫描输出里带 `...` 的条目不能直接判定为占位符安全**——那可能是显示层加的掩码，文件字节里是完整真 key。验证方法：
1. 用计数查询而非内容展示确认：`git grep -cE 'AIzaSy[A-Za-z0-9_-]{33}' <commit>`（正则要求完整长度，不含点号，命中即真 key）
2. 或用 python 读取文件统计 `len(m)` 和是否含字面 `...`
3. 本次教训：youtube_api_pool.json 历史版本含 3 个完整 AIzaSy key，扫描输出全部显示为 `AIzaSy...XX` 被误判为安全，实际已在公开仓库暴露

**连字符盲区（同日教训）**：`tvly-[A-Za-z0-9]{20,}` 匹配不了 `tvly-dev-*`（连字符中断量词），导致 config.yaml 中真实 Tavily key 漏报。字符类必须含 `-`。

## 修复流程

### 替换密钥为占位符

```python
# 在 ~/.hermes 下执行
import re, subprocess
result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
for f in result.stdout.strip().split('\n'):
    if not f.endswith(('.md', '.py', '.json', '.yaml', '.yml', '.sh')):
        continue
    try:
        content = open(f).read()
        new = re.sub(r'AIzaSy[A-Za-z0-9_-]{33}|tvly-[A-Za-z0-9]{20,}|ok_[A-Za-z0-9]{20,}|IL6v[A-Za-z0-9]{20,}', 'YOUR_API_KEY', content)
        if new != content:
            open(f, 'w').write(new)
            print(f'fixed: {f}')
    except: pass
```

### 排除含 PII 的数据文件

```bash
# 数据文件（CSV/JSON）含邮箱/手机号时，从暂存区移除 + 加入 .gitignore
git rm --cached workspace/ig_kol_bios.json   # 示例
echo 'workspace/ig_kol_bios.json' >> .gitignore
```

### .gitignore 必须覆盖的条目

```gitignore
# API Key 配置文件（每个新池都要加）
config/youtube_api_pool.json
config/tavily_api_pool.json
config/omkar_usage.txt

# 运行时/本地数据
state/
desktop-compat/
verification_evidence.db

# 含 PII 的 KOL 数据
workspace/*.csv
workspace/ig_kol_bios.json
workspace/ig_kol_data.json
```

**⚠️ 新 API 池文件陷阱（2026-08-03）**：新建 `config/tavily_api_pool.json` 后忘了加 .gitignore，内含真实 `tvly-*` key，差点被 `git add -A` 提交。**任何新建的 config/*api_pool*.json 立即加入 .gitignore。**

### 推送

```bash
cd ~/.hermes
git config http.proxy socks5://127.0.0.1:1082 && git config https.proxy socks5://127.0.0.1:1082
git push origin main
# HTTP 代理 503 → 用 SOCKS5(1082) → v2rayN(10808) → ClashX(7890)
git config --unset http.proxy && git config --unset https.proxy  # 推送后清理
```

## 泄露已在历史中的处理

- 即使当前版本已清理，旧 commit 中的 key 仍可能被缓存/已 fork
- **必须轮换 key**：在对应服务后台删除并重新生成（Omar、ScrapeCreators、YouTube 等）
- 轮换后更新 `~/.hermes/config/youtube_api_pool.json`、`~/.config/last30days/.env`

## 报告模板

```markdown
## 🔐 安全审查结果
| 检查项 | 结果 | 详情 |
|:-------|:----:|:-----|
| 已跟踪文件密钥 | ✅/🔴 | 扫描结果 |
| 已暂存文件密钥 | ✅/🔴 | git diff --cached 结果 |
| 未跟踪文件密钥 | ✅/🔴 | git ls-files --others 结果 |
| PII（邮箱/手机号） | ✅/🔴 | 数据文件扫描 |
| 仓库是否 Private | ✅/🔴 | gh repo view 验证 |
| 泄露历史 key 轮换 | ✅/🔴 | 是否已通知用户 |
```
