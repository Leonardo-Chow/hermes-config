# Lmi Live App 逆向分析报告

**App**: Lmi 直播 (`com.lmi.live`)
**分析日期**: 2026-05-27（v1-v3），2026-05-28（v4-v10），2026-05-29（v11 修复登录）
**APK 大小**: 221MB (原始多架构) / 107MB (arm64-v8a 精简版)
**技术栈**: Flutter + 腾讯云 TRTC + Google Play Billing v7.1.1 + 自建门票系统

## Lmi APK 文件清单（~/Downloads/）

| 文件 | 大小 | 说明 |
|:-----|:-----|:-----|
| `lmi.apk` | 112MB | 原始 APK（多架构，未修改） |
| `Lmi_NoTicket_v10.apk` | 114MB | v10 修改版（API 地址被改，登录失败） |
| `Lmi_v11_WithRefresh.apk` | 107MB | v11 arm64-only（**安装失败：与操作系统不兼容**） |
| `Lmi_v11_Fixed.apk` | 221MB | v11 Fixed 多架构版（保留原始 API + RefreshHelper）✅ 当前使用 |
| `Lmi_Patched_Stripped.apk` | 112MB | 中间产物 |
| `Lmi_NoTicket_v7.apk` | 258MB | v7 旧版（多架构臃肿） |

## 技术架构

```
Flutter (Dart) 层:
  - 业务代码: package:lmi_app（纯移动App，无web版）
  - 源码路径: D:/JAVA/LLI/live-streaming-app-repository/lmi_app/
  - HTTP: Dart 原生 HttpClient（不走 Java OkHttp）
  - 门票检测: _hasOwnedRoomTicket@953456253, _isTicketOwned@..., _exitDueToTicket@...
  - 弹窗: _buildTicketDialog@994430884, _buildTicketRequiredOverlay@...
  - 数据传输: _loadTicketDataFromApi@..., _fetchTicketPriceThenShow@...
  - 分享链接: lmilive://live-room/share?liveRoomId=1419&roomDisplayId=55555&anchorName=...
  - 网络监控: libc.connect hook 可看到连接 IP:port 但内容加密

Native (Java) 层:
  - MainActivity (Flutter 宿主)
  - BillingClient (Google Play 支付)
  - ProxyBillingActivity (支付 Activity)
  - MethodChannel: com.lmi.live/payment_browser — 支付浏览器（拦截此 channel 可阻止付费弹窗）
  - MethodChannel: com.lmi.live/screen_awake — 屏幕常亮
  - MethodChannel: com.lmi.live/screen_protection — 屏幕保护
  - MethodChannel: com.lmi.live/screen_protection/events — 屏幕保护事件（EventChannel）
  - 自定义 MethodChannel: com.lmi.live/refresh — 刷新直播间（v12 新增）

网络层:
  - 域名: lmilive.lmizhibo.com (81.71.248.163)
  - Auth header: lmi-live-token
  - TRTC SDK License: 1385395381.trtcube-license.cn
  - 直播协议: 腾讯云 TRTC（专有 UDP 协议，非 RTMP/FLV/HLS）
  - 登录: /app/user/email/login
  - 无公开 API — 所有端点均需认证（2026-05-30 枚举确认）
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

## 破解策略演变（v1 → v12）

| 版本 | 方案 | 效果 | 问题 |
|:-----|:-----|:-----|:-----|
| v1 | Frida Gadget + Java Hook + network_security_config | ❌ 弹窗依旧 | Dart HTTP 不走 Java 层，Flutter Widget 弹窗不触发 AlertDialog |
| v2 | v1 + mitmproxy 代理脚本 | ❌ 弹窗依旧 | 华为 HarmonyOS 未安装 CA 证书，HTTPS 均失败 |
| v3 | Frida Gadget + Dart AOT 符号 Hook（enumerateSymbols） | ❌ 弹窗依旧 | nm -D 仅有 5 snapshot 符号，enumerateSymbols() 找不到业务函数 |
| **v4** | **嵌入 mitmproxy CA 到 APK + MitM 代理拦截** | **待验证** | App 信任代理 CA，MitM 拦截 API 请求 |
| v7-v9 | 多轮迭代（从已修改的 APK 再解码，累积问题） | ⚠️ 结构问题 | v9 用 `-r` 模式解码导致结构损坏 |
| **v10** | 从原始 APK 完整重建 + 3个二进制补丁 + RefreshHelper 按钮 | ❌ **登录失败** | API 地址被改成 `http://81.71.248.163:80//`，该服务器无登录服务 |
| **v11** | 从原始 APK 重建，**只加 RefreshHelper，保留原始 API 地址** | ✅ 登录正常 + 刷新按钮 | 正确做法：功能性修改不碰 API 地址 |
| **v11 Fixed** | 从 `app-release (2).apk.1`（221MB 多架构）重建 | ✅ 安装正常 + 登录正常 | v11 之前用了精简 APK（107MB arm64-only），部分设备报「与操作系统不兼容」 |
| **v12** | 从原始 APK 重建 + MethodChannel 软刷新（`com.lmi.live/refresh`） | ⚠️ 制作中 | 刷新按钮改为通过 MethodChannel 发送 `refreshLiveRoom` 消息，不再 `recreate()`。用户需求还包括：阻止付费弹窗、全面分析软件。待验证安装和功能 |
| **v14** | RefreshHelper + RefreshHelper$1 + RefreshHelper$2（看直播/关直播双按钮） | ❌ 打不开 | 多内部类 smali 导致 App 崩溃 |
| **v3-final** | 单 RefreshHelper + RefreshHelper$1（recreate） | ⚠️ 可用 | 服务器端口冲突导致用户无法下载，功能上 recreate() 仍是重启整个 App |

