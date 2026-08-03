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
- **⚠️ 品牌大使直播不算 Dedicated Video**（Michael Alama 等定期使用 OBSBOT 直播的博主，属于 Integration Video）

### Instagram（必须执行，置信度 MEDIUM）

**⚠️ Instagram 搜索是必选项**，每天必须执行。用户多次反馈漏掉了 Instagram 帖子。

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

## OBSBOT上线监测完整SOP（2026-06-24更新）

### 目标
1. 建立统一的视频上线搜集与检查流程，及时追踪各平台产品相关视频的发布情况，确保视频按营销节奏上线，并检查描述区链接、折扣信息、标签等内容是否完整。
2. 持续搜集优质内容、行业活动相关内容及红人自发视频，沉淀可复用素材与案例，为后续营销推广、合作优化及品牌传播提供支持。

### Step 1 社交媒体检索推广视频

**覆盖平台**：YouTube/Instagram/TikTok/X

**产品关键词**：
```
OBSBOT / Talent 2 / Tiny 3 / Tiny 3 Lite / Tail 2 / Tiny 2 Lite / Meet 2 / Tiny SE / Meet SE / Tiny 2 / Tail Air
```
*建议优先按照项目规划产品进行检索，例如6月上线应参考4月规划产品

**视频类型细化**：
- YTB Dedicated Video
- YTB Integration Video
- YTB Shorts
- TT video
- INS reel
- INS post
- X post

**判定依据**：视频必须包含完整的产品测评内容
- ❌ 无效视频：只是挂了购买链接未在视频内展示产品
- ❌ 无效视频：纯官方宣传素材切片
- ❌ 无效视频：游戏/娱乐视频中OBSBOT仅在设备列表中提及
- ❌ 无效视频：音乐反应/生活方式视频中OBSBOT仅在设备列表中提及

**⚠️ 重要：只筛选美欧博主**（用户明确要求多次）
- 俄语/日语/韩语/东南亚语言博主自动过滤
- 西班牙语/葡萄牙语/法语/德语/意大利语博主可保留（属于美欧）
- 俄语KOL自发评测/开箱/对比等有价值内容可保留
- 过滤方法：检查描述和标题中是否包含亚洲语言关键词

### Step 2 推广视频内容质检

**1. 视频内容**：
- 是否包含原画直出
- 是否是特殊主题：榜单/对比/OBS教程/多机搭建/特殊使用场景（播客/体育/直播）等需要特殊标记
- 常规的产品测评/工作流展示/desk setup/小工具推荐不用特殊标记
- 非合作性质视频：博主自发测评，根据博主体量大小/视频内容价值自行判断
- 展会/采访等特殊活动视频：需要标记

**2. 视频描述区**：
- 是否包含官网链接/亚马逊链接/渠道链接（如有）/标签/折扣信息
- 有些博主喜欢用短链，不确定链接是否正确可以直接点开查看
- 有些博主喜欢用1-2个标签，例如只选择#obsbot；#obsbot_tiny3lite，这些也属于符合视频信息完善
- 如果信息有遗漏，可以标记出来提醒对应的小伙伴

### Step 3 信息汇总&同步业务群

**1. 已合作红人**：需标记对应小伙伴名字
- 检索位置：网红系统/KOL资源交接表
- 对接资源需写原负责人和后续跟进人
- 一般合作的红人链接/标签/折扣信息都很全面，很好判断，少部分红人会遗漏信息
- 注意查看合作日期、产品、视频内容是否与系统录入一致
- 如24年合作的红人在26年检索到关键词视频，红人可能只是长期挂链接而非合作的，可标记为XXX曾经合作过

**2. 非合作红人**：需标记自发，如果是特殊主题也需要标记
- 同一个红人会在不同时间多平台发布，属于正常现象
- 每天都需同步上线视频，如遇节假日，需在工作日全部补齐

### 报告格式

**⚠️ 文件格式**：Word文档（不要用智能表格，用户多次明确要求）

**文件命名**：`YYYY-MM-DD-视频上线监测`（不要加"上午/下午"）

**⚠️ 每个视频条目格式**：
```
序号. 产品-KOL ID-@对应小伙伴名字（或KOC自发/KOL自发）
视频链接
视频标题
```

