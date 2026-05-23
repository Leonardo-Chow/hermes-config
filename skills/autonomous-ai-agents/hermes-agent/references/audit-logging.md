# Audit Logging Setup (Session Transcript)

## Architecture

A dual-layer approach to capture every command + result + ID:

| Layer | Coverage | Mechanism |
|-------|----------|-----------|
| CLI Tool (`hermes-audit`) | Agent `terminal()` calls | Explicit before/after logging |
| Shell Hooks (`audit.sh`) | User interactive terminal | zsh `preexec` / `precmd` hooks |

## Key Files

```
~/.hermes/audit/
├── audit.sh           — Shell hooks (sourced from .zshrc)
├── hermes-audit       — CLI tool (added to PATH)
├── hermes-retro       — Auto retro/review script (added to PATH)
├── .counter           — Monotonic ID counter (persistent)
├── commands.log       — Audit log file (10MB auto-rotate)
└── retro/             — Generated retro report files (--report mode)
```

## `audit.sh` — Shell Hook Installer

```bash
#!/bin/bash
export HERMES_AUDIT_DIR="$HOME/.hermes/audit"
export HERMES_AUDIT_LOG="$HERMES_AUDIT_DIR/commands.log"
export HERMES_AUDIT_MAX_SIZE=$((10 * 1024 * 1024))
export HERMES_AUDIT_CMD_COUNTER_FILE="$HERMES_AUDIT_DIR/.counter"
export HERMES_AUDIT_SESSION_ID="S$(date +%Y%m%d-%H%M%S)-$$"

# Initialize counter
[ -f "$HERMES_AUDIT_CMD_COUNTER_FILE" ] || echo "0" > "$HERMES_AUDIT_CMD_COUNTER_FILE"

_hermes_audit_rotate() {
    [ -f "$HERMES_AUDIT_LOG" ] || return
    local size; size=$(stat -f%z "$HERMES_AUDIT_LOG" 2>/dev/null)
    [ "$size" -gt "$HERMES_AUDIT_MAX_SIZE" ] || return
    local i=1
    while [ -f "${HERMES_AUDIT_LOG}.${i}" ]; do i=$((i + 1)); done
    mv "$HERMES_AUDIT_LOG" "${HERMES_AUDIT_LOG}.${i}"
    while [ "$i" -gt 5 ]; do rm -f "${HERMES_AUDIT_LOG}.${i}"; i=$((i - 1)); done
}

_hermes_audit_next_id() {
    local c; c=$(cat "$HERMES_AUDIT_CMD_COUNTER_FILE")
    c=$((c + 1)); echo "$c" > "$HERMES_AUDIT_CMD_COUNTER_FILE"
    printf "CMD-%05d" "$c"
}

_hermes_audit_log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" >> "$HERMES_AUDIT_LOG"; }

_hermes_audit_preexec() {
    local cmd_id; cmd_id=$(_hermes_audit_next_id)
    export HERMES_LAST_CMD_ID="$cmd_id"
    _hermes_audit_log "$cmd_id" "CMD: $1"
}

_hermes_audit_precmd() {
    local rc=$?
    [ -n "$HERMES_LAST_CMD_ID" ] && _hermes_audit_log "$HERMES_LAST_CMD_ID" "EXIT: $rc"
}

# zsh hooks
autoload -Uz add-zsh-hook
add-zsh-hook preexec _hermes_audit_preexec
add-zsh-hook precmd _hermes_audit_precmd

mkdir -p "$HERMES_AUDIT_DIR"
_hermes_audit_rotate
_hermes_audit_log "SESSION_START" "Session $HERMES_AUDIT_SESSION_ID started"
_hermes_audit_log "SHELL" "SHELL=$SHELL PWD=$(pwd) USER=$(whoami)"
```

## `hermes-audit` — CLI Tool

