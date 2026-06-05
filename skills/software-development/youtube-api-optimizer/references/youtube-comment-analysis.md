# YouTube 评论爬取 + 产品反馈分析工作流

## 适用场景

批量爬取 YouTube 视频评论 → 按用户关注点分类 → 生成 Word/Excel 报告。典型用途：竞品评论分析、产品反馈收集、KOL 评论区监控。

## 核心 API

```
GET /youtube/v3/commentThreads
参数：
  videoId=<VIDEO_ID>
  part=snippet
  maxResults=100（上限）
  order=relevance（热门优先）| time（时间倒序）
  textFormat=plainText（纯文本，避免 HTML）
  pageToken=<TOKEN>（分页）
```

每调用 = 1 单位配额。14 个视频各 500 条评论 ≈ 70 次调用 = 70 单位。

## 评论数据结构

```json
{
  "id": "评论ID",
  "snippet": {
    "topLevelComment": {
      "snippet": {
        "authorDisplayName": "用户名",
        "textDisplay": "评论内容",
        "likeCount": 123,
        "publishedAt": "2025-01-01T00:00:00Z"
      }
    },
    "totalReplyCount": 5  // 回复数
  }
}
```

## 关键词分析模板（产品反馈）

适用于摄像头/硬件产品的评论分析，可按需扩展：

| 关注点 | 英文关键词 | 中文关键词 |
|--------|-----------|-----------|
| 画质/图像质量 | image quality, 4k, sharp, blur, noise, color, exposure, low light, hdr | 画质, 清晰, 模糊, 噪点, 色彩 |
| AI Tracking | tracking, follow, auto track, gesture, motion | 追踪, 跟踪, 跟随 |
| 云台/稳定 | gimbal, stabiliz, pan, tilt, smooth, shake | 云台, 稳定, 转动, 抖动 |
| 兼容性 | compatible, zoom, teams, obs, discord, windows, mac | 兼容, 支持, 适配 |
| 安装/设置 | install, setup, mount, clamp, tripod | 安装, 设置, 支架 |
| 连接/接口 | connect, usb, hdmi, wireless, wifi, bluetooth, lag, latency | 连接, 断连, 延迟, 卡顿 |
| 软件/App | software, app, firmware, update, bug, crash | 软件, 固件, 更新, 闪退 |
| 价格/性价比 | price, expensive, cheap, value, worth | 价格, 贵, 性价比 |
| 售后/客服 | warranty, return, refund, repair, customer service | 售后, 保修, 退换 |
| 音频/麦克风 | audio, microphone, mic, sound, noise cancel | 麦克风, 收音, 降噪 |
| 散热/噪音 | heat, hot, fan, noise, quiet | 散热, 发热, 噪音 |
| 竞品对比 | insta360, logitech, dji, compared, alternative | 对比, 比较 |

## Word 文档结构模板

```
一、评论总览（表格：产品 × 评论数/问题数）
二、视频列表（表格：标题/频道/日期/播放量/评论数）
三、用户关注点分析（汇总表：关注点 × 产品 × 提及数 × 占比）
四、各关注点详细评论（每个关注点下按产品分表，按点赞数排序，取 Top 20）
五、高赞评论 Top 20（跨产品汇总）
六、关键发现与建议（Top 5 关注点 + 人工复核提示）
```

## 关键 pitfall

1. **代理必须用 requests** — urllib + SOCKS5 会 IncompleteRead，见主 SKILL pitfall #9
2. **commentThreads 不是 comments** — `comments` 端点只获取回复，不获取顶级评论
3. **maxResults 上限 100** — 超过需分页，用 nextPageToken 循环
4. **评论可能关闭** — 部分视频禁用评论，API 返回空 items，需 try/except
5. **order=relevance 更有用** — 按相关性排序比按时间排序更能发现核心问题
6. **关键词误匹配** — "support" 会同时匹配兼容性和售后，"noise" 会匹配音频和散热。分析结果需注明"基于关键词匹配，建议人工复核"
7. **textFormat=plainText** — 避免 HTML 标签干扰关键词匹配
8. **中文评论少** — YouTube 英文视频评论以英文为主，中文关键词命中率低，但仍需包含以覆盖中文用户

## 依赖

```bash
pip install requests PySocks python-docx
```
