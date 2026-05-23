# 境外新闻源访问问题

## 经济学人 (The Economist) 访问问题

### 问题描述

在中国大陆，即使使用 VPN，经济学人网站也可能无法访问：
- SSL 握手失败（`SSL_ERROR_SYSCALL`）
- DNS 解析异常（解析到 Facebook 的 IP `31.13.68.169`）
- 连接超时

### 测试过的方案

| 方案 | 结果 |
|:-----|:-----|
| 直接访问 | ❌ 超时 |
| ClashX Pro 代理 | ❌ Connection reset |
| 0dcloud VPN | ❌ SSL 握手失败 |
| Camoufox 浏览器 | ❌ 超时 |
| Jina Reader | ❌ 无响应 |
| Google Cache | ❌ 无响应 |
| RSS Feed | ❌ 无响应 |
| **MiMo 联网搜索** | ✅ 成功 |

### 解决方案

使用 MiMo 联网搜索功能获取经济学人内容，然后生成 PDF 上传到 IMA 知识库。

## 其他被墙的新闻源

- BBC Business
- Reuters
- Financial Times
- Bloomberg
- CNBC
- Wall Street Journal

## 可访问的中文财经新闻源

| 网站 | URL | 状态 |
|:-----|:-----|:-----|
| 第一财经 | https://www.yicai.com/ | ✅ |
| 新浪财经 | https://finance.sina.com.cn/ | ✅ |
| 财联社 | https://www.cls.cn/ | ✅ |
| 界面新闻 | https://www.jiemian.com/ | ✅ |
