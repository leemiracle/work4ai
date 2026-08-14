# 讲透RL · 思想史

> **一句话定位**：强化学习从巴甫洛夫的狗到 DeepSeek-R1 的推理引擎，走了 120 年——它的历史不是"算法越来越强"的线性进步，而是三场范式转移（行为主义→计算→深度学习→语言推理），每场转移都伴随一个核心思想的"换问法"：从"刺激-反应怎么形成"到"序贯决策怎么最优化"，从"表格式函数"到"神经网络泛化"，从"游戏得分"到"人类偏好与可验证推理"。

> 配套：[`讲透AI历史/00-为什么学AI历史`](../讲透AI历史/00-为什么学AI历史.md)（方法论）+ [`讲透AI历史/advanced/01-范式转移的库恩分析`](../讲透AI历史/advanced/01-范式转移的库恩分析.md)（库恩框架）+ [本系列 README](./README.md)

---

## 0. 方法论

> 本篇遵循 [`讲透AI历史`](../讲透AI历史/) 的方法论：**思想史 > 年代史**。

**年代史**会这样写：

```
1898  Thorndike Law of Effect
1957  Bellman Dynamic Programming
1989  Watkins Q-Learning
2013  DQN (Mnih et al.)
2016  AlphaGo beats Lee Sedol
2022  RLHF → ChatGPT
2025  DeepSeek-R1
```

这给你事实，但不告诉你**为什么 Q-Learning 1989 年提出、却要等 24 年才成为工业级别的方法**；不告诉你**RLHF 的思想根源在 2017 年一篇被引用上千次但无人认真跟进的论文里**；不告诉你**Sutton 在 1980s 坚持的"无模型学习"路线当时被整个领域视为异端**。

**思想史**问的问题：

| 问题 | 在 RL 史上的体现 |
|---|---|
| 为什么此时此地？ | 为什么 DQN 在 2013 而非 2003？（答：GPU + 经验回放 + target network 三个条件凑齐）|
| 为什么被淘汰？ | 为什么策略迭代在 2000s 被冷落？（答：维度灾难——表格方法搞不定高维状态）|
| 为什么复兴？ | 为什么 model-based RL 在 2020 后突然热起来？（答：Dreamer 系列证明了世界模型可行）|
| 路径依赖与偶然性 | 如果 Tesauro 1992 年没做 TD-Gammon，RL 可能多沉寂十年 |
| 谁影响了谁？ | Sutton 是 Widrow 学生→Widrow 是自适应滤波先驱→RL 和信号处理的血缘 |

**本篇的五条原则**（承接 [`讲透AI历史`](../讲透AI历史/) ）：

1. **思想史 > 年代史**——每个"突破"都问"为什么此时"
2. **路径依赖敏感**——当前"最优算法"可能是历史偶然
3. **失败与成功同等重要**——被淘汰的方向有教训
4. **跨学科**——RL 受心理学/控制论/运筹学/神经科学影响
5. **批判性**——不把"赢家"当真理

---

## 1. 前夜：行为主义心理学（1890s-1950s）

### 1.1 RL 的"灵魂"来自心理学

强化学习的核心思想——**行为由其后果塑造**——不是计算机科学家的发明。它来自三个心理学家：

| 人物 | 年代 | 贡献 | RL 对应物 |
|------|------|------|----------|
| **巴甫洛夫**（Pavlov）| 1849-1936 | 经典条件反射：铃声→食物→狗流口水 | 刺激-反应映射（$s \to a$） |
| **桑代克**（Thorndike）| 1874-1949 | **效果律**（Law of Effect, 1898）：带来好结果的行为更可能被重复 | **RL 的公理**——reward 增大行为概率 |
| **斯金纳**（Skinner）| 1904-1990 | 操作性条件反射：**强化时间表**（固定比率/可变比率/固定间隔/可变间隔） | reward 的**时间结构**如何影响学习 |

### 1.2 桑代克的猫：RL 史上的第一个实验

1898 年，桑代克把饥饿的猫放进"迷箱"（puzzle box）。箱子里有一个踏板，踩到就能开门吃到外面的鱼。猫起初乱抓乱撞，偶然踩到踏板→逃出→吃到鱼。重复多次后，猫逃出的时间越来越短。

**桑代克的发现**：学习不是"顿悟"，而是**试错**（trial-and-error）——通过反复尝试，有效行为被"强化"，无效行为被"消退"。

> 🎯 **这就是 RL 的第一性原理**：agent 通过与环境交互，最大化累积奖励。桑代克 1898 年的猫，和 2025 年的 DeepSeek-R1，在做同一件事。

### 1.3 斯金纳的鸽子：reward 时间表塑造行为

斯金纳的实验更精妙。他发现：**同样的总 reward，不同的发放时间表（schedule）会产生截然不同的行为模式和学习速度**。

- **固定比率**（每按 10 次给食物）：动物学会快速按
- **可变比率**（平均每 10 次给食物，但随机）：动物学会**不知疲倦地按**——这是赌博上瘾的原理
- **固定间隔**（每 60 秒第一次按给食物）：动物学会"等待+爆发"模式

> 🎯 **RL 的 reward 工程学根源**：今天 RLHF 的 reward model 输出、GRPO 的组内相对优势、curriculum learning 的难度阶梯——**全部是斯金纳强化时间表思想的算法化**。2024 年 reward hacking（policy 钻空子刷分）的失败模式，斯金纳 70 年前就在鸽子里见过：动物学会了"不按踏板而是啄传感器缝隙"这种"reward gaming"行为。

### 1.4 为什么心理学是 RL 的前夜而非起点

行为主义给了 RL **直觉**（试错学习、强化塑造行为），但缺少三样东西：

1. **数学框架**：效果律是定性描述，无法计算"应该选哪个动作"
2. **序列决策**：桑代克的猫是单步问题（踩/不踩），但围棋有 200 步、机器人控制连续不断
3. **计算工具**：没有计算机，无法验证理论

这三样东西要等到 1950s 的 Bellman。**RL 史上的第一次范式转移**：从"心理学直觉"到"数学最优化"。

> ⚠️ **反常识预警**：行为主义在 1960s 后被认知科学取代（Chomsky 批判 Skinner 的《言语行为》），但它的核心洞见（试错学习）却在 RL 里获得了永生。**一个被心理学抛弃的范式，成了 AI 最活跃分支的地基**——这是思想史上典型的"死亡与复活"模式。

---

## 2. MDP 与动态规划：Bellman 的方程（1950s）

### 2.1 Richard Bellman（1920-1984）与动态规划

1957 年，RAND 公司的数学家 Richard Bellman 出版 *Dynamic Programming*。他要解决的核心问题是：**如何在多步决策中找到最优策略？**

