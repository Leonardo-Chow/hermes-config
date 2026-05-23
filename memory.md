# 持久化内存

## 系统状态
- **Hermes 版本**: v2026.5.7 (HEAD faa13e49f)
- **版本差距**: 846 commits behind v2026.5.16
- **技能数量**: 125+
- **内存状态**: 已初始化 (2026-05-17)

## 环境事实
- **操作系统**: macOS (zhoulong)
- **网络环境**: 中国大陆 GFW
- **代理工具**: Shadowrocket VPN v2.2.80 (主VPN)
- **备用代理**: v2rayN (端口 10808/10809), 0dcloud VPN, ClashX Pro (端口 7890)

## 核心方法论
- **钱学森工程控制论**: 系统思维、反馈控制、信息流通、层级结构、动态均衡、模型驱动、鲁棒性、最优解
- **数据分流规则**: 底层逻辑 → memory；操作细节 → skill；历史数据/参考资料 → IMA 知识库
- **复盘框架**: 输入→处理→输出→反馈→修正，形成闭环

## 关键约束
- **VPN 节点切换**: 不要乱切换节点，这是网络错误的根本原因
- **微博热搜 API**: 自 2026-05-12 起返回 Forbidden
- **Hermes 更新**: 需要运行 `hermes update` 更新到最新版本
- **hermes-retro CLI**: 未安装，需要手动从 session_search 生成复盘报告

## 常用命令
- **Shadowrocket 连接/断开**: `scutil --nc start/stop "Shadowrocket"`
- **IMA API 调用**: `node ~/.hermes/skills/ima-skills/ima_api.cjs`
- **微博热搜**: `node ~/.hermes/skills/ima-skills/scripts/weibo.js [数量] [--json]`
- **Reddit 热搜**: `node ~/.hermes/skills/ima-skills/scripts/reddit.js [数量] [--json]`

## 任务模板
- **摸鱼日报 v3.0**: 19 板块，数据源 30+ 个，总新闻条数 100+ 条
- **复盘报告**: 每日 11:00 cron job 自动生成，投递到飞书
- **数据收集**: 优先用 AutoCLI（快）和 Agent-Reach（全）

## 问题追踪
- 🔴 **持久化内存未初始化** → 已解决 (2026-05-17)
- 🔴 **hermes-retro CLI 未安装** → 待解决
- 🟡 **微博热搜 API 返回 Forbidden** → 待解决
- 🟡 **摸鱼日报图片质量 ~60%** → 待解决
- ⚠️ **Hermes 846 commits behind** → 待更新