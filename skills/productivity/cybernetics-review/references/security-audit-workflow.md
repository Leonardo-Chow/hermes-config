# 安全审查工作流 (Security Audit Workflow)

每日复盘时执行的安全审查标准流程。适用于 `~/.hermes` 及其他配置仓库。

## 1. 敏感信息扫描

扫描 git 跟踪文件中的真实凭证（排除文档示例和二进制文件）：

```bash
cd ~/.hermes && git ls-files | xargs grep -n \
  'AIzaSy[A-Za-z0-9_-]\{30\}\|sk-[A-Za-z0-9]\{20,\}\|ghp_[A-Za-z0-9]\{30\}\|gho_[A-Za-z0-9]\{30\}\|ghu_[A-Za-z0-9]\{30\}\|ghs_[A-Za-z0-9]\{30\}' \
  2>/dev/null | head -30
```

### 判断标准

| 匹配类型 | 安全风险 | 处理方式 |
|:---------|:--------:|:---------|
| 完整 API Key (39+ 字符) | 🔴 高 | 立即替换为占位符，force push |
| 掩码 Key (含 `...`) | ✅ 安全 | 无需处理 |
| 文档示例 (`sk-xxx...xxxx`) | ✅ 安全 | 无需处理 |
| 二进制文件匹配 | ⚠️ 误报 | 检查是否为编译嵌入字符串 |

### 验证 Key 是否被掩码

```python
import json
with open('config/youtube_api_pool.json') as f:
    d = json.load(f)
for k in d.get('api_keys', []):
    print(f'Length: {len(k)}, Contains dots: {"..." in k}')
```

- 长度 39 且含 `...` → 已掩码，安全
- 长度 39 且不含 `...` → 真实 Key，需清理

### 批量替换脚本（推荐，比 sed 更可靠）

```python
import re, os, subprocess
os.chdir(os.path.expanduser('~/.hermes'))

# 从 git ls-files 获取已跟踪文件
result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
files = [f for f in result.stdout.strip().split('\n') 
         if f.endswith(('.md', '.py', '.json', '.yaml', '.yml', '.sh'))]

# 匹配所有常见 API Key 格式
patterns = {
    'YouTube': r'AIzaSy[A-Za-z0-9_-]{33}',
    'OpenAI': r'sk-[A-Za-z0-9]{20,}',
    'GitHub': r'gh[po]_[A-Za-z0-9]{30,}',
}

fixed = 0
for filepath in files:
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        total_matches = 0
        for name, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                placeholder = f'YOUR_{name.upper()}_API_KEY'
                content = re.sub(pattern, placeholder, content)
                total_matches += len(matches)
        if total_matches:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f'✅ Fixed {filepath}: {total_matches} keys')
            fixed += 1
    except: pass
print(f'Total: {fixed} files fixed')
```

**优势**：自动遍历所有已跟踪文件，正则精确匹配，不会误改掩码 Key。

## 2. GitHub 仓库检查

```bash
# 确认仓库仍为 private
gh repo view Leonardo-Chow/hermes-config --json isPrivate -q '.isPrivate'

# 检查最近 commit 是否有敏感信息
cd ~/.hermes && git log --oneline -5
```

### 仓库可见性处理

如果 `isPrivate` 返回 `false`，**立即标记为 🔴 高风险**并报告：
- 即使当前密钥已脱敏，PUBLIC 仓库暴露完整配置结构、skill 细节、工具链信息
- 修复命令：`gh repo edit Leonardo-Chow/hermes-config --visibility private`
- 历史 commit 中可能残留已删除的密钥（force push 前需检查 `git log --all --oneline` 中的旧 commit）

### ⚠️ GitHub Token 权限陷阱（2026-06-03 验证）

`gh repo edit --visibility private` 返回 `HTTP 403` 时，说明 token 缺少 `repo` scope：

```bash
# 检查当前 token 权限
gh auth status

# 刷新 token 添加 repo scope（交互式，需浏览器）
gh auth refresh -s repo
```

**非交互环境（cron job）无法刷新 token**，需提示用户手动操作：
1. 打开 https://github.com/settings/tokens
2. 确保 token 勾选 `repo` 完整权限
3. 或直接在网页端修改仓库可见性

### .gitignore 陷阱

`config.yaml.bak.*` 模式**不匹配** `config.yaml.bak`（无后缀版本）。如果 `config.yaml.bak` 包含敏感信息，需要：
1. 添加 `config.yaml.bak` 到 `.gitignore`
2. `git rm --cached config.yaml.bak` 取消跟踪
3. 提交并推送

## 3. 发现泄露时的处理

### 完整修复流程

```bash
# 1. 替换为占位符（用上面的 Python 批量替换脚本）

# 2. 提交修复
cd ~/.hermes
git add -A
git commit -m "SECURITY: Remove leaked API keys from all files"

# 3. Force push（需要清除历史中的泄露）
git config http.proxy socks5://127.0.0.1:1082
git config https.proxy socks5://127.0.0.1:1082
git push --force origin main

# 4. 验证修复
curl -s -x socks5://127.0.0.1:1082 \
  "https://raw.githubusercontent.com/Leonardo-Chow/hermes-config/main/config/youtube_api_pool.json"
# 确认返回 YOUR_YOUTUBE_API_KEY 而非真实 key

# 5. 清理代理配置
git config --unset http.proxy
git config --unset https.proxy
```

