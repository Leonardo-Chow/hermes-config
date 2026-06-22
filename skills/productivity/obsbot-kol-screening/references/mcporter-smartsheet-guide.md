# mcporter smartsheet 操作注意事项

## 创建 smartsheet 全流程

```python
import json, subprocess, time

# 1. 创建文件
r = subprocess.run(['mcporter','call','tencent-docs','manage.create_file','--args',
    json.dumps({"title":"标题","file_type":"smartsheet"})], capture_output=True, text=True, timeout=30)
file_id = json.loads(r.stdout).get('file_id','')

# 2. 获取 sheet_id（有时 list_tables 会失败，直接用 t00i2h）
sheet_id = "t00i2h"  # 默认值，新创建的 smartsheet 通常都是这个

# 3. 删除默认字段（5个：单选/数字/日期/图片/文本）
r = subprocess.run(['mcporter','call','tencent-docs','smartsheet.list_fields','--args',
    json.dumps({"file_id":file_id,"sheet_id":sheet_id})], capture_output=True, text=True, timeout=30)
for f in json.loads(r.stdout).get('fields',[]):
    subprocess.run(['mcporter','call','tencent-docs','smartsheet.delete_fields','--args',
        json.dumps({"file_id":file_id,"sheet_id":sheet_id,"field_ids":[f['field_id']]})],
        capture_output=True, text=True, timeout=30)
    time.sleep(0.2)

# 4. 添加自定义字段
fields = [...]  # 14列模板
subprocess.run(['mcporter','call','tencent-docs','smartsheet.add_fields','--args',
    json.dumps({"file_id":file_id,"sheet_id":sheet_id,"fields":fields})],
    capture_output=True, text=True, timeout=30)

# 5. 移动到目标文件夹
subprocess.run(['mcporter','call','tencent-docs','manage.move_file','--args',
    json.dumps({"file_id":file_id,"target_folder_id":"FOLDER_ID"})],
    capture_output=True, text=True, timeout=30)

# 6. 逐条添加记录（不要批量！）
for rec in records:
    payload = json.dumps({"file_id":file_id,"sheet_id":sheet_id,"records":[rec]}, ensure_ascii=False)
    for attempt in range(3):
        try:
            r = subprocess.run(['mcporter','call','tencent-docs','smartsheet.add_records','--args',payload],
                capture_output=True, text=True, timeout=60)
            if json.loads(r.stdout).get('records'):
                break
        except: pass
        time.sleep(2)
    time.sleep(0.3)
```

## 关键坑

| 问题 | 解决方案 |
|:-----|:---------|
| **批量 add_records 超时** | 逐条添加（1条/次），timeout=60s，间隔 0.3s |
| **list_tables 返回空** | 直接用 `sheet_id="t00i2h"`，新 smartsheet 默认都是这个 |
| **字段用 field_name** | 不用 field_id，直接用字段名（如 "KOL ID"） |
| **特殊字符** | creator_id 必须用 `shell_quote()` 包裹 |
| **VPN 冲突（关键！）** | VPN 连接时 mcporter auth 会失败（"fetch failed"/"SSE error"/"HTTP 405"）。**必须先断开 VPN**：`scutil --nc stop "Shadowrocket"`，认证/操作成功后再重连。mcporter 走腾讯文档直连，不经过代理。 |
| **VPN 断连** | mcporter 调用返回空 → 重连 VPN + re-auth |
| **re-auth** | `mcporter auth tencent-docs` 解决大部分连接问题。但**必须先断 VPN 再 auth**。 |
| **record_id 获取** | 从 list_records 返回的 records[].record_id |
| **去重** | list_records → 按 KOL ID 去重 → delete_records 多余的 |

## 常用文件夹 ID

| 文件夹 | ID |
|:-------|:---|
| OBSBOT | DjbGtzenXmbX |
| 红人筛选 | DTmwKKobNEvK |
| 每日监测 | DumZsGZJrwsf |
