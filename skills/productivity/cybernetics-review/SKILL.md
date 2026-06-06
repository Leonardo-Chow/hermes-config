---
name: cybernetics-review
description: 基于钱学森工程控制论的复盘框架。复盘时用控制论闭环（输入→处理→输出→反馈→修正）梳理经验。底层逻辑存 memory，操作细节存 skill。Hermes 首要标准。
tags: [review, cybernetics, qian-xuesen, retrospection, control-theory, primary-standard]
version: 1.1.0
---

# 控制论复盘框架 (Cybernetics Review Framework)

## 触发条件
- 每日 11:00 自动复盘
- 完成复杂任务后（5+ tool calls）
- 遇到错误/失败后的即时复盘
- 用户要求复盘/总结时

## 核心原则（钱学森工程控制论）

### 八大准则
1. **系统思维** — 一切皆系统，从整体出发分析
2. **反馈控制** — 每次执行必须有反馈回路
3. **信息流通** — 确保信息链路完整无断点
4. **层级结构** — 任务拆解时保持层级清晰
5. **动态均衡** — 通过持续调整寻求平衡
6. **模型驱动** — 先建模再行动
7. **鲁棒性** — 通过冗余和适应性构建韧性
8. **最优解** — 在约束条件下寻找最优

## 复盘流程（控制闭环）

### Step 1: 输入分析 (Input Analysis)
```
问题：任务的初始条件是什么？
- 目标明确度：是否清晰？
- 资源充足度：工具、信息、权限是否具备？
- 环境约束：网络、平台、时间限制？
```

### Step 2: 处理过程 (Process Analysis)
```
问题：执行路径是否最优？
- 决策点：哪些关键决策影响了结果？
- 路径选择：是否尝试了多条路径？
- 瓶颈识别：哪里卡住了？为什么？
```

### Step 3: 输出评估 (Output Evaluation)
```
问题：结果是否符合预期？
- 目标达成度：完成了多少？
- 质量评估：输出质量如何？
- 效率评估：时间/资源消耗是否合理？
```

### Step 4: 反馈回路 (Feedback Loop)
```
问题：哪里可以改进？
- 正反馈：哪些做法应该坚持？
- 负反馈：哪些做法应该停止？
- 新发现：学到了什么新知识/方法？
```

### Step 5: 修正方案 (Correction)
```
问题：下次如何做得更好？
- 流程优化：步骤可以简化/合并吗？
- 工具升级：有更好的工具/方法吗？
- 知识补充：需要学习什么新知识？
```

## 经验分类规则

### → 存入 Memory（底层逻辑）
- **用户偏好**：用户喜欢/不喜欢什么
- **环境事实**：系统配置、工具特性、平台限制
- **核心方法论**：可复用的思维模型
- **关键约束**：不会随时间变化的限制条件

示例：
```
memory add: 用户要求任务完成后必须汇报，不能默默做完。
memory add: 经济人网站有付费墙，archive.today 有 CAPTCHA。
memory add: 控制论核心：系统思维+反馈控制+信息流通。
```

### → 存入 Skill（操作细节）
- **操作流程**：具体的步骤和命令
- **工具用法**：特定工具的使用技巧
- **错误处理**：遇到特定错误的解决方案
- **模板/脚本**：可复用的代码/模板

示例：
```
skill create: economist-scraping — 如何绕过经济学人付费墙的完整流程
skill patch: moyu-daily-generator — 新增控制论复盘步骤
skill patch: autocli — 更新可用站点列表
```

### → 存入 IMA 知识库（长期归档）
- **历史数据**：过去的日报、报告
- **参考资料**：文档、论文、教程
- **备份**：重要的 skill/memory 快照

## 复盘报告模板

```markdown
## 📋 控制论复盘报告 — [日期/任务名]

### 🔄 控制闭环

| 环节 | 状态 | 说明 |
|:-----|:-----|:-----|
| 输入 | ✅/⚠️/❌ | 初始条件是否充分 |
| 处理 | ✅/⚠️/❌ | 执行路径是否最优 |
| 输出 | ✅/⚠️/❌ | 结果是否符合预期 |
| 反馈 | ✅/⚠️/❌ | 反馈回路是否闭合 |
| 修正 | ✅/⚠️/❌ | 改进方案是否明确 |

### 📊 关键指标
- 任务完成率：X%
- 工具调用次数：N 次
- 错误/重试次数：M 次
- 耗时：T 分钟

### 💡 底层逻辑（→ Memory）
- [发现1]
- [发现2]

### 🔧 操作优化（→ Skill）
- [优化1]
- [优化2]

### 📝 下一步行动
- [ ] [行动1]
- [ ] [行动2]
```

