# 第 05 章 · 模型结构真的停滞了吗？——架构创新真相、训练计算墙与跨学科突破路径

> **本章定位**：研究综述 + 创新提案（Synthesis 卷核心章节之一）
> **核心命题**：AI 的下一步突破到底卡在哪里？是模型结构停滞、是硬件瓶颈、还是底层基础设施？
> **方法论**：用 2022–2026 年的一手论文证据说话，所有 arXiv ID 经联网核实。
> **写作日期**：2026-07-20 ｜ **版本**：v1.6

---

## 开篇：一个被反复争论的命题

在 AI 研究社区，过去三年最持久的争论之一是：「**模型结构创新是不是停滞了？**」这个命题有几种看似合理的版本：

- **悲观版**：「自 2017 年 Transformer 以来，我们再没见过真正的架构革命，大家都在做 Transformer 变种，这是创新枯竭的信号。」
- **硬件决定版**：「瓶颈不在算法，全在算力——只要 NVIDIA 出新卡，所有问题自动解决。」
- **infra 红利版**：「真正的创新在底层——FlashAttention、TileLang、DualPipe 这些『看不见』的工作才是当前最大的红利来源。」

本章的目的是**用证据裁决这场争论**。需要先说明的是：作者（与你）最初提出的命题是「模型结构停滞」，但在系统梳理 2022–2026 年的论文后，**我们必须诚实地修正这个判断**。这不是附和，而是被数据说服。下面会先列出「看似停滞」的证据（必须诚实呈现才能有力反驳），再列出「极度活跃」的证据（每一个都附核实过的 arXiv ID），然后给出硬件瓶颈的分场景真相、TileLang 类思路的实质，最后落到跨学科创新提案与你专属的研究路线。

本章承诺三件事：

1. **不喊口号**：所有架构都给具体论文、具体技术贡献、具体性能数字。
2. **不分场景不下结论**：推理阶段是 memory-bound、训练阶段是 compute-bound，二者瓶颈完全不同，混为一谈必生谬误。
3. **把「红利在哪」讲清楚**：算法红利、工程红利、infra 红利，三者层次不同，对你的研究选题意义不同。

读完这一章，你应该能回答：**未来 5 年，应用数学研究型工程师该把时间投在哪里，才有最高的边际收益？**

---

## 一、前提 1：架构创新真的停滞了吗？（核心修正章节）

### 1.1 看似停滞的证据（先诚实列出，再反驳）

要公正地评估「停滞论」，必须先把它最强有力的论据摆出来。停滞论者并非无理取闹，他们有几条相当硬的证据：

**证据一：Transformer 的统治地位长达 8 年。** 自 2017 年 Vaswani 等人提出 Transformer 以来，几乎所有主流大模型（GPT 系列、Claude、Gemini、LLaMA、Qwen、DeepSeek、Mistral……）的骨干仍然是 Transformer。一个 8 年前的架构至今未被推翻，这在深度学习史上是罕见的——回想一下 CNN 时代，AlexNet (2012) 到 ResNet (2015) 到 EfficientNet (2019) 到 Vision Transformer (2020)，骨干更替的节奏是 3–4 年一次。

**证据二：主流模型清一色是 Transformer 变种。** 即便是号称「颠覆 Transformer」的架构（Mamba、RWKV、RetNet），目前也只在中小规模或特定场景取得胜利，没有任何一个在万亿参数规模上正面击败 Transformer。GPT-4、Claude 4、Gemini 2.5 的内部架构（据公开信息）仍是 Transformer + MoE 的组合。

**证据三：「革命」变得越来越少。** 2012–2018 是深度学习「范式转移」的高频期（ReLU、Dropout、BatchNorm、Attention、ResNet、Adam、GAN、BERT、GPT……每年都有改写教科书的工作）。2019 年之后，能称为「范式转移」的工作明显变少，更多的是「在已有范式上做工程优化」。

这三条证据都成立，停滞论的直觉正是来源于此。**但直觉是错的。** 下面的证据会表明：停滞论犯了一个典型的错误——**把「范式转移的频率下降」误读成了「创新停滞」**。实际上，我们正处在一个创新极度密集、但创新形式发生迁移的时期。

### 1.2 实际上极度活跃的证据

下面分七个维度，每一个都列举 2022–2026 年的具体工作（全部附核实过的 arXiv ID），你会看到创新不是停滞了，而是**爆炸了**。

#### A. Transformer 之外的新架构（state space / linear RNN / 长卷积 / 混合 / 仿生）

这是「停滞论」最该被打脸的地方。2023–2024 年涌现了一批足以与 Transformer 在中小规模正面竞争的非 Transformer 架构：

