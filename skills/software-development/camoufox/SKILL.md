---
name: camoufox
description: "Camoufox — 反检测浏览器自动化工具。指纹伪装、自动化浏览、免封号抓取。可配合 bb-browser、Agent-Reach 使用，增强微信公众号全文阅读等场景。"
version: 1.0.0
author: Hermes Agent
tags: [camoufox, browser, automation, anti-detection, scraping]
---

# Camoufox Skill

[Camoufox](https://github.com/daijro/camoufox) — 反检测浏览器自动化工具。伪装浏览器指纹，绕过反爬和 WAF 检测。

## Status

- **Version:** v135.0.1-beta.24
- **CLI:** `/Users/zhoulong/.hermes/hermes-agent/venv/bin/camoufox`
- **Also installed as dependency of:** xiaohongshu-cli

## Commands

```bash
camoufox fetch          # Update binaries
camoufox version        # Current version
camoufox path           # Binary path
camoufox server         # Launch Playwright server
camoufox test           # Open Playwright inspector
camoufox remove         # Remove downloaded files
```

## Usage with Agent-Reach

Camoufox enhances 微信公众号 (WeChat) article reading via Agent-Reach:
- Provides better full-text extraction from WeChat articles
- Handles anti-bot detection on WeChat's pages

## Usage with bb-browser

Camoufox can serve as an alternative browser backend instead of Chrome:
```bash
camoufox server --port 19824
```
Then point bb-browser daemon to it.

## Python Usage

```python
from camoufox import Camoufox

async with Camoufox() as browser:
    page = await browser.new_page()
    await page.goto("https://example.com")
    # Camoufox handles fingerprinting automatically
    content = await page.content()
```

## News Article Scraping with Images

Camoufox 可用于抓取 BBC/Reuters 等新闻网站的全文和配图（需 VPN 可用）。

### BBC Business 文章抓取

```python
from camoufox.async_api import AsyncCamoufox

async def scrape_bbc_article(url):
    async with AsyncCamoufox(headless=True) as browser:
        page = await browser.new_page()
        await page.goto(url, timeout=20000)
        await page.wait_for_timeout(3000)
        
        # 提取标题
        title = await page.evaluate("""() => {
            const h1 = document.querySelector('h1');
            return h1 ? h1.innerText : '';
        }""")
        
        # 提取正文
        content = await page.evaluate("""() => {
            const paragraphs = document.querySelectorAll('article p, [data-component="text-block"] p');
            let result = [];
            paragraphs.forEach(p => {
                const text = p.innerText.trim();
                if (text && text.length > 30) result.push(text);
            });
            return result.join('\\n\\n');
        }""")
        
        # 提取配图
        images = await page.evaluate("""() => {
            const imgs = document.querySelectorAll('article img, [data-component="image-block"] img');
            let result = [];
            imgs.forEach(img => {
                const src = img.src || img.dataset.src;
                const alt = img.alt;
                if (src && !src.includes('logo') && !src.includes('icon') && !src.includes('bbcdotcom')) {
                    result.push({src: src, alt: alt});
                }
            });
            return result.slice(0, 3);
        }""")
        return title, content, images
```

### BBC Business 首页头条抓取

```python
async with AsyncCamoufox(headless=True) as browser:
    page = await browser.new_page()
    await page.goto("https://www.bbc.com/news/business", timeout=20000)
    await page.wait_for_timeout(5000)  # JS 渲染需要更长等待
    
    articles = await page.evaluate("""() => {
        const links = document.querySelectorAll('a[href*="/news/business-"]');
        let result = [], seen = new Set();
        links.forEach(el => {
            const text = el.innerText.trim();
            const href = el.href;
            if (text && text.length > 15 && !seen.has(text)) {
                seen.add(text);
                result.push({title: text, url: href});
            }
        });
        return result.slice(0, 5);
    }""")
```

### 配图下载

BBC 配图 URL 格式: `https://ichef.bbci.co.uk/news/480/cpsprodpb/.../*.jpg.webp`

```bash
# 下载 webp 格式配图
curl -sL "$IMAGE_URL" -o /tmp/image.webp
```

### PDF 生成（含嵌入配图）

```python
import base64
from playwright.sync_api import sync_playwright

# 将图片 base64 嵌入 HTML
with open('image.webp', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

html = f'<img src="data:image/webp;base64,{img_b64}">'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_content(html)
    page.pdf(path='output.pdf', format='A4')
    browser.close()
```

## Reference Files

- `references/amazon-scraping.md` — Amazon 评论抓取方案：Cookie 登录、选择器、分页限制、反爬注意事项

## Pitfalls

- **先验证代理可用再用 Camoufox** — `curl -sL --max-time 5 --proxy http://127.0.0.1:7890 "https://httpbin.org/ip"` 测试通了再跑浏览器
- Network proxy needed in China (ClashX etc.)
- For bb-browser integration, run `camoufox server` + `bb-browser daemon`
- **Camoufox 不会自动走系统 VPN 隧道** — 如果 VPN 是纯隧道模式（如 0dcloud 的 utun4），Camoufox 的 Chromium 内核可能不走该隧道。需要显式传 `proxy` 参数给 Camoufox
- **proxy 参数格式:** `AsyncCamoufox(headless=True, proxy={"server": "http://127.0.0.1:7890"})` — 但如果代理端口本身不通（节点失效），Camoufox 也会超时
- **先验证代理可用再用 Camoufox** — `curl -sL --max-time 5 --proxy http://127.0.0.1:7890 "https://httpbin.org/ip"` 测试通了再跑浏览器
- 诊断代理问题详见 `gfw-bypass` skill
