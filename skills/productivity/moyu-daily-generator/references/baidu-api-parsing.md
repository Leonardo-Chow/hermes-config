# 百度热搜 API 解析模式

## 正确的解析方式（2026-05-28 验证）

**问题**：直接将 curl 输出管道到 Python 解析容易超时或阻塞。

**解决方案**：分两步执行——先保存到文件，再解析。

### 步骤 1：保存到文件

```bash
curl -s 'https://top.baidu.com/api/board?tab=realtime' \
  -H 'User-Agent: Mozilla/5.0' \
  -o /tmp/baidu_hot.json
```

### 步骤 2：解析文件

```python
python3 -c "
import json

with open('/tmp/baidu_hot.json', 'r') as f:
    data = json.load(f)

cards = data.get('data', {}).get('cards', [])
if cards:
    content = cards[0].get('content', [])
    for i, item in enumerate(content[:8]):
        title = item.get('word', '')
        score = item.get('hotScore', '')
        url = item.get('url', '')
        print(f'{i+1}. {title} (热度: {score})')
        print(f'   链接: {url}')
"
```

## 数据结构

```json
{
  "success": true,
  "data": {
    "cards": [
      {
        "component": "hotList",
        "content": [
          {
            "word": "热搜标题",
            "hotScore": "7808471",
            "url": "https://www.baidu.com/s?wd=...",
            "desc": "描述文本",
            "hotTag": "3",
            "hotChange": "same"
          }
        ]
      }
    ]
  }
}
```

## 关键字段

| 字段 | 说明 |
|:-----|:-----|
| `word` | 热搜标题 |
| `hotScore` | 热度值（字符串） |
| `url` | 搜索链接 |
| `desc` | 描述文本 |
| `hotTag` | 标签类型（1=新, 3=热, 5=荐） |
| `hotChange` | 变化趋势（same=持平, up=上升, down=下降） |

## 注意事项

1. **必须分步执行**：不要用管道连接 curl 和 Python，容易超时
2. **保存到临时文件**：使用 `/tmp/baidu_hot.json` 作为中间文件
3. **解析后清理**：解析完成后可以删除临时文件
4. **错误处理**：检查 `success` 字段和 `cards` 是否为空

## 完整示例（带错误处理）

```bash
# 保存到文件
curl -s 'https://top.baidu.com/api/board?tab=realtime' \
  -H 'User-Agent: Mozilla/5.0' \
  -o /tmp/baidu_hot.json

# 检查是否成功
if [ -s /tmp/baidu_hot.json ]; then
  python3 -c "
import json, sys

try:
    with open('/tmp/baidu_hot.json', 'r') as f:
        data = json.load(f)
    
    if not data.get('success'):
        print('API 返回失败', file=sys.stderr)
        sys.exit(1)
    
    cards = data.get('data', {}).get('cards', [])
    if not cards:
        print('无数据', file=sys.stderr)
        sys.exit(1)
    
    content = cards[0].get('content', [])
    for i, item in enumerate(content[:8]):
        title = item.get('word', '')
        score = item.get('hotScore', '')
        url = item.get('url', '')
        print(f'{i+1}. {title} (热度: {score})')
        print(f'   链接: {url}')
except Exception as e:
    print(f'解析错误: {e}', file=sys.stderr)
    sys.exit(1)
"
else
  echo "保存失败"
fi
```
