#!/bin/bash
# YouTube 视频数据快速抓取（curl + regex）
# 用法: bash youtube_curl_scrape.sh <video_url>
# 输出: JSON 格式的视频数据

URL="$1"
if [ -z "$URL" ]; then
    echo "用法: $0 <youtube_video_url>"
    exit 1
fi

# 获取页面 HTML
HTML=$(curl -s -L --max-time 20 "$URL")

# 提取点赞数
LIKES=$(echo "$HTML" | grep -oP '"likeCount":"\K\d+' || echo "0")
if [ "$LIKES" = "0" ]; then
    LIKES=$(echo "$HTML" | grep -oP '"defaultText":\{"simpleText":"([\d,]+)"\}' | grep -oP '[\d,]+' | head -1 | tr -d ',' || echo "0")
fi

# 提取浏览量
VIEWS=$(echo "$HTML" | grep -oP '"viewCount":"\K\d+' || echo "0")
if [ "$VIEWS" = "0" ]; then
    VIEWS=$(echo "$HTML" | grep -oP '<meta itemprop="interactionCount" content="\K\d+' || echo "0")
fi

# 提取标题
TITLE=$(echo "$HTML" | grep -oP '<title>\K[^<]+' | head -1)

# 提取博主
CHANNEL=$(echo "$HTML" | grep -oP '"ownerChannelName":"\K[^"]+' || echo "")

# 输出 JSON
echo "{\"title\":\"$TITLE\",\"url\":\"$URL\",\"channel\":\"$CHANNEL\",\"views\":$VIEWS,\"likes\":$LIKES}"
