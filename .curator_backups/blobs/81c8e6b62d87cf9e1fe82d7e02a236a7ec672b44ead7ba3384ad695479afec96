# 每日视频上线监测 Word 文档模板

参照 2026-06-12——视频上线监测——上午.docx 格式。

## 文档结构

### 标题
```
OBSBOT 上线资源报告
日期：YYYY年M月D日（周X）
搜索范围：M月D日（周X）~ M月D日（周X）
```

### 一、全平台搜索结果

按平台列出所有找到的视频。每个视频格式：

```
1. 视频标题
博主：KOL ID
链接：URL
产品：产品名
类型：Dedicated Video / Integration（特殊主题"榜单""对比"）
发布时间：YYYY-MM-DD
简介：简短描述
```

### 二、符合 SOP 要求的视频（含质检）

**质检格式**：
```
1. 视频标题
博主：KOL ID
链接：URL
产品：产品名
类型：类型
视频内容质检：
☑️ 常规产品测评/开箱/展示
☑️ 原画直出：有
☑️ 特殊主题：无/对比/榜单/教程/多机搭建
描述区质检：
☒/☑️ 官网链接：有/无
☒/☑️ 亚马逊链接：有（联盟链接）/无
☒/☑️ 折扣信息：有/无
☒/☑️ 标签：有/无/未确认
```

### 三、统计汇总
| 平台 | 数量 |
|------|------|
| YouTube | N |
| TikTok | N |
| Instagram | N |
| X/Twitter | N |
| 合计 | N |

### 四、产品覆盖情况
| 产品 | 状态 |
|------|------|
| OBSBOT Tail Air | ✅有新视频/无新视频 |

### 五、过滤说明
| 过滤项 | 原因 |
|--------|------|

## Python 生成代码示例
```python
from docx import Document
doc = Document()
doc.add_paragraph('OBSBOT 上线资源报告')
doc.save('/Users/zhoulong/Downloads/YYYY-MM-DD-视频上线监测.docx')
```

## 关键规则
- 分两部分：全平台搜索结果 + 符合SOP视频（含质检）
- 质检含：视频内容质检 + 描述区质检
- 类型标注：Dedicated Video / Integration Video
- 特殊主题用括号标注（如"榜单""对比"）
- 文件格式：Word 文档（.docx），不要用 markdown 或智能表格
- 文件命名：YYYY-MM-DD-视频上线监测（不要加"上午/下午"）
- 保存路径：~/Downloads/
- 不要添加 @KOL 负责人员
