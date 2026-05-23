# YouTube 全量视频搜索 + KOL 调研工作流

当用户要求搜索某产品的**所有 YouTube 视频**并整理成表格时，使用此工作流。

## 工作流

### Step 1: 多关键词搜索（delegate_task）
- 15-20 组关键词，每组翻页到 250 条上限
- 去重（按 videoId）
- 典型耗时：2-3 分钟

### Step 2: 过滤产品变体
- 用正则排除不需要的产品变体（如 ISO 版本、Lite 版本等）
- 从 title + description 中匹配排除关键词

### Step 3: 批量获取详情（execute_code）
- 视频统计：videos API，每次 50 个 ID
- 频道信息：channels API，每次 50 个 ID
- 注意 API 配额限制，遇到限流停止

### Step 4: 自动分析（execute_code）
- 网红类型分类（头部/腰部/中小/素人 × 科技/影视/音乐等）
- 视频分类（评测/开箱/教程/直播/对比等）
- 使用场景识别
- 关键词提取
- Pros/Cons 从 description 中提取

### Step 5: 上传腾讯文档
- 创建 smartsheet（英文短标题 → rename → move）
- 添加字段后清理默认字段和空行
- 小批次上传（10 条/批）
- 用文件传递 JSON 参数避免 shell 截断

## 关键 Pitfalls
- YouTube API 搜索配额有限，20 组查询可能中途被限流
- 腾讯文档 smartsheet 标题最长 36 字符
- 批量上传 output 超 20KB 会截断，必须小批次
- 详见 `tencent-docs` skill 的 `references/smartsheet-pitfalls.md`
- 详见 `youtube-scraping` skill 的 `references/product-youtube-search.md`
