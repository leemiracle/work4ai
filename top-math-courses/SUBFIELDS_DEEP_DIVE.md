# SUBFIELDS_DEEP_DIVE：细分方向深扎指南

> **本章核心**：顶级数学家**必有一个 niche**——一个深到能发顶刊的方向。泛读 10 个方向不如深扎 1 个。这份文档帮你**选方向 + 知道深扎到什么程度**。
>
> 每个方向给：核心问题 / 关键人物 / 必读论文 / 强校 / Open Problems / 与你目标的契合度。

---

## 〇、选方向的原则（先读这个）

### 0.1 "兴趣 × 天赋 × 时代"

Tao 反复强调：选方向要满足三个条件的交集。

| 维度 | 问自己 |
|------|--------|
| **兴趣** | 你读这个方向的论文时是否感到兴奋？卡 3 个月会不会放弃？ |
| **天赋** | 你的思维模式匹配这个方向吗？（代数派 vs 分析派 vs 几何派）|
| **时代** | 这个方向现在是 hot 还是 cold？10 年后还有大问题吗？ |

### 0.2 不要选"已死"的方向

例子（2025-2026 视角）：
- ✅ **Hot**：ML 理论 / 形式化数学（AlphaProof 后）/ 随机矩阵 / 高维概率 / 几何 Langlands / 解析数论
- ⚠️ **温**：经典代数拓扑（Hatcher 后工具成熟，难出大结果）/ 调和分析（经典问题少）
- ❌ **冷或饱和**：经典单变量复分析 / 经典微分方程定性理论

### 0.3 你的画像（应用数学研究型工程师）

基于你的资产（Lean4 + ML 工程 + 数学学习路径），**最适合你的方向**（按契合度）：

| 优先级 | 方向 | 为什么契合你 |
|--------|------|-------------|
| ⭐⭐⭐⭐⭐ | **ML 理论**（泛化 / 优化 / 高维）| 直接用你的 ML 背景 + 数学 |
| ⭐⭐⭐⭐⭐ | **形式化数学 + AI for math** | 你的 Lean4 + AI 是稀缺组合（AlphaProof 方向）|
| ⭐⭐⭐⭐ | **数值分析 / 科学计算** | 应用数学工程师的本职 |
| ⭐⭐⭐⭐ | **随机分析 / 扩散模型数学** | SDE + ML 交叉，扩散模型热 |
| ⭐⭐⭐ | **优化**（非凸 / 分布式）| ML 优化器方向 |
| ⭐⭐⭐ | **信息论**（网络 / 随机矩阵）| 与 ML 紧密 |
| ⭐⭐ | **加性组合**（Tao 方向）| 经典纯数，需要纯数学博士训练 |

---

## 一、ML 理论（Machine Learning Theory）⭐⭐⭐⭐⭐

### 1.1 核心问题

- **泛化**：深度网络为什么在训练误差 0 时还能泛化？double descent？
- **优化**：非凸 SGD 为什么收敛？哪种 landscape 结构决定收敛速率？
- **表达力**：什么函数类神经网络能近似？深度 vs 宽度？
- **隐式正则**：SGD 偏向哪些解？

### 1.2 关键人物 / 学派

| 人 | 机构 | 贡献 |
|---|------|------|
| **Peter Bartlett** | Berkeley | 学习理论带头人 |
| **Mikhail Belkin** | MIT/UCSD | Double descent |
| **Arthur Jacot** | EPFL | Neural Tangent Kernel |
| **Tengyu Ma** | Stanford | 优化与泛化 |
| **Jason Lee** | Princeton | 优化理论 |
| **Andrea Montanari** | Stanford | 高维统计 |
| **Behnam Neyshabur** | Toyotalands | 泛化 |
| **Daniel Soudry / Nati Srebro** | Technion/TTIC | 隐式正则 |

### 1.3 必读论文（奠基）

| 论文 | 年 | 贡献 |
|------|---|------|
| **Belkin et al. "Reconciling modern ML and bias-variance tradeoff"** | 2018 | Double descent（arXiv:1812.11118）|
| **Jacot et al. "NTK"** | 2018 | NTK（arXiv:1806.07572）|
| **Bartlett et al. "Spectrally-normalized margin bounds"** | 2017 | NN 泛化界 |
| **Neyshabur et al.**系列 | 2014-2018 | Path-norm / 隐式正则 |
| **Allen-Zhu, Li, Song**系列 | 2018-2019 | SGD 收敛分析 |
| **Soltanolkotabi et al.** | 2018+ | 过参数优化 |

