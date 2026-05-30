---
name: android-reverse-engineering
description: 安卓逆向工程工具链 — 反编译 APK、去弹窗/收费、改逻辑、重签名
tags: [android, reverse-engineering, jadx, apktool, frida, smali, flutter]
---

# 安卓逆向工程

## 工具链（macOS 已安装）

使用前加 PATH：`export PATH="$HOME/.local/bin:/opt/homebrew/opt/openjdk@21/bin:$PATH"`

| 工具 | 路径 | 版本 | 用途 |
|:-----|:-----|:----:|:-----|
| **JDK 21** | `/opt/homebrew/Cellar/openjdk@21/21.0.11` | 21.0.11 | JADX/APKTool 依赖 |
| **JADX** | `~/.local/bin/jadx` | 1.5.1 | Dex → Java 反编译 |
| **APKTool** | `~/.local/bin/apktool` | 3.0.2 | 解包/回编 APK，改 smali |
| **uber-apk-signer** | `~/.local/bin/uber-apk-signer` | 1.3.0 | 重签名 |
| **mitmproxy** | `/Users/zhoulong/Library/Python/3.9/bin/mitmproxy` | 9.0.1 | API 中间人拦截 |

### GFW 环境安装技巧

```bash
# 连 VPN 再用 brew 安装
scutil --nc start "Shadowrocket"
HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles brew install openjdk@21

# brew 下载队列卡住时删锁重试
rm -f ~/Library/Caches/Homebrew/downloads/*.incomplete
rm -f /opt/homebrew/Library/Locks/*

# pip 安装工具（比 brew 快）
pip3 install mitmproxy
```

JADX 手动下载（先连 VPN）：
```bash
curl -sL "https://github.com/skylot/jadx/releases/download/v1.5.1/jadx-1.5.1.zip" -o /tmp/jadx.zip
# 解压后用 java -jar lib/jadx-1.5.1-all.jar
```

---

## 逆向工作流程

### Phase 0: 识别 App 技术栈

先判断是 Native 还是 Flutter：

```bash
# 1. 检查 AndroidManifest
cat AndroidManifest.xml | grep flutter

# 2. 检查 native libs
ls lib/arm64-v8a/
# 有 libflutter.so + libapp.so → Flutter 应用
# 无 libflutter.so → Native 应用

# 3. Flutter 应用的关键特征
# - manifests: io.flutter.embedding.android.FlutterActivity, flutterEmbedding=2
# - libs: libflutter.so, libapp.so
# - JADX 反编译后业务代码极少（全在 Dart 层）
```

**Flutter vs Native 策略差异：**

| 维度 | Native (Java) | Flutter (Dart) |
|:-----|:-------------|:---------------|
| 业务代码位置 | smali 文件 | `libapp.so`（Dart AOT 编译） |
| JADX 反编译 | ✅ 可读 | ❌ 只能看到引擎层 |
| 快速分析工具 | JADX GUI | `strings libapp.so` |
| 收费弹窗位置 | `AlertDialog`, `Activity` | Dart Widget |
| Frida 拦截 | Hook Java 层 | 需 Hook Dart snapshot 或网络层 |
| 修改方式 | 改 smali | Frida Gadget / MitM / Patch .so |

### Phase 1: 快速分析（strings 优先）

对 Flutter 应用，**strings 分析比 JADX 反编译更有效**。JADX 处理大型 APK（如 221MB）可能卡死或内存不足（需 -Xmx4G 仍可能超时）。

```bash
# 提取关键 API 端点
strings lib/arm64-v8a/libapp.so | grep "/api/\|/app/" | sort -u

# 提取 Dart 函数名（收费相关）
strings libapp.so | grep -iE "ticket|vip|pay|billing|owned|dialog" | sort -u

# 提取 HTTP 方法
strings libapp.so | grep -iE "GET|POST|PUT|DELETE|Content-Type" | sort -u

# 提取所有 URL
strings libapp.so | grep -E "https?://" | grep -v "flutter\|pub.dev" | sort -u
```

### Phase 2: 分析收费模式

通过 Phase 1 的 strings 输出判断收费模式：

**模式 A：自建门票/会员系统 + 服务端 API**
```
特征：API 端点如 /live/ticket/my, /vip/list, /vip/privileges
      Dart 函数如 _hasOwnedRoomTicket, _exitDueToTicket
工作流：App 调 HTTP API → 服务端返回 JSON → Dart 解析 → 弹窗/放行
破解：Frida Gadget + MitM 代理拦截 API 响应（最有效）
```

**模式 B：Google Play Billing（内购）**
```
特征：AndroidManifest 有 BILLING 权限
      smali 中有 com.android.billingclient.api
工作流：Flutter → MethodChannel → Java BillingClient → Google Pay
破解：改 BillingClientImpl.smali 的 queryPurchasesAsync 方法
     或 Frida Hook BillingClient 返回假 Purchase
```

**模式 C：双重校验（自建 API + Google Play）**
```
特征：既有 /ticket/ 系列 API 又有 BILLING 权限
      Google Pay 支付后服务端再记录门票
破解：需要同时拦截 API 响应 + 支付流程
```