**⚠️ 重要：不要自己添加@KOL负责人员**（用户明确纠正）
- 我的任务是找到视频
- @KOL负责人员由用户或业务团队填写
- 如果知道负责人可以备注，但不要作为默认行为

**示例**：
```
1. Tiny 3 Lite-MCPHONEY-@熊雪博（Cecilia）
https://www.youtube.com/watch?v=qUL8jcAqYkE
Which AI Webcam is better? OBSBOT TINY 3 LITE vs YOLOCAM S3?

2. Tiny 3 Lite-VV Tech Enthusiast-KOC自发
https://www.youtube.com/watch?v=omuMxy98eOs
Webcam Pro Player & Live Streaming 4K! Obsbot Tiny 3 Lite + Obsbot Vox SE
```

**平台分类**：
- YouTube
- Instagram
- TikTok
- X/Twitter

**汇总统计**：
- TT/X暂无（如有内容需列出）

### ⚠️ mcporter doc.insert_markdown 已知故障

`mcporter call tencent-docs doc.insert_markdown` 在 mcporter 0.10.1 中持续报错 "missing required parameters: [idx]"，即使参数格式正确也无法调用。

**可靠替代方案**：使用 COS import 方式上传文档：
```bash
# Step 1: 上传到 COS
cd ~/.hermes/skills/tencent-docs
bash import_file.sh "/path/to/file.docx"
# 输出：IMPORT_READY, FILE_KEY, FILE_NAME, FILE_MD5, TASK_ID, FILE_SIZE

# Step 2: 触发异步导入
mcporter call "tencent-docs" "manage.async_import" --args '{"task_id": "<TASK_ID>", "file_size": "<FILE_SIZE>", "file_key": "<FILE_KEY>", "file_name": "<FILE_NAME>", "file_md5": "<FILE_MD5>"}'

# Step 3: 等待导入完成（15秒）
sleep 15

# Step 4: 搜索找到 file_id
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key": "文件名关键词"}'

# Step 5: 移动到每日监测文件夹 (DumZsGZJrwsf)
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id": "<file_id>", "target_folder_id": "DumZsGZJrwsf"}'
```

## OBSBOT上线监测SOP（权威版本 2026-06-25）

### ⚠️ 关键约束（用户反复强调）

1. **报告格式必须是Word文档**，不要用智能表格、markdown
2. **不要添加@KOL负责人员** — 这是用户的工作，AI只负责找到视频
3. **只筛选美欧博主** — 俄语/日语/韩语/东南亚语言博主自动过滤
4. **文件命名**：`YYYY-MM-DD-视频上线监测`（不要加"上午/下午"）

### 视频条目格式（用户确认的标准格式）

```
序号. 产品-KOL ID
视频链接
视频标题
```

**示例**：
```
19. Tiny 3 Lite-Faiz Aly
https://www.youtube.com/watch?v=LzOn9piupCE
The BEST Apple Deals & iPad/iPhone Accessories on Amazon Prime Day 2026

20. Tiny 3-Conor Butkovic
https://www.youtube.com/watch?v=q1E7L0R0mtU
Why I Bought Two Apple Studio Displays
```

### 完整SOP

**目标**：
1. 建立统一的视频上线搜集与检查流程，及时追踪各平台产品相关视频的发布情况
2. 持续搜集优质内容、行业活动相关内容及红人自发视频

**Step 1 社交媒体检索推广视频**

覆盖平台：YouTube/Instagram/TikTok/X

产品关键词：
```
OBSBOT / Talent 2 / Tiny 3 / Tiny 3 Lite / Tail 2 / Tiny 2 Lite / Meet 2 / Tiny SE / Meet SE / Tiny 2 / Tail Air
```

视频类型：YTB Dedicated Video / YTB Integration Video / YTB Shorts / TT video / INS reel / INS post / X post

判定依据：视频必须包含完整的产品测评内容
- ❌ 无效：只挂购买链接未在视频内展示产品
- ❌ 无效：纯官方宣传素材切片
- ❌ 无效：游戏/娱乐视频中OBSBOT仅在设备列表中提及

**Step 2 推广视频内容质检**

视频内容：
- 是否包含原画直出
- 是否是特殊主题：榜单/对比/OBS教程/多机搭建/特殊使用场景（播客/体育/直播）

