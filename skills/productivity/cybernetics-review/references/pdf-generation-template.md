# PDF 生成模板（新闻风格）

## 使用场景
- 新闻文章归档（CNN/BBC/经济学人等）
- 网页内容保存为 PDF
- 知识库文档导出

## 依赖
```bash
pip3 install reportlab --quiet
```

## CNN 风格 PDF 模板

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
import os

def generate_news_pdf(
    title: str,
    source: str,
    date: str,
    author: str,
    content: str,
    images: list[dict],  # [{'path': str, 'caption': str}]
    output_path: str
) -> str:
    """
    生成新闻风格的 PDF 文件
    
    Args:
        title: 文章标题
        source: 来源（如 CNN, BBC）
        date: 发布日期
        author: 作者
        content: 文章正文（段落用 \n\n 分隔）
        images: 图片列表 [{'path': '/path/to/img.jpg', 'caption': '图片说明'}]
        output_path: 输出 PDF 路径
    
    Returns:
        str: 生成的 PDF 文件路径
    """
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    
    # 颜色配置（CNN 风格）
    accent_color = HexColor('#CC0000')  # CNN 红
    dark_color = HexColor('#1A1A1A')
    gray_color = HexColor('#666666')
    
    # 样式定义
    title_style = ParagraphStyle(
        'NewsTitle',
        parent=styles['Title'],
        fontSize=24,
        leading=30,
        textColor=dark_color,
        spaceAfter=12,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    source_style = ParagraphStyle(
        'NewsSource',
        parent=styles['Normal'],
        fontSize=12,
        textColor=accent_color,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    date_style = ParagraphStyle(
        'NewsDate',
        parent=styles['Normal'],
        fontSize=10,
        textColor=gray_color,
        spaceAfter=20,
        fontName='Helvetica'
    )
    
    content_style = ParagraphStyle(
        'NewsContent',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=dark_color,
        spaceAfter=12,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    caption_style = ParagraphStyle(
        'NewsCaption',
        parent=styles['Normal'],
        fontSize=9,
        textColor=gray_color,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=gray_color,
        alignment=TA_CENTER
    )
    
    # 构建内容
    story = []
    
    # 标题
    story.append(Paragraph(title, title_style))
    
    # 来源和日期
    story.append(Paragraph(f"Source: {source}", source_style))
    story.append(Paragraph(f"Published: {date} | Author: {author}", date_style))
    story.append(Spacer(1, 10))
    
    # 主图（第一张）
    if images and os.path.exists(images[0]['path']):
        img = Image(images[0]['path'], width=6*inch, height=4*inch)
        story.append(img)
        if images[0].get('caption'):
            story.append(Paragraph(images[0]['caption'], caption_style))
    
    # 正文
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), content_style))
    
    # 其他图片
    for img_info in images[1:]:
        if os.path.exists(img_info['path']):
            story.append(Spacer(1, 10))
            img = Image(img_info['path'], width=6*inch, height=4*inch)
            story.append(img)
            if img_info.get('caption'):
                story.append(Paragraph(img_info['caption'], caption_style))
    
    # 页脚
    story.append(Spacer(1, 30))
    story.append(Paragraph("This article was sourced for educational purposes.", footer_style))
    story.append(Paragraph(f"Generated on {date} | Hermes Agent", footer_style))
    
    # 生成 PDF
    doc.build(story)
    return output_path


# 使用示例
if __name__ == '__main__':
    pdf_path = generate_news_pdf(
        title="Russia holds scaled-down Victory Day parade",
        source="CNN",
        date="May 9, 2026",
        author="Zahra Ullah",
        content="Article content here...",
        images=[
            {'path': '/tmp/main.jpg', 'caption': 'Main image caption'},
            {'path': '/tmp/second.jpg', 'caption': 'Second image caption'},
        ],
        output_path='/tmp/output.pdf'
    )
    print(f"PDF generated: {pdf_path}")
```

## 风格变体

| 风格 | 主色 | 适用场景 |
|------|------|---------|
| CNN | `#CC0000` | 美国新闻 |
| BBC | `#BB1919` | 英国新闻 |
| 经济学人 | `#E3120B` | 财经分析 |
| 纽约时报 | `#121212` | 深度报道 |

## 与 IMA 集成

生成 PDF 后上传到 IMA 知识库：

```bash
SKILL_DIR="$HOME/.hermes/skills/ima-skills"
KB_ID="<knowledge_base_id>"

node "$SKILL_DIR/knowledge-base/scripts/upload-to-kb.cjs" \
  "/tmp/output.pdf" "$KB_ID" "output.pdf"
```
