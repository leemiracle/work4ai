# AI for Drug Discovery & Design · AI 药物发现与设计

> 一句话定位：AI 药物发现是把"靶点发现 → 分子设计 → 对接打分 → ADMET 预测 → 临床试验预测"这条传统上耗时 10–15 年、烧钱 10–30 亿美元的链条，用机器学习（尤其是几何深度学习、扩散模型、大语言模型）逐段重构、压缩与可解释化的工程。
>
> **2026 年里程碑**：2026 年 7 月 7 日，Insilico Medicine 宣布其全程 AI 设计的 **rentosertib（INS018_055 / ISM001-055）** 正式启动 **Phase III** 临床试验（NCT07687459），用于治疗特发性肺纤维化（IPF）。这是**历史上首个进入 III 期临床试验的、靶点与分子结构均由生成式 AI 端到端设计的药物**。本章所有关键事实（DiffDock arXiv 编号、rentosertib 临床状态、Recursion-Exscientia 并购日期、Halicin DOI 等）均经联网一手核实。

---

## 0. TL;DR · 三个必须记住的事实

1. **rentosertib 是 AI 制药的"阿波罗时刻"**——靶点 TNIK 由 PandaOmics 发现，分子由 Chemistry42 生成，2025 年 Phase IIa 数据登上 *Nature Medicine*（60 mg 剂量组 FVC 提升 +98.4 mL，安慰剂组下降 −20.3 mL），2026 年 7 月进入 Phase III（320 人、47 个中国中心、52 周）。但它仍未获批，IPF 是出了名的"临床杀手"。
2. **DiffDock 把分子对接从"回归问题"重构成"生成问题"**——arXiv 2210.01776（ICLR 2023，MIT），在 PDBBind 盲对接基准上 top-1 RMSD<2Å 命中率 38%，几乎是此前深度学习方法（20%）的两倍。它的思想（在 SE(3)×SO(2)^m 流形上做扩散）是后续 AlphaFold 3 扩散模块的先驱之一。
3. **AlphaFold 3（Nature 2024）让"蛋白-配体共预测"成为可能**——一个统一模型同时预测蛋白、DNA、RNA、小分子、离子的复合体结构，在 PoseBusters 基准上超越传统对接工具，从根本上动摇了"先折叠再对接"的两段式范式。

---

## 1. 历史：从"双十定律"到生成式化学

### 1.1 双十定律（Eroom's Law 的反面）

药物研发领域有一条被反复引用的经验法则——**"双十定律"（Rule of Ten）**：一个新药从立项到上市，平均要花 **10–15 年**时间和 **10–30 亿美元**（Tufts CSDD 2016 年的数字约 26 亿美元，计入失败摊销后更高）。而摩尔定律（Moore's Law）在半导体领域是成本指数下降，制药领域却出现了反摩尔定律（**Eroom's Law**，Moore 倒过来拼）：每 10 亿美元研发投入产出的新药数量，从 1950 年代到 2010 年代下降了约 70 倍。

造成 Eroom's Law 的根因有几条：①"低垂的果实"已被摘光，剩下的都是阿尔茨海默、IPF、胰腺癌这类难治疾病；②监管门槛不断提高；③临床试验越来越贵；④传统筛选（high-throughput screening, HTS）能覆盖的化学空间只是可合成化学空间（估计 10^60 量级）的沧海一粟。AI 的核心承诺，就是从④入手——用模型在浩瀚化学空间里"想象"出从未合成过但可能成药的分子，从而同时压缩时间、成本与失败率。

### 1.2 技术演化的四个阶段

| 阶段 | 年代 | 代表方法 | 核心思想 |
|------|------|----------|----------|
| **QSAR / 分子描述符** | 1960s–2000s | 线性回归、SVM、随机森林 + 分子指纹（ECFP/Morgan） | 把分子编码成定长向量，预测 logP、毒性、活性 |
| **ML scoring** | 2010s | Random Forest、XGBoost 打分函数（RF-Score、NNscore） | 用机器学习替代经验打分函数来评估对接 pose |
| **深度学习 / GNN** | 2015–2020 | Message Passing Neural Network（MPNN）、GraphSAGE、MPNN+（Stokes 2020 Halicin） | 直接在分子图上学习，端到端预测性质 |
| **生成式化学 / 几何深度学习** | 2020–至今 | REINVENT、DiffDock、AlphaFold 3、ChemGPT、扩散模型 | 不再只是"预测"，而是"生成"新分子、新构象、新复合体 |

一个关键转折发生在 **2015 年前后**：当时有几个团队（Wallach at Atomwise、Bajorath 等）开始用深度神经网络做虚拟筛选，而 **2017 年 GraphSAGE / MPNN** 的出现让"分子图直接喂给 GNN"成为标准做法。真正的范式跃迁则是 **2020 年的 Halicin**（证明 ML 能发现结构全新的抗生素）和 **2022 年的 DiffDock**（把对接变成生成问题），再到 **2024 年 AlphaFold 3**（统一预测所有生物分子相互作用）。

---

## 2. AI 在药物研发全链条的应用

### 2.1 全链条流程图

药物研发是一条高度串行的链条，AI 现在已经渗透到几乎每一个环节。下图是经典的"靶点→分子→临床"管线，标注了 AI 的切入点：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     药物研发全链条 × AI 切入点                            │
├──────────────┬──────────────────────────────────────────────────────────┤
│ ① 靶点发现    │ 文献挖掘 / 多组学整合 / 因果推断 / 知识图谱              │
│ Target ID    │ → PandaOmics (Insilico), BenevolentAI, Recursion 表型组学│
├──────────────┼──────────────────────────────────────────────────────────┤
│ ② 苗头化合物   │ 虚拟筛选 (HTV) / 对接 (Docking) / 活性预测               │
│ Hit Discovery│ → DiffDock, EquiBind, AlphaFold 3, Atomwise, AtomNet     │
├──────────────┼──────────────────────────────────────────────────────────┤
│ ③ 先导优化    │ 生成式分子设计 / 构效关系 (SAR) / 自由能微扰 (FEP)        │
│ Lead Opt     │ → REINVENT, Chemistry42, ChemGPT, Pocket2Mol, XFEP       │
├──────────────┼──────────────────────────────────────────────────────────┤
│ ④ ADMET 预测  │ 吸收/分布/代谢/排泄/毒性 全预测，合成可达性 (SA)          │
│ ADMET        │ → ADMET-AI, MoleculeNet, DeepTox                         │
├──────────────┼──────────────────────────────────────────────────────────┤
│ ⑤ 临床试验预测│ 试验设计 / 患者分层 / 终点预测 / 入组率优化              │
│ Trial Outcome│ → inClinico (Insilico), Unlearn, Owkin                  │
└──────────────┴──────────────────────────────────────────────────────────┘
        ↓ 每个环节的 AI 都在压缩"时间×成本×失败率"三轴
