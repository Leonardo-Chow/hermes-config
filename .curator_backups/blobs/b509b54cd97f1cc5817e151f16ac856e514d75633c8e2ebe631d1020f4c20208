# OBSBOT 提及模式库

## 视频标签中的 OBSBOT 提及

| 视频 | 标签 | 来源 |
|------|------|------|
| Stream Scheme "Don't Buy A 4K Webcam" | `#streamwithobsbot` | 视频描述区 hashtags |

**检查方法**：在视频页面用 browser_console 提取 hashtags：
```javascript
const hashtags = [];
document.querySelectorAll('a[href*="hashtag"]').forEach(el => {
    hashtags.push(el.textContent.trim().toLowerCase());
});
const obsbotHashtags = hashtags.filter(h => 
    h.includes('obsbot') || h.includes('meet') || h.includes('tiny')
);
```

## 评论区中的 OBSBOT 提及

### 负面信号（用户转向竞品）

| 视频 | 用户 | 评论内容 | 信号类型 |
|------|------|---------|---------|
| Stream Scheme "Don't Buy A 4K Webcam" | @Ryakk1 | "ended up bying the obsbot meet 2, but then I cancelled the order and chose the yolocam s3 instead" | 取消订单转竞品 |

### OBSBOT 关键词列表

```javascript
const obsbotKeywords = [
    'obsbot', 
    'meet 2', 'meet se', 'meet2',
    'tiny 2', 'tiny 3', 'tiny2', 'tiny3', 'tiny se',
    'tail 2', 'tail air', 'tail2',
    'obsbot meet', 'obsbot tiny',
    'streamwithobsbot'
];
```

### 负面信号关键词

```javascript
const negativeKeywords = [
    'cancelled', 'canceled', 'returned', 'sent back', 'refund',
    'overheating', 'broke', 'defective', 'disappointed',
    'better alternative', 'switched to', 'replaced with',
    'waste of money', 'not worth', 'regret'
];
```

## 检查顺序

1. **先检查视频 hashtags** — 在视频描述区查找 `#streamwithobsbot` 等标签
2. **再检查评论区** — 搜索 OBSBOT 关键词
3. **识别负面信号** — 取消订单、退货、转向竞品等

## 结果记录格式

- **有 OBSBOT 提及**：`评论区发现OBSBOT提及：用户@XXX提到"具体评论内容"，说明XXX。`
- **有负面信号**：`评论区发现OBSBOT提及：用户@XXX提到"考虑购买obsbot但最终选择了竞品XXX"，说明用户在对比中倾向竞品。`
- **无 OBSBOT 提及**：留空
