---
name: obsbot-kol-screening
description: OBSBOT KOL 筛选工作流 — NoxInfluencer 搜索 + YouTube API 三重验证 + 腾讯文档输出。包含 Post-Screening 补全流程（读取已有 Excel 表格、批量获取频道信息、填写分类和建议）。覆盖 Tech/Camera/Livestream/Apple/Gamer/Desk Setup 等品类。
version: 1.0.0
tags: [obsbot, kol, influencer, noxinfluencer, youtube, screening]
---

# OBSBOT KOL 筛选工作流

## 概述

通过 NoxInfluencer 搜索 + YouTube API 验证，筛选适合 OBSBOT 产品的中腰部 KOL。

## ⚠️ 执行纪律（用户明确要求）

1. **不要一步一停** — 用户多次强调"继续执行走，不要做一半的任务"。整个流程必须一口气跑完（搜索→验证→创建表格→写入），中间不要等用户指令。用户说"继续"是因为你停了——下次别停。
2. **开始前检查日期** — `date '+%Y-%m-%d %A'`，用当天日期命名文件。
3. **想尽办法去找** — 搜索不够就换关键词再来一轮，直到数量达标。
4. **用户市场** — 用户负责**北美市场（US/CA）**，除非明确指定其他地区。
5. **Daily Running 品类** — 用户明确指定的品类：YouTube（直播垂类、Apple类、桌搭类、科技类）+ Instagram（桌搭类）。

## 核心筛选标准

| 标准 | 要求 |
|:-----|:-----|
| **播放/粉丝比** | **优先找播放量高、粉丝少的 KOL（高性价比）** |
| 博主量级 | 中腰部/nano，不要 Top 级大博主 |
| 活跃度 | 3 个月内有更新，超过 3 个月直接筛掉 |
| OBSBOT 合作 | 已合作过的直接筛掉 |
| 竞品合作 | 重点关注竞品合作过但 OBSBOT 未合作的 |
| 邮箱 | 暂不获取 |
| **语言** | **只找英语类博主，欧洲/法语/西班牙语直接 pass，优先北美（US/CA）** |
| **国家限制** | **默认只找 US 和 CA，除非用户明确指定其他市场** |
| **Shorts** | **全是 Shorts 的频道直接过滤掉** |
| **游戏** | **全是游戏内容的频道直接过滤掉** |
| **官号** | **产品官号不要收录（Reolink、Sling Pilot Academy 等）** |
| **安防** | **安防摄像头类不要收录** |
| **偏离主题** | **野生动物/天气/航空/无人画面直播等偏离主题的不要** |
| **视频数** | **视频数 < 10 的频道直接过滤** |
| **播放/粉丝比** | **优先找播放量高、粉丝少的 KOL（高性价比）** |
| **教会频道** | **教会频道本身不是目标，要找设备评测博主** |
| **Talent 产品** | **找设备评测/教程博主，不是终端用户（教会/活动频道本身不要）** |

## CPM 定价模型（2026-06-15 新增）

用户提供了完整 CPM 参考表，按品类×产品×格式定价。**不再按粉丝量简单估算价格**。

### CPM 基准参考（含产品成本）

| 品类 | 专题 Webcam | 专题 Camera | 插播 Webcam | 插播 Camera | IG Webcam | IG Camera | TT Webcam | TT Camera |
|:-----|:-----------|:-----------|:-----------|:-----------|:----------|:----------|:----------|:----------|
| Tech | $60 | $110 | $50 | / | $20 | / | $20 | / |
| Apple | $50 | / | $42 | / | $20 | / | $20 | / |
| Gamer | $50 | / | $35 | / | $20 | / | $20 | / |
| Desk Setup | $30 | / | $80 | / | $20 | / | / | / |
| Livestream | $100 | $115 | $250 | / | / | / | / | / |
| Game Recording | $30 | / | $17 | / | / | / | / | / |
| Content Creator | $37 | $100 | $58 | / | / | $100 | / | $100 |
| Camera | / | $125 | / | / | / | / | / | / |

### 计算公式

```
合作价格 = 预估播放量 × CPM / 1000
```

- **低于基准值 20%** = 加分（性价比高）
- **超过基准值 20%** = 上线价格（可接受但不加分）
- **视频溢出率** = 实际播放/预期播放，用于评估是否值得续约

### 使用方法

1. 确定 KOL 的品类（Tech/Apple/Gamer 等）
2. 确定合作形式（专题/插播/IG/TT）
3. 确定产品类型（Webcam/Camera）
4. 查表获取 CPM 基准值
5. 用 KOL 的均播 × CPM / 1000 计算建议价格
6. 与 KOL 报价对比，判断是否在合理范围

### OBSBOT 产品分类

| 产品 | 类型 |
|:-----|:-----|
| Tiny 3 / Tiny 3 Lite / Tiny 2 | Webcam |
| Tail 2 / Tail Air | Camera |
| Meet 2 / Meet SE | Webcam |
| Talent 2 | Camera |
| Tiny SE | Webcam |

## 执行风格（用户明确要求）

- **不要一步一停** — 搜索→验证→创建表格→写入，一气呵成，不要等用户说"继续"
- **每次开始前检查日期** — `date '+%Y-%m-%d %A'` 确认今天日期
- **一天至少 50 个合格 KOL** — 因为用户审核会淘汰一部分，所以要多找

## 用户黑名单（不合格 KOL）

以下 KOL 已确认不合格，永久排除：

