# IMA Skill 安装与配置指南

> 记录从 SkillHub 安装 ima-skills 的完整流程，供未来直接参考。

## 安装方式

### 方式 A：通过 SkillHub 网页安装（推荐）

1. 打开 SkillHub 页面：https://skillhub.cn/skills/ima-skills
2. 查看"安装方式"标签页获取最新指引
3. 技能数据来源于 ClawHub，可通过 Hermes 的 ClawHubSource 自动发现

### 方式 B：手动 ZIP 安装（离线/备选）

如果自动安装不可用，可手动下载安装：

```bash
# 1. 下载技能 ZIP 包（版本号从 SkillHub 页面获取）
curl -sL -o /tmp/ima-skills.zip "https://app-dl.ima.qq.com/skills/ima-skills-{version}.zip"

# 2. 解压到 Hermes skills 目录
mkdir -p /tmp/ima-skill && cd /tmp/ima-skill
unzip -o /tmp/ima-skills.zip
cp -r ima-skill/* ~/.hermes/skills/ima-skills/
chmod +x ~/.hermes/skills/ima-skills/ima_api.cjs
```

## 凭证配置

凭证获取地址：https://ima.qq.com/agent-interface

### 方式 A — 配置文件（推荐）

```bash
mkdir -p ~/.config/ima
echo "your_client_id" > ~/.config/ima/client_id
echo "your_api_key" > ~/.config/ima/api_key
```

### 方式 B — 环境变量

```bash
export IMA_OPENAPI_CLIENTID="your_client_id"
export IMA_OPENAPI_APIKEY="your_api_key"
```

Agent 按优先级：环境变量 → 配置文件。

## 连接验证

安装和配置后，用以下命令测试连接：

```bash
export IMA_OPENAPI_CLIENTID="xxx"
export IMA_OPENAPI_APIKEY="xxx"
SKILL_DIR="$HOME/.hermes/skills/ima-skills"
OPTS=$(printf '{"clientId":"%s","apiKey":"%s"}' "$IMA_OPENAPI_CLIENTID" "$IMA_OPENAPI_APIKEY")

# 测试：列出笔记
node "$SKILL_DIR/ima_api.cjs" "openapi/note/v1/list_note" '{"limit":5}' "$OPTS"

# 测试：搜索知识库
node "$SKILL_DIR/ima_api.cjs" "openapi/wiki/v1/search_knowledge_base" '{"query":"","cursor":"0","limit":20}' "$OPTS"
```

预期输出：`{"code":0,"msg":"success","data":{...}}`

## API 凭证格式

- `Client ID`：16 进制字符串（如 `6b4ad97e...`）
- `API Key`：Base64 格式的较长字符串
- HTTP 请求头：`ima-openapi-clientid`、`ima-openapi-apikey`、`ima-openapi-ctx`
- Base URL：`https://ima.qq.com`

## 注意事项

- Skill 子模块：`skill_view("notes")` 或 `skill_view("knowledge-base")` 加载子模块
- 每天首次 API 调用自动检查技能更新（`openapi/check_skill_update`）
- 凭证仅发送到 `ima.qq.com`，不上传到其他域名
- 文件上传流程会向 `*.myqcloud.com` (COS) 发送请求，使用临时凭据
