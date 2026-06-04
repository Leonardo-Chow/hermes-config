---
name: obsbot-competitor-monitor
description: |
  OBSBOT竞品YouTube上线监测。搜索18款核心竞品在YouTube的上线视频，抓取数据，分析评论区，生成Excel报告上传腾讯文档。
  定时任务：周一/三/五自动执行。
user-invocable: true
---

# OBSBOT 竞品上线监测

## ⚠️ 关键执行原则

1. **第一步必须检测日期** — 用 `date` 命令获取今天的实际日期和星期几，不要假设
2. **连续执行，不要停顿** — 搜索→统计→过滤→生成→上传，全程自动，不要中途汇报等确认
3. **日期必须准确** — 根据今天实际日期计算搜索范围，不要假设
4. **API key 不要写在脚本里** — 会被系统截断，用浏览器搜索或直接 curl
5. **时区说明** — YouTube API 返回的是 **UTC 时间**，用户在东八区（UTC+8）。搜索和筛选时以 UTC 时间为准，不需要转换时区。

## 日期计算规则（严格执行）

| 执行日 | 搜索范围 | 说明 |
|--------|---------|------|
| 周一 | 上周六 ~ 本周一 | 3天 |
| 周三 | 周二 ~ 周三 | 2天 |
| 周五 | 周四 ~ 周五 | 2天 |
| 周四（手动触发） | 周三 ~ 周四 | 2天 |
| 其他日期（手动触发） | 前一天 ~ 当天 | 2天 |

**⚠️ 时区处理**：
- YouTube API 返回的 `publishedAt` 是 UTC 时间（如 `2026-06-03T15:00:00Z`）
- 用户在 UTC+8（北京时间），但搜索筛选时以 UTC 日期为准
- 浏览器显示的 "X小时前"、"1天前" 是基于用户本地时区（UTC+8）的相对时间
- **不需要手动转换时区**，直接用 UTC 日期即可

**计算方法**：
```bash
# 获取今天日期和星期几（本地时间）
TODAY=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%u)  # 1=周一, 2=周二, ..., 7=周日
DAY_NAME=$(date +%A)

echo "今天是: $TODAY ($DAY_NAME, 星期$DAY_OF_WEEK)"

# 根据星期几计算搜索范围（UTC 日期）
case $DAY_OF_WEEK in
    1)  # 周一
        START_DATE=$(date -v-2d -u +%Y-%m-%d)  # 周六 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        ;;
    3)  # 周三
        START_DATE=$(date -v-1d -u +%Y-%m-%d)  # 周二 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        ;;
    5)  # 周五
        START_DATE=$(date -v-1d -u +%Y-%m-%d)  # 周四 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        ;;
    4)  # 周四（手动触发）
        START_DATE=$(date -v-1d -u +%Y-%m-%d)  # 周三 UTC
        END_DATE=$(date -u +%Y-%m-%d)  # 今天 UTC
        ;;
    *)  # 其他日期
        START_DATE=$(date -v-1d -u +%Y-%m-%d)
        END_DATE=$(date -u +%Y-%m-%d)
        ;;
esac

echo "搜索范围: $START_DATE ~ $END_DATE (UTC)"
```

## 核心竞品清单（18款）

| 品牌 | 搜索关键词 |
|------|-----------|
| Logitech Series | Logitech Brio webcam, Logitech C920, Logitech MX Brio, Logitech C922 |
| Insta360 Link 2 | Insta360 Link 2 webcam |
| Insta360 Link 2c | Insta360 Link 2c |
| Insta360 Wave | Insta360 Wave webcam |
| Insta360 Link 2 Pro | Insta360 Link 2 Pro |
| Elgato Facecam 4K | Elgato Facecam 4K |
| Elgato Facecam mk2 | Elgato Facecam mk2 |
| Emeet Pixy | Emeet Pixy webcam, EMEET Pixy |
| EMEET SmartCam S600 | EMEET S600 webcam |
| EMEET SmartCam S800 | EMEET S800 webcam |
| EMEET PIXY Wireless | EMEET PIXY Wireless |
| EMEET S600L | EMEET S600L webcam |
| Yolocam S3 | Yolocam S3 webcam, YoloLiv YoloCam S3 |
| Yolocam S7 | Yolocam S7 webcam, YoloLiv YoloCam S7 |
| Hollyland VenusLiv Air | Hollyland VenusLiv Air |
| Hollyland Lyra 4K | Hollyland Lyra 4K webcam |
| Razer Kiyo | Razer Kiyo webcam, Razer Kiyo V2 |
| UGREEN 4K Webcam | UGREEN 4K webcam |

