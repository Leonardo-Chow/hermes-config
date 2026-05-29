"""
Flutter App MitM Proxy Bypass Template v2
Intercept ticket/API calls and return fake "authorized" responses.

Usage: mitmdump -s flutter-api-bypass.py --listen-host 0.0.0.0 --listen-port 8888
Phone: WiFi proxy → Mac IP : 8888

Pre-requisites:
  - Option A (user can install CA): Modify APK's network_security_config
    to trust user CAs, then install mitmproxy CA at http://mitm.it
  - Option B (user CANNOT install CA): Embed mitmproxy CA cert into APK
    res/raw/mitmproxy_ca.pem + add <certificates src="@raw/mitmproxy_ca" />
    to network_security_config.xml (see skill "方案D" section)
"""
import json
from mitmproxy import http

# --- CUSTOMIZE: Add your app's API endpoints below ---

# Category 1: Ticket check APIs → return "has ticket" = true
TICKET_APIS = [
    "/live/ticket/my",
    "/live/ticket/verify",
    "/live/ticket/config",
    "/live/ticket/buy",
    "/live/ticket/save",
    "/live/ticket/preset/query",
]

# Category 2: VIP/subscription check → return max level VIP
VIP_APIS = [
    "/vip/list",
    "/vip/privileges",
    "/noble/",
    "/fanclub/my",
]

# Category 3: Balance/wallet → return large fake balance
WALLET_APIS = [
    "/earning/balance",
    "/earning/account/",
    "/wallet/",
]

def make_fake_response(data: dict) -> http.Response:
    """Helper to create a fake success JSON response."""
    return http.Response.make(
        200,
        json.dumps({"code": 0, "msg": "success", "data": data}, ensure_ascii=False),
        {"Content-Type": "application/json; charset=utf-8"}
    )

def request(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url

    # Block ticket APIs
    for ep in TICKET_APIS:
        if ep in url:
            flow.response = make_fake_response({
                "myTickets": [{
                    "ticketId": "bypass_proxy",
                    "ticketType": "room",
                    "roomId": 0,
                    "ticketStatus": "valid",
                    "expireTime": 9999999999,
                }],
                "currentTicket": {
                    "ticketId": "bypass_proxy",
                    "ticketType": "room",
                    "ticketStatus": "valid",
                    "expireTime": 9999999999,
                },
                "hasTicket": True,
                "owned": True,
                "allowed": True,
                "myTicketCount": 999,
            })
            print(f"[TICKET BLOCKED] {ep}")
            return

    # Block VIP checks
    for ep in VIP_APIS:
        if ep in url:
            flow.response = make_fake_response({
                "isVip": True,
                "vipLevel": "max",
                "privileges": ["all"],
                "expireTime": 9999999999,
            })
            print(f"[VIP BLOCKED] {ep}")
            return

    # Block balance checks
    for ep in WALLET_APIS:
        if ep in url:
            flow.response = make_fake_response({
                "balance": 999999,
                "coin": 999999,
                "points": 999999,
            })
            print(f"[BALANCE FAKED] {ep}")
            return

def response(flow: http.HTTPFlow) -> None:
    """Log important API responses for debugging/stream URL capture."""
    url = flow.request.pretty_url
    if not flow.response:
        return

    # --- CUSTOMIZE: Add your app's important API endpoints ---
    IMPORTANT_APIS = [
        "/live/info",       # Returns room info + stream URL/TRTC params
        "/live/join",       # Join room response
        "/live/start",      # Start streaming
        "/live/summary/",
        "/user/publicProfile",
    ]

    for api in IMPORTANT_APIS:
        if api not in url:
            continue

        body = flow.response.text or ""
        try:
            body_json = json.loads(body)
            body_str = json.dumps(body_json, ensure_ascii=False)
            print(f"\n=== API: {url.split('?')[0]} ===")
            print(f"Status: {flow.response.status_code}")
            print(f"Body: {body_str[:2000]}")

            # Auto-detect stream URL keywords
            STREAM_KEYWORDS = ["stream", "url", "rtmp", "flv", "m3u8",
                               "pullUrl", "pushUrl", "playUrl", "cdnUrl",
                               "trtc", "webrtc", "sdkAppId", "userSig"]
            for kw in STREAM_KEYWORDS:
                if kw.lower() in body_str.lower():
                    print(f">>> STREAM KEYWORD '{kw}' FOUND IN RESPONSE!")
        except json.JSONDecodeError:
            print(f"\n=== API (text): {url.split('?')[0]} ===")
            if len(body) > 100:
                print(f"Body: {body[:500]}")
        break  # Only report first match