```bash
#!/bin/bash
# Usage:
#   hermes-audit CMD <command>           → returns CMD-ID
#   hermes-audit RESULT <id> <rc> [...]  → log result
#   hermes-audit TOOL <name> [args]      → log non-terminal tool call
#   hermes-audit SESSION <start|end>     → session lifecycle
#   hermes-audit TAIL [lines]            → view recent log

HERMES_AUDIT_DIR="$HOME/.hermes/audit"
HERMES_AUDIT_LOG="$HERMES_AUDIT_DIR/commands.log"
HERMES_AUDIT_COUNTER="$HERMES_AUDIT_DIR/.counter"
mkdir -p "$HERMES_AUDIT_DIR"
_ts() { date '+%Y-%m-%d %H:%M:%S'; }
_next_id() {
    local c=0; [ -f "$HERMES_AUDIT_COUNTER" ] && c=$(cat "$HERMES_AUDIT_COUNTER")
    c=$((c + 1)); echo "$c" > "$HERMES_AUDIT_COUNTER"
    printf "CMD-%05d" "$c"
}
case "${1:-help}" in
    CMD)
        id=$(_next_id)
        echo "[$(_ts)] [$id] CMD: ${*:2}" >> "$HERMES_AUDIT_LOG"
        echo "$id"
        ;;
    RESULT)
        echo "[$(_ts)] [${2:-?}] EXIT: ${3:-?} ${*:4}" >> "$HERMES_AUDIT_LOG"
        ;;
    TOOL)
        id=$(_next_id)
        echo "[$(_ts)] [$id] TOOL: $2 ${*:3}" >> "$HERMES_AUDIT_LOG"
        echo "$id"
        ;;
    SESSION)
        echo "[$(_ts)] [SESSION] SESSION_${2:-start}: ${*:3}" >> "$HERMES_AUDIT_LOG"
        ;;
    TAIL)
        tail -n "${2:-20}" "$HERMES_AUDIT_LOG"
        ;;
esac
```

## `hermes-retro` — Auto Retro/Review Script

Generates structured daily summaries from the audit log. Supports date-range filtering, error detection, and report file generation.

```bash
hermes-retro --today              # Today's retro to stdout
hermes-retro --yesterday          # Yesterday's retro
hermes-retro --date 2026-05-08    # Specific date
hermes-retro --last-100           # Last 100 log entries
hermes-retro --report             # Save report to ~/.hermes/audit/retro/retro-YYYY-MM-DD.md
```

**Report content:**
- Time range (first → last entry)
- Total log lines, command count, session count, unique CMD-IDs
- Exit code breakdown (success rate if exit codes recorded)
- Anomaly detection (non-zero exits, error keywords: error/fail/timeout/denied/429/403/500)
- Key output detection (import_doc, add_knowledge, note_id, media_id, DOC-)
- Command category breakdown (web, git, npm, python)

**Common `grep -c` pitfall:** When piping multi-line output to `grep -c`, grep exits 1 on zero matches. Using `|| echo 0` produces two output lines (grep's "0" + echo's "0") → `$((var + 0))` breaks. Fix: use `grep -cE 'pattern' 2>/dev/null || true` — `|| true` suppresses the exit code without adding output.

## `hermes-retro` — Full Script

