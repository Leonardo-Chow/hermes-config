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

## 常见陷阱

### ⚠️ 重构时必须从原始 APK 解码

不要从已修改/回编过的 APK 再次解码修改。**每次都从最原始的未修改 APK 重新解码**：

```bash
# ✅ 正确：始终从原始 APK 解码
apktool d -o work/ original.apk

# ❌ 错误：从已修改的 APK 解码（累积结构差异，华为等设备可能安装失败）
apktool d -o work/ modded_v1.apk
```

从已回编的 APK 再次解码→回编，dex 结构和资源对齐的细微差异会累积。在华为 Mate30 / HarmonyOS 设备上表现为「无效安装包」「与操作系统不兼容」。

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
