# KOL 品类 × 产品场景映射指南

当需要为特定产品（如 OBSBOT Tiny 3 AI PTZ 摄像头）寻找合适的 KOL 时，应先将产品核心功能映射到 KOL 的内容场景。

## 产品功能 → KOL 场景映射

以 OBSBOT Tiny 3（AI 追踪 PTZ 摄像头）为例：

| 产品功能 | 对应 KOL 场景 | 推荐品类 | 推荐理由 |
|---------|--------------|---------|---------|
| AI 自动追踪 | 运动中/走动中需自动跟拍 | Sports / Fitness / Dance | 健身教练、舞者、瑜伽老师在示范时需要自动跟拍 |
| PTZ 远程控制 | 多机位无人值守拍摄 | Livestream / Camera | 直播主需要多角度切换，单人创作者需第二机位 |
| 高清视频 / 自动构图 | 远程会议、在线教学 | Tech / Education / Apple | 远程工作者、在线教师需要高质量会议体验 |
| 手势控制 | 录音棚/工作室免触碰操作 | Music / Studio | 音乐人在演奏时无法手动操控摄像头 |
| Webcam 即插即用 | 一般科技/生产力内容 | Content Creator / Desk Setup | 桌搭博主、生产力创作者展示工作流 |
| 高颜值设计 | 桌面美学展示 | Content Creator / Desk Setup | 桌搭博主、审美驱动的创作者 |

## 品类优先级矩阵（针对 AI PTZ 摄像头）

| 优先级 | 品类 | 典型 KOL | 推荐合作形式 | 预计价格 |
|:-------:|------|---------|------------|:-------:|
| ⭐⭐⭐ | Livestream | 直播设备评测/OBS教程 | Dedicated Review | $150-700 |
| ⭐⭐⭐ | Sports/Fitness | 健身教练/瑜伽老师 | Integration/演示 | $80-500 |
| ⭐⭐⭐ | Camera/Videography | 相机教程/多机位教学 | Tutorial/方案展示 | $200-700 |
| ⭐⭐ | Content Creator/Setup | 桌搭/Studio Tour | Integration/Setup Tour | $80-600 |
| ⭐⭐ | Music/Audio | 录音棚/音乐制作 | Behind-the-scenes | $120-500 |
| ⭐⭐ | Tech/3C | 科技产品评测 | Dedicated Review | $100-700 |
| ⭐ | Apple/Accessories | Mac/iPad配件评测 | Product Recommendation | $200-700 |
| ⭐ | Education | 在线教学/课程 | Tutorial/教学演示 | $80-400 |
| ⭐ | Gamer | 游戏Setup/外设 | Setup Tour/Integration | $200-900 |

## KOL 量级定义（按 YouTube 均播）

| 层级 | 均播范围 | NoxInfluencer 搜索参数 | 建议策略 |
|:----:|:--------:|:-----------------------|:--------:|
| Nano | < 10k | `--avg_view_min 2000 --avg_view_max 10000 --follower_max 30000` | 预算友好，UGC内容，可批量合作 |
| Mid-tier | 10k-30k | `--avg_view_min 10000 --avg_view_max 30000 --follower_max 100000` | 性价比最高，推荐主力 |
| Lower Macro | 30k-50k | `--avg_view_min 30000 --avg_view_max 50000 --follower_max 200000` | 品质较高，适合Dedicated Review |
| Macro | 50k-100k | `--avg_view_min 50000 --avg_view_max 100000 --follower_max 500000` | 预算充足时选择 |
| Elite | ≥ 100k | `--avg_view_min 100000` | 品牌曝光为主，预算较高 |

## NoxInfluencer 多品类并行搜索模板

```bash
# 模板：替换 <niche> 和 <country>
noxinfluencer creator search --platform youtube \
  --keywords '[<主关键词>,<次关键词1>,<次关键词2>]' \
  --country '[US,CA]' \
  --avg_view_min 3000 \
  --avg_view_max 50000 \
  --follower_min 3000 \
  --follower_max 150000 \
  --published_within_days 90 \
  --page_size 20 --lang zh
```

**典型搜索组合：**

| 品类 | keywords 参数 |
|------|--------------|
| Tech/3C | `'[webcam review,tech gadget,3C,camera review]'` |
| Livestream | `'[live streaming gear,stream setup,OBS tutorial,PTZ camera]'` |
| Desk Setup | `'[desk setup,studio tour,workspace tour,home office setup]'` |
| Fitness | `'[fitness training,home gym,yoga instructor,workout video]'` |
| Music | `'[music production,home studio,recording,guitar tutorial]'` |
| Apple | `'[apple accessories,mac setup,iphone accessories,macbook pro]'` |
| Camera | `'[camera review,photography tutorial,sony camera,fujifilm]'` |
