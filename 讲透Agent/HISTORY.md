# 讲透Agent · 思想史

> **一句话定位**：AI Agent 从 1957 年 Newell-Simon 的"通用问题求解器"到 2026 年自主完成软件工程的 Agentic AI，走了近 70 年——它的历史不是"Agent 越来越聪明"的线性进步，而是四次范式转移（符号推理→行为/认知架构→深度 RL→语言推理），每次转移都伴随一个核心思想的"换问法"：从"如何搜索问题空间"到"如何在环境里行动"，从"手工编码信念-欲望-意图"到"用奖励信号塑造策略"，从"为每一步写规则"到"让语言模型自己推理下一步该做什么"。

> 配套：[`讲透AI历史/00-为什么学AI历史`](../讲透AI历史/00-为什么学AI历史.md)（方法论）+ [`讲透AI历史/advanced/01-范式转移的库恩分析`](../讲透AI历史/advanced/01-范式转移的库恩分析.md)（库恩框架）+ [`讲透RL/HISTORY.md`](../讲透RL/HISTORY.md)（RL 范式转移与 Agent 交叉）+ [本系列 README](./README.md)

---

## 0. 方法论

> 本篇遵循 [`讲透AI历史`](../讲透AI历史/) 的方法论：**思想史 > 年代史**。

**年代史**会这样写：

```
1957  Newell-Shaw-Simon GPS
1987  Bratman 提出 BDI 哲学
1987  Laird-Newell-Rosenbloom 提出 Soar
1995  Rao-Georgeff 形式化 BDI
1986  Brooks 行为机器人
2013  DQN（深度 RL Agent）
2022  ReAct（Yao et al.）
2023  AutoGPT / BabyAGI / Generative Agents
2023  Voyager / Toolformer
2024  MCP / Devin
2025  Agentic AI 主流化
```

这给你事实，但不告诉你**为什么 GPS 在 1957 年是革命性的、却在 1970s 被抛弃**；不告诉你**BDI 的"信念-欲望-意图"模型和 2023 年的 ReAct 循环共享同一个哲学根**；不告诉你**Brooks 1986 年"没有表征的智能"这一反叛思想，在 40 年后以 LLM Agent 的形态复活**。

**思想史**问的问题：

| 问题 | 在 Agent 史上的体现 |
|---|---|
| 为什么此时此地？ | 为什么 ReAct 在 2022 年而非 2012 年出现？（答：GPT-3 + 思维链 + function calling 三个条件凑齐）|
| 为什么被淘汰？ | 为什么 BDI/Soar 在 2000s 被冷落？（答：手工编码知识的成本爆炸——与专家系统同病）|
| 为什么复兴？ | 为什么"Agent"概念在 2023 年大爆发？（答：LLM 提供了通用推理引擎，让 Agent 不再需要手工编码领域知识）|
| 路径依赖与偶然性 | 如果 Yao 没有 ReAct 想法，AutoGPT 的病毒式传播可能不存在——LangChain 缺了灵魂 |
| 谁影响了谁？ | Newell→Soar（Laird）→OODA 循环→ReAct，70 年一脉相承 |

**本篇的五条原则**（承接 [`讲透AI历史`](../讲透AI历史/)）：

1. **思想史 > 年代史**——每个"突破"都问"为什么此时"
2. **路径依赖敏感**——当前"最优 Agent 架构"可能是历史偶然
3. **失败与成功同等重要**——被淘汰的方向（BDI/Soar/GOFAI Agent）有教训
4. **跨学科**——Agent 受哲学（行动理论）/ 认知科学 / 控制论 / 经济学（多智能体博弈）/ 机器人学影响
5. **批判性**——不把"赢家"（ReAct/AutoGPT）当真理——可能只是"等到了对的载体（LLM）"

---

## 1. 前夜：符号主义 GPS（1956-1970s）

### 1.1 Logic Theorist 与 GPS：Agent 的"创世纪"

1955-1957 年，卡内基理工学院（今 CMU）的 **Allen Newell**、**Herbert Simon** 和 RAND 公司的 **Cliff Shaw** 开发了两个程序，定义了"智能体"的最初形态。

**Logic Theorist**（1956）：证明了《数学原理》（Whitehead & Russell）中 38 条定理的前 15 条，甚至给出了一条比原书更优雅的证明。它是**人类第一个真正意义上的 AI 程序**——比 Dartmouth Conference 还早几个月。

**GPS（General Problem Solver）**（1957-1959）：Newell-Simon 的野心之作。GPS 的核心创新是 **means-ends analysis（手段-目的分析）**：

> 给定当前状态 $S$ 和目标状态 $G$，找到操作符 $O$ 来缩小 $S$ 和 $G$ 的差距。如果 $O$ 不能直接应用（前提条件不满足），则递归地设定新子目标：让 $O$ 的前提条件成立。

这是 Agent 史上**第一个显式的"感知→推理→行动"循环**：

```
当前状态 → 比较目标 → 找差距 → 选操作符 → 执行 → 新状态 → （循环）
```

> 🎯 **思想史定位**：GPS 把"求解问题"形式化为**在问题空间里的搜索**——这个框架统治了 AI 头 20 年，并直接演化出 Soar 认知架构。GPS 的"目标→子目标→操作"递归分解，在 65 年后以 **Plan-and-Execute Agent** 的形态复活。

### 1.2 GPS 的天才与局限

GPS 的天才在于**领域无关**——同一个搜索框架可以做逻辑证明、下棋、积分、密码破解。这是 Agent 史上**第一次"通用"而非"专用"的野心**。

但 GPS 有致命局限：

1. **需要人类提供问题表示**——GPS 不自己"看"世界，人必须把问题编码成"状态+操作符+目标"的符号形式
2. **组合爆炸**——状态空间随问题规模指数增长，GPS 只能处理玩具问题
3. **无感知能力**——GPS 是"纯思考"的 agent，不能看、不能听、不能在物理世界里行动

> 🎯 **思想史洞察**：GPS 的局限定义了接下来 60 年 Agent 研究的核心议程——**如何让 agent 自己感知世界、自己表示问题、自己学习？** 每个范式都在回答 GPS 留下的这些问题：
> - BDI/Soar 回答"agent 的内部认知结构应该是什么"
> - Brooks 回答"agent 是否需要内部世界模型"
> - RL Agent 回答"agent 如何从试错中学习"
> - LLM Agent 回答"agent 如何获得通用推理能力"

### 1.3 物理符号系统假说

1976 年，Newell 和 Simon（此时都已拿图灵奖）发表 **Physical Symbol System Hypothesis（PSSH）**：

> 一个物理符号系统（进行符号操作的计算系统）具有产生通用智能行为的充分和必要条件。

这是符号主义 Agent 的**公理**——它断言智能 = 符号操作。此后 30 年，整个 Agent 领域都在这个假设下工作。直到 Brooks（1986）和连接主义复兴，PSSH 才受到根本挑战。

> ⚠️ **反常识预警**：PSSH 在今天看来"显然过时"，但在 1976 年它是严肃的科学假说。Newell-Simon 不是傻瓜——GPS + Logic Theorist 确实展示了符号操作的威力。PSSH 的失败不是因为它"错了"（LLM 内部也在做某种符号处理），而是因为它**低估了感知和学习的难度**——符号操作可能只是智能的一部分，不是全部。

---

## 2. 认知架构三巨头：BDI / Soar / ACT-R（1980s-2000s）

