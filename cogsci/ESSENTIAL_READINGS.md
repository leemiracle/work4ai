# 经典论文与著作导读 — 认知科学的 15 块基石

> **为什么读经典**：认知科学的理论不是凭空产生的——每一篇经典论文都是一个**思想炸弹**，改变了人们看待心智的方式。本文档不是论文清单，是**导读**——告诉你每篇论文的核心贡献、为什么必读、与 AI 的关系。
>
> **如何使用**：按 §16 的阅读路线选择适合你的顺序。不必全读——先读 ★ 标记的 5 篇核心论文，再按兴趣扩展。
>
> **配套**：[HISTORY.md](HISTORY.md)（思想史背景）+ [THINKERS.md](THINKERS.md)（作者列传）+ [RESOURCES.md](RESOURCES.md)（资源清单）

---

## §0 阅读框架

每篇论文用统一结构：
1. **作者 / 年份 / 出处**（完整引用）
2. **核心贡献**（一句话说清它改变了什么）
3. **关键论点**（2-3 个要点）
4. **为什么必读**（它的历史地位）
5. **与 AI / interp 的关系**（对当代 AI 研究的意义）
6. **难度**（★ = 可读科普 / ★★ = 需要背景 / ★★★ = 专业论文）

---

## §1 ★ Turing (1950) — Computing Machinery and Intelligence

**引用**：Turing, A. M. (1950). Computing Machinery and Intelligence. *Mind*, 59(236), 433-460.

**核心贡献**：提出了"模仿游戏"（图灵测试）——用**行为标准**判断机器是否有智能。

**关键论点**：
1. **不问"机器能否思考"，而问"机器能否通过对话被区分出来"**——把哲学问题转化为经验问题
2. **预测**：到 2000 年，机器能在 5 分钟对话中骗过 30% 的裁判——**基本已实现（LLM 时代）**
3. **回应了 9 个反对意见**（神学/意识/各种限制）——展示了惊人的预见性

**为什么必读**：定义了"什么是智能"的行为主义标准——这是所有 AI benchmark 的哲学根基。

**与 AI / interp 的关系**：
- **图灵测试 = 行为评估**：LLM benchmark 哲学一致——用行为推断能力
- **图灵测试的局限**：只看输入输出——interp 正是要**超越图灵测试**，打开黑箱
- **"不问内部"的哲学问题**：图灵选择不讨论内部机制，interp 选择**必须**讨论内部机制

**难度**：★（非常可读，文笔优雅）

---

## §2 ★ Chomsky (1957) — Syntactic Structures

**引用**：Chomsky, N. (1957). *Syntactic Structures*. Mouton.

**核心贡献**：推翻了结构主义语言学——证明语言有**递归结构**，不能用统计方法（N-gram）充分描述。

**关键论点**：
1. **"Colorless green ideas sleep furiously"**——语法正确但无意义的句子，证明句法独立于语义
2. 语言是**规则系统**（生成语法），不是习惯集合
3. 句法有**层次结构**（树结构），不是线性序列

**为什么必读**：语言学革命的开端——直接催生了认知革命（1956），改变了"语言是什么"的根本理解。

**与 AI / interp 的关系**：
- **LLM 的直接挑战**：Chomsky 说语言需要规则系统，但 GPT 从纯统计中学到了语言——**这是对他理论的最大冲击**
- **组合性争论**：LLM 的组合性能力如何？这是符号主义 vs 联结主义的当代版本
- **interp 可以检验**：LLM 内部是否形成了类似句法树的表征？

**难度**：★★（薄书但需要语言学基础，117 页）

---

## §3 ★ Marr (1982) — Vision

**引用**：Marr, D. (1982). *Vision: A Computational Investigation into the Human Representation and Processing of Visual Information*. W. H. Freeman.

**核心贡献**：提出了**三层级分析框架**——理解任何信息处理系统需要从计算、算法、实现三个层次分析。

**关键论点**：
1. **三层分析**：
   - **计算层**（Computational）：系统**在算什么**？为什么？
   - **算法层**（Algorithmic）：**怎么**算？什么表示和过程？
   - **实现层**（Implementational）：**物理上**怎么实现？
2. **计算层最重要**——如果你不知道系统在算什么，算法和实现层的研究是盲目的
3. **视觉的分层模型**：primal sketch → 2.5D sketch → 3D model
4. **零交叉（zero-crossing）**：从 $\nabla^2 G$ 的过零点提取边缘

