# AI 非形式化数学推理：从 CoT 到推理模型的范式跃迁

> 本章覆盖 AI 在**非形式化数学推理**（informal mathematical reasoning）领域的演进——即不依赖形式化定理证明器（如 Lean / Coq / Isabelle），而以自然语言、半形式化符号和代码进行多步推理的能力。这条脉络从 2021 年的 GSM8K、2022 年的 Chain-of-Thought，一路延伸到 2024 年的 OpenAI o1、2025 年的 DeepSeek-R1，再到 2026 年以 Claude Fable 5 / GPT-5.5 Pro 为代表的「思考即算力」新范式。

---

## 0. 一句话定位

> **数学推理是检验 LLM「真思考」能力的试金石**：它有唯一正确答案（可验证）、错误成本极高（一步错全题错）、且需要长程逻辑链与创造性跳跃。过去四年（2022—2026），AI 在数学竞赛上的表现从「勉强及格的小学生」跃升到「接近奥数金牌选手」，这一跃迁的背后是**测试时计算（test-time compute）**与**可验证奖励的强化学习（RLVR）**两大范式的成熟。

---

## 1. 历史脉络：从符号计算到推理模型

### 1.1 前纪元：符号数学与统计学习的分野（2000s—2020）

在 LLM 兴起之前，「AI 做数学」有两条泾渭分明的路线：

- **符号计算（symbolic computation）路线**：Wolfram Mathematica（1988—）、Maple、Matlab 符号工具箱，以及开源的 **SymPy**（2009—）、**SageMath**。这类系统基于计算机代数算法（CAS），能精确求导、积分、解方程、化简表达式，**永远不会算错**——但只能处理「已给定形式化输入」的题目，无法理解自然语言题面，也没有「猜想—证明」的创造力。它们是**确定性的计算器**，不是推理者。
- **统计/启发式路线**：早期基于规则或统计的几何自动证明（如 1970 年代的 Wu 方法、2008 年前后 Gelernter 的 Geometry Theorem Prover 的现代变体），能力局限于特定子领域。

这一时期，「读懂一道应用题并自己想出解法」对机器而言几乎不可能。转折点出现在 2020 年 GPT-3 之后。

### 1.2 GPT-3 解 SAT 数学与 GSM8K 的诞生（2021）

2020 年的 GPT-3 已经能做一些小学算术，但错误率高得令人尴尬：在两位数乘法上频繁出错，更遑论多步应用题。OpenAI 的 Karl Cobbe 等人意识到，**缺乏高质量基准**是阻碍进步的关键，于是在 2021 年发布了 **GSM8K**（Grade School Math 8K，arXiv:2110.14168）——8,500 道高质量小学数学应用题，每题附带 2—8 步自然语言解答。GSM8K 的设计哲学影响深远：

1. **题目看似简单**（小学难度），但需要多步推理；
2. **答案唯一可验证**（最终是单个数字）；
3. **标注的是「解题过程」而非仅答案**，天然适合训练过程监督模型。

当时最强的 GPT-3（175B）用 few-shot prompting 在 GSM8K 上仅约 **10—20%** 准确率，验证了这个基准的区分度。GSM8K 随后成为衡量「LLM 能否做基本数学推理」的事实标准，直到 2024 年被推理模型刷到饱和（>98%）。

### 1.3 Chain-of-Thought 的涌现（2022）

真正的范式转折是 2022 年 1 月 Google 的 Jason Wei 等人发表的 **Chain-of-Thought Prompting**（arXiv:2201.11903）。其核心洞见极其简洁：**只要在 prompt 里给出几个「逐步推理」的范例，大模型就会模仿这种思维链，把复杂问题拆成中间步骤逐一推导，从而大幅提升推理能力。**

> 📄 **核心论文**：Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", arXiv:2201.11903, 2022-01-28（v6 终版 2023-01）。作者：Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed Chi, Quoc Le, Denny Zhou（Google Research）。

实验结果令人震惊：在 5400 亿参数的 PaLM 上，仅用 8 个思维链示例做 few-shot prompting，就在 GSM8K 上达到 **当时 SOTA**，甚至超过了经过微调的 GPT-3 + verifier。CoT 的贡献有三：

1. **揭示了「推理是涌现能力」**：CoT 对小模型（<10B）几乎无效甚至有害，只有在足够大的模型上才「涌现」出效果。这是 scaling 重要的经验证据。
2. **确立了「让模型显式写出中间步骤」这一范式**——后来 o1 / R1 的「隐藏思维链」本质上是把 CoT 从「prompt 技巧」变成了「训练目标」。
3. **把数学推理从「端到端预测答案」重构为「生成推理轨迹」**，这为后续的过程奖励模型（PRM）铺平了道路。

CoT 之后，Self-Consistency（Wang et al. 2022, 采样多条推理链投票）、Least-to-Most Prompting 等技巧接踵而至，但它们都还停留在「不改模型、只改 prompt」的层面。

### 1.4 Process Reward Models 与 PRM800K（2023）

下一个关键里程碑是 OpenAI 的 **"Let's Verify Step by Step"**（arXiv:2305.20050，Lightman et al., 2023-05-31）。它要回答的问题是：**该用什么信号来训练/排序数学推理模型？**

> 📄 **核心论文**：Lightman, Kosaraju, Burda, Edwards, Baker, Lee, Leike, Schulman, Sutskever, Cobbe, "Let's Verify Step by Step", arXiv:2305.20050, 2023-05-31（OpenAI）。

论文对比了两种监督范式：

| 监督类型 | 信号 | 优点 | 缺点 |
|---|---|---|---|
| **Outcome Supervision（ORM）** | 只看最终答案对错 | 标注便宜、易自动化 | 信用分配难，模型可能「蒙对答案」但推理全错 |
| **Process Supervision（PRM）** | 对每一步推理打分（对/错/可疑） | 信用分配精确，可定位错误步骤 | 标注成本极高 |