### 2.1 共同动机：从"解题器"到"认知体"

GPS 解决了"如何搜索问题空间"，但留下一个问题：**一个能在不确定、动态环境中持续行动的 agent，内部认知结构应该是什么样的？**

1980s-1990s，三个流派同时回答这个问题——它们构成了 **"认知架构"（cognitive architecture）** 这一研究范式。认知架构的目标是：提出一个**关于人类心智的完整计算理论**——包括感知、记忆、学习、决策、行动的统一框架。

### 2.2 BDI 模型：从哲学到工程

**Bratman（1987）**：哲学家 Michael Bratman 出版 *Intention, Plans, and Practical Reason*。他论证：**"意图"（intention）是一个不可还原的一阶概念**——你不能把意图还原为信念和欲望。一个人"意图去巴黎"，不只是"相信去巴黎好"加上"想去巴黎"——意图意味着**承诺**（commitment），意味着你已经在规划了，会拒绝其他诱惑。

Bratman 的**实践推理**框架：

```
信念（Beliefs）：世界是什么样的
    ↓
欲望（Desires）：我想达成什么
    ↓
意图（Intentions）：我承诺去做什么（从欲望中筛选+锁定）
    ↓
计划（Plans）：怎么达成意图
    ↓
行动（Actions）
```

**Rao & Georgeff（1991/1995）**：澳大利亚 AI 研究者 Anand Rao 和 Michael Georgeff 把 Bratman 的哲学形式化为可计算的 **BDI 架构**。他们在美国 SRI 国际研究所工作，开发了 **PRS（Procedural Reasoning System）**——第一个工业级 BDI agent 系统，用于 NASA 航天器故障管理。

BDI agent 的执行循环：

```
1. 用感知器更新 Beliefs（信念集）
2. 基于 Beliefs 生成/选择 Desires（可选目标）
3. 从 Desires 中过滤出 Intentions（承诺的目标+计划）
4. 执行当前计划的一个步骤
5. （循环）
```

> 🎯 **思想史定位**：BDI 的核心洞见——**意图是对行动的承诺而非偏好**——在 36 年后以 **Plan-and-Execute Agent** 的形态复活。当 LLM Agent "先生成 plan，再逐步执行"时，它在做 Bratman 1987 年描述的事：锁定意图，拒绝诱惑（replan 之前不改方向）。**BDI 没有死，它只是等了 30 年换了一层语言模型做引擎。**

### 2.3 Soar：Newell 的终极野心

**Laird, Newell, Rosenbloom（1987）**：GPS 的创始团队发表了 **Soar**——*SOAR: An architecture for general intelligence*。这是 Newell 晚年的终极野心：**一个统一的、通用的认知架构**。

Soar 的核心组件：

| 组件 | 功能 | 对应物 |
|------|------|--------|
| **Problem Space** | 所有认知活动都是"在问题空间里搜索" | GPS 的遗产 |
| **Production Memory** | 规则：`if 条件 then 动作` | 专家系统的遗产 |
| **Working Memory** | 当前状态（符号） | 类似 LLM 的 context window |
| **Decision Procedure** | 选哪个操作符 | LLM 的 action selection |
| **Chunking** | 从问题解决过程中自动学习新规则 | 最接近"学习"的机制 |

Soar 的**统一性野心**：所有认知——从下棋到语言理解——都用同一套"问题空间搜索 + 产生式规则"机制。这与 Newell-Simon 的 PSSH 一脉相承。

> 🎯 **思想史意义**：Soar 是 **"符号主义 Agent"的最高成就**。它把 GPS 的搜索框架扩展为完整认知架构，加入了学习机制（chunking），并在 30+ 年的发展中不断扩展（Soar 9 加入了 episodic/semantic memory；Soar 可以做机器人控制）。**但 Soar 始终受困于手工编码规则的瓶颈**——和专家系统一样，每写一个新领域就需要大量 if-then 规则。这是整个符号主义范式的死穴。

### 2.4 ACT-R：认知心理学路线

**John R. Anderson（1976 → 1993 ACT-R → 至今）**：卡内基梅隆大学（CMU）的认知心理学家。ACT-R（Adaptive Control of Thought—Rational）走的是和 Soar 不同的路线——它不追求"通用智能"，而追求**精确模拟人类认知数据**（反应时、错误率、学习曲线）。

ACT-R 的关键创新：**理性分析**（rational analysis）——不从"机制是什么"出发，而从"大脑应该怎么最优地适应环境"出发推导认知结构。

ACT-R 至今仍在使用，广泛应用于认知建模（数学学习、驾驶模拟、编程学习）。它和 Soar 的区别：

| 维度 | Soar | ACT-R |
|------|------|-------|
| 目标 | 通用智能 | 认知建模（拟合人类数据）|
| 学习 | chunking（规则学习）| 产出编译 + 效率调整 |
| 验证 | 能不能做任务 | 能不能匹配人类行为 |

### 2.5 认知架构的共同困境

三个认知架构（BDI / Soar / ACT-R）在 1990s 达到顶峰后，共同陷入困境：

1. **知识获取瓶颈**：所有架构都需要手工编码大量领域知识（规则、信念、计划模板）。这和专家系统的困境完全相同。
2. **感知缺失**：架构都是"纯思考"的——它们假设感知问题已经解决（有符号输入）。但真实世界的感知（视觉、语言）恰恰是最难的。
3. **缺乏学习**：虽然 Soar 有 chunking、ACT-R 有产出编译，但这些学习机制远不如后来的统计/深度学习强大。
4. **不可规模化**：手工编码的知识无法扩展到开放世界。

> 🎯 **思想史教训**：认知架构的失败不是因为"想法错了"——BDI 的信念-欲望-意图框架、Soar 的问题空间搜索、ACT-R 的模块化记忆，这些思想全部在后来的 Agent 系统中复活。**它们失败是因为"实现手段"（手工编码符号）无法规模化**。LLM Agent 的突破恰恰在于：**用语言模型替代了手工编码**——LLM 自己生成信念、推理意图、编写计划。

---

## 3. 多智能体系统与行为机器人：两条反叛路线（1986-2010s）

### 3.1 Brooks 的反叛：没有表征的智能

**Rodney Brooks（1986）**：MIT 的 Brooks 发表 *Elephants Don't Play Chess* 和随后的 *Intelligence Without Representation*。他对符号主义 Agent 发起了最猛烈的攻击：

> "我的论点是：在移动自主智能体的构建中，我们可以且应该消除表征和中央模型。智能通过智能体与世界的交互产生，而不是通过内部符号推理。"

Brooks 提出了 **subsumption architecture（包容架构）**：

- 不是"感知→建模世界→规划→行动"的自上而下流水线
- 而是**多层并行行为**：避障层、漫游层、寻物层……每层独立工作，高层"覆盖"（subsume）低层
- **没有中央世界模型**——agent 直接从感知映射到行动

Brooks 的机器人（Allen 1989、Herbert、Genghis）证明了：**不需要符号推理也能做出看起来"智能"的行为**——机器人能在房间漫游避障、收集易拉罐、走过不平地形。

> 🎯 **思想史意义**：Brooks 是符号主义 Agent 的"叛逆者"——他挑战了 Newell-Simon PSSH 的根基。他论证智能**不需要**内部表征——"世界就是最好的模型"（the world is its own best model）。这个反叛思想在 40 年后以 **LLM Agent** 的形态部分复活：ReAct Agent 不维护显式的世界模型，而是通过**与工具交互**（调 API、查网页、跑代码）来"感知世界"——这正是 Brooks 的"世界即模型"思想！

