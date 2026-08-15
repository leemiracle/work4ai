# 透视 GitHub Harness 高星仓库全景（topic:harness · stars≥1K · 37 仓全量）

> 数据快照：2026-08-15 · 来源：GitHub Search API（`topic:harness stars:>=1000`，按 star 降序单页全量）
> 三重校验：API total_count=37 = 解析条数 37 = 附录数据行 37 = 赛道合计 37 ✓ **零遗漏**
> 姊妹篇：[`透视GitHub-AI高星仓库全景.md`](./透视GitHub-AI高星仓库全景.md)（topic:ai · 279 仓）、[`透视GitHub-LLM高星仓库全景.md`](./透视GitHub-LLM高星仓库全景.md)（topic:llm · 240 仓）——三篇合成「开源生态观测三镜」：ai 镜看 Agent 基建热，llm 镜看全栈分层，**harness 镜看 2026 年正在爆发的新共识词**。
> 落地层：单仓源码级深读见 [`Agent框架案例/`](./Agent框架案例/README.md)（DeepSeek Harness 案例）；蒸馏成的 opencode skill 见 [`harness精华合入-总入口.md`](./harness精华合入-总入口.md)。

---

## 0. 一句话总纲

**2025-2026 年，"agent 框架"这个词正在被"harness（运行时环境）"替换**：社区共识从"给模型写编排代码"（框架思维）转向"给模型造可靠的工作环境"（harness 思维）。公式化表达（ruflo 67.9k★ 的口号）：

> **Agent = Model + Harness。模型决定写什么代码，harness 决定何时、何地、怎么写。**

数据证据：topic:harness 共 1,427 仓，其中 ≥1K★ 的 37 仓里 **20 仓（54%）创建于 2026 年、28 仓（76%）创建于 2025 年之后**——这是本次三镜观测中最年轻的赛道（对比：topic:ai 高星仓只有 11% 创建于 2026）。qm（yc-software）2026-07-29 创建，三周冲到 13.6k★，star 通胀与赛道爆发同步。

---

## 1. 宏观统计（硬数据）

### 1.1 Star 分桶（总量 1,427 仓，高星头部集中）

| 区间 | 仓库数 | 占比 |
|---|---:|---:|
| 50K+ | 2 | 5.4% |
| 20K–50K | 4 | 10.8% |
| 10K–20K | 6 | 16.2% |
| 5K–10K | 6 | 16.2% |
| 1K–5K | 19 | 51.4% |

中位数 ≈ 5.3K；最高 80,031（bytedance/deer-flow）。

**Top 10**：

| # | 仓库 | ★ | 定位 |
|---:|---|---:|---|
| 1 | bytedance/deer-flow | 80.0k | SuperAgent harness（研究/编码/创作，字节出品） |
| 2 | ruvnet/ruflo | 67.9k | Agent 元 harness（Claude Code/Codex 的执行层，35 插件） |
| 3 | zhayujie/CowAgent | 46.5k | 超级 AI 助理 harness（chatgpt-on-wechat 转生） |
| 4 | openai/openai-agents-python | 28.7k | 多 agent 工作流轻量框架 |
| 5 | rohitg00/agentmemory | 27.0k | 编码 agent 持久记忆（跨 harness） |
| 6 | alibaba/open-code-review | 20.5k | 确定性管线 + LLM 的混合代码评审 |
| 7 | pydantic/pydantic-ai | 19.3k | 类型化端到端 agent 框架 |
| 8 | NevaMind-AI/memU | 14.3k | 跨 agent 个人记忆（存成 Wiki） |
| 9 | mindfold-ai/Trellis | 13.9k | "The best agent harness"（.trellis 工程层） |
| 10 | yc-software/qm | 13.6k | 多人协作 agent harness（Slack + Web） |

### 1.2 语言分布：Python + TypeScript 双寡头（70%）

| 语言 | 数量 | 占比 | 主战场 |
|---|---:|---:|---|
| Python | 13 | 35.1% | 全功能 harness 运行时、SDK |
| TypeScript | 13 | 35.1% | 编码 agent 周边、插件生态、桌面端 |
| Go | 3 | 8.1% | 代码评审、终端 agent、openclaw 重写 |
| Rust | 2 | 5.4% | 桌面 harness、跨端助理 |
| Java | 1 | 2.7% | 分布式长任务 agent（阿里 agentscope-java） |
| HTML/MDX/C#/未标 | 4 | 10.8% | 元技能包、教程站、领域工具 |

