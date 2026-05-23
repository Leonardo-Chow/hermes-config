# YouTube 数据采集 → 腾讯文档智能表格上传工作流

## 适用场景

YouTube Data API 采集视频数据，清洗后批量上传到腾讯文档智能表格。支持网红调研、竞品分析、产品评测汇总等场景。

## 完整流程

### 1. YouTube API 搜索

```python
import requests

API_KEY = "YOUR_YOUTUBE_API_KEY"
BASE_URL = "https://www.googleapis.com/youtube/v3"

# 搜索视频
params = {
    "part": "snippet",
    "q": "搜索关键词",
    "type": "video",
    "publishedAfter": "2026-01-13T00:00:00Z",  # 产品上市日期
    "maxResults": 50,
    "order": "date",
    "key": API_KEY
}
response = requests.get(f"{BASE_URL}/search", params=params)
```

**要点**：
- 多组关键词搜索以提高覆盖率（产品名、review、unboxing、test、vs 等）
- 每次搜索之间加 `time.sleep(0.1)` 避免 API 限流
- 搜索结果按 video_id 去重
- 用 `pageToken` 翻页，每个查询最多 5 页（250 条）
- **VPN 必须连接**（中国大陆环境），否则 API 超时

### 2. 获取视频详情（批量）

```python
# 每批最多 50 个 video_id
params = {
    "part": "snippet,statistics,contentDetails",
    "id": ",".join(video_ids),
    "key": API_KEY
}
response = requests.get(f"{BASE_URL}/videos", params=params)
```

**关键字段**：
- `statistics`: viewCount, likeCount, commentCount
- `contentDetails`: duration (ISO 8601 格式)
- `snippet`: tags, categoryId

**频道信息**：
```python
# 获取频道订阅数和国家
params = {"part": "snippet,statistics", "id": channel_ids, "key": API_KEY}
response = requests.get(f"{BASE_URL}/channels", params=params)
# → subscriberCount, country
```

### 3. 获取评论（用于 Pros/Cons 分析）

```python
# 按相关度排序获取热门评论
params = {
    "part": "snippet",
    "videoId": video_id,
    "maxResults": 10,
    "order": "relevance",  # 按点赞数排序
    "key": API_KEY
}
response = requests.get(f"{BASE_URL}/commentThreads", params=params)
```

**要点**：
- 逐视频获取，`time.sleep(0.08)` 避免限流
- 提取 `textDisplay` 和 `likeCount`
- 评论是 Pros/Cons 的**真实数据来源**，不要仅靠标题推断

### 4. 数据清洗

**去重规则**：
- 标题和描述中都不包含目标产品名 → 移除
- 竞品单独视频（标题不含目标产品名）→ 移除

**过滤规则**（满足任一即移除）：
- 素人粉丝数 < 1000
- 视频无评论（commentCount == 0）
- 视频无点赞（likeCount == 0）
- 关键词不包含核心产品名

**网红类型分类**（按内容实际类型，非粉丝量级）：
- Livestream: 直播相关
- Camera: 摄像头/摄影设备
- Review: 评测/开箱
- Tutorial: 教程/设置指南
- Podcast: 播客/音频
- Church/Worship: 教会
- Gaming: 游戏
- Comparison: 对比评测
- Broadcast: 广播/新闻
- General Video: 其他

**受众地区格式**：`English Name/中文名`
- 欧洲国家统一标注为 `Germany/欧洲`, `France/欧洲`, `Italy/欧洲` 等
- 非欧洲：`United States/美国`, `Japan/日本`, `India/印度` 等

