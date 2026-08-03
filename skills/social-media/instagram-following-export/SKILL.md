---
name: instagram-following-export
description: 通过 Instagram 网页版 DevTools 导出关注列表为 CSV。适用场景：发现竞品KOL、分析目标账号的关注网络、批量获取同类博主。需用户手动操作浏览器。
---

# Instagram 关注列表导出

通过 Instagram 网页版 DevTools 注入 JS，解析关注弹窗中的 DOM 元素，提取用户名 + 个人主页 URL 并下载为 CSV。

## 适用场景

- 发现竞品 KOL 的关注网络
- 分析目标账号的同类博主
- 批量获取细分领域创作者清单
- 竞争情报中的社交关系挖掘

## 操作步骤

### 前提
- 在浏览器（Chrome/Edge）中登录 Instagram 网页版
- 已打开目标博主的个人主页

### 第一步：打开关注列表

1. 进入目标博主的 Instagram 主页
2. 点击「Following」（关注中）按钮，打开关注列表弹窗

### 第二步：加载更多账号

在弹窗中手动向下滚动（scroll），每滚一段会加载新一批关注账号。**滚得越多，导出的数据越全。** 建议滚到底部加载完所有账号。

> ⚠️ 如果账号关注数很大（500+），建议只滚动一部分，先测试脚本是否能正常工作。确认能抓到后再重新加载全部。

### 第三步：打开 DevTools

按住 `Ctrl+Shift+J`（Mac 是 `Cmd+Option+J`）打开 DevTools Console 面板。

### 第四步：允许粘贴

在 Console 中输入以下命令并回车（绕过浏览器的粘贴安全限制）：

```
allow paste
```

### 第五步：运行脚本

将以下代码粘贴到 Console 并回车：

```javascript
(() => {
    function downloadCSV(data, filename = 'ig_following_clickable.csv') {
        const csvContent = 'username,profile_url\n' + 
            data.map(d => `${d.username},${d.url}`).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    }

    function getFollowingAccounts() {
        const dialog = document.querySelector('div[role="dialog"]');
        if (!dialog) return [];
        const links = dialog.querySelectorAll('a[href*="/"]');
        const data = [];
        links.forEach(link => {
            let url = link.href;
            if (!url.startsWith('http')) {
                url = 'https://www.instagram.com' + link.getAttribute('href');
            }
            // 从 URL 提取 username
            const username = url.replace('https://www.instagram.com/', '').replace('/', '').trim();
            if (username && url) data.push({ username, url });
        });
        // 去重
        return Array.from(new Map(data.map(item => [item.url, item])).values());
    }

    const accounts = getFollowingAccounts();
    if (accounts.length === 0) {
        alert('未抓取到账号，请先滚动弹窗加载更多！');
    } else {
        downloadCSV(accounts);
        alert(`抓取完成，共 ${accounts.length} 个账号！`);
    }
})();
```

### 第六步：获取结果

脚本会自动下载一个 `ig_following_clickable.csv` 文件，包含两列：
- `username` — Instagram 用户名
- `profile_url` — 个人主页 URL（可直接点击跳转）

## 输出示例

```csv
username,profile_url
elonmusk,https://www.instagram.com/elonmusk/
nasa,https://www.instagram.com/nasa/
...
```

## 注意

- 脚本只抓取当前弹窗中**已加载**的账号，未滚动加载的部分不会被捕获。需要的数据量越大，滚动越充分。
- 如果抓取结果为 0，检查是否已打开关注弹窗（`div[role="dialog"]` 是否存在于 DOM 中）
- CSV 已做 URL 去重，不会重复抓取
- 此方法适用于关注列表（Following），同理也可用于粉丝列表（Followers）——将弹窗切换到 Followers tab 后运行同一脚本
- 文件名可通过修改 `downloadCSV` 调用的 `filename` 参数自定义

## 自动化替代方案（推荐）

可用 Hermes 浏览器工具（browser_navigate + browser_console）自动化导出，无需手动操作：
1. `browser_navigate` 打开 Instagram，用 cookie 注入登录态（platform_cookies.json 中的 instagram 字段）
2. 点击关注数链接打开弹窗（snapshot 里 `X关注` 的 link）
3. 用 `browser_console` 执行 JS 循环滚动弹窗加载全部账号（div[role="dialog"] 的 overflowY:scroll 容器）
4. 运行上述提取脚本下载 CSV

## 数据筛选与入库流程（2026-07-30 实战验证）

### 端到端 SOP（关注列表 → 有效 KOL 数据库）

```
1. 导出关注列表 CSV（浏览器自动化或手动 JS）
2. 抓粉丝数 → 筛选 followers > 50K
3. 抓 views → 双重筛选（followers≥50K 且 avg_video_views≥5K）
4. OBSBOT 类目分类
5. 过滤明星/品牌号
6. 腾讯文档智能表格入库（查重）
7. 生成最终 CSV 交付
```

### 1. 批量获取粉丝数（匿名，无需登录）
**关键经验：`https://www.instagram.com/api/v1/users/web_profile_info/?username=X` API 匿名可调，返回 followers + 最近 12 条帖子的 video_view_count（视频播放量）。**