## 过滤规则（必须严格执行）

### 过滤1：官方账号排除
- ❌ 排除竞品官方频道发布的视频（如 `Hollyland FAQ`、`Insta360`、`YoloLiv Tech` 等官号）
- 判断方法：频道名包含品牌名 + "FAQ"/"Official"/"Tech"/"Tutorials" 等后缀

### 过滤2：非 webcam 内容排除
- 标题必须与 webcam 直接相关，排除以下：
  - ❌ 运动相机、全景相机、无人机（如 Insta360 X5、Insta360 Luna、Insta360 Ace Pro）
  - ❌ 麦克风、采集卡、NAS、Hub 等非摄像头产品
  - ❌ 纯品牌选购指南（如「Insta360 全系列選購指南」）
  - ❌ 游戏直播内容（如 FORZA HORIZON 6 + webcam 组合，但无产品测评）
- ✅ 保留：标题包含 webcam/facecam/camera + streaming/review/unboxing/comparison 等关键词

### 过滤3：游戏直播排除
- ❌ 排除纯游戏直播内容，没有讲解 webcam 产品
- 判断：标题含游戏名（FORZA、VALORANT、COD 等）且无 webcam 测评内容

### 过滤4：低质量视频排除
- 播放量 < 50 **且** 时长 < 1分钟 → 直接过滤

### 过滤5：是否上评判断
- 仅在以下情况标记"是"：
  - 评论区明确提到 obsbot/meet/tiny/tail 等关键词
  - 视频 hashtags 包含 obsbot 相关标签（如 `#streamwithobsbot`）
  - 整体舆论明显负面（差评集中）
- ⚠️ 注意：用户取消 OBSBOT 订单转选竞品 = 负面信号，需标记上评

### 用户纠正案例（2026-06-03）
- 「裝備魔 JBTVHK」的「Insta360 全系列選購指南」→ ❌ 排除（不是专门讲 webcam）
- 「FORZA HORIZON 6 E WEBCAM EMEET PIXY 4K」→ ❌ 排除（纯游戏内容）
- 「Hollyland FAQ」频道的所有视频 → ❌ 排除（官方账号）

## 数据字段

| 字段 | 说明 |
|------|------|
| Date | 发布日期（YYYY-MM-DD） |
| 竞品 | 品牌名 |
| 网红ID | 频道名 |
| 视频链接 | YouTube URL |
| 量级 | KOL/KOC/素人（按播放量：≥10k=KOL，≥1k=KOL，≥100=KOC，<100=素人） |
| Content Type | Review/VS/Shorts/Tutorials/Unboxing/Roundup/Livestream |
| 是否上评 | 是/空（仅评论提到obsbot或舆论差时=是） |
| 曝光量 | 播放量 |
| 点赞量 | 点赞数 |
| 点赞率 | 点赞/播放 % |
| 评论数 | 评论数 |
| 评论率 | 评论/播放 % |
| 互动率 | (点赞+评论)/播放 % |
| Title | 视频标题 |
| Comment | 评论区分析（OBSBOT提及、舆论导向） |

## 执行流程

### Step 0: 确定日期范围（第一步必须执行）
```bash
# 获取今天是周几
DAY_OF_WEEK=$(date +%u)  # 1=Mon, 7=Sun
TODAY=$(date +%Y-%m-%d)
DAY_NAME=$(date +%A)

echo "今天是: $TODAY ($DAY_NAME)"

# 计算搜索范围
case $DAY_OF_WEEK in
    1)  # 周一
        START_DATE=$(date -v-2d +%Y-%m-%d)  # 周六
        END_DATE=$TODAY
        ;;
    3)  # 周三
        START_DATE=$(date -v-1d +%Y-%m-%d)  # 周二
        END_DATE=$TODAY
        ;;
    4)  # 周四（手动触发）
        START_DATE=$(date -v-1d +%Y-%m-%d)  # 周三
        END_DATE=$TODAY
        ;;
    5)  # 周五
        START_DATE=$(date -v-1d +%Y-%m-%d)  # 周四
        END_DATE=$TODAY
        ;;
    *)  # 其他日期（手动触发）
        START_DATE=$(date -v-1d +%Y-%m-%d)
        END_DATE=$TODAY
        ;;
esac

echo "搜索范围: $START_DATE ~ $END_DATE"
```