**关键词提取**（从标题+描述）：
- 产品名、功能特性、使用场景
- 描述中的 Hashtags (#xxx)
- 竞品名（如有对比）

**Pros/Cons 提取**（必须基于评论区真实内容）：
- Pros：用户认可的功能点（如"画质优秀"、"操作友好"、"多机位切换流畅"）
- Cons：用户不认可的功能点（如"散热问题"、"固件不稳定"、"价格偏高"）
- 每条精简提炼，不超过 8 个字

### 5. 上传到腾讯文档智能表格

```bash
# 创建智能表格（⚠️ 中文标题可能报错，先用英文再重命名）
mcporter call tencent-docs manage.create_file --args '{
  "title": "Product YouTube Data",
  "file_type": "smartsheet"
}'
# → 获取 file_id

# 重命名为中文标题
mcporter call tencent-docs manage.rename_file_title --args '{
  "file_id": "xxx",
  "title": "产品 YouTube视频数据"
}'

# 移动到目标文件夹
mcporter call tencent-docs manage.move_file --args '{
  "file_id": "xxx",
  "target_folder_id": "folder_id"
}'

# 获取工作表 ID
mcporter call tencent-docs smartsheet.list_tables --args '{"file_id": "xxx"}'
# → 获取 sheet_id

# 添加字段
mcporter call tencent-docs smartsheet.add_fields --args '{
  "file_id": "xxx",
  "sheet_id": "xxx",
  "fields": [...]
}'

# 删除默认空行和字段
# ... (同上)

# 批量添加记录（⚠️ 每批 ≤10 条，避免输出截断）
# 使用文件传递 JSON 避免 shell 转义问题
echo "$PAYLOAD" > /tmp/atem_batch.json
mcporter call tencent-docs smartsheet.add_records --args "$(cat /tmp/atem_batch.json)"
```

**重命名列**：
```bash
mcporter call tencent-docs smartsheet.update_fields --args '{
  "file_id": "xxx",
  "sheet_id": "xxx",
  "fields": [{"field_id": "fXXX", "field_title": "新列名", "field_type": "text"}]
}'
```

## KOL 调研数据采集完整工作流

### 数据结构（13列标准表头）

| 列名 | 类型 | 说明 |
|:-----|:-----|:-----|
| 网红ID | text | 频道名称 |
| 渠道链接 | text | YouTube 频道 URL |
| 网红类型 | text | 见下方分类表 |
| 受众地区 | text | `English/中文` 格式 |
| 量级（k） | number | 近三年均播/1000 |
| 案例视频 | text | 最佳表现视频 URL |
| 点赞量 | number | 视频点赞数 |
| 评论数 | number | 视频评论数 |
| 关键词铺设 | text | 标题+描述+Hashtags |
| 场景 | text | 具体使用场景 |
| Pros | text | 评论区正面反馈 |
| Cons | text | 评论区负面反馈 |
| 结论 | text | ≤30字精简评价 |

### 网红类型分类（必须基于视频内容）

| 类型 | 触发条件 |
|:-----|:---------|
| Livestream | 标题含 livestream/live stream/concert/conference |
| Camera/Video | 标题含 camera/cinema/filmmaking/dslr |
| Tutorial/Education | 标题含 tutorial/how to/setup/guide |
| Product Review | 标题含 review/unboxing/hands on/comparison |
| Gaming/Esports | 标题含 gaming/game/esports/twitch |
| Church Production | 标题含 church/worship/propresenter |
| Music Production | 标题含 music/recording/audio/band |
| Corporate/Business | 标题含 corporate/business/meeting/webinar |
| Podcast Production | 标题含 podcast/interview/talk show |

**禁止使用**：`Tech/Video Production`、`内容创作`、`视频制作` 等泛化类型。

### 量级计算公式

```
量级(k) = 近三年所有视频的平均播放量 ÷ 1000
```

**计算步骤**：
1. 获取频道 uploads playlist ID：`GET /channels?part=contentDetails`
2. 获取近三年视频列表：`GET /playlistItems?part=snippet`，过滤 `publishedAt >= 三年前`
3. 批量获取播放量：`GET /videos?part=statistics`（每批50个）
4. 计算平均值：`total_views / video_count`

**注意**：量级反映的是频道整体播放能力，不是单个视频表现。无近三年视频的频道量级为 0。

### 受众地区格式

必须使用 `English/中文` 格式：
- `United States/美国`, `United Kingdom/英国`
- 欧洲国家统一标注：`Germany/欧洲`, `France/欧洲`, `Sweden/欧洲`
- 亚洲：`Japan/日本`, `South Korea/韩国`, `India/印度`
- 其他：`Australia/澳大利亚`, `Brazil/巴西`
- 未知：`Global/全球`

### KOL 去重规则

**每个 KOL 只保留一个视频**（表现最佳的那个）：
1. 按 `channelId` 分组
2. 选择 `viewCount` 最高的视频作为案例视频
3. 最终记录数 = 唯一频道数（通常 60-70% 去重率）

### Pros/Cons 提取规则

**必须基于评论区真实内容**，不能仅靠标题推断：
1. 用 `commentThreads` API 获取每个视频的 Top 15 评论（按 relevance 排序）
2. 从评论中提取正面/负面反馈关键词
3. 精简提炼，每条不超过 8 个字
4. **无明确 Pro/Con 时用 `——` 代替**（禁止用"待分析"）

**Pro 示例**：画质优秀 | 多机位切换流畅 | 便携性好 | USB-C即插即用 | 音频处理优秀
**Con 示例**：散热问题 | 软件不稳定 | 价格偏高 | 学习曲线陡 | 屏幕太小

### 结论格式

**≤30 个中文字符**，格式：`层级+类型，关键优劣势，推荐建议`

示例：
- `头部评测，多机位切换流畅，注意学习曲线陡` (20字)
- `中腰部教堂制作，流媒体功能强，推荐关注` (19字)
- `尾部教程，价格偏高，可补充参考` (14字)

层级划分：头部(≥50k均播), 中腰部(10-50k), 腰部(5-10k), 尾部(<5k)

### 场景分类

必须基于视频标题+描述+评论分析，**禁止使用泛化描述**：

| 场景 | 触发条件 |
|:-----|:---------|
| Product Review | 评测/开箱/对比 |
| Tutorial/Education | 教程/设置/指南 |
| Church/Worship Streaming | 教会/礼拜/ProPresenter |
| Live Event Production | 演唱会/会议/活动 |
| Gaming/Esports | 游戏/电竞/直播 |
| Music Production | 音乐/录音/乐队 |
| Corporate/Business | 企业/会议/Zoom |
| Podcast Production | 播客/访谈 |

## Sheet API 更新工作流

当需要更新普通 Sheet（非 smartsheet）的单元格数据时：

```python
# 1. 获取子表信息
mcporter call tencent-docs sheet.get_sheet_info --args '{"file_id": "xxx"}'
# → sheet_id

# 2. 批量更新单元格（必须用类型化参数）
for i, val in enumerate(values):
    mcporter call tencent-docs sheet.set_cell_value --args '{
        "file_id": "xxx",
        "sheet_id": "xxx",
        "row": i + 1,       # 0-based, 数据从第2行开始
        "col": 4,           # 0-based, E列=4
        "value_type": "NUMBER",
        "number_value": val
    }'

# 3. 验证更新
mcporter call tencent-docs get_content --args '{"file_id": "xxx"}'
```

**⚠️ 关键 pitfall**：`set_cell_value` 必须使用 `value_type` + `number_value`/`string_value`，不能用 `value` 字段。

## 用户偏好

- **视频链接用文本类型，不要超链接类型**（用户明确要求）
- 观看次数等数字字段用千位分隔（`use_separate: true`）
- **每批记录 ≤10 条**（50 条会导致 mcporter 输出截断）
- **网红类型按实际内容分类**，不要用 KOL 量级（头部/腰部/素人）
- **受众地区必须带英文名**：`United States/美国`
- **Pros/Cons 必须基于评论区真实内容**，不能仅靠标题推断
- **关键词从标题+描述+Hashtags 综合提取**
- **量级是近三年均播**，不是粉丝数
- **结论 ≤30 字**，精简评价
- **无 Pros/Cons 时用 `——`**，禁止用"待分析"
- **每个 KOL 只保留一个最佳视频**

## Pitfalls

- `mcporter call` 用**空格分隔**，不是点号：`mcporter call tencent-docs tool_name --args '...'`
- 字段类型（field_type）创建后**不可修改**，需要删除重建
- 单选字段的 `text` 必须与已定义的选项完全匹配
- 默认工作表名为"智能表1"，需要先 `list_tables` 获取 sheet_id
- **⚠️ `manage.create_file` 中文标题可能报错 400010**：先用英文标题创建，再用 `manage.rename_file_title` 改为中文
- **⚠️ mcporter 输出截断**：50 条记录的 JSON 响应超过 20K 字符会被截断，导致 JSON 解析失败。**必须用 ≤10 条/批**
- **⚠️ JSON 大载荷**：用 `write_file` 写入临时文件 + `$(cat /tmp/file.json)` 命令替换传递，不要内联 JSON
- **⚠️ 批量删除记录**：用 `python3 -c "import sys,json; ..."` 管道提取 record_id，避免输出截断导致解析失败
- **⚠️ API 配额**：YouTube Data API 有每日配额限制，大批量搜索可能耗尽配额
