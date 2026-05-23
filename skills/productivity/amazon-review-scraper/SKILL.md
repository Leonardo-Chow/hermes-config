---
name: amazon-review-scraper
description: "Amazon 评论抓取工具 — 通过 woot.com 公开 AJAX 端点抓取亚马逊商品评论，无需 API Key、无需登录、无需浏览器自动化。支持多星级×多排序组合最大化提取。"
version: v1.3
tags: [amazon, reviews, scraping, woot, ecommerce]
---

# Amazon Review Scraper

通过 `woot.com/review/Reviews/{ASIN}` 公开 AJAX 端点抓取 Amazon 商品评论。

**核心优势：无需 API Key、无需登录、无需浏览器、纯 Python 3 stdlib。**

## 安装

脚本已复制到 skill 目录下：
- `scripts/amazon_review_scraper.py` — 主抓取脚本
- `scripts/review_dedup_merge.py` — 双源去重合并脚本

## 使用方式

### 基本命令

```bash
# 最大化抓取（默认模式，推荐）
python3 ${SKILL_DIR}/scripts/amazon_review_scraper.py {ASIN} --mode max -o /tmp/{ASIN}_reviews.json

# 快速预览（最多 100 条）
python3 ${SKILL_DIR}/scripts/amazon_review_scraper.py {ASIN} --mode basic

# 仅输出摘要
python3 ${SKILL_DIR}/scripts/amazon_review_scraper.py {ASIN} --summary
```

### 抓取模式

| 模式 | 最大评论数 | 速度 | 适用场景 |
|------|-----------|------|----------|
| `basic` | 100 | 快速 | 快速预览 |
| `full` | ~500 | 中等 | 按星级分组抓取 |
| `max` | ~500-700 | 较慢 | 星级×排序组合，最大化提取（默认） |

### 工作原理

`woot.com/review/Reviews/{ASIN}` 是一个公开 AJAX 端点，返回 Amazon 评论 JSON 数据。
每个 `(filter, sort)` 组合最多返回 100 条评论。通过遍历 5 个星级 × 4 种排序并去重，最大化提取。

### 覆盖率

| 产品评论数 | 预期覆盖率 |
|-----------|-----------|
| < 100 条 | **100%** |
| 100-500 条 | **~95-100%** |
| 500-1000 条 | **~85-95%** |
| > 1000 条 | **~70-85%** |

### API 返回字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `Author` | string | 评论者名称 |
| `Title` | string | 评论标题 |
| `Text` | string | 评论全文 |
| `OverallRating` | int | 星级 (1-5) |
| `OriginDescription` | string | 评论日期和地区 |
| `IsVerifiedPurchase` | bool | 已验证购买 |
| `IsVineReview` | bool | Vine 评论 |
| `HelpfulVotes` | int | 有用票数 |
| `ImageUrls` | array | 评论图片 URL |
| `MediaUrls` | array | 评论视频 URL |

### 日期过滤（后处理）

```python
import json, re
from datetime import datetime, timedelta

with open("/tmp/{ASIN}_reviews.json") as f:
    data = json.load(f)

reviews = data["reviews"]
cutoff = datetime.now() - timedelta(days=90)  # 最近 3 个月

def parse_date(desc):
    if not desc: return None
    m = re.search(r"on (\w+ \d{1,2},?\s+\d{4})", desc)
    if m:
        date_str = re.sub(r"\s+", " ", m.group(1).replace(",", "").strip())
        try: return datetime.strptime(date_str, "%B %d %Y")
        except ValueError: pass
    return None

filtered = [r for r in reviews if (d := parse_date(r.get("OriginDescription", ""))) and d >= cutoff]
```

### 星级过滤

```python
bad_reviews = [r for r in reviews if r.get("OverallRating", 0) <= 2]
good_reviews = [r for r in reviews if r.get("OverallRating", 0) >= 4]
```

## 注意事项

- ⚠️ **Ratings ≠ Reviews**（最重要）：Amazon 显示的 "X ratings" 包含纯星级评分，**有文字的评论通常只占 10-20%**。必须向用户说明："138 ratings 中只有 29 条有文字评论"
- ⚠️ **仅支持 Amazon US**（amazon.com），其他站点用 Sorftime MCP
- ⚠️ 只抓取**有文字的评论**，不含纯星级评分
- ⚠️ 5星评论上限约 135 条/ASIN
- ⚠️ `OriginDescription` 日期格式可能多样，脚本内置多格式解析器
- ⚠️ `Title` 字段可能含 HTML 实体（`&amp;` 等），dedup 脚本已处理 `html.unescape`
- ⚠️ 少数产品 Woot 端点返回空结果（可能未收录），此时回退到浏览器方案
- ✅ Python 3.6+，无外部依赖

## 备用方案：浏览器直接提取 Amazon 评论

