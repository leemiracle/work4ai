# UT Austin M 385C — Theory of Probability (Graduate)

> **学校**：UT Austin | **学期**：Fall (研究生)
> **一手来源**：[catalog.utexas.edu/search/?P=M+385C](https://catalog.utexas.edu/search/?P=M+385C) + [math.utexas.edu/...preliminary-exams](https://math.utexas.edu/information/graduate-students/preliminary-exams)

## 课程信息
- **编号**：M 385C / CSEM 384K（互认）
- **先修**：M 365C 实分析 + M 341 线代 + M 362K 本科概率
- **教材**：**Durrett, *Probability: Theory and Examples*** ★；或 Billingsley
- **特色**：**UT Austin Probability Prelim 序列第一学期**

## 教学大纲
1. Probability spaces, σ-algebras
2. Random variables, expectation
3. $L^p$ spaces
4. Convergence modes (a.s. / prob / $L^p$ / dist)
5. **LLN & CLT** ★
6. **Conditional expectation**
7. **Martingales**（停时、收敛、可选停时）
8. **Brownian motion** 入门

## 与 ML 的关联（**ML 理论核心**）
- 集中不等式 → 泛化界
- 鞅 → RL 理论
- Brownian → 扩散模型
- 学完后：能读所有 ML 理论论文

## 参考资源
- Durrett, *Probability: Theory and Examples* (5th, 免费 PDF)
- Billingsley, *Probability and Measure*
- Williams, *Probability with Martingales*
- MIT 对照：[MIT 18.175](../../mit-math-courses/18_175_probability/)

## 学习建议
- **节奏**：每周 6-8 小时，14-16 周
- **核心**：第 4-7 章（ML 理论用的工具）

---

## 📍 在数学全景中的位置

```
本科概率 + 实分析                       研究生测度论概率                         ML 理论前沿
─────────────────                      ────────────────                       ──────────
M 362K 概率 I ──┐                  M 385C Theory of Probability ────────→  集中不等式 → 泛化界
M 365C 实分析 ──┴──→  (Durrett: σ-代数/收敛/LLN/CLT/鞅/Brownian)          鞅 → RL TD 学习
                      UT Probability Prelim 第一学期                       Brownian → 扩散模型 SDE
```

- **前置**：[M 365C 实分析](../m365c_real_analysis/)（Lebesgue 积分、$L^p$ 空间）+ [M 362K 概率](../m362K_probability/)（应用概率直觉）+ 线代
- **本课**：UT Austin Probability Prelim 第一学期——测度论概率空间、四种收敛、SLLN/CLT、条件期望、鞅（停时/可选停时/收敛）、Brownian motion 入门（与 [MIT 18.175](../../mit-math-courses/18_175_probability/) 同级金课）
- **后续**：UT Probability Prelim 第二学期（随机过程 / 数学统计）→ ML 理论论文（Bartlett / Belkin / Mohri）

---

## 🔬 理论联系实际

| 概率概念 | ML / 工程应用 | 公式级对应 |
|---|---|---|
| **强大数定律 SLLN** | SGD 收敛 | $\dfrac{1}{n}\sum\nabla\ell(\theta;x_i)\xrightarrow{a.s.}\nabla L(\theta)$ → 梯度平均几乎必然收敛 |
| **中心极限定理 CLT** | BatchNorm 稳定性 / 参数渐近正态 | $\dfrac{S_n-n\mu}{\sigma\sqrt{n}}\xRightarrow{d}\mathcal{N}(0,1)$ → mini-batch 梯度噪声正态化 |
| **Hoeffding 不等式** | 泛化界（PAC 学习） | $P(\|\hat{R}(h)-R(h)\|>\epsilon)\leq 2e^{-2n\epsilon^2}$ → 样本数 $n$ 与泛化误差的定量关系 |
| **Berry-Esseen** | 有限样本校正 | $\sup_x\|F_n-\Phi\|\leq CE\|X\|^3/(\sigma^3\sqrt{n})$ → 小 batch 下 CLT 的精确误差 |
| **鞅 + 可选停时** | RLHF 收敛 / TD 学习 / 期权定价 | $E[X_\tau]=E[X_0]$ → TD 误差在真值处是鞅差，期望为 0 |
| **Doob 鞅 + Azuma** | 联机学习 regret bound | $f-Ef=\sum D_i$（鞅差）+ Azuma → regret $O(\sqrt{T})$ |
| **Markov 链遍历定理** | MCMC / PageRank | $\pi P^n\to\pi^*$（平稳分布）→ 贝叶斯后验采样 |
| **Brownian motion** | Diffusion model（SDE 基础） | $dX_t=f(X_t)dt+\sigma dW_t$ → 扩散模型前向加噪；Itô 引理 $df=f'dW+\tfrac12 f''dt$ |

**核心洞察**：UT 385C 与 MIT 18.175 同属 ML 理论的两大支柱——**集中不等式**（Hoeffding / McDiarmid → 泛化界）与**随机逼近**（SLLN + 鞅 → SGD / RL 收敛）——的数学根基。学完本课即能读懂 Bartlett / Belkin / Mohri 的 ML 理论论文。

---

## 🆕 2024-2026 最新研究

1. **Diffusion model 的 SDE / Score matching 基础** ⭐
   - Song et al. (arXiv:2011.13456) 将扩散模型统一为 SDE；前向 $dX_t=f(X_t)dt+g(t)dW_t$，反向 SDE 需要 score function $\nabla\log p_t(x)$
   - 2024-2025 进展：Flow Matching（Lipman et al., arXiv:2210.02747）、Rectified Flow 成为 Stable Diffusion 3 底层框架
   - **与本课关联**：反向 SDE 推导依赖 Girsanov 定理（测度变换）+ Brownian motion 的鞅性质；DDPM（Ho et al., arXiv:2006.11239 ✅）的噪声预测目标即 score matching

2. **Conformal prediction（保形预测）** ⭐
   - 2024 年成为大模型不确定性量化的标准工具（Amazon / Google 生产部署）
   - 核心：用交换排列不变性（i.i.d. 的弱化）构造分布无关预测区间；覆盖率保证用 Hoeffding / DKW 不等式
   - **与本课关联**：交换排列不变性 = i.i.d. 的推广；覆盖率证明用本课的集中不等式

3. **信息论泛化界（Information-theoretic generalization bounds）** ⭐
   - 2024-2025 热点：用互信息 $I(W;S)$（算法输出 $W$ 与训练集 $S$）控制泛化误差
   - Russo & Zou (2016), Xu & Raginsky (2017)：$|E[R(W)]-E[\hat{R}(W,S)]|\leq\sqrt{2\sigma^2 I(W;S)/n}$（⚠️ 具体常数以原文为准）
   - **与本课关联**：KL 散度 + Pinsker 不等式 + 鞅方法 → PAC-Bayes 的信息论推广

📌 **下一步**：→ 进入 [前沿专题](../../) 或回到 [UT Austin SCHOOL.md](../SCHOOL.md)