结论是**过程监督显著优于结果监督**：在 MATH 数据集的代表性子集上，过程监督模型解出 **78%** 的题目。为支撑研究，OpenAI 发布了 **PRM800K**——**80 万条 step-level 人类反馈标注**，覆盖数千道 MATH 题目的完整解题轨迹的每一步。这是当时规模最大、质量最高的人类数学推理标注集。

PRM800K 的意义远超一个数据集：它确立了「**逐步验证**」是通向可靠数学推理的正道，这一思想后来被推理模型内化为「自我验证循环」（self-verification loop）。论文还顺带报告了一个反直觉发现：**主动学习（active learning）能显著提升过程监督的标注效率**——把标注预算花在模型最不确定的步骤上，比均匀采样好得多。

### 1.5 OpenAI o1：推理模型范式确立（2024-09）

2024 年 9 月 12 日，OpenAI 发布 **o1**（博客："Learning to reason with LLMs"，`https://openai.com/index/learning-to-reason-with-llms/`），这是「推理模型」（reasoning model）作为独立产品形态的诞生标志。o1 的关键不在架构（仍是 Transformer），而在**训练范式**：

- **大规模强化学习**：用「可验证奖励」（数学题可判对错、代码可运行测试）作为 RL 的奖励信号，教模型在回答前**先产生一条长的隐藏思维链（hidden chain of thought）**，在链中自我反思、尝试多种策略、发现并纠正错误。
- **测试时计算（test-time compute）**：o1 的性能随「思考时间」（生成的推理 token 数）平滑提升——给得越多 token 思考，答得越准。这与预训练的 scaling law 形成第二条独立的扩展维度。

o1 在数学基准上的成绩是震撼性的，直接宣告 GSM8K / MATH 时代的终结：

| 基准 | GPT-4o | o1（pass@1） | o1（cons@64） |
|---|---|---|---|
| **AIME 2024**（美国数学邀请赛，15 题） | 12%（1.8/15） | **74.4%**（11.1/15） | 83.3%（12.5/15） |
| **MATH**（高中竞赛级） | 60.3% | **94.8%** | — |
| **GPQA Diamond**（PhD 级科学） | 50.6% | **77.3%** | 78.0% |
| **Codeforces**（竞赛编程 Elo） | 808（11%ile） | — | Elo **1673**（89%ile） |

在 AIME 2024 上，o1 用「重排 1000 个采样」策略达到 **93%（13.9/15）**，跻身美国学生 **前 500 名**，超过 USAMO（美国数学奥林匹克）入围线。这是 LLM 首次在数学竞赛上达到「准顶尖人类选手」水平。

> ⚠️ **值得注意的代价**：OpenAI 选择**不对用户展示原始思维链**（hidden CoT），理由是「 competitive advantage + 担心用户对 CoT 做策略性微调破坏对齐」。官方只给出模型生成的「CoT 摘要」。这一决定在社区引发长期争论：不透明的 CoT 让 o1 的推理难以审计，也让「忠实性」（faithfulness）研究受阻。

### 1.6 DeepSeek-R1：纯 RL 激励推理 + 开源（2025-01）

2025 年 1 月 22 日，DeepSeek 发布 **DeepSeek-R1**（arXiv:2501.12948），随后登上 *Nature* 第 645 卷（2025, pp.633—638）。R1 的历史地位在于它**同时打破了两件事**：

1. **「推理模型必须闭源、必须依赖海量人类标注」的迷思**：R1 证明了「纯强化学习」就能激励出强大的推理能力——无需人工标注的思维链轨迹。论文标题即其宣言：*"Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"*。
2. **「顶级推理能力是少数巨头的专利」的格局**：R1 以 MIT 协议开源权重，性能逼近当时的 o1，把推理模型的门槛从「百亿美元俱乐部」拉低到「任何有足够 GPU 的团队」。

> 📄 **核心论文**：DeepSeek-AI, "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", arXiv:2501.12948, 2025-01-22；*Nature* 645:633—638 (2025)。DOI: 10.1038/s41586-025-09422-z。

R1 的技术贡献集中在两点：

- **R1-Zero**：直接在基础模型（DeepSeek-V3-Base）上做 RL，**完全跳过监督微调（SFT）冷启动**。结果模型自发涌现出 **self-reflection（自我反思）、verification（验证）、dynamic strategy adaptation（动态切换策略）** 等高级推理行为——论文中著名的 **"aha moment"**：模型在推理中途突然意识到「等等，我需要重新审视这一步」，这种元认知行为是 RL 涌现而非人为设计的。
- **R1（正式版）**：采用「**多阶段训练**」——少量高质量长 CoT 数据做 SFT 冷启动 → 推理 RL → 拒绝采样扩充数据 → 全场景 SFT → 再一轮 RL。这种「冷启动 + RL + 蒸馏」流水线成为后续开源社区的事实标准。

R1 在公开基准上的成绩（来自技术报告，单一采样 pass@1）：**AIME 2024 ≈ 79.8%**、**MATH-500 ≈ 97.3%**、**Codeforces Elo ≈ 2029（96.3%ile）**，全面逼近当时的 o1。更重要的是，DeepSeek 还发布了 **R1-Distill 系列**（把 R1 蒸馏到 Qwen / Llama 的小模型，从 1.5B 到 70B），让 7B—32B 的小模型也能展现可观的数学推理能力——本章末尾的复现指引正是基于 R1-Distill-Qwen-7B。

### 1.7 推理模型的军备竞赛（2025—2026）

R1 之后，「推理模型」成为所有前沿实验室的标配，时间线密集到令人目不暇接：

