---
name: leonardo-brand
description: Leonardo 统一品牌设计系统。当创建任何视觉产物（HTML报告、PPT、PDF、日报、网页、数据可视化）时必须加载此 skill，确保所有输出风格一致。触发词：品牌、主题、配色、样式、报告模板、日报样式、PPT风格、设计规范。
---

# Leonardo Brand Guidelines

统一设计系统——所有产物（报告、PPT、网页、日报、PDF）共用一套色板、字体、间距、组件规范。

---

## 🎨 色板 (Color Palette)

### 主色系 — 深蓝科技

| 角色 | Hex | RGB | 用途 |
|------|-----|-----|------|
| **Primary** | `#1a56db` | 26,86,219 | 主按钮、标题强调、链接 |
| **Primary Dark** | `#1e3a5f` | 30,58,95 | 深色背景、导航栏 |
| **Primary Light** | `#3b82f6` | 59,130,246 | Hover 状态、次要强调 |
| **Surface Dark** | `#0f172a` | 15,23,42 | 页面/卡片深色背景 |
| **Surface** | `#1e293b` | 30,41,59 | 卡片背景 |
| **Surface Light** | `#f8fafc` | 248,250,252 | 浅色模式背景 |

### 功能色

| 角色 | Hex | 用途 |
|------|-----|------|
| **Success / 涨** | `#10b981` | 正面数据、上涨、成功 |
| **Danger / 跌** | `#ef4444` | 负面数据、下跌、错误 |
| **Warning** | `#f59e0b` | 警告、待处理 |
| **Info** | `#06b6d4` | 信息提示、次要数据 |
| **Muted** | `#64748b` | 次要文字、说明文字 |

### 图表色板（按顺序循环）

```
#3b82f6  #8b5cf6  #06b6d4  #10b981  #f59e0b
#ef4444  #ec4899  #14b8a6  #f97316  #6366f1
```

### 渐变

| 名称 | CSS |
|------|-----|
| 主渐变 | `linear-gradient(135deg, #1a56db 0%, #8b5cf6 100%)` |
| 暗底渐变 | `linear-gradient(180deg, #0f172a 0%, #1e293b 100%)` |
| 卡片高光 | `linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(139,92,246,0.05) 100%)` |

---

## 🔤 字体 (Typography)

### 字体栈

| 角色 | 主选 | 备选 | 用途 |
|------|------|------|------|
| **Display / 标题** | Inter | -apple-system, BlinkMacSystemFont, "Segoe UI" | 大标题、数字 |
| **Body / 正文** | "Noto Sans SC", "PingFang SC" | "Microsoft YaHei", sans-serif | 中文正文 |
| **Mono / 代码** | "JetBrains Mono", "Fira Code" | "SF Mono", monospace | 代码、数据、标签 |

### 字号规范

| 级别 | 大小 | 行高 | 字重 | 用途 |
|------|------|------|------|------|
| h1 | 2.25rem (36px) | 1.2 | 800 | 页面主标题 |
| h2 | 1.75rem (28px) | 1.3 | 700 | 板块标题 |
| h3 | 1.25rem (20px) | 1.4 | 600 | 子标题 |
| body | 1rem (16px) | 1.6 | 400 | 正文 |
| small | 0.875rem (14px) | 1.5 | 400 | 注释、来源 |
| caption | 0.75rem (12px) | 1.4 | 500 | 标签、角标 |

### 大数字 (Data Hero)

```css
.data-hero {
  font-family: 'Inter', sans-serif;
  font-size: 3.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## 📐 布局 (Layout)

### 间距系统（4px 基准）

| Token | 值 | 用途 |
|-------|-----|------|
| `--space-xs` | 4px | 图标与文字间距 |
| `--space-sm` | 8px | 紧凑元素间距 |
| `--space-md` | 16px | 默认内边距 |
| `--space-lg` | 24px | 卡片间距 |
| `--space-xl` | 32px | 板块间距 |
| `--space-2xl` | 48px | 大区块间距 |

### 圆角

| 级别 | 值 | 用途 |
|------|-----|------|
| sm | 6px | 按钮、标签 |
| md | 10px | 卡片、输入框 |
| lg | 16px | 大卡片、弹窗 |
| full | 9999px | 头像、圆形按钮 |

### 阴影

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
--shadow-md: 0 4px 12px rgba(0,0,0,0.4);
--shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
--shadow-glow: 0 0 20px rgba(59,130,246,0.3);
```

---

## 🧩 组件规范 (Components)

### 卡片 (Card)

```css
.card {
  background: #1e293b;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
```

### 标签 (Tag / Badge)

```css
.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.tag-up { background: rgba(16,185,129,0.15); color: #10b981; }
.tag-down { background: rgba(239,68,68,0.15); color: #ef4444; }
.tag-info { background: rgba(59,130,246,0.15); color: #3b82f6; }
```

### 表格 (Table)

