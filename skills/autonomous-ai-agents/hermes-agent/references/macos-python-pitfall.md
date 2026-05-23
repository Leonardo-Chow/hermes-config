# macOS Python Version Pitfall

## Problem

On macOS, `python3` resolves to `/usr/bin/python3` which is **Python 3.9.6**.
Many modern Python tools require **>= 3.10** (Agent-Reach, etc.).

Installing via `python3 -m pip install <pkg>` will succeed but the tool won't
work at runtime because it requires a newer Python.

## The Hermes Venv Python

Hermes Agent's own venv uses a newer Python:
```
/Users/zhoulong/.hermes/hermes-agent/venv/bin/python3  →  Python 3.11.15
```

Use this for all pip installs:
```bash
# Right — uses hermes venv Python 3.11:
/Users/zhoulong/.hermes/hermes-agent/venv/bin/python3 -m pip install <pkg>

# Also right — activate first:
source /Users/zhoulong/.hermes/hermes-agent/venv/bin/activate
pip install <pkg>

# Wrong — uses system Python 3.9.6, will fail at runtime:
python3 -m pip install <pkg>
pip install <pkg>
```

## Symptoms

- `pip install` succeeds but the CLI or import fails with version errors
- `agent-reach` → `ModuleNotFoundError: No module named 'agent_reach.cli'`
- `python3 -c "import agent_reach"` → `ModuleNotFoundError` (because system python doesn't have it)
- Any tool installed via system pip but requiring Python >= 3.10

## How to Detect

```bash
python3 --version
# → Python 3.9.6   (system — don't use for pip)

/Users/zhoulong/.hermes/hermes-agent/venv/bin/python3 --version
# → Python 3.11.15  (hermes venv — use for pip)
```

## Recommendations

1. Always use the full venv Python path for pip installs in this environment
2. If a tool's CLI script points to system python (hashbang), reinstall via hermes venv
3. Consider making `hermes venv python3` the default `python3` in `~/.zshrc` if it causes repeated friction
