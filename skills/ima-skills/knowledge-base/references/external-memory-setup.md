# IMA 作为外部 Memory 参考

## 背景

Hermes Agent 内置持久记忆有 4,000 字符限制（`memory_char_limit`）。当信息量超过限制时，需要一个无限容量的外部记忆后端。IMA 知识库天然适合这个角色。

## 架构

```
┌─────────────────────────────┐
│  Hermes 内置 Memory (4KB)   │  ← 高频信息：工具链、供应商、关键ID
│  memory_char_limit: 4000    │
└──────────────┬──────────────┘
               │ 每日同步（cron job）
               ▼
┌─────────────────────────────┐
│  IMA 知识库（外部 Memory）  │  ← 无上限：持久记忆、技能清单、历史记录
│  • 持久记忆笔记             │
│  • 技能清单笔记             │
│  • 日后复盘报告等           │
└─────────────────────────────┘
```

## 实现步骤

### 1. 创建专用知识库
在 IMA 中创建一个专用知识库（如 "Herme记忆库"），作为外部 Memory 存储。

### 2. 上传 Memory 内容
将 Hermes 的 memory 内容导出为 Markdown，通过 `import_doc` + `add_knowledge` 上传：
```bash
# 创建笔记
node ima_api.cjs "openapi/note/v1/import_doc" '{"title":"🧠 Hermes持久记忆","content":"...","content_format":1}'
# 添加到知识库
node ima_api.cjs "openapi/wiki/v1/add_knowledge" '{"media_type":11,"note_info":{"content_id":"<note_id>"},"title":"...","knowledge_base_id":"<kb_id>"}'
```

### 3. 上传技能清单
读取 `~/.hermes/skills/` 下所有技能，生成清单文档，上传到同一知识库。

### 4. 自动同步
在每日 cron job 中加入同步步骤：每次复盘时自动更新 memory 和技能清单到 IMA。

## 使用场景
- Memory 接近 4KB 限制时，将低频信息迁移到 IMA
- 需要查询历史信息时，从 IMA 知识库搜索
- 每日复盘时自动同步，保持 IMA 中的数据最新
