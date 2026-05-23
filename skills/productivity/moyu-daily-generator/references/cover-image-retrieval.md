# 封面图片获取流程

## 获取签名 URL

封面图片存储在 IMA 知识库中，COS 签名 URL 会过期，每次生成日报时需重新获取。

```python
import json, subprocess

skill_dir = "/Users/zhoulong/.hermes/skills/ima-skills"
media_id = "img_804ad0c79724fcebb6bc3d08062b3588_c7ac315e6d0c84f26b1c25ca4c771cc87454811872052525"

payload = json.dumps({"media_id": media_id}, ensure_ascii=False)
result = subprocess.run(
    ['node', 'ima_api.cjs', 'openapi/wiki/v1/get_media_info', payload],
    cwd=skill_dir, capture_output=True, text=True, timeout=30
)
resp = json.loads(result.stdout)
cover_url = resp['data']['url_info']['url']

# 日报顶部使用：
# ![摸鱼日报](cover_url)
```

## 注意事项

- **每次生成日报必须重新获取**，签名 URL 有效期有限
- API 路径是 `openapi/wiki/v1/get_media_info`（不是 note/v1）
- media_id 固定不变，存在 memory 中
- 获取失败时检查 IMA API 凭证（~/.config/ima/）

## 验证图片可访问

获取 URL 后可用 curl 验证：
```bash
curl -sI "$COVER_URL" | head -5
# 应返回 HTTP 200
```
