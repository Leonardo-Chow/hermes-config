# OBSBOT 每日监测工作流

每日监测 OBSBOT 产品在 YouTube/Instagram/TikTok/X 四大平台的新增内容，创建智能表格记录。

## 触发条件

用户要求「每日监测」「今天更新的 OBSBOT 视频」「daily monitor」时执行。

## 产品关键词

```
OBSBOT Tail Air, OBSBOT Tail 2, OBSBOT Meet SE, OBSBOT Meet 2,
OBSBOT Tiny SE, OBSBOT Tiny 2, OBSBOT Tiny 2 Lite,
OBSBOT Tiny 3, OBSBOT Tiny 3 Lite, OBSBOT Talent 2
```

## 视频类型分类

| 类型代码 | 平台 | 说明 |
|:---------|:-----|:-----|
| YTB Dedicated Video | YouTube | 纯 OBSBOT 产品评测/开箱/展示 |
| YTB Integration Video | YouTube | 视频中使用 OBSBOT 但主题不是评测（设备列表、赞助植入、使用场景） |
| YTB Shorts | YouTube | YouTube Shorts 短视频 |
| TT video | TikTok | TikTok 视频 |
| INS reel | Instagram | Instagram Reels |
| INS post | Instagram | Instagram 图文帖子 |
| X post | X/Twitter | 推文 |

## 搜索策略

### YouTube（置信度 HIGH）

使用 YouTube Data API v3，API Key 在 memory 中。

```bash
# 按关键词搜索今天发布的视频
curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=OBSBOT+Tiny+3&type=video&publishedAfter=${TODAY}T00:00:00Z&publishedBefore=${TODAY}T23:59:59Z&maxResults=20&key=${API_KEY}"

# 获取完整视频详情（含完整 description）
curl -s "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${VIDEO_IDS}&key=${API_KEY}"
```

**关键**：
- 10 个产品关键词逐一搜索
- 日期过滤无效时，手动检查 publishedAt 是否为今天
- 去掉 "OBSBOT" 前缀再搜一遍（如 "Tiny 3 review"）
- 过滤误报（游戏直播标签含 OBSBOT 但内容无关）

### Instagram（置信度 MEDIUM）

**方法1：web_search（快速，覆盖有限）**

```
web_search('site:instagram.com OBSBOT 2026')
web_search('instagram OBSBOT "May 29" 2026')
web_search('instagram.com obsbot reel May 2026')
```

**方法2：Scrapling StealthyFetcher（深度爬取，推荐）**

Scrapling 可以成功爬取 Instagram @obsbot 公开页面，获取帖子链接、描述、产品提及。需要 Python 3.10+ venv。

```python
import sys
sys.path.insert(0, '/Users/zhoulong/.hermes/skills/scrapling/venv/lib/python3.12/site-packages')
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://www.instagram.com/obsbot/',
    headless=True, network_idle=True, disable_resources=True,
    block_webrtc=True, hide_canvas=True,
)
# 获取帖子链接
post_links = page.css('a[href*="/p/"]::attr(href)').getall()
post_links += page.css('a[href*="/reel/"]::attr(href)').getall()
# 获取描述文本
texts = page.css('article *::text').getall()
```

**2026-05-29 验证结果**：成功爬取 12 条 @obsbot 帖子 + 5 条 #obsbot 热门帖。能找到帖子链接和描述，但**无法获取精确发布日期**（Instagram 公开页面不显示日期，需登录）。

**⚠️ 已知问题**：
- web_extract 被 Instagram 登录墙拦截
- Scrapling 能获取帖子但**无法确定精确日期**（只有相对顺序）
- 搜索引擎索引延迟（当天帖子可能几小时后才收录）
- 第一次搜索可能遗漏！必须用多种查询变体重试
- 检查 @obsbot 官方 bio 中是否有当天活动信息
- 需要 VPN（Shadowrocket）才能访问 Instagram

### TikTok（置信度 LOW）

```
web_search('site:tiktok.com OBSBOT 2026')
web_search('tiktok OBSBOT Tiny 3 May 2026')
```

**⚠️ 已知限制（2026-05-29 全面验证）**：

TikTok 的视频列表受 `X-Bogus` 反爬令牌保护，以下所有方案均已验证失败：