> ⚠️ **反常识预警**：Brooks 的"无表征智能"在 1990s 被视为异端，但在 LLM Agent 时代变成了主流直觉。ReAct 的核心循环——**Thought → Action → Observation**——本质上是 Brooks 的"感知-行动耦合"加上一层"思考"（这是 LLM 时代的新增物）。**符号主义走了 40 年，最终在"外部化推理到语言 + 交互式感知"的混合形态中找到了出路。**

### 3.2 分布式 AI 与多智能体系统（MAS）

与 Brooks 的行为机器人平行，另一条路线在发展：**多智能体系统**（Multi-Agent Systems, MAS）。

MAS 的起源是 **分布式人工智能**（DAI），始于 1970s：

- **HEARSAY-II**（1971-1976）：CMU 的语音理解系统，用"黑板架构"（blackboard）——多个知识源（agent）在共享的"黑板"上协作解决问题。这是 MAS 的最早原型。
- **Contract Net Protocol**（Smith, 1980）：任务分配协议——一个 agent 发出任务招标，其他 agent 投标，最优者获得任务。这是 agent 协商的基础。
- **DVMT**（Lesser & Corkill, 1983）：分布式车辆监控测试床——多个 agent 协作跟踪车辆。

1980s-1990s，MAS 发展为独立学科：

| 贡献 | 代表 |
|------|------|
| Agent 形式化 | Wooldridge & Jennings (1995) *Intelligent Agents* |
| MAS 博弈论 | Rosenschein & Zlotkin (1994) *Rules of Encounter* |
| Agent 组织 | Stone & Veloso (2000) 多智能体学习 |
| 机器人足球赛 | **RoboCup**（1997 至今）|

RoboCup 的终极目标："到 2050 年，一支全自主人形机器人足球队战胜人类世界杯冠军。" 这是 MAS 最具浪漫色彩的研究议程——它同时推动了感知、规划、协调、学习的综合发展。

> 🎯 **思想史意义**：MAS 在 2000s 之后被"并入"其他领域（分布式系统、博弈论、机器人学），但其核心思想——**多个 agent 协作、竞争、协商**——在 2023 年以 **多 Agent 框架**（AutoGen / CrewAI / MetaGPT）的形态爆发。当你让两个 LLM Agent 互相对话辩论时，你在做 MAS——只是 agent 的"大脑"从手工编码规则变成了语言模型。

### 3.3 OODA 循环：军事思想的贡献

Agent 的"感知-决策-行动"循环还有一个重要来源：军事思想家 **John Boyd** 的 **OODA 循环**（Observe-Orient-Decide-Act，1970s）。Boyd 原本研究空战中的决策优势，但 OODA 循环被广泛用于 Agent 设计。ReAct 的 **Observation → Thought → Action** 循环与 OODA 高度对应——这并非偶然，而是 agent 设计的**普适结构**：任何在环境中行动的实体都需要"感知 → 理解 → 决策 → 行动"的闭环。

---

## 4. 第一次范式转移：RL Agent（2013-2020）

### 4.1 库恩框架：为什么这是范式转移

按 [`讲透AI历史/advanced/01`](../讲透AI历史/advanced/01-范式转移的库恩分析.md) 的库恩框架：

| 维度 | 旧范式（符号/认知架构 Agent）| 新范式（RL Agent）|
|------|------|------|
| 行为来源 | **手工编码**规则/计划模板 | **从试错中学习** |
| 知识表示 | 符号（if-then 规则）| 神经网络权重 |
| 核心循环 | 推理（推理引擎）| 交互（agent-environment loop）|
| 异常累积 | 知识获取瓶颈 | — |
| 触发器 | — | **DQN (2013) + GPU + 深度学习** |

### 4.2 DQN：RL Agent 的诞生

2013 年，DeepMind 的 **DQN**（Mnih et al.）把深度学习和 RL 结合，让 agent 从像素直接学习玩 49 款 Atari 游戏。这是 Agent 史上第一次——**agent 不需要任何手工编码知识，纯靠与环境交互学会复杂行为**。

> 🎯 **与符号主义的不可通约性**：DQN agent 内部没有"信念"、"意图"、"规则"——它只有一个 Q 函数 $Q_\theta(s, a)$。从 BDI/Soar 的视角看，这"不是 agent"——它没有显式的认知结构。但从结果看，它比任何手工编码的 agent 都更强。**这场范式转移的核心是：用"学习"替代"编码"。**

### 4.3 AlphaGo → AlphaZero：搜索 + 学习的巅峰

2016-2017 年，DeepMind 的 **AlphaGo** 和 **AlphaZero** 让 RL Agent 达到了"超越人类"的水平。AlphaZero 的关键：**纯自我对弈 + MCTS 搜索 + 深度神经网络**——不需要人类棋谱。

> 🎯 **思想史意义**：AlphaZero 是 Sutton *Bitter Lesson* 的完美验证——**通用方法（搜索+学习）超越人类知识**。但 AlphaZero 也是 RL Agent 的"天花板"——它只在**封闭世界**（围棋规则确定、完全可观测）里有效。真正的 Agent 需要在**开放世界**（不确定、部分可观测）里行动——这是 RL Agent 做不到的。

### 4.4 RL Agent 的局限：为什么它没有"普及"

RL Agent 在游戏和仿真中表现惊艳，但在真实世界应用极少。原因：

1. **需要明确的 reward 信号**——真实世界的 reward 难以定义
2. **样本效率极低**——需要百万次交互才能学会
3. **封闭世界假设**——RL 理论依赖 MDP（马尔可夫决策过程），但真实世界远非 MDP
4. **不可解释**——神经网络策略是黑箱

这些局限让 RL Agent 停留在"游戏 AI"领域，直到 RLHF（2022）把它引入语言世界。

> **详见 [`讲透RL/HISTORY.md`](../讲透RL/HISTORY.md) §4-8 的完整 RL 思想史。** RL Agent 是 Agent 史的重要一章，但它的局限直接催生了 LLM Agent 的需求——**通用推理能力**比 RL 的"从零学习"更高效。

---

## 5. 第二次范式转移：LLM Agent 与 ReAct（2022）

### 5.1 催化剂：GPT-3 + CoT + Function Calling

LLM Agent 的爆发需要三个条件同时成熟：

1. **GPT-3（2020）**：提供了**通用推理引擎**——第一次有一个模型可以零样本完成各种任务
2. **Chain-of-Thought（Wei et al., 2022）**：让 LLM "展示推理过程"——CoT 论文证明，让 LLM "一步一步想"能大幅提升推理能力
3. **Function Calling（OpenAI, 2023.06）**：LLM 可以结构化地输出工具调用——这给了 Agent 的"手脚"

CoT 是关键的中间一步。Wei et al. 的洞察是：**LLM 不是不会推理，而是不会"展示"推理**。只要在 prompt 里加一句 "Let's think step by step"，LLM 的推理能力就涌现了。

> 🎯 **思想史洞察**：CoT 模糊了"推理"和"生成"的边界——CoT 把推理变成了 token 生成。这直接催生了 ReAct：**如果"推理"可以变成"生成"，那"行动"为什么不能也变成"生成"？** ReAct 的洞察就是把推理和行动统一到同一个生成过程中。

### 5.2 ReAct：LLM Agent 的"创世论文"

