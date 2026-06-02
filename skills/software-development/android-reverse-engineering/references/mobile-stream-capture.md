# 移动端直播源抓取：mitmproxy + WiFi 代理方案

**适用场景：** App 使用 HLS/FLV 等标准协议，但有反爬保护或 VPN 冲突，需要从真实设备抓取流地址。

## 为什么不用手机端抓包工具？

| 工具 | 问题 |
|:-----|:-----|
| Packet Capture | 使用 VPN 模式，与 Lmi 直播等 App 冲突（网络错误） |
| HTTP Canary（黄鸟） | 同样使用 VPN 模式，部分 App 检测 VPN 会拒绝连接 |
| StreamCapture | 同 VPN 模式 |

**根本原因：** Android 同时只能开一个 VPN。抓包工具的 VPN 会干扰目标 App 的网络连接。

**解决方案：** 不在手机上开 VPN，而是通过 WiFi 代理将流量转发到 Mac 上的 mitmproxy。

## Mac 端设置

### 1. 确认 mitmproxy 已安装

```bash
# pip3 安装的路径
/Users/zhoulong/Library/Python/3.9/bin/mitmdump --version
```

### 2. 获取 Mac 局域网 IP

```bash
ipconfig getifaddr en0  # 如 192.168.0.24
```

### 3. 创建抓包脚本

```python
# /tmp/capture_stream.py
from mitmproxy import http

KEYWORDS = ['m3u8', 'flv', 'stream', 'live', 'video', 'play', 'hls', '.ts']

def response(flow: http.HTTPFlow):
    url = flow.request.pretty_url.lower()
    
    # 直播流文件
    if any(ext in url for ext in ['.m3u8', '.flv', '.ts']):
        print(f"🎬 [直播流] {flow.request.pretty_url}")
        print(f"  Content-Type: {flow.response.headers.get('content-type', '')}")
        print(f"  Size: {len(flow.response.content)} bytes")
        if '.m3u8' in url:
            print(f"  Content:\n{flow.response.text[:500]}")
    
    # JSON API 响应含流地址
    elif 'json' in flow.response.headers.get('content-type', ''):
        body = flow.response.text.lower()
        if any(kw in body for kw in ['m3u8', 'flv', 'play_url', 'live_url', 'video_url']):
            print(f"🎯 [API含流地址] {flow.request.pretty_url}")
            print(f"  {flow.response.text[:500]}")

def request(flow: http.HTTPFlow):
    url = flow.request.pretty_url
    # 特别关注的域名
    if any(d in url for d in ['landapiqq', 'cloudfront', 'live', 'stream']):
        print(f"📡 {flow.request.method} {url[:150]}")
```

### 4. 启动 mitmproxy

```bash
# 杀掉占用端口的进程
lsof -ti :8080 | xargs kill -9 2>/dev/null
sleep 2

# 启动（用 terminal(background=true)）
/Users/zhoulong/Library/Python/3.9/bin/mitmdump \
  -s /tmp/capture_stream.py \
  --listen-host 0.0.0.0 --listen-port 8080

# 验证
sleep 3
lsof -i :8080  # 应显示 Python LISTEN
```

## 手机端设置

### 1. 设置 WiFi 代理

1. 设置 → WLAN → 长按已连的 WiFi → 修改网络
2. 代理 → 手动
3. 主机名：`Mac 的 IP`（如 192.168.0.24）
4. 端口：`8080`
5. 保存

### 2. 安装 mitmproxy CA 证书

1. 手机浏览器打开 `http://mitm.it`
2. 点 **Android** 下载证书
3. 安装证书：
   - 设置 → 安全 → 更多安全设置 → 加密和凭据
   - 从存储设备安装 → CA 证书
   - 选择下载的证书文件

### 3. 验证代理生效

手机浏览器打开 `http://mitm.it`：
- 如果看到证书下载页面 → ✅ 代理生效
- 如果看到 "traffic is not going through mitmproxy" → ❌ 代理未生效，检查 IP/端口

## 抓包流程

1. **Mac 端：** 启动 mitmproxy（确认 lsof 显示端口监听）
2. **手机端：** 设置 WiFi 代理 → 安装证书 → 验证生效
3. **手机端：** 打开目标 App → 进入直播间
4. **Mac 端：** 观察 mitmproxy 输出，寻找 m3u8/flv/stream 相关请求
5. **抓到后：** 复制 URL，在电脑上用 `ffplay` 或 VLC 验证

```bash
# 验证流地址
ffplay "抓到的m3u8地址"
```

## 注意事项

- 手机和 Mac 必须在**同一 WiFi** 下
- 抓完后记得把手机 WiFi 代理改回**无**，否则手机上不了网
- 国产 App（如 Lmi 直播）不需要翻墙，代理指向 Mac 后直连就行
- 如果 App 使用 Flutter Dart HTTP（不读 WiFi 代理），此方案无效 → 改用方案 E（二进制改 API 地址）

## Flutter App 的特殊问题

**Flutter Dart HTTP 不读系统 WiFi 代理！** 这是 Android 平台的关键坑：

- Native 应用（Java/Kotlin OkHttp）：遵守 WiFi 代理设置 ✅
- Flutter 应用（Dart HttpClient）：忽略 WiFi 代理设置 ❌

**诊断方法：** 设好代理后开 mitmdump，看日志里有没有目标域名。如果只有系统服务流量（`connectivitycheck.*`、`grs.dbankcloud.*`），说明 Dart HTTP 不读代理。

**解决方案：** 见 `android-reverse-engineering` skill 的方案 E（二进制改 libapp.so API 地址）。
