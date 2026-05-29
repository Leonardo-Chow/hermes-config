# Model Switching Reference

## Quick Switch via CLI

```bash
# Set all three in sequence
hermes config set model <model-name>
hermes config set provider <provider-name>
hermes config set base_url <api-endpoint>
```

Restart session after switching (`/new` or reconnect).

## Known Provider Configs

### DeepSeek (dpsk)
- provider: `deepseek`
- base_url: `https://api.deepseek.com/v1`
- key_env: `DEEPSEEK_API_KEY` (stored in `~/.hermes/.env`)
- Models:
  - `deepseek-chat` — V3 general chat
  - `deepseek-reasoner` — R1 reasoning model
- User shorthand: "dpsk" = DeepSeek

### Xiaomi MiMo
- provider: `xiaomi`
- base_url: `https://token-plan-cn.xiaomimimo.com/v1`
- Models: `mimo-v2.5-pro`

### Claude Code → DeepSeek (Anthropic-compatible bridge)
In `~/.zshrc` (for Claude Code only, not Hermes):
```
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_MODEL=deepseek-v4-pro
ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-pro
CLAUDE_CODE_SUBAGENT_MODEL=deepseek-v4-flash
```

## Pitfalls
- `hermes config get model` does NOT exist — use `hermes config show | grep -A5 Model` instead
- Model name must match what the provider expects (e.g., DeepSeek uses `deepseek-chat`, not `deepseek-v3`)
- API key must be set in `~/.hermes/.env` or as environment variable; check with `cat ~/.hermes/.env | grep -i <provider>`
- Setting model/provider/base_url requires session restart to take effect
