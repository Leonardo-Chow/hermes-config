# IMA 作为外部 Memory 的使用模式

## 概述

IMA 知识库可以作为 Hermes Agent 的外部 Memory 存储，突破内置 4KB 限制。

## 架构

```
┌─────────────────────────────┐
│  Hermes 内置 Memory (4KB)   │  ← 高频信息
│  memory_char_limit: 4000    │
└──────────────┬──────────────┘
               │ 每日同步（cron job）
               ▼
┌─────────────────────────────┐
│  IMA 知识库（外部 Memory）  │  ← 无上限存储
│  • 持久记忆笔记             │
│  • 技能清单                 │
│  • 历史记录                 │
│  • 学习资料                 │
└─────────────────────────────┘
```

## 使用场景

1. **Memory 接近限制时**：将低频信息迁移到 IMA 知识库
2. **每日复盘时**：自动同步 memory 和 skills 到 IMA
3. **长期存储**：历史记录、学习笔记、参考资料

## 操作流程

### 上传 Memory 到 IMA

```bash
SKILL_DIR=~/.hermes/skills/ima-skills

# 1. 创建笔记
node "$SKILL_DIR/ima_api.cjs" "openapi/note/v1/import_doc" \
  '{"title": "🧠 Hermes Memory", "content": "...", "content_format": 1}'

# 2. 添加到知识库
node "$SKILL_DIR/ima_api.cjs" "openapi/wiki/v1/add_knowledge" \
  '{"media_type": 11, "note_info": {"content_id": "<note_id>"}, "title": "...", "knowledge_base_id": "<kb_id>"}'
```

### 从 IMA 检索信息

```bash
# 搜索知识库
node "$SKILL_DIR/ima_api.cjs" "openapi/wiki/v1/search_knowledge" \
  '{"query": "<keyword>", "knowledge_base_id": "<kb_id>", "cursor": ""}'

# 浏览知识库内容
node "$SKILL_DIR/ima_api.cjs" "openapi/wiki/v1/get_knowledge_list" \
  '{"knowledge_base_id": "<kb_id>", "cursor": "", "limit": 20}'
```

## 推荐知识库结构

| 知识库 | 用途 | 更新频率 |
|:-------|:-----|:---------|
| Herme记忆库 | 外部 Memory、技能清单 | 每日同步 |
| 学习知识库 | 学习资料、技术文档 | 按需 |
| 摸鱼日报 | 每日新闻聚合 | 每日 |

## Pitfalls

- **导入笔记端点**：使用 `openapi/note/v1/import_doc`（不是 `wiki/v2`）
- **COS token 截断**：文件上传时 token 875+ 字符会被 shell 截断，需用 Node.js spawn 或一体化脚本
- **搜索限制**：`search_knowledge` 需要指定 `knowledge_base_id`，不能跨库搜索
- **索引延迟**：新上传的内容可能需要几秒才能被搜索到