| KOL | 不合格原因 |
|:-----|:-----|
| Coast Cams | 内容偏离 |
| Reolink | 官号 |
| DaizeDreams | 全是 Shorts |
| Milktea Emma | 全是 Shorts |
| ToolBox BD | 安防摄像头 |
| Nightfury | 视频少，定位不明确 |
| Eddie's DL | 偏游戏 |
| Big Bear Live Stream | 严重偏离主题，无人画面 |
| HASIBxBRO | 纯游戏 |
| PTZtv | 内容不合格 |
| DWDderWetterdienst | 内容不合格（天气） |
| WEBCAM NEPAL LIVE | 内容不合格 |
| Sling Pilot Academy | 官号 |
| Scottish Wildlife Trust | 内容不合格（野生动物） |
| EGE – Gesellschaft | 内容不合格 |
| Sugarloaf | 画像严重偏差 |
| Alex Explorer - Scotventure | 画像严重偏差 |
| VISIONPLUS TV RDC | 法语频道 |
| 安防摄像头 | **不要收录**（security、surveillance、cctv、alarm） |
| 纯 Shorts | **过滤掉**（频道只发短视频的） |
| 纯游戏 | **过滤掉**（4/5 视频为游戏内容的） |
| Vlog 类型 | **谨慎选择**（标记但不排除，审核时注意） |
| 邮箱 | 暂不获取 |

## 完整流程（5 步）

### Step 1: NoxInfluencer 搜索

```bash
# 确保 VPN 连接
scutil --nc start "Shadowrocket"
noxinfluencer doctor  # 确认 ok

# 搜索模板（优先高播放/低粉丝比，仅北美）
noxinfluencer creator search \
  --platform youtube \
  --keywords '[关键词1,关键词2]' \
  --country '[US,CA]' \
  --avg_view_min 10000 --avg_view_max 50000 \
  --follower_min 3000 --follower_max 80000 \
  --published_within_days 90 \
  --page_size 15 --lang en
```

**搜索参数说明：**
- `--country '[US,CA]'` — **只找北美博主**（用户明确要求）
- `avg_view_min 10000` — 均播 ≥ 10K，确保内容有足够曝光
- `avg_view_max 50000` — 均播 ≤ 50K，避免头部 KOL（价格高）
- `follower_min 3000` — 粉丝 ≥ 3K，确保是真正的 KOL
- `follower_max 80000` — 粉丝 ≤ 80K，优先中腰部（高播放/粉丝比）

**注意**：除非用户明确指定其他市场（如欧洲、北欧），否则默认只搜 US 和 CA。

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

> **配额优化**：使用 `~/.hermes/scripts/yt_optimizer.py`，每个频道从 300 单位降至 2 单位（节省 99%）。

```python
import sys
sys.path.insert(0, str(Path.home() / '.hermes' / 'scripts'))
from yt_optimizer import api_call, get_channel_uploads

# 验证 1: 活跃度（channels.list = 1 单位，代替 search.list 100 单位）
ch = api_call("channels", {"id": "UC...", "part": "snippet,statistics"}, cost=1)

# 验证 2: 最近视频（playlistItems.list = 1 单位，代替 search.list 100 单位）
uploads = get_channel_uploads("UC...")
# 检查最新视频的 publishedAt 是否在 90 天内

# 验证 3: OBSBOT/竞品合作（search.list = 100 单位，带缓存）
obsbot_check = api_call("search", {
    "channelId": "UC...",
    "q": "obsbot OR tiny 3 OR tiny 2 OR tail 2 OR meet 2",
    "type": "video", "part": "snippet", "maxResults": "5"
}, cost=100, ttl=86400)  # 24h 缓存
```

传统方式：300 单位/频道 → 优化方式：2 单位/频道（search 带缓存后更低）。

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

### Step 5: 写入腾讯文档（严格去重）

**⚠️ 只写全新 KOL，不写入已存在的。必须在写入前检查去重。**

```python
# 1. 读取已存在的 KOL
existing = set()
r = subprocess.run(['mcporter','call','tencent-docs','smartsheet.list_records','--args',
    json.dumps({"file_id":file_id,"sheet_id":sheet_id})], capture_output=True, text=True, timeout=30)
for rec in json.loads(r.stdout).get('records',[]):
    for fv in rec.get('field_values',[]):
        if fv.get('field') == 'KOL ID':
            existing.add(fv.get('text_value',{}).get('items',[{}])[0].get('text','').strip().lower())

# 2. 只添加不存在的 KOL
for c in kols:
    nick = c.get('nickname','').lower()
    if nick in existing: continue  # ← 跳过已存在的
    # ... 添加记录 ...

# 3. 写入完成后去重
recs = json.loads(r.stdout).get('records',[])
seen = {}
dupes = []
for rec in recs:
    nick = ''
    for fv in rec.get('field_values',[]):
        if fv.get('field') == 'KOL ID':
            nick = fv.get('text_value',{}).get('items',[{}])[0].get('text','').strip()
    if nick in seen: dupes.append(rec['record_id'])
    else: seen[nick] = nick
if dupes:
    mcporter call tencent-docs smartsheet.delete_records --args '{"file_id":"FID","sheet_id":"SID","record_ids":DUPES}'
```

### VPN 开关规则

| 操作 | VPN | 原因 |
|:-----|:----|:-----|
| NoxInfluencer 搜索 | **ON** | API 在 GFW 外 |
| mcporter 写入腾讯文档 | **OFF** | VPN 会导致 TLS 断开 |
| YouTube API 验证 | **OFF** | 直连更快 |
| 获取 NoxInfluencer profile | **ON** | 同上 |