## Skill 梳理规则（按控制论）

复盘时，将所有 skill 按控制论框架分类：

### 1. 输入类 Skills（数据获取）
- `autocli` — 快速数据获取
- `agent-reach` — 多渠道数据获取
- `bb-browser` — 登录态数据获取
- `camoufox` — 反检测数据获取

### 2. 处理类 Skills（数据分析/转换）
- `moyu-daily-generator` — 日报生成
- `cybernetics-review` — 控制论复盘
- 各种数据分析/处理 skill

### 3. 输出类 Skills（内容发布）
- `ima-skill` — 知识库存储
- 各种导出/发布 skill

### 4. 反馈类 Skills（监控/评估）
- `daily-digest` — 每日摘要
- 各种监控/评估 skill

### 5. 修正类 Skills（优化/改进）
- 各种调试/优化 skill
- 各种配置/设置 skill

## 每日自动复盘工作流（Cron Job）

### 触发
- Cron Job ID: `22b9ed16db32`（每天 11:00）
- 涉及 skill: `ima-skill`（IMA 记忆同步）、`hermes-agent`（更新检测）

### 执行步骤
1. **安全审查（最优先）** — 扫描敏感信息、检查仓库隐私状态。详见 `references/security-audit-workflow.md`
2. **运行 hermes-retro** — 脚本路径: `~/.hermes/audit/hermes-retro`（bash 脚本，非 npm 包）
   ```bash
   bash ~/.hermes/audit/hermes-retro --today
   ```
2. **session_search** — 补充复盘上下文，获取今日会话详情
3. **Memory 同步到 IMA** — 读取 `~/.hermes/memory.md` + `~/.hermes/user.md` + `~/.hermes/memory/` 下文件，用 `import_doc` 创建笔记，再 `add_knowledge` 到 Herme记忆库（`uhcEva4nd2xus1Q2yt7yn_N4_waEdOsQlVU3lhnkLXw=`）
4. **Hermes 更新检测** — `git fetch origin main` + `git log HEAD..origin/main --oneline`
5. **数据分流** — 底层逻辑→memory，操作细节→skill，历史数据→IMA

### ⚠️ Cron Job 环境限制
- **`memory` 工具不可用** — cron job 中无法调用 `memory(action='add/replace')`，需在报告中注明待下次会话更新
- **`skill_manage` 可用** — 可以在 cron 中 patch/create skills
- **VPN 由用户手动开启** — git fetch 等 GitHub 操作需要用户先开启 VPN

### 数据分流规则
| 类型 | 目标 | 示例 |
|------|------|------|
| 底层逻辑 | memory.md / user.md | 用户偏好、环境事实、方法论 |
| 操作细节 | skill (skill_manage) | 工具用法、错误处理、工作流 |
| 历史数据 | IMA 知识库 | 日报、复盘报告、记忆快照 |

### Memory 清理方法论
当 memory 使用率超过 70% 时，执行四步清理法：
1. **删除重复** — 检查高度相似条目，保留最完整的一份
2. **删除过时** — 已禁用 cron job、已修复问题、已卸载工具
3. **迁移操作细节** — 检查是否已在 skill 中，是则删除 memory 条目
4. **精简冗长** — 引用 skill 的条目压缩为 "详见 xxx skill"

详见 `references/memory-cleanup-methodology.md`

## 注意事项
1. **闭环优先**：每次复盘必须形成闭环，不能只分析不修正
2. **底层优先**：先提取底层逻辑存 memory，再存操作细节到 skill
3. **层级清晰**：skill 分类按控制论层级，不要混杂
4. **动态更新**：每次复盘后更新相关 skill，保持技能库鲜活
5. **VPN 由用户管理**：涉及 GitHub 操作时，如需 VPN 提示用户手动开启

## 参考资料

- `references/security-audit-workflow.md` — 每日安全审查流程（敏感信息扫描、仓库检查、泄露处理）
- `references/qian-xuesen-cybernetics.md` — 钱学森工程控制论核心理论详解
- `references/pdf-generation-template.md` — 新闻风格 PDF 生成模板（CNN/BBC/经济学人）
- `references/ima-memory-sync.md` — Memory 文件同步到 IMA Herme记忆库的完整流程
- `references/memory-cleanup-methodology.md` — Memory 清理方法论（四步清理法、操作陷阱、检查清单）
