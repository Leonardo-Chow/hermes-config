# OBSBOT Admin JS 逆向分析记录

## 从 Vue SPA Bundle 定位 API 端点

### 步骤 1：下载主入口 JS
```bash
curl -s 'https://obsbot-cn.remo-ai.com/obsbot_admin/assets/index-DxUNngwW.js' > /tmp/obsbot_main.js
```
文件约 432KB，包含路由配置和 API 函数定义。

### 步骤 2：提取 chunk 列表
HTML 中的 `<link rel="modulepreload">` 标签列出预加载的 chunk。
关键 chunk：
- `market-DvH-txIb.js` — 包含 `kt`（API base URL）和 `Tt`（cookie key 枚举）
- `use-celebrity-Bq_2_Sdg.js` — 网红 store（Pinia）
- `ConfirmedList-pLdQibul.js` — 已确认网红列表页
- `CelebrityVisualization-BDa03rl8.js` — 数据可视化

### 步骤 3：定位 API base URL
```
# market-DvH-txIb.js 中：
c = `/obsbot_admin`     # 前端 base path
l = `https://api.obsbot.cn`  # API base URL (kt = l)
```
导出映射：`l as t` → 主文件中 `t as kt` → 所以 `kt = "https://api.obsbot.cn"`

### 步骤 4：定位 axios 实例
主文件中有两个 axios 实例：
```javascript
Gy = Uo({baseURL: `${kt}/ums`})  // 用户管理
Z  = Uo({baseURL: `${kt}/pms`})  // 产品/网红管理
```

### 步骤 5：定位认证逻辑
`Uo` 函数的请求拦截器：
```javascript
// dealer-proxy-type 从路由 meta.dealerKey 获取，默认 Xn.REMO ("Remo")
if (a) {  // a = isAuth，默认 true
    let t = or();  // or() = 从 cookie 读取 WEB_ADMIN_KEY_USER_TOKEN
    t && (e.headers.Authorization = t);  // 直接设原始 token，无 Bearer 前缀
}
```

### 步骤 6：定位具体 API 函数
确认列表页的调用链：
```
ConfirmedList.js → fe() = Ot from index → Dp = async e => Z.post(`/v1/netizen/infos-filtering`, e)
```

请求体构建：
```javascript
// re() 函数构建过滤参数
let re = async () => {
    let e = v();  // getFinalFilterData()
    return {
        status: A.value,  // 默认 Ce.ACTIVE = "active"
        ...e,
        search_type: `confirmed`
    };
};

// 调用
await fe({
    page_no: M.currentPage,
    page_size: M.pageSize,
    ...await re()
});
```

### 关键发现
- `Tt.USER_TOKEN = "WEB_ADMIN_KEY_USER_TOKEN"`
- `Xn.REMO = "Remo"`（首字母大写）
- `Dt.CN = "cn"`, `Dt.KR = "kr"`, `Dt.JP = "jp"`, `Dt.TIKTOK = "tk"`
- `Uo` 是 axios 实例工厂函数，支持 `isAuth`、`isToast`、`isRawResponse` 等选项
