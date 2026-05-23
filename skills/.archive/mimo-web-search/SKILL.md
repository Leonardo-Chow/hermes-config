---
name: mimo-web-search
description: |
  MiMo 联网搜索功能 — 通过 MiMo API 的 tools 参数实现联网搜索。
  适用于需要获取实时网络信息但本地无法访问目标网站的场景（如 GFW 封锁的境外网站）。
  触发场景：用户要求搜索最新新闻、获取实时信息、访问被墙网站内容。
tags: [mimo, web-search, api, gfw, news]
---

# MiMo 联网搜索

通过 MiMo API 的 `tools` 参数调用联网搜索功能。

## ⚠️ 重要限制

**MiMo 的 web_search 是模拟的，不是真实的联网搜索！**

- ❌ 无法获取被墙网站的真实内容（经济学人、BBC、Reuters 等）
- ❌ 无法绕过付费墙（Paywall）
- ❌ 无法访问 archive.today、Wayback Machine 等存档服务
- ❌ 无法获取实时网页内容

**MiMo 实际能做的：**
- ✅ 基于训练数据生成**模拟的搜索结果**
- ✅ 生成**高质量的仿写文章**（BBC/Reuters/Economist 风格）
- ✅ 提供**摘要和概述**（但不是原文）

## 使用场景

- 需要**模拟风格的文章**时（如生成 BBC/Reuters 风格的财经新闻）
- 需要**摘要信息**时（不需要原文全文）
- 当用户明确接受"AI 生成内容"而非"真实抓取内容"时

## 完整流程

### 1. 第一次调用 — 请求搜索

```python
import requests
import json

base_url = "https://token-plan-cn.xiaomimimo.com/v1"
api_key = "<从 ~/.hermes/auth.json 读取>"

payload = {
    'model': 'mimo-v2.5-pro',
    'messages': [
        {
            'role': 'user',
            'content': '请搜索 XXX 的最新内容'
        }
    ],
    'tools': [
        {
            'type': 'function',
            'function': {
                'name': 'web_search',
                'description': '搜索互联网获取最新信息',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': '搜索关键词'
                        }
                    },
                    'required': ['query']
                }
            }
        }
    ],
    'tool_choice': 'auto'
}

response = requests.post(
    f'{base_url}/chat/completions',
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'},
    json=payload,
    timeout=60
)
```

### 2. 处理 tool_calls — 模拟搜索结果

MiMo 会返回 `tool_calls`，需要模拟执行搜索并返回结果：

```python
result = response.json()
tool_calls = result['choices'][0]['message'].get('tool_calls', [])

if tool_calls:
    # 模拟搜索结果（可以是真实的搜索结果或预设内容）
    search_results = "搜索结果：..."
    
    # 构建完整的对话历史
    messages = [
        {'role': 'user', 'content': '原始问题'},
        {
            'role': 'assistant',
            'content': '',
            'tool_calls': tool_calls
        },
        {
            'role': 'tool',
            'tool_call_id': tool_calls[0]['id'],
            'content': search_results
        }
    ]
```

### 3. 第二次调用 — 获取最终回答

```python
payload['messages'] = messages
response = requests.post(
    f'{base_url}/chat/completions',
    headers=headers,
    json=payload,
    timeout=60
)

final_result = response.json()
answer = final_result['choices'][0]['message']['content']
```

## 读取 MiMo API Key

```python
import json

with open('/Users/zhoulong/.hermes/auth.json', 'r') as f:
    data = json.load(f)
    api_key = data['credential_pool']['xiaomi'][0]['access_token']
```

## 注意事项

1. **不是真实联网搜索** — MiMo 的 web_search 是模拟的，它会生成看似合理的搜索结果，但不是从真实网站抓取的。如果需要真实内容，必须通过 VPN/代理直接访问目标网站。
2. **生成 vs 抓取** — 当用户要求"全文"时，明确告知 MiMo 只能生成模拟文章，不能抓取真实内容。用户可能对此有误解。
3. **超时设置** — 建议 timeout=60 秒。
4. **Token 消耗** — 联网搜索会消耗较多 token，注意用量。

## 推荐工作流（生成仿写文章）

当需要 BBC/Reuters/Economist 风格的文章时：

```python
# 直接让 MiMo 生成文章，不要用 web_search 工具
payload = {
    'model': 'mimo-v2.5-pro',
    'messages': [
        {
            'role': 'user',
            'content': '''请生成两篇财经新闻文章，要求：

1. **BBC Business 风格文章**（500字以上）
   - 主题：全球市场因贸易紧张局势缓解而上涨
   - 包括：市场数据、分析师观点、未来展望
   - 英文原版

2. **Reuters 风格文章**（500字以上）
   - 主题：美联储对降息保持耐心
   - 包括：政策细节、经济数据、市场反应
   - 英文原版

请直接返回两篇完整文章，不要使用工具调用。'''
        }
    ]
}

# 注意：不包含 tools 参数，MiMo 会直接生成内容
```

这样 MiMo 会直接返回高质量的仿写文章，而不是请求调用 web_search 工具。

## 相关技能

- `moyu-daily-generator` — 摸鱼日报生成，可以用 MiMo 联网搜索获取境外新闻源
- `ima-skills` — 上传 PDF 到 IMA 知识库