**Yao, Shunyu et al.（2022, ICLR 2023）**：普林斯顿大学的 Shunyu Yao（姚顺宇）发表 *ReAct: Synergizing Reasoning and Acting in Language Models*——**LLM Agent 史上最重要的单一论文**。

ReAct 的核心创新极其简洁——**让 LLM 交错输出推理轨迹（Thought）和行动（Action）**：

```
Thought 1: 我需要查北京天气
Action 1: search_weather("北京")
Observation 1: 25℃
Thought 2: 现在需要查上海
Action 2: search_weather("上海")
Observation 2: 30℃
Thought 3: 差值 = 30 - 25 = 5
Action 3: finish("上海比北京高 5℃")
```

> 🎯 **为什么 ReAct 是革命性的**：
> 1. **统一了推理和行动**——CoT 只有"想"，function calling 只有"做"，ReAct 让 LLM 在"想"和"做"之间自由切换
> 2. **不需要训练**——ReAct 是纯 prompt 工程，任何 LLM 加上 ReAct prompt 就是 Agent
> 3. **可解释**——每一步 Thought 都是人类可读的推理链
> 4. **极其通用**——同一个 ReAct 框架可以做问答、代码、搜索、游戏

> **思想史定位**：ReAct 之于 LLM Agent，等同于 GPS 之于符号 Agent——它定义了**Agent 的基本循环**。但 ReAct 和 GPS 有本质区别：GPS 的搜索是**符号逻辑的**，ReAct 的搜索是**语言生成的**。GPS 的操作符是手工编码的，ReAct 的操作符是 LLM 自己选择的。**这是从"编码"到"生成"的根本性转变。**

### 5.3 ReAct 与 BDI 的思想血缘

一个深刻但很少被指出的连接：**ReAct 循环和 BDI 循环共享同一个行动理论根**。

| BDI 阶段 | ReAct 对应 |
|----------|-----------|
| Beliefs（信念）| Observation（工具返回的事实）|
| Desires（欲望）| 用户给的任务目标 |
| Intentions（意图/承诺）| Thought 中"我决定下一步做 X" |
| Plans（计划）| 多步 Thought-Action 序列 |

**Bratman 1987 年的行动理论，在 2022 年以 ReAct 的形态复活——只是"推理引擎"从 PRS 变成了 GPT。** 这不是巧合，而是 agent 设计的**深层结构**：任何在环境中行动的智能体都需要信念更新、目标管理、行动选择。BDI 和 ReAct 是同一棵树的不同枝——根在 Bratman 的哲学。

### 5.4 Tree-of-Thoughts / Reflexion / Plan-and-Execute

ReAct 之后，一系列变体在 2022-2023 年涌现：

| 范式 | 论文 | 核心创新 | 对应 BDI |
|------|------|---------|----------|
| **Tree-of-Thoughts** | Yao et al. (2023) | 搜索多条推理路径，用 LLM 自评剪枝 | BDI 的多计划并行评估 |
| **Reflexion** | Shinn et al. (2023) | 失败后反思，把教训写入记忆，下次重试 | BDI 的信念修正 |
| **Plan-and-Execute** | 多个实现 | 先一次性生成完整 plan，再逐步执行 | BDI 的意图锁定 |

> **详见本系列 [01-经典Agent范式对比](./01-经典Agent范式对比.md) 的 200 次实测对比。**

---

## 6. 2023 Agent 大爆发：AutoGPT / BabyAGI / Generative Agents / Voyager

### 6.1 AutoGPT：Agent 的"病毒时刻"

2023 年 3 月，开发者 Toran Bruce Richards（GitHub 用户名 Significant Gravitas）发布了 **AutoGPT**——一个让 GPT-4 自主完成任务的开源 Agent。

AutoGPT 的核心循环：

```
用户给一个高层目标（如"研究 AI 行业并写报告"）
    ↓
GPT-4 自己分解成子任务
    ↓
GPT-4 自己执行（浏览网页、读写文件、调用 API）
    ↓
GPT-4 自己评估结果，决定下一步
    ↓
（循环直到任务完成或预算耗尽）
```

AutoGPT 在 GitHub 上两周内获得 **10 万+ Star**，成为 2023 年增长最快的开源项目之一。它引爆了 "AI Agent" 的公众认知。

> 🎯 **思想史意义**：AutoGPT 的价值不在技术——它的实现很粗糙。它的价值在于**展示了一种可能性**：**LLM 可以作为"大脑"驱动一个自主 Agent**。AutoGPT 是 Agent 的"概念验证"（proof of concept）——它证明了 ReAct 循环可以扩展到"完全自主"的场景。

### 6.2 BabyAGI：极简任务管理

2023 年 4 月，DoNotPay 创始人 Yohei Nakajima 发布 **BabyAGI**——一个极其简洁的自主 Agent：

```
1. 从目标创建第一个任务
2. 执行优先级最高的任务
3. 根据结果创建新任务 + 重新排序优先级
4. 循环
```

BabyAGI 的代码不到 200 行，但它的**任务创建-优先级排序-执行**循环成为后来无数 Agent 框架的模板。

### 6.3 Generative Agents：斯坦福的"西部世界"

**Park, Joon Sung et al.（Stanford, 2023, UIST）**：*Generative Agents: Interactive Simulacra of Human Behavior*。这是 2023 年 Agent 研究中最具学术深度的工作。

研究者创建了一个叫 **Smallville** 的虚拟小镇，放了 25 个 LLM Agent，每个有独特的性格、职业、社交关系。然后——**让它们自由活动**。

结果令人惊叹：

- Agent 们自发组织了一场**情人节派对**——一个 Agent 先有了"办派对"的想法，然后主动邀请朋友，朋友再邀请朋友
- Agent 之间产生了**社交动态**——友谊、八卦、社交回避
- Agent 表现出**日常作息**——起床、上班、吃饭、社交

关键技术创新：**Memory Stream + Retrieval + Reflection + Planning**

| 组件 | 功能 | 对应物 |
|------|------|--------|
| Memory Stream | 记录所有观察，带时间戳 | 类似 ACT-R 的 declarative memory |
| Retrieval | 按相关性 + 近因 + 重要性检索记忆 | RAG 的前身 |
| Reflection | 定期从原始记忆中抽象出高层洞察 | 类似人的"反思" |
| Planning | 基于记忆和反思生成日程计划 | BDI 的意图 |

> 🎯 **思想史定位**：Generative Agents 是**认知架构（BDI/Soar/ACT-R）的 LLM 复活**——记忆流 = 工作记忆 + 情景记忆，反思 = Soar 的 chunking（学习），计划 = BDI 的意图。**只是"推理引擎"从手工编码变成了语言模型。** 35 年前 Bratman 和 Newell 的愿景，在 LLM 时代终于可以规模化实现。

### 6.4 Voyager：终身学习 Agent

**Wang, Guanzhi et al.（NVIDIA + Caltech, 2023）**：*Voyager: An Open-Ended Embodied Agent with Large Language Models*。在 Minecraft 中实现**终身学习**的 Agent。

Voyager 的三大创新：

1. **Automatic Curriculum**：GPT-4 根据当前状态自动生成"下一个该学什么"
2. **Skill Library**：把学会的技能（Minecraft 代码）存储为可复用的技能库——**新技能可以在旧技能基础上组合**
3. **Iterative Prompting**：执行失败后自动反思修正，类似 Reflexion

