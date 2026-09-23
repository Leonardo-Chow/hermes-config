# Flutter AOT APK Proxy Script Patterns

## 完整 Proxy 脚本模板（HTTP）

```python
#!/usr/bin/env python3
"""HTTP proxy for intercepting Flutter app API calls"""
import http.server
import urllib.request
import json
import ssl
import re

REAL_HOST = "original-api-server.com"
TICKET_PATHS = [
    "/app/live/ticket/",
    "/app/vip/",
    "/app/noble/",
    "/app/earning/balance",
]

def make_success_response(extra_data=None):
    """返回通用的"成功"响应"""
    data = {
        "hasTicket": True, "owned": True, "allowed": True,
        "myTicketCount": 999,
        "myTickets": [{
            "ticketId": "bypass",
            "ticketType": "room", "roomId": 0,
            "ticketStatus": "valid", "expireTime": 9999999999
        }],
        "currentTicket": {
            "ticketId": "bypass",
            "ticketType": "room",
            "ticketStatus": "valid", "expireTime": 9999999999
        }
    }
    if extra_data:
        data.update(extra_data)
    return {"code": 0, "msg": "success", "data": data}

class Proxy(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle("GET")
    def do_POST(self):
        self._handle("POST")
    
    def _handle(self, method):
        path = self.path
        clean_path = re.sub(r'^/+', '/', path)  # 去掉填充的多余斜杠
        
        # 1. 拦截门票类 API
        if any(ep in path for ep in TICKET_PATHS):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(make_success_response()).encode())
            print(f"[BLOCKED] {path.split('?')[0]}")
            return
        
        # 2. 读取请求体
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        # 3. 转发到真实服务器
        real_url = f"https://{REAL_HOST}{clean_path}"
        req = urllib.request.Request(
            real_url, data=body,
            headers={
                "User-Agent": "App/1.0",
                "Content-Type": self.headers.get("Content-Type", ""),
                # 透传认证 token
                "token": self.headers.get("token", ""),
            },
            method=method
        )
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        resp = urllib.request.urlopen(req, context=ctx, timeout=15)
        resp_data = resp.read()
        
        # 4. 修改特定 API 的响应
        if "/app/live/info" in path:
            try:
                resp_json = json.loads(resp_data)
                room = resp_json.get("data", {}).get("liveRoomInfo", {})
                if room.get("isPaid") == "OPEN":
                    room["isPaid"] = "CLOSED"
                    room["ticketPrice"] = 0
                    print(f"[MODIFIED] isPaid: OPEN -> CLOSED")
                    resp_data = json.dumps(resp_json, ensure_ascii=False).encode()
            except Exception as e:
                print(f"[ERROR] modify response: {e}")
        
        # 5. 返回修改后的响应
        self.send_response(resp.status)
        for key, val in resp.headers.items():
            if key.lower() not in ("transfer-encoding", "content-encoding", "content-length"):
                self.send_header(key, val)
        self.end_headers()
        self.wfile.write(resp_data)

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 8888), Proxy)
    print(f"[PROXY] http://0.0.0.0:8888 -> https://{REAL_HOST}")
    server.serve_forever()
```

## Flutter AOT Snapshot 字符串格式说明

Dart AOT snapshot 中的 Latin1 字符串格式：
- **对象头**：4-8 字节（类型标记 + 大小）
- **长度字段**：4-8 字节（UTF-16 长度或字节长度）
- **字符数据**：Latin1 是每字符 1 字节，UTF-16 是每字符 2 字节

修改限制：
1. **必须同字符长度**替换（不能多不能少）
2. Dart 字符串通过长度字段读取，非 null 终止。末尾 null 字节会被当作字符
3. 替换后需手动验证：`assert TARGET not in data`

## URL 填充字符串对照表

| 原始 URL | 长度 | 替换目标 | 说明 |
|:---------|:-----|:---------|:-----|
| `https://example.com` | 27 | `http://192.168.0.6:8888/////` | 5条斜杆填充 |
| `https://server.cn` | 24 | `http://10.0.0.2:8080/:./` | 斜杠+点+斜杠 |
| `https://api.test.com` | 24 | `http://127.0.0.1:8888/././` | ././ 填充 |
| `https://example.com/v4` | 30 | `http://192.168.0.6:8888/./././` | 较长的填充 |

## 签名命令模板

```bash
# uber-apk-signer
java -jar /Users/zhoulong/.local/bin/uber-apk-signer.jar \
  --apks /path/to/apk.apk --overwrite --allowResign
```
