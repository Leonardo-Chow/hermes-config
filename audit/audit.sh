#!/bin/bash
# =============================================================================
# Hermes Audit Logger
# =============================================================================
# Sources into .zshrc to capture ALL shell commands automatically.
# Logs to ~/.hermes/audit/commands.log with auto-rotation.
#
# Install: echo "source ~/.hermes/audit/audit.sh" >> ~/.zshrc
# =============================================================================

export HERMES_AUDIT_DIR="$HOME/.hermes/audit"
export HERMES_AUDIT_LOG="$HERMES_AUDIT_DIR/commands.log"
export HERMES_AUDIT_MAX_SIZE=$((10 * 1024 * 1024))  # 10MB before rotation
export HERMES_AUDIT_CMD_COUNTER_FILE="$HERMES_AUDIT_DIR/.counter"
export HERMES_AUDIT_SESSION_ID="S$(date +%Y%m%d-%H%M%S)-$$"

# Initialize counter
if [ ! -f "$HERMES_AUDIT_CMD_COUNTER_FILE" ]; then
    echo "0" > "$HERMES_AUDIT_CMD_COUNTER_FILE"
fi

_hermes_audit_init() {
    mkdir -p "$HERMES_AUDIT_DIR"
    _hermes_audit_rotate
    # Log session start
    _hermes_audit_log "SESSION_START" "Session $HERMES_AUDIT_SESSION_ID started"
    _hermes_audit_log "SHELL" "SHELL=$SHELL PWD=$(pwd) USER=$(whoami)"
}

_hermes_audit_rotate() {
    if [ -f "$HERMES_AUDIT_LOG" ]; then
        local size
        size=$(stat -f%z "$HERMES_AUDIT_LOG" 2>/dev/null || stat -c%s "$HERMES_AUDIT_LOG" 2>/dev/null || echo 0)
        if [ "$size" -gt "$HERMES_AUDIT_MAX_SIZE" ]; then
            local i=1
            while [ -f "${HERMES_AUDIT_LOG}.${i}" ]; do
                i=$((i + 1))
            done
            mv "$HERMES_AUDIT_LOG" "${HERMES_AUDIT_LOG}.${i}"
            # Keep max 5 rotated files
            while [ "$i" -gt 5 ]; do
                rm -f "${HERMES_AUDIT_LOG}.${i}"
                i=$((i - 1))
            done
        fi
    fi
}

_hermes_audit_next_id() {
    local counter
    counter=$(cat "$HERMES_AUDIT_CMD_COUNTER_FILE")
    counter=$((counter + 1))
    echo "$counter" > "$HERMES_AUDIT_CMD_COUNTER_FILE"
    printf "CMD-%05d" "$counter"
}

_hermes_audit_log() {
    local cmd_id="$1"
    local msg="$2"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$ts] [$cmd_id] $msg" >> "$HERMES_AUDIT_LOG"
}

# Core logging function — call this before each command
_hermes_audit_preexec() {
    local cmd_id
    cmd_id=$(_hermes_audit_next_id)
    export HERMES_LAST_CMD_ID="$cmd_id"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$ts] [$cmd_id] CMD: $1" >> "$HERMES_AUDIT_LOG"
}

# Log exit code after each command
_hermes_audit_precmd() {
    local rc=$?
    if [ -n "$HERMES_LAST_CMD_ID" ]; then
        local ts
        ts=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$ts] [$HERMES_LAST_CMD_ID] EXIT: $rc" >> "$HERMES_AUDIT_LOG"
    fi
}

# Hook into zsh
_hermes_audit_install_zsh() {
    # preexec() runs before each command. It receives the command line as $1.
    autoload -Uz add-zsh-hook
    _hermes_audit_preexec_hook() { _hermes_audit_preexec "$1"; }
    _hermes_audit_precmd_hook() { _hermes_audit_precmd; }
    add-zsh-hook preexec _hermes_audit_preexec_hook
    add-zsh-hook precmd _hermes_audit_precmd_hook
}

# Auto-detect shell and install
case "$SHELL" in
    */zsh)
        _hermes_audit_init
        _hermes_audit_install_zsh
        ;;
    */bash)
        # Bash uses trap DEBUG + PROMPT_COMMAND
        _hermes_audit_init
        trap '_hermes_audit_preexec "$BASH_COMMAND"' DEBUG
        if [ -z "$PROMPT_COMMAND" ]; then
            PROMPT_COMMAND="_hermes_audit_precmd"
        else
            PROMPT_COMMAND="_hermes_audit_precmd; $PROMPT_COMMAND"
        fi
        ;;
esac
