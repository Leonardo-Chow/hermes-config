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

## Phase 2: 浏览器补充搜索（仅在 Phase 1 结果不足时）

如果 Phase 1 找到 0 个或极少视频在日期范围内，用浏览器搜索补充。

### Subagent 配置

- **2 个 subagent**，各搜索 9 个品牌
- 每个品牌搜索 URL: `https://www.youtube.com/results?search_query=QUERY&sp=EgIIAw%3D%3D`
- `sp=EgIIAw%3D%3D` = 按上传日期排序

### 品牌分配

**Subagent 1**（9 个品牌）:
Logitech Series, Insta360 Link 2, Insta360 Link 2c, Insta360 Wave, Insta360 Link 2 Pro, Elgato Facecam 4K, Elgato Facecam mk2, Emeet Pixy, EMEET SmartCam S600

**Subagent 2**（9 个品牌）:
EMEET SmartCam S800, EMEET PIXY Wireless, EMEET S600L, Yolocam S3, Yolocam S7, Hollyland VenusLiv Air, Hollyland Lyra 4K, Razer Kiyo, UGREEN 4K Webcam

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

## 典型时间分布

| 阶段 | 耗时 | 产出 |
|------|------|------|
| Phase 1 搜索 | ~75s | 242 个视频 |
| Phase 1 详情获取 | ~80s | 0-N 个日期范围内视频 |
| Phase 2 浏览器搜索 | ~400s | 5-15 个新视频 |
| Phase 3 详情获取 | ~10s | 补充视频详情 |
| **总计** | **~10 min** | **完整覆盖** |