当 Woot 端点返回空结果时，用 browser 工具直接访问 Amazon 产品页面提取评论。

### 为什么不能用 curl
Amazon 对 curl 请求返回 CAPTCHA 验证码页面，无法获取评论内容。

### 浏览器提取流程

```bash
# 1. 导航到产品页面
browser_navigate url="https://www.amazon.com/dp/{ASIN}"

# 2. 点击 "评论" 链接滚动到评论区
browser_click ref=e15  # "Reviews" link

# 3. 滚动页面加载评论
browser_scroll direction=down

# 4. 用 JavaScript 提取评论
browser_console expression="""
const pageContent = document.body.innerText;
const reviewStart = pageContent.indexOf('来自美国的热门评论');
if (reviewStart > -1) {
    pageContent.substring(reviewStart, reviewStart + 8000);
} else {
    const custIdx = pageContent.indexOf('customer review');
    if (custIdx > -1) pageContent.substring(custIdx - 100, custIdx + 8000);
    else 'No reviews found';
}
"""
```

### JavaScript 提取评论（多种方式）

```javascript
// 方式1：获取页面文本中的评论区域
const pageContent = document.body.innerText;
const reviewStart = pageContent.indexOf('来自美国的热门评论');
pageContent.substring(reviewStart, reviewStart + 8000);

// 方式2：通过 data-hook 属性获取结构化评论
const reviews = document.querySelectorAll('[data-hook="review"]');
reviews.forEach(review => {
    const title = review.querySelector('[data-hook="review-title"]')?.textContent;
    const body = review.querySelector('[data-hook="review-body"]')?.textContent;
    const rating = review.querySelector('[data-hook="review-star-rating"]')?.textContent;
});

// 方式3：搜索关键词定位评论
const keywords = ['customer', 'review', 'star', 'rating'];
keywords.forEach(kw => {
    const idx = document.body.innerText.toLowerCase().indexOf(kw);
    // 提取上下文
});
```

### 注意事项
- Amazon 页面语言可能自动切换为中文，评论区域标识为 "来自美国的热门评论"
- 每次滚动只能加载约 8 条评论，需要多次滚动
- 页面可能有 "查看更多评论" 按钮，需要点击
- 浏览器模式下提取的评论需要手动解析格式

## 批量抓取多个产品

当需要抓取多个 ASIN 时，用 `delegate_task` 并行执行，总耗时 ≈ 单个产品：

```
delegate_task with N parallel tasks, each task:
  1. python3 scripts/amazon_review_scraper.py {ASIN} --mode max -o /tmp/{ASIN}_reviews.json
  2. Generate MDX from JSON (group by star rating, include full text)
  3. mcporter call tencent-docs create_smartcanvas_by_mdx (title ≤ 36 chars)
  4. mcporter call tencent-docs manage.move_file to target folder
```

实际测试：3 个产品并行，总耗时 ~3 分钟（含 206 条评论的产品）。

## 与腾讯文档集成（2026-05-14 验证）

抓取完成后上传到腾讯文档的完整流程：

```bash
# 1. 生成 Word 文档（python-docx）
python3 gen_amazon_doc.py  # 读取 JSON → 生成 .docx

# 2. 上传到腾讯文档
cd ~/.hermes/skills/tencent-docs
bash import_file.sh /tmp/product_reviews.docx

# 3. 触发异步导入
mcporter call tencent-docs manage.async_import task_id="drivetask_xxx" ...

# 4. 轮询进度
mcporter call tencent-docs manage.import_progress task_id="drivetask_xxx"

# 5. 移动到 Amazon 文件夹
mcporter call tencent-docs manage.move_file file_id="xxx" target_folder_id="DKQjkLCCkwLR"
```

**Amazon 文件夹 ID**: `DKQjkLCCkwLR`

**Word 文档格式**（参考已有文档）：
- 标题：产品名 - Amazon Customer Reviews
- 信息区：Product / ASIN / Rating / Total Reviews / Verified / Generated / Source
- 📊 Rating Breakdown 表格（5→1星，含数量和百分比）
- 🇺🇸 Reviews from the United States（按星级排列）
- 🌍 Reviews from Other Countries（按国家分组）
- 每条评论：星级+作者+日期+Verified Purchase标记+标题+正文+有用票数

**⚠️ Ratings ≠ Reviews**（最重要）：Amazon 显示的 "X ratings" 包含纯星级评分，**有文字的评论通常只占 10-20%**。必须向用户说明。

## 与之前方法对比

| 方式 | 评论数 | 需要登录 | 需要浏览器 |
|------|--------|----------|-----------|
| 浏览器 + Cookie | ~13 | ✅ | ✅ |
| **Woot 端点** | **~29+** | ❌ | ❌ |

## 实测数据

详见 `references/real-world-results.md`，含 4 个产品的真实抓取结果和关键发现。
