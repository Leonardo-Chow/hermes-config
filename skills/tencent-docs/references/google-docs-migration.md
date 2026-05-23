# Google Docs → 腾讯文档迁移（含图片）

将 Google Docs 文档完整迁移到腾讯文档，保留文本内容和所有嵌入图片。

## 适用场景

- 用户提供 Google Docs 链接，要求迁移到腾讯文档
- 需要保留原始文档的图片、表格、列表等格式
- 目标是 OBSBOT 等企业的云盘空间

## 完整工作流

### Step 1: 提取文本内容

Google Docs 编辑器使用 Canvas 渲染，无法从 DOM 直接提取文本。使用 `mobilebasic` 视图：

```javascript
// browser_navigate 到 mobilebasic URL
// https://docs.google.com/document/d/<DOC_ID>/mobilebasic

// 提取全部文本（分段获取，每段 8000 字符）
const text = document.body.innerText;  // 总长度
const chunk1 = text.substring(0, 8000);
const chunk2 = text.substring(8000, 16000);
const chunk3 = text.substring(16000);
```

**注意**：`document.body.innerText` 在 mobilebasic 视图下返回干净的文本内容（含表格用 `\t` 分隔）。主编辑器视图的 innerText 为空。

### Step 2: 提取图片

```javascript
// 在 mobilebasic 页面上获取所有图片
browser_get_images()
// 返回 [{src, alt, width, height}, ...]
// src 是 docs.google.com/docs-images-rt/ 的 URL，无需登录即可访问
```

### Step 3: 下载图片

```bash
# 创建目录
mkdir -p /tmp/obsbot_images

# 批量下载（写 URL 到文件，用 xargs 并行）
# 注意：xargs 命令行长度有限制，改用 while 循环
i=1
while IFS= read -r url; do
    printf -v fname "img_%03d.png" "$i"
    curl -sL -o "$fname" "$url" &
    i=$((i+1))
    if [ $((i % 10)) -eq 0 ]; then wait; fi
done < /tmp/image_urls.txt
wait

# 压缩为 JPEG（减小文件体积）
for f in *.png; do
    sips -s format jpeg -s formatOptions 50 "$f" --out "${f%.png}.jpg"
done
```

**图片大小**：Google Docs 图片通常 800px 宽，PNG 格式每张 50-150KB。57 张约 4MB。
转 JPEG quality=50 后约 1.3MB，适合导入。

### Step 4: 生成 .docx 文件（python-docx）

由于 `upload_image` MCP 工具不可用（RPC 未注册），采用 `.docx` 导入绕过方案：

```python
from docx import Document
from docx.shared import Inches
import os

doc = Document()

# 添加文本内容（逐行解析，识别标题/列表/表格）
for line in content_lines:
    if is_heading(line):
        doc.add_heading(line, level=level)
    elif is_bullet(line):
        doc.add_paragraph(line, style='List Bullet')
    else:
        doc.add_paragraph(line)

# 添加图片
for idx in range(1, img_count + 1):
    img_path = f'/tmp/obsbot_images/img_{idx:03d}.jpg'
    if os.path.exists(img_path):
        doc.add_picture(img_path, width=Inches(5.5))

doc.save('/tmp/output.docx')
```

### Step 5: 导入到腾讯文档

```bash
cd ~/.hermes/skills/tencent-docs

# 上传到 COS + 获取 task_id
bash import_file.sh /tmp/output.docx
# 输出: FILE_KEY, FILE_NAME, FILE_MD5, FILE_SIZE, TASK_ID

# 触发异步导入
mcporter call tencent-docs manage.async_import --args '{
  "task_id": "TASK_ID",
  "file_size": "FILE_SIZE",
  "file_key": "FILE_KEY",
  "file_name": "FILE_NAME",
  "file_md5": "FILE_MD5"
}'

# 验证导入成功（不要用 manage.import_progress，返回 405）
sleep 15
mcporter call tencent-docs manage.search_file --args '{"search_key": "文档标题"}'
```

### Step 6: 移动到目标文件夹

```bash
# manage.move_file 使用 target_folder_id（不是 folder_id）
mcporter call tencent-docs manage.move_file --args '{
  "file_id": "新文档ID",
  "target_folder_id": "目标文件夹ID"
}'
```

## ⚠️ 关键陷阱

### 1. 内容完整性验证（必须执行）

**用户明确要求**：上传前必须自检内容完整性，不合格不能上传。

验证方法：
```python
from docx import Document
doc = Document('/tmp/output.docx')
docx_text = '\n'.join([p.text for p in doc.paragraphs])

with open('/tmp/raw_text.txt') as f:
    raw_text = f.read()

coverage = len(docx_text) / len(raw_text) * 100
# 要求 > 95%

# 检查关键板块是否存在
key_sections = ['Step 1', 'Step 2', ..., 'PayPal', 'Refersion', '金蝶']
for s in key_sections:
    assert s in docx_text, f"Missing: {s}"
```

**上次失败案例**：第一版只提取了 43% 的内容（7,861/18,090 字符），用户要求重做。
原因：使用了 AI 总结/压缩而非原文提取。

### 2. 图片压缩

- PNG 原图 57 张约 4MB → .docx 约 3.5MB → COS 上传超时
- JPEG quality=50 后约 1.3MB → .docx 约 1.3MB → 上传成功
- macOS 用 `sips` 压缩，Linux 用 `convert` (ImageMagick)

### 3. document.body.innerText 变量重复声明

浏览器 console 中多次声明 `const t = ...` 会报 `Identifier has already been declared`。
解决：每次用不同变量名（t2, t3, ...）或用 IIFE 包裹。

### 4. manage.move_file 参数名

`manage.move_file` 的目标文件夹参数是 `target_folder_id`，不是 `folder_id`。
