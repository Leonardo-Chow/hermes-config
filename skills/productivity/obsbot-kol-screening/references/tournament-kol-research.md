# 赛事关联 KOL 研究方法论

当 OBSBOT 成为某赛事官方赞助商时，需要系统化筛选该赛事关联的 KOL。以下方法论以 EWC 2026 为例，可复用于任何电竞/游戏赛事。

## 研究框架

### Phase 1: 赛事情报采集

确定赛事基本信息后，识别以下关键信息：
- 赛事项目（哪些游戏）
- 参赛队伍/选手（尤其是目标国家/地区的）
- 赛事官方 YouTube 频道（如有）
- 往届内容创作者合作模式

### Phase 2: 多维度 KOL 搜索策略

按以下维度搜索，每个维度独立搜索后合并去重：

| 维度 | NoxInfluencer keywords 示例 | 说明 |
|:-----|:---------------------------|:-----|
| 游戏专属 | `["Valorant","valorant ranked","valorant montage"]` | 核心游戏内容创作者 |
| 电竞生态 | `["esports français","compétition gaming","tournoi"]` | 电竞赛事内容 |
| 赛事品牌 | `["EWC","esports world cup"]` | 赛事直接关联 |
| FPS 交叉 | `["FPS français","shooter","counter-strike"]` | 同品类受众重叠 |
| 泛游戏 | `["streamer","gameur","youtubeur gaming"]` | 头部泛游戏 KOL |

**关键参数**：非英语国家搜索必须用对应语言的 `--lang` 参数（法国用 `--lang fr`）。

### Phase 3: 电竞组织频道

电竞组织频道是赛事关联的核心渠道，必须单独搜索：

```python
# 识别目标赛事相关的电竞组织
orgs = ["Karmine Corp", "Team Vitality", "Gentle Mates"]
# 搜索方式：直接按组织名搜索
keywords = [org for org in orgs]
```

评估维度：
- 是否有该游戏的战队/分部
- 赛事参赛概率（基于往届表现）
- 组织旗下个人创作者（如 KC 的 Gotaga/Kamet0）

### Phase 4: 分级筛选

按赛事关联度和商业价值分为三级：

| 级别 | 定义 | 合作策略 |
|:-----|:-----|:---------|
| S-Tier | 游戏专属头部 KOL | 产品评测、赛事期间深度植入 |
| A-Tier | 电竞组织频道 | 战队设备赞助、联名内容 |
| B-Tier | 泛游戏头部 KOL | 设备 setup 视频、品牌曝光 |

### Phase 5: 输出格式

赛事关联 KOL 报告应包含：
1. 赛事概览（基本信息 + OBSBOT 合作定位）
2. 游戏专属 KOL（按 S/A/B 分级）
3. 电竞组织频道（含赛事参赛概率）
4. 跨品类 KOL（FPS/泛游戏）
5. 合作策略建议（分层 + 预估费用）

## 法国 Valorant 生态速查（2026-06）

| 组织 | YouTube 订阅 | Valorant 相关性 |
|:-----|:------------|:----------------|
| Karmine Corp | 206K | Gotaga+Kamet0 创立，有 Valorant 战队 |
| Team Vitality | 423K | 法国老牌电竞，Valorant 分部活跃 |
| Gentle Mates | 464K | 新锐组织，Valorant 核心内容 |
| Mandatory GG | 24.3K | 专注 Valorant 电竞 |

| KOL | 订阅 | 平均播放 | 互动率 | 定位 |
|:----|:-----|:---------|:-------|:-----|
| Rayakuzaa | 567K | 101K | 5.14% | 法国最大 Valorant YouTuber |
| Fugu | 646K | 173K | 8.36% | Apex+Valorant 头部 |
| Jbzz | 874K | 215K | 5.17% | 游戏综合，Valorant 标签 |
| WiPR | 84.4K | 12.5K | 7.35% | Valorant 专属 |
| Rojin & Fuziah | 91.2K | 26.9K | 6.77% | Valorant 双人组合 |
| Sanjay | 59.6K | 6.4K | 4.32% | Valorant 创作者 |
| SachaSLM | 12.5K | 22K | 4.07% | 小而精 Valorant |
| DARICK | 36.9K | 69.7K | 3.56% | FPS/Valorant |
