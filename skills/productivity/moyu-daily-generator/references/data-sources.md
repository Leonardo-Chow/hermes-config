# 摸鱼日报数据源参考

## 指标行情

### A股指数
```bash
curl -s 'https://qt.gtimg.cn/q=sh000001,sh000688,sz399001,sz399006,sz399005'
# GBK解码: iconv -f GBK -t UTF-8 或 python3处理
```
**⚠️ 采集时机注意：** 早盘开盘前（09:15-09:25集合竞价）或刚开盘时，涨跌幅字段显示 0.00%。如果摸鱼日报在 09:30 前生成，A股数据可能是开盘价而非实时涨跌。建议在 09:30 后采集或标注"早盘数据"。

### 板块涨幅排行
东方财富 push2.eastmoney.com API（需从 delegate_task 获取或直接用python抓取）
```bash
curl -s 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=8&po=1&np=1&fields=f2,f3,f4,f12,f14&fs=m:90+t:3' -H 'User-Agent: Mozilla/5.0'
```
**⚠️ 可能返回空结果（2026-05-29验证）：** 该API偶发返回空内容(0字节)，原因为服务器端限流或连接reset。无报错信息，需检查返回内容长度。失败时不阻塞日报生成，直接从A股指数数据推断市场方向，或用 `web_search(query="A股 板块涨幅")` 从财经新闻网站获取当日热门板块信息作为替代。

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

### TechCrunch AI 专栏 ✅ 可靠
```bash
curl -sL "https://api.rss2json.com/v1/api.json?rss_url=https://techcrunch.com/category/artificial-intelligence/feed/"
```
适合 AI 板块独立采集，内容与主 RSS 有重叠但 AI 专题更集中。

### Hacker News ✅ 可靠（需VPN或RSS降级）

**方案A：Firebase API**（需VPN，中国大陆被墙）
```bash
curl -s --proxy http://127.0.0.1:1082 "https://hacker-news.firebaseio.com/v0/topstories.json"
```

**方案B：HN RSS via rss2json**（✅ 2026-06-08验证可用，无需VPN）
```bash
curl -sL --max-time 20 'https://api.rss2json.com/v1/api.json?rss_url=https://hnrss.org/frontpage'
```
返回10条首页文章，包含标题和链接，质量与Firebase API相当。`hnrss.org` 是 HN 官方认可的第三方 RSS 服务。

**⚠️ 批量获取Firebase详情容易超时：** 逐条获取HN故事详情（`/v0/item/{id}.json`）在批量调用时容易超时。建议用RSS方案一次性获取，或只取前5条。

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

### CNN World ⚠️ RSS返回过时内容（2026-05-29验证）
`http://rss.cnn.com/rss/edition_world.rss` 通过 rss2json 转换后，返回的文章可能是 2022-2023 年的旧内容，而非当天新闻。CNN 的 RSS feed 可能已停止更新或被重定向到存档。
**替代方案：** 用 `web_search(query="CNN world news today")` 获取当天 CNN 新闻，或使用 NPR/BBC/Al Jazeera 的 RSS 代替。

### France 24 ✅ 可靠（2026-06-08验证）
```bash
curl -sL --max-time 20 'https://api.rss2json.com/v1/api.json?rss_url=https://www.france24.com/en/rss'
```
返回10条当天新闻，质量稳定，适合作为国际新闻第4-5来源。

### Reuters ⚠️ 经常超时/返回空（2026-06-09验证：rss2json返回空items）
无稳定可用RSS端点，不要依赖此源

### NYT World ⚠️ 经常返回空（2026-06-09验证：rss2json返回空items）
`https://rss.nytimes.com/services/xml/rss/nyt/World.xml` → rss2json 后 items 为空

### TMZ ⚠️ 返回空（2026-06-09验证）
`https://www.tmz.com/rss.xml` → rss2json 后 items 为空

### EW (Entertainment Weekly) ⚠️ 返回空（2026-06-09验证）
`https://ew.com/feed/` → rss2json 后 items 为空

### AP News ⚠️ 经常超时
`https://apnews.com/rss/world` → 经常 timeout

### ✅ 验证可靠的RSS源清单（2026-06-09实测）
按类别排列，优先使用这些源：
- **科技：** TechCrunch · Ars Technica · The Verge · Wired
- **国际：** BBC · NPR · Al Jazeera · France 24
- **娱乐：** Variety · Hollywood Reporter
- **AI：** TechCrunch AI 专栏
- **综合：** HN RSS (hnrss.org)

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

---

## 加密货币

### CoinGecko API ⚠️ 中国大陆经常超时（2026-06-11验证）
```bash
curl -s 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true'
```
该API在中国大陆GFW环境下经常超时（15秒timeout内无响应）。CoinGecko服务器可能对大陆IP限流。
**降级方案**：在日报中标注"加密货币数据因API超时暂缺"，或从百度/微博热搜中提取财经相关条目补充。不要反复重试浪费时间。
