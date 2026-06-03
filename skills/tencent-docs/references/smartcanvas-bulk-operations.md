# 智能表格大批量数据操作参考

## 背景

当需要向腾讯文档智能表格上传 1000+ 条记录时，会遇到以下问题：
1. `list_records` 每页最多返回 100 条（无论 page_size 设多大）
2. mcporter 单次调用 ~300s 超时
3. 大批量删除需要逐页获取 record_id 再批量删除

## 完整工作流：清空 + 重建

### Step 1: 清空现有数据

```python
import json, subprocess, time

FILE_ID = "xxx"
SHEET_ID = "xxx"

# 逐批获取所有 record_id
all_ids = []
offset = 0
while True:
    args = json.dumps({"file_id": FILE_ID, "sheet_id": SHEET_ID, "page_size": 500, "offset": offset})
    r = subprocess.run(["mcporter", "call", "tencent-docs", "smartsheet.list_records", "--args", args],
                      capture_output=True, text=True, timeout=30)
    d = json.loads(r.stdout)
    recs = d.get('records', [])
    if not recs: break
    all_ids.extend([rec['record_id'] for rec in recs])
    offset += len(recs)
    if not d.get('has_more', True): break
    time.sleep(0.15)

# 逐批删除（每批 100 条）
for i in range(0, len(all_ids), 100):
    batch = all_ids[i:i+100]
    args = json.dumps({"file_id": FILE_ID, "sheet_id": SHEET_ID, "record_ids": batch})
    subprocess.run(["mcporter", "call", "tencent-docs", "smartsheet.delete_records", "--args", args],
                  capture_output=True, text=True, timeout=30)
    time.sleep(0.15)
```

**注意**：如果记录数 > 1200，需要多轮删除（每轮获取 1200 条，删除后重新获取）。

### Step 2: 上传新数据（断点续传）

```python
BATCH = 10
uploaded = 0  # 首次从 0 开始；续传时改为上次的值

for i in range(uploaded, len(records), BATCH):
    batch = records[i:i+BATCH]
    sm_records = []
    for r in batch:
        fv = []
        for key, field_name in FIELD_MAP.items():
            val = r.get(key, '')
            if key == 'id':
                if val: fv.append({"field": field_name, "number_value": int(val)})
            else:
                if val: fv.append({"field": field_name, "text_value": {"items": [{"text": str(val), "type": "text"}]}})
        sm_records.append({"field_values": fv})
    
    args = json.dumps({"file_id": FILE_ID, "sheet_id": SHEET_ID, "records": sm_records}, ensure_ascii=False)
    try:
        result = subprocess.run(["mcporter", "call", "tencent-docs", "smartsheet.add_records", "--args", args],
                              capture_output=True, text=True, timeout=30)
        if '"error":""' in result.stdout:
            uploaded += len(batch)
        else:
            print(f"Error at batch {i}: {result.stdout[:200]}")
    except:
        print(f"Timeout at batch {i}")
    
    # 超时保护：280s 时停止，打印断点
    if time.time() - start > 280:
        print(f"Resume from {i + BATCH}")
        break
    time.sleep(0.15)
```

## API 逆向工程模式（从 minified JS 提取端点）

当需要调用的 API 端点未知时，从前端 JS bundle 中提取：

1. 获取 HTML 页面，找到 `<script>` 标签引用的 JS 文件
2. 下载主 JS bundle（通常是最大的那个）
3. 搜索关键模式：
   - `baseURL` — axios 实例的基础 URL
   - `/v1/` 或 `/v2/` — API 路径前缀
   - `Authorization` 或 `Bearer` — 认证方式
   - `.post(` 或 `.get(` — HTTP 方法调用
4. 提取 export 别名（如 `export {a as b}`）追踪变量来源
5. 找到 axios 实例创建位置，确认 baseURL

### 示例：OBSBOT Admin API 逆向

```bash
# 1. 获取 HTML
curl -s "https://obsbot-cn.remo-ai.com/obsbot_admin/login"

# 2. 找到 JS bundle
grep -oE 'assets/[a-zA-Z0-9_-]+\.js' index.html

# 3. 下载主 bundle
curl -s "https://.../assets/index-XXX.js" > /tmp/main.js

# 4. 搜索 API 路径
grep -oE '/v[0-9]+/[a-zA-Z0-9/_-]+' /tmp/main.js | sort -u

# 5. 找 baseURL
grep -o '.{0,100}baseURL.{0,100}' /tmp/main.js

# 6. 找认证方式
grep -o '.{0,100}Authorization.{0,100}' /tmp/main.js
```

## 并发 ID 扫描模式（列表接口不可用时）

当列表 API 返回 500 但详情 API 正常时，用并发扫描替代：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(nid):
    try:
        r = urllib.request.Request(f"{API}/detail?id={nid}", headers=h)
        resp = urllib.request.urlopen(r, timeout=8)
        return json.loads(resp.read().decode())
    except:
        return None

confirmed = {}
W = 50  # 并发数

for bs in range(1, MAX_ID + 1, W):
    ids = list(range(bs, min(bs + W, MAX_ID + 1)))
    with ThreadPoolExecutor(max_workers=W) as ex:
        futs = {ex.submit(fetch, i): i for i in ids}
        for f in as_completed(futs):
            d = f.result()
            if d and d.get('communication_state') == 'confirm':
                confirmed[d['id']] = d
```

**性能参考**：
- 50 workers × 8s timeout ≈ 8-10 IDs/秒
- 20,000 IDs ≈ 35-45 分钟
- 约 40-50% 的请求会超时/失败，需要重试扫描
