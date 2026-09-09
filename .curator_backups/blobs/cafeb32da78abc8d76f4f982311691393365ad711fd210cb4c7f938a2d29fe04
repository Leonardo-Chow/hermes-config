# 腾讯文档智能表格批量操作参考

## Pagination
- `list_records` 返回最多 **100 条/页**（即使设 page_size=500）
- 使用 `offset` 参数分页（不是 page_token）
- `has_more` 字段标识是否还有更多数据

```python
offset = 0
while True:
    args = {"file_id": fid, "sheet_id": sid, "page_size": 500, "offset": offset}
    result = mcporter_call("smartsheet.list_records", args)
    records = result.get("records", [])
    if not records: break
    offset += len(records)
    if not result.get("has_more", True): break
```

## Batch Delete
- `delete_records` 接受 `record_ids` 数组
- 建议每批 **100 条**
- 删除后 offset 需重置为 0（记录位置会变）

```python
# 循环删除直到为空
while True:
    # 获取当前记录
    ids = get_all_record_ids()
    if not ids: break
    # 删除一批
    mcporter_call("smartsheet.delete_records", {"file_id": fid, "sheet_id": sid, "record_ids": ids[:100]})
```

## Batch Upload
- `add_records` 每批 **≤10 条**（mcporter 20K 字符输出限制）
- 记录格式：`{"field_values": [{"field": "字段名", "text_value": {...}}]}`
- 文本值格式：`{"text_value": {"items": [{"text": "内容", "type": "text"}]}}`
- 数字值格式：`{"number_value": 123}`

## Field Types
- text: `property_text: {}`
- number: `property_number: {"decimal_places": 0, "use_separate": true}`
- 创建字段时**必须包含 property 对象**，否则静默失败

## 去重策略
1. 拉取全部记录（分页）
2. 按唯一字段（如 ID）分组
3. 保留第一条，删除其余
4. 或清空后重新上传（更快）

## 清空+重传 vs 增量更新
| 策略 | 适用场景 | 速度 |
|------|---------|------|
| 清空+重传 | 数据量 <5000，有完整数据集 | 快 |
| 增量更新 | 数据量大，只需更新部分 | 慢（需查重） |

## 大批量上传超时处理
- `add_records` 每批10条，约0.3s/批
- 上传1500条 ≈ 45秒（理论），实际因网络波动可能需要3-5分钟
- **terminal timeout=300s 可能不够** — 分段上传：先上传前500条，检查进度，再继续
- 上传中断后检查已上传数量，从断点继续（用 `list_records` 获取 total）

## 清空全部记录的可靠方法
```python
# 循环获取+删除直到 total=0
while True:
    # 每次获取前100条
    result = mcporter_call("smartsheet.list_records", {"file_id": fid, "sheet_id": sid, "page_size": 500, "offset": 0})
    ids = [r['record_id'] for r in result.get('records', [])]
    if not ids: break
    # 批量删除
    for i in range(0, len(ids), 100):
        mcporter_call("smartsheet.delete_records", {"file_id": fid, "sheet_id": sid, "record_ids": ids[i:i+100]})
```
⚠️ 删除后必须重新从 offset=0 获取（记录位置会变化）

## 上传字段映射模板
```python
FIELDS = {
    'id': 'ID',           # number_value
    'platform_id': '网红ID',  # text_value
    'name': '姓名',        # text_value
    'country': '国家',      # text_value
    'liaison': '对接人',    # text_value
    'contact': '联系方式',   # text_value
}
# number 字段: {"field": "ID", "number_value": 123}
# text 字段: {"field": "网红ID", "text_value": {"items": [{"text": "xxx", "type": "text"}]}}
```
