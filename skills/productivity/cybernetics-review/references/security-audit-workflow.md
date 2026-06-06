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

## 4. 常见误报过滤

以下文件中的匹配通常是文档示例，非真实泄露：
- `SKILL.md` 中的 `sk-xxx...xxxx` 示例
- `git-secret-scanning.md` 中的演示代码
- `native-mcp/SKILL.md` 中的 Authorization header 示例
- 二进制文件 (`bin/tirith` 等 Mach-O 可执行文件)

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
