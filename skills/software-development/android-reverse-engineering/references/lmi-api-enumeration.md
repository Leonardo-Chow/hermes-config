# Lmi Live API 端点枚举结果（2026-05-30）

## 结论

- **无网页版** — LMI Live 是纯 Flutter 移动应用（`package:lmi_app`），libapp.so 中无 H5/web 代码
- **全部需要认证** — 所有 `/app/*` 端点均返回 401（需 `lmi-live-token` header）
- **无公开端点** — 无 `/public/*`、`/api/*`、`/web/*` 等公开路径
- **无 H5/分享页** — `/h5`、`/share`、`/live-room/share` 均返回 501 资源不存在

## API 域名

- `lmilive.lmizhibo.com`（IP: 81.71.248.163）— 唯一 API 服务器
- `lmizhibo.com` / `www.lmizhibo.com` — 无法连接，无 web 服务

## 端点枚举详情

| 路径 | 参数 | 结果 | 说明 |
|:-----|:-----|:-----|:-----|
| `/app/live/info` | `?roomId=1419` | 401 | 房间信息+TRTC参数 |
| `/app/live/info` | `?roomDisplayId=55555` | 401 | 用展示ID也不行 |
| `/app/live/summary/info` | `?roomId=1419` | 401 | 房间摘要 |
| `/app/live/room/1419` | — | 401 | RESTful 风格 |
| `/app/live/room` | `?roomId=1419` | 401 | 查询风格 |
| `/app/live/web/info` | `?roomId=1419` | 401 | 尝试web端点 |
| `/app/share/live` | `?liveRoomId=1419` | 401 | 分享接口 |
| `/app/config` | — | 401 | 配置 |
| `/app/config/list` | — | 401 | 配置列表 |
| `/app/version` | — | 401 | 版本信息 |
| `/app/announcement` | — | 401 | 公告 |
| `/app/banner/list` | — | 401 | Banner |
| `/app/category/list` | — | 401 | 分类列表 |
| `/app/hot/room` | — | 401 | 热门房间 |
| `/app/recommend` | — | 401 | 推荐 |
| `/api/live/info` | `?roomId=1419` | 401 | 非 /app 前缀也需认证 |
| `/public/live/1419` | — | 501 | 公开路径不存在 |
| `/share` | `?liveRoomId=1419&roomDisplayId=55555` | 501 | 分享页不存在 |
| `/live-room/share` | `?liveRoomId=1419` | 501 | 深度链接路径不存在 |
| `/live/1419` | — | 501 | 直接路径不存在 |
| `/web/live/1419` | — | 501 | Web路径不存在 |
| `/web/room/1419` | — | 501 | Web路径不存在 |
| `/h5/live/1419` | — | 501 | H5路径不存在 |
| `/h5/room/55555` | — | 501 | H5路径不存在 |
| `/h5` | — | 空响应 | H5入口不存在 |

## 网页版搜索结果

| URL | 结果 |
|:-----|:-----|
| `https://lmizhibo.com` | ERR_CONNECTION_CLOSED |
| `http://lmizhibo.com` | 超时 |
| `https://www.lmizhibo.com` | ERR_CONNECTION_CLOSED |
| `https://h5.lmizhibo.com` | 超时 |
| `https://web.lmizhibo.com` | 超时 |
| `https://live.lmizhibo.com` | 超时 |
| `https://m.lmizhibo.com` | 超时 |

## libapp.so 关键字符串

```
# 项目源码路径（确认是纯移动App）
file:///D:/JAVA/LLI/live-streaming-app-repository/lmi_app/

# TRTC SDK License
https://1385395381.trtcube-license.cn/license/v2/1385395381_1/v_cube.license

# 分享深度链接正则
lmilive://live-room/share\?[^\s]+

# 认证相关
lmi-live-token
lmi_live_token
lmi_live_user_id
lmi_live_user_sig
lmi_live_im_account
lmi_device_id
```

## 结论：获取直播源的唯一路径

1. **修改版 APK + 本地代理（方案E）** — 改 libapp.so 的 API 地址到本地 HTTP 代理，拦截 `/app/live/info` 响应
2. **但即使拿到 TRTC 参数也无法用标准播放器播放** — TRTC 是专有 UDP 协议
3. **手机投屏（Scrcpy）是唯一可行方案** — 如果确实需要在电脑上看
