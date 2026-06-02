# BBC 新闻抓取脚本（Scrapling）

## 使用方法

```bash
# 激活 Scrapling 虚拟环境
source ~/.hermes/skills/scrapling/venv/bin/activate

# 抓取 BBC News（默认 10 条）
python3 ~/.hermes/skills/ima-skills/scripts/bbc_scraper.py

# 抓取指定数量
python3 ~/.hermes/skills/ima-skills/scripts/bbc_scraper.py --limit 15

# 保存到 JSON 文件
python3 ~/.hermes/skills/ima-skills/scripts/bbc_scraper.py --limit 10 --output /tmp/bbc_news.json
```

## 前提条件

1. **VPN 必须连接**：BBC 被 GFW 封锁
   ```bash
   用户先手动开启 VPN（Shadowrocket）
   ```

2. **Scrapling 虚拟环境**：Python 3.12 venv
   ```bash
   /opt/homebrew/bin/python3.12 -m venv ~/.hermes/skills/scrapling/venv
   source ~/.hermes/skills/scrapling/venv/bin/activate
   pip install "scrapling[all]"
   scrapling install
   ```

## 技术细节

- 使用 `DynamicFetcher`（不是 `StealthyFetcher`）
- `disable_resources=True` 禁用资源加载，加快速度
- `network_idle=True` 等待网络空闲
- BBC 没有 Cloudflare 保护，不需要 `solve_cloudflare`

## 输出格式

```json
[
  {
    "rank": 1,
    "title": "News Title",
    "link": "https://www.bbc.com/news/articles/xxx"
  }
]
```

## 已知问题

- VPN 断开时会超时
- 页面结构变化可能需要调整 CSS 选择器
- 首次运行需要安装浏览器（`scrapling install`）