### Phase 3: 选定破解方案

#### 方案 A：改 smali（Native 应用，无需 root）

适用于收费逻辑在 Java 层的 Native 应用。

```bash
# 1. 解包
apktool d -o /tmp/decompiled/ target.apk

# 2. 按关键词定位 smali 文件并修改
# 常用修改模式：
#   isVip() 返回 false → 改成 true
#   if-nez v0 :cond  →  goto :cond（跳过条件判断）
#   删除 invoke-virtual AlertDialog.show()

# 3. 回编 + 重签名
apktool b -o /tmp/modified.apk /tmp/decompiled/
uber-apk-signer -a /tmp/modified.apk --allowResign
```

#### 方案 B：Frida Gadget 注入（Flutter 应用，无 root，含 Dart 层 Hook）

对 Flutter 应用，Frida Gadget 可注入到 APK 中，让 App 启动时自动加载 Hook 脚本。**不需要 root**。

**⚠️ 局限性：**
- 只能 Hook Java 层（AlertDialog、BillingClient、MethodChannel 等）
- **Flutter HTTP 调用不走 OkHttp** — Dart 使用自己的 `dart:io` HttpClient 或 `dio` 包，Java 层 Hook OkHttpClient 无效
- Dart 层的 HTTP 请求（如 `/app/live/ticket/my`）只能靠 MitM 代理或 Dart AOT 符号 Hook
- 需要配合符号枚举尝试 Hook Dart AOT 函数（详见 `references/dart-aot-hooking.md`）

```bash
# 1. 下载 Frida Gadget（Android ARM64）
curl -sL "https://github.com/frida/frida/releases/download/16.7.19/frida-gadget-16.7.19-android-arm64.so.xz" -o /tmp/frida-gadget.so.xz
xz -d /tmp/frida-gadget.so.xz

# 2. 注入解包后的 APK
cp /tmp/frida-gadget.so /tmp/unpack/lib/arm64-v8a/libfrida-gadget.so

# 3. 创建配置（文件名必须带 .so 后缀！）
# 脚本用 "code" 字段内联，无需 assets 路径
cat > /tmp/unpack/lib/arm64-v8a/libfrida-gadget.config.so << 'CONFIGEOF'
{
  "interaction": {
    "type": "script",
    "on_change": "reload",
    "code": "/* 脚本内容直接内联 */"
  }
}
CONFIGEOF

# 4. 修改 smali：在 MainActivity.onCreate() 最前面加
#    const-string v0, "frida-gadget"
#    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

# 5. 回编 + 签名
apktool b -o /tmp/mod.apk /tmp/unpack/
uber-apk-signer -a /tmp/mod.apk --allowResign
```

**Dart 层 Hook 流程（实验性）：**

详见 `templates/flutter-dart-aot-hook.js` 和 `references/dart-aot-hooking.md`。

核心思路：
1. 用 `strings` 从 `libapp.so` 提取 Dart 函数名（`_hasOwnedRoomTicket@123456`）
2. Frida 脚本用 `module.enumerateSymbols()` 查找函数地址
3. `Interceptor.attach()` 修改返回值
4. 同时附带 Socket 监控（记录 App 连接了哪些服务器）

**已知问题：** Dart AOT release 编译可能 strip 符号表，此时 `enumerateSymbols()` 返回空。需回退到 MitM 代理方案。

#### 方案 C：MitM 代理拦截（推荐用于 Flutter 应用，需每次挂代理）

最适用于 Flutter 应用场景。前提是 App **没有 SSL pinning（证书固定）**。

**⚠️ 中国手机（华为/小米等）限制：**
- Android 7+ 默认不信任用户安装的 CA 证书
- 华为 HarmonyOS 有额外网络隔离，WiFi 代理对部分 App 不生效
- **优先考虑 Frida Gadget 改包方案**，代理作为备选
- 如用户手机无法安装 CA 证书，见「方案D：嵌入代理CA证书到APK」

**检查 SSL pinning：**
```bash
# 无证书文件 = 大概率无固定
find /tmp/unpack/res -name "*.crt" -o -name "*.pem" -o -name "*.cer"
find /tmp/unpack -name "network_security_config*"
strings libapp.so | grep -iE "pinning|certificate|trust"
```

**修改 APK 信任用户证书（Android 7+ 需要）：**

创建 `res/xml/network_security_config.xml`：

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

在 AndroidManifest.xml 的 `<application>` 标签添加：
```
android:networkSecurityConfig="@xml/network_security_config"
```

**部署步骤：**

模板脚本见 `templates/mitmproxy-bypass-template.py`。

```bash
# 运行代理
mitmproxy -s bypass.py --listen-host 0.0.0.0 --listen-port 8888

# 手机上：WiFi → 代理 → 手动 → IP: Mac局域网IP, Port: 8888
# 安装 CA 证书：手机浏览器访问 http://mitm.it
```

---

#### 方案 D：嵌入代理 CA 证书到 APK（华为/无法安装用户CA时使用）

