# Instagram Cookie 注入到 Hermes 浏览器

在 Hermes 的 `browser_navigate` 工具中使用 Instagram 登录态。

## 流程

1. 读取 `~/.hermes/cookies/platform_cookies.json` 中的 `instagram` key
2. 通过 `browser_navigate('https://www.instagram.com/')` 打开 Instagram
3. 通过 `browser_console` 注入 cookie

## Cookie 注入 JS

```javascript
const cookieStr = 'ps_n=1;datr=...;sessionid=...;csrftoken=...';
const cookies = cookieStr.split(';').map(c => c.trim());
cookies.forEach(c => {
    const eqIdx = c.indexOf('=');
    if (eqIdx > 0) {
        const name = c.substring(0, eqIdx).trim();
        const value = c.substring(eqIdx + 1).trim();
        document.cookie = name + '=' + value + ';domain=.instagram.com;path=/;';
    }
});
```

## 关键 Cookie

| Cookie | 必需 | 说明 |
|--------|------|------|
| `sessionid` | ✅ | 登录会话令牌 |
| `csrftoken` | ✅ | CSRF 保护令牌 |
| `ds_user_id` | ✅ | 用户数字 ID |
| `rur` | ✅ | 路由/请求令牌 |

## 验证

```javascript
browser_navigate('https://www.instagram.com/SOME_USER/')
// snapshot 应显示 "消息" 按钮 → 已登录
```

## ⚠️ Cookie 过期

注入后仍显示登录页 → 需用户从 Chrome 重新导出 cookie。