描述区：
- 官网链接/亚马逊链接/渠道链接/标签/折扣信息

**Step 3 信息汇总**

已合作红人：需标记对应小伙伴名字（检索位置：网红系统/KOL资源交接表）
非合作红人：标记KOC自发/KOL自发

### Word文档上传流程（COS import方式）

mcporter doc.insert_markdown 在 mcporter 0.10.1 中不可用，必须用COS import：

```bash
# 1. 生成Word文档到 /tmp/YYYY-MM-DD-视频上线监测.docx

# 2. COS上传
cd ~/.hermes/skills/tencent-docs
bash import_file.sh /tmp/YYYY-MM-DD-视频上线监测.docx
# 记录 TASK_ID, FILE_KEY, FILE_NAME, FILE_MD5, FILE_SIZE

# 3. 触发异步导入
mcporter call "tencent-docs" "manage.async_import" --args '{"task_id": "...", "file_size": "...", "file_key": "...", "file_name": "...", "file_md5": "..."}'

# 4. 等待15秒后搜索文件
sleep 15
mcporter call tencent-docs manage.search_file --args '{"search_key": "YYYY-MM-DD-视频上线监测"}'

# 5. 移动到每日监测文件夹 (DumZsGZJrwsf)
mcporter call tencent-docs manage.move_file --args '{"file_id": "...", "target_folder_id": "DumZsGZJrwsf"}'
```

### YouTube API 注意事项

⚠️ youtube_api_pool.py 返回的key被截断/脱敏，无法直接使用。需要用memory中存储的完整API key。

## 搜索时间范围

**重要**：每天的监测报告只包含**当天**发布的视频，不是汇总。搜索范围应为：
- UTC时间：前一天 UTC 00:00 ~ 当天 UTC 23:59
- 北京时间：前一天 08:00 ~ 次日 07:59

例如6月22日的报告，搜索范围是6月21日 08:00 ~ 6月22日 07:59（北京时间）。

如果用户要求"汇总"多天数据，再扩大搜索范围。

**⚠️ 用户明确纠正过**：不要把多天数据混在一起报。每天只报当天的，用户会单独要求汇总。

## 视频过滤规则

**必须过滤的内容**：

1. **设备列表/产品列表视频**：提到OBSBOT但无实质评测内容
2. **游戏/直播/杂谈**：OBSBOT仅作为"设备之一"被提及（如 Vali2kx 游戏视频、Michael Alama 直播）
3. **技术参数对比/规格表**：无实际使用体验
4. **专业媒体/技术评测**：GadgetDoc等技术分析型频道，非KOC视角
5. **Vlog/直播中的提及**：在其他内容（赛车、游戏）中顺便使用OBSBOT
6. **俄语/日语/韩语/东南亚语言博主**：自动过滤（俄语KOL自发评测/开箱/对比等有价值内容应保留）
7. **棒球/体育直播**：OBSBOT仅在设备列表中提及（如 Darren Buchko StreamPro）
7. **音频/灯光/非摄像头设备评测**：OBSBOT仅在设备列表中被提及（如播客设备推荐中的Tail 2）
8. **整套设备推荐**：OBSBOT非主角，仅作为设备之一（如"20款科技好物"）

**保留的内容**：
- ✅ 专门评测OBSBOT产品的视频（Dedicated Video）
- ✅ 品牌大使开箱/展示视频（如 Tutz、ItsKole 等 #obsbotambassador 标签）
- ✅ 包含OBSBOT折扣码/购买链接的视频
- ✅ 俄语KOL自发评测/开箱/对比（有价值内容）
- ✅ Prime Day / 促销推荐中包含OBSBOT的视频（Integration Video）
- ✅ 桌搭/直播间搭建中使用OBSBOT的视频（Integration Video）
- ✅ 多产品对比横评中包含OBSBOT的视频（Integration Video）
- ✅ 直播技术/设备推荐中使用OBSBOT的视频（StreamTek等，Integration Video）

