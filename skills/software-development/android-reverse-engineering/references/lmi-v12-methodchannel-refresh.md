# Lmi v12: MethodChannel 软刷新实现记录

## 背景

用户要求刷新按钮只刷新直播间（不重启整个 App）。v10/v11 使用 `activity.recreate()` 导致整个 App 重启。

## 用户完整需求（2026-05-29）

1. ✅ 软件可以正常使用（登录、直播）
2. ✅ 设置一个可以刷新直播间的按钮（MethodChannel 软刷新）
3. ⏳ 阻止软件弹窗收费，或可以直接关闭付费的弹窗
4. ⏳ 全面分析软件，彻底搞懂软件逻辑

## 当前状态

v12 已制作完成（MethodChannel 软刷新），但用户反馈「打不开应用」。可能原因：
- apktool 回编后的 APK 结构与原始 APK 有差异
- 需要进一步调试安装失败原因

**下一步：** 考虑不使用 apktool 重新打包，而是直接修改原始 APK 中的 libapp.so 二进制文件（方案E 的思路），然后用 zip 工具重新打包，避免 apktool 引入的结构差异。

## 技术方案

通过 Flutter MethodChannel 向 Dart 层发送 `refreshLiveRoom` 消息，由 Flutter 层调用 `_refreshPlayUrlFromServer` 方法。

## 关键发现

### Flutter 层已有的刷新机制

通过 `strings libapp.so` 发现：
```
_refreshPlayUrlFromServer@953456253
_shouldRefreshPlayUrl@953456253
[LiveRoomView] refresh playUrl failed:
```

说明 Flutter 层已有刷新直播间播放地址的方法，只需通过 MethodChannel 触发。

### 直播间相关字符串

```
joinLiveRoom
liveRoomId
LiveRoomEffectSettingsStore
LiveRoomMessageType.
_LiveRoomViewPageState@953456253
```

## 实现细节

### MainActivity.smali 修改

1. 添加字段：`.field private refreshChannel:Lio/flutter/plugin/common/MethodChannel;`
2. 在 `configureFlutterEngine()` 末尾创建 channel：
   ```smali
   new-instance v0, Lio/flutter/plugin/common/MethodChannel;
   # ... 获取 BinaryMessenger ...
   const-string v2, "com.lmi.live/refresh"
   invoke-direct {v0, v1, v2}, Lio/flutter/plugin/common/MethodChannel;-><init>(...)
   iput-object v0, p0, Lcom/lmi/live/MainActivity;->refreshChannel:Lio/flutter/plugin/common/MethodChannel;
   ```
3. `onCreate()` 中传递 channel：
   ```smali
   iget-object v0, p0, Lcom/lmi/live/MainActivity;->refreshChannel:...
   invoke-static {p0, v0}, Lcom/lmi/live/RefreshHelper;->addRefreshButton(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
   ```

### RefreshHelper.smali 修改

- 构造函数：`<init>(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V`
- 添加字段：`.field private final channel:Lio/flutter/plugin/common/MethodChannel;`
- `addRefreshButton` 静态方法：接收 `MethodChannel` 参数
- `onClick`：调用 `channel.invokeMethod("refreshLiveRoom", null)` 而非 `activity.recreate()`

## 多架构 APK 处理

原始 APK `app-release (2).apk.1`（221MB）包含 arm64-v8a + armeabi-v7a。

**关键教训：必须从完整原始 APK 开始工作。** 之前从 107MB 的 arm64-only APK 修改，导致部分设备安装失败。

## 文件命名

用户提供的 APK 文件名可能非标准（如 `.apk.1`），用 `file` 命令仍可识别为 ZIP archive。
