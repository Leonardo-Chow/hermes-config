# YouTube视频信息提取方法

## 提取标题

```bash
curl -s "https://www.youtube.com/watch?v=VIDEO_ID" | grep -o '"title":"[^"]*"' | head -1
```

备选：oembed API
```bash
curl -s "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=VIDEO_ID&format=json" | python3 -c "import json,sys; print(json.load(sys.stdin)['title'])"
```

## 提取博主/频道名

```bash
curl -s "https://www.youtube.com/watch?v=VIDEO_ID" | grep -o '"ownerChannelName":"[^"]*"'
```

备选：oembed API
```bash
curl -s "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=VIDEO_ID&format=json" | python3 -c "import json,sys; print(json.load(sys.stdin)['author_name'])"
```

## 提取发布时间

```bash
curl -s "https://www.youtube.com/watch?v=VIDEO_ID" | grep -o '"publishDate":"[^"]*"'
```

## 提取时长（秒）

```bash
curl -s "https://www.youtube.com/watch?v=VIDEO_ID" | grep -o '"lengthSeconds":"[^"]*"'
```

## 提取播放量

```bash
curl -s "https://www.youtube.com/watch?v=VIDEO_ID" | grep -o '"viewCount":"[^"]*"'
```

## 字幕获取

### 首选：youtube_transcript_api

设置代理后直接获取：
```python
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1082'
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['en', 'zh-Hans', 'zh-Hant'])
```

### 备选：yt-dlp + Chrome cookies

当 `youtube_transcript_api` 报 `RequestBlocked` 或 `IpBlocked` 时使用：
```bash
yt-dlp --cookies-from-browser chrome --proxy socks5://127.0.0.1:1082 \
  --write-auto-subs --sub-lang en --sub-format vtt --skip-download \
  --ignore-no-formats-error -o "/tmp/vt_%(id)s" "URL"
```

VTT 字幕含重复时间戳（每条字幕按行拆分，每行一个独立 cue），需解析清理：
```python
blocks = re.split(r'\n\n+', content)
for block in blocks:
    parts = block.split('\n')
    # 提取时间戳和文本，去重
```

## 注意事项

- 浏览器打开YouTube经常失败（GFW环境），curl + grep 是更可靠的方式
- 中国大陆环境需要 VPN + 代理（socks5://127.0.0.1:1082）
- 部分视频（Shorts等）yt-dlp 可能只返回 images，此时 `--ignore-no-formats-error` 跳过视频流错误但字幕仍可下载
- yt-dlp 版本过旧可能导致 JS challenge 失败，及时 `pip3 install --upgrade yt-dlp`