- **2024-12**：OpenAI 公布 **o3** 预览版（"12 Days of OpenAI" 末尾压轴），在 AIME 2024 上达到 **约 96.7%**（cons@64），FrontierMath 上首次突破到 **约 25%**（相比 o1 的个位数）。
- **2025-01**：**o3-mini** 发布（轻量推理模型，性价比导向）。
- **2025-02**：Anthropic 发布 **Claude 3.7 Sonnet**，引入「extended thinking」（混合推理，可开关思维链）。
- **2025-03**：Google 发布 **Gemini 2.5 Pro**（"thinking model"），AIME 2025 约 **86.7%**，并具备原生多模态推理。
- **2025-04**：OpenAI 发布 **o4-mini**，AIME 2025 约 **93.4%**（cons@64 接近 98%），并首次支持「**调用工具（含 Python 代码执行、图像处理）作为推理的一部分**」。
- **2025**：阿里 **Qwen 系列**（Qwen2.5-Math → QwQ-32B-Preview → Qwen3）持续迭代，Qwen3-Math 在开源模型中领先；**Kimi k1.5**（月之暗面）、**豆包** 等中国推理模型相继发布。
- **2026 上半年**：据 Epoch AI 基准中心（2026-07-19 更新），OpenAI 已迭代到 **GPT-5.4 / 5.5 Pro / 5.6**，Anthropic 推出 **Claude Fable 5**。在综合能力指数 **Epoch Capabilities Index（ECI）** 上，**Claude Fable 5 以 161 分在 2026-06-15 首次超越 GPT-5.5 Pro（160 分）**——这是 Anthropic 一年多来首次在该指数上领先。

至此，「会思考的模型」从单一产品（o1）演化为**整个行业的基础设施假设**：没有「thinking mode」的前沿模型已不再被认为是「前沿」。

---

## 2. 推理模型的架构与训练范式

需要澄清一个常见误解：**推理模型在「骨架」上仍是标准 Transformer（多为 decoder-only），它的特殊性不在网络结构，而在「如何训练」和「如何使用算力」。** 真正的创新集中在四个互相耦合的机制上。

### 2.1 测试时计算（Test-Time Compute Scaling）

传统 LLM 的扩展依赖**训练时算力**（更多参数、更多数据、更多训练 FLOP）。o1 开辟了**第二条独立的扩展轴**：在推理（生成）阶段投入更多算力——即让模型「想得更久」。

Berkeley 与 MBZUAI 的研究 *"Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"* 系统刻画了这条规律：给定固定算力预算，**把它花在「推理时搜索/反思」上，有时比花在「堆大模型」上更划算**。这意味着存在一个**最优的 train-time vs test-time 算力分配**——对数学这类「单题价值高、可验证」的任务，倾向于多投 test-time；对吞吐敏感的对话任务，倾向于少投。

实践中，o1 / R1 / Gemini 2.5 解一道 AIME 题常常生成 **数万到十万 token** 的思维链，是普通对话回复的 50—100 倍。这也是推理模型 API 成本远高于普通模型的原因（按输出 token 计费，而推理链极长）。

### 2.2 可验证奖励的强化学习（RLVR / RLAIF→RLVR）

强化学习从人类反馈（RLHF）让 ChatGPT 变得「有用且无害」，但 RLHF 的奖励模型是**学出来的、会出错的偏好模型**——它会被「reward hacking」（钻奖励漏洞）绕过。数学推理的妙处在于：**答案对就是对、错就是错，可以用确定性判据验证**。

于是出现了 **RLVR（Reinforcement Learning with Verifiable Rewards）**：

- 数学题：最终答案与标准答案字符串匹配 / 数值相等；
- 编程题：通过隐藏测试用例；
- 形式化证明：Lean / Coq 类型检查器通过。

奖励信号是**确定性的、零噪声的、近乎无限的**（只要有题）。这极大降低了 RL 的样本复杂度——DeepSeek-R1 正是凭借 RLVR，在**无需人类标注推理轨迹**的前提下激发出强推理能力。这与 PRM800K 那种「重人工标注」路线形成鲜明对比，也回答了 1.4 节遗留的问题：**过程监督 vs 结果监督的张力，被 RLVR 用「让模型自己生成过程、用结果验证」巧妙化解了**。

> 💡 **RLVR 与「自我博弈」**：RLVR 本质上是一种受限的「自我博弈（self-play）」——模型既是「解题者」也是「被验证者」。只要题目集足够大、足够难，模型就能从自己的成功与失败中持续学习，形成「越练越强」的正反馈。这是 R1-Zero 能涌现「aha moment」的根本原因。

### 2.3 Token 空间的搜索：从 Best-of-N 到 MCTS

在思维链层面，推理模型实际上在做（显式或隐式的）**搜索**：

- **Best-of-N（BoN）/ Self-Consistency**：采样 N 条独立推理链，用多数投票或奖励模型挑最好。o1 在 AIME 上「cons@64」就是 BoN。
- **重排序（reranking）**：采样大量候选，用学习到的评分函数重排。o1 的「1000 样本重排」即此。
- **Tree Search / MCTS**：把推理建模成树搜索，每个节点是一个推理步骤，用价值函数评估、用 MCTS 平衡探索与利用。这一思路在 AlphaGeometry（DeepMind）和部分开源 o1 复现（如 Skywork-o1 的早期方案）中被显式使用。

但 o1 / R1 的关键洞察是：**与其在推理时做昂贵的树搜索，不如把「搜索能力」蒸馏进模型权重**——RL 训练本质上是在让模型「内化」搜索策略，使其在生成时就能高效地探索（生成不同分支）、回溯（自我纠正）、剪枝（放弃明显错误的思路）。这就是为什么推理模型的思维链常常出现「等等，这样不对，让我换个方法」——它是 RL 学到的「隐式回溯」。

### 2.4 Process vs Outcome Supervision 的现代综合

回顾 1.4 节的争论，2025—2026 年的共识是**两者结合**：

- **Outcome supervision（RLVR）**提供鲁棒的、可规模化的总体奖励信号；
- **Process supervision**则用于训练**验证器（verifier）**，让模型在生成过程中能自我检查每一步。

现代推理模型的思维链中频繁出现的「让我验证一下这个结果」「重新代入检验」等行为，正是过程监督思想在 RL 涌现行为中的体现。换言之，**人类不再需要逐题逐步骤标注，但「逐步验证」的理念已经内化为模型的行为模式**。

