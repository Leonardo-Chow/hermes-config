# OBSBOT Admin API Reference

## Base URLs
- **Domain**: `api.obsbot.cn`
- **UMS** (User Management): `https://api.obsbot.cn/ums`
- **PMS** (Product/Netizen Management): `https://api.obsbot.cn/pms`
- **Frontend**: `obsbot-cn.remo-ai.com/obsbot_admin/`

## Authentication
- **JWT Token**: Pass via `Authorization` header (NO "Bearer" prefix, just raw token)
- **Cookie**: `WEB_ADMIN_KEY_USER_TOKEN=<jwt>`
- **Required Header**: `dealer-proxy-type: Remo` (or China/Korea/Japan/Tiktok)

## Key Endpoints

### User Management (UMS)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/users/operation/infos` | Get current user info |

### Netizen Management (PMS)
| Method | Path | Status | Description |
|--------|------|--------|-------------|
| POST | `/v1/netizen/infos-filtering` | ❌ 500 | List netizens (BROKEN) |
| POST | `/v1/netizen/infos/export` | ❌ 500 | Export (BROKEN) |
| GET | `/v1/netizen/detail/infos?id=N` | ✅ | Get single netizen by ID |
| GET | `/v1/netizen/confirmed/status?netizen_platform_id=X` | ✅ | Check confirmed status |
| GET | `/v1/netizen/currency/infos` | ✅ | Currency list |
| GET | `/v1/netizen/region-relations/infos` | ✅ | 67 countries, 12 regions |
| POST | `/v1/netizen/ambassador/program/list` | ✅ | Ambassador list (599) |
| GET | `/v1/netizen/ambassador/program/info?id=N` | ✅ | Ambassador detail |

### V2 Statistics (PMS) - All Working
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v2/netizen/confirmed/statistics` | Stats by region/product |
| POST | `/v2/netizen/confirmed/collaborators` | Collaboration timeline |
| POST | `/v2/netizen/confirmed/views/distribution` | Views distribution |
| POST | `/v2/netizen/confirmed/category/distribution` | Category distribution |

## Netizen Communication States
- `confirm` — Confirmed合作
- `contact_not_reply` — 已联系未回复
- `replying` — 已回复沟通中
- `reply_not_cooperate` — 已回复不合作
- `need_try_product` — 需要先试用产品
- `blacklisted` — 已拉黑

## Data Retrieval Strategy (workaround for 500 error)
1. Scan IDs 1-20000 via `detail/infos?id=N` with 50 concurrent workers
2. Fetch ambassadors via `ambassador/program/list` (page_size=50)
3. Merge & deduplicate by platform_id
4. Confirmed total: 2,385 (from v2 statistics)

## Confirmed Status Endpoint
- `GET /v1/netizen/confirmed/status?netizen_platform_id=<encoded_name>`
- Returns: `flag=0` (not confirmed/not found), `flag=1` (confirmed), `flag=2` (confirmed in other team)
- URL-encode the platform_id (spaces → %20)
- Works for all proxy types (Remo/China/Korea/Japan)

## Data Counts
- **Ambassador total**: 599 (active: 590, draft: 8)
- **Confirmed netizens (all_total_infos)**: 2,385
- **Views distribution total**: 2,860 (multi-platform entries, not unique netizens)
- **Regions**: EU (818), NA (1,235), Others (331)
- **Netizen categories**: Game Streamers (446), Tech Enthusiasts (111), Livestream Instructor (22)

## Ambassador Endpoint Details
- Supports `page_size=200` (tested, works — 3 pages for 599 records)
- `page_size=100` causes IncompleteRead (response too large)
- `keyword` filter does NOT work (always returns all records)
- `category` and `status` filters work correctly
- All proxy types return same 599 records

## ID Scanning Results (2026-06-01)
- IDs 1-20000: 2,147 confirmed netizens found
- IDs 20001-30000: 0 valid records (all return 500)
- Best range: IDs 12001-14000 (highest density of confirmed)
- Scanning rate: ~50 IDs/second with 50 concurrent workers, 8s timeout
- Error rate: ~40% of IDs return timeout/connection errors
- Each scan pass finds ~100-200 new confirmed (due to random timeouts)

## JS Reverse Engineering
- Main bundle: `/obsbot_admin/assets/index-*.js`
- Market module: exports base URL `https://api.obsbot.cn`
- Token in cookie `WEB_ADMIN_KEY_USER_TOKEN`, interceptor sets Authorization header (no Bearer)
- Auth interceptor also sets `dealer-proxy-type` header based on route meta.dealerKey
- Confirmed list imports filtering function as `Ot as fe` from index → calls `Z.post('/v1/netizen/infos-filtering', body)`
