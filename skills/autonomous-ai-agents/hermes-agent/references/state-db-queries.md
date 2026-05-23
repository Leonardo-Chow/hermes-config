# 查询 Hermes 内部状态数据库

> 当 `hermes-retro` 不可用时，直接查询 `state.db` 获取 session 统计数据。

## 数据库位置

```
~/.hermes/state.db  (SQLite)
```

## 常用查询

### 列出所有表

```bash
sqlite3 ~/.hermes/state.db ".tables"
```

主要表：`sessions`, `messages`, `messages_fts` (全文搜索)

### Sessions 表结构

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,          -- feishu, cli, cron, etc.
    user_id TEXT,
    model TEXT,
    title TEXT,
    message_count INTEGER DEFAULT 0,
    tool_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    started_at REAL NOT NULL,      -- Unix timestamp
    ended_at REAL,
    end_reason TEXT,
    estimated_cost_usd REAL,
    ...
);
```

### 按日期查询 sessions

```bash
# 今天 (2026-05-10) 的 sessions
sqlite3 ~/.hermes/state.db \
  "SELECT id, source, title, message_count, tool_call_count 
   FROM sessions 
   WHERE started_at > $(date -j -f '%Y-%m-%d' '2026-05-10' +%s) 
   ORDER BY started_at;"

# JSON 格式输出
sqlite3 -json ~/.hermes/state.db \
  "SELECT id, source, title, message_count, tool_call_count, started_at, ended_at 
   FROM sessions 
   WHERE started_at > 1778382000 
   ORDER BY started_at;"
```

### 统计汇总

```bash
# 总消息数和工具调用数
sqlite3 ~/.hermes/state.db \
  "SELECT COUNT(*) as sessions, SUM(message_count) as messages, SUM(tool_call_count) as tool_calls 
   FROM sessions 
   WHERE started_at > 1778382000;"
```

### 按来源分组

```bash
sqlite3 ~/.hermes/state.db \
  "SELECT source, COUNT(*), SUM(message_count) 
   FROM sessions GROUP BY source;"
```

## ⚠️ 注意事项

1. **时间戳是 Unix 秒**（不是毫秒），Python `datetime.timestamp()` 直接可用
2. **messages 表** 存储完整对话历史，但查询较慢（大量数据）
3. **messages_fts** 支持全文搜索，可用于搜索历史对话内容
4. **hermes-retro 脚本** 依赖 `~/.hermes/audit/commands.log`，如果 audit 系统未激活则无数据，此时回退到 state.db 查询