**当前状态（2026-05-30）：** 用户需求为「看直播/关直播」两个按钮 + 阻止付费弹窗。多内部类方案导致崩溃，需探索其他实现方式（如单类多按钮、View ID 区分）。

### v10 登录失败根因

- 二进制补丁把 `https://lmilive.lmizhibo.com` 替换为 `http://81.71.248.163:80//`
- 同时把 `http://192.168.2.117:9000` 替换为 `http://81.71.248.163:80/////`
- 81.71.248.163 服务器没有实现 `/app/user/email/login` 等认证端点
- 所有 API 请求（包括登录）都发到了这个不完整的服务器

### v11 修复方案（两轮迭代）

**v11 第一轮（失败）：** 使用 `lmi.apk`（107MB，arm64-only）作为源
1. 从 `lmi.apk` 重新 `apktool d`（不从 v10 解码）
2. 只复制 `RefreshHelper.smali` 到 `smali_classes2/com/lmi/live/`
3. 在 `MainActivity.onCreate()` 末尾添加 RefreshHelper 调用
4. 修复 `$avd_hide_password__2` 资源缺失（创建空 stub XML）
5. `apktool b` + `uber-apk-signer` 签名 → 107MB
6. ❌ **安装失败：「与操作系统不兼容」** — `lmi.apk` 本身只有 arm64-v8a 架构

**v11 Fixed（成功）：** 使用 `app-release (2).apk.1`（221MB，多架构）作为源
1. 从 `app-release (2).apk.1` 重新 `apktool d`
2. 复制 `RefreshHelper.smali` + 修改 `MainActivity.smali`
3. `apktool b` + `uber-apk-signer` 签名 → 221MB
4. ✅ 安装正常 + 登录正常 + 刷新按钮正常

**教训：必须使用包含所有 CPU 架构的原始 APK 作为源文件。**

### 验证方法

```bash
# 确认 API 地址未被修改
strings output.apk | grep "lmilive"
# 应输出: https://lmilive.lmizhibo.com（原始地址）

# 确认 RefreshHelper 已添加
unzip -o output.apk classes2.dex -d /tmp/check
strings /tmp/check/classes2.dex | grep "RefreshHelper"
# 应输出: Lcom/lmi/live/RefreshHelper; 和 RefreshHelper.java
```

### v1-v3 失败根因
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

## 千度热播（qiandurebo.com）关联分析（2026-05-30 深度分析）

### App 历史
LMI Live 前身为「千度热播」，由**许昌千润网络科技有限公司**开发。App 包名 `com.lmi.live` 未变，API 域名 `lmilive.lmizhibo.com` 未变。新版 PWA 改名为「**17歲**」。

### 旧版网页（已失效）
千度热播曾有网页版直播观看页面：
- URL: `https://qiandurebo.com/web/video.php?roomnumber=55555`
- 页面内嵌 JavaScript 变量 `var user = {...}`，含 `play_url`（FLV 流地址）和 `zb_nickname`（主播名）
- DouyinLiveRecorder 的 `get_qiandurebo_stream_data()` 函数曾基于此接口工作
- StreamGet 也曾支持（`QiandureboLiveStream` 类），但 **v4.0.9 起已废弃**
- **提取方法（已失效）：**
  ```python
  data = re.search(r'var user = (.*?)\r\n\s+user\.play_url', html, re.S).group(1)
  play_url = re.findall(r'"play_url": "(.*?)",\r\n', data)
  ```

### 新版网页架构（2026年全面改版，Flutter Web PWA）

