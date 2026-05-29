# 已验证的 KOL 偏好模式（2026-05-28 美洲市场V3经验）

## 用户从 V2 保留的 12 个 KOL（已验证偏好样本）

这些是用户从 39 个中腰部 KOL 中选出的，反映了真实偏好：

| KOL | 粉丝 | 均播 | 互动率 | 品类 |
|:----|:----:|:----:|:-----:|:----:|
| Rjey Tech | 78.9k | 9.7k | 1.68% | Tech/3C |
| TonyTechBytes | 64.9k | **38.8k** | 3.16% | Tech/PC Build |
| securitybros | 35.6k | 2.1k | 0.92% | Tech/Gadget |
| Kyler Steele | 62.5k | 6.4k | 1.80% | Camera |
| Jessie's Flying | 34k | **34.9k** | 2.58% | Apple/Mac |
| GivemChills | 137k | 21.6k | 4.47% | Gamer/Gear |
| GutzyAiden | 132k | 18.9k | 3.79% | Gamer/Setup |
| Andrew Chapman Creative | 47k | 21.5k | 4.75% | Music/Studio |
| JHawk | 111k | 5.5k | 4.84% | Apple/Office |
| Craig Neidel | 68k | 11.5k | **5.81%** | Apple配件 |
| Tausif Hussain | 127k | 20.4k | 3.39% | Apple/News |
| astronuggie | 48.8k | 8.7k | **5.13%** | Setup/Gaming |

### 偏好特征总结
- **粉丝范围**: 34k ~ 137k，中位数 ~70k
- **均播范围**: 2k ~ 38k，中位数 ~15k
- **品类偏好**: 多样性（Tech/Camera/Apple/Gamer/Music 全都有）
- **❌ 不要选**: Elite（均播≥50k或粉丝≥150k）
- **✅ 首选**: Mid-tier（均播10k-30k）/ Nano（均播<10k），可加少量 Lower Macro（30k-50k）

## NoxInfluencer 已验证可行的搜索组合

### Tech/3C（1247 命中）
```bash
--keywords '[tech review,gadget review,3C,smartphone review]'
--avg_view_min 3000 --avg_view_max 60000 --follower_max 150000 --published_within_days 90
```

### Livestream/Streaming（190 命中，较精准）
```bash
--keywords '[live streaming tutorial,stream gear review,OBS studio]'
--avg_view_min 3000 --avg_view_max 40000 --follower_max 150000 --published_within_days 90
```

### 健身/运动（1602 命中）
```bash
--keywords '[home gym,fitness training,workout video,yoga instructor]'
--avg_view_min 3000 --avg_view_max 40000 --follower_max 150000 --published_within_days 90
```

### 墨西哥市场（2626 命中）
```bash
--keywords '[tecnologia,review gadgets,productos tecnologicos,reseña]'
--country '[MX]' --avg_view_min 1000 --avg_view_max 50000 --follower_max 150000
```

### 远程办公/教育（1304 命中）
```bash
--keywords '[online teaching,remote work,hybrid work,webcam setup]'
--avg_view_min 3000 --avg_view_max 40000 --follower_max 150000 --published_within_days 90
```

### VTuber 赛道（2026-05 新发现）
```bash
--keywords '[vtuber,vtube studio,streaming tutorial,OBS]'
```
发现 Phlox Labs（46.2k, 12.33% eng）— VTuber 是 AI 追踪摄像头的隐藏刚需市场。

## NoxInfluencer GFW 恢复

```
Error: Request failed: fetch failed
→ scutil --nc start Shadowrocket（需手动在app里选节点）
→ 重试 → 完成后 scutil --nc stop Shadowrocket
备用：用之前搜索结果的数据
```
