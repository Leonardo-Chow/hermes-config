# GitHub Secret Scanning & Push Protection

When pushing repos that contain (or historically contained) secrets, GitHub's push protection blocks the push. This covers the full remediation workflow.

## How Push Protection Works

GitHub scans **all commits in the push** for known secret patterns:
- Personal Access Tokens (`ghp_`, `github_pat_`)
- API keys (Tavily `tvly-`, OpenAI `sk-`, AWS `AKIA`, etc.)
- Private keys, connection strings, OAuth tokens

It blocks at the **pre-receive hook** level — the push is rejected before any data is transferred.

## Step 1: Identify the Secrets

The error message shows exact locations:
```
remote: —— GitHub Personal Access Token ——————
remote:   locations:
remote:     - commit: <hash>
remote:       path: config.yaml:6
```

## Step 2: Remove Secrets from Current Working Tree

Replace secrets with placeholders:
```bash
# Replace API keys in config files
sed -i '' 's|tavilyApiKey=[^ ]*|tavilyApiKey=YOUR_TAVILY_API_KEY|g' config.yaml
sed -i '' 's|GITHUB_PERSONAL_ACCESS_TOKEN:.*|GITHUB_PERSONAL_ACCESS_TOKEN: "YOUR_GITHUB_TOKEN"|g' config.yaml

# For .env files — just gitignore them entirely
echo ".env" >> .gitignore
```

## Step 3: Remove Secrets from Git History

Simply removing secrets from the latest commit is NOT enough — push protection scans **all history**. You must rewrite history.

### Option A: git filter-branch (built-in, no install)

```bash
# IMPORTANT: stash or commit any untracked changes first
git stash  # or git add . && git commit -m "WIP"

FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --tree-filter '
  if [ -f config.yaml ]; then
    sed -i "" "s|GITHUB_PERSONAL_ACCESS_TOKEN:.*|GITHUB_PERSONAL_ACCESS_TOKEN: \"YOUR_GITHUB_TOKEN\"|g" config.yaml
    sed -i "" "s|tavilyApiKey=[^ ]*|tavilyApiKey=YOUR_TAVILY_API_KEY|g" config.yaml
  fi
' --tag-name-filter cat -- --all
```

**Pitfalls:**
- `filter-branch` fails with `Cannot rewrite branches: You have unstaged changes` — stash or commit first
- `sed -i ""` syntax is macOS; Linux uses `sed -i` (no empty string)
- After filter-branch, `git log --oneline` shows new commit hashes
- Old refs are kept in `.git/refs/original/` — safe to ignore

### Option B: git filter-repo (recommended for large repos)

```bash
pip install git-filter-repo
git filter-repo --replace-text <(echo 'ghp_==>REDACTED_PAT')
```

### Verify History is Clean

```bash
# Check all commits for remaining secrets
git log --all --oneline | while read hash msg; do
  secrets=$(git show "$hash:config.yaml" 2>/dev/null | grep -c "github_pat\|tvly-dev\|ghp_\|sk-" || true)
  if [ "$secrets" -gt 0 ]; then
    echo "SECRETS in $hash: $msg ($secrets matches)"
  fi
done
```

## Step 4: Force Push

```bash
git push -u origin main --force
```

**Note:** This requires the token to have `contents:write` permission on the repo (Fine-Grained PAT) or `repo` scope (Classic token).

## Step 5: Clean Up Local Repo

```bash
# Remove stale filter-branch refs
rm -rf .git/refs/original/

# Clean up any unstaged changes from the process
git checkout -- .
```

## Handling Large Files (>100MB)

GitHub rejects files over 100MB. Common offenders:
- `node_modules/` (should always be gitignored)
- `.tar.gz` backups
- Database files (`.db`)

```bash
# Add to .gitignore
echo "*.tar.gz" >> .gitignore
echo "backups/" >> .gitignore

# Remove from tracking
git rm --cached path/to/large-file.tar.gz
git commit -m "Exclude large files"

# If large files are in history, use filter-branch
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/large-file.tar.gz' \
  --prune-empty --tag-name-filter cat -- --all
```

