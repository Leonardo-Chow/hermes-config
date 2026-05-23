# 常用知识库 ID

## 学习知识库
- **ID:** `dyhBpuSFEIoU_cuWlgKN5meq8LX0FU5uKQ-hK4rXog4=`
- **用途:** 存储学习资料、财经新闻 PDF 等
- **创建者:** Leonardo

## 摸鱼日报知识库
- **ID:** `VBTByTbvSYzGkdimVKRGgRE_rV75-vH1VdXWenYU96o=`
- **用途:** 存储每日摸鱼日报
- **封面图片 media_id:** `img_804ad0c79724fcebb6bc3d08062b3588_c7ac315e6d0c84f26b1c25ca4c771cc87454811872052525`

## Herme记忆库
- **ID:** `uhcEva4nd2xus1Q2yt7yn_N4_waEdOsQlVU3lhnkLXw=`
- **用途:** 作为 Hermes 外部 Memory，存储持久记忆和技能清单
- **笔记 ID:**
  - 持久记忆笔记: 7458759479674019
  - 技能清单笔记: 7458759588728714

## OBSBOT知识库
- **ID:** `mmYXYA4QIUsKj6PikZYHx1HtEhrPFvmysbEUrO4UfvQ=`
- **用途:** OBSBOT 公司相关文档（KOL Workflow、社媒监控等）
- **创建者:** Leonardo

## OBSBOT社媒监控
- **ID:** `EmO3hjd7GDxTm3Oc5TaTJac-Lzutinhil9N4_SOxdVI=`
- **用途:** OBSBOT 社媒监控数据

## 使用示例

```bash
# 上传 PDF 到学习知识库
node ~/.hermes/skills/ima-skills/knowledge-base/scripts/upload-to-kb.cjs \
  /tmp/report.pdf \
  "dyhBpuSFEIoU_cuWlgKN5meq8LX0FU5uKQ-hK4rXog4=" \
  "report.pdf"

# 搜索知识库
node ~/.hermes/skills/ima-skills/ima_api.cjs \
  "openapi/wiki/v1/search_knowledge_base" \
  '{"query":"学习","cursor":"","limit":10}'
```
