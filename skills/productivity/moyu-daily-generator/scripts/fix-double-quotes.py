#!/usr/bin/env python3
"""
自动修复 ZH 字典 value 内 ASCII 双引号 → 「」
每次 ZH 字典大改动后必跑。
"""

import re

def fix_double_quotes_in_file(filepath):
    """将文件中 ZH 字典 value 内的 ASCII 双引号替换为中文「」。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 ZH 字典的开始和结束
    zh_start = content.find('ZH = {')
    if zh_start == -1:
        print("未找到 ZH 字典")
        return
    
    # 简单策略：找到 ZH = { 后的内容，直到下一个同级的变量定义
    # 这里用简单的行级处理：只处理看起来像 ZH 字典条目的行
    lines = content.split('\n')
    in_zh = False
    brace_count = 0
    fixed_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # 检测进入 ZH 字典
        if 'ZH = {' in line:
            in_zh = True
            brace_count = 1
        elif in_zh:
            # 计算大括号平衡
            brace_count += line.count('{')
            brace_count -= line.count('}')
            if brace_count <= 0:
                in_zh = False
        
        if in_zh:
            # 替换 value 部分的双引号
            # 匹配模式: "key": "value with "quotes""
            # 只替换冒号后第一个双引号到最后一个双引号之间的双引号
            # 简单处理：将行中所有 ASCII 双引号替换为中文「」
            # 但要避免替换 key 部分的引号
            # 简单策略：冒号后的第一个 " 到行尾最后一个 " 之间的 " 替换为 「」
            # 这里用正则替换：在冒号后的内容中替换 "
            def replace_quotes_in_value(match):
                prefix = match.group(1)  # "key": "
                value = match.group(2)   # value with "quotes"
                suffix = match.group(3)  # ",
                # 替换 value 中的双引号
                value = value.replace('"', '「').replace('"', '」')
                return prefix + value + suffix
            
            # 匹配 "key": "value", 模式
            line = re.sub(r'(^\s*"[^"]+"\s*:\s*")([^"]*")?(.*?)(",\s*$)', 
                         lambda m: m.group(1) + m.group(2).replace('"', '「').replace('"', '」') + m.group(3) + m.group(4) if m.group(2) else m.group(1) + m.group(3).replace('"', '「').replace('"', '」') + m.group(4), 
                         line)
            # 更简单的方法：直接替换 value 部分
            # 找到第一个冒号后的内容
            colon_idx = line.find(':')
            if colon_idx != -1:
                prefix = line[:colon_idx+1]
                value_part = line[colon_idx+1:].strip()
                if value_part.startswith('"') and value_part.endswith('",'):
                    # 替换中间的双引号
                    inner = value_part[1:-2]  # 去掉首尾的 "
                    inner = inner.replace('"', '「').replace('"', '」')
                    line = prefix + ' "' + inner + '",'
                elif value_part.startswith('"') and value_part.endswith('"'):
                    inner = value_part[1:-1]
                    inner = inner.replace('"', '「').replace('"', '」')
                    line = prefix + ' "' + inner + '"'
        
        fixed_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    print(f"已修复: {filepath}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        fix_double_quotes_in_file(sys.argv[1])
    else:
        fix_double_quotes_in_file('/Users/zhoulong/.hermes/skills/productivity/moyu-daily-generator/gen_html.py')