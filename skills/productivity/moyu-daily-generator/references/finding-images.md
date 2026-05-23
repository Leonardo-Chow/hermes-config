# 每日精选配图获取指南

## 原理

大多数新闻网站会在 HTML 的 `<head>` 中设置 Open Graph 标签，其中 `og:image` 包含文章的特色图片URL。通过提取这个标签，可以获得真实的高质量新闻图片。

## 已验证的可靠来源

### NPR（最可靠 ✅）
```python
import urllib.request, re
url = 'https://www.npr.org/2026/05/07/...'  # 任意NPR文章URL
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=10)
html = resp.read().decode('utf-8')
m = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', html)
image_url = m.group(1)  # → npr.brightspotcdn.com/...
# 示例输出：https://npr.brightspotcdn.com/dims3/default/strip/false/crop/5000x2813+0+420/...
```

**特点：**
- CDN域名：`npr.brightspotcdn.com`
- 图片来自 Getty Images / AP，质量高
- 支持 HTTPS，长期有效（但参数中的签名会过期——每个会话单独获取）

### BBC（有时超时 ⚠️）
同上方法，但 BBC 的服务器有时会 SSL 握手超时。

### The Guardian（有时超时 ⚠️）
同上方法，Guardian 的服务器可能超时。

## 注意事项

1. **不要用 picsum.photos 等占位图** — 用户明确要求真实配图
2. **不要用百度图片搜索结果** — 链接通常无法直链使用
3. **图片URL可能带签名参数** — 不影响嵌入使用
4. **CDN域名可能因地区访问慢** — 但图片会显示（只是加载慢）
5. **备用方案**：如果所有新闻文章都超时，可以使用 IMA 知识库中已有的封面图片作为每日精选配图
