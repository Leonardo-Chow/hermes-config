# 产品竞品 YouTube 全量搜索模式（2026-05-19 验证）

当需要搜索某产品的**所有 YouTube 视频**（竞品分析、KOL 调研）时，使用以下模式。

## 多关键词覆盖搜索

用 15-20 组关键词确保全覆盖，每组翻页到 250 条上限：
```python
queries = [
    '"产品名"', '"产品名 review"', '"产品名 setup"', '"产品名 unboxing"',
    '"产品名 tutorial"', '"产品名 live stream"', '"产品名 vs"',
    '"产品名 2021"', '"产品名 2022"', '"产品名 overview"',
    '"品牌名 产品名"', '"产品名 test"', '"产品名 hands on"',
]
```

## 过滤竞品变体

用正则过滤掉不需要的产品变体（如 ISO 版本）：
```python
import re
exclude_patterns = [r'\bISO\s*GO\s*2\b', r'\b产品名\s*ISO\b']
for v in videos:
    combined = v['title'].lower() + ' ' + v['description'].lower()
    if any(re.search(p, combined, re.IGNORECASE) for p in exclude_patterns):
        excluded.append(v)
```

## 批量获取详情

- **视频统计**：`videos?part=statistics,contentDetails&id=ID1,ID2,...`（每次 50 个）
- **频道信息**：`channels?part=snippet,statistics&id=CH1,CH2,...`（每次 50 个）
- **Country mapping**：用 `snippet.country` 映射到中文国名
- **注意 API 配额**：搜索 API 配额消耗较快，20 组查询可能在中途被限流（返回空 JSON）。遇到限流停止搜索，已获取的结果足够使用。

## 自动分类

从 title + description 中提取：
- **网红类型**：根据 subscriberCount 分为头部KOL/腰部KOL/中小KOL/素人，再根据频道描述细分领域
- **视频分类**：评测/开箱/教程/直播/对比/介绍/技巧/测试
- **使用场景**：教会/播客/游戏/活动/婚礼/教育/体育/音乐/直播/内容创作
- **关键词提取**：从 title 中匹配预定义关键词列表
- **Pros/Cons**：从 description 中提取正面/负面关键词

## 上传到腾讯文档

1. 创建 smartsheet（先英文短标题 → rename 中文 → move 到目标文件夹）
2. 添加字段后删除默认字段和空行
3. 小批次上传（10 条/批），用文件传递 JSON 参数
4. 详见 `tencent-docs` skill 的 `references/smartsheet-pitfalls.md`
