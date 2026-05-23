# Google Docs → 腾讯文档导入工作流

## 场景
将 Google Docs 文档（含图片）完整迁移到腾讯文档。

## 限制
- Google Docs 在 Canvas 上渲染，**无法从 DOM 提取格式化文本**
- `/mobilebasic` 视图可获取纯文本，但丢失表格结构、标题层级
- 图片位置信息可通过 HTML 分割保留

## 完整流程

### Step 1: 提取文本+图片位置
```javascript
// 在浏览器中访问 mobilebasic 页面
// 用 JS 将 HTML 按 <img> 标签分割为 text+image 交错数组
const parts = html.split(/<img[^>]+>/i);
// 每个 text 部分提取纯文本，每个 image 部分记录 URL
// 输出: [{type:'text', content:'...'}, {type:'image', url:'...'}, ...]
```

### Step 2: 下载图片
```bash
# 800px 原图 → 压缩到 400px + 质量 30%
sips -s formatOptions 30 -Z 400 input.jpg --out output_sm.jpg
# 57 张图片压缩后约 900KB
```

### Step 3: 生成 .docx（图片内嵌）
```python
from docx import Document
doc = Document()
img_counter = 0
for part in structured_data:
    if part['type'] == 'image':
        img_counter += 1
        doc.add_picture(find_image(img_counter), width=Inches(4.5))
    elif part['type'] == 'text':
        for line in part['content'].split('\n'):
            # 根据内容判断 heading/bullet/paragraph
            doc.add_paragraph(line)
doc.save('output.docx')
```

### Step 4: 导入腾讯文档
```bash
cd ~/.hermes/skills/tencent-docs
bash import_file.sh /tmp/output.docx
# 获取 TASK_ID 后：
mcporter call tencent-docs manage.async_import --args '{...}'
```

### Step 5: 自检
- 文字覆盖率：提取文本长度 / 原始文本长度 ≥ 95%
- 关键板块：列出所有章节逐一确认
- 图片位置：确认图片内嵌在正文中，不是堆在末尾

## 文件大小限制
- COS 上传 >2MB 可能超时 → 压缩图片
- 57 张 400px JPG + 700 段文本 ≈ 2.5MB → 上传成功