当用户手机（华为 HarmonyOS 等）**无法安装 mitmproxy 的 CA 证书**时，直接将 CA 证书打包进 APK。这样 App 会信任代理的证书，MitM 代理方案可以正常工作。

**适用场景：**
- 华为 HarmonyOS 禁止安装用户 CA 证书
- 用户不愿意或不会手动安装证书
- 其他 Android 7+ 定制系统不信任用户 CA

**步骤 1：导出 mitmproxy CA 证书**

```bash
ls ~/.mitmproxy/mitmproxy-ca-cert.pem
```

**步骤 2：复制证书到 APK 资源目录**

```bash
mkdir -p /tmp/decoded/res/raw
cp ~/.mitmproxy/mitmproxy-ca-cert.pem /tmp/decoded/res/raw/mitmproxy_ca.pem
```

**步骤 3：修改 network_security_config.xml，添加 `<certificates src="@raw/mitmproxy_ca" />`**

```xml
<base-config cleartextTrafficPermitted="true">
    <trust-anchors>
        <certificates src="system" />
        <certificates src="user" />
        <certificates src="@raw/mitmproxy_ca" />    <!-- 嵌入的 CA 证书 -->
    </trust-anchors>
</base-config>
```

**步骤 4：回编 + 重签名**

```bash
apktool b /tmp/decoded -o /tmp/mod_unsigned.apk
java -jar ~/.local/bin/uber-apk-signer.jar \
  --apks /tmp/mod_unsigned.apk --overwrite --allowResign
```

**步骤 5：用户安装 + 设置 WiFi 代理**

```
1. 卸载原版 App（签名冲突）
2. 安装修改版 APK
3. 手机 WiFi → 代理 → 手动 → IP: Mac局域网IP, Port: 8888
```

---

#### 方案 E：二进制修改 libapp.so API 地址 + 本地 HTTP 代理（Flutter 应用，无需代理，无需证书）

**适用场景：**
- Flutter 应用，方案 B（Frida）和方案 C/D（MitM）均失败
- Dart HTTP 客户端不读系统 WiFi 代理
- 用户手机无法/不愿装 CA 证书
- 最可靠的 Flutter 收费绕过方案

**原理：**
1. Dart AOT 编译的 `libapp.so` 中，Base URL 字符串以明文存储（如 `https://lmilive.lmizhibo.com`）
2. 用二进制替换改为 `http://192.168.0.6:8888/////`（等长替换，维持 snapshot 结构）
3. App 所有 API 请求发到本机 HTTP 端口 → 无 TLS 开销
4. 本机运行 Python HTTP 代理：拦截门票类 API、转发其余到真实服务器

```bash
# 1. 找到 Base URL 字符串
python3 -c "
import zipfile
z = zipfile.ZipFile('app.apk')
d = z.read('lib/arm64-v8a/libapp.so')
s = b'https://lmilive.lmizhibo.com'
i = d.find(s)
print(f'URL at offset {i} ({len(s)} bytes)')
"

# 2. 替换为等长 HTTP 地址
#    https://lmilive.lmizhibo.com  (27 bytes)
#    http://192.168.0.6:8888/////   (27 bytes) — 多余斜杠被代理 strip
REPLACE_WITH = b"http://192.168.0.6:8888/////"
assert len(OLD_URL) == len(REPLACE_WITH), "Length must match!"

# 3. 打包回 ZIP 并重签名
python3 -c "
import zipfile, shutil, tempfile
z = zipfile.ZipFile('app.apk', 'r')
d = z.read('lib/arm64-v8a/libapp.so')
d = d.replace(OLD_URL, REPLACE_WITH)
# 写回新 ZIP
"

java -jar uber-apk-signer.jar --apks mod.apk --overwrite --allowResign
```

**HTTP 代理脚本模板：** `templates/http-forward-proxy.py`

```bash
# 启动代理（Python3 自带，无需额外依赖）
python3 http-forward-proxy.py
```

**代理注意事项：**
- Base URL 后面的多余斜杠（`/////`）在 Python `http.server` 中作为 path，用 `re.sub(r'^/+', '/', path)` 清理
- 代理转发到真实服务器使用 `urllib.request.urlopen(real_url, context=ssl.create_default_context())`
- 如果要修改的字符串不在 `libapp.so` 而在一级索引（如 `.so` 不包含该字符串），检查整个 APK：`grep -a 'https://domain' app.apk`

**验证方法：** 装好改版 APK + 启动代理后，在代理日志中看到 `[FORWARD] GET /app/live/info` 等请求，说明 App 流量已走本机。

**优点：**
- ✅ 无需证书、无需安装代理 CA
- ✅ 无 TLS 开销、无 MITM 兼容性问题
- ✅ 一次改包永久生效（除非 App 版本更新）
- ✅ 可用于华为等无法装用户 CA 的手机

**缺点：**
- ❌ 需 Mac/PC 一直运行代理（手机依赖本机网络）
- ❌ App 更新后需重新改包
- ❌ 字符串长度匹配限制（必须找到等长替换或接受 padding）

---

## JADX 使用注意事项

