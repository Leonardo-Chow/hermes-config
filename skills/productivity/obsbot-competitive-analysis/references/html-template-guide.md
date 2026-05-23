# 深色杂志风格 HTML 模板

## 页面结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{标题} | {日期}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>/* CSS 变量 + 组件样式 */</style>
</head>
<body>
  <!-- Hero 区 -->
  <div class="hero">
    <div class="hero-label">标签文字</div>
    <h1>主标题</h1>
    <p class="hero-sub">副标题</p>
    <div class="hero-stats">/* 大数字指标 */</div>
  </div>
  
  <!-- 内容区 -->
  <div class="section">
    <div class="section-num">01 / SECTION</div>
    <h2>标题</h2>
    <p class="section-desc">描述</p>
    <div class="metric-grid">/* 指标卡片 */</div>
    <div class="chart-container"><canvas id="xxx"></canvas></div>
  </div>
  
  <!-- Footer -->
  <div class="footer">/* 数据来源 */</div>
  
  <script>/* Chart.js 图表 */</script>
</body>
</html>
```

## 关键 CSS 组件

### Hero 区
```css
.hero {
  min-height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center;
  text-align:center; padding:60px 20px;
  background: radial-gradient(ellipse at 30% 50%, rgba(0,206,201,0.08) 0%, transparent 50%);
}
```

### 指标卡片
```css
.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:20px; text-align:center; }
.big-num { font-family:var(--mono); font-size:48px; font-weight:700; color:var(--accent); }
```

### 评价卡片（正/负面）
```css
.card { background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:30px; }
/* 正面：border-left:3px solid var(--green) */
/* 负面：border-left:3px solid var(--red) */
```

### 引用块
```css
.quote { border-left:3px solid var(--accent); padding:12px 20px; background:var(--bg-highlight); font-style:italic; }
.quote-pos { border-left-color:var(--green); }
.quote-neg { border-left-color:var(--red); }
```

## Chart.js 深色主题配置

```javascript
Chart.defaults.color = '#8a8a9a';
Chart.defaults.borderColor = '#2a2a3a';
Chart.defaults.font.family = "'Inter', sans-serif";
```

## 常用图表配置

### 水平柱状图（TOP N 排名）
```javascript
{ type:'bar', options:{ indexAxis:'y', plugins:{legend:{display:false}} } }
```

### 环形图（占比分布）
```javascript
{ type:'doughnut', options:{ plugins:{legend:{position:'right'}} } }
```

### 雷达图（多维对比）
```javascript
{ type:'radar', options:{ scales:{r:{beginAtZero:true,max:100}} } }
```

### 堆叠柱状图（正负对比）
```javascript
{ options:{ scales:{x:{stacked:true},y:{stacked:true}} } }
```
