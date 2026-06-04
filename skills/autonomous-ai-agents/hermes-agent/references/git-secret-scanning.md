# Git Secret Scanning & Remediation

When the hermes config repo (`~/.hermes` → `Leonardo-Chow/hermes-config`) is pushed to GitHub, sensitive credentials may leak.

## Known Leak Patterns

| Pattern | Example | Files affected |
|---------|---------|----------------|
| YouTube API Key | `AIzaSy[A-Za-z0-9_-]{33}` | skills/*.md, config/*.json, user.md |
| OpenAI Key | `sk-[A-Za-z0-9]{48}` | skills/*.md |
| GitHub Token | `ghp_[A-Za-z0-9]{36}` | skills/*.md |
| IMA credentials | `client_id`, `api_key` | `~/.config/ima/` (not in repo) |

## Pre-Push Scanning (MANDATORY before git push)

```bash
cd ~/.hermes

# 1. Scan all tracked files for API keys
git ls-files | xargs grep -lE "AIzaSy[A-Za-z0-9_-]{33}|sk-[A-Za-z0-9]{48}|ghp_[A-Za-z0-9]{36}" 2>/dev/null

# 2. Scan staged changes
git diff --cached | grep -E "AIzaSy|sk-|ghp_" | head -20

# 3. Check untracked sensitive files
git status --short | grep -iE "auth|secret|credential|\.env|token"
```

## Remediation Workflow

When leaked keys are found:

### Step 1: Replace keys with placeholders

```python
import re, glob

# Pattern for YouTube API keys
pattern = r'AIzaSy[A-Za-z0-9_-]{33}'

files = glob.glob('**/*.md', recursive=True) + glob.glob('**/*.json', recursive=True) + glob.glob('**/*.py', recursive=True)
for f in files:
    with open(f) as fh:
        content = fh.read()
    if re.search(pattern, content):
        new = re.sub(pattern, 'YOUR_YOUTUBE_API_KEY', content)
        with open(f, 'w') as fh:
            fh.write(new)
        print(f'Fixed: {f}')
```

### Step 2: Commit and force push

```bash
cd ~/.hermes
git add -A
git commit -m "SECURITY: Remove leaked API keys"
git push --force origin main  # Force push to overwrite history
```

### Step 3: Rotate the leaked keys

- YouTube: https://console.cloud.google.com/apis/credentials → delete old keys, generate new
- Update local config: `~/.hermes/config/youtube_api_pool.json`

### Step 4: Verify on GitHub

```bash
curl -s -x socks5://127.0.0.1:1082 \
  "https://raw.githubusercontent.com/Leonardo-Chow/hermes-config/main/config/youtube_api_pool.json"
# Should show YOUR_YOUTUBE_API_KEY, not real keys
```

## .gitignore Checklist

These must be excluded:

```
.env
auth.json
sessions/
memories/
memory/
state.db*
logs/
cache/
```

These ARE tracked (and must be kept clean):

```
config/*.json        ← youtube_api_pool.json
skills/**/*.md       ← often contain inline examples with real keys
user.md              ← memory file
memories/MEMORY.md   ← persistent memory
```

## Pitfall: Inline Key Examples

When writing skill documentation, NEVER use real API keys in examples. Use placeholders:

```
❌ curl "https://api.example.com?key=YOUR_YOUTUBE_API_KEY"
✅ curl "https://api.example.com?key=YOUR_API_KEY"
```

The `memory/memory.md` and `memory/user.md` files are tracked by git. Any API key written to memory WILL leak to GitHub.
