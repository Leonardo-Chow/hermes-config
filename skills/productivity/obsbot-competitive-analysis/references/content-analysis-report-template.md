# 博主合作内容分析报告（Excel 模板格式）

## 适用场景

拿到一份「品牌 × 博主合作数据表」（如 Insta360/Elgato/Yolo 的 IG 投放记录，多数分析列只有占位符"1"），要求按既有《内容分析报告》模板格式补全分析并输出。模板示例：内容分析报告.xlsx（Razer Hello Kitty / Logitech Aurora / K/DA / Elgato Fallout 案例）。产出为**复刻模板格式的 Excel**。

## 14 列结构（表头固定）

`品牌 | 产品 | IP | 平台 | 内容链接 | 博主类型 | 内容主题 | 内容形式 | IP呈现方式 | 关键词（标题/Hashatg） | 博主关注点 | 用户关注点 | 样本Insights | 整体insights/合作建议`

## 合并单元格约定（复刻模板）

- 品牌列 + IP 列：按品牌块合并（如 Razer 5 行 → A2:A6、C2:C6）
- 产品列：同一品牌下产品不同时不合并（逐行显示）
- 平台列：模板中按平台分段合并（Youtube 段 / Instagram 段）
- N 列（整体insights/合作建议）：**整列合并**（如 N2:N28），放全报告总洞察

## 样式（openpyxl）

- 表头：宋体 10 bold，填充 E1EAFF，居中换行，行高 ~32
- 正文：宋体 9，垂直顶端 + 自动换行；行高按内容量估算 `max(50, min(len*1.9, 220))`
- 列宽参考：A13 B12 C8 D12 E40 F18 G30 H10 I24 J34 K40 L40 M45 N55
- `freeze_panes = "A2"`

## 各列写作要求（用户认可风格）

- **内容主题**：一句话概括（场景+卖点+形式），如「Stream Room 巡礼：展示 AI 追踪效果」「Prime Day 促销种草：前10单送收纳包+折扣码」
- **内容形式**：Reels / 图片 / YTB dictated video（YouTube 长视频口播）
- **IP呈现方式**：非 IP 联名统一写 `"/（非 IP 联名，产品作为…出现）"`；联名则写 IP 如何呈现（视觉元素 / 口播提及 / 桌搭融合），参考模板「背景为粉色桌搭+三丽鸥元素，视觉统一，口播提到 hellokitty」
- **博主关注点**：编号列表，从**真实 caption** 提取博主讲了什么（外观/功能/促销机制/场景）
- **用户关注点**：编号列表，**必须基于真实评论**（IG 评论 API / YT commentThreads），不能编造
- **样本Insights**：每条 2-3 条可执行洞察。模板高频句式：不可只展示外观、必须设定一个核心应用痛点、Brief 中要求博主解答说明书外的小细节、保留"挑剔感"再肯定核心卖点、评论关键词自动回复机制有效
- **整体insights（N列合并）**：分段落覆盖：①平台投放分布与功能分工（如 IG 种草+转化、YT 教育+决策） ②红人选择趋势（垂类化/去科技化：Study With Me / Music / Lifestyle / Gamer） ③内容方向（从评测转向场景展示） ④卖点/IP 在内容中的作用 ⑤可复用互动机制（评论CODE、抽奖、限时折扣、前后对比） ⑥⚠️负面反馈管理（如 Win11 兼容性吐槽，投放前需确认固件）

## 生成脚本要点

- 先 `openpyxl.load_workbook` 逐格读取原模板理解结构——**read_file 的 xlsx 提取会截断/丢失合并单元格信息，必须用 openpyxl 才完整**（含 merged_cells.ranges、样式）
- ⚠️ **合并分组 off-by-one**：rows[i] 映射到 Excel 行 = i+2；按品牌分组时，上一组结束行 = i+1，新组起始行 = i+2，最后一组结束 = len(rows)+1。实测首版公式少 1 导致 Elgato 组合并错位到 Insta360 最后一行
- 本类任务 90% 工作量在数据采集，先抓真实数据再写分析

## 数据采集（IG 博主合作表）

- 帖子 caption：curl 帖子页 `og:description`（匿名，短 UA + X-IG-App-ID）
- 评论区：IG comments API（需 cookie，shortcode 解码 media_id）——详见 instagram-follower-batch-fetch skill「帖子级内容获取」
- 数据表脏数据核对清单：产品列与 caption 不符（标 Facecam 实为 Prompter）、官方号转发 KOC（caption 作者≠博主 ID）、内容链接是主页而非单帖（无法分析，标注"需人工确认"）、同一链接重复多行、占位符"1"

## 实测数据（2026-08-04 Insta360/Elgato/Yolo 报告）

- 27 条记录：Insta360 19 / Elgato 7 / Yolo 1，全部 Reels
- 互动率洞察：参数罗列型 IG 内容互动极低（59赞）；情绪/场景种草型最高（7.3K-25K 赞）；抽奖拉爆评论（3,971 评论≈点赞量）
