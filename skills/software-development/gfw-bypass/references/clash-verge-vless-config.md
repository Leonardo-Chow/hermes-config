# Clash Verge — 添加 VLESS 节点配置

## 配置文件位置

```
~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml
```

## VLESS + XTLS-Vision 节点格式（无 Reality）

```yaml
- name: 🇺🇸节点名称
  type: vless
  server: example.com
  port: 443
  uuid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  udp: true
  tls: true
  skip-cert-verify: false
  flow: xtls-rprx-vision
  client-fingerprint: chrome
  servername: example.com      # SNI，通常与 server 相同
  network: tcp
```

## VLESS + XTLS-Vision + Reality 节点格式

```yaml
- name: 🇭🇰节点名称
  type: vless
  server: example.com
  port: 443
  uuid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  udp: true
  tls: true
  skip-cert-verify: false
  flow: xtls-rprx-vision
  client-fingerprint: chrome
  servername: www.apple.com    # Reality 的 SNI 伪装域名（与 server 不同）
  reality-opts:
    public-key: BASE64_PUBLIC_KEY
    short-id: HEX_SHORT_ID
```

## 添加节点到配置文件的正确方法

### ✅ 正确：使用 Python（推荐）

```python
import re

config_file = "path/to/clash-verge.yaml"

with open(config_file, 'r') as f:
    content = f.read()

new_node = """- name: 🇺🇸新节点名称
  type: vless
  server: example.com
  port: 443
  uuid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  udp: true
  tls: true
  skip-cert-verify: false
  flow: xtls-rprx-vision
  client-fingerprint: chrome
  servername: example.com
  network: tcp
"""

# 1. 添加到 proxies 列表（在第一个节点前插入）
if "新节点名称" not in content:
    proxies_pos = content.find("proxies:")
    if proxies_pos != -1:
        after_proxies = content[proxies_pos:]
        first_node_pos = after_proxies.find("\n- name:")
        if first_node_pos != -1:
            insert_at = proxies_pos + first_node_pos + 1
            content = content[:insert_at] + new_node + content[insert_at:]

# 2. 添加到代理组（如"良心云"、"自动选择"）
group_pattern = r'(- name: 良心云\n  type: select\n  proxies:\n)'
group_match = re.search(group_pattern, content)
if group_match and "新节点名称" not in content[group_match.end():group_match.end()+200]:
    insert_pos = group_match.end()
    content = content[:insert_pos] + "  - 🇺🇸新节点名称\n" + content[insert_pos:]

with open(config_file, 'w') as f:
    f.write(content)
```

### ❌ 错误：使用 sed

**绝对不要用 sed 编辑 Clash Verge 的 YAML 配置文件！**

sed 处理含 Unicode（emoji）和多行 YAML 的文件时会：
- 破坏缩进结构
- 重复插入内容（数百行重复）
- 生成无效 YAML

真实案例（2026-05-16）：用 sed 添加一个节点引用，导致配置文件从 29KB 膨胀到 200KB+，数百行重复引用。必须从备份恢复。

## 添加节点的完整步骤

1. **备份配置**
   ```bash
   CONFIG=~/Library/Application\ Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml
   cp "$CONFIG" "$CONFIG.$(date +%Y%m%d%H%M%S).bak"
   ```

2. **用 Python 添加节点**（见上方代码）

3. **验证配置**
   ```bash
   # 检查节点定义存在
   grep "name: 🇺🇸新节点名称" "$CONFIG"
   # 检查代理组引用
   grep "  - 🇺🇸新节点名称" "$CONFIG"
   ```

4. **重启 Clash Verge 加载配置**
   ```bash
   open -a "Clash Verge"
   # 然后在 GUI 中点击 配置 → 重载配置
   ```

5. **测试连接**
   ```bash
   curl -x http://127.0.0.1:7897 -s --max-time 10 "https://www.google.com" | wc -c
   ```

## vless:// 链接解析

vless:// 格式：
```
vless://UUID@SERVER:PORT?encryption=none&flow=xtls-rprx-vision&security=tls&sni=SNI&fp=chrome&type=tcp&host=HOST#NAME
```

| 参数 | 说明 | Clash 字段 |
|------|------|-----------|
| UUID | 用户标识 | `uuid` |
| SERVER | 服务器地址 | `server` |
| PORT | 端口 | `port` |
| flow | 流控类型 | `flow` |
| security | 传输安全 | `tls: true` |
| sni | TLS SNI | `servername` |
| fp | 指纹 | `client-fingerprint` |
| type | 传输协议 | `network` |
| host | 主机头 | 通常与 sni 相同 |

## Pitfalls

1. **永远不要用 sed 编辑含 emoji 的 YAML** — 用 Python 或 YAML 库
2. **先备份再修改** — 配置文件损坏会导致所有代理不可用
3. **Reality 和普通 TLS 的区别** — Reality 有 `reality-opts`（public-key + short-id），普通 TLS 没有
4. **servername vs server** — Reality 节点的 servername（伪装 SNI）通常与 server 不同；普通 TLS 节点通常相同
5. **代理组必须手动添加引用** — 只在 proxies 部分添加节点不会自动出现在代理组中
