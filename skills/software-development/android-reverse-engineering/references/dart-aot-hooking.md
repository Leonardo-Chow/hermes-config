# Dart AOT 符号表分析与 Frida Hook

## Dart AOT 编译原理（Flutter Release 模式）

Flutter release 模式的 APK 中，Dart 代码被 AOT（Ahead-of-Time）编译为 `libapp.so`。这是**原生 ARM64 机器码**，不是解释执行的。

## 关键特征

| 特征 | 说明 |
|:-----|:-----|
| 文件名 | `lib/arm64-v8a/libapp.so` 或 `lib/armeabi-v7a/libapp.so` |
| 大小 | 通常 5-20MB（取决于 Dart 代码量） |
| nm -D 输出 | 仅 5 个 ELF 动态符号：`_kDartVmSnapshotData`, `_kDartVmSnapshotInstructions`, `_kDartIsolateSnapshotData`, `_kDartIsolateSnapshotInstructions`, `_kDartSnapshotBuildId` |
| 业务函数 | **不在动态符号表**中，`nm -D` 看不到。嵌入在 snapshot 指令段内 |
| strings 命令 | ✅ 能提取函数名、API 端点、错误消息（.rodata 段中的调试/日志字符串） |
| JADX 反编译 | ❌ 看不到业务代码 |

## libapp.so 中字符串的存储与定位（方案E基础）

Dart AOT 编译会将代码中的字符串常量（Base URL、API 路径、错误消息等）以**明文 ASCII/UTF-8** 形式存储在 `libapp.so` 的 `.rodata` 段。这是逆向 Flutter 应用的核心优势：**不需要反编译，直接用字符串搜索即可定位关键配置**。

### 字符串定位方法

```python
import zipfile
z = zipfile.ZipFile("app.apk")
d = z.read("lib/arm64-v8a/libapp.so")

target = b"https://api.example.com"
idx = d.find(target)
if idx >= 0:
    print(f"Found at offset {idx}")
    print(f"Occurrences: {d.count(target)}")
    # 查看上下文（确认是 Dart 字符串对象中的字面量）
    ctx_start = max(0, idx - 30)
    ctx_end = min(len(d), idx + len(target) + 30)
    print(f"Context: {d[ctx_start:ctx_end]}")
```

### 二进制字符串替换（方案E核心）

Dart AOT snapshot 中，字符串长度信息存储在对象头的专门字段中（不是 null terminated），因此：

**核心规则：替换字符串必须与原字符串等长**
- `len(OLD) == len(NEW)` 是强制约束
- 不等长会破坏 snapshot 结构 → App 运行时闪退

**不等长时的 padding 策略：**
- 用 URL 安全的字符填充尾部
- `https://lmilive.lmizhibo.com` (27 bytes) → `http://192.168.0.6:8888/////` (27 bytes)
  多余的斜杠由代理端用 `re.sub(r'^/+', '/', path)` 清理
- **不要用 null 字节 padding** — Dart 不靠 null 结尾，但 null 在 URL 解析时会报错

**修改并重建 APK：**
```python
import zipfile

zin = zipfile.ZipFile("app.apk", "r")
data = bytearray(zin.read("lib/arm64-v8a/libapp.so"))

OLD = b"https://api.example.com"
NEW = b"http://192.168.0.6:8888/////"

assert len(OLD) == len(NEW), f"Length mismatch!"
assert data.count(OLD) == 1, f"Expected 1 occurrence, got {data.count(OLD)}"

data = data.replace(OLD, NEW)

# 重建 ZIP（必须重建以更新 checksum）
with zipfile.ZipFile("app_patched.apk", "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == "lib/arm64-v8a/libapp.so":
            zout.writestr(item, bytes(data))
        else:
            zout.writestr(item, zin.read(item.filename))
zin.close()
```

## 分析流程

### 1. 提取所有 Dart 函数名

