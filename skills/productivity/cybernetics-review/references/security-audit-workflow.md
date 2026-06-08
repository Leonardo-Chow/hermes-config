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

### .gitignore 陷阱

`config.yaml.bak.*` 模式**不匹配** `config.yaml.bak`（无后缀版本）。如果 `config.yaml.bak` 包含敏感信息，需要：
1. 添加 `config.yaml.bak` 到 `.gitignore`
2. `git rm --cached config.yaml.bak` 取消跟踪
3. 提交并推送

## 3. 发现泄露时的处理

```bash
# 1. 替换为占位符
sed -i '' 's/AIzaSy[A-Za-z0-9_-]\{33\}/YOUR_API_KEY/g' <file>

# 2. 提交修复
git add -A
git commit -m "SECURITY: Remove leaked API keys"

# 3. Force push（需要清除历史中的泄露）
git push --force origin main
```

### Git Push 代理回退策略

当 `git push` 需要代理时，按序尝试：
```bash
# 尝试 Shadowrocket (1082)
git config http.proxy socks5://127.0.0.1:1082 && git config https.proxy socks5://127.0.0.1:1082 && git push origin main

# 失败则尝试 v2rayN (10808)
git config http.proxy socks5://127.0.0.1:10808 && git config https.proxy socks5://127.0.0.1:10808 && git push origin main

# 失败则尝试 ClashX Pro (7890)
git config http.proxy http://127.0.0.1:7890 && git config https.proxy http://127.0.0.1:7890 && git push origin main

# 全部失败：清理代理配置，commit 已本地保存，记录待推送
git config --unset http.proxy && git config --unset https.proxy
echo "⚠️ 推送失败：所有代理不可用。commit 已本地保存，代理恢复后手动推送。"
```

**重要**：推送失败后必须清理 git proxy config，否则后续 git 操作也会走失败的代理。

## 4. 常见误报过滤

以下文件中的匹配通常是文档示例，非真实泄露：
- `SKILL.md` 中的 `sk-xxx...xxxx` 示例
- `git-secret-scanning.md` 中的演示代码
- `native-mcp/SKILL.md` 中的 Authorization header 示例
- 二进制文件 (`bin/tirith` 等 Mach-O 可执行文件)
- 任何 `password`/`secret` 出现在 YAML narrative 文本中（如 noir prompt 里的 "city of silicon and secrets"）
- `redact_secrets: true` 等配置选项名

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
