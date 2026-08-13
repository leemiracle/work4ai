# 资源清单 §03 · 经典论文精读清单（P1）

> **为什么读论文**：项目 md 是教材（5-20 年前的成熟知识）。专家活在**今天的 arXiv**。不会读论文 = 永远在别人消化的二手知识里打转。这份清单是"从教材走向研究"的桥梁。
>
> **⚠️ 铁律**：以下论文的**标题、作者、年份**我确信，但 **arXiv ID 绝不凭记忆**（人记忆错误率 30-50%）。需要精读某篇时，让 AI 用 `webfetch` 抓 arXiv abs 页核实，或去 INSPIRE-HEP / PROLA /期刊官网查。
>
> **配套**：[EXPERT_PATH_2026.md §4.3](../EXPERT_PATH_2026.md)

---

## §0 怎么读论文（方法论）

### 三遍读法（S. Keshav "How to Read a Paper"）
1. **第一遍（5 分钟）**：标题/摘要/引言/结论/图表。判断值不值得读。
2. **第二遍（1 小时）**：通读，不懂的细节先跳过。记下关键词、找参考文献。
3. **第三遍（4-5 小时）**：深度读，尝试复现推导，找漏洞，和自己工作对比。

### 三个层次
- **了解**：知道这篇论文做了什么（第一遍）
- **理解**：能给别人讲清楚方法（第二遍）
- **掌握**：能复现关键结果（第三遍）

### 工具
- **Zotero / Mendeley**：论文管理
- **Notion / Obsidian**：读书笔记
- **arXiv vanity / ar5iv**：arXiv 论文 HTML 渲染（易读）
- **Semantic Scholar / Connected Papers**：找相关论文、引用图谱

---

## §1 量子力学基础（10 篇，必读）

| # | 论文 | 为什么必读 | 难度 |
|---|------|----------|------|
| 1 | **Einstein, Podolsky, Rosen (1935)** *Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?* | EPR 悖论，质疑量子力学完备性的开山之作 | ★★ |
| 2 | **Bell (1964)** *On the Einstein Podolsky Rosen Paradox* | **贝尔不等式**——证明局域隐变量理论可被实验排除。物理学最重要的论证之一 | ★★★ |
| 3 | **CHSH (1969)** *Proposed Experiment to Test Local Hidden-Variable Theories* | Bell 不等式的实用形式（CHSH）| ★★ |
| 4 | **Aspect, Dalibard, Roger (1982)** *Experimental Test of Bell's Inequalities* | **第一次**用钙原子级联辐射验证 Bell，量子非局域性实锤 | ★★ |
| 5 | **Hensen et al. (2015)** *Loophole-free Bell inequality violation* | 第一次同时关闭所有漏洞的 Bell 实验 | ★★★ |
| 6 | **Everett (1957)** *"Relative State" Formulation of Quantum Mechanics* | 多世界诠释。学位论文，被忽视 20 年后成主流之一 | ★★★ |
| 7 | **Zurek (2003)** *Decoherence, einselection, and the quantum origins of the classical* | 退相干——为什么宏观世界看起来经典 | ★★★ |
| 8 | **Dirac (1939)** *A new notation for quantum mechanics* | bra-ket 记号引入（短文，必读）| ★ |
| 9 | **Feynman (1948)** *Space-time approach to non-relativistic quantum mechanics* | **路径积分**的诞生 | ★★★ |
| 10 | **Wigner (1961)** *Remarks on the mind-body question* | "Wigner 的朋友"思想实验，量子测量与意识 | ★ |

---

## §2 统计物理（10 篇，必读）

