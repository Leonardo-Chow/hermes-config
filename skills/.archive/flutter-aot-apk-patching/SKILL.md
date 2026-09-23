---
name: flutter-aot-apk-patching
description: Flutter AOT APK 逆向工程方法论 — 网络 API 端点提取 + Dart AOT snapshot 二进制修改 + HTTP 代理拦截，用于绕过付费检查、弹窗、API 限制等。
---

# Flutter AOT APK 修改方法论

用于修改 Flutter AOT 编译的 Android APK，核心思路是通过 **多层叠加** 确保绕过逻辑生效。

## Phase 1: 网络信息提取（修补前必做）

在修改 APK 之前，先从 APK 中提取网络 API 端点、域名和认证方式。

### 提取域名和 API 端点

```bash
# 找到所有 API 路径（Flutter 应用通常以 /app/ 开头）
strings app.apk | grep -E '^/app/' | sort -u

# 找到 HTTP URL（过滤 SDK/广告库噪音）
strings app.apk | grep -E 'https?://' | grep -v 'com\.android\|google\|facebook\|tencent\|huawei\|amazon' | sort -u

# 找到包级 Dart imports（提示架构分层）
strings app.apk | grep -E 'package:.*services/' | sort -u
```

### 测试端点和识别认证

```bash
# 测试公开端点
curl -sk "https://<domain>/app/live/info?roomId=ROOM_ID" -H "User-Agent: AppName/1.0"
# 200 + 数据 → 公开 API；401 "未能读取到有效 token" → 需要认证

# 搜索认证相关字符串
strings app.apk | grep -iE 'token|authorization|bearer|auth.*key|secret|header'
```

常见认证模式：`lmi-live-token`（自定义 Header）、`Authorization: Bearer xxx`（JWT）、`x-auth-token`（自定义 Header）。

### 用代理拦截获取 Token

当 API 需要认证时，通过 mitmproxy 拦截已登录请求提取 token：
```bash
mitmdump --listen-host 0.0.0.0 --listen-port 8888
```
手机设置代理 → 打开 App → 发起请求 → 抓到完整 header。

### TRTC 直播流特征

- 使用腾讯云 TRTC SDK（libTXRTC.*.so）
- 拉流地址不是静态 RTMP/HLS，而是动态协商生成
- 通常需要 sdkAppId + userId + userSig + roomId 四元组
- License URL: `https://*.trtcube-license.cn/license/`

> **完整 API 端点参考**：`references/lmi-live-api-example.md`

## 三层方案（从简单到复杂）

### 第一层：API 重定向（最有效）
1. **找到 API base URL** — 在 `libapp.so` 中找到字符串如 `https://xxx.com`
2. **同长度替换** — 替换为指向本地 HTTP proxy 的地址（必须同字节数）
   - 用 `python3 zipfile` 提取、修改、写回压缩包
   - 原 27 字节 `https://lmilive.lmizhibo.com` → `http://192.168.0.6:8888/////`（27 字节）
   - **关键**：必须同字节长度！用斜杠/点号填充补齐
   ```python
   TARGET = b"https://example.com"  # 27 bytes
   REPLACE = b"http://192.168.0.6:8888/////"  # 27 bytes
   ```
3. **运行 HTTP proxy** — 在本机监听，拦截门票/VIP/余额 API，返回伪造成功响应
4. **需要受控环境**：用户手机 WiFi 代理指向本机

### 第二层：Dart AOT 字符串 patching
1. 在 `libapp.so` 中搜索关键字符串（如 `"OPEN"`, `"PAID"`, `"isPaid"`）
2. 确认只出现一次后，同长度替换
   - `"OPEN"` (4 bytes) → `"OPEE"` (4 bytes) 让比较永远失败
3. 用 `zipfile` 直接在压缩包内替换，无需 apktool

### 第三层：埋入 Frida Gadget（最后防线）
1. 注入 `frida-gadget.so` 到 `lib/arm64-v8a/`
2. 添加 `frida-script.js` 到 `assets/`
3. 配置 `libfrida-gadget.config.so` 以 `interaction.type = "script"` 自动运行
4. **局限**：Java Hook 打不到 Flutter Dart HTTP 层，需要 hook 网络层