与 topic:ai 镜同构：**Python 造运行时，TypeScript 造周边生态**。值得注意的差异：harness 镜里 TypeScript 与 Python 完全打平（ai 镜是 104:69）——因为大量 harness 是"装进 Claude Code / Codex / opencode 的插件层"，天然长在 TS 生态上。

### 1.3 创建年份：一年内重建的赛道

| 创建年 | ≤2022 | 2023 | 2024 | 2025 | 2026(至8月) |
|---|---:|---:|---:|---:|---:|
| 仓库数 | 4 | 1 | 4 | 8 | **20** |

- 存量幸存者（≤2022 的 4 仓）里只有 polyaxon（2016，ML 控制面）是真"前 agent 时代"词汇使用者——彼时 harness 泛指实验脚手架（如 lm-evaluation-harness，在 topic:ai 镜里）。
- **2026 年前 8 个月贡献了 54% 的高星仓**：话题标签本身是 2025 下半年才开始被大规模使用的"新共识词"，star 增速远超 ai/llm 镜同期。
- 新词登顶速度样本：qm（07-29 创建 → 13.6k★）、penguin-harness（07-19 → 1.3k★）、llm-space（06-28 → 1.6k★）。

### 1.4 组织集中度：大厂全部入场

bytedance（deer-flow 80k）、openai、pydantic、vercel、alibaba×2（open-code-review + agentscope-java）、strands-agents（AWS 系）、zilliztech（memsearch）——但 Top 10 里 6 席仍是独立开发者/初创（ruvnet、zhayujie、rohitg00、NevaMind、mindfold、yc-software）。**大厂做 SDK 和基础设施，个人开发者做超级助理**，分层清晰。

---

## 2. 七条赛道分类图（全量见附录）

| 赛道 | 数量 | 头部代表 | 一句话判断 |
|---|---:|---|---|
| A. 超级 Agent Harness（全功能运行时） | 14 | deer-flow、CowAgent、ruflo、hive | "batteries included"的个人/团队 AI 助理运行时，是 topic 的主体（38%）——先做可用产品，再谈工程 |
| B. Harness Engineering 方法论与教学 | 2 | learn-harness-engineering、awesome 清单 | 概念的定义层：五子系统模型 + 产业文献地图，本主题的知识密度之王 |
| C. SDK/框架（harness 当库写） | 6 | openai-agents-python、pydantic-ai、harness-sdk、eve | 与"框架"赛道的分界在消融：这些框架全都自称 harness，卖点是类型/可控/厂商无关 |
| D. 记忆/上下文子系统 | 4 | agentmemory、memU、memsearch、puppyone | "跨 harness 记忆"是独立产品品类——harness 可换，记忆沉淀 |
| E. 元 harness（生成/优化 harness 的 harness） | 4 | revfactory/harness、penguin-harness、Trellis、CommandCodeAI | L3 层：一句话生成 agent 团队 + skills；RSI（自改进）路线的载体 |
| F. 领域专用 harness | 5 | open-code-review、Unity-Skills、modlens、Chorus、goclaw | 把 harness 思想压进单一领域：代码评审/Unity 自动化/视觉外挂/AI-DLC |
| G. Harness 工具/基建 | 2 | llm-space（harness IDE）、polyaxon（控制面） | 给造 harness 的人造工具：trace/replay/评测；观测闭环补齐 |

**结构判断**：A+B+E 合计 20 仓（54%）做的是"harness 本体或其生成"，C+D+G 合计 12 仓（32%）做"harness 的零件"，F 5 仓做垂直应用。**这是一个"整机 > 零件"的赛道**——与 orchestration 镜（引擎为核）互补：编排管流程，harness 管环境。

---

## 3. 概念卡：harness 到底是什么（本主题的独特价值）

topic:ai / topic:llm 镜观测的是"生态分布"；topic:harness 镜额外贡献了一个**概念的定义现场**。综合 walkinglabs 教程（11.4k★）与 awesome 清单（3.8k★）：

### 3.1 定义与五大子系统

