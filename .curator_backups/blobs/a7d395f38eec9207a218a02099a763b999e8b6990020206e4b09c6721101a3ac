# 混合搜索策略：yt-dlp + 浏览器搜索

## 概述

单用 yt-dlp 搜索会漏掉低播放量的新视频（按相关性排序），单用浏览器搜索太慢且容易超时。
最佳方案是两阶段混合搜索。

## Phase 1: yt-dlp 搜索 + 并行详情获取

### 搜索阶段（~75秒）

```python
import subprocess, json, os
from concurrent.futures import ThreadPoolExecutor

os.environ['https_proxy'] = 'http://127.0.0.1:1082'

all_videos = {}
for brand, queries in brands.items():
    for query in queries:
        cmd = ['yt-dlp', '--flat-playlist', '--no-warnings',
               '--print', '{"title":"%(title)s","channel":"%(channel)s","id":"%(id)s","views":"%(view_count)s","duration":"%(duration)s"}',
               f'ytsearch8:{query}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20, env={**os.environ})
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                vid = json.loads(line)
                vid_id = vid.get('id', '')
                if vid_id and vid_id not in all_videos:
                    vid['brand'] = brand
                    all_videos[vid_id] = vid

video_ids = list(all_videos.keys())
# 典型结果: 242 个唯一视频
```

### 详情获取阶段（~80秒，8 并行）

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_video_date(vid_id):
    cmd = ['yt-dlp', '--no-warnings', '--no-download',
           '--print', '%(id)s|||%(upload_date)s|||%(view_count)s|||%(like_count)s|||%(comment_count)s|||%(duration)s|||%(channel)s|||%(title)s',
           f'https://www.youtube.com/watch?v={vid_id}']
    # ⚠️ 不要添加 --skip-unavailable-formats（该选项不存在，会导致全部失败）
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env={**os.environ})
    if result.returncode == 0 and '|||' in result.stdout:
        parts = result.stdout.strip().split('|||')
        if len(parts) >= 8:
            return {'id': parts[0], 'upload_date': parts[1], 'views': parts[2],
                    'likes': parts[3], 'comments': parts[4], 'duration': parts[5],
                    'channel': parts[6], 'title': parts[7]}
    return None

recent_videos = []
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(get_video_date, vid_id): vid_id for vid_id in video_ids}
    for future in as_completed(futures):
        result = future.result()
        if result and START_DATE <= result['upload_date'] <= END_DATE:
            recent_videos.append(result)
```

⚠️ **VPN 断开风险**：搜索阶段（~75秒）后 VPN 可能断开。如果详情获取全部返回 `Unable to connect to proxy`，需在 terminal 中重连 VPN 后重新执行详情获取脚本。

⚠️ **2026-06-22 重要更新**：yt-dlp 批量并行请求（300+ 视频）可能触发 YouTube 全局 bot 检测，导致所有后续请求（包括单个请求）全部失败。症状：搜索阶段成功获取视频 ID，但详情获取阶段 307 个视频全部返回 `Sign in to confirm you're not a bot`。此时不要重试 yt-dlp，直接跳到 Phase 2 浏览器搜索。

## Phase 2: 浏览器补充搜索（Phase 1 失败或结果不足时）

如果 Phase 1 找到 0 个或极少视频在日期范围内，**或者 Phase 1 详情获取因 bot 检测全部失败**，用浏览器搜索补充。

### Subagent 配置

- **3 个 subagent**，各搜索 6-7 个品牌（受 max_concurrent_children=3 限制）
- 19 品牌分配：7 + 6 + 6（2026-06-22 验证可行，每路 ~200-320 秒）
- 每个品牌搜索 URL: `https://www.youtube.com/results?search_query=QUERY&sp=EgIIAw%3D%3D`
- `sp=EgIIAw%3D%3D` = 按上传日期排序
- ⚠️ 浏览器相对日期（"2天前"）与 yt-dlp 绝对日期可能有 1 天偏差（UTC+8 vs UTC），最终以浏览器 description 中的绝对日期为准

### 品牌分配（24 品牌，3 subagent × 8）

**Subagent 1**（8 个品牌）:
Hollyland Astra P1, Logitech Brio, Logitech C920, Logitech MX Brio, Logitech C922, Insta360 Link 2, Insta360 Link 2 Pro, Elgato Facecam 4K

**Subagent 2**（8 个品牌）:
Elgato Facecam mk2, Emeet Pixy, EMEET SmartCam S600, EMEET SmartCam S800, EMEET PIXY Wireless, EMEET S600L, EMEET SmartCam C960 Ultra, EMEET C60E

**Subagent 3**（8 个品牌）:
Yolocam S3, Yolocam S7, Hollyland VenusLiv Air, Hollyland Lyra 4K, Razer Kiyo, UGREEN 4K Webcam, Insta360 Link 2c, Insta360 Wave

### 提取 JS