```bash
#!/bin/bash
# =============================================================================
# Hermes Audit Retro — 自动复盘
# =============================================================================
# Supports: --today, --yesterday, --date YYYY-MM-DD, --last-100, --report
# =============================================================================

HERMES_AUDIT_DIR="$HOME/.hermes/audit"
HERMES_AUDIT_LOG="$HERMES_AUDIT_DIR/commands.log"
HERMES_RETRO_DIR="$HERMES_AUDIT_DIR/retro"
mkdir -p "$HERMES_RETRO_DIR"

_ts() { date '+%Y-%m-%d %H:%M:%S'; }

_collect_logs() {
    local filter="$1"
    if [ "$filter" = "all" ]; then cat "$HERMES_AUDIT_LOG" 2>/dev/null
    elif [ "$filter" = "last-100" ]; then tail -100 "$HERMES_AUDIT_LOG" 2>/dev/null
    else grep "^\[$filter" "$HERMES_AUDIT_LOG" 2>/dev/null; fi
}

_generate_retro() {
    local filter="$1" label="$2"
    local log_data; log_data=$(_collect_logs "$filter")
    [ -z "$log_data" ] && { echo "📭 ${label}: 暂无日志数据"; return; }

    local total_lines; total_lines=$(echo "$log_data" | wc -l | tr -d ' ')
    local cmd_count; cmd_count=$(echo "$log_data" | grep -cE '\[CMD-|\[TOOL:' || true)
    local session_count; session_count=$(echo "$log_data" | grep -c 'SESSION_START' || true)
    local exit_0; exit_0=$(echo "$log_data" | grep 'EXIT: 0' | wc -l | tr -d ' ')
    local exit_err; exit_err=$(echo "$log_data" | grep -E 'EXIT: [1-9][0-9]*' | wc -l | tr -d ' ')
    local exit_total=$((exit_0 + exit_err))
    local unique_cmds; unique_cmds=$(echo "$log_data" | grep -oE '\[CMD-[0-9]+\]' | sort -u | wc -l | tr -d ' ')

    local errors; errors=$(echo "$log_data" | grep -E 'EXIT: [1-9][0-9]*')
    local uploads; uploads=$(echo "$log_data" | grep -iE 'import_doc|add_knowledge|note_id|media_id|DOC-' | head -10)
    local anomalies; anomalies=$(echo "$log_data" | grep -iE 'error|fail|timeout|denied|reject|blocked|429|500|403' | head -10)
    local first_ts; first_ts=$(echo "$log_data" | head -1 | grep -oE '^\[[^]]+\]' | tr -d '[]')
    local last_ts; last_ts=$(echo "$log_data" | tail -1 | grep -oE '^\[[^]]+\]' | tr -d '[]')

    # Command category breakdown
    local web_cmds; web_cmds=$(echo "$log_data" | grep -cE 'curl|wget|web_|http' 2>/dev/null || true)
    local git_cmds; git_cmds=$(echo "$log_data" | grep -cE 'git ' 2>/dev/null || true)
    local npm_cmds; npm_cmds=$(echo "$log_data" | grep -cE 'npm |pnpm |yarn ' 2>/dev/null || true)
    local python_cmds; python_cmds=$(echo "$log_data" | grep -cE 'python |pip ' 2>/dev/null || true)

    local report=""
    report+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report+="  📊 复盘报告: ${label}\n"
    report+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    report+="📅 时间范围: ${first_ts:-N/A} → ${last_ts:-N/A}\n\n"
    report+="📈 统计概览\n"
    report+="  · 日志条目:     ${total_lines} 行\n"
    report+="  · 命令/工具调用: ${cmd_count} 次\n"
    report+="  · 独立会话:     ${session_count} 个\n"
    report+="  · 唯一 CMD-ID:  ${unique_cmds} 个\n\n"
    report+="✅ 执行结果\n"
    if [ "$exit_total" -gt 0 ]; then
        local success_pct=$((exit_0 * 100 / exit_total))
        report+="  · 成功 (EXIT 0):  ${exit_0} 次 (${success_pct}%)\n"
        report+="  · 失败 (EXIT ≠0): ${exit_err} 次\n"
    else
        report+="  · 结果记录暂缺 (非交互式 shell 无 exit hook)\n"
    fi
    report+="\n"

    [ -n "$errors" ] && { report+="❌ 异常命令\n"; while IFS= read -r line; do report+="  · ${line}\n"; done <<< "$errors"; report+="\n"; }
    [ -n "$anomalies" ] && { report+="⚠️  异常关键字\n"; while IFS= read -r line; do report+="  · ${line}\n"; done <<< "$anomalies"; report+="\n"; }
    [ -n "$uploads" ] && { report+="📎 关键产出\n"; while IFS= read -r line; do report+="  · ${line}\n"; done <<< "$uploads"; report+="\n"; }

    report+="🔧 命令分类\n"
    [ "$web_cmds" -gt 0 ] 2>/dev/null && report+="  · 🌐 Web 请求:  ${web_cmds} 次\n"
    [ "$git_cmds" -gt 0 ] 2>/dev/null && report+="  · 📦 Git 操作:  ${git_cmds} 次\n"
    [ "$npm_cmds" -gt 0 ] 2>/dev/null && report+="  · 📦 npm/包管理: ${npm_cmds} 次\n"
    [ "$python_cmds" -gt 0 ] 2>/dev/null && report+="  · 🐍 Python:    ${python_cmds} 次\n"
    report+="\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    echo -e "$report"
}

case "${1:---today}" in
    --today|-t)    filter="$(date '+%Y-%m-%d')"; label="$(date '+%Y-%m-%d') 今日复盘"; _generate_retro "$filter" "$label";;
    --yesterday|-y) filter="$(date -v-1d '+%Y-%m-%d' 2>/dev/null || date --date='yesterday' '+%Y-%m-%d')"; label="$filter 昨日复盘"; _generate_retro "$filter" "$label";;
    --date|-d)     filter="$2"; label="$filter 复盘"; _generate_retro "$filter" "$label";;
    --last-100|-l) _generate_retro "last-100" "最近 100 条";;
    --report|-R)   filter="$(date '+%Y-%m-%d')"; label="$(date '+%Y-%m-%d')"; report=$(_generate_retro "$filter" "$label" 2>/dev/null); report_path="${HERMES_RETRO_DIR}/retro-${label}.md"; echo "$report" > "$report_path"; echo "✅ 报告已保存: $report_path";;
    *)             filter="$(date '+%Y-%m-%d')"; label="$(date '+%Y-%m-%d') 今日复盘"; _generate_retro "$filter" "$label";;
esac
```

