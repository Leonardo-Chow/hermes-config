# YouTube API 内容类型验证

## 四重验证流程（2026-06-04）

每个候选频道必须通过以下 4 项验证才能入库：

### 1. 活跃度验证
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CH_ID&type=video&maxResults=1&order=date&key=API_KEY"
```
- 检查 `publishedAt` 是否在 90 天内
- 超过 90 天 → 排除

### 2. OBSBOT 合作历史
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CH_ID&q=obsbot+webcam+camera&type=video&maxResults=5&order=date&key=API_KEY"
```
- 标题含 obsbot/tiny 3/tiny 2/tail 2/meet 2/talent → 排除

### 3. 内容类型过滤
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CH_ID&type=video&maxResults=5&order=date&key=API_KEY"
```
获取最新 5 个视频标题，检查：

| 过滤条件 | 判断逻辑 | 处理 |
|:---------|:---------|:-----|
| 纯游戏 | 4/5 标题含 game/gaming/twitch/fortnite/minecraft/valorant | 排除 |
| 纯 Shorts | 标题很短且频道无长视频 | 排除 |
| Vlog 类型 | 3+ 标题含 vlog/day in my life/routine | 标记 ⚠️ |
| 安防摄像头 | 频道名含 security/surveillance/cctv/alarm | 排除 |
| 产品官号 | 频道名含 official/inc./systems/corp/nexigo/hikvision | 排除 |

### 4. 竞品合作历史
```bash
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CH_ID&q=insta360+OR+elgato+OR+logitech+webcam&type=video&maxResults=5&order=date&key=API_KEY"
```
- 标题含 insta360 link/elgato facecam/logitech brio → 标记为竞品合作（优先级更高）

## 排除关键词列表

**品牌官号**：official, inc., systems, corp, ltd, nexigo, hikvision, nikon, bose, acasis, tp-link, obsbot

**安防摄像头**：security, surveillance, cctv, alarm

**游戏关键词**：game, gaming, twitch, fortnite, minecraft, valorant, cod, apex, league of legends, overwatch

**Vlog 关键词**：vlog, day in my life, routine, morning routine, daily life
