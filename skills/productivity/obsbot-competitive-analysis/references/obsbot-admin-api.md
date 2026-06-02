# OBSBOT Admin System API Reference

Internal admin system for managing netizen/influencer data. Separate from the public OBSBOT website.

## System Architecture

```
Frontend: https://obsbot-cn.remo-ai.com/obsbot_admin/ (Vue SPA)
API:      https://api.obsbot.cn/
  ├── /ums/  — User Management System (auth, users, permissions)
  └── /pms/  — Product/Netizen Management System (influencers, ambassadors)
```

## Authentication

**JWT Token** — passed as raw `Authorization` header (NO "Bearer" prefix):

```bash
curl -H "Authorization: <JWT_TOKEN>" ...
```

Token also stored in cookie `WEB_ADMIN_KEY_USER_TOKEN`. JWT payload:
```json
{"exp": 2080020247, "userId": "f090463b24be48dab174"}
```

**Required header** for all PMS requests:
```
dealer-proxy-type: Remo
```

## Working Endpoints

### User Management (UMS)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ums/v1/users/operation/infos` | Current user info |
| POST | `/ums/v1/users/operation/login` | Login |

### Netizen/Influencer (PMS)

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | `/pms/v1/netizen/detail/infos?id=<N>` | Single netizen detail | ✅ Works |
| GET | `/pms/v1/netizen/currency/infos` | Currency list | ✅ Works |
| GET | `/pms/v1/netizen/region-relations/infos` | Country→Region mapping (67 countries) | ✅ Works |
| GET | `/pms/v1/netizen/confirmed/status?netizen_platform_id=<X>` | Check if confirmed | ✅ Works |
| GET | `/pms/v1/netizen/tags/infos?page_no=1&page_size=1000&type=netizen` | Tag list | ✅ Works |
| POST | `/pms/v1/netizen/ambassador/program/list` | Ambassador list (paginated) | ✅ Works |
| GET | `/pms/v1/netizen/ambassador/program/info?id=<N>` | Ambassador detail | ✅ Works |
| POST | `/pms/v1/netizen/infos-filtering` | **Main netizen list** | ❌ **500 error** |
| POST | `/pms/v1/netizen/infos/export` | Export netizens | ❌ **500 error** |

### V2 Statistics (PMS) — All work ✅

| Method | Path | Description |
|--------|------|-------------|
| POST | `/pms/v2/netizen/confirmed/statistics` | Confirmed stats by region/product |
| POST | `/pms/v2/netizen/confirmed/collaborators` | Collaboration timeline + fees |
| POST | `/pms/v2/netizen/confirmed/views/distribution` | Views grade distribution (total count) |
| POST | `/pms/v2/netizen/confirmed/category/distribution` | Category distribution |
| POST | `/pms/v2/netizen/publish/statistics` | Published stats |
| POST | `/pms/v2/netizen/publish/collaborators` | Published collaborators |
| POST | `/pms/v2/netizen/publish/video/trend/distribution` | Video trend |
| POST | `/pms/v2/netizen/publish/video/daily/trend` | Daily trend |

## Netizen Data Structure

```json
{
  "id": 241,
  "netizen_platform_id": "The Tech Preacher",
  "name": "Eric W",
  "communication_state": "confirm",
  "influence_region": "United States",
  "liaison": "姜姗杉",
  "contact": "email@example.com",
  "operation_platforms": [{
    "platform": "youtube",
    "link": "https://youtube.com/@...",
    "follower": 66400,
    "views": 1075,
    "operate_products_infos": [{"sku": "P.B.1.00022", "product_name": "OBSBOT Tiny 2 Lite"}]
  }],
  "shipping_details": {...},
  "cost_details": {...}
}
```

### Communication States

| Value | Label | Chinese |
|-------|-------|---------|
| `contact_not_reply` | Contacted, no reply | 已联系未回复 |
| `replying` | In communication | 已回复沟通中 |
| `reply_not_cooperate` | Declined | 已回复不合作 |
| `need_try_product` | Need to try product | 需要先试用产品 |
| `confirm` | **Confirmed合作** | 确认合作 |
| `blacklisted` | Blacklisted | 已拉黑 |

## Workaround: Batch ID Scanning

Since `/v1/netizen/infos-filtering` returns 500, individual records can be fetched by ID:

```python
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

h = {"Authorization": TOKEN, "Accept": "application/json", "dealer-proxy-type": "Remo"}

def fetch(nid):
    try:
        r = urllib.request.Request(f"https://api.obsbot.cn/pms/v1/netizen/detail/infos?id={nid}", headers=h)
        resp = urllib.request.urlopen(r, timeout=8)
        return json.loads(resp.read().decode())
    except:
        return None

# Scan with 30-50 concurrent workers
with ThreadPoolExecutor(max_workers=50) as ex:
    futs = {ex.submit(fetch, i): i for i in range(1, 10001)}
    for f in as_completed(futs):
        d = f.result()
        if d and d.get('communication_state') == 'confirm':
            # Process confirmed netizen
            pass
```

### ID Range Findings (2026-06-01)

- **Valid IDs**: 1-20,000 (sparse, ~50% return data)
- **Above 20,000**: All return 500 (invalid)
- **Confirmed density**: ~13% of valid IDs are `confirm` state
- **Scan rate**: ~8-13 IDs/sec with 50 workers
- **Time**: ~18 min for 10,000 IDs

### Ambassador Endpoint

Separate from netizen list. 599 total ambassadors. Use `page_size=50` (larger causes IncompleteRead).

```bash
curl -X POST "https://api.obsbot.cn/pms/v1/netizen/ambassador/program/list" \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -H "dealer-proxy-type: Remo" \
  -d '{"page_no":1,"page_size":50}'
```

Deduplication: ~201 ambassadors overlap with netizen list (match on `url`/`netizen_platform_id`).

## Upload to Tencent Docs

Smartsheet workflow: create → list_tables → delete default fields → add custom fields → add_records (batch ≤10) → delete empty rows → move to folder.

**Field value formats**:
- Text: `{"text_value": {"items": [{"text": "value", "type": "text"}]}}`
- Number: `{"number_value": 123}`

## Pitfalls

1. **`/v1/netizen/infos-filtering` is broken** — Returns 500 for ALL parameter combinations. Server-side bug, not client-side.
2. **ID scanning is slow** — 10,000 IDs takes ~18 min with 50 workers. Use `background=true` + `notify_on_complete=true`.
3. **Ambassador page_size limit** — `page_size=100` causes `IncompleteRead`. Use `page_size=50`.
4. **`operation_platforms` sparse** — Only ~0.4% of netizen detail records have populated `operation_platforms`. Most records only have basic info (name, country, liaison).
5. **mcporter network flakiness** — Tencent Docs MCP sometimes drops connections. Retry on `SSE error` / `fetch failed`.
6. **Python stdout buffering** — Background scripts don't output until buffer fills. Use `sys.stdout.reconfigure(line_buffering=True)` or `flush=True` on prints.