## 品类搜索关键词

### Tiny 3 / Tiny 3 Lite 专属关键词

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

### Talent 2 专属关键词

| 品类 | NoxInfluencer keywords | 定位 |
|:-----|:----------------------|:-----|
| ATEM Review | `ATEM Mini review,ATEM switcher review,Blackmagic ATEM` | 视频切换设备评测 |
| Live Equipment | `live streaming equipment review,streaming gear review` | 直播设备评测 |
| Multicam Tutorial | `multicam setup tutorial,multi camera live,live switching` | 多机位教程 |
| Church Tech | `church tech setup,church AV,live stream church equipment` | 教会技术（设备评测类，非终端用户） |
| Event Video | `event videography,multi camera event,wedding videography` | 活动拍摄 |
| PTZ Review | `PTZ camera review,PTZ camera tutorial,tracking camera` | PTZ 摄像头评测 |
| Broadcast Tech | `broadcast equipment review,professional video gear` | 广播设备评测 |
| Video Mixer | `video mixer review,video mixer tutorial,HDMI switcher` | 视频混合器评测 |
| Camera Control | `camera control software,remote camera control,NDI camera` | 摄像机控制 |
| Music Live | `live music production,concert live stream equipment` | 音乐直播设备 |

**搜索关键词应聚焦设备评测，不是终端场景：**
- ✅ `ATEM Mini review, video switcher review, multicam setup tutorial`
- ❌ `church streaming, worship live stream, event production`

**语言要求：只找英语区博主（US/CA/UK/AU），欧洲/法语/西班牙语直接 pass。**

### Talent 产品专属关键词

| 品类 | NoxInfluencer keywords | 定位 |
|:-----|:----------------------|:-----|
| ATEM Review | `ATEM Mini review,ATEM switcher review,Blackmagic ATEM` | 视频切换设备评测 |
| Live Equipment | `live streaming equipment review,streaming gear review` | 直播设备评测 |
| Multicam Tutorial | `multicam setup tutorial,multi camera live,live switching` | 多机位教程 |
| OBS Tutorial | `OBS tutorial,streaming software tutorial,live stream setup` | 直播软件教程 |
| Event Video | `event videography,multi camera event,wedding videography` | 活动拍摄 |
| PTZ Review | `PTZ camera review,PTZ camera tutorial,tracking camera` | PTZ摄像头评测 |
| Broadcast Tech | `broadcast equipment review,professional video gear` | 广播设备评测 |
| Video Mixer | `video mixer review,video mixer tutorial,HDMI switcher` | 视频混合器评测 |
| Stream Encoder | `streaming encoder review,capture card review` | 推流设备评测 |
| Camera Control | `camera control software,remote camera control,NDI camera` | 摄像机控制 |

⚠️ **Talent 筛选关键教训**：
- **不要找终端用户**（如教会频道本身）→ 要找**做设备评测/教程的专业博主**
- **教会频道不是目标** → 教会技术志愿者分享 setup 知识的才是目标
- **优先 ATEM/vMix 评测博主** → 他们最可能对 Talent 多机位切换功能感兴趣

## 量级筛选参数

| 目标 | avg_view | follower |
|:-----|:---------|:---------|
| Nano | 2k-10k | 3k-30k |
| Mid-tier | 10k-30k | 30k-100k |
| Lower Macro | 30k-50k | 100k-200k |
| **推荐范围** | **2k-35k** | **3k-150k** |

## 价格估算（基于 CPM 模型）

详细 CPM 分析模型见 `references/cpm-analysis-model.md`。

### 产品价格

| 产品 | 价格 | 类型 | 推荐优先级 |
|:-----|:-----|:-----|:-----------|
| Tiny 3 Lite | $199 | Webcam | ⭐⭐⭐ 优先推荐 |
| Tiny 3 | $349 | Webcam | ⭐⭐ 次选 |
| Tail 2 | $499 | Camera | ⭐⭐ |
| Talent | $999 | Camera | ⭐ |

### 合作决策规则

| 条件 | 合作类型 | 说明 |
|:-----|:---------|:-----|
| 实际 CPM ≤ 加分 CPM | ✅ 付费合作 | 优秀 CPM，优先合作 |
| 加分 CPM < 实际 CPM ≤ 基准 CPM | ✅ 付费合作 | 良好 CPM，建议合作 |
| 基准 CPM < 实际 CPM ≤ 上线 CPM | ⚠️ 置换/付费 | CPM 偏高，可考虑置换 |
| 实际 CPM > 上线 CPM | ❌ 仅置换 | CPM 过高，建议仅置换产品 |

### CPM 基准表（专题视频 - Webcam）

| 品类 | 基准 CPM | 加分 CPM | 上线 CPM |
|:-----|:---------|:---------|:---------|
| Desk Setup | $30 | $24 | $45 |
| Game Recording | $30 | $24 | $55 |
| Content Creator | $37 | $30 | $57 |
| Apple | $50 | $40 | $76 |
| Gamer | $50 | $40 | $52 |
| Tech | $60 | $48 | $77 |
| Livestream | $100 | $80 | $115 |

### 产品选择策略

- **默认**: Tiny 3 Lite ($199) — 产品成本最低，CPM 最优
- **高均播 KOL (>30K)**: Tiny 3 ($349) — 均播高，产品成本占比低
- **Camera 类 KOL**: Tail 2 ($499) — Camera 品类基准 CPM 更高
- **直播类 KOL**: Talent ($999) — Livestream 基准 CPM $100-250

