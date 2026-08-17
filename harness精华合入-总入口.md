# harness 精华合入 · 总入口

> 来源：[GitHub topics/harness](https://github.com/topics/harness) 高星 37 仓（≥1K★，全量快照见 [透视GitHub-Harness高星仓库全景.md](./透视GitHub-Harness高星仓库全景.md)）。
> 精化产物：**1 个新 opencode skill**（`harness-engineering`），安装于 `~/.config/opencode/skills/`，opencode 启动时自动加载。
> 本文档是使用说明；蒸馏细节见 [harness精华笔记](./harness精华笔记.md)。
> 学术线（2026-08-17 新增）：四篇 harness 综述 + LLM Ensemble + 领域 Harnessing 的合并解析与 NFL 分析见 [harness三综述合并解析](./harness三综述合并解析.md)（引用全部一手核实，修复原拆解 8 处错误，明细在 [.research/harness-survey/引用核实报告.md](./.research/harness-survey/引用核实报告.md)）。

## 一、仓库 → skill 映射

| 仓库 | ★ | 类型 | 合入去向 |
|---|---|---|---|
| walkinglabs/learn-harness-engineering | 11.4k | 教学课程 | `harness-engineering`（五子系统+四层栈+会话生命周期） |
| walkinglabs/awesome-harness-engineering | 3.8k | 文献地图 | `harness-engineering`（产业共识与文献索引） |
| bytedance/deer-flow | 80k | SuperAgent harness | `harness-engineering`（skill 渐进加载+验证即证据条目） |
| ruvnet/ruflo | 67.9k | 元 harness | `harness-engineering`（Agent=Model+Harness 公式条目） |
| mindfold-ai/Trellis | 13.9k | 工程层 | `harness-engineering`（spec 晋升循环条目） |
| revfactory/harness | 8.8k | 元工厂 | `harness-engineering`（6 团队模式清单） |
| aden-hive/hive | 10.9k | 生产 harness | 不单设 skill——"一个 loop 控多个 loop" 已被 `orchestration-fleet`/`orchestration-dag` 覆盖 |
| zhayujie/CowAgent、nexent、Yuxi、qm 等 A 赛道 14 仓 | — | 全功能运行时 | 不合入（是产品不是方法；其思想已被公式/五子系统吸收） |
| agentmemory、memU、memsearch、puppyone | — | 记忆/上下文 | 不合入（记忆层已有 hermes 式 MEMORY.md 约定 + `orchestration-statemachine` 记忆图谱） |
| openai-agents-python、pydantic-ai、harness-sdk、eve、agenta、agentscope-java | — | SDK/框架 | 不合入（写代码时用库，不是 agent 行为纪律） |
| alibaba/open-code-review、Unity-Skills、modlens、Chorus、goclaw | — | 领域专用 | 不合入（域外） |
| polyaxon、llm-space、CommandCodeAI 等 | — | 工具/存量词 | 不合入（观测工具或非 agent 义） |

蒸馏原则：harness 镜与 orchestration 镜互补不重叠——**编排管流程（DAG/状态机/舰队），harness 管环境（指令/状态/验证/边界/生命周期）**；loop/graph 层交叉处归 orchestration-*，环境五子系统归本次新 skill。

## 二、skill 速查

### 本次新增（1 个）

| Skill | 来源 | 一句话 | 触发词示例 |
|---|---|---|---|
| `harness-engineering` | learn-harness + awesome + deer-flow/ruflo/Trellis/revfactory | 给模型造可靠工作环境：五子系统检查单、四层栈定位、会话生命周期仪式、最小四文件落地、6 团队模式 | "harness"、"装一个 harness"、"agent 不可靠"、"跑不完任务"、"会话接续"、"宣布完成" |

### 与既有 skill 的组合拳

| 场景 | 组合 |
|---|---|
| agent 干活不可靠/提前宣布完成 | `harness-engineering`（五子系统体检：验证即证据）→ 缺哪补哪 |
| 长任务跨会话 | `harness-engineering`（progress/feature_list/handoff）+ `orchestration-statemachine`（防跳步守卫） |
| 大型任务组织形态选型 | `harness-engineering` 的 6 团队模式选架构 → `orchestration-fleet` 并行执行 → `orchestration-hyperplan` 敌意审计划 |
| 造完 harness 要评测 | `harness-engineering` 的基准观（测 harness 不测模型）+ awesome 清单基准索引 |
| 方法论自改进 | Trellis 的 spec 晋升循环 + `orchestration-ultrawork` 完成审计 |

## 三、使用说明

1. **触发**：无需手动调用——命中描述词自动加载。也可显式说：`用 harness-engineering 的五子系统给这个项目做体检` / `按会话生命周期仪式收尾这次任务`。
2. **位置**：`C:\Users\mirac\.config\opencode\skills\harness-engineering\SKILL.md`；修改后重启 opencode 生效。
3. **克制**：skill ≤64 行一张纸读完；扩展细节写回本项目的 [harness精华笔记](./harness精华笔记.md)，不撑爆 skill。

## 四、后续候选（不合入但留观）

| 仓库 | ★ | 留观理由 |
|---|---|---|
| penguin-harness | 1.3k | RSI（自进化）若成主流，可能需要独立 skill；暂与 `orchestration-ultrawork` 完成审计重叠 |
| deer-flow/llm-space | 1.6k | harness IDE 思想（trace/replay）若 opencode 原生缺口扩大再议 |
| alibaba/open-code-review | 20.5k | 若项目引入 PR 自动评审，可提炼确定性管线+LLM 分工检查单 |

---
生成：2026-08-15 · 对齐 [orchestration精华合入-总入口.md](./orchestration精华合入-总入口.md) 的体例


# harness 精华笔记（蒸馏细节）

> 本文是 [harness精华合入-总入口](./harness精华合入-总入口.md) 的资料附录：topic:harness 头部 20 仓 README 级核心思想蒸馏，供人工研读与后续迭代 skill 用。全景快照见 [透视GitHub-Harness高星仓库全景.md](./透视GitHub-Harness高星仓库全景.md)。
> 抓取：2026-08-15 · raw.githubusercontent.com 原文

## 一、walkinglabs/learn-harness-engineering（11.4k★）——概念的定义层

**核心立场**：The Model Is Smart, The Harness Makes It Reliable（模型已够聪明，harness 让它可靠）。

**硬证据**：Anthropic 对照实验——同模型同任务，无 harness $9/20min 产出不可用；全套 harness（planner+generator+evaluator）$200/6h 产出可玩的游戏。模型没变，harness 变了。

**五子系统**（教程 L02，全景 §3.1 已表）：Instructions / State / Verification / Scope / Session Lifecycle。

**会话生命周期**（教程核心仪式，值得逐字照抄）：

```
START   读 AGENTS.md → 跑 init.sh → 读 progress.md → 读 feature_list.json → 看 git log
SELECT  只挑一个未完成 feature
EXECUTE 实现 → 跑验证（tests/lint/type-check）→ 失败则修复重跑 → 通过则记录证据
WRAP UP 更新 progress.md → 更新 feature_list.json → 记录仍未解决/未验证项 → 干净状态提交
```

**四层栈**（L13/L14 收敛）：prompt → context → loop → graph。
- Loop 层六原语：automations、worktrees、skills、connectors、sub-agents、external state；generator/evaluator 分离；三种 loop：goal loop / timer loop / maker-checker loop。
- Graph 层判断式："一个 loop 是只有一个节点的图。当任务需要特化、并行、共享状态、验证、恢复——它就不再是 loop，是 graph。" in-loop 检查点治不了三种结构病：Goodhart（指标被 gaming）、向上盲区（局部节点看不见全局冲突）、冲突（并行分支互相踩）。
- 金句：**Harness engineering builds the vehicle. Loop engineering designs the road.**（你在车外设计路，而不是坐在车里打方向盘）

**最小落地四文件**：AGENTS.md + init.sh + feature_list.json + progress.md——"四个文件，agent 会话立刻显著稳定"。

**8 个项目**全部围绕同一个 Electron 知识库 app 迭代：P(N+1) 的 starter = P(N) 的 solution——app 演化，harness 技能同步生长（教学设计的巧思：让学习者和被 harness 的 agent 走同一条演化路径）。

## 二、walkinglabs/awesome-harness-engineering（3.8k★）——产业文献地图

- 定义："harness engineering 处在 context engineering、evaluation、observability、orchestration、safe autonomy、软件架构的交叉口。"
- Foundations 五支柱：OpenAI《Harness engineering: leveraging Codex in an agent-first world》；Anthropic《Effective harnesses for long-running agents》（initializer agents / feature lists / init.sh / 自验证 / 交接产物）+ 续篇（任务态与 evaluator 设计）；LangChain《The Anatomy of an Agent Harness》；Thoughtworks（context engineering + 架构约束 + 对熵的垃圾回收）；HumanLayer《Skill Issue》（"编码 agent 的弱结果多半是 harness 问题不是模型问题"）。
- 学术线：CAR 分解（Control–Agency–Runtime）+ HarnessCard 结构化报告格式（preprints 202603.1756）；harness 设计综述（preprints 202604.0428）。
- 基准观：40+ 基准按"能不能测出 harness 质量（而非模型质量）"筛选——SWE-bench Verified、Terminal-Bench 2.0/Harbor、τ-bench、OSWorld、GAIA、ClawBench、ClawWork（44 职业真实经济约束）…
- 运行时参考：deepagents、SWE-agent（harness/prompt/tools/环境全部可检视）、SWE-ReX（沙箱执行）、Harbor（Terminal-Bench 2.0 配套通用评测 harness）、Harness Evolver（基于 Meta-Harness 论文 Lee et al. 2026，多 agent 提案 + LangSmith 评测 + worktree 隔离地自主进化 harness）、Ralph（`while :; do cat PROMPT.md | claude-code; done` 极简 loop 玄学）、skills.sh（跨 runtime 技能市场）。

## 三、bytedance/deer-flow 2.0（80k★）——SuperAgent harness 工业标杆

- 转型叙事："DeerFlow 起家是 Deep Research 框架，社区拿它建数据管线、生成幻灯片、起 dashboard——我们意识到它不是研究工具，是 harness。于是 2.0 从零重写。"（LangGraph+LangChain 底座，自带 filesystem/memory/skills/sandbox/子代理）
- **Skill 渐进加载**：只在任务需要时加载（省上下文）；`/skill-name` 单轮显式激活；skill 目录是包边界（嵌套 SKILL.md 只算数据）。
- **allowed-tools 策略语义**（细到惊人）：策略只在 skill 被显式激活或经 read_file 装入活动上下文后生效；slash 激活期间该 skill 策略权威（读别的 SKILL.md 不能扩权）；发现类工具（tool_search/describe_skill）豁免但"发现≠授权执行"；fail-closed 到框架安全工具。且诚实声明："这是 best-effort 行为域限定，不是硬安全边界"。
- **沙箱信任边界诚实声明**：Lark 集成把凭据目录挂进沙箱，README 直说"prompt 注入拿到的代码能读到它们——在 credential-broker 后续移除挂载前，把沙箱视为 Lark 凭据信任边界之内"。
- **CLI 即模型 provider**：Codex CLI / Claude Code OAuth 可直接配成模型后端（复用订阅额度）。
- **DX 工程**：`make setup` 向导、`make doctor`、`make support-bundle`（issue-summary.md + AI 填报草稿 + triage.json，且明令 AI 不许编造缺失事实）；一行句把安装任务直接丢给任意编码 agent（Install.md）。

## 四、ruvnet/ruflo（67.9k★）——元 harness 与插件宇宙

- 口号：**Agent = Model + Harness**。"模型写，harness 给它工具、记忆、循环、沙箱和控制，让活儿真的能干成。"
- 自学习环：User → Ruflo(CLI/MCP) → Router → Swarm → Agents → Memory → LLM，Learning Loop 从成功模式中学习回灌。
- 35 插件九类：编排（core/swarm/autopilot/loop-workers/workflows/**federation 跨机联邦**）、记忆（agentdb/rag-memory/rvf/ruvector/knowledge-graph）、智能（从过去成功学习/daa/goals）、质量（testgen/browser/jujutsu/docs）、安全（security-audit/aidefence）、方法论（adr/ddd/sparc/**metaharness 给 harness 打分**/**arena 策略竞标赛爬山进化**）、DevOps、扩展（rvagent WASM 沙箱/plugin-creator）、领域（iot/neural-trader）。
- 双轨安装：插件市场（零文件落地）vs CLI init（全量 loop + hooks + daemon）——表格式讲清差异，不诱导过度安装。

## 五、zhayujie/CowAgent（46.5k★）——harness 工程参考实现（国民级）

- 定位："Agent Harness 工程的参考实现"：Channels（9 大 IM+Web）→ Agent Core（规划+记忆+知识+工具+skills 推理）→ Models，各层解耦。
- **三级记忆**：context → daily → core，自动 "Deep Dream" 蒸馏，关键词+向量混合检索。
- **知识层**：自动策展成 Markdown wiki + 演化知识图谱可视化。
- **自进化**：Self-Evolution 自动复盘对话→改进 skills→跟进未完成任务→固化记忆与知识。
- Skill Hub 一键装/自然语言造 skill；chat/vision/imagegen/ASR/TTS/embedding 各路由可指到不同厂商。

## 六、mindfold-ai/Trellis（13.9k★）——.trellis 工程层

- 痛点：AI 写码快但每个会话从零开始——没有项目记忆、没有团队规范。
- 结构：`.trellis/spec/`（规范一次写好按需注入）+ `.trellis/tasks/`（PRD/实现上下文/评审上下文/状态）+ `.trellis/workspace/`（个人 journal）。
- **4 阶段循环**：Plan（brainstorm 一次一问出 PRD）→ Implement（子代理带精选上下文写码，不 commit）→ Verify（check 子代理对着 spec 评审 diff + lint/类型/测试，能自修则自修）→ Finish（`/trellis:finish-work` 归档任务，**update-spec 把新学到的规则晋升回 spec**——下个会话更聪明）。
- 22 平台同构：同一套结构生成到 Claude Code/Codex/opencode/cursor…；"CLAUDE.md/AGENTS.md 是好入口但会变大泥球，Trellis 在其上加作用域 spec、任务 PRD、工作流闸门、平台感知生成"。

## 七、revfactory/harness（8.8k★）——L3 元工厂：6 种团队架构

- 层级自认：L3 Meta-Factory（生成别的 harness 的层），与 Archon（运行时配置工厂）、ECC（跨 harness 工作流）分层共存。
- **6 种团队架构模式**：Pipeline（串行依赖）/ Fan-out·Fan-in（并行独立）/ Expert Pool（按上下文选择性调用）/ Producer-Reviewer（生成+质检）/ Supervisor（中枢动态分发）/ Hierarchical Delegation（自顶向下递归委派）。
- 6 阶段流程：领域分析 → 团队架构设计 → agent 定义生成（.claude/agents/）→ skill 生成 → 编排集成 → 验证测试（触发验证、dry-run、带 skill vs 不带 skill 对照）。
- Skill 生成带渐进披露结构；输出即文件（agents/ + skills/），可 review 可版本化。

## 八、aden-hive/hive（10.9k★）——一个 loop 控制多个 loop

- 机制：Queen（持久的主 loop）按需克隆 worker（同工具同模型、独立任务）——"没有图要编译，没有编排样板要写"，colony 靠共享台账（tracker ledger）+ 持久计划协调。
- 生产四件套：crash-safe park/resume、成本强制、带外 human-in-the-loop（Sentinel）、深度可观测。
- 选题判断式："当瓶颈不再是模型而是它周围的 harness 时用 Hive"——需要状态持久+崩溃恢复+成本+审计的生产负载。

## 九、vercel/eve（4.6k★）——文件系统即编写界面

```
agent/
├── agent.ts         # 可选：模型与运行时配置
├── instructions.md  # 必需：常驻 system prompt
├── tools/           # 可选：类型化工具
├── skills/          # 可选：按需装载的流程
├── channels/        # 可选：HTTP/Slack/Discord 通道
└── schedules/       # 可选：cron 定时
```
- 约定位置 > 配置文件；durable（持久执行）；**npm 包自带全量文档**（node_modules/eve/docs），编码 agent 可本地读——"给 agent 造的框架，文档也按 agent 可读来发"。

## 十、strands-agents/harness-sdk（6.9k★，AWS 系）——SDK 化的 harness

- "Build an agent harness. Control it end-to-end."：model-driven（few lines of code 起步）+ 厂商无关（Bedrock/Anthropic/OpenAI/Gemini/自建）。
- 四卖点：内置上下文管理/执行上限/可观测；loop 每个决策默认留痕；hooks 拦截任意步骤（记日志/校验/改道）；guardrails 先拦后跑 + steering handlers 让 agent 自纠而不是静默失败。

## 十一、ModelEngine-Group/nexent（5.8k★）——零代码 harness 平台

- 自述"基于 Harness Engineering 原则"的零代码平台：统一工具/skills/记忆/编排 + **内置约束、反馈环、控制面**——不做拖拽编排，纯语言开发。
- v2.0：A2A 协作、渐进 skill 披露、分层记忆（用户级+用户-agent级）、多租户 RBAC、agent 版本管理与市场。

## 十二、Prism-Shadow/penguin-harness（1.3k★）——RSI：让 AI 造 AI

- 三段论证：①极简工具集+干净底层接口=更少 token（数据分析精度最优、成本 1/70 Claude Code，深度调优 DeepSeek）；②一句话生成完整 agent 应用（RAG 应用全程 $0.02）；③**自进化**：跑基准→找失分点→发 N+1 版，每轮留快照，Trace 视图可观测。
- 四组内置 skills 里最关键的是 **Agent Tuning 组**：agent-creation / benchmark-design / agent-evaluation / agent-optimization——把"造 agent"本身做成了 skill。

## 十三、deer-flow/llm-space（1.6k★）——harness IDE

- 面向 agent 构建者的桌面端：Build（提示词/工具/设置版本化）→ Trace（看见 loop 内每次模型调用与工具执行）→ Debug（从历史回放一次运行逐步找错）→ Evaluate（跨 run 测量）→ Generate（AI 帮你写 prompt/工具，任意对话可导出为 LangGraph agent）。
- deer-flow 每个版本都用它构建和调试（dogfooding 闭环）。

## 十四、Chorus-AIDLC/Chorus（1.1k★）——AI-DLC 方法论 harness

- 定义 harness："包住 LLM agent 的基础设施——会话生命周期、任务状态、子代理编排、可观测、故障恢复。"
- 源自 AWS AI-DLC（AI 驱动开发生命周期）；核心哲学 **Reversed Conversation：AI 提案，人类验证**；细粒度可配置权限的多 agent + 人协作走完需求→交付全流程。

## 十五、puppyone-ai/puppyone（1.3k★）——Git 原生 context drive

- 上下文托管：给 agent 的上下文带 Git 版本控制 + **每个 agent 文件级作用域权限**——"context 当代码管"（上下文的 review/回滚/审计）。

## 十六、记忆三家：agentmemory（27k）/ memU（14.3k）/ memsearch（2.5k）

- agentmemory：编码 agent 持久记忆，自称真实基准第一；卖点是跨 harness（Claude Code/Codex/Cursor/Copilot 通吃）。
- memU："个人记忆，存成 Wiki——跨会话、跨 agent、跨设备"。记忆形态选 Wiki（可读可编辑）而非向量黑盒，与 rowboat 的 Markdown 双链图谱同路（见 orchestration 精华笔记 §五）。
- memsearch（zilliz 出品）：Markdown + Milvus 双底座的统一持久记忆层。
- **共性判断：记忆独立于 harness 成为一等品类**——harness 可换（qm 让员工自选 harness），记忆必须沉淀（"personal memory across agents"）。

## 十七、框架三家：openai-agents-python（28.7k）/ pydantic-ai（19.3k）/ agentscope-java（5.1k）

- openai-agents-python：轻量多 agent 工作流——agents/handoffs/guardrails/sessions/tracing 五原语，"多写普通代码，少配黑盒"。
- pydantic-ai：全接口类型化端到端（agents/realtime voice/图像生成/embeddings），每模型每接口；官方 topic 里并列 harness 与 **harness-engineering** 标签——框架厂主动认领 harness 词汇。
- agentscope-java（阿里）：分布式、生产级、**长任务**（long-running）agent——Java 企业生态的 harness 答卷。

## 十八、yc-software/qm（13.6k★）——多人 harness

- "work 的多人 agent harness"：在 Slack 和 Web 里，员工每人一个 agent；**自带 harness 与模型选择器**（"pick your own harness and model and switch between"）——harness 成为用户级可换件。侧栏：个人文件/crons/密钥链/部署/记忆/skills。

## 十九、领域两件：alibaba/open-code-review（20.5k）/ modlens（1.5k）

- open-code-review：混合架构评审——确定性管线（规则集：NPE/线程安全/XSS/SQL 注入）+ LLM agent，行级精准评论，阿里规模实战过。与 ECC 公理同构：**确定性层先过筛，LLM 只做规则覆盖不到的语义判断**。
- modlens：DeepSeek Harness 视觉插件——纯文本编码 agent 粘贴图片即得结构化 JSON 证据（OCR/版面/语义）。dsh 生态分析的"周边载体证明运行时中性"又一例。

## 二十、横向综合：harness 镜的六条公理

1. **公式**：Agent = Model + Harness（模型决定写什么，harness 决定何时/何地/怎么写）——ruflo、deer-flow、hive、awesome 清单四方一致。
2. **五子系统是最小完备集**：Instructions/State/Verification/Scope/Lifecycle——教程给定义，Trellis（spec/progress/feature）、dsh（插件化实现）、Chorus（会话生命周期+故障恢复）给实现。
3. **验证即证据**：没有跑通的测试不算完成（learn-harness L09、Trellis Verify、open-code-review 的确定性管线）。
4. **渐进披露无处不在**：skill 按需加载（deer-flow/nexent/Trellis）、指令分文件给地图不给百科（L04）、文档随包分发给 agent 读（eve）。
5. **诚实声明边界**：deer-flow 明说 allowed-tools 非 hard boundary、沙箱在凭据信任边界内；hive 说"不适合简单实验"——好 harness 项目都写清楚自己治不了什么。
6. **元层在生长**：revfactory（生成团队）、penguin（自进化）、ruflo-metaharness（打分）、Harness Evolver（论文化）、qm（用户自选）——"造 harness 的 harness"是 2026 下半年最活跃的子方向（RSI/自改进路线）。

---
生成：2026-08-15 · 20 仓 README 精读蒸馏（原文缓存：Temp/opencode/harness-readmes/）
