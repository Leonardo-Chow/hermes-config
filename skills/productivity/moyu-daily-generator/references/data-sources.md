# 摸鱼日报数据源参考

## 指标行情

### A股指数
```bash
curl -s 'https://qt.gtimg.cn/q=sh000001,sh000688,sz399001,sz399006,sz399005'
# GBK解码: iconv -f GBK -t UTF-8 或 python3处理
```

### 板块涨幅排行
东方财富 push2.eastmoney.com API（需从 delegate_task 获取或直接用python抓取）

---

## 热搜榜单

### 微博热搜 ✅ 可靠
```bash
# 推荐接口（避免403）：
curl -s 'https://weibo.com/ajax/statuses/hot_band' -H 'User-Agent: Mozilla/5.0'
# 备用：/ajax/side/hotSearch 可能返回403 Forbidden
# 数据在 data[].word / realtime 字段
```

### 百度热搜 ✅ 可靠
```bash
curl -s 'https://top.baidu.com/api/board?tab=realtime' -H 'User-Agent: Mozilla/5.0'
# 返回 JSON，解析 data.running[].query + hotScore
```

### 抖音热榜 ✅ 可靠
```bash
curl -s 'https://www.douyin.com/aweme/v1/web/hot/search/list/' \
  -H 'Referer: https://www.douyin.com/' -H 'User-Agent: Mozilla/5.0'
# 数据在 word_list 字段（完整TOP50），trending_list 只有5条上升热点
```

### 知乎热榜 ⚠️ 困难
知乎有严格的反爬机制（安全验证 / 403）。以下方法可尝试：
- `curl https://www.zhihu.com/hot` → 大概率 403
- `curl https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=10` → 需要鉴权
- 浏览器方式：`browser_navigate('https://www.zhihu.com/hot')` → 可能触发安全验证
- **兜底**：如果实在拿不到，告知用户知乎热榜暂时无法获取，用百度热搜补充

---

## 科技新闻

### TechCrunch ✅ 可靠
```bash
# RSS via rss2json
curl -sL "https://api.rss2json.com/v1/api.json?rss_url=https://techcrunch.com/feed/"
```
注意日期过滤，TC的RSS会返回多天文章。

### The Verge ✅ 可靠
```bash
# Atom格式，需特殊解析
curl -sL "https://www.theverge.com/rss/index.xml" -H 'User-Agent: Mozilla/5.0'
```

### Ars Technica ✅ 可靠
```bash
curl -sL "https://feeds.arstechnica.com/arstechnica/index" -H 'User-Agent: Mozilla/5.0'
```

### Wired ✅ 可靠
```bash
curl -sL "https://www.wired.com/feed/rss" -H 'User-Agent: Mozilla/5.0'
```

### 爱范儿 ifanr ✅ 可靠（中文）
```bash
curl -sL "https://www.ifanr.com/feed" -H 'User-Agent: Mozilla/5.0'
```

### Hacker News ✅ 可靠
```bash
# Firebase API
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json"
# 或通过 news.ycombinator.com 页面抓取
```

---

## 国际新闻

### 通用策略：通过 rss2json 转换
```python
url = f"https://api.rss2json.com/v1/api.json?rss_url={rss_url}"
```
部分来源直接请求会失败，rss2json 成功率更高。

### BBC News ✅
`https://feeds.bbci.co.uk/news/rss.xml` → rss2json

### NPR ✅
`https://feeds.npr.org/1001/rss.xml` → rss2json

### Al Jazeera ✅
`https://www.aljazeera.com/xml/rss/all.xml` → 可直接curl

### CNBC ⚠️ 偶发500
`https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114`

### France 24 ✅ 之前成功
无稳定RSS，尝试直接请求首页或通过搜索获取

### Reuters ⚠️ 经常超时
无稳定可用RSS端点

### AP News ⚠️ 经常超时
`https://apnews.com/rss/world` → 经常 timeout

---

## 娱乐新闻

### Hollywood Reporter ✅
```bash
curl -sL "https://www.hollywoodreporter.com/feed/" -H 'User-Agent: Mozilla/5.0'
```

### Variety ✅
```bash
curl -sL "https://variety.com/feed/" -H 'User-Agent: Mozilla/5.0'
```

### AceShowbiz ⚠️
RSS有时404，可用THR和Variety替代