**为什么必读**：**这是 mech interp 的方法论圣经。** Marr 的三层框架至今是 interp 研究的隐性结构——好的 interp 论文先问"模型在算什么"（计算层），再找"用什么回路"（算法层），最后看"怎么实现"（实现层）。

**与 AI / interp 的关系**（最重要）：
- **interp 的三层**：
  - 计算层 = LLM 在学什么表征？（探针/表征几何）
  - 算法层 = LLM 用什么回路？（induction heads/copy circuit）
  - 实现层 = 权重矩阵/GPU 细节
- **Marr 的忠告**：不要只在实现层做 interp——如果你只看权重，不知道"在算什么"，你只是看到了数字
- **计算层是 interp 的终极目标**

**难度**：★★★（视觉部分需要数学，但三层框架的前两章非常可读）

---

## §4 Newell & Simon (1972) — Human Problem Solving

**引用**：Newell, A. & Simon, H. A. (1972). *Human Problem Solving*. Prentice-Hall.

**核心贡献**：用"问题空间 + 搜索"框架系统化地模拟人类问题解决——奠定了**认知架构**范式。

**关键论点**：
1. **问题空间**（Problem Space）：思维 = 在问题空间中搜索；问题空间 = 初始状态 + 目标状态 + 算子
2. **启发式搜索**：手段-目的分析（means-ends analysis）、爬山法（hill climbing）
3. **产生式系统**（Production System）：IF-THEN 规则——知识以条件-行动规则组织
4. **协议分析**（Protocol Analysis）：让被试"大声思考"，分析其问题空间搜索路径

**为什么必读**：确立了"认知 = 搜索"的范式——影响了 ACT-R、SOAR 等认知架构，至今影响 AI 规划/推理。

**与 AI / interp 的关系**：
- **问题空间 → 思维链**（Chain-of-Thought）：CoT 本质上是让 LLM 在问题空间中搜索
- **产生式系统 → 模块化回路**：LLM 内部是否形成了 IF-THEN 类型的回路？
- **搜索范式 vs 联结主义**：LLM 不是显式搜索，而是"一步到位"的并行处理——这是对符号 AI 的颠覆

**难度**：★★★（厚重，但核心思想在前几章）

---

## ★5 Rumelhart, McClelland & PDP Group (1986) — Parallel Distributed Processing

**引用**：Rumelhart, D. E., McClelland, J. L., & the PDP Research Group (1986). *Parallel Distributed Processing: Explorations in the Microstructure of Cognition* (Vols. 1-2). MIT Press.

**核心贡献**：联结主义的全面宣言——证明**分布式表征 + 并行处理 + 反向传播**可以产生涌现认知能力。

**关键论点**：
1. **分布式表征**（Distributed Representation）：概念不是单个符号，而是跨神经元的激活模式
2. **并行处理**：多个单元同时计算
3. **反向传播**（Backpropagation）：通过误差反向传播学习权重（Rumelhart, Hinton & Williams, 1986）
4. **涌现**：复杂行为从简单单元的相互作用中涌现
5. **过去时模型**（Rumelhart & McClelland 1986）：网络学习英语动词过去时——无需规则，通过模式联想，模仿了儿童的 U 形曲线

**为什么必读**：**深度学习的思想源头。** PDP 的核心思想——分布式表征 + 梯度下降学习——直接演化成了今天的大规模神经网络。AlexNet/Transformer/GPT 都是 PDP 的直系后裔。

**与 AI / interp 的关系**：
- **分布式表征 → interp 的核心挑战**：如果表征是分布式的，如何找到"概念"在哪里？——SAE/探针正是回答这个问题
- **涌现 → LLM 的涌现能力**：PDP 预言了"复杂行为从简单规则中涌现"——LLM 的 in-context learning 正是这种涌现
- **超叠加**（Superposition）：PDP 的分布式表征思想的深化——一个神经元可以参与多个概念的表征

**难度**：★★★（两卷厚重，建议读 Vol.1 第 1-3 章和过去时模型章节）

---

## ★6 Friston (2010) — The Free-Energy Principle

**引用**：Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138.

**核心贡献**：提出**自由能原理**——一个可能统一感知/行动/学习/注意/情绪/精神病理的数学框架。

**关键论点**：
1. **核心原理**：任何自组织系统（包括大脑）都在最小化其**变分自由能**：

$$\mathcal{F} = D_{KL}[q(s) \| p(s|o)] + [-\ln p(o)]$$