### 1.4 强校

- **Berkeley**（Bartlett）/ **MIT**（Belkin）/ **Stanford**（Montanari, Tengyu Ma）/ **Princeton**（Jason Lee）/ **TTIC**（Srebro）/ **Technion**

### 1.5 Open Problems（2025-2026）

- 深度网络为什么泛化？机制级的解释（不只是 bound）
- Adam 为什么 work（严格的优化收敛证明）
- Transformer 的数学理论（attention 的几何）
- LLM 的 in-context learning 的理论解释
- LLM scaling laws 的第一性原理推导

### 1.6 你的切入点

```
读 5-10 篇奠基论文（2018-2022）
  ↓
学 Vershynin《High-Dimensional Probability》
  ↓
在 Lean 里形式化一个泛化界（与讲透泛化系列联动）
  ↓
找一个具体问题（如"Adam 收敛"）做小研究
```

---

## 二、形式化数学 + AI for Math ⭐⭐⭐⭐⭐

### 2.1 核心问题

- **形式化**：把数学论文翻译成 Lean / Coq，可机械验证
- **Auto-formalization**：LLM 把自然语言数学自动翻成 Lean
- **AI 猜想生成**：LLM 提出新的数学猜想
- **AI 辅助证明**：LLM 找证明步骤（AlphaProof 方向）
- **大规模协作**：50+ 人用 Lean 协作一个数学项目

### 2.2 关键人物 / 学派

| 人 | 机构 | 贡献 |
|---|------|------|
| **Terence Tao** | UCLA | liquid tensor / PFR / Equational Theories |
| **Kevin Buzzard** | Imperial College | Fermat 形式化 / Lean 教育 |
| **Peter Scholze** | Bonn / MPIM | liquid tensor experiment |
| **Jeremy Avigad** | CMU | 形式化证明理论 |
| **Mario Carneiro** | CMU | Lean 元编程 |
| **Christian Szegedy** | Stanford | 形式化数学 LLM |
| **Wenda Li** | DeepMind | auto-formalization |
| **Geoffrey Irving** | DeepMind | AlphaProof |

### 2.3 必读论文

| 论文 | 年 | 贡献 |
|------|---|------|
| **DeepMind "AlphaProof" Nature paper** | 2025 | IMO 银牌（DOI: 10.1038/s41586-025-09833-y）|
| **Tao "Machine Assisted Proofs"** | 2024 | 综述 |
| **Szegedy "A Promising Path Towards Auto-formalization"** | 2020 | LLM 翻译 |
| **Wu et al. "Autoformalization with LLMs"** | 2022 | arXiv:2205.12615 |
| **Polu & Sutskever "Generative Language Modeling for Automated Theorem Proving"** | 2020 | arXiv:2009.03393 |
| **First et al. "Baldur"** | 2023 | auto-repair |
| **Equational Theories Project paper** | 2025 | 大规模协作 |

### 2.4 强校 / 机构

- **Imperial College**（Buzzard）/ **CMU**（Avigad）/ **Bonn**（Scholze）/ **UCLA**（Tao）/ **DeepMind** / **Stanford**（Szegedy）

### 2.5 Open Problems

- de Bruijn factor < 1 的工具链（Tao 预测 5-10 年）
- Auto-formalization 准确率从 ~30% → 95%
- AI 解奥数 IMO 金牌
- 形式化 Fermat 大定理（Buzzard 5 年计划）
- 形式化数学的"GitHub"（collaborative math at scale）

### 2.6 你的切入点（**最大杠杆**）

```
完成讲透Lean4数学 系列
  ↓
Clone Tao Analysis I Lean companion，填 sorry
  ↓
给 mathlib 提 PR（good first issue）
  ↓
参与 Equational Theories 类项目
  ↓
关注 AlphaProof 开放资源（miniF2F / formal-conjectures）
  ↓
自己的形式化项目（如形式化某个 ML 理论论文）
```

---

## 三、数值分析 / 科学计算 ⭐⭐⭐⭐

### 3.1 核心问题

