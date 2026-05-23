# Sheet 批量数据上传工作流

## 概述

将结构化数据（JSON/CSV）批量写入腾讯文档在线表格的完整流程。

## 前置条件

1. **mcporter 已配置 tencent-docs 服务**
2. **Token 已设置**（环境变量 `TENCENT_DOCS_TOKEN` 或 mcporter 配置）

## 工作流

### 1. 配置 mcporter（首次）

```bash
# 使用 Token 添加服务
mcporter config add tencent-docs "https://docs.qq.com/openapi/mcp" \
    --header "Authorization=$TENCENT_TOKEN" \
    --transport http \
    --scope home
```

### 2. 获取表格信息

从 URL 提取 `file_id`：
- URL: `https://docs.qq.com/sheet/DRG5sWm1Rbk9CZmty`
- file_id: `DRG5sWm1Rbk9CZmty`

```bash
mcporter call tencent-docs sheet.get_sheet_info file_id=<file_id>
```

返回：
```json
{
  "sheets": [
    {
      "sheet_id": "BB08J2",
      "sheet_name": "工作表1",
      "row_count": 200,
      "col_count": 26
    }
  ]
}
```

### 3. 准备批量数据

构建 `values` 数组，每个元素包含 `row`、`col`、`value_type`、`string_value`：

```python
import json

headers = ['列A', '列B', '列C']
data = [{'列A': '值1', '列B': '值2', '列C': '值3'}]

values = []

# 表头（第0行）
for col, header in enumerate(headers):
    values.append({
        "row": 0,
        "col": col,
        "value_type": "STRING",
        "string_value": header
    })

# 数据行（从第1行开始）
for row_idx, item in enumerate(data, 1):
    for col_idx, header in enumerate(headers):
        values.append({
            "row": row_idx,
            "col": col_idx,
            "value_type": "STRING",
            "string_value": str(item.get(header, ''))
        })

payload = {
    "file_id": "<file_id>",
    "sheet_id": "<sheet_id>",
    "values": values
}

with open('/tmp/sheet_payload.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
```

### 4. 批量写入

```bash
mcporter call tencent-docs sheet.set_range_value \
    file_id=<file_id> \
    sheet_id=<sheet_id> \
    values='[{"row":0,"col":0,"value_type":"STRING","string_value":"表头"}]'
```

或使用 Python 调用：
```python
import subprocess
import json

with open('/tmp/sheet_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

cmd = ['mcporter', 'call', 'tencent-docs', 'sheet.set_range_value']
for k, v in payload.items():
    if k == 'values':
        cmd.append(f'values={json.dumps(v, ensure_ascii=False)}')
    else:
        cmd.append(f'{k}={v}')

result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
print(result.stdout)
```

### 5. 验证写入

```bash
mcporter call tencent-docs sheet.get_cell_data \
    file_id=<file_id> \
    sheet_id=<sheet_id> \
    row=0 col=0
```

## 性能限制

- 单次写入建议不超过 **1MB**（约几千个单元格）
- 超大批量需拆分为多次写入
- 35行×11列 = 396个单元格，约36KB，一次写入无压力

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `400006` Token 鉴权失败 | Token 过期或无效 | 重新获取 Token：https://docs.qq.com/scenario/open-claw.html |
| `SSE error: fetch failed` | 网络超时 | 检查 VPN 连接，重试 |
| 数据为空 | sheet_id 错误 | 先调用 `get_sheet_info` 获取正确的 sheet_id |

## 完整示例

见本会话中 `/tmp/obsbot_merged_data.json` → 腾讯文档表格的完整流程。
