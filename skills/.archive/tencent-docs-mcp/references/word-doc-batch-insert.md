# Word 文档大内容批量插入模式

## 问题
`doc.insert_markdown` 插入大段 Markdown 内容时可能失败（网络超时、API 限制）。

## 解决方案：分批插入

将大内容拆分为每批约 5000 字符，逐批插入。

### 完整代码

```python
import json
import subprocess

# 1. 创建 Word 文档
result = subprocess.run([
    'mcporter', 'call', 'tencent-docs', 'manage.create_file',
    'file_type=doc', 'title=文档标题', 'parent_id=文件夹ID'
], capture_output=True, text=True, timeout=30)
file_id = json.loads(result.stdout)['file_id']
doc_url = json.loads(result.stdout)['url']

# 2. 获取最后可操作位置
result = subprocess.run([
    'mcporter', 'call', 'tencent-docs', 'doc.get_last_operable_pos',
    f'file_id={file_id}'
], capture_output=True, text=True, timeout=30)
pos_data = json.loads(result.stdout)
current_index = pos_data['position']
current_version = pos_data['version']

# 3. 分批插入内容
content = "大段 Markdown 内容..."
batch_size = 5000

for i in range(0, len(content), batch_size):
    batch = content[i:i+batch_size]
    
    result = subprocess.run([
        'mcporter', 'call', 'tencent-docs', 'doc.insert_markdown',
        f'file_id={file_id}',
        f'index={current_index}',
        f'markdown={batch}'
    ], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        current_version = response.get('version', current_version)
        current_index = response.get('last_index', current_index)
        print(f"✅ 批次 {i//batch_size + 1} 成功")
    else:
        print(f"❌ 批次 {i//batch_size + 1} 失败: {result.stderr[:100]}")
        # 重试一次
        result = subprocess.run([
            'mcporter', 'call', 'tencent-docs', 'doc.insert_markdown',
            f'file_id={file_id}',
            f'index={current_index}',
            f'markdown={batch}'
        ], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            current_version = response.get('version', current_version)
            current_index = response.get('last_index', current_index)

print(f"\n✅ 文档创建完成: {doc_url}")
```

## 关键参数

| 参数 | 说明 |
|------|------|
| `file_id` | 文档 ID（从 create_file 返回） |
| `index` | 插入位置（不是 `pos`！） |
| `markdown` | Markdown 内容 |
| `version_info` | 可选，`{"is_latest": true}` 或 `{"base_version": N}` |

## Pitfalls

1. **参数名是 `index` 不是 `pos`** — 用错会报 "missing required parameters: [index]"
2. **分批大小建议 5000 字符** — 太大可能超时，太小效率低
3. **网络不稳定时重试** — 某些批次可能因网络问题失败
4. **最后一批可能失败** — 如果失败，单独重试一次
5. **版本号递增** — 每次插入后版本号会递增，下次插入用新版本

## 实战数据

- 65,459 字符的评论报告
- 分 14 批插入（每批约 5000 字符）
- 总耗时约 66 秒
- 13/14 批成功，最后一批重试后成功