- 大型 APK（≥100MB）可能卡死 → 跑 `ps aux | grep java` 观察进程状态
- 设置更大堆内存：`java -Xmx4G -jar jadx-1.5.1-all.jar --show-bad-code -d /tmp/out/ app.apk`
- 即使设置 4G 堆，221MB 的 Flutter APK 仍可能被 SIGTERM
- **优先用 `strings libapp.so` 代替 JADX 分析 Flutter 应用**

## 重签名注意事项

- 修改版 APK 签名与原版不同，必须先卸载原版再安装
- `uber-apk-signer` 默认输出 `-aligned-debugSigned.apk` 文件
- 签名验证：`apksigner verify --verbose app.apk`

## 模板文件

| 文件 | 用途 |
|:-----|:-----|
| `templates/flutter-frida-gadget-script.js` | Frida Gadget 脚本模板（AlertDialog + Billing + MethodChannel 拦截） |
| `templates/mitmproxy-bypass-template.py` | MitM 代理拦截脚本模板（含 API 端点自动匹配 + JSON 伪造） |
| `templates/http-forward-proxy.py` | HTTP 正向代理（方案E用，改 API 地址后运行在本机，拦截+转发） |
| `templates/flutter-dart-aot-hook.js` | Dart AOT 符号枚举 + Hook 模板（尝试 Hook libapp.so 原生的 Dart 函数） |
| `references/dart-aot-hooking.md` | Dart AOT 符号表分析指南（strings 提取、函数分类、Hook 方式优先级） |

## Phase 4（扩展）：在 Flutter App 中添加原生叠加层 UI

Flutter 渲染在 `SurfaceView/TextureView` 上，无法直接修改 Flutter 层。但可以通过 **smali 修改在原生 Java 层添加 UI 叠加层**，覆盖在 Flutter 画面之上。

### 适用场景

- 需要一个不依赖 Flutter 内部逻辑的 **刷新/返回/控制按钮**
- 无需修改 Flutter Dart 源码，纯原生安卓层实现
- 按钮点击后触发 `Activity.recreate()`（硬重启直播间）或 MethodChannel 消息

### 实现步骤

**Step 1: 创建 OnClickListener 辅助类（新 smali 文件）**

```smali
# RefreshHelper.smali — 放在对应的 smali_classes* 目录下
.class public Lcom/example/app/RefreshHelper;
.super Ljava/lang/Object;
.source "RefreshHelper.java"
.implements Landroid/view/View$OnClickListener;

.field private final activityRef:Ljava/lang/ref/WeakReference;

.method public constructor <init>(Landroid/app/Activity;)V
    .locals 1
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    new-instance v0, Ljava/lang/ref/WeakReference;
    invoke-direct {v0, p1}, Ljava/lang/ref/WeakReference;-><init>(Ljava/lang/Object;)V
    iput-object v0, p0, Lcom/example/app/RefreshHelper;->activityRef:Ljava/lang/ref/WeakReference;
    return-void
.end method

.method public onClick(Landroid/view/View;)V
    .locals 1
    iget-object v0, p0, Lcom/example/app/RefreshHelper;->activityRef:Ljava/lang/ref/WeakReference;
    invoke-virtual {v0}, Ljava/lang/ref/WeakReference;->get()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/app/Activity;
    if-eqz v0, :cond_0
    invoke-virtual {v0}, Landroid/app/Activity;->isFinishing()Z
    move-result v0
    if-nez v0, :cond_0
    iget-object v0, p0, Lcom/example/app/RefreshHelper;->activityRef:Ljava/lang/ref/WeakReference;
    invoke-virtual {v0}, Ljava/lang/ref/WeakReference;->get()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/app/Activity;
    invoke-virtual {v0}, Landroid/app/Activity;->recreate()V
    :cond_0
    return-void
.end method
```

**Step 2: 添加静态方法创建并注入按钮**

```smali
.method public static addRefreshButton(Landroid/app/Activity;)V
    .locals 7

    # 创建 Button
    new-instance v0, Landroid/widget/Button;
    invoke-direct {v0, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    # 设置文字（如 ↻ 符号）
    const-string v1, "\u21bb"
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V
    const/high16 v1, 0x41800000    # 16.0f
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextSize(F)V

    # 样式：半透明背景 + 白色文字 + 圆角阴影
    const v1, -0x44cccccd    # 0xBB333333
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setBackgroundColor(I)V
    const/4 v1, -0x1
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setTextColor(I)V
    const/16 v1, 0x10
    invoke-virtual {v0, v1, v1, v1, v1}, Landroid/widget/Button;->setPadding(IIII)V
    const/high16 v1, 0x40c00000    # 6.0f
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setElevation(F)V
    const v1, 0x3f59999a    # 0.85f
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setAlpha(F)V

    # 获取 DecorView → ViewGroup
    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;
    move-result-object v1
    invoke-virtual {v1}, Landroid/view/Window;->getDecorView()Landroid/view/View;
    move-result-object v1
    instance-of v2, v1, Landroid/view/ViewGroup;
    if-nez v2, :cond_0
    return-void
    :cond_0
    check-cast v1, Landroid/view/ViewGroup;
    move-object v5, v1

    # LayoutParams: WRAP_CONTENT x WRAP_CONTENT, 右下角
    new-instance v1, Landroid/widget/FrameLayout$LayoutParams;
    const/4 v2, -0x2
    const/4 v3, -0x2
    invoke-direct {v1, v2, v3}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V
    move-object v6, v1
    const/16 v1, 0x55    # Gravity.BOTTOM | Gravity.RIGHT
    iput v1, v6, Landroid/widget/FrameLayout$LayoutParams;->gravity:I
    const/16 v1, 0x18    # 24px margin
    iput v1, v6, Landroid/widget/FrameLayout$LayoutParams;->bottomMargin:I
    iput v1, v6, Landroid/widget/FrameLayout$LayoutParams;->rightMargin:I

    # 设置 OnClickListener + addView
    new-instance v1, Lcom/example/app/RefreshHelper;
    invoke-direct {v1, p0}, Lcom/example/app/RefreshHelper;-><init>(Landroid/app/Activity;)V
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V
    invoke-virtual {v5, v0, v6}, Landroid/view/ViewGroup;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    return-void
.end method
```