## .gitignore Template for Config Repos

When pushing configuration directories (like `~/.hermes/`), always exclude:

```gitignore
# API Keys and secrets
.env
auth.json
*.bak

# Session data
sessions/
state.db*
response_store.db*

# Logs
logs/
*.log

# Cache
cache/
*_cache/

# Database files
*.db
*.db-shm
*.db-wal

# Large files
*.tar.gz
*.zip

# Node modules
node_modules/

# OS files
.DS_Store
```

## Classic vs Fine-Grained Token Behavior

| Behavior | Classic Token (`ghp_`) | Fine-Grained (`github_pat_`) |
|----------|----------------------|------------------------------|
| Push to any owned repo | ✅ with `repo` scope | ❌ must add repo to token scope |
| Create repos | ✅ with `repo` scope | ❌ needs `administration:write` |
| `gh auth login --with-token` | ✅ | ⚠️ may fail with `missing required scope 'read:org'` |
| Secret scanning bypass | Manual approval via URL | Same |

**Recommendation:** Use Classic tokens for CI/automation. Use Fine-Grained for specific, scoped access.

## Pitfalls from Real Sessions

### Multiple filter-branch passes may be needed

GitHub may show truncated secret forms in error messages (e.g., `github...eNVk` instead of the full token). Your first `sed` pattern might not match these truncated forms. After the first filter-branch pass, **verify every commit**:

```bash
git log --all --oneline | while read hash msg; do
  secrets=$(git show "$hash:config.yaml" 2>/dev/null | grep -c "github_pat\|tvly-dev\|ghp_\|GITHUB_PERSONAL_ACCESS_TOKEN: \"github" || true)
  if [ "$secrets" -gt 0 ]; then
    echo "SECRETS in $hash: $msg ($secrets matches)"
  fi
done
```

If secrets remain, re-run filter-branch with broader patterns. You may need 2-3 passes.

### `gh auth login --with-token` rejects Fine-Grained PATs

Fine-Grained PATs (`github_pat_...`) fail with `error validating token: missing required scope 'read:org'` when piped to `gh auth login --with-token`. This is because `gh` requires `read:org` which Fine-Grained PATs can't grant.

**Workaround:** Use Classic tokens (`ghp_...`) for `gh auth login`, or skip `gh` entirely and configure git credential helper directly:

```bash
# Set up git to use the token for HTTPS pushes
git remote set-url origin https://USERNAME:ghp_TOKEN@github.com/OWNER/REPO.git
git push -u origin main
# Then remove the token from the URL after pushing
git remote set-url origin https://github.com/OWNER/REPO.git
```

### Clean up after filter-branch

After successful push, clean up stale refs:

```bash
rm -rf .git/refs/original/
git checkout -- .
git clean -fd  # removes untracked files created during filter-branch
```

### Hermes-specific .gitignore

When pushing `~/.hermes/` to GitHub, use this .gitignore (tested in production):

```gitignore
# Secrets
.env
auth.json
config.yaml.bak.*

# Session data & databases
sessions/
state.db*
response_store.db*
kanban.db*

# Logs
logs/
*.log
gateway.log

# Cache
cache/
audio_cache/
image_cache/
models_dev_cache.json
ollama_cloud_models_cache.json

# Memory & pairing
memories/
memory/
pairing/
sandboxes/

# Temporary
*.lock
*.pid
processes.json
gateway_state.json
gateway.pid
gateway.lock
feishu_seen_message_ids.json
.update_check
.hermes_history
.skills_prompt_snapshot.json

# Large curator backups (130MB+ each, rebuildable)
skills/.curator_backups/

# LSP / Cron / Hooks
lsp/
cron/
hooks/
desktop/
hermes-office/

# Node
node_modules/

# Python
__pycache__/
*.pyc
.venv/
venv/

# OS
.DS_Store
```
