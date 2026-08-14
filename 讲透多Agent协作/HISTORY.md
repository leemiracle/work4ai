# 讲透多Agent协作 · 思想史

> **一句话定位**：从 1944 年 von Neumann-Morgenstern 的博弈论到 2026 年的 LLM 多 Agent 框架，"多个智能体如何协作"这个问题被问了 80 年——它的历史不是"协作越来越高效"的线性进步，而是四次范式转移（理性博弈→分布式 AI→涌现自组织→语言协商），每次转移都伴随一个核心思想的"换问法"：从"理性个体如何最优地互动"到"多个程序如何分工"，从"如何设计涌现"到"让语言模型自己谈判下一步该做什么"。

> 配套：[`讲透AI历史/00-为什么学AI历史`](../讲透AI历史/00-为什么学AI历史.md)（方法论）+ [`讲透AI历史/advanced/01-范式转移的库恩分析`](../讲透AI历史/advanced/01-范式转移的库恩分析.md)（库恩框架）+ [`讲透Agent/HISTORY.md`](../讲透Agent/HISTORY.md)（单 Agent 思想史，互补）+ [`讲透群体智能/`](../讲透群体智能/)（涌现 vs 编排）+ [本系列 README](./README.md)

---

## 0. 方法论

> 本篇遵循 [`讲透AI历史`](../讲透AI历史/) 的方法论：**思想史 > 年代史**。

**年代史**会这样写：

```
1944  von Neumann & Morgenstern, Theory of Games
1950  Nash 均衡
1975  Holland, 遗传算法
1980  Smith, Contract Net Protocol
1984  Axelrod 囚徒困境锦标赛
1984  Santa Fe Institute 成立
1986  Minsky, Society of Mind
1987  Reynolds, Boids 群集模型
1992  Dorigo, 蚁群优化
1995  Kennedy & Eberhart, 粒子群优化
1995  Wooldridge & Jennings, MAS 综述
2002  Wooldridge, MAS 教材
2023  CAMEL / Generative Agents / ChatDev / MetaGPT / AutoGen / Du 辩论
2024  CrewAI / OpenAI Swarm / LangGraph / AutoGen v0.4
2025  Anthropic 多 agent 研究系统
2026  多 Agent 框架工业化
```

这给你事实，但不告诉你**为什么博弈论 1944 年诞生而非 1924 年**；不告诉你**1980s 的分布式 AI 为什么在 2010s 沉寂、又在 2023 年以 LLM 形态复活**；不告诉你**Swarm Intelligence 的"涌现"哲学和 LLM 多 Agent 的"显式编排"哲学是矛盾的**——它们却被统称为"多 Agent"。

**思想史**问的问题：

| 问题 | 在多 Agent 协作史上的体现 |
|---|---|
| 为什么此时此地？ | 为什么 CAMEL/AutoGen/MetaGPT 集中在 2023 年爆发？（答：GPT-3.5/4 + function calling + 开源生态三条件凑齐）|
| 为什么被淘汰？ | 为什么 BDI 多 agent 体系在 2000s 被冷落？（答：手工编码协调规则的成本爆炸——与专家系统同病）|
| 为什么复兴？ | 为什么"多 Agent"概念在 2023 年大爆发？（答：LLM 让 agent 之间可以用自然语言"对话"，不再需要手工设计通信协议）|
| 路径依赖与偶然性 | 如果 Park 没有 Generative Agents 的想法，"LLM 小镇"的范式可能延迟两年 |
| 谁影响了谁？ | von Neumann→Nash→Axelrod→Minsky→Holland→Wooldridge→Park/Du/Li，80 年一脉相承 |

**本篇的五条原则**（承接 [`讲透AI历史`](../讲透AI历史/)）：

1. **思想史 > 年代史**——每个"突破"都问"为什么此时"
2. **路径依赖敏感**——当前"最优多 Agent 框架"可能是历史偶然
3. **失败与成功同等重要**——被淘汰的方向（BDI 多 agent / FIPA 标准）有教训
4. **跨学科**——多 Agent 受博弈论 / 经济学 / 生物学 / 复杂性科学 / 社会学影响
5. **批判性**——不把"赢家"（AutoGen/CrewAI）当真理——可能只是"等到了对的载体（LLM）"

---

## 1. 前夜：博弈论（von Neumann–Nash，1944–1951）

### 1.1 一个数学家定义了"互动理性"

1944 年，**John von Neumann**（冯·诺依曼）和经济学家 **Oskar Morgenstern** 出版了 *Theory of Games and Economic Behavior*（《博弈论与经济行为》），普林斯顿大学出版社，640 页。这本书做了一件此前没人做过的事：**把"多个理性决策者之间的互动"变成一个严格的数学学科**。

von Neumann 在 1928 年已经证明了**极小极大定理**（Minimax Theorem）——零和博弈中，每个参与者都有一个最优的混合策略，使得无论对手怎么做，自己的期望收益不低于某个值。1944 年的著作把这个结果推广到多人博弈，并引入了**期望效用理论**（expected utility theory）——理性人应该最大化期望效用。

> 🎯 **思想史定位**：博弈论是多 Agent 协作的**数学前夜**。它第一次形式化地提出："当多个决策者互相影响时，'最优'不再是一个人的事——我的最优策略取决于你做什么，你的最优策略取决于我做什么。"这种**耦合性**（interdependence）是多 Agent 系统的灵魂。

### 1.2 Nash 均衡：互动中的"不动点"

1950 年，22 岁的 **John Nash** 在普林斯顿完成了 28 页的博士论文 *Non-Cooperative Games*。1951 年发表在 *Annals of Mathematics* 第 54 卷第 2 期。

Nash 证明了一个惊人的定理：**任何有限博弈（n 个玩家，每个有有限个纯策略），都至少存在一个均衡点**——在这个点上，没有任何玩家能通过单方面改变策略来获益。

这就是 **Nash 均衡**（Nash Equilibrium）。它推广了 von Neumann 的零和解：**即使是非零和、非合作的多人博弈，也存在某种"稳定状态"**。

Nash 均衡的深刻之处在于：它定义了一种**集体理性**——不是"每个人最大化自己的收益"（那可能导致囚徒困境），而是"在给定他人策略的前提下，没有人有动机偏离"。**这是一种多 Agent 的"静止状态"——不是最优，但稳定。**

> 🎯 **思想史洞察**：Nash 均衡是"多 Agent 协作"概念史上**第一个严格定义的"均衡态"**。它告诉你：多个自利个体的互动不一定会达到全局最优，但会收敛到某种**局部稳定**。这个洞察在 80 年后被 LLM 多 Agent 系统继承——当你让多个 LLM Agent "辩论"或"谈判"时，你本质上在观察它们**趋向某种 Nash 均衡的过程**。

### 1.3 博弈论的局限：为什么它不是"多 Agent 系统"

博弈论奠定了数学基础，但它有致命局限——它假设：

1. **完全理性**（perfect rationality）：每个参与者都是"理性经济人"，无限计算能力
2. **共同知识**（common knowledge）：每个人都知道规则，知道别人知道规则，知道别人知道别人知道……
3. **静态分析**：博弈论分析的是"均衡点"，不是"如何动态地达到均衡"