**Step 3: 在 MainActivity.onCreate 末尾调用**

```smali
# 修改 onCreate：增加 .locals 1，尾部加：
invoke-static {p0}, Lcom/example/app/RefreshHelper;->addRefreshButton(Landroid/app/Activity;)V
```

**Step 4: 回编 + 签名（同标准流程）**

```bash
apktool b -o mod.apk /tmp/decoded/
java -jar uber-apk-signer.jar --apks mod.apk --overwrite --allowResign
```

### 原理说明

```
┌─────────────────────────────────┐
│  DecorView (FrameLayout)         │
│  ┌───────────────────────────┐  │
│  │  FlutterSurfaceView        │  │
│  │  (Flutter 渲染层)           │  │
│  └───────────────────────────┘  │
│  ┌──────┐                       │
│  │  ↻   │  ← 新加的 Button      │
│  └──────┘                       │
│  (Gravity.BOTTOM|RIGHT + margin)│
└─────────────────────────────────┘
```

- `Activity.recreate()` 会销毁并重建 Activity，Flutter 引擎也随之重启
- 相当于「强制重连直播流」的效果
- 新按钮随着 Activity 重建自动重新添加，不用额外维护

### ⚠️ 关键注意事项

- **WeakReference 是必须的**：防止 Activity 销毁后 Button 持有 Activity 引用导致内存泄漏
- **`.locals 0` → `.locals 1`**：原 onCreate 如果有 `.locals 0` 必须改大，否则 smali 编译报错
- **按钮在 `super.onCreate()` 之后加**：确保 DecorView 已初始化完成
- **`recreate()` 的副作用**：Flutter 应用状态也会重置（导航回首页），适合「硬刷新」场景。如需「软刷新」（如仅刷新直播画面不丢状态），需通过 MethodChannel 向 Flutter 发消息
- **Unicode 字符在 smali 中**：使用 `\uXXXX` 转义，如 `"\u21bb"` 表示 ↻

### 变体：MethodChannel 软刷新（只刷新直播间，不重启 App）

`Activity.recreate()` 会重启整个 App（Flutter 引擎重建，导航回首页）。对于「刷新直播间」这种场景，应通过 MethodChannel 向 Flutter 发消息，让 Flutter 层自行刷新。

**完整实现（4 步）：**

**Step 1: MainActivity.smali 添加 channel 字段**

```smali
# 在 .field 声明区域添加：
.field private refreshChannel:Lio/flutter/plugin/common/MethodChannel;
```

**Step 2: configureFlutterEngine() 中创建 channel**

在 `configureFlutterEngine` 方法末尾、`return-void` 之前添加：

```smali
# 创建 refreshChannel
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
```

**Step 3: RefreshHelper.smali 改为接收 MethodChannel**

```smali
# 构造函数改为接收 Activity + MethodChannel
.method public constructor <init>(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
    .locals 1
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    new-instance v0, Ljava/lang/ref/WeakReference;
    invoke-direct {v0, p1}, Ljava/lang/ref/WeakReference;-><init>(Ljava/lang/Object;)V
    iput-object v0, p0, Lcom/lmi/live/RefreshHelper;->activityRef:Ljava/lang/ref/WeakReference;
    iput-object p2, p0, Lcom/lmi/live/RefreshHelper;->channel:Lio/flutter/plugin/common/MethodChannel;
    return-void
.end method

# addRefreshButton 也改为接收 MethodChannel
.method public static addRefreshButton(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
    # ... 创建 Button 代码不变 ...
    new-instance v1, Lcom/lmi/live/RefreshHelper;
    invoke-direct {v1, p0, p1}, Lcom/lmi/live/RefreshHelper;-><init>(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
    # ... addView 代码不变 ...
.end method

# onClick 改为通过 channel 发消息
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
    iget-object v0, p0, Lcom/lmi/live/RefreshHelper;->channel:Lio/flutter/plugin/common/MethodChannel;
    if-eqz v0, :cond_0
    const-string v1, "refreshLiveRoom"
    const/4 v2, 0x0
    invoke-virtual {v0, v1, v2}, Lio/flutter/plugin/common/MethodChannel;->invokeMethod(Ljava/lang/String;Ljava/lang/Object;)V
    :cond_0
    return-void
.end method
```