2. **两种最小化方式**：
   - **感知推理**：更新内部模型 → 学习/感知
   - **主动推理**：改变感觉输入 → 行动
3. **统一框架**：感知、行动、学习、注意、情绪都可以用"最小化预测误差"解释
4. **预测编码**：层级系统中只传递预测误差——大大减少信息传输量

**为什么必读**：可能是认知科学自 1956 认知革命以来**最大的理论统一尝试**。自由能原理不是解释某一个认知现象，而是试图**用同一个原理解释所有认知现象**。

**与 AI / interp 的关系**（极重要）：
- **LLM = 预测机器**：next-token prediction 本质上就是预测处理——LLM 训练目标就是最小化预测误差
- **自由能 ≈ 交叉熵损失**：$\mathcal{L}_{\text{CE}} = -\ln p(o) \approx \mathcal{F}$——数学同构
- **主动推理 → RL 替代**：基于自由能的 Active Inference AI 正在发展
- **interp 的理论框架**：如果 LLM 是预测机器，interp 的目标就是理解 LLM 学到了什么"世界模型"
- **幻觉 = 预测过强**：如果精神分裂 = 先验过强，LLM 幻觉也可能 = 先验过强

**难度**：★★★（数学密集，建议先读 Clark《Surfing Uncertainty》的科普版）

---

## ★7 Clark & Chalmers (1998) — The Extended Mind

**引用**：Clark, A. & Chalmers, D. J. (1998). The Extended Mind. *Analysis*, 58(1), 7-19.

**核心贡献**：提出**延展心智论题**——认知过程不限于头骨和皮肤，外部工具（笔记本/计算器/AI）是认知的一部分。

**关键论点**：
1. **"认知过程的边界不在皮肤上"**
2. **Otto 例子**：阿尔茨海默症患者 Otto 用笔记本记录一切——他的笔记本就是他的记忆，与正常人脑中的记忆功能上等价
3. **耦合系统**（Coupled System）：大脑 + 可靠使用的外部工具 = 认知系统
4. **信任原则**（Parity Principle）：如果外部过程做的是内部认知做的事，它就**是**认知

**为什么必读**：挑战了"认知 = 脑内计算"的根本假设——延展心智是 4E 认知（Embodied/Embedded/Extended/Enacted）的核心文本。

**与 AI / interp 的关系**：
- **人 + AI = 认知单元**：如果延展心智是对的，使用 Copilot/ChatGPT 的人 + AI 构成一个认知系统
- **interp 不只是理解 AI**：是理解这个**混合认知系统**
- **工具使用改变表征**：LLM 使用工具（搜索/代码执行）是否会改变其内部表征？——interp + tool use 前沿

**难度**：★★（哲学论文，但写得清楚——只有 13 页）

---

## §8 Baars (1988) — A Cognitive Theory of Consciousness

**引用**：Baars, B. J. (1988). *A Cognitive Theory of Consciousness*. Cambridge University Press.

**核心贡献**：提出**全局工作空间理论**（Global Workspace Theory, GWT）——意识是信息在全脑"广播"的结果。

**关键论点**：
1. **剧场隐喻**：意识像聚光灯——大量无意识处理在"后台"并行运行
2. **全局广播**：当信息进入**全局工作空间**（Global Workspace）被广播给整个系统，就变成**有意识**
3. **有限容量**：工作空间容量有限——只有一条信息能进入意识
4. **后续发展**：Dehaene 的**全局神经元工作空间**（GNW, 2014）——用神经科学实现 GWT

**为什么必读**：第一个**可操作**的意识理论——可以用实验检验（"点火"信号可被 EEG 测量）。

**与 AI / interp 的关系**：
- **AI 意识评估**：如果 AI 有全局工作空间架构→可能有某种意识——Butlin et al. (2023) 用 GWT 评估 AI 意识
- **interp 寻找"全局工作空间"**：LLM 内部是否有类似"全局广播"的机制？——注意力机制可能是候选
- **"意识"的可操作定义**：GWT 提供了一个**可检验的**意识标准——比哲学争论有用

**难度**：★★（需要认知心理学基础）

---

## §9 Kahneman (2011) — Thinking, Fast and Slow

**引用**：Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

**核心贡献**：系统化**双系统理论**（System 1 vs System 2）——人类思维有两种模式：快速直觉 vs 慢速推理。

