#!/usr/bin/env python3
"""
HTTP Forward Proxy for Android Flutter APK Bypass (方案E)
用法：
  1. 改 APK 把 API 地址指向本机 http://HOST:8888
  2. 运行本脚本
  3. 手机和 Mac 同 WiFi，设代理为 MacIP:8888
  4. 手机打开改版 App

拦截指定的 API 路径并返回伪造响应，其余请求转发到真实服务器。
"""
import http.server
import urllib.request
import json
import ssl
import re

# === 配置区 ===
REAL_HOST = "lmilive.lmizhibo.com"  # 真实服务器域名
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8888

# 需要拦截的 API 路径前缀（匹配即拦截）
BLOCK_PATHS = [
    "/app/live/ticket/",
    "/app/vip/",
    "/app/noble/",
    "/app/earning/balance",
    "/app/earning/account/",
]

# 伪造的响应（根据具体 API 调整）
def fake_response(path: str) -> dict:
    """根据路径返回伪造的 JSON 响应体"""
    if "/ticket/" in path or "/vip/" in path or "/noble/" in path:
        return {
            "code": 0, "msg": "success",
            "data": {
                "hasTicket": True, "owned": True, "allowed": True,
                "myTicketCount": 999,
                "myTickets": [{
                    "ticketId": "bypass_proxy",
                    "ticketType": "room", "roomId": 0,
                    "ticketStatus": "valid", "expireTime": 9999999999
                }],
                "currentTicket": {
                    "ticketId": "bypass_proxy",
                    "ticketType": "room",
                    "ticketStatus": "valid", "expireTime": 9999999999
                }
            }
        }
    if "/balance" in path:
        return {
            "code": 0, "msg": "success",
            "data": {"balance": 999999, "coin": 999999, "points": 999999}
        }
    return {"code": 0, "msg": "success", "data": {}}

class Proxy(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle("GET")
    
    def do_POST(self):
        self._handle("POST")
    
    def do_PUT(self):
        self._handle("PUT")
    
    def do_DELETE(self):
        self._handle("DELETE")
    
    def _handle(self, method):
        path = self.path
        
        # 1. 检查是否需要拦截
        is_blocked = any(ep in path for ep in BLOCK_PATHS)
        
        if is_blocked:
            resp = fake_response(path)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode())
            print(f"[BLOCKED] {method} {path.split('?')[0]}")
            return
        
        # 2. 转发到真实服务器
        # 清理多余前导斜杠（APK 改包 padding 可能加斜杠）
        clean_path = re.sub(r'^/+', '/', path)
        real_url = f"https://{REAL_HOST}{clean_path}"
        
        # 读取请求体
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        # 构造转发请求
        try:
            req = urllib.request.Request(
                real_url,
                data=body,
                headers={
                    "User-Agent": self.headers.get("User-Agent", "Dart/3.7"),
                    "Content-Type": self.headers.get("Content-Type", ""),
                    # 保留认证头
                    "lmi-live-token": self.headers.get("lmi-live-token", ""),
                    "Authorization": self.headers.get("Authorization", ""),
                    "Cookie": self.headers.get("Cookie", ""),
                },
                method=method
            )
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            resp = urllib.request.urlopen(req, context=ctx, timeout=15)
            
            self.send_response(resp.status)
            for key, val in resp.headers.items():
                if key.lower() not in ("transfer-encoding", "content-encoding", "content-length", "connection"):
                    self.send_header(key, val)
            self.end_headers()
            data = resp.read()
            self.wfile.write(data)
            
            # 3. 日志输出
            show_path = path[:80] + "..." if len(path) > 80 else path
            log_body = data[:200].decode('utf-8', errors='replace') if data else ""
            print(f"[FORWARD] {resp.status} {method} {show_path}")
            
            # 重点 API 打印响应体
            important_apis = ["/app/live/info", "/app/live/join", "/app/live/start"]
            if any(api in path for api in important_apis):
                print(f"[IMPORTANT] Response body: {log_body}")
                
        except urllib.error.HTTPError as e:
            print(f"[HTTP ERROR] {method} {clean_path} -> {e.code}")
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            print(f"[ERROR] {method} {clean_path}: {e}")
            self.send_response(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

if __name__ == "__main__":
    server = http.server.HTTPServer((LISTEN_HOST, LISTEN_PORT), Proxy)
    print(f"[PROXY] Listening on http://{LISTEN_HOST}:{LISTEN_PORT}")
    print(f"[PROXY] Forwarding to https://{REAL_HOST}")
    print(f"[PROXY] Blocking: {', '.join(BLOCK_PATHS)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[PROXY] Shutting down")
        server.server_close()