> 🎯 **思想史意义**：Voyager 是**Soar chunking 的 LLM 版**——Soar 通过 chunking 自动学习新规则，Voyager 通过 skill library 自动学习新技能。区别在于 Voyager 的"技能"是可执行的代码（比 Soar 的产生式规则更灵活），而且 Voyager 用 GPT-4 生成技能而非从搜索过程中学习。**终身学习 Agent 的梦想，在 LLM + 代码执行环境中第一次有了可行路径。**

### 6.5 Toolformer：自学用工具

**Schick et al.（Meta AI, 2023）**：*Toolformer: Language Models Can Teach Themselves to Use Tools*。

Toolformer 的核心：**让 LLM 自己学会何时调用工具**——通过自监督方式。模型先生成带工具调用的文本，然后看调用结果是否帮助预测下一个 token，只保留有用的工具调用做微调。

> 🎯 **思想史意义**：Toolformer 是 ReAct 的"内化版"——ReAct 在推理时用 prompt 提示工具调用，Toolformer 在训练时就把工具使用"烧进"模型权重。这预言了后来的 **原生 function calling 模型**（GPT-4 function calling / Claude tool use）——工具调用不再是 prompt 工程，而是模型的核心能力。

---

## 7. 第三次范式转移：工具使用标准化与 MCP（2023-2024）

### 7.1 从 prompt hack 到标准化

2023 年的 Agent 面临一个工程困境：**工具调用全靠 prompt 工程**。每个工具的描述、参数格式、错误处理都要手写——而且不同 LLM（GPT-4 / Claude / Llama）的工具调用格式不兼容。

2023.06，OpenAI 推出 **Function Calling API**——第一次把工具调用标准化为 API 级别的能力。这催生了一波 Agent 框架：

| 框架 | 时间 | 定位 |
|------|------|------|
| **LangChain** | 2022.10 | Agent 编排框架（最早、最大） |
| **AutoGen** | Microsoft, 2023 | 多 Agent 对话框架 |
| **MetaGPT** | 2023 | 多 Agent "软件公司"模拟 |
| **CrewAI** | 2024 | 角色制多 Agent 框架 |

LangChain 是其中最具影响力的——它把 Agent 的"工具 + 循环 + 记忆"封装为可复用组件，大幅降低了 Agent 开发门槛。

### 7.2 MCP：Agent 工具调用的"USB-C"

2024 年 11 月，**Anthropic** 发布 **Model Context Protocol（MCP）**——一个开放协议，标准化 AI 模型与外部数据源/工具的连接。

MCP 的设计哲学：**像 USB-C 标准化了硬件接口一样，标准化 Agent 的工具接口**。

MCP 的架构：

```
MCP Host（应用，如 Claude Desktop）
    ↕ MCP 协议
MCP Client（协议适配器）
    ↕ MCP 协议
MCP Server（工具提供方，如 GitHub/数据库/API）
```

任何 MCP Server 暴露统一的接口（tools / resources / prompts），任何 MCP Host 可以连接任何 Server——**Agent 不再需要为每个工具写适配器**。

> 🎯 **思想史定位**：MCP 的意义在于**生态标准化**。此前每个 Agent 框架有自己的工具格式（LangChain Tools / OpenAI Functions / Claude Tool Use），碎片化严重。MCP 让"工具"成为**跨平台、跨框架的公共基础设施**——这类似于 HTTP 对 Web 的意义。如果 MCP 成功，Agent 的工具生态将从"定制"走向"通用"。

### 7.3 Devin：第一个"AI 软件工程师"

2024 年 3 月，Cognition Labs 发布 **Devin**——号称"第一个 AI 软件工程师"。

Devin 的演示令人震撼：它能**自主完成完整的软件工程任务**——从需求理解到代码编写、测试、调试、部署。它有命令行、浏览器、代码编辑器三个工具，可以像一个真正的工程师一样工作。

虽然后来有人指出 Devin 的演示有**精心筛选**的成分（不是所有任务都能那么顺利），但它点燃了 **"AI 替代程序员"** 的公众讨论。

> 🎯 **思想史意义**：Devin 标志着 Agent 从"研究玩具"走向"商业产品"。它把 ReAct 循环 + 工具调用 + 记忆打包成了一个**面向终端用户的产品**——用户只需描述需求，Agent 自主完成。虽然能力有限，但它展示了 Agent 的**商业可行路径**。

### 7.4 Agent 评测：SWE-bench 与 WebArena

2023-2024 年，Agent 评测基准的成熟是另一个重要标志：

| 基准 | 来源 | 任务 | 初始→当前水平 |
|------|------|------|-------------|
| **SWE-bench** | Princeton, 2023 | 修复真实 GitHub issue | ~2% → ~50%+（2025）|
| **WebArena** | CMU, 2023 | 网页操作任务 | ~14% → ~40%+ |
| **GAIA** | Meta, 2023 | 通用助手任务 | ~15% → ~50%+ |
| **τ-bench** | Sierra, 2024 | 客服 Agent 多轮对话 | — |

**SWE-bench** 最具代表性——它从真实的开源项目中提取 issue 和对应 PR，要求 Agent 自主修复。初始时（2023）最好的 Agent 只能解决 ~2% 的 issue。到 2025 年，SWE-bench 的解决率已突破 50%——**Agent 在真实软件工程任务上的能力正在快速逼近人类**。

> 🎯 **思想史意义**：Agent 评测基准的成熟标志着领域从"概念验证"走向"可衡量进步"。没有 SWE-bench，你不知道 Agent 到底有多强；有了它，每一次改进都可量化。**这类似于 ImageNet 之于深度学习——评测驱动进步。**

---

## 8. 第四次范式转移：Agentic AI 主流化（2025-2026）

### 8.1 从"Agent 实验"到"Agentic AI 产业"

2025 年开始，Agent 从"极客玩具"走向"产业基础设施"：

- **Anthropic Claude** 内置 Agent 能力（computer use / MCP 原生支持）
- **OpenAI** 推出 GPTs / Assistants API / Operator（浏览器自主操作）
- **Google** 推出 Gemini + Project Mariner（自主浏览）
- **Manus**（2025，中国）成为第一个病毒式传播的通用 Agent 产品

**Agentic AI** 成为 2025 年最热门的行业关键词——Gartner 把它列为 2025 年顶级技术趋势。从"ChatGPT"（对话 AI）到"Agentic AI"（自主行动 AI），公众认知发生了根本性转变。

### 8.2 长程规划与推理 Agent

2024-2025 年最重要的技术突破是**推理 Agent**的成熟：

- **OpenAI o1/o3 / DeepSeek R1**（2024-2025）：通过 RLVR 训练出**长思维链推理**能力——模型可以在给出答案前"想很久"
- **推理 = test-time planning**：o1/R1 的推理本质上是 **MCTS 式的搜索**——这直接呼应 AlphaZero 的"搜索+学习"范式

> 🎯 **闭环**：AlphaZero（2017）证明了"搜索+学习"在围棋上的威力。o1/R1（2024-2025）把同样的范式**扩展到语言推理**——模型不再只是"生成"，而是在"搜索"推理空间。**RL Agent 的遗产以"推理 Agent"的形态回到了语言世界。**

### 8.3 多 Agent 协作：从辩论到分工

2024-2025 年，多 Agent 系统从学术研究走向工程实践：

