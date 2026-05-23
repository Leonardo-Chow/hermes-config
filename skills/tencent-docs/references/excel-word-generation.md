# Excel/Word 文档生成与上传工作流

## Excel (.xlsx) 生成 — openpyxl

```bash
pip3 install openpyxl -q
```

### 基本模板

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()

# ===== Sheet 1: 数据总览 =====
ws1 = wb.active
ws1.title = "数据总览"

# 样式
header_font = Font(bold=True, color="FFFFFF", size=11)
header_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
thin_border = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin")
)

# 写表头
headers = ["序号", "名称", "数值", "链接"]
for col, h in enumerate(headers, 1):
    cell = ws1.cell(row=1, column=col, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align
    cell.border = thin_border

# 写数据
for i, item in enumerate(data, 1):
    row = i + 1
    for col, val in enumerate([i, item["name"], item["value"], item["url"]], 1):
        cell = ws1.cell(row=row, column=col, value=val)
        cell.border = thin_border

# 设置列宽
widths = [6, 25, 12, 40]
for i, w in enumerate(widths, 1):
    ws1.column_dimensions[get_column_letter(i)].width = w

wb.save("/tmp/output.xlsx")
```

### 多 Sheet 模板

```python
# Sheet 1: 数据总览
ws1 = wb.active
ws1.title = "视频总览"
# ... 写入视频列表

# Sheet 2: 评论详情
ws2 = wb.create_sheet("评论详情")
# ... 写入评论列表
```

## Word (.docx) 生成 — python-docx

```bash
pip3 install python-docx -q
```

### 基本模板

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(10)

# 标题
title = doc.add_heading('报告标题', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 信息表
info_table = doc.add_table(rows=3, cols=2)
info_table.style = 'Light Grid Accent 1'
info_data = [('数据来源', 'YouTube API'), ('采集时间', '2026-05-13'), ('总数', '100 条')]
for i, (label, val) in enumerate(info_data):
    info_table.rows[i].cells[0].text = label
    info_table.rows[i].cells[1].text = val
    for p in info_table.rows[i].cells[0].paragraphs:
        for r in p.runs:
            r.bold = True

doc.add_page_break()

# 按视频分节
for video in videos:
    doc.add_heading(video['title'], level=1)
    
    # 视频信息表
    info_table = doc.add_table(rows=5, cols=2)
    info_table.style = 'Light Grid Accent 1'
    # ... 填充
    
    # 评论表格
    cmt_table = doc.add_table(rows=len(video['comments'])+1, cols=4)
    cmt_table.style = 'Light Grid Accent 1'
    # ... 填充表头和数据

doc.save('/tmp/report.docx')
```

## 上传到腾讯文档

```bash
# 上传 Excel
bash ~/.hermes/skills/tencent-docs/import_file.sh /tmp/output.xlsx FOLDER_ID
# → 获取 TASK_ID, FILE_SIZE, FILE_KEY, FILE_MD5

# 触发导入
mcporter call tencent-docs manage.async_import \
    task_id="drivetask_xxx" file_size=12345 \
    file_key="temp/xxx/file.xlsx" file_name="output.xlsx" file_md5="xxx"

# 轮询进度
mcporter call tencent-docs manage.import_progress task_id="drivetask_xxx"
```

## 要点

- **Excel 多 Sheet**：用 `wb.active` 创建第一个，`wb.create_sheet("名称")` 创建后续
- **Word 分节**：每个视频/主题用 `doc.add_heading` + `doc.add_page_break` 分隔
- **数字格式化**：大数字用 K/M 后缀（如 `1.2K`），用 `openpyxl` 的数字格式或手动转换
- **中文文件名**：`import_file.sh` 支持中文文件名
- **大文件**：Excel/Word 超过 100KB 时导入可能较慢，轮询间隔 5 秒