| 方案 | 结果 | 原因 |
|:-----|:-----|:-----|
| curl + proxy | ❌ 空响应 | API 需要 X-Bogus 参数 |
| Scrapling DynamicFetcher + proxy | ❌ 视频不渲染 | SSR itemList 为空，视频由客户端 JS API 加载 |
| Playwright + 用户 Cookie | ❌ 被反爬检测 | 无头浏览器指纹被识别 |
| bb-browser (真实 Chrome + CDP) | ❌ API 返回空 | 手动 fetch 缺 X-Bogus 令牌 |
| NoxInfluencer | ⚠️ 仅 tagged 创作者 | 无法按日期筛选，无法确认当天是否发了 OBSBOT 内容 |

**结论**：TikTok 目前无法自动化爬取视频列表。X-Bogus 由 TikTok 客户端 JS 动态生成，无法在非浏览器环境或通过 API 拦截模拟。

**降级方案**：
1. 用户手动打开 @obsbot TikTok 主页查看今天是否有新视频
2. NoxInfluencer Brand Monitor 配置后长期监控（需要 brand_id）
3. web_search 搜索 TikTok 相关内容（覆盖有限，索引延迟严重）

### X/Twitter（置信度 LOW）

```
web_search('site:x.com OBSBOT 2026')
web_search('twitter OBSBOT "May 29" 2026')
web_search('twitter.com OBSBOT Tail 2 2026')
```

**⚠️ 已知限制**：
- X 内容实时索引差
- web_extract 被 X 拦截
- NoxInfluencer 不支持 X 平台
- 在 GFW 环境下需要 VPN

## 视频过滤规则

**必须过滤的内容**：

1. **设备列表/产品列表视频**：提到OBSBOT但无实质评测内容
2. **游戏/直播/杂谈**：OBSBOT仅作为"设备之一"被提及
3. **技术参数对比/规格表**：无实际使用体验
4. **专业媒体/技术评测**：GadgetDoc等技术分析型频道，非KOC视角
5. **Vlog/直播中的提及**：在其他内容（赛车、游戏）中顺便使用OBSBOT
6. **俄语/日语/韩语/东南亚语言博主**：自动过滤（俄语KOL自发评测/开箱/对比等有价值内容应保留）
7. **音频/灯光/非摄像头设备评测**：OBSBOT仅在设备列表中被提及（如播客设备推荐中的Tail 2）
8. **整套设备推荐**：OBSBOT非主角，仅作为设备之一（如"20款科技好物"）

**保留的内容**：
- ✅ 专门评测OBSBOT产品的视频（Dedicated Video）
- ✅ 品牌大使开箱/展示视频
- ✅ 包含OBSBOT折扣码/购买链接的视频
- ✅ 俄语KOL自发评测/开箱/对比（有价值内容）
- ✅ OBSBOT作为主要设备的播客/直播设备推荐

## 置信度标注规范

搜索结果必须标注置信度：

| 置信度 | 含义 | 判定条件 |
|:-------|:-----|:---------|
| HIGH | 确认有/无内容 | API 直接查询（YouTube Data API） |
| MEDIUM | 可能有/无 | web_search 有结果但无法直接验证 |
| LOW | 无法确认 | 平台拦截、搜索引擎不索引、工具不可用 |

## 简介完整性要求（用户明确要求）

视频简介必须包含**所有内容**，不能摘要：

- ✅ 完整描述文字（逐字，不删减）
- ✅ 营销链接（affiliate/official/amazon 链接）
- ✅ 折扣码（coupon code / promo code）
- ✅ Hashtags 和 tags
- ✅ 免责声明（disclaimer/sponsor 声明）
- ✅ 社交媒体链接
- ✅ 购买链接（smartstore/amazon 等）
- ✅ 联系方式（电话/邮箱/网站）
- ❌ 不要总结或精简

## 腾讯文档表格结构

在 `云盘→OBSBOT→每日监测` 文件夹（ID: `DumZsGZJrwsf`）创建智能表格。

### 7 列定义

