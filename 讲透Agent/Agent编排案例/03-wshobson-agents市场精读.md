# wshobson/agents 市场精读：一份 Markdown，五 harness 原生分发

> 仓库：wshobson/agents · 38.8k★ · Python+Markdown · MIT · 2025-07 创建
> 证据层：2026-08-15 抓取的仓库 README + 文件树。标 📄 的论断来自 README 原文。

## 一、定位

**多 harness agentic 插件市场**：以 Claude Code 插件格式为"单一事实源"，同一份 Markdown 自动生成五种 harness 的**原生**产物（不是最低公分母翻译）📄：
**94 插件 / 203 agents / 175 skills / 109 commands / 16 orchestrators** 📄。

## 二、五 harness 适配矩阵 📄

| Harness | 生成物 | 要点 |
|---|---|---|
| Claude Code | 源（marketplace.json + plugins/） | 原生宿主 |
| Codex CLI | `.agents/plugins/` 注册表 + plugin.json | 8KB skill 上限，commands→skills 转换 |
| Cursor | `.cursor-plugin/` + `.cursor/rules/` | 复用 .claude/ 目录 |
| **OpenCode** | `.opencode/agents/` `commands/` `skills/` | **`tools:` 白名单 → `permission:` 块**的自动转换；OpenCode 安全 skill 名 📄 |
| Gemini CLI | skills/agents/commands（TOML） | 2026-04 spec 原生 subagents |

安装（OpenCode 侧）📄：
```bash
gh repo clone wshobson/agents ~/agents && cd ~/agents
make install-opencode    # 运行 generate + symlink
```

## 三、内容架构（对本项目最有参考价值）

### 3.1 插件 = 最小可装载单元 📄
```
plugins/python-development/
├── .claude-plugin/plugin.json
├── agents/    # 3 个 Python agent（python-pro/django-pro/fastapi-pro）
├── commands/  # 1 个脚手架命令
└── skills/    # 16 个专项 skill（async/testing/packaging/…）
```
**装一个插件只载入它的组件，不是整个市场进 context** 📄——渐进披露的工程兑现。

### 3.2 分层模型策略 📄
| Tier | 模型 | 用途 |
|---|---|---|
| 0 | Fable 5 | 最长程自主工作（大迁移，多小时，opt-in 高成本） |
| 1 | Opus | 架构/安全/评审/生产关键 |
| 2 | inherit | 用户自选：后端/前端/AI-ML/专项 |
| 3 | Sonnet | 文档/测试/调试/API 参考 |
| 4 | Haiku | 快速操作：SEO/部署/内容 |
→ 与 OmO 的类别路由同一思想：**按任务形状选强度，不让用户手挑**。

### 3.3 plugin-eval 三层质量评估 📄
1. **Static**：确定性结构分析（<2s，免费）；
2. **LLM Judge**：4 维语义评审（~30s）；
3. **Monte Carlo**：50-100 次模拟运行的统计可靠性（~2-5min）。
`uv run plugin-eval score <skill> --depth quick` / `certify`。
→ 对本项目的启示：**skill 也该有质量门**——静态检查（触发词覆盖/结构完整）+ 语义评审 + 抽样实测，三层递进，成本递增。

## 四、评价（诚实披露）

- **强**：单源多 harness 是内容分发面的正确解；94 插件粒度克制；plugin-eval 把"skill 质量"从玄学变测量。
- **弱/风险**：内容量巨大（203 agents）必然良莠不齐——市场模式的质量方差靠 eval 补，但 eval 未默认强制 📄；Windows 下 `make + symlink` 路径有坑（README 未覆盖，需自行验证）。
- **本项目取舍**：不整装（203 agents 会淹没现有 100+ 技能体系）；按需单插件摘取 + 借鉴其 permission 白名单转换法与 plugin-eval 分层评估法。