**Step 4: onCreate 调用时传入 channel**

```smali
# 原来：invoke-static {p0}, Lcom/lmi/live/RefreshHelper;->addRefreshButton(Landroid/app/Activity;)V
# 改为：
iget-object v0, p0, Lcom/lmi/live/MainActivity;->refreshChannel:Lio/flutter/plugin/common/MethodChannel;
invoke-static {p0, v0}, Lcom/lmi/live/RefreshHelper;->addRefreshButton(Landroid/app/Activity;Lio/flutter/plugin/common/MethodChannel;)V
```

**⚠️ 注意事项：**
- Flutter 端需要注册对应的 MethodChannel 监听器（`MethodChannel('com.lmi.live/refresh').setMethodCallHandler(...)`）
- 如果 Flutter 端没有注册，`invokeMethod` 会静默失败（不会崩溃）
- channel name 必须两端一致（如 `com.lmi.live/refresh`）
- 用 `strings libapp.so | grep -i "refresh\|method.*channel"` 找 Flutter 端已有的 channel name，避免冲突

---

## 已知陷阱

### ⚠️ Flutter 应用：JADX 看不到业务代码
收费弹窗在 Dart Widget 层（编译到 `libapp.so`），不在 smali 中。修改 smali 层只能影响 Java 原生组件（AlertDialog、Activity 等）。

### ⚠️ Flutter HTTP 不走 Java 层 —— Frida Java Hook 无效
Dart 应用使用自己的 HTTP 客户端（`dart:io` HttpClient 或 `dio` 包），**完全绕过 Java 层的 OkHttp/HttpURLConnection**。
- Frida 在 Java 层 Hook OkHttpClient、MethodChannel **对 Dart HTTP 请求无效**
- 拦截 Flutter HTTP 的唯一手段：
  1. **MitM 代理**（前提：无 SSL pinning + 用户可安装 CA 证书）
  2. **Hook Dart AOT 函数**（实验性，release 版符号表可能被 strip）
  3. **Hook libc 的 connect/send/recv**（但 HTTPS 内容加密，只能看到 IP:port）
  4. **二进制改 libapp.so 字串**（见方案E：直接改 API 地址到本地 HTTP 代理）✅ 最可靠

### ⚠️ Flutter Dart HTTP 客户端不读系统 WiFi 代理（Android 关键坑）

这是 Android 平台 Flutter 应用和 Native 应用的一个关键行为差异：

- **Native 应用**（Java/Kotlin OkHttp）：遵守 WiFi 设置里的「手动代理」→ 流量走代理
- **Flutter 应用**（Dart `dart:io` HttpClient）：**忽略 WiFi 代理设置** → 直连服务器

**表现：** mitmdump 日志里只有华为系统服务的流量（`connectivitycheck.*`、`grs.dbankcloud.*`、`hwid-drcn.*` 等），**看不到 App 目标域名的任何请求**（如 `lmilive.lmizhibo.com`）。

**原因：** Flutter 的 Dart HTTP 客户端通过封装原生 socket（`libc.connect`）直接建立 TCP 连接，不走 Java 层的 ProxySelector。WiFi 代理设置是通过 Android 的 `ProxySelector.setDefault()` 配置的 Java 层行为，Dart socket 不读取此配置。

**解决方案（按可靠性排序）：**

| 方案 | 原理 | 可靠性 |
|:-----|:-----|:------:|
| **方案E：二进制改 libapp.so URL** | 把 App 的 API 地址改成本机 HTTP 地址 → 本地 HTTP 代理 | ✅ 最高 |
| **方案D：嵌入 CA 到 APK + DNS 劫持** | 改 DNS 解析 + 透明代理（需 root/ARP 毒化/自定义 DNS） | ⚠️ 复杂 |
| **方案C：嵌入 CA 到 APK + WiFi 代理** | 对 Native 应用有效，对 Flutter 应用因不读代理而**无效** | ❌ 无效 |
| **浅层方案：VPN 热点** | Mac 开热点让手机连，在 Mac 上做透明代理 | ⚠️ 可行但复杂 |

**诊断方法：** 设好 WiFi 代理后运行 `mitmdump`，观察日志中是否出现目标域名。如果没有（只有华为/小米系统服务），说明 Dart HTTP 不读代理。

### ⚠️ 服务端强验票
即使客户端拦截了弹窗，服务端可能拒绝发送直播流。表现：点击取消支付后返回直播间黑屏。此时需 MitM 代理方案或改 `libapp.so`。