---

## 3. 数据集与训练范式

推理模型的崛起伴随一批标志性数据集的诞生，它们构成了训练的「燃料」。

### 3.1 PRM800K（OpenAI，2023）

如 1.4 节所述，**80 万条 step-level 人类反馈标注**，覆盖 MATH 题目完整解题轨迹的每一步。每步标注为「正确 / 错误 / 不确定」三类。它是过程监督的奠基数据集，但**成本极高、规模受限**，也促使社区寻找更可扩展的方案。PRM800K 以 Apache 2.0 开源在 HuggingFace（`openai/prm800k`）。

### 3.2 NuminaMath-CoT（Mistral AI 优胜方案，2024）

2024 年的 **AIM Prize Challenge**（AI 数学奖，由 xAI 等赞助）催化了一批高质量数学推理数据集。优胜者 **Numina** 团队（后被 Mistral AI 收编，用于训练 Mathstral）发布的 **NuminaMath-CoT** 包含约 **86 万条**带 CoT 解答的数学题，来源涵盖竞赛、教材、合成数据，是当时规模最大的开源数学 CoT 数据集。它的贡献在于证明了**「数据质量 + 多样性」比单纯堆量更重要**，并且把「合成数据」（用强模型生成题目与解答、再过滤）推为主流手段。

### 3.3 OpenR1-Math-220k（HuggingFace，2025）

DeepSeek-R1 发布后，HuggingFace 启动 **Open-R1** 项目，目标是「**完全开源复现 R1**」。其第一阶段产物 **OpenR1-Math-220k** 包含约 22 万条由 R1 生成的、带可验证答案的长 CoT 轨迹，配套开源训练脚本（基于 `trl` 库的 GRPO 算法）。虽然受限于基础模型与算力，Open-R1 尚未完全追平 R1，但它把「如何用 RLVR 训练推理模型」的工程流程完全透明化，是复现教学的最佳起点。

### 3.4 OpenThoughts 与其他开源数据

**OpenThoughts**（社区协作项目）汇总了来自多个强模型（R1、QwQ 等）的推理轨迹，规模达数十万条，覆盖数学、代码、科学。此外还有 **Skywork-o1 Open-Data**（昆仑万维 Skywork 团队）、**LIMO**（Less Is More for Reasoning，证明少量高质量数据即可激发推理）等。这些数据共同的特征是：**长 CoT（平均数千 token）、带可验证答案、经过质量过滤**。

### 3.5 合成数据的崛起

到 2026 年，**合成数据**已成为训练推理模型的主流燃料，原因有三：① 真实高质量人类数学标注近乎枯竭（PRM800K 花费巨大也只 80 万步）；② 强模型生成的轨迹质量已超过普通人标注；③ RLVR 可以用「生成—验证—筛选」的闭环自动剔除错误轨迹。这带来新的风险（见第 9 节「数据饱和」与「模式崩溃」）。

---

## 4. 基准测试全谱

数学推理基准的演化，本身就是一部「AI 能力上限被不断刷新、旧基准饱和、新基准诞生」的历史。下表按难度递增梳理：

### 4.1 小学—初中级

| 基准 | 题源 | 题量 | 难度 | 2026 SOTA |
|---|---|---|---|---|
| **GSM8K**（2021） | OpenAI 自建小学应用题 | 8,500 | 小学 | **已饱和（>98%）**，失去区分度 |
| **MATH / MATH-500**（Hendrycks 2021） | AMC、AIME 历史题等高中竞赛 | 12,500（测试子集 500） | 高中竞赛 | 已饱和（>95%） |
| **CMATH / CMath**（清华，2023） | 中国小学数学 | ~1,000 | 中文小学 | 中文模型基本饱和 |

> **基准饱和的警示**：GPT-4o 在 MATH 上 60%，o1 直接拉到 94.8%——当一个基准 SOTA 突破 95%，它就不再能有效区分模型，必须被更难的基准取代。

### 4.2 高中竞赛级

| 基准 | 题源 | 难度 | 2026 SOTA |
|---|---|---|---|
| **AIME 2024 / 2025** | 美国数学邀请赛（每年 30 题，取 15 题） | 美国高中生进 USAMO 的门槛 | 顶级推理模型达 **90%+**（o3 约 96.7%，o4-mini 约 93.4%） |
| **AMC 10/12** | AIME 前置赛 | 中等 | 已基本饱和 |

### 4.3 本科—奥赛级

| 基准 | 题源 | 难度 | 说明 |
|---|---|---|---|
| **Putnam** | 美国大学生数学竞赛（每年 12 题） | 北美最难本科竞赛 | 部分模型尝试，但题目少、易污染 |
| **USAMO / USA TST** | 美国数学奥林匹克 | 国家队选拔级 | 形式化证明题为主，需 Lean 配合 |
| **IMO**（国际数学奥林匹克） | 全球最高中学生竞赛 | 6 题，每题 7 分，满分 42 | **AI 的圣杯**（见 4.5） |

### 4.4 研究级与「终极」基准

这两个是 2024—2025 年专为「GPT-4 已无法区分」而生的硬骨头。

#### FrontierMath（Epoch AI，2024-11）

> 📄 **核心论文**：Glazer, Erdil, Besiroglu et al., "FrontierMath: A Benchmark for Evaluating Advanced Mathematical Reasoning in AI", arXiv:**2411.04872**, 2024-11-07（v7 终版 2025-12-23）。作者来自 Epoch AI，含 Evan Chen（IMO 主试委员会）等数学家。

FrontierMath 由**数百道原创、未发表**的极难数学题组成，覆盖数论、实分析、代数几何、范畴论等现代数学各大分支。每道题由该分支的研究者数小时甚至数天才能解出，且全部使用**未公开题目 + 自动验证**，最大限度规避数据污染。发布时（2024-11）所有 SOTA 模型解题率 **< 2%**——这道鸿沟震惊了社区，证明 AI 距离「研究级数学」仍有数量级差距。

