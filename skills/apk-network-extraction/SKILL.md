---
name: apk-network-extraction
description: 从 Android APK 中提取网络 API 端点、域名和认证信息的系统化方法。适用于 Flutter 原生应用分析。
category: software-development
---

# APK 网络信息提取

从 Android APK 中提取 API 端点、域名和认证方式的系统方法。

## 适用场景

- 需要了解 Android App 的后端 API 结构
- 需要找直播流 URL、支付接口、认证端点
- Flutter 应用的 Dart 层/Java 层网络分析
- 逆向分析 app 的网络通信

## 工作流

### 1. 提取域名和 API 端点

```bash
# 找到所有 API 路径（Flutter 应用通常以 /app/ 开头）
strings app.apk | grep -E '^/app/' | sort -u

# 找到 HTTP URL（域名大部分在 strings 表中）
strings app.apk | grep -E 'https?://' | grep -v 'com\.android\|google\|facebook\|tencent\|huawei\|amazon' | sort -u

# 找到包级 Dart imports（提示架构分层）
strings app.apk | grep -E 'package:.*services/' | sort -u
```

### 2. 测试端点

```bash
# 测试公开端点
curl -sk "https://<domain>/app/live/info?roomId=ROOM_ID" -H "User-Agent: AppName/1.0"

# 常见响应：
# - 200 + 数据 → 公开 API
# - 401 "未能读取到有效 token" → 需要认证
# - 404 → 路径不存在
```

### 3. 识别认证方式

```bash
# 搜索认证相关字符串
strings app.apk | grep -iE 'token|authorization|bearer|auth.*key|secret|header'
```

常见模式：
- `lmi-live-token` — 自定义 Header Token（LMI Live 风格）
- `Authorization: Bearer xxx` — 标准 JWT
- `x-auth-token` — 自定义 Header

### 4. 用代理拦截获取 Token

当 API 需要认证时，通过 mitmproxy 拦截一次已登录的请求提取 token header：

```bash
mitmdump --listen-host 0.0.0.0 --listen-port 8888
```

然后在手机上设置代理，打开 App 发起一次请求即可抓到完整 header。

### 5. 使用 Token 调用 API

```bash
TOKEN="<extracted_token>"
curl -sk "https://domain/app/live/info?roomId=1410" \
  -H "lmi-live-token: $TOKEN" \
  -H "User-Agent: LmiLive/1.0"
```

## 常见端点命名模式（直播类 App）

| 端点 | 作用 | 典型返回 |
|------|------|----------|
| `/app/live/info` | 直播间信息（含推流/拉流地址） | TRTC 配置、stream URL |
| `/app/live/join` | 加入房间 | 房间凭证 |
| `/app/live/summary/info` | 直播摘要 | 观看人数、时长 |
| `/app/live/ticket/my` | 门票状态 | hasTicket, owned |
| `/app/live/heartbeat` | 心跳保持 | 保活 |
| `/app/live/categoryList` | 分类列表 | 直播分类 |

## TRTC 直播流特征

- 使用腾讯云 TRTC SDK（libTXRTC.*.so）
- 拉流地址不是静态 RTMP/HLS，而是动态协商生成
- 通常需要 sdkAppId + userId + userSig + roomId 四元组
- 典型包名: `com.tencent.trtc`、`com.tencent.liteav`
- License URL: `https://*.trtcube-license.cn/license/`

## 注意事项

- **先 Mac 端分析再做手机操作** — 先用 `strings` + `curl` 从 APK 提取信息，确认需要手机 Token 后才启动代理
- Flutter APK 的 Dart 逻辑编译到 `libapp.so` 中，Java 层主要放 SDK 框架代码
- API 响应体 `code: 401 / msg: "未登录"` 表示需要认证
- 部分直播 App 有 Web 版本，可用浏览器直接访问域名测试
- 如果 `strings` 输出太多，用 `grep -v` 过滤 SDK/广告库噪音
