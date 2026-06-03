---
name: obsbot-kol-screening
description: OBSBOT KOL 筛选工作流 — NoxInfluencer 搜索 + YouTube API 三重验证 + 腾讯文档输出。排除已合作博主，优先竞品合作过的。覆盖 Tech/Camera/Livestream/Apple/Gamer/Desk Setup 等品类。
version: 1.0.0
tags: [obsbot, kol, influencer, noxinfluencer, youtube, screening]
---

# OBSBOT KOL 筛选工作流

## 概述

通过 NoxInfluencer 搜索 + YouTube API 验证，筛选适合 OBSBOT 产品的中腰部 KOL。

## 核心筛选标准

| 标准 | 要求 |
|:-----|:-----|
| 博主量级 | 中腰部/nano，不要 Top 级大博主 |
| 活跃度 | 3 个月内有更新，超过 3 个月直接筛掉 |
| OBSBOT 合作 | 已合作过的直接筛掉 |
| 竞品合作 | 重点关注竞品合作过但 OBSBOT 未合作的 |
| 邮箱 | 暂不获取 |

## 完整流程（5 步）

### Step 1: NoxInfluencer 搜索

```bash
# 确保 VPN 连接
scutil --nc start "Shadowrocket"
noxinfluencer doctor  # 确认 ok

# 搜索模板
noxinfluencer creator search \
  --platform youtube \
  --keywords '[关键词1,关键词2]' \
  --country '[US,CA,UK,AU]' \
  --avg_view_min 2000 --avg_view_max 35000 \
  --follower_min 3000 --follower_max 150000 \
  --published_within_days 90 \
  --page_size 15 --lang en
```

### Step 2: 获取频道 URL

NoxInfluencer search 结果不含 channel_url，需单独调 profile：

```python
from hermes_tools import terminal, shell_quote
for creator in search_results:
    r = terminal(f'noxinfluencer creator profile {shell_quote(creator["id"])} --json 2>&1', timeout=30)
    d = json.loads(r['output'])
    if d.get('success'):
        creator['channel_url'] = d['data'].get('channel_url','')
        # 从 social_media 提取 yt_channel_id
```

⚠️ **关键**：creator_id 必须用 `shell_quote()` 包裹，否则特殊字符会导致命令失败。

### Step 3: YouTube API 三重验证

```python
API_KEY = "YOUR_YOUTUBE_API_KEY"

# 验证 1: 活跃度（3 个月）
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CH_ID&type=video&maxResults=1&order=date&key=API_KEY"
# 检查 publishedAt 是否在 90 天内

# 验证 2: OBSBOT 合作历史
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CH_ID&q=obsbot+webcam&type=video&maxResults=5&order=date&key=API_KEY"
# 标题包含 obsbot/tiny 3/tiny 2/tail 2/meet 2/talent → 排除

# 验证 3: 竞品合作历史
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CH_ID&q=insta360+OR+elgato+OR+logitech+webcam&type=video&maxResults=5&order=date&key=API_KEY"
# 标题包含 insta360 link/elgato facecam/logitech brio → 标记为竞品合作
```

### Step 4: 排除已筛选 KOL

维护一个 excluded_names set，包含所有历史筛选过的 KOL 名称（小写）。每次新搜索前加载：

```python
excluded_names = set()
# 从历史 JSON 文件加载
for file in ['kol_verified_final.json', 'kol_final_40.json', 'kol_round3_verified.json']:
    try:
        with open(f'/tmp/{file}') as f:
            for c in json.load(f):
                excluded_names.add(c.get('nickname','').strip().lower())
    except: pass
```

### Step 5: 写入腾讯文档

```python
# 创建 smartsheet
mcporter call tencent-docs manage.create_file --args '{"title":"KOL筛选M月D日 vN","file_type":"smartsheet"}'

# 添加 14 列字段（产品/KOL ID/频道链接/受众国家/粉丝量K/量级/互动率/一级类目/二级类目/视频形式/平台/建议价格/建议理由/筛选时间）

# 逐条添加记录（不要批量，mcporter 会超时）
for rec in records:
    mcporter call tencent-docs smartsheet.add_records --args '{"file_id":"FID","sheet_id":"SID","records":[rec]}'
    time.sleep(0.3)

# 移动到 OBSBOT → 每日监测 文件夹
mcporter call tencent-docs manage.move_file --args '{"file_id":"FID","target_folder_id":"DumZsGZJrwsf"}'
```

