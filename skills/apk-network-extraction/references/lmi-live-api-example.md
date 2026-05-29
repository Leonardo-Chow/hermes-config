# LMI Live API 参考（实战案例）

## 基础信息

| 项目 | 值 |
|------|-----|
| 包名 | `com.lmi.live` |
| 域名 | `lmilive.lmizhibo.com` |
| IP | `81.71.248.163` |
| 认证 Header | `lmi-live-token: <token>` |
| 框架 | Flutter + Tencent TRTC (liteavSDK) |
| 流协议 | 腾讯云 TRTC（非标准 RTMP/HLS） |

## 已发现的 API 端点

### 直播相关

| 端点 | Method | 作用 |
|------|--------|------|
| `/app/live/info` | GET | 直播间信息（推测含流地址） |
| `/app/live/join` | POST | 加入直播间 |
| `/app/live/heartbeat` | POST | 心跳保活 |
| `/app/live/leave` | POST | 离开直播间 |
| `/app/live/summary/info` | GET | 直播摘要信息 |
| `/app/live/categoryList` | GET | 直播分类列表 |
| `/app/live/pageList` | GET | 直播列表 |
| `/app/live/start` | POST | 开始直播（主播） |
| `/app/live/stop` | POST | 结束直播（主播） |

### 门票系统

| 端点 | 作用 |
|------|------|
| `/app/live/ticket/my` | 查询我的门票 |
| `/app/live/ticket/buy` | 购票 |
| `/app/live/ticket/verify` | 验票 |
| `/app/live/ticket/config` | 门票配置 |
| `/app/live/ticket/preset/query` | 预设查询 |
| `/app/live/ticket/save` | 门票保存 |

### 用户系统

| 端点 | 作用 |
|------|------|
| `/app/user/email/login` | 邮箱登录 |
| `/app/user/publicProfile` | 用户公开信息 |
| `/app/user/block` | 用户拉黑 |
| `/app/user/blockList` | 黑名单 |

### 其他

| 端点 | 作用 |
|------|------|
| `/app/follow/save` | 关注 |
| `/app/earning/balance/info` | 余额信息 |
| `/app/config/switches` | 配置开关 |
| `/app/roomadmin/save` | 房间管理员 |
| `/app/roomadmin/list` | 管理员列表 |
| `/app/effect/backpack/pageList` | 特效背包 |

## 认证响应示例

```json
{
  "code": 401,
  "msg": "未能读取到有效 token",
  "data": null,
  "status": {
    "code": "UNAUTHOR",
    "msg": "未登录",
    "bizCode": 401
  },
  "isSuccess": false
}
```

## 已知 Depth 逻辑函数（Flutter libapp.so）

- `_hasOwnedRoomTicket@...` — 门票检测
- `_buildTicketRequiredOverlay@...` — 门票弹窗
- `viewerPushUrl` — 观众推流地址
- `pushUrl` — 推流地址

## 直播间信息

- 房间号（显示）: 55555
- 房间号（内部）: 1410
- 主播: 户外小龙
- Deeplink: `lmilive://live-room/share?liveRoomId=1410&roomDisplayId=55555`