## CPM 模型（2026-06-15 新增）

### OBSBOT 产品价格

| 产品 | 价格 | 类型 |
|:-----|:-----|:-----|
| Tiny 3 | $349 | Webcam |
| Tiny 3 Lite | $199 | Webcam |
| Tiny 2 | $299 | Webcam |
| Meet 2 | $249 | Webcam |
| Tail 2 | $499 | Camera |
| Talent | $999 | Camera |

### CPM 计算公式

```
CPM = (合作价格 / 均播) × 1000
合作价格 = (基准CPM × 均播) / 1000
总成本 = 合作价格 + 产品成本
实际CPM = (总成本 / 均播) × 1000
```

### 基准 CPM 表（专题视频 - Webcam）

| 品类 | 基准CPM | 加分CPM(-20%) | 上线CPM | 溢出率 |
|:-----|:--------|:--------------|:--------|:-------|
| Tech | $60 | $48 | $77 | 70% |
| Apple | $50 | $40 | $76 | 70% |
| Gamer | $50 | $40 | $52 | 90% |
| Desk Setup | $30 | $24 | $45 | 70% |
| Livestream | $100 | $80 | $115 | 70% |
| Game Recording | $30 | $24 | $55 | 70% |
| Content Creator | $37 | $30 | $57 | 70% |
| Camera | $70 | $56 | $70 | 70% |

### 基准 CPM 表（插播视频 - Webcam）

| 品类 | 基准CPM | 加分CPM(-20%) | 上线CPM | 溢出率 |
|:-----|:--------|:--------------|:--------|:-------|
| Tech | $50 | $40 | $80 | 80% |
| Apple | $42 | $34 | $50 | 70% |
| Gamer | $35 | $28 | $50 | 90% |
| Desk Setup | $80 | $64 | $80 | 80% |
| Livestream | $250 | $200 | $250 | 70% |
| Game Recording | $17 | $14 | $23 | 100% |
| Content Creator | $58 | $46 | $58 | 70% |

### 基准 CPM 表（Instagram - Webcam）

| 品类 | 基准CPM | 加分CPM(-20%) | 上线CPM | 溢出率 |
|:-----|:--------|:--------------|:--------|:-------|
| Tech | $20 | $16 | $40 | 90% |
| Desk Setup | $20 | $16 | $44 | - |
| Gamer | $20 | $16 | $40 | 90% |

### 基准 CPM 表（TikTok - Webcam）

| 品类 | 基准CPM | 加分CPM(-20%) | 上线CPM | 溢出率 |
|:-----|:--------|:--------------|:--------|:-------|
| Tech | $20 | $16 | $40 | 90% |
| Gamer | $20 | $16 | $30 | 90% |

### Camera 类型 CPM（专题视频）

| 品类 | 基准CPM | 加分CPM(-20%) | 上线CPM | 溢出率 |
|:-----|:--------|:--------------|:--------|:-------|
| Tech | $110 | $88 | $120 | 70% |
| Livestream | $115 | $92 | $115 | 80% |
| Content Creator | $100 | $80 | $110 | 70% |
| Camera | $125 | $100 | $115 | 70% |

### CPM 优化策略

1. **优先 Desk Setup 品类** — 基准 CPM 最低（$30），性价比最高
2. **优先高均播 KOL** — 均播越高，产品成本占比越低，实际 CPM 越接近基准
3. **考虑 Tiny 3 Lite**（$199）— 产品成本低 43%，CPM 更容易达标
4. **Livestream 品类需谨慎** — 基准 CPM 最高（$100），但溢出率低（70%）
5. **Gamer 品类溢出率高**（90%）— 实际播放量可能超出预期

## 关键词列表

**OBSBOT 关键词**：`obsbot, tiny 3, tiny 2, tail 2, meet 2, talent, tiny 3 lite, meet se, tiny se`

**竞品关键词**：`insta360 link, elgato facecam, logitech brio, logitech streamcam, razer kiyo, insta360 link 2, huddly, meeting owl`

## ⚠️ 关键执行原则

**不要一步一停** — 用户明确要求连续执行，不要每步都等确认。用 todo 跟踪进度，一个 execute_code 块完成搜索→验证→写入全流程。只在真正需要用户输入时才停下。

### 官号过滤（自动排除）

**所有搜索结果在入库前必须过官号检测**。以下类型直接过滤：

```python
brand_patterns = [
    # 品牌/官方标识
    "official", "inc.", "systems", "corp", "ltd", "co.,",
    # 已知品牌官号
    "reolink", "nexigo", "hikvision", "nikon", "bose",  "acasis",
    "tp-link", "obsbot", "sling pilot", "anvil", "cable matters",
    # 教会/组织频道（非个人创作者）
    "ministries", "church", "tabernacle", "temple", "dwelling",
    "gesellschaft", "ege",
    # 机构/学校
    "sling pilot academy", "scottish wildlife trust",
    # 家具/仓储（非科技频道）
    "warehouse", "furniture",
    # 媒体/新闻
    "visionplus", "officiel", "inbroadcast",
    # 厂商频道
    "hoto", "sony | professional",
]
```

**检测规则**：
1. 检查 KOL 名称是否包含 brand_patterns 中任何关键词
2. 检查频道 URL 是否来自已知品牌域名
3. 检查频道描述是否包含 "official channel" / "brand page" 等标识
4. 检查视频内容是否主要为产品宣传（非独立评测）

### 活跃度过滤（自动排除 3 个月未更新）