**产品识别注意**：
- Roomsthetic 频道 = 越南语博主，主要评测 Meet 2（不是 Tiny 2 Lite）
- Freaky Tech Reviews 可能评测 EMEET 产品（竞品），需仔细核对标题和描述
- ✅ OBSBOT作为主要设备的播客/直播设备推荐
- TechDriftzone = 印尼语博主，评测 Tiny 2 Lite（不是通用 OBSBOT）
- ANTMEDIA = 韩语博主，Tail 2 直播带货演示 → 保留（Dedicated Video）
- Michael Alama = 品牌大使直播 → Integration Video（非 Dedicated）
- Placide = 法语品牌大使，Tiny 3 评测 → Dedicated Video
- Vali2kx = 德语游戏博主，OBSBOT 仅在设备列表中 → 过滤
- VETOMIC = 游戏直播，OBSBOT Meet SE 仅在设备描述中 → 过滤
- MST.TV = Yu-Gi-Oh 卡牌游戏，OBSBOT 仅在设备列表中 → 过滤
- Darren Buchko StreamPro = 棒球直播，OBSBOT 仅在设备列表中 → 过滤
- PSS Creative Media = 多机位直播配置，OBSBOT Tail 2 非主角 → 过滤
- AML Equestrian Coaching = 马术教学，OBSBOT 非摄像头评测 → 过滤
- Zou RH = DJI 设备开箱，OBSBOT 仅在描述中提及 → 过滤

**⚠️ 用户反馈的过滤经验（2026-06-23 修正）**：
- 韩语直播带货（ANTMEDIA）= 保留（Dedicated Video，非设备列表）
- 多机位直播配置（PSS Creative Media）= 过滤（OBSBOT 非主角）
- 马术/体育教学（AML Equestrian Coaching）= 过滤（非摄像头评测）
- DJI 设备开箱（Zou RH）= 过滤（OBSBOT 仅设备列表）
- 意大利语 C64 视频（Tomnicist）= 过滤（非摄像头评测）

## Tavily API池管理

当Tavily API返回HTTP 432（配额耗尽）时，自动轮换API key：

```bash
# 获取当前API key
python3 ~/.hermes/scripts/tavily_api_pool.py current

# 轮换到下一个API key
python3 ~/.hermes/scripts/tavily_api_pool.py rotate

# 添加新的API key
python3 ~/.hermes/scripts/tavily_api_pool.py add <new_key>
```

**自动轮换逻辑**：
1. 调用Tavily API时，先用当前key
2. 如果返回HTTP 432（配额耗尽），自动调用 `rotate` 切换到下一个key
3. 重试请求
4. 如果所有key都耗尽，降级到web_search

**配置文件**：
- 脚本：`~/.hermes/scripts/tavily_api_pool.py`
- 配置：`~/.hermes/config/tavily_api_pool.json`
- MCP配置：`~/.hermes/config.yaml`（已更新）

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

## 腾讯文档报告上传

**⚠️ 用户明确要求：报告必须用 Word 文档（markdown），不要用智能表格。**

### 上传方式：COS import（推荐）

`doc.insert_markdown` 工具在 mcporter 0.10.1 中持续报错 "missing required parameters: [idx]"，无法使用。必须用 COS import 方式：

```bash
# Step 1: 上传 markdown 到 COS
cd ~/.hermes/skills/tencent-docs
bash import_file.sh /tmp/obsbot_report.md
# 输出：IMPORT_READY, FILE_KEY, FILE_NAME, FILE_MD5, TASK_ID, FILE_SIZE

# Step 2: 触发异步导入
mcporter call "tencent-docs" "manage.async_import" --args '{"task_id": "<TASK_ID>", "file_size": "<FILE_SIZE>", "file_key": "<FILE_KEY>", "file_name": "<FILE_NAME>", "file_md5": "<FILE_MD5>"}'

# Step 3: 等待导入完成（15-30秒）
sleep 20

# Step 4: 搜索找到 file_id
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key": "<关键词>"}'

# Step 5: 移动到每日监测文件夹 (DumZsGZJrwsf)
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id": "<file_id>", "target_folder_id": "DumZsGZJrwsf"}'
```

**⚠️ 已知问题**：
- mcporter `tencent-docs` 服务可能暂时离线（TCP timeout），需等待 30 秒后重试
- `manage.search_file` 可能因服务离线失败，需重试
- `doc.insert_markdown` 工具在 mcporter 0.10.1 中完全不可用，不要尝试

### 文件命名规范

**⚠️ 用户明确纠正过**：文件名不要加"上午/下午"时间段。