### Step 1: 搜索竞品视频（浏览器方式 - 推荐）

⚠️ **API key 在 shell 中会被截断，必须用浏览器搜索**

```
对每个品牌执行：
1. browser_navigate 到 YouTube 搜索页：
   https://www.youtube.com/results?search_query=BRAND+QUERY&sp=EgIIAw%3D%3D
   （sp=EgIIAw%3D%3D = 按上传日期排序）

2. browser_console 提取视频数据：
   const vidList = [];
   document.querySelectorAll('ytd-video-renderer').forEach((el, i) => {
       if (i < 15) {
           const titleEl = el.querySelector('#video-title');
           const channelEl = el.querySelector('#channel-name a');
           const metaSpans = el.querySelectorAll('#metadata-line span');
           let views = '', date = '';
           metaSpans.forEach(s => {
               const t = s.textContent.trim();
               if (t.includes('次观看') || t.includes('views')) views = t;
               if (t.includes('前') || t.includes('ago')) date = t;
           });
           if (titleEl) {
               vidList.push({
                   title: titleEl.textContent.trim().substring(0, 80),
                   channel: channelEl?.textContent.trim() || '',
                   views: views,
                   date: date,
                   videoId: titleEl.href?.split('v=')[1]?.split('&')[0] || ''
               });
           }
       }
   });
   JSON.stringify(vidList, null, 2);

3. 从搜索结果中筛选日期范围内的视频
   - "X小时前" = 今天
   - "1天前" = 昨天
   - "X天前" = 需要计算是否在范围内
```

### Step 2: 获取视频详情

对每个视频，用 browser_navigate 访问视频页面，browser_console 提取：
```javascript
const title = document.querySelector('h1.ytd-watch-metadata yt-formatted-string')?.textContent?.trim();
const channel = document.querySelector('#channel-name a')?.textContent?.trim();
const views = document.querySelector('#info-container span:first-child')?.textContent?.trim();
const likes = document.querySelector('#top-level-buttons-computed button:first-child')?.textContent?.trim();
```

### Step 3: 过滤
- 删除播放量<50且时长<1分钟的视频
- 解析时长：从搜索结果的 heading 文本中提取（如 "8分钟12秒钟"）

### Step 4: 评论区分析
对高互动视频（播放≥500 且 评论≥3），用浏览器提取评论：

**4a. 先检查视频 hashtags（在视频描述区）：**
```javascript
// 检查 hashtags 是否包含 obsbot 相关标签
const hashtags = [];
document.querySelectorAll('a[href*="hashtag"]').forEach(el => {
    hashtags.push(el.textContent.trim().toLowerCase());
});
const obsbotHashtags = hashtags.filter(h => h.includes('obsbot') || h.includes('meet') || h.includes('tiny'));
```

**4b. 再检查评论区：**
```javascript
const comments = [];
document.querySelectorAll('ytd-comment-thread-renderer').forEach((el, i) => {
    if (i < 30) {
        const author = el.querySelector('#author-text')?.textContent?.trim() || '';
        const text = el.querySelector('#content-text')?.textContent?.trim() || '';
        if (text) comments.push({ author, text: text.substring(0, 300) });
    }
});

// OBSBOT 关键词匹配
const obsbotKeywords = ['obsbot', 'meet 2', 'meet se', 'tiny 2', 'tiny 3', 'tail 2', 'tail air'];
const obsbotMentions = comments.filter(c => {
    const lower = c.text.toLowerCase();
    return obsbotKeywords.some(kw => lower.includes(kw));
});
```

