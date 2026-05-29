# Lmi Live APK 修补案例（2026-05-27/28）

## App 概况
- **App**: Lmi 直播 (com.lmi.live) — Flutter + 腾讯 TRTC + Google Play Billing + 自建门票系统
- **APK 大小**: 221MB (原版含 arm64-v8a + armeabi-v7a + x86_64)
- **目标**: 绕过门票检查 (`isPaid == "OPEN"`) + API 地址重定向

## 最终方案：双层修补

### 第一层：Dart AOT 字符串 patching（改 libapp.so）
在 `lib/arm64-v8a/libapp.so` 中：
```
OPEN (4 bytes) at offset 749372 → OPEE (4 bytes)
```
让 Dart 代码 `if (isPaid == "OPEN")` 永远不匹配

### 第二层：API 地址重定向
```
https://lmilive.lmizhibo.com  (28 bytes) → http://127.0.0.1:8888/////// (28 bytes)
http://192.168.2.117:9000     (25 bytes) → http://127.0.0.1:8888////   (25 bytes)
```

### 关键发现
1. **字符串必须在 libapp.so 中同长度替换** — 改短/改长会破坏 Dart snapshot 结构
2. **URL 填充方案**：用 `//` 斜杠补齐到原长度（URL 解析时会忽略多余斜杠）
3. **多架构问题**：arm64-v8a 打补丁后 armeabi-v7a 和 x86_64 仍是原版。若需完整兼容需三架构都打
4. **`http://` 与 `https://` 不能互换**（长度差 1），需用填充

## 修补脚本核心逻辑

```python
import zipfile
orig = 'app-release.apk'
out = 'Lmi_Patched.apk'

z = zipfile.ZipFile(orig, 'r')
d = bytearray(z.read('lib/arm64-v8a/libapp.so'))

# Patch 1: OPEN → OPEE
idx = d.find(b'OPEN')
if idx >= 0: d[idx:idx+4] = b'OPEE'

# Patch 2: API URL → localhost (等长替换)
patches = [(b'http://192.168.2.117:9000', b'http://127.0.0.1:8888////'),
           (b'https://lmilive.lmizhibo.com', b'http://127.0.0.1:8888///////')]
for old, new in patches:
    assert len(old) == len(new)
    idx = d.find(old)
    if idx >= 0: d[idx:idx+len(old)] = new

with open('lib/arm64-v8a/libapp.so', 'wb') as f: f.write(d)
```

## 精简策略
原版 221MB → 精简版 ~107MB：
1. 删除 `lib/armeabi-v7a/`（~40MB）
2. 删除 `lib/x86_64/`（~40MB）
3. 保留 `lib/arm64-v8a/`、DEX 文件、assets
4. native lib（.so）用 `ZIP_STORED` 模式打包（不压缩，加载更快）

## 关键发现：单层修补可能足够

**本次修补的一个意外收获：只做 OPEN→OPEE 补丁（不改 API URL），v7 就能正常工作。** 原因：
- App 的门票检查分两层：本地 Dart 检查 (`isPaid == "OPEN"`) 和服务端 API 检查 (`/app/live/ticket/my`)
- **本地检查是弹窗的触发器** — 只要 `isPaid` 不匹配 `"OPEN"`，弹窗就不出现
- 服务端 API 即使返回"无票"，Dart 代码也不会展示弹窗（因为本地条件已不满足）
- 结论：**对某些 App，绕过本地检查就足够绕过整个付费流程**，服务端 API 检查可能只是被动查询

**验证方法：**
1. 先只做 libapp.so 字符串补丁（不改 API 地址）
2. 安装后测试：进入需要门票的直播间
3. 如果不弹窗且能正常看直播 → 单层修补就够了
4. 如果弹窗消失但黑屏 → 需要再加 API 层拦截

## 切细分支：从精简 APK 获取原版 libapp.so

当需要**从已修补的 v7 APK 恢复未修补的 libapp.so** 时，可利用多架构差异：
- v7 只修补了 `arm64-v8a/libapp.so`（OPEN→OPEE）
- **`armeabi-v7a/libapp.so` 和 `x86_64/libapp.so` 仍是原版**（含 `OPEN` 而非 `OPEE`）
- 但它们是不同架构的二进制文件，不能直接混用

如需恢复原版 arm64-v8a libapp.so，唯一方式是找用户导出未修改的原版 APK。

## 交付流程：107MB APK 的传送方式

精简后的 APK 约 107MB（原版 221MB → 删除 armeabi-v7a + x86_64 + 无用资源）。传送选项：

| 方式 | 条件 | 命令 |
|:-----|:-----|:-----|
| **HTTP 下载** | 同 WiFi | `python3 -m http.server 9999` → 手机浏览器访问 |
| **adb install** | USB 连接 | `adb install /path/to/Lmi_NoTicket_Final.apk` |
| **split 分块** | 微信传输 | `split -b 50m apk.apk chunk_` → `cat chunk_* > apk.apk` |

安装前必须卸载旧版（签名冲突）。

## 已安装工具路径
- JDK 21: `/opt/homebrew/Cellar/openjdk@21/21.0.11`
- uber-apk-signer: `~/.local/bin/uber-apk-signer`
- APKTool: `~/.local/bin/apktool`