| 模式 | 代表 | 机制 |
|------|------|------|
| **辩论型** | Multi-Agent Debate | 多个 Agent 对同一问题辩论，投票/综合得出更好答案 |
| **分工型** | CrewAI / MetaGPT | 不同角色（产品经理/架构师/程序员/测试）协作完成软件项目 |
| **层级型** | sub-agent 编排 | 主 Agent 分解任务给子 Agent，子 Agent 再分解 |

**MetaGPT**（2023-2024）是最有代表性的——它让多个 Agent 扮演软件公司角色（PM / 架构师 / 工程师 / QA），协作完成软件开发。它的核心创新是**标准化 Agent 间的通信协议**（SOP 标准操作流程），让多 Agent 协作有章可循。

> 🎯 **思想史意义**：多 Agent 协作是 MAS（多智能体系统）的 LLM 复活——25 年前 RoboCup 让机器人在足球场上协作，今天 CrewAI 让 LLM Agent 在虚拟办公室里协作。**只是"大脑"从手工编码规则变成了语言模型。**

### 8.4 2026 趋势：Agent 的基础设施化

2026 年的 Agent 发展趋势正在清晰化：

1. **Agent OS / Agent 基础设施**：Agent 正在成为操作系统级别的基础设施——MCP 是工具总线，记忆系统是数据层，规划引擎是调度器
2. **Agent 训练**：从"prompt 工程"转向"Agent 训练"——用 RL 训练 Agent 的工具选择/规划能力（而非只训练 base LLM）
3. **Agent 安全**：Agent 信任栈、工具调用审计、可验证执行成为核心议题
4. **端侧 Agent**：手机/PC 上的本地 Agent（如 Open-AutoGLM 手机 Agent）——见本系列 [实战案例](./实战案例-Open-AutoGLM手机Agent/)

---

## 9. 思想史反思：5 个反常识

### 反常识 1：ReAct 不是新发明，是 BDI 的 LLM 复活

**官方叙事**：ReAct（2022）开创了 LLM Agent 范式。

**真相**：ReAct 的 Thought-Action-Observation 循环与 BDI 的 Belief-Intention-Action 循环共享同一个行动理论根（Bratman 1987）。35 年前 Bratman 论证的"实践推理"结构，在 2022 年以 LLM 为引擎复活了。**ReAct 的创新不在结构，在实现——用语言模型替代了手工编码的推理引擎。**

**教训**：**警惕"新发明"叙事。** 大多数"突破"是旧思想 + 新载体。BDI→ReAct 的演化告诉我们：好的思想结构会跨范式存活。

### 反常识 2：Brooks 的"无表征智能"在 LLM Agent 时代复活

**官方叙事**：Brooks（1986）的反叛失败了——符号主义在 1990s 被连接主义取代。

**真相**：Brooks 的核心洞见——**agent 不需要内部世界模型，通过与环境交互来感知世界**——在 ReAct Agent 中完全实现。ReAct Agent 不维护显式世界模型——它通过调工具（搜索 API、代码执行、网页浏览）来"看世界"。**"世界即模型"不是 Brooks 的失败，而是他超前时代 40 年的预言。**

**教训**：**被"淘汰"的思想可能只是在等待对的载体。** Brooks 的思想等了 40 年，直到 LLM 提供了"通用感知-行动"的引擎。

### 反常识 3：RL Agent 不是 LLM Agent 的"前身"，是"平行进化"

**官方叙事**：Agent 从 RL（DQN/AlphaGo）发展到 LLM Agent（ReAct），是线性进步。

**真相**：RL Agent 和 LLM Agent 是**两条平行的进化路线**，只是最近在"推理 Agent"（o1/R1）处合流。RL Agent 从"环境交互中学习"（bottom-up），LLM Agent 从"语言推理中决策"（top-down）。两者解决的是**不同的问题**——RL 适合封闭世界（游戏），LLM 适合开放世界（真实任务）。o1/R1 的推理 Agent 是**两条路线的合流**——用 RL 训练 LLM 的推理能力。

**教训**：**技术发展不是单线进化，是多线平行+交叉融合。** RL 和 LLM Agent 各自发展了 10 年，最终在推理 Agent 处合流。

### 反常识 4：认知架构（BDI/Soar/ACT-R）没有失败，只是"超前了 30 年"

**官方叙事**：BDI/Soar/ACT-R 是"被淘汰的旧范式"。

**真相**：认知架构提出的所有核心概念——信念管理、意图锁定、情景记忆、反思学习——全部在 LLM Agent 中复活。Generative Agents 的记忆流 = ACT-R 的 declarative memory；ReAct 的 Thought = BDI 的 intention deliberation；Voyager 的 skill library = Soar 的 chunking。**认知架构的"失败"不在思想，在实现——手工编码无法规模化。LLM 恰恰提供了可规模化的推理引擎。**

**教训**：**区分"思想失败"和"实现失败"。** 很多被淘汰的方向，思想是对的，只是实现手段（算力/数据/模型）不够。**LLM 时代的很多"突破"是给旧思想配了新引擎。**

### 反常识 5：Agent 的核心不是 LLM，是循环 + 工具 + 记忆

**官方叙事**：LLM Agent = LLM + 工具 = 自主智能体。

**真相**：LLM 只是 Agent 的一个组件（大脑）。真正决定 Agent 能力的是**循环设计**（ReAct vs Plan-Execute vs Reflexion）、**工具生态**（MCP / function calling）、**记忆系统**（working memory / episodic memory / skill library）。同一个 LLM，配不同的循环/工具/记忆，能力天差地别。**Agent ≠ LLM，Agent = LLM + 循环 + 工具 + 记忆。**

**教训**：**不要把 Agent 等同于 LLM。** Agent 是一个**系统工程**——循环设计、工具编排、记忆管理、错误处理、评估度量，每一步都不可少。

---

## 10. 关键人物谱系：Newell → Simon → Laird → Yao → Wang

### 10.1 Newell-Simon 谱系：Agent 的"王族"

```
Herbert Simon (1916-2001, Nobel 1978, Turing 1975)
Allen Newell (1927-1992, Turing 1975)
    ↓ 共同创立
GPS (1957) → PSSH (1976)
    ↓ Newell 晚年
John Laird (Michigan, Soar 1987-至今)
    ↓ 思想传承
"问题空间搜索" → "Agent 认知架构"
```

Newell 和 Simon 是 Agent 史的"创世者"——他们定义了"智能 = 搜索问题空间"这一根本范式。GPS 是 Agent 的第一个实例，Soar 是这个范式的终极形态。

### 10.2 BDI 谱系：从哲学到工程

```
Michael Bratman (Stanford 哲学, 1987)
    ↓ 行动理论形式化
Anand Rao & Michael Georgeff (SRI, 1991/1995)
    ↓ 工程实现
PRS → JACK → 各种 BDI agent 平台
    ↓ LLM 复活
ReAct (Yao 2022) = BDI 的 LLM 引擎版
```

Bratman 的哲学提供了 Agent 的**行动理论根**。Rao-Georgeff 把它形式化。30 年后，ReAct 用 LLM 重新实现了同一个理论框架。

### 10.3 Yao-Wang 谱系：LLM Agent 的新一代

```
Shunyu Yao (Princeton → OpenAI)
    ↓
ReAct (2022) → Tree-of-Thoughts (2023)
    ↓ 影响
整个 LLM Agent 领域

Guanzhi Wang (NVIDIA + Caltech)
    ↓
Voyager (2023) → 终身学习 Agent
```

