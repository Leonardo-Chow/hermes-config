---
name: macos-webview-app
description: 把本地 Web UI 打包成原生 macOS .app（Swift+WKWebView 壳）。
---

# macOS 原生 WebView 客户端（Swift + WKWebView）

## 何时用
- 用户已有本地 Web 服务（Python stdlib / Node 等），要求「做一个**桌面可点击的客户端**，不是网页」——即双击 .app、Dock 有图标、有自己窗口的原生应用
- 方案：swiftc 编译一个 WKWebView 壳（~90KB 单二进制），壳负责服务编排 + 加载本地 URL；无需 Xcode 工程，`swiftc main.swift -framework Cocoa -framework WebKit` 即可

## 已验证架构
```
MyClient.app/Contents/
├─ Info.plist              # CFBundleExecutable/IconFile/NSAppTransportSecurity(NSAllowsArbitraryLoads+LocalNetworking)
├─ MacOS/Binary            # swiftc -O main.swift -framework Cocoa -framework WebKit
└─ Resources/
   ├─ AppIcon.icns         # iconset→iconutil；SVG底稿用 headless Chrome 截 1024 PNG 再 sips 缩放
   ├─ server.py            # 后端服务脚本（--root 参数指定静态目录！）
   ├─ public/              # 静态前端整目录
   └─ loading.html         # 启动页（logo+呼吸动画），服务就绪后切真实 URL
```
Swift 壳职责：检测端口 → 未开则 Process() 拉起服务 → 轮询端口就绪 → webView.load(http://127.0.0.1:PORT)。

## 必踩坑（全部实测）
1. **argparse 参数必须显式注册**：给 server.py 加 `--root` 时手动读 `sys.argv` 不够——argparse 遇到未知参数直接 error exit，进程静默死亡，App 卡启动页。必须 `ap.add_argument("--root", default=None)`。
2. **静态目录定位**：打包进 .app 后 `__file__` 同级的 `public/` 不存在，必须用 `--root <Bundle.main.resourcePath>/public` 显式传入。
3. **ATS 本地网络**：Info.plist 需要 `NSAppTransportSecurity → NSAllowsArbitraryLoads=true`（仅 NSAllowsLocalNetworking 在某些 WKWebView 场景仍拦 http://127.0.0.1）。
4. **签名与隔离**：`codesign --force --deep -s -` ad-hoc 签名；分发前 `xattr -dr com.apple.quarantine` 免 Gatekeeper。
5. **导航失败要重试**：WKWebView 加载失败默认白屏无提示。实现 `didFailProvisionalNavigation/didFail` → 延时重试 N 次 → 弹 NSAlert。
6. **外部链接劫持**：navigationDelegate 里非 127.0.0.1 的 host 一律 cancel + `NSWorkspace.shared.open()`，否则点外链会在壳内迷航。

## 调试手段（窗口不显示/卡启动页时）
- **文件日志**：Swift 里写 `/tmp/app.log`（print 在后台进程里看不到）；在 boot/portReady/loadApp/didFail 各埋点。
- **抓指定窗口截图**：`screencapture -x -l <windowID>`；windowID 用 CGWindowListCopyWindowInfo 按 owner 名过滤拿（CGWindowListCreateImage 已废弃不可用）。
- **最小复现二分法**：先写 30 行 miniweb.swift 直接 load 目标 URL，跑通说明 WKWebView/网络没问题，再往回查编排逻辑（Task 异步块、端口探测顺序）。
- **确认 WebView 是否真的发了请求**：`lsof -i :PORT | grep ESTABLISHED`，WebKit.Networking 进程出现连接 = 加载成功。
- osascript System Events 查窗口需要辅助功能权限，没授权会报 -25211；用 CGWindowList 替代。

## 参考
- `references/build-playbook.md` — 完整构建命令序列、main.swift 关键代码段、图标制作流程
