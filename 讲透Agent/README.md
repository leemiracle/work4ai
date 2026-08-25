# 讲透 Agent（智能体）

> **Agent = LLM + 工具 + 循环**。从单次 LLM 调用的"闭眼猜"升级为"感知→推理→行动→反馈"的闭环。本系列从 ReAct 地基讲到规划/记忆/工具调用/实战案例，覆盖 2024-2026 Agent 工程全栈。
>
> 配套：[`讲透LLM/`](../讲透模型/讲透LLM/)（基座）+ [`讲透Prompt/03`](./讲透Prompt/03-结构化输出与函数调用.md)（function calling）+ [`讲透RL/`](../讲透模型/讲透RL/)（Agent RL）+ [`Agent架构模式参考/`](./Agent架构模式参考/)（生产架构）+ [`Agent记忆系统案例/`](./Agent记忆系统案例/)（memory 落地）

---

## 篇目

| # | 标题 | 核心 |
|---|------|------|
| **00** | [为什么需要 Agent](./00-为什么需要Agent.md) | 单次 LLM 三硬伤；ReAct 范式；Agent vs 单次 vs Pipeline |
| **00'** | [讲透笔记-算法经验枢纽](./00-讲透笔记-算法经验枢纽.md) | Agent 算法经验枢纽 |
| **01** | [经典 Agent 范式对比](./01-经典Agent范式对比.md) | ReAct / Reflexion / Tree-of-Thought / Plan-and-Execute |
| **02** | [工具调用工程](./02-工具调用工程.md) | function calling / tool description / error handling |
| **03** | [规划与搜索](./03-规划与搜索.md) | MCTS / BFS / DFS / 长程任务分解 |
| **04** | [记忆机制](./04-记忆机制.md) | short-term / long-term / RAG memory / summary buffer |
| **05** | [自进化延伸](./05-自进化延伸.md) | What/When/How 三维分类（arXiv:2507.21046）；Reflexion→Self-Rewarding→ADAS/AFlow→RAGEN→EvoAgentX 谱系；自改稳定性三条件 |
| **05'** | [自进化2.0-整体叠加](./自进化2.0-整体叠加.md) | 五层扩**八层谱系**（Skills/Harness 独立成层）+ **RSI 四系统**（STOP→DGM 2505.22954→DGM-H 2603.19461→AlphaEvolve 2506.13131，一级证据全核实）+ 2026 三新综述（更新算子/动态图重写/记忆三阶段）+ 八层落地自查表 + 最小 DGM 实验（贪心 0/30 vs 存档 15/30，p<0.0001：**探索权>探索技巧**）|
| **实战** | [Open-AutoGLM 手机 Agent](./实战案例-Open-AutoGLM手机Agent/) | 真实端到端 Agent 案例 |
| **实战** | [DeepSeek Harness 框架](./Agent框架案例/deepseek-harness插件化框架/) | 工业级 agent harness："一切皆插件"+ 信任平面源码解剖 |
| **实战** | [opencode 自成长改造](./Agent框架案例/opencode自成长改造/) | hermes×ECC 蓝图：把本地 opencode 改造成自成长 Agent（闭环学习环实操） |
| **实战** | [MCP 协议生态全景](./Agent框架案例/MCP协议生态全景/) | topics/mcp 64k 仓知识集成：生态六赛道 + **2026-07-28 规范无状态化重构** + SDK v2/Registry 格局 + 项目内 MCP 互链网 |
| **实战** | [RL 领域 Agent](./实战案例-RL领域Agent/) | ★自建可跑：contextual bandit 内核+四层记忆+Reflexion+**三进化环**（Q表/APO/Ctx-APO context 栈）+kb_curate 知识固化+debate 双 agent（892 行纯标准库，31 项技术映射经两轮五角色审查核验）|
| **实践** | [实践阶梯 · 端侧事实记忆 Agent](./实践阶梯/) | ★L1→L5 上手动手单元：CPU-only Qwen2.5-0.5B 事实抽取+记忆+意图识别；**34 条任务集×5 版消融**（few-shot 治塌缩 32→0、反馈重试净负、受限 generation 65% 完胜 scoring 27%）；评估环否决 3 个自己的设计断言——「上手/设计/衡量」三缺口的实操答案 |
| **参考** | [AI-Agents-in-Depth 全书深读卡](./AI-Agents-in-Depth全书深读卡.md) | 306页 2026 教科书逐章知识点+核验（✓互锁15+/△转引30/⚠自引8+/✗偏差1：Mem0 v3数字）；与项目14资产对账表——**评估方法论(Ch7)与多Agent失败模式学(Ch10)为最大增量** |
| **实战** | [性能优化 Agent](./实战案例-性能优化Agent/) | GPU/CPU/Linux 设备性能优化 Agent 设计蓝图：**2025-2026 四线全景**（AKO4X/KernelAgent/KernelArc/SemaTune/LumOS/SchedCP/AgentKernelArena 一手实证）+ 三大遗留缺口速答（上手三级跳 T0-T2 / 取舍四问×guard 分工 / 三层指标+reward hacking 博弈档案 14.5% 作弊率）|
| **实战** | [Prover 数学 Agent](./实战案例-Prover数学Agent/) | ★内网 DCU 实测：DeepSeek-Prover-V2-7B 逆向蒸馏**十条规律**（子目标分解=难度在跨度/RZPD 策展/一致性奖励/专家迭代/小模型技能枝）→ 三件套（oprover-math skill 全局已装 + prover_harness.py 递归闭环 + 官方 prompt 双模式）+ DCU 三坑实录 |
| **讲透** | [讲透 Skills](./讲透Skills/) | ★2026-08-25 新建：Agent Skills 全景知识站（00-09 + 实验室三实验全跑通：E1 触发评测 zero-shot 2/10→few-shot 4/10 欠触发铁证 / E2 渐进披露省 93.1% + CC 1% 预算下 128K 窗口仅装 5 个 / E3 本机 117 目录扫出 2 真 C4 bug）+ 官方规范/skill-creator 485 行一手拆解 + **六线研究地图**（MCE 2601.21557/SkillRL/MemSkill/Memento-Skills/skill smells 实证/SkillNet 全核实）+ 数学五型 skill 类型学×MATH_LOOP_ENGINE 挂网 |