```bash
# 全部函数（带 @number 消歧后缀）
strings libapp.so | grep -E '^_[a-zA-Z]+@[0-9]+$' | sort

# 按用途筛选
strings libapp.so | grep -iE "ticket|vip|pay|billing|owned|dialog|purchase|room|live|stream" | sort -u

# 提取 API 端点
strings libapp.so | grep "/api/\|/app/" | sort -u

# 提取域名和 base URL
strings libapp.so | grep -E "https?://" | grep -v "flutter\|pub.dev\|google\|bugly" | sort -u
```

### 2. 审计 `nm -D` 确认符号存在性

在深入 Frida Hook 之前，先确认动态符号表是否有目标函数：

```bash
nm -D lib/arm64-v8a/libapp.so
# 输出示例：
# 0000000000004ac0 R _kDartIsolateSnapshotData
# 0000000000546940 T _kDartIsolateSnapshotInstructions
# 00000000000001c8 R _kDartSnapshotBuildId
# 0000000000000340 R _kDartVmSnapshotData
# 0000000000530000 T _kDartVmSnapshotInstructions
```

如果只有这 5 个 snapshot 符号 → `enumerateSymbols()` 在 Frida 中只能找到这些，**找不到业务函数名**。

### 3. 分类识别关键函数

以门票系统为例，函数可分以下几类：

| 类别 | 函数模式 | 破解方式 |
|:-----|:---------|:---------|
| **权限检测** | `_hasOwned*`, `_isTicket*`, `_canEnter*`, `_isVip*` | 强制返回 true |
| **退出/阻断** | `_exitDueTo*`, `_pausePlayback*`, `_safeExit*` | 跳过/NOP |
| **UI 弹窗** | `_show*Dialog*`, `_buildTicket*`, `_show*Pay*` | 阻止执行 |
| **数据加载** | `_load*Data*`, `_fetch*Price*`, `_parseMy*` | 伪造返回空/成功 |
| **支付** | `_buyTicket*`, `_startPayment*`, `_purchase*` | 阻拦 |

### 4. 符号查找方式（按优先级）

**方式 A：`enumerateSymbols()`（推荐，但当 nm -D 只有 snapshot 符号时失效）**
```javascript
var module = Process.getModuleByName("libapp.so");
var symbols = module.enumerateSymbols();
for (var i = 0; i < symbols.length; i++) {
    if (symbols[i].name.indexOf("_hasOwnedRoomTicket") >= 0) {
        console.log("Found at " + symbols[i].address);
    }
}
```

**方式 B：`Memory.scanSync()`（备选，扫描 .rodata 段搜索函数名字符串）**
```javascript
var module = Process.getModuleByName("libapp.so");
var scan = Memory.scanSync(module.base, module.size, "_hasOwnedRoomTicket");
// 注意：这里找到的是字符串地址（在 .rodata 段），不是函数入口
```

**方式 C：`Module.findExportByName()`（最直接，但 Dart AOT 函数不在 .dynsym 中，失败）**
```javascript
var addr = Module.findExportByName("libapp.so", "_hasOwnedRoomTicket@953456253");
// Dart AOT 函数不在 ELF 动态符号表中，此法常失败
```

### 5. Hook 模式示例

```javascript
function hookReturnTrue(module, name) {
    var symbols = module.enumerateSymbols();
    for (var i = 0; i < symbols.length; i++) {
        if (symbols[i].name.indexOf(name) >= 0) {
            Interceptor.attach(symbols[i].address, {
                onEnter: function(args) {
                    console.log("[HACK] " + name + " called");
                },
                onLeave: function(retval) {
                    retval.replace(ptr(1)); // return true (1)
                }
            });
            return true;
        }
    }
    return false;
}

// 使用
var mod = Process.getModuleByName("libapp.so");
hookReturnTrue(mod, "_hasOwnedRoomTicket");
hookReturnTrue(mod, "_isTicketOwned");
```

## 已知陷阱

