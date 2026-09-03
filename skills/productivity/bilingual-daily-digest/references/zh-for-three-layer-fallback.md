# 双语 zh_for 三层 Fallback 完整指南

## 问题背景

RSS 标题中常含 Unicode 弯引号（U+2018/2019/201C/201D），与映射表 key 的 ASCII 引号（`'` `"`）不一致，导致 `startswith` 静默漏翻。**2026-08-26 实测：41 条双语漏 16 条**，但评分系统不会报错，仅靠统计 `class="zh"` 缺失数才暴露。

## 三层 Fallback 完整代码

```python
def zh_for(en_title):
    def norm(s):
        # 1. 弯引号 → ASCII 直引号
        for a, b in [("\u2019","'"), ("\u2018","'"),
                     ("\u201c",'"'), ("\u201d",'"'),
                     ("&#x27;","'"), ("&apos;","'")]:
            s = s.replace(a, b)
        return s

    t_norm = norm(en_title)
    k = norm(en_title[:30])  # 第一层 key 归一化

    if k in ZH:
        return ZH[k]

    # 第二层：剥前缀标点后前缀匹配
    for pref, tr in ZH.items():
        p = norm(pref).lstrip("'\"")[:25]
        t = t_norm.lstrip("'\"")
        if t.startswith(p):
            return tr

    # 第三层：ZH key 也归一化+剥标点
    ZH_norm = {norm(k).lstrip("'\""): v for k, v in ZH.items()}
    if k in ZH_norm:
        return ZH_norm[k]

    return ""
```

**三层各覆盖的场景**：

| 层 | 处理 | 例子 |
|----|------|------|
| 1 | key 用 ASCII 引号、value 字符串对得上 | `"It's the ultimate regifting" → "It's the ultimate regifting"` |
| 2 | key 缺前导 `'`、value 开头有 `'...` | `"'It's the ultimate regifting" → 剥 ' 后以 `It's` 匹配` |
| 3 | key 和 value 都用弯引号，归一化后还不对 | 实测罕见，但兜底防万一 |

## 验证脚本（每期生成必跑）

```python
import re
html = open("moyu_daily_YYYY-MM-DD.html", encoding="utf-8").read()
lis = re.findall(r"<li>.*?</li>", html, re.S)
total_bi = sum(1 for li in lis if "t-en" in li)
miss_zh  = sum(1 for li in lis if "t-en" in li and 'class="zh"' not in li)
print(f"双语 {total_bi} 条, 缺中文 {miss_zh} 条")
assert miss_zh == 0, f"❌ 双语缺译 {miss_zh} 条，需补 ZH 字典"
```

## 关联踩坑

- **ZH 字典 value 不能含 ASCII `"`**：会切断 Python 字符串并 SyntaxError
  - 解法：value 内的 `"` 改成「」或单引号
  - 自动化修复见 `bilingual-daily-digest` SKILL.md §2

- **cnvertify 测试用例**（来自实际漏翻事件）：
  - `'\u2018My main goal is to help people\u2019: I\u2019m single, 74...'` → 第二层 `lstrip("'\"")` 后匹配 `My main goal is to help peopl` ✅
  - `'\u2018Paranormal Activity\u2019 Review: Spooky...'` → 同上 ✅
