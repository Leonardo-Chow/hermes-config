# TRTC（腾讯云实时音视频）直播协议说明

## 概述

TRTC（Tencent Real-Time Communication）是腾讯云的实时音视频 SDK，广泛应用于直播、连麦、在线教育等场景。Lmi Live 等直播 App 使用 TRTC 实现主播推流和观众拉流。

## 关键事实

| 属性 | 说明 |
|:-----|:-----|
| 协议 | 专有协议（UDP-based），**非标准 RTMP/FLV/HLS** |
| 播放方式 | 只能用 TRTC SDK（或兼容 WebRTC 的浏览器）播放 |
| VLC/MPV/ffplay | ❌ 不支持 |
| URL 可提取性 | 不存在静态的可播放 URL，只有动态鉴权参数 |

## App 中的关键 API 端点

通过 `strings libapp.so` 提取的典型 TRTC 直播相关 API（以 Lmi Live 为例）：

```
/app/live/info              → 返回房间信息 + TRTC 参数（sdkAppId, userSig, roomId 等）
/app/live/join              → 加入房间
/app/live/heartbeat         → 心跳保活
/app/live/summary/info      → 房间摘要信息
/app/live/leave             → 离开房间
/app/live/start             → 开始直播（主播）
/app/live/stop              → 结束直播（主播）
/app/live/like              → 点赞
/app/live/mute              → 禁言
/app/live/blacklist         → 黑名单
/app/live/audience/list     → 观众列表
/app/live/pk/status         → PK 状态
/app/live/pk/respond        → 响应 PK
```

## Lmi Live 特有字段

strings 中发现以下 TRTC 相关字段：

| 字段 | 说明 |
|:-----|:-----|
| `viewerPushUrl` | 观众推流地址（TRTC 内部字段，非标准 RTMP） |
| `pushUrl` | 推流地址 |
| `trtcCloud` | TRTC 云实例引用 |
| `_trtcObserver@...` | TRTC 观察者回调 |
| SDK AppID | `1385395381`（从 license URL 提取：`https://1385395381.trtcube-license.cn/...`） |

## 鉴权参数

TRTC 房间需要以下参数才能连接：

- **sdkAppId** — 应用标识（示例：1385395381）
- **roomId** — 房间号（Lmi 中为 1410）
- **userId** — 用户标识
- **userSig** — 鉴权签名（服务端签发，有时效）
- **license** — 可选：`https://{sdkAppId}.trtcube-license.cn/license/v2/{sdkAppId}_1/v_cube.license`

## 从 API 响应中提取 TRTC 参数

如果能够拦截 API（通过 MitM 或 Hook），`/app/live/info?roomId=1410` 的响应通常包含：

```json
{
    "code": 0,
    "data": {
        "sdkAppId": 1385395381,
        "roomId": 1410,
        "userId": "user_xxx",
        "userSig": "xxx",
        "streamUrl": "trtc://...",      // TRTC 专用，不可播放
        "cdnUrl": "http://xxx.flv"      // 可选，仅当启用了 CDN 转推
    }
}
```

## CDN 转推（CSS）

TRTC 可以配置 CDN 转推（Tencent Cloud CSS — Cloud Streaming Services），此时会生成标准的 FLV/HLS 地址。但不是所有 App 都启用。判断方式：

1. 从 API 响应/strings 中找关键词：`cdnUrl`, `hlsUrl`, `flvUrl`, `playUrl`
2. 找模式：`{{sdkAppId}}.liveplay.myqcloud.com`
3. 找模式：`bizid.liveplay.myqcloud.com`

如果 App **未启用** CDN 转推，则**不存在**任何可以提取的标准流 URL。

## 与 MitM 代理的结合

在 MitM 拦截脚本中，可以通过 `response` handler 捕捉 `/app/live/info` 响应的完整 JSON：

```python
def response(flow):
    if "/app/live/info" in flow.request.pretty_url:
        body = json.loads(flow.response.text)
        # 检查是否有 CDN URL 字段
        if "cdnUrl" in body.get("data", {}):
            print(f"[CDN URL] {body['data']['cdnUrl']}")
        # 否则只返回 TRTC 参数（不能直接播放）
```

将此逻辑加入 `templates/mitmproxy-bypass-template.py` 的 `response()` 函数。

## 实用建议

| 场景 | 方案 |
|:-----|:-----|
| 只是想免门票看直播 | ✅ 方案D：嵌入CA到APK + MitM 代理拦截门票 API |
| 想在 PC 上看 | 检查是否有 Web 版；或安装 Android 模拟器运行改版 APK |
| 想提取流用 VLC 播放 | ⚠️ 只有 App 启用了 CDN 转推才可能，否则无法实现 |
| 想录播 | 在模拟器/手机上运行 App，用 OBS 窗口录制；或用 scrcpy + 录屏 |

## 其他 RTC 厂商

类似的专有协议直播 SDK：

| 厂商 | SDK | 协议 |
|:-----|:-----|:-----|
| 腾讯云 | TRTC / LiteAVSDK | 专有 UDP（部分场景可推 CDN FLV） |
| 声网 Agora | Agora RTC SDK | 专有 UDP |
| 七牛云 | QNRTC | 专有 UDP |
| Zego | ZegoExpress | 专有 UDP |