正确格式：`YYYY-MM-DD——视频上线监测`
错误示例：❌ `2026-06-23——视频上线监测——上午`

## YouTube API Python脚本模式

**⚠️ 已知问题**：在bash中使用`$(...)`命令替换获取API Key时，如果命令包含`&`字符，会导致语法错误（被解释为后台运行）。

**解决方案**：写入Python脚本后执行：

```python
# /tmp/obsbot_search.py
import subprocess
import json

def get_key():
    r = subprocess.run(['python3', '/Users/zhoulong/.hermes/scripts/youtube_api_pool.py', 'current'], capture_output=True, text=True)
    return r.stdout.strip()

k = get_key()

# 10个产品关键词
keywords = [
    "OBSBOT+Tail+Air", "OBSBOT+Tail+2", "OBSBOT+Meet+SE", "OBSBOT+Meet+2",
    "OBSBOT+Tiny+SE", "OBSBOT+Tiny+2", "OBSBOT+Tiny+2+Lite",
    "OBSBOT+Tiny+3", "OBSBOT+Tiny+3+Lite", "OBSBOT+Talent+2"
]

UTC_START = "YYYY-MM-DDT00:00:00Z"
UTC_END = "YYYY-MM-DDT23:59:59Z"

all_vids = {}

for kw in keywords:
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&q=" + kw + "&type=video&publishedAfter=" + UTC_START + "&publishedBefore=" + UTC_END + "&maxResults=20&key=" + k
    r = subprocess.run(['curl', '-s', '--max-time', '15', url], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        items = d.get('items', [])
        for i in items:
            vid = i['id']['videoId']
            if vid not in all_vids:
                all_vids[vid] = {
                    'channel': i['snippet']['channelTitle'],
                    'title': i['snippet']['title'],
                    'published': i['snippet']['publishedAt']
                }
    except:
        pass

# 获取视频详情并过滤
for vid in all_vids:
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=" + vid + "&key=" + k
    r = subprocess.run(['curl', '-s', '--max-time', '12', url], capture_output=True, text=True)
    # ... 过滤逻辑
```

然后执行：`python3 /tmp/obsbot_search.py`

## 腾讯文档智能表格创建流程（已废弃）

**⚠️ 用户明确要求不要用智能表格，用 Word 文档。此流程保留供参考。**

<details>
<summary>点击展开旧流程</summary>

```
1. manage.create_file → 创建 smartsheet（先用英文标题）
2. smartsheet.list_tables → 获取 sheet_id
3. smartsheet.list_fields → 获取默认字段
4. smartsheet.delete_fields → 逐个删除默认字段（至少保留1个）
5. smartsheet.add_fields → 添加 7 个自定义字段（每个必须含 property_text: {}）
6. smartsheet.list_records → 获取默认空行
7. smartsheet.delete_records → 删除默认空行
8. smartsheet.add_records → 添加数据（每批 ≤10 条，用 JSON 文件传递）
9. manage.rename_file_title → 改为中文标题
10. manage.move_file → 移动到每日监测文件夹
```

**已知问题**：
- `smartsheet.rename_table` 工具不存在
- 删除默认字段时，至少保留1个字段
- 批量数据用 `write_file` 写入 JSON 文件，再用 `$(cat file.json)` 传递给 mcporter

</details>

## 并行搜索策略

使用 `delegate_task` 3 路并行：

| 路线 | 任务 | 工具 |
|:-----|:-----|:-----|
| 路线1 | YouTube API 搜索 10 个关键词 | terminal (curl) |
| 路线2 | Instagram/TikTok/X web_search + NoxInfluencer | web + terminal |
| 路线3 | 腾讯文档文件夹定位 | terminal (mcporter) |

总耗时约 5-8 分钟。

## 输出汇报格式（参照2026-06-12模板）

### Word文档结构（必须生成Word文档！不要用markdown或智能表格）

