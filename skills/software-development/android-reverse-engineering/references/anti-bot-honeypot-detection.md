# 反爬蜜罐检测模式（Anti-Bot Honeypot Detection）

**发现日期:** 2026-05-30
**触发场景:** 千度热播（qiandurebo.com）新版 Vue.js SPA

## 蜜罐识别特征

当爬虫/无头浏览器被网站检测到时，常见的蜜罐注入模式：

### 1. 假内容注入（Decoy Content Injection）
```html
<!-- 千度热播案例：注入「草履虫科普」内容 -->
<body style="display:none">
  <h4>在生态文明日益发展的当下，对自然的保护更是我们每个人应尽的责任和义务。</h4>
  <h2>我的身体呈圆筒形，前端较圆，中后部较宽，后端较尖。</h2>
</body>
```

**特征：**
- `<body style="display:none">` — 隐藏正文
- 内容与网站主题完全无关（直播网站显示生物学科普）
- 文本大量重复或循环出现
- 无交互元素（无按钮、无表单、无视频）

### 2. CSS 隐藏类（Hidden CSS Classes）
```css
[class*=-p1-zse-]{display:none}
[class*=-ls-ps5-]{display:none}
```
- 使用随机后缀的 CSS 类名
- 匹配特定模式的元素被隐藏

### 3. 伪装 Meta 标签（Fake Meta Tags）
```html
<meta name="AVCLRbHY-a2Ldb" content="一次草履虫短期培养实验记录">
<meta name="gs5vEKjS-CdZJe" content="草履虫是怎样感知外界刺激的？">
```
- meta name 使用随机字符串
- content 与网站业务无关

### 4. JS 挑战页（JavaScript Challenge）
```html
Loading in progress.<script>location.href="";</script>
```
- 返回 503 状态码
- Set-Cookie 设置反爬标识
- JS 重载页面（需执行 JS 才能获取真实内容）

## 检测方法

```python
# Python 检测蜜罐特征
def is_honeypot(html: str, expected_keywords: list[str]) -> bool:
    """检测页面是否为反爬蜜罐"""
    import re
    
    # 1. 检查 body 是否隐藏
    if 'style="display:none"' in html or "style='display:none'" in html:
        return True
    
    # 2. 检查是否包含预期关键词
    if not any(kw in html for kw in expected_keywords):
        return True
    
    # 3. 检查是否有视频元素
    if '<video' not in html and 'iframe' not in html and expected_keywords:
        # 对于视频网站，没有视频元素可能是蜜罐
        pass
    
    # 4. 检查蜜罐特征文本
    honeypot_patterns = [
        r'草履虫|纤毛纲|原生动物门',  # 千度热播案例
        r'Loading in progress',  # JS 挑战
        r'class\*=-[a-z]+-zse-',  # CSS 隐藏类
    ]
    for pattern in honeypot_patterns:
        if re.search(pattern, html):
            return True
    
    return False
```

## 应对策略

| 策略 | 可行性 | 说明 |
|:-----|:-------|:-----|
| Camoufox 反检测浏览器 | ⚠️ 部分有效 | 高级指纹检测仍可能失败 |
| 真实浏览器 + Cookie | ⚠️ 需手动 | 用户先在真实浏览器访问，导出 Cookie |
| API 逆向 + 加密复现 | ⚠️ 复杂 | 需逆向 JS 中的加密逻辑 |
| 放弃自动化 | ✅ 最终方案 | 有些网站的反爬太强，只能手动获取 |

## 相关案例

| 网站 | 蜜罐类型 | 应对 |
|:-----|:---------|:-----|
| qiandurebo.com | 假内容 + JS挑战 + AES加密 | 无法自动化，需手动 |
| Cloudflare 保护 | JS 挑战 + 浏览器指纹 | Camoufox 有时有效 |
| 验证码页面 | CAPTCHA | 需人工或第三方服务 |
