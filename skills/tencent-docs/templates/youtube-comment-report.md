# YouTube 评论分析报告 — Word 文档模板

## 使用场景
从 YouTube Data API 抓取评论后，生成结构化 Word 报告并上传腾讯文档。

## 完整模板

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

def generate_comment_report(product_name, videos_with_comments, output_path):
    """
    videos_with_comments: list of dicts with keys:
        - channel, title, views, likes, date, url, video_id
        - comments: list of {author, text, likes, date, reply_count}
    """
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)
    
    # === 标题 ===
    title = doc.add_heading(f'OBSBOT {product_name} YouTube 视频评论分析报告', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # === 统计概要 ===
    total_videos = len(videos_with_comments)
    total_comments = sum(len(v['comments']) for v in videos_with_comments if v['comments'])
    commented_videos = sum(1 for v in videos_with_comments if v['comments'])
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f'生成日期: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n')
    run.font.size = Pt(11)
    run = p.add_run(f'视频数量: {total_videos} 个 | 评论总数: {total_comments} 条 | 有评论视频: {commented_videos} 个')
    run.font.size = Pt(11)
    doc.add_paragraph()
    
    # === 📊 视频总览表格 ===
    doc.add_heading('📊 视频总览', level=1)
    table = doc.add_table(rows=1, cols=7)
    table.style = 'Light Grid Accent 1'
    headers = ['序号', '博主', '视频标题', '观看', '点赞', '评论', '发布日期']
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(9)
    
    for idx, v in enumerate(videos_with_comments, 1):
        row = table.add_row()
        row.cells[0].text = str(idx)
        row.cells[1].text = str(v.get('channel', '?'))[:20]
        row.cells[2].text = str(v.get('title', '?'))[:50] + ('...' if len(str(v.get('title', ''))) > 50 else '')
        row.cells[3].text = str(v.get('views', '0'))
        row.cells[4].text = str(v.get('likes', '0'))
        row.cells[5].text = str(len(v.get('comments', [])))
        row.cells[6].text = str(v.get('date', ''))
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8)
    
    doc.add_paragraph()
    
    # === 📝 评论详情（按视频分节）===
    doc.add_heading('📝 评论详情', level=1)
    
    for v in videos_with_comments:
        comments = v.get('comments', [])
        if not comments:
            continue
        
        # 视频标题
        doc.add_heading(f'🎬 {v.get("title", "Unknown")}', level=2)
        
        # 视频信息
        p = doc.add_paragraph()
        run = p.add_run(f'频道: {v.get("channel", "?")}  |  评论数: {len(comments)} 条\n')
        run.font.size = Pt(10)
        run.bold = True
        run = p.add_run(f'链接: {v.get("url", "")}')
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0, 102, 204)  # 蓝色链接
        
        # 每条评论
        for c in comments:
            p = doc.add_paragraph()
            run = p.add_run(f'@{c.get("author", "")}')
            run.bold = True
            run.font.size = Pt(9)
            run = p.add_run(f'  (👍 {c.get("likes", 0)}, {c.get("date", "")})')
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(128, 128, 128)  # 灰色日期
            
            p2 = doc.add_paragraph()
            run = p2.add_run(str(c.get('text', '')))
            run.font.size = Pt(9)
            p2.paragraph_format.space_after = Pt(4)
    
    doc.save(output_path)
    return output_path
```

## 样式要点

| 元素 | 样式 | 说明 |
|------|------|------|
| 标题 | `level=0`, 居中 | 报告大标题 |
| 统计概要 | `Pt(11)`, 居中 | 视频数/评论数/有评论视频数 |
| 总览表格 | `Light Grid Accent 1` | 7列：序号/博主/标题/观看/点赞/评论/日期 |
| 视频标题 | `level=2` | 每个视频的评论区块标题 |
| 博主信息 | **加粗**, `Pt(10)` | 频道名 + 评论数 |
| 视频链接 | 蓝色 `RGBColor(0, 102, 204)` | 可点击跳转 |
| 评论作者 | **加粗**, `Pt(9)` | @作者名 |
| 点赞+日期 | 灰色 `RGBColor(128, 128, 128)`, `Pt(8)` | 辅助信息 |
| 评论正文 | `Pt(9)`, `space_after=Pt(4)` | 正文，评论间有小间距 |

## 上传流程

```bash
# 1. 生成 docx
python3 generate_report.py  # → /tmp/report.docx

# 2. 上传到腾讯文档
cd ~/.hermes/skills/tencent-docs
bash import_file.sh /tmp/report.docx

# 3. 触发导入
mcporter call tencent-docs manage.async_import \
    task_id="drivetask_xxx" file_size=12345 \
    file_key="temp/xxx/file.docx" file_name="report.docx" file_md5="xxx"

# 4. 轮询进度（每5秒）
mcporter call tencent-docs manage.import_progress task_id="drivetask_xxx"

# 5. 移动到目标文件夹
mcporter call tencent-docs manage.move_file \
    file_id="Dxxx" target_folder_id="文件夹ID"
```

## Pitfalls

- **execute_code sandbox 无 python-docx** — 必须用 `terminal` 执行 docx 生成
- **sum() 括号嵌套** — `sum(len(v['comments'] for v in ...))` 会报语法错误，正确写法：`sum(len(v['comments']) for v in ...)`
- **评论文本含 HTML 实体** — YouTube API 返回的 `textDisplay` 含 `&amp;` 等，需 `html.unescape()` + 正则去标签
- **大表格性能** — 超过 100 个视频时 Word 生成可能较慢（~10秒），属正常