**入库前必须验证最近更新日期**。超过 3 个月未更新的频道直接排除。

```python
from datetime import datetime, timedelta
cutoff = datetime.now() - timedelta(days=90)

# YouTube API search.list 检查最新视频日期
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CH_ID&type=video&maxResults=1&order=date&key=API_KEY"
# 检查 items[0].snippet.publishedAt 是否在 90 天内
```

**检测规则**：
1. YouTube 频道：通过 API 检查最新视频的 `publishedAt`
2. NoxInfluencer 已过滤 `published_within_days 90`
3. 如 API 调用失败（VPN 断开），跳过验证但标注 "⚠️ 未验证活跃度"

## 排除关键词列表

```python
brand_patterns = ["official", "inc.", "systems", "reolink", "nexigo", "hikvision", "nikon", "bose", "acasis", "tp-link", "obsbot", "sling pilot", "ege", "gesellschaft", "visionplus", "ministries", "church", "tabernacle", "temple"]
security_patterns = ["security", "surveillance", "cctv", "alarm", "reolink", "toolbox"]
offtopic_patterns = ["wildlife", "weather", "aviation", "pilot", "eulen", "sugarloaf", "scotventure", "nepal live", "live cam", "webcam live", "bear live"]
gaming_patterns = ["game", "gaming", "twitch", "fortnite", "minecraft", "valorant", "cod", "apex", "league of legends", "overwatch"]
euro_patterns = ["deutsch", "français", "español", "italiano", "português", "nederlands", "polski", "türk", "العربية", "한국어", "日本語", "中文"]
```

## YouTube API 验证规则

```python
# 1. 活跃度：3 个月未更新 → 排除
if (datetime.now() - last_date).days > 90: skip

# 2. 纯游戏：4/5 视频为游戏 → 排除
if gaming_count >= 4: skip

# 3. 纯 Shorts：4/5 视频含 #shorts → 排除
if shorts_count >= 4: skip

# 4. 偏离主题：3/5 视频含 off-topic 关键词 → 排除
if offtopic_count >= 3: skip

# 5. 视频太少：< 10 个视频 → 排除
if video_count < 10: skip

# 6. Vlog 类型：标记但不排除（需人工审核）
c['_is_vlog'] = vlog_count >= 3
```

## 已知坑

| 问题 | 解决方案 |
|:-----|:---------|
| NoxInfluencer 403/Cloudflare | VPN 断了，`scutil --nc start "Shadowrocket"` |
| mcporter add_records 超时 | 逐条添加（1 条/次），不要批量 |
| mcporter list_tables 失败 | 直接用 `sheet_id="t00i2h"`，跳过 list_tables |
| creator profile 命令失败 | 用 `shell_quote(cid)` 包裹 creator_id |
| 搜索结果无 channel_url | 必须单独调 `creator profile` 获取 |
| 重复 KOL 跨批次 | 维护全局 excluded_names set |
| mcporter auth 失败 (VPN 冲突) | VPN 连接时 mcporter auth 会失败（"fetch failed"/"SSE error"）。**必须先断开 VPN**：`scutil --nc stop "Shadowrocket"`，认证成功后再重连 VPN。mcporter 走腾讯文档直连，不经过代理。 |
| mcporter HTTP 405 / 连接错误 | mcporter 服务可能挂了或需要重新认证。先 `scutil --nc stop "Shadowrocket"` 断 VPN，再 `mcporter auth tencent-docs` 重新认证。 |
| NoxInfluencer content 命令失败 | `noxinfluencer creator content` 偶尔报 "Unexpected token '<'"（Cloudflare 拦截）。改用 YouTube API `search.list` 搜索频道内的 OBSBOT 相关视频。 |
| VPN 长任务断连 | 每 10 个 profile 查询后重连 VPN：`scutil --nc start "Shadowrocket"` + `sleep 5` |
| YouTube API 验证失败 | VPN 断了导致 curl 返回空。重连后重试。或跳过验证直接用 NoxInfluencer 数据 |
| mcporter move_file 超时 | timeout 设 60s，不要用默认 30s |
| 非英语频道混入 | 搜索时加 `--country '[US,CA,UK,AU]'`，过滤掉欧洲/法语/西班牙语频道 |
| mcporter smartsheet.list_tables 报 RPC invalid | `mcporter auth tencent-docs` 重新认证 |
| `--country` 和 `--keywords` 必须是 JSON 数组 | 字符串值会报 `Input should be a valid list`。正确格式：`--keywords '["a","b"]' --country '["FR"]'` |
| 重复 KOL 跨批次 | 维护全局 excluded_names set，每次新搜索前加载所有历史 JSON |
| 新 smartsheet 默认字段 | 有 5 个默认字段（单选/数字/日期/图片/文本），必须先删除再添加自定义字段 |
| NoxInfluencer VPN 长任务断连 | 每次 API 调用前检查，断了就重连。长搜索（50+ 创作者）中间会断 2-3 次 |
| profile 获取只有 36/91 成功 | NoxInfluencer creator search 返回的 ID 并非都能解析为 YouTube 频道，成功率约 40% |
| execute_code 没有 openpyxl | execute_code 的沙盒环境没有 openpyxl，必须用 terminal 执行 Python 脚本 |
| yt-dlp 批量获取频道信息超时 | yt-dlp 太慢（~30s/频道），批量处理会超时。改用 curl + YouTube 页面解析（~5s/频道） |
| Tavily 配额 | Tavily MCP 默认为 keyless 模式（有严格日限额 ~25-30 次）。**必须检查 config.yaml 中 tavilyApiKey 是否为真实 key**。配额耗尽后用 curl 直接调 REST API 绕过 MCP：`curl -s -X POST "https://api.tavily.com/search" -H "Authorization: Bearer $KEY" -d '{"query":"..."}'`。详见 tavily-python skill |
| delegate_task 超时 | 子代理 600s 超时。如果 Tavily 配额耗尽，子代理会反复重试直到超时。**第一次超时后检查 /tmp/kol_batchN.json 是否有部分数据；第二次超时后放弃委托，用 training knowledge + curl 直接调 Tavily REST API 补全** |
| IG handle 误匹配 | Tavily 返回的 IG 链接经常匹配到同名不同人（厨师/名人/完全不同的人）。**必须验证标题/内容包含目标人物名**才采信。短 handle（@p, @reel）直接过滤 |
| YT URL 带后缀 | 搜索结果的 YT URL 经常带 /videos, /playlists, /shorts, /about 后缀。**必须清洗后再写入 Excel** |
| 订阅数过期 | Tavily 搜索片段中的订阅数可能来自过期缓存（偏差可达 50-90%）。**必须做第二轮验证**，对所有有 YT 频道的 KOL 重新搜索确认 |
| Notes 语言 | **Leonardo 要求 Notes 必须写中文**。即使原始数据是英文也要翻译 |
| Google bot 检测 | 浏览器访问 Google 搜索会被拦截（CAPTCHA/sorry 页面）。用 Bing 或 DuckDuckGo 替代 |
| execute_code 无 openpyxl | execute_code 沙盒环境没有 openpyxl/pandas，必须用 terminal 执行 Python 脚本 |
| 跨平台 Excel 样式 | 用户期望绿色/橙色高亮区分已找到/未找到数据，方便快速识别空白项 |
| 邮箱误匹配 | Tavily 返回的邮箱经常是同名不同人（学者/志愿者/员工）。**必须做二次验证**：搜索 "姓名 + 邮箱" 确认匹配。大学/组织/品牌邮箱需额外警惕。实测 30 个邮箱中 6 个为误匹配（20%） |
| 邮箱搜索脚本 key 泄露 | Python 脚本中硬编码 API key 会被系统 censor（显示为 ***）。**必须用 grep 从 config.yaml 读取**：`cfg = subprocess.run(["grep", "tavilyApiKey", "~/.hermes/config.yaml"], ...).stdout` |
| Leonardo 要求可点击链接 | Excel 中社交链接必须是完整 URL（https://instagram.com/xxx/），不能只是 @xxx。URL 列设置蓝色下划线字体 + hyperlink |