这些假设在 1980s 受到根本挑战——真实的 agent（人类、机器人、软件程序）**不是完全理性的、信息是不完全的、互动是动态的**。这就催生了**分布式 AI**。

---

## 2. 第一次范式转移：分布式 AI / MAS（1980s）

### 2.1 旧范式的反常累积

到 1980s 初，传统 AI（符号主义 GOFAI）面临一个根本问题：**真实世界的任务太大、太分散，单个中心化系统搞不定**。

典型案例：**分布式车辆监控**（Distributed Vehicle Monitoring, DVMT）——Victor Lesser 和 Daniel Corkill 1983 年在 UMass Amherst 做的经典实验。想象一组传感器分布在高速公路上，每个只能看到一小片区域。如何让它们**协作**拼出整条路的车辆轨迹？

单中心方案的问题：通信带宽不够、单点故障、延迟太高。**必须让多个节点各自处理局部信息，再协调汇总**。

这就是**分布式 AI**（Distributed AI, DAI）的起源动机——从"一个大脑管所有事"到"多个大脑各管一摊、协调合作"。

> 🎯 **范式转移**：博弈论问"理性个体如何最优互动"，DAI 问"**多个计算节点如何分工协作**"。前者假设完全理性和共同知识，后者面对的是**有限理性、不完全信息、通信受限**的真实计算环境。这是从"数学"到"工程"的换问法。

### 2.2 Contract Net Protocol：第一个多 Agent 协作协议

1980 年，RPI 的 **Reid G. Smith** 在 *IEEE Transactions on Computers* 发表了 *The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver*。

Contract Net 的设计极其优雅，模拟人类经济中的**招标-投标**过程：

```
1. Manager（管理者）广播任务
2. 多个 Contractor（承包商）评估自己的能力和成本，提交投标
3. Manager 选最优投标者，"签约"
4. Contractor 执行任务，回报结果
```

这是一个**去中心化的任务分配机制**——不需要全局调度器，不需要每个节点知道全局状态。Manager 只需要广播任务，Contractor 只需要评估自己。

> ⚠️ **反常识预警**：Contract Net Protocol 出现在 1980 年——**比 OpenAI Swarm 的 handoff 抽象早了 44 年**。Swarm 的"一个 agent 把任务交给另一个"和 Contract Net 的"manager 派任务给 contractor"在哲学上是同一个东西。**多 Agent 协作的核心原语，40 年没变过。**

### 2.3 Wooldridge-Jennings：MAS 学科的诞生

1995 年，伦敦大学玛丽女王学院的 **Michael Wooldridge** 和南安普顿大学的 **Nicholas Jennings** 在 *The Knowledge Engineering Review* 第 10 卷第 2 期发表了综述 *Intelligent Agents: Theory and Practice*。这篇论文（及后来的教材 *An Introduction to MultiAgent Systems*, 2002/2009）正式定义了 **Multi-Agent Systems（MAS，多智能体系统）** 这一学科。

Wooldridge-Jennings 给 agent 下了经典定义——一个 agent 是具有以下属性的计算机系统：

1. **自主性**（autonomy）：不需要人干预，自己运行
2. **社交性**（social ability）：能和其他 agent 交互（某种 agent 通信语言）
3. **反应性**（reactivity）：能感知环境并响应
4. **主动性**（pro-activeness）：能主动采取行动实现目标

**MAS 的核心问题**：当多个这样的 agent 共存于一个环境中，它们如何**协调**（coordination）、**协作**（cooperation）、**谈判**（negotiation）？

MAS 时代（1980s-2000s）产生了大量经典成果：
- **BDI 多 agent**：把 Bratman 的信念-欲望-意图模型扩展到多 agent（Rao-Georgeff 1995）
- **Agent 通信语言**：KQML（Knowledge Query and Manipulation Language）、FIPA-ACL
- **多 agent 规划**：如何让多个 agent 共同制定不冲突的执行计划
- **拍卖与机制设计**：把经济学引入多 agent 资源分配
- **共识算法**：多个 agent 如何对共享状态达成一致

### 2.4 MAS 的失败与"漫长的冬天"

到 2000s 中期，MAS 作为独立学科开始**萎缩**。原因：

1. **手工编码成本爆炸**——每个 agent 的行为规则、通信协议、协调机制都要人工设计。跟专家系统同病。
2. **FIPA 标准化运动失败**——试图制定统一的 agent 通信标准（FIPA-ACL），但因为太重、太理想化，工业界不采用。
3. **机器学习崛起**——2000s 是 SVM/统计学习的天下，"手工设计规则"的 MAS 被边缘化。
4. **没有杀手级应用**——MAS 的研究产出大量论文和玩具系统，但没有一个进入日常使用。

> 🎯 **思想史洞察**：MAS 没有失败——它"超前了 20 年"。它的核心思想（去中心化协调、任务分配、共识、谈判）在 2023 年被 LLM 多 Agent 系统**全部复活**。AutoGen 的"多 agent 对话"是 MAS 谈判的 LLM 版；MetaGPT 的"角色分工"是 MAS 协调的 LLM 版；Contract Net 的"招标投标"是 orchestrator-worker 的前身。**思想不死，只是等待新引擎。**

---

## 3. Swarm Intelligence（1990s）

### 3.1 从"设计协作"到"涌现协作"

当 MAS 学派在**显式设计**协作协议时，另一个流派走了截然相反的路：**不设计协作，让协作从简单规则中涌现**。

这就是 **Swarm Intelligence（群体智能）** 的核心哲学——**复杂的集体行为可以从大量简单个体的局部交互中涌现出来，无需任何中央控制**。

这个思想的生物学灵感来自：
- **蚁群**：单只蚂蚁智力极低，但蚁群能找到最短路径、分工协作、建造复杂巢穴
- **蜂群**：蜜蜂通过"8 字舞"传递食物位置信息
- **鸟群/鱼群**：大量个体同步运动，形成优雅的集体模式

### 3.2 Boids：第一个涌现模型

1987 年， Symbolics 公司的 **Craig Reynolds** 发表了 *Flocks, Herds, and Schools: A Distributed Behavioral Model*。他设计了 **Boids**——一个鸟群模拟程序，每个"鸟"（boid）只遵循三条简单规则：

1. **分离**（Separation）：避免和邻居太近
2. **对齐**（Alignment）：朝邻居的平均方向飞
3. **凝聚**（Cohesion）：朝邻居的平均位置靠拢

**就这三条规则**，Boids 模拟出了极其逼真的鸟群运动——没有 leader，没有全局规划，纯粹从局部规则涌现。

Reynolds 的 Boids 后来被用在电影特效中（蝙蝠侠Returns 的企鹅群、狮子王的角马群）。更重要的是，它证明了一个深刻的原则：

> **全局秩序可以从局部规则中涌现，无需任何 agent 知道"全局状态"。**

### 3.3 蚁群优化（ACO）：从蚂蚁到算法

1992 年，布鲁塞尔自由大学的 **Marco Dorigo** 在博士论文 *Optimization, Learning and Natural Algorithms* 中提出了 **Ant Colony Optimization（蚁群优化，ACO）**。

灵感：蚂蚁觅食时会在路径上留下**信息素**（pheromone）。短路径上的蚂蚁往返更快，信息素积累更多，吸引更多蚂蚁走这条路——**正反馈**导致蚁群最终收敛到接近最优的路径。

