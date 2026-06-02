## mcporter smartsheet 写入注意事项（2026-05-29 验证）

- **批量 add_records 经常超时**（30s limit）→ 逐条添加（1条/次），timeout 设 60s
- **新 smartsheet 默认有 5 个字段**（单选/数字/日期/图片/文本）→ 先删除再添加自定义字段
- **字段用 field_name**（如 "KOL ID"），不用 field_id
- **creator_id 特殊字符** → 必须用 `shell_quote()` 包裹
- **VPN 会断** → 每次 NoxInfluencer 调用前检查，断了就 `scutil --nc start "Shadowrocket"`

## 完整 KOL 筛选 Skill

详见 `obsbot-kol-screening` skill（位于 `productivity/obsbot-kol-screening/`）。