## 输出文件位置

- **腾讯文档**：OBSBOT → 每日监测（folder_id: `DumZsGZJrwsf`）
- **本地临时**：`/tmp/kol_*.json`

## Cross-Platform KOL Research（跨平台调研）

当拿到一份已有 KOL 名单（Excel/表格），需要跨 YouTube/Instagram/X/TikTok/Google 等平台补充信息时使用此流程。

### 适用场景

- Leonardo 提供了一份 KOL 名单，需要补全频道链接、订阅数、社交账号、任职机构等
- 与 Post-Screening 的区别：Post-Screening 侧重 YouTube 频道分类和合作建议；Cross-Platform 侧重多平台信息发现

### 搜索优先级

| 优先级 | 工具 | 适用场景 | 注意事项 |
|:-------|:-----|:---------|:---------|
| 1 | Tavily MCP | 通用搜索 | 确认 config.yaml 中有真实 API Key（非占位符） |
| 2 | curl + Tavily REST API | MCP 配额耗尽或 keyless 模式 | 直接 `curl -X POST "https://api.tavily.com/search"` 绕过 MCP |
| 3 | 浏览器 Bing/DuckDuckGo | Tavily 完全不可用时 | Google 有 bot 检测，用 Bing |
| 4 | Training knowledge | 已知知名创作者 | MKBHD/iJustine/Casey Neistat 等头部创作者可直接填充 |
| 5 | Manual verification | 数据稀疏的 DP/Gaffer | 标记"需手动验证"，不要编造 |

### 并行分批策略

```
55 人 → 分 3 路 delegate_task（每路 ~18 人）
├── 每路独立搜索 + 写 JSON 到 /tmp/kol_batchN.json
├── 最后合并 → 生成 Excel
└── 超时处理：检查 /tmp/kol_batchN.json 是否有部分数据
```

**关键**：delegate_task 有 600s 超时。如果 Tavily 配额耗尽，子代理会反复重试直到超时。**第二次超时后应放弃委托，直接用 training knowledge 补全剩余数据。**

### Tavily 配额管理

- Tavily MCP **默认为 keyless 模式**，有严格日限额（~25-30 次搜索）。**必须检查 config.yaml 中 tavilyApiKey 是否为真实 key**
- 有 API Key 后无日限额，但 55 人 × 3-5 次搜索/人 = 165-275 次仍需注意并发
- **curl 直接调 REST API** 可绕过 MCP 连接限制，配额独立计算
- 策略：delegate_task 分 3 路并行 → 子代理用 Tavily MCP 搜索 → 配额耗尽后子代理自动降级到 training knowledge → 超时后主代理用 curl 补全

### Excel 输出格式