Yao 的 ReAct 和 ToT 定义了 LLM Agent 的基础范式。Wang 的 Voyager 开创了终身学习 Agent。两人都是 2018-2020 年前后进入博士项目的年轻研究者——**库恩定律再次验证：新范式由年轻一代主导。**

### 10.4 跨谱系连接

| 连接 | 意义 |
|------|------|
| Simon → BDI（Bratman 在 CMU 参与认知科学项目）| **行动理论的哲学根** |
| Soar chunking → Voyager skill library | **终身学习的传承** |
| AlphaZero 搜索+学习 → o1/R1 推理搜索 | **RL 与 LLM Agent 的合流** |
| Brooks "世界即模型" → ReAct "工具即感知" | **反符号主义的遗产** |
| MAS RoboCup → CrewAI/MetaGPT 多 Agent | **多智能体协作的传承** |

---

## 11. 失败方向：被淘汰的 Agent 路线

> 承接 `讲透AI历史/advanced/02`（待写/未落盘） 的方法论：**失败和成功同等重要。**

### 11.1 纯符号 Agent 的死亡（2000s）

BDI/Soar/ACT-R 在 2000s 后基本退出主流 AI 研究。原因不是"想法错了"——而是**手工编码无法规模化**。每写一个新领域需要数百条规则——这和专家系统的知识获取瓶颈完全相同。

**教训**：**没有学习能力，Agent 只能是专家系统。** BDI/Soar 的悲剧在于它们的"学习机制"（chunking / production compilation）太弱——远不如后来的统计学习/深度学习。

### 11.2 AgentScript / 复杂 Agent 工作流的过度工程（2010s）

2010s，很多工业界尝试构建"企业级 Agent 平台"——用复杂的规则引擎/工作流编排来构建 agent。这些系统极其复杂、维护成本高、无法适应新场景。

**教训**：**灵活性 > 复杂性。** Agent 的核心价值是"根据情况动态决策"——把决策逻辑写死在规则里，就退化成了普通的 Workflow。

### 11.3 AutoGPT 式"完全自主"的幻觉（2023-2024）

AutoGPT 的病毒式传播让很多人相信"完全自主的 AI Agent 即将到来"。但实践发现：AutoGPT 式的"完全自主"在大多数真实任务上**成功率极低**——agent 会在循环中迷失方向、重复调用工具、产生幻觉。

**教训**：**"完全自主"是 Agent 的远期目标，不是短期现实。** 有效的 Agent 需要**人机协作**——人类设定目标和约束，Agent 执行细节。

### 11.4 Agent RL 的 reward 瓶颈（2024-2026）

2024 年起，大量论文宣称用 RL 训练 LLM Agent（工具调用/网页浏览/代码执行）。但大多数工作的 reward 设计有根本问题——任务完成信号太稀疏、太二元（成功/失败），容易 reward hack。

**教训**：**Agent 的 reward 设计比 RLHF 更难。** LLM 对齐至少有人类偏好做 ground truth，Agent 任务的 reward（"这个软件 bug 修好了吗？"）往往是主观的、依赖上下文的。

---

## 12. 路径依赖与偶然性

### 12.1 如果没有 ReAct

如果 Yao 没有在 2022 年发表 ReAct，LLM Agent 会怎样？可能 LangChain 缺少了灵魂循环，AutoGPT 的病毒式传播不会发生，Agent 的爆发会推迟 1-2 年。**一篇论文定义了一个领域的基础范式——这种"单一论文"效应在 AI 史上反复出现（Attention Is All You Need → Transformer, ReAct → LLM Agent）。**

### 12.2 如果 GPT-3 没有 few-shot 能力

ReAct 的前提是 LLM 能零样本/少样本遵循指令。如果 GPT-3（2020）没有展示 few-shot 能力，function calling 可能不会出现，Agent 循环无法实现。**Agent 的爆发依赖 LLM 的指令遵循能力——而 few-shot 是 GPT-3 的"涌现"特性，不是设计目标。**

### 12.3 如果 Brooks 没有发表"无表征智能"

如果 Brooks 1986 年没有挑战符号主义，"Agent 不需要内部世界模型"的思想可能晚 20 年才进入主流。ReAct 的"工具即感知"设计可能不会出现——因为没有人想到 Agent 可以不维护世界模型。

### 12.4 如果 Anthropic 没有 MCP

如果 Anthropic 2024 年没有发布 MCP，Agent 的工具生态可能继续碎片化——每个框架有自己的工具格式，没有跨平台标准。**MCP 是 Agent 基础设施化的关键一步——它把工具调用从"每框架定制"变成"通用协议"。**

> 🎯 **路径依赖的核心教训**：Agent 史上的关键转折点，几乎都依赖"**对的思想 × 对的人 × 对的技术条件 × 对的时机**"的交叉。ReAct 需要 GPT-3 + CoT + function calling 同时成熟；AutoGPT 的爆发需要 ReAct + GitHub 开源文化 + GPT-4 发布；MCP 的成功需要 Anthropic 的行业地位 + 开发者社区的需求。**没有任何单一因素是充分的。**

---

## 13. 开放问题

1. **Agent 能否实现真正的"完全自主"？** AutoGPT 式的完全自主在大多数任务上失败。人机协作（human-in-the-loop）是否是 Agent 的终极形态？

2. **推理 Agent（o1/R1）的"搜索"本质是什么？** 它是 MCTS 在语言空间的推广吗？还是有根本不同？推理搜索能否扩展到无限长？

3. **多 Agent 系统的理论基础是什么？** LLM Agent 间的协作是 emergent（涌现）还是 designed（设计的）？最优的多 Agent 拓扑结构（辩论 / 分工 / 层级）是什么？

4. **Agent 的记忆系统能否逼近人类？** Generative Agents 的 memory stream + reflection 是第一步，但远不如人类的情景记忆/语义记忆/程序记忆。终身学习 Agent 的记忆架构应该是什么？

5. **Agent 安全：如何防止 Agent 被恶意指令劫持？** Agent 调用工具意味着它可以执行真实操作（删文件 / 发邮件 / 转账）。如何构建 Agent 的信任栈？

6. **Agent 会取代软件工程师吗？** SWE-bench 的解决率从 2% 涨到 50%+——但这意味着"修 bug"，不是"从零构建系统"。Agent 与人类工程师的协作模式是什么？

7. **Agent 的"统一架构"是什么？** GPS/Soar 试图用"问题空间搜索"统一所有认知。LLM 时代，Agent 的统一架构是什么？是 ReAct + MCP + memory 的组合，还是某种更深层的东西？

---

## 14. 配套资源

### 14.1 项目内

| 资源 | 链接 | 定位 |
|------|------|------|
| Agent 地基 | [00-为什么需要Agent](./00-为什么需要Agent.md) | ReAct 循环 |
| 范式对比 | [01-经典Agent范式对比](./01-经典Agent范式对比.md) | ReAct/Plan-Execute/Reflexion |
| 工具调用 | [02-工具调用工程](./02-工具调用工程.md) | function calling / MCP |
| 规划搜索 | [03-规划与搜索](./03-规划与搜索.md) | ToT / MCTS / Plan-Execute |
| 记忆机制 | [04-记忆机制](./04-记忆机制.md) | working / episodic / semantic memory |
| 实战案例 | [Open-AutoGLM 手机 Agent](./实战案例-Open-AutoGLM手机Agent/) | 端到端 Agent |
| RL 思想史 | [`讲透RL/HISTORY.md`](../讲透RL/HISTORY.md) | RL Agent 范式转移 |
| AI 思想史方法论 | [`讲透AI历史/00`](../讲透AI历史/00-为什么学AI历史.md) | 本篇方法论基础 |
| 范式转移 | [`讲透AI历史/advanced/01`](../讲透AI历史/advanced/01-范式转移的库恩分析.md) | 库恩框架 |
| 苏煜访谈 | [第139集-苏煜-Agent技术史](../访谈及其他/张小珺访谈精读/) | Agent 四幕进化史 |

