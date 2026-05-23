# Google Docs → 腾讯文档 完整迁移工作流

将 Google Docs 文档（含表格、图片、列表、标题）完整迁移到腾讯文档，保留原始结构。

## 核心思路

Google Docs 用 Canvas 渲染内容，无法直接提取结构化数据。但 `mobilebasic` 视图返回完整 HTML，包含表格/标题/列表/图片的 DOM 结构。

## 完整流程

### Step 1: 获取 mobilebasic HTML

```javascript
// Node.js — 获取原始 HTML（含结构）
const https = require('https');
const docId = 'GOOGLE_DOC_ID';
const url = `https://docs.google.com/document/d/${docId}/mobilebasic`;

https.get(url, {headers: {'User-Agent': 'Mozilla/5.0'}}, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        require('fs').writeFileSync('/tmp/gdoc.html', data);
        console.log('Saved: ' + data.length + ' chars');
    });
});
```

### Step 2: 解析 HTML 提取结构化元素

```python
import re, urllib.parse

with open('/tmp/gdoc.html', 'r') as f:
    html = f.read()

# 关键预处理（必须按顺序）
body_match = re.search(r'<body[^>]*>(.*)', html, re.DOTALL)
html = body_match.group(1) if body_match else html

# 1. 剥离 JS/CSS（否则混入正文）
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)

# 2. 解包 Google 重定向 URL
def unwrap_google(m):
    href = m.group(1)
    if 'google.com/url?' in href:
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        href = qs.get('q', [href])[0]
    return f'href="{href}"'
html = re.sub(r'href="([^"]*google\.com/url\?[^"]*)"', unwrap_google, html)

# 3. 提取各结构元素（按位置排序）
# 表格
table_pat = re.compile(r'<table[^>]*>(.*?)</table>', re.DOTALL|re.I)
tr_pat = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL|re.I)
td_pat = re.compile(r'<t[dh][^>]*>(.*?)</t[dh]>', re.DOTALL|re.I)

# 图片
img_pat = re.compile(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', re.I)

# 标题
heading_pat = re.compile(r'<(h[1-4])[^>]*>(.*?)</\1>', re.DOTALL|re.I)

# 列表
list_pat = re.compile(r'<(ul|ol)[^>]*>(.*?)</\1>', re.DOTALL|re.I)
li_pat = re.compile(r'<li[^>]*>(.*?)</li>', re.DOTALL|re.I)
```

### Step 3: 下载图片

```bash
# 从 HTML 中提取所有 docs-images-rt URL
# 批量下载（限制并发）
mkdir -p /tmp/gdoc_images
i=1
while IFS= read -r url; do
    curl -sL -o "/tmp/gdoc_images/img_$(printf '%03d' $i).jpg" "$url" &
    i=$((i+1))
    [ $((i % 10)) -eq 0 ] && wait
done < /tmp/img_urls.txt
wait

# 压缩到 400px 宽（否则 docx 太大，COS 上传超时）
cd /tmp/gdoc_images
for f in *.jpg; do
    sips -Z 400 "$f" --out "${f%.jpg}_400.jpg" 2>/dev/null
done
```

### Step 4: 生成 .docx

```python
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
# 按位置顺序遍历所有元素
for etype, data in sorted_elements:
    if etype == 'heading':
        doc.add_heading(data['content'], level=min(data['level'], 3))
    elif etype == 'table':
        # 创建表格，首行加粗
        table = doc.add_table(rows=len(data), cols=max_cols)
        table.style = 'Table Grid'
        for i, row in enumerate(data):
            for j, cell_text in enumerate(row):
                table.rows[i].cells[j].text = cell_text
    elif etype == 'list':
        for item in data['items']:
            doc.add_paragraph(item, style='List Bullet')
    elif etype == 'image':
        path = find_image(data['idx'])
        if path:
            doc.add_picture(path, width=Inches(5.0))
    elif etype == 'text':
        doc.add_paragraph(data)
```

### Step 5: 上传到腾讯文档

```bash
cd ~/.hermes/skills/tencent-docs
bash import_file.sh /tmp/output.docx
# → 拿到 TASK_ID
mcporter call tencent-docs manage.async_import --args '{"task_id": "...", ...}'
# → 等待导入完成
```

## ⚠️ 必须遵守的质量门禁

**上传前必须验证：**

1. **文字覆盖率** ≥ 95%：提取 docx 文字总长度 ÷ 原始 HTML 文字总长度
2. **表格数量** 匹配：docx 表格数 == HTML 中 `<table>` 数
3. **图片数量** 匹配：docx 嵌入图片数 == HTML 中内容图片数
4. **无 JS 污染**：grep 排除 `DOCS_init`、`window.navigator` 等关键词
5. **无 URL 重复**：检查不存在 `url + url` 拼接

```python
# 验证脚本
from docx import Document
doc = Document('/tmp/output.docx')
text = '\n'.join(p.text for p in doc.paragraphs)
img_count = sum(1 for r in doc.part.rels.values() if 'image' in r.reltype)

assert len(text) / raw_html_text_len > 0.95, f"覆盖率不足: {len(text)/raw_html_text_len:.1%}"
assert len(doc.tables) == expected_table_count, f"表格数不匹配"
assert img_count >= expected_image_count, f"图片数不足"
assert 'DOCS_init' not in text, "JS 污染"
```

## 已知坑

| 坑 | 表现 | 修复 |
|---|---|---|
| JS 混入正文 | 第一段是 `if ((!this['DOCS_initDocsMobileWeb'])...` | 解析前 `re.sub(r'<script>.*?</script>', ...)` |
| URL 重复 | `https://xxxhttps://xxx` | `<a>` 标签内文字跳过，只取 href |
| `\xa0` 乱码 | 文档中出现不可见字符 | `.replace('\xa0', ' ')` |
| Google 包装链接 | `google.com/url?q=实际URL` | 正则解包 |
| COS 上传超时 | 文件 > 2MB 常超时 | 图片压缩到 400px，docx 控制在 2.5MB 以内 |
| `upload_image` 不可用 | MCP 返回 RPC invalid | 服务端未注册，用 .docx 导入绕过 |
| `scrape_url` 不可用 | MCP 返回 RPC invalid | 同上，用 .docx 导入绕过 |
| `import_progress` 不可用 | HTTP 405 | 不轮询，sleep 20s 后用 `search_file` 查结果 |