## Cron Integration: Daily Auto Retro

Add a cron job that runs the retro and delivers the report to the user's messaging platform (Feishu):

```bash
hermes cron create --schedule "0 11 * * *" --name "每日自动复盘" \
  --prompt "运行 hermes-retro --today 获取今日审计日志复盘报告。然后生成 Markdown 格式发送给用户。报告内容包括：今日命令统计、成功率、异常命令、关键产出（上传的文档ID等）、命令分类分布。格式要整洁可读。如果发现异常命令（EXIT ≠0），加上分析和建议。"
```

Key params:
- `--deliver origin` — deliver to the same platform/conversation the user created it from
- The cron session passes `skip_memory=True` by default (clean context each run)
- Cron output includes header/footer framing (not mirrored into gateway session)

**User preference:** Report delivered at **11:00 AM** daily.

## Installation

```bash
mkdir -p ~/.hermes/audit
# Write all files above to ~/.hermes/audit/
chmod +x ~/.hermes/audit/audit.sh ~/.hermes/audit/hermes-audit ~/.hermes/audit/hermes-retro

# Add to .zshrc (must be zsh, not bash)
cat >> ~/.zshrc << 'EOF'
export HERMES_AUDIT_DIR="$HOME/.hermes/audit"
source "$HERMES_AUDIT_DIR/audit.sh"
export PATH="$HOME/.hermes/audit:$PATH"
EOF

# Initialize for current session (zsh only)
source ~/.hermes/audit/audit.sh
```

**⚠️ bash 兼容性:** `audit.sh` 使用了 zsh 专有的 `autoload` 和 `add-zsh-hook` 命令。在 bash 环境下会报错 `autoload: command not found`，但不影响 `hermes-audit` 和 `hermes-retro` CLI 工具的使用。shell hooks（preexec/precmd）仅在交互式 zsh 会话中生效。

## Agent Protocol (Must Follow)

