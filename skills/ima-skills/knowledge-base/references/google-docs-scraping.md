# Google Docs 爬取技术

## 问题
Google Docs 内容在 Canvas 上渲染，无法直接从 DOM 提取文本。标准导出 URL（`/export?format=txt`、`/pub`）需要 Google 登录。

## 解决方案：mobilebasic URL

**唯一可靠的公开 Google Docs 爬取方式：**

```
https://docs.google.com/document/d/{DOC_ID}/mobilebasic
```

- 适用于「知道链接的任何人都可以查看」的公开文档
- 内容以 HTML 渲染（非 Canvas），可从 DOM 提取
- 多标签页文档会在同一页面展示所有内容
- 不需要登录 Google 账号

## 提取方法

### 方法 1：Node.js HTTP 请求（推荐）

```javascript
const https = require('https');
const url = 'https://docs.google.com/document/d/{DOC_ID}/mobilebasic';

https.get(url, {headers: {'User-Agent': 'Mozilla/5.0'}}, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        const bodyMatch = data.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
        if (bodyMatch) {
            let html = bodyMatch[1];
            html = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
            html = html.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
            // 转换标签为 Markdown
            html = html.replace(/<h1[^>]*>/gi, '\n# ');
            html = html.replace(/<\/h1>/gi, '\n');
            html = html.replace(/<h2[^>]*>/gi, '\n## ');
            html = html.replace(/<\/h2>/gi, '\n');
            html = html.replace(/<br[^>]*>/gi, '\n');
            html = html.replace(/<p[^>]*>/gi, '\n');
            html = html.replace(/<\/p>/gi, '\n');
            html = html.replace(/<li[^>]*>/gi, '\n- ');
            html = html.replace(/<td[^>]*>/gi, ' | ');
            html = html.replace(/<tr[^>]*>/gi, '\n');
            html = html.replace(/<[^>]+>/g, '');
            html = html.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
            html = html.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&nbsp;/g, ' ');
            html = html.replace(/\n{3,}/g, '\n\n').trim();
            require('fs').writeFileSync('/tmp/output.txt', html);
        }
    });
});
```

### 方法 2：浏览器 Console（Headless Browser）

```javascript
// 在 mobilebasic 页面执行
document.body.innerText  // 获取全部文本
```

⚠️ 注意：`document.body.innerText` 在页面导航后会清空，需要在页面加载完成后立即提取。

## 不可用的方法

| 方法 | 状态 | 原因 |
|------|------|------|
| `/export?format=txt` | ❌ 需要登录 | 重定向到 Google 登录页 |
| `/pub` | ❌ 需要登录 | 同上 |
| `/gviz/tq?tqx=out:txt` | ❌ 404 | 仅适用于 Sheets |
| Canvas DOM 提取 | ❌ 无文本 | 内容在 Canvas 上渲染 |
| `iframe.contentDocument` | ❌ 空 | 跨域限制或内容为空 |

## 与 IMA 集成

爬取后的内容可以：
1. **创建笔记** → `import_doc` API → `add_knowledge` 添加到知识库
2. **导入 URL** → `import_urls` API（仅保存链接，不保存内容）

推荐两者都做：URL 作为来源备份，笔记作为离线可读内容。

### 大内容处理

当内容 >10KB 时，不要通过 shell 传递 JSON（会被截断）。使用 Node.js 脚本：

```javascript
const { execSync } = require('child_process');
const fs = require('fs');
const content = fs.readFileSync('/tmp/content.md', 'utf8');
const body = JSON.stringify({ content_format: 1, content });
const result = execSync(`node ima_api.cjs 'openapi/note/v1/import_doc' '${body.replace(/'/g, "'\\''")}'`, {
    encoding: 'utf8', maxBuffer: 10 * 1024 * 1024
});
```

## 已知限制

- 需要文档设置为「知道链接的任何人可查看」
- 私有文档无法使用此方法
- 图片无法通过此方式提取（只有 alt 文本）
- 表格格式需要后处理清理（`|` 分隔符）