## 品类搜索关键词

| 品类 | NoxInfluencer keywords | 定位 |
|:-----|:----------------------|:-----|
| Tech 3C | `webcam review,4K webcam,PTZ camera` | 摄像头评测 |
| Camera | `camera review,videography,filmmaking` | 摄影/多机位 |
| Livestream | `live streaming,stream setup,OBS tutorial` | 直播设备 |
| Apple | `MacBook accessories,Apple setup,Mac review` | Mac 外接摄像头 |
| Desk Setup | `desk setup,room tour,studio tour` | 桌搭展示 |
| Gamer | `gaming webcam,streaming camera,game setup` | 游戏直播 |
| Video Call | `video conferencing,webcam comparison,best webcam` | 远程办公 |
| Home Office | `home office setup,work from home,productivity` | 办公 Setup |
| Podcast/Audio | `podcast setup,home studio,microphone review` | 录音棚多机位 |
| Streaming Gear | `streaming setup,stream gear,obs setup` | 直播设备 |

## 量级筛选参数

| 目标 | avg_view | follower |
|:-----|:---------|:---------|
| Nano | 2k-10k | 3k-30k |
| Mid-tier | 10k-30k | 30k-100k |
| Lower Macro | 30k-50k | 100k-200k |
| **推荐范围** | **2k-35k** | **3k-150k** |

## 价格估算

| 粉丝量 | 建议价格 |
|:-------|:---------|
| <30K | $100-$200 |
| 30K-80K | $200-$400 |
| 80K-150K | $400-$700 |
| >150K | $700-$1,200 |

## 关键词列表

**OBSBOT 关键词**：`obsbot, tiny 3, tiny 2, tail 2, meet 2, talent, tiny 3 lite, meet se, tiny se`

**竞品关键词**：`insta360 link, elgato facecam, logitech brio, logitech streamcam, razer kiyo, insta360 link 2, huddly, meeting owl`

## ⚠️ 关键执行原则

**不要一步一停** — 用户明确要求连续执行，不要每步都等确认。用 todo 跟踪进度，一个 execute_code 块完成搜索→验证→写入全流程。只在真正需要用户输入时才停下。

## 已知坑

| 问题 | 解决方案 |
|:-----|:---------|
| NoxInfluencer 403/Cloudflare | VPN 断了，`scutil --nc start "Shadowrocket"` |
| mcporter add_records 超时 | **逐条添加**（1 条/次），timeout 设 60s，间隔 0.3s。批量必然超时 |
| creator profile 命令失败 | 用 `shell_quote(cid)` 包裹 creator_id，特殊字符会导致命令失败 |
| 搜索结果无 channel_url | 必须单独调 `creator profile` 获取，search 结果只有 NoxInfluencer 内部 ID |
| 重复 KOL 跨批次 | 维护全局 excluded_names set，每次新搜索前加载所有历史 JSON |
| 新 smartsheet 默认字段 | 有 5 个默认字段（单选/数字/日期/图片/文本），必须先删除再添加自定义字段 |
| NoxInfluencer VPN 长任务断连 | 每次 API 调用前检查，断了就重连。长搜索（50+ 创作者）中间会断 2-3 次 |
| profile 获取只有 36/91 成功 | NoxInfluencer creator search 返回的 ID 并非都能解析为 YouTube 频道，成功率约 40% |

## 输出文件位置

- **腾讯文档**：OBSBOT → 每日监测（folder_id: `DumZsGZJrwsf`）
- **本地临时**：`/tmp/kol_*.json`

## 参考文件

- `noxinfluencer/references/obsbot-kol-sourcing-workflow.md` — 完整品类映射和排除流程
- `noxinfluencer/references/search-filters.md` — 搜索过滤器语义
- `noxinfluencer/references/kcl-product-scenario-mapping.md` — 产品场景→KOL品类映射
- `noxinfluencer/references/validated-search-niches.md` — 2026-05-29 验证的 15 个搜索品类及有效性
- `noxinfluencer/references/mcporter-smartsheet-pitfalls.md` — mcporter 写入注意事项