- **必须用 curl 调用**，不能用 urllib（TLS 指纹不同会被 429 限流）
- **User-Agent 不能用 `Chrome/150.0.0.0`**（不存在的版本号会导致 Instagram 返回不含 og:description 的缩短版页面）。用短 UA：`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36`
- 需带 `X-IG-App-ID: 936619743392459` 头
- **不要带 Cookie**（带登录 cookie 时 API 不返回 media edges，即拿不到 views）
- 1s 间隔可避免限流，~5 分钟可跑完 200+ 账号
- 备用方案：抓 profile HTML 的 og:description（`<meta property="og:description" content="X Followers, Y Following, Z Posts">`），无 views 但无限流风险低。注意 parse K/M/B 后缀
- **限流应对**：批量请求 ~20 个后 IP 可能被限（"Please wait a few minutes before you try again"）。对策：
  1. 通过系统代理换出口 IP：`curl --proxy http://127.0.0.1:1082`（Shadowrocket 端口 1082；macOS `scutil --proxy` 可查）
  2. 慢速重试版脚本 `~/.hermes/workspace/fetch_ig_views_slow.py`：直连+代理双通道、3-5s 随机间隔、断点续跑（自动合并已有结果）
  3. 等 30-60 分钟让 IP 冷却后恢复直连
  4. instagrapi 库（`login_by_sessionid`）可用但也会触发账号级 FeedbackRequired，且 media_info 逐条很慢——仅作兜底

### 2. 筛选标准
- followers > 50K
- avg_video_views > 5K（取最近 12 条视频的平均播放量）

### 3. OBSBOT 内容分类体系
一级类目（渠道占比最多内容）→ 二级类目：
- **Tech**: Hometech(智能家居/美容光疗/睡眠科技) / Gadget Review / VR / 3C(消费电子) / Drone / PC Build
- **Livestream**: Tips / Device / Tutorial / Scene（直播设备如 Yolobox/Atem mini）
- **Camera**: Photography / Videography / Filmmaker / Camera Settings
- **Gamer**: Game Streamer / Game Gear / Game Recording(FPS) / Game Recording / Gaming PC / Game Only
- **Content Creator**: Productive Tools / Earning / Draw / Art / Music / Dance / Instrument / DIY / Home Mom / Study Vlog / Online Education / Animal / Fashion / Beauty / Lifestyle / Family / Travel
- **Setup**: Desk Setup / Game Setup
- **Apple**: Accessories / News
- **Live Production** (Solution): Church / Wedding / DJ / Music / Interview / Podcast / Healthcare / Concert / Education / Cooking / Sports / Equestrian / Construction
- **Entertainment**: Reaction / Comedy / Spoof / ASMR / Cosplay / Magic / Anime / Commentary
- **Sports**: 球类 + Fitness / Yoga / Darts / Golf 等
- **Social Profession**: Teacher / Player / Coach / Worker / Groups / Club / Organization / Community / Esports Team

**⚠️ 纯手机/电脑/键盘/鼠标测评不计入有效类型**（品牌官方号做纯产品测评的排除）

### 4. 明星/品牌号过滤规则
分类依据含以下关键词 → 过滤（非可合作 KOL）：
`品牌号 | 官方号 | 官方赛事号 | 频道 | 负责人 | 歌手 | 演员 | 名人 | 公众人物 | 选美`
（如 Taylor Swift/Sephora/NYX/迪士尼/F1/Logitech 等）

### 5. 腾讯文档智能表格入库
- 创建 smartsheet：`manage.create_file` (file_type=smartsheet)，中文标题可能报错用英文创建再改名
- 字段：ID (用户名)/主页链接(url)/粉丝数量(number)/Views(number)/帖子数(number)/账号类别(singleSelect)/二级类目(text)/来源博主(text)/添加日期(dateTime)
- **records 格式**：`{"field_values": [{"field": "字段标题", "text_value": {"items": [{"text": "值", "type": "text"}]}}, ...]}`（按字段**标题**，不是 field_id）
- url 字段：`{"field": "主页链接", "url_value": {"items": [{"text": "链接", "type": "url", "link": "链接"}]}}`
- singleSelect：`{"option_value": {"items": [{"text": "选项"}]}}`
- dateTime：`{"string_value": "毫秒时间戳"}`
- **mcporter 调用坑**：subprocess 用参数列表（list）不要用 shell=True + `$(cat file)`（会失败）；每批 ≤5 条防输出截断；失败批次带重试（网络波动常见，重试 3-5 次间隔递增）
- 查重：list_records 拉取现有 username 与待写入比对，用 `field_titles` 参数减少输出量（limit=10 分页避免输出截断）

### 6. 脚本位置
- `~/.hermes/workspace/fetch_ig_simple.py` — 抓 followers（HTML og:description 解析，备用）
- `~/.hermes/workspace/fetch_ig_views.py` — 抓 followers+views（web_profile_info API，主力）
- `~/.hermes/workspace/classify_obsbot.py` — OBSBOT 类目分类 + 生成分类 CSV
- `~/.hermes/workspace/filter_kols.py` — 过滤明星/品牌号
- `~/.hermes/workspace/prepare_records.py` — 生成腾讯文档 records
- `~/.hermes/workspace/upload_records.py` / `retry_records.py` — 批量上传（带重试）
- `~/.hermes/workspace/update_categories.py` — 更新类目字段
- `~/.hermes/workspace/delete_filtered.py` — 删除被过滤记录