```python
# 列结构（扩展原始表格）
headers = [
    "First name", "Last name", "Type", "ROI",
    "YouTube Channel", "YouTube Subscribers",
    "Instagram", "X/Twitter", "TikTok",
    "Affiliation / Employment",
    "Notes"  # 合并原始备注 + 新增调研信息
]

# 样式
found_fill = PatternFill(start_color="E2EFDA")     # 绿色 = 找到数据
not_found_fill = PatternFill(start_color="FCE4D6")  # 橙色 = 未找到
header_fill = PatternFill(start_color="2F5496")      # 深蓝表头
```

**注意事项**：
- execute_code 沙盒没有 openpyxl/pandas，必须用 `terminal` 执行 Python
- Notes 列合并原始备注 + 新增信息，用 ` | ` 分隔
- 冻结首行 + 自动筛选，方便 Leonardo 过滤

### Email Discovery（邮箱搜索）

当拿到已有 KOL 名单需要补全邮箱时，使用 Tavily 搜索：

```python
import subprocess, json, re

cfg = subprocess.run(["grep", "tavilyApiKey", "~/.hermes/config.yaml"],
    capture_output=True, text=True).stdout
API_KEY=cfg.st...o extract_emails(text):
    return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

def search(q, n=3):
    r = subprocess.run(["curl", "-s", "-X", "POST", "https://api.tavily.com/search",
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer ***        "-d", json.dumps({"query": q, "max_results": n})],
        capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)

for kol in kol_list:
    fn, ln = kol['first_name'], kol['last_name']
    query = f'"{fn} {ln}" email contact'
    r = search(query, 3)
    for res in r.get("results", []):
        emails = extract_emails(res.get("content", ""))
        # Filter: check if email contains person's name
        name_parts = [fn.lower(), ln.lower()]
        for e in emails:
            if any(p in e.lower() for p in name_parts):
                kol['email'] = e
                break
```

**邮箱验证（必须步骤）**：搜索结果中经常出现同名不同人的邮箱。**必须做二次验证**：

```python
# 搜索 "姓名 + 邮箱" 确认匹配
r = search(f'"{name}" "{email}"', 2)
for res in r.get("results", []):
    if email in res.get("content", ""):
        name_parts = name.lower().split()
        if any(p in res["content"].lower() for p in name_parts):
            print(f"Verified: {email}")  # confirmed
```

**已知错误模式**：
- 大学邮箱（@yale.edu, @ucla.edu）经常匹配到同名学者
- 志愿者组织邮箱（@nynjtc.org）匹配到同名志愿者
- 时尚品牌邮箱（@loveshackfancy.com）匹配到同名员工
- 管理公司邮箱（@xxxmanagement.com）可能是经纪人而非本人

**过滤规则**：
```python
skip_patterns = ['example.com', 'test.com', 'noreply', 'no-reply',
                 'support@', 'info@google', 'help@', 'abuse@',
                 'privacy@', 'legal@']
```

**实测结果**（55人名单）：搜索到 30 个邮箱，验证后保留 24 个（20% 为误匹配）。

### Social Media URL Conversion（社交链接格式化）

**Leonardo 要求所有社交链接必须是可点击的完整 URL**，不能只是 @handle。

```python
def to_url(platform, handle):
    h = handle.lstrip('@')
    urls = {
        'yt': f"https://www.youtube.com/@{h}" if not h.startswith('c/') else f"https://www.youtube.com/{h}",
        'ig': f"https://www.instagram.com/{h}/",
        'x': f"https://x.com/{h}",
        'tk': f"https://www.tiktok.com/@{h}",
    }
    return urls.get(platform)

# Excel 中 URL 设置为超链接
from openpyxl.styles import Font
link_font = Font(color="0563C1", underline="single")
cell.font = link_font
cell.hyperlink = url
```

### 数据质量分层

| 层级 | 描述 | 处理方式 |
|:-----|:-----|:---------|
| Rich data | 头部创作者（MKBHD, iJustine, Casey Neistat 等） | 全平台信息齐全 |
| Good data | 中腰部有 YouTube 频道的 | YouTube + IG + 部分其他 |
| Partial data | 有 IG 但无 YT 的摄影师 | 标记已有信息 |
| Limited data | 专业 DP/Gaffer，公开信息少 | 标记"需手动验证" |

### 数据质量验证（必须步骤）

初次采集后**必须做一轮验证**，修正误匹配数据。以下是已知的高频错误模式：

#### Instagram Handle 误匹配

Tavily 搜索返回的 IG 链接经常匹配到**同名不同人**。必须验证：

| 错误模式 | 示例 | 验证方法 |
|:---------|:-----|:---------|
| 同名厨师/名人 | Tom Keller → @chefthomaskeller（厨师，不是DP） | 检查页面标题/内容是否提到 cinematographer/DP/photographer |
| 同名不同人 | Timm Brückner → @alexander.bruckner（完全不同的人） | 检查 first name 是否匹配 |
| 通用词误匹配 | Fred Johnny Hammerø → @_codyhammer_（hammer 误匹配） | 检查 full name 是否出现在标题中 |
| 短 handle 噪音 | @p, @reel, @stories, @explore, @accounts | 直接过滤掉长度 ≤ 2 的 handle |

**验证代码**：
```python
# 在搜索结果中，只有标题/内容包含目标人物名时才采信 IG handle
person_first = kol['first_name'].lower()
person_last = kol['last_name'].lower()
if person_first in (title+content).lower() or person_last in (title+content).lower():
    kol["instagram"] = "@" + ig_handle  # verified
```

#### YouTube URL 清洗

搜索结果的 YT URL 经常带后缀，必须清理：
```python
clean = url.split("?")[0].rstrip("/")
for suffix in ["/videos", "/playlists", "/shorts", "/about"]:
    if clean.endswith(suffix):
        clean = clean[:-len(suffix)]
```