**关键论点**：
1. **系统 1**（快）：自动、直觉、并行、无意识——"看到 2+2=4"
2. **系统 2**（慢）：受控、推理、序列、有意识——"算 17×24"
3. **认知偏差**：锚定效应、可得性启发式、代表性启发式、损失厌恶——系统 1 的系统性错误
4. **前景理论**（Kahneman & Tversky 1979）：人类对损失的痛苦大于对等量收益的快乐——**颠覆了期望效用理论，2002 诺奖**

**为什么必读**：行为经济学和认知心理学的**终极科普**——让数百万人理解了"人类思维的系统偏差"。

**与 AI / interp 的关系**：
- **LLM = System 1？**：LLM 是快速直觉（一步生成），缺少 System 2 的慢速推理——CoT/o1 正在给 LLM 加 System 2
- **AI 的认知偏差**：LLM 也有偏差（训练数据偏差/confirmation bias）——interp 可以研究这些偏差的机制
- **benchmark 设计**：认知偏差实验可以改编为 AI 评估——测 LLM 是否有同样的偏差

**难度**：★（顶级科普，非常可读）

---

## §10 Damasio (1994) — Descartes' Error

**引用**：Damasio, A. (1994). *Descartes' Error: Emotion, Reason, and the Human Brain*. Putnam.

**核心贡献**：证明**情绪不是理性的敌人，而是理性不可或缺的组成部分**——推翻了"情绪 vs 理性"的笛卡尔框架。

**关键论点**：
1. **Phineas Gage 案例**：1848 年铁路工人 Gage 前额叶受损后——认知能力正常，但无法做决策、社会行为崩溃。**情绪不是"理性思维的障碍"，而是决策的基础**
2. **躯体标记假说**（Somatic Marker Hypothesis）：身体状态（情绪）标记不同选项的价值——帮助你快速排除坏选项
3. **理性需要情绪**：没有情绪反馈的纯理性系统会被无限可能性淹没（Damasio 的患者能列出优缺点但无法选择）

**为什么必读**：颠覆了西方哲学"理性 vs 情绪"的二分法——情绪不是需要克服的，而是**理性计算的一部分**。

**与 AI / interp 的关系**：
- **LLM 有"情绪"吗？**：如果情绪对决策不可或缺，LLM 没有"身体情绪"是否意味着它的"决策"本质不同？
- **RLHF 的"情绪"维度**：人类偏好（reward signal）是否包含了"躯体标记"？——训练 LLM 的偏好可能包含隐性情绪编码
- **奖励信号 = 躯体标记？**：如果 reward signal 扮演类似"躯体标记"的角色，那 RLHF 训练的 LLM 某种程度上"内化"了人类情绪

**难度**：★（科普，有中文版《笛卡尔的错误》）

---

## §11 Pinker (1994) — The Language Instinct

**引用**：Pinker, S. (1994). *The Language Instinct: How the Mind Creates Language*. William Morrow.

**核心贡献**：把 Chomsky 的语言学翻译成大众语言——论证语言是**演化形成的本能**。

**关键论点**：
1. **语言本能**：语言不是文化产物，是**生物本能**——像蜘蛛结网一样自然
2. **语言获得是自动的**：儿童不需要正式教育就能获得语言（只要有正常的社会输入）
3. **关键期**：语言获得有时间窗口——过了关键期，获得能力急剧下降
4. **普遍性**：所有人类语言共享深层结构（支持 Chomsky 的普遍语法）

**为什么必读**：最成功的语言学科普——让数百万人理解了"语言是本能"。

**与 AI / interp 的关系**：
- **LLM 挑战语言本能论**：GPT 从纯文本统计中学语言——不需要"本能"
- **但**：Transformer 的架构先验（注意力/位置编码）可能是某种"数字本能"——先天结构不一定是生物的
- **interp 检验"普遍语法"**：LLM 内部是否形成了类似"句法参数"的表征？

**难度**：★（顶级科普）

---

## §12 Dennett (1991) — Consciousness Explained

**引用**：Dennett, D. C. (1991). *Consciousness Explained*. Little, Brown and Company.

**核心贡献**：提出**多重草稿模型**——意识不是单一"剧场"，没有中央"自我"在看屏幕。

**关键论点**：
1. **多重草稿模型**：信息在大脑中并行处理，没有"中央编辑"——意识是事后的叙事重构
2. **用户幻觉**（User Illusion）：意识是大脑制造的**简化界面**——就像电脑桌面（图标不是真实的，但有用）
3. **意向性姿态**（Intentional Stance）：我们"假装"系统有信念和欲望——对人类和 AI 都适用——这是一种预测策略
4. **否认 qualia**：主观感觉不是真实存在的"东西"，而是大脑的简化叙事