| # | 论文 | 为什么必读 | 难度 |
|---|------|----------|------|
| 11 | **Boltzmann (1877)** *Über die Beziehung...* | 熵 = log W 的诞生（$S = k_B \ln W$）。可读德语原文或英译 | ★★ |
| 12 | **Gibbs (1902)** *Elementary Principles in Statistical Mechanics* | 系综理论奠基（书）| ★★★ |
| 13 | **Wilson (1971)** *Renormalization Group and Critical Phenomena* | **重整化群**——20 世纪理论物理最伟大进展之一，Wilson 据此拿 1982 诺奖 | ★★★★ |
| 14 | **Kadanoff (1966)** *Scaling laws for Ising models* | 重整化群思想的先驱 | ★★★ |
| 15 | **Onsager (1944)** *Crystal Statistics. I. A Two-Dimensional Model* | **2D Ising 模型精确解**——展示相变可以严格处理 | ★★★★ |
| 16 | **Landauer (1961)** *Irreversibility and Heat Generation in Computing* | **Landauer 原理**：擦除 1 bit 至少耗散 $kT\ln 2$ 热量。"信息是物理的" | ★★ |
| 17 | **Jaynes (1957)** *Information Theory and Statistical Mechanics* | 最大熵原理——统计力学与信息论的统一 | ★★★ |
| 18 | **Hopfield (1982)** *Neural networks and physical systems with emergent collective computational abilities* | **Hopfield 网络**——统计物理→神经网络→AI 的起点（**2024 诺奖!**）| ★★ |
| 19 | **Anderson (1972)** *More Is Different* | 凝聚态物理的独立宣言，反还原论。**每个物理学生必读** | ★ |
| 20 | **Wilson & Kogut (1974)** *The renormalization group and the ε expansion* | 重整化群权威综述 | ★★★★ |

---

## §3 凝聚态物理（10 篇）

| # | 论文 | 为什么必读 | 难度 |
|---|------|----------|------|
| 21 | **Bloch (1928)** *Über die Quantenmechanik der Elektronen in Kristallgittern* | **Bloch 定理**——周期势中电子的能带基础 | ★★★ |
| 22 | **Bardeen, Cooper, Schrieffer (1957)** *Theory of Superconductivity* | **BCS 理论**——超导微观机制，诺奖 | ★★★★ |
| 23 | **Landau (1957)** *The theory of a Fermi liquid* | **费米液体理论**——金属的标准模型 | ★★★ |
| 24 | **Anderson (1958)** *Absence of Diffusion in Certain Random Lattices* | **Anderson 局域化**——无序导致的金属-绝缘体相变 | ★★★ |
| 25 | **Kohn & Luttinger (1957)** *Quantum Theory of Electrical Transport Phenomena* | DFT 的思想先驱 | ★★★ |
| 26 | **Kohn & Sham (1965)** *Self-Consistent Equations Including Exchange and Correlation Effects* | **DFT 的实用形式**——你跑 Quantum ESPRESSO 用的就是这个 | ★★★ |
| 27 | **Thouless, Kohmoto, Nightingale, den Nijs (1982)** *Quantized Hall Conductance in a Two-Dimensional Periodic Potential* | **TKNN 公式**——拓扑物相的诞生（Chern 数）。2016 诺奖 | ★★★★ |
| 28 | **Kane & Mele (2005)** *Quantum Spin Hall Effect in Graphene* | **拓扑绝缘体**预测。拓扑物相的现代复兴 | ★★★ |
| 29 | **Haldane (1988)** *Model for a Quantum Hall Effect without Landau Levels* | **Haldane 模型**——不需要磁场的拓扑相。2016 诺奖 | ★★★ |
| 30 | **Berezinskii, Kosterlitz, Thouless (1972-73)** | **BKT 相变**——拓扑相变。2016 诺奖 | ★★★★ |

---

## §4 广义相对论与宇宙学（10 篇）

| # | 论文 | 为什么必读 | 难度 |
|---|------|----------|------|
| 31 | **Einstein (1915)** *Die Feldgleichungen der Gravitation* | **爱因斯坦场方程**的原始发表。GR 的诞生 | ★★★ |
| 32 | **Schwarzschild (1916)** *Über das Gravitationsfeld eines Massenpunktes* | **史瓦西解**——第一个黑洞解，在战壕里算出 | ★★★ |
| 33 | **Penrose (1965)** *Gravitational Collapse and Space-Time Singularities* | **奇点定理**——证明合理条件下奇点必然形成。2020 诺奖 | ★★★★ |
| 34 | **Hawking (1974)** *Black hole explosions?* | **Hawking 辐射**——黑洞会蒸发。量子引力第一线索 | ★★★ |
| 35 | **Hubble (1929)** *A Relation between Distance and Radial Velocity among Extra-Galactic Nebulae* | **宇宙膨胀**的观测发现 | ★ |
| 36 | **Guth (1981)** *Inflationary universe: A possible solution to the horizon and flatness problems* | **暴胀理论**——宇宙早期指数膨胀 | ★★★ |
| 37 | **Abbott et al. (LIGO) (2016)** *Observation of Gravitational Waves from a Binary Black Hole Merger* | **第一次直接探测引力波**。爱因斯坦预言 100 年后成真 | ★★ |
| 38 | **Aghanim et al. (Planck) (2018)** *Planck 2018 results* | 宇宙学参数的精确测量（暗能量 68%, 暗物质 27%, 普通 5%）| ★★★ |
| 39 | **Riess et al. (1998)** *Observational evidence from supernovae for an accelerating universe* | **暗能量**的发现（加速膨胀）。2011 诺奖 | ★★ |
| 40 | **Penrose (1989) 书籍** *The Emperor's New Mind* | 物理学家对意识/Gödel/量子的思辨（不是论文，但启发性极强）| ★★ |