Dorigo 把这个过程变成了一个优化算法：人工"蚂蚁"在解空间中搜索，根据信息素浓度选择路径，不断更新信息素。ACO 在旅行商问题（TSP）、路由优化、调度问题中表现出色。

### 3.4 粒子群优化（PSO）

1995 年，社会心理学家 **James Kennedy** 和电气工程师 **Russell Eberhart** 发表了 *Particle Swarm Optimization*（IEEE International Conference on Neural Networks）。

PSO 的灵感来自鸟群觅食：每个"粒子"（候选解）在解空间中飞行，根据两个信息调整方向：
1. **自身历史最优位置**（pbest）——"我曾经找到的最好的地方"
2. **群体历史最优位置**（gbest）——"整个群体找到的最好的地方"

PSO 极其简洁——几行代码就能实现——却在大量连续优化问题上表现出色。

### 3.5 Stigmergy：间接协调的深刻原理

群体智能的核心机制是 **Stigmergy（间接协同 / 痕迹诱导）**——agent 不直接通信，而是通过**修改环境**来间接影响其他 agent 的行为。蚂蚁的信息素是 stigmergy 的经典案例。

> 🎯 **思想史定位**：Stigmergy 是多 Agent 协作史上**最反直觉的思想**——**零直接通信也能实现高效协调**。它揭示了：协作不一定需要"对话"，环境本身就是通信介质。这个洞察在 2023 年的 LLM 多 Agent 系统中几乎完全被遗忘——现代框架全都是"直接对话"式协作。**但 stigmergy 的思想迟早会回来**——当 agent 数量达到上百时，O(N²) 的直接通信撑不住，环境介导的间接协调是唯一的出路。

---

## 4. 第二次范式转移：复杂自适应系统

### 4.1 Santa Fe Institute 与复杂性科学

1984 年，**Santa Fe Institute（SFI）** 在新墨西哥州成立——由 Los Alamos 国家实验室的一群物理学家（包括 Murray Gell-Mann）和经济学家（包括 Kenneth Arrow）创立。SFI 的使命是研究**复杂自适应系统**（Complex Adaptive Systems, CAS）。

CAS 的核心问题：**大量相互作用的个体，如何自发产生宏观层面的秩序、适应性和复杂性？**

这个问题横跨物理学（相变）、生物学（进化、生态系统）、经济学（市场）、社会学（城市、文化）——它是多 Agent 思想的**最广义版本**：agent 不一定是程序，可以是分子、细胞、生物、人、公司。

### 4.2 Holland：遗传算法与 CAS 理论

密歇根大学的 **John Holland** 是 CAS 理论的奠基人之一。1975 年，他出版了 *Adaptation in Natural and Artificial Systems*，提出了**遗传算法**（Genetic Algorithm, GA）——模拟自然选择的优化算法。

Holland 的贡献不只是 GA——他后来在 SFI 系统提出了 **CAS 理论**：
- **涌现**（emergence）：宏观行为不能从微观规则简单推导
- **适应**（adaptation）：系统通过反馈不断改变自身
- **非线性**（nonlinearity）：整体不等于部分之和

Holland 的 **Echo 模型**（1990s）是 CAS 的计算实现——一个虚拟生态系统中，多个 agent 互相交换资源、竞争、进化。

### 4.3 Minsky：Society of Mind

1986 年，MIT 的 **Marvin Minsky** 出版了 *The Society of Mind*（《心智社会》）。Minsky 提出了一个惊人的假说：

> **人类心智不是一个统一的智能体，而是由成百上千个微小的、各自专门化的"心智代理"（agents of mind）组成的"社会"。** 这些心智代理各自做极简单的事，但它们的大量组合产生了我们称之为"智能"的宏观行为。

Minsky 的洞察把多 Agent 思想推到了**认知科学的最前沿**——如果人类心智本身就是多 Agent 系统，那么"多 Agent 协作"就不只是一个工程问题，而是**智能的本质结构**。

> ⚠️ **反常识预警**：2023 年 Du et al. 的"多 agent 辩论提升推理"论文（arXiv:2305.14325）在 LLM 圈引发轰动——"让多个 LLM 实例辩论就能提升推理质量"。但 Minsky 1986 年就提出了同样的思想：**"心智社会"的内部辩论就是智能的来源**。Du 的贡献不是"发明"了多 agent 辩论，而是**验证了 Minsky 假说在 LLM 上的可计算性**。

### 4.4 复杂性科学的遗产

CAS / Swarm Intelligence 这一脉（1980s-2000s）给多 Agent 协作留下了深刻遗产：

1. **涌现 > 设计**：好的多 Agent 系统不靠全局规划，靠局部规则涌现
2. **Stigmergy > 直接通信**：环境是最好的协调介质
3. **多样性 > 单一性**：异质 agent 比同质 agent 更鲁棒
4. **非线性 > 线性**：整体能力 ≠ 部分能力之和

但这一脉也有局限：它**太"自下而上"了**——难以精确控制行为。你需要什么结果，全靠调参碰运气。这让它在工程应用中受限。

---

## 5. 经济学与社会模拟（Axelrod）

### 5.1 囚徒困境锦标赛

1980 年，密歇根大学的政治学家 **Robert Axelrod** 组织了一场**囚徒困境计算机锦标赛**——邀请各领域的学者提交策略程序，让它们在反复囚徒困境中对弈。

结果震惊了所有人：冠军是 **Tit for Tat（一报还一报）**——由心理学家 **Anatol Rapoport** 提交的策略，只有 4 行代码：
1. 第一回合合作
2. 之后每一回合复制对手上一回合的行为

Tit for Tat 的胜利揭示了**合作可以如何涌现**——即使没有中央权威、没有道德约束，"以牙还牙"这种简单策略就能在自利个体中**维持长期合作**。

Axelrod 在 1984 年出版的 *The Evolution of Cooperation*（《合作的进化》）中总结了锦标赛的发现，提炼出成功策略的四个特征：
1. **善良**（nice）：永不先背叛
2. **可激怒**（retaliatory）：被背叛后必须报复
3. **宽容**（forgiving）：报复后愿意回归合作
4. **清晰**（clear）：行为可预测，让对手能学习

> 🎯 **思想史定位**：Axelrod 的锦标赛是多 Agent 协作史上**最重要的实验之一**。它证明了：**合作的演化不依赖于理性或道德——它可以从简单的互动规则中涌现**。这个洞察直接影响了后来的 LLM 多 Agent 设计——当你让多个 agent"辩论"或"投票"时，你本质上在运行一个 Axelrod 式的锦标赛。

### 5.2 从博弈论实验到社会模拟

Axelrod 的工作催生了一整个领域：**基于 agent 的社会模拟**（Agent-Based Social Simulation, ABSS）。研究者用计算机模拟大量虚拟"人"（agent）的互动，研究社会现象如何涌现—— segregation（居住隔离）、rumor spreading（谣言传播）、opinion dynamics（舆论动力学）。

最经典的是 **Schelling 的隔离模型**（Thomas Schelling, 1971）——每个 agent 只要求"我的邻居中至少有 30% 和我同类"。结果：即使每个个体都接受混合居住，宏观上仍然涌现出高度隔离的社区。**微观善意 + 互动 = 宏观非预期结果**。

