# oh-my-openagent（OmO）精读：opencode 生态第一编排 harness

> 仓库：code-yeongyu/oh-my-openagent · 67.9k★ · TypeScript · 2025-12 创建 · 默认分支 dev
> 证据层：2026-08-15 抓取的仓库 README（英文版）+ 仓库文件树。标 📄 的论断来自 README 原文；未逐行读源码。

## 一、定位与三版本

**"For your Codex, for your OpenCode"** 📄——一个装进 opencode（或 Codex CLI）的 agent harness 插件，作者口号是"未来的模型会每月更便宜更聪明，没有单一供应商能统治；我们为开放市场构建，不为围墙花园"。README 称 Anthropic 曾因该项目封锁 OpenCode 接入 📄（此事为作者单方陈述，存档备查）。

| 版本 | 宿主 | 安装 | 内容量 |
|---|---|---|---|
| **Ultimate** | OpenCode | `bunx oh-my-openagent install` | 11 agents + 54+ hooks + 5 内置 MCP + Team Mode + 全部 slash 命令 📄 |
| **Light** | Codex CLI | `npx lazycodex-ai install` | 8 个可移植组件（rules/comment-checker/git-bash/lsp/ultrawork/ulw-loop/续跑/遥测）📄 |
| **Senpi**（beta 独立版） | 自带引擎 | `npm i -g omo-ai@beta` | 内置 OMO 扩展的原生命令 📄 |

注意：npm 上裸包名 `omo` 是无关项目，官方强调必须用 `omo-ai@beta` 📄。

## 二、agent 编排体系（本项目最关注部分）

### 2.1 纪律 agent 团队 📄
- **Sisyphus**（主编排，推荐 claude-opus-5 / kimi-k3 / glm-5）：计划、派发、驱动完成，"不会中途停"。
- **Hephaestus**（深度执行，gpt-5.6-sol）：给目标不给菜谱，端到端自主探索执行。
- **Prometheus**（规划器）：**面试模式**——先像真工程师一样盘问你、圈定 scope、消歧，再产出计划。
- 另有 Oracle（架构/调试）、Librarian（文档/代码检索）、Explore（快速 grep）、Multimodal Looker 📄。

### 2.2 类别路由（category dispatch）📄
Sisyphus 派发子任务时不选模型，选**类别**，类别自动映射模型：
`visual-engineering`（前端 UI）/ `deep`（自主研究执行）/ `quick`（单文件小改）/ `ultrabrain`（硬逻辑架构，路由 GPT-5.6 Sol xhigh）。
→ **精化去向**：`orchestration-fleet` 技能的类别路由表。

### 2.3 Team Mode v4.0（默认关）📄
- lead + 最多 8 个并行成员，经 `team_create / team_send_message / team_task_create / team_status` 等专用工具通信；
- tmux 实时可视化（focus + grid 窗口）；
- 两个上层技能：**hyperplan**（5 个敌意 agent 从正交角度撕计划）、**security-research**（3 漏洞猎手 + 2 PoC 工程师并行审计，严重度按真实可利用性校准）。
- 配置：`.opencode/oh-my-openagent.jsonc` → `"team_mode": {"enabled": true, "max_parallel_members": 4, "tmux_visualization": true}` 📄
→ **精化去向**：`orchestration-fleet`（lead-worker 骨架）+ `orchestration-hyperplan`（五敌评审）。

## 三、三大杀手级功能（带数据证据）

### 3.1 ultrawork 纪律循环 📄
`ultrawork`（或 `ulw`）一个词激活全部机制：Goal 持久化（`/goal` 每次空闲重注入续跑提示，直到完成审计通过）、Todo Enforcer（agent 一闲就被拉回任务）、Ulw Loop（`.omo/ulw-loop/` 落盘的多目标持久编排 + 证据审计）。
用户证言（README 摘录）："一晚上 8000 条 eslint 告警清零"；"45k 行 tauri 应用一夜转 SaaS"。📄
→ **精化去向**：`orchestration-ultrawork` 技能（goal 文件 + 完成审计 + 续跑纪律的纯协议版）。

### 3.2 Hash 锚定编辑（Hashline）📄
每行读出时带内容哈希 `11#VK| function hello() {`，编辑按锚引用；文件若已变，哈希失配则**在破坏发生前拒绝**。引 The Harness Problem（can.ac, 2026-02）：多数 agent 失败不是模型的错，是编辑工具逼模型"复现见过的内容"。数据：Grok Code Fast 1 成功率 **6.7% → 68.3%**，仅靠换编辑工具 📄。
→ **opencode 原生已部分覆盖**（edit 工具的 oldString 强匹配同理）；整装版才具备。

### 3.3 /init-deep 分层上下文 📄
一键在项目每层目录生成 `AGENTS.md`（project/src/components 三层示例），agent 自动就近读相关层——token 省且性能升。
→ **可直接借鉴的实践**：大 repo 应分层放 AGENTS.md 而非单个巨型文件。

## 四、其余功能速览 📄

- **内置 MCP**：Exa（web 搜索）/ Context7（官方文档）/ Grep.app（GitHub 代码搜索），运行时注入。
- **Skill 内嵌 MCP**：skill 自带 MCP server，按需拉起、用完即走，不占常驻 context——与本项目[前沿103 AgentSkills 解析](../前沿与媒体/103-AgentSkills开放标准深度解析.md)的渐进披露互证。
- **LSP 四件套**：`lsp_rename/goto_definition/find_references/diagnostics`；AST-Grep 25 语言模式改写；Tmux 全交互终端。
- **Comment Checker**：专治 AI 味注释；**Rules 注入**：`AGENTS.md` + `.omo/rules/**` 每 prompt 自动载入。
- **Claude Code 兼容**：hooks/commands/skills/MCPs/plugins 原样可跑。
- **遥测**：默认开（每日一次匿名 DAU/WAU/MAU，SHA256 安装 ID）；`"telemetry": false` 或 `OMO_DISABLE_POSTHOG=1` 关闭 📄。

## 五、评价（诚实披露）

- **强**：把"完成纪律"做成了产品（goal/todo/audit 三件套）；类别路由是对"模型选型焦虑"的正确抽象；hash 编辑有量化证据。
- **弱/风险**：单一维护者主导（"99% 用 OpenCode 构建，我不太会 TypeScript" 📄）；功能面极大 = 供给面复杂，与 opencode 版本耦合紧；SUL-1.0 许可（非标准 OSI）。
- **本项目取舍**：不整装安装，只精化其**协议层**（纪律/评审/舰队三个技能）+ 把整装路径写进[手册](./04-opencode合入手册.md)留给用户自决。