**为什么必读**：最系统的"消除主义"意识理论——直接挑战 Chalmers 的"困难问题"。

**与 AI / interp 的关系**：
- **意向性姿态**：我们对 LLM 说"它'知道'、它'欺骗'"——这是有用的预测策略，但不要过度本体论化
- **多重草稿 → LLM 并行回路**：LLM 没有中央自我——多回路并行——interp 发现的就是这种并行性
- **意识 = 用户幻觉**：如果 Dennett 对，"AI 有意识吗"的问题本身就是错误提问

**难度**：★★（需要哲学基础，但 Dennett 写得好）

---

## §13 Chalmers (1995) — Facing Up to the Problem of Consciousness

**引用**：Chalmers, D. J. (1995). Facing Up to the Problem of Consciousness. *Journal of Consciousness Studies*, 2(3), 200-219.

**核心贡献**：区分意识的**简单问题**和**困难问题**——重新定义了意识研究的议程。

**关键论点**：
1. **简单问题**（Easy Problems）：大脑如何整合信息、控制行为、产生报告——**原则上**科学可解
2. **困难问题**（Hard Problem）：**为什么**物理过程伴随着主观体验？
3. **哲学僵尸**：一个行为上完全相同但没有主观体验的"僵尸"在逻辑上可能——存在解释鸿沟
4. **信息双重原理**：意识可能和信息一样是**基本属性**

**为什么必读**：定义了当代意识研究的核心问题——每个意识研究者都要面对困难问题。

**与 AI / interp 的关系**：
- **"AI 有意识吗"的哲学框架**：即使 interp 完美理解 LLM 机制，仍面临解释鸿沟
- **困难问题 vs interp**：interp 回答的是"简单问题"（机制如何工作），但无法回答"困难问题"（为什么有体验）
- **意识的可检验指标**：Chalmers 倾向于 IIT 等指标——但这是间接证据

**难度**：★★（哲学论文，但论证清楚）

---

## §14 Tononi (2004) — An Information Integration Theory of Consciousness

**引用**：Tononi, G. (2004). An Information Integration Theory of Consciousness. *BMC Neuroscience*, 5, 42.

**核心贡献**：提出**整合信息论**（IIT）——用 $\Phi$ 量化意识，意识 = 信息整合能力。

**关键论点**：
1. **意识 = 整合信息**：系统整合信息的能力用 $\Phi$（Phi）量化
2. **$\Phi$ 的含义**：衡量系统"整体大于部分之和"的程度——系统内部的信息不可被独立部分完全解释
3. **可检验预测**：$\Phi$ 高的系统有意识（人脑清醒 > 睡眠 > 麻醉）
4. **惊人推论**：任何高 $\Phi$ 系统都有某种意识——包括 AI

**为什么必读**：第一个**量化**意识的理论——可以用 TMS-EEG 实验检验，区分意识状态。

**与 AI / interp 的关系**：
- **AI 意识检测**：如果 LLM 的 $\Phi$ 高→可能有意识？——但当前 Transformer 的前馈架构 $\Phi$ 很低
- **IIT 对架构的要求**：IIT 预测递归架构 $\Phi$ 高——这暗示当前 LLM（前馈为主）意识水平低
- **可检验的 AI 意识标准**：IIT 提供了一个**数学上可计算**的意识指标——虽然争议巨大

**难度**：★★★（数学密集，但核心概念可从 Tononi 的科普书理解）

---

## §15 Smith et al. (2024) / 最近 — LLM 作为认知模型

**引用方向**（多篇代表）：
- Cummins et al. (2024). LLMs as cognitive models.（及其引用的多篇论文）
- Butlin, P. et al. (2023). Consciousness in Artificial Intelligence: Insights from the Science of Consciousness.（AI 意识评估）
- Goldstein & Levinstein (2024). Open Problems in mech interp.

**核心贡献**：开始严肃讨论 **LLM 作为认知模型** 的可能性和 AI 意识的检测。

**关键论点**：
1. **LLM 的表征与大脑的比较**：如果 LLM 的表征与人类大脑相似（已在语言区发现证据），LLM 就是**可观察的认知系统**
2. **AI 意识评估清单**：用 GWT/IIT/HOT 等理论评估 AI 意识——提出初步的可检验标准
3. **Mech Interp 的前沿问题**：如何系统化地理解 LLM 的表征和回路？