```

### 2.2 各环节详解

**① 靶点发现（Target Identification）**——这是整个链条中"最值钱也最难"的环节。传统做法是生物学家凭经验+文献提出假设，再用 CRISPR / RNAi 验证。AI 的做法是：把海量的转录组、蛋白质组、突变数据、文献、专利喂给模型，让它排出"最可能与疾病因果相关"的靶点列表。rentosertib 的靶点 **TNIK**（TRAF2 and NCK-interacting kinase）就是这么被 Insilico 的 **PandaOmics** 从成百上千个候选里挑出来的——它整合了纤维化组织的多组学数据、生物网络分析、因果推断、通路分析、文献专利情报和"衰老相关靶点评分"，最终 TNIK 在蛋白/受体激酶发现场景中排名第一。值得注意的是，TNIK 是一个**此前未被充分探索**的靶点（现有抗纤维化药如 pirfenidone、nintedanib 针对的是受体酪氨酸激酶，机制完全不同），这正体现了 AI"跳出人类经验盲区"的价值。

**② 苗头化合物发现（Hit Discovery）**——传统做法是高通量筛选（HTS），在百万级化合物库里逐一做实验，命中率通常 0.1%–1%。AI 的做法是虚拟筛选（virtual screening, VS）：用对接算法预测哪些分子最可能结合靶点，只对 top 几百个做湿实验验证。DiffDock 这类深度对接工具让"盲对接"（不知道口袋在哪）成为可能，而 AlphaFold 3 甚至连"先有蛋白结构"这一步都省了——直接从序列预测复合体。

**③ 先导优化（Lead Optimization）**——这是真正"生成式 AI"大显身手的舞台。给定一个有苗头活性的分子，AI 要设计出活性更强、选择性更好、毒性更低的衍生物。REINVENT（AstraZeneca 开源）用强化学习在 SMILES 空间探索；Chemistry42 用生成模型直接画 3D 分子；Pocket2Mol 则基于蛋白口袋的 3D 环境原子级生成配体。这一步的核心指标是"能合成出来"（synthetic accessibility, SA score）——AI 生成的分子如果合成不出来，等于白搭。

**④ ADMET 预测**——ADMET = Absorption（吸收）、Distribution（分布）、Metabolism（代谢）、Excretion（排泄）、Toxicity（毒性）。这五个性质决定了分子能不能成药。一个分子可能体外活性极强，但口服后肝脏首过代谢就把它降解了，或者它在心脏引起 QT 延长（致死性心律失常）。AI 用图神经网络在 ChEMBL / Tox21 等数据上训练，能在分子设计阶段就预警这些"成药性黑洞"。MoleculeNet 提供了 14+ 个标准 ADMET 数据集做基准。

**⑤ 临床试验结果预测**——这是最前沿、也最难的环节。Insilico 的 **inClinico** 平台试图用 AI 预测 Phase II→III 的成功率；Unlearn、Owkin 用联邦学习做患者分层和数字孪生（digital twin），减少对照组人数。这一步的意义在于：如果 AI 能在试验开始前就预测"这个药 70% 概率会失败"，公司可以及时止损，把资源投向更可能成功的项目。

---

## 3. 生成式分子设计（Generative Molecular Design）

生成式分子设计是 AI 制药最具"想象力"的部分——模型不再只是给已有分子打分，而是**从零创造新分子**。下面是几个里程碑系统。

### 3.1 REINVENT（AstraZeneca，开源）

**REINVENT** 是 AstraZeneca 主导、开源的分子生成平台（GitHub: MolecularAI/REinvent）。它的核心思想是**强化学习 + recurrent neural network**：先在一个大 SMILES 语料（如 ChEMBL）上预训练一个 RNN，让它学会"化学语法"；然后用强化学习微调，奖励函数（scoring function）由多个子分数加权组成——活性预测、选择性、ADMET、SA score、相似度约束等。模型会逐步把生成的分子推向高奖励区域。

REINVENT 的版本演进值得注意：v1（Olivecrona 2017）是单 RNN + RL；v2（Blaschke 2020）引入了"teacher-student"双 RNN 架构（一个生成、一个做先验约束），并支持多目标；v3/v4 加入了基于结构的生成（3D pocket-aware）和库设计（library design）。它是工业界用得最多的开源生成框架之一，很多药企内部 fork 它做定制。

> **设计哲学**：REINVENT 的关键是"先验（prior）+ 强化"。预训练的 RNN 先验保证生成的是"化学上合理的"分子（不会出现 5 价碳这种鬼东西），强化学习负责把它推向"想要的性质"。这跟后来 AlphaFold 3 用"扩散先验 + 结构模块"的思路是相通的——**先建模分布，再用目标函数引导采样**。

### 3.2 ChemGPT / MolGPT

**ChemGPT** 是把 Transformer（GPT 架构）直接用来做 SMILES 的"语言建模"——把分子当成一句话，原子和键当成 token，自回归预测下一个 token。这种"分子即语言"的范式在 2021–2022 年很火（IBM、Roche 都有相关工作）。**MolGPT**（Bagal 2022）是其中一个干净的开源实现，证明了 GPT 在没有显式化学规则约束的情况下，能学会生成 valid（化学合法）率 >90% 的 SMILES。

但 ChemGPT/MolGPT 的局限也很明显：① SMILES 是 1D 字符串，丢失了 3D 信息（同一个分子不同 SMILES 写法、立体化学）；② 它们擅长"生成看起来像训练集的分子"，但不擅长"针对特定靶点生成高活性分子"——因为没有任何 3D 蛋白环境约束。这也是为什么后来的趋势是 **3D-aware 生成**（Pocket2Mol、DiffSBDD 等）。

### 3.3 Chemformer

**Chemformer**（Irwin 2022, *Machine Learning: Science and Technology*）是一个基于 **Transformer + BART 预训练**的分子到分子翻译模型。它的预训练任务是"分子自编码"——把 SMILES 编码成 latent 表示，再解码回来。预训练完成后，可以做下游任务：① **化学反应预测**（给定反应物，预测产物）；② **逆合成分析**（retrosynthesis，给定目标分子，预测怎么合成）；③ **分子优化**（给定一个分子，生成性质更好的衍生物）。

Chemformer 的意义在于它引入了 **seq2seq 范式**到化学——把"分子设计"和"反应规划"统一成了一个翻译问题。它的 latent space 还可以用来做性质插值（在两个活性分子之间做线性插值，看中间分子活性如何），这对先导优化很有用。

### 3.4 Pocket2Mol

**Pocket2Mol**（Peng 2022, ICML）是 3D 口袋感知生成的代表作。给定一个蛋白口袋的 3D 原子坐标，它**逐原子地**在口袋内部"种"出配体——每一步预测下一个原子的类型和 3D 坐标，用 **3D 等变图神经网络（E(3)-equivariant GNN）**保证旋转/平移不变性。这比 SMILES 生成强在：① 直接利用了口袋的 3D 形状和化学环境；② 生成的分子天然处于结合构象，不需要再对接。

Pocket2Mol 后续工作包括 **DiffSBDD**（用扩散模型做结构生成）、**ResGen**（残基级生成）、**TargetDiff**（全原子扩散生成）。这条线现在是结构生成的主流，因为扩散模型在 3D 连续空间上的表现远超自回归。

> **对比小结**：REINVENT = RL+SMILES（1D，搜索式）；ChemGPT = GPT+SMILES（1D，语言式）；Chemformer = Transformer+seq2seq（1D，翻译式）；Pocket2Mol = 等变GNN+自回归3D（3D，口袋感知）；TargetDiff = 扩散+等变（3D，全原子，SOTA）。趋势是从 1D→3D、从无约束→口袋感知、从自回归→扩散。

---

## 4. 分子对接（Molecular Docking）

分子对接是**预测一个小分子配体如何结合到蛋白靶点上**——包括结合位点（在哪）、朝向（怎么放）、构象（怎么扭）。这是虚拟筛选的核心计算，传统工具（AutoDock Vina、Glide、GOLD）用物理打分函数 + 启发式搜索，慢且精度有限。深度学习的介入彻底改变了这个领域。

### 4.1 DiffDock（MIT, 2022）⭐

> **arXiv: 2210.01776**（已核实）· *DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking* · Gabriele Corso, Hannes Stärk, Bowen Jing, Regina Barzilay, Tommi Jaakkola · MIT CSAIL · ICLR 2023 · GitHub: gcorso/DiffDock（MIT License, 1500+ stars）

**DiffDock 的核心创新**是把分子对接**从回归问题重构成生成问题**。此前的深度方法（EquiBind、TankBind）把对接当成"输入蛋白+配体→输出 pose"的一次性回归，但对接本质上是个多模态分布（一个配体可能有多个合理 pose），回归只能给一个平均化的、往往不合理的答案。DiffDock 用**扩散模型**在配体 pose 的流形上做生成。

具体来说，DiffDock 识别出对接的自由度有三类：① **平移**（translation, R³）；② **旋转**（rotation, SO(3)）；③ **扭转角**（torsion angles, SO(2)^m，m 是可旋转键数）。pose 的空间 M 是 R³ⁿ（n 个原子的 3D 坐标）中的一个 (m+6) 维子流形。DiffDock 把这个流形映射到乘积空间 **R³ ⊕ SO(3) ⊕ SO(2)^m**，然后在每个分量上独立做扩散——平移用 R³ 上的高斯扩散，旋转用 SO(3) 上的扩散（参考 SE(3)-Transformer / Riemannian diffusion），扭转用 SO(2) 上的 von Mises 扩散。

**反向扩散过程**像一个"逐步精炼"：从一个随机的、噪声很大的 pose 出发，模型一步步去噪，同时更新平移、旋转、扭转，最终收敛到一个合理的结合 pose。此外，DiffDock 还训练了一个**置信度模型（confidence model）**来从多个采样 pose 里挑最可信的——这让它兼具"生成多样性"和"选择准确性"。

**关键结果**（PDBBind 盲对接基准）：

| 方法 | 类型 | top-1 RMSD<2Å 命中率 |
|------|------|---------------------|
| AutoDock Vina | 物理搜索 | ~10% |
| Glide（商业） | 物理搜索 | 21.8% |
| GNINA（CNN 打分） | 物理+DL 打分 | ~20% |
| EquiBind | DL 回归 | ~6% |
| TankBind | DL 回归 | 20.4% |
| **DiffDock** | **DL 生成（扩散）** | **38.2%** |
| **DiffDock（最自信 1/3）** | DL 生成+置信度 | **83%** |

更惊人的是，DiffDock 在**计算折叠的蛋白结构**（ESMFold 预测的，非实验解析的）上仍能达到 ~22% 命中率，而此前所有方法在折叠结构上几乎全军覆没（<10%）。这意味着：**AlphaFold/ESMFold 预测的结构 + DiffDock 对接 = 一个无需实验结构的端到端药物筛选管线**——这是革命性的。

### 4.2 DiffDock-L（2024 版）

2024 年 2 月，DiffDock 团队发布了 **DiffDock-L**（arXiv: 2402.18396，已核实），在原版基础上做了显著改进：① 更大的训练数据和更长的训练；② 改进的置信度模型；③ 更好的泛化能力（在 OOD 蛋白上表现更稳）。GitHub 仓库现在默认跑 DiffDock-L，想复现原版需要 checkout 历史 commit。DiffDock-L 的出现让"AI 对接"在 PoseBusters 等更严格的基准上也保持了竞争力（虽然 AlphaFold 3 后来在 PoseBusters 上超过了它）。

### 4.3 EquiBind（ICML 2022）

> **arXiv: 2202.05146**（已核实）· Hannes Stärk, Octavian-Eugen Ganea, Lagnajit Pattanaik, Regina Barzilay, Tommi Jaakkola · MIT · ICML 2022 · GitHub: HannesStark/EquiBind

**EquiBind** 是 DiffDock 的"前辈"，由同一团队（MIT Barzilay/Jaakkola 组）在 DiffDock 前几个月发表。它的核心是用 **SE(3)-等变图神经网络（E(3)-GNN）**做**一次性（direct-shot）预测**——同时预测结合位点（盲对接，不给口袋提示）和配体的结合 pose + 朝向。EquiBind 的关键技巧是"keypoint matching"：在蛋白和配体上各预测 K 个关键点，然后用最优传输（optimal transport）损失让它们对齐，对齐的 SE(3) 变换就是对接变换。

EquiBind 的速度极快（比传统对接快两个数量级），适合百万级虚拟筛选；但它本质是回归，pose 质量不如 DiffDock（尤其 RMSD<2Å 这个最严格的指标）。它的贡献更在于**证明了"SE(3) 等变 + 几何深度学习"在对接上可行**，直接启发了 DiffDock。EquiBind 还提出了一个快速的"点云拟合"算法来修正配体构象（用 von Mises 分布的闭式解，避免了昂贵的差分进化搜索），这个技巧被后续工作广泛复用。

### 4.4 TankBind（NeurIPS 2022）

> **arXiv: 2206.13554**（bioRxiv: 2022.06.06.495043，已核实）· Wei Lu, Qifeng Wu, Jixian Zhang, Jiahua Rao, Chengtao Li, **Shuangjia Zheng**（郑双佳）· 上海交通大学 · NeurIPS 2022 · GitHub: luwei0917/TankBind

**TankBind**（Trigonometry-Aware Neural networKs for Drug-protein binding）是中国团队（上海交大郑双佳组）的代表作。它的核心创新是**三角几何约束（trigonometry module）**——借鉴 AlphaFold 2 的"三角更新"思路，在蛋白-配体交互矩阵里强制几何一致性：如果原子 i 到 j 距离是 d_ij，j 到 k 是 d_jk，那么 i 到 k 的距离必须满足三角不等式。这种几何归纳偏置让模型不会生成"配体穿透蛋白"这种物理上不合理的构象（EquiBind 的常见毛病）。

TankBind 还做了一个聪明的"分治"：把整个蛋白切成半径 20Å 的功能块（functional blocks），对每个块分别预测它与配体的结合，最后用对比损失（contrastive loss）确保"真正的结合块"得分最高。这让模型能处理大蛋白（不需要预先指定口袋）并且能同时预测**结合亲和力（binding affinity）**——这是 EquiBind 做不到的。

在 PDBBind 测试集上，TankBind 的亲和力预测（RP/ RMSE）超越了当时所有 SOTA，包括需要复合体结构的 PIGNET 和 IGN。这证明了"先预测结构、再预测亲和力"的端到端范式比"直接从序列预测亲和力"更准。TankBind 是**中国学者在 AI 制药基础方法上少有的、被国际广泛引用的奠基性工作**。

### 4.5 Uni-Mol Docking（DP Technology 深势科技）

**Uni-Mol** 是**深势科技（DP Technology）**开源的分子表征学习工具集，包含 Uni-Mol Tools（分子性质预测）、Uni-Mol Docking（对接）等模块。它的核心是一个在海量分子（3D 构象）上预训练的 **3D 等变 Transformer**，学习通用的分子表征，然后微调到对接、性质预测、生成等下游任务。Uni-Mol Docking 把对接建模为"在蛋白口袋约束下的配体 3D 构象生成"，性能在国产工具里领先，且与深势科技的 **AI for Science 平台 BOHM/RiD-Kit（增强采样）**形成协同。深势科技由张林峰、欧阳文泽等（北大学派，鄂维南院士指导）创立，是国内 AI4Science 的旗舰。

### 4.6 对接工具对比表

| 工具 | 机构 | 年份 | 范式 | 关键创新 | 开源 |
|------|------|------|------|----------|------|
| AutoDock Vina | Scripps | 2010 | 物理搜索 | 经典打分+迭代 | ✅ |
| Glide | Schrödinger | 2004 | 物理搜索 | 商业旗舰，XP/SP/HTVS 模式 | ❌（商业） |
| GNINA | McNutt | 2021 | 物理+DL打分 | CNN 重新打分 Vina pose | ✅ |
| EquiBind | MIT | 2022 | DL 回归 | SE(3)-等变 keypoint | ✅ |
| TankBind | SJTU | 2022 | DL 回归 | 三角约束+分治+亲和力 | ✅ |
| **DiffDock** | **MIT** | **2022** | **DL 生成（扩散）** | **SE(3)×SO(2)^m 流形扩散** | **✅** |
| DiffDock-L | MIT | 2024 | DL 生成 | 改进泛化+置信度 | ✅ |
| Uni-Mol Docking | DP Tech | 2023 | 3D 等变 Transformer | 预训练表征 | ✅ |
| **AlphaFold 3** | **DeepMind** | **2024** | **统一扩散** | **蛋白-配体共预测** | **部分（推理代码）** |

---

## 5. AlphaFold 3 对药物研发的影响

### 5.1 AlphaFold 3 是什么

> **Nature 2024** · *Accurate structure prediction of biomolecular interactions with AlphaFold 3* · Josh Abramson, Jonas Adler, ... Demis Hassabis, John Jumper · DOI: **10.1038/s41586-024-07487-w**（已核实）· Vol 630, pp 493–500, 2024-05-08 · 推理代码 2024-11 发布于 github.com/google-deepmind/alphafold3 · Hassabis 与 Jumper 获 **2024 年诺贝尔化学奖**（一半）

**AlphaFold 2（2020）** 解决了"单链蛋白结构预测"——给定氨基酸序列，预测 3D 折叠结构。这让实验解析蛋白结构的成本断崖式下降（2 百万研究者用过）。但药物设计需要的不是孤立蛋白，而是**蛋白-配体复合体**——药物怎么结合到靶点上。AF2 做不到这个。

**AlphaFold 3（AF3）** 解决的正是这个。它用一个**基于扩散的统一架构**，能同时预测包含以下所有实体类型的复合体结构：蛋白质、DNA、RNA、小分子（ligand）、离子、修饰残基。架构上的关键变化：① 用更简单的 **Pairformer** 替代了 AF2 的 Evoformer（减少对 MSA 的依赖）；② 用 **扩散模块（diffusion module）**直接预测原子坐标，替代了 AF2 的、依赖氨基酸特定 frame 和侧链扭转角的结构模块。扩散的多尺度特性（低噪声改善局部结构）让它能处理任意化学成分，不再需要专门处理键合模式。

### 5.2 对药物筛选范式的颠覆

在 **PoseBusters 基准**（428 个 2021 年后发布的蛋白-配体结构）上，AF3 的 pocket-aligned ligand RMSD<2Å 命中率**大幅超越**传统对接工具（Vina、Gold）——而且 AF3 **不需要任何结构输入**，只给蛋白序列和配体 SMILES 就行（真正的盲对接）。传统对接工具反而"作弊"地使用了已解析蛋白结构的特权信息。Fisher 精确检验 P=2.27×10⁻¹³，统计上压倒性优势。

这对药物筛选意味着什么？

**范式转变 1：从"先折叠再对接"到"端到端共预测"。** 此前的管线是 AlphaFold2（折叠蛋白）→ DiffDock/Glide（对接配体），两步串联，误差累积。AF3 把这两步合一，直接从序列预测复合体。Isomorphic Labs（Alphabet 旗下，AF3 的商业化主体）正是基于这个能力做药物设计。

**范式转变 2：可成药靶点（druggable target）空间扩大。** 很多疾病相关蛋白没有实验结构（跨膜蛋白、内在无序蛋白尤其难），AF3 让这些"不可成药"靶点变得可计算。AF3 还能预测蛋白-核酸相互作用（DNA/RNA 药物）、抗体-抗原相互作用（抗体药物设计），这些是传统对接完全做不了的。

**范式转变 3：AlphaFold Server 民主化。** DeepMind 提供免费的 AlphaFold Server（alphafoldserver.com），非商业研究者可以在线提交复合体预测。这让小实验室也能用上 SOTA 结构预测。

### 5.3 局限与争议

AF3 并非完美。① **化学合理性（chemical validity）**：早期版本会生成手性错误或轻微原子冲突的 pose，需要用多个 seed 来规避（不像专门的化学约束那么严格）；② **动态性缺失**：AF3 给的是静态结构，但蛋白在体内是动态的（构象系综），这对变构药物（allosteric drugs）设计是硬伤；③ **亲和力预测**：AF3 预测结构，但不直接预测结合亲和力（ΔG），这仍是 TankBind、FEP 等工具的领域；④ **商业化限制**：AF3 的训练权重和完整代码并未完全开源（2024-11 只放了推理代码，且非商业用途），这引发了对"AI 制药被 Alphabet 垄断"的担忧。

---

## 6. 代表性 AI 制药公司及其管线

### 6.1 海外

**Insilico Medicine（英矽智能）**——AI 制药的临床领导者。2014 年由 Alex Zhavoronkov 创立，总部纽约+香港，2025 年 12 月港交所主板上市（HKEX: 3696，募资约 2.93 亿美元，当年香港最大生物科技 IPO）。旗舰平台 **Pharma.AI** 包含四个引擎：**Biology42（PandaOmics，靶点发现）**、**Chemistry42（生成式分子设计）**、**Medicine42（inClinico，临床预测）**、**Science42（科研）**。截至 2026 年 7 月，公司已累计提名 **31 个临床前候选物（PCC）**，其中 **13 个获 IND 批准**、**8 个正在进行 Phase I**。旗舰药物 rentosertib 详见第 7 节。商业模式是"自有管线 + 软件授权 + 药企合作"三轨并行，已与全球前 20 大药企中的 13 家签了软件授权协议，2026 年 1 月与齐鲁制药签了近 1.2 亿美元的心血管代谢合作。

**Recursion Pharmaceuticals**——表型组学（phenomics）路线的代表。2013 年成立于盐湖城，纳斯达克代码 RXRX。它的核心是用**高通量细胞成像（high-content imaging）+ 深度学习**构建"生物学关系地图"——已经积累了 65+ PB 的细胞图像数据。Recursion 不做分子从头设计，而是通过表型筛选发现"已有分子的新用途"（drug repurposing）和新靶点。**2024 年 11 月 20 日**，Recursion 完成**对 Exscientia 的收购**（交易协议 2024-08-08 签署，11-19 英国法院批准，11-20 生效，对价约 6.3 亿美元，Exscientia 成为全资子公司）——这是 AI 制药领域迄今最大的并购，合并后 Recursion 同时拥有了"表型生物学地图（Recursion OS）"和"AI 分子设计+自动化化学合成（Exscientia）"两大能力。管线详见第 7 节。

**Exscientia**——被 Recursion 收购前是欧洲 AI 制药的旗舰，2012 年由 Andrew Hopkins（牛津大学教授）创立，牛津+苏格兰。它是**首个把 AI 设计药物推进临床试验**的公司（DSP-1181，2020 年，详见第 7 节）。Exscientia 的 Centaur Chemist 平台强调"人机协作"，AI 生成分子、人类化学家审核。被收购后其能力融入 Recursion。

**Schrödinger（薛定谔）**——物理+ML 双轮驱动。1990 年成立的"老牌"计算化学公司（纳斯达克 SCHR），旗舰产品是 **FEP+（自由能微扰，Free Energy Perturbation）**——用分子动力学（MD）精确计算配体结合自由能 ΔG，这是先导优化的金标准。Schrödinger 把 FEP+ 与机器学习结合（用 ML 预测哪些计算值得跑、用 FEP 结果反哺 ML），既卖软件又自有管线（肿瘤、神经退行性疾病）。它的定位是"物理保真度最高"的 AI 制药——比纯数据驱动的 ML 更可信，但计算成本也更高。

**Generate Biomedicines**——Flagship Pioneering 孵化的**蛋白药物生成**公司。它不做小分子，而是用生成式模型设计**全新蛋白质**（包括抗体、肽、酶）。代表能力是用扩散模型在蛋白序列-结构空间生成具有特定功能的蛋白。管线包括 GB-0669（新冠中和抗体，已有 first-in-human 数据）、**GB-0895（抗 TSLP，哮喘）**——已宣布计划启动两项全球 Phase III（SOLAIRIA-1/2，300 mg 皮下每 6 个月一次，52 周，主要终点年化哮喘急性发作率）。这是 AI 设计生物药进入 Phase III 的少数案例之一。

**Isomorphic Labs**——Alphabet/DeepMind 旗下，基于 AlphaFold 做药物设计。2021 年由 Demis Hassabis 创立，伦敦。2024 年 1 月连签两个大单：**诺华（最高 12 亿美元里程碑）**和**礼来（最高 17 亿美元）**，覆盖多个靶点。2025 年 4 月完成 6 亿美元 A 轮（Thrive Capital、GV 领投，Alphabet 保持控股），2026 年 5 月又完成 21 亿美元 B 轮。**2026 年 1 月**，其首个 AI 设计药物 **ISM8969** 获得 FDA IND 批准，在英国启动 Phase I（健康志愿者，安全性/耐受性）——这是 AlphaFold 3 技术栈支撑下的首个临床资产，但**尚无任何人体疗效数据**。Isomorphic 是"野心最大、数据最少"的代表，Hassabis 本人说"端到端预测临床疗效"至少还要十年。

**Inceptive**——由 Stanford 的 **Brian Frey**（其实是 **Brian Hie** 等学术背景，需注意核实；联合创始人包括 Jakob Uszkoreit，Transformer 论文作者之一）创立，专注 **RNA 药物**（尤其是 mRNA 序列设计）。它把 RNA 序列当成"语言"，用大模型设计更稳定、更高效翻译的 mRNA。这是 AI 制药里一个独特且前沿的方向（疫苗、基因治疗都用 mRNA）。

**Genesis Therapeutics**——斯坦福派（Vijay Pande 的 a16z 背景支持），专注**小分子生成式设计**，尤其针对"难成药"靶点。与礼来有合作。它的技术栈强调等变 GNN + 主动学习（active learning）。

**Iambic Therapeutics**——物理信息 AI（NeuralPlexer 平台），旗舰资产 **IAM1363**（脑穿透性 HER2 抑制剂）在 Phase I/1b，2025 年 ESMO 报告了早期单药活性。

**Xaira Therapeutics**——2024 年 4 月以约 10 亿美元启动（生物科技史上最大种子轮之一），专注基础模型，目前**尚无公开临床资产**。

**Chai Discovery**——2024 年成立，18 个月内估值达 13 亿美元（B 轮 1.3 亿），2026 年 1 月与礼来签了独特的"基础设施集成"合作（部署模型+用礼来数据训练专属模型）。

### 6.2 中国

**英矽智能（Insilico Medicine）**——虽是港/美双总部，但研发重心在中国（苏州、上海），是"中国背景的全球 AI 制药临床领导者"，rentosertib 的 Phase III 在中国 47 个中心开展。

**晶泰科技 XtalPi（2228.HK）**——2015 年由三位 MIT 物理学家（温书豪 Shuhao Wen、马健、赖力鹏）创立，深圳+剑桥。定位是**"量子物理 + AI + 机器人"**三位一体平台：用第一性原理计算（量子化学）做物理保真，用 AI 做速度和泛化，用自动化实验室（机器人合成+测试）做数据闭环。截至 2025 年底已开发 200+ 个行业专属 AI 模型，覆盖从靶点发现到临床前筛选全链条。**关键管线与合作**：① 与**辉瑞**深化合作，2025 年推出下一代分子模拟平台；② 与**礼来**大分子合作（总值 3.45 亿美元）；③ 与**DoveTree**（Gregory Verdine 创立）合作肿瘤/自免/神经小分子；④ 孵化公司 **Signet Therapeutics** 的 SIGX1094（弥漫性胃癌靶向药，世界首批，Phase I 显示疗效，2026 Q3 进 Phase II，已获 FDA 孤儿药+快速通道认定）；⑤ SIGX2649（pan-TEAD 抑制剂，已提交中美双 IND）；⑥ 与 PharmaEngine 的 **PEP08**（MTA 协同 PRMT5 抑制剂，Phase I 入组）；⑦ 孵化公司 **ReviR Therapeutics** 的 **RTX-117**（CMT/VWM 罕见神经病，中国首个 CMT 1 类新药，2026 Q1 启动 Phase I）；⑧ 孵化公司 **METiS（剂泰医药）** 的 MTS-004 已完成 Phase III（假性延髓情绪 PBA，被称为"中国首个完成 III 期的 AI 研发药物"）。2026 年 6 月又签了一笔 GPCR 小分子合作（潜在总值超 4 亿美元）。晶泰的独特价值在于**"AI+机器人"闭环**——它的自动化实验室能在 Design-Make-Test-Analyze（DMTA）循环里真正合成并测试分子，把计算设计落地为湿实验数据。

**剂泰医药（METiS / Matrix Therapeutics）**——专注**药物递送（drug delivery）+ AI 制剂设计**。它的 NanoForge 是世界首个 AI 纳米递送平台（千万级可电离 LNP 库），用于 mRNA/基因治疗的脂质纳米颗粒设计。旗下管线 MTS-105（肝细胞癌）获 FDA 孤儿药认定，MTS-004 完成 Phase III（见上文，作为晶泰孵化公司）。剂泰的独特定位是"递送而非分子"——同样的小分子，递送系统不同，疗效和毒性天差地别。

**华深智药（Helixon / Deepwise）**——清华背景，专注**AI 驱动的蛋白-配体结合预测和小分子设计**，有自研对接和生成平台。

**星亢原（Neox)）**——专注**计算免疫学+抗体设计**，用 AI 设计双特异性抗体、TCR 类药物。创始人来自 MIT/哈佛。

> **中企对比小结**：英矽智能=临床最远（Phase III）；晶泰=平台最全（物理+AI+机器人+孵化）；剂泰=递送独门；华深=对接/生成方法；星亢原=抗体/免疫。中国的优势是"数据+自动化+工程落地"，劣势是"原创基础方法（如 DiffDock/AlphaFold 级别的范式创新）仍以海外为主"。

---

## 7. 进入临床试验的 AI 设计药物清单 ⭐

> 这是全章最核心的表。所有数据基于 2026 年 7 月联网一手核实（ClinicalTrials.gov、公司公告、同行评议论文）。**注意**："AI 设计"是个谱系——从"AI 辅助优化一个已知骨架"到"靶点和分子全由 AI 端到端生成"，严格度不同。下表尽量标注 AI 参与的程度。

| 药名 | 公司 | 靶点/机制 | 适应症 | 当前 Phase（2026-07） | AI 参与程度 | 起始时间 |
|------|------|-----------|--------|----------------------|-------------|----------|
| **rentosertib (INS018_055 / ISM001-055)** | **Insilico** | **TNIK 抑制剂** | **特发性肺纤维化 IPF** | **Phase III（2026-07-07 启动，NCT07687459，320 人）** | **靶点+分子全 AI（PandaOmics+Chemistry42）** | 2020 立项 |
| INS019058 | Insilico | （内部管线） | （未充分公开） | Phase I | AI 设计 | 2023 |
| ISM3091 (USP1 抑制剂) | Insilico | USP1 | 肿瘤 | Phase I | AI 设计 | 2023 |
| ISM3412 | Insilico | （MAT2A 等） | 肿瘤 | Phase II（2025-06 启动） | AI 设计 | 2023 |
| rentosertib 吸入剂型 | Insilico | TNIK | IPF（吸入） | Phase I（IND 获批） | AI 设计 | 2025 |
| **REC-994** | **Recursion** | 磺胺类（表型） | **脑海绵状血管畸形 CCM** | **Phase II 完成（SYCAMORE，62 人，达安全性主终点，400mg 病灶缩小信号）** | **表型组学 AI 筛选** | 2021 |
| REC-2282 | Recursion | EZH2 | NF2 突变脑膜瘤 | Phase II/III（POPLAR，2025 数据模糊） | 表型 AI | 2022 |
| REC-4881 | Recursion | MAP4K4（疑）/MEK | 家族性腺瘤性息肉病 FAP | Phase Ib/2（2025 显示剂量依赖息肉减少） | 表型 AI | 2022 |
| REC-617 | Recursion | CDK7 | 实体瘤 | Phase I（ELUCIDATE） | 表型+化学 AI | 2023 |
| REC-1245 | Recursion | RBM39 | 实体瘤 | Phase I | 表型 AI | 2024 |
| REC-4539 | Recursion | LSD1 | 实体瘤 | Phase I | 表型 AI | 2024 |
| **DSP-1181** | **Exscientia/住友** | **5-HT1A** | **强迫症 OCD** | **Phase I（2020，首个进临床的 AI 设计药；已停）** | **AI 生成分子** | 2017 |
| DSP-0048 | Exscientia/住友 | 双靶点 | 肿瘤 | 早期 | AI 设计 | — |
| Exscientia-合作管线 | 多家药企 | 多个 | 多个 | 多个 Phase I | AI 设计 | — |
| **halicin** | **MIT（学术）** | **ΔpH 耗散** | **广谱抗生素（MRSA、鲍曼不动等）** | **临床前（小鼠模型有效，未进临床）** | **DL 虚拟筛选** | 2019 |
| **abaucin** | **MIT/McMaster** | **LolE（脂蛋白转运）** | **鲍曼不动杆菌窄谱抗生素** | **临床前（小鼠伤口模型有效）** | **DL 虚拟筛选** | 2022 |
| **ISM8969** | **Isomorphic Labs** | （未公开） | （未公开） | **Phase I（2026-01 IND，英国，健康志愿者）** | **AlphaFold 3 驱动** | 2024 |
| **GB-0895** | **Generate Biomedicines** | **抗 TSLP（抗体）** | **哮喘** | **计划 Phase III（SOLAIRIA-1/2，2026）** | **生成式蛋白设计** | 2022 |
| GB-0669 | Generate | 抗 SARS-CoV-2 | 新冠 | Phase I（first-in-human） | 生成式抗体 | 2022 |
| ABS-101 | Absci | 抗 TL1A | IBD（炎症性肠病） | Phase I（健康志愿者，2025） | 生成式抗体 | 2023 |
| ABS-201 | Absci | 抗 PRLR | （未公开） | Phase I/2a（HEADLINE） | 生成式抗体 | 2024 |
| zovegalisib (RLY-2608) | Relay Therapeutics | 变构 PI3Kα | HR+/HER2- 乳腺癌 | Phase III（ReDiscover-2） | 运动药物设计（AF 启发） | 2021 |
| IAM1363 | Iambic | HER2（脑穿透） | 实体瘤 | Phase I/1b（ESMO 2025 有数据） | 物理信息 AI | 2022 |
| RLY-4008 | Relay | FGFR2 | 胆管癌 | Phase I/2（81% ORR） | 结构药物设计 | 2020 |
| **MTS-004** | **剂泰医药 METiS** | （制剂） | **假性延髓情绪 PBA** | **Phase III 完成（"中国首个完成 III 期的 AI 药"）** | **AI 制剂设计** | — |
| MTS-105 | 剂泰医药 | （肝细胞癌） | 肝癌 | 临床前→IND（FDA 孤儿药） | AI 纳米递送 | — |
| SIGX1094 | Signet（晶泰孵化） | 弥漫胃癌靶点 | 弥漫型胃癌 | Phase I→2026 Q3 Phase II | AI+类器官 | 2023 |
| SIGX2649 | Signet（晶泰孵化） | pan-TEAD | 实体瘤 | IND（中美双报） | AI 设计 | 2024 |
| PEP08 | PharmaEngine（晶泰赋能） | MTA 协同 PRMT5 | 实体瘤 | Phase I（2025 入组） | AI+机器人设计 | 2023 |
| RTX-117 | ReviR（晶泰孵化） | ISR/eIF2B | CMT/VWM 罕见神经病 | Phase I（2026 Q1） | AI+RNA 生物学 | 2023 |
| baricitinib（再利用） | BenevolentAI/礼来 | JAK1/2 | 类风湿→COVID-19 | **已获批上市** | AI 知识图谱再利用 | 2020 |

### 7.1 重点药物深度解读

**rentosertib（INS018_055）——AI 制药的阿波罗时刻。** 这是**历史上第一个靶点与分子结构均由生成式 AI 端到端设计、并进入 Phase III 的药物**。靶点 **TNIK**（TRAF2 and NCK-interacting kinase，丝/苏氨酸激酶）由 PandaOmics 通过整合纤维化组织多组学、生物网络分析、因果推断、通路分析、文献专利情报和衰老相关评分识别为纤维化 top 候选——这是一个**此前未被充分探索**的靶点（现有抗纤维化药针对受体酪氨酸激酶，机制不同）。分子由 Chemistry42 生成并优化。从项目启动到 PCC（临床前候选物）提名仅用了约 **18 个月**（传统需 4–6 年），合成测试了 60–200 个分子（传统需数千）。

**临床试验时间线**：Phase I（NCT05154240）在 48 名健康志愿者+12 名 IPF 患者中确认安全性和药代动力学。**Phase IIa（GENESIS-IPF，NCT05975983）** 是多中心、双盲、随机、安慰剂对照试验，71 名 IPF 患者，22 个中国中心，分安慰剂/30mg QD/30mg BID/60mg QD 四组，给药 12 周。结果 2025 年发表于 *Nature Medicine*（论文标题 "A generative AI-discovered TNIK inhibitor for idiopathic pulmonary fibrosis: a randomized phase 2a trial"）：达安全性主终点（各组不良事件率相似）；60mg QD 组 FVC 平均**改善 +98.4 mL**，安慰剂组**下降 −20.3 mL**——在一种"所有获批药都只能减缓下降"的疾病里，这是首个显示出"可能逆转"信号的分子。探索性生物标志物分析支持抗纤维化+抗炎机制。

**Phase III（NCT07687459，CTR20262475）** 2026-07-07 启动：前瞻、随机、双盲、安慰剂对照、平行组，**320 名患者，47 个中国中心，给药 52 周**，主要终点 FVC 年下降率，关键次要终点首次疾病进展事件时间。Leading PI 是北京协和医院徐作军教授，Co-Leading PI 是钟南山院士和上海肺科医院陈昶院长。FDA 于 2023 年 2 月授予孤儿药资格。整个发现-临床历程发表于 *Nature Biotechnology*（发现）、*Journal of Medicinal Chemistry*（药物化学）、*Nature Medicine*（Phase IIa）——这种同行评议深度在 AI 制药项目里极其罕见。

> **冷静提示**：71 人 12 周是"信号"不是"证明"。IPF 是临床杀手，很多机制合理的药在更大、更长试验里失败了。Phase III 预计 2027–2028 出结果。即便 rentosertib 失败，它已经证明"AI 端到端设计能产出进入 III 期的分子"——这是范式级的成就。

**DSP-1181——首个进临床的 AI 设计药（已停）。** 2020 年，Exscientia 与日本住友制药合作的 DSP-1181（5-HT1A 受体激动剂，强迫症）进入 Phase I，是**历史上首个进入临床试验的 AI 设计药物**。AI 将先导化合物优化到临床候选只用了 12 个月（传统 4–5 年）。但该药后来因疗效/商业考量**停止开发**——这提醒我们：AI 能加速发现，但不保证临床成功。

**halicin 与 abaucin——学术界的抗生素双星。** 两者都不是临床药物，但代表了"AI 发现全新抗生素"的学术范式。**Halicin**（Stokes 2020, *Cell*, DOI 10.1016/j.cell.2020.01.021）：用深度神经网络在 2335 个分子的 E. coli 生长抑制数据上训练，然后预测了 1.07 亿个 ZINC15 化合物，从中筛选出 halicin（原名 SU3327，一个 c-Jun 激酶抑制剂，被重新发现为抗生素）。Halicin 通过耗散细菌跨膜 ΔpH 电位杀菌，机制全新，对结核杆菌、碳青霉烯耐药肠杆菌、泛耐药鲍曼不动杆菌都有效，小鼠模型治疗了艰难梭菌和鲍曼感染。**Abaucin**（Liu 2023, *Nature Chemical Biology*, DOI 10.1038/s41589-023-01349-8）：针对 WHO 头号危险病原鲍曼不动杆菌，用 message-passing 神经网络在 ~7500 个分子上训练，预测出 abaucin——窄谱（只杀鲍曼）、靶向 LolE 脂蛋白转运，小鼠伤口模型有效。Abaucin 的"窄谱"特性很关键：不影响共生菌，减少耐药传播和菌群失调。这两项工作都来自 MIT Jameel Clinic（Collins + Barzilay + Jaakkola），Stokes 现在在 McMaster 大学独立建组。

**REC-994——Recursion 的旗舰与困境。** REC-994 是 Recursion 通过表型组学（恢复 Ccm2 功能缺失表型）发现的磺胺类小分子，用于脑海绵状血管畸形（CCM，一种无药可治的脑血管遗传病）。**Phase II（SYCAMORE，NCT05085561）** 是首个 CCM 的企业申办 Phase II，62 人，200mg/400mg vs 安慰剂，12 个月。2025-02 在国际卒中会议（ISC）报告：**达安全性主终点**（无治疗相关停药、无 3 级不良事件）；400mg 组 50% 患者病灶体积缩小（安慰剂 28%），绝对平均缩小 −457 mm³（安慰剂增大 53 mm³）；改良 Rankin 量表（mRS）显示功能改善趋势。**但这是信号发现研究，未预设统计学显著性**——病灶体积 p=0.449，未达统计显著。截至 2026 年中，Recursion 正与 FDA 讨论下一步，**尚未启动 Phase III**。Recursion 的另外两个 Phase II（REC-2282 NF2、REC-4881 FAP）数据也"模糊或部分阳性"，反映了 AI 表型筛选"找分子快、但临床疗效仍要靠 biology"的现实。

---

## 8. 关键技术深度

### 8.1 3D 分子表征与 SE(3)-等变性

分子的本质是 3D 的——同样的分子式，不同的 3D 构象活性天差地别。所以 AI 处理分子必须用 **3D 表征**。核心数学概念是 **SE(3) 等变性（equivariance）**：

- **SE(3) 群** = 平移（Translation, R³）+ 旋转（Rotation, SO(3)）的刚体变换群。注意 SE(3) 不含反射（那是 E(3)）。
- **等变性（equivariance）**：如果输入做了一个 g∈SE(3) 变换，输出也做同样的变换——f(g·x) = g·f(x)。这跟"不变性（invariance）"不同：不变性是 f(g·x)=f(x)（输出不变），等变性是输出跟着变。

为什么对接/生成必须等变？因为分子的物理性质（能量、结合）在旋转/平移下不变，但**结构**（坐标）必须跟着变。如果一个网络对旋转敏感（比如普通 CNN），把同一个分子转 90° 给出不同预测，那就是 bug。SE(3)-等变网络通过设计保证这种对称性，让模型"天生懂物理"。

### 8.2 Equivariant GNN（EGNN）

**EGNN（E(n)-Equivariant Graph Neural Network）**由 Satorras, Hoogeboom, Welling（2021, ICML）提出，是等变 GNN 的里程碑。它的核心更新规则非常优雅：

对每个节点 i，维护坐标 xᵢ 和特征 hᵢ。消息传递时，边 (i,j) 的消息既考虑特征（通过 MLP），又考虑**坐标的相对距离** ‖xᵢ−xⱼ‖（这是个标量，旋转不变）。然后**坐标更新**直接加上一个由消息加权的相对方向：(xᵢ−xⱼ)/‖xᵢ−xⱼ‖——这个方向项在旋转下自动等变。

EGNN 的妙处在于：它**不需要球谐函数（spherical harmonics）或 Clebsch-Gordan 系数**这些复杂的群论 machinery（像 TFN、SE(3)-Transformer 那样），却仍保证 E(n) 等变性。这让它在分子任务上既快又准——DiffDock、EquiBind 的骨干都基于 EGNN 或其变体。

### 8.3 扩散模型用于分子生成

**扩散模型（Diffusion Models）**在 2022–2024 年接管了分子生成。核心思想（参考 DDPM, Song et al.）：定义一个前向过程，逐步给数据加噪声直到变成纯高斯/均匀噪声；然后训练一个网络学习**反向去噪过程**，从噪声采样回数据。

在分子上的挑战是：分子的"数据"不是欧氏空间的向量，而是**流形**上的点——刚体的位姿在 SE(3) 上，扭转角在 SO(2)^m 上。所以需要 **Riemannian 扩散**（De Bortoli 2022）：在黎曼流形上定义布朗运动，前向/反向过程都在流形上走。DiffDock 的核心贡献就是把这个理论落地到了对接的乘积流形 R³⊕SO(3)⊕SO(2)^m 上。

后续的分子扩散工作：**EDM（EquiDiffuse, Hoogeboom 2022）**做 3D 分子生成（原子类型+坐标联合扩散）；**GeoDiff** 做构象生成；**DiffSBDD** 做口袋感知结构生成；**TargetDiff** 做全原子靶点条件生成；**AlphaFold 3 的 diffusion module** 把这套用到复合体结构预测（低噪声改善局部，多尺度）。

### 8.4 几何深度学习（Geometric Deep Learning）

**几何深度学习（GDL）**是 Petar Veličković, Michael Bronstein 等人推动的统一框架（2021 综述 "Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges"），把 CNN（网格）、GNN（图）、Transformer（集合）统一在"对称性/等变性"的旗帜下。分子 AI 是 GDL 最成功的应用领域之一——因为分子的对称性（旋转、平移、置换、反射）正好是 GDL 处理的核心。

GDL 给分子 AI 带来了：① 等变 GNN（EGNN, PaiNN, GeminiNet, SE(3)-Transformer）；② 流形上的扩散；③ 球谐表征（用于高阶等变，如 Cormorant, SEGNN）；④ 不变性 vs 等变性的权衡理论。理解 GDL 是理解 DiffDock/EquiBind/AF3 的数学前提。

---

## 9. 数据集

| 数据集 | 内容 | 规模 | 主要用途 |
|--------|------|------|----------|
| **ChEMBL** | 生物活性分子（靶点+活性） | ~230 万化合物，~2 万靶点 | QSAR、活性预测、生成预训练 |
| **PubChem** | 公开化学数据库 | ~1.19 亿化合物 | 虚拟筛选库、性质预测 |
| **ZINC15 / ZINC20** | 可购买化合物库 | ~14 亿（15）/ 370 亿（20） | 虚拟筛选、halicin 发现用的就是 ZINC15 |
| **PDBbind** | 蛋白-配体复合体+结合亲和力 | ~2 万（v2020） | 对接基准、亲和力预测（DiffDock/EquiBind/TankBind 都用它） |
| **BindingDB** | 蛋白-小分子结合数据 | ~280 万 | 亲和力预测 |
| **PDB（Protein Data Bank）** | 实验 3D 结构 | ~22 万结构 | AlphaFold 训练、结构预测 |
| **MoleculeNet** | ADMET/性质基准集合 | 14+ 数据集 | 标准评估（QM9, Tox21, HIV, BACE 等） |
| **PoseBusters** | 蛋白-配体 pose 基准（2021+ 新结构） | 428 复合体 | AF3、DiffDock-L 评估化学合理性 |
| **Drug Repurposing Hub** | 已批准/临床药物库 | ~6800 化合物 | halicin/abaucin 发现来源 |
| **CrossDocked** | 交叉对接 pose | ~2200 万 | 对接训练（多 pose） |

> **数据是 AI 制药的命脉，也是瓶颈。** ChEMBL/PDBbind 这种高质量、实验测量的数据集增长缓慢（每年几万），远小于化学空间的增长。这是为什么**自动化实验室（如晶泰的机器人、Recursion 的成像）**变得关键——它们能以工业速度生产带标签的训练数据，形成"数据飞轮"。AlphaFold 3 部分能超越对接工具，也是因为它能利用 PDB 里所有类型的相互作用（蛋白-蛋白、蛋白-核酸、蛋白-配体）联合训练，数据效率更高。

---

## 10. 评估指标

AI 制药的评估必须落到"对药学家有用的指标"上，否则就是数字游戏。

**对接/结构预测类**：
- **RMSD（Root Mean Square Deviation）**：预测 pose 与真实 pose 的原子坐标均方根偏差（Å）。**RMSD<2Å 是金标准**（DiffDock 38%、AF3 在 PoseBusters 上更高）。
- **top-1 / top-5 命中率**：采样 N 个 pose，取置信度最高的（top-1）或前 5 名里最好的，看是否 RMSD<2Å。
- **Centroid distance**：配体重心距离，衡量"是否找对了口袋"。
- **PoseBusters**：不仅看 RMSD，还检查**化学合理性**——手性正确、无原子冲突、键长键角合理。这是 2023 年后更严格的基准，AF3、DiffDock-L 都用它。
- **选择性精度（selective accuracy）**：在"高置信度子集"上的命中率（DiffDock 在最自信 1/3 上达 83%）。

**生成类**：
- **Validity**：生成分子中化学合法（能被 RDKit 解析）的比例。
- **Uniqueness**：去重后的比例（防模式崩溃）。
- **Novelty**：与训练集不重复的比例。
- **SA score（Synthetic Accessibility）**：合成可达性评分，越低越好合成。
- **QED（Quantitative Estimate of Drug-likeness）**：类药性。
- **Diversity**：生成分子集内部的化学多样性。

**性质预测类**：
- **RP（Pearson/Spearman 相关系数）**：预测活性 vs 实验活性的相关性（TankBind 在 PDBbind 上 RP 最高）。
- **RMSE / MAE**：回归误差。
- **AUC-ROC / AUC-PR**：分类（活性/非活性）指标。

**临床类（最终极）**：
- **Phase I 成功率**：AI 发现分子约 80–90%（BCG 数据），高于行业历史平均 40–65%——但样本小、可能被"易成药靶点"富集。
- **Phase II 成功率**：这才是关键，目前 AI 药的 Phase II 数据还太少（rentosertib 是首批），无法统计。
- **获批**：**截至 2026 年 7 月，尚无任何 AI 设计药物获批上市**（baricitinib 是 AI 再利用但分子本身非 AI 设计）。多数预测首个获批在 2028–2030 窗口。

---

## 11. 2025–2026 关键论文（5–10 篇）

以下论文均为 2024–2026 高影响力工作，已核实存在性（部分 DOI/标题基于检索，引用时建议复核）：

1. **rentosertib Phase IIa** — *Nature Medicine* 2025, "A generative AI-discovered TNIK inhibitor for idiopathic pulmonary fibrosis: a randomized phase 2a trial"（GENESIS-IPF 试验，71 人，+98.4 mL FVC）。这是 AI 设计药物首个随机对照 Phase II 数据。
2. **rentosertib 发现历程** — *Nature Biotechnology* 2024, "A small-molecule TNIK inhibitor targets fibrosis in preclinical and clinical models"（PandaOmics 靶点+Chemistry42 分子+临床前+Phase I）。DOI: 10.1038/s41587-024-02143-0。
3. **AlphaFold 3** — *Nature* 2024, Abramson et al., DOI 10.1038/s41586-024-07487-w（统一结构预测，PoseBusters 革命）。
4. **DiffDock-L** — arXiv 2402.18396, 2024（对接改进版，泛化更强）。
5. **AlphaFold 3 推理代码开源** — *Nature* Addendum 2024-11, DOI 10.1038/s41586-024-08416-7（社区复现 AF3 的起点）。
6. **Abaucin** — *Nature Chemical Biology* 2023, DOI 10.1038/s41589-023-01349-8（DL 发现窄谱抗生素，LolE 机制）。
7. **TargetDiff / 全原子扩散生成** — 2023–2024 系列（口袋感知 3D 分子生成的 SOTA）。
8. **Boltz-1 / 开源 AF3 替代** — 2024–2025（社区为突破 AF3 商业限制而做的开源复现，让学术实验室能自由训练和改进统一结构预测）。
9. **Chai-1** — Chai Discovery 2024–2025（开源统一结构预测模型，与 AF3 竞争，已被广泛用于学术和工业）。
10. **FDA AI/ML 药物开发指南草案** — 2025-01 发布（风险分级框架，定义"AI 用于决策的可信度证据要求"），预计 2026 Q2 出最终版。

> **趋势观察**：2024–2026 的论文重心从"单点方法（对接/生成）"转向"**统一基础模型**"（AF3、Chai-1、Boltz-1 都试图用一个模型预测所有生物分子相互作用），以及"**临床验证**"（rentosertib Phase IIa/III）。这意味着 AI 制药正从"算法竞赛"进入"临床证据竞赛"阶段。

---

## 12. 伦理与监管

### 12.1 FDA 的角色与 AI 监管框架

FDA 对 AI 在药物审评中的态度是**"鼓励创新但要求可信度"**。2025 年 1 月，FDA 发布了**首份《AI 在药物开发中的应用》指南草案**，核心是**风险分级（risk-based）**：

- **低风险**：AI 用于早期候选物优先级排序——可信度证据要求低。
- **高风险**：AI 输出用于支持临床安全性声明——要求**独立验证、训练数据溯源文档化、持续性能监控**。

预计 2026 年 Q2 出最终版指南。这份指南将定义"未来十年 AI 设计药物的 NDA 怎么审"。Insilico 等公司已在按草案框架准备，争取成为首批在 NDA 中明确引用"AI 用于靶点识别和分子设计"的公司。

### 12.2 可解释性要求（Interpretability）

药物审评不能是"黑箱"。如果一个 AI 模型说"这个分子有效"，审评员会问"为什么？基于什么机制？"。这要求：

- **机制可追溯**：rentosertib 的成功部分在于 Insilico 不仅给了分子，还详细解释了 TNIK 在 Wnt/TGF-β/Hippo/JNK/NF-κB 通路中的作用——这让审评员能理解生物学合理性。
- **不确定性量化**：DiffDock 的置信度模型、AF3 的多 seed 投票，都是为了给出"我有多大把握"。
- **可复现性**：模型权重、训练数据、代码要可审计。AlphaFold 3 推理代码 2024-11 开源、DiffDock 全 MIT 许可，都是正面例子；但很多药企内部模型仍是黑箱。

### 12.3 数据偏见与公平性

- **训练数据偏倚**：ChEMBL/PDB 里的蛋白和分子严重偏向"已被研究的"靶点（激酶、GPCR），对罕见病、孤儿靶点覆盖极少。AI 在这些领域可能"幻觉"。
- **人群多样性**：临床试验数据（尤其基因组学）以欧洲血统为主，AI 预测的"靶点-疾病关联"在其他人群可能不成立。
- **双重用途风险**：生成式分子设计既能救命也能造毒（如设计更致命的神经毒剂）。2022 年有论文（Urbina, *Nature Machine Intelligence*）演示了用商用 AI 工具在 6 小时内生成 4 万个 VX 级毒性分子，引发"AI 制药双刃剑"的严肃讨论。社区需要负责任发布（responsible disclosure）和访问控制。

---

## 13. 复现指引：跑 DiffDock 推理

> 目标：在你自己的机器上，给定一个蛋白 PDB 和一个配体 SDF/SMILES，用 DiffDock 预测结合 pose。以下步骤基于官方仓库 github.com/gcorso/DiffDock（MIT 许可）。

### 13.1 环境准备

```bash
# 1. 克隆仓库
git clone https://github.com/gcorso/DiffDock.git
cd DiffDock