Bellman 的天才洞察是 **"最优性原理"**：

> 一个策略是最优的，当且仅当：不管初始状态和初始决策是什么，剩余的决策必须构成一个相对于第一步产生的状态的最优策略。

这句话翻译成数学就是 **Bellman 方程**：

$$V^*(s) = \max_a \sum_{s'} P(s'|s,a) \left[ R(s,a,s') + \gamma V^*(s') \right]$$

> 🎯 **思想史定位**：Bellman 方程把"无穷步的最优化"拆成"当前一步 + 递归"——就像反向传播把"全局误差"拆成"局部梯度 + 链式传播"。**Bellman 方程之于 RL，等同于反向传播之于深度学习**。

### 2.2 MDP 的形式化：Ronald Howard（1960）

Bellman 处理的是确定性动态规划。1960 年，MIT 的 Ronald Howard 在博士论文 *Dynamic Programming and Markov Processes* 中，将 Bellman 的框架扩展到**随机环境**——定义了**马尔可夫决策过程（MDP）**：

$$\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R, \gamma)$$

"马尔可夫"意味着**未来只依赖当前状态，不依赖历史**——$P(s_{t+1} | s_t, a_t, \text{历史}) = P(s_{t+1} | s_t, a_t)$。

这个假设是双刃剑：
- ✅ 让问题**可解**——不需要记住全部历史
- ❌ 在现实中几乎**不成立**——真实世界是部分可观测的（POMDP）

> 🎯 **思想史洞察**：MDP 是 RL 的柏拉图理型——一个理想化的数学对象，真实世界几乎从不是严格 MDP。RL 的全部工程努力可以理解为：**如何在非理想 MDP 上近似求解**。

### 2.3 动态规划的局限：维度灾难

Bellman 和 Howard 给了优雅的理论，但有一个致命问题：**维度灾难**。

状态空间 $\mathcal{S}$ 随问题维度**指数增长**。围棋的状态空间 $\approx 10^{170}$，国际象棋 $\approx 10^{43}$。即使每个状态只存一个浮点数，宇宙也装不下。

动态规划需要**知道**转移函数 $P$ 和奖励函数 $R$——但现实中你不知道环境规则（就像你不知道围棋对手会怎么走）。

**两条出路**（后来分裂为 RL 的两大流派）：

1. **值函数近似**：不存所有状态的值，而是用一个函数 $V_\theta(s) \approx V^*(s)$ 来近似
2. **采样替代枚举**：不遍历所有状态，而是通过交互来采样（这就是"学习"的开始）

这两条出路在 1980s 汇合为 **Sutton 的 TD 学习**。

> 🎯 **思想史转折**：从 1960 到 1985，RL 的理论框架（MDP + Bellman）一直在，但**做不了任何有趣的事**——因为维度灾难。这不是理论的失败，是**等待计算工具**的 25 年空白期。这种"理论超前实践几十年"的模式在 AI 史上反复出现（反向传播 1974→1986，注意力机制 1990s→2017）。

---

## 3. TD 学习与 Q-Learning：RL 找到自己的算法（1980s）

### 3.1 Sutton 与时间差分学习（1988）

**Richard Sutton**（1957-），被公认为"强化学习之父"。他在 1984 年从 UMass（阿默斯特）博士毕业，导师是 Andrew Barto。1988 年，Sutton 在 *Machine Learning* 期刊发表 *"Learning to Predict by the Methods of Temporal Differences"*——提出了 **TD(λ) 学习**。

**核心思想**：与其等到一局游戏结束才知道输赢（Monte Carlo 方法），不如**每一步都用"当前估计 + 即时奖励"来更新前一步的估计**。

$$V(s_t) \leftarrow V(s_t) + \alpha \left[ r_{t+1} + \gamma V(s_{t+1}) - V(s_t) \right]$$

方括号里的项 $r_{t+1} + \gamma V(s_{t+1}) - V(s_t)$ 就是著名的 **TD 误差**——它衡量"实际看到的"和"原来预测的"之间的差距。

> 🎯 **为什么 TD 是革命性的**：
> 1. **不依赖环境模型**（model-free）——不需要知道 $P$ 和 $R$，只需与环境交互
> 2. **在线学习**——每一步都能更新，不用等一局结束
> 3. **自举（bootstrapping）**——用自己估计的值来更新自己（这是 TD 和 Monte Carlo 的本质区别）
>
> Sutton 后来在 2017 年写了一篇影响深远的博客 *"The Bitter Lesson"*，总结他一生的洞察：**通用方法（搜索+学习）最终胜过人类精心设计的特征**——这个观点在 RL 史上反复被验证。

### 3.2 Watkins 与 Q-Learning（1989）

**Christopher Watkins**，1989 年在剑桥大学完成博士论文 *"Learning from Delayed Rewards"*。他提出了 **Q-Learning**——可以说是 RL 史上最重要的单一算法。

$$Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha \left[ r_{t+1} + \gamma \max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t) \right]$$

**Q-Learning 的天才之处**：直接学 $Q^*(s,a)$（最优动作值函数），而不需要知道策略是什么。学完之后，$\pi^*(s) = \arg\max_a Q^*(s,a)$。

Watkins 证明了 Q-Learning 在表格情况下**收敛到最优 Q 值**——这是 RL 少有的严格收敛性保证。

> ⚠️ **思想史的反讽**：Q-Learning 的收敛性证明只在**表格**情况下成立。一旦用神经网络近似 $Q_\theta(s,a)$，收敛性就被打破——这就是后来 Tsitsiklis & Van Roy (1997) 证明的 **"deadly triad"（致命三角）**：函数近似 + bootstrapping + off-policy 三者同时出现时，Q-Learning 会发散。这个"理论陷阱"困扰了 RL 二十年，直到 DQN 用 target network + 经验回放来缓解。

### 3.3 TD-Gammon：第一个震撼级演示（1992-1995）

**Gerald Tesauro**，IBM 研究员。1992 年，他用 TD(λ) 训练了一个神经网络来下西洋双陆棋（backgammon），叫 **TD-Gammon**。

TD-Gammon 的训练方式极其简单：
1. 神经网络自己和自己下
2. 每局结束后用 TD 学习更新
3. 不给任何人类棋谱

结果：TD-Gammon 达到了**世界冠军级别**。它是第一个通过自我对弈达到专家水平的程序，比 Deep Blue（国际象棋，靠暴力搜索+人类知识）早了 5 年。

> 🎯 **思想史意义**：TD-Gammon 是 RL 的"ImageNet 时刻之前 20 年的 ImageNet 时刻"。它证明了三件事：
> 1. **无模型学习可行**——不需要人类知识
> 2. **自我对弈有效**——self-play 的种子
> 3. **神经网络和 RL 可以结合**——虽然要再等 20 年才大规模成功

