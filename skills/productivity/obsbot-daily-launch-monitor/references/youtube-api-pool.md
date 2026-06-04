# YouTube API Pool Configuration

## 文件位置

- 配置文件：`~/.hermes/config/youtube_api_pool.json`
- 管理脚本：`~/.hermes/scripts/youtube_api_pool.py`

## 配置文件格式

```json
{
  "api_keys": [
    "AIzaSy...Key1",
    "AIzaSy...Key2",
    "AIzaSy...Key3"
  ],
  "current_index": 0,
  "updated_at": "2026-06-02"
}
```

## 管理命令

```bash
# 获取当前 API Key
python3 ~/.hermes/scripts/youtube_api_pool.py current

# 轮换到下一个 API Key
python3 ~/.hermes/scripts/youtube_api_pool.py rotate

# 添加新的 API Key
python3 ~/.hermes/scripts/youtube_api_pool.py add NEW_KEY

# 列出所有 API Key
python3 ~/.hermes/scripts/youtube_api_pool.py list
```

## 配额说明

- 每个 API Key 每天 10,000 单位
- 搜索 API：100 单位/次
- 视频详情 API：1 单位/次（最多 50 个视频/次）
- 3 个 Key = 30,000 单位/天 = 300 次搜索

## 使用示例

```bash
# 在脚本中使用
API_KEY=$(python3 ~/.hermes/scripts/youtube_api_pool.py current)
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=OBSBOT&type=video&key=$API_KEY"

# 配额用完时轮换
python3 ~/.hermes/scripts/youtube_api_pool.py rotate
API_KEY=$(python3 ~/.hermes/scripts/youtube_api_pool.py current)
```