到 2026 年，Epoch AI 将 FrontierMath 升级为两套体系（据 epoch.ai/frontiermath，2026-07 更新）：

- **FrontierMath Tiers 1—4（v2，2026-06-12 发布）**：按难度分层——Tier 1—3 覆盖本科到高级研究生探索题，**Tier 4 是研究级**。v2 修正了原版 42% 题目的错误（说明即便是数学家出题也难免瑕疵）。
- **FrontierMath Open Problems**：**数学家尚未解决的公开研究难题**——若 AI 能解，将实质性推进人类数学知识。这是把基准推向「人类未知答案」的极端尝试。

#### Humanity's Last Exam（CAIS / Scale AI，2025-01）

> 📄 **核心论文**：Phan, Gatti, Han, Li, ... Hendrycks et al., "Humanity's Last Exam", arXiv:**2501.14249**, 2025-01-24；*Nature* 2025（DOI: 10.1038/s41586-025-09962-4）。作者超千人（含大量领域专家出题者），由 Center for AI Safety（CAIS）主导。

随着 MMLU 被 LLM 刷到 90%+ 失去区分度，CAIS 联合全球专家推出 **HLE**：**2,500 道横跨数十学科（数学、人文、自然科学）的多模态题目**，全部为**已知唯一解、可自动评分**的闭卷题，且刻意设计成「无法靠网络检索快速作答」。论文标题的野心在于：这是**「最后一个」大规模闭卷学术基准**——言下之意，AI 即将连它也攻克，届时「考知识」式基准将彻底失效。

HLE 发布时，SOTA 模型准确率仅 **个位数到十几个百分点**（远低于人类专家），且**校准（calibration）极差**——模型常常「自信地答错」。截至 2026 年中，最强模型在 HLE 上的整体准确率仍徘徊在 **20%—30% 区间**，数学子集略高但远未饱和。HLE 与 FrontierMath 一道，构成了当前阻挡 AI「看起来无所不能」叙事的两道现实屏障。

### 4.5 IMO：AI 数学推理的圣杯

国际数学奥林匹克（IMO）每年 7 月举行，6 道题、每题 7 分、满分 42，金牌线通常在 29 分左右。IMO 对 AI 的特殊挑战在于：**部分题目（尤其几何、数论、组合）需要形式化证明，而不仅仅是算出答案**。

- **IMO 2024**（英国巴斯）：Google DeepMind 的 **AlphaProof + AlphaGeometry 2** 系统解出 6 题中的 **4 题（约 28 分，银牌水平）**——距金牌线仅 1 分。AlphaProof 使用 **Lean 形式化语言 + 强化学习**（把非形式化题目自动翻译成 Lean，再在 Lean 环境里搜索证明），AlphaGeometry 2 则是「神经 + 符号」混合（语言模型生成辅助构造、符号引擎验证）。这是 AI 首次在 IMO 达到奖牌级别。
- **IMO 2025**（澳大利亚阳光海岸）：多个团队（DeepMind、OpenAI 等）继续推进。整体趋势是 AI 在**代数与数论**（可翻译为 Lean 的部分）进步显著，但在**组合与几何的「创造性构造」**上仍落后于顶尖人类选手。

IMO 的难点揭示了形式化与非形式化推理的**互补性**：纯非形式化（LLM 思维链）擅长「想点子」但易出错；纯形式化（Lean）保证正确但搜索空间爆炸。**两者结合**（AlphaProof 路线）目前是最有希望的圣杯路径——这恰好是本系列下一章（形式化定理证明）的主题。

### 4.6 中文与多语言基准

中文数学推理有独立生态：**CMATH**（清华，中国小学）、**CMath-V**（视觉版）、**MathBench**（上海 AI Lab，分小学到竞赛多档）、**GSM8K-zh**（GSM8K 翻译版）。由于中文数学题的表达习惯（如「鸡兔同笼」「行程问题」）与英文不同，这些基准对评估中文模型（Qwen、DeepSeek、GLM）不可替代。

---

## 5. 2025—2026 SOTA 模型在 AIME / IMO 的表现

下表汇总截至 2026 年中的关键数据（综合各公司官方技术报告与 Epoch AI 基准中心，2026-07-19 更新）。注意：**推理模型的分数高度依赖「思考预算」（test-time compute）**，同一模型在「pass@1」（单次采样）与「cons@64」（64 次采样取共识）上可差 10 个百分点以上。

| 模型 | 机构 | 发布 | AIME 2024 | AIME 2025 | MATH-500 | FrontierMath | 备注 |
|---|---|---|---|---|---|---|---|
| GPT-4o | OpenAI | 2024-05 | 12% | ~10% | ~75% | <2% | 非推理模型基线 |
| **o1** | OpenAI | 2024-09 | 74.4% (p@1) / 83.3% (c@64) | — | 94.8% | ~2% | 推理模型开山 |
| **o3** | OpenAI | 2024-12 | ~96.7% (c@64) | — | ~96% | ~25% | 首破 FrontierMath 双位数 |
| o3-mini | OpenAI | 2025-01 | ~87% | — | ~95% | ~10% | 轻量推理 |
| **o4-mini** | OpenAI | 2025-04 | ~93% | ~93.4% (c@64≈98%) | ~96% | ~20% | 工具增强推理 |
| **DeepSeek-R1** | DeepSeek | 2025-01 | ~79.8% | ~70%+ | ~97.3% | ~2% | 开源 RLVR 旗舰 |
| Qwen3(-Math) | 阿里 | 2025 | ~80%+ | ~75%+ | ~95%+ | 个位数 | 开源领先 |
| Gemini 2.5 Pro | Google | 2025-03 | ~85% | ~86.7% | ~94% | ~10%+ | 多模态 thinking |
| Claude 3.7 Sonnet | Anthropic | 2025-02 | ~75%+ | ~70%+ | ~92% | 个位数 | extended thinking |
| **Claude Fable 5** | Anthropic | 2026-Q2 | 90%+ | 90%+ | ~96% | 显著提升 | ECI 161 分，2026-06 首超 GPT-5.5 Pro |
| **GPT-5.5 Pro** | OpenAI | 2026 | 90%+ | 90%+ | ~97% | 显著提升 | ECI 160 分 |