---

## §5 粒子物理与 QFT（10 篇）

| # | 论文 | 为什么必读 | 难度 |
|---|------|----------|------|
| 41 | **Yang & Mills (1954)** *Conservation of Isotopic Spin and Isotopic Gauge Invariance* | **Yang-Mills 理论**——非阿贝尔规范场，标准模型的数学基础 | ★★★ |
| 42 | **Higgs (1964)** *Broken Symmetries and the Masses of Gauge Bosons* | **Higgs 机制**——粒子质量的来源。2013 诺奖 | ★★★ |
| 43 | **Weinberg (1967)** *A Model of Leptons* | **电弱统一理论**——电磁与弱相互作用的统一 | ★★★ |
| 44 | **'t Hooft & Veltman (1972)** *Regularization and renormalization of gauge fields* | 规范理论的可重整化证明。1999 诺奖 | ★★★★ |
| 45 | **Wilson (1974)** *Confinement of quarks* | **格点 QCD** 的思想 + 夸克禁闭 | ★★★ |
| 46 | **Feynman (1949)** *The theory of positrons* | **费曼图**的诞生 | ★★★ |
| 47 | **ATLAS & CMS Collaborations (2012)** *Observation of a new particle in the search for the Standard Model Higgs boson* | **希格斯玻色子的发现**。完成标准模型最后一块 | ★★ |
| 48 | **Minkowski (1977) / Dimopoulos & Georgi (1981)** | **SUSY（超对称）模型**——超出标准模型的最大候选 | ★★★★ |
| 49 | **Polyakov (1981)** *Quantum geometry of bosonic strings* | 弦理论的路径积分方法 | ★★★★ |
| 50 | **Witten (1995)** *String theory dynamics in various dimensions* | **M 理论**——五种弦理论的统一。Witten 据此拿 Fields Medal | ★★★★★ |

---

## §6 AI × Physics（10 篇 — **你的主战场，最重要**）

> ⚠️ 这部分 ID 待核实（记忆易错），用 webfetch 抓 arXiv abs 页或查 Semantic Scholar。

| # | 论文 | 为什么必读 | 难度 |
|---|------|----------|------|
| 51 | **Hopfield (1982)** 同 #18 | **2024 诺奖**。统计物理→神经网络。必读 | ★★ |
| 52 | **Ackley, Hinton, Sejnowski (1985)** *A learning algorithm for Boltzmann machines* | **Boltzmann 机**——能量模型，Hinton 2024 诺奖另一支柱 | ★★ |
| 53 | **Raissi, Perdikaris, Karniadakis (2017-2019)** *Physics-informed neural networks* | **PINN 奠基**——你跑的 `pinn_poisson.py` 就是这个 | ★★ |
| 54 | **Carleo & Troyer (2017) Science** *Solving the quantum many-body problem with artificial neural networks* | **神经网络量子态**——用 RBM 表示波函数 | ★★★ |
| 55 | **Behler & Parrinello (2007) PRL** *Generalized neural-network representation of high-dimensional potential-energy surfaces* | **BPNN**——神经网络势能的诞生 | ★★★ |
| 56 | **Zhang et al. (2018)** DeepMD 系列 | DeepMD-kit——中国主导的大规模神经势能 | ★★★ |
| 57 | **Batzner et al. (2022) Nature Comm.** NequIP | **SE(3)-等变神经势能**——精度 SOTA | ★★★ |
| 58 | **Batatia et al. (2022)** MACE | **高阶消息传递等变网络**——2023-2026 主流 | ★★★★ |
| 59 | **Merchant et al. (2023) Nature** GNoME | **DeepMind 用 ML 发现 220 万新晶体**——材料发现的 AlphaGo 时刻 | ★★ |
| 60 | **Jumper et al. (2021) Nature** AlphaFold 2 | **蛋白质结构预测革命**——从序列到结构 | ★★★ |

