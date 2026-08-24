#!/usr/bin/env python3
"""提交前安全扫描 — git commit/push 前必跑。

检查三类文件中的真实密钥与 PII（邮箱/手机号）：
  1. 已跟踪文件（git ls-files）
  2. 已暂存文件（git diff --cached）—— git add -A 后新增的未跟踪文件靠这里兜底
  3. 未跟踪文件（git ls-files --others --exclude-standard）

用法:
  python3 ~/.hermes/scripts/git_pre_commit_scan.py [--exit]
    --exit  发现风险时退出码 1（可用于提交前钩子）

跳过规则（避免误报）:
  - 字符串含 '...'（掩码/占位符，如 AIzaSy...aA1Q）
  - @im.wechat 后缀（channel_directory 的 webhook ID，非邮箱）
  - 二进制文件（bin/*, *.db, *.pyc 等）

常见真实 Key 格式覆盖:
  AIzaSy* (YouTube), sk-* (OpenAI), ghp_/gho_/ghu_/ghs_ (GitHub),
  tvly-* (Tavily), ok_* (Omar), IL6v* (ScrapeCreators), 32位hex（ScraperAPI/ScrapeCreators）
"""
import os
import re
import subprocess
import sys

KEY_PATTERNS = [
    (r'AIzaSy[A-Za-z0-9_-]{20,}', 'YouTube API Key'),
    (r'sk-[A-Za-z0-9]{20,}', 'OpenAI-style key'),
    (r'gh[po]_[A-Za-z0-9]{30,}', 'GitHub token'),
    (r'tvly-[A-Za-z0-9]{20,}', 'Tavily API Key'),
    (r'ok_[A-Za-z0-9]{20,}', 'Omar API Key'),
    (r'IL6v[A-Za-z0-9]{20,}', 'ScrapeCreators Key'),
    (r'8oBP7[A-Za-z0-9]{10,}', 'known account password'),
]
PII_PATTERNS = [
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'email'),
    (r'\b1[3-9]\d{9}\b', 'CN phone number'),
]
SKIP_DIRS = ('node_modules', 'venv', '.venv', 'lsp', '.next', 'vendor')
BINARY_EXT = ('.db', '.pyc', '.pyo', '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.so', '.dylib', '.exe', '.a')


def run_git(args):
    r = subprocess.run(['git'] + args, capture_output=True, text=True, cwd=os.path.expanduser('~/.hermes'))
    return [l for l in r.stdout.strip().split('\n') if l]


def scan_file(path, label):
    findings = []
    if path.endswith(BINARY_EXT) or any(s in path for s in SKIP_DIRS):
        return findings
    if not os.path.isfile(path):
        return findings
    try:
        with open(path, 'r', errors='ignore') as f:
            content = f.read()
    except Exception:
        return findings

    for pat, name in KEY_PATTERNS:
        for m in re.findall(pat, content):
            if '...' in m:  # 掩码/占位符，安全
                continue
            findings.append((label, 'KEY', name, m[:40]))
    for pat, name in PII_PATTERNS:
        for m in re.findall(pat, content):
            if m.endswith('@im.wechat'):  # webhook ID 误报
                continue
            findings.append((label, 'PII', name, m[:40]))
    return findings


def main():
    root = os.path.expanduser('~/.hermes')
    os.chdir(root)

    all_files = set()
    for f in run_git(['ls-files']):
        all_files.add(f)
    for f in run_git(['diff', '--cached', '--name-only']):
        all_files.add(f)
    for f in run_git(['ls-files', '--others', '--exclude-standard']):
        all_files.add(f)

    findings = []
    for f in sorted(all_files):
        findings.extend(scan_file(f, 'tracked/staged'))

    if not findings:
        print(f'✅ 扫描 {len(all_files)} 个文件，无真实密钥/PII 风险')
        return 0

    print(f'🔴 发现 {len(findings)} 个风险项（共 {len(all_files)} 文件）:')
    for path, kind, name, val in findings:
        print(f'   [{kind}] {name}: {val}  ← {path}')
    print('\n处理建议: 数据文件用 `git rm --cached <file>` + 加入 .gitignore；密钥替换为占位符。')
    return 1 if '--exit' in sys.argv else 0


if __name__ == '__main__':
    sys.exit(main())
