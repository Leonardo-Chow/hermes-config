# 腾讯文档 Smartcanvas Fallback

## 问题

`create_smartcanvas_by_mdx` 工具可能返回 RPC 错误：

```
MCP error -32603: tool execution failed: rpc name /api/v6/open/agent/smartcanvas/create_smartcanvas_by_mdx invalid
```

## 解决方案

使用 doc 类型 + `doc.insert_markdown` 作为 fallback：

```bash
# 步骤1: 创建 doc 类型文件
mcporter call tencent-docs manage.create_file --args '{"title": "文件名", "file_type": "doc"}'
# 返回: {"file_id": "xxx", "url": "https://docs.qq.com/doc/xxx"}

# 步骤2: 插入 Markdown 内容
mcporter call tencent-docs doc.insert_markdown --args '{"file_id": "xxx", "index": 0, "markdown": "# 标题\n\n内容..."}'

# 步骤3: 移动到目标文件夹
mcporter call tencent-docs manage.move_file --args '{"file_id": "xxx", "target_folder_id": "DjbGtzenXmbX"}'
```

## 注意事项

- `doc.insert_markdown` 的 `index` 参数是插入位置，0 表示文档开头
- doc 类型的排版不如 smartcanvas 美观，但功能完整
- 如果 doc.insert_markdown 也失败，尝试重新授权：`mcporter auth tencent-docs`
