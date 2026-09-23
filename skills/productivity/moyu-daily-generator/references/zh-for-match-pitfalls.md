# zh_for 归一化匹配陷阱案例集（2026-08-26 至 2026-09-15）

记录历次 `zh_for` 归一化匹配失败的真实案例、根因与修复清单。每次新增翻译后，**必须**在生成后验证 `class="zh"` 缺失数=0 才算过。

---

## 陷阱分类与修复清单

### 1. 弯引号 / 破折号 / 重音字符不一致

| 场景 | RSS 标题片段 | ZH 字典 key | 根因 | 修复 |
|------|-------------|------------|------|------|
| 弯单引号 | `Dick's Sporting Goods` | `Dick's Sporting Goods` | RSS 用 `\u2019` (')，key 用 ASCII `'` | `norm` 统一替换 `\u2019` → `'` |
| 弯双引号 | `“South Park”` | `"South Park"` | RSS 用 `\u201c`/`\u201d` | `norm` 替换 `\u201c`/`\u201d` → `"` |
| En-dash | `Jay-Z–Colin` | `Jay-Z-Colin` | RSS 用 `\u2013` (–) | `norm` 替换 `\u2013` → `-` |
| Em-dash | `A—B` | `A-B` | RSS 用 `\u2014` (—) | `norm` 替换 `\u2014` → `-` |
| 重音 é | `Beyoncé` | `Beyonce` | RSS 用 `\u00e9` | `norm` 替换 `\u00e9` → `e` |
| 重音 è | `cafè` | `cafe` | `\u00e8` | `norm` 替换 `\u00e8` → `e` |
| 重音 â | `crème` | `creme` | `\u00e2` | `norm` 替换 `\u00e2` → `a` |
| 重音 ñ | `señor` | `senor` | `\u00f1` | `norm` 替换 `\u00f1` → `n` |
| 重音 ü | `für` | `fur` | `\u00fc` | `norm` 替换 `\u00fc` → `u` |

**修复代码**（`zh_for` 内部 `norm` 函数）：
```python
def norm(s):
    for a, b in [
        ("\u2019","'"), ("\u2018","'"), ("\u201c",'"'), ("\u201d",'"'),
        ("\u2013","-"), ("\u2014","-"),
        ("\u00e9","e"), ("\u00e8","e"), ("\u00ea","e"), ("\u00eb","e"),
        ("\u00e0","a"), ("\u00e2","a"), ("\u00f1","n"), ("\u00fc","u"),
        ("'","'"), ("&apos;","'"), (""",'"'),
    ]:
        s = s.replace(a, b)
    return s
```

---

### 2. HTML 实体未还原

| 实体 | 原始 | 期望 | 根因 | 修复 |
|------|------|------|------|------|
| `'` | `I'd` | `I'd` | `zh_for` 入口未 `html.unescape` | 入口先 `html.unescape(en_title)` |
| `&apos;` | `I&apos;d` | `I'd` | 同上 | 同上 |
| `"` | `"Hello"` | `"Hello"` | 同上 | 同上 |
| `&` | `A&B` | `A&B` | 同上 | 同上 |

**修复**：`zh_for` 入口第一行 `en_title = _html.unescape(en_title)`

---

### 3. RSS 标题首字符弯引号

| RSS 标题 | ZH 字典 key | 根因 | 修复 |
|----------|------------|------|------|
| `‘South Park’` | `South Park` | 标题以 `\u2018` 开头，归一化后变 `'`，比 key 多一字符 | `t_norm.lstrip("'\"")` 剥离首字符引号后再 `startswith` |

**修复**：
```python
t_norm = norm(en_title)
k = norm(en_title[:30])
t = t_norm.lstrip("'\"")  # 剥离首字符引号后再 startswith
for pref, tr in ZH.items():
    p = norm(pref).lstrip("'\"")[:25]
    if t.startswith(p):
        return tr
```

---

### 4. HTML 实体与弯引号混合

| 场景 | RSS 标题 | ZH 字典 key | 根因 | 修复 |
|------|----------|------------|------|------|
| `I'd` | `I'd` | `I'd` | 实体未还原 + 首字符引号 | 先 `html.unescape` 再 `lstrip("'\"")` |

---

### 5. RSS 标题首字符弯双引号

| RSS 标题 | ZH 字典 key | 根因 | 修复 |
|----------|------------|------|------|
| `“The Fire Within You”` | `The Fire Within You` | 标题以 `\u201c` 开头，归一化后变 `"` | `lstrip("'\"")` 同时剥离单双引号 |

---

### 6. RSS 标题包含 en-dash 但 key 用连字符

| 场景 | RSS 标题 | ZH 字典 key | 根因 | 修复 |
|------|----------|------------|------|------|
| En-dash | `Jay-Z–Colin` | `Jay-Z-Colin` | RSS 用 `\u2013`，key 用 `-` | `norm` 替换 `\u2013` → `-` |

---

### 6. 重音字符（é/è/â/ñ/ü 等）

| 场景 | RSS 标题 | ZH 字典 key | 根因 | 修复 |
|------|----------|------------|------|------|
| 重音 é | `Beyoncé` | `Beyonce` | RSS 用 `\u00e9`，key 无重音 | `norm` 替换 `\u00e9` → `e` 等 |

---

### 7. ZH 字典 key 与 RSS 标题前缀匹配逻辑

**问题**：ZH 字典 key 使用英文标题前 30 字符（归一化后），但 RSS 标题可能更长，且可能以弯引号开头。旧逻辑 `t_norm.startswith(p[:25])` 存在三个问题：
1. `p` 未归一化，`p[:25]` 可能包含弯引号
2. `t_norm` 可能以 `'` 开头，比 `p` 多一字符
3. `p` 未归一化，可能包含弯引号/重音

**修复**：双向归一化 + 双向 `startswith` 检查
```python
t_norm = norm(en_title)
k = norm(en_title[:30])
if k in ZH: return ZH[k]
t = t_norm.lstrip("'\"")  # 剥离首字符引号
for pref, tr in ZH.items():
    p = norm(pref).lstrip("'\"")[:25]  # key 也归一化并剥离首字符引号
    if t.startswith(p):
        return tr
# 兜底：key 归一化后去首字符引号再查
ZH_norm = {norm(k).lstrip("'\""): v for k, v in ZH.items()}
if k in ZH_norm: return ZH_norm[k]
```

---

### 7. ZH 字典 value 内 ASCII 双引号

| 场景 | value | 后果 | 修复 |
|------|-------|------|------|
| `"Beyoncé《B'Day》发行 20 周年"` | 包含 `"` | `SyntaxError: invalid syntax` | 手动改为 `「Beyoncé《B'Day》发行 20 周年」` |

**自动修复脚本**：`scripts/fix-double-quotes.py` - 扫描 ZH 字典 value 内 ASCII 双引号 → 「」。每次 ZH 大改动后必跑。

---

### 8. 重复 key 导致翻译丢失

| 场景 | 后果 | 修复 |
|------|------|------|
| ZH 字典中重复 key（如 `South Park Creators...` 出现两次） | 后者覆盖前者，导致前者翻译丢失 | 新增翻译前先检查是否已存在；生成后验证 `class="zh"` 缺失数=0 |

---

### 9. ZH 字典 key 与 RSS 标题前缀匹配：key 过短/过长

| 场景 | 根因 | 修复 |
|------|------|------|
| key 只取前 25 字符，RSS 标题前 30 字符不同 | 统一为前 30 字符，且双向归一化后比较 | 统一 `norm(en_title[:30])` 与 `norm(pref[:30])` |

---

### 9. 重复 key 导致翻译丢失（补记）

| 日期 | 重复 key | 后果 | 修复 |
|------|----------|------|------|
| 2026-09-10 | `South Park Creators...` 重复 | 后者覆盖前者 | 清理重复项，生成后验证缺失数=0 |
| 2026-09-10 | `The Fire Within You...` 重复 | 同上 | 同上 |
| 2026-09-10 | `Place to Be...` 重复 | 同上 | 同上 |

---

## 验证清单（每期生成后必跑）

```python
import re
html = open('moyu_daily_YYYY-MM-DD.html').read()
lis = re.findall(r"<li>.*?</li>", html, re.S)
total_bi = sum(1 for li in lis if "t-en" in li)
miss_zh = sum(1 for li in lis if "t-en" in li and 'class="zh"' not in li)
print(f'双语 {total_bi}, 缺中文 {miss_zh} {"✅" if miss_zh==0 else "❌"}')
```

**必须**：`miss_zh == 0` 才算过关。

---

## 自动修复脚本

`scripts/fix-double-quotes.py` - 扫描 ZH 字典 value 内 ASCII 双引号 → 「」。每次 ZH 大改动后必跑。

```bash
python3 scripts/fix-double-quotes.py
```

---

## 陷阱总结表（快速查阅）

| # | 陷阱 | 症状 | 核心修复 | 参考文件 |
|----|------|--------|----------|----------|
| 1 | 弯引号/破折号/重音 | `class="zh"` 缺失 | `norm` 统一替换 | §1 |
| 2 | HTML 实体 | 同左 | `html.unescape` 入口 | §2 |
| 3 | 首字符弯引号 | 同左 | `lstrip("'\"")` | §3 |
| 4 | HTML 实体+弯引号 | 同左 | 组合修复 | §4 |
| 5 | 首字符弯双引号 | 同左 | `lstrip("'\"")` | §5 |
| 6 | En-dash | 同左 | `norm` 替换 `\u2013` | §6 |
| 6 | 重音字符 | 同左 | `norm` 扩展替换表 | §6 |
| 7 | key/RSS 前缀匹配 | 同左 | 双向归一化 + 双向 startswith | §7 |
| 7 | value 内 ASCII " | SyntaxError | 手动改「」、跑 fix-double-quotes.py | §7 |
| 8 | 重复 key | 翻译丢失 | 新增前检查 + 生成后验证 | §8 |
| 9 | key 长度不一致 | 同左 | 统一前 30 字符 | §9 |
| 10 | 重复 key 补记 | 翻译丢失 | 清理重复 + 验证 | §10 |

---

## 关联文件

- `scripts/fix-double-quotes.py` — 自动修复 ZH 字典 value 内 ASCII 双引号
- `gen_html.py` 中的 `zh_for` 函数 — 核心匹配逻辑
- `gen_html.py` 中的 `ZH` 字典 — 中文翻译映射表
- `scripts/fix-double-quotes.py` — 自动修复脚本