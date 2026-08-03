# Tavily API 池管理

## 脚本位置
- 脚本：`~/.hermes/scripts/tavily_api_pool.py`
- 配置：`~/.hermes/config/tavily_api_pool.json`

## 常用命令
```bash
# 获取当前API key
python3 ~/.hermes/scripts/tavily_api_pool.py current

# 轮换到下一个API key
python3 ~/.hermes/scripts/tavily_api_pool.py rotate

# 添加新的API key
python3 ~/.hermes/scripts/tavily_api_pool.py add <new_key>

# 列出所有API key
python3 ~/.hermes/scripts/tavily_api_pool.py list
```

## MCP配置
Tavily MCP 配置在 `~/.hermes/config.yaml` 中，URL 包含 API key：
```yaml
tavily:
  url: "https://mcp.tavily.com/mcp/?tavilyApiKey=<key>"
  timeout: 180
  connect_timeout: 60
```

## 配额耗尽时的处理
1. 先用 `list` 查看可用的 key
2. 用 `rotate` 切换到下一个 key
3. 更新 `~/.hermes/config.yaml` 中的 URL
4. 或者直接用 `add` 添加新的 key

## Shell 脚本中的 API Key 处理

**⚠️ 关键 Pitfall**：Hermes 的 terminal 工具会自动 redact API key 模式。在 shell 脚本中使用 `$(command)` 获取 API key 时，输出会被替换为 `***`，导致语法错误。

**错误示例**：
```bash
API_KEY=$(python3 ~/.hermes/scripts/youtube_api_pool.py current)
# 输出被 redact 为: API_KEY=***，导致 bash 语法错误
```

**正确方案**：写 Python 脚本到文件，然后执行：
```python
# /tmp/fetch_data.py
import subprocess, json

def get_key():
    r = subprocess.run(['python3', '~/.hermes/scripts/youtube_api_pool.py', 'current'], capture_output=True, text=True)
    return r.stdout.strip()

k = get_key()
# 后续用 k 调用 API
```

```bash
python3 /tmp/fetch_data.py
```