### ⚠️ TRTC/腾讯云音视频：无法提取标准流 URL
使用腾讯 TRTC（或七牛云 RTC）的直播 App，视频通过专有协议传输。即使拿到鉴权参数（sdkAppId + userId + userSig + roomId），也无法在 VLC/MPV 等播放器播放。
- **不要承诺用户「提取出 RTMP/FLV/HLS 链接」** — TRTC 不走这些协议
- 鉴权参数本身有时效（几分钟到几小时），非长期有效
- 唯一可靠的观看途径是 App 本身（或 Web 版 TRTC SDK）
- 可通过 Frida 拦截 `/app/live/info` 等 API 的响应体来确认返回的是 TRTC 参数还是 CDN 流地址

### ⚠️ 架构选择：保留原始 APK 的所有 CPU 架构

华为/小米等主流手机是 arm64（`arm64-v8a`），但旧款或低端机可能是 32 位（`armeabi-v7a`）。

```bash
# 检查目标设备架构
adb shell getprop ro.product.cpu.abi

# 检查 APK 包含哪些架构
unzip -l app.apk | grep "lib/" | awk '{print $NF}' | cut -d'/' -f2 | sort -u
```

**关键规则：修改后的 APK 必须保留原始 APK 的所有架构目录。**

**Lmi 实战教训（2026-05-29）：**
- 原始 APK 包含 `arm64-v8a` + `armeabi-v7a`（221MB）
- apktool 解码后只保留了 `arm64-v8a`（107MB）
- 结果：部分设备报「与操作系统不兼容」安装失败
- 修复：从包含所有架构的原始 APK 重新制作

**检查清单：**
```bash
# 解码前记录原始架构列表
ORIG_ARCHS=$(unzip -l original.apk | grep "lib/" | awk '{print $NF}' | cut -d'/' -f2 | sort -u)
echo "原始架构: $ORIG_ARCHS"

# 回编后验证架构列表是否一致
NEW_ARCHS=$(unzip -l modified.apk | grep "lib/" | awk '{print $NF}' | cut -d'/' -f2 | sort -u)
echo "修改后架构: $NEW_ARCHS"

diff <(echo "$ORIG_ARCHS") <(echo "$NEW_ARCHS") && echo "✅ 架构一致" || echo "❌ 架构丢失！"
```

- 只注入 `arm64-v8a` 的 Gadget → arm64 手机正常，32 位手机闪退
- 建议所有架构都注入，避免兼容性问题

### ⚠️ App 有加固
360加固、腾讯加固等需先脱壳。脱壳工具：frida-decrypt、BlackDex。

### ⚠️ 签名校验
启动闪退 → 在 smali 中搜 `signature`、`getPackageManager`、`signingInfo` 跳过校验逻辑。

### ⚠️ 改 API 地址会破坏登录/认证（方案E 的致命副作用）

使用方案E（二进制改 libapp.so API 地址）时，**Base URL 被替换后，所有 API 请求（包括登录）都会发到新地址**。如果新地址（如本机 HTTP 代理）没有实现登录接口，用户将无法登录。

**Lmi 实战教训（2026-05-29）：**
- v10 把 `https://lmilive.lmizhibo.com` 改成了 `http://81.71.248.163:80//`
- 该 IP 没有登录服务 → 用户登录失败
- v11 从原始 APK 重新制作，保留原始 API 地址，只添加 RefreshHelper 按钮 → 登录恢复正常

**正确做法：区分「功能性修改」和「网络层修改」**

| 修改类型 | 改什么 | 能改 API 地址？ |
|:---------|:-------|:---------------|
| 添加 UI 叠加层（按钮等） | smali 层 | ❌ 不改 |
| 去弹窗/改收费逻辑 | smali 层 | ❌ 不改 |
| MitM 代理拦截（方案E） | libapp.so | ✅ 改，但代理必须实现所有必要端点 |
| 本地 HTTP 代理转发 | libapp.so | ✅ 改，代理转发到真实服务器 |

**规则：除非你同时运行一个完整的代理转发服务，否则不要改 API 地址。**

### ⚠️ 重构时必须从原始 APK 解码，不要从已修改的 APK 再解码

在同一 App 的多次修改迭代中，**每次都从原始未修改的 APK 解码**，不要从上次修改后回编的 APK 再次解码。

**错误做法（会导致安装失败）：**
```bash
# 第一轮：从原始 APK 解码
apktool d -o v1 original.apk       # ✅ 正确
# ... 修改 ... 回编签名 → app_v1.apk

# 第二轮：从修改版解码
apktool d -o v2 app_v1.apk         # ❌ 错误！从已修改的 APK 解码
# ... 再改 ... 回编签名 → app_v2.apk  # 此时安装可能失败
```

**正确做法：**
```bash
# 每一轮都从原始 APK 解码
apktool d -o v1 original.apk       # 第一轮
apktool d -o v2 original.apk       # 第二轮（盖掉 v1，或分别保存）
# 两轮各修各的，确保基础一致
```

**原因：**
- 已回编的 APK 经过 apktool 重新打包，dex 结构、资源对齐可能有细微差异
- 从已修改的 APK 再次解码→回编，这些差异累积可能导致 APK 在特定机型（如华为 HarmonyOS/EMUI）上安装失败，提示「无效安装包」或「与操作系统不兼容」
- `apktool d -r`（保留原始资源模式）尤其容易触发此问题