**重定向链路：**
```
qiandurebo.com (302) → dqcevbcm.94qr5.com (302) → d7i10uvnpwrqh.cloudfront.net (Vue.js SPA)
                     ↓
                   PWA 链接（从 /landing-page API 解密获取）:
                   d31ft00iqx11xs.cloudfront.net, d3sdwbmksqkkhw.cloudfront.net,
                   dv8ynndi5ln13.cloudfront.net, b7w3r9k2.wyccp.com, b4v6n1p8.o9l8z.com 等
```

**技术栈：**
- 入口页：Vue.js SPA（`d7i10uvnpwrqh.cloudfront.net`）— 引导页，加载 PWA 配置
- PWA 应用：**Flutter Web**（dart2js 编译，html renderer）— 实际直播间在此
- PWA manifest：`name: "17歲"`，`display: standalone`
- 直播协议：**HLS**（PWA 加载 `hls.js`）— 移动端用 TRTC，Web 端用 HLS
- 入口 JS：`flutter_bootstrap.js` → `main.dart.js`（4.8MB，dart2js 编译）

**Flutter Web 路由：**
- `/live/55555` — 加载 hls.js + 直播间页面
- `/live/?roomnumber=55555` — 参数形式
- Flutter 内部路由通过 `main.dart.js` 中的混淆代码处理，无法直接提取

**反爬措施（极其强硬，2026-05-30 全部验证）：**

| 层级 | 措施 | 绕过尝试 | 结果 |
|:-----|:-----|:---------|:-----|
| 1. JS 挑战 | 首次返回 503 + `location.href=""` | curl 带 cookie 重试 | ❌ 挑战持续 |
| 2. 浏览器指纹 | 无头浏览器返回蜜罐假页面 | Playwright + stealth 插件 | ❌ 仍返回蜜罐 |
| 3. AES-CBC 加密 | API payload 全部加密 | 找到 key/IV 并成功解密 | ✅ 解密成功 |
| 4. Flutter Web 初始化 | Flutter 引擎不完全初始化 | 延长等待 + 多种 URL 格式 | ❌ Flutter 未完全加载 |
| 5. 动态加载 | 直播间数据通过 Flutter 内部路由加载 | 分析 main.dart.js（4.8MB） | ❌ 代码高度混淆 |

**反爬蜜罐特征（bot 检测标志）：**
- 页面标题「主页」，内容全是「草履虫是怎样感知外界刺激的」等科普文本
- `<body style="display:none">` + CSS 隐藏类 `[class*=-p1-zse-]{display:none}`
- 伪装 meta 标签：`content="一次草履虫短期培养实验记录"`
- **判断方法：** 内容含「草履虫」「纤毛纲」「原生动物门」且无 video 元素 → 被识别为 bot

**API 结构（从 SPA JS 提取并成功解密）：**
- 域名：`kpi.landapiqq.com`、`kpich.landapiqq.com`、`kpiv4.landapiqq.com`
- 端点：`/landing-page`（POST，加密 payload）— 返回 PWA 链接和联系信息
- 端点：`/channel/statistics`（POST）— 渠道统计
- 加密：AES CBC，key=`BioItun4JIOFL78hlQECIb==`，IV=`dfg2s8g9klc3jab1`
- Auth：`Bearer 6sHdXgiC8FFKkfAyR4EMrlyAMuV0DBG4itzeMglyFHponGYXFwl7tf31BPB4TwMX`

**解密示例（成功解密 landing-page 响应）：**
```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
cipher = AES.new(b'BioItun4JIOFL78hlQECIb==', AES.MODE_CBC, b'dfg2s8g9klc3jab1')
result = unpad(cipher.decrypt(base64.b64decode(encrypted)), 16).decode()
# 返回: {"pwaLinks":["https://d31ft00iqx11xs.cloudfront.net",...],"contactList":[...]}
```

**结论：** 千度热播网页版已从 PHP 升级为 Flutter Web PWA。即使解密了 API 通信，Flutter Web 在无头浏览器中不完全初始化，无法导航到直播间。直播间 HLS 流地址只能通过**真实浏览器手动操作 + 抓包**获取。DouyinLiveRecorder 和 StreamGet 的千度热播集成均已失效。

## 已知限制（不可行事项）

### ❌ 网页版存在但无法自动提取（2026-05-30 确认）\n\nLMI Live 移动端（`package:lmi_app`）使用 TRTC 协议，无法提取标准流。\n千度热播（qiandurebo.com）有 Flutter Web PWA 网页版（改名「17歲」），使用 HLS 协议，但：\n- 无头浏览器被反爬检测，返回蜜罐假页面\n- Flutter Web 引擎在 headless 环境不完全初始化\n- API 通信使用 AES-CBC 加密（已破解但无用，无法导航到直播间）\n- **唯一可行方案：真实浏览器手动操作 + 抓包获取 HLS m3u8 地址**

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
