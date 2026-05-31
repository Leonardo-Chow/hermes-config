# Lmi APK 迭代失败记录 (v10 → v11 → v12 → v13)

## 迭代历史

| 版本 | 改动 | 结果 | 失败原因 |
|:-----|:-----|:-----|:---------|
| v10 | 改 API 地址 + RefreshHelper(recreate) | ❌ 登录失败 | API 地址从 lmilive.lmizhibo.com 改成 81.71.248.163 |
| v11 | 从原始 APK 重新制作，只加 RefreshHelper(recreate) | ❌ 安装失败 | apktool 回编只保留 arm64-v8a，丢了 armeabi-v7a |
| v11 Fixed | 从原始完整 APK（221MB双架构）制作 | ✅ 安装成功 | 但刷新是重启整个 App |
| v12 | 改为 MethodChannel 软刷新 | ❌ 打不开 | apktool 回编的 APK 结构问题 |
| v13 | 尝试 patch libapp.so 函数 | ❌ 未完成 | ARM64 函数序言检测失败 |
| v14 (2026-05-30) | RefreshHelper + RefreshHelper$1 + RefreshHelper$2（多按钮） | ❌ 打不开 | smali 内部类创建导致崩溃 |
| v3 (2026-05-30) | 简化为单 RefreshHelper + 单 RefreshHelper$1 | ❌ 用户未确认 | recreate() 重启整个 App，不是用户要的「刷新直播间」 |
| v14 (2026-05-30 晚) | RefreshHelper + RefreshHelper$1 + RefreshHelper$2（看直播/关直播双按钮） | ❌ 打不开 | 多内部类 smali 导致崩溃 |
| v3-final (2026-05-30 晚) | 简化单按钮 RefreshHelper + RefreshHelper$1（recreate） | ⚠️ 制作完成 | 服务器端口冲突导致用户无法下载 |

## 核心教训

### 1. 不要改 API 地址（除非有完整代理转发）
```
原始: https://lmilive.lmizhibo.com
v10:  http://81.71.248.163:80//  ← 登录服务不存在
```
改 API 地址 = 所有请求（包括登录）都发到新地址。

### 2. 保留所有 CPU 架构
```
原始 APK: arm64-v8a + armeabi-v7a = 221MB
apktool 解码后: 可能只保留 arm64-v8a = 107MB
结果: 部分设备「与操作系统不兼容」
```

### 3. apktool 回编可能破坏 APK
- 资源文件缺失（$avd_hide_password__2）
- dex 结构变化
- 某些设备（华为 HarmonyOS）对结构变化敏感

### 4. ARM64 函数二进制 patching 不可靠
- Dart AOT 编译器不生成标准 ARM64 函数序言
- 搜索 `stp x29, x30` 可能匹配数据区而非代码区
- 函数边界难以确定

### 5. 替代方案优先级
1. **MethodChannel 拦截**（smali 层，最可靠）
2. **API 重定向 + 本地代理**（需实现所有端点）
3. **Frida Gadget**（运行时 Hook）
4. ~~ARM64 二进制 patching~~（不可靠）

### 6. smali 内部类创建容易导致崩溃
- 创建 `RefreshHelper$1.smali`、`RefreshHelper$2.smali` 等多个内部类文件容易导致 App 崩溃
- 原因：内部类需要正确的 `InnerClasses` 注解和外部类引用
- 更可靠：只创建一个 RefreshHelper 类 + 一个 RefreshHelper$1 内部类（单按钮场景）
- 多按钮场景：用 View ID 区分，不要创建多个内部类文件

### 7. 用户说「刷新直播间」≠「重启 App」
- `activity.recreate()` 重启整个 App，Flutter 引擎重建，导航回首页
- 用户要的是「软刷新」：只刷新直播画面，不丢失页面状态
- 正确实现：通过 MethodChannel 向 Flutter 发消息
- 在动手前确认用户要「硬刷新」还是「软刷新」

## 关键字符串位置

| 字符串 | 偏移量 | 用途 |
|:-------|:-------|:-----|
| `_showPaySuccessDialog` | 0x59edc | 付费成功弹窗 |
| `_showTicketPayDialog` | 0x5af04 | 门票支付弹窗 |
| `_showCustomRechargeDialog` | 0x53e2d | 充值弹窗 |
| `_handlePayTap` | 0x79145 | 支付点击处理 |
| `_pollPaymentStatus` | 0x4e0ff | 轮询支付状态 |
| `_refreshPlayUrlFromServer` | 0x65c16 | 刷新播放地址 |
| `joinLiveRoom` | 0x5be59 | 加入直播间 |
| `leaveLiveRoom` | 0x8732f | 离开直播间 |

## MethodChannel 列表

| Channel | 用途 | 拦截点 |
|:--------|:-----|:-------|
| `com.lmi.live/payment_browser` | 支付浏览器 | configureFlutterEngine 中的 lambda$2 |
| `com.lmi.live/screen_awake` | 屏幕常亮 | lambda$0 |
| `com.lmi.live/screen_protection` | 屏幕保护 | lambda$1 |
| `com.lmi.live/screen_protection/events` | 屏幕保护事件 | configureFlutterEngine$4 |
