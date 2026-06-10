## mcporter smartsheet 写入注意事项（2026-05-29 验证）

- **批量 add_records 经常超时**（30s limit）→ 逐条添加（1条/次），timeout 设 60s
- **新 smartsheet 默认有 5 个字段**（单选/数字/日期/图片/文本）→ 先删除再添加自定义字段
- **字段用 field_name**（如 "KOL ID"），不用 field_id
- **creator_id 特殊字符** → 必须用 `shell_quote()` 包裹
- **mcporter list_tables 有时失败** → 直接用 `sheet_id="t00i2h"`，跳过 list_tables 调用
- **mcporter move_file 超时** → timeout 设 60s

## VPN 稳定性模式（2026-06-09 验证）

NoxInfluencer API 需要 VPN，但 VPN 在长任务中会断连。最佳实践：

1. **搜索阶段**：每个品类搜索之间重连 VPN（`scutil --nc start "Shadowrocket"` + `sleep 2`）
2. **Profile 获取**：每 10 个 profile 后重连 VPN
3. **YouTube API 验证**：每 15 个频道后重连 VPN
4. **mcporter 写入**：不需要 VPN（腾讯文档在国内），但需要 mcporter auth 有效
5. **VPN 断连症状**：NoxInfluencer 返回 HTTP 403 / YouTube API 返回空 / mcporter 返回空 JSON

## 完整 KOL 筛选 Skill

详见 `obsbot-kol-screening` skill（位于 `productivity/obsbot-kol-screening/`）。
