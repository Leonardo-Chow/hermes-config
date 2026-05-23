# MiMo Token Plan 配置指南

## Token Plan vs 按量付费

| 特性 | 按量付费 | Token Plan |
|:----|:---------|:-----------|
| 计费方式 | 按使用量 | 固定月费 |
| API Key 前缀 | `sk-` | `tp-` |
| Base URL | `https://api.xiaomimimo.com/v1` | `https://token-plan-cn.xiaomimimo.com/v1` |
| 适用场景 | 轻度使用 | 重度使用 |

## 可用模型

- `mimo-v2.5-pro` — 最新推理模型（推荐）
- `mimo-v2.5` — 标准版
- `mimo-v2-pro` — V2 推理版
- `mimo-v2-omni` — 多模态

## 配置方法

### 方法一：预定义供应商（推荐）

```bash
cat >> ~/.hermes/.env << 'EOF'
XIAOMI_API_KEY=tp-xxxxx
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
EOF
```

### 方法二：自定义供应商

```bash
hermes config set model.provider custom
hermes config set model.base_url https://token-plan-cn.xiaomimimo.com/v1
hermes config set model.api_key tp-xxxxx
hermes config set model.default mimo-v2.5-pro
```

## 测试 API

```bash
curl -s https://token-plan-cn.xiaomimimo.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tp-xxxxx" \
  -d '{"model": "mimo-v2.5-pro", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 50}' \
  --max-time 15
```

## Pitfalls

- **mimo-v2.5-pro 是推理模型**：回复在 `reasoning_content` 和 `content` 两个字段，需要更多 `max_tokens`
- **Token Plan 域名不同**：必须使用 `token-plan-cn.xiaomimimo.com` 而非 `api.xiaomimimo.com`
- **API Key 格式**：Token Plan 使用 `tp-` 前缀，按量付费使用 `sk-` 前缀
