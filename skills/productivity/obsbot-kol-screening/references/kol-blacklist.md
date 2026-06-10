# KOL 黑名单（永久排除）

以下 KOL 已确认不合格，每次搜索前必须排除。

## 黑名单（按原因分类）

### 官号
- Reolink
- Sling Pilot Academy
- NexiGo
- Hikvision / Hikvision Uzbekistan
- Nikon USA
- BIGO LIVE Official
- Acasis Official
- TP-Link Systems Inc.
- Bose Professional

### 安防摄像头
- ToolBox BD
- CCTV Camera Pros
- VIKYLIN Security
- securitybros

### 全是 Shorts
- DaizeDreams
- Milktea Emma

### 纯游戏
- HASIBxBRO
- Eddie's DL

### 内容偏离主题
- Coast Cams
- Big Bear Live Stream（无人画面）
- Nightfury（视频少，定位不明确）
- PTZtv
- DWDderWetterdienst（天气）
- WEBCAM NEPAL LIVE
- Scottish Wildlife Trust（野生动物）
- EGE – Gesellschaft zur Erhaltung der eulen e.V.
- Sugarloaf（画像偏差）
- Alex Explorer - Scotventure（画像偏差）

### 非英语频道
- VISIONPLUS TV RDC OFFICIEL（法语）

## 排除模式（正则匹配）

品牌模式：`official, inc., systems, reolink, nexigo, hikvision, nikon, bose, acasis, tp-link, obsbot, sling pilot, ege, gesellschaft, visionplus`

安防模式：`security, surveillance, cctv, alarm, reolink, toolbox`

偏离主题模式：`wildlife, weather, aviation, pilot, eulen, sugarloaf, scotventure, nepal live, live cam, webcam live, bear live`

欧洲语言模式：`deutsch, français, español, italiano, português, nederlands, polski, türk, 한국어, 日本語, 中文`

## 使用方法

每次搜索前加载黑名单：
```python
blacklist = ["coast cams", "reolink", "daizedreams", "milktea emma", "toolbox bd", "nightfury",
    "eddie's dl", "big bear live stream", "hasibxbro", "ptztv", "dwdderwetterdienst",
    "webcam nepal live", "sling pilot academy", "scottish wildlife trust",
    "ege", "sugarloaf", "scotventure", "visionplus"]
```