TD-Gammon 没有引发像 ImageNet 那样的革命，原因很简单：**算力不够**。TD-Gammon 用的是浅层网络（一个隐藏层），状态空间也小。在 1992 年，没人能跑动 Atari 游戏级别的深度网络。

### 3.4 Sutton-Barto 教材：RL 的圣经

1998 年，Sutton 和 Barto 出版 *Reinforcement Learning: An Introduction*。这本教材系统整理了 1980s-1990s 的 RL 理论，定义了术语（MDP、TD、Q-Learning、policy gradient……），统一了来自心理学、运筹学、最优控制的线索。它之于 RL，等同于 Bishop 的 *Pattern Recognition* 之于机器学习。

2018 年出第二版（加入深度 RL），2024 年 Sutton 宣布正在写第三版。

> **思想史教训**：一个领域需要一本"圣经"来统一语言。RL 在 1980s-1990s 散落在 5 个社区（心理学/控制论/运筹学/AI/神经科学），Sutton-Barto 把它们捏在一起。没有这本教材，RL 可能一直是"运筹学的一个分支"而非独立学科。

---

## 4. 第一次范式转移：深度 RL（DQN 2013-2015）

### 4.1 库恩范式转移框架回顾

按 [`讲透AI历史/advanced/01`](../讲透AI历史/advanced/01-范式转移的库恩分析.md) 的库恩框架：

```
常规科学 → 异常累积 → 危机 → 范式转移 → 新常规科学
```

**RL 的第一次范式转移发生在 2013 年**：

| 维度 | 旧范式（经典 RL）| 新范式（深度 RL）|
|------|-----------------|------------------|
| 值函数表示 | 表格 / 线性特征 | **深度神经网络** |
| 状态表示 | 人工设计特征 | **端到端学习** |
| 可处理问题 | 小状态空间（棋类）| **高维原始输入**（像素）|
| 异常累积 | TD-Gammon 暗示可行，但没人能扩展到更复杂任务 | — |
| 触发器 | **GPU + CNN + 经验回放 + target network** | — |

### 4.2 DQN：三个工程技巧的合体

2013 年 NIPS Workshop，DeepMind 的 **Volodymyr Mnih** 等人发表论文 *"Playing Atari with Deep Reinforcement Learning"*。2015 年，扩展版发表在 *Nature*。

DQN 用**同一个网络**玩 49 款 Atari 游戏，输入是原始像素，在大多数游戏上达到或超越人类水平。

DQN 的成功不在于单个理论突破，而在于**三个工程技巧**的组合：

