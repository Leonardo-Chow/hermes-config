# OBSBOT KOL 资源开发工作流

## 数据源

| 文件 | 用途 | 位置 |
|:-----|:-----|:-----|
| **Tiny 3 & Lite KOL(1).xlsx** | 已合作博主排除名单（~172 唯一 KOL） | Downloads |
| **Leonardo的 KOL资源开发.xlsx** | 模板格式 + 已有半完成 KOL | Downloads |
| **KOL筛选标准** (IMA笔记) | 量级定义、品类分类、市场规则 | Leonardo知识库 |

## 模板格式（16 列）

生成表格时必须包含以下字段，最后 1 列（@审核人员）留空：

1. 产品（固定 `Tiny 3& Tiny 3 Lite`）
2. KOL ID（频道显示名）
3. 邮箱（可空，用户自己补）
4. 频道链接（完整 YouTube 链接）
5. 受众国家（美国/加拿大/墨西哥）
6. 粉丝量（k）（如 `127k`）
7. 量级（k）（视频均播）
8. 互动率（百分比）
9. 网红类型-一级类目
10. 网红类型-二级类目
11. 视频形式&内容
12. 合作平台（固定 `youtube`）
13. 建议合作价格
14. 是否建议合作及理由（必须填写，不能空）
15. 筛选时间
16. @审核人员：是否合格&反馈意见（留空）

## 排除流程

```python
# 从 Tiny 3 & Lite KOL(1).xlsx 提取所有已合作 KOL ID
import openpyxl
wb = openpyxl.load_workbook('/path/to/Tiny 3 & Lite KOL(1).xlsx')
ws = wb['网红信息表']
excluded = set()
for row in ws.iter_rows(min_row=3, values_only=True):
    name = str(row[2]).strip() if row[2] else ''
    if name and name != 'None':
        excluded.add(name.lower())
# 对每个候选 KOL: candidate.lower() in excluded → 排除
```

## 品类搜索优先级（针对 PTZ/AI 追踪摄像头）

| 优先级 | 品类 | NoxInfluencer keywords | 合作理由 |
|:-------:|------|------------------------|---------|
| ⭐⭐⭐ | Livestream | `'[live streaming,stream setup,OBS tutorial,PTZ camera]'` | PTZ 最直接需求 |
| ⭐⭐⭐ | Sports/Fitness | `'[fitness training,home gym,yoga instructor,workout]'` | AI 追踪核心场景 |
| ⭐⭐⭐ | Camera | `'[camera review,photography tutorial,multicam,sony]'` | 多机位教学 |
| ⭐⭐ | Tech/3C | `'[tech review,gadget review,webcam,3C,smartphone]'` | 科技产品评测 |
| ⭐⭐ | Content Creator/Setup | `'[desk setup,workspace tour,home office,studio]'` | 桌搭/工作室 |
| ⭐⭐ | Music/Audio | `'[music production,home studio,recording,guitar]'` | 录音棚多机位 |
| ⭐⭐ | Apple | `'[apple accessories,mac setup,ipad,iphone]'` | Apple 生态配件 |
| ⭐ | Gaming | `'[gaming setup,gaming gear,game peripherals,streamer]'` | 游戏房 Setup |
| ⭐ | Education | `'[online teaching,tutorial,classroom,homeschool]'` | 教学演示/远程 |

## NoxInfluencer 量级筛选参数

| 目标 | avg_view | follower | 
|:----|:---------|:---------|
| Nano | 2k - 10k | 3k - 30k |
| Mid-tier | 10k - 30k | 30k - 100k |
| Lower Macro | 30k - 50k | 100k - 200k |
| 中腰部综合 | 3k - 50k | 3k - 150k |

## YouTube API 三重验证流程（2026-05-29 新增）

NoxInfluencer 搜索结果只提供基础指标。入库前必须用 YouTube Data API 做三重验证：

### Step 1: 获取频道 ID
NoxInfluencer `creator search` 结果不含 `channel_url`，需单独调 `creator profile`：
```python
for creator in search_results:
    r = terminal(f'noxinfluencer creator profile {shell_quote(creator["id"])} --json 2>&1', timeout=30)
    d = json.loads(r['output'])
    creator['channel_url'] = d['data']['channel_url']
    # 从 social_media 中提取 YouTube channel_id
```

### Step 2: 活跃度验证（3 个月）
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CHANNEL_ID&type=video&maxResults=1&order=date&key=API_KEY"
# 检查 publishedAt 是否在 90 天内
```

### Step 3: OBSBOT 合作历史检查
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CHANNEL_ID&q=obsbot+webcam+camera&type=video&maxResults=5&order=date&key=API_KEY"
# 搜索标题中包含 obsbot/tiny 3/tiny 2/tail 2/meet 2/talent 的视频
# 如果找到 → 排除（已合作过）
```

### Step 4: 竞品合作历史检查
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CHANNEL_ID&q=insta360+OR+elgato+OR+logitech+webcam&type=video&maxResults=5&order=date&key=API_KEY"
# 搜索标题中包含 insta360 link/elgato facecam/logitech brio 等竞品关键词
# 如果找到 → 标记为"有竞品合作"（优先级更高）
```

### 关键词列表
OBSBOT 关键词：`obsbot, tiny 3, tiny 2, tail 2, meet 2, talent, tiny 3 lite, meet se, tiny se`
竞品关键词：`insta360 link, elgato facecam, logitech brio, logitech streamcam, razer kiyo, insta360 link 2, huddly, meeting owl`

### YouTube API Key
`YOUR_YOUTUBE_API_KEY`

## 输出文件管理

- 每次生成新版本时**递增版本号**（V1, V2, V3）
- 文件名格式：`Leonardo的 KOL资源开发_美洲市场中腰部_V{数字}_YYYYMMDD.xlsx`
- 上传到腾讯文档 OBSBOT 文件夹（folder_id: `DjbGtzenXmbX`）
- **上传前删除同一版本号的旧文件**，避免堆积
- 腾讯文档上传流程：`import_file.sh` → `manage.async_import` → `manage.move_file`
