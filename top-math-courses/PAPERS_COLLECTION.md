# PAPERS_COLLECTION：数学论文库（奠基 + 前沿，按方向）

> **本章核心**：教材给"已知"，论文给"前沿"。要成为研究者，必须读论文。
>
> 每个方向给：奠基论文（必读）+ 前沿综述 + arXiv 分类。
>
> ⚠️ arXiv ID 我尽量凭记忆写出"近似"，**正式读之前必须 webfetch abs 页核实**（你的铁律）。

---

## 一、ML 理论（你的强方向）

### 奠基论文（必读）

| 论文 | arXiv（待核实）| 贡献 |
|------|---------------|------|
| **Belkin, Hsu, Ma, Mandal 2018** "Reconciling modern machine learning and the bias-variance trade-off" | 1812.11118 | Double descent 现象 |
| **Jacot, Gabriel, Hongler 2018** "NTK" | 1806.07572 | Neural Tangent Kernel |
| **Bartlett, Foster, Telgarsky 2017** "Spectrally-normalized margin bounds for neural networks" | 1706.08498 | NN 泛化界 |
| **Neyshabur et al. 2015** "Norm-based capacity control" | — | path-norm |
| **Allen-Zhu, Li, Song 2019** "On the convergence rate of training recurrent neural networks" | 1810.12065 | 训练收敛 |
| **Soudry et al. 2018** "The implicit bias of gradient descent" | 1710.10345 | 隐式偏向 margin |
| **Arora et al. 2019** "Fine-grained analysis of optimization and generalization for overparameterized two-layer neural networks" | 1901.08584 | 过参数理论 |

### 综述（入门必读）

- **Bartlett & Montanari** "Deep learning: a statistical viewpoint"（2021 ACM Acta Numerica）
- **Belkin** "Fit without fear: remarkable mathematical phenomena of deep learning"（2021 PNAS）

### 前沿（2024-2026）

- Transformer 理论（attention 的几何 / 训练动力学）
- LLM in-context learning 的理论
- Diffusion models 的数学（convergence rates）
- Scaling laws 的第一性原理

### arXiv 分类

- `cs.LG`（Machine Learning）
- `stat.ML`（Stats - ML）
- `math.ST`（Statistics Theory）
- `math.OC`（Optimization and Control）

---

## 二、形式化数学 + AI for Math（你的最大杠杆）

### 奠基论文

| 论文 | 来源 | 贡献 |
|------|------|------|
| **DeepMind "AlphaProof" Nature 2025** | DOI 10.1038/s41586-025-09833-y | IMO 银牌 |
| **Tao 2024 "Machine Assisted Proofs"** | Tao blog PDF | 综述 |
| **Polu & Sutskever 2020** "Generative Language Modeling for Automated Theorem Proving" | arXiv:2009.03393 | GPT-f |
| **Wu et al. 2022** "Autoformalization with Large Language Models" | arXiv:2205.12615 | auto-formalization |
| **First et al. 2023** "Baldur: Whole-Proof Generation and Repair" | arXiv:2303.04910 | auto-repair |
| **Han, Lewis, Rute 2024** "Theorem proving with Lean" | 综述 |

### 大型形式化项目

- **Scholze "Liquid tensor experiment"**（2022 完成）
- **Polynomial Freiman-Ruzsa**（Gowers-Green-Manners-Tao 2023，3 周形式化）
- **Equational Theories Project**（2024-25，arXiv 2025-12）
- **Buzzard Fermat 大定理**（2024 启动，5 年计划）

### 资源

- **miniF2F benchmark**：https://github.com/google-deepmind/miniF2F
- **formal-conjectures repo**：https://github.com/google-deepmind/formal-conjectures

---

## 三、概率 / 高维

### 奠基

- **Vershynin《High-Dimensional Probability》**（书，2018）—— ML 理论必备
- **Rigollet & Hütter** "High-Dimensional Statistics" notes（MIT 18.S997）
- **Roman Vershynin 2012** "Introduction to the non-asymptotic analysis of random matrices"