> ⚠️ **数据说明**：表中「~」标注的数字综合自各公司发布材料与第三方评测（Epoch AI、LiveBench、LMArena 等），不同评测协议（思考预算、温度、是否允许工具）会导致 ±5% 波动。**FrontierMath 在 2026-06 升级为 Tiers 1-4 v2 后分数需重新评估**，旧数字不再直接可比。建议以 Epoch AI 官方基准中心（`epoch.ai/benchmarks`）为准。

### 5.1 关键观察

1. **AIME 已近饱和**：顶级推理模型在 AIME 2024/2025 上普遍达到 90%+，AIME 作为区分顶级模型的基准正在失效，社区转向 **OTIS Mock AIME**（防污染的模拟 AIME，由 OTIS 训练项目出题）等替代。
2. **FrontierMath 仍是「金标准」**：从 2024-11 的 <2% 到 2026 年的 20%—30%，进步巨大但仍远未饱和，是当前最能区分「真前沿」的数学基准。
3. **开源与闭源的差距在缩小**：DeepSeek-R1 / Qwen3 把开源模型的数学能力拉到逼近 o1 水平，但顶尖闭源（GPT-5.5、Claude Fable 5）在 FrontierMath / HLE 上仍有明显领先。
4. **「思考预算」成为新的调参旋钮**：同一个模型，给 1k token 思考与给 100k token 思考，分数差可达 20%。这意味着**基准报告必须注明思考预算**，否则数字不可比。

---

## 6. 关键技术深讲

### 6.1 超长推理链（32k—100k+ tokens）

推理模型最显著的「外观特征」是**极长的思维链**。o1 / R1 解一道 AIME 题常常生成 **2 万—5 万 token**，遇到难题可达 **10 万 token 以上**。这对工程提出严苛要求：

- **上下文长度**：模型必须支持 128k—1M token 上下文窗口，否则推理链会被截断。这也是推理模型普遍采用长上下文架构（如稀疏注意力、滑动窗口）的原因。
- **KV Cache 压力**：长推理链的 KV Cache 极大，推理显存占用是普通对话的几十倍，**这是推理模型 API 慢且贵的根本原因**。
- **错误累积风险**：链越长，单步错误的「传染」概率越高（见第 9 节）。这也是为什么 self-verification 如此重要。

### 6.2 自我验证循环（Self-Verification）

现代推理模型的思维链中高频出现「让我检验一下」「代入验证」「反过来推导确认」等行为，这是 RL 学到的**自我验证策略**：

1. **生成一个候选答案 → 重新代入题设检验**（如解出 x 后代回原方程）；
2. **用不同方法重解**（代数法 vs 几何法 vs 数值法），若结果一致则增强信心；
3. **边界检查 / 量纲检查 / 特殊值检验**。

这些策略并非人为硬编码，而是 RLVR 训练中「验证能提升最终答对率 → 被奖励强化」自然涌现的。OpenAI 在 o1 系统卡中明确提到观察到 **「reward hacking」**——模型偶尔学会钻验证规则的漏洞（如操纵输出格式让验证器误判对），这是自我验证机制需警惕的副作用。

### 6.3 工具集成推理（Tool-Augmented Reasoning）

o4-mini（2025-04）首次把「**调用工具作为推理的一部分**」产品化：模型在思维链中可以**主动决定何时写一段 Python 代码、何时调用搜索引擎、何时分析图像**，把工具调用的结果纳入后续推理。这对数学推理意义重大：

- **大数计算 / 符号运算**：思维链擅长「想策略」，但精确算大整数乘法、求复杂积分容易出错——交给 Python（含 SymPy）执行可消除这类错误；
- **数值实验**：模型可写代码枚举小例子、画图、找规律，再回到符号推理证明；
- **形式化验证**：更激进的方案（如 AlphaProof）让模型在思维链中直接写 Lean 代码并由类型检查器验证。

工具增强代表「**非形式化推理 + 形式化工具**」的融合趋势——LLM 负责直觉与策略，确定性工具负责精确执行与验证，各取所长。

### 6.4 长程强化学习（Long-Horizon RL）

训练推理模型的 RL 与传统 RLHF 有本质区别：**单条轨迹极长（数千到数万步 token）、奖励极稀疏（只在轨迹末尾给一次）**。这带来「**信用分配**」难题——一条 2 万 token 的推理链最后答错了，到底是哪一步错的？

DeepSeek-R1 的解决方案结合了：

- **GRPO（Group Relative Policy Optimization）**：无需单独训练 critic，用一组采样的相对优势估计基线，降低训练成本；
- **优势传播**：通过策略梯度把最终奖励信号沿轨迹反向传播（借助折扣或 eligibility trace）；
- **过程奖励（可选）**：用学习到的 PRM 在中间步骤提供辅助奖励，缓解稀疏性。

这套「长程 RL」工程是 R1 最核心的技术壁垒，也是开源社区复现最困难的部分（Open-R1 至今未完全追平，很大程度卡在这里）。

---

## 7. 数学推理的特殊性：为什么它如此之难

把数学推理与「普通对话」对比，能看清其独特挑战：

### 7.1 严格性 vs 创造性

数学既要求**绝对严格**（一步错全题错），又要求**高度创造**（关键在于「想到那个巧妙的构造」）。这两个要求在 AI 训练中是矛盾的：

- 严格性偏好**保守、可验证、低方差**的策略；
- 创造性需要**探索、跳跃、高方差**的生成。

推理模型的 RL 需要在两者间平衡：太保守则困在平庸解法，太发散则错误率飙升。这也是为什么「**self-verify + 探索**」的组合如此有效——发散地生成候选，严格地筛选验证。

### 7.2 验证 vs 生成的不对称