```
OBSBOT 上线资源报告
日期：YYYY年M月D日（周X）
搜索范围：M月D日（周X）~ M月D日（周X）

一、全平台搜索结果

YouTube（N条）
1. 视频标题
博主：KOL ID
链接：URL
产品：产品名
类型：Dedicated Video / Integration（特殊主题如"榜单""对比"）
发布时间：YYYY-MM-DD
简介：简短描述

TikTok（N条，已验证日期）
1. 视频标题
博主：@KOL ID
链接：URL
产品：产品名
发布时间：YYYY-MM-DD
简介：简短描述

Instagram（N条）
1. 视频标题
博主：@KOL ID（官方/KOC自发）
链接：URL
产品：产品名
发布时间：YYYY-MM-DD
简介：简短描述

X/Twitter（0条）
今日无新帖。

二、符合 SOP 要求的视频（含质检）

YouTube
1. 视频标题
博主：KOL ID
链接：URL
产品：产品名
类型：Dedicated Video / Integration（特殊主题）
视频内容质检：
☑️ 常规产品测评/开箱/展示
☑️ 原画直出：有
☑️ 特殊主题：无/对比/榜单/教程/多机搭建/特殊场景等
描述区质检：
☒/☑️ 官网链接：有/无
☒/☑️ 亚马逊链接：有（联盟链接）/无
☒/☑️ 折扣信息：有/无
☒/☑️ 标签：有/无/未确认

TikTok
（同上格式，如无第三方产品测评则写"今日无第三方产品测评类内容。"）

Instagram
今日无第三方产品测评类内容。

X/Twitter
今日无新帖。

三、统计汇总
| 平台 | 数量 |
|------|------|
| YouTube | N |
| TikTok | N |
| Instagram | N |
| X/Twitter | N |
| 合计 | N |

四、产品覆盖情况
| 产品 | 状态 |
|------|------|
| OBSBOT Tail Air | ✅有新视频（N条）/无新视频 |
| OBSBOT Tail 2 | ... |
| ... | ... |

五、过滤说明
| 过滤项 | 原因 |
|--------|------|
| xxx | xxx |
```

### 关键规则
- **分两部分**：第一部分是"全平台搜索结果"（列出所有找到的视频），第二部分是"符合SOP要求的视频（含质检）"（筛选+质检）
- **质检内容**：视频内容质检（☑️/☒）+ 描述区质检（☑️/☒）
- **类型标注**：Dedicated Video / Integration Video（特殊主题用括号标注，如"榜单""对比"）
- **文件格式**：Word文档（.docx）
- **文件命名**：`YYYY-MM-DD-视频上线监测`
- **⚠️ 不要添加@KOL负责人员**：我的任务是找到视频，@KOL负责人员由用户自行填写

## 腾讯文档上传工作流（更新 2026-06-29）

doc.insert_markdown 在 mcporter 0.10.1 中存在参数问题（idx参数不被识别）。**统一改用 COS import 方式**：

```bash
# Step 1: 上传到 COS
cd ~/.hermes/skills/tencent-docs
bash import_file.sh "/path/to/文档.docx"
# 输出：IMPORT_READY, FILE_KEY, FILE_NAME, FILE_MD5, TASK_ID, FILE_SIZE

# Step 2: 触发异步导入
mcporter call "tencent-docs" "manage.async_import" --args '{"task_id": "<TASK_ID>", "file_size": "<FILE_SIZE>", "file_key": "<FILE_KEY>", "file_name": "<FILE_NAME>", "file_md5": "<FILE_MD5>"}'

# Step 3: 等待导入完成（15秒）
sleep 15

# Step 4: 搜索找到 file_id
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key": "文件名关键词"}'

# Step 5: 移动到每日监测文件夹 (DumZsGZJrwsf)
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id": "<file_id>", "target_folder_id": "DumZsGZJrwsf"}'
```

⚠️ 所有临时文件保存到 `~/Downloads/`，不要放 `/tmp/`（macOS 定期清理）。

## Word文档生成脚本（python-docx）

使用系统 Python 生成 Word 文档：
```python
from docx import Document
doc = Document()
doc.save('/Users/zhoulong/Downloads/YYYY-MM-DD-视频上线监测.docx')
```

## 常见陷阱

### ⚠️ YouTube API Key 问题（2026-06-26 验证）
`youtube_api_pool.py` 返回的 key 被系统 redact 后变成无效 key（返回 "API key not valid"）。**直接使用已知可用 key**：
```
API_KEY="YOUR_YOUTUBE_API_KEY"
```
不要依赖 `python3 ~/.hermes/scripts/youtube_api_pool.py current`。

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