### 前沿

- **Tao** 系列（random matrix）
- **Sellke** "Learning a single neuron" 系列

---

## 四、优化（与 ML 交叉）

### 奠基

- **Nesterov 2004**《Introductory Lectures on Convex Optimization》
- **Kingma & Ba 2014** "Adam"（arXiv:1412.6980）
- **Duchi, Hazan, Singer 2011** "Adagrad"
- **Reddi, Kale, Kumar 2018** "On the convergence of Adam and beyond"（AMSGrad）

### 前沿

- **Lion optimizer**（Google 2023）
- 非凸优化的 landscape（用 algebraic topology）

---

## 五、随机分析 / 扩散模型

### 奠基

- **Song, Sohl-Dickstein, Kingma, Kumar, Ermon, Poole 2020** "Score-Based Generative Modeling through SDEs"（arXiv:2011.13456）
- **Ho, Jain, Abbeel 2020** "DDPM"（arXiv:2006.11239）
- **Song, Ermon 2019** "Generative modeling by estimating gradients of the data distribution"
- **Karras et al. 2022** "Elucidating the design space of diffusion-based generative models"

### 综述

- **Yang Song 2023** "Diffusion models" tutorial

---

## 六、调和分析

- **Tao《Topics in Harmonic Analysis》** notes
- **Stein & Shakarchi** 四卷本（教材）

---

## 七、代数几何

### 奠基（历史）

- **Grothendieck EGA / SGA**（1960s，至今基础）
- **Deligne 1974** "Weil II"（证明 Weil 猜想）
- **Wiles 1995** "Modular elliptic curves and Fermat's Last Theorem"

### 前沿

- 几何 Langlands（Frenkel, Gaitsgory）
- Derived algebraic geometry（Toën, Lurie）
- **Lurie《Higher Topos Theory》**（书）

---

## 八、数论

### 奠基

- **Wiles 1995** Fermat
- **Yitang Zhang 2014** Bounded gaps
- **Maynard 2015** Small gaps
- **Scholze 2012** Perfectoid spaces
- **Mochizuki** IUT（争议）

### Open

- Riemann 假设
- BSD conjecture
- abc conjecture（Mochizuki vs Scholze/Stix 争议）

---

## 九、PDE

- **Perelman 2002-2003** Ricci flow 三论文（证 Poincaré）
- **Chen-Hou 2022** finite time blowup for Euler

---

## 十、读论文的方法

见 [`RESEARCH_METHODOLOGY.md`](RESEARCH_METHODOLOGY.md) §二。

简版：
1. 先读 abstract + intro + main theorem
2. 判断值不值得深读
3. 深读时拿纸笔重推导
4. 用 Lean 形式化（最深理解）

---

## 十一、订阅 arXiv RSS

```bash
# 你感兴趣的 arXiv 分类
# 数学：math.CO/PR/ST/IT/NA/FA/CA/CT/AG/NT/AT/DG/SG/LO
# CS 理论：cs.LG, cs.CL, cs.SC (Symbolic Computation), cs.LO (Logic)
# Stats: stat.ML, stat.TH

# 订阅方式：
# 1. RSS reader (Feedly / Inoreader) 订阅 https://arxiv.org/rss/math.CO 等
# 2. arxiv-sanity-preserver (开源工具)
# 3. https://arxiv.org/list/cs.LG/recent 每日看
```

---

📌 **下一步**：
- 选你方向（ML 理论 / 形式化数学）
- 读该方向的奠基论文 5-10 篇
- 在 Lean 里形式化 1 篇
- 看 [`RESEARCH_METHODOLOGY.md`](RESEARCH_METHODOLOGY.md) §二学读论文方法

> ⚠️ **再次提醒**：本表 arXiv ID 是凭记忆，**正式读前 webfetch 核实**。你的铁律：arXiv ID 错误率 30-50%。