> Harness engineering = 给模型造完整工作环境的工程实践。它不是写更好的 prompt，而是设计模型运行其中的系统。

| 子系统 | 内容 | 落地文件 |
|---|---|---|
| **Instructions** | 告诉 agent 做什么、什么顺序、先读什么——渐进披露，不是一本百科全书 | AGENTS.md / CLAUDE.md + 分域文档 |
| **State** | 做了什么/在做什么/下一步；**持久化到磁盘**，跨会话精确接续 | progress.md、feature_list.json、git log |
| **Verification** | 只有跑通的测试算证据；agent 不能没有可运行证明就宣布胜利 | tests + lint + type-check + smoke + e2e |
| **Scope** | 一次只做一个 feature；不许改 feature 清单来掩盖未完成 | feature_list.json（机器可读边界） |
| **Session Lifecycle** | 开始初始化、结束清场、留下次会话的交接条 | init.sh、clean-state checklist、handoff note |

### 3.2 硬证据：Anthropic 对照实验

同模型（Opus 4.5）同任务（"做个 2D 复古游戏编辑器"）：无 harness 花 $9/20 分钟产出不可用；全套 harness（planner+generator+evaluator）花 $200/6 小时产出可玩游戏。**模型没变，harness 变了**。OpenAI 对 Codex 报告同构结论：好 harness 让同一模型从"不可靠"变"可靠"，是质性跃迁而非边际改进。

### 3.3 四层栈：prompt → context → loop → graph

walkinglabs 教程的 14 讲最终收敛为一条演化链：

1. **Prompt 层**：单次对话写好指令（大多数人停在这里）
2. **Context 层**：管上下文预算——裁剪、KV-cache 局部性、工具屏蔽、文件系统记忆（Manus 打法）
3. **Loop 层**：六原语——automations / worktrees / skills / connectors / sub-agents / external state；generator 与 evaluator 分离（maker-checker）
4. **Graph 层**：单 loop 是"只有一个节点的图"；任务需要特化/并行/共享状态/恢复时，它就不再是 loop 而是 graph（nodes, edges, shared state, routing）。警示：in-loop 检查点治不了三种结构病——Goodhart（指标被 gaming）、向上盲区、冲突

### 3.4 与"框架"的分野

awesome 清单直接收录 Inngest 的檄文《Your Agent Needs a Harness, Not a Framework》与 LangChain 的《The Anatomy of an Agent Harness》（agent = model + harness：prompts、tools、middleware、orchestration、runtime infrastructure）。学界同步跟进：preprint 提出 **CAR 分解**（Control–Agency–Runtime）与 HarnessCard 结构化报告格式。**"harness"从口语进入学术命名**。

### 3.5 五条产业共识（Awesome 清单 Foundations 精要）

1. OpenAI《Harness engineering》：架构约束 + 仓库本地指令 + 浏览器验证 + 遥测
2. Anthropic《Effective harnesses》：initializer agent、feature list、init.sh、自验证、跨上下文窗口交接
3. Thoughtworks（MartinFowler 站）：harness = 上下文工程 + 架构约束 + 对熵的"垃圾回收"
4. HumanLayer《Skill Issue》：编码 agent 弱结果多半是 harness 问题不是模型问题
5. 评测观：**基准应该比的是 harness 质量而不是模型质量**（SWE-bench/Terminal-Bench/τ-bench 的 harness 读法）

---

## 4. 三镜互证

- **LLM 镜 §7** 已观测：topic:llm 榜首 ECC 240k 是"给编码 Agent 做训练与性能优化的 harness 系统"——元工具登顶。本镜 37 仓是同一现象的正面战场：`harness-engineering` 已成为正式 topic 标签（pydantic-ai 等 6 仓同时挂着它）。
- **AI 镜"第一公理"**（"LLM 提意图，确定性层做决定"，24 批中 15+ 批复现）在 harness 镜的表述：**模型决定写什么，harness 决定何时/何地/怎么写**——同一公理的赛道内重言。
- **dsh 案例**（Agent框架案例/deepseek-harness插件化框架）证明"harness 本身可插件化"；本镜 ruflo（35 插件）、deer-flow（skills 包边界 + allowed-tools 策略）是同一"一切皆插件"思想在不同宿主上的实现。**skill 是跨 harness 的通用货币**（SKILL.md 是数据不是代码）——与 dsh 生态分析结论完全一致，互为 37 仓规模的外部验证。
- **orchestration 镜**（17 仓 → 7 skill）管"流程编排"；harness 镜管"运行环境"。二者交集在 loop/graph 层（maker-checker = producer-reviewer 模式）。

