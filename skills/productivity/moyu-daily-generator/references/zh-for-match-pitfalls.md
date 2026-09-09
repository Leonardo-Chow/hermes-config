# zh_for 归一化陷阱与最佳实践

`gen_html.py` 里的 `zh_for(en_title)` 负责把 RSS 英文标题映射成中文翻译。这段逻辑看似简单，但 RSS 标题里的引号/破折号/重音/HTML 实体是导致双语漏翻的**最常见根因**——2026-08-26 至 2026-09-07 期间发现并修复了 5+ 起，全部因为归一化没覆盖某种字符变体。

## 现状（2026-09-07 已落地的归一化）

```python
import html as _html
en_title = _html.unescape(en_title)  # 还原 &#x27; 等 HTML 实体

def norm(s):
    for a, b in [
        ("\u2019", "'"), ("\u2018", "'"),                # ’ ‘ → '
        ("\u201c", '"'), ("\u201d", '"'),                # “ ” → "
        ("&apos;", "'"),                                 # &apos; → '
        ("\u2013", "-"), ("\u2014", "-"),                # – — → -
        # 重音/西文字符归一
        ("\u00e9","e"), ("\u00e8","e"), ("\u00ea","e"), ("\u00eb","e"),
        ("\u00e0","a"), ("\u00e2","a"), ("\u00f1","n"), ("\u00fc","u"),
    ]:
        s = s.replace(a, b)
    return s
```

匹配流程：
1. `en_title = html.unescape(en_title)` → 把 `&#x27;` → `'`
2. `k = norm(en_title[:30])` → 头 30 字符归一化后查字典
3. `if k in ZH: return ZH[k]` → 直接命中
4. 否则循环 `ZH.items()` 用 `pref[:25]` 前缀匹配
5. 仍不命中则用 `lstrip("'\"")` 跳过最前面的引号后再次前缀匹配
6. 兜底：`{norm(k).lstrip("'\""): v for k, v in ZH.items()}` 重新建归一化字典

## 历次踩坑 → 根因 → 修复

| 日期 | 现象 | 根因 | 修复 |
|------|------|------|------|
| 2026-08-26 | 41 条双语漏 16 条 | ZH key 用 ASCII `'` 而 RSS 是 `’` | 加入 `norm` 替换 |
| 2026-08-26 | 2 条（MarketWatch）漏 | RSS 标题最前面有 `\u2018`，归一化后比 key 多一个字符 | `lstrip("'\"")` 剥前缀标点 |
| 2026-08-27 | `Mountain View police` 类带撇号仍漏 | 字典里有 `Mountain View` 但 RSS 是 `Mountain View'` | 在 norm 后加 ZH_norm 兜底 |
| 2026-09-03 | BBC `‘I&#x27;d be the last to know’` 漏 | HTML 实体 `&#x27;` 没还原 | zh_for 入口加 `html.unescape` |
| 2026-09-04 | Jay-Z–Kaepernick `–` 不匹配 | 字典用 `-`，RSS 用 en-dash | norm 加 `\u2013/\u2014 → -` |
| 2026-09-04 | Beyoncé 重音 `é` 不匹配 | 字典无重音 `Beyonce`，RSS 是 `Beyoncé` | norm 加 `\u00e9 → e` |
| 2026-09-07 | Variety/THR 9 条新内容漏 | 字典 key 与 RSS 实际前缀不一致（如 `Ready to talk` vs `Ready to talk: ...`） | 用 startswith 的"短前缀"模式（key 25字符刚好够识别） |

## 双语漏翻的快速诊断流程

```python
import re
html = open('/tmp/moyu_data/moyu_daily_YYYY-MM-DD.html', encoding='utf-8').read()
lis = re.findall(r'<li>.*?</li>', html, re.S)
miss = [(re.search(r'class="src">(.*?)</span>', li).group(1),
         re.search(r'class="t-en">(.*?)</span>', li).group(1))
        for li in lis
        if 't-en' in li and 'class="zh"' not in li]
for src, title in miss:
    print(f'[{src}] {title[:80]}')
```

**关键经验**：每期生成后必须跑这段代码，缺译数 > 0 必须补字典后重生成，**不能直接传 HTML 上传**。

## 添加新翻译时的纪律

1. **先看 RSS 实际标题前 30 字符**：用浏览器查看 rss2json 输出的 `title` 字段
2. **字典 key 用 ASCII 撇号/连字符**：避免 `’/‘/“/”` 等 Unicode 字符
3. **中文 value 内部不要用 ASCII 双引号**（会破坏 Python 字符串）：
   - ❌ `"Anthropic 召回 \"Fable\""`
   - ✅ `"Anthropic 召回「Fable」"`
4. **ASCII 双引号自动修复脚本**（见 `scripts/fix-double-quotes.py`）：
   ```python
   import re
   src = open('gen_html.py', encoding='utf-8').read()
   lines = src.split('\n')
   for i, line in enumerate(lines):
       m = re.match(r'^(\s*"[^"]+":\s*")(.*)("\,?\s*)$', line)
       if m and '"' in m.group(2):
           # value 内 " → 「」
           ...
   ```
5. **每加完一个 key** 必须跑语法检查：`python3 -c "import ast; ast.parse(open('gen_html.py').read())"`

## 何时需要把 zh_for 重写

目前的 3 段匹配（dict 直接查 → 前缀 startswith → 归一化重建字典）能覆盖 95%+ 情况。当出现以下信号时考虑重写：
- 字典条目数 > 200 且大量条目与 RSS 实际标题前缀不匹配
- 同一条新闻的 5 个不同来源 5 个不同前缀（每条都要单独写 key）
- 此时可考虑用**模糊匹配**（编辑距离 ≤ 2）代替前缀匹配

## 关联资源

- 主 skill：`moyu-daily-generator` (v4.2)
- IMA 上传脚本：`~/.hermes/skills/ima-skills/knowledge-base/scripts/upload-to-kb.cjs`
- 双语质量评分：在 `moyu-daily-generator/SKILL.md` 质量评分章节
- 自动 ASCII 双引号修复：见 `gen_html.py` 生成后的 `fix-double-quotes.py`
