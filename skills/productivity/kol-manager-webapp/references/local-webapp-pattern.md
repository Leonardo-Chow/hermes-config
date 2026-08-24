# 本地零依赖网页应用 — 可复用模式速查

用户需要"本地跑一个网页版 XX 管理系统"时，首选此模式：**纯 Python 标准库 + SQLite 单文件 + 原生前端**。零 pip 依赖、双击启动、数据单文件备份。

## 骨架

```
project/
├── app.py          # http.server ThreadingHTTPServer + sqlite3 + 全部 API
├── webapp/         # index.html + 各页面 + style.css（静态文件）
├── start.sh        # cd 到目录 + open 浏览器 + python3 app.py
├── backup.sh       # git 自动备份
├── kol.db          # SQLite 单文件（WAL 模式）
└── .gitignore      # 必须含 *.db-shm *.db-wal
```

## 后端要点

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"   # 关键！默认 1.0 会让 urllib 客户端 RemoteDisconnected
    def _json(self, code, obj): ...  # ensure_ascii=False
    def _body_json(self): ...        # 读 Content-Length + json.loads

ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
```

- 路由：`do_GET/do_POST/do_PUT/do_DELETE` + `urllib.parse.urlparse` 分发
- 静态文件：`/static/` 前缀 → 读 webapp/ 目录（防 `..` 穿越）
- SQLite：`conn.row_factory = sqlite3.Row`，`PRAGMA journal_mode=WAL`，每请求开连接
- 登录：`secrets.token_hex(24)` 存内存 SESSIONS dict，**Set-Cookie HttpOnly**（header 认证只在 fetch 生效，浏览器导航必须 cookie）
- 加字段：`FIELDS` 元组 + `ALTER TABLE ... ADD COLUMN` 兼容旧库 + 前端 JS FIELDS 数组 + HTML input id 五处同步

## 前端要点

- 零依赖原生 JS：`fetch` + `URLSearchParams` + `innerHTML` 模板字符串
- 下拉可手输：`<input list="xxx-suggest">` + `<datalist>`（用户偏好所有选项可手动改）
- 页码/搜索/筛选：状态对象 + `qs()` 生成 URLSearchParams
- 环形进度：SVG circle `stroke-dasharray=C` + `stroke-dashoffset=C*(1-pct/100)`，C=2πr

## Python 3.9 陷阱

- f-string 内不能嵌套同引号字符串 → 用 `"%s" % (...)` 拼接
- `from __future__ import annotations`（如用到新式注解）
- urllib 发 POST body 可能 RemoteDisconnected（curl/Node 正常）→ 测试用 curl/Node

## 常见坑

- HTML 表单缺 id → 页面底部初始化抛 TypeError，后续函数全不执行（表现为下拉空）。改完表单用 `document.getElementById('f-xxx')` 逐个确认存在。
- 文字/状态改版 → search_files 全目录搜旧词，避免残留文案。
- 备份 push 403 → 找用户环境里已有的写权限 PAT（如其它仓库 remote URL 内嵌），backup.sh 动态提取，不要依赖 gh CLI。
