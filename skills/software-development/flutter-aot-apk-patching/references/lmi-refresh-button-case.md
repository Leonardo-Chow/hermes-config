# Lmi 直播 App 刷新按钮添加案例

## 背景
用户需要在 Lmi 直播 App 中添加一个刷新直播间按钮，但之前的实现使用了 `activity.recreate()` 导致重启整个 App。

## 问题分析

### v10 版本问题
- API 地址被改成 `http://81.71.248.163:80//`（原始是 `https://lmilive.lmizhibo.com`）
- 登录请求发到了不工作的服务器，导致登录失败

### v11 版本问题
- 只包含 arm64-v8a 架构（107MB），原始 APK 包含双架构（221MB）
- 某些设备需要 armeabi-v7a 架构，导致"与操作系统不兼容"错误

### v12 版本问题
- 刷新按钮使用 `activity.recreate()` 重启整个 App
- 用户体验差，丢失所有状态

## 解决方案

### 1. 保留原始 API 地址
```bash
# 检查 API 地址
strings app.apk | grep -E "lmilive|lmizhibo|81\.71\.248"

# 确保使用原始地址
# ✅ https://lmilive.lmizhibo.com
# ❌ http://81.71.248.163:80//
```

### 2. 保留原始架构
```bash
# 检查架构
unzip -l app.apk | grep "lib/" | grep "\.so$" | awk '{print $NF}' | cut -d'/' -f2 | sort -u

# 输出应包含 arm64-v8a 和 armeabi-v7a
```

### 3. 使用 MethodChannel 通信

#### RefreshHelper.smali（完整实现）
```smali
.class public Lcom/lmi/live/RefreshHelper;
.super Ljava/lang/Object;
.source "RefreshHelper.java"

# interfaces
.implements Landroid/view/View$OnClickListener;

# instance fields
.field private final activityRef:Ljava/lang/ref/WeakReference;
.field private final channel:Lio/flutter/plugin/common/MethodChannel;

# 构造函数
.method public constructor <init>(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
    .locals 1
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    new-instance v0, Ljava/lang/ref/WeakReference;
    invoke-direct {v0, p1}, Ljava/lang/ref/WeakReference;-><init>(Ljava/lang/Object;)V
    iput-object v0, p0, Lcom/lmi/live/RefreshHelper;->activityRef:Ljava/lang/ref/WeakReference;
    iput-object p2, p0, Lcom/lmi/live/RefreshHelper;->channel:Lio/flutter/plugin/common/MethodChannel;
    return-void
.end method

# 添加刷新按钮
.method public static addRefreshButton(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
    .locals 7
    # 创建按钮
    new-instance v0, Landroid/widget/Button;
    invoke-direct {v0, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V
    
    # 设置按钮样式
    const-string v1, "\u21bb"  # ↻ 符号
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V
    const/high16 v1, 0x41800000    # 16.0f
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextSize(F)V
    const v1, -0x44cccccd  # 半透明背景
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setBackgroundColor(I)V
    const/4 v1, -0x1  # 白色文字
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextColor(I)V
    
    # 设置位置（右下角）
    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;
    move-result-object v1
    invoke-virtual {v1}, Landroid/view/Window;->getDecorView()Landroid/view/View;
    move-result-object v1
    check-cast v1, Landroid/view/ViewGroup;
    
    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;
    const/4 v3, -0x2
    invoke-direct {v2, v3, v3}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V
    const/16 v3, 0x55  # Gravity.BOTTOM | Gravity.END
    iput v3, v2, Landroid/widget/FrameLayout$LayoutParams;->gravity:I
    const/16 v3, 0x18
    iput v3, v2, Landroid/widget/FrameLayout$LayoutParams;->bottomMargin:I
    iput v3, v2, Landroid/widget/FrameLayout$LayoutParams;->rightMargin:I
    
    # 设置点击事件
    new-instance v3, Lcom/lmi/live/RefreshHelper;
    invoke-direct {v3, p0, p1}, Lcom/lmi/live/RefreshHelper;-><init>(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
    invoke-virtual {v0, v3}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V
    
    # 添加到视图
    invoke-virtual {v1, v0, v2}, Landroid/view/ViewGroup;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V
    return-void
.end method

# 点击事件处理
.method public onClick(Landroid/view/View;)V
    .locals 3
    iget-object v0, p0, Lcom/lmi/live/RefreshHelper;->activityRef:Ljava/lang/ref/WeakReference;
    invoke-virtual {v0}, Ljava/lang/ref/WeakReference;->get()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/app/Activity;
    
    if-eqz v0, :cond_0
    invoke-virtual {v0}, Landroid/app/Activity;->isFinishing()Z
    move-result v0
    if-nez v0, :cond_0
    
    # 通过 MethodChannel 发送刷新消息
    iget-object v0, p0, Lcom/lmi/live/RefreshHelper;->channel:Lio/flutter/plugin/common/MethodChannel;
    if-eqz v0, :cond_0
    const-string v1, "refreshLiveRoom"
    const/4 v2, 0x0
    invoke-virtual {v0, v1, v2}, Lio/flutter/plugin/common/MethodChannel;->invokeMethod(Ljava/lang/String;Ljava/lang/Object;)V
    
    :cond_0
    return-void
.end method
```