> **Mamba**：Gu & Dao, *Mamba: Linear-Time Sequence Modeling with Selective State Spaces* [arXiv:2312.00752](https://arxiv.org/abs/2312.00752)（2023-12-01）。提出**选择性状态空间模型（Selective SSM）**——让 SSM 的参数成为输入的函数，使模型能根据当前 token 选择性地保留或遗忘信息。推理吞吐量是 Transformer 的 5×，序列长度线性扩展，在语言/音频/基因组多模态达到 SOTA。这是第一个在语言建模上真正威胁 Transformer 的非注意力架构。

> **Mamba-2 (SSD)**：Dao & Gu, *Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality* [arXiv:2405.21060](https://arxiv.org/abs/2405.21060)（ICML 2024）。**理论上的关键突破**：证明了 SSM 与 attention 之间存在深刻的对偶关系（State Space Duality, SSD），通过结构化半可分矩阵（semiseparable matrices）的分解把两大家族统一起来。Mamba-2 的核心层比 Mamba 快 2–8×。这不仅是工程，更是**数学**——它告诉我们 attention 不是凭空发明的，它是某种更一般结构的一个特例。

> **RetNet**：Sun et al. (Microsoft), *Retentive Network: A Successor to Transformer for Large Language Models* [arXiv:2307.08621](https://arxiv.org/abs/2307.08621)（2023-07-17）。提出 **retention 机制**，同一个模型支持三种计算范式：并行（训练并行性）、循环（$O(1)$ 推理）、分块循环（线性复杂度长序列）。理论上推导了 recurrence 与 attention 的联系。这是微软对「Transformer 继承者」的官方下注。

> **Hyena**：Poli, Massaroli, Fu, Dao, Bengio, Ré et al., *Hyena Hierarchy: Towards Larger Convolutional Language Models* [arXiv:2302.10866](https://arxiv.org/abs/2302.10866)（2023-02-21）。用**隐式参数化长卷积 + 数据控制门控**构造 attention 的次平方替代品。在 8K 序列上比优化版 attention 快 2×，在 64K 上快 100×。这是把「长卷积」重新带回语言建模的代表作。

> **Jamba**：AI21 Labs, *Jamba: A Hybrid Transformer-Mamba Language Model* [arXiv:2403.19887](https://arxiv.org/abs/2403.19887)（2024-03-28）。**混合架构**的里程碑：交错堆叠 Transformer 块和 Mamba 块，部分层加 MoE。实现了单卡 80GB GPU 可装下、256K 上下文的高吞吐模型。它证明了一个关键事实——**未来很可能不是「Transformer vs 非 Transformer」的二选一，而是「如何在同一个模型里混合多种原语」**。

> **KAN**：Liu, Tegmark et al., *KAN: Kolmogorov-Arnold Networks* [arXiv:2404.19756](https://arxiv.org/abs/2404.19756)（ICLR 2025）。灵感来自 **Kolmogorov-Arnold 表示定理**：把激活函数从节点（neuron）移到边（weight），用样条参数化。每个权重参数被一个单变量函数取代。理论+实验显示 KAN 比 MLP 有更快的 scaling law，且**可解释**——能可视化、能帮助科学家重新发现数学物理定律。这是「从数学结构反推网络架构」的稀少尝试。

**小结**：仅 2023–2024 两年，就出现了至少 6 个有分量的非 Transformer 主干。其中 Mamba-2 还给出了 attention 与 SSM 的统一理论。**这与「停滞」毫无关系。**

#### B. Attention 机制的持续演化（一条清晰的工程演化树）

即便骨干仍是 attention，attention 本身也在剧烈演化。下面这条演化树值得每个研究者牢记，因为它直接关联推理成本：

```
MHA (原始, 2017)
   │
   ├─→ MQA  (Shazeer, 2019)        所有 query 共享 1 个 KV head
   │      [arXiv:1911.02150]
   │
   ├─→ GQA  (Ainslie et al., 2023)  介于 MHA 与 MQA 之间的分组
   │      [arXiv:2305.13245]        Llama 2/3 标配
   │
   ├─→ MLA  (DeepSeek V2, 2024)     把 KV cache 压进低维 latent 向量
   │      [arXiv:2405.04434]        KV cache 减少 93.3%
   │
   ├─→ NSA  (DeepSeek, 2025)        原生可训练稀疏注意力
   │      [arXiv:2502.11089]        粗粒度压缩 + 细粒度选择
   │
   └─→ Lightning Attention (Kimi K2) 线性 attention 的 IO-aware 高效实现
          [arXiv:2401.04658]
```

> **MQA**：Shazeer, *Fast Transformer Decoding: One Write-Head is All You Need* [arXiv:1911.02150](https://arxiv.org/abs/1911.02150)（2019-11-06）。让所有 attention head 共享同一对 K、V，大幅减少自回归解码时反复加载 K/V 张量的内存带宽开销。代价是轻微质量下降。

> **GQA**：Ainslie et al., *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints* [arXiv:2305.13245](https://arxiv.org/abs/2305.13245)（EMNLP 2023）。MQA 与 MHA 的插值——用「介于 1 和 head 数之间」的 KV head 数。提出把已有的 MHA checkpoint 用 5% 预训练算力 uptrain 成 GQA，质量接近 MHA、速度接近 MQA。**Llama 2 之后几乎所有开源模型都采用 GQA。**

> **MLA (Multi-head Latent Attention)**：DeepSeek-AI, *DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model* [arXiv:2405.04434](https://arxiv.org/abs/2405.04434)（2024-05-07）。把 K、V 压缩成一个低维 latent 向量再缓存，推理时再上投影还原。**KV cache 减少 93.3%**，生成吞吐提升 5.76×。这是目前推理效率最强的 attention 变体之一，DeepSeek V2/V3、Kimi K2 都在用。

> **NSA (Native Sparse Attention)**：Yuan, Gao, Dai et al. (DeepSeek), *Native Sparse Attention* [arXiv:2502.11089](https://arxiv.org/abs/2502.11089)（2025-02-16）。**原生可训练**（end-to-end）的稀疏注意力，结合粗粒度 token 压缩 + 细粒度 token 选择，做到算术强度均衡（arithmetic-intensity-balanced）+ 硬件对齐优化。在 64K 序列上对 full attention 全面加速，且预训练计算不牺牲性能。这是稀疏注意力从「推理时近似」走向「训练时原生」的关键一步。

> **Lightning Attention-2**：Qin, Yang, Wei et al., *Lightning Attention-2: Surpassing the Throughput of FlashAttention-2 in Long-Context Training* [arXiv:2401.04658](https://arxiv.org/abs/2401.04658)（2024-01-09）。把线性 attention 在因果设定下的累积求和（cumsum）瓶颈用 tiling 拆成 intra-block（常规 attention）+ inter-block（线性 kernel trick），用 Triton 做 IO-aware 实现。训练推理速度与序列长度无关（恒定）。这是 Kimi K2 长上下文的核心。

**演化逻辑**：MQA→GQA 是「减少 KV head 数」（一次压缩），MLA 是「把 KV 压进低维潜空间」（二次压缩），NSA 是「训练时就稀疏」（结构性压缩），Lightning Attention 是「换数学形式」（线性化）。每一次演化都对应着推理/训练成本的量级下降。这哪里是停滞？这是教科书级的工程演化。

还有一类专门解决长上下文分布的：

> **Ring Attention**：Liu et al. (UC Berkeley), *Ring Attention with Blockwise Transformers for Near-Infinite Context* [arXiv:2310.01889](https://arxiv.org/abs/2310.01889)（2023-10-03）。把长序列分块分布在多台设备上，块状计算 attention 与 FFN，把 KV 块的通信与块状 attention 的计算完全重叠。能训练/推理「设备数倍」于以往的序列长度，无近似、无额外开销，做到百万级 token 上下文。

#### C. MoE（混合专家）大爆发

MoE 不是新概念，但 2023–2024 是它从「实验室玩具」走向「主流标配」的两年：

- **Mixtral 8x7B / 8x22B**（Mistral AI）：把 MoE 带入开源主流，8 个专家每次激活 2 个。
- **DeepSeekMoE**（[arXiv:2405.04434](https://arxiv.org/abs/2405.04434)）：**细粒度专家 + 共享专家**创新——专家划得更细，并保留一部分「总是被用」的共享专家处理通用知识。DeepSeek V3 把这一思路推到 256 个路由专家 + 1 个共享专家，671B 总参数但每 token 只激活 37B。
- **Qwen MoE / Kimi K2**：Kimi K2 用 128 专家、激活约 32B，把 MoE 与 Lightning Attention 结合做万亿参数级长上下文。

**MoE 的本质**是**解耦「参数量」与「激活算力」**：参数可以无限大（提升模型容量），但每个 token 只激活一小部分（控制计算成本）。这是当前**绕过训练计算墙的最重要架构杠杆**——后面会详述。

#### D. Diffusion Transformer（DiT）：生成模型的统一骨干

> **DiT**：Peebles & Xie (Adobe/NYU), *Scalable Diffusion Models with Transformers* [arXiv:2212.09748](https://arxiv.org/abs/2212.09748)（2022-12-19）。把 latent diffusion 模型里传统的 U-Net 骨干换成在 latent patch 上操作的 Transformer。分析表明 DiT 的 Gflops 越高 FID 越低，具有良好的 scaling 性质。

DiT 的影响是深远的：**今天几乎所有顶级视频/图像生成模型都基于 DiT**——OpenAI Sora、NVIDIA Cosmos、阿里 Wan、快手 Kling、Google Veo。这意味着 Transformer 的统治范围从语言扩展到了视觉生成，并且扩散模型与自回归模型开始融合（Diffusion + AR hybrid）。这不是「停滞」，这是「骨干统一」。

#### E. 训练范式创新（这同样属于架构创新！）

很多人把「架构创新」狭义理解为「网络拓扑」，但训练范式本身就是架构的一部分。2022–2025 年训练范式的演化密度甚至超过了网络拓扑：

```
RLHF (InstructGPT, 2022)
   │
   ├─→ DPO  (Rafailov et al., 2023)        去掉 reward model，直接分类损失
   │      [arXiv:2305.18290]
   │
   ├─→ GRPO (DeepSeekMath, 2024)            去掉 critic，用 group-relative 优势
   │      [arXiv:2402.03300]                DeepSeek-R1 的核心
   │
   ├─→ Self-Rewarding (Meta, 2024)          LLM 自己给自己打分
   │      [arXiv:2401.10020]                ICML 2024
   │
   └─→ RLVR (Verifiable Rewards)            o1 / R1 的范式
          奖励来自可验证的程序（数学、代码）
```

> **DPO**：Rafailov et al., *Direct Preference Optimization: Your Language Model is Secretly a Reward Model* [arXiv:2305.18290](https://arxiv.org/abs/2305.18290)（2023-05-29）。重新参数化 reward model，使最优策略有闭式解，从而把 RLHF 变成一个简单的分类损失。无需采样、无需调大量超参。**这是对齐训练的范式简化**，几乎瞬间取代 PPO 成为主流。

> **GRPO**：Shao et al. (DeepSeek), *DeepSeekMath: Pushing the Limits of Mathematical Reasoning* [arXiv:2402.03300](https://arxiv.org/abs/2402.03300)（2024-02-05）。PPO 的变体，去掉 value network，用组内相对优势（group-relative advantage），大幅省显存。**DeepSeek-R1 就是靠 GRPO + 可验证奖励（RLVR）实现推理能力涌现的**，这件事直接引爆了 2025 年的推理模型竞赛。

> **Self-Rewarding**：Yuan et al. (Meta), *Self-Rewarding Language Models* [arXiv:2401.10020](https://arxiv.org/abs/2401.10020)（ICML 2024）。用 LLM-as-Judge 让模型自己给自己打分，迭代 DPO。三代迭代后，Llama-2-70B 在 AlpacaEval 2.0 上超越 Claude 2、Gemini Pro、GPT-4 0613。这暗示了「超越人类反馈」的可能路径——要训练超人智能，反馈信号本身也必须超人。

**RLVR + Test-Time Compute**：o1 (OpenAI) 和 R1 (DeepSeek) 开启了一个全新的维度——**推理时计算（test-time compute）成为可 scale 的维度**。模型在回答前可以「思考」成千上万 token。这本质上是把「算力」从一个训练维度变成了训练+推理两个维度。这是 Transformer 架构本身不变的情况下，**最大的一次范式扩张**。

#### F. 多模态架构

- **Native Multimodal（早期融合）**：GPT-4o、Gemini——所有模态从一开始就在同一个网络里，共享 embedding 空间。
- **Q-Former / Cross-Attention（后期融合）**：BLIP-2 用一个小型 transformer 桥接冻结的视觉编码器和冻结的 LLM。
- **Any-to-Any**：Meta 的 Chameleon、社区版 Anole，所有模态（文本、图像、代码）tokenize 后用统一的 next-token 预测。

多模态架构的演化方向是「tokenize 一切」——把图像、音频、视频、动作全部离散化成 token，然后用统一的 Transformer 处理。这进一步巩固了 Transformer 的地位，但也提出了新的架构问题（不同模态的最优 tokenization 不同）。

#### G. VLA / World Model 新领域（与第 01 卷呼应）

具身智能（embodied AI）催生了一类全新架构——**Vision-Language-Action (VLA) 模型**：

- **π0**（Physical Intelligence）：用 flow matching 输出连续动作（不是离散 token）。
- **Cosmos Policy / DreamZero / GR00T N1**（NVIDIA）：基于 world model 的机器人策略。
- **π0.5 / Helix**：把 VLA 推向通用机器人。

VLA 的架构创新点在于「动作输出」——传统 LLM 输出离散 token，机器人需要连续、高频、多维的动作。flow matching、diffusion policy、action chunking 都是为这个问题设计的新原语。这是 Transformer 架构在「输出端」的根本扩展，与第 01 卷的世界模型专题紧密关联。

### 1.3 真实判断：创新没有停滞，但形式迁移了

把上面七条合起来看，**2022–2026 年是自 2017 年以来架构创新最密集的时期**。停滞论者犯的错误是把「范式转移（paradigm shift）频率下降」误读为「创新停滞」。

真相是：**创新的形式从「范式转移」转向了「组合创新 + 工程优化」**。这有一个绝佳的历史类比：

> **CPU 1995–2005 的类比**：1995–2000 年，CPU 主频从 100MHz 飙到 1GHz，那是「范式转移」时代（每个工艺节点都带来数量级提升）。2005 年后，主频提升撞上功耗墙（ Dennard scaling 失效），单核频率停滞在 ~4GHz。于是有人说「CPU 创新停滞了」。但实际上，CPU 进入了一个**更密集但形式不同的创新期**：多核、超线程、SIMD/AVX 向量指令、多级 cache 层级、乱序执行、分支预测、NUMA、3D 堆叠……创新一点没少，只是从「单点突破」变成了「系统协同」。

AI 架构正处在完全相同的转折点。Transformer 像 CPU 的「单核」——它本身已经成熟，但围绕它的「多核」（MoE 多专家并行）、「向量指令」（FlashAttention 的 tiling）、「cache 层级」（KV cache 管理）、「乱序执行」（speculative decoding）、「多芯片互联」（Ring Attention）正在爆炸式发展。

**所以，命题一的修正版是**：架构创新没有停滞，反而处于高度活跃期；创新形式从「换骨干」转向「在 Transformer 之上做组合创新与工程优化」，同时非 Transformer 骨干（Mamba/RWKV/RetNet）正在快速逼近，混合架构（Jamba）已登场。**这对研究者意味着：再问「下一个 Transformer 在哪」可能是错的问题；正确的问题可能是「在这个生态里，哪个组合位最值得攻」。**

---

## 二、前提 2：硬件瓶颈的真相（核心深化章节）

「硬件是瓶颈」这句正确但模糊的话，需要被拆成两个完全不同的场景：**推理**和**训练**。两者瓶颈性质截然相反，混为一谈是大多数错误判断的根源。

### 2.1 分场景分析

#### 推理阶段：memory-bound 是主敌

LLM 推理（尤其是自回归解码）的根本瓶颈是**内存带宽**，而非算力。

**为什么？** 自回归解码时，每生成一个 token，都要把整个模型权重和不断增长的 KV cache 从 HBM（显存）搬到计算单元。如果 batch size 很小（比如 1），生成本身的 FLOPs 极少，但搬运的字节数几乎是模型大小。算术强度（arithmetic intensity）极低。

经验数据：**LLM 推理约 70% 的时间花在搬权重上，只有约 30% 用于实际计算**。这就是为什么推理是 memory-bound。

**Roofline 模型完整推导**：

定义**算术强度** $I = \frac{\text{FLOPs}}{\text{Bytes}}$（每搬运一字节做多少次浮点运算）。一个 kernel 的性能上限由 Roofline 决定：

$$
\text{Attainable FLOPs/s} = \min\left(\pi_{\text{peak}},\ I \cdot \beta_{\text{peak}}\right)
$$

其中 $\pi_{\text{peak}}$ 是峰值算力（FLOPs/s），$\beta_{\text{peak}}$ 是峰值带宽（Bytes/s）。**转折点（ridge point）的算术强度**为：

$$
I^* = \frac{\pi_{\text{peak}}}{\beta_{\text{peak}}}
$$

以 H100 SXM 为例（业界公开规格）：
- BF16 峰值 $\pi \approx 989$ TFLOPS
- HBM3 带宽 $\beta \approx 3.35$ TB/s
- 转折点 $I^* = \frac{989 \times 10^{12}}{3.35 \times 10^{12}} \approx 295$ FLOPs/Byte

也就是说，**一个 kernel 的算术强度低于 295 时，它是 memory-bound**——算力被白白浪费，瓶颈在搬运。只有算术强度高于 295，才进入 compute-bound 区。

对自回归解码生成单个 token：FLOPs 主要是一次前向的矩阵-向量乘（约 $2N$，$N$ 是激活参数量），字节搬运约 $2N$ bytes（权重 + KV cache 读取）。算术强度 $I \approx 1$ FLOPs/Byte ——**远低于 295，深度 memory-bound**。

这就是为什么：
- **推理优化主线是「降字节搬运」**：MLA 压缩 KV cache（减 93.3%）、量化（FP8/INT4 减权重字节）、KV cache 量化、PagedAttention（碎片管理）、speculative decoding（用小模型草拟、大模型批量验证，提升有效 batch）。
- **专用推理芯片（Groq LPU、Cerebras WSE、Etched.ai Sohu）的核心卖点都是「带宽」**：Groq 用 SRAM 替代 HBM 换取 ~80TB/s 片上带宽；Cerebras 把整个模型放在一片晶圆级 SRAM 上。

**DRAM vs SRAM 的 100× 差距**：HBM 带宽 ~3–8 TB/s，而片上 SRAM 带宽 ~10–80 TB/s，且延迟低 1–2 个数量级。这就是 FlashAttention 的动机——把 attention 的中间结果（softmax 分母、max）尽量留在 SRAM 里，避免回写 HBM。

#### 训练阶段：compute-bound（但有三大子墙）

训练与推理相反，**整体是 compute-bound**。原因：

1. **大 batch**：训练用大 batch（几千到几万 token），矩阵乘是大矩阵-大矩阵乘（GEMM），算术强度高。
2. **前向 + 反向**：反向传播约是 2× 前向 FLOPs（激活对权重求导 + 激活对激活求导），整体训练约 $6N$ FLOPs/token（$N$ = 非嵌入参数量）的著名经验公式。
3. **GEMM 占大头**：FFN 的两个大矩阵乘（尤其 MoE 后 FFN 巨大）+ QKV projection，这些是高算术强度的 GEMM，操作强度远超转折点。

**但「训练是 compute-bound」这句话过于笼统**。训练的真实瓶颈分三个层次（三堵子墙），下面详述。这是本章的核心深化部分。

### 2.2 训练计算墙深度解析（重点章节）

#### A. 为什么训练整体是 compute-bound，但局部有 memory-bound

虽然整体 compute-bound，训练里仍有局部 kernel 是 memory-bound：
- **标准 attention 实现**：softmax 中间结果反复读写 HBM，算术强度低于转折点 → memory-bound。这正是 FlashAttention 要解决的问题。
- **LayerNorm、激活函数、dropout**：这些逐元素操作 FLOPs 少但要把整个张量搬进搬出，操作强度低。
- **小 batch 下的 MoE router、通信**：也有 memory/通信 bound 风险。

但把这些加起来，**GEMM 仍占训练总 FLOPs 的 70%+ 且是 compute-bound**，所以整体训练是 compute-bound。优化的重点是把那些「拖后腿」的 memory-bound kernel 也加速（fusion、kernel 优化），让它们不拖累 GEMM 主干。

#### B. 训练的三层计算墙

##### 层 1：总算力墙（Scaling Laws 决定）

> **Kaplan Scaling Laws**：Kaplan et al. (OpenAI), *Scaling Laws for Neural Language Models* [arXiv:2001.08361](https://arxiv.org/abs/2001.08361)（2020-01-23）。核心发现：测试 loss 与参数量 $N$、数据量 $D$、计算量 $C$ 呈幂律关系，跨度 7 个数量级。$L(C) \propto C^{-0.05}$（计算量的指数约 0.05，意味着 loss 每降一点需要约 $6\times$ 的计算）。

> **Chinchilla 修正**：Hoffmann et al. (DeepMind), *Training Compute-Optimal Large Language Models* [arXiv:2203.15556](https://arxiv.org/abs/2203.15556)（2022-03-29）。**关键修正**：Kaplan 高估了最优模型大小、低估了最优数据量。Chinchilla 法则是「**模型大小和数据量应等比例 scale**」——每翻倍模型参数，训练 token 也应翻倍。最优 token 数 $\approx 20 \times$ 参数量。

这两条 scaling law 决定了「总算力墙」的形状：**要训练更强的模型，总算力需求是指数增长的**。具体数字（业界估计）：

| 模型 | 参数量 | 训练 token | 训练算力 | 成本（业界估计）|
|---|---|---|---|---|
| GPT-3 | 175B | 300B | ~3.1e23 FLOPs | ~$5M |
| GPT-4 | ~1.8T (MoE) | ~13T | ~2.1e25 FLOPs | ~$63–100M |
| Llama 3.1 405B | 405B | 15T | ~2.5e25 FLOPs (16K H100 × 54 天) | ~$60–80M |
| DeepSeek V3 | 671B/37B (MoE) | 14.8T | 2.788M H800-hours | ~$5.6M |
| GPT-5（业界传闻）| 多万亿 MoE | ~30T+ | ~2e26 FLOPs | ~$1B+ |

**层 1 的真相**：Scaling Laws 没有失效。每提升一代模型，总算力需求大致 ×5–10。这条墙**只能靠砸钱+砸卡**突破，没有捷径——除非算法/架构创新让「同等性能所需算力」下降（这正是 MoE、MLA、Distillation 在做的事）。

##### 层 2：实际效率墙（MFU 30–50%）

光有总算力不够，**实际能利用多少**是另一回事。这里的关键指标是 **MFU（Model FLOPs Utilization）**——实际 FLOPs / 峰值 FLOPs。

H100 BF16 峰值 ~989 TFLOPS，但训练大模型时实际 MFU 通常只有 **30–50%**。损失去哪了？

- **通信开销（30–40%）**：多卡训练要同步梯度、做 all-reduce/all-to-all，这些通信不能完全被计算覆盖。
- **显存碎片与重新分配**。
- **数据加载、预处理瓶颈**。
- **Kernel launch 开销**：小 kernel 频繁启动 CPU-GPU 同步。
- **memory-bound kernel 拖累**：attention、layernorm 等非 GEMM 部分。
- **数值稳定性开销**：loss scaling、梯度裁剪。

业界 MFU 对比（2024–2025）：

| 系统 | MFU | 关键技术 |
|---|---|---|
| GPT-4（估计）| ~35% | 闭源 |
| Llama 3.1 405B | ~40% | 3D 并行 + 通信 overlap |
| Kimi K2 | ~45% | Lightning Attention |
| **DeepSeek V3** | **~50%（业界领先）** | **FP8 + DualPipe + MLA + MoE** |

DeepSeek V3 用 2.788M H800-hours 训练出 GPT-4 级模型——以业界估计 GPT-4 的算力约 2.1e25 FLOPs、DeepSeek V3 约 2.788M H800-hours（H800 BF16 ~989 TFLOPS × 0.5 MFU × 2.788M × 3600 ≈ 5e24 有效 FLOPs），**用约 1/4 到 1/10 的总算力达到接近的性能**。这是层 2（效率墙）被突破的标志性事件。

##### 层 3：通信墙（多卡同步）

当模型大到必须分布式训练，**卡间通信**就成为硬约束。Llama 3.1 405B 训练在 16,000 张 H100 上进行，**每一步训练的梯度同步通信量是 PB 级**。

硬件层面的通信带宽：
- **NVLink/NVSwitch（节点内）**：~900 GB/s（H100）/ ~1.8 TB/s（B200）
- **InfiniBand（节点间）**：400 Gb/s = 50 GB/s（NDR）/ 800 Gb/s（XDR）
- **以太网（RoCE）**：400 Gb/s，成本更低

**通信墙的本质**：随着 GPU 数量增加，all-reduce 的通信时间随 $\log N$ 增长（ring topology），但当 N 上万时，通信时间占比不可忽略。更重要的是，**MoE 的 expert-parallel 引入了 all-to-all 通信**，比 all-reduce 更昂贵。

这就是为什么 **3D/4D 并行**（DP + TP + PP + EP + SP）如此重要——把通信按拓扑摊薄到多个维度。

#### C. 突破训练计算墙的 6 大技术族

下面是当前 SOTA 训练系统采用的 6 类核心技术，每一类都在直接攻击某一层计算墙：

**技术 1：混合精度训练**——攻击层 2（效率墙）
- FP16（2017）→ BF16（2020，Google TPU）→ **FP8（2024，主流化）**。
- FP8 把权重的字节减半（vs BF16），等效带宽与算力翻倍。DeepSeek V3 用 FP8 训练是业界大规模验证 FP8 可行性的里程碑（论文 [arXiv:2412.19437](https://arxiv.org/abs/2412.19437)）。
- 更前沿：MXFP4、INT4、log-domain（LogNav）正在研究中。

**技术 2：分布式训练（多维并行）**——攻击层 3（通信墙）
- **DP（Data Parallel）**：每卡完整模型，分数据。
- **TP（Tensor Parallel）**：单层矩阵切到多卡（Megatron-LM）。
- **PP（Pipeline Parallel）**：不同层在不同卡，micro-batch 流水。
- **SP（Sequence Parallel）**：长序列切到多卡（与 Ring Attention 配合）。
- **EP（Expert Parallel）**：MoE 专家分布到多卡。
- **3D/4D 并行**：上述维度的组合，把通信摊到多个拓扑方向。

**技术 3：显存优化**——攻击层 2
- **Gradient Checkpointing**：前向不存激活，反向重算，用算力换显存。
- **ZeRO-1/2/3**（DeepSpeed）：把优化器状态/梯度/参数分片到多卡，ZeRO-3 可训练 1T 模型。
- **CPU/NVMe offload**：把不活跃的参数卸到 CPU/SSD。

**技术 4：通信优化**——攻击层 3
- **Gradient accumulation**：多步本地累积再同步，减少同步次数。
- **Communication overlap**：把通信与计算重叠（关键技术）。
- **DualPipe / ZeroBubble**：双向流水线 + 零气泡调度，最大化 overlap。DeepSeek V3 的 DualPipe 是代表作。
- **Topology-aware placement**：按物理拓扑分配并行维度。

**技术 5：算法-硬件协同（架构级）**——同时攻击三层墙
- **MoE**：参数大但激活小，等效节省 5–20× 训练算力。
- **MLA**：减 KV cache、减 attention 计算。
- **Lightning Attention**：线性 attention，长上下文恒速。

**技术 6：高效 Kernel（这是 TileLang 的主场）**——攻击层 2
- **FlashAttention 1/2/3**：把 attention 从 memory-bound 拉到接近 compute-bound。
- **Triton / CUTLASS / TileLang**：高层 DSL 生成接近手写的高效 kernel。
- **Mojo**：Modular 的新语言，主打 AI infra。

> **FlashAttention 系列（最经典的「单点突破」案例）**：
> - **FA-1**：Dao et al., *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness* [arXiv:2205.14135](https://arxiv.org/abs/2205.14135)（NeurIPS 2022）。IO-aware 精确 attention，用 tiling 减少 HBM↔SRAM 读写，理论上证明对一定 SRAM 大小是最优的。
> - **FA-2**：Dao, *FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning* [arXiv:2307.08691](https://arxiv.org/abs/2307.08691)（2023-07）。优化线程块/ warp 间的 work partitioning，A100 达 225 TFLOPs/s（72% MFU）。
> - **FA-3**：Dao, Shah et al., *FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-Precision* [arXiv:2407.08608](https://arxiv.org/abs/2407.08608)（2024-07）。针对 Hopper 架构用 warp-specialization + TMA 异步 + FP8，H100 上 FP16 达 740 TFLOPs/s（75% utilization），FP8 达 1.2 PFLOPs/s。

FlashAttention 的意义不只是「attention 变快」——它**证明了「IO-aware kernel 设计」能带来的收益是数量级的**。这一个工作让全世界大模型的训练吞吐普涨 2–4×。**这是「infra 红利 > 算法红利」的最有力证据**。

#### D. 训练计算墙的真实状态（2026）

把好消息和坏消息都列清楚：

**好消息**：
- DeepSeek V3 用 ~1/10 算力做出 GPT-4 级模型，证明**计算墙正在被架构 + infra 创新快速突破**。
- FlashAttention、DualPipe、MLA、MoE 等技术已让 MFU 从 ~30% 提到 ~50%。
- FP8 训练已大规模验证，下一步 MXFP4/INT4 会再提一档。

**坏消息**：
- **绝对算力需求仍在指数增长**：GPT-5 级模型业界传闻 ~$1B 训练成本。Scaling Laws 没有失效，每代模型仍需 ×5–10 算力。
- **地缘政治卡脖子**：H800/H20 出口限制，中国大陆可用算力被人为压缩（这也反向催生了 DeepSeek 这类极致效率创新）。
- **能耗与碳排放成为新瓶颈**：10 万卡集群 ~10 MW 持续 6 个月，相当于一个中型电厂。能源正在成为继算力、带宽之后的「第四墙」。
- **数据墙**：互联网高质量文本即将耗尽，合成数据、多模态数据成为新前线。

**综合判断**：训练计算墙**不会在短期内被一击突破**，而是被「架构创新 + infra 创新 + 新硬件」三方合力持续侵蚀。这是一场长期消耗战，不是闪电战。

---

## 三、前提 3：TileLang 类思路是不是 AI infra 最重要的方向？

你（用户）在命题中判断「TileLang 类思路是 AI infra 最重要的方向之一」。下面用实证和对比工作来裁决这个判断——结论是：**完全正确，而且这个判断的价值被严重低估**。

### 3.1 TileLang 实证调研

TileLang 是一个**面向异构 AI 加速器的高性能 kernel DSL + 编译器**，核心定位是「让算法专家不用懂底层硬件也能写出媲美手写汇编的 kernel」。基于其公开 README 与文档，关键技术特征包括：

- **极简实现**：约 80 行 Python 就能实现 FlashMLA（DeepSeek MLA 的高效 kernel），性能媲美工程师手写的 assembly。
- **跨硬件**：支持 NVIDIA H100（TMA/WGMMA）、AMD MI300X、Apple Metal、华为 Ascend（国产 NPU）。
- **形式化集成**：集成 Z3 theorem prover 做 SMT 验证——这是把形式化方法引入 kernel 生成的稀有尝试。
- **2:4 sparse tensor core 支持**：直接吃 NVIDIA Ampere+ 的稀疏硬件。
- **tile-level 抽象**：用户在「tile（块）」层级描述计算，编译器自动处理内存层级、同步、数据搬运。

### 3.2 类似工作（编译器 DSL 谱系）

把 TileLang 放进 AI 编译器的演化谱系里看，它属于「**tile-level DSL**」这一支：

| 系统 | 出品方 | 核心思想 | 出处 |
|---|---|---|---|
| **TVM** | 陈天奇等 (UW/OctoML) | 图级 + 算子级优化，自动调度 | [arXiv:1802.04799](https://arxiv.org/abs/1802.04799) (OSDI 2018) |
| **MLIR** | Chris Lattner et al. (Google/LLVM) | 可扩展的多级中间表示 | [arXiv:2002.11054](https://arxiv.org/abs/2002.11054) (CGO 2021) |
| **Triton** | OpenAI | Python 类 DSL，block-level 编程 | Philippe Tillet et al. (MAPL 2019) |
| **CuTe DSL** | NVIDIA | 基于 C++ 的 tile 抽象（CUTLASS 之上）| NVIDIA 官方 |
| **Exo** | Ragan-Kelley 组 (MIT/Stanford) | Exocompilation——用户可定制调度 | Ikarashi, Reinking, Bernstein, Ragan-Kelley, OOPSLA 2023 |
| **Halide** | Ragan-Kelley et al. (MIT/Adobe) | 算法与调度解耦（图像处理起源）| Ragan-Kelley et al., PLDI 2013 |
| **Mojo** | Modular (Chris Lattner) | AI 原生语言，超集 Python | Modular 官方 |
| **TileLang** | 社区/学术 | tile-level Python DSL + 形式化验证 | 项目文档 |

这条谱系的共同主题是：**让人类在「块/tile」这个甜点抽象层级上思考，让编译器处理底层细节**。这背后有一个深刻的认知科学原理——**人脑不擅长同时管理「算法正确性」和「内存层级/同步细节」两件事**，把它们解耦能让两边都做到极致。

> **TVM**：Chen et al., *TVM: An Automated End-to-End Compiler for Deep Learning* [arXiv:1802.04799](https://arxiv.org/abs/1802.04799)（OSDI 2018）。第一个系统性地把「图级优化 + 算子级优化 + 学习式 cost model 自动调度」整合的深度学习编译器，支持从手机 CPU 到 FPGA 的多后端。

> **MLIR**：Lattner, Amini, Bondhugula et al., *MLIR: Scaling Compiler Infrastructure for Domain Specific Computation* [arXiv:2002.11054](https://arxiv.org/abs/2002.11054)（CGO 2021）。Lattner（LLVM 之父）的下一个大作。MLIR 不是单一编译器，而是一个**可扩展的编译器基础设施**——用统一的「dialect」机制让不同抽象层级（tensor、linalg、affine、gpu、vector……）能互译。今天 Triton、IREE、StableHLO、JAX/XLA 的底层都跑在 MLIR 上。

> **Exo**：Ikarashi, Reinking, Bernstein, Ragan-Kelley, *Exocompilation for Productive High-Performance Hardware Querying*, OOPSLA 2023 (PACMPL)。提出「exocompilation」概念——把调度决策外化给用户，编译器提供「硬件查询」原语让用户精确控制。这是对「全自动调度」路线的反叛，主张「人在 loop 里」。

> **Halide**：Ragan-Kelley et al., *Decoupling Algorithmic Choices from Detailed Scheduling in the Halide Image Processing Language*, PLDI 2013（综述见 CACM 2018）。**算法与调度解耦**的奠基论文。同一个算法描述可以配多种 schedule，分别针对不同硬件。这个思想直接启发了后来所有 tile-DSL。

### 3.3 TileLang 思路的本质

把这一谱系抽象一下，TileLang 类思路的**本质**是三件事的融合：

1. **编译器思维**：把高层算法分解为硬件友好的子任务，自动处理内存层级、同步、数据搬运。
2. **硬件感知**：DSL 暴露 tile、warp、shared memory 这些硬件概念，但又不过度暴露（甜点抽象层）。
3. **算法结构利用**：利用算法的已知结构（如 attention 的 softmax 可分块、conv 的 im2col）生成特化代码。

这三者融合的价值在于：**让算法专家与硬件专家解耦**。算法专家写 tile 级 Python（关心数学正确性），编译器+硬件专家关心寄存器分配、bank conflict、async copy。这是一种**社会分工的优化**，而不仅仅是技术优化。

更深一层：当前 AI 最大的瓶颈不是「算法不够聪明」，而是「**已有的算法无法高效跑在已有的硬件上**」。GPU 的理论峰值利用率只有 30–50%，剩下的 50–70% 都被 kernel 写得不够好、调度不够优、通信没重叠给浪费了。**这 50–70% 的「浪费空间」就是 infra 创新的红利池**，而且这个池子比「换一个新架构」的红利池大得多、确定性高得多。

### 3.4 真实判断

> **命题三裁决：完全正确。**

TileLang 类思路（tile-level DSL + 编译器 + 硬件感知）是当前 AI infra **最有确定性回报的方向**。理由：

1. **红利池巨大**：MFU 从 50% 到 80% 的空间，相当于免费多出 60% 的算力。
2. **确定性高**：不像算法创新需要灵感，infra 优化的收益是可预测的（Roofline 模型告诉你理论上限）。
3. **跨硬件价值**：每一代新硬件（Hopper→Blackwell→Rubin→国产 NPU）都需要重写 kernel，DSL 类工具的需求是持续的。
4. **国产化刚需**：美国出口管制下，华为 Ascend、燧原、寒武纪等国产 NPU 急需生态，tile DSL 是构建生态的关键层。
5. **人才稀缺**：同时懂算法和硬件的人极少，这个交叉位置是供需最失衡的。

**关键洞察**：当前 AI 最大红利是 **infra 创新**（确定性、大池子、人才稀缺），而非算法创新（需要灵感、竞争激烈、红利递减）。**这是对你「应用数学研究型工程师」定位最重要的一个判断。**

---

## 四、跨学科创新提案（6 大方向）

下面是本章的创造性部分。基于前三章的分析，提出 6 个跨学科创新方向，每个方向都尝试**把 AI infra 与另一个学科交叉**，找到少有人走的路。这些不是空想——每个都对应真实的研究前沿和工业需求。

### 创新 1：编译器 + 算法联合设计（Compiler-Algorithm Co-Design）

**核心思想**：传统范式是「算法专家设计算法 → 编译器负责实现」。但这两者本应联合优化。一个算法的数学等价变体可能有几百个，它们的硬件友好性天差地别。**让编译器能自动探索「算法的等价变体 + 对应的最优 schedule」**，而不是只优化固定算法的实现。

**具体子方向**：

1. **硬件感知的算法变体生成**：给定一个数学操作（如 attention、convolution、matmul），自动生成多个数学等价但计算顺序不同的变体，每个变体配最优 schedule，用 cost model 选最好的。例如 FlashAttention 本质上是「attention 的一个 tile 友好变体 + 对应 schedule」——这个组合本可以由编译器自动发现。

2. **Symbolic Compilation（符号编译）**：用 Z3、Lean、Coq 等定理证明器做 kernel 等价性验证。给定两个 kernel（一个参考实现、一个优化实现），自动证明它们在所有输入上等价。TileLang 已集成 Z3，但还有大量空间——比如用 Lean 做更复杂的浮点数值等价证明（含误差界）。

3. **Differentiable Compilation（可微编译）**：把调度参数（tile size、unroll factor、pipeline depth）当作可优化变量，用梯度下降自动调参。AutoTVM/Ansor 是离散搜索版，可微版是前沿。

4. **Auto-scheduling for emerging hardware**：CIM（存内计算）、光计算（photonic）、类脑（neuromorphic）、sparse-first 架构——这些新硬件没有成熟的库，DSL + 自动调度是唯一可行的路径。

**数学结构支撑**：这个方向天然需要形式化方法（SMT、类型论）、图论（调度依赖图）、优化（组合优化、可微优化）的交叉。**对你的「数学专家」目标是直接入口**——把抽象代数/范畴论用在编译器 pass 的正确性证明上，是一个极有学术深度且工业急需的方向。

**研究选题示例**：用 Lean 4 形式化验证 Triton/TileLang 生成的 kernel 与参考 PyTorch 实现的数值等价性（含 FP8 误差界）。这是 NOFA（neural operator formal assurance）方向，目前几乎没有公开工作。

### 创新 2：OS 级 AI 调度（OS for AI Workloads）

**核心思想**：当前 AI 推理服务（vLLM、SGLang、TensorRT-LLM）都在**用户态**做调度——KV cache 管理、batch 调度、speculative decoding。但这些本质上是**操作系统该做的事**（内存管理、进程调度、I/O 调度）。把 AI workload 上升到 OS 一等公民，能带来根本性优化。

**具体子方向**：

1. **KV cache 的 OS 原生管理**：当前 vLLM 的 PagedAttention 是在用户态模拟分页——把 KV cache 切成 block，用页表管理。但**真正的 OS 分页机制（虚拟内存、swap、NUMA）本可以原生支持 KV cache**。设计一个 KV-cache-aware 的内核内存子系统，让 KV cache 的分配/迁移/换出由 OS 统一管理，能避免用户态模拟的开销，还能跨进程共享 KV cache（多副本服务）。

2. **Speculative scheduling**：speculative decoding 用小模型预测大模型输出，本质上是「**预测性执行**」——与 CPU 的分支预测是同构问题。把 speculative decoding 上升到 OS 调度器层级，做预测性资源分配。

3. **NUMA-aware inference**：多 socket 服务器上，跨 NUMA 节点的内存访问慢 2–4×。OS 调度器本可以原生感知 NUMA 拓扑，把推理请求路由到 KV cache 所在的 NUMA 节点。当前用户态框架基本忽略这点。

4. **AI workload cgroups**：把 LLM 推理作为一种 workload class，像 `cpu.shares`、`memory.limit` 一样支持 `kv_cache.quota`、`tokens_per_second` 原生控制。

**学科交叉**：操作系统 + 分布式系统 + 体系结构。**这是一个被深度学习社区严重低估的方向**——大多数 AI 研究者不懂 OS，大多数 OS 研究者不关心 LLM。这个交叉点的人才极度稀缺，且一旦做出成果（比如一个 KV-cache-native 的内核模块），工业落地极快。

**研究选题示例**：设计并实现一个 Linux 内核模块 `kvmem`，把 KV cache 作为一类内存对象纳入 slab allocator 管理，支持跨进程共享、压缩、换出到 NVMe。benchmark 显示对多副本推理服务的吞吐提升。

### 创新 3：硬件-算法协同设计（Hardware-Algorithm Co-Design）

**核心思想**：当前是「算法适应通用硬件（GPU）」。但通用硬件对每类算法都有浪费——GPU 为图形/通用计算设计，跑 attention 时一半晶体管闲置。**为新算法范式定制硬件**能带来数量级提升。这正是当前一批 AI 芯片创业公司的逻辑。

**代表案例**：

| 公司 | 路线 | 核心创新 | 状态 |
|---|---|---|---|
| **Cerebras** | 晶圆级 WSE | 整个模型放一片晶圆，无片间通信 | CS-3 商用 |
| **Groq** | LPU + SRAM | 片上 SRAM ~80TB/s 带宽，确定性时延 | 推理快但显存小 |
| **SambaNova** | RDU | 数据流架构，可重构 | 企业市场 |
| **Tenstorrent** | RISC-V + AI | Jim Keller 领导，小芯片互联 | 量产中 |
| **Etched.ai (Sohu)** | Sohu ASIC | **Transformer 硬连线** ASIC | 2024 融资，宣称比 H100 快 20× |

**前沿子方向**（更激进的协同设计）：

1. **Sparse-first hardware**：硬件原生支持稀疏（不只是 2:4 结构化稀疏，而是动态稀疏）。MoE 天然稀疏，但当前 GPU 按稠密设计，稀疏加速比有限。
2. **Variable precision unit**：硬件支持任意 bit-width（1/2/4/8/16 混合）运算，让模型每一层用最优精度。
3. **In-memory attention**：在 SRAM/HBM 内部直接做 attention 计算，避免数据搬运（与 CIM 结合）。
4. **Photonic interconnect**：用光互连替代电互连，带宽提升 10–100×，解决通信墙。

**学科交叉**：体系结构 + VLSI + 光学 + 算法。Etched.ai 的 Sohu 是最极端的例子——它把 Transformer 的 attention + FFN 直接做成 ASIC 硬连线，宣称单卡推理比 H100 快 20×。**代价是只能跑 Transformer**（如果 Transformer 被替代，硬件作废）。这是一个高风险高回报的押注。

**研究选题示例**：设计一个「MoE-native」加速器微架构——router 直接在硬件里做 top-k 选择，expert 计算单元按稀疏激活配置。用体系结构模拟器（gem5/SCALE-Sim）评估 vs GPU 的加速比。

### 创新 4：可计算理论视角的新算法（Computational Complexity → New Algorithms）

**核心思想**：很多 AI 工程师不知道当前算法离理论下界有多远。**复杂度理论能告诉我们「算法还有多少改进空间」**，这个空间就是创新红利。

**已知下界与现状**：

1. **矩阵乘法**：当前最好上界 $O(n^{2.371552})$（Williams-Xu-Zhou 2024，Duan-Wu-R Zhou 系列），理论下界猜测是 $O(n^{2}\,\mathrm{polylog})$。**也就是说，matmul 还有 $O(n^{0.37})$ 的理论改进空间**——这是一个数量级。如果有人找到接近下界的实用算法，整个深度学习算力需求会暴跌。

2. **Attention 复杂度**：标准 attention 是 $O(n^2 d)$。线性 attention（Mamba、Hyena、Lightning）已做到 $O(n d^2)$ 或 $O(n d)$。**理论下界是多少？** 这是一个开放问题，与「序列建模的最小信息复杂度」相关。

3. **学习理论的不可解性**：Kearns-Valiant（1994）证明某些概念类（如 parity 函数）在 PAC 模型下多项式不可学。这说明**存在「原则上不可学」的问题**，再大的模型也学不会。当前 LLM 在某些推理任务上的失败，可能不全是「数据不够」，而是触及了计算复杂性墙。

4. **AlphaTensor 启示**：DeepMind 的 AlphaTensor（Nature 2022）用 RL 发现了更快的矩阵乘法算法（在 $4\times4$ 上找到 47 步 vs 之前 49 步的分解）。**这说明「用 AI 发现新算法」本身是一个可 scale 的研究方向**——把算法发现形式化为游戏，用 RL 搜索。这把「算法创新」从「人类灵感」变成了「机器搜索」，潜力巨大。

**学科交叉**：计算复杂性 + 代数（张量分解）+ 强化学习。**这是「数学专家」目标最纯粹的研究出口**——研究 attention/matmul/conv 的代数结构与下界，是从数学结构反推新算法的范式。

**研究选题示例**：用 AlphaTensor 风格的 RL 搜索「attention 的等价分解」——寻找比 $QK^T V$ 更少乘法的等价计算序列。这是一个明确的开放问题，且即便只在小规模（如 head_dim=64）找到改进，也能直接转化为 kernel 加速。

### 创新 5：认知科学启发的新架构（Cognitive-Science-Inspired Architectures）

**核心思想**：Transformer 是一个「通用序列映射器」，但人脑不是这么工作的。**人脑有大量 Transformer 缺失的机制**——预测编码、稀疏分布式记忆、全局工作空间、海马回放。这些机制对应着不同的计算图，可能启发更高效的架构。

**具体机制**：

1. **Predictive Coding（预测编码）**：Rao & Ballard (1999)。大脑不是被动处理输入，而是**不断预测输入、只处理预测误差（residual）**。这天然是一种稀疏计算——大部分信号被预测对了，只有误差需要传播。这与 ResNet 的残差、与下一帧预测的世界模型有精神共鸣。一个严格基于 predictive coding 的 LLM 架构可能用更少计算达到同等性能，因为「大部分 token 是可预测的」。

2. **Sparse Distributed Memory（SDM）**：Kanerva (1988)。人脑记忆是「稀疏分布式」的——一个概念分散存在很多神经元，一个神经元参与很多概念。这本质上是 MoE 的生物学版本，但 SDM 的地址机制（基于汉明球的稀疏寻址）比 MoE 的 router 更优雅。**SDM-inspired 的寻址机制可能解决 MoE 的 load imbalance 问题**。

3. **Global Workspace Theory（全局工作空间）**：Baars (1988)。大脑有一个「全局工作空间」（类似广播总线），各专用模块竞争访问它，胜者广播给所有模块。这启发了 **模块化 AI 架构**——多个专用 agent 共享一个有限带宽的工作记忆，竞争广播。这与 Mixture-of-Agents、与多智能体系统直接相关。

4. **Hippocampal Replay（海马回放）**：人脑在睡眠/休息时「回放」白天的经验，强化记忆、提取规律。这对应 **offline reinforcement learning + experience replay**，但更激进——回放会「重新组合」经验生成「想象」的场景。这启发了一种训练范式：模型在推理间隙「做梦」，生成合成数据自我训练。

**学科交叉**：神经科学 + 认知科学 + 深度学习。**这是一个高风险高回报的方向**——生物启发的架构大多没在工程上胜出（Spiking Neural Network 至今没大规模成功），但一旦某个机制被正确工程化，可能打开新范式。Predictive Coding 和 Global Workspace 是目前最有希望的候选。

**研究选题示例**：设计一个「Predictive Coding Transformer」——每一层预测下一层的输出，只传播预测误差。在小规模（GPT-2 124M）上验证是否能用更少 FLOPs 达到同等 loss。

### 创新 6：数学结构的利用（Exploiting Mathematical Structure）

**核心思想**：当前深度学习**几乎完全忽略了数据的数学结构**——对称性、等变性、几何、代数结构。Geometric Deep Learning（Bronstein et al.）已经证明，把这些结构显式编码进网络能带来巨大的样本效率提升。但这一思想在 LLM 上几乎没人系统做过。

**具体子方向**：

1. **Equivariant networks for LLM（等变网络用于 LLM）**：文本序列有置换结构（句子内部、文档内部）、层级结构（句法树）。当前 LLM 完全用位置编码（RoPE）硬编码位置，**忽略了语言的置换等变性**（「猫追狗」和「狗追猫」的对称性）。设计一个 permutation-equivariant 的语言模型，可能用更少数据学到语法结构。这是一个学术空白。

2. **Tensor decomposition（张量分解）压缩**：权重矩阵 $W$ 可以分解为 $W \approx U \Sigma V^T$（SVD）或更一般的 CP/Tucker 分解。低秩分解（LoRA 用了 rank-$r$ 近似）能极大压缩模型。**但更深的问题是：训练时直接参数化在低秩流形上，而非训练完再压缩**——这能从源头获得压缩友好的模型。

3. **Attention 的代数结构**：$QK^T$ 是一个双线性型，softmax 是一个非线性，整体是「双线性 + 逐行指数 + 归一化」。这个组合的代数性质（结合律、分配律在哪些条件下成立）几乎没人系统研究。如果发现某种「结合律」成立，attention 可以重新结合成更少乘法的等价形式。

4. **Geometric Deep Learning（几何深度学习）**：Bronstein et al. 的框架把 CNN、GNN、Transformer 都统一在「对称群上的等变函数」这个抽象下。**这个抽象尚未被充分用于设计新架构**——比如在非欧结构（双曲空间、树）上做 attention，可能更适合语言的层级性。

**学科交叉**：抽象代数（群论、表示论）+ 微分几何 + 张量分析 + 深度学习。**这是「应用数学研究型工程师」最纯粹的研究方向**——它直接调用你的目标学科（代数、几何、优化），且产出（等变 LLM、几何 attention）有清晰的工程价值。Bronstein 团队（牛津/Meta）是这个方向的旗手。

**研究选题示例**：设计一个「句法树等变 attention」——让 attention 在句法树的子树置换下等变。在 PTB 语法标注数据上验证是否比 RoPE-based attention 更快学到句法结构。

---

## 五、研究路线图（短中长期）

基于前三章的分析和六大创新方向，给出三条互补的研究路线。这三条路线不是互斥的，而是可以叠加的——短期做工程、中期做跨学科、长期做理论。

### 路线 A：工程驱动（短期 1–2 年）——「先拿到一张入场券」

**目标**：成为「能写高效 kernel 的工程师」，进入 AI infra 领域。

**学习路径**：
1. **基础**（3 个月）：CUDA 编程入门（NVIDIA 官方教程）+ GPU 体系结构（Hopper whitepaper）+ Roofline 模型实操。
2. **Triton**（2 个月）：阅读 FlashAttention Triton 实现，自己用 Triton 重写一个 attention 变体，benchmark vs PyTorch。
3. **TileLang / TVM / MLIR**（3 个月）：学 TileLang，用它实现一个新硬件（华为 Ascend）上的 kernel，对比性能。
4. **分布式训练**（3 个月）：读 Megatron-LM 源码，理解 3D 并行，在一个小集群上跑通 Llama 微调。
5. **产出**：贡献一个开源 kernel（如为某个新 attention 变体写 Triton/TileLang 实现），或一个跨硬件移植案例。

**为什么这条路**：infra 人才极度稀缺，薪资高、需求确定。即便后面转研究，这段工程经验是「入场券」——没有它，你的跨学科创新提案会被当成空想。

### 路线 B：跨学科创新（中期 2–5 年）——「找一个特色细分」

**目标**：从路线 A 的工程基础出发，选一个跨学科方向（创新的 1–6 之一），发 1–2 篇有特色的论文，建立学术身份。

**推荐组合**：
- **编译器 + 形式化方法**（创新 1 + 数学）：用 Lean/Z3 验证 kernel 等价性。这个方向**懂的人极少**，工业急需（芯片公司要验证工具），学术有深度。
- **OS + AI**（创新 2）：做 KV-cache-native 内核模块。这个方向**几乎没人做**，一旦做出来影响力大。
- **数学结构 + LLM**（创新 6）：等变 attention、张量分解训练。这个方向**最契合数学专家定位**，且 Geometric DL 社区成熟。

**里程碑**：在第 2 年投出一篇特色论文（如 MLSys、SC、ASPLOS for 系统；NeurIPS/ICLR for 算法），第 3–5 年建立「在 X 方向上最懂 Y 的人」的细分声誉。

### 路线 C：理论创新（长期 5+ 年）——「数学专家的真正出口」

**目标**：从算法下界、神经-符号、认知科学启发中找到**根本性突破**。

**候选方向**：
1. **算法下界**（创新 4）：attention/matmul 的代数下界，从数学结构反推新算法。这条路最纯数学，但最难——十年磨一剑。
2. **神经-符号融合**：把符号推理（Lean/Coq 证明器）与神经网络的模式识别结合，解决 LLM 的「概率性 vs 确定性」矛盾（详见第 04 卷 04 章）。这条路有明确工业出口（形式化数学、代码生成）。
3. **认知科学启发**（创新 5）：把 predictive coding、global workspace 工程化为新架构。这条路高风险高回报。

**为什么这是长期**：理论突破需要深厚的数学积累（你的目标学科：代数、几何、优化、信息论），而你在 2026 年数学基础是 0。路线 C 是「应用数学研究型工程师」6–8 年后的真正出口，不是现在。

**三条路线的关系**：A 是地基，B 是特色，C 是归宿。**最优策略是 A+B 并行 3–5 年，再用 B 的成果支撑 C 的理论探索。**

---

## 六、给用户的专属建议

基于你的画像——「应用数学研究型工程师」、零基础起步、每周 10–20h、目标 6–8 年到研究入门级、强偏好有趣（可视化/历史/工程落地/难题）——给出具体建议。

### 1. 最优路径：路线 A + B 结合

**前 3 个月**：掌握 TileLang / Triton（路线 A 起点）。这是「确定性最高、回报最快」的投资。具体：
- 跟 NVIDIA 官方 CUDA 教程过一遍基础。
- 读 FlashAttention-3 论文（[arXiv:2407.08608](https://arxiv.org/abs/2407.08608)）+ 源码。
- 用 TileLang 实现 DeepSeek 的 MLA kernel，benchmark vs FlashMLA。
- 在一台 H100/A100 上跑通，写一篇技术博客。

**第 4–24 个月**：转入路线 B 的「编译器 + 形式化方法」方向。具体：
- 学 Lean 4（教程：Theorem Proving in Lean 4）。
- 学形式化语义（操作语义、指称语义）。
- 第一个项目：用 Lean 证明一个简单 Triton kernel 与 PyTorch 参考实现的等价性。
- 第二个项目：扩展到 FP8 误差界的数值等价。

### 2. 研究选题建议（按优先级）

1. **用形式化方法（Z3/Lean）做 kernel 等价性验证**——这是黄金交叉点。懂编译器的人多，懂数学的人多，但两者交集且做验证的人极少。TileLang 已集成 Z3 是入口信号。
2. **设计新 attention 算法变体**——在 TileLang 上实现并 benchmark。比如把 NSA 的稀疏选择做成硬件友好的变体。
3. **跨硬件移植**——华为 Ascend + TileLang。国产化刚需，工业需求大，且 Ascend 的稀疏/向量指令与 NVIDIA 不同，本身就是研究问题。

### 3. 避坑清单

- ❌ **不要做「微调开源大模型」**：LoRA/QLoRA 微调已饱和，工程非研究，红利递减。
- ❌ **不要做「prompt engineering」**：这是工程技巧，不是研究。除非做 prompt 的形式化理论。
- ❌ **不要做「通用 AGI」**：太远、太抽象，不适合零基础起步的人。
- ❌ **不要纯做数学证明而不落地**：你的定位是「应用数学研究型工程师」，要有工程出口。
- ⚠️ **不要只跟热点**：Mamba/RWKV 已是红海。冷门交叉（编译器+形式化、OS+AI）反而机会大。

### 4. 黄金交叉点

> **编译器 + 数学/形式化方法**：少有人做，工业需求大（芯片公司、AI infra 公司急需验证工具），学术有深度（形式化语义、类型论、范畴论），且天然契合你的「数学专家」目标。这是当前供需最失衡、最适合你的交叉位。

如果只能选一件事做未来 3 年，选这个。

---

## 本章核心结论速览

| 命题 | 原始判断 | 修正后裁决 |
|---|---|---|
| 架构创新停滞 | 「模型结构停滞」 | ❌ **错误**。架构创新处于 2017 年以来最活跃期，创新形式从「换骨干」转向「组合创新+工程优化」 |
| 硬件是瓶颈 | 笼统的「硬件阻碍」 | ✅ 但需分场景：**推理 memory-bound，训练 compute-bound（含三层子墙）** |
| TileLang 是重要方向 | 「最重要的方向之一」 | ✅ **完全正确**，且被严重低估。当前 AI 最大红利是 infra 创新 |

| 方向 | 红利池 | 确定性 | 人才稀缺度 | 适合你 |
|---|---|---|---|---|
| 算法创新（新架构） | 中 | 低（需灵感） | 中 | ⚠️ 长期 |
| Infra 创新（TileLang 类） | **大（MFU 50→80%）** | **高** | **极高** | ✅ **首选** |
| 跨硬件（国产 NPU） | 大 | 高 | 高 | ✅ |
| 编译器+形式化 | 中 | 中 | **极高** | ✅ **黄金交叉** |
| 硬件协同（ASIC） | 大 | 中 | 高 | ❌ 需 VLSI 背景 |
| 数学结构（等变/几何） | 大 | 低（基础研究） | 中 | ⚠️ 长期 |

---

## 📌 进一步阅读

**架构创新（第一章）**：
- Mamba 系列：[2312.00752](https://arxiv.org/abs/2312.00752) / [2405.21060](https://arxiv.org/abs/2405.21060)
- RetNet / Hyena / Jamba / KAN：[2307.08621](https://arxiv.org/abs/2307.08621) / [2302.10866](https://arxiv.org/abs/2302.10866) / [2403.19887](https://arxiv.org/abs/2403.19887) / [2404.19756](https://arxiv.org/abs/2404.19756)
- Attention 演化：MQA [1911.02150](https://arxiv.org/abs/1911.02150) → GQA [2305.13245](https://arxiv.org/abs/2305.13245) → MLA/DeepSeek-V2 [2405.04434](https://arxiv.org/abs/2405.04434) → NSA [2502.11089](https://arxiv.org/abs/2502.11089) → Lightning Attention [2401.04658](https://arxiv.org/abs/2401.04658)
- 训练范式：DPO [2305.18290](https://arxiv.org/abs/2305.18290) / GRPO [2402.03300](https://arxiv.org/abs/2402.03300) / Self-Rewarding [2401.10020](https://arxiv.org/abs/2401.10020)
- DiT [2212.09748](https://arxiv.org/abs/2212.09748)

**硬件瓶颈（第二章）**：
- Scaling Laws：Kaplan [2001.08361](https://arxiv.org/abs/2001.08361) / Chinchilla [2203.15556](https://arxiv.org/abs/2203.15556)
- DeepSeek V3（业界领先 MFU）：[2412.19437](https://arxiv.org/abs/2412.19437)
- FlashAttention 三部曲：[2205.14135](https://arxiv.org/abs/2205.14135) / [2307.08691](https://arxiv.org/abs/2307.08691) / [2407.08608](https://arxiv.org/abs/2407.08608)
- Ring Attention [2310.01889](https://arxiv.org/abs/2310.01889)
- GPU 规格：NVIDIA H100/H200/B100/B200/Rubin 官方 whitepaper

**TileLang / 编译器（第三章）**：
- TVM [1802.04799](https://arxiv.org/abs/1802.04799) / MLIR [2002.11054](https://arxiv.org/abs/2002.11054)
- Exo（Ikarashi et al., OOPSLA 2023）/ Halide（Ragan-Kelley et al., PLDI 2013）
- TileLang 官方文档与 README

**跨学科创新（第四章）**：
- Predictive Coding：Rao & Ballard, *Nature Neuroscience* 1999
- Geometric Deep Learning：Bronstein et al., *arXiv:2104.13478*（待核实，建议查最新版）
- AlphaTensor：DeepMind, *Nature* 610:47 (2022)
- Kearns & Valiant, *Cryptography and Learning* (1994)

---

## ✍️ 思考题（7 道）

1. **架构判断题**：如果让你押注 2027 年最可能「在万亿规模上正面击败纯 Transformer」的非 Transformer 架构，你会选 Mamba-2、Jamba 式混合、还是 RetNet？用本章的证据论证你的选择，并指出每个候选最可能失败的点。

2. **Roofline 计算题**：给定一个 H100 SXM（BF16 峰值 989 TFLOPS，HBM 带宽 3.35 TB/s），一个 MoE 模型每 token 激活 37B 参数、batch size = 1 自回归解码。请计算：① 转折点算术强度；② 该场景的算术强度；③ 判断是 memory-bound 还是 compute-bound；④ 每生成一个 token，理论最短时间是多少（假设无 overhead）？

3. **MFU 追踪题**：DeepSeek V3 用 2.788M H800-hours 训练 671B/37B MoE 模型，业界估计 MFU ~50%。请反推：① 它的有效 FLOPs 总量；② 如果 MFU 提升到 70%（理论接近上限），训练时间能缩短到多少？③ 哪些技术可能让 MFU 从 50% 提到 70%？

4. **FlashAttention 反思题**：FlashAttention 把 attention 从 memory-bound 拉到接近 compute-bound。请回答：① 它具体利用了哪些 Hopper 架构特性（FA-3）？② 如果让你设计「FlashAttention-4 for Blackwell」，你会用 B200 的哪些新特性？③ FlashAttention 的思想能否推广到 FFN 层？为什么 FFN 不需要 Flash？

5. **TileLang 价值题**：TileLang 让算法专家不用懂硬件就能写出高效 kernel。请论证：① 这个「解耦」的社会价值（让多少原本写不了高效代码的人能写）；② 它的局限（什么样的 kernel 仍必须手写）；③ 如果你是一个国产 NPU 公司（如华为/燧原）的 infra 负责人，你会如何用 TileLang 构建生态？

6. **跨学科选题题**：在六大创新方向里，选一个你认为「最被低估但最有潜力」的，写一份 1 页的研究提案（问题陈述、核心创新、预期成果、所需学科背景、2 年里程碑）。要求：必须明确这个方向**为什么别人没做**以及**你能做**。

7. **个人路线题**：基于你的画像（零基础、每周 10–20h、6–8 年到研究入门级、数学专家目标），用本章的三条路线设计你未来 24 个月的具体计划。要求：① 每个季度一个可验证的里程碑；② 明确「放弃什么」（至少列出 3 件不做的事）；③ 设计一个「6 个月自检点」，如果未达标则调整方向。

---

<!-- delegate 直接写入，2026-07-20 -->
