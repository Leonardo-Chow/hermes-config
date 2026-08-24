#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""零依赖本地网页工具骨架：http.server + sqlite3 + 原生前端。
复制后修改 FIELDS / 路由 / webapp/ 前端即可。启动: python3 app.py（或 ./start.sh）"""
import json, sqlite3, csv, io, os, re, sys, webbrowser, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data.db")
WEB_DIR = os.path.join(BASE_DIR, "webapp")
PORT = int(os.environ.get("APP_PORT", "8787"))
HOST = "127.0.0.1"

# (字段名, 中文表头) —— 驱动建表/表单/表格/导出，前后端保持一致
FIELDS = [("name", "名称"), ("note", "备注")]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    cols = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + [f'"{f}" TEXT DEFAULT ""' for f, _ in FIELDS]
    conn = get_db()
    conn.execute(f"CREATE TABLE IF NOT EXISTS items ({', '.join(cols)})")
    # 兼容旧库：补充缺失列
    exist = {r["name"] for r in conn.execute("PRAGMA table_info(items)").fetchall()}
    for f, _ in FIELDS:
        if f not in exist:
            conn.execute(f'ALTER TABLE items ADD COLUMN "{f}" TEXT DEFAULT ""')
    conn.commit(); conn.close()

class Handler(BaseHTTPRequestHandler):
    server_version = "LocalApp/1.0"
    protocol_version = "HTTP/1.1"  # 必须！默认 1.0 会让 Python urllib 客户端 RemoteDisconnected

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _body_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def log_message(self, fmt, *a):
        sys.stderr.write("[%s] %s\n" % (datetime.now().strftime("%H:%M:%S"), fmt % a))

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        if p in ("/", "/index.html"):
            self._serve("index.html")
        elif p.startswith("/static/"):
            self._serve(p[len("/static/"):])
        elif p == "/api/items":
            self._json(200, {"items": self._list()})
        else:
            self._json(404, {"error": "Not Found"})

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        if p == "/api/items":
            self._create()
        else:
            self._json(404, {"error": "Not Found"})

    def _list(self):
        conn = get_db()
        rows = [dict(r) for r in conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()]
        conn.close()
        return rows

    def _create(self):
        data = self._body_json()
        cols = [f for f, _ in FIELDS]
        vals = [str(data.get(f, "")).strip() for f in cols]
        # Python 3.9 f-string 不能嵌套同引号 → 用 % 拼接
        col_str = ", ".join('"%s"' % c for c in cols)
        ph = ", ".join("?" * len(cols))
        conn = get_db()
        cur = conn.execute("INSERT INTO items (%s) VALUES (%s)" % (col_str, ph), vals)
        conn.commit(); conn.close()
        self._json(200, {"id": cur.lastrowid})

    def _serve(self, name):
        fp = os.path.join(WEB_DIR, os.path.normpath(name))
        if not os.path.isfile(fp) or name.startswith(".."):
            self._json(404, {"error": "Not Found"})
            return
        ext = name.rsplit(".", 1)[-1]
        ctype = {"css": "text/css; charset=utf-8", "js": "application/javascript; charset=utf-8"}.get(ext, "text/html; charset=utf-8")
        with open(fp, "rb") as f:
            self._send(200, f.read(), ctype)

if __name__ == "__main__":
    init_db()
    print("本地工具运行: http://%s:%d" % (HOST, PORT))
    if "--no-browser" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open("http://%s:%d" % (HOST, PORT))).start()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止，数据已保存。")
        srv.shutdown()
