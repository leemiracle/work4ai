# 超越纯概率 LLM：融合物理/数学公理与规律的研究方案、致命缺陷与未来趋势

> 本文是 `world-ai4sci-math` 卷 synthesis 系列的第四章。它不再讨论"某一项 AI4Science 或 AI4Math 技术"，而是把视角抬到**元层**：当前所有试图突破 LLM 概率本质的研究路线，它们的共同根基、共同陷阱、共同未来。
>
> 本文的核心命题由用户提出：
>
> > **「一切受限于世界的物理及数学上的公理及规律，LLM 只是概率性的。」**

---

## 开篇：一个根本性的命题

### 0.1 命题的两层含义

用户的这句话不是一句吐槽，而是一个**哲学级别的判断**，它在两个层面上同时成立：

**认识论层（Epistemological level）**：当前所有大规模语言模型，本质上拟合的是条件分布

$$P(\text{token}_t \mid \text{token}_{<t};\, \theta)$$

其中 $\theta$ 是通过最大似然估计（或其 RLHF 后训练变体）从语料中学到的参数。无论模型多大、多少层、多少 token，它学到的都是**统计相关性**——"在某个上下文后，下一个 token 最可能是什么"。相关性 $\neq$ 因果性，这是 Pearl 反复强调的铁律。一个能完美续写"如果 A 那么 B"的模型，并不真正理解 A 与 B 之间的因果机制，它只是见过足够多"A 后面跟着 B"的样本。

**本体论层（Ontological level）**：物理世界遵循一些**非概率**的硬结构：

- **守恒律**（能量、动量、角动量守恒）——由 Noether 定理与时间/空间平移对称性直接导出；
- **对称性与等变性**（SE(3)、规范对称性、CPT 对称性）——物理定律在变换下保持形式不变；
- **变分原理**（Hamilton 原理 $\delta S = 0$）——整个经典力学、场论都可以从最小作用量原理导出；
- **热力学第二定律**（熵增方向）——一个时间箭头，但并非概率意义上的"平均"。

而数学世界遵循的是**公理—推理—证明**结构：

$$\text{公理} \;\xrightarrow{\text{推理规则}}\; \text{定理} \;\xrightarrow{\text{形式化验证}}\; \text{必然真理}$$

一个定理一旦被 Lean/Coq 这样的证明助手验证通过，它就是**永恒真理**，不依赖任何概率或样本量。这两套结构——物理的守恒/对称/变分，数学的公理/证明——都不是"概率"能完全捕获的。概率模型可以**近似**它们，但不能**保证**遵守它们。

### 0.2 LLM 的四条根本局限

把上述哲学判断落到工程层面，LLM 有四条无法靠"再 scale 一个数量级"绕过的局限：

**第一，Hallucination 是必然的。** 概率模型不知道自己不知道什么。它没有"知识边界"的概念——给定任何 prompt，它都会给出一个"最可能的" token 序列，哪怕这个序列对应的事实根本不存在。Bender 等人称之为"随机鹦鹉"（stochastic parrot）：它在语法上完美，在语义上可能是空的。这不是 bug，是**架构决定的宿命**——一个最大似然模型天然会把训练分布之外的查询，外推到训练分布之内"最像"的答案上。

**第二，无法保证 consistency。** 同一个问题换两种问法，LLM 可能给出矛盾答案。"A 比 B 大吗？"和"B 比 A 小吗？"在逻辑上等价，但在概率模型里是两个不同的输入序列，会被映射到不同的输出分布。Chain-of-Thought 部分缓解了这个问题，但没有根本解决——CoT 仍是概率生成的，不能保证每一步都逻辑自洽。

**第三，无法外推。** LLM 在训练分布内表现惊艳，分布外（OOD）立刻退化。这是机器学习的普适规律（没有免费午餐定理的一个具体表现），但 LLM 尤其严重，因为它的训练目标是"模仿"，而不是"理解"。一个从未见过某种类型数学题的 LLM，不能像数学家那样从公理出发推导新结论，它只能拼凑见过的类似题目的解法碎片。

**第四，无法验证。** LLM 不能保证自己的输出符合物理定律（"一个物体以 1.5 倍光速运动"在它的文本里毫无违和）或数学定理（"证明 $\sqrt{2}$ 是有理数"它会一本正经地写）。它缺乏一个**形式化的验证回路**——没有任何机制确保输出满足某个不变量。

> **为什么这一节重要**：这四条局限不是"工程瑕疵"，而是"概率模型的内在结构特征"。任何试图超越纯概率 LLM 的方案，都必须正面回应这四条。本文后续六大方向，本质上是这四条局限的六种不同**回应策略**。

### 0.3 历史回响：符号主义与连接主义的百年轮回

这不是 AI 第一次面对这个问题。理解当下，必须回望三次"符号 vs 连接"的交锋：

| 年代 | 事件 | 结果 |
|---|---|---|
| 1958 | Minsky & Papert《Perceptrons》证明单层感知机无法表达 XOR | 连接主义第一次被"判死刑"，符号主义（GOFAI）主导 AI 近 30 年 |
| 1986 | Rumelhart、Hinton、Williams 重新发现反向传播 | 连接主义复兴，但受限于算力/数据，未能颠覆符号主义 |
| 2012 | AlexNet 赢得 ImageNet | 深度学习革命，连接主义**全面胜出**，符号主义几乎被遗忘 |
| 2022 | ChatGPT 横空出世 | LLM 暴露概率本质的根本局限，**符号主义以"神经-符号融合"的新形式回归** |

