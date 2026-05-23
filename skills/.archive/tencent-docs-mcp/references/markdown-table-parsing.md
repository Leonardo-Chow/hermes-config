# 从 get_content 解析 Markdown 表格

## 问题

`get_content` 返回的 SmartSheet/Sheet 数据格式是 pipe-delimited Markdown 表格：

```
|工作表1
|博主名称|博主粉丝量|视频标题|观看次数|点赞量|评论数量|发布日期|产品型号|Tags|视频链接|
|----|----|----|----|----|----|----|----|----|----|
|BuyNestix|40|Insta360 Link 2C Tripod Bundle|2|0|0|2026-05-11|Insta360 Link 2C|tags|https://youtube.com/watch?v=xxx|
```

**核心难题**：视频标题等文本字段可能包含 `|` 字符（如 `Insta360 Link 2C Pro 4K Webcam | Unsponsored Review`），导致 naive `line.split("|")` 列错位。

## 解决方案：反向锚定解析

不从左往右 split，而是利用格式固定的字段作为锚点从右往左定位。

### 锚点识别

| 列 | 格式 | 可靠度 |
|----|------|--------|
| 视频链接 | `https://youtube.com/watch?v=[a-zA-Z0-9_-]+` | ✅ 固定格式 |
| 发布日期 | `\d{4}-\d{2}-\d{2}` | ✅ 固定格式 |
| 观看次数/点赞/评论 | 纯数字（可含 K/M 后缀） | ✅ 末尾 3 列连续数字 |
| 博主粉丝量 | 数字+K/M | ⚠️ 可能和标题中数字混淆 |
| 视频标题 | 任意文本，含 `|` | ❌ 不可靠，不能作为锚点 |

### 解析流程

```
1. 正则提取 URL（从整个行）→ 移除 URL 及其后内容
2. 正则提取日期 YYYY-MM-DD → 分割为「日期前」和「日期后」
3. 日期后 = 产品型号 | Tags
4. 日期前 = 博主名称 | 粉丝量 | 标题 | 观看 | 点赞 | 评论
5. 从日期前的右侧找 3 个连续数字字段 = 观看/点赞/评论
6. 3 个数字字段左边 = 标题（可能含多个 |，合并）
7. 标题左边第一个 = 粉丝量，再左边 = 博主名称
```

### Python 实现要点

```python
import re

def parse_line(line):
    # 1. 提取 URL
    url_match = re.search(r'(https://youtube\.com/watch\?v=[a-zA-Z0-9_-]+)', line)
    url = url_match.group(1)
    before_url = line[:url_match.start()].rstrip("| ")

    # 2. 提取日期
    date_match = re.search(r'\|(\d{4}-\d{2}-\d{2})\|', before_url)
    date = date_match.group(1)

    # 3. 日期后 = 产品型号 + Tags
    after_date = before_url[date_match.end():].strip("| ")
    after_parts = [p.strip() for p in after_date.split("|")]
    product = after_parts[0]
    tags = "|".join(after_parts[1:])  # Tags 也可能含 |

    # 4. 日期前 = 名称 + 粉丝 + 标题 + 3个数字
    before_date = before_url[:date_match.start()].rstrip("| ")
    parts = [p.strip() for p in before_date.split("|")]

    # 5. 从右找 3 个数字字段
    num_pattern = re.compile(r'^[\d,.]+[KMkm]?$')
    numeric_indices = []
    for i in range(len(parts)-1, max(len(parts)-6, -1), -1):
        if num_pattern.match(parts[i].replace(" ", "")):
            numeric_indices.insert(0, i)
            if len(numeric_indices) == 3:
                break

    views_idx, likes_idx, comments_idx = numeric_indices

    # 6. 标题 = 数字字段左边的中间部分（合并 |）
    name = parts[0]
    title_parts = parts[1:views_idx]
    followers = title_parts[0]
    title = "|".join(title_parts[1:])  # 关键：合并含 | 的标题

    return {
        "博主名称": name,
        "博主粉丝量": followers,
        "视频标题": title,
        "观看次数": parts[views_idx],
        "点赞量": parts[likes_idx],
        "评论数量": parts[comments_idx],
        "发布日期": date,
        "产品型号": product,
        "Tags": tags,
        "视频链接": url,
    }
```

## 注意事项

- 首行 `|工作表1` 是 Sheet 名称标记，需跳过
- 表头行包含 `博主名称`，需跳过
- 分隔行 `|---|---|` 需跳过
- YouTube 链接格式固定，但其他平台可能不同，需调整 URL 正则
- 数字锚点法假设最后 3 列是纯数字；如果列顺序变化需调整
- **get_content 字符截断**：API 返回内容约 27K 字符后截断，大表格后半部分数据丢失。无法用 `get_content` 验证大数据量写入，需信任 `set_range_value` 的成功响应（`"error": ""`）。
- **file_id 必须用 search_file 返回的**，不能用 URL 中的 sheet ID。
