# Hermes Memory & Skills 同步到 IMA 知识库

> 将 Hermes Agent 的内部状态（memory、skills 清单）导出为笔记，上传到 IMA 知识库长期保存。
> 适用于每日复盘 cron job 或手动备份。

## 场景

Hermes 内置 memory 有 4KB 限制，且不持久化跨重装。将关键信息同步到 IMA 知识库可实现：
- 外部 Memory 备份（用户偏好、环境配置、工具链状态）
- Skills 清单归档（便于跨实例恢复）
- 每日复盘报告存档

## 前置条件

- IMA 凭证已配置（`~/.config/ima/client_id` + `api_key`）
- 目标知识库已存在（需 `knowledge_base_id`）
- `node` 可用，`ima_api.cjs` 在 `~/.hermes/skills/ima-skills/`

## 流程：import_doc → add_knowledge

```bash
SKILL_DIR=~/.hermes/skills/ima-skills
KB_ID="<目标知识库ID>"

# 读取凭证
CLIENT_ID=$(cat ~/.config/ima/client_id)
API_KEY=$(cat ~/.config/ima/api_key)
OPTS=$(printf '{"clientId":"%s","apiKey":"%s"}' "$CLIENT_ID" "$API_KEY")

# Step 1: import_doc 创建笔记
RESP=$(node "$SKILL_DIR/ima_api.cjs" "openapi/note/v1/import_doc" \
  '{"content_format":1,"content":"# 标题\n\n正文内容"}' "$OPTS")
NOTE_ID=$(echo "$RESP" | jq -r '.data.note_id')

# Step 2: add_knowledge 将笔记关联到知识库 (media_type=11)
node "$SKILL_DIR/ima_api.cjs" "openapi/wiki/v1/add_knowledge" \
  "{\"media_type\":11,\"note_info\":{\"content_id\":\"$NOTE_ID\"},\"title\":\"笔记标题\",\"knowledge_base_id\":\"$KB_ID\"}" "$OPTS"
```

## ⚠️ 注意事项

1. **media_type=11** 是笔记类型，不是文件上传。文件上传用 `create_media` + COS 流程
2. **title 必须有意义** — 知识库列表中显示的是 title，不是笔记正文
3. **日期后缀** — 建议 title 包含日期（如 `Hermes记忆库_20260510`），便于区分版本
4. **内容大小** — 单篇笔记上限约 14000 字符，超限时拆分为多篇
5. **UTF-8 编码** — content 必须为合法 UTF-8（Python `json.dumps(ensure_ascii=False)` 安全）

## Memory 导出模板

Hermes memory 不存储为文件，需从 session 上下文重建。关键字段：

```markdown
# Hermes Agent 记忆库
> 更新时间: YYYY-MM-DD HH:MM

## 用户信息
- 用户名、平台、时区

## 环境配置
- Python venv 路径、npm/pip 镜像、代理设置
- Memory config (char_limit, search_provider)

## 已安装工具链
- 表格：工具名、版本、路径、状态

## IMA 知识库
- 知识库 ID 列表

## 待办/未完成
- 未完成的配置、待解决的问题
```

## Skills 清单导出模板

```bash
# 扫描所有 SKILL.md
find ~/.hermes/skills -name "SKILL.md" | sort
```

按类别分组，提取 skill name 和 description（从 YAML frontmatter）。

## Cron Job 集成

每日自动执行：
```
1. 生成复盘报告（hermes-retro 或手动 session 分析）
2. 导出 memory → import_doc → add_knowledge
3. 导出 skills 清单 → import_doc → add_knowledge
4. 上传复盘报告 → import_doc → add_knowledge
```

## ⚠️ 从 Node.js 调用 ima_api.cjs 的正确方式

当在 Node.js 脚本中调用 `ima_api.cjs` 时，**必须使用 `execFileSync` 而非 `execSync`**。
`execSync` 通过 shell 执行，JSON 中的特殊字符（引号、括号、换行）会被 shell 解释/截断。

```javascript
const { execFileSync } = require('child_process');

// ✅ 正确：execFileSync 直接传参数数组，不经过 shell
const result = execFileSync('node', [
  `${SKILL_DIR}/ima_api.cjs`,
  'openapi/wiki/v1/add_knowledge',
  JSON.stringify(body),    // body 作为字符串传入，不会被 shell 解释
  JSON.stringify(options)  // options 同理
], { encoding: 'utf8', timeout: 30000 });

// ❌ 错误：execSync 会经过 shell，JSON 中的单引号/特殊字符会导致截断或解析失败
const result = execSync(`node "${SKILL_DIR}/ima_api.cjs" "api/path" '${bodyJson}' '${optsJson}'`);
```

### 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| `code=200002 clientID or apiKey is empty` | shell 截断了 options JSON | 改用 `execFileSync` |
| `invalid AddKnowledgeReq.KnowledgeBaseId` | 字段名用了 `wiki_id` 而非 `knowledge_base_id` | 检查字段名 |
| `code=-100` 参数非法 | shell 解释了 JSON 中的特殊字符 | 改用 `execFileSync` |
