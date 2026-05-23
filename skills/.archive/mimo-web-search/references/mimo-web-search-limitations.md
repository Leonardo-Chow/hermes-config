# MiMo 联网搜索实际能力测试记录

## 测试日期：2026-05-09

### 测试场景：获取经济学人全文

**用户需求**：抓取经济学人今日头版新闻全文，生成 PDF 上传到 IMA

**测试结果**：

| 方案 | 结果 | 说明 |
|:-----|:-----|:-----|
| MiMo web_search + 经济学人 | ❌ 只能获取摘要 | MiMo 返回搜索结果摘要，无法获取全文 |
| MiMo web_search + archive.today | ❌ 无法访问 | MiMo 报告"网络超时" |
| MiMo web_search + Wayback Machine | ❌ 无法访问 | MiMo 报告"网络超时" |
| MiMo 直接生成仿写文章 | ✅ 成功 | 生成了高质量的 BBC/Reuters 风格文章 |

### 关键发现

1. **MiMo 的 web_search 是模拟的**
   - 它会返回看似合理的搜索结果，但不是从真实网站抓取的
   - 它无法访问被墙的网站（archive.today、Wayback Machine 等）
   - 它无法绕过付费墙

2. **MiMo 可以生成高质量仿写文章**
   - 当不使用 tools 参数，直接让 MiMo 生成文章时，效果很好
   - 生成的 BBC/Reuters 风格文章质量很高，包含具体数据、分析师观点等
   - 每篇文章 500-900 字，符合专业财经新闻标准

3. **用户误解**
   - 用户可能认为"联网搜索"= 能访问任何网站
   - 需要明确告知用户：MiMo 的联网搜索是模拟的，不是真实的

### 推荐工作流

```
用户需求：获取 BBC/Reuters/Economist 文章
    ↓
明确告知：MiMo 只能生成仿写文章，不能抓取真实内容
    ↓
用户接受：让 MiMo 生成仿写文章
    ↓
MiMo 生成：高质量仿写文章（不使用 tools 参数）
    ↓
生成 PDF：用 Playwright 生成 PDF
    ↓
上传 IMA：用 upload-to-kb.cjs 上传到知识库
```

### 代码示例

```python
# 正确的方式：直接生成仿写文章
payload = {
    'model': 'mimo-v2.5-pro',
    'messages': [
        {
            'role': 'user',
            'content': '请生成 BBC Business 风格的财经新闻文章（500字以上），主题是...'
        }
    ]
    # 注意：不包含 tools 参数
}

# 错误的方式：使用 web_search 工具
payload = {
    'model': 'mimo-v2.5-pro',
    'messages': [...],
    'tools': [{'type': 'function', 'function': {'name': 'web_search', ...}}]
    # 这会触发 MiMo 请求调用 web_search，但实际无法获取真实内容
}
```

### 相关技能

- `ima-skills` — 上传 PDF 到 IMA 知识库
- `moyu-daily-generator` — 摸鱼日报生成
