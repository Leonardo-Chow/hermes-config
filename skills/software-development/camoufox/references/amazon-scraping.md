# Amazon Web Scraping

## Reviews Page Access

Amazon 的评论页面 (`/product-reviews/ASIN/`) **必须登录**才能访问，未登录会 302 跳转到 `/ap/signin`。

### Cookie 登录方案

1. 用户提供 Amazon Cookie 字符串（从浏览器 DevTools → Application → Cookies 导出）
2. 在浏览器中设置 cookie：
```javascript
document.cookie = "cookie_name=value; domain=.amazon.com; path=/; secure";
```
3. 设置完后导航到评论页面即可正常访问

### 关键 Cookie 字段
- `session-id` / `session-token` — 会话认证
- `at-main` — 访问令牌
- `ubid-main` — 用户标识
- `x-main` — 主密钥
- `lc-main` — 语言设置（`en_US` 为英文界面）

### 评论提取选择器

```javascript
document.querySelectorAll('[data-hook="review"]').forEach(el => {
  const title = el.querySelector('h5')?.textContent?.trim()
    ?.replace(/^\d+\.\d+ out of \d+ stars\s*/, '');
  const author = el.querySelector('.a-profile-name')?.textContent?.trim();
  const date = el.querySelector('[data-hook="review-date"]')?.textContent?.trim();
  const rating = el.querySelector('.a-icon-alt')?.textContent?.trim();
  const body = el.querySelector('[data-hook="review-body"]')?.textContent?.trim();
  const verified = el.querySelector('[data-hook="avp-badge"]')?.textContent?.trim();
});
```

### 分页限制

- Amazon 评论分页 **通过 AJAX 不生效** — `pageNumber` 参数被忽略，所有页面返回相同评论
- 产品页面显示约 8 条美国评论 + 5 条国际评论（共 ~13 条）
- 评论页面也只显示 Top Reviews（~8 条），无分页控件
- **结论**：对于评论数不多的产品（<100 条 written reviews），能获取的评论数量有限

### 产品页面 vs 评论页面

| 页面 | 评论正文 | 国际评论 | 分页 |
|------|---------|---------|------|
| 产品页 `/dp/ASIN` | ❌ body 为空 | ✅ 有 | N/A |
| 评论页 `/product-reviews/ASIN/` | ✅ 完整正文 | ❌ 仅美国 | ❌ 无分页 |

### 反爬注意事项

- Browserbase 浏览器（无代理）可能被 Amazon 拦截，需 cookie 认证
- Camoufox **不走系统 VPN 隧道**，需要显式传 proxy 参数
- Node.js `https.get` 直接请求会被 Amazon 拦截（即使带 cookie）
- 浏览器内 `fetch()` 带 `credentials: 'include'` 可正常访问评论页面