## 工具链

### 必备工具
- **APKTool** — 全量反编译/重编译
- **uber-apk-signer** — 重签名（debug keystore 内置）
- **JADX** — Java 反编译
- **JDK 21** — Java 运行环境

### 分析命令
```bash
# 搜索关键字符串
strings /tmp/app.apk | grep -iE 'api|token|ticket|paid'

# 在 libapp.so 中搜索（Dart AOT snapshot）
python3 -c "
import zipfile
z = zipfile.ZipFile('app.apk')
d = z.read('lib/arm64-v8a/libapp.so')
idx = d.find(b'TARGET_STRING')
print(f'Found at offset {idx}, ctx={d[idx-10:idx+30]}')
"

# 统计字符串出现次数
python3 -c "
import zipfile
z = zipfile.ZipFile('app.apk')
d = z.read('lib/arm64-v8a/libapp.so')
print(d.count(b'OPEN'))  # 确认只出现一次
"

# 签名 APK
/opt/homebrew/opt/openjdk@21/bin/java -jar /Users/zhoulong/.local/bin/uber-apk-signer.jar \
  --apks /path/to/app.apk --overwrite --allowResign
```

## 本地 HTTP Proxy 实现

```python
# 核心逻辑：拦截 → 修改响应 → 转发
class Proxy(http.server.BaseHTTPRequestHandler):
    def _handle(self, method):
        if self._is_ticket_api(path):
            return fake_ticket_response()
        
        # 修改 room info 响应中的关键字段
        if "/app/live/info" in path:
            resp_data = self._forward_to_real_server(method, path, body)
            resp_json = json.loads(resp_data)
            if resp_json["data"]["liveRoomInfo"].get("isPaid") == "OPEN":
                resp_json["data"]["liveRoomInfo"]["isPaid"] = "CLOSED"
                resp_json["data"]["liveRoomInfo"]["ticketPrice"] = 0
                resp_data = json.dumps(resp_json, ensure_ascii=False)
            return resp_data
        
        return self._forward_to_real_server(method, path, body)
```

## 添加功能到 Flutter App（Smali + MethodChannel）

当需要给 Flutter App 添加原生 UI 功能（如刷新按钮）时，**必须通过 MethodChannel 与 Flutter 层通信**，而不是用 Android 层的方案。

### ❌ 错误方案：activity.recreate()
```smali
# 这会重启整个 App，用户体验差
invoke-virtual {v0}, Landroid/app/Activity;->recreate()V
```

### ✅ 正确方案：MethodChannel 通信
```smali
# 1. 在 MainActivity 中创建 MethodChannel
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

# 2. 在 RefreshHelper 中调用 MethodChannel
iget-object v0, p0, Lcom/lmi/live/RefreshHelper;->channel:Lio/flutter/plugin/common/MethodChannel;
const-string v1, "refreshLiveRoom"
const/4 v2, 0x0
invoke-virtual {v0, v1, v2}, Lio/flutter/plugin/common/MethodChannel;->invokeMethod(Ljava/lang/String;Ljava/lang/Object;)V
```

### 关键点
- Flutter App 的业务逻辑在 Dart 层，原生层只是容器
- `activity.recreate()` 会重启整个 App，丢失所有状态
- MethodChannel 可以触发 Flutter 层的特定功能（如刷新直播间播放地址）
- 在 libapp.so 中搜索 `refresh`、`reload` 等关键词，找到 Flutter 层的刷新方法

## 架构保留

**修改 APK 时必须保留原始架构**，否则会导致"与操作系统不兼容"错误：

```bash
# 检查原始 APK 包含哪些架构
unzip -l app.apk | grep "lib/" | grep "\.so$" | awk '{print $NF}' | cut -d'/' -f2 | sort -u

# 如果原始 APK 包含多架构（如 arm64-v8a + armeabi-v7a），
# 修改后的 APK 也必须包含相同架构
```

