#!/usr/bin/env python3
"""Tavily API池管理 - 自动轮换API密钥"""
import json
import os

CONFIG_FILE = os.path.expanduser("~/.hermes/config/tavily_api_pool.json")

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_current_api_key():
    config = load_config()
    index = config['current_index']
    return config['api_keys'][index]

def rotate_api_key():
    config = load_config()
    config['current_index'] = (config['current_index'] + 1) % len(config['api_keys'])
    save_config(config)
    return config['api_keys'][config['current_index']]

def add_api_key(new_key):
    config = load_config()
    if new_key not in config['api_keys']:
        config['api_keys'].append(new_key)
        save_config(config)
        return True
    return False

def list_api_keys():
    config = load_config()
    return config['api_keys']

def mark_key_used():
    """标记当前密钥已使用（用于配额跟踪）"""
    config = load_config()
    index = config['current_index']
    if 'usage' not in config:
        config['usage'] = {}
    key = config['api_keys'][index]
    if key not in config['usage']:
        config['usage'][key] = 0
    config['usage'][key] += 1
    save_config(config)

def get_usage():
    """获取所有密钥的使用情况"""
    config = load_config()
    return config.get('usage', {})

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 tavily_api_pool.py current    # 获取当前API密钥")
        print("  python3 tavily_api_pool.py rotate     # 轮换到下一个API密钥")
        print("  python3 tavily_api_pool.py add KEY    # 添加新的API密钥")
        print("  python3 tavily_api_pool.py list       # 列出所有API密钥")
        print("  python3 tavily_api_pool.py usage      # 查看使用情况")
        print("  python3 tavily_api_pool.py mark       # 标记当前密钥已使用")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "current":
        print(get_current_api_key())
    elif cmd == "rotate":
        print(rotate_api_key())
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("错误: 需要提供API密钥")
            sys.exit(1)
        new_key = sys.argv[2]
        if add_api_key(new_key):
            print(f"成功添加新密钥: {new_key[:10]}...")
        else:
            print("密钥已存在")
    elif cmd == "list":
        keys = list_api_keys()
        for i, key in enumerate(keys):
            print(f"{i}: {key[:10]}...")
    elif cmd == "usage":
        usage = get_usage()
        for key, count in usage.items():
            print(f"{key[:10]}...: {count}次")
    elif cmd == "mark":
        mark_key_used()
        print("已标记")
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