---

## 怎么用（按目标分流）

### 🛤 第一次了解 Agent
 [00](./00-为什么需要Agent.md) → [01](./01-经典Agent范式对比.md) → [02](./02-工具调用工程.md)

### 🛤 想搭生产 Agent
 [02 工具调用](./02-工具调用工程.md) → [04 记忆](./04-记忆机制.md) → [Agent架构模式参考](./Agent架构模式参考/)

### 🛤 想搞长程规划
 [03 规划与搜索](./03-规划与搜索.md) → Tree-of-Thought / MCTS / Plan-and-Execute

### 🛤 想做自进化 / 自改进 Agent
 [05 自进化](./05-自进化延伸.md) → [05' 整体叠加 RSI](./自进化2.0-整体叠加.md) → [experiments/05_selfevolve.py](./experiments/05_selfevolve.py)（最小 DGM 真跑）→ [实战案例-RL领域Agent](./实战案例-RL领域Agent/)（三进化环工程版）

### 🛤 想做 Agent RL
 [`讲透RL/`](../讲透模型/讲透RL/)（PPO/GRPO + tool use reward）

---

## 配套生态

- **基座**：[`讲透LLM/`](../讲透模型/讲透LLM/)（生命周期）
- **架构参考**：[`Agent架构模式参考/`](./Agent架构模式参考/)（生产架构模式）
- **记忆案例**：[`Agent记忆系统案例/`](./Agent记忆系统案例/)（MemGPT/Letta 等）
- **框架案例**：[`Agent框架案例/deepseek-harness插件化框架/`](./Agent框架案例/deepseek-harness插件化框架/)（DeepSeek 官方 harness，loop/日志/沙箱/接缝源码级笔记）
- **Prompt 工程**：[`讲透Prompt/03`](./讲透Prompt/03-结构化输出与函数调用.md)（function calling）
- **外部论文流**：[`PaperAgent精华合入-总入口`](./PaperAgent精华合入-总入口.md)（PaperAgent 公众号 15 主题精华：Agent/RAG/记忆/工具学习/RL×LLM/自演化/**Agentic RL/Deep Research/Vibe Coding/AI4Research/世界模型×具身**；讲透Agent 01-04 章+RL/代码生成/RAG 系列各有对应合入条目）
- **应用形态**：[`讲透DeepResearch/`](./讲透DeepResearch/README.md)（Deep Research = Agent 循环 × 检索 × 综合成文的产品级汇流；讲透Agent 的 01 循环 + 02 工具 + 04 记忆在该系列组装成调研工作流）
- **工业生态对照**：[`AgentRL生态深读/`](./AgentRL生态深读/README.md)（2026 八大开源 RL 项目深读：AgentGym-RL/Uni-Agent understand 三件套 + verl/verl-tool/AWorld-RL/SkyRL 深读卡 + torchrl/cleanrl 双管线[卡+三件套]——rl_agent "教学前置层"定位的工业对照组；torchrl=组件化工业库 ↔ cleanrl=单文件教学库构成"怎么写 RL 代码"的纵向参考系）
- **运行环境深读**：[`omarchy-深读/`](./omarchy-深读/README.md)（2026-08-25 新增：DeepWiki 39 子页全量归档 + omarchy-quattro v4 分叉 10 页 docs/ 产出——**第一个把 AI coding agent 当系统组件设计的桌面**：agent 选择/无值守启动/用量采集/崩溃诊断全系统命令化，"agent 运行环境"维度的活教材）
- **学习循环上游**：[`top-math-courses/MATH_LOOP_ENGINE.md`](../top-math-courses/MATH_LOOP_ENGINE.md)（数学循环引擎：七阶段 理论→计划→实践→观察→反思→理论'→深挖 × BFS 63 类知识森林——Prover 数学 Agent 的"子目标分解+验证闭环"在**人类学习侧**的同构操作系统；agent 工具=@oracle/@fixer，reward=五类验证信号，expert iteration=蒸馏三件套）

---

---

## 🎭 欺骗动力学视角：Agent 自主规划藏诈

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](../欺骗动力学-社会进步的隐秘引擎.md) §5。

### 三问

1. **讲透Agent 防的是什么欺骗？** → Agent 的中间推理步骤隐藏错误或被工具欺骗。
2. **被什么攻破？** → 工具返回伪造 / 规划死循环 / 记忆被污染。
3. **沉淀进哪条主链？** → AI 安全主链——Agent 信任栈 / 工具调用审计 / 可验证执行。

### 一句话

> Agent 越自主，越需要它的每一步都可审计——这是 Agent 时代的反欺骗基础设施。

## 🔗 与其他宇宙的连接

- **[`讲透多Agent协作/`](./讲透多Agent协作/)**：单 Agent 的可靠性问题在多体下放大为协调问题；深读卡 §十 补三块增量——**信息增量判据**（协作是否引入生成时无法获得的新信息=多Agent价值唯一标准）、六失败模式学（Why Multi-Agent Fail 14种归纳）、A2A 协议（Agent×Agent 的 MCP）
- **[`AI-Agents-in-Depth全书深读卡.md`](./AI-Agents-in-Depth全书深读卡.md)**：本宇宙的教科书坐标系（10章逐点核验+与14资产对账表）；深潜任何主题前先翻对应章建图
