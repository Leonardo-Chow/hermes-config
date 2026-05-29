# Lmi Live App 逆向分析报告

**App**: Lmi 直播 (`com.lmi.live`)
**分析日期**: 2026-05-27（v1-v3），2026-05-27（v4）
**APK 大小**: 221MB (arm64-v8a)
**技术栈**: Flutter + 腾讯云 TRTC + Google Play Billing v7.1.1 + 自建门票系统

## 技术架构

```
Flutter (Dart) 层:
  - 业务逻辑: libapp.so（Dart AOT 编译）
  - HTTP: Dart 原生 HttpClient（不走 Java OkHttp）
  - 门票检测: _hasOwnedRoomTicket@953456253, _isTicketOwned@..., _exitDueToTicket@...
  - 弹窗: _buildTicketDialog@994430884, _buildTicketRequiredOverlay@...
  - 数据传输: _loadTicketDataFromApi@..., _fetchTicketPriceThenShow@...
  - 网络监控: libc.connect hook 可看到连接 IP:port 但内容加密

Native (Java) 层:
  - MainActivity (Flutter 宿主)
  - BillingClient (Google Play 支付)
  - ProxyBillingActivity (支付 Activity)
  - MethodChannel: com.lmi.live/payment_browser

网络层:
  - 域名: lmilive.lmizhibo.com (81.71.248.163)
  - Auth header: lmi-live-token
  - 直播协议: 腾讯云 TRTC（专有 UDP 协议，非 RTMP/FLV/HLS）
  - 登录: /app/user/email/login
```

## 关键 API 端点（从 libapp.so strings 提取）

| 端点 | 用途 |
|:-----|:-----|
| `/app/live/info` | 房间信息 + TRTC 参数（sdkAppId, userSig, roomId） |
| `/app/live/join` | 加入房间 |
| `/app/live/summary/info` | 房间摘要信息 |
| `/app/live/heartbeat` | 心跳保活 |
| `/app/live/ticket/my` | 查询用户门票列表 |
| `/app/live/ticket/buy` | 购买门票 |
| `/app/live/ticket/verify` | 验证门票 |
| `/app/live/ticket/config` | 门票配置 |
| `/app/live/ticket/preset/query` | 预设门票查询 |
| `/app/vip/list` | VIP 列表 |
| `/app/vip/privileges` | VIP 特权 |
| `/app/earning/balance/info` | 余额信息 |
| `/app/fanclub/my` | 粉丝俱乐部状态 |
| `/app/user/email/login` | 邮箱登录 |
| `/app/user/publicProfile` | 公开用户信息 |

## 门票工作流

1. 用户进直播间（roomId=1410, displayId=55555）→ `_hasOwnedRoomTicket()` 检查
2. App 调 API `GET /app/live/ticket/my`（通过 Dart HttpClient，不走 Java OkHttp）
3. 服务端返回门票列表 → 有票则进，无票则弹窗
4. 弹窗 → `_buildTicketDialog()` / `_buildTicketRequiredOverlay()` → 用户点购买
5. `_showTicketPayDialog()` → Google Pay / 自建支付
6. 支付成功后可能调 `/app/live/ticket/buy` → 再调 `/app/live/ticket/verify`

## 破解策略演变（v1 → v4）

| 版本 | 方案 | 效果 | 问题 |
|:-----|:-----|:-----|:-----|
| v1 | Frida Gadget + Java Hook + network_security_config | ❌ 弹窗依旧 | Dart HTTP 不走 Java 层，Flutter Widget 弹窗不触发 AlertDialog |
| v2 | v1 + mitmproxy 代理脚本 | ❌ 弹窗依旧 | 华为 HarmonyOS 未安装 CA 证书，HTTPS 均失败 |
| v3 | Frida Gadget + Dart AOT 符号 Hook（enumerateSymbols） | ❌ 弹窗依旧 | nm -D 仅有 5 snapshot 符号，enumerateSymbols() 找不到业务函数 |
| **v4** | **嵌入 mitmproxy CA 到 APK + MitM 代理拦截** | **待验证** | App 信任代理 CA，MitM 拦截 API 请求 |

### v3 失败根因
- Dart AOT release 编译 strip 了业务函数的 ELF 符号（nm -D 仅 5 个 snapshot 符号）
- `module.enumerateSymbols()` 只返回 snapshot 符号，找不到 `_hasOwnedRoomTicket` 等函数
- `Interceptor.attach()` 没有有效地址可 hook
- Memory.scanSync() 只能找到 .rodata 段的字符串，不是函数入口
- 结论：Frida Java 层 Hook 对 Flutter Dart HTTP 请求**完全无效**

### v4 思路
- 不依赖 Frida Hook Dart 函数
- 改为**网络层拦截**：将 mitmproxy CA 证书打包到 APK 的 `res/raw/` 目录
- 修改 `network_security_config.xml` 添加 `@raw/mitmproxy_ca` 信任锚点
- App 启动后信任代理证书 → MitM 可以解密 HTTPS 流量
- proxy 拦截所有 `/app/live/ticket/*` 请求 → 返回假「有票」响应
- 同时可捕获 `/app/live/info` 的完整响应（含 TRTC 参数）

## 已知限制（不可行事项）

### ❌ 无法提取 TRTC 直播流 URL
- App 使用腾讯 TRTC（专有 UDP 协议），非标准 RTMP/FLV/HLS
- 即使拿到 sdkAppId + userSig，也无法在 VLC/MPV 等播放器播放
- 除非 App 启用了 CDN 转推（CSS），否则不存在可提取的标准流地址

### ❌ Frida Java Hook 不能拦截 Dart HTTP
- Dart 使用自己的 `dart:io` HttpClient 或 `dio` 包
- **不走 Java 层的 OkHttp/HttpURLConnection**
- Java 层 Hook（OkHttpClient、MethodChannel）对 Dart HTTP 请求无效

### ❌ 华为 HarmonyOS 证书安装限制
- 无法通过 `http://mitm.it` 安装用户 CA 证书
- 即使修改 network_security_config 信任用户 CA，系统层仍可能阻止
- 解决方案：将 CA 证书嵌入 APK 的 `res/raw/`（方案D）

## Frida Gadget 注入部署要点

- 文件: `lib/arm64-v8a/libfrida-gadget.so`（25MB）
- 配置: `lib/arm64-v8a/libfrida-gadget.config.so`（带 `.so` 后缀！）
- 脚本: 用 `"code"` 字段内联嵌在 config 中，无需 assets 路径
- 加载: `System.loadLibrary("frida-gadget")` 加在 MainActivity.onCreate()
- 回编: `apktool b` 后 `uber-apk-signer --allowResign`
- 签名冲突: 原版必须先卸载

## GFW 环境注意事项

- Homebrew: 设置 `HOMEWBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles`
- GitHub: 先连 Shadowrocket VPN
- JADX 对 221MB APK 可能卡死（ps aux 看 java 状态） → 优先用 `strings libapp.so` 分析