**4c. 负面信号识别：**
- 用户说"cancelled the order"（取消订单）转选竞品 → 负面
- 用户说"returned"/"sent back"/"refund" → 负面
- 用户说"overheating"/"broke"/"defective" → 负面
- 用户说"better alternative"/"switched to" → 负面

**4d. 结果记录到 Comment 字段：**
- 有 OBSBOT 提及：记录具体评论内容 + 正面/负面判断
- 无 OBSBOT 提及：留空或写"无"

### Step 5: 生成 Excel
```python
import openpyxl
# 按日期+品牌排序
# 表头：Date, 竞品, 网红ID, 视频链接, 量级, Content Type, 是否上评, 曝光量, 点赞量, 点赞率, 评论数, 评论率, 互动率, Title, Comment
```

### Step 6: 上传腾讯文档
```bash
# 先尝试直连
cd ~/.hermes/skills/tencent-docs && bash import_file.sh /path/to/excel.xlsx

# 如果失败，加代理重试
https_proxy=http://127.0.0.1:1082 http_proxy=http://127.0.0.1:1082 \
  cd ~/.hermes/skills/tencent-docs && bash import_file.sh /path/to/excel.xlsx

# 触发导入
mcporter call "tencent-docs" "manage.async_import" --args '{...}'

# 等待 5 秒后搜索文件
mcporter call "tencent-docs" "manage.search_file" --args '{"search_key": "TITLE"}'

# 移动到目标文件夹
mcporter call "tencent-docs" "manage.move_file" --args '{"file_id": "ID", "target_folder_id": "DnNkcnCRIHGt"}'
```

## 文件命名规则

`{当天日期}——竞品检测报告——时间范围（{起始日期}-{结束日期}）`

示例：`2026-06-03——竞品检测报告——时间范围（6.2-6.3）`

## 保存位置

腾讯文档：云盘 → OBSBOT → 竞品监测
文件夹 ID：`DnNkcnCRIHGt`

## 已知陷阱

> 📖 **OBSBOT 提及模式库**：详见 `references/obsbot-mention-patterns.md`，包含 hashtags 检查方法、评论区关键词列表、负面信号识别等。

### Pitfall 1: API Key 截断
YouTube API key (`AIzaSy...aA1Q`) 在 shell heredoc/变量中会被系统截断为 `***`。
**解决方案**：用浏览器搜索方式，不要在脚本中写 API key。

### Pitfall 2: 代理不稳定
- `import_file.sh` 有时需要代理，有时不需要
- `mcporter` 调用也类似
- **策略**：先尝试直连，失败后加代理重试

### Pitfall 3: 日期判断
- 搜索结果中的 "X小时前"、"X天前" 需要根据当前时间推算
- 不要只看 "最新" 标签，要看具体时间

### Pitfall 4: 不要中途停顿（最高优先级）
用户明确要求连续执行（2026-06-03 多次强调）：
- "开始啊，不要等我的指令！！说了很多次了"
- "继续，不要停"
- "不要一步一停，自己继续执行走"

正确做法：搜索→统计→过滤→生成→上传→最终汇报，全程自动。
错误做法：每完成一步就汇报等待确认、生成中间结果后询问是否继续、做一半就停下来。

### Pitfall 6: 内容相关性判断不精确
用户纠正（2026-06-03）：仅提到品牌但与 webcam 无关的视频必须排除。
- 「Insta360 全系列選購指南」→ ❌ 排除
- 「Insta360 Mic Pro Review」→ ❌ 排除（麦克风不是 webcam）
- 「FORZA HORIZON 6 E WEBCAM EMEET PIXY 4K」→ ❌ 排除（纯游戏）
- 「Insta360 Link 2 Pro Review」→ ✅ 保留

### Pitfall 7: 评论区分析必须检查 hashtags
用户纠正（2026-06-03）：视频 hashtags 可能包含 `#streamwithobsbot` 等标签，即使评论区没有提到 OBSBOT，hashtags 中有也算提及。检查顺序：先 hashtags → 再评论区。

### Pitfall 5: mcporter 代理切换
mcporter 有时直连成功，有时需要代理。如果遇到 HTTP 405 或连接超时：
1. 先尝试不加代理
2. 失败后 `export https_proxy=http://127.0.0.1:1082` 再试
3. 两种都失败则等待几秒后重试
