#!/usr/bin/env python3
"""Omar TikTok API 额度管理工具"""

import os
import sys
from datetime import datetime
from pathlib import Path

USAGE_FILE = Path.home() / ".hermes/config/omkar_usage.txt"
MONTHLY_LIMIT = 100

def get_usage():
    """获取本月使用情况"""
    if not USAGE_FILE.exists():
        return 0, []
    
    current_month = datetime.now().strftime("%Y-%m")
    total = 0
    records = []
    
    with open(USAGE_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 格式: 2026-06-08: 5 (用途)
            date_str, rest = line.split(": ", 1)
            if date_str.startswith(current_month):
                count, purpose = rest.split(" ", 1)
                total += int(count)
                records.append({"date": date_str, "count": int(count), "purpose": purpose})
    
    return total, records

def add_usage(count, purpose):
    """记录使用"""
    with open(USAGE_FILE, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d')}: {count} ({purpose})\n")

def check_budget(needed=1):
    """检查是否有足够额度"""
    used, _ = get_usage()
    remaining = MONTHLY_LIMIT - used
    if remaining < needed:
        print(f"❌ 额度不足！已用 {used}/{MONTHLY_LIMIT}，需要 {needed}，剩余 {remaining}")
        return False
    print(f"✅ 额度充足：已用 {used}/{MONTHLY_LIMIT}，需要 {needed}，剩余 {remaining - needed}")
    return True

def show_status():
    """显示状态"""
    used, records = get_usage()
    remaining = MONTHLY_LIMIT - used
    
    print(f"📊 Omar TikTok API 额度状态")
    print(f"   月份: {datetime.now().strftime('%Y-%m')}")
    print(f"   已用: {used}/{MONTHLY_LIMIT}")
    print(f"   剩余: {remaining}")
    print(f"   使用率: {used/MONTHLY_LIMIT*100:.1f}%")
    
    if records:
        print(f"\n📝 使用记录:")
        for r in records:
            print(f"   {r['date']}: {r['count']} ({r['purpose']})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_status()
    elif sys.argv[1] == "check":
        needed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        check_budget(needed)
    elif sys.argv[1] == "add":
        if len(sys.argv) < 4:
            print("用法: omkar_usage.py add <count> <purpose>")
            sys.exit(1)
        add_usage(int(sys.argv[2]), " ".join(sys.argv[3:]))
        print("✅ 已记录")
    else:
        print("用法: omkar_usage.py [check [N] | add <count> <purpose>]")
