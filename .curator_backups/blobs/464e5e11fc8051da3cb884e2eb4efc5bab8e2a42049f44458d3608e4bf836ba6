# Omar TikTok Scraper API 文档摘要

## 概述

Omar TikTok Scraper 是专注 TikTok 数据的 REST API，提供视频详情（含 HD 无水印下载链接）。

- 官网：https://www.omkar.cloud/tools/tiktok-scraper
- 文档：https://www.omkar.cloud/tools/tiktok-scraper/about
- 注册：https://www.omkar.cloud
- 免费额度：100 次/月

## 认证

使用 `API-Key` header：

```
API-Key: YOUR_OMKAR_API_KEY
```

## 端点详情

### GET /tiktok/users/profile

获取用户资料。

**参数**：
- `handle` (required): TikTok 用户名（不含 @）

**响应字段**：
- `user.user_id`: 用户 ID
- `user.handle`: 用户名
- `user.display_name`: 昵称
- `user.bio`: 个人简介
- `user.is_verified`: 是否认证
- `stats.following_count`: 关注数
- `stats.follower_count`: 粉丝数
- `stats.total_likes`: 总点赞
- `stats.video_count`: 视频数

### GET /tiktok/videos/details

获取视频详情，包含下载链接。

**参数**：
- `video_url` (required): TikTok 视频 URL

**响应字段**：
- `video_id`: 视频 ID
- `region`: 地区
- `caption`: 视频描述
- `created_at`: 创建时间（Unix timestamp）
- `duration_seconds`: 时长
- `author.user_id`: 作者 ID
- `author.handle`: 作者用户名
- `author.display_name`: 作者昵称
- `media.video_url`: 标清视频 URL
- `media.hd_video_url`: 高清无水印视频 URL
- `media.file_size_bytes`: 文件大小
- `thumbnails.cover_url`: 封面图
- `audio.title`: 音频标题
- `audio.artist`: 音频作者
- `stats.views`: 播放量
- `stats.likes`: 点赞数
- `stats.comments`: 评论数
- `stats.shares`: 分享数
- `stats.downloads`: 下载数
- `stats.saves`: 收藏数

### GET /tiktok/videos/search

搜索视频。

**参数**：
- `search_query` (required): 搜索关键词

**⚠️ 注意**：搜索结果可能较少，建议配合其他数据源使用。

### GET /tiktok/videos/trending

获取热门推荐视频。

**参数**：无

## 错误响应

```json
{
  "message": "Invalid API key."
}
```

或

```json
{
  "message": "Not Found"
}
```

## 额度限制

- 免费额度：100 次/月
- 付费方案：
  - $16 = 3,000 次/月
  - $48 = 15,000 次/月
  - $148 = 75,000 次/月

## 使用策略

由于额度有限（100次/月），建议：

1. **优先用免费方案**：oembed API、Scrapling
2. **关键查询才用 Omar**：需要 HD 下载链接、完整统计数据
3. **记录每次使用**：用 `~/.hermes/scripts/omkar_usage.py` 追踪

## 与其他 API 对比

| 特点 | Omar API | ScrapeCreators |
|:-----|:---------|:---------------|
| 专注平台 | TikTok | 33+ 平台 |
| HD 下载链接 | ✅ | ❌ |
| 免费额度 | 100/月 | 100 积分 |
| 搜索功能 | ⚠️ 较弱 | ✅ hashtag 搜索 |
| 用户资料 | ✅ | ✅ |
