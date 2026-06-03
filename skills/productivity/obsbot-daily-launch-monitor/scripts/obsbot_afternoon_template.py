#!/usr/bin/env python3
"""OBSBOT 下午视频监测模板 - 与上午去重，只输出新内容"""
import datetime
import json
import os

TODAY = datetime.date.today()
MORNING_FILE = f"/tmp/obsbot_morning_{TODAY.strftime('%Y%m%d')}.json"
TITLE = f"{TODAY.strftime('%Y-%m-%d')}——视频上线监测——下午"

def load_morning_ids():
    """加载上午已发布的视频ID"""
    if os.path.exists(MORNING_FILE):
        with open(MORNING_FILE) as f:
            data = json.load(f)
            return set(data.get('video_ids', []))
    return set()

def save_results(videos):
    """保存下午结果，供次日参考"""
    output_file = f"/tmp/obsbot_afternoon_{TODAY.strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'date': str(TODAY),
            'video_ids': [v['id'] for v in videos],
            'videos': videos
        }, f, ensure_ascii=False, indent=2)

# 主逻辑
morning_ids = load_morning_ids()
print(f"上午已发布视频: {len(morning_ids)} 个")
print(f"文件名: {TITLE}")

# TODO: 执行搜索逻辑（同上午）
# TODO: 过滤掉 morning_ids 中已存在的视频
# TODO: 只输出新增视频
# TODO: 调用 save_results 保存