| 列名 | 类型 | 说明 |
|:-----|:-----|:-----|
| 更新时间 | text | 格式 `YYYY-MM-DD HH:MM` 或 `YYYY-MM-DD` |
| KOL ID | text | 频道名/账号 handle |
| 产品关键词 | text | 具体产品名（如 OBSBOT Tiny 3 / VOX SE） |
| 平台 | text | YouTube / Instagram / TikTok / X |
| 视频类型 | text | YTB Dedicated Video / YTB Integration Video / YTB Shorts / TT video / INS reel / INS post / X post |
| 视频简介 | text | **完整描述**（见上方简介完整性要求） |
| 视频链接 | text | 视频/帖子 URL（文本类型，非超链接类型） |

### 创建流程

```
1. manage.create_file → 创建 smartsheet（先用英文标题）
2. smartsheet.list_tables → 获取 sheet_id
3. smartsheet.list_fields → 获取默认字段
4. smartsheet.delete_fields → 逐个删除默认字段
5. smartsheet.add_fields → 添加 7 个自定义字段（每个必须含 property_text: {}）
6. smartsheet.list_records → 获取默认空行
7. smartsheet.delete_records → 删除默认空行
8. smartsheet.add_records → 添加数据（每批 ≤10 条）
9. smartsheet.rename_table → 重命名工作表标签
10. manage.rename_file_title → 改为中文标题
11. manage.move_file → 移动到每日监测文件夹
```

**⚠️ 重要**：
- 链接字段用 `text` 类型，不用 `url` 类型
- 中文标题先用英文创建再 rename
- 先删除默认字段再添加自定义字段
- `property_text: {}` 必须包含，否则字段创建静默失败

## 并行搜索策略

使用 `delegate_task` 3 路并行：

| 路线 | 任务 | 工具 |
|:-----|:-----|:-----|
| 路线1 | YouTube API 搜索 10 个关键词 | terminal (curl) |
| 路线2 | Instagram/TikTok/X web_search + NoxInfluencer | web + terminal |
| 路线3 | 腾讯文档文件夹定位 | terminal (mcporter) |

总耗时约 5-8 分钟。

## 输出汇报格式

```
✅ 任务执行完毕

## 搜索结果（YYYY-MM-DD）
| 平台 | 搜索结果 | 置信度 |
|:-----|:---------|:------|
| YouTube | ✅ N条 | HIGH |
| Instagram | ✅/❓ N条 | MEDIUM/LOW |
| TikTok | ❓ 未检测到 | LOW |
| X/Twitter | ❓ 未检测到 | LOW |

## 表格已创建
- 位置：云盘→OBSBOT→每日监测
- 链接：[表格名](URL)
- 记录数：N条

## ⚠️ 检测限制说明
（如有平台置信度为 LOW，必须说明原因）
```

## 常见陷阱

### ⚠️ YouTube API bash 命令语法
当在 bash 中使用 `$(...)` 命令替换获取 API Key 时，如果命令包含 `&` 字符，会导致语法错误（被解释为后台运行）。解决方案：
```bash
# ❌ 错误：直接在 bash 中使用 $(...)
API_KEY=*** ~/.hermes/scripts/youtube_api_pool.py current)
curl "...&key=$API_KEY"  # & 会被解释为后台运行

# ✅ 正确：写入 Python 脚本后执行
cat > /tmp/get_videos.py << 'EOF'
import subprocess
result = subprocess.run(['python3', '/path/to/youtube_api_pool.py', 'current'], capture_output=True, text=True)
API_KEY=*** ... 脚本内容
EOF
python3 /tmp/get_videos.py
```

### ⚠️ Tavily API 配额限制
Tavily API 有月度配额限制，超额后返回 HTTP 432。解决方案：
1. 检查配额：`mcp_tavily_tavily_search` 返回 432 错误
2. 降级方案：使用 `web_search` 替代（但覆盖有限）
3. 手动检查：建议用户手动查看 @obsbot 社交媒体主页

### ⚠️ 系统 Python vs venv
python-docx 和 openpyxl 安装在系统 Python 3.9 中（`~/Library/Python/3.9/lib/python/site-packages/`），不在 Hermes venv 中。必须用 `python3` 而非 venv 的 python。

### ⚠️ Excel 中文编码
openpyxl 读取中文内容时默认 UTF-8，一般不需要额外处理。但如果遇到乱码，检查文件编码。