这条线索（Axelrod → ABSS → Generative Agents）在 2023 年被 Park et al. 的斯坦福小镇重新点燃。

---

## 6. 第三次范式转移：LLM 多 Agent（2023）

### 6.1 三条件凑齐

2023 年是多 Agent 协作的**大爆炸之年**。在短短几个月内，至少 6 篇里程碑论文同时出现——这在科学史上极为罕见。为什么是 2023 年？

**三个条件同时成熟**：

1. **GPT-3.5/4 的推理能力**（2022 底-2023 初）：LLM 第一次具备了"可以对话、可以推理、可以扮演角色"的能力
2. **思维链 + function calling**（2022-2023）：Wei et al. 的 CoT 让 LLM 能"逐步思考"；OpenAI 的 function calling 让 LLM 能"调用工具"
3. **开源生态成熟**：LangChain、Hugging Face 提供了快速搭建 agent 的基础设施

**关键洞察**：LLM 让 agent 之间的通信从"手工设计的协议语言（KQML/FIPA-ACL）"变成了**自然语言**。这是革命性的——你不再需要为 agent 之间的每种交互设计一套消息格式，它们直接"说话"就行。

> 🎯 **范式转移**：MAS 时代问"如何设计 agent 通信协议"，LLM 时代问"**如何让 agent 用自然语言自主协商**"。前者是工程师视角（设计协议），后者是导演视角（设计角色和场景）。这是从"协议工程"到"提示工程"的换问法。

### 6.2 CAMEL：第一个 LLM 多 Agent 框架

2023 年 3 月 31 日，阿卜杜拉国王科技大学（KAUST）的 **Guohao Li** 等人提交了 CAMEL（arXiv:2303.17760），被 NeurIPS 2023 接收。

CAMEL 的核心创新是 **role-playing（角色扮演）框架**：两个 LLM agent 分别扮演"用户"（AI User）和"助手"（AI Assistant），通过 **inception prompting**（初始提示）被引导自主协作完成任务。用户 agent 给指令，助手 agent 执行并反馈，循环直到任务完成。

CAMEL 的贡献不只是框架——它还生成了大量"agent 对话数据"，用于研究 LLM 在多 agent 场景下的行为。CAMEL 是**第一个系统性地探索"LLM agent 社会行为"的工作**。

### 6.3 ChatDev：LLM 软件公司

2023 年 7 月 16 日，清华大学的 **Chen Qian** 等人提交了 ChatDev（arXiv:2307.07924，ACL 2024）。ChatDev 把软件公司的角色（CEO → CTO → 程序员 → 测试员）全部用 LLM agent 扮演，让它们通过"对话链"（chat chain）协作完成软件开发。

ChatDev 的关键创新是 **communicative dehallucination（通信去幻觉）**——agent 之间的多轮对话本身就能减少单个 agent 的幻觉。这呼应了 §4.3 中 Minsky 的"心智社会"思想。

### 6.4 MetaGPT：SOP 即架构

2023 年 8 月 1 日，DeepWisdom 的 **Sirui Hong** 等人（包括 Jürgen Schmidhuber）提交了 MetaGPT（arXiv:2308.00352）。

MetaGPT 的核心洞察是：**人类组织的效率来自标准化操作流程（SOP）**。MetaGPT 把 SOP 编码为 prompt 序列，让不同角色的 agent 按照流水线协作——产品经理写 PRD，架构师设计系统，工程师写代码，测试员做 QA。

MetaGPT 明确提出：**naive chaining（朴素串联）会导致级联幻觉**——多个 LLM 简单地首尾相连，错误会逐层放大。SOP 的作用是在每一步加入**人类式的中间结果验证**，降低错误传播。

### 6.5 AutoGen：通用多 Agent 对话框架

2023 年 8 月 16 日，微软的 **Qingyun Wu** 等人提交了 AutoGen（arXiv:2308.08155）。AutoGen 的定位是**通用基础设施**——提供可定制、可对话的 agent 抽象，让开发者用几行代码就能搭起多 agent 系统。

AutoGen 的关键设计：
- agent 可以是 LLM 驱动的、人类驱动的、或工具驱动的
- 用自然语言或代码编程 agent 的交互行为
- 支持各种复杂度的应用

AutoGen 在 2024 年被重写为 v0.4，引入了 **actor 模型 + 异步消息** 架构——这标志着多 Agent 框架从"研究原型"向"生产系统"演进。

### 6.6 2023 大爆炸的思想史意义

CAMEL（3月）→ Generative Agents（4月）→ Du 辩论（5月）→ ChatDev（7月）→ MetaGPT（8月）→ AutoGen（8月）——半年内 6 篇里程碑论文密集爆发。

这并非偶然：GPT-4 在 2023 年 3 月发布，function calling 在 6 月开放。**这些论文几乎都是"等 GPT-4 一出来就立刻做的"**——它们是同一个范式的不同切面。

> 🎯 **反常识**：很多人以为 CAMEL/AutoGen/MetaGPT 是"全新发明"。实际上，它们的**核心机制全部来自 MAS 时代**——CAMEL 的角色扮演是 MAS negotiation 的 LLM 版；MetaGPT 的 SOP 是 MAS coordination protocol 的 LLM 版；AutoGen 的 agent 对话是 MAS agent communication 的 LLM 版。**LLM 没有发明多 Agent 协作，它只是让 20 年前的思想终于"能跑了"。**

---

## 7. Stanford Generative Agents（2023）

### 7.1 小镇实验

2023 年 4 月 7 日，斯坦福大学的 **Joon Sung Park** 等人（指导教师 Michael Bernstein 和 Percy Liang）提交了 *Generative Agents: Interactive Simulacra of Human Behavior*（arXiv:2304.03442，UIST 2023 最佳论文）。

他们在 The Sims 风格的虚拟小镇 **Smallville** 中放了 **25 个 LLM agent**，每个有自己的人格、职业、关系。这些 agent 会自主地起床、做饭、上班、社交、形成意见、发起对话。

结果令人惊叹：研究者只给了**一个种子信息**——"某个 agent 想办情人节派对"——agent 们就在接下来的两天里**自主地传播邀请、认识新朋友、邀约、协调时间，最终一起出现在派对上**。

### 7.2 认知架构的复活

Generative Agents 的技术贡献是一个三组件**认知架构**：

1. **Memory Stream（记忆流）**：用自然语言记录 agent 的所有经历，按时间排序
2. **Reflection（反思）**：定期把低层记忆综合成高层洞察（"我最近好像花太多时间在工作上"）
3. **Planning（计划）**：基于记忆和反思，生成行动计划

消融实验证明：去掉任何一个组件，agent 行为的"可信度"显著下降。

> ⚠️ **反常识预警**：很多人把 Generative Agents 当作"全新突破"。但仔细看它的架构——记忆流 + 反思 + 计划——**这完全是 1987-1993 年 BDI/Soar/ACT-R 认知架构的 LLM 版**。BDI 的 Belief = Memory Stream；Intention = Planning；Soar 的 chunking = Reflection。**认知架构没有失败，它只是"超前了 30 年"——等 LLM 提供可规模化的推理引擎，旧思想全部复活。**（参见 [`讲透Agent/HISTORY.md`](../讲透Agent/HISTORY.md) §2）