Each time you perform a significant tool call:
1. **Before**: `terminal("hermes-audit CMD \"description\"")` → capture the returned CMD-ID
2. **During**: Execute the actual command
3. **After**: `terminal("hermes-audit RESULT <id> <exit_code> [summary]")`

For non-terminal tools (delegate, cron job): use the `TOOL` subcommand.

Non-terminal tool calls:
```bash
hermes-audit TOOL delegate_task "goal=analyze data"
hermes-audit RESULT CMD-00007 0 "summary of result"
```

## Verification

```bash
cat ~/.hermes/audit/commands.log
hermes-retro --today
```

## Fallback: Session JSON Analysis (When Audit Log Is Empty)

The audit log only records commands after the system was set up and `.zshrc` hooks are active. If `hermes-retro --today` returns `📭 ... 暂无日志数据`, the agent **must generate the retro from session files directly**.

### Data Sources

| Source | Location | Contains |
|--------|----------|----------|
| Session JSON files | `~/.hermes/sessions/session_YYYYMMDD_*.json` | Full message history, tool calls, raw outputs |
| SQLite state.db | `~/.hermes/state.db` → `sessions` table | Session metadata (message_count, tool_call_count, model, cost, timestamps) |
| Error logs | `~/.hermes/logs/errors.log` | Exception traces and failures |

### Quick Sanity: Query `state.db`

```bash
sqlite3 ~/.hermes/state.db \
  "SELECT id, source, datetime(started_at, 'unixepoch', '+8 hours') as start,
          message_count, tool_call_count, estimated_cost_usd, title
   FROM sessions
   WHERE date(datetime(started_at, 'unixepoch', '+8 hours')) = '$(date +%Y-%m-%d)'
   ORDER BY started_at;"
```

This gives: session ID, source platform, start time, message/tool/counts, cost, and title — all without parsing individual JSON files.

### Deep Analysis: Parse Session JSONs

```bash
python3 << 'PYEOF'
import json, os, glob
from collections import Counter

sessions_dir = os.path.expanduser("~/.hermes/sessions")
today_sessions = sorted(glob.glob(os.path.join(sessions_dir, f"session_$(date +%Y%m%d)_*.json")))

all_data = {
    'total_messages': 0, 'total_tool_msgs': 0,
    'roles': Counter(), 'tool_calls': Counter(), 'errors': [],
    'sessions': []
}

for sf in today_sessions:
    with open(sf) as fh:
        data = json.load(fh)
    msgs = data.get('messages', [])
    roles = Counter(m.get('role','?') for m in msgs)

    # Tool call names
    tool_names = []
    for m in msgs:
        if m.get('tool_calls'):
            for tc in m['tool_calls']:
                tool_names.append(tc.get('function',{}).get('name', 'unknown'))

    # Error detection from tool responses
    session_errors = 0
    for m in msgs:
        if m.get('role') == 'tool':
            content = str(m.get('content',''))
            if not content:
                continue
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    ec = parsed.get('exit_code', 0)
                    if ec != 0:
                        session_errors += 1
                        all_data['errors'].append({
                            'session': os.path.basename(sf),
                            'exit_code': ec,
                            'preview': str(content)[:150]
                        })
            except (json.JSONDecodeError, TypeError):
                pass

    all_data['total_messages'] += len(msgs)
    all_data['total_tool_msgs'] += roles.get('tool', 0)
    all_data['roles'] += roles
    all_data['tool_calls'] += Counter(tool_names)
    all_data['sessions'].append({
        'file': os.path.basename(sf),
        'msgs': len(msgs),
        'tools': len(tool_names),
        'errors': session_errors
    })

# Print summary
total_tools = sum(all_data['tool_calls'].values())
print(f"📊 $(date +%Y-%m-%d) Retro (from session files)")
print(f"🔸 会话: {len(today_sessions)} | 消息: {all_data['total_messages']} | 工具: {total_tools}")
print(f"🔸 异常: {len(all_data['errors'])} ({len(all_data['errors'])/max(total_tools,1)*100:.1f}%)")
print()
print("🔧 工具分布:")
for name, count in sorted(all_data['tool_calls'].items(), key=lambda x: -x[1]):
    print(f"  {name}: {count}")
print()
print("📋 会话:")
for s in all_data['sessions']:
    print(f"  {s['file'][:45]}... | msgs={s['msgs']} | tools={s['tools']} | err={s['errors']}")

if all_data['errors']:
    print()
    print("❌ 前10个异常:")
    for e in all_data['errors'][:10]:
        print(f"  exit={e['exit_code']} | {e['preview'][:120]}")
PYEOF
```