### 14.2 经典论文（按时间线）

| 年份 | 论文 | 历史地位 |
|------|------|---------|
| 1957 | Newell-Shaw-Simon, *GPS* | Agent 第一个实例——问题空间搜索 |
| 1976 | Newell-Simon, *PSSH* | 符号主义 Agent 公理 |
| 1986 | Brooks, *Elephants Don't Play Chess* | 反符号主义——无表征智能 |
| 1987 | Bratman, *Intention, Plans, and Practical Reason* | BDI 行动理论哲学根 |
| 1987 | Laird-Newell-Rosenbloom, *Soar* | 认知架构巅峰 |
| 1991/95 | Rao-Georgeff, *BDI Agents* | BDI 形式化 |
| 1993 | Anderson, *ACT-R* | 认知建模路线 |
| 2022 | Wei et al., *Chain-of-Thought* | LLM 推理能力涌现 |
| 2022 | Yao et al., *ReAct* | **LLM Agent 范式定义** |
| 2023 | Richards, *AutoGPT* | Agent 病毒时刻 |
| 2023 | Nakajima, *BabyAGI* | 极简自主 Agent |
| 2023 | Park et al., *Generative Agents* | 认知架构 LLM 复活 |
| 2023 | Wang et al., *Voyager* | 终身学习 Agent |
| 2023 | Schick et al., *Toolformer* | 自学工具使用 |
| 2023 | Yao et al., *Tree-of-Thoughts* | 搜索式推理 |
| 2023 | Jimenez et al., *SWE-bench* | Agent 评测基准 |
| 2023 | Zhou et al., *WebArena* | Web Agent 评测 |
| 2024 | Anthropic, *MCP* | 工具调用标准化 |
| 2024 | Cognition, *Devin* | 第一个 AI 软件工程师 |

### 14.3 关键书籍

| 书 | 作者 | 定位 |
|----|------|------|
| *Mind as Machine* (2006) | Margaret Boden | 认知科学/Agent 史巨著 |
| *The Quest for Artificial Intelligence* (2009) | Nils Nilsson | AI 通史 |
| *Intention, Plans, and Practical Reason* (1987) | Michael Bratman | BDI 哲学根 |
| *An Introduction to MultiAgent Systems* (2009) | Michael Wooldridge | MAS 教材 |

---

## 15. 费曼回炉

> L2 自检：能不能用大白话把 Agent 思想史讲清楚？

### F2 卡壳点

- **卡点 A**：长期以为"Agent 是 LLM 时代的新发明"——ReAct/AutoGPT 是全新概念。重读史料后才钉死：**Agent 不是新事物——GPS 1957 年就是 Agent，BDI 1987 年就定义了信念-欲望-意图循环**。ReAct 的 Thought-Action-Observation 和 BDI 的 Belief-Intention-Action 是同一个行动理论的不同实现。**Agent 走了 70 年，结构没变，引擎从"手工编码"变成了"语言模型"。**

- **卡点 B**：以为认知架构（BDI/Soar/ACT-R）是"失败的旧范式"。重读 Generative Agents 论文才发现——记忆流 + 反思 + 计划完全是 ACT-R/Soar 的认知架构组件的 LLM 版。**认知架构没有失败，只是"超前了 30 年"——等 LLM 提供可规模化的推理引擎，旧思想全部复活。**

- **卡点 C**：以为 RL Agent 和 LLM Agent 是"前后关系"（RL→LLM）。重读后意识到它们是**平行进化**——RL 从环境交互学策略（bottom-up），LLM 从语言推理做决策（top-down）。o1/R1 是两条路线的**合流**。Agent 不是线性进化，是多线平行+交叉融合。

### F3 术语翻译

- **认知架构（cognitive architecture）** → 一个完整的"心智蓝图"——包括感知/记忆/学习/决策/行动的统一计算框架。GPS/Soar/ACT-R 是符号版，Generative Agents 是 LLM 版
- **BDI（信念-欲望-意图）** → 你相信什么（信念）、想要什么（欲望）、决定去做什么（意图=承诺）。ReAct 的 Thought 就是"形成意图"这一步
- **Subsumption 架构** → 不搞"先想后做"的流水线，让多个行为层并行跑——高层可以覆盖低层。像一个公司：前线员工（低层行为）自动处理日常，只有特殊情况才上报经理（高层）
- **MCP** → 给 Agent 工具调用定的"统一插座标准"——以前每个工具有自己的插头（格式），现在统一成 USB-C

### F4 回炉

- **v1（错误直觉）**：以为 Agent 的历史是"从 GPS 到 AutoGPT 到 Devin，越来越自主、越来越厉害"的线性进步。
- **v2（修正后）**：Agent 的历史是**四次范式转移**，每次转移都是核心思想的"换问法"：从"如何搜索问题空间"（GPS）到"agent 的内部认知结构应该是什么"（BDI/Soar）到"如何从试错中学习策略"（RL Agent）到"如何让语言模型自主推理+行动"（LLM Agent）。而且**旧范式（BDI/Soar/ACT-R/Brooks）没有死——它们的核心思想在 LLM Agent 中全部复活**。diff 在于从"进步叙事"升级为"**思想复活的循环叙事**"——Agent 的历史不是"新取代旧"，而是"旧思想等待新引擎"。

---

📌 **下一步**

1. **回到** [00-为什么需要Agent](./00-为什么需要Agent.md) 理解 ReAct 循环
2. **深入** [01-经典Agent范式对比](./01-经典Agent范式对比.md) 看三种范式实测
3. **读** [`讲透AI历史/00`](../讲透AI历史/00-为什么学AI历史.md) 理解思想史方法论
4. **读** [`讲透RL/HISTORY.md`](../讲透RL/HISTORY.md) 理解 RL Agent 与 LLM Agent 的平行进化
5. **读** 苏煜访谈（[第139集精读](../访谈及其他/张小珺访谈精读/)）理解 Agent 四幕进化史
6. **思考** §13 的 7 个开放问题——每个都是博士论文级方向

---

### ✍️ 思考题

1. **方法论题**：如果用一个词概括 Agent 70 年思想史的核心矛盾，你会选什么？（提示：编码 vs 学习？推理 vs 行动？封闭世界 vs 开放世界？自主 vs 可控？）
2. **反事实题**：如果 2022 年 Yao 没有发表 ReAct，LLM Agent 会怎样发展？可能延迟多少年？
3. **判断题**：BDI/Soar/ACT-R 是"被淘汰的旧范式"还是"超前了 30 年的正确思想"？给出你的判断和理由。
4. **批判题**：AutoGPT 式"完全自主 Agent"是 Agent 的终极目标还是过渡形态？人机协作是否是更好的终态？
5. **延伸题**：选一个当前热门 Agent 方向（如 Agent OS / Agent 训练 / Agent 安全），用思想史视角分析——它的"前世"是什么？思想是否真正新？可能的失败模式是什么？