### 7.3 Generative Agents 的独特贡献

尽管认知架构是旧的，Generative Agents 有真正的创新：

1. **第一次用 LLM 实现了"可信的人类行为模拟"**——之前的社会模拟（Schelling、Axelrod）用的是极简规则 agent，Generative Agents 第一次让 agent 有了"人格"
2. **emergent social behavior（涌现社会行为）**——情人节派对的自主组织是真正的涌现，不是被设计的
3. **把 CAS / Swarm 的涌现哲学带回了 LLM 时代**——Generative Agents 证明，即使每个 agent 是 LLM（"聪明"），涌现仍然会发生

Generative Agents 是**两条传统（MAS 认知架构 + CAS 涌现）在 LLM 上的汇流点**——这是它真正的思想史地位。

---

## 8. 多 Agent 辩论与协作范式

### 8.1 Du 的"心智社会"实验

2023 年 5 月 23 日，MIT 的 **Yilun Du**、**Shuang Li**、**Antonio Torralba**、**Joshua Tenenbaum** 和 Google 的 **Igor Mordatch** 提交了 *Improving Factuality and Reasoning in Language Models through Multiagent Debate*（arXiv:2305.14325）。

核心方法极其简洁：让**多个 LLM 实例**就同一个问题各自给出答案和推理，然后**多轮辩论**——每个 instance 看到别人的答案后修正自己的，最终收敛到一个共同答案。

实验结果：辩论显著提升了数学推理和策略推理的正确率，并减少了幻觉。

Du 等人明确引用了 Minsky 的 *Society of Mind*，把多 agent 辩论称为 **"society of minds"（心智社会）** 方法。

> 🎯 **思想史定位**：Du 的工作是**博弈论 + 认知科学 + LLM 的三重交汇**。从博弈论看，多 agent 辩论是一个**趋向 Nash 均衡的迭代过程**——每个 agent 根据他人的"策略"（答案）调整自己的策略，直到稳定。从认知科学看，它验证了 Minsky 的"内部辩论 = 智能"假说。从 LLM 看，它发现了一种**不改变模型权重就能提升推理能力**的方法。

### 8.2 辩论的有效条件：多样性

Du 的辩论方法有一个关键前提，很多人忽略了：**辩论要有效，agent 必须有多样性**。

数学上（参见本系列 [`02-数学-协作的形式化`](./02-数学-协作的形式化.md) §6）：设单 agent 答对率 $p$，judge 在"一个对一个错"时选对的概率 $q$。辩论后正确率：

$$P(\text{correct}) = p^2 + 2p(1-p) \cdot q$$

当 $q > 0.5$ 时，辩论严格优于单 agent。但如果所有 agent 是**同一个基模型的副本**——它们会犯**同样的错**——此时 $q \approx 0.5$，增益消失。

这就是"群体幻觉"（collective hallucination）的危险：**多个同质 agent 不仅不会纠正彼此的错误，反而会互相"确认"错误，把幻觉固化。**

> 🎯 **工程教训**：debate 要用**不同模型、不同 prompt、不同温度**的 agent 才有效。同质 agent 的辩论是回音室（echo chamber）。

### 8.3 五种协作范式的思想史根

把 2023-2026 年的所有多 Agent 协作模式拉通看，它们各自有深刻的思想史根：

| 协作范式 | 2023-2026 实现 | 思想史根 |
|---|---|---|
| **Orchestrator-Worker** | Anthropic 多 agent 研究、OpenAI Swarm | Contract Net Protocol（Smith 1980） |
| **Hierarchy / SOP** | MetaGPT、ChatDev | MAS coordination protocols（1980s-90s） |
| **Debate** | Du et al. multi-agent debate | Minsky Society of Mind（1986）+ 博弈论 Nash 均衡 |
| **Role-Playing** | CAMEL | MAS negotiation theory + 社会学角色理论 |
| **Emergent Society** | Generative Agents | CAS / Swarm Intelligence（1980s-90s）+ Schelling/Axelrod 社会模拟 |

**这五种范式没有一种是"新发明"——它们全部是 20-40 年前思想的 LLM 复活。** 这是理解多 Agent 协作史最重要的反常识。

---

## 9. 第四次范式转移：商业化多 Agent 框架（2024–2026）

### 9.1 从论文到产品

2023 年是论文大爆炸，2024-2026 年是**框架工业化**。几个关键节点：

- **OpenAI Swarm**（2024 年 10 月）：极简的 handoff 抽象——一个 agent 可以把控制权"交"给另一个。Swarm 的哲学是"**轻量编排 > 重框架**"。它的名字叫 swarm（群体），但实际是**最显式的中心化编排**，不是真正的涌现自组织——这是术语膨胀的经典案例。

- **CrewAI**（2024 年初）：由 João Moura 发起的框架，用 **角色 + 任务 + 流程** 的简洁抽象快速搭建多 agent 原型。它的定位是"降低多 agent 的入门门槛"。

- **LangGraph 0.2+**（2024-2025）：把 agent 流程建模为**显式状态图**（state graph），支持断点、重放、人审（human-in-the-loop）。它的哲学是"**生产系统需要可控可审计**"。

- **AutoGen v0.4**（2024 年底）：完全重写，引入 **actor 模型 + 异步消息传递**。从"研究原型"进化为"高并发生产系统"。

- **Anthropic 多 agent 研究系统**（2025）：一个 lead agent 派多个 sub-agent 并行搜资料再综合。关键设计：**sub-agent 之间不直接通信，只通过 lead 中转**——这避免了 O(N²) 通信爆炸。Claude 在评审 Claude 写的报告——这是"debate + orchestrator"的工业级实践。

### 9.2 工业化的核心矛盾

2024-2026 年的多 Agent 框架繁荣背后，有一个**根本矛盾**在撕裂整个领域：

**涌现 vs 编排的光谱**

```
←— 涌现（无中心） ───────────── 编排（有中心）—→
   Swarm Intelligence            Orchestrator-Worker
   Generative Agents             MetaGPT / CrewAI
   Stigmergy                     LangGraph / AutoGen
```

- **涌现派**（继承 CAS/Swarm 传统）认为：最好的多 agent 系统应该像蚁群——没有 leader，局部规则涌现全局智能
- **编排派**（继承 MAS 传统）认为：生产系统必须可控、可审计、可复现——必须有显式的流程编排

2024-2026 年的工业化**几乎一边倒地倒向了编排派**——OpenAI Swarm、LangGraph、AutoGen、Anthropic 多 agent 系统，全都是显式编排。

> 🎯 **思想史洞察**：这不是因为"编排比涌现好"，而是因为**当前的 LLM agent 还不够可靠**——涌现需要每个 agent 足够鲁棒，才能让局部规则产生好的全局结果。当前 LLM agent 的幻觉率太高，让它们自由涌现只会产生混乱。**涌现是被可靠性门槛挡在门外的——当 agent 足够可靠时，涌现会回来。**

### 9.3 Brooks 定律的 AI 版回归

