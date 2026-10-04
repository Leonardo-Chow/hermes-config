---
name: cybernetics-review
description: 基于钱学森工程控制论的复盘框架。复盘时用控制论闭环（输入→处理→输出→反馈→修正）梳理经验。底层逻辑存 memory，操作细节存 skill。Hermes 首要标准。
tags: [review, cybernetics, qian-xuesen, retrospection, control-theory, primary-standard]
version: 1.2.0
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

### 标准模板（通用）

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

### 每日复盘专用模板（用户指定格式，含 6 维控制论分析）

```markdown
# 📋 每日复盘报告 — YYYY-MM-DD

## 🔐 1. 安全审查结果

| 检查项 | 结果 | 详情 |
|--------|------|------|
| 敏感信息扫描 | ✅/🔴 | 扫描结果 |
| 凭证存储 | ✅/🔴 | 存储位置安全性 |
| GitHub 仓库私有性 | ✅/🔴 | gh repo view 结果 |
| 最近提交检查 | ✅/🔴 | 无敏感泄露 |

## 📋 2. 任务执行总览（近期关键会话）

| 日期 | 会话 | 来源 | 核心任务 | 状态 |
|------|------|------|----------|------|
| YYYY-MM-DD | 会话名 | cli/cron | 任务描述 | ✅/🔄/❌ |

## 🔄 3. 钱学森工程控制论复盘分析

### 3.1 系统思维 — 整体视角

| 维度 | 输入 | 处理 | 输出 | 反馈 | 修正 |
|------|------|------|------|------|------|
| 系统名 | 输入源 | 处理流程 | 交付物 | 反馈机制 | 改进措施 |

### 3.2 反馈控制 — 执行质量闭环

| 任务 | 目标明确性 | 偏差检测 | 输出符合度 | 修正措施 |
|------|------------|----------|------------|----------|
| 任务名 | ✅/⚠️/❌ | ✅/⚠️/❌ | ✅/⚠️/❌ | 措施描述 |

### 3.3 信息流通 — 会话活动分析

- **Cron 会话**：数量、状态
- **人工会话**：高强度交互会话
- **关键成果**：列表
- **待办积压**：列表

### 3.4 层级结构 — 任务优先级分类

| 优先级 | 任务 | 状态 | 备注 |
|--------|------|------|------|
| 🔴 紧急且重要 | 任务 | 待计划/进行中/待确认 | 原因 |
| 🟡 重要不紧急 | 任务 | 状态 | 原因 |
| 🟢 日常任务 | 任务 | ✅/🔄 | 原因 |

### 3.5 动态均衡 — 资源使用

| 资源 | 状态 | 备注 |
|------|------|------|
| API 配额 | 正常/紧张/超限 | 详情 |
| VPN 稳定性 | 正常/不稳定/不可用 | 通道状态 |
| 工具链健康度 | 良好/部分故障/严重 | 故障项 |
| IMA API | 正常/异常 | 成功率 |

### 3.6 鲁棒性 — 系统韧性评估

| 维度 | 评估 | 措施 |
|------|------|------|
| 故障恢复 | 强/中/弱 | 措施 |
| 降级方案 | 完善/部分/缺失 | 详情 |
| 冗余配置 | 充足/部分/不足 | 详情 |
| 单点风险 | 存在/无 | 详情 |

## 📦 4. GitHub 同步状态

| 项目 | 状态 | 详情 |
|------|------|------|
| 本次提交 | ✅/❌ | commit hash |
| 变更文件 | N 个 | 核心文件列表 |
| 噪音文件 | ⚠️/无 | 误提交文件列表 |
| 代理配置 | ✅/❌ | socks5://... |

## ⚡ 5. 待办事项和建议

### 🔴 立即行动（今日/本周）
1. [任务1]
2. [任务2]

### 🟡 近期规划（本月）
1. [任务1]

### 🟢 持续优化
1. [任务1]

## 📊 6. 关键指标快照

| 指标 | 数值 |
|------|------|
| Hermes 版本 | vX.Y.Z (YYYY.M.D) |
| 落后 commits | N |
| 技能总数 | N（M 分类） |
| Cron 任务 | N 个（M 活跃） |
| IMA 知识库条目 | 条目数 |
| 最近会话总数 | N+ |
| Git 仓库状态 | Public/Private ⚠️、working tree 状态 |
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
1. **安全审查（最优先）** — 扫描敏感信息、检查仓库隐私状态。**检查 macOS 元数据污染（`__MACOSX/`、`._*`、`.history/`、`*.zip`）**。详见 `references/security-audit-workflow.md`
2. **session_search** — 补充复盘上下文，获取今日会话详情（替代已废弃的 `hermes-retro`）
3. **Hermes 更新检测** — `hermes --version`（最快，无需网络）优先；落后时再用 `git fetch origin main` + `git log HEAD..origin/main --oneline` 精确计数
4. **子模块健康检查** — `cd ~/.hermes/hermes-agent && git status && git log HEAD..origin/main --oneline | wc -l` 检查落后程度与本地脏状态
5. **Git 仓库清理** — 若发现 macOS 元数据文件被跟踪，执行清理并更新 `.gitignore`：
   ```bash
   git rm -r --cached skills/__MACOSX/ skills/**/.history/ skills/*.zip
   # 确保 .gitignore 包含：__MACOSX/ _.* .history/ *.zip
   git add .gitignore && git commit -m "chore: remove macOS metadata from tracking"
   ```
6. **IMA 记忆同步** — 读取 `~/.hermes/memory.md` + `~/.hermes/user.md` + `~/.hermes/memory/` 下文件，用 `import_doc` 创建笔记，再 `add_knowledge` 到 Herme记忆库。**需注入代理**：`https_proxy=http://127.0.0.1:1082 node ima_api.cjs ...`
7. **数据分流** — 底层逻辑→memory，操作细节→skill，历史数据→IMA
   - ⚠️ **Cron Job 限制**：`memory` 工具不可用，Memory→IMA 同步需在人工会话中补做
   - ⚠️ **VPN 限制**：GitHub 操作需用户手动开启 VPN，代理不可用时直连重试
   - ⚠️ **IMA 代理限制**：GFW 环境下 IMA API 调用必须显式注入 https_proxy

### ⚠️ Cron Job 环境限制
- **`memory` 工具不可用** — cron job 中无法调用 `memory(action='add/replace')`，需在报告中注明待下次会话更新
- **`skill_manage` 可用** — 可以在 cron 中 patch/create skills
- **VPN 由用户手动开启** — git fetch 等 GitHub 操作需要用户先开启 VPN，**Cron 运行时 VPN 工具（Shadowrocket/v2rayN/ClashX）均未运行**，代理端口不可用
- **IMA API 需显式代理** — GFW 环境下 `node ima_api.cjs` 调用必须注入 `https_proxy=http://127.0.0.1:1082`（或当前可用代理端口），否则返回 `fetch failed`。建议在调用前检测代理可用性
- **`hermes --version` 优于 git fetch** — 版本检测最快，无需网络，优先使用；落后大量 commits 时再用 `git log HEAD..origin/main --oneline | wc -l` 精确计数
- **Cron 代理端口不可靠** — SOCKS5 1082/10808/7890 端口在 cron 环境下**不可用**，直连 GitHub 超时（60s）。GitHub push **必须**在人工会话中由用户开启 VPN 后补推

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

## 持续性安全发现（每次复盘必检）

以下问题在多次复盘中反复出现，修复前每次必须标记：

| 发现 | 首次发现 | 风险 | 状态 | 修复命令 |
|:-----|:---------|:----:|:-----|:---------|
| GitHub 仓库为 PUBLIC | 2026-06-18 | 🔴 高 | ⚠️ 未修复 (2026-10-02 复盘确认仍为 Public) | `gh repo edit Leonardo-Chow/hermes-config --visibility private` |

> 当问题修复后，从本表移除并记录到 memory。

## 持续性维护发现（每次复盘关注）

以下非安全类问题长期存在，需定期评估优先级：

| 发现 | 首次发现 | 影响 | 状态 | 处理建议 |
|:-----|:---------|:----:|:-----|:---------|
| hermes-agent 子模块严重滞后 (16k+ commits) | 2026-09-09 | 🟠 中 | ⚠️ 未处理 (2026-10-03 确认落后 16285 commits) | 规划 `hermes update` 维护窗口，备份配置后执行 |
| hermes-agent 子模块本地脏状态 (未提交变更) | 2026-09-11 | 🟡 低 | ⚠️ 未处理 | 确认 `flake.lock` 删除、`web_server.py` 修改、`feishu_attempt.py` 新增是否需保留/上游同步 |
| macOS 元数据文件污染 git 仓库 | 2026-09-26 | 🟡 低 | 🔄 反复出现 | `.gitignore` 已补全；每次复盘执行 `git ls-files \| grep -E '__MACOSX\|_history\|\.zip$'` 检查 |

> 维护发现不阻塞复盘，但需在复盘报告中明确记录，避免长期累积技术债。

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
- `references/session-search-daily-review.md` — session_search 每日复盘使用模式（发现会话、提取闭环、Cron Job 适配）