```css
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
th {
  background: rgba(26,86,219,0.1);
  color: #3b82f6;
  font-weight: 600;
  text-align: left;
  padding: 12px 16px;
  border-bottom: 2px solid rgba(59,130,246,0.2);
}
td {
  padding: 10px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  color: #e2e8f0;
}
tr:hover td { background: rgba(59,130,246,0.05); }
```

### 按钮 (Button)

```css
.btn-primary {
  background: linear-gradient(135deg, #1a56db, #3b82f6);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
```

### 进度条 / 指标条

```css
.progress-bar {
  height: 6px;
  background: rgba(255,255,255,0.08);
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width 0.6s ease;
}
```

---

## 📊 数据可视化规范 (Charts)

### Chart.js 全局默认

```javascript
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Inter', 'Noto Sans SC', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 16;
Chart.defaults.plugins.tooltip.backgroundColor = '#1e293b';
Chart.defaults.plugins.tooltip.borderColor = '#3b82f6';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.padding = 10;
```

### 配色方案

- **折线图 / 面积图**: 主色 `#3b82f6`，渐变填充 `rgba(59,130,246,0.1)` → `rgba(59,130,246,0)`
- **柱状图**: 循环图表色板，hover 时加深 20%
- **饼图 / 环形图**: 前 5 色循环，`borderWidth: 2, borderColor: '#0f172a'`
- **涨跌**: 涨 `#10b981`，跌 `#ef4444`，平 `#64748b`

---

## 📄 各产物应用规范

### HTML 报告 / 日报

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

- 暗色背景 `#0f172a`，卡片 `#1e293b`
- 板块间用 `--space-xl` 分隔
- 每个板块标题前加色条 `border-left: 4px solid #3b82f6`
- 响应式：`max-width: 1200px; margin: 0 auto; padding: 0 24px`

### PPT / 幻灯片

- 标题幻灯片：深蓝渐变背景 + 白色大字
- 内容幻灯片：浅色背景 `#f8fafc`，左侧蓝色色条
- 图表：使用图表色板，白色背景
- 字体：标题 28-36pt Bold，正文 16-18pt Regular

### PDF 报告

```python
# fpdf2 配色
PRIMARY = (26, 86, 219)       # #1a56db
PRIMARY_DARK = (30, 58, 95)   # #1e3a5f
SURFACE = (15, 23, 42)        # #0f172a
TEXT = (226, 232, 240)         # #e2e8f0
MUTED = (100, 116, 139)       # #64748b
SUCCESS = (16, 185, 129)      # #10b981
DANGER = (239, 68, 68)        # #ef4444
```

### 数据表格 (Excel)

- 表头：深蓝背景 `#1e3a5f` + 白色文字
- 交替行：`#f8fafc` 和 `#ffffff`
- 涨跌数字：绿 `#10b981` / 红 `#ef4444`
- 金额列：右对齐，千分位，2 位小数
- 百分比列：右对齐，带 % 号

---

## ⚡ 快速应用

### CSS 变量（复制到任何 HTML 顶部）

```css
:root {
  --primary: #1a56db;
  --primary-dark: #1e3a5f;
  --primary-light: #3b82f6;
  --surface-dark: #0f172a;
  --surface: #1e293b;
  --surface-light: #f8fafc;
  --success: #10b981;
  --danger: #ef4444;
  --warning: #f59e0b;
  --info: #06b6d4;
  --muted: #64748b;
  --text: #e2e8f0;
  --text-secondary: #94a3b8;
  --border: rgba(255,255,255,0.06);
  --gradient-primary: linear-gradient(135deg, #1a56db 0%, #8b5cf6 100%);
  --font-display: 'Inter', sans-serif;
  --font-body: 'Noto Sans SC', 'PingFang SC', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --shadow-md: 0 4px 12px rgba(0,0,0,0.3);
}
```

### Python 报告色值字典

```python
BRAND = {
    'primary': '#1a56db',
    'primary_dark': '#1e3a5f',
    'primary_light': '#3b82f6',
    'surface_dark': '#0f172a',
    'surface': '#1e293b',
    'surface_light': '#f8fafc',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'info': '#06b6d4',
    'muted': '#64748b',
    'text': '#e2e8f0',
    'text_secondary': '#94a3b8',
    'charts': ['#3b82f6','#8b5cf6','#06b6d4','#10b981','#f59e0b',
               '#ef4444','#ec4899','#14b8a6','#f97316','#6366f1'],
    'gradient': ('#1a56db','#8b5cf6'),
}
```

---

## ⚠️ 铁律

1. **所有产物必须使用此色板** — 不允许自选颜色
2. **字体必须声明 fallback** — 中文环境必须包含 Noto Sans SC / PingFang SC
3. **数据涨跌只用绿涨红跌** — 不允许反过来
4. **图表最多用 5-7 色** — 超过时用透明度区分
5. **深色为主** — 默认深色背景，浅色模式仅用于打印/PDF
6. **大数字必须突出** — 用 hero 样式 + 渐变色
7. **来源标注** — 每个数据板块底部标注数据来源和时间
