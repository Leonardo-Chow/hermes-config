# 封面图片降级方案

当 IMA API 认证失败（code 200002）无法获取签名 URL 时，使用以下降级方案：

## 方案 1：Placeholder 服务（推荐）

使用 [placehold.co](https://placehold.co) 生成临时封面：

```markdown
![摸鱼日报](https://placehold.co/1200x630/1a1a2e/16213e?text=摸鱼日报+YYYY-MM-DD)
```

**参数说明**：
- `1200x630`：尺寸（适合社交媒体分享）
- `1a1a2e`：背景色（深蓝黑色）
- `16213e`：文字色（深蓝色）
- `text=摸鱼日报+YYYY-MM-DD`：显示文字

**优点**：
- 无需认证，随时可用
- 自动生成，无需手动操作
- 尺寸和颜色可自定义

**缺点**：
- 不是真实封面图片
- 质量评分会扣 10 分（封面图片项）

## 方案 2：Unsplash 随机图片

使用 Unsplash 的随机图片 API：

```markdown
![摸鱼日报](https://source.unsplash.com/1200x630/?news,technology)
```

**优点**：
- 真实图片，质量高
- 无需认证

**缺点**：
- 图片内容不可控
- 可能加载缓慢

## 方案 3：本地默认图片

如果本地有默认封面图片，可直接使用：

```markdown
![摸鱼日报](/path/to/default_cover.png)
```

**优点**：
- 完全可控
- 加载快速

**缺点**：
- 需要预先准备
- 不同日期使用相同封面

## 质量评分影响

根据质量评分标准，封面图片占 10 分：
- ✅ 有封面图片（IMA 签名 URL）：10 分
- ⚠️ 使用 Placeholder：0 分（但仍可上传）
- ❌ 无封面图片：0 分

**建议**：当 IMA API 认证失败时，使用 Placeholder 方案确保日报可正常生成和上传，同时记录问题以便后续修复。

## 修复 IMA 认证

如果需要恢复 IMA 签名 URL 功能：

1. 检查凭证文件：
   ```bash
   cat ~/.config/ima/client_id
   cat ~/.config/ima/api_key
   ```

2. 测试 API 连通性：
   ```bash
   cd ~/.hermes/skills/ima-skills
   node ima_api.cjs "openapi/check_skill_update" '{"version":"1.0.0"}'
   ```

3. 如果返回 200002，联系 IMA 管理员检查：
   - API Key 是否过期
   - 应用权限是否被撤销
   - 服务端配置是否正常
