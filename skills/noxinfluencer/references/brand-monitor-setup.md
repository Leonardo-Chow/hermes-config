# Brand Monitor Setup Guide

## Key Limitation (verified 2026-05-29)

**There is NO `brand-monitor create` command.** Only `brand-monitor add <brand_id>` exists.

The `brand_id` is an opaque identifier from NoxInfluencer's internal brand database. It cannot be:
- Searched via CLI
- Searched via API
- Guessed or generated

## How to Get a Brand ID

1. Open https://www.noxinfluencer.com or https://cn.noxinfluencer.com in a browser
2. Navigate to Brand Monitor
3. Search for the brand (e.g., "OBSBOT")
4. Copy the brand_id from the URL or page

## Adding a Brand

```bash
noxinfluencer brand-monitor add <brand_id> --force
```

## Existing Monitors

As of 2026-05-29, the account has:
- Roblox: `2_Zo8xvGlDG5LEOMSWvFdi9yhcXHEsLnnOyPRBkS` (YouTube, Instagram, TikTok)
- Nike: `6qc-ihHOWMRVe6cJNcXf_MNRDt7Ar3q6z5wROW2t2ckO` (YouTube, Instagram, TikTok)

## Available Brand Monitor Commands

| Command | Purpose |
|---------|---------|
| `brand-monitor list` | List monitored brands |
| `brand-monitor get <brand_id>` | Get brand details |
| `brand-monitor add <brand_id>` | Add brand (requires existing brand_id) |
| `brand-monitor competition-matrix` | Brand competition analysis |
| `brand-monitor cooperate-matrix` | Cooperation matrix |
| `brand-monitor influencer-portrait` | Influencer demographics |
| `brand-monitor defense-gap` | Brand defense gap analysis |
| `brand-monitor product-*` | Product signals (YouTube only) |
| `brand-monitor influencer-list` | Influencer asset list |
| `brand-monitor content-list` | Content asset list |
| `brand-monitor *-export` | Export data |

## Product Signal Limitation

Product signal commands (`product-*`) currently support **YouTube only**. Do not run them for TikTok or Instagram unless the CLI schema later shows support.

## GFW Pitfall

NoxInfluencer's API server (`skill.noxinfluencer.com`) is behind the GFW. Connect Shadowrocket VPN first:
```bash
用户需先手动开启 Shadowrocket VPN
noxinfluencer doctor  # Verify reachable
```

**⚠️ VPN conflicts with Tencent Docs:** After finishing NoxInfluencer work, disconnect VPN before uploading to Tencent Docs:
```bash
用户手动关闭 Shadowrocket VPN
mcporter auth tencent-docs  # Re-authenticate if needed
```
