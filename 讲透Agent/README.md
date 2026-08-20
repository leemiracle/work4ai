# 讲透 Agent（智能体）

> **Agent = LLM + 工具 + 循环**。从单次 LLM 调用的"闭眼猜"升级为"感知→推理→行动→反馈"的闭环。本系列从 ReAct 地基讲到规划/记忆/工具调用/实战案例，覆盖 2024-2026 Agent 工程全栈。
>
> 配套：[`讲透LLM/`](../讲透LLM/)（基座）+ [`讲透Prompt/03`](../讲透Prompt/03-结构化输出与函数调用.md)（function calling）+ [`讲透RL/`](../讲透RL/)（Agent RL）+ [`Agent架构模式参考/`](../Agent架构模式参考/)（生产架构）+ [`Agent记忆系统案例/`](../Agent记忆系统案例/)（memory 落地）

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
| **实战** | [Open-AutoGLM 手机 Agent](./实战案例-Open-AutoGLM手机Agent/) | 真实端到端 Agent 案例 |
| **实战** | [DeepSeek Harness 框架](./Agent框架案例/deepseek-harness插件化框架/) | 工业级 agent harness："一切皆插件"+ 信任平面源码解剖 |
| **实战** | [opencode 自成长改造](./Agent框架案例/opencode自成长改造/) | hermes×ECC 蓝图：把本地 opencode 改造成自成长 Agent（闭环学习环实操） |
| **实战** | [MCP 协议生态全景](./Agent框架案例/MCP协议生态全景/) | topics/mcp 64k 仓知识集成：生态六赛道 + **2026-07-28 规范无状态化重构** + SDK v2/Registry 格局 + 项目内 MCP 互链网 |
| **实战** | [RL 领域 Agent](./实战案例-RL领域Agent/) | ★自建可跑：contextual bandit 内核+四层记忆+Reflexion+**三进化环**（Q表/APO/Ctx-APO context 栈）+kb_curate 知识固化+debate 双 agent（892 行纯标准库，31 项技术映射经两轮五角色审查核验）|

---

## 怎么用（按目标分流）

### 🛤 第一次了解 Agent
 [00](./00-为什么需要Agent.md) → [01](./01-经典Agent范式对比.md) → [02](./02-工具调用工程.md)

### 🛤 想搭生产 Agent
 [02 工具调用](./02-工具调用工程.md) → [04 记忆](./04-记忆机制.md) → [Agent架构模式参考](../Agent架构模式参考/)

### 🛤 想搞长程规划
 [03 规划与搜索](./03-规划与搜索.md) → Tree-of-Thought / MCTS / Plan-and-Execute

### 🛤 想做 Agent RL
 [`讲透RL/`](../讲透RL/)（PPO/GRPO + tool use reward）

---

## 配套生态

- **基座**：[`讲透LLM/`](../讲透LLM/)（生命周期）
- **架构参考**：[`Agent架构模式参考/`](../Agent架构模式参考/)（生产架构模式）
- **记忆案例**：[`Agent记忆系统案例/`](../Agent记忆系统案例/)（MemGPT/Letta 等）
- **框架案例**：[`Agent框架案例/deepseek-harness插件化框架/`](./Agent框架案例/deepseek-harness插件化框架/)（DeepSeek 官方 harness，loop/日志/沙箱/接缝源码级笔记）
- **Prompt 工程**：[`讲透Prompt/03`](../讲透Prompt/03-结构化输出与函数调用.md)（function calling）
- **外部论文流**：[`PaperAgent精华合入-总入口`](../PaperAgent精华合入-总入口.md)（PaperAgent 公众号 15 主题精华：Agent/RAG/记忆/工具学习/RL×LLM/自演化/**Agentic RL/Deep Research/Vibe Coding/AI4Research/世界模型×具身**；讲透Agent 01-04 章+RL/代码生成/RAG 系列各有对应合入条目）
- **应用形态**：[`讲透DeepResearch/`](../讲透DeepResearch/README.md)（Deep Research = Agent 循环 × 检索 × 综合成文的产品级汇流；讲透Agent 的 01 循环 + 02 工具 + 04 记忆在该系列组装成调研工作流）
- **工业生态对照**：[`AgentRL生态深读/`](../AgentRL生态深读/README.md)（2026 八大开源 RL 项目深读：AgentGym-RL/Uni-Agent understand 三件套 + verl/verl-tool/AWorld-RL/SkyRL 深读卡 + torchrl/cleanrl 双管线[卡+三件套]——rl_agent "教学前置层"定位的工业对照组；torchrl=组件化工业库 ↔ cleanrl=单文件教学库构成"怎么写 RL 代码"的纵向参考系）

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

- **[`讲透多Agent协作/`](../讲透多Agent协作/)**：单 Agent 的可靠性问题在多体下放大为协调问题