---

## §7 必读综述（5 篇，建立全貌）

| # | 综述 | 为什么 |
|---|------|--------|
| 61 | **Anderson (1972) Science** 同 #19 | 一篇 4 页文章胜过一本教材 |
| 62 | **Karniadakis et al. (2021) Nature Reviews Physics** *Physics-informed machine learning* | PINN 的权威综述 |
| 63 | **Cardy (1996)** *Scaling and Renormalization in Statistical Physics*（书/讲义）| 重整化群的最佳入门 |
| 64 | **Weinberg (1977) Scientific American** *The Forces of Nature* | 大统一理论的科普级综述，物理品味教科书 |
| 65 | **Wilczek (2016) Nature** | 拓扑物相的诺奖综述 |

---

## §8 诺贝尔演讲（品味来源，每年看一遍）

Nobel Prize 官网所有讲座**免费**（文字+视频）。强烈推荐：

| 年份 | 得主 | 必看理由 |
|------|------|---------|
| 2024 | **Hopfield & Hinton** | 统计物理→神经网络→AI 的完整故事 |
| 2022 | Aspect, Clauser, Zeilinger | Bell 不等式与量子信息 |
| 2020 | Penrose, Genzel, Ghez | 黑洞理论与观测 |
| 2016 | Thouless, Haldane, Kosterlitz | 拓扑物相 |
| 2013 | Higgs, Englert | 希格斯机制 |
| 1998 | Laughlin, Störmer, Tsui | 分数量子霍尔效应 |
| 1982 | Wilson | 重整化群 |
| 1965 | Feynman, Schwinger, Tomonaga | QED |

**看法**：先读 Popular Science 演讲（通俗版），再读 Advanced 演讲（技术版）。

---

## §9 论文跟踪渠道（建立每日/每周习惯）

| 渠道 | 内容 | 频率 |
|------|------|------|
| **arXiv listings** `arxiv.org/list/cond-mat/recent` | 每天 new submissions | 每日 15 分钟 |
| **INSPIRE-HEP** `inspirehep.net` | 粒子/理论论文库 + 引用网络 | 每周 |
| **Physics Today** | 物理学家必读杂志 | 每月 |
| **Nature Physics / PRL** | 顶级期刊 | 每周扫标题 |
| **KITP online** `online.kitp.ucsb.edu` | Santa Barbara seminar 录像 | 每周 |
| **Perimeter Recorded Seminar Archive** | PI 所有 seminar 免费 | 每周 |
| **Physics Stack Exchange** | 同行讨论 | 每日 |
| **Twitter/X 物理圈** | @seanmcarroll @johncarlosbaez @_akhaliq @GoogleDeepMind | 每日 |
| **AK (@_akhaliq)** | 每天推送 HuggingFace Daily Papers + AI 论文 | 每日 |

---

## §10 你的 90 天论文精读计划（前 12 篇）

按依赖排序，每篇做"三遍读"：

| 周 | 论文 | 为什么这个顺序 |
|----|------|--------------|
| 1 | #19 Anderson *More Is Different* | 4 页，建立"涌现"直觉 |
| 2 | #11 Boltzmann 熵公式 | 统计力学的根基 |
| 3 | #18 Hopfield (1982) | **你的主战场起点**，统计物理→神经网络 |
| 4-5 | #2 Bell 不等式 + #4 Aspect 实验 | 量子非局域性，物理学最重要论证 |
| 6 | #16 Landauer 原理 | 信息与物理的桥梁 |
| 7 | #53 Raissi PINN | **配合你跑过的 `pinn_poisson.py`** |
| 8 | #22 BCS | 超导微观机制 |
| 9 | #31 Einstein 场方程 | GR 的诞生 |
| 10 | #41 Yang-Mills | 标准模型数学基础 |
| 11 | #13 Wilson 重整化群 | 20 世纪最伟大理论进展 |
| 12 | #59 GNoME | **你的方向**——AI for Physics 的 AlphaGo 时刻 |

**产出**：每篇写一份精读笔记（结构：核心贡献 / 方法 / 关键公式 / 实验 / 局限 / 与你工作的关系），放 GitHub 或 Obsidian。

---

**完成日期**：2026-08-13
**配套**：[04_research_training.md](04_research_training.md) + [EXPERT_PATH_2026.md](../EXPERT_PATH_2026.md) + [ai_for_physics/](../ai_for_physics/)