---

## 5. 映射到 work4ai

| 本镜产出 | 去处 |
|---|---|
| 概念卡（§3 五子系统/四层栈/CAR） | [`讲透Agent/`](./讲透Agent/)、[`Agent架构模式参考/`](./Agent架构模式参考/) 的生态锚点 |
| 20 仓核心思想蒸馏 | [`harness精华笔记.md`](./harness精华笔记.md) |
| skill 合入 | [`harness精华合入-总入口.md`](./harness精华合入-总入口.md)（1 个 opencode skill） |
| 单仓源码级深读 | [`Agent框架案例/`](./Agent框架案例/README.md)（已有 dsh 案例；deer-flow/CowAgent 是候选） |
| AgentSkills 开放标准 | [`前沿与媒体/103-AgentSkills开放标准深度解析.md`](./前沿与媒体/103-AgentSkills开放标准深度解析.md) |

---

## 6. 误差声明

1. star 数为 2026-08-15 快照，本赛道增速极快（qm 三周 13.6k），数字半衰期短；
2. topic 标签自报，存在蹭词（polyaxon 的 harness 指 ML 实验控制面）与漏标（Claude Code/opencode 本体不用该标签，但生态全在造 harness）——按标签口径统计，**结果偏低估而非高估**；
3. ≥1K★ 阈值是本镜选择（总量 1,427 仓的头部 2.6%）；500–1K 区间另有 17 仓未入表；
4. 语言/创建年取 GitHub API 字段，"未标"2 仓为 awesome 清单（实为 Markdown）与 CommandCodeAI。

---

## 附录：37 仓全量清单（按 star 降序）