### ❌ `nm -D` 只有 5 个 snapshot 符号
Dart AOT release 编译不将业务函数名导出为 ELF 动态符号。经实测 Lmi Live（221MB APK）：
```
nm -D lib/arm64-v8a/libapp.so  →  5 symbols (全部 snapshot 相关)
```
此时 `module.enumerateSymbols()` 只返回这 5 个符号，Hook 脚本找不到任何 Dart 函数。

**解决方案：**
- 放弃 `enumerateSymbols()`，改用 `strings libapp.so` 提取函数名后尝试 `Memory.scanSync()`
- 或回退到 **MitM 代理方案**（前提：用户能安装 CA 证书或嵌入 CA 到 APK）
- 或只 Hook **Java 层**（AlertDialog、BillingClient 等——注意：这对 Flutter HTTP 无效）

### ❌ 返回值类型不确定
Dart bool 在 AOT 中可能用 0/1（标准 ARM64），也可能用 Dart 内部布尔值（非 0/1）。Hook 后 `retval.replace(ptr(1))` 可能不生效。

### ❌ 函数地址不对齐
Dart AOT 函数可能不是标准的 4 字节对齐。`Interceptor.attach()` 可能会报错。

### ❌ Frida Gadget Java Hook ≠ Dart HTTP 拦截
Flutter App 的 Dart 层使用自己的 HTTP 客户端（`dart:io` HttpClient 或 `dio` 包）：
- **Java 层 Hook OkHttpClient → 对 Dart HTTP 请求无效**
- **Java 层 Hook MethodChannel → 仅拦截 Flutter→Native 通道，不拦截 HTTP 请求**
- **Java 层 Hook AlertDialog.show → Flutter Widget 弹窗不触发 AlertDialog**
- Flutter 的弹窗是 Dart Widget，在 Flutter 引擎内部渲染，不会调用 `android.app.AlertDialog`
- 结论：**Frida Gadget 的 Java Hook 无法拦截 Flutter 应用的 HTTP 流量和弹窗**

### ❌ libc.connect/send/recv Hook 只能看到加密数据
即使 hook `libc` 的 socket 函数：
```javascript
var connect = Module.findExportByName("libc.so", "connect");
Interceptor.attach(connect, {
    onEnter: function(args) {
        // 只能看到 IP:port，看不到请求内容（HTTPS 加密）
    }
});
```
- 可以监控 App 连接了哪些服务器（IP:port）
- 但 HTTPS 流量已加密，无法看到 HTTP 请求/响应内容
- 只能用于了解 App 的服务器架构，不能用于绕过收费

## 兜底方案

当 `enumerateSymbols()` 找不到目标函数时，回退策略：

1. **Frida Gadget + Java 层 Hook（最稳定，但局限大）**：拦截 AlertDialog、BillingClient、MethodChannel、WebView。**仅限弹窗/支付在 Java 层处理的情况**，对 Flutter 应用几乎无效。
2. **MitM 代理**：绕过 App 内部逻辑，直接在网络层拦截 API 响应。**推荐方案**，详见主 skill 的「方案C」和「方案D」。
3. **嵌入 CA 证书到 APK**：当用户手机无法安装 CA 证书时（华为等），将 mitmproxy CA 打包进 APK。详见主 skill 的「方案D：嵌入代理CA证书到APK」。
4. **二进制改 libapp.so 字串（方案E）**：直接替换 `libapp.so` 中的 Base URL 字符串，将 HTTPS API 重定向到本地 HTTP 代理。**最可靠**，详见主 skill 的「方案E：二进制修改 libapp.so API 地址 + 本地 HTTP 代理」。
5. **逆向替代工具**：
   - `objection` — 运行时探索和 Hook
   - Frida's `Stalker` — 代码追踪
6. **整体思维**：先找最简单的入口，不要死磕一个点。如果 Dart Hook 不可行，优先试 MitM 代理。如果 MitM 因 Flutter 不读代理而失败，直接试方案E。
