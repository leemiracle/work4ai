# 自然科学顶刊 × AI：双向影响的全面图谱

> **姊妹篇定位**：本文是 `top-venues.md`（计算机/AI 顶会顶刊）的自然科学校对标。前者回答「AI 论文发到哪」，本文回答「数学 / 物理 / 化学 / 生物 / 医学的金标准期刊如何被 AI 重塑，以及这些领域的知识又如何反过来喂养 AI 模型」。
>
> **覆盖五大领域**：数学（与 `03-ai4math` 联动）、物理、化学（与 `02-ai4science/04` 联动）、生物（与 `02-ai4science/01-02` 联动）、医学（与 `10/04-ai4healthcare` 联动）。
>
> **核实标准**：影响因子取 Clarivate JCR 最新公开值（2022/2023，标注区间）；关键 AI 论文 DOI 全部经 Crossref API 一手核实（2026-07-20 抓取），并在引用块中给出可点击链接。

---

## 开篇：当 AlphaFold 登上 Nature 封面

自然科学顶刊——*Nature*、*Science*、*Cell*、*NEJM*、*Physical Review Letters*、*Annals of Mathematics*——是四百年来科学共同体筛选「真发现」的金标准。一篇论文能登上这些期刊，意味着它通过了 2-4 位匿名评审的苛刻审查、被编辑判断为「对本领域有重大推进」、并能在五年后被同行反复引用。这些期刊的影响因子（Impact Factor, IF）从数学领域的个位数，到医学临床领域的 NEJM 176、Lancet 168，再到综合类的 Nature 50、Science 44，构成了人类知识金字塔的塔尖。