2024-2026 年，一个反复被验证的工程教训是 Brooks 定律的 AI 版（参见本系列 [`01-直觉`](./01-直觉-为什么需要多个Agent.md)）：

> **N 个 Agent 之间的通信链路数 = O(N²)，而每个链路都是幻觉/误解/死锁的潜在入口。**

实践一再证明：**3 个笨 Agent 的协作，常常不如 1 个聪明的 Agent + 好的 prompt。** Anthropic 的多 agent 研究系统之所以成功，关键就是 **sub-agent 不直接通信**——它们把 O(N²) 的通信降到了 O(N)。

这呼应了 §3.5 的 stigmergy 原理和 §2.2 的 Contract Net——**大规模系统的协调，必然走向分层或市场化，而非全连接。**

---

## 10. 思想史反思：5 个反常识

### 反常识 1：多 Agent 协作不是 LLM 时代的新发明——它 80 岁了

从 1944 年博弈论到 2023 年 LLM 多 Agent，"多个智能体如何协作"这个问题被问了 80 年。CAMEL/AutoGen/MetaGPT 的核心机制（角色分工、任务分配、通信协议、辩论）全部可以追溯到 MAS 时代（1980s-2000s）。**LLM 没有发明多 Agent 协作，它只是让 20 年前的思想终于"能跑了"。**

### 反常识 2：Swarm Intelligence 和 LLM 多 Agent 是哲学对立面

Swarm Intelligence（蚁群/PSO/ACO）信奉**涌现**——不设计协作，让它从简单规则中自发生长。LLM 多 Agent 框架（AutoGen/LangGraph/CrewAI）信奉**编排**——显式设计每一步的协调流程。**它们却被统称为"多 Agent"，但哲学完全矛盾。** OpenAI Swarm 甚至叫"swarm"却是显式编排——术语膨胀的典型案例。

### 反常识 3：Contract Net Protocol 比 OpenAI Swarm 早 44 年

Smith 1980 年的 Contract Net Protocol——manager 广播任务、contractor 投标、签约执行——和 OpenAI Swarm 2024 年的 handoff 抽象在哲学上是**同一个东西**。**多 Agent 协作的核心原语（任务分配 + 控制权转移），40 年没变过。** 变的只是实现载体：从 RPC 消息到 LLM 对话。

### 反常识 4：BDI/Soar 认知架构没有失败，它在 Generative Agents 中复活

Generative Agents 的"记忆流 + 反思 + 计划"三组件，完全是 1987-1993 年 BDI/Soar/ACT-R 认知架构的 LLM 版。BDI 的 Belief = Memory Stream；Intention = Planning；Soar 的 chunking = Reflection。**认知架构没有失败，它只是"超前了 30 年"。** 这和 [`讲透Agent/HISTORY.md`](../讲透Agent/HISTORY.md) 的核心论点一致：Agent 史不是"新取代旧"，而是"旧思想等待新引擎"。

### 反常识 5：多 Agent 辩论提升推理 = Minsky 1986 年的假说

Du et al. 2023 的"多 agent 辩论提升 LLM 推理"在圈内引发轰动。但 Minsky 1986 年在 *Society of Mind* 中就提出：**人类智能来自心智内部多个 agent 的辩论。** Du 的贡献不是发明了这个思想，而是**验证了 Minsky 假说在 LLM 上的可计算性**。而且 Du 自己在论文中明确引用了 Minsky。

### 反常识 6（附赠）：多 Agent 不如你想的强——同质性陷阱

很多人以为"多个 agent 自然比一个强"。但数学上，如果所有 agent 是同一个基模型的副本（同质），它们的辩论增益几乎为零——因为它们会犯同样的错、互相确认幻觉。**debate 要用多样化的 agent 才有效**。这就是为什么"多 agent 框架繁荣"和"单 agent + 更好 prompt"的争论永远不会有一边完胜——它取决于任务能否分解、agent 是否多样、通信开销是否可控。

---

## 11. 关键人物谱系

```
博弈论根
├─ John von Neumann (1903-1957)
│   └─ 极小极大定理 (1928) → Theory of Games (1944)
├─ John Nash (1928-2015)
│   └─ Nash 均衡 (1950)
├─ Thomas Schelling (1921-2016)
│   └─ 隔离模型 (1971) → 策略行为 → 影响社会模拟
└─ Robert Axelrod (1943-)
    └─ 囚徒困境锦标赛 (1980) → 合作的进化 (1984)

分布式 AI / MAS 根
├─ Victor Lesser (1944-2024)
│   └─ DVMT 分布式车辆监控 (1983)
├─ Reid Smith
│   └─ Contract Net Protocol (1980)
├─ Michael Wooldridge (1966-)
│   └─ Intelligent Agents (1995) → MAS 教材
├─ Nicholas Jennings
│   └─ 与 Wooldridge 合著 MAS 综述
└─ Michael Bratman (1945-) [哲学根]
    └─ BDI 行动理论 (1987)

复杂性科学 / Swarm 根
├─ Marvin Minsky (1927-2016)
│   └─ Society of Mind (1986) → 影响 Du 辩论
├─ John Holland (1929-2015)
│   └─ 遗传算法 (1975) → CAS 理论 → Santa Fe Institute
├─ Craig Reynolds
│   └─ Boids (1987) → 涌现群集
├─ Marco Dorigo (1970-)
│   └─ 蚁群优化 (1992)
├─ James Kennedy & Russell Eberhart
│   └─ 粒子群优化 (1995)
└─ Murray Gell-Mann / Kenneth Arrow
    └─ Santa Fe Institute 联合创始人 (1984)

LLM 多 Agent 根（2023 大爆炸）
├─ Guohao Li (KAUST)
│   └─ CAMEL (2023.03) → role-playing → camel-ai 开源生态
├─ Joon Sung Park (Stanford → OpenAI)
│   └─ Generative Agents (2023.04) → 认知架构复活
├─ Yilun Du (MIT) / Igor Mordatch (Google)
│   └─ Multi-agent debate (2023.05) → Society of Minds
├─ Chen Qian (清华大学)
│   └─ ChatDev (2023.07) → LLM 软件公司
├─ Sirui Hong / Jürgen Schmidhuber (DeepWisdom)
│   └─ MetaGPT (2023.08) → SOP 编排
└─ Qingyun Wu (Microsoft)
    └─ AutoGen (2023.08) → 通用多 agent 对话框架

商业化根（2024-2026）
├─ João Moura → CrewAI (2024)
├─ OpenAI → Swarm (2024.10)
├─ Harrison Chase → LangGraph (2024-2025)
└─ Anthropic → 多 agent 研究系统 (2025)
```

---

## 12. 失败方向

> 失败和成功同等重要——被淘汰的方向有教训。（参见 [`讲透AI历史/advanced/02-失败的教训`](../讲透AI历史/advanced/02-失败的教训被淘汰的方向.md)）

### 12.1 FIPA 标准化运动（1990s-2000s）

**Foundation for Intelligent Physical Agents（FIPA）** 试图制定统一的 agent 通信标准（FIPA-ACL）。结果：太重、太理想化、工业界不采用。**教训**：当你为"未来所有 agent"设计一个完美协议时，你已经失败了——真实系统需要的是"够用就好"的最小抽象。

### 12.2 全连接多 Agent 架构

