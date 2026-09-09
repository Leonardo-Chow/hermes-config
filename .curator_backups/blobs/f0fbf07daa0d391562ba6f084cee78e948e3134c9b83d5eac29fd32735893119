# YouTube 浏览器搜索技巧

## 搜索 URL 参数

```
https://www.youtube.com/results?search_query=QUERY&sp=EgIIAw%3D%3D
```

- `sp=EgIIAw%3D%3D` = 按上传日期排序（最近上传优先）
- 不加 sp 参数 = 按相关性排序（会返回很多旧视频）

## 从搜索结果提取视频数据

```javascript
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
```

## 从视频页面提取详情

```javascript
const title = document.querySelector('h1.ytd-watch-metadata yt-formatted-string')?.textContent?.trim();
const channel = document.querySelector('#channel-name a')?.textContent?.trim();
const views = document.querySelector('#info-container span:first-child')?.textContent?.trim();
const likes = document.querySelector('#top-level-buttons-computed button:first-child')?.textContent?.trim();
```

## 提取评论

```javascript
const comments = [];
document.querySelectorAll('ytd-comment-thread-renderer').forEach((el, i) => {
    if (i < 20) {
        const author = el.querySelector('#author-text')?.textContent?.trim() || '';
        const text = el.querySelector('#content-text')?.textContent?.trim() || '';
        if (text) comments.push({ author, text });
    }
});
JSON.stringify(comments, null, 2);
```

## 日期解析规则

| 搜索结果文本 | 含义 |
|-------------|------|
| X小时前 | 今天 |
| 1天前 | 昨天 |
| X天前 | 需要计算 |
| X周前 | 需要计算 |
| X个月前 | 超出范围 |
| X年前 | 超出范围 |

## 注意事项

- YouTube 可能显示中文或英文界面，取决于浏览器语言
- `次观看` = views, `前` = ago
- 某些视频可能没有显示观看次数（如直播、新发布）

## 已知问题（2026-06-05 发现）

### URL 编码双重转义
`browser_navigate` 会对 URL 进行编码，导致 `sp=EgIIAw%3D%3D` 被双重编码为 `sp=EgIIAw%253D%253D`。
这可能导致排序过滤不生效，返回按相关性排序的结果。

**解决方案**：
- 直接使用 `sp=EgIIAw`（不带编码后的 `==`），或
- 使用 YouTube 界面手动点击"最近上传"标签（ref 找 `tab "最近上传"`）
- 或改用 yt-dlp 搜索 + upload_date 后过滤

### 浏览器搜索结果不加载
有时 YouTube 搜索页面加载但 `ytd-video-renderer` 元素为空（0 个结果）。
原因可能是 bot 检测（stealth_warning: Running WITHOUT residential proxies）。

**解决方案**：
- 刷新页面或重新导航
- 换用 yt-dlp 搜索
- 检查 VPN 代理是否正常