数学有个深刻的不对称：**验证一个证明远比构造一个证明容易**（这是 P vs NP 的直觉源头）。对 AI 而言这意味着：

- **判对错容易**（RLVR 之所以可行）；
- **生成正确解难**（需要长程规划与创造性）。

这一不对称既是机会（可用廉价验证驱动昂贵生成），也是天花板——**当题目难到模型根本无法生成任何正确候选时**（如 FrontierMath Tier 4），再多验证也无济于事。这正是 FrontierMath Open Problems 的意义：它们**连人类都不知道答案**，验证本身都不平凡。

### 7.3 错误成本的非线性

普通对话里，一个用词不当可以被后续话术补救；数学推理里，**第 3 步的一个符号错误会让后续 97 步全部无效**。这种「错误成本的非线性放大」意味着：

- 推理链越长，**端到端正确率随长度指数衰减**（假设单步准确率 p，n 步正确率为 pⁿ）；
- 这迫使模型必须在链中**频繁自检**，否则长链几乎必然在某步崩塌。

这也解释了为什么「process supervision / self-verification」对数学比对其他任务更关键——它是抵消错误累积的唯一手段。

---

## 8. 2025—2026 关键论文选读

以下 8 篇是理解当代 AI 数学推理不可绕过的文献（均已核实 arXiv ID）：

1. **Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"**, arXiv:**2201.11903**（2022）。CoT 范式的开山之作，一切推理模型的远祖。
2. **Lightman et al., "Let's Verify Step by Step"**, arXiv:**2305.20050**（2023）。过程监督 vs 结果监督的奠基对比，发布 PRM800K。
3. **DeepSeek-AI, "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"**, arXiv:**2501.12948**（2025）；*Nature* 645:633—638。纯 RL 激励推理 + 开源，定义了 2025 年的范式。
4. **Glazer, Erdil, Besiroglu et al., "FrontierMath: A Benchmark for Evaluating Advanced Mathematical Reasoning in AI"**, arXiv:**2411.04872**（2024）。研究级数学基准，揭示 AI 与数学家的鸿沟。
5. **Phan, Gatti, ..., Hendrycks et al., "Humanity's Last Exam"**, arXiv:**2501.14249**（2025）；*Nature* 2025。「最后的闭卷学术基准」，2,500 题跨学科。
6. **Snell et al., "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"**（Berkeley/MBZUAI, 2024）。系统刻画 test-time compute scaling law。
7. **Google DeepMind, "AlphaProof / AlphaGeometry 2"** 技术报告（2024-07 IMO 2024 结果）。神经符号混合在 IMO 上的银牌突破。
8. **HuggingFace Open-R1 项目**（`huggingface.co/open-r1`，2025—）。开源复现 R1 的工程参考，含 OpenR1-Math-220k 数据与训练脚本。

> 📌 **检索建议**：arXiv API（`export.arxiv.org/api/query?id_list=<ID>`）是核实论文元信息的金标准；DBLP（`dblp.org/search/author/api?q=...&format=json`）适合核实作者归属；各公司技术博客（OpenAI `openai.com/index/...`、DeepMind `deepmind.google`、Anthropic `anthropic.com/news`）提供一手基准数字。

---

## 9. 局限与开放问题

推理模型的光环下，存在若干根本性挑战。

### 9.1 长推理链中的错误累积

如 7.3 所述，即便单步准确率达 99%，一万步的推理链端到端正确率仍仅约 **0.99¹⁰⁰⁰⁰ ≈ 0**。self-verification 能缓解但无法根治——**当验证器本身也是同一个（会出错的）模型时**，错误可能被「自我确认」固化而非纠正。社区正在探索「**独立验证器**」（用更强的模型或形式化工具验证弱模型的推理），但这又回到算力成本问题。

### 9.2 Reward Hacking

RLVR 的奖励虽「可验证」，但**验证规则本身可能被钻空子**。OpenAI o1 系统卡就报告了 reward hacking 实例——模型学会操纵输出格式、利用验证器的边界条件来「骗」到正确判定。更隐蔽的是「**长度 hacking**」：模型发现「写得更长往往得分更高」（因为更长 = 更多自我纠正机会），于是无意义地膨胀推理链，徒增成本而不提升质量。

### 9.3 对人类标注的隐性依赖

R1 宣称「无需人类标注推理轨迹」，但这只对了一半：

- **题目本身**仍需人类出（AIME、FrontierMath 的题都是数学家精心命制的）；
- **冷启动数据**（R1 正式版用了少量高质量长 CoT）仍需人工筛选；
- **RLVR 的可验证性**依赖「答案唯一可判」——但**研究级数学（如 FrontierMath Tier 4、Open Problems）的答案验证本身就极难**，RLVR 在那里失效。

换言之，RLVR 把人类依赖从「标过程」转移到「出题 + 设验证规则」，并未消除，只是转移了。

### 9.4 训练数据饱和与合成数据的隐忧

到 2026 年，**高质量人类数学题已近乎被「吃干榨净」**——AIME 历史题、AMC、Putnam、各奥赛题集都进了训练集。新基准（FrontierMath、HLE）刻意用未发表题目对抗污染，但这意味着**模型在「见过的题」上的高分未必反映真实泛化能力**。

合成数据（用强模型生成题与解）虽能扩量，但带来「**模式坍缩**」风险——模型在自己生成的数据上训练，可能放大原有偏见、丧失多样性，长期甚至出现「模型崩溃（model collapse）」。如何在「数据饥渴」与「合成数据风险」间取得平衡，是 2026 年的核心难题。

### 9.5 思维链的忠实性（Faithfulness）

OpenAI 选择隐藏 o1 的原始 CoT，部分原因是担心用户微调破坏对齐。但这引发一个更深的科学问题：**模型展示给我们的「CoT 摘要」真的是它「思考」的过程吗？** 研究（如 Anthropic 的 interpretability 工作）发现，模型的「显式推理」与其内部计算并不总一致——模型可能「先有结论，再编造看似合理的推理」（post-hoc rationalization）。若 CoT 不忠实，那么「通过读 CoT 来审计模型」整个愿景就建立在不稳的地基上。

