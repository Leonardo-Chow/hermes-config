# Hermes Agent Configuration

Leonardo 的 AI 助手配置仓库，运行在 [Hermes Agent](https://hermes-agent.nousresearch.com) 上。

## 📁 目录结构

```
hermes-config/
├── config.yaml          # 主配置文件（已脱敏）
├── SOUL.md              # AI 人格定义
├── user.md              # 用户画像
├── memory.md            # 长期记忆
├── skills/              # 135+ 技能文件
│   ├── apple/           # Apple 生态技能
│   ├── creative/        # 创意设计技能
│   ├── data-science/    # 数据科学技能
│   ├── devops/          # 运维技能
│   ├── productivity/    # 效率工具技能
│   ├── research/        # 研究技能
│   ├── software-development/  # 开发技能
│   └── ...              # 更多分类
├── audit/               # 审计工具
├── bin/                 # 可执行脚本
└── scripts/             # 辅助脚本
```

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/Leonardo-Chow/hermes-config.git ~/.hermes

# 安装依赖
cd ~/.hermes
pip install -r requirements.txt  # 如果有的话

# 配置 API keys
cp .env.example .env  # 然后编辑 .env 填入你的 API keys
```

## 🔧 配置说明

### 必需的 API Keys

在 `~/.hermes/.env` 中配置：

```bash
# AI 模型
XIAOMI_API_KEY=your_xiaomi_api_key

# 搜索工具
TAVILY_API_KEY=your_tavily_api_key

# GitHub（可选）
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token

# 腾讯文档（可位选）
TENCENT_DOC_API_KEY=your_tencent_doc_key
```

### 可选配置

- **代理设置**：在 `config.yaml` 的 `network` 部分配置
- **TTS 语音**：在 `config.yaml` 的 `tts` 部分配置
- **技能目录**：在 `config.yaml` 的 `skills` 部分配置

## 📚 技能列表

### 核心技能（已激活）

| 技能 | 分类 | 说明 |
|------|------|------|
| moyu-daily-generator | productivity | 摸鱼日报生成器 |
| tencent-docs | productivity | 腾讯文档操作 |
| youtube-full | media | YouTube 数据采集 |
| obsbot-competitive-analysis | productivity | OBSBOT 竞品分析 |
| tavily-python | software-development | Tavily 搜索工具 |
| guizang-ppt-skill | creative | 杂志风 PPT 生成 |
| ima-skill | ima-skills | IMA 知识库操作 |

### 技能分类

- **apple** (5)：iMessage、Reminders、Notes、FindMy、macOS 自动化
- **creative** (25)：ASCII 艺术、图表、设计、视频、音乐
- **data-science** (1)：Jupyter 内核
- **devops** (3)：Kanban、Webhook、定时任务
- **media** (5)：YouTube、GIF、音乐、音频
- **mlops** (15)：模型训练、推理、评估
- **productivity** (15)：文档、表格、报告、分析
- **research** (10)：论文、市场、YouTube 研究
- **software-development** (20)：开发、调试、测试、部署

## 🔒 安全说明

- ✅ 所有 API keys 已从仓库中移除
- ✅ 使用 `.gitignore` 排除敏感文件
- ✅ 会话数据、缓存、日志已排除
- ✅ 大文件（260MB+）已排除

### 需要手动配置的文件

1. **`.env`**：所有 API keys 和 secrets
2. **`auth.json`**：认证信息
3. **`sessions/`**：会话历史（自动生成）
4. **`state.db`**：状态数据库（自动生成）

## 🛠️ 维护

### 更新技能

```bash
cd ~/.hermes
git pull origin main

# 或者手动更新单个技能
hermes skills update <skill-name>
```

### 备份配置

```bash
# 备份当前配置
cp config.yaml config.yaml.backup.$(date +%Y%m%d)

# 提交更改
git add -A
git commit -m "Update config: $(date +%Y-%m-%d)"
git push origin main
```

## 📖 相关文档

- [Hermes Agent 官方文档](https://hermes-agent.nousresearch.com/docs)
- [GitHub 仓库](https://github.com/Leonardo-Chow/hermes-config)
- [IMA 知识库](https://ima.copilot)

## 🤝 贡献

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**Last Updated**: 2026-05-23  
**Maintainer**: Leonardo (Leonardo-Chow)  
**AI Assistant**: Hermes Agent (mimo-v2.5-pro)