| # | 仓库 | ★ | 语言 | 赛道 | 一句话 |
|---:|---|---:|---|---|---|
| 1 | bytedance/deer-flow | 80.0k | Python | A | SuperAgent harness：子代理+记忆+沙箱+可扩展 skills；2.0 全面重写（LangGraph 底座） |
| 2 | ruvnet/ruflo | 67.9k | TypeScript | A | Claude Code/Codex 的元 harness："Agent=Model+Harness"；35 插件（swarm/记忆/联邦/安全） |
| 3 | zhayujie/CowAgent | 46.5k | Python | A | 超级助理 harness（原 chatgpt-on-wechat）：规划+三级记忆+知识库+自进化，9 渠道 |
| 4 | openai/openai-agents-python | 28.7k | Python | C | 轻量多 agent 工作流框架：handoffs/guardrails/sessions/tracing |
| 5 | rohitg00/agentmemory | 27.0k | TypeScript | D | 编码 agent 持久记忆，自称真实基准第一；跨 Claude Code/Codex 等 |
| 6 | alibaba/open-code-review | 20.5k | Go | F | 混合架构代码评审：确定性管线 + LLM agent，行级评论，多语言规则集 |
| 7 | pydantic/pydantic-ai | 19.3k | Python | C | "Python 做 AI 的方式"：全接口类型化端到端；自带 harness-engineering 标签 |
| 8 | NevaMind-AI/memU | 14.3k | Python | D | 个人记忆存成 Wiki：跨会话/跨 agent/跨设备 |
| 9 | mindfold-ai/Trellis | 13.9k | TypeScript | E | "The best agent harness"：.trellis/ 工程层（spec/tasks/journal），4 阶段循环，22 平台 |
| 10 | yc-software/qm | 13.6k | TypeScript | A | 多人 agent harness（Slack+Web）：每人一个 agent，自选 harness 与模型 |
| 11 | walkinglabs/learn-harness-engineering | 11.4k | TypeScript | B | Harness engineering 项目制课程：14 讲 8 项目，五子系统+四层栈（§3 主源） |
| 12 | aden-hive/hive | 10.9k | Python | A | 生产级多 agent harness："一个 loop 控制多个 loop"，Queen+worker 克隆+共享台账 |
| 13 | revfactory/harness | 8.8k | HTML | E | L3 元工厂：一句话生成 agent 团队+skills，6 种团队架构模式 |
| 14 | strands-agents/harness-sdk | 6.9k | Python | C | AWS 系 SDK："Build an agent harness, control it end-to-end"；hooks/guardrails/steering |
| 15 | xerrors/Yuxi | 6.5k | Python | A | 多租户 harness 平台：LightRAG 知识库+知识图谱（LangChain+Vue+FastAPI+Neo4j） |
| 16 | ModelEngine-Group/nexent | 5.8k | Python | A | 零代码平台，明言基于 Harness Engineering 原则：约束+反馈环+控制面 |
| 17 | the-open-agent/openagent | 5.5k | Go | A | 下一代个人助理：LLM+RAG+agent loop，支持 computer-use/browser-use/coding |
| 18 | agentscope-ai/agentscope-java | 5.1k | Java | C | 分布式、生产级、长任务 agent（阿里系 Java 版） |
| 19 | vercel/eve | 4.6k | TypeScript | C | 文件系统优先的 durable agent 框架：instructions.md/tools/skills/channels/schedules 约定位置 |
| 20 | Agenta-AI/agenta | 4.5k | TypeScript | C | 团队 agent 工作台：构建/评测/观测一体 |
| 21 | walkinglabs/awesome-harness-engineering | 3.8k | — | B | 产业文献地图：OpenAI/Anthropic/Thoughtworks 原文+基准库+harness 运行时（§3.5 主源） |
| 22 | polyaxon/polyaxon | 3.7k | MDX | G | ML 时代 AI infra/编排/控制面（2016 存量词，非 agent 义） |
| 23 | CommandCodeAI/command-code | 3.7k | — | E | Command Code AI（harness 生成器） |
| 24 | nextlevelbuilder/goclaw | 3.5k | Go | F | OpenClaw 的 Go 重写：多租户隔离+5 层安全+原生并发 |
| 25 | Project-N-E-K-O/N.E.K.O | 2.5k | Python | A | 具身情感引擎驱动的实时 AI 伴侣（会主动找你玩） |
| 26 | zilliztech/memsearch | 2.5k | Python | D | 统一持久记忆层：Markdown + Milvus 向量双底座 |
| 27 | kevinluosl/deepbot | 2.4k | TypeScript | A | 系统级 AI 助理：一键部署+飞书原生集成 |
| 28 | PhyAgentOS-dev/PhyAgentOS | 1.8k | Python | A | 自进化具身 AI 操作系统（agentic workflows 底座） |
| 29 | deer-flow/llm-space | 1.6k | TypeScript | G | harness IDE：原型/逐步 trace/失败回放/评测（deer-flow 御用调试器） |
| 30 | Besty0728/Unity-Skills | 1.6k | C# | F | Unity AI 自动化技能包 |
| 31 | liustack/modlens | 1.5k | TypeScript | F | DeepSeek Harness 视觉插件：纯文本 agent 外挂 OCR/版面/语义 |
| 32 | shiwenwen/hope-agent | 1.4k | Rust | A | 跨端桌面助理：记忆+持续推进目标+动态多 agent 编排，可常驻 NAS |
| 33 | Prism-Shadow/penguin-harness | 1.3k | TypeScript | E | RSI harness："让 AI 造 AI"——benchmark→找失分→发版 N+1 自进化 |
| 34 | puppyone-ai/puppyone | 1.3k | TypeScript | D | Git 原生 context drive：上下文托管+文件级 agent 权限 |
| 35 | Chorus-AIDLC/Chorus | 1.1k | TypeScript | F | AI-DLC 方法论 harness："反向对话"——AI 提案、人类验证 |
| 36 | zhnt/loushang | 1.1k | Python | A | Python 版 AI-native 编码 harness：多模型编排+会话状态+工具治理+可追溯交付 |
| 37 | Onelevenvy/flock | 1.1k | Rust | A | Rust/Tauri 桌面多 agent harness（langgraph-rust 驱动） |

赛道合计：A14 + B2 + C6 + D4 + E4 + F5 + G2 = 37 ✓

---

生成：2026-08-15 · GitHub Search API 全量抓取 + 20 仓 README 精读（蒸馏见 [harness精华笔记](./harness精华笔记.md)）