**最佳实践：**
- 保留原始 APK 的副本，每次重新解码
- 用脚本化记录修改内容（smali patch、二进制替换），而不是靠修改后的 APK 作为中间产物

### ⚠️ apktool 回编资源错误：`$avd_hide_password__2` 缺失

apktool 解码后回编时，可能报错：
```
error: resource drawable/$avd_hide_password__2 (aka com.lmi.live:drawable/$avd_hide_password__2) not found.
```

**原因：** 原始 APK 中的 `res/drawable/avd_hide_password.xml` 引用了 `$avd_hide_password__2` 动画资源，但 apktool 解码时丢失了该文件（只有 `__0` 和 `__1`）。

**修复：** 创建空的 stub XML 文件：
```bash
cat > res/drawable/\$avd_hide_password__2.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
</set>
EOF
```

然后重新 `apktool b` 即可。这个空动画不影响 App 运行（只是密码隐藏图标的过渡动画）。

### ⚠️ 安装失败诊断：「无效安装包」或「与操作系统不兼容」

Android 安装 APK 失败的常见原因及修复：

| 错误提示 | 原因 | 修复 |
|:---------|:-----|:-----|
| **无效安装包** | APK 结构损坏（从已修改的 APK 再次解码累积错误） | 从原始 APK 重新解码制作 |
| **与操作系统不兼容** | APK 缺少设备所需的 CPU 架构（如只有 arm64 但设备需要 armeabi-v7a） | 保留原始 APK 的所有架构目录 |
| **签名冲突** | 已安装同包名但不同签名的 APK | 先卸载旧版再安装 |
| **解析包时出现问题** | APK 文件下载不完整或被截断 | 重新下载，检查文件完整性 |

**快速诊断流程：**
```bash
# 1. 检查 APK 完整性
unzip -t app.apk | tail -3  # "No errors detected" = OK

# 2. 检查签名
apksigner verify --verbose app.apk

# 3. 检查架构覆盖
unzip -l app.apk | grep "lib/" | awk '{print $NF}' | cut -d'/' -f2 | sort -u

# 4. 检查 AndroidManifest 是否有效
unzip -p app.apk AndroidManifest.xml | xxd | head -3
# 有效: 第一字节 03 (binary XML)
# 无效: 乱码或 00 填充
```

### ⚠️ 签名使用内置 debug keystore（华为兼容性）

华为 Mate30 / HarmonyOS / EMUI 设备对 APK 签名证书更敏感。**推荐用 uber-apk-signer 的内置 debug keystore**（无需指定 `--ks` 参数）而不是自定义创建的 keystore。

```bash
# ✅ 推荐：内置 debug keystore（自动使用，兼容性最好）
java -jar uber-apk-signer.jar --apks app.apk --overwrite --allowResign

# ❌ 避免：自定义 keystore（可能被华为拒绝）
java -jar uber-apk-signer.jar --apks app.apk --ks ~/.android/debug.keystore --ksAlias androiddebugkey ...
```

uber-apk-signer 内置的标准 Android debug 证书（CN=Android Debug, OU=Android, O=US, L=US, ST=US, C=US）在所有 Android 设备上兼容性最好。新创建的 debug keystore 签名指纹不同，可能触发华为的额外校验。

### ⚠️ APK 文件可能有非标准扩展名

用户提供 APK 文件时，扩展名可能不是 `.apk`，如：
- `app-release (2).apk.1` — 下载工具添加的序号
- `app-release.apk.zip` — 重命名过的
- 无扩展名

用 `file` 命令仍可识别：`file app-release (2).apk.1` → `Zip archive data`

**处理方式：** 复制为 `.apk` 后缀再操作：
```bash
cp "app-release (2).apk.1" /tmp/work/app-release.apk
```

### ⚠️ 验证 APK 编译结果：smali 文件在 dex 中不可见
`apktool b` 编译后，所有 smali 文件被编译合并到 `classes.dex` / `classes2.dex` / `classes3.dex` 中。如果用 `zipfile.namelist()` 搜索新增的 smali 类的文件名，**找不到是正常的**。

正确验证方式：
```python
import zipfile
with zipfile.ZipFile('output.apk') as z:
    dex_data = z.read('classes2.dex')  # 或 classes.dex
    if b'YourNewClass' in dex_data:    # 搜索类名字符串
        print('✅ 类已编译到 dex 中')
```

## 参考案例

- `references/lmi-live-app-analysis.md` — Lmi 直播 App 完整逆向分析报告（Flutter + 自建门票系统 + Google Play Billing v7.1.1）
- `references/lmi-api-enumeration.md` — Lmi API 端点枚举结果（2026-05-30）：全部需要认证、无公开端点、无网页版
- `references/trtc-live-streaming.md` — TRTC（腾讯云实时音视频）直播协议说明：为何无法提取 RTMP/FLV/HLS 流 URL，API 端点一览，CDN 转推判断方式
- `references/trtc-live-streaming.md` — TRTC（腾讯云实时音视频）直播协议说明：为何无法提取 RTMP/FLV/HLS 流 URL，API 端点一览，CDN 转推判断方式