```javascript
const vidList = [];
document.querySelectorAll('ytd-video-renderer').forEach((el, i) => {
  if (i < 10) {
    const titleEl = el.querySelector('#video-title');
    const channelEl = el.querySelector('#channel-name a');
    const metaSpans = el.querySelectorAll('#metadata-line span');
    let views = '', date = '';
    metaSpans.forEach(s => {
      const t = s.textContent.trim();
      if (t.includes('views')) views = t;
      if (t.includes('ago')) date = t;
    });
    if (titleEl) {
      vidList.push({
        title: titleEl.textContent.trim().substring(0, 100),
        channel: channelEl?.textContent.trim() || '',
        views, date,
        videoId: titleEl.href?.split('v=')[1]?.split('&')[0] || ''
      });
    }
  }
});
JSON.stringify(vidList);
```

### 日期判断

- "X小时前" = 今天
- "1天前" = 昨天
- "X天前" = 需要计算是否在范围内
- "Jun 6" / "June 7" = 直接比较

## Phase 3: 获取补充视频详情

对 Phase 2 发现的新视频 ID，用 yt-dlp 获取详情（与 Phase 1 相同的 get_video_date 函数）。

⚠️ **2026-06-12 发现**：yt-dlp 对 <48 小时的新视频会报 `Requested format is not available` 错误（见 Pitfall 17）。此时必须用浏览器获取详情。

### Phase 3b: 浏览器详情获取（当 yt-dlp 失败时）

用 `delegate_task` + browser tools 批量获取视频详情：
- 每个 subagent 处理 **7 个视频**（每次 ~30 秒）
- 提取字段：title, channel, views, likes, date, duration, paidPromotion, hashtags, description

```javascript
// 在视频页面的 browser_console 中执行（2026-06-22 更新，增加 paid promotion 和 hashtags 检测）
JSON.stringify({
  title: document.querySelector('h1.ytd-watch-metadata yt-formatted-string')?.textContent?.trim(),
  channel: document.querySelector('#channel-name a')?.textContent?.trim(),
  views: document.querySelector('#info-container span:first-child')?.textContent?.trim(),
  likes: document.querySelector('like-button-view-model button')?.getAttribute('aria-label'),
  date: document.querySelector('#info-container span:nth-child(3)')?.textContent?.trim(),
  duration: document.querySelector('.ytp-time-duration')?.textContent?.trim(),
  actualDate: (document.querySelector('#description-inner')?.textContent?.match(/(\d{4})年(\d{1,2})月(\d{1,2})日/) || []).slice(1,4).join('-') || 'unknown',
  paidPromotion: !!document.querySelector('a[href*="paid_promotion"]'),
  hashtags: Array.from(document.querySelectorAll('a[href*="hashtag"]')).map(el => el.textContent.trim().toLowerCase()).join(','),
  description: document.querySelector('#description-inner')?.textContent?.trim().substring(0, 500)
});
```

## 实际命中率数据

### 2026-06-22 周一（3天窗口，yt-dlp 被封锁）

| 阶段 | 搜索范围 | 找到视频 | 在日期范围内 |
|------|---------|---------|------------|
| Phase 1 yt-dlp 搜索 | 19品牌×63关键词=搜索成功 | 307 个唯一视频 | N/A（详情获取全部被 bot 检测拦截） |
| Phase 2 浏览器 | 3 subagent × 6-7品牌 | ~15 个候选视频 | **6 个**（过滤后） |

**结论**：yt-dlp 批量请求触发全局 bot 检测后，浏览器搜索是唯一可靠方案。3 天窗口命中率比 2 天窗口高。

### 2026-06-12 周五（2天窗口）

| 阶段 | 搜索范围 | 找到视频 | 在日期范围内 |
|------|---------|---------|------------|
| Phase 1 yt-dlp | 19品牌×3关键词=51查询 | 254 个唯一视频 | **1 个** |
| Phase 2 浏览器 | 19品牌×1查询 | ~40 个视频 | **7 个**（含1个重复） |

**结论**：对于 2 天窗口，yt-dlp 按相关性排序找到的视频中仅 ~0.4% 在日期范围内。浏览器按日期排序搜索是发现新视频的主要来源。

## 典型时间分布

| 阶段 | 耗时 | 产出 | 备注 |
|------|------|------|------|
| Phase 1 搜索 | ~60s | 300+ 个视频 | yt-dlp ytsearch 成功 |
| Phase 1 详情获取 | ~160s 或 失败 | 0-N 个日期范围内视频 | ⚠️ 可能被 bot 检测全部拦截 |
| Phase 2 浏览器搜索 | ~540s（3路并行） | 5-15 个新视频 | 每路 6-7 品牌，~200-320s/路 |
| Phase 2 浏览器详情 | ~200s（2路并行） | 完整视频元数据 | 每路 7-8 个视频 |
| Phase 3 详情补充 | ~10s 或 ~240s（浏览器） | 补充视频详情 | 仅 yt-dlp 失败时 |
| **总计（正常）** | **~10-15 min** | **完整覆盖** | |
| **总计（yt-dlp 被封）** | **~15-20 min** | **浏览器全覆盖** | 跳过 Phase 1 详情获取 |