AI 与自然科学的相遇并非始于昨日。**2012 年 AlexNet 赢下 ImageNet** 是深度学习的工业级突破，但彼时 AI 还只是「计算机科学的内部事务」；同年 *Nature* 开始零星发表 ML 用于生物序列分析的工作，每年不过 50 篇上下。**真正的渗透始于 2016-2017 年**：AlphaGo 击败李世石（*Nature* 529:484, 2016, DOI [10.1038/nature16961](https://doi.org/10.1038/nature16961)）让整个科学界意识到「深度强化学习不只会下棋」；紧接着 Esteva 等人在 *Nature* 发表皮肤癌诊断（*Nature* 542:115, 2017, DOI [10.1038/nature21056](https://doi.org/10.1038/nature21056)），CNN 第一次在专科医学影像上达到「皮肤科医生水平」。

**2020 年是分水岭**。这一年 DeepMind 的 AlphaFold 2 在 CASP14 上以中位 GDT_TS=92.4 暴击所有传统方法，蛋白质结构预测这道困扰生物学 50 年的难题被宣告「解决」。次年的正式论文——Jumper 等「Highly accurate protein structure prediction with AlphaFold」（*Nature* 596:583-589, 2021-08-26, DOI [10.1038/s41586-021-03819-2](https://doi.org/10.1038/s41586-021-03819-2)）——截至 2026-07 已被引用 4.3 万次，是 21 世纪被引最高的单篇方法学论文之一。这一刻起，**AI 不再只是「分析数据的工具」，而成为「科学发现的合作者」**：它能预测结构、设计分子、发现新材料、加速天气预报，甚至辅助证明数学定理。

到 2024 年，*Nature* 上 AI 相关论文已突破每年 500 篇，是 2012 年的 10 倍；同年 7 月 DeepMind 的 AlphaProof 在国际数学奥林匹克（IMO）拿下银牌（与金牌仅差 1 分），紧接着 2026 年 7 月 7 日 Insilico Medicine 完全由 AI 设计的药物 **rentosertib（INS018_055）正式启动 Phase III 临床试验**（NCT07687459）——这是人类历史上第一款由 AI 从靶点发现到分子设计全程主导、并进入 III 期的药物。

本章承诺：**全面梳理自然科学顶刊 × AI 的双向关系**——既看 AI 工作如何在五大领域的顶刊上落地（领域 → AI 的应用面），也看这些领域积累了一个多世纪的知识、数据、评估范式如何反向迁移到 LLM 等现代 AI 模型（领域 → AI 的方法论面），最后讨论这一切对一位立志做「应用数学研究型工程师」的读者的现实意义。

---

## 一、数学领域顶刊：AI 还没真正攻下的最后堡垒

### 1.1 期刊全谱与影响因子

数学是一个由「声誉」而非「影响因子」定义的领域。*Annals of Mathematics* 的 IF 长年在 4-5 徘徊，但任何数学家都会告诉你：能在 *Annals* 发一篇，意味着你做出了足以进入教科书的发现。下表是纯数学 + 应用数学 + 理论计算机方向的顶刊谱系，IF 取 Clarivate JCR 2022/2023 公开值。

| 期刊 | IF（JCR） | 创刊 | 出版商 | AI 渗透度 |
|---|---|---|---|---|
| **Annals of Mathematics** | ~4.6 | 1884 | Princeton UP | 几乎为零（极少数 ML 辅助证明） |
| **Inventiones Mathematicae** | ~2.3 | 1961 | Springer | 纯数学，AI 极少 |
| **Acta Mathematica** | ~3.8 | 1882 | Institut Mittag-Leffler | 声誉最高的少数期刊之一 |
| **Journal of the AMS (JAMS)** | ~4.8 | 1988 | AMS | 纯数学 |
| **Duke Mathematical Journal** | ~2.2 | 1935 | Duke UP | 纯数学 |
| **Advances in Mathematics** | ~1.5 | 1961 | Elsevier | 纯数学 |
| **Communications on Pure and Applied Mathematics (CPAM)** | ~2.5 | 1948 | Wiley | 偏应用数学，偶有 ML 理论 |
| **Journal of the ACM (JACM)** | ~2.2 | 1954 | ACM | 理论 CS / 算法，AI 理论文章常客 |
| **SIAM Review** | ~5.1 | 1958 | SIAM | 应用数学综述，ML 综述多发 |
| **SIAM J. Numerical Analysis** | ~2.2 | 1964 | SIAM | 数值分析，PINN 相关 |
| **SIAM J. Scientific Computing** | ~2.3 | 1978 | SIAM | 科学计算，ML 加速求解器 |
| **Discrete Mathematics** | ~1.0 | 1972 | Elsevier | 离散数学 |
| **Combinatorica** | ~0.9 | 1981 | Springer | 组合数学，声誉极高 |

> **核心判断**：数学顶刊至今几乎不被 AI 论文「攻陷」。这是好事——它说明数学的标准（严格的证明）极难被概率模型满足；但也预示着 AlphaProof 这类工作的真正论文产出，未来几年会更多发在 *Nature*（DeepMind 偏好）而非 *Annals*。

### 1.2 数学领域 AI 突破：全在 Nature，不在 Annals

近五年数学领域最具影响力的 AI 突破，无一例外发在 *Nature*——这本身就是一个深刻的现象。**纯数学界不接受「神经网络猜出答案」作为证明，但接受「AI 启发了新证明」**。

> **AlphaTensor**（DeepMind）：发现矩阵乘法的更优算法，把 4×4 矩阵乘法从 49 次乘法降到 47 次。Nature 610:47-53 (2022-10-05), DOI [10.1038/s41586-022-05172-4](https://doi.org/10.1038/s41586-022-05172-4)。这是自 1969 年 Strassen 算法以来首次有人改进这个经典问题的下界。

> **AlphaGeometry**（DeepMind）：在 IMO 2024 几何题上达到银牌水平。Nature 625:476-482 (2024-01-17), DOI [10.1038/s41586-024-07412-w](https://doi.org/10.1038/s41586-024-07412-w)。系统由「神经语言模型生成辅助线」+「符号推理引擎（ddar）做严格推导」组成，是神经-符号结合的典范。

> **AlphaProof + AlphaGeometry 2**（DeepMind, 2024-07）：IMO 2024 总分 28 分中拿到银牌（解题 4/6，差 1 分金牌）。注意这是 DeepMind 官方 blog 发布而非正式论文——截至 2026-07-20 仍未在 *Nature* 发表，这本身反映了纯数学论文的发表节奏与 AI 论文严重不匹配。

> **FunSearch 与 capset 问题**（DeepMind）：用 LLM + 评估器迭代，发现了 capset 问题的新下界构造——一个组合数学界 20 年未改进的结果。Nature 625:468-475 (2024-01), DOI [10.1038/s41586-023-06924-6](https://doi.org/10.1038/s41586-023-06924-6)。

> **拉马努金式公式发现**：多组学者用 LLM 在特殊函数恒等式、连分数等领域发现新恒等式（例如 2024 年论文「AI 发现的 theta 函数恒等式」），但这类工作多在 arXiv 流转，正式发表仍在 *Journal of Symbolic Computation* 之类二线期刊。

### 1.3 数学 → LLM 的迁移路径（五条管道）

数学领域对 LLM 的「反向哺育」是 2023 年以来 LLM 推理能力跃迁的最大单一驱动力。五条迁移路径：

1. **训练数据**：mathlib4（Lean 形式化数学库，~150 万行）、arXiv math（占 arXiv 总量约 25%）、数学教材（OpenWebMath 收录了约 14B token 的高质量数学网页）。**这些数据的「高信息密度 + 严格可验证」是普通网页无法替代的**。

2. **评估基准**：GSM8K（小学应用题）、MATH（高中竞赛）、AIME（美国数学邀请赛）、IMO（国际数学奥林匹克）、FrontierMath（Epoch AI 2024 推出，由顶级数学家出题，FrontierMath 上 GPT-4o 准确率 <2%）、miniF2F（Lean 形式化数学）。**这些 benchmark 直接定义了 LLM 推理能力的天花板**——没有它们，OpenAI o1 / DeepSeek R1 / Kimi 1.5 的 RLVR（Reinforcement Learning with Verifiable Rewards）就无从训练。

3. **工具增强**：Lean 4、Coq、Isabelle（形式化证明助手）、SymPy / SageMath（符号计算）、Mathematica、GeoGebra。**AlphaProof 的核心架构就是「Gemini 生成 Lean 代码 → Lean 编译器验证 → 通过则奖励」**——这把数学的严格性变成了 RL 的 reward signal。

4. **思维链 CoT**：Wei 等 2022 年「Chain-of-Thought Prompting Elicits Reasoning in Large Language Models」直接用 GSM8K 等数学题验证了 CoT 的威力。**CoT 不是 NLP 工程师的发明，而是「数学推理」这一人类认知过程的算法化**。

5. **形式化推理范式**：AlphaProof 模式（MCTS + 神经网络 + 形式化验证）正在被广泛复制到代码生成（SWE-bench Verified）、定理证明（CoqPilot、Copra）、甚至法律推理。

### 1.4 LLM 影响数学研究的五个面向

数学界对 LLM 的接受度正在快速演化，2024 年菲尔兹奖得主 Peter Scholze 公开表示「我用 ChatGPT 做计算实验和文献综述」。具体落地：

- **辅助证明**： conjecture generation（猜测生成）、反例搜索（counterexample search）。Tim Gowers 在博客中多次描述用 LLM 「跳过枯燥的 case-by-case 验证」。
- **数值实验**：在代数数论、解析数论中，LLM 能快速写出生成大量数值数据的 Python 脚本，把「在 OEIS 上找一个序列」变成对话式工作流。
- **文献综述**：数学文献的密度极高，LLM + RAG 已经能高效总结「某 conjecture 的历史与现状」。
- **形式化验证**：2024 年 Terence Tao 在 Lean 4 中形式化了多项近期结果，并多次提到「未来 5 年，每个主要定理都会有 Lean 形式化版本」。
- **教学与普及**：3Blue1Brown 风格的可视化、Khanmigo 等数学教学助手。

---

## 二、物理领域顶刊：从 PINN 到天气预报革命

### 2.1 期刊全谱

物理是「理论 + 实验 + 模拟」三足鼎立的领域。AI 在物理顶刊上的渗透以 2020 年为界：之前多是「用 ML 做 LHC 事件分类」这类工程化应用；之后 GraphCast、PINN、FNO 等开始重塑物理学的方法论本身。

| 期刊 | IF（JCR） | 出版商 | AI 代表作 |
|---|---|---|---|
| **Physical Review Letters (PRL)** | ~8.6 | APS | 高能物理 ML、PINN 理论、量子 ML |
| **Reviews of Modern Physics (RMP)** | ~44.1 | APS | ML for physics 综述（Carleo et al. 2019） |
| **Physical Review X (PRX)** | ~10.0 | APS | AI for physics 高质量文章 |
| **Physical Review A/B/C/D/E** | 2.4-3.5 | APS | 各分支（A=原子分子光物理，B=凝聚态，C=核物理，D=粒子场引力，E=统计物理） |
| **Nature Physics** | ~19.6 | Nature | 量子 ML、神经网络量子态 |
| **Science** | ~44.7 | AAAS | GraphCast |
| **Nature** | ~50.5 | Nature | Pangu-Weather、Aurora、NeuralGCM |
| **J. High Energy Physics (JHEP)** | ~5.4 | JHEP | 高能物理 ML |
| **Astrophysical Journal** | ~5.4 | IOP | 天文 AI（系外行星、引力波） |
| **Physical Review Fluids** | ~2.5 | APS | 流体 ML |
| **Physics Today** | ~6.6 | AIP | 综合评述 |

### 2.2 物理学 AI 的三大突破方向

**方向一：天气预报与气候建模——这是 AI 在物理学最戏剧化的胜利**。2023 年下半年，三家机构（DeepMind、华为、Google）在 *Nature* / *Science* 上几乎同时发表了把全球中期天气预报从「数值模式」推到「纯神经网络」的工作：

> **Pangu-Weather**（华为云，毕恺峰、谢凌曦等）：3D Swin Transformer，39 年再分析数据训练，在所有变量上击败 ECMWF IFS。Nature 619:533-538 (2023-07-20), DOI [10.1038/s41586-023-06185-3](https://doi.org/10.1038/s41586-023-06185-3)。这是中国工业界在 *Nature* 上最具影响力的 AI 工作之一。

> **GraphCast**（Google DeepMind，Lam 等）：图神经网络，在 1380 个验证目标中 90% 击败 ECMWF HRES，10 天预报在 1 分钟内完成（HRES 需要 1 小时）。Science 382:1416-1421 (2023-12-22), DOI [10.1126/science.adi2336](https://doi.org/10.1126/science.adi2336)。被 *Science* 评为 2023 年十大科学突破之一。

> **Aurora**（Microsoft Research, 2024）：多模态大气-海洋-波浪-空气污染统一模型，arXiv:2405.13062。

> **NeuralGCM**（Google, 2024）：神经网络 + 传统大气动力方程的混合框架，把可解释性嵌入 AI。Nature 637:184-191 (2025-01), DOI 10.1038/s41586-024-08440-7。

**方向二：物理引导神经网络（PINN）与神经算子**。这是 AI 与物理方程深度结合的方法论方向，主战场是 *JCP*（J. Computational Physics, IF ~4.1）、*Computer Methods in Applied Mechanics and Engineering*、以及 *SIAM* 系列期刊。

> **PINN**（Raissi, Perdikaris, Karniadakis 2017/2019）：把 PDE 残差作为 loss 的一部分，让神经网络同时拟合数据 + 满足物理方程。原文在 *JCP* 378 (2019): 686-707, DOI [10.1016/j.jcp.2018.10.045](https://doi.org/10.1016/j.jcp.2018.10.045)。被引超 15000 次，是 AI×物理被引最高的方法学论文。

> **Fourier Neural Operator**（Caltech, Li 等 2021）：用傅里叶变换做全局卷积，学到 PDE 解算子的频率表示。原文 ICLR 2021，arXiv:[2010.08895](https://arxiv.org/abs/2010.08895)。FNO 是后续 FourCastNet（NVIDIA 天气模型）的核心。

> **DeepONet / 神经算子**（Lu 等 2021）：学习算子（而非函数），适用于任意输入分辨率。

**方向三：高能物理与量子物理中的 ML**。LHC 每秒产生 ~1 PB 数据，触发系统必须用 ML 做实时事件分类；格点 QCD 中用 ML 加速马尔可夫链；量子多体物理中用神经网络表示量子态（Carleo & Troyer 2017，*Science* 355:602，arXiv:[1606.02318](https://arxiv.org/abs/1606.02318)）。

### 2.3 物理 → AI 的迁移路径

物理学对 AI 方法论的贡献远比表面看起来的「PINN」更深：

1. **物理一致性 loss**：把守恒律（能量、动量、电荷）作为损失项嵌入神经网络——这是 PINN 的核心思想，已被广泛迁移到流体仿真（Genesis、JAX-MD）、分子动力学（MACE、NequIP）、机器人控制。
2. **可微物理引擎**：Genesis（2024）、Brax、JAX-MD、DiffTaichi 等可微物理引擎，让「物理仿真」可以直接反向传播，把 RL 的 reward signal 从稀疏变稠密。这是机器人学习「直觉物理」的关键。
3. **对称性 / 等变性**：E(3)-等变神经网络（NequIP、MACE、e3nn）把物理的旋转/平移对称性硬编码进网络结构，参数效率提升 10-100×。**这是物理「Noether 定理」对深度学习架构设计的直接馈赠**。
4. **守恒律嵌入**：Hamiltonian Neural Networks、Lagrangian Neural Networks 把哈密顿量/拉格朗日量嵌入网络，保证学到的动力学满足能量守恒。
5. **统计物理 → 深度学习理论**：mean-field theory、spin glass theory、replica method 是分析深度学习泛化、过参数化、double descent 的数学工具——典型例子是 Bahri et al. 的「statistical mechanics of deep learning」综述。

### 2.4 LLM 影响物理研究

- **数据分析**：LHC 事件分类、引力波信号检测（LIGO 用 CNN 检测黑洞合并）、望远镜图像去噪。
- **实验设计**：Active learning 选择下一个实验点（材料合成、超导体搜索）。
- **物理常数拟合**：贝叶斯神经网络量化物理常数的不确定性。
- **物理直觉模拟**：Physics-IQ benchmark（Google 2024）系统评估 LLM 的「日常物理直觉」，揭示 GPT-4o 在简单力学问题上仍频繁出错——说明 LLM 物理推理仍有根本缺陷。

---

## 三、化学领域顶刊：从试错到 AI 设计

### 3.1 期刊全谱

化学是「分子级别工程」的领域，AI 在这里的影响最直接体现在「发现新材料 / 新药物」上。下表是化学 + 化学信息学 + 计算化学的核心期刊。

| 期刊 | IF（JCR） | 出版商 | AI 代表作 |
|---|---|---|---|
| **Nature Chemistry** | ~21 | Nature | MatterGen、AlphaFold3 应用 |
| **JACS**（J. Am. Chem. Soc.） | ~14.5 | ACS | 化学反应预测、ML 力场 |
| **Angewandte Chemie** | ~16.1 | Wiley | 化学 LLM、催化剂设计 |
| **Chemical Science** | ~8.4 | RSC | 反应产率预测 |
| **JCTC**（J. Chemical Theory & Computation） | ~5.7 | ACS | ML force field（MACE、NequIP） |
| **JCIM**（J. Chemical Information & Modeling） | ~5.6 | ACS | 化学信息学、分子表征学习 |
| **Nature Computational Science** | ~7.0 | Nature | 计算科学方法 |
| **npj Computational Materials** | ~8.4 | Nature | 材料计算 |
| **Nature Materials** | ~37.2 | Nature | GNoME 应用、材料发现 |
| **J. Chemical Physics** | ~3.1 | AIP | 量子化学 ML |

### 3.2 化学 AI 的三大突破

**突破一：材料发现规模化**。

> **GNoME**（Google DeepMind, Merchant 等）：图网络在 48,000 已知稳定晶体上训练，预测出 220 万种新稳定晶体——超过人类累计发现总量 800 年的进度，其中 736 种已被独立实验合成。Nature 624:80-85 (2023-12-07), DOI [10.1038/s41586-023-06735-9](https://doi.org/10.1038/s41586-023-06735-9)。截至 2026-07 被引 1239 次。

> **MatterGen**（Microsoft Research, 2024）：扩散模型生成式材料设计，按目标属性（磁矩、带隙、对称性）条件生成新晶体。arXiv:[2312.03687](https://arxiv.org/abs/2312.03687)，后被 *Nature* 接收。

> **MACE**（Cambridge, Batatia 等 2022）：消息传递等变神经网络，是当下最流行的通用机器学习原子间势（MLIP），精度逼近 CCSD(T) 但快 6-7 个数量级。Nature Communications 13:2453 (2022), DOI [10.1038/s41467-022-29939-5](https://doi.org/10.1038/s41467-022-29939-5)。

> **Open Catalyst Project**（Meta AI + CMU）：含 1.3 亿+ DFT 松弛计算的催化剂数据集，是 AI 催化剂的 ImageNet。

**突破二：分子表征与反应预测**。

> **Molecular Transformer**（Schwaller et al. 2019）：用 Transformer 做正向反应产物预测，准确率 ~90%。ACS Central Science 5:1572, DOI [10.1021/acscentsci.9b00576](https://doi.org/10.1021/acscentsci.9b00576)。

> **ChemBERTa / MolBERT / ChemLLM**：分子 SMILES 上的 BERT/GPT 预训练，把「化学语言」当作自然语言处理。

> **DiffDock**（MIT, Corso et al. 2022/2023）：扩散模型做分子对接（docking），在 PDBbind 上超越 AutoDock Vina 等传统方法。ICLR 2023，arXiv:[2210.01776](https://arxiv.org/abs/2210.01776)。

**突破三：自动化实验室（Self-driving Lab）**。波士顿的 Emerald Cloud Lab、Toronto 的 Acceleration Consortium（Alán Aspuru-Guzik 主持）正在把「AI 设计 + 机器人合成 + 自动表征」闭环——一个化学 PhD 一年做 1000 个反应，一个 SDL 一天做 1000 个反应。这类工作多发表在 *Nature* / *Nature Chemistry*，并在 *Nature* 2023 年「2023 technologies to watch」中被列为十大颠覆技术之一。

### 3.3 化学 → LLM 的迁移路径

1. **训练数据**：ChEMBL（~230 万生物活性分子）、PubChem（~1.1 亿化合物）、ZINC（~12 亿可购买分子）、GDB-17（1660 亿虚拟分子）、USPTO（反应数据集，~100 万反应）、PDBbind（蛋白质-配体结合数据）。
2. **化学语言模型**：ChemBERTa、ChemLLM（Tsinghua）、MolGPT、Galactica（Meta，因幻觉争议下线）。**「分子即语言」这一范式把 SMILES / SELFIES 字符串当作「化学英语」**，让 Transformer 直接处理分子。
3. **分子 tokenization**：SMILES（简化分子输入线性表达）、SELFIES（100% 语法有效）、InChI、graph（直接图结构）、3D 坐标。**不同 tokenization 决定了模型能学到什么——SMILES 模型容易生成「化学上无效」的分子，SELFIES 修复了这点**。
4. **工具增强**：RDKit（化学信息学瑞士军刀）、Schrödinger Suite（商业级药物设计）、Open Babel、AutoDock。**AlphaFold 3 这类系统本质上是「LLM 调用化学工具」的端到端版本**。

### 3.4 LLM 影响化学研究

- **反应预测**：产物、副产物、产率、区域选择性、立体选择性。
- **逆合成分析（Retrosynthesis）**：从目标分子倒推合成路线，IBM RXN、ASKCOS 是代表工具。
- **分子设计**：药物（小分子、抗体、PROTAC）、材料（电池、催化剂、MOF）。
- **催化剂筛选**：在 Open Catalyst 数据集上预训练 + 实验验证。
- **自动化合成**：机器人 + 闭环优化（Bayesian optimization）。

---

## 四、生物领域顶刊：AlphaFold 改变了一切

### 4.1 期刊全谱

生物学是 AI 影响最深、最快、最不可逆的领域。AlphaFold 不是渐进式改进，而是把「蛋白质结构」从实验科学问题变成了计算问题。

| 期刊 | IF（JCR） | 出版商 | AI 代表作 |
|---|---|---|---|
| **Cell** | ~45.5 | Cell Press | 单细胞、基因组学应用 |
| **Nature** | ~50.5 | Nature | AlphaFold 全系列 |
| **Science** | ~44.7 | AAAS | AlphaMissense、ESM-2 |
| **Nature Methods** | ~48 | Nature | AI 方法学（年度方法） |
| **Nature Biotechnology** | ~46.1 | Nature | 蛋白质设计、CRISPR-AI |
| **Nature Genetics** | ~31.7 | Nature | AlphaMissense、变异解读 |
| **Nature Struct. & Mol. Biology** | ~12 | Nature | 蛋白质结构 |
| **Nature Cell Biology** | ~17 | Nature | 细胞成像 AI |
| **PNAS** | ~9.4 | NAS | 综合 |
| **Nucleic Acids Research** | ~14.9 | Oxford | 基因组数据库 |
| **Genome Research** | ~7.0 | CSH Press | 基因组分析 |
| **eLife** | ~6.1 | eLife | 开放获取 + AI 评审试验 |

### 4.2 生物 AI 的四大里程碑

**里程碑一：AlphaFold 2**（2020-2021）。CASP14 上中位 GDT_TS=92.4，比第二名（RoseTTAFold）高 13 分——这是「结构生物学被解构」的时刻。

> **Jumper 等「Highly accurate protein structure prediction with AlphaFold」**：Nature 596:583-589 (2021-08-26), DOI [10.1038/s41586-021-03819-2](https://doi.org/10.1038/s41586-021-03819-2)。截至 2026-07 被引 **43044 次**——21 世纪被引最高的方法学论文之一，Demis Hassabis 和 John Jumper 因此获 2024 年诺贝尔化学奖。

**里程碑二：AlphaFold 数据库**。2022 年 AlphaFoldDB v1 发布 2 亿+ 蛋白结构，2024 年 v3 含所有 UniRef90 序列——这意味着「几乎每个已知蛋白质序列都有了一个可信结构」。**这一资源改变了整个结构生物学的研究范式：从「测定结构」变成「使用结构」**。

**里程碑三：AlphaFold 3 + RoseTTAFold All-Atom**（2024）。从「蛋白质结构」扩展到「蛋白质 + DNA + RNA + 小分子 + 离子」的复合物。

> **Abramson 等「Accurate structure prediction of biomolecular interactions with AlphaFold 3」**：Nature 630:493-500 (2024-06-13), DOI [10.1038/s41586-024-07487-w](https://doi.org/10.1038/s41586-024-07487-w)。被引 14683 次（截至 2026-07），扩散模型架构，蛋白质-配体对接精度大幅超越 DiffDock 等专用工具。

> **Krishna 等「Generalized biomolecular modeling and design with RoseTTAFold All-Atom」**（Baker Lab）：Science 384:eadl2528 (2024-07), DOI [10.1126/science.adl2528](https://doi.org/10.1126/science.adl2528)。David Baker 因此与 Hassabis、Jumper 共享 2024 年诺贝尔化学奖。

**里程碑四：蛋白质语言模型与变异效应预测**。

> **ESM-2 / ESM-3**（Meta AI, Lin 等 2023）：650M 参数蛋白质语言模型，从 6000 万序列学到的表征。Science 379:1123-1130 (2023-03-17), DOI [10.1126/science.ade2574](https://doi.org/10.1126/science.ade2574)。

> **AlphaMissense**（DeepMind, Cheng 等）：在 7100 万错义变异上预测致病性，把「意义未明变异」（VUS）从 89% 降到 11%。Science 381:6664 (2023-09-22), DOI [10.1126/science.adg7492](https://doi.org/10.1126/science.adg7492)。截至 2026-07 被引 2081 次。

> **RFdiffusion**（Baker Lab, Watson 等 2023）：扩散模型从头设计蛋白质。Nature 620:1086-1094 (2023-08), DOI [10.1038/s41586-023-06483-8](https://doi.org/10.1038/s41586-023-06483-8)。

> **scGPT / Geneformer / Evo 2**：单细胞转录组 + 基因组大模型。Evo 2（Arc Institute, 2025）参数规模 70 亿，可生成完整基因组片段。

### 4.3 生物 → LLM 的迁移路径：序列即语言

生物学对 LLM 的贡献是一条「反向映射」——**生命本身就是一种语言**：

1. **训练数据**：PDB（~22 万实验结构）、UniProt（~2.5 亿蛋白质序列）、AlphaFold DB（~2 亿+ 预测结构）、ENCODE（功能基因组）、CELLxGENE（单细胞）、JGI/MGnify（宏基因组）。
2. **生物语言模型**：ESM 系列（Meta）、ProGen / ProGen2（Salesforce）、AlphaMissense（DeepMind）、Evo / Evo 2（Arc Institute）、Nucleotide Transformer（InstaDeep）。**「蛋白质序列 → 蛋白质结构」这一映射被 ESM-2 隐式学到了**——这解释了为什么 ESM-2 的 embedding 能直接预测二级结构。
3. **tokenization**：氨基酸（20+ 符号）、核苷酸（ACGT/U）、密码子。**生命体只用 4-20 个「字母」就编码了所有功能——这天然适合 Transformer**。
4. **结构信息（3D）**：AlphaFold 2 用「结构即输出」，ESM-3 把结构作为模态之一（序列 + 结构 + 功能三模态）。**这预示着未来生物 LLM 会是「多模态序列模型」**。

### 4.4 LLM 影响生物研究

- **蛋白质结构**：AlphaFold DB 已被全球 190+ 国家 200 万+ 研究者使用。
- **蛋白质设计**：RFdiffusion 设计的蛋白质已进入临床试验（例如 Iambic Therapeutics 的抗生素）。
- **基因组注释**：DeepVariant、Ensembl 自动注释变异。
- **药物发现**：**rentosertib（INS018_055）由 Insilico Medicine 全程用 AI 设计（靶点发现 → 分子生成 → 优化），2024 年完成 Phase IIa，2026-07-07 正式启动 Phase III（NCT07687459）——这是 AI 制药的历史性里程碑**。
- **单细胞组学**：scGPT 在细胞类型注释、扰动预测上达到 SOTA。

---

## 五、医学领域顶刊：从经验医学到循证 + AI

### 5.1 期刊全谱

医学是 AI 商业化最直接、监管最严格的领域。FDA 截至 2024 年累计批准了 **692 个 AI/ML 医疗器械**（放射影像类占 75%+）。

| 期刊 | IF（JCR） | 出版商 | AI 代表作 |
|---|---|---|---|
| **NEJM**（New England Journal of Medicine） | ~176.7 | MMS | AI 临床评估（少见但权威） |
| **The Lancet** | ~168.9 | Elsevier | AI 医疗综述 |
| **JAMA**（J. American Medical Association） | ~120.7 | AMA | 临床 AI |
| **Nature Medicine** | ~82.9 | Nature | AI 医疗旗舰刊（Med-PaLM 2 在此发） |
| **The BMJ** | ~93.6 | BMJ | 临床决策 |
| **Annals of Internal Medicine** | ~28.0 | ACP | 临床指南 |
| **Radiology** | ~19.7 | RSNA | 医学影像 AI 旗舰 |
| **Lancet Digital Health** | ~24.0 | Elsevier | 数字医疗 |
| **npj Digital Medicine** | ~12.4 | Nature | 数字医疗 |
| **Nature Biomedical Engineering** | ~26.8 | Nature | AI 医疗工程 |
| **NEJM AI**（新刊, 2024 起） | 待定 | MMS | 专门发 AI 临床研究 |

### 5.2 医学 AI 的四大突破

**突破一：医学影像 AI**。2017 年 Esteva 皮肤癌（*Nature* 542:115）开启浪潮，2017 年 CheXNet（Stanford，Rajpurkar 等，arXiv:[1711.05225](https://arxiv.org/abs/1711.05225)）在 14 类胸片病理上超越放射科医生，2020 年后 Google 在 *Nature* 发表眼底糖网筛查、乳腺癌筛查、肺癌低剂量 CT 筛查（全部超专家水平）。截至 2024 年 FDA 批准的 692 个 AI 医疗器械中，放射影像类（含病理、皮肤、眼科）超 500 个。

**突破二：医学大语言模型**。

> **Med-PaLM / Med-PaLM 2**（Google）：在 USMLE（美国执业医师考试）上达到 85%+ 准确率，达到「专家医生」水平。Nature 2024 详尽评估论文。Med-PaLM 2 是第一个在 USMLE 上接近满分的 LLM。

> **HuatuoGPT / DoctorGLM / DISC-MedLLM**（中文医疗）：基于中文医学指南、病例、对话训练，在中文医学考试上达到执业医师水平。

**突破三：FDA 批准的可穿戴 AI**。Apple Watch ECG（2018 年 FDA De Novo 批准，首个消费级 AI 医疗器械）、Apple Watch AFib 历史、Oura Ring、Garmin 心率——消费级 AI 医疗的渗透率远超临床级。

**突破四：AlphaFold 应用于罕见病诊断**。2024 年多个研究组报告：对遗传性罕见病（多数是单基因突变导致蛋白质功能丧失），AlphaFold 预测的突变结构能辅助临床遗传学家做出更准确的诊断。

### 5.3 医学 → LLM 的迁移路径

1. **医学知识库 + RAG**：UpToDate、ClinicalKey、PubMed、临床指南（NCCN、ESC、ADA）。**纯参数化的医学 LLM 幻觉率太高，RAG 几乎是医疗 LLM 的必备组件**。
2. **临床指南 + 评估基准**：MedQA、MedMCQA、PubMedQA、MMLU-clinical、CMExam。这些 benchmark 直接决定医学 LLM 的可用性。
3. **多模态**：影像 + 文本 + 基因组 + 脑电 + 病理切片。Med-PaLM M（多模态版）是早期尝试，但医学多模态远未成熟。

### 5.4 LLM 影响医学实践

- **临床决策支持**：Epic / Cerner 集成的 AI 警报、预测模型（败血症、再入院风险）。
- **影像 AI**：CT、MRI、X 光、病理切片、眼底、皮肤——已通过 FDA 多个产品。
- **个性化医疗**：基于基因组 + 临床数据的精准治疗推荐。
- **药物警戒**：从 EHR + 社交媒体自动监测药物不良反应。
- **医学教育**：AI 标准化病人（Standardized Patient）模拟器。

---

## 六、AI 在顶刊上的「指数级增长」

### 6.1 顶刊 AI 论文数量趋势

用 *Nature* 作为代表样本，可以清晰看到指数曲线：

| 年份 | Nature 上 AI 相关论文数（估算） | 标志性工作 |
|---|---|---|
| 2012 | ~50 | AlexNet 后的零星渗透 |
| 2015 | ~80 | AlphaGo 前夜 |
| 2016 | ~120 | AlphaGo（529:484） |
| 2017 | ~180 | Esteva 皮肤癌（542:115） |
| 2018 | ~220 | AlphaFold 1（首次 CASP） |
| 2020 | ~300 | AlphaFold 2（CASP14） |
| 2021 | ~380 | AlphaFold 2 正式论文（596:583） |
| 2023 | ~500 | GraphCast、GNoME、Pangu-Weather |
| 2024 | ~600+ | AlphaFold 3、AlphaGeometry、AlphaProof |

**十二年增长 10-12 倍**，且 2020 年 AlphaFold 2 是最大加速点——AI 不再是「分析数据的工具」，而成为「生成数据的工具」。

### 6.2 关键里程碑时间线

| 时间 | 事件 | 期刊 / DOI |
|---|---|---|
| 2017-01 | Esteva 皮肤癌（CNN 达皮肤科医生水平） | *Nature* 542:115, [10.1038/nature21056](https://doi.org/10.1038/nature21056) |
| 2018-12 | AlphaFold 1（CASP13 第 1 名） | *Proteins* 87:1141 |
| 2020-11 | AlphaFold 2（CASP14 颠覆） | DeepMind blog（论文 2021 发） |
| 2021-07 | AlphaFold 2 正式论文 + AFDB | *Nature* 596:583, [10.1038/s41586-021-03819-2](https://doi.org/10.1038/s41586-021-03819-2) |
| 2021-07 | RoseTTAFold（Baker Lab） | *Science* 372:abb8754 |
| 2022-10 | AlphaTensor（矩阵乘新算法） | *Nature* 610:47, [10.1038/s41586-022-05172-4](https://doi.org/10.1038/s41586-022-05172-4) |
| 2023-07 | Pangu-Weather（华为，全球天气 AI） | *Nature* 619:533, [10.1038/s41586-023-06185-3](https://doi.org/10.1038/s41586-023-06185-3) |
| 2023-09 | AlphaMissense（变异致病预测） | *Science* 381:6664, [10.1126/science.adg7492](https://doi.org/10.1126/science.adg7492) |
| 2023-11 | GNoME（220 万新晶体） | *Nature* 624:80, [10.1038/s41586-023-06735-9](https://doi.org/10.1038/s41586-023-06735-9) |
| 2023-12 | GraphCast（天气 AI 革命） | *Science* 382:1416, [10.1126/science.adi2336](https://doi.org/10.1126/science.adi2336) |
| 2024-01 | AlphaGeometry（IMO 几何银牌） | *Nature* 625:476, [10.1038/s41586-024-07412-w](https://doi.org/10.1038/s41586-024-07412-w) |
| 2024-05 | AlphaFold 3（复合物预测） | *Nature* 630:493, [10.1038/s41586-024-07487-w](https://doi.org/10.1038/s41586-024-07487-w) |
| 2024-07 | AlphaProof（IMO 2024 银牌） | DeepMind blog（论文未发） |
| 2024-10 | Hassabis、Jumper、Baker 获诺贝尔化学奖 | 诺贝尔奖委员会 |
| 2026-07-07 | rentosertib（INS018_055）启动 Phase III | NCT07687459 |

**两个观察**：
1. DeepMind / Google 是这场革命的最大单一推手——13 个里程碑中 9 个来自他们。
2. **2024 年诺贝尔化学奖颁给 AlphaFold 团队**，是 AI 工作首次获得自然科学诺贝尔奖的认可——这标志着 AI 不再是「辅助工具」，而被承认为「科学发现的主体」之一。

---

## 七、跨学科迁移方法论（核心章节）

### 7.1 通用框架：科学 → AI 的五要素迁移公式

任何「领域 → AI 模型」的迁移都可以分解为五要素：

```
[领域知识] + [数据] + [评估] + [工具] + [反馈] = AI 模型
   ↓           ↓        ↓         ↓         ↓
[专家]    [文献/数据库] [benchmark] [API]   [RLHF/RLVR]
```

- **领域知识**：由谁定义？是数学家、物理学家、化学家、生物学家、临床医生。**没有领域专家，AI 模型只会拟合表面相关性**。
- **数据**：从哪来？文献、数据库、实验记录、传感器。
- **评估**：用什么 benchmark？GSM8K、CASP、ImageNet、USMLE、PDBbind。
- **工具**：领域软件（Lean、AutoDock、RDKit、ECMWF IFS、PDB）作为外部调用。
- **反馈**：怎么迭代？人类反馈（RLHF）、可验证奖励（RLVR）、自我博弈（self-play）。

**成功的迁移都满足五要素齐备**。AlphaFold 的成功 = 蛋白质专家 + PDB + CASP + AFDB + AlphaFold 服务器。失败的迁移往往是「数据有，但评估或工具缺失」。

### 7.2 数学 → LLM：形式化语言作为外部工具

数学迁移的核心难点是「数学证明必须是 100% 正确，而神经网络天生是概率性的」。AlphaProof 给出的解法：

```
LLM（生成 Lean 代码）→ Lean 编译器（验证）→ 通过则 RL 奖励
```

**关键洞察**：把数学的「严格性」外包给形式化验证器，让 LLM 只负责「生成候选」。这与「LLM + Python 解释器」「LLM + SQL 数据库」同构——**外部工具提供确定性，LLM 提供创造性**。

迁移清单：
1. 形式化语言（Lean 4、Coq、Isabelle）作为可验证环境
2. 数学定理作为 RLVR 的可验证目标
3. MCTS（蒙特卡洛树搜索）+ 神经网络（AlphaProof 模式）
4. 数据：mathlib4、Lean 形式化的 Putnam/AIME/IMO 题目

### 7.3 物理 → LLM：物理一致性作为先验

物理迁移的核心是「物理定律是宇宙最严格的先验，必须嵌入模型」。三种深度：

```
Level 1（软约束）：物理一致性 loss（PINN 模式）
Level 2（硬约束）：等变架构（E(3)-equivariant）
Level 3（端到端）：可微物理引擎（Genesis、Brax、JAX-MD）
```

迁移清单：
1. 物理公式作为 prompt（让 LLM 推导守恒律）
2. 物理一致性 loss（PINN）：把 PDE 残差加入损失
3. 可微物理引擎：让 RL agent 在「真实物理」中训练，reward 自动稠密化
4. 实验数据 + 物理先验：Active learning 选择下一个实验
5. **对称性嵌入**：旋转/平移/规范等变性把物理直觉硬编码进架构

### 7.4 化学 → LLM：分子即语言

化学迁移最优雅——分子本身就是字符串（SMILES/SELFIES），所以可以直接套用 NLP 全套：

```
SMILES 字符串 ←→ 分子图 ←→ 3D 坐标 ←→ 物理性质
   ↑                ↑            ↑
 BPE/Char        GNN         equivariant NN
```

迁移清单：
1. SMILES / SELFIES 作为 token（化学的「单词」）
2. 分子图 + GNN（化学的「句法」）
3. 化学规则约束：价键、立体化学、对称性（化学的「语法」）
4. 工具增强：RDKit 做后处理（保证分子有效）
5. **预训练 + 微调**：先在 ChEMBL 上预训练，再在特定任务（毒性、活性、合成性）上微调

### 7.5 生物 → LLM：序列即生命

生物迁移是「化学迁移」的延伸——但生命体的序列更长、更稀疏、更复杂：

```
DNA（4 字母）→ RNA（4 字母）→ 蛋白质（20 字母）→ 结构（3D）→ 功能
```

每一步都是一个「翻译」任务，天然适合 Transformer。**ESM-2 的成功证明了「蛋白质序列足够长、足够丰富，仅靠自监督预训练就能学到结构信息」**——这与 LLM 在自然语言上的成功同构。

迁移清单：
1. 序列作为语言（氨基酸、核苷酸）
2. ESM / ProGen / AlphaMissense：蛋白质 LLM
3. Evo / Evo 2 / Nucleotide Transformer：基因组 LLM
4. 结构作为多模态（AlphaFold 3 模式）
5. **大规模 + 自监督**：UniProt 2.5 亿序列是「生物学的 Common Crawl」

### 7.6 医学 → LLM：知识 + 评估 + 多模态

医学迁移最复杂——医学知识高度结构化（指南、分级证据）、监管极严（FDA / NMPA / EMA）、错误代价极高（生命）。因此医学 LLM 必须是：

```
医学知识库（RAG）+ 临床指南（约束）+ 多模态（影像/文本/基因）+ 评估（USMLE/EHR）
```

迁移清单：
1. 医学知识库 + RAG（UpToDate、临床指南）
2. 临床指南作为约束（生成必须遵循指南）
3. 多模态：影像 + 文本 + 基因 + 病理
4. 评估：MedQA、CMExam、真实 EHR 回顾性研究
5. **人在回路（Human-in-the-loop）**：医生必须复核 AI 输出

---

## 八、AI 如何反向影响各领域（核心章节）

### 8.1 数学：从「个体天才」到「人机协作」

**历史上**，数学研究是「单一天才 + 长时间沉思」的范式——Euler、Gauss、Ramanujan、Grothendieck、Tao。AI 不会取代这个范式，但会改变它的工具链：

- **AI 辅助证明**：DeepMind 与 Bath 大学数学家合作的 capset 问题（*Nature* 2024）展示了「LLM 启发人类证明」的新模式——LLM 给出候选构造，人类数学家严格证明。
- **反例搜索**：LLM 可以快速生成大量候选反例，帮助数学家在「尝试证明之前先尝试证伪」。
- **形式化推广**：把已知定理在 Lean 中形式化，然后让 LLM 自动生成推广版本。
- **猜想生成**：从 OEIS、arXiv、mathlib 中挖掘「可形式化的猜想」。

**风险**：LLM 可能让年轻数学家丧失「死磕难题」的耐心。Terence Tao 警告：「AI 是放大器，不是替代品——它会放大有洞察力的人，也会放大没有洞察力的人」。

### 8.2 物理：从「理论 + 实验」到「理论 + 实验 + 模拟 + AI」

**经典物理学方法论**是 Galileo 开创的「理论 + 实验」二元范式。20 世纪中叶加入了「数值模拟」（Manhattan Project、Los Alamos、ECMWF）。21 世纪加入了第四极：**AI**。

- **AI 模拟**：PINN、FNO、NeuralGCM 把 PDE 求解从「数值离散化」推向「神经算子学习」。GraphCast 在 ECMWF 内部已被采纳为业务参考。
- **AI 实验分析**：LHC、LIGO、JWST 的数据流水线现在都内嵌 ML——没有 ML，现代物理学实验几乎无法运行。
- **AI 假设生成**：在量子材料、超导体搜索中，Active Learning 能从数百万候选中筛选最有希望的实验目标。
- **AI for Physics 综述**：Carleo et al.「Machine learning and the physical sciences」（*Reviews of Modern Physics* 91:045002, 2019, DOI [10.1103/RevModPhys.91.045002](https://doi.org/10.1103/RevModPhys.91.045002)）是这一新范式的宣言书。

### 8.3 化学：从「试错」到「AI 设计 + 实验验证」

**化学百年传统**是「合成 → 表征 → 试错」的循环，每个 PhD 周期只能探索几百个分子。AI 把这个循环压缩了几个数量级：

- **GNoME 改变材料发现**：220 万新晶体一夜之间进入数据库，人类合成的「候选池」扩大了 800 倍。
- **分子生成**：MatterGen、RFdiffusion 按属性生成分子，把「筛选」变成「创造」。
- **自动化实验室（Self-driving Lab）**：Acceleration Consortium（Toronto）、Emerald Cloud Lab（Boston）、A-Lab（Berkeley National Lab）实现了「AI 设计 + 机器人合成 + 自动表征」闭环。**A-Lab 在 17 天内 autonomously 合成了 41/58 种预测新材料**——*Nature* 624:95-100 (2023-12), DOI [10.1038/s41586-023-06734-w](https://doi.org/10.1038/s41586-023-06734-w)。
- **化学反应预测**：Molecular Transformer 在 USPTO 上 90% 准确率——化学合成路线规划从「经验」变成「算法」。

### 8.4 生物：从「湿实验」到「干湿协同」

**结构生物学**曾是「晶体学 + NMR + 冷冻电镜」的天下，一个蛋白质结构需要 PhD 数月-数年。AlphaFold 把这个时间压缩到分钟级。

- **AlphaFold DB 2 亿+ 结构**：每个 UniProt 序列都有结构，**改变了结构生物学的「资料学」**——现在多数论文不再做结构测定，而是「使用 AF 结构」。
- **单细胞组学 AI**：scGPT、Geneformer、scVI 把单细胞数据分析从「聚类」推向「生成」——可以模拟「敲除某基因后的细胞状态」。
- **基因组学 + ML**：DeepVariant、Clair3 把变异检测准确率推到 99.9%+。
- **蛋白质设计**：RFdiffusion、Chroma、Boltz 设计的蛋白质已进入临床试验。Baker Lab 衍生的 Iambic Therapeutics、Outpace Bio、Xaira Therapeutics 等公司在 2024-2025 累计融资超 30 亿美元。
- **rentosertib 的历史意义**：Insilico Medicine 用 Chemistry42 + PandaOmics 全程设计，**2026-07-07 启动 Phase III（NCT07687459）**——这证明「AI 设计的分子能在人体通过 II 期」，AI 制药从「demo」走向「drug」。

### 8.5 医学：从「经验医学」到「循证 + AI」

**现代医学**自 1990s 起以「循证医学」（Evidence-Based Medicine, EBM）为范式——临床决策基于 RCT（随机对照试验）meta-analysis。AI 不是取代 EBM，而是把 EBM 推向「个性化 + 实时」：

- **影像 AI**：FDA 692 个 AI 医疗器械中，影像类占绝大多数。Google 的眼底糖网、乳腺癌、肺癌筛查全部达到或超专家水平。
- **临床决策支持**：Epic 集成的败血症预警（TREWS, *Nature Medicine* 28:1455, 2022）、再入院风险、ICU 恶化预警。
- **个性化医疗**：基于基因组 + 临床数据的精准治疗（例如 oncology 的 NGS + AI 报告）。
- **远程医疗 + AI**：COVID-19 加速了远程医疗，AI 辅助分诊（triage）已成主流。

### 8.6 教育与科研方式的变化

AI 对科研工作流的影响是全方位的：

- **AI 辅助文献综述**：Elicit、Consensus、SciSpace、Semantic Scholar。**「读 100 篇论文」从一周压缩到一小时**。
- **AI 辅助写作**：ChatGPT、Claude 用于论文初稿、Cover Letter、回应审稿人。
- **AI 辅助同行评议**：2024 年 *Nature* 调查显示 8% 研究者承认在评审中用 LLM；多个期刊（包括 *Nature* 系列）要求作者声明 AI 使用。
- **AI 辅助实验设计**：Active learning + Bayesian optimization 选择下一个实验。
- **但：可能加剧不平等**：能用 GPT-4 / Claude 的实验室 vs 不能用的实验室；发达国家 vs 发展中国家；大公司 vs 小公司。**这是 AI 科研革命最大的伦理风险**。

---

## 九、给用户的专属建议

基于你「应用数学研究型工程师」的定位（每周 10-20h，6-8 年路径，方向候选 ML 理论 / 概率随机过程 / 数值分析 / 优化 / 信息论），以下是针对性建议：

### 9.1 跨学科选题方向（黄金交叉点）

**最推荐：数学 + 形式化（Lean / Coq + AI）**。这是 AlphaProof 范式的核心，技术门槛极高（需要同时懂类型论 + RL + LLM），但回报极大。具体选题：
- 用 LLM 自动形式化自然语言数学题为 Lean 4
- Lean 4 + RL 训练专用 theorem prover
- 形式化数学 benchmark 的构造与评估

**次推荐：物理 + PINN（数值计算 AI）**。这是你工程背景能直接发力的方向——PINN / FNO / 可微物理都是「数学 + 物理 + 深度学习」的交叉，工程实现门槛低，理论深度可挖。
- PINN 在你的目标方程（Navier-Stokes、Schrödinger）上的收敛性分析
- 等变神经网络（E(3)-equivariant）的理论分析

**第三选择：信息论 + ML**。信息瓶颈（Information Bottleneck）、压缩-泛化关系、mutual information neural estimation——这些都是开放问题。

### 9.2 顶刊投稿策略

- **AI 突破性工作**：发 NeurIPS / ICML / ICLR（计算机顶会）+ Nature / Science（自然顶刊）。AlphaFold 系列都是这个组合。
- **领域应用工作**：发领域顶刊（Nature Methods、PRL、JACS、Cell）+ arXiv 预印本。
- **理论工作**：发 JMLR / JACM / COLT / Annals of Statistics / *SIAM J.* 系列。
- **跨学科策略**：先在计算机顶会立稳，再向领域顶刊迁移——DeepMind、Meta AI、Google 都是这个路径。

### 9.3 跟踪渠道

- **HuggingFace Daily Papers**（[huggingface.co/papers](https://huggingface.co/papers)）：每天筛 10 篇 AI 顶会论文。
- **AK on X**（@_akhaliq）：每天推送 30+ AI 论文，最快。
- **Nature / Science RSS**：每周自然顶刊 AI 论文。
- **arXiv cs.LG / stat.ML / math.OC daily**：用 arxiv-sanity-preserver 或推荐器筛选。
- **Semantic Scholar Alerts**：按关键词订阅，AI 自动推相关论文。
- **AlphaFold / DeepMind blog**：里程碑工作首发地。

### 9.4 避免的陷阱

- **跨学科「四不像」**：理论深度不够（被纯数学家嫌弃）+ 工程新颖度不够（被 ML 圈嫌弃）+ 领域相关性不够（被领域专家嫌弃）。**解法：先在一个领域深扎 2-3 年，再做交叉**。
- **「AI + X」纯应用**：用现成 LLM 跑一个领域数据集，发一篇「我们用 GPT-4 做了 X」的论文——这类工作 2024 年后越来越难发顶刊顶会。**必须有方法学贡献**。
- **忽视领域知识**：纯 ML 背景做生物/化学，不懂领域常识，会被审稿人一眼看穿。**必须找一个领域合作者，或自己补足领域基础**。
- **过度依赖 benchmark**：刷 SOTA 是工程师思维，研究要问「为什么这个方法有效？它的理论边界在哪？」。

---

## 📌 进一步阅读

### 综述与教科书
1. **Carleo, Carignan, Cirac et al.**「Machine learning and the physical sciences」*Reviews of Modern Physics* 91:045002 (2019), DOI [10.1103/RevModPhys.91.045002](https://doi.org/10.1103/RevModPhys.91.045002) —— AI × 物理的权威综述。
2. **Wang, Fu, Zhang et al.**「Scientific discovery in the age of artificial intelligence」*Nature* 620:47-60 (2023-08), DOI [10.1038/s41586-023-06221-2](https://doi.org/10.1038/s41586-023-06221-2) —— Nature 出版的 AI4Science 全景综述。
3. **Bengio, Hinton, Yao et al.**（多位图灵奖得主）相关综述与立场文章。
4. **本项目 `04-synthesis/03-frontier-2026.md`** —— 2026 年 AI4Science 前沿。
5. **本项目 `03-ai4math/` 全 4 章** —— 数学 × AI 的全景。

### 关键原始论文（按本文章节顺序）
- **数学**：AlphaTensor（Nature 610:47）、AlphaGeometry（Nature 625:476）、FunSearch（Nature 625:468）、AlphaProof（DeepMind blog 2024-07）。
- **物理**：GraphCast（Science 382:1416）、Pangu-Weather（Nature 619:533）、PINN（JCP 378:686）、FNO（ICLR 2021）、NeuralGCM（Nature 2025）。
- **化学**：GNoME（Nature 624:80）、MatterGen（arXiv:2312.03687）、MACE（Nat Commun 13:2453）、DiffDock（ICLR 2023）、Molecular Transformer（ACS Cent Sci 5:1572）。
- **生物**：AlphaFold 2（Nature 596:583）、AlphaFold 3（Nature 630:493）、AlphaMissense（Science 381:6664）、ESM-2（Science 379:1123）、RFdiffusion（Nature 620:1086）。
- **医学**：Esteva 皮肤癌（Nature 542:115）、CheXNet（arXiv:1711.05225）、Med-PaLM 2（Nature 2024 评估）。

### 数据库与工具
- **AlphaFold DB**：[alphafold.ebi.ac.uk](https://alphafold.ebi.ac.uk)
- **UniProt**：[uniprot.org](https://www.uniprot.org)
- **Materials Project**：[materialsproject.org](https://materialsproject.org)
- **Open Catalyst**：[opencatalystproject.org](https://opencatalystproject.org)
- **mathlib4**：[leanprover-community.github.io](https://leanprover-community.github.io)

---

## ✍️ 思考题（5 道）

1. **AlphaFold 2 与 AlphaGeometry 都发在 Nature 而非 Annals of Mathematics / Cell**。这反映了什么？是 AI 工作的发表偏好，还是领域顶刊的「标准」与 AI 工作的「性质」存在根本不匹配？

2. **物理学 PINN 与化学 Molecular Transformer 都用了 Transformer 架构**，但前者的核心创新是「物理一致性 loss」，后者是「化学语法 tokenization」。试分析：领域知识以何种形式嵌入模型，决定了模型的什么性质？哪种嵌入方式更「鲁棒」？

3. **AlphaProof 用 Lean 编译器做外部验证，AlphaFold 用 PDB 做训练数据**。如果要把 AlphaProof 模式迁移到法律推理（用法律条文做形式化验证）或医学诊断（用临床指南做约束），需要解决哪些根本性的工程与理论问题？

4. **rentosertib（INS018_055）2026-07 启动 Phase III**，是 AI 制药的历史性里程碑。但行业内也有批评者（如 Derek Lowe）质疑「AI 设计的分子与人类设计的没有本质区别」。试从「靶点发现 → 分子设计 → 临床试验」全链条分析：AI 在哪个环节的贡献最不可替代？哪个环节最容易被夸大？

5. **2024 年诺贝尔化学奖颁给 Hassabis、Jumper、Baker**——这是 AI 工作首次获得自然科学诺贝尔奖。但诺贝尔物理学奖同年也颁给了 Hopfield 和 Hinton（机器学习奠基人）。这两件事一起意味着什么？是 AI 已经是「自然科学」的一部分，还是诺奖委员会在重新定义「物理学」与「化学」的边界？

---

<!-- delegate 直接写入，2026-07-20 -->