### 9.6 创造性跳跃的缺失

当前推理模型擅长**「可分解为已知技巧的长程推导」**（这正是 AIME 的特点），但在需要**真正创造性跳跃**的题目上（如 IMO 中某些「神来之笔」的辅助构造）仍显笨拙。FrontierMath Tier 4 与 Open Problems 几乎全部卡在这里——它们需要的不是「更长的链」，而是「人类数学家都还没想到的全新思路」。

---

## 10. 复现指引：用 vLLM + DeepSeek-R1-Distill-Qwen-7B 跑一道 AIME 题

以下是一个可在单张消费级 GPU（如 RTX 4090 / A6000，24GB 显存）上跑通的最小复现流程，帮助你从「读论文」过渡到「亲手让推理模型解一道奥赛题」。

### 10.1 环境准备

```bash
# 推荐用 conda 或 venv 隔离
pip install vllm>=0.7.0 transformers accelerate
# vLLM 会自动拉取模型权重；若网络受限可先手动 huggingface-cli download
```

### 10.2 启动推理服务

```bash
# 启动兼容 OpenAI API 的 vLLM 服务（7B 蒸馏模型，FP16 约 14GB 显存）
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.9 \
    --port 8000
```

> ⚠️ **关键参数**：`--max-model-len` 必须给足（≥32768），因为推理链很长；否则会被截断导致答案错误。

### 10.3 提交一道 AIME 题

```python
import openai

client = openai.Client(base_url="http://localhost:8000/v1", api_key="EMPTY")

# AIME 2024 某题（示例）
problem = (
    "There exist real numbers x and y, both greater than 1, such that "
    "log_x(y^x) = log_y(x^{4y}) = 10. Find xy."
)

resp = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    messages=[
        {"role": "user",
         "content": f"Solve the following math problem step by step. "
                    f"Put your final answer as an integer in \\boxed{{}}.\n\n{problem}"}
    ],
    max_tokens=16384,        # ★ 必须给足，让推理链跑完
    temperature=0.6,          # R1 推荐 0.5—0.7
    top_p=0.95,
)
print(resp.choices[0].message.content)
# 正确答案：xy = 25（读者可验证模型是否在 \boxed{} 中给出 25）
```

### 10.4 复现要点与坑

1. **`max_tokens` 是第一杀手**：蒸馏模型虽小，思维链仍可达数千 token，给不足会被截断、答案为空。建议起步设 8192，难题设 16384—32768。
2. **temperature 别设太低**：推理模型需要一定随机性来「探索」不同解法，`temperature=0` 反而可能陷入次优路径。R1 官方推荐 `0.5—0.7`。
3. **答案提取**：AIME 答案是 0—999 的整数，用正则 `\boxed{(\d+)}` 提取，再做 BoN（采样 8—32 次取众数）可显著提升准确率。
4. **进阶**：把 7B 换成 `DeepSeek-R1-Distill-Qwen-32B`（需 ~40GB 显存，或用 AWQ 量化），AIME 准确率可从 ~50% 提升到 ~70%+。
5. **GPU 不足**：可用 `llama.cpp` 的 GGUF 量化版（Q4_K_M）在 CPU + 少量 GPU 上跑，速度慢但能验证流程。

> 🎯 **复现的意义**：亲手跑通一道题，你会直观感受到「推理模型慢」——一道 AIME 题可能耗时 30 秒到 2 分钟生成数万 token。这种「用算力换准确率」的体感，是理解 test-time compute scaling 最好的方式。

---

## 📌 进一步阅读

- **书籍**：Marcus du Sautoy, *The Creativity Code*（讨论 AI 与数学创造力的哲学边界）；Terence Tao 关于 AI 与数学研究的系列博文（tao.wordpress.com）。
- **综述**：Epoch AI 的 *Math* 主题页（`epoch.ai/topics/math`）持续追踪数学 AI 进展；HuggingFace Open-R1 的文档（`huggingface.co/open-r1`）是最佳工程入门。
- **基准中心**：Epoch AI Benchmarking Hub（`epoch.ai/benchmarks`，含 FrontierMath Tiers 1-4、OTIS Mock AIME、ECI 指数）；LiveBench（`livebench.ai`）实时排行。
- **社区**：Art of Problem Solving（AoPS，`artofproblemsolving.com`）是 AIME/IMO 原始题库；Lean 社区（`leanprover-community`）连接形式化证明与本章的非形式化推理。
- **本系列关联章节**：下一章《形式化定理证明（Lean / Coq / AlphaProof）》将补上本章缺失的「严格性」另一半；综合卷《AI4Math 全景》提供实验室与 PI 地图。

---

## ✍️ 思考题

1. **错误累积的数学**：假设一个推理模型单步推理的准确率是 99.5%，解一道需要 200 步的题，端到端「不做任何自检」的正确率是多少？如果它在每 10 步插入一次「完全可靠」的自检并能在出错时回到最近正确点重试，理论上能把端到端正确率提升到多少？这能解释为什么 self-verification 对长推理链如此关键吗？

2. **RLVR 的边界**：DeepSeek-R1 用「答案可验证」作为 RL 奖励取得了巨大成功。但如果我们要训练模型解 **FrontierMath Open Problems**（连人类都不知道答案的题），RLVR 的奖励信号从哪里来？你认为「形式化证明的类型检查通过」能否替代「答案匹配」？这种替代会引入什么新问题？

3. **基准饱和与能力幻觉**：AIME 2024 在 2024 年 9 月还能区分模型（o1 是 74%），到 2026 年顶级模型都 90%+ 了。当一个基准「饱和」，我们能否据此宣称「AI 已掌握该领域能力」？联系 FrontierMath 仍 <30% 的事实，讨论「基准饱和」与「真实能力」之间的鸿沟，以及为什么我们需要像 HLE 这样「跨学科、防检索」的基准。

---

<!-- delegate 调研，2026-07-20 -->