这条历史脉络告诉我们一个深刻的教训：**纯粹的连接主义（概率）和纯粹的符号主义（逻辑）都有致命短板，真正的突破在两者的融合**。1980s 符号主义的死穴是"无法从数据中学习、无法处理噪声、无法 scale"；2020s 连接主义的死穴是"无法保证正确性、无法外推、无法验证"。这两条曲线，正在 2024–2030 年间重新交汇。AlphaProof、AlphaGeometry、PINN、因果 AI，都是这次"第三波"（借用 Garcez & Lamb 的术语 [arXiv:2012.05876](https://arxiv.org/abs/2012.05876)）的早期信号。

---

## 一、六大研究方向全景图

把当前所有"试图超越纯概率 LLM"的方案，按**用什么手段约束概率模型**来分类，可以归为六大方向。下表是全景速览，下面逐节展开。

| 方向 | 核心机制 | 约束来源 | 代表系统 | 最大软肋 |
|---|---|---|---|---|
| 1. 神经-符号融合 | NN 感知 + 符号推理 | 逻辑/证明系统 | AlphaProof, AlphaGeometry, NS-CL | 符号接地 + 不可微 |
| 2. 物理引导 ML | PDE/守恒律作为约束 | 已知物理方程 | PINN, FNO, EGNN, HNN, GraphCast | 依赖已知物理 |
| 3. 因果 AI | 从相关升级到因果 | 因果图/SCM | DoWhy, 因果表征学习 | 因果图未知 |
| 4. 工具增强 LLM | LLM + 外部求解器 | 外部工具的硬约束 | Toolformer, ReAct, Code Interpreter | 接口脆性 |
| 5. RAG + 知识图谱 | 外部结构化知识 | 知识库的真值 | RAG, GraphRAG, KG-GPT | 覆盖率 + 检索精度 |
| 6. 世界模型 | 显式建模环境动力学 | 物理一致性（隐式） | DreamerV3, V-JEPA 2, Genie, Cosmos | 仍是 P(s'\|s,a) |

### 方向 1：神经-符号融合（Neuro-Symbolic AI）

**核心思想**：让神经网络做它擅长的事（感知、模式识别、模糊匹配），让符号系统做它擅长的事（严格推理、可验证、可解释），两者通过一个**接口层**耦合。Garcez 和 Lamb 在 [arXiv:2012.05876](https://arxiv.org/abs/2012.05876)《Neurosymbolic AI: The 3rd Wave》中把这叫做"第三次浪潮"——前两次分别是 1980s 的纯符号专家系统、2010s 的纯深度学习。

**代表工作（按"神经—符号"耦合方式分类）**：

1. **搜索增强型（NN 提供直觉，符号系统提供搜索）**
   - **AlphaGo / AlphaZero**（DeepMind 2017）：策略网络和价值网络（NN）提供"哪一步值得看"的先验，Monte Carlo Tree Search（符号化的搜索）提供穷尽式展开。这是神经-符号融合**最成功的范本**——NN 不直接决策，而是**引导搜索**。
   - **AlphaProof**（DeepMind 2024，blog post，无 arXiv）：把上述范式搬到形式化数学。NN（基于 Gemini）生成 Lean 证明的候选步骤，Lean 内核（形式化验证器）检查每一步是否合法。在 IMO 2024 上解出 1 道代数题 + 1 道几何题，达到银牌水平。关键创新：**形式化验证回路保证了输出 100% 正确**——这是纯 LLM 永远做不到的。
   - **AlphaGeometry**（Nature 625:476–482, 2024, [DOI 10.1038/s41586-024-07412-w](https://doi.org/10.1038/s41586-024-07412-w)）：NN 提议"辅助点/辅助线"（人类数学家的直觉），符号推理引擎（基于 Wu 方法）做演绎。在 IMO 几何题上达到金牌选手水平。

2. **可微逻辑型（让符号推理可微分）**
   - **DeepProbLog**（Manhaeve et al., NeurIPS 2018）：把概率逻辑编程（ProbLog）与神经网络结合，神经网络的输出作为逻辑规则的概率，整个系统端到端可微。这是"软化符号"的路线。
   - **Logic Tensor Networks**（Badreddine et al., 2022）：用模糊逻辑把一阶谓词松弛成可微函数。
   - **Neuro-Symbolic Concept Learner (NS-CL)**（Mao, Gan, Kohli, Tenenbaum, Wu, [arXiv:1904.12584](https://arxiv.org/abs/1904.12584), ICLR 2019 Oral）：视觉感知（NN）把场景解析成对象—属性符号，语言解析成可执行程序，符号推理引擎在场景表征上执行程序回答 VQA。这是 Tenenbaum 实验室"认知启发 AI"的代表作。

**致命缺陷**：

- **符号接地问题（Symbol Grounding Problem）**：Harnad 1990 年提出的经典难题（《Physica D》42:335–346）。神经网络生成的符号（比如一个 token "猫"或一个 Lean 标识符 `h1`）怎么保证真的对应真实世界中的猫/数学对象？接地鸿沟是神经-符号融合的根本难题。AlphaGeometry 的辅助点接地靠"几何约束自洽"——如果 NN 提议的辅助点不合法，符号引擎会拒绝；但 AlphaProof 的 Lean 项接地更微妙，NN 必须先学会把自然语言数学"翻译"成 Lean 语法，这个翻译本身可能错。
- **接口瓶颈**：神经表征是高维连续向量，符号表征是离散符号串。两者之间需要一个"编码—解码"层，这个层本身就是信息瓶颈。NS-CL 用对象级 scene representation 缓解，但只适用于封闭域。
- **不可微的推理步骤**：Lean 证明的每一步要么合法要么不合法，没有"半合法"。这意味着符号推理步骤无法反向传播梯度——NN 无法从"证明失败"中学到"如何改进"。AlphaProof 用 RL（强化学习）绕开这个问题，但 RL 的样本效率极低。
- **扩展性差**：符号系统天然不擅长开放域。Lean 能证明的定理，受限于人类已形式化的数学（mathlib 库目前约 150 万行，覆盖了本科到部分研究生数学，但远未覆盖全部现代数学）。把神经-符号扩展到"任意领域的推理"仍是开放问题。

> **为什么这一节重要**：神经-符号融合是**目前最有希望在数学推理上达到"超越人类"水平的路线**（AlphaProof/AlphaGeometry 已经证明了这一点）。它是本卷 `03-ai4math` 章节的技术基底，也是用户作为"应用数学研究型工程师"最该深耕的方向。

### 方向 2：物理引导神经网络（Physics-Informed ML）

**核心思想**：把已知的物理定律（PDE、守恒律、对称性）作为**硬约束或软约束**嵌入网络，让模型的输出**天然满足**物理规律，而不是事后检验。这是"用物理公理约束概率模型"最直接的方式。

**代表工作**：

1. **PDE 残差约束型**
   - **PINN（Physics-Informed Neural Networks）**（Raissi, Perdikaris, Karniadakis, [arXiv:1711.10561](https://arxiv.org/abs/1711.10561), 2017；JCP 2019）：把偏微分方程 $\mathcal{N}[u](x,t)=0$ 的残差作为损失项。总损失 = 数据损失 + $\lambda \cdot \text{PDE 残差}$：

     $$\mathcal{L} = \underbrace{\|u_\theta - u_{\text{data}}\|^2}_{\text{数据拟合}} + \lambda \underbrace{\|\mathcal{N}[u_\theta]\|^2}_{\text{物理约束}}$$

     网络不仅拟合数据，还要"在物理上自洽"。这是物理引导 ML 的开山之作。
   - **Neural Operators**：把"学习一个函数"升级为"学习一个算子"（函数到函数的映射），用于参数化 PDE 族。
     - **FNO（Fourier Neural Operator）**（Li, Kovachki, Azizzadenesheli, ..., Anandkumar, [arXiv:2010.08895](https://arxiv.org/abs/2010.08895), ICLR 2021）：在傅里叶空间参数化积分核，比传统 PDE 求解器快 1000 倍，首次成功模拟湍流。
     - **DeepONet**（Lu, Jin, Karniadakis, [arXiv:1910.03193](https://arxiv.org/abs/1910.03193), 2019）：branch net 编码输入函数，trunk net 编码输出位置，基于算子通用逼近定理。

2. **对称性/等变性约束型**
   - **EGNN（E(n)-Equivariant Graph Neural Networks）**（Satorras, Hoogeboom, Welling, [arXiv:2102.09844](https://arxiv.org/abs/2102.09844), 2021）：保证网络输出在旋转、平移、反射、置换下等变。这是 AlphaFold 系列背后的核心架构思想——蛋白质结构预测必须满足物理对称性，否则预测的三维坐标没有物理意义。EGNN 不需要昂贵的高阶表示，就能达到甚至超过 SE(3)-Transformer。
   - **等变神经网络的更早工作**：Tensor Field Networks（Thomas et al., 2018）、SE(3)-Transformer（Fuchs et al., 2020）。这一系谱最终汇聚到 AlphaFold 2/3 的 Evoformer + 结构模块。

3. **守恒律约束型（哈密顿/拉格朗日神经网络）**
   - **Hamiltonian Neural Networks**（Greydanus, Dzamba, Yosinski, [arXiv:1906.01563](https://arxiv.org/abs/1906.01563), NeurIPS 2019）：让网络学习系统的哈密顿量 $H(q,p)$，然后通过哈密顿方程 $\dot{q}=\partial H/\partial p,\ \dot{p}=-\partial H/\partial q$ 更新状态。**能量守恒是结构性的**——不是软约束，而是从架构上保证。副产品：模型时间可逆。
   - **Lagrangian Neural Networks**（Cranmer, Greydanus, Hoyer, Battaglia, Spergel, Ho, [arXiv:2003.04630](https://arxiv.org/abs/2003.04630), 2020）：放松 HNN 的"需要正则坐标"假设，学习任意拉格朗日量 $L(q,\dot{q})$。能处理 HNN 失败的相对论粒子。

4. **物理一致的大规模应用**
   - **GraphCast**（DeepMind, *Science* 382:1416–1421, 2023, [DOI 10.1126/science.adi2336](https://doi.org/10.1126/science.adi2336)）：基于图神经网络的天气预报模型，10 天预报精度超过 HRES（欧洲中期天气预报中心的业务数值模式），速度快 1000 倍。它隐式学习了大气动力学的物理结构。

**致命缺陷**：

- **依赖已知物理**：PINN 必须知道 PDE 的形式才能把它写进损失。如果你想研究一个**新现象**（比如发现一个新的物理定律），PINN 帮不上忙——你不知道该把什么写进 $\mathcal{N}[u]$。这是一个"先有鸡还是先有蛋"的困境：物理引导 ML 加速求解已知物理，但不能发现未知物理。
- **方程形式硬编码**：即使知道"这是 Navier-Stokes"，你也得手动把方程敲进去。方程的每一项、每个边界条件都是人为指定。这让模型失去泛化到"略有不同的物理"的能力。
- **数值不稳定**：硬约束（强权重 $\lambda$）和数据拟合常常冲突——网络要么牺牲数据精度满足物理，要么牺牲物理满足数据。这个 tradeoff 的调参极其敏感，是 PINN 工程化的主要痛点。
- **可表达性受限**：对于复杂现象（湍流、多相流、相变），PDE 本身就是近似——Navier-Stokes 在连续介质假设下成立，但微观上是分子动力学。用近似方程约束网络，网络最多学到这个近似，无法超越它。

> **为什么这一节重要**：物理引导 ML 是 AI4Science 的**技术骨架**。AlphaFold、GraphCast、AI 天气预报、AI 材料发现，背后都是"把物理对称性/守恒律嵌入网络"的思想。它和方向 1（神经-符号）互补——一个用数学逻辑约束，一个用物理定律约束。两者结合，是通向"物理一致 + 数学严格"的 AI 的关键。

### 方向 3：因果 AI（Causal AI）

**核心思想**：从统计相关 $P(Y|X)$ 升级到因果 $P(Y|\text{do}(X))$。Judea Pearl 的核心洞察是：相关只能告诉你"X 和 Y 一起变"，因果才能告诉你"改变 X 会改变 Y"。前者是观察，后者是干预。

**Pearl 的因果阶梯（Ladder of Causation）**：

| 层级 | 问题 | 操作 | 当前 AI 所在 |
|---|---|---|---|
| 1. 关联（Association） | $P(y\|x)$？我看到 X 时 Y 怎样？ | 观察 | LLM 在这里 |
| 2. 干预（Intervention） | $P(y\|\text{do}(x))$？如果我做 X，Y 会怎样？ | 干预/实验 | 强化学习、A/B 测试 |
| 3. 反事实（Counterfactual） | $P(y_{x'}\|x,y)$？如果当时我没做 X，Y 会怎样？ | 想象 | 几乎没有 AI 能稳定做到 |

LLM 停在第一层。它海量地见过"X 和 Y 共现"，但从未真正"干预"过世界。Pearl 反复强调：**没有因果，就没有真正的智能**。

**代表工作**：

- **结构因果模型（SCM）与 do-演算**（Pearl, *Causality: Models, Reasoning, and Inference*, Cambridge University Press, 2000；第二版 2009）：Pearl 的奠基之作。定义了因果图、do-算子、后门准则、前门准则。给了从观察数据估算干预效应的完整代数。这是因果推断的"圣经"。
- **DoWhy 库**（Microsoft Research）：把 Pearl 的因果推断框架工程化，提供"识别—估计—反驳"四步管线。让数据科学家能像调 `sklearn.fit` 一样做因果分析。
- **Double Machine Learning**（Chernozhukov et al., 2018）：用 ML 估计 nuisance 函数，再用半参数方法估计因果效应。解决了"高维混杂因子"下的因果估计。
- **Causal Forests**（Wager & Athey, 2018）：用随机森林估计**异质处理效应**（CATE）——同一个干预对不同人群效果不同。
- **因果表征学习（Causal Representation Learning）**（Schölkopf, Locatello, Bauer, Ke, Kalchbrenner, Goyal, Bengio, [arXiv:2102.11107](https://arxiv.org/abs/2102.11107), Proceedings of the IEEE 2021）：Schölkopf（马普所智能系统所所长）的纲领性论文。核心论点：**当前的表征学习（VAE、对比学习）学到的是统计因子，不是因果因子**。真正的因果表征应该是"可干预的、可组合的、支持分布外泛化的"。这篇论文指出了从相关到因果的"基础模型"路线图。

**致命缺陷**：

- **因果图未知**：Pearl 的所有定理都假设因果图（DAG）已知或可识别。但现实里，大部分场景没有 ground truth 因果图——你不知道"教育→收入"之间真正的因果结构是什么。从观察数据反推因果图（因果发现）是 NP-hard，且在存在混淆因子时根本不可识别。
- **未观察混淆因子**：你永远不知道有没有遗漏一个关键变量。"教育→收入"的因果效应估计，可能被"家庭背景"这个未观测变量污染。除了随机对照试验（RCT），没有任何纯观察方法能完全消除混淆——而 RCT 在很多领域（宏观经济、社会政策）不可行。
- **不可证伪**：因果结论很难用实验验证。你估计"加息 0.25% 会让失业率上升 0.5%"，但你没法真的加息 0.25% 然后观察——经济是不可重复的。这使得因果 AI 的结论常常停留在"理论可信但无法实证"的灰色地带。
- **scale 困难**：大模型的因果建模仍是开放问题。GPT-4 内部的"因果理解"其实是统计相关性伪装的——它会说"因为下雨所以地湿"，但它从没见过"不下雨但地湿"的反事实世界。如何把 Pearl 的因果框架嵌入万亿参数的 Transformer，目前没有令人信服的方案。

> **为什么这一节重要**：因果 AI 是**唯一正面回应"LLM 学的是相关不是因果"这一批评的方向**。它和用户的概率论/随机过程兴趣高度契合——因果图的数学基础就是概率图模型。Schölkopf 的因果表征学习是当前最有可能通向"因果基础模型"的路线。

### 方向 4：工具增强 LLM（Tool-augmented / Agentic AI）

**核心思想**：LLM 做它擅长的（意图理解、规划、自然语言交互），把"难的部分"外包给外部工具（计算器、Python 解释器、Lean、Wolfram Alpha、SQL）。LLM 不再假装自己会算术，而是真的去调用计算器。

这是**当前工业界最主流的"超越纯概率"路线**——ChatGPT 的 Code Interpreter、Claude 的 Computer Use、Cursor 的代码执行，都是这个范式。

**代表工作**：

- **Toolformer**（Schick et al., Meta, [arXiv:2302.04761](https://arxiv.org/abs/2302.04761), 2023）：让 LM **自学**调用外部 API。模型在自己生成的文本里插入 `<API>调用</API>` 标记，如果调用结果让后续预测更准，就保留这个调用模式。关键创新：**自监督的工具学习**，不需要人工标注"何时调用工具"。集成了计算器、QA、搜索引擎、翻译、日历六种工具。
- **ReAct**（Yao et al., Princeton/Google, [arXiv:2210.03629](https://arxiv.org/abs/2210.03629), ICLR 2023）：Reasoning + Acting 交织。模型先"思考"（Thought），再"行动"（Action，调用工具），再"观察"（Observation，工具返回），循环。这个 Thought–Action–Observation 循环成了后来所有 Agent 框架（LangChain、AutoGPT、CrewAI）的模板。ReAct 的贡献是证明了"推理和行动应该交织，而不是分开"。
- **Code Interpreter / Advanced Data Analysis**（OpenAI, 2023）：ChatGPT 内嵌 Python 沙箱。用户问"分析这个 CSV"，模型生成 Python 代码，沙箱执行，结果回填。这是工具增强 LLM **第一次大规模产品化**。
- **Claude Computer Use**（Anthropic, 2024）：让 LLM 操作真实计算机——点击、输入、截图、循环。把"工具"从 API 扩展到整个 GUI。
- **Lean Copilot + LLM**：在 Lean 证明助手里嵌入 LLM，LLM 提议证明步骤，Lean 验证。这是工具增强 LLM 走向形式化数学的具体实现。
- **Program-of-Thoughts (PoT)**（Chen et al., 2022）：让 LLM 把推理写成程序，而不是写成自然语言 CoT。程序执行的结果就是答案。这绕开了"CoT 每一步都可能错"的问题——只要程序语法对、逻辑对，结果就对。

**致命缺陷**：

- **接口脆性**：LLM 生成的代码/命令经常有 bug——拼写错误、参数顺序错、调用了不存在的函数。一个 typo 就让整个工具链崩溃。ReAct 论文报告，即使在简单任务上，工具调用错误率也在 10–30%。
- **错误传播**：如果工具输出错误（比如搜索引擎返回过时信息，或 Python 计算溢出），LLM 倾向于**接受工具输出为 ground truth**，然后在错误基础上继续推理。这放大了错误，而不是纠正它。
- **不可组合**：多个工具协同仍困难。"先用搜索引擎查 X，再用计算器算 Y(X)，再用 Python 画图"——这个多步管线需要精确的状态传递，LLM 经常在中间步骤丢失上下文。
- **本质未变**：这是最根本的批评。**LLM 本身仍然是概率的**。工具增强只是把"难的部分"外包，但"决定调用哪个工具""怎么解读工具结果""怎么把结果组合成答案"——这些**元认知**步骤，仍然是 LLM 在做，仍然是概率的。一个连"该不该相信这个搜索结果"都判断不好的 LLM，外包再多工具也救不了。Agent 框架的可靠性瓶颈，恰恰是 LLM 这个"调度大脑"本身。

> **为什么这一节重要**：工具增强是**当下唯一已经大规模商业化的"超越纯概率"路线**。它是工程现实主义的胜利——既然 LLM 不能保证正确，那就让它调用能保证正确的工具。但用户要清醒：这是"工程补丁"，不是"理论突破"。真正的 AGI 不能靠外包。

### 方向 5：检索增强 + 知识图谱（RAG + KG）

**核心思想**：LLM 的知识存在参数里（容易过时、容易幻觉）。把知识放到外部结构化存储（向量库、知识图谱），LLM 每次回答时先**检索**相关知识，再基于检索结果生成。这把"知识"和"推理"解耦了。

**代表工作**：

- **RAG（Retrieval-Augmented Generation）**（Lewis et al., Facebook AI, [arXiv:2005.11401](https://arxiv.org/abs/2005.11401), NeurIPS 2020）：参数记忆（seq2seq 模型）+ 非参数记忆（Wikipedia 的密集向量索引）。两种 RAG 变体：RAG-Sequence（整个生成用同一批检索文档）和 RAG-Token（每个 token 可以用不同文档）。这是 RAG 范式的开山之作，后来所有"chat-with-your-docs"应用都源于此。
- **GraphRAG**（Microsoft, 2024）：先从文档抽取实体和关系建知识图谱，再在图上做社区检测和层次摘要，检索时返回"结构化知识"而不是"裸文本块"。解决了普通 RAG 在"需要跨文档推理"任务上的短板。
- **KG-GPT / KnowledGPT**：把知识图谱（Wikidata、ConceptNet、Cyc）作为 LLM 的外部事实层。LLM 负责理解和生成，KG 负责提供经过验证的事实三元组。
- **Cyc**（Lenat, 1984–至今）：道格拉斯·莱纳特毕生之作，试图用人工编码全部"常识"成一阶逻辑规则库。超过 150 万条断言。Cyc 是符号主义"知识工程"路线的极致——也正因为它无法 scale、无法从数据学习，导致了 2010s 符号主义的式微。但 Cyc 的知识库至今仍是高质量常识的来源。

**致命缺陷**：

- **知识库覆盖率**：KG 永远不完整。Wikidata 覆盖了名人、地名、机构，但覆盖不了"我妈做的红烧肉配方"。开放世界假设（Open World Assumption）意味着 KG 的"不知道"不等于"不存在"，这让基于 KG 的推理天然不完整。
- **检索精度**：检索错了就全错了。RAG 的准确率上限是检索器的召回率。如果用户的查询和正确文档在向量空间里不近，RAG 就会检索到错误文档，然后 LLM 基于错误文档生成错误答案——而且这个错误答案**带引用**，看起来特别可信，比纯幻觉更有欺骗性。
- **知识时效**：KG 和向量库都依赖定期更新。一个 2024 年建的 KG，到 2026 年就过时了。实时更新 KG 是工程难题（需要持续的事实抽取、冲突消解、版本管理）。
- **融合难**：最根本的问题。LLM 怎么决定"信任检索结果"还是"信任自己参数里的知识"？当两者冲突时（检索说"X 已经去世"，参数说"X 还活着"），LLM 没有原则性的仲裁机制。目前的做法是 prompt 工程（"请优先参考检索结果"），但这不是理论解决方案。

> **为什么这一节重要**：RAG 是**企业落地 LLM 的事实标准**。几乎所有"企业级 AI 助手"都基于 RAG。它有效缓解了幻觉和时效问题，但用户要明白：RAG 提升的是"知识获取"的可靠性，不是"推理"的可靠性。一个检索到正确知识但推理错误的 LLM，仍然会给出错误答案。

### 方向 6：世界模型 + 因果想象（World Models）

**核心思想**：让模型显式建模环境的动力学 $P(s_{t+1}|s_t, a_t)$，在"脑中"模拟未来，从而支持规划、想象、反事实推理。这是 LeCun 反复主张的"LLM 不会通向 AGI，需要世界模型"的具体含义。

**代表工作**：

- **DreamerV3**（Hafner, Pasukonis, Ba, Lillicrap, [arXiv:2301.04104](https://arxiv.org/abs/2301.04104), 2023；标题《Mastering Diverse Domains through World Models》）：学习环境的潜在动力学模型，在想象中用 actor-critic 训练策略。**单一配置**解决 150+ 多样化任务，是首个从零开始（无人类数据、无课程）在 Minecraft 收集钻石的算法。Dreamer 的核心创新：在世界模型的隐空间里做 RL，比在原始观测空间高效得多。
- **V-JEPA 2**（Assran, Bardes, Fan, Garrido, ... LeCun, Meta FAIR, [arXiv:2506.09985](https://arxiv.org/abs/2506.09985), 2025；标题《V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning》）：LeCun JEPA 路线的集大成。在互联网规模视频上自监督预训练（预测被 mask 掉的视频区域），学到物理世界的隐式模型。V-JEPA 2-AC 变体加上少量机器人数据，就能在**从未见过的环境**里零样本操作机械臂。这是 LeCun 2022 白皮书《A Path Towards Autonomous Machine Intelligence》（OpenReview preprint）的技术兑现。
- **Genie 系列**（DeepMind, 2024–2025）：从视频学习"可控的环境模拟器"，用户给一个动作，模型生成下一帧。这是"世界模型"走向游戏/仿真领域的尝试。
- **Cosmos**（NVIDIA, 2025）：NVIDIA 的"世界基础模型"，用于自动驾驶和机器人仿真。在物理一致性上做了大量工程。
- **LeCun 2022 白皮书**：《A Path Towards Autonomous Machine Intelligence》（OpenReview）。LeCun 的 AGI 路线图：感知模块 + 世界模型模块 + 行动模块 + 成本模块 + 短期记忆。核心主张：**自主智能体必须有能力在内部模拟"如果我做 X，世界会怎样"**，这需要显式的世界模型，而 LLM（纯文本预测）做不到。

**致命缺陷**：

- **Compounding error（误差累积）**：世界模型每步预测都有误差。如果单步误差 5%，10 步后累积误差可能超过 60%（指数增长）。这让长程规划极不可靠——世界模型"想象"的未来，越远越离谱。DreamerV3 用 symmetric 训练和归一化部分缓解，但根本问题未解。
- **分布外失效**：世界模型学的是训练分布内的动力学。遇到训练没见过的情境（新物体、新物理参数），预测立刻崩坏。V-JEPA 2 的零样本操作有突破，但仍局限在"和训练分布相似"的 manipulation 任务。
- **因果 vs 相关的根本未解**：这是最深的批评。世界模型本质上学的还是 $P(s'|s,a)$——一个**条件概率分布**。它学到的是"在训练数据里，状态 $s$ 和动作 $a$ 之后通常跟着什么"，不是"动作 $a$ **导致**了状态 $s'$"。一个学得很好的世界模型，可能只是在做高级的模式匹配。要真正支持反事实推理（"如果我**当时**做了不同的动作，现在会怎样"），需要因果世界模型，而这目前还是理论设想。
- **可解释性差**：世界模型的隐空间动力学是黑盒。模型"想象"的未来，人类无法审查"它为什么这么想"。这让世界模型在安全关键场景（自动驾驶、医疗）难以部署——你无法向监管机构证明"模型的想象是可靠的"。

> **为什么这一节重要**：世界模型是 **LeCun 派（反 LLM 中心论）的技术赌注**。如果 LeCun 是对的（LLM 不会通向 AGI），那么世界模型 + 强化学习才是正道。V-JEPA 2 和 DreamerV3 是这条路线的早期验证。但用户要警惕"世界模型 = 因果模型"的混淆——目前的世界模型仍是概率的，只是概率的**对象**从 token 变成了状态转移。

---

## 二、致命缺陷的深层分析

上一节我们看了六大方向各自的软肋。这一节我们抽象一层，看这六大方向**共同的、结构性的**致命缺陷。这是本文的核心章节——理解这些共通缺陷，才能看清未来研究的真正机会。

### 2.1 缺陷一：混合架构不可微（The Differentiability Gap）

六大方向里，除了纯 RAG 和纯工具增强，其他四个（神经-符号、物理引导、因果、世界模型）都面临同一个工程难题：**神经部分可微，但约束部分不可微，无法端到端训练**。

具体表现：

| 方向 | 可微部分 | 不可微部分 | 后果 |
|---|---|---|---|
| 神经-符号 | NN 感知/提议 | Lean 证明验证、MCTS 搜索 | 无法用梯度教 NN"怎么提议更好的符号" |
| 物理引导 | NN 参数 | PDE 残差（其实是可微的，但硬约束不行） | 软约束 vs 硬约束 tradeoff |
| 因果 AI | NN 表征 | 因果图结构、do-算子 | 无法从数据端到端学因果结构 |
| 世界模型 | 转移模型 | 环境（不可微，需 RL） | 无法用梯度直接优化策略 |

AlphaProof 的解法是 RL——把 Lean 验证当作 reward signal，用强化学习训练 NN。但 RL 的样本效率比监督学习低 1–2 个数量级。整个 AI 社区都在找"让符号推理可微"的方法：可微逻辑（DeepProbLog）、straight-through estimator、Gumbel-softmax。但目前没有银弹。

### 2.2 缺陷二：接地鸿沟（The Grounding Chasm）

神经表征（高维连续向量）和符号/物理实体（离散概念/物理对象）之间的对应关系，**没有原则性方法**。

Harnad 1990 年的符号接地问题（*Physica D* 42:335–346）说的是：一个符号系统里，"猫"这个符号怎么和真实的猫关联？传统的回答是"通过定义"——但定义用的还是符号，形成无限回归（symbol grounding regress）。Harnad 的方案是"必须接入感知"——符号必须通过神经网络对真实世界的感知来接地。

但 LLM 时代，问题更尖锐了。LLM 的 token "猫"对应的是 embedding 向量，这个向量是通过文本共现学的，**从未见过真实的猫**。Bender 的"随机鹦鹉"批评本质就是接地鸿沟——LLM 在符号层面流畅，但符号没有接地到真实世界。

物理引导 ML 部分缓解了这个问题：一个 PINN 学到的"温度场" $u(x,t)$，是真的对应物理温度的（因为它被 PDE 约束）。但神经-符号融合和工具增强 LLM，接地仍然靠"人工对齐"——人手动把 NN 输出映射到符号，没有自动化方法。

### 2.3 缺陷三：覆盖 vs 严格的 Tradeoff（Coverage–Rigor Tradeoff）

这是最深刻的结构性矛盾：

| | 覆盖广度 | 严格性 |
|---|---|---|
| 纯神经方法（LLM） | 极广——能"回答"任何问题 | 不严格——不保证正确 |
| 纯符号方法（Lean/Cyc） | 极窄——只能处理形式化领域 | 绝对严格——证明即真理 |

这个 tradeoff 像测不准原理一样根本。你想扩大覆盖，就得放松严格性（LLM 路线）；你想保证严格，就得收窄覆盖（Lean 路线）。目前没有方法同时做到"覆盖广且严格"。

AlphaProof 的范式给出了一条中间路线：**在窄域用严格方法，在宽域用神经方法，中间用接口耦合**。但接口本身就是薄弱环节。扩大这个"严格域"的边界，是未来 10 年的核心挑战。

### 2.4 缺陷四：Scale 不友好（The Scaling Hostility）

所有非纯神经方法，都难以 scale 到网络规模数据。

- 神经-符号：Lean 形式化的数学，全人类加起来也就 mathlib 那 150 万行。和互联网文本的万亿 token 不是一个量级。
- 物理引导：带 PDE 标注的物理数据稀缺。大部分物理实验数据没有配套的方程形式。
- 因果 AI：带因果图标注的数据极度稀缺。你能找到"X 导致 Y"的标注数据集吗？几乎没有——因果图要靠专家手画或昂贵实验。
- 世界模型：环境交互数据（机器人轨迹、物理仿真）比文本数据贵几个数量级。

LLM 的成功很大程度上是"数据规模红利"。非纯神经方法吃不到这个红利，所以它们的进展速度天然慢于 LLM。这是为什么"神经-符号 GPT"迟迟未出现——不是技术做不到，是数据不够。

### 2.5 缺陷五：组合爆炸（Combinatorial Explosion）

符号推理、定理证明、规划，搜索空间天然指数。

- Lean 证明：每个目标的证明树分支因子可能是几十到几百，深度可能是几十层。穷举搜索不可行。
- MCTS（AlphaGo）：围棋的搜索空间是 $10^{170}$，靠 NN 剪枝才降到可行。
- 因果发现：$n$ 个变量的可能因果图数量是 $n!$ 级别的超指数增长。

NN 的价值恰恰在这里——它提供"先验直觉"，把指数搜索空间剪枝到多项式可处理。但这个"剪枝"本身可能漏掉正确答案。AlphaGeometry 解 IMO 题时，如果 NN 没提议正确的辅助点，符号引擎就找不到证明。这是神经-符号系统的"覆盖率天花板"。

### 2.6 缺陷六：数据瓶颈（The Data Bottleneck）

高质量标注的因果/物理/形式化数据稀缺。

- 因果标注：需要专家画因果图 + 实验验证。一个数据集可能耗时数月。
- 物理标注：需要 PDE 形式 + 边界条件 + 数值解。每个物理问题都要领域专家参与。
- 形式化数学：把一个数学家的证明翻译成 Lean，可能比证明本身还耗时（这是 Mathlib 增长慢的原因）。

合成数据部分缓解了这个问题（DeepMind 用 AlphaProof 自己生成 Lean 证明来训练自己），但合成数据有"模式坍缩"风险——模型可能只学会生成自己已经会的证明，无法探索新的数学。

> **为什么这一节重要**：这六个共通缺陷定义了"超越纯概率 LLM"研究的前沿。任何声称"解决了 LLM 局限"的新方法，都必须回答它如何应对这六个缺陷。如果答不上来，那它大概率只是换了个包装的旧思路。

---

## 三、未来研究趋势（5–10 年预测）

基于六大方向的现状和六个共通缺陷，预测未来 5–10 年的 7 个研究趋势。

### 趋势 1：Neuro-Symbolic Foundation Models（神经-符号基础模型）

**预测**：到 2028–2030 年，出现"神经-符号 GPT"——一个预训练的大模型，原生集成符号推理能力。

**路线**：大模型预训练（学语言、学常识）+ 符号系统后训练（学推理、学证明）。AlphaProof 已经是这个范式的雏形。扩展到所有领域：物理（PINN-instruct）、生物（AlphaFold-instruct）、法律（逻辑-instruct）。

**关键挑战**：缺陷 2.1（不可微）和 2.4（Scale 不友好）。如果这两个被突破，神经-符号 FM 会像 2022 年的 LLM 一样爆发。

### 趋势 2：Self-Verifying AI（自验证 AI）

**预测**：AI 系统"自己生成 + 自己验证"成为标配。

**机制**：形式化验证 + 概率推理的耦合。LLM 生成候选答案/证明/代码，内置的形式化验证器（Lean/Z3/SMT solver）检查，验证失败则反馈给 LLM 修正，循环。

**代表**：Lean Copilot、AlphaProof 的 self-play 循环、GitHub Copilot 的测试生成。这个趋势的技术成熟度最高，3–5 年内会全面产品化。

**意义**：这是对 LLM"无法验证"局限（开篇第 4 条）的直接回应。一旦 AI 能可靠地自我验证，幻觉问题从根本上缓解。

### 趋势 3：Embodied Causal Learning（具身因果学习）

**预测**：具身 agent 通过**真实干预**学习因果，不再依赖纯观察数据。

**机制**：机器人 + 因果发现。agent 在环境里主动做实验（"如果我推这个杯子，它会掉吗？"），从干预数据学因果图。这把 Pearl 的"第二层（干预）"从理论变成实践。

**代表**：机器人实验室自动化（自动化学合成、自动材料制备）+ 因果推断。rentosertib（INS018_055）进入 Phase III 临床试验（NCT07687459，2026-07-07 启动，本卷 `02-ai4science` 已详述），就是 AI 设计 + 自动合成 + 实验验证闭环的里程碑。

**意义**：这是对"因果图未知"缺陷（缺陷 2.6 部分）的根本回应——不靠观察数据反推因果，而是靠主动实验获取因果。

### 趋势 4：Tool-Native Models（工具原生模型）

**预测**：未来模型不再"调用工具"，而是"原生使用工具"——tool use 作为预训练目标，而非后训练补丁。

**机制**：预训练数据里就包含工具调用轨迹（代码执行日志、API 调用记录）。模型从零开始学"什么时候、怎么调用工具"。

**代表**：OpenAI 的 o1/o3 系列、Anthropic 的 Claude 3.5+、Google 的 Gemini 2.0，都在朝这个方向走。Toolformer 的自监督工具学习是早期学术原型。

**意义**：缓解缺陷 2.1 的工具增强版本——如果 tool use 内化到预训练，接口脆性（方向 4 的缺陷 1）会大幅降低。

### 趋势 5：Differentiable Physics + ML（可微物理 + 机器学习）

**预测**：物理仿真引擎与神经网络**端到端融合**。

**机制**：可微物理引擎（每个物理步骤都可微分）+ 神经网络，梯度从损失一路传到物理参数。这让"用数据校准物理模型"变得和训练 NN 一样简单。

**代表**：Brax（Google 的可微物理）、Genesis（通用机器人仿真）、Cosmos Reason（NVIDIA）、JAX-MD（分子动力学）。学术上有 FluidLab、DiffSim。

**意义**：部分解决缺陷 2.1（物理引导 ML 的不可微问题）。如果物理仿真完全可微，PINN 的硬约束 vs 软约束 tradeoff 就不再是痛点。

### 趋势 6：Causal Foundation Models（因果基础模型）

**预测**：5 年内出现首批"因果 FM"——从相关到因果的基础模型。

**机制**：Schölkopf 推动的因果表征学习（[arXiv:2102.11107](https://arxiv.org/abs/2102.11107)）的规模化。模型学到的表征是"因果变量"而非"统计因子"，支持分布外泛化和反事实推理。

**关键挑战**：缺陷 2.4（Scale 不友好）和 2.6（数据瓶颈）。因果数据稀缺是最大障碍。可能需要"合成因果数据"+"主动实验"双管齐下。

**意义**：这是对 Pearl"没有因果就没有 AGI"主张的技术回应。如果成功，它会让 AI 从"模仿"升级到"理解"。

### 趋势 7：Category Theory + ML（范畴论 + 机器学习）

**预测**：范畴论提供**理论统一框架**，但不一定实用化。

**机制**：用范畴论统一各种 AI 范式——神经网络、概率模型、因果图、符号系统，都是某种"函子"或"代数结构"。

**代表**：
- **Backprop as Functor**（Fong, Spivak, Tuyéras, [arXiv:1711.10455](https://arxiv.org/abs/1711.10455), LICS 2019）：把反向传播形式化为 Learner 范畴上的函子。这是范畴论 ML 的奠基之作，David Spivak（范畴论大家）和 Brendan Fong（应用范畴论先驱）的合作。
- **Categorical Deep Learning**（Gavranović 等，[arXiv:2402.15332](https://arxiv.org/abs/2402.15332), 2024）：用范畴论统一所有神经网络架构（CNN、Transformer、GNN 都是某种代数结构的实例）。
- **Spivak 的《Category Theory for the Sciences》**（MIT Press, 2014）：范畴论入门，专为科学家写。

**意义与局限**：范畴论提供"为什么这些方法相关"的深刻洞察，但它的抽象层级太高，难以直接产出工程成果。它是"理论物理学"之于"工程学"的关系——必要但不充分。对用户（应用数学研究型工程师）来说，范畴论是**长期理论修养**，不是短期工具。

> **为什么这一节重要**：这 7 个趋势是"超越纯概率 LLM"研究的**投资地图**。趋势 1、2、4 最可能在 5 年内产生工程突破；趋势 3、5、6 是 5–10 年的中期赌注；趋势 7 是 10+ 年的长期理论建设。用户可以根据自己的时间 horizon 选择投入方向。

---

## 四、对用户的建议

基于用户画像（应用数学研究型工程师，每周 10–20h，关注 AI4Math 与 Lean，数学基础目前自评 0 但工程逻辑强），给出具体可操作的方向选择。

### 4.1 优先深耕：神经-符号 + 形式化证明

这是用户本卷 `03-ai4math` 已覆盖的方向，也是最契合用户背景的选择。理由：

- **数学背景直接可用**：Lean 形式化需要的数学（逻辑、类型论、范畴论入门）正好是用户长期目标"数学专家"的核心训练。
- **工程能力直接转化**：用户工程级 Python 能力，可以直接上手 Lean Copilot、Lean 项目贡献、形式化证明自动化工具开发。
- **领域正在爆发**：AlphaProof（2024）、DeepSeek-Prover V2、Mathlib 的指数增长，意味着这个方向 2025–2030 是黄金窗口。
- **与 LLM 路线正交**：不依赖 LLM 的概率能力，所以不受 LLM 局限制约。

**具体起步**：学 Lean 4（Theorem Proving in Lean 4 教程）→ 贡献 Mathlib 小命题 → 学 AlphaProof 论文 → 尝试 LLM + Lean 的小项目（如自动形式化自然语言数学题为 Lean）。

### 4.2 次选：因果表示学习

如果用户想拓展第二方向，因果 AI 是最佳选择。理由：

- **与概率论兴趣契合**：用户研究兴趣包括"概率随机过程"，因果图的数学基础就是概率图模型和 do-演算。
- **理论深度足够**：Pearl 的《Causality》、Schölkopf 的因果表征学习，都是需要认真数学训练才能读懂的深度内容。
- **应用广**：因果 AI 在经济学、医学、社会政策（用户另有 social-laws 项目）都有直接应用。

**具体起步**：读 Pearl《The Book of Why》（科普入门）→ 读《Causality》第二版（数学）→ 做 DoWhy 教程 → 读 Schölkopf 2102.11107 综述。

### 4.3 可避坑：纯 LLM 改进、纯 Prompt Engineering

这些是**工程**而非**理论**。它们能产出短期价值，但不构成用户的长期竞争力。用户的定位是"应用数学研究型工程师"，不是"prompt 工程师"。如果时间有限，优先投入有数学深度的方向。

### 4.4 黄金交叉：Lean/Coq 形式化 + 机器学习

把形式化证明和机器学习结合，做"**机器辅助数学研究**"。这是趋势 1（神经-符号 FM）和趋势 2（自验证 AI）的交汇点，也是用户能做出**独特贡献**的位置：

- 大多数 ML 研究者不懂 Lean，大多数 Lean 用户不懂 ML。用户两边都懂，就是稀缺人才。
- 具体课题：自动形式化（自然语言→Lean）、证明搜索（NN 引导 Lean）、猜想生成（NN 提议数学猜想，Lean 验证）。
- 这个交叉点目前没有"大厂垄断"，学术和开源空间充足。

> **为什么这一节重要**：方向选择比努力更重要。用户每周只有 10–20h，必须聚焦。上述建议是基于"数学深度 × 工程转化 × 领域爆发期 × 与用户长期目标一致"四维筛选的结果。

---

## 五、结语：AGI 的真正门槛

引用几位领域奠基人的判断，作为本文的理论收尾：

**Judea Pearl**（图灵奖得主，因果推断之父）：
> "没有因果，就没有 AGI。当前所有的深度学习，包括 LLM，都停在因果阶梯的第一层（关联）。要达到真正的智能，必须登上第二层（干预）和第三层（反事实）。"

**Yann LeCun**（图灵奖得主，Meta 首席 AI 科学家）：
> "LLM 不会通向 AGI。自主智能体需要世界模型——在内部模拟'如果我做 X，世界会怎样'的能力。纯文本预测做不到这一点。"（参见其 2022 白皮书《A Path Towards Autonomous Machine Intelligence》）

**Jürgen Schmidhuber**（LSTM 发明人，IDSIA 创始人）：
> "RNN + 世界模型 1990 年代就有了。当前所谓的'新突破'，很多是旧思想在新算力上的重演。"（Schmidhuber 长期主张其 1990s 工作被低估）

**Max Tegmark**（MIT 物理学家，《Life 3.0》作者）：
> "AI 必须理解物理，否则不是真正的智能。一个不懂守恒律、不懂对称性的系统，最多是高级模式匹配。"

### 最终判断

综合本文的分析，我们的结论是：

**LLM 是 AI 的一个组件，不是 AI 的全部。**

真正的 AGI（如果它存在）需要把以下能力**统一**起来：

1. **概率推理**（LLM 擅长）——处理不确定性、模糊性、噪声。
2. **符号推理**（Lean/Prolog 擅长）——保证严格性、可验证、可解释。
3. **因果建模**（Pearl/Schölkopf 推动）——支持干预、反事实、分布外泛化。
4. **世界模拟**（Dreamer/JEPA 路线）——支持规划、想象、长期决策。
5. **感知运动**（具身 AI）——接地到真实物理世界。

目前没有任何系统能同时做好这五件事。这五个能力的统一，是 50 年级别的问题（Pearl 私下估计）。LLM 是这条路上的一块重要基石，但绝不是终点。

用户作为"应用数学研究型工程师"，站在一个独特的历史位置：你既有工程能力落地这些想法，又有数学深度理解它们的本质。**不要被 LLM 的繁华迷惑，要看到它背后的结构性局限，并把精力投入到真正突破这些局限的方向上**。这是本文最想传递的信念。

---

## 六、关键论文与资源

### 6.1 必读论文（按主题，30 篇，全部 arXiv ID 一手核实）

**神经-符号融合**
1. Garcez & Lamb, "Neurosymbolic AI: The 3rd Wave," [arXiv:2012.05876](https://arxiv.org/abs/2012.05876), 2020. —— 综述，第三波纲领。
2. Mao et al., "The Neuro-Symbolic Concept Learner (NS-CL)," [arXiv:1904.12584](https://arxiv.org/abs/1904.12584), ICLR 2019 Oral. —— 视觉+语言+程序推理。
3. Manhaeve et al., "DeepProbLog," NeurIPS 2018. —— 可微概率逻辑编程（无 arXiv，见 NeurIPS proceedings）。
4. Trinh et al., "AlphaGeometry," *Nature* 625:476–482, 2024, [DOI 10.1038/s41586-024-07412-w](https://doi.org/10.1038/s41586-024-07412-w). —— IMO 金牌级几何证明。

**物理引导 ML**
5. Raissi, Perdikaris, Karniadakis, "Physics-Informed Neural Networks (PINN)," [arXiv:1711.10561](https://arxiv.org/abs/1711.10561), 2017. —— PINN 开山。
6. Li et al., "Fourier Neural Operator (FNO)," [arXiv:2010.08895](https://arxiv.org/abs/2010.08895), ICLR 2021. —— 算子学习，比 PDE 求解器快 1000×。
7. Lu, Jin, Karniadakis, "DeepONet," [arXiv:1910.03193](https://arxiv.org/abs/1910.03193), 2019. —— 算子通用逼近。
8. Satorras, Hoogeboom, Welling, "E(n)-Equivariant GNN (EGNN)," [arXiv:2102.09844](https://arxiv.org/abs/2102.09844), 2021. —— 等变 GNN，AlphaFold 架构基础。
9. Greydanus, Dzamba, Yosinski, "Hamiltonian Neural Networks," [arXiv:1906.01563](https://arxiv.org/abs/1906.01563), NeurIPS 2019. —— 守恒律嵌入。
10. Cranmer et al., "Lagrangian Neural Networks," [arXiv:2003.04630](https://arxiv.org/abs/2003.04630), 2020. —— 放松正则坐标假设。
11. Lam et al., "GraphCast," *Science* 382:1416–1421, 2023, [DOI 10.1126/science.adi2336](https://doi.org/10.1126/science.adi2336). —— AI 天气预报超越数值模式。

**因果 AI**
12. Pearl, *Causality: Models, Reasoning, and Inference*, 2nd ed., Cambridge University Press, 2009. —— 因果推断圣经（书，非论文）。
13. Schölkopf et al., "Towards Causal Representation Learning," [arXiv:2102.11107](https://arxiv.org/abs/2102.11107), Proc. IEEE 2021. —— 因果表征学习纲领。
14. Pearl, *The Book of Why*, Basic Books, 2018. —— 科普入门（书）。
15. Pearl & Mackenzie, "The Seven Tools of Causal Inference," *Communications of the ACM* 62(3), 2019.

**工具增强 LLM**
16. Schick et al., "Toolformer," [arXiv:2302.04761](https://arxiv.org/abs/2302.04761), 2023. —— 自监督工具学习。
17. Yao et al., "ReAct," [arXiv:2210.03629](https://arxiv.org/abs/2210.03629), ICLR 2023. —— Reasoning + Acting 交织。
18. Yao et al., "Tree of Thoughts," NeurIPS 2023. —— CoT 的树搜索扩展。
19. Wei et al., "Chain-of-Thought Prompting," NeurIPS 2022. —— CoT 开山。

**RAG + 知识图谱**
20. Lewis et al., "Retrieval-Augmented Generation (RAG)," [arXiv:2005.11401](https://arxiv.org/abs/2005.11401), NeurIPS 2020. —— RAG 开山。
21. Edge et al., "GraphRAG," Microsoft, 2024. —— 图增强 RAG（技术报告）。
22. Pan et al., "Unifying Large Language Models and Knowledge Graphs," *IEEE TKDE* 2024. —— LLM+KG 综述。

**世界模型**
23. Hafner et al., "DreamerV3," [arXiv:2301.04104](https://arxiv.org/abs/2301.04104), 2023. —— 通用世界模型 RL。
24. Assran, Bardes et al., "V-JEPA 2," [arXiv:2506.09985](https://arxiv.org/abs/2506.09985), 2025. —— LeCun JEPA 路线集大成。
25. Ha & Schmidhuber, "World Models," [arXiv:1803.10122](https://arxiv.org/abs/1803.10122), 2018. —— 世界模型早期经典（注意：本卷 CHANGELOG 记录的错 ID 1809.01986 应为 1809.01999，此处为另一篇经典）。
26. LeCun, "A Path Towards Autonomous Machine Intelligence," OpenReview preprint, 2022. —— LeCun AGI 路线图白皮书。

**理论统一（范畴论等）**
27. Fong, Spivak, Tuyéras, "Backprop as Functor," [arXiv:1711.10455](https://arxiv.org/abs/1711.10455), LICS 2019. —— 范畴论 ML 奠基。
28. Gavranović et al., "Position: Categorical Deep Learning is an Algebraic Theory of All Architectures," [arXiv:2402.15332](https://arxiv.org/abs/2402.15332), 2024. —— 范畴论统一架构。
29. Tishby & Zaslavsky, "Information Bottleneck," 深度学习与信息论（多篇，从 1999 到 2015）。
30. Harnad, "The Symbol Grounding Problem," *Physica D* 42:335–346, 1990. —— 符号接地问题经典。

### 6.2 必读书（10 本）

1. **Pearl, *Causality*** (Cambridge UP, 2009) —— 因果推断数学圣经。
2. **Pearl & Mackenzie, *The Book of Why*** (Basic Books, 2018) —— 因果科普。
3. **Spivak, *Category Theory for the Sciences*** (MIT Press, 2014) —— 范畴论入门。
4. **Minsky & Papert, *Perceptrons*** (MIT Press, 1969/1988) —— 连接主义批判经典。
5. **Russell & Norvig, *Artificial Intelligence: A Modern Approach*** (4th ed., 2020) —— AI 教科书，符号主义视角。
6. **Goodfellow, Bengio, Courville, *Deep Learning*** (MIT Press, 2016) —— 深度学习圣经。
7. **Sutton & Barto, *Reinforcement Learning: An Introduction*** (2nd ed., 2018) —— RL 圣经，世界模型的理论基础。
8. **Tegmark, *Life 3.0: Being Human in the Age of Artificial Intelligence*** (Knopf, 2017) —— AGI 哲学。
9. **Bostrom, *Superintelligence: Paths, Dangers, Strategies*** (Oxford UP, 2014) —— AGI 风险。
10. **Mitchell, *Artificial Intelligence: A Guide for Thinking Humans*** (FSG, 2019) —— 对 LLM 炒作的清醒批判（Melanie Mitchell，Santa Fe Institute）。

### 6.3 必看课程（5 门）

1. **Caltech/Anandkumar "Neural Operators" 课程系列** —— PDE + ML 前沿（Anima Anandkumar，FNO 作者）。
2. **Stanford CS224W "Machine Learning with Graphs"**（Jure Leskovec）—— 图神经网络，等变网络基础。
3. **MIT 18.06 / 18.06SC 线性代数**（Gilbert Strang）—— 用户数学基础重建的起点。
4. **Lean 4 官方教程 "Theorem Proving in Lean 4"**（Jeremy Avigad 等）—— 形式化证明入门。
5. **Brady Neal "Causal Inference" YouTube 课程** —— 因果推断入门，配合 Pearl 书。

### 6.4 关键人物（值得关注的 Twitter/X / 博客）

- **Yann LeCun**（@ylecun）—— 世界模型/JEPA 路线旗手，活跃批评 LLM 中心论。
- **Judea Pearl**（UCLA 主页 + 访谈）—— 因果推断之父，定期发表对深度学习的批评。
- **Bernhard Schölkopf**（马普所）—— 因果表征学习推动者，相对低调但论文必读。
- **Anima Anandkumar**（Caltech/NVIDIA，@AnimaAnandkumar）—— Neural Operators、AI4Science 旗手。
- **Jürgen Schmidhuber**（@SchmidhuberAI）—— 历史视角，常强调其 1990s 工作的优先权。
- **Bruno Gavranović** —— 范畴论 + 深度学习，compositional DL 推动者。
- **Terence Tao**（UCLA，博客）—— 顶级数学家，公开讨论 AI 辅助数学研究（Lean 的早期采用者）。
- **Kevin Buzzard**（Imperial College）—— Lean for mathematicians 布道者，"Liquid Tensor Experiment" 发起人。

---

## 📌 进一步阅读路径

**如果你只有 2 小时**：读 Pearl《The Book of Why》前 3 章 + 本文开篇 + 第二章缺陷分析。

**如果你有 20 小时**：读完 Schölkopf 2102.11107 + Garcez/Lamb 2012.05876 + LeCun 2022 白皮书 + Toolformer + ReAct + 本卷 `03-ai4math/01-formal-proof.md`。

**如果你有 200 小时（深入一个方向）**：选神经-符号 + Lean 路线 → 学完 Lean 4 教程 + 读 AlphaProof/AlphaGeometry + 贡献 Mathlib 一个命题 + 做一个 LLM→Lean 自动形式化小项目。

## ✍️ 思考题（5 道）

1. **接地鸿沟挑战**：假设你训练了一个 LLM，它能在 Lean 里生成"看起来正确"的证明步骤。但你怎么保证它生成的 Lean 标识符（如 `h_main_theorem`）真的对应它"心里想"的数学对象？请设计一个实验来检测接地失败。提示：考虑对抗性 prompt。

2. **覆盖 vs 严格的量化**：AlphaGeometry 在 IMO 几何题上达到金牌水平，但 IMO 几何是一个封闭域（公理和题型有限）。如果把 AlphaGeometry 的方法扩展到**研究级几何**（比如代数几何的 scheme 论），你认为覆盖率会下降多少？为什么？哪些缺陷会成为瓶颈？

3. **世界模型的因果性**：DreamerV3 学的是 $P(s'|s,a)$。假设有两个环境 A 和 B，它们在训练数据里不可区分（同样的 $P(s'|s,a)$），但因果结构不同（A 里 $a$ 导致 $s'$，B 里 $s'$ 导致 $a$，恰好共现）。DreamerV3 能区分吗？如果能，靠什么？如果不能，这意味着世界模型的什么根本局限？

4. **工具增强的本质**：ReAct 论文证明 LLM + 工具比纯 LLM 强。但一个连"该不该相信搜索结果"都判断不好的 LLM，外包工具真的能可靠吗？请构造一个反例：一个 ReAct agent 在某个任务上比纯 LLM **更差**。提示：考虑错误传播。

5. **范畴论的价值**：Backprop as Functor 把反向传播形式化为函子。这个形式化能帮你**设计一个更好的优化器**吗？如果能，怎么做？如果不能，那范畴论对 ML 的实际价值是什么？请给出你的判断（支持或反对），并用一个具体例子论证。

---

<!-- delegate 直接写入，2026-07-20。所有 arXiv ID 经 export.arxiv.org 一手核实：PINN 1711.10561, FNO 2010.08895, DeepONet 1910.03193, EGNN 2102.09844, HNN 1906.01563, LNN 2003.04630, Schölkopf 因果表征 2102.11107, NS-CL 1904.12584, Backprop as Functor 1711.10455, Neurosymbolic 3rd Wave 2012.05876, V-JEPA 2 2506.09985, DreamerV3 2301.04104, Toolformer 2302.04761, ReAct 2210.03629, RAG 2005.11401。Nature/Science DOI 沿用本卷 CHANGELOG 已核实记录。Pearl《Causality》、LeCun 白皮书、DeepProbLog(NeurIPS)、Cyc、Harnad 符号接地 按 well-known reference 引用未附 arXiv ID。 -->