### 常见错误
- 原始 APK 221MB（双架构）→ 修改后 107MB（仅 arm64）→ 安装失败
- 某些设备（特别是低端机）只支持 armeabi-v7a，缺少该架构会安装失败

## 资源编译错误修复

apktool 打包时可能遇到资源缺失错误：

```
error: resource drawable/$avd_hide_password__2 not found
```

### 解决方案
```bash
# 1. 找到缺失的资源文件
ls app-decoded/res/drawable/ | grep avd_hide_password

# 2. 创建空的资源文件
cat > app-decoded/res/drawable/\$avd_hide_password__2.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
</set>
EOF

# 3. 重新打包
apktool b app-decoded -o app-modified.apk
```

## ⚠️ ARM64 函数二进制 patching 极不可靠

尝试通过搜索 ARM64 函数序言（`stp x29, x30, [sp, #-N]!`）来定位 libapp.so 中的 Dart AOT 编译函数并 patch 为 `ret` 指令，**成功率极低**：

- Dart AOT 编译器不生成标准 ARM64 函数序言
- 函数边界难以确定（没有 symbol table）
- 搜索 `stp x29, x30` 模式可能匹配到数据区而非代码区

**正确做法：** 不要尝试 patch libapp.so 中的单个函数。用以下替代方案：
1. **拦截 MethodChannel**（推荐）— 在 smali 层替换 `setMethodCallHandler` 为空实现
2. **API 重.redirect + 本地代理** — 改 API 地址，代理返回假数据
3. **Frida Gadget** — 运行时 Hook
4. **等长字符串替换**（最简单）— 在 libapp.so 中替换关键字符串，让比较逻辑失败
   - `PAID` → `FREE`（4 字节，让付费判断失败）
   - `isPaidRoom` → `isFreeRoom`（10 字节）
   - `OPEN` → `OPEE`（4 字节）
   - **必须等长替换**，否则破坏 Dart AOT snapshot 结构

## ⚠️ apktool 回编 Flutter APK 几乎必然失败

apktool 回编的 Flutter APK 在华为/HarmonyOS 等设备上**几乎必然安装失败**（"无效安装包"或"与操作系统不兼容"）。原因：
- apktool 重新打包改变了 dex 文件内部结构
- 资源文件重新编译引入细微差异
- Flutter 引擎对 APK 结构更敏感

**正确做法：用 Python zipfile 直接修改原始 APK，不经过 apktool**

```python
import zipfile

with zipfile.ZipFile('original.apk', 'r') as original:
    with zipfile.ZipFile('modified.apk', 'w') as new_apk:
        for file_name in original.namelist():
            file_info = original.getinfo(file_name)
            content = original.read(file_name)
            
            if file_name == 'lib/arm64-v8a/libapp.so':
                content = content.replace(b'PAID', b'FREE')
            
            # 关键：用 file_info 保留原始压缩方式（ZIP_STORED vs ZIP_DEFLATED）
            new_apk.writestr(file_info, content)
```

**关键**：必须用 `writestr(file_info, content)` 而不是 `write()`，否则所有文件会被重新压缩为 ZIP_DEFLATED，导致文件大小从 221MB 降到 120MB，安装失败。

详见 `references/flutter-direct-binary-modification.md`

## 常见陷阱

### ⚠️ 必须先加载此技能再开始修改

Flutter APK 修改有严格的规则（同长度替换、MethodChannel 通信、保留原始架构）。**不要凭记忆或通用方法修改**，必须先加载此技能阅读完整方法论。

典型错误模式：
- 用 `activity.recreate()` 代替 MethodChannel（重启整个 App）
- 直接 patch libapp.so 函数为 `ret` 指令（Dart AOT 无标准函数序言，成功率极低）
- 零值替换函数名字符串（破坏 Dart snapshot 结构，导致崩溃）
- 创建复杂 smali 内部类（编译失败或运行时异常）

### ⚠️ 重构时必须从原始 APK 解码

不要从已修改/回编过的 APK 再次解码修改。**每次都从最原始的未修改 APK 重新解码**：

```bash
# ✅ 正确：始终从原始 APK 解码
apktool d -o work/ original.apk

# ❌ 错误：从已修改的 APK 解码（累积结构差异，华为等设备可能安装失败）
apktool d -o work/ modded_v1.apk
```

