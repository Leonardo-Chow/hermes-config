# last30days Skill 安装与配置

## 安装路径
```bash
# 克隆到 /tmp
git clone --depth 1 https://github.com/mvanhorn/last30days-skill.git /tmp/last30days-skill

# 复制 skill 到 Hermes
cp -r /tmp/last30days-skill/skills/last30days ~/.hermes/skills/last30days

# 清理
rm -rf /tmp/last30days-skill
```

## 环境要求
- Python 3.12+（macOS 路径：`/opt/homebrew/bin/python3.12`）
- 系统自带 Python 3.9 不满足要求

## 配置文件
`~/.config/last30days/.env`：
```
SCRAPECREATORS_API_KEY=xxx
SCRAPERAPI_API_KEY=xxx
OMKAR_API_KEY=xxx
SETUP_COMPLETE=true
```
⚠️ 权限必须 `chmod 600`

## 运行命令
```bash
/opt/homebrew/bin/python3.12 ~/.hermes/skills/last30days/scripts/last30days.py "话题" --emit=compact --quick
```

## 关键 Pitfall

### 1. --plan 参数（LAW 7）
命名实体话题（人名/品牌/产品）必须传 `--plan` JSON，否则降级为确定性回退（弱搜索）。
```bash
# ❌ 错误：裸调用
python3 last30days.py "OBSBOT" --emit=compact

# ✅ 正确：传 plan
cat > /tmp/plan.json << 'EOF'
{"intent":"entity","freshness_mode":"recent","subqueries":[{"label":"primary","search":"OBSBOT webcam review","sources":["reddit","youtube","hackernews"]},{"label":"products","search":"OBSBOT Tiny 3 OR Tail 2","sources":["reddit","youtube"]}]}
EOF
python3 last30days.py "OBSBOT" --plan /tmp/plan.json --emit=compact
```

### 2. 输出格式（LAWs 1-8）
- 第一行必须是 badge：`🌐 last30days v{VERSION} · synced {YYYY-MM-DD}`
- 不要加 `##` section headers（GENERAL 查询）
- 不要加 `Sources:` 块（用引擎的 emoji-tree footer）
- 用 `[name](url)` 内联链接，不要裸 URL
- 用 ` - ` 替代 `—`（em-dash）

### 3. 可用数据源（诊断命令）
```bash
/opt/homebrew/bin/python3.12 ~/.hermes/skills/last30days/scripts/last30days.py --diagnose
```
返回 JSON，列出 available_sources、providers、认证状态。

### 4. TikTok/Instagram 需要 ScrapeCreators key
没有 key 时这两个源返回 0 结果。有 key 但额度用完也返回 0。

### 5. Reddit 被反爬
Reddit JSON API 返回 403。需要代理或浏览器 cookie。