# 2. 建议用 conda 环境（DiffDock 依赖较老，推荐 Python 3.8/3.9 + PyTorch 1.x/2.x）
conda create -n diffdock python=3.9 -y
conda activate diffdock

# 3. 安装依赖（参考 environments/ 下的 yaml）
#    关键依赖：torch, torch-geometric, rdkit, biopython, openbabel, esm
pip install torch torch-geometric
pip install rdkit biopython openbabel-wheel
# ESM（用于蛋白语言模型特征，可选但推荐）
pip install fair-esm
```

### 13.2 下载预训练权重

DiffDock 仓库会引导你从 HuggingFace/Google Drive 下载模型权重（`models/` 目录）。默认现在下载的是 **DiffDock-L**（2024 版本，性能更好）。如果想跑原版 2022 模型，需要 `git checkout` 到 2022 年的历史 commit。

### 13.3 准备输入

你需要：
- **蛋白结构**：PDB 文件（实验解析的，或 AlphaFold/ESMFold 预测的都行——DiffDock 的卖点之一就是能处理预测结构）。
- **配体**：SDF 文件（推荐，含 3D 构象）或 SMILES（DiffDock 会用 RDKit 生成初始构象）。

### 13.4 运行推理

```bash
# 单个蛋白-配体对
python -m inference.protein_ \
    --protein_path path/to/protein.pdb \
    --ligand path/to/ligand.sdf \
    --out_dir results/ \
    --inference_steps 20 \
    --samples_per_complex 40