- **数值稳定性**：浮点数误差如何传播？哪些算法稳定？
- **大规模计算**：百万维 / GPU / 分布式的数值方法
- **快速算法**：FFT / 快速矩阵乘 / random sketching
- **科学机器学习**：物理约束的 NN（PINN）/ Neural ODE

### 3.2 关键人物

- **Lloyd Trefethen**（Oxford）/ **Nick Higham**（Manchester，数值稳定性）/ **Nick Trefethen**（同样）/ **Emmanuel Candès**（Stanford，压缩感知）/ **Tao**（随机矩阵 / 压缩感知）/ **Stephen Boyd**（凸优化）/ **Jorge Nocedal**（优化）

### 3.3 必读论文

- **Candès, Romberg, Tao 2006**（压缩感知，robust uncertainty principle）
- **Donoho 2006**（compressed sensing）
- **Trefethen 系列**（pseudospectra）
- **Highham《Functions of Matrices》**

### 3.4 强校

- **Oxford**（Trefethen）/ **Manchester**（Higham）/ **Stanford**（Candès, Boyd）/ **MIT**（MIT NA group）/ **Caltech** / **ETH**（NA + 科学计算）

### 3.5 Open Problems

- 随机化数值线性代数（RandNLA）
- Neural ODE / PINN 的收敛性理论
- 高精度科学计算的 GPU 友好算法
- Tensor 算法（TT / Tucker / tensor train）

---

## 四、随机分析 / 扩散模型数学 ⭐⭐⭐⭐

### 4.1 核心问题

- **SDE 的数值解**：Euler-Maruyama / Milstein / 高阶
- **反向 SDE**：扩散模型的数学基础
- **大偏差理论**：罕见事件的概率
- **随机控制**：RL 的数学基础

### 4.2 关键人物

- **Song Yang**（Stanford，扩散模型）/ **Stefano Ermon**（Stanford）/ **Jascha Sohl-Dickstein**（Google）/ **Max Welling**（Amsterdam）/ **Bernt Øksendal**（Oslo，SDE 教材作者）/ **Ioannis Karatzas**（Columbia）

### 4.3 必读论文

- **Song et al. "Score-Based Generative Modeling through SDEs"**（arXiv:2011.13456）
- **Ho et al. "DDPM"**（arXiv:2006.11239）
- **Kingma et al. "Variational Diffusion Models"**（arXiv:2107.00630）

### 4.4 强校

- **Stanford** / **NYU**（Courant）/ **Columbia** / **Princeton** / **Bonn**

### 4.5 Open Problems

- 扩散模型的收敛速率（理论上）
- 流匹配（Flow Matching）vs 扩散的数学关系
- SDE 与 PDE 的数值稳定性

---

## 五、纯数学方向（速览）

如果你最终想做纯数学，这些是各方向的金标准路径：

### 5.1 代数几何（Pure 数学最大的方向）

- **起点**：Harris *Algebraic Geometry* + Vakil notes
- **核心**：Hartshorne + EGA
- **前沿**：几何 Langlands / derived algebraic geometry / mirror symmetry
- **强校**：Princeton / IAS / Berkeley / MIT / Columbia / Harvard / Stanford

### 5.2 代数数论

- **起点**：Marcus *Number Fields* + Milne notes
- **核心**：Neukirch + Lang
- **前沿**：Langlands program / BSD conjecture / IUT（Mochizuki）/ p-adic Hodge theory
- **强校**：Princeton / IAS / Harvard / Berkeley / Bonn / Oxford

### 5.3 解析数论

- **起点**：Apostol
- **核心**：Iwaniec & Kowalski
- **前沿**：Riemann 假设 / bounded gaps（Yitang Zhang, Maynard）/ 大 sieve
- **强校**：Princeton / IAS / UCLA（Tao）/ Oxford / Bonn

### 5.4 表示论

- **起点**：Fulton & Harris
- **核心**：Serre + representation of Lie groups (Knapp)
- **前沿**：geometric representation theory / Langlands
- **强校**：MIT / Harvard / Chicago / Berkeley / IAS

### 5.5 微分几何 / 几何分析

- **起点**：Do Carmo
- **核心**：Petersen / Jost
- **前沿**：Ricci flow（Perelman）/ minimal surfaces / SYZ / 6th Millennium Problem（Hodge）
- **强校**：Princeton / Stanford / Berkeley / MIT / IAS / Columbia

### 5.6 偏微分方程 / 几何分析