| 技巧 | 解决的问题 | 原理 |
|------|-----------|------|
| **经验回放**（Experience Replay）| 样本相关性 → 训练不稳定 | 存 $(s,a,r,s')$ 到 buffer，随机采样 mini-batch 打破时序相关 |
| **Target Network** | 自举导致正反馈发散 | 用一个延迟更新的网络计算 target $y = r + \gamma \max Q_{\theta^-}$ |
| **CNN 端到端** | 无法处理像素输入 | 用 CNN 直接从像素学状态表示 |

> 🎯 **思想史洞察**：DQN 的"创新"不是算法——Q-Learning 是 1989 年的。DQN 的创新在于**工程化地解决了"神经网络 + Q-Learning"的不稳定性**。这呼应 Sutton 的 *Bitter Lesson*：不是算法多精巧，而是**通用方法 + 算力**最终胜出。

### 4.3 为什么是 2013 年而不是 2003 年

回答"为什么此时"这个问题——DQN 需要三个条件同时成熟：

1. **GPU 算力**：2003 年没有 CUDA，跑不动 CNN；2013 年有
2. **CNN 技术**：AlexNet 2012 年证明了 CNN 可以从像素学特征；DQN 借用
3. **工程洞察**：经验回放（Lin 1992 提出，沉寂 20 年）+ target network（Mnih 团队的工程创新）

> 🎯 **路径依赖**：DQN 是一个"条件成熟"的产物。如果 AlexNet 晚 5 年出现，DQN 也会晚 5 年。如果 Mnih 团队没有同时想到 target network 这个 trick，DQN 可能还卡在发散问题上。**历史不是必然的。**

### 4.4 DQN 之后：Rainbow（2017）

2017 年，Hessel 等人发表 *Rainbow*，把 DQN 的 6 个改进（Double DQN / Dueling / Prioritized Replay / Multi-step / Distributional / Noisy Nets）组合在一起，大幅超过原始 DQN。

Rainbow 标志着**值函数路线的成熟**——此后 Atari 基准被视为"已解决"，注意力转向更难的问题（连续控制、策略方法、大规模应用）。

---

## 5. 围棋革命：AlphaGo → AlphaZero（2016-2017）

### 5.1 AlphaGo 击败李世石（2016）

2016 年 3 月，DeepMind 的 **AlphaGo**（Silver et al., *Nature* 2016）以 4:1 击败围棋世界冠军李世石。

AlphaGo 不是纯 RL——它是 RL + 深度学习 + 蒙特卡洛树搜索（MCTS）的组合：

1. **监督学习初始化**：用人类棋谱训练策略网络（学"人类会怎么下"）
2. **RL 自我对弈**：策略网络自己和自己下，用策略梯度优化（学"比人类更好的下法"）
3. **值网络**：用 RL 学"当前局面谁占优"
4. **MCTS**：在推理时搜索，结合策略网络和值网络做决策

> 🎯 **思想史意义**：AlphaGo 证明了 RL 可以解决"搜索空间 $10^{170}$"的问题——这在 2010 年被视为不可能。但 AlphaGo 仍依赖人类棋谱（监督学习初始化）。**真正的突破在 AlphaZero。**

### 5.2 AlphaZero：纯自我对弈的围棋之神（2017）

2017 年 12 月，DeepMind 发表 *Mastering the Game of Go Without Human Knowledge*——**AlphaZero**。

AlphaZero 的革命：**完全不需要人类棋谱**。它从随机下棋开始，纯靠自我对弈 RL，72 小时后超越击败李世石的 AlphaGo 版本，然后继续变强。

AlphaZero 的三个要素：
1. **自我对弈**（self-play）：始终和自己的历史版本对弈
2. **MCTS**：用树搜索做"想象力"
3. **策略-值网络**：统一网络，MCTS 的搜索结果反过来训练网络

> 🎯 **范式转移**：AlphaZero 证明了 Sutton 的 *Bitter Lesson*——**通用方法（搜索+学习）可以超越人类知识**。国际象棋、将棋、围棋，同一个算法全部搞定。这不是"更好的围棋 AI"，是"一种全新的 AI 范式"：不学人类，自己发现知识。

### 5.3 从 AlphaGo 到 MuZero（2020）

**MuZero**（Schrittwieser et al., 2020, *Nature*）更进一步：**连游戏规则都不给**。

MuZero 学习一个**隐式世界模型**——不显式建模环境，而是学一个"表示+动态+预测"的三部件网络，然后用 MCTS 在学到的隐空间里规划。它在 Atari（57 款）和棋类（围棋/象棋/将棋）上都达到 SOTA。

> 🎯 **思想史定位**：MuZero 是 model-based RL 和 model-free RL 的合流——它不显式建模环境（model-free 的精神），但内部学了一个隐式模型来做规划（model-based 的精神）。这条路线后来在 **Dreamer** 系列中被发扬光大（见 §9）。

---

## 6. PPO / SAC / IMPALA：工业级 RL 的工具箱（2017-2018）

### 6.1 策略梯度与 PPO（2017）

值函数方法（DQN 家族）适合离散动作，但面对连续动作空间（机器人控制、LLM token 生成）力不从心。**策略梯度方法**直接优化策略 $\pi_\theta(a|s)$ 的参数。

**PPO**（Proximal Policy Optimization，Schulman et al., 2017）是策略梯度的集大成者。它的核心创新是 **clipped surrogate objective**——限制策略更新幅度，防止一步更新太大导致崩溃：

$$L^{CLIP}(\theta) = \hat{E}_t\left[\min\left(r_t(\theta)\hat{A}_t,\, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t\right)\right]$$

其中 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$ 是重要性采样比率。

> 🎯 **为什么 PPO 成为工业标准**：PPO 不是最强的算法（TRPO 有更强理论保证，SAC 在连续控制上更好），但它是**最好用的**——超参数不敏感、实现简单、训练稳定。OpenAI 的所有 RLHF（包括 InstructGPT/ChatGPT）都用 PPO。**工程胜出不是因为理论最优，而是因为"够好且好调"**——这是工业 AI 的核心逻辑。

### 6.2 SAC：最大熵 RL（2018）

**Soft Actor-Critic**（Haarnoja et al., 2018, ICML）引入**最大熵原理**——不仅最大化回报，还最大化策略的熵（鼓励探索）：

$$J(\pi) = \sum_t \mathbb{E}_{(s_t,a_t)\sim\rho_\pi}\left[r_t + \alpha H(\pi(\cdot|s_t))\right]$$

SAC 的三个关键组件：
1. **最大熵目标**：鼓励探索，避免过早收敛
2. **软 Bellman 方程**：把熵奖励加入值函数
3. **双 Q 网络**（Twin Q）：取 min 来消除 Q 值高估（解决 deadly triad）

SAC 成为连续控制的 SOTA——机器人操作、自动驾驶仿真、游戏 AI。

### 6.3 IMPALA：分布式 RL（2018）

**IMPALA**（Importance Weighted Actor-Learner Architecture，Espeholt et al., 2018）解决了 RL 的**规模化问题**：如何用数百个 CPU 并行收集经验？

IMPALA 的 actor-learner 架构 + V-trace off-policy 修正，让 RL 可以扩展到数百个并行环境。Google 用它在 DMLab-30 上训练，达到了多任务学习的新高度。

> 🎯 **工业 RL 的成熟标志**：PPO（算法）+ SAC（连续控制）+ IMPALA（分布式）——这三者构成了 2018 年后工业 RL 的标准工具箱。此后 RL 的注意力从"算法创新"转向"**应用创新**"——把同样的算法用到不同领域。

---

## 7. 第二次范式转移：RLHF 进入 LLM（2017-2022）

### 7.1 RLHF 的前史：ChristianO 2017

RLHF 的思想根源在 **Christiano et al. (2017)** 的论文 *"Deep Reinforcement Learning from Human Preferences"*。

这篇论文的核心创新：**不写 reward 函数，而是让人类标注"哪个行为更好"，然后训练一个 reward model 来模拟人类偏好。**

但 2017 年时，这篇论文没有引起太大轰动——因为：
1. 深度 RL 社区关注的是游戏（Atari/MuJoCo），不是语言
2. "人类偏好"作为 reward 太弱、太主观
3. 没有 LLM 可以作为 policy

> 🎯 **路径依赖**：Christiano 2017 是一篇"超前时代 5 年"的论文。如果 OpenAI 没有自己的 LLM（GPT 系列），RLHF 可能永远停留在学术玩具阶段。**RLHF 的爆发不是算法突破，是"算法等到了对的载体（LLM）"**。

### 7.2 InstructGPT / ChatGPT：RLHF 的工业化（2022）

2022 年 1 月，OpenAI 发表 **InstructGPT**（Ouyang et al., 2022）。三阶段流水线：

```
① SFT（监督微调）→ 用人类写的高质量回答微调 GPT-3
② RM（奖励模型）→ 用人类偏好对（A > B）训练打分模型
③ PPO（RL 微调）→ 用 RM 的分数当 reward，PPO 优化策略
```

2022 年 11 月，**ChatGPT** 发布，引爆全球。RLHF 是 ChatGPT 从"续写模型"变成"对话助手"的关键技术。

> 🎯 **第二次范式转移**：RLHF 之前，RL 的 reward 是"游戏得分"（Atari/围棋），RL 的 policy 是"游戏 AI"。RLHF 之后，**RL 的 reward 变成"人类偏好"，RL 的 policy 变成"语言模型"**。这不是渐进改进，是 **reward 信号和 policy 架构的双重质变**——完全符合库恩的"不可通约性"。

### 7.3 DPO：去掉 reward model（2023）

**DPO**（Direct Preference Optimization，Rafailov et al., 2023, NeurIPS）的数学洞察：RLHF 的最优解可以从偏好数据**直接**推导出来，**不需要显式训练 reward model**。

DPO 把 RLHF 的目标重写为一个简单的分类损失：

$$\mathcal{L}_{DPO} = -\log\sigma\left(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta\log\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\right)$$

DPO 的吸引力在于**工程简洁**：不需要 PPO 的多阶段训练、不需要 critic、不需要 KL 约束——就是标准的分类训练。

> 🎯 **思想史教训**：DPO 证明了 RLHF 可以不用 RL。这是 RL 社区的"尴尬"——最重要的 RL 应用（LLM 对齐）的最流行方法，居然不是 RL。**但后续实践表明，DPO 在 reasoning 任务上不如 PPO/GRPO**——RL 的探索能力在某些场景下不可替代。

### 7.4 GRPO：DeepSeek 的去 critic 创新（2024）

**GRPO**（Group Relative Policy Optimization，DeepSeek，2024）是 PPO 的精简版——**去掉 critic 网络**，用组内相对优势代替：

对同一个 prompt 采样 $G$ 个回答，计算组内相对优势 $\hat{A}_i = \frac{r_i - \text{mean}(r)}{\text{std}(r)}$，然后用 PPO 的 clipped 目标优化。

GRPO 省一半显存（不需要 critic），在 DeepSeek-R1 上证明可以训练出顶级 reasoning 能力。

---

## 8. 第三次范式转移：RLVR + Reasoning（2024-2026）

### 8.1 从 RLHF 到 RLVR：reward 的回归

RLHF 的 reward 是人类偏好模型——主观、模糊、容易过拟合。2024 年起，一个新方向崛起：**RLVR（RL with Verifiable Rewards）**。

**RLVR 的核心**：用**可验证**的 reward 代替人类偏好——数学题答对=1/答错=0，代码通过测试=1/失败=0，证明验证成功=1/失败=0。

| 维度 | RLHF（2022）| RLVR（2024-2026）|
|------|-------------|------------------|
| Reward 来源 | 人类偏好模型 | **规则验证**（数学/代码/证明）|
| Reward 可靠性 | 低（模型可能有偏）| **高**（规则是确定性的）|
| 适用范围 | 对话/创作/通用 | 数学/代码/形式化（有标准答案的）|
| 风险 | reward hacking / 对齐税 | **多样性坍缩**（pass@k 反转）|

### 8.2 DeepSeek-R1：纯 RL 训出 reasoning（2025.01）

**DeepSeek-R1**（2501.12948）是 2025 年最大的里程碑。它证明了两件事：

1. **不需要 SFT**——R1-Zero 从 base model 直接用 GRPO + RLVR 训出 reasoning
2. **纯 RL 可以涌现思维链**——模型自发学会"让我想想……""等等，我需要重新检查"

DeepSeek-R1 的发布震惊业界——它以开源方式达到了接近 o1 的 reasoning 能力。

> 🎯 **第三次范式转移**：RLVR 让 RL 从"对齐人类偏好"转向"**训练推理能力**"。这是 RL 目标的又一次质变——从"让人喜欢"到"做对事情"。项目内 [05-RLVR的极限](./05-RLVR的极限.md) 详细分析了 RLVR 的能力边界。

### 8.3 RLVR 的极限：pass@k 反转（2025-2026）

但 RLVR 有暗面。**Yue et al. (2025, NeurIPS Oral)** 的论文 *"Limit of RLVR"* 揭示了一个反直觉的结果：

- RLVR 训练后，pass@1（取最优答案）确实提升
- 但 pass@k（取前 k 个采样中最好的）**下降**——RLVR 让模型**收窄**了输出分布

这意味着：**RLVR 是"分布锐化器"而非"知识发现器"**——它让模型更好地利用已有知识，但不让模型发现新知识。

> 🎯 **思想史意义**：这是 RL 史上少有的"反方论文改变领域共识"的案例。Limit of RLVR 让所有人重新审视 RLVR 的真正价值——它不是万能药，而是有明确边界的工具。项目内 [05](./05-RLVR的极限.md) 有完整的 6 算法对比 + 数学根因分析。

### 8.4 2026 的 RL 加速：让 RLVR 更便宜

RLVR 的核心痛点：**太贵**——每个 prompt 需要多次 rollout（采样多个回答），计算成本远超 SFT。2026 年的最新工作都在"少 rollout 提强信号"：

| 工作 | 来源 | 创新 | 效果 |
|------|------|------|------|
| **ARRoL** | ACL 2026 | 在线 rollout 剪枝 | **1.7× 加速** |
| **OM-GRPO** | 2026 | label-free RLVR | +4.24（test-time）|
| **Spec-RL** | 2026 | speculative decoding 加速 rollout | 工程加速 |

详见项目内 [07-2026最新研究全景](./07-2026最新研究全景.md) §2 主题③。

---

## 9. 世界模型 + RL 路线：从 MuZero 到 Dreamer

### 9.1 为什么需要世界模型

model-free RL（DQN/PPO/SAC）直接在真实环境里学习——样本效率低（需要百万次交互）。model-based RL 先学一个环境模型 $\hat{P}(s'|s,a)$，然后在模型里做规划——样本效率高（真实交互少），但模型可能不准。

**世界模型**（world model）是 model-based RL 的高级形态：不仅学环境动态，还学一个**抽象表征空间**，在这个空间里做规划和想象。

### 9.2 Dreamer 系列（2019-2023）

**Danijar Hafner**（Google DeepMind）的 Dreamer 系列是世界模型 + RL 的旗舰：

| 版本 | 年份 | 创新 | 成就 |
|------|------|------|------|
| **PlaNet** | 2019 | 循环状态空间模型 (RSSM) | 第一个可用的世界模型 RL |
| **Dreamer** | 2020 | 在想象空间里做 actor-critic | 样本效率大幅提升 |
| **DreamerV2** | 2021 | 离散表征 | Atari 55 款 SOTA |
| **DreamerV3** | 2023 | 固定超参数 | **一个超参搞定 150+ 任务**（Atari/Procgen/Crafter/DM Control/机器人）|

> 🎯 **DreamerV3 的思想史意义**：它证明了世界模型路线**不比 model-free 弱**——而且样本效率高得多。这是 model-based RL 长期被质疑后的翻身仗。

### 9.3 Genie / Genie 2：交互式世界模型（2024）

2024 年，DeepMind 发布 **Genie 2**——从视频中学习交互式 3D 世界模型。它可以生成"你可以用键盘控制角色移动"的虚拟环境——世界模型从研究原型走向通用基础设施。

> 🎯 **开放问题**：世界模型路线能否成为 AGI 的关键组件？如果是，RL 的核心将从"policy 优化"转向"世界建模"。这条路线的赌注很高——如果世界模型够好，你可以在里面训练任何 agent，不需要真实环境。

### 9.4 Decision Transformer：RL = 序列建模（2021）

**Chen et al. (2021)** 的 *Decision Transformer* 提出了一个激进的视角：**RL 不需要 Bellman 方程、不需要 TD 学习——只需要序列建模**。

Decision Transformer 把 $(s_1, a_1, r_1, s_2, a_2, r_2, ...)$ 当作序列，用 Transformer 做 conditional generation（条件是"Return-to-go" $R = \sum_{t'=t}^{T} r_{t'}$）。

> 🎯 **思想史意义**：Decision Transformer 模糊了 RL 和监督学习的边界——如果 RL 只是"带 reward 条件的序列生成"，那 Bellman 方程是否是必要的？这场争论至今未决。**RL 社区面临一个存在论危机：RL 的本质是什么？是 Bellman 方程，还是更一般的"从数据中学决策"？**

---

## 10. 思想史反思：5 个反常识

### 反常识 1：Q-Learning 1989 年就有了，为什么等了 24 年才"好用"？

**事实**：Q-Learning 1989（Watkins）→ DQN 2013（Mnih）= **24 年**。

**为什么**：
- 1989-2003：算力不够，跑不动神经网络
- 2003-2012：CNN 还没被"重新发现"（AlexNet 2012）
- 2012-2013：GPU + CNN + target network 三条件凑齐

**教训**：**想法 vs 时机**。RL 史上最大的教训不是"算法不够好"，而是"算法够好了但条件不成熟"。**大量被遗忘的论文只是超前了时代**。

### 反常识 2：AlphaGo 的胜利不是 RL 的胜利

**官方叙事**：AlphaGo 证明 RL 超越人类围棋。

**真相**：AlphaGo 是 **MCTS + 监督学习 + RL** 的组合。真正超越人类的是 MCTS 的搜索能力 + 神经网络的价值评估。纯 RL（没有搜索的 policy network）只是"强业余"水平。

**AlphaZero 才是真正的 RL 胜利**——它去掉了监督学习，纯自我对弈。但从 AlphaGo 到 AlphaZero 花了一年——**去掉人类知识比想象中难**。

**教训**：**警惕"胜利者叙事"**。AlphaGo 被包装成"RL 的胜利"，但真正的功臣是搜索+学习的组合。**在 AI 史上，胜利常被归功于单一技术，但实际是多技术的组合。**

### 反常识 3：RLHF 的成功不在于 RL，在于 reward 信号的设计

RLHF 的三阶段里，**最关键的不是 PPO（RL 部分），而是 reward model 的训练**。reward model 把"人类偏好"转成连续分数——这个"翻译"的质量决定了最终效果。

PPO 在 RLHF 中的角色是"执行者"——给它一个 reward 函数，它去优化。换一个更好的 RL 算法（比如 GRPO），效果差别不大。但换一个更好的 reward model，效果天差地别。

**教训**：**RL 的瓶颈不在算法，在 reward**。这是 RL 史上一贯的主题——从 Atari 的 reward hacking 到 RLHF 的 reward model 过拟合。Sutton 的 *Bitter Lesson* 只说对了一半：通用方法胜出，但"通用方法"的前提是 reward signal 对了。

### 反常识 4：RLVR 可能不是"教模型推理"，而是"让模型更自信"

Limit of RLVR 的发现——RLVR 训练后 pass@k 下降——意味着 RLVR 可能在做一件出乎意料的事：**不是教模型新知识，而是让模型更"自信"地输出它已经知道的东西**。

如果这个结论成立，那 RLVR 的本质是**分布锐化（distribution sharpening）**，而非**能力提升（capability gain）**。这类似于"复习"而非"学习"。

**教训**：**警惕"能力提升"的幻觉**。很多时候，我们以为是"模型变强了"，实际是"模型更自信了"。区分这两者需要 pass@k 这类多采样指标——而大多数 benchmark 只看 pass@1。

### 反常识 5：RL 在 LLM 时代"看似成功"，实际在退场

表面上，RLHF/DPO/GRPO 是 LLM 后训练的核心。但如果仔细看：

- **DPO** 绕过了 RL（直接用偏好对做分类训练）
- **DPO 在很多场景下和 PPO 效果相当**——而且简单得多
- **RLVR 的收益可能被高估**（Limit of RLVR）
- **大规模预训练**（SFT 阶段）才是能力的主要来源，RL 只是"微调"

**教训**：**RL 在 LLM 中的角色可能是"精调器"而非"能力引擎"**。如果预训练 + SFT 足够好，RL 可能变成一个可选的优化步骤而非核心组件。**RL 的长期命运可能取决于它能否提供预训练无法提供的"增量能力"**——目前证据混合。

---

## 11. 关键人物谱系

### 11.1 Sutton-Barto 谱系：RL 的"王族"

```
Arthur Samuel (1959, 机器学习先驱，跳棋程序)
    ↓
A. Harry Klopf (1970s, "间态行为主义"，激发 Sutton)
    ↓
Andrew Barto (UMass, 1970s-2018)
    ↓                    ↓
Richard Sutton (1984 PhD)   多位 RL 学者
    ↓
Peter Dayan (TD 学习共同作者)
Doina Precup (options framework)
Michael Littman (MDP 算法)
Satinder Singh (PAC-MDP)
```

**Sutton 是 RL 的精神领袖**——不仅是 TD 学习和策略梯度的发明者，更是 *The Bitter Lesson* (2017) 的作者，这篇文章深刻影响了 OpenAI 的 Scaling Law 信仰。

### 11.2 David Silver 谱系：DeepMind RL

```
David Silver (UCL, 棋牌 AI 博士, 2009 加入 DeepMind)
    ↓
AlphaGo (2016) → AlphaZero (2017) → MuZero (2020)
    ↓ 影响
Julian Schrittwieser (MuZero 一作)
Danijar Hafner (Dreamer 系列)
```

Silver 的贡献：**把 RL 从"实验室玩具"变成"超越人类的引擎"**。他的 AlphaGo/AlphaZero/MuZero 路线是"搜索+学习"范式的巅峰。

### 11.3 LLM RL 谱系：从 Christiano 到 DeepSeek

```
Paul Christiano (2017, Deep RL from Human Preferences)
    ↓
OpenAI InstructGPT 团队 (Long Ouyang et al., 2022)
    ↓
开源社区：TRL / OpenRLHF / verl
    ↓
DeepSeek RL 团队 (GRPO / R1, 2024-2025)
```

Christiano 的 2017 论文是 RLHF 的种子，但 5 年后才被 OpenAI 内部"激活"。**这证明了"重要论文不等于即时影响"——需要对的载体和时机**。

### 11.4 跨谱系连接

| 连接 | 意义 |
|------|------|
| Sutton 是 Widrow 学生 → Widrow 是自适应滤波先驱 | **RL 和信号处理的血缘** |
| Silver 在 UCL 读博时受 Demis Hassabis 招募进 DeepMind | **DeepMind 的 RL 帝国始于一次招聘** |
| Schulman (PPO 作者) 后来加入 OpenAI 做 RLHF | **PPO 是 RLHF 的基础设施** |
| Hafner 从 Dreamer 路线独立于 MuZero | **世界模型是平行进化** |

---

## 12. 失败方向：被淘汰的 RL 路线

> 承接 [`讲透AI历史/advanced/02`](../讲透AI历史/advanced/02-失败的教训被淘汰的方向.md) 的方法论：**失败和成功同等重要**。

### 12.1 表格方法的死亡（2000s）

1980s-1990s，RL 几乎全是表格方法（每个状态存一个值）。当状态空间超过 $10^6$，表格方法彻底失效——**维度灾难**。

**教训**：没有函数近似，RL 只能处理玩具问题。这是 DQN 范式转移的必要性。

### 12.2 纯策略迭代的困境（2000s-2010s）

策略迭代（policy iteration）在 1980s 是 MDP 的标准解法。但它需要：
1. 知道完整的环境模型（$P$ 和 $R$）
2. 在每步做精确的策略评估

两个条件在真实世界几乎不满足。**策略迭代被 model-free 方法（TD/Q-Learning）取代**。

### 12.3 进化策略（ES）的短暂复兴（2017）

2017 年，OpenAI 发表 *"Evolution Strategies as a Scalable Alternative to Reinforcement Learning"*——用进化策略替代 RL，号称在大规模并行上更好。

**结果**：ES 在简单环境（MuJoCo）上可行，但在复杂环境（Atari/围棋）上远不如 RL。**进化策略缺乏信用分配能力**——它不知道"哪一步做对了"，只知道"总回报高不高"。

**教训**：**没有信用分配（credit assignment），大规模 RL 不可行**。这是进化方法的根本局限。

### 12.4 基于模型的经典方法（2003-2015）

2000s 的 model-based RL（如 PILCO, Deisenroth & Rasmussen 2011）用高斯过程做环境模型——精确但极慢，只适合低维问题。

**教训**：model-based RL 的瓶颈一直是**模型不够好**。直到深度世界模型（Dreamer/MuZero），这条路线才真正起飞。

### 12.5 LLM Agent RL 的泡沫（2024-2026）

2024 年起，大量论文宣称用 RL 训练 LLM Agent（工具调用/网页浏览/代码执行）。但大多数工作的"成功"是：
1. 在窄域 benchmark 上刷分
2. reward 是人为设计的（容易 reward hack）
3. 泛化到真实任务时崩溃

**教训**：**Agent RL 的 reward 设计比 RLHF 更难**——LLM 对齐至少有人类偏好作 ground truth，Agent RL 的 reward（"任务完成了吗？"）往往是二元的、稀疏的、容易被 hack 的。这条路线仍在早期。

---

## 13. 路径依赖与偶然性

### 13.1 如果 Tesauro 没做 TD-Gammon

TD-Gammon（1992）是 RL 的"第一个证据"——证明无模型学习可以达到专家水平。如果 Tesauro 没有做这个实验，RL 可能在 1990s 被完全边缘化——**没有"可以工作的演示"，就没有资金和关注**。

TD-Gammon 让 Sutton-Barto 的研究在 1990s 维持了生命力，直到 DQN 的条件成熟。**一个实验可能保住了一个领域十年**。

### 13.2 如果 Christiano 2017 论文没有 OpenAI

Christiano 的 "Deep RL from Human Preferences" 发表在 2017 年，被引用千余次。但真正把它变成工业级技术的是 OpenAI 的 InstructGPT（2022）——因为只有 OpenAI 同时拥有 LLM（GPT-3）和 RL 工程能力（PPO 团队）。

如果 Christiano 不在 OpenAI、如果 OpenAI 没有 GPT-3、如果 Schulman（PPO 作者）不加入 OpenAI——**RLHF 可能永远不会爆发**。

### 13.3 如果 DeepSeek 没有开源 R1

DeepSeek-R1（2025.01）开源后，整个开源社区在数周内复现了 RLVR 训练。如果 R1 没有开源，RLVR 的训练方法可能仍然是闭源公司的秘密——**开源一个关键模型，可能加速整个领域 1-2 年**。

### 13.4 Sutton 的 *Bitter Lesson* 与 Scaling Law 的交叉

Sutton 2017 年的 *The Bitter Lesson*——"通用方法（搜索+学习）最终胜过人类知识"——深刻影响了 Ilya Sutskever 和 OpenAI 的 Scaling Law 信仰。**一篇 1500 字的博客，可能间接催生了 GPT-3/GPT-4 的训练策略**。

> 🎯 **路径依赖的核心教训**：RL 史上的关键转折点，几乎都依赖"**对的论文 × 对的人 × 对的机构 × 对的时机**"的交叉。**没有任何单一因素是充分的。**

---

## 14. 开放问题

1. **RL 能否提供预训练无法提供的增量能力？** 这是 RL 在 LLM 时代的存在论问题。如果答案是否，RL 将退化为"微调工具"。

2. **RLVR 的多样性坍缩能解决吗？** Limit of RLVR 揭示 RLVR 收窄输出分布。如果解决不了，RLVR 只能做"复习"不能做"发现"。

3. **世界模型能否成为 AGI 核心？** Dreamer/Genie 路线如果成功，RL 将从"policy 优化"变成"世界建模"——这是范式的又一次质变。

4. **Reward 设计能否自动化？** RLHF（学 reward model）/ RLVR（用规则）/ Constitutional AI（用 AI 自己做 reward）——三条路线的终局是什么？**Reward 是 RL 的阿喀琉斯之踵**。

5. **Decision Transformer 是否意味着 RL 不需要 Bellman？** 如果序列建模能做决策，Bellman 方程是否是必要的？**RL 的数学根基可能被动摇**。

6. **多智能体 RL 的终局？** AlphaStar（StarCraft）/ 多 Agent debate / Agent 社交——真实世界是多智能体的，但多智能体 RL 的理论远不如单智能体成熟。

7. **RL 能做到 sample efficient 吗？** 人类用几次经验就能学会新技能，RL 需要百万次。这个 gap 能缩小到多少？

---

## 15. 配套资源

### 15.1 项目内

| 资源 | 链接 | 定位 |
|------|------|------|
| RL 地基 | [00-为什么RL与MDP](./00-为什么RL与MDP.md) | MDP/Bellman/探索利用 |
| DQN | [01-Q-Learning与DQN](./01-Q-Learning与DQN.md) | 值函数方法 |
| PPO | [02-策略梯度与PPO](./02-策略梯度与PPO.md) | 策略梯度方法 |
| RLHF/DPO/GRPO | [03](./03-RLHF-DPO-GRPO.md) | LLM 对齐 |
| RLVR 极限 | [05](./05-RLVR的极限.md) | pass@k 反转 |
| 2026 前沿 | [07](./07-2026最新研究全景.md) | 全景索引 |
| Actor-Critic/SAC | [08](./08-Actor-Critic-SAC-ModelBased-OfflineRL.md) | CS285 硬通货 |
| AI 思想史方法论 | [`讲透AI历史/00`](../讲透AI历史/00-为什么学AI历史.md) | 本篇方法论基础 |
| 范式转移 | [`讲透AI历史/advanced/01`](../讲透AI历史/advanced/01-范式转移的库恩分析.md) | 库恩框架 |
| 世界模型 | [`讲透世界模型`](../讲透世界模型/) | Dreamer/Genie 谱系 |

### 15.2 经典论文（按时间线）

| 年份 | 论文 | 历史地位 |
|------|------|---------|
| 1898 | Thorndike, *Animal Intelligence* | 效果律——RL 的心理学起源 |
| 1957 | Bellman, *Dynamic Programming* | Bellman 方程——RL 的数学根基 |
| 1960 | Howard, *Dynamic Programming and Markov Processes* | MDP 形式化 |
| 1988 | Sutton, *Learning to Predict by TD* | TD 学习 |
| 1989 | Watkins, PhD thesis | Q-Learning |
| 1992 | Tesauro, *TD-Gammon* | 第一个专家级 RL |
| 1998 | Sutton & Barto, *RL: An Introduction* | RL 圣经 |
| 2013/2015 | Mnih et al., *DQN* | 深度 RL 范式转移 |
| 2016 | Silver et al., *AlphaGo* | 围棋革命 |
| 2017 | Silver et al., *AlphaZero* | 纯自我对弈 |
| 2017 | Schulman et al., *PPO* | 工业标准算法 |
| 2017 | Christiano et al., *Deep RL from Human Preferences* | RLHF 种子 |
| 2018 | Haarnoja et al., *SAC* | 最大熵 RL |
| 2020 | Schrittwieser et al., *MuZero* | 隐式世界模型 |
| 2021 | Chen et al., *Decision Transformer* | RL = 序列建模 |
| 2022 | Ouyang et al., *InstructGPT* | RLHF 工业化 |
| 2023 | Rafailov et al., *DPO* | 去 RM 对齐 |
| 2023 | Hafner et al., *DreamerV3* | 世界模型成熟 |
| 2025 | DeepSeek, *R1* | RLVR + reasoning |
| 2025 | Yue et al., *Limit of RLVR* | RLVR 边界揭示 |

### 15.3 关键书籍

| 书 | 作者 | 定位 |
|----|------|------|
| *Reinforcement Learning: An Introduction* (2nd, 2018) | Sutton & Barto | **RL 圣经** |
| *Dynamic Programming* (1957) | Bellman | RL 数学起源 |
| *Algorithms for Reinforcement Learning* (2010) | Csaba Szepesvári | 理论精简版 |
| *Deep Reinforcement Learning Hands-On* | Maxim Lapan | 工程实战 |

---

## 16. 费曼回炉

> L2 自检：能不能用大白话把 RL 思想史讲清楚？

### F2 卡壳点

- **卡点 A**：长期把 RL 的历史理解成"算法越来越强"的线性进步——从 Q-Learning 到 DQN 到 PPO 到 RLHF，像爬楼梯一样。重读思想史后才钉死：**RL 的进步不是线性爬楼梯，而是三次"换问法"**——从"刺激-反应怎么形成"（心理学）到"序贯决策怎么最优化"（Bellman/MDP），从"表格函数怎么算"（经典 RL）到"神经网络怎么泛化"（深度 RL），从"游戏得分怎么最大化"（DQN/AlphaGo）到"人类偏好和推理能力怎么训"（RLHF/RLVR）。每次"换问法"都不是"更好的答案"，而是"**换了问题**"——这是库恩范式转移的核心。

- **卡点 B**：以为 DQN 是"理论突破"——某个天才发明了新算法。重读史料后才意识到 DQN 的核心算法（Q-Learning）是 1989 年的，DQN 的真正创新是**三个工程技巧**（经验回放 + target network + CNN）。**RL 史上最大的"突破"不是算法创新，是工程拼装**——这呼应 Sutton 的 *Bitter Lesson*。

- **卡点 C**：以为 RLHF 是 2022 年突然发明的。重读史料才知道 RLHF 的种子在 Christiano 2017——比 ChatGPT 早 5 年。**最重要的技术往往"沉睡"多年才被对的载体激活**。

### F3 术语翻译

- **范式转移（paradigm shift）** → 不是"更好的方法取代旧方法"，而是"**换了问题**"——深度 RL 不是"更会算表格"，而是"不再用表格，改用神经网络"
- **Bitter Lesson** → **"别太聪明，用暴力"**——人类精心设计的特征和启发式，最终都被通用方法+算力超越
- **Deadly Triad** → 函数近似 + 自举 + off-policy 三件事同时做就会发散——就像"同时踩油门和刹车还在冰面上"
- **RLVR 的 pass@k 反转** → 训练后"平均分"涨了，但"最好可能的分"降了——像考试训练让你平均分提高但扼杀了灵光一现的天才解法

### F4 回炉

- **v1（错误直觉）**：以为 RL 的历史是"从简单到复杂"的技术进步——Q-Learning → DQN → AlphaGo → RLHF，越来越厉害。
- **v2（修正后）**：RL 的历史是三次"换问法"——每次范式转移都是 reward 信号或 policy 架构的质变（游戏分数→人类偏好→可验证推理）。而且**当前 RL 的"成功"可能是暂时的**——DPO 绕过 RL、RLVR 收窄多样性、预训练才是能力主源。RL 在 LLM 时代到底是"核心引擎"还是"可选精调器"，这个问题**尚未定论**。diff 在于从"进步叙事"升级为"**存在论危机叙事**"——RL 正面临"自己是否必要"的质疑。

---

📌 **下一步**

1. **回到** [00-为什么RL与MDP](./00-为什么RL与MDP.md) 学 MDP 数学地基
2. **深入** [07-2026最新研究全景](./07-2026最新研究全景.md) 看 2026 前沿
3. **读** [`讲透AI历史/00`](../讲透AI历史/00-为什么学AI历史.md) 理解思想史方法论
4. **读** Sutton & Barto *Reinforcement Learning* (2nd ed.) 第一章（历史概述）
5. **读** Sutton *"The Bitter Lesson"* (2017, 1500 字博客)——影响 RL 和整个 AI 的深刻洞察
6. **思考** §14 的 7 个开放问题——每个都是博士论文级方向

---

### ✍️ 思考题

1. **方法论题**：如果用一个词概括 RL 120 年思想史的核心矛盾，你会选什么？（提示：探索 vs 利用？reward 设计 vs 能力涌现？model-free vs model-based？）
2. **反事实题**：如果 2013 年 DeepMind 没有发表 DQN，RL 今天会在哪里？可能延迟多少年？
3. **判断题**：RLVR 是"第三次范式转移"还是"RLHF 的变体"？给出你的判断和理由。
4. **批判题**：Sutton 的 *Bitter Lesson* 在 RL 史上被验证了几次？有没有反例（人类知识胜过通用方法的案例）？
5. **延伸题**：Decision Transformer 声称"RL 不需要 Bellman 方程"。如果你是 RL 社区的"正统派"，你会怎么反驳？
