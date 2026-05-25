# IMA 记忆同步工作流

## 概述
将 Hermes 本地 memory/user 文件同步到 IMA Herme记忆库，实现跨设备持久化。

## 源文件
| 文件 | 路径 | 内容 |
|------|------|------|
| memory.md | `~/.hermes/memory.md` | 系统状态、环境事实、方法论、关键约束 |
| user.md | `~/.hermes/user.md` | 用户信息、偏好、技术环境、认证信息 |
| memory/memory.md | `~/.hermes/memory/memory.md` | IMA知识库ID、工具链、维护记录 |
| memory/user.md | `~/.hermes/memory/user.md` | 工作风格、格式偏好、网络工具 |

## 目标知识库
- **Herme记忆库**: `uhcEva4nd2xus1Q2yt7yn_N4_waEdOsQlVU3lhnkLXw=`

## 流程（Python + ima_api.cjs）

```python
import json, subprocess
from datetime import datetime

skill_dir = "/Users/zhoulong/.hermes/skills/ima-skills"
kb_id = "uhcEva4nd2xus1Q2yt7yn_N4_waEdOsQlVU3lhnkLXw="

# 1. 读取所有 memory 文件
files = [
    "~/.hermes/memory.md",
    "~/.hermes/user.md",
    "~/.hermes/memory/memory.md",
    "~/.hermes/memory/user.md"
]
contents = {}
for f in files:
    with open(f.replace("~", "/Users/zhoulong"), "r", encoding="utf-8") as fh:
        contents[f] = fh.read()

# 2. 组合内容
today = datetime.now().strftime("%Y-%m-%d")
combined = f"# Hermes 记忆同步 | {today}\n\n"
for path, content in contents.items():
    combined += f"---\n## {path}\n\n{content}\n\n"

# 3. 创建笔记
title = f"Hermes记忆同步 | {today}"
payload = json.dumps({"title": title, "content": combined, "content_format": 1}, ensure_ascii=False)
result = subprocess.run(
    ['node', 'ima_api.cjs', 'openapi/note/v1/import_doc', payload],
    cwd=skill_dir, capture_output=True, text=True, timeout=60
)
resp = json.loads(result.stdout)
note_id = resp['data']['note_id']

# 4. 添加到知识库
kb_payload = json.dumps({
    "media_type": 11,
    "note_info": {"content_id": note_id},
    "title": title,
    "knowledge_base_id": kb_id
}, ensure_ascii=False)
subprocess.run(
    ['node', 'ima_api.cjs', 'openapi/wiki/v1/add_knowledge', kb_payload],
    cwd=skill_dir, capture_output=True, text=True, timeout=30
)
```

## 注意事项
- 标题格式: `Hermes记忆同步 | YYYY-MM-DD`
- 每次同步创建新笔记，不覆盖旧的
- memory.md 和 user.md 各有两个副本（根目录 + memory/ 子目录），都应包含
- cron job 中 `memory` 工具不可用，无法在此流程中更新 memory.md