### Git Push 代理回退策略

当 `git push` 需要代理时，按序尝试：
```bash
# 尝试 Shadowrocket SOCKS5 (1082)
git config http.proxy socks5://127.0.0.1:1082 && git config https.proxy socks5://127.0.0.1:1082 && git push origin main

# HTTP 代理返回 503 时切换 SOCKS5（2026-06-03 验证）
# Shadowrocket HTTP 代理可能返回 503，但 SOCKS5 正常

# 失败则尝试 v2rayN (10808)
git config http.proxy socks5://127.0.0.1:10808 && git config https.proxy socks5://127.0.0.1:10808 && git push origin main

# 失败则尝试 ClashX Pro (7890)
git config http.proxy http://127.0.0.1:7890 && git config https.proxy http://127.0.0.1:7890 && git push origin main

# 全部失败：清理代理配置，commit 已本地保存，记录待推送
git config --unset http.proxy && git config --unset https.proxy
echo "⚠️ 推送失败：所有代理不可用。commit 已本地保存，代理恢复后手动推送。"
```

**重要**：推送失败后必须清理 git proxy config，否则后续 git 操作也会走失败的代理。

### ⚠️ Force Push 后的注意事项

- GitHub 可能仍缓存旧 commit（GC 延迟）
- **强烈建议轮换已泄露的 API Key**，即使已 force push
- 旧 commit 在 GitHub 的 CDN 缓存中可能保留数小时

## 4. 常见误报过滤

以下文件中的匹配通常是文档示例，非真实泄露：
- `SKILL.md` 中的 `sk-xxx...xxxx` 示例
- `git-secret-scanning.md` 中的演示代码
- `native-mcp/SKILL.md` 中的 Authorization header 示例
- 二进制文件 (`bin/tirith` 等 Mach-O 可执行文件)
- 任何 `password`/`secret` 出现在 YAML narrative 文本中（如 noir prompt 里的 "city of silicon and secrets"）
- `redact_secrets: true` 等配置选项名

### ⚠️ Skills 目录是泄露高发区（2026-06-08 验证）

**关键发现**：SKILL.md 和 references/*.md 文件中经常硬编码 API Key 作为示例或默认值。扫描时**必须包含 skills/ 目录**。

已确认泄露文件类型：
- `skills/*/SKILL.md` — 工具配置示例中嵌入真实 key
- `skills/*/references/*.md` — 工作流文档中的 curl 命令
- `skills/*/templates/*.py` — 脚本模板中的默认 key
- `config/*.json` — API key 池配置文件
- `user.md` / `memories/MEMORY.md` — 用户记录中引用的 key

**扫描命令必须覆盖所有目录**：
```bash
cd ~/.hermes && git ls-files | xargs grep -l "AIzaSy\|sk-\|ghp_\|gho_" 2>/dev/null
```

### ⚠️ API 服务名称混淆陷阱

| 服务 | 用途 | Key 格式 |
|:-----|:-----|:---------|
| **ScrapeCreators** | TikTok/Instagram/X 社交媒体抓取 | 32 位 hex |
| **ScraperAPI** | 通用网页抓取代理池 | 32 位 hex |
| **Scrapling** | 反检测浏览器自动化（本地库） | 无需 key |

三者名称相似但完全不同。用户可能混淆，配置前确认是哪个服务。

### ⚠️ grep 模式选择

**不要使用宽泛模式**（如 `password|secret`），会产生大量误报。使用严格正则：

```bash
# ✅ 推荐：严格匹配真实 key 格式
git ls-files | xargs grep -n 'AIzaSy[A-Za-z0-9_-]\{30\}\|sk-[A-Za-z0-9]\{20,\}\|ghp_[A-Za-z0-9]\{30\}'

# ❌ 避免：宽泛模式（误报率极高）
git ls-files | xargs grep -l 'AIzaSy\|sk-\|password\|secret'
```

**验证流程**：grep 找到匹配后，必须读取实际内容判断：
1. 含 `...` 的截断字符串 → 已掩码，安全
2. 完整 39 字符 API key → 真实泄露
3. 出现在文档/注释中的模式引用 → 误报

## 5. 安全审查报告模板

```markdown
## 🔐 安全审查结果

| 检查项 | 结果 | 详情 |
|:-------|:----:|:-----|
| API Key 泄露 | ✅/🔴 | 扫描结果 |
| 密码/Token/Secret | ✅/🔴 | 扫描结果 |
| 仓库是否 Private | ✅/🔴 | gh repo view 结果 |
| 最近 commit 泄露 | ✅/🔴 | git log 检查结果 |
```

## 6. 预防措施

### 新文件提交前检查

```bash
# 在 git add 之前检查待提交文件
git diff --cached | grep -E 'AIzaSy|sk-|ghp_|gho_'
```

### 推荐的 .gitignore 条目

```gitignore
# 敏感配置
.env
auth.json
config.yaml.bak
config.yaml.bak.*
*.key
*.pem

# API Key 配置文件（如果包含真实 key）
# config/youtube_api_pool.json  # 可选：如果用环境变量管理 key
```

### 环境变量管理 API Key（推荐）

将 API Key 存储在环境变量而非文件中：
```bash
# ~/.zshrc 或 ~/.bashrc
export YOUTUBE_API_KEY="your_key_here"
```

然后在代码中读取：
```python
import os
api_key = os.environ.get('YOUTUBE_API_KEY', '')
```
