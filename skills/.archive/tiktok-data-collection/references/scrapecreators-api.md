# ScrapeCreators API 文档摘要

## 概述

ScrapeCreators 是一个覆盖 33+ 社交媒体平台的统一数据采集 API。

- 官网：https://scrapecreators.com
- 文档：https://docs.scrapecreators.com
- 注册：https://app.scrapecreators.com
- 免费额度：100 积分

## 支持平台

TikTok, TikTok Shop, Instagram, YouTube, Rumble, LinkedIn, Facebook, GitHub, Facebook Marketplace, Facebook Events, Facebook Ad Library, Google Ad Library, LinkedIn Ad Library, Twitter, Reddit, Truth Social, Threads, Bluesky, Pinterest, Google, Twitch, Spotify, SoundCloud, Kick, Snapchat, Linktree, Komi, Pillar, Linkbio, Amazon Shop

## 认证

所有请求需要 `x-api-key` header：

```
x-api-key: YOUR_API_KEY
```

## TikTok 端点详情

### GET /v1/tiktok/profile

获取用户资料。

**参数**：
- `handle` (required): TikTok 用户名

**响应字段**：
- `success`: 是否成功
- `credits_remaining`: 剩余积分
- `user.uniqueId`: 用户名
- `user.nickname`: 昵称
- `user.verified`: 是否认证
- `user.signature`: 个人简介
- `user.createTime`: 创建时间（Unix timestamp）

### GET /v1/tiktok/search/hashtag

按 hashtag 搜索视频。

**参数**：
- `hashtag` (required): hashtag 名称（不含 #）
- `count`: 返回数量（默认 20）

**响应字段**：
- `success`: 是否成功
- `credits_remaining`: 剩余积分
- `aweme_list`: 视频列表
  - `aweme_list[].desc`: 视频描述
  - `aweme_list[].create_time`: 创建时间（Unix timestamp）
  - `aweme_list[].author.unique_id`: 作者用户名
  - `aweme_list[].statistics.play_count`: 播放量
  - `aweme_list[].statistics.digg_count`: 点赞数

### GET /v1/tiktok/search/keyword

按关键词搜索视频。

**参数**：
- `query` (required): 搜索关键词
- `count`: 返回数量

**⚠️ 已知问题**：此端点经常返回空结果，建议用 hashtag 搜索替代。

### GET /v1/tiktok/profile/videos

获取用户的视频列表。

**参数**：
- `handle` (required): 用户名
- `count`: 返回数量

## 错误响应

```json
{
  "success": false,
  "credits_remaining": 0,
  "message": "Looks like you're out of credits"
}
```

## 无速率限制

ScrapeCreators 不限制请求频率，建议保持在 500 并发以下。

## 积分消耗

每次 API 调用消耗 1 积分。积分用完后需要充值：
- $100 = 3,000 积分
- $48 = 15,000 积分
- $148 = 75,000 积分
