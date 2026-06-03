# OBSBOT Admin System API Reference

## API Architecture

- **Frontend**: `https://obsbot-cn.remo-ai.com/obsbot_admin/` (Vue SPA, heavy JS bundle)
- **API Base**: `https://api.obsbot.cn`
  - **UMS** (User Management): `https://api.obsbot.cn/ums/`
  - **PMS** (Product/Netizen Management): `https://api.obsbot.cn/pms/`

## Authentication

- **Token**: JWT stored in cookie `WEB_ADMIN_KEY_USER_TOKEN`
- **Header format**: `Authorization: <raw_JWT>` (NO "Bearer" prefix)
- **Required header**: `dealer-proxy-type: Remo` (or China/Korea/Japan/Tiktok)
- **User info endpoint**: `GET /ums/v1/users/operation/infos`

## Netizen (网红) Endpoints

### Working Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pms/v1/netizen/detail/infos?id=N` | GET | Single netizen detail by ID |
| `/pms/v1/netizen/confirmed/status?netizen_platform_id=X` | GET | Check if confirmed (flag: 0=no, 1=yes, 2=other team) |
| `/pms/v1/netizen/currency/infos` | GET | Currency list |
| `/pms/v1/netizen/region-relations/infos` | GET | 67 countries, 12 regions |
| `/pms/v1/netizen/ambassador/program/list` | POST | Ambassador list (599 total, page_size up to 200) |
| `/pms/v1/netizen/ambassador/program/info?id=N` | GET | Ambassador detail |
| `/pms/v2/netizen/confirmed/statistics` | POST | Confirmed stats by region/product (total: 2,385) |
| `/pms/v2/netizen/confirmed/views/distribution` | POST | Views distribution (2,860 entries) |
| `/pms/v2/netizen/confirmed/collaborators` | POST | Collaboration timeline |
| `/pms/v2/netizen/confirmed/category/distribution` | POST | Category distribution |
| `/pms/v2/netizen/publish/statistics` | POST | Published video stats |
| `/pms/v2/netizen/publish/collaborators` | POST | Published collaborators |

### ⚠️ BROKEN Endpoint

**`/pms/v1/netizen/infos-filtering`** — The main list/filtering endpoint returns **HTTP 500** for ALL requests. This is a server-side bug, not a client issue. Tested with:
- All parameter combinations (page_no/page, status, search_type, communication_state, type)
- All auth methods (Authorization header, Cookie, both)
- All dealer-proxy-types (Remo, China, Korea, Japan)
- Browser context fetch (same 500)
- Form-encoded POST (415)

Also broken: `/pms/v1/netizen/infos/export` (500)

### Workaround: ID Scanning

Since the list endpoint is broken, individual records can be fetched by ID:
- **Endpoint**: `GET /pms/v1/netizen/detail/infos?id=N`
- **Valid ID range**: 1-20,000 (IDs above 20k return 500)
- **Confirmed netizens**: ~1,572 found via scanning with retries (out of ~2,385 total)
- **Concurrency**: 30-50 workers recommended, 15s timeout
- **Retries**: 3 attempts with exponential backoff for IncompleteRead errors
- **Rate**: ~8-10 IDs/second with 50 workers
- **Script**: `scripts/scan_netizens.py`

### ⚠️ Count Discrepancy

The v2 endpoints report **two different totals**:
- `v2/netizen/confirmed/statistics` → `all_total_infos.total` = **2,385** (unique confirmed netizens)
- `v2/netizen/confirmed/views/distribution` → sum of `total_netizen_num` = **2,860** (platform-level entries, one netizen can have multiple platforms)

Use 2,385 as the confirmed netizen count. The 2,860 includes duplicate platform entries.

### Ambassador vs Netizen

Ambassadors (`/v1/netizen/ambassador/program/list`, 599 records) are a **separate dataset** from confirmed netizens. After deduplication by `platform_id`/`url`, ~398 ambassadors are unique (not in the netizen list). Combined total: ~1,970 unique records.

### Upload to Tencent Docs

After scanning, upload to smartsheet using batched `smartsheet.add_records`:
- **Batch size**: ≤10 records per call (mcporter output truncation at 20K chars)
- **Field mapping**: ID (number), 网红ID/姓名/国家/对接人/联系方式 (text)
- **Save location**: `~/Downloads/obsbot_confirmed_netizens.json` (persistent, not /tmp)

### JS Reverse-Engineering Tips

To find the API base URL in minified Vue bundles:
1. Look for the axios instance factory: `function Uo(e){let{baseURL:t,...}=e||{}`
2. Trace the `baseURL` variable back to its source module (e.g., `market-DvH-txIb.js` exports `l='https://api.obsbot.cn'`)
3. The import chain: `import{...l as kt...}from"./market-..."` → `baseURL: \`${kt}/pms\``
4. Auth interceptor reads cookie `WEB_ADMIN_KEY_USER_TOKEN` via `or()` function and sets raw value as `Authorization` header

### Netizen Data Fields

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
  }]
}
```

### Communication States

| State | Label |
|-------|-------|
| `contact_not_reply` | 已联系未回复 |
| `replying` | 已回复沟通中 |
| `reply_not_cooperate` | 已回复不合作 |
| `need_try_product` | 需要先试用产品 |
| `confirm` | 确认合作 |
| `blacklisted` | 已拉黑 |

### Ambassador Categories

- Game Streamers: 446
- Tech Enthusiasts: 111
- Livestream Instructor: 22
- Art Creation: 10
- Lifestyle: 10

## How to Discover API Endpoints

1. Download main JS bundle: `curl -s 'https://obsbot-cn.remo-ai.com/obsbot_admin/assets/index-DxUNngwW.js'`
2. Search for API paths: `grep -oE '/v[0-9]+/netizen/[a-zA-Z0-9/_-]+' file.js | sort -u`
3. Find base URL: Look for vendor module that exports the API domain (e.g., `market-DvH-txIb.js` exports `https://api.obsbot.cn` as `l`)
4. Find auth: Look for `Uo()` axios instance factory with `interceptors.request.use` that reads cookie and sets Authorization header

## Current User

- **Account**: leonardo@obsbot.com (周龙)
- **Role**: Market Admin (role=2)
- **Proxy**: Remo
- **Token expiry**: ~2036
