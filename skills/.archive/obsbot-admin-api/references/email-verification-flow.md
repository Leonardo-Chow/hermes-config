# Email Verification Code Auto-Retrieval

## Problem
OBSBOT Admin login requires email verification code when IP changes. Manual retrieval is slow.

## Solution: IMAP Auto-Fetch

### Alibaba Cloud Mail IMAP Settings
- Server: `imap.qiye.aliyun.com`
- Port: `993` (SSL)
- Auth: email + app-specific password (三方客户端安全密码)

### Python Script
```python
import imaplib, email, re
from email.header import decode_header

def get_verification_code(email_addr, password):
    """Fetch latest login verification code from Alibaba Mail."""
    imap = imaplib.IMAP4_SSL("imap.qiye.aliyun.com", 993)
    imap.login(email_addr, password)
    imap.select("INBOX")
    
    status, messages = imap.search(None, "ALL")
    msg_ids = messages[0].split()
    
    for msg_id in reversed(msg_ids[-10:]):
        status, msg_data = imap.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        
        subject = ""
        for part, encoding in decode_header(msg.get("Subject", "")):
            if isinstance(part, bytes):
                subject += part.decode(encoding or "utf-8", errors="replace")
            else:
                subject += part
        
        if "异地登录" in subject:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            html = payload.decode("utf-8", errors="replace")
                            codes = re.findall(r'\b\d{6}\b', html)
                            if codes:
                                imap.logout()
                                return codes[0]
            break
    
    imap.logout()
    return None
```

### Full Login Flow
```python
import urllib.request, json

# Step 1: Send verification code
data = json.dumps({"account": "leonardo@obsbot.com"}).encode()
req = urllib.request.Request(
    "https://api.obsbot.cn/ums/v1/users/operation/verification-code",
    data=data, headers={"Content-Type": "application/json"}, method="POST"
)
urllib.request.urlopen(req, timeout=10)

# Step 2: Wait and fetch code from email
import time; time.sleep(8)
code = get_verification_code("leonardo@obsbot.com", "<app_password>")

# Step 3: Login with code
login_data = json.dumps({
    "account": "leonardo@obsbot.com",
    "password": "<password>",
    "verification_code": code
}).encode()
req = urllib.request.Request(
    "https://api.obsbot.cn/ums/v1/users/operation/login",
    data=login_data, headers={"Content-Type": "application/json"}, method="POST"
)
resp = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
# resp contains token on success, or error_code on failure
```

### Key Timing
- Verification code email arrives in ~5-10 seconds
- Code validity: ~2 minutes (short!)
- Rate limit: too many requests may trigger cooldown
- Search subject: "异地登录验证码" (remote login verification code)

### Error Codes
- `RM.100114` - IP changed, verification needed
- `RM.100110` - Invalid/expired verification code
- `RM.100111` - Wrong password