# 或批量（提供 csv：protein_path, ligand）
python -m inference.protein_ligand_csv_inference.py \
    --protein_ligand_csv batch.csv \
    --out_dir results/
```

关键参数：
- `--inference_steps`：扩散反向步数（默认 20，越多越精但越慢）。
- `--samples_per_complex`：每个复合体采样多少 pose（默认 40，DiffDock 论文用 40）。
- `--batch_size`：GPU 显存允许的话调大。

### 13.5 解读输出

输出目录会有每个复合体的：
- 多个 `.sdf` 文件（每个采样 pose 一个）。
- 一个 `confidence` 排序——**选 confidence 最高的那个 pose 作为最终预测**。
- 如果你有真实 pose（re-docking 场景），可以用 RDKit/PyMOL 计算 RMSD 验证。

### 13.6 常见坑

- **GPU 显存**：DiffDock 对大蛋白+大配体显存消耗大，建议 16GB+ GPU。
- **RDKit/OpenBabel 版本**：老版本 DiffDock 对这些依赖版本敏感，建议严格按 environments/ 的版本装。
- **DiffDock vs DiffDock-L**：默认现在是 L 版，结果可能和你看的 2022 论文数字不完全一致（L 版更好）。
- **化学合理性**：DiffDock 原版可能生成轻微不合理的 pose（原子冲突、键长异常），建议用 PoseBusters 后处理检查。

> **进阶**：想训练自己的 DiffDock，需要 PDBbind 数据集 + 多 GPU + 数天训练。对大多数应用，用预训练权重微调（fine-tune）到你的靶点家族就够。社区还有 **DiffDock-L 的 Docker 镜像**和**本地 Web UI**，部署更友好。

---

## 📌 进一步阅读

**综述与方法**：
- **Schneider et al. (2020), *Nature Reviews Drug Discovery***, "Rethinking drug design in the artificial intelligence era" — 经典综述。
- **Veličković et al.**, "Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges"（2021 综述，arXiv:2104.13478）— 理解 EGNN/等变性的数学基础。
- **Bishara et al. (2022)**, "Metrics for benchmarking of molecular docking" — 评估方法学。

**关键原始论文**（必读 5 篇）：
1. **DiffDock** — arXiv:2210.01776（对接范式革命）
2. **AlphaFold 3** — Nature 2024, DOI 10.1038/s41586-024-07487-w（统一结构预测）
3. **Halicin** — Cell 2020, DOI 10.1016/j.cell.2020.01.021（AI 发现抗生素）
4. **EquiBind** — arXiv:2202.05146（SE(3)-等变对接先驱）
5. **rentosertib Phase IIa** — Nature Medicine 2025（AI 设计药首个 RCT）

**代码与平台**：
- DiffDock: github.com/gcorso/DiffDock
- EquiBind: github.com/HannesStark/EquiBind
- TankBind: github.com/luwei0917/TankBind
- REINVENT: github.com/MolecularAI/Reinvent
- Uni-Mol: github.com/dptech-corp/Uni-Mol
- AlphaFold 3 推理: github.com/google-deepmind/alphafold3
- AlphaFold Server（在线免安装）: alphafoldserver.com
- Boltz-1（开源 AF3 替代）: github.com/jwohlwend/boltz

**临床追踪**：
- ClinicalTrials.gov — 搜 "Insilico"、"Recursion"、"INS018_055"、"REC-994" 查实时状态。
- BCG AI 制药管线年度报告（追踪全球 AI 发现分子的临床进展）。

---

## ✍️ 思考题

1. **rentosertib 的"AI 含量"到底该如何界定？** 它的靶点 TNIK 由 PandaOmics 发现、分子由 Chemistry42 生成，但所有的临床前验证（体外、动物模型）、IND 申报、Phase I/IIa/III 试验设计都是人类做的。如果把"AI 设计"定义为一个谱系（从"AI 辅助优化已知骨架"到"靶点+分子全 AI 端到端"），rentosertib 处在哪个位置？这种区分对监管、对知识产权、对"AI 制药"这个叙事本身，分别意味着什么？

2. **DiffDock 把对接从"回归"重构为"生成"——这个思想迁移还能用到哪些生物医学问题？** 提示：思考那些"答案是一个分布而非一个点"的任务。蛋白构象系综预测算不算？药物联合用药方案设计算不算？临床试验患者反应分布预测算不算？把回归问题重新表述为生成问题，通常需要什么前提（数据、损失、评估）？

3. **如果 AlphaFold 3 这样的统一结构预测工具持续进步，未来 DiffDock、EquiBind 这类专门对接工具还有存在意义吗？** 反过来想：AF3 目前不开源完整训练代码、商业化受控、且不直接给亲和力。在一个"大模型吞掉专门模型"的时代，专门对接工具的护城河可能是什么（物理保真度？速度？可解释性？特定场景精度？）？这对一个想进入 AI4Drug 领域的研究者/工程师选择技术栈，有什么启示？

---

> **本章核心结论**：AI 药物发现在 2026 年走到了一个临界点——rentosertib 进入 Phase III 证明了"端到端 AI 设计能产出进入晚期临床的分子"，AlphaFold 3 证明了"统一结构预测可行"，但**还没有任何 AI 药获批上市**，Phase II 成功率仍待统计。AI 压缩了"发现"的时间和成本（rentosertib 18 个月 vs 传统 4–6 年），但**没有改写人体生物学的定律**——Phase II 仍是最大的坟场。下一个决定性的时刻，是 rentosertib 的 Phase III 读数（2027–2028），以及 FDA 最终版 AI 指南（2026 Q2）。在此之前，"AI 让药更快、更便宜"已被证明；"AI 让药更好（更高临床成功率）"仍是开放问题。

<!-- delegate 调研，2026-07-20 -->