让 N 个 agent 两两通信的方案，在 N > 5 时就因 O(N²) 通信开销而崩溃。**教训**：大规模系统必然走向分层或市场化（stigmergy），全连接是反模式。

### 12.3 Naive Chaining（朴素串联）

MetaGPT 论文明确指出：把多个 LLM 简单首尾相连，会导致**级联幻觉**——错误逐层放大。**教训**：每一步必须有中间结果验证（SOP / 审查 agent），否则多 agent 比单 agent 更差。

### 12.4 完全自主 Agent（AutoGPT 式）

2023 年 AutoGPT/BabyAGI 的"完全自主、无需人类干预"路线被证明不可行——agent 会陷入无限循环、幻觉级联、目标漂移。**教训**：当前阶段，human-in-the-loop 不可省略。"完全自主"是过渡形态，不是终态。

### 12.5 同质 Agent 辩论（回音室）

多个同基模型、同 prompt 的 agent 辩论，不会纠正错误反而会互相确认幻觉。**教训**：debate 需要多样性（不同模型/prompt/温度）。同质 debate = 回音室。

---

## 13. 路径依赖与偶然性

### 13.1 如果 GPT-4 晚一年发布

CAMEL、Generative Agents、Du 辩论、ChatDev、MetaGPT、AutoGen——这 6 篇里程碑论文**全部在 2023 年 3-8 月集中出现**，时间窗口不到 6 个月。如果 GPT-4 晚一年发布（2024 年 3 月），整个 LLM 多 Agent 范式可能延迟一年——但**不会缺席**。因为思想（MAS 认知架构 + Minsky 心智社会 + Axelrod 合作演化）早已就绪，只等载体。

### 13.2 如果 KAUST 没有 CAMEL

CAMEL 是第一个 LLM 多 Agent 框架（3 月 31 日提交，比 Generative Agents 早一周、比 AutoGen 早近 5 个月）。如果 Guohao Li 没有做 CAMEL，多 Agent 的"角色扮演"范式可能由后来者补上——但开源生态（camel-ai）可能长得不同。CAMEL 的开源库后来影响了大量后续工作。

### 13.3 如果 Minsky 没写 Society of Mind

Minsky 1986 年的 *Society of Mind* 是 Du 2023 年多 agent 辩论的**直接灵感来源**（Du 在论文中引用）。如果 Minsky 没写这本书，"心智社会"思想仍然会从博弈论和 CAS 中长出来——但可能以不同的形态、由不同的人、在更晚的时间点提出。

### 13.4 偶然 vs 必然

**必然的**：只要有足够强的通用推理引擎（LLM），多 Agent 协作范式必然复活——因为 MAS 时代的思想早已成熟，只缺可规模化的 agent 引擎。

**偶然的**：具体哪些框架胜出（AutoGen vs LangGraph vs CrewAI），取决于开源时机、大厂背书、社区运营——这些是商业和社交因素，不是技术必然。

---

## 14. 开放问题

1. **涌现何时回归？** 当前 LLM agent 可靠性不够，多 Agent 框架一边倒地走向编排。当 agent 够可靠时，swarm 式涌现会回来吗？什么阈值？

2. **多 Agent 会超越单 Agent 吗？** 当基座模型从 GPT-4 升级到 GPT-6/7，单 agent 能力暴涨——多 agent 的"分工/并行/对抗"收益是否会缩水？是否存在一个模型能力阈值，超过它后单 agent 全面碾压多 agent？

3. **Stigmergy 在 LLM 时代如何实现？** 蚁群用信息素做 stigmergy。LLM agent 的"环境"是什么？共享文件系统？共享 embedding store？如何设计 LLM 原生的 stigmergy 机制？

4. **多 Agent 的"宪法"是什么？** 当 agent 数量上百、自主性增强，如何防止串谋、责任扩散、群体幻觉？需要什么样的"治理结构"？（呼应 [`04-不足-协作失败模式`](./04-不足-协作失败模式.md)）

5. **Nash 均衡在 LLM 辩论中会出现吗？** 多个 LLM agent 辩论收敛到的"共同答案"，是 Nash 均衡吗？如果是，它是"好的均衡"还是"坏的均衡"（如回音室）？

6. **多 Agent vs 多模态：谁先到 AGI？** 路线 A：一个超大多模态模型。路线 B：多个专精 agent 协作。哪条路更可能到达通用智能？

7. **多 Agent 的"统一理论"是什么？** 博弈论、CAS、MAS、LLM 多 Agent——这四条传统有没有一个统一的数学框架？马尔可夫博弈（本系列 [`02-数学`](./02-数学-协作的形式化.md) §1）够吗？

---

## 15. 配套资源

### 15.1 项目内

| 资源 | 链接 | 定位 |
|------|------|------|
| 多 Agent 直觉 | [01-直觉-为什么需要多个Agent](./01-直觉-为什么需要多个Agent.md) | 单 Agent 三大极限 + Brooks 定律 |
| 协作数学 | [02-数学-协作的形式化](./02-数学-协作的形式化.md) | 马尔可夫博弈 / 共识 / 通信信息论 |
| 最小编排 | [03-代码-最小多Agent编排](./03-代码-最小多Agent编排.md) | 200 行 orchestrator-worker |
| 失败模式 | [04-不足-协作失败模式](./04-不足-协作失败模式.md) | 死锁/幻觉级联/串谋 |
| 选型决策 | [05-应用-协作模式选型](./05-应用-协作模式选型.md) | 五种拓扑 + 框架对比 |
| 单 Agent 思想史 | [`讲透Agent/HISTORY.md`](../讲透Agent/HISTORY.md) | BDI/Soar→ReAct 四次范式转移 |
| 群体智能 | [`讲透群体智能/`](../讲透群体智能/) | 涌现 vs 编排（光谱另一端）|
| AI 思想史方法论 | [`讲透AI历史/00`](../讲透AI历史/00-为什么学AI历史.md) | 思想史方法论 |
| 范式转移分析 | [`讲透AI历史/advanced/01`](../讲透AI历史/advanced/01-范式转移的库恩分析.md) | 库恩框架 |

### 15.2 经典论文（按时间线）

| 年份 | 论文/著作 | 历史地位 |
|------|---------|---------|
| 1944 | von Neumann & Morgenstern, *Theory of Games* | 博弈论奠基——多 Agent 的数学前夜 |
| 1950 | Nash, *Non-Cooperative Games* | Nash 均衡——互动中的稳定态 |
| 1971 | Schelling, 隔离模型 | 微观规则→宏观涌现 |
| 1975 | Holland, *Adaptation in Natural and Artificial Systems* | 遗传算法 → CAS 理论 |
| 1980 | Smith, *Contract Net Protocol* | **第一个多 Agent 协作协议** |
| 1984 | Axelrod, *The Evolution of Cooperation* | 合作的涌现——Tit for Tat |
| 1986 | Minsky, *Society of Mind* | 心智社会——影响 Du 辩论 |
| 1987 | Reynolds, *Boids* | 涌现群集模型 |
| 1992 | Dorigo, 博士论文 | 蚁群优化（ACO）|
| 1995 | Kennedy & Eberhart, *PSO* | 粒子群优化 |
| 1995 | Wooldridge & Jennings, *Intelligent Agents* | **MAS 学科定义** |
| 2023.03 | Li et al., *CAMEL* (arXiv:2303.17760) | **第一个 LLM 多 Agent 框架** |
| 2023.04 | Park et al., *Generative Agents* (arXiv:2304.03442) | 认知架构 LLM 复活 |
| 2023.05 | Du et al., *Multiagent Debate* (arXiv:2305.14325) | "Society of Minds" |
| 2023.07 | Qian et al., *ChatDev* (arXiv:2307.07924) | LLM 软件公司 |
| 2023.08 | Hong et al., *MetaGPT* (arXiv:2308.00352) | SOP 编排 |
| 2023.08 | Wu et al., *AutoGen* (arXiv:2308.08155) | 通用多 agent 对话框架 |