- **起点**：Evans
- **核心**：Gilbarg-Trudinger / Taylor
- **前沿**：Navier-Stokes（Millennium）/ fluid equations blowup（Chen-Hou, Tao 等）/ dispersive PDE
- **强校**：Princeton / IAS / Stanford / Berkeley / MIT / UCLA（Tao）/ Chicago

### 5.7 概率论

- **起点**：Durrett
- **核心**：Karatzas-Shreve / Revuz-Yor
- **前沿**：SLE / random geometry / KPZ / 4D critical phenomena
- **强校**：MIT / Berkeley / Stanford / Cambridge / Courant / UCLA

### 5.8 数学物理 / 几何 Langlands

- **起点**：Arnold *Mechanics* + Frenkel *Langlands》*
- **核心**：Deligne et al. *Quantum Fields and Strings》*
- **前沿**：geometric Langlands（Frenkel, Gaitsgory）/ mirror symmetry / quantum gravity
- **强校**：IAS / Harvard / Berkeley / MIT / Paris / Moscow

---

## 六、选方向的决策树

```
你想做哪种数学？
├─ 应用（解决现实问题）
│   ├─ ML 理论 → §一
│   ├─ 数值 / 优化 → §三、七
│   └─ 形式化数学 → §二
├─ 半应用（数学结构 + 应用）
│   ├─ 概率 / 随机分析 → §四、5.7
│   ├─ 信息论 / 编码 → §八
│   └─ 数学物理 → 5.8
└─ 纯数学（自身美）
    ├─ 代数派 → 5.1 / 5.2 / 5.4
    ├─ 分析派 → 5.6 / 调和分析
    ├─ 几何派 → 5.5 / 5.8
    ├─ 数论派 → 5.2 / 5.3
    └─ 逻辑/基础 → §九
```

---

## 七、优化（更细节）

略，已在 [`TEXTBOOK_LIBRARY.md`](TEXTBOOK_LIBRARY.md) §七列出。前沿方向：
- 非凸优化（landscape 分析）
- 分布式 / 联邦优化
- 一阶方法的 lower bound
- 在线学习 / bandits

强校：Stanford（Boyd）/ MIT（Sra）/ Princeton（Lee）/ Toronto（Hinton 体系）

---

## 八、信息论（更细节）

略，已列教材。前沿方向：
- 网络信息论
- 随机矩阵与信息论交叉
- private information retrieval
- ML 与信息论（信息瓶颈 / 互信息估计）

强校：MIT / Stanford / Berkeley / Princeton / Yale

---

## 九、数理逻辑与基础

### 9.1 集合论

- **起点**：Halmos / Jech
- **前沿**：large cardinals / forcing / descriptive set theory / inner model theory
- **强校**：Berkeley（Steel, Woodin）/ UCLA / Harvard / Helsinki

### 9.2 计算复杂性

- **前沿**：P vs NP / 唯一博弈 / PCP / 量子复杂性
- **强校**：MIT / Berkeley / Princeton / IAS / Weizmann

---

## 十、给你的最终建议

### 10.1 第一年：探索

读以下 5 个方向各 1 篇综述（不要深扎）：
1. Bartlett, Montanari 的 ML 理论综述
2. Tao "Machine Assisted Proofs"
3. Vershynin《High-Dimensional Probability》前 3 章
4. Song Yang 扩散模型综述
5. Buzzard Lean 形式化综述

### 10.2 第二年：聚焦

选 1-2 个方向深扎。**对你**（应用数学研究型工程师 + Lean + AI 经验），我推荐：
- **主攻**：ML 理论 OR 形式化数学 + AI for math
- **辅攻**：随机分析 / 数值分析（与应用相关）

### 10.3 第三年+：深扎 + 产出

- 读你方向的所有奠基论文（20-50 篇）
- 参加你方向的暑期学校 / 会议
- 找导师（PhD 或合作者）
- 写第一篇论文

---

📌 **下一步**：
- 看 [`TEXTBOOK_LIBRARY.md`](TEXTBOOK_LIBRARY.md) 选你方向的教材
- 看 [`FIELDS_LEVEL_PLAYBOOK.md`](FIELDS_LEVEL_PLAYBOOK.md) 看怎么从 PhD 走到顶级
- 看 [`COMMUNITY_AND_CAREER.md`](COMMUNITY_AND_CAREER.md) 找暑期学校 / 会议