### Key Metrics to Extract

| Metric | How | Why |
|--------|-----|-----|
| Tool call distribution | Count by `function.name` | Shows workload pattern |
| Error rate | Non-zero exit codes / total tool calls | Quality indicator |
| Session count | Unique JSON files | Engagement measure |
| Key outputs | grep for `media_id`, `document_id`, `import_doc`, `note_id` | Deliverables |
| Cost | `state.db` `estimated_cost_usd` | Usage tracking |

### Pitfalls of Session JSON Analysis

1. **Session JSON format varies** — different Hermes versions produce slightly different structures. Always check top-level keys first (`list(data.keys())`).
2. **Role alternation matters** — messages with `tool_calls` and `role='tool'` are separate entries. Count tool-related messages from `role='tool'`, not from `tool_calls` key.
3. **Unended sessions** — sessions without an `ended_at` timestamp (common for long-running talks or mid-session interruptions) still have usable data.
4. **Null exit codes** — some tool calls succeed but return `exit_code: null` or no exit code field. Treat those as successful unless content shows errors.
5. **File size pressure** — session JSONs can be 1MB+. For very large sessions, parse only `messages` array with field-limited iteration rather than loading the whole file.

## `hermes-retro` Location

`hermes-retro` lives at `~/.hermes/audit/hermes-retro`. It is **not** always in PATH — if `hermes-retro --today` returns "command not found", run it explicitly:

```bash
bash ~/.hermes/audit/hermes-retro --today
```

The same applies to `hermes-audit` (`~/.hermes/audit/hermes-audit`).

## Pitfalls

1. **Shell hooks don't fire in `terminal()` calls** — each call is a fresh non-interactive shell. Never rely on hooks for agent-initiated commands. Always use the CLI tool explicitly.
2. **Counter file desync** — if two processes write to `.counter` simultaneously, IDs can collide. The `.counter` file is read-then-write without locking, so sequential calls within the same `terminal()` are safe but concurrent terminal() calls (e.g. from delegation) need atomic seqfile ops.
3. **Log rotation on macOS** uses `stat -f%z` (BSD stat); on Linux use `stat -c%s`. The script auto-detects.
4. **Mid-session `terminal()` failure** — if the `CMD` logging succeeds but the actual command crashes, the returned CMD-ID is orphaned. Always log the result in the same `terminal()` call or handle the error.
5. **`write_file` blocks `.env` writes** — protected credential file. Use `terminal("cat >> ~/.hermes/.env << 'EOF' ... EOF")` for secrets.
6. **`grep -c` with `|| echo 0` produces double output** — grep exits 1 when zero matches, `|| echo 0` adds a second "0". Never combine `grep -c` with `|| echo 0`. Use `grep -cE 'pattern' 2>/dev/null || true` instead.
7. **`$((var + 0))` doesn't trim whitespace** in bash arithmetic — if `var` contains embedded newlines, the expression fails. Sanitize with `var=$(echo "$var" | tr -d ' ')` before arithmetic.
8. **No web dashboard exists** for the audit system — user has requested a 控制面板 (dashboard URL). Future work: build a static HTML/JS dashboard reading `commands.log` for real-time log viewing, search, and retro report display.