**为什么必读**：代表了认知科学与 AI **重新汇流**的前沿——2024-2026 年最活跃的交叉领域。

**与 AI / interp 的关系**：这就是 interp 本身——认知科学的理论框架指导 interp，interp 的发现检验认知科学理论。

**难度**：★★★（需要认知科学 + interp 双重背景）

---

## §16 阅读路线（按目标选择）

### 路线 A：理解 interp 的认知科学根基（★ 推荐）

```
1. Marr 1982《Vision》前 2 章（★ 三层框架）
   ↓
2. Friston 2010 论文 + Clark《Surfing Uncertainty》（预测处理）
   ↓
3. Kahneman《Thinking, Fast and Slow》（双系统 → System 1 vs System 2）
   ↓
4. Baars 1988 / Dehaene GNW（全局工作空间 → AI 意识评估）
   ↓
5. 最近 LLM 认知模型论文（前沿交叉）
```

### 路线 B：理解语言认知

```
1. Chomsky 1957《句法结构》
   ↓
2. Pinker 1994《语言本能》
   ↓
3. Rumelhart & McClelland 1986 过去时模型（联结主义对 Chomsky 的挑战）
   ↓
4. interp 论文：LLM 内部的句法表征
```

### 路线 C：理解意识问题

```
1. Dennett 1991《Consciousness Explained》（幻觉论）
   ↓
2. Chalmers 1995（困难问题）
   ↓
3. Baars 1988（全局工作空间）
   ↓
4. Tononi 2004（IIT）
   ↓
5. Butlin et al. 2023（AI 意识评估）
```

### 路线 D：理解认知科学全貌（按历史顺序）

```
1. Turing 1950（计算心智）
   ↓
2. Chomsky 1957（语言革命）
   ↓
3. Newell & Simon 1972（符号 AI）
   ↓
4. Marr 1982（三层框架）
   ↓
5. PDP 1986（联结主义）
   ↓
6. Dennett 1991 / Chalmers 1995（意识）
   ↓
7. Clark & Chalmers 1998（延展心智）
   ↓
8. Friston 2010（自由能原理）
   ↓
9. Kahneman 2011 / Damasio 1994（双系统 / 情绪）
   ↓
10. 2024+ 前沿（LLM 认知模型）
```

---

## §17 核心论文优先级表

| 优先级 | 论文 | 理由 |
|--------|------|------|
| ★★★ | **Marr 1982** | interp 方法论根基，必读 |
| ★★★ | **Friston 2010** | 理解 LLM = 预测机器 |
| ★★★ | **PDP 1986** | 深度学习思想源头 |
| ★★ | Turing 1950 | 计算心智的起点 |
| ★★ | Kahneman 2011 | 双系统理论，可读性最高 |
| ★★ | Clark & Chalmers 1998 | 延展心智，哲学影响大 |
| ★★ | Dennett 1991 | 意识幻觉论 |
| ★★ | Chalmers 1995 | 困难问题 |
| ★ | Chomsky 1957 | 语言革命（但被 LLM 挑战）|
| ★ | Pinker 1994 | 语言科普 |
| ★ | Damasio 1994 | 情绪与理性 |
| ★ | Baars 1988 | 全局工作空间 |
| ★ | Tononi 2004 | IIT |
| 参考 | Newell & Simon 1972 | 历史 |
| 前沿 | 2024 LLM 认知模型 | 最新 |

---

## §18 一个反直觉的建议

> **先读 Marr 和 Friston，再读任何 interp 论文。**
>
> 大多数 interp 研究者直接跳到技术细节——探针怎么设计、SAE 怎么训练、回路怎么分析——但不知道**为什么要这样做**。
>
> Marr 告诉你：interp 的目标是**计算层理解**（模型在学什么），不只是**实现层**（权重长什么样）。
>
> Friston 告诉你：LLM 训练不是"最小化交叉熵"这么简单——它是"构建世界模型，最小化对世界的意外"。同一个事实，完全不同的理解深度。
>
> **认知科学经典论文的价值不在于"知识"，而在于"思考工具"。** Marr 的三层框架和 Friston 的自由能原理是**你一辈子都能用的分析工具**——比任何单个 interp 实验都更有价值。

---

**完成日期**：2026-08-13
**配套**：[HISTORY.md](HISTORY.md)（思想史）+ [THINKERS.md](THINKERS.md)（列传）+ [RESOURCES.md](RESOURCES.md)（资源清单）+ [README.md](README.md)（领域总览）