#### 订阅数二次验证

初次采集的订阅数可能来自过期缓存。**必须做第二轮验证**：
```python
# 对所有有 YT 频道的 KOL，用 Tavily 搜 "youtube.com @handle subscribers" 验证
# 对比 expected vs actual，修正偏差 >20% 的数据
```

实际案例（2026-06-04）：
- Matthew Allard: 初始 ~200K → 实际 18.4K（偏差 91%）
- Justin Brown (PrimalVideo): 初始 ~4M → 实际 1.89M（偏差 53%）
- Bharat Bala: 初始 ~500K → 实际 329K（偏差 34%）
- Faruk Korkmaz: 初始 ~500K → 实际 633K（偏差 27%）

#### Notes 语言要求

**Leonardo 要求 Notes 必须写中文**。即使原始数据是英文，Notes 列也要翻译成中文。格式：
```
中文身份描述 | YT: @handle (订阅数) | IG: @handle | 其他平台 | 网站/机构
```

示例：
```
芬兰旅行电影人 | YT: @mattih (1.28M) | IG: @mattih | TravelFeels创始人 | 网站: mattihaapoja.com | 多伦多定居
```

## Post-Screening 补全流程

当拿到一个部分填写的 KOL 表格（如 Leonardo 手动筛选后需要补全剩余字段）时：

### Step 1: 识别待填写行

```python
import openpyxl
wb = openpyxl.load_workbook('path/to/file.xlsx')
ws = wb.active

need_fill = []
for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_col=15, values_only=True), start=2):
    if not row[7] and row[1]:  # H列(一级类目)为空且有KOL名称
        need_fill.append({'row': row_idx, 'kol_id': row[1], ...})
```

### Step 2: 批量获取 YouTube 频道信息

**优先级排序**（从快到慢）：
1. **curl + YouTube 页面解析**（最快，~5s/频道）— 直接抓取频道页面 HTML，解析嵌入的 JSON
2. **Tavily 搜索**（较快但有日限额）— 适合少量查询
3. **yt-dlp**（最慢，易超时）— 不推荐批量使用

```bash
# 推荐方式：curl 抓取频道页面
curl -s "https://www.youtube.com/channel/CHANNEL_ID" | grep -o '"channelMetadataRenderer":{[^}]*}' | head -1
```

**并行处理**：用 `delegate_task` 分 3 路并行，每路 6-7 个频道，总耗时约 3-5 分钟。

### Step 3: 填写字段

按照 Leonardo 的风格填写（详见 `references/leonardo-kol-writing-style.md`）：
- **一级类目**（H列）：Tech / Setup / Livestream / Camera / Content Creator / Gamer / Sports
- **二级类目**（I列）：3C / Setup / Desk Setup / Camera Settings / Photography 等
- **视频形式&内容**（J列）：简短描述，5-10字
- **合作平台**（K列）：youtube
- **合作建议**（L列）：1-2句话，提到博主特点和合作切入点

**不填写的列**：
- N列（审核人员意见）
- O列（建议合作价格）

### Step 4: 生成新文件

```python
# 保存为新文件，带 _filled 后缀
output_path = '原始文件名_filled.xlsx'
wb.save(output_path)
```

## Creator Deep Research（创作者深度调研）

当需要为**特定产品/活动**（如 Meet 3 粉色款、IP联名）寻找合作创作者时，使用深度调研流程。与常规筛选互补：筛选找候选人，深度调研评估具体合作适配度。

详见 `references/creator-deep-research-workflow.md`，包含：
- 四阶段流程（框架→筛选→分析→产出）
- 6维度博主分析模板
- 评论区用户需求金字塔
- 评估矩阵维度定义
- Word报告生成技巧
- 创意Brief模板

## 参考文件
## 参考文件

- `references/campaign-plan-2026.md` — OBSBOT KOL 营销作战计划（2026年6-8月），含 Talent 2 上市、Daily Running、欧洲/北欧市场、品牌大使完整计划
- `references/cpm-analysis-model.md` — CPM 分析模型（产品价格、基准表、合作决策规则、品类优先级）
- `references/2026-h2-campaign-plan.md` — 2026 H2 营销作战计划（Talent 2 上市 7.29、Daily Running、欧洲/北欧市场、BA 计划、Micro Center 渠道）
- `references/daily-running-campaign-plan.md` — Daily Running 营销计划（2026年6-8月），含品类结构、预算、CPM基准、决策矩阵
- `references/creator-deep-research-workflow.md` — 创作者深度调研方法论（多平台搜索+分析+Word报告）
- `references/leonardo-kol-writing-style.md` — Leonardo 的 KOL 评价风格指南
- `references/youtube-channel-scraping.md` — YouTube 频道信息抓取技术方案
- `references/tournament-kol-research.md` — 赛事关联 KOL 研究方法论（EWC/VCT 等赛事赞助场景）
- `noxinfluencer/references/obsbot-kol-sourcing-workflow.md` — 完整品类映射和排除流程
- `noxinfluencer/references/search-filters.md` — 搜索过滤器语义
- `noxinfluencer/references/kcl-product-scenario-mapping.md` — 产品场景→KOL品类映射
- `noxinfluencer/references/validated-search-niches.md` — 2026-05-29 验证的 15 个搜索品类及有效性
- `noxinfluencer/references/mcporter-smartsheet-pitfalls.md` — mcporter 写入注意事项
