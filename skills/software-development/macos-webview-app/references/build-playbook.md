# 构建手册：本地 Web 服务 → 原生 macOS .app

本会话完整验证的构建序列。场景：`~/deepseek-harness-client/server.py`(Python stdlib, 端口 8799) + `public/` 前端，打包为 `DeepSeek Harness.app`。

## 1. 图标（SVG → icns）

```bash
mkdir -p /tmp/ds_icon.iconset
# SVG 底稿 → 1024 PNG（headless Chrome 渲染，白底居中）
cat > /tmp/icon.html << 'EOF'
<body style="margin:0;width:1024px;height:1024px;display:flex;align-items:center;justify-content:center;background:#fff">
<img src="/path/logo.svg" style="width:760px;max-width:90%">
</body>
EOF
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --screenshot=/tmp/icon1024.png --window-size=1024,1024 "file:///tmp/icon.html"

for s in 16 32 64 128 256 512; do sips -z $s $s /tmp/icon1024.png --out /tmp/ds_icon.iconset/icon_${s}x${s}.png; done
sips -z 32 32   /tmp/icon1024.png --out /tmp/ds_icon.iconset/icon_16x16@2x.png
sips -z 64 64   /tmp/icon1024.png --out /tmp/ds_icon.iconset/icon_32x32@2x.png
sips -z 128 128 /tmp/icon1024.png --out /tmp/ds_icon.iconset/icon_64x64@2x.png
sips -z 256 256 /tmp/icon1024.png --out /tmp/ds_icon.iconset/icon_128x128@2x.png
sips -z 512 512 /tmp/icon1024.png --out /tmp/ds_icon.iconset/icon_256x256@2x.png
sips -z 1024 1024 /tmp/icon1024.png --out /tmp/ds_icon.iconset/icon_512x512@2x.png
iconutil -c icns /tmp/ds_icon.iconset -o /tmp/AppIcon.icns
```

## 2. main.swift 骨架（关键段）

```swift
let clientPort = 8799, dshPort = 3080

func portOpen(_ port: Int) -> Bool {
    let sock = socket(AF_INET, SOCK_STREAM, 0); defer { close(sock) }
    var addr = sockaddr_in()
    addr.sin_family = sa_family_t(AF_INET)
    addr.sin_port = UInt16(port).bigEndian
    addr.sin_addr.s_addr = inet_addr("127.0.0.1")
    return withUnsafePointer(to: &addr) {
        $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
            connect(sock, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
        }
    } == 0
}

func launch(_ path: String, _ args: [String]) -> Process {
    let p = Process(); p.executableURL = URL(fileURLWithPath: path); p.arguments = args
    p.standardOutput = FileHandle.nullDevice; p.standardError = FileHandle.nullDevice
    try? p.run(); return p
}

func waitPort(_ port: Int, timeout: Double) async -> Bool { /* 轮询 portOpen 每 400ms */ }

class AppDelegate: NSObject, NSApplicationDelegate, WKUIDelegate, WKNavigationDelegate {
    func applicationDidFinishLaunching(_ n: Notification) {
        log("boot: dsh=\(portOpen(dshPort)) client=\(portOpen(clientPort))")  // 文件日志！
        Task {
            if !portOpen(dshPort) { dshProc = launch("/bin/bash", ["-lc", "exec dsh web --no-open"]) }
            guard await waitPort(dshPort, timeout: 25) else { showError(...); return }
            if !portOpen(clientPort) {
                proxyProc = launch("/usr/bin/python3",
                    [Bundle.main.resourcePath! + "/server.py",
                     "--port", String(clientPort),
                     "--root", Bundle.main.resourcePath! + "/public"])  // ← root 必须显式传
            }
            if await waitPort(clientPort, timeout: 10) {
                loadApp()   // webView.load(URLRequest(url: http://127.0.0.1:8799))
            } else { showError(...) }
        }
        // 先显示窗口 + loadFileURL(Resources/loading.html) 占位
    }
    // didFailProvisionalNavigation / didFail → retryLoad()（最多10次×1.2s）→ NSAlert
    // navigationDelegate: host != "127.0.0.1" → cancel + NSWorkspace.shared.open(url)
}
```

坑：`webView.navigationDelegate = self as? WKNavigationDelegate` 有 warning 但可用；直接 `= self` 且类 extension conform 更干净。

## 3. Info.plist 关键项

```xml
<key>CFBundleExecutable</key><string>Binary名</string>
<key>CFBundleIconFile</key><string>AppIcon</string>
<key>NSHighResolutionCapable</key><true/>
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSAllowsArbitraryLoads</key><true/>
  <key>NSAllowsLocalNetworking</key><true/>
</dict>
```

## 4. 组装 + 签名 + 安装

```bash
swiftc -O -o DeepSeekHarness main.swift -framework Cocoa -framework WebKit
APP="$HOME/Desktop/MyClient.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp Binary "$APP/Contents/MacOS/"
cp Info.plist "$APP/Contents/"
cp AppIcon.icns loading.html server.py "$APP/Contents/Resources/"
cp -r public "$APP/Contents/Resources/public"
codesign --force --deep -s - "$APP"
xattr -dr com.apple.quarantine "$APP"   # 本机分发免 Gatekeeper
open "$APP"
```

## 5. server.py 的 --root 支持（argparse 版，勿用手动 sys.argv）

```python
ROOT = Path(__file__).resolve().parent / "public"
...
def main():
    ap.add_argument("--root", default=None)     # ← 必须注册，否则未知参数 error exit
    args = ap.parse_args()
    global ROOT
    if args.root: ROOT = Path(args.root).resolve()
```

## 6. 调试速查

| 症状 | 手段 |
|------|------|
| 双击后无窗口 | 后台跑二进制 + 文件日志埋点；`ps aux \| grep` 查进程 |
| 卡启动页 | `lsof -i :PORT \| grep ESTABLISHED` 看 WebKit.Networking 是否连上；连了但没切页 = loadApp 未执行 |
| 服务没起来 | 手动按 App 同参数跑 server.py 看 stderr（argparse 报错在这里现形） |
| WKWebView 本身是否正常 | 写 30 行 miniweb.swift 直接 load URL 做最小复现 |
| 截窗口 | CGWindowListCopyWindowInfo 拿 windowID → `screencapture -o -l <id>` |
| print 看不到 | 后台进程 stdout 丢失，必须写文件日志 |