#### MainActivity.smali 修改
```smali
# 1. 添加字段
.field private refreshChannel:Lio/flutter/plugin/common/MethodChannel;

# 2. 在 configureFlutterEngine 中创建 MethodChannel
new-instance v0, Lio/flutter/plugin/common/MethodChannel;
invoke-virtual {p0}, Lcom/lmi/live/MainActivity;->getFlutterEngine()Lio/flutter/embedding/engine/FlutterEngine;
move-result-object v1
invoke-virtual {v1}, Lio/flutter/embedding/engine/FlutterEngine;->getDartExecutor()Lio/flutter/embedding/engine/dart/DartExecutor;
move-result-object v1
invoke-virtual {v1}, Lio/flutter/embedding/engine/dart/DartExecutor;->getBinaryMessenger()Lio/flutter/plugin/common/BinaryMessenger;
move-result-object v1
const-string v2, "com.lmi.live/refresh"
invoke-direct {v0, v1, v2}, Lio/flutter/plugin/common/MethodChannel;-><init>(Lio/flutter/plugin/common/BinaryMessenger;Ljava/lang/String;)V
iput-object v0, p0, Lcom/lmi/live/MainActivity;->refreshChannel:Lio/flutter/plugin/common/MethodChannel;

# 3. 在 onCreate 中调用 addRefreshButton
iget-object v0, p0, Lcom/lmi/live/MainActivity;->refreshChannel:Lio/flutter/plugin/common/MethodChannel;
invoke-static {p0, v0}, Lcom/lmi/live/RefreshHelper;->addRefreshButton(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
```

## 验证结果

### API 地址验证
```bash
strings Lmi_v12_RefreshRoom.apk | grep -E "lmilive|81\.71\.248|lmizhibo"
# 输出应包含 https://lmilive.lmizhibo.com，不包含 81.71.248
```

### 架构验证
```bash
unzip -l Lmi_v12_RefreshRoom.apk | grep "lib/" | grep "\.so$" | awk '{print $NF}' | cut -d'/' -f2 | sort -u
# 输出应包含 arm64-v8a 和 armeabi-v7a
```

### RefreshHelper 验证
```bash
unzip -o Lmi_v12_RefreshRoom.apk classes2.dex -d /tmp/check
strings /tmp/check/classes2.dex | grep "RefreshHelper"
# 输出应包含 Lcom/lmi/live/RefreshHelper; 和 RefreshHelper.java
```

## 关键教训

1. **保留原始 API 地址** - 除非用户明确要求修改，否则不要改变 API 地址
2. **保留原始架构** - 如果原始 APK 包含多架构，修改后也必须包含
3. **使用 MethodChannel** - Flutter App 的功能应该通过 MethodChannel 触发，而不是 Android 层的 `activity.recreate()`
4. **从原始 APK 解码** - 每次修改都从最原始的 APK 开始，不要从已修改的 APK 解码