从已回编的 APK 再次解码→回编，dex 结构和资源对齐的细微差异会累积。在华为 Mate30 / HarmonyOS 设备上表现为「无效安装包」「与操作系统不兼容」。

**更可靠方案：直接二进制修改 libapp.so**

当只需要修改字符串（如 API 地址）时，直接用 Python 修改 libapp.so 二进制文件，然后用 zip 工具重新打包，避免 apktool 回编引入结构差异：

```bash
# 1. 解压原始 APK
unzip original.apk -d /tmp/work/

# 2. 用 Python 修改 libapp.so
python3 -c "
import sys
data = open('/tmp/work/lib/arm64-v8a/libapp.so', 'rb').read()
old = b'https://lmilive.lmizhibo.com'
new = b'http://192.168.0.6:8888/////'  # 等长替换
data = data.replace(old, new)
open('/tmp/work/lib/arm64-v8a/libapp.so', 'wb').write(data)
"

# 3. 用 zip 重新打包（保留原始 ZIP 结构）
cd /tmp/work && zip -r /tmp/modified.apk . -x 'META-INF/*'

# 4. 重签名
uber-apk-signer -a /tmp/modified.apk --allowResign
```

**何时用哪种方案：**

| 修改类型 | 推荐方案 |
|:---------|:---------|
| 只改 API 地址 / 字符串 | 直接二进制修改（避免 apktool） |
| 添加新 smali 类（如 RefreshHelper） | apktool 回编（需要 smali 编译） |
| 修改已有 smali 方法 | apktool 回编 |
| 两者都需要 | 先用 apktool 制作 smali 补丁，再用二进制方式应用到原始 APK |

**Lmi 实战教训（2026-05-30）：**
- v13 用 apktool 回编 → 用户报"应用打不开"
- v13.1 直接二进制修改 libapp.so → APK 正常安装运行
- 结论：只改字符串时，直接二进制修改更可靠

### ⚠️ 签名用内置 debug keystore

华为设备对签名证书敏感。推荐 uber-apk-signer **不带 `--ks` 参数**（自动用内置标准 Android debug 证书）：

```bash
java -jar uber-apk-signer.jar --apks app.apk --overwrite --allowResign
```

避免用自定义创建的 debug.keystore，新证书的指纹可能触发华为额外校验。

### ⚠️ Dart/Flutter HTTP 不走系统代理
- Flutter 的 Dart HTTP client 可能绕开 WiFi 代理设置
- **方案**：直接改 APK 中的 API 地址指向本机

### ⚠️ TLS 证书问题
- 华为/HarmonyOS 手机安装 CA 证书困难
- **方案**：改 HTTPS 为 HTTP（同长度替换），或嵌入 CA 证书到 APK

### ⚠️ 同长度替换限制
- Dart AOT snapshot 中字符串长度不可变（改变会破坏 snapshot 结构）
- **方案**：用 `///`、`/.`、`/./` 等 URL 合法字符填充补齐

### ⚠️ 门票检查可能走 WebSocket/IM 通道
- 有些 App 用 IM SDK（如腾讯 IM）的 WebSocket 做门票验证
- HTTP proxy 无法拦截 WebSocket 流量
- **方案**：配合 AOT 字符串 patching + API 响应修改双重保险

## 代理脚本参考

参见 `references/proxy-script-pattern.md`

## 验证步骤
1. 确认 libapp.so 中旧字符串已清除：`assert TARGET not in data`
2. 确认新字符串已写入：`assert REPLACE in data`
3. 签名后验证 signature verified [v2, v3]
4. 用户安装后通过代理日志确认请求正常转发

## 实战案例

完整的 Lmi 直播 App 修补案例（含确切偏移量、字符串上下文、多架构处理、精简策略）：
- `references/lmi-live-apk-case-study.md` — 2026-05 月修补记录

### 刷新按钮添加案例
- `references/lmi-refresh-button-case.md` — 使用 MethodChannel 添加刷新直播间功能（不重启 App）