### 15.3 关键书籍

| 书 | 作者 | 年份 | 定位 |
|----|------|------|------|
| *Theory of Games and Economic Behavior* | von Neumann & Morgenstern | 1944 | 博弈论圣经 |
| *The Evolution of Cooperation* | Robert Axelrod | 1984 | 合作如何涌现 |
| *Society of Mind* | Marvin Minsky | 1986 | 心智=多 Agent 社会 |
| *Hidden Order: How Adaptation Builds Complexity* | John Holland | 1995 | CAS 理论科普 |
| *An Introduction to MultiAgent Systems* | Michael Wooldridge | 2002/2009 | MAS 标准教材 |
| *Swarm Intelligence* | Kennedy & Eberhart | 2001 | 群体智能专著 |

---

## 16. 费曼回炉

> L2 自检：能不能用大白话把多 Agent 协作思想史讲清楚？

### F2 卡壳点

- **卡点 A**：长期以为"多 Agent 协作是 LLM 时代的新发明"——CAMEL/AutoGen/MetaGPT 是全新概念。重读史料后才钉死：**Contract Net Protocol 1980 年就定义了任务分配 + 控制权转移**，和 OpenAI Swarm 2024 年的 handoff 在哲学上是同一个东西。**多 Agent 协作的核心原语，40 年没变过。** LLM 没有发明多 Agent，它只是让 20 年前的思想终于"能跑了"。

- **卡点 B**：以为 Swarm Intelligence 和 LLM 多 Agent 是"同一个东西的不同实现"。重读后意识到它们是**哲学对立面**——Swarm 信奉"无中心的涌现"（蚁群），LLM 多 Agent 信奉"有中心的编排"（orchestrator）。OpenAI Swarm 叫 swarm 却做编排，是术语膨胀。**它们被统称"多 Agent"，但一个要消灭中心，一个要设计中心。**

- **卡点 C**：以为 BDI/Soar 认知架构是"失败的旧范式"。重读 Generative Agents 论文才发现——记忆流 + 反思 + 计划完全是 BDI/Soar 的 LLM 版。**认知架构没有失败，它超前了 30 年。** 这和 [`讲透Agent/HISTORY.md`](../讲透Agent/HISTORY.md) 的核心论点完全一致：Agent 史不是"新取代旧"，而是"旧思想等待新引擎"。

### F3 术语翻译

- **博弈论（Game Theory）** → 多个决策者互相影响时，"最优"不再是一个人的事——我的最优策略取决于你做什么。多 Agent 的数学前夜
- **Nash 均衡** → 多个自利个体互动后收敛到的"稳定态"——不是全局最优，但没人有动力单方面改变。LLM 辩论收敛到的"共同答案"就是某种 Nash 均衡
- **Contract Net Protocol** → "招标-投标"式任务分配：manager 广播任务，contractor 投标，中标者执行。和 OpenAI Swarm 的 handoff 是同一个东西
- **Stigmergy（间接协同）** → agent 不直接通信，而是通过修改环境间接影响别人（蚂蚁留信息素）。零通信也能协调
- **BDI（信念-欲望-意图）** → agent 的认知三件套：相信什么（Belief）、想要什么（Desire）、决定做什么（Intention）。Generative Agents 的 Memory = Belief，Planning = Intention
- **SOP（标准化操作流程）** → MetaGPT 把人类组织的"流水线"编码成 prompt 序列，让 agent 按流程协作
- **Handoff** → 一个 agent 把控制权"交"给另一个——OpenAI Swarm 的核心抽象，本质就是 Contract Net

### F4 回炉

- **v1（错误直觉）**：以为多 Agent 协作的历史是"从博弈论到 AutoGen 到 CrewAI，协作越来越高效"的线性进步。
- **v2（修正后）**：多 Agent 协作的历史是**四次范式转移**——从"理性个体如何最优互动"（博弈论）到"多个程序如何分工"（MAS）到"如何设计涌现"（Swarm/CAS）到"让语言模型自主协商"（LLM 多 Agent）。而且**旧范式全部复活**：Contract Net = Swarm handoff；BDI = Generative Agents；Minsky 心智社会 = Du 辩论。diff 在于从"进步叙事"升级为"**思想复活的循环叙事**"——多 Agent 协作史不是"新取代旧"，而是"旧思想等待新载体（LLM）"。更深一层：**涌现和编排是永恒的张力**——当 agent 够可靠时涌现回归，不够可靠时编排主导。当前 LLM agent 不可靠，所以全行业倒向编排；但这不是终态。

---

📌 **下一步**

1. **回到** [01-直觉](./01-直觉-为什么需要多个Agent.md) 理解 Brooks 定律的 AI 版——什么时候该用多 Agent
2. **深入** [02-数学](./02-数学-协作的形式化.md) 看马尔可夫博弈如何形式化协作
3. **读** [04-不足](./04-不足-协作失败模式.md) 了解死锁、幻觉级联、串谋——失败和成功同等重要
4. **读** [`讲透Agent/HISTORY.md`](../讲透Agent/HISTORY.md) 理解单 Agent 思想史——两者互补
5. **读** [`讲透群体智能/`](../讲透群体智能/) 理解涌现 vs 编排的光谱
6. **思考** §14 的 7 个开放问题——每个都是博士论文级方向

---

### ✍️ 思考题

1. **方法论题**：如果用一个词概括多 Agent 协作 80 年思想史的核心张力，你会选什么？（提示：涌现 vs 编排？自利 vs 合作？中心化 vs 去中心化？编码 vs 学习？）
2. **反事实题**：如果 Minsky 1986 年没有写 *Society of Mind*，Du 2023 年的"多 agent 辩论"还会出现吗？会延迟多少年？以什么形态？
3. **判断题**：当基座模型从 GPT-4 升级到 GPT-7（假设能力暴涨 10 倍），多 Agent 的收益会缩水还是放大？给出基于历史规律的预测 + 理由。
4. **批判题**：OpenAI Swarm 叫"swarm"却做显式编排——这是术语膨胀还是哲学混淆？找另一个多 Agent 领域的术语膨胀案例并分析。
5. **延伸题**：Stigmergy（间接协同 / 环境介导协调）在 LLM 时代如何实现？设计一个基于 stigmergy 的 LLM 多 Agent 系统（提示：共享文件系统？共享 embedding？）。
6. **综合题**：把博弈论、MAS、Swarm、LLM 多 Agent 四条传统画在一张图上，标注它们的**共同问题**和**哲学差异**。这张图能统一吗？
