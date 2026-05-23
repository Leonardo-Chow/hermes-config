# YouTube 数据抓取实战记录（2026-05-10）

## 任务背景
批量抓取 35 个 OBSBOT 相关 YouTube 视频的详细数据（博主、浏览量、点赞、评论、粉丝数），并上传到腾讯文档。

## 工具测试结果

### yt-dlp
- **成功率**：14/35（40%）
- **失败原因**：YouTube n challenge 机制（IncompleteRead 错误）
- **成功时**：可获取完整数据（点赞、评论、浏览量、描述、标签）
- **建议**：不再作为首选工具，仅在需要评论数时尝试

### curl + regex
- **成功率**：35/35（100%）
- **可获取**：点赞、浏览量
- **不可获取**：评论（需 JS 渲染）
- **速度**：约 2 秒/个
- **正则模式**：
  - 点赞：`"defaultText":\{"simpleText":"([\d,]+)"\}.*?"accessibilityText":"like this video"`
  - 备选：`"likeCount":"(\d+)"`
  - 浏览量：`"viewCount":"(\d+)"`

### Camoufox (StealthyFetcher)
- **成功率**：5/5（100%）
- **优势**：反检测浏览器，可提取更多页面内容
- **页面文本**：约 5290 字符（curl 只有约 200 字符）
- **提取方式**：
  ```python
  from scrapling import StealthyFetcher
  import re
  fetcher = StealthyFetcher()
  page = fetcher.fetch(url)
  text = page.get_all_text()
  like_match = re.search(r'([\d,.]+)\n[Ll]ikes?', text)
  ```

### Scrapling Fetcher
- **成功率**：0/5（0%）
- **问题**：页面文本只有 205 字符，无法提取任何数据
- **结论**：不适用于 YouTube

## 博主粉丝数获取

### 方法
访问博主频道页面，用正则提取粉丝数：
```python
# 频道 URL 格式
url = f"https://www.youtube.com/@{channel}"  # 或 /{channel}

# 正则提取
match = re.search(r'([\d,.]+[KMB]?)\nsubscribers', text, re.IGNORECASE)
```

### 实战结果
- **成功**：20/31 个博主
- **失败原因**：部分博主频道页面不显示粉丝数，或格式不同

## 数据完成率

| 指标 | 完成数 | 完成率 |
|------|:------:|:------:|
| 浏览量 | 35/35 | 100% |
| 点赞 | 34/35 | 97% |
| 评论 | 14/35 | 40% |
| 博主粉丝数 | 21/35 | 60% |

## VPN 注意事项（用户明确反馈）

> **绝对不要乱切换 VPN 节点，这是网络错误的根本原因。**

- 保持 VPN 连接稳定，不做多余操作
- 如需切换节点，**必须从已有节点列表里选择**
- Shadowrocket 节点切换只能通过 GUI 操作
- 批量抓取失败率 > 50% 时，应停止并用已有数据

## 腾讯文档写入流程

```bash
# 1. 清空现有数据
mcporter call tencent-docs sheet.clear_range_all file_id=<ID> sheet_id=<SHEET_ID> start_row=0 end_row=40 start_col=0 end_col=12

# 2. 批量写入（通过 Python subprocess）
python3 -c "
import json, subprocess
payload = {'file_id': '<ID>', 'sheet_id': '<SHEET_ID>', 'values': [...]}
cmd = ['mcporter', 'call', 'tencent-docs', 'sheet.set_range_value']
for k, v in payload.items():
    if k == 'values':
        cmd.append(f'values={json.dumps(v, ensure_ascii=False)}')
    else:
        cmd.append(f'{k}={v}')
result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
"

# 3. 设置表头加粗
for col in {0..10}; do
    mcporter call tencent-docs sheet.set_cell_style file_id=<ID> sheet_id=<SHEET_ID> row=0 col=$col bold=true
done
```

## 教训总结

1. **yt-dlp 不可靠**：YouTube 的 n challenge 机制导致大量失败
2. **curl 是最稳的**：对于只需点赞和浏览量的场景，curl 100% 成功
3. **Camoufox 补充**：当 curl 无法提取时，Camoufox 是最佳备选
4. **评论数难以获取**：需要 JS 渲染，yt-dlp 成功时才有
5. **VPN 稳定性关键**：不要乱切节点，保持连接稳定
6. **分批处理**：每批 5 个视频，避免长时间运行被 kill
