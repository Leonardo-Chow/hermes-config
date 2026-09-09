#!/usr/bin/env python3
"""修复 gen_html.py 中中文 value 内的 ASCII 双引号 → 「」

写中文翻译时如果用 ASCII 双引号包了内层短语（如 "Anthropic 召回 \"Fable\""），
会破坏 Python 字符串语法。本脚本扫描 ZH / GH_ZH / HN_ZH 字典，把 value
内部的 " 替换为 「」（成对）。

用法：python3 scripts/fix-double-quotes.py
"""
import re, sys, ast

PATH = sys.argv[1] if len(sys.argv) > 1 else "gen_html.py"
src = open(PATH, encoding='utf-8').read()
lines = src.split('\n')
fixed = 0

for i, line in enumerate(lines):
    # 匹配 "key": "value", 这种字典行
    m = re.match(r'^(\s*"[^"]+":\s*")(.*)("\,?\s*)$', line)
    if not m: continue
    prefix, value, suffix = m.groups()
    if '"' not in value: continue
    # value 内 " → 「/」 成对
    new_value, in_quote = '', False
    for ch in value:
        if ch == '"':
            new_value += '\u300c' if not in_quote else '\u300d'
            in_quote = not in_quote
        else:
            new_value += ch
    lines[i] = prefix + new_value + suffix
    fixed += 1

open(PATH, 'w', encoding='utf-8').write('\n'.join(lines))
print(f'fixed {fixed} lines')

# 验证语法
try:
    ast.parse(open(PATH, encoding='utf-8').read())
    print('AST OK')
except SyntaxError as e:
    print(f'AST ERR: {e}')
    sys.exit(1)
