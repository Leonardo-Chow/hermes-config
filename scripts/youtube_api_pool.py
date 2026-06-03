#!/usr/bin/env python3
"""YouTube API池管理 - 自动轮换API密钥"""
import json
import os

CONFIG_FILE = os.path.expanduser("~/.hermes/config/youtube_api_pool.json")

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

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 youtube_api_pool.py current    # 获取当前API密钥")
        print("  python3 youtube_api_pool.py rotate     # 轮换到下一个API密钥")
        print("  python3 youtube_api_pool.py add KEY    # 添加新的API密钥")
        print("  python3 youtube_api_pool.py list       # 列出所有API密钥")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "current":
        print(get_current_api_key())
    elif cmd == "rotate":
        new_key = rotate_api_key()
        print(f"已轮换到: {new_key}")
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("错误: 请提供API密钥")
            sys.exit(1)
        new_key = sys.argv[2]
        if add_api_key(new_key):
            print(f"已添加: {new_key}")
        else:
            print("该API密钥已存在")
    elif cmd == "list":
        config = load_config()
        for i, key in enumerate(config['api_keys']):
            current = " <-- 当前" if i == config['current_index'] else ""
            print(f"  {i+1}. {key}{current}")
    else:
        print(f"未知命令: {cmd}")
