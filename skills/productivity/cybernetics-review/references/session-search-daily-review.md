# session_search 每日复盘使用模式

## 发现今日会话（推荐模式）

```python
# 按日期搜索，获取今日所有会话
session_search(query="2026-09-30", limit=10)
```

**输出结构**：
- `results[]` — 每个会话包含：`session_id`、`when`、`source`、`model`、`title`
- `matched_role` — 命中角色（user/assistant/tool）
- `match_message_id` — 命中消息 ID
- `snippet` — FTS5 高亮片段
- `bookend_start` — 会话前 3 轮（目标/启动上下文）
- `bookend_end` — 会话后 3 轮（结果/决策）
- `messages` — 命中消息前后 ±5 条（含锚点消息）

## 关键洞察

| 场景 | 推荐用法 |
|------|----------|
| **每日复盘** | `query="YYYY-MM-DD"` + `limit=10` 发现所有今日会话 |
| **任务回溯** | 用 `bookend_start` 看目标，`bookend_end` 看结果，`messages` 看关键步骤 |
| **深度挖掘** | 用 `session_id` + `around_message_id` 滚动读取完整上下文 |

## 实测效果（2026-09-30）

- 发现 2 个活跃会话（竞品监测、视频上线监测）
- `bookend_start` + `bookend_end` + `messages` 窗口完整复现了任务目标→执行→结果闭环
- 无需读取完整 transcript 即可提取：核心任务、关键产出、自检状态、观察洞察
- 耗时 < 2 秒，比 `hermes-retro` 脚本更可靠（后者未安装）

## Cron Job 中的限制

- `session_search` 可用（只读，不依赖 memory 工具）
- 适合作为 cron job 复盘的核心数据源
- 结合 `hermes --version` + `git status` + `session_search` 可形成完整自动复盘管线