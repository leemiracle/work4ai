# Stanford MATH 113 — Linear Algebra and Matrix Theory

> **学校**：Stanford
> **一手来源**：[mathematics.stanford.edu/academics/courses](https://mathematics.stanford.edu/academics/courses)

## 课程信息
- **编号**：MATH 113（4 units）
- **先修**：MATH 51
- **教材**：Axler, *Linear Algebra Done Right*；Strang *Introduction to Linear Algebra*
- **特色**：**理论线代**（MATH 51 升级版）

## 教学大纲
1. Vector spaces, subspaces
2. Linear maps, null/rank
3. Eigenvalues, eigenvectors
4. Inner products
5. Operators on inner product spaces
6. Spectral theorem ★
7. Jordan form（如时间允许）

## 与 ML 的关联
- 谱定理 → PCA、协方差
- Jordan 形式 → Neural ODE 稳定性

## 参考资源
- Axler, *Linear Algebra Done Right* (4th ed, 2023, 免费 PDF)
- Berkeley 对照：[Math 110](../../berkeley-math-courses/math110_linear_algebra/)

---

## 📍 在数学全景中的位置

Stanford 113 是"应用数学大本营"Stanford 的**理论线代**——把 MATH 51（应用线代）升级为证明导向，同时为硅谷的 ML/优化铺路。

```
应用入门                     本课（理论线代）                        Stanford 后续
──────                       ──────────────                          ────────────
MATH 51 (应用线代) ──▶  MATH 113 理论线代 (Axler+Strang) ──┬──▶  CME 364A 凸优化 (Boyd)
                                                           ├──▶  CME 108 科学计算
                                                           ├──▶  STATS 200 统计理论
                                                           └──▶  CS 229 机器学习 (理论基础)
```

- **前置**：MATH 51（会矩阵运算与基本应用）。
- **本课特色**：兼用 **Axler（证明）+ Strang（直觉）**，是少数"理论 + 应用双轨"的线代课。重点在谱定理与 Jordan 形式。
- **后续**：Stanford 体系下，113 → CME 364A（凸优化，用正定矩阵/特征值）/ STATS 200（统计，用协方差谱）/ CS 229（ML 理论）。

> 一句话：**Stanford 113 是"给 ML 工程师的数学严格性"——既要懂证明，又要连得上优化和统计。**

---

## 🔬 理论联系实际（公式级 ML/工程对应）

1. **Jordan 形式 → Neural ODE / RNN 稳定性**
   - 线性系统 $\dot{\mathbf{x}}=A\mathbf{x}$ 的解 $\mathbf{x}(t)=e^{At}\mathbf{x}_0$。$e^{At}$ 的行为由 $A$ 的 Jordan 形式决定：每个特征值 $\lambda$ 贡献 $e^{\lambda t}$，每个 Jordan 块贡献 $t^{k}e^{\lambda t}/k!$ 项。
   - $\text{Re}(\lambda)<0$ → 衰减（稳定）；$\text{Re}(\lambda)>0$ → 爆炸。Jordan 块带来多项式增长项 $t^k$。
   - **ML**：Neural ODE $\dot{\mathbf{h}}=f(\mathbf{h},t)$ 在平衡点线性化，稳定性 = Jacobian 的特征值实部。

2. **谱定理 → 协方差 / 高斯 / PCA**
   - 对称 $S=Q\Lambda Q^T$ → 协方差对角化 → PCA 主轴。多元高斯等概率面 = 椭球，轴 = 特征向量。

3. **正定矩阵 → 凸优化 / Hessian**
   - $f$ 凸 ⟺ Hessian $\nabla^2f\succeq0$（半正定）。严格凸 ⟺ 正定。**Stanford CME 364A 全程建立在正定矩阵上**。

4. **矩阵指数 $e^{At}$ → Transformer 残差流的连续化**
   - 残差网络 $\mathbf{h}_{l+1}=\mathbf{h}_l+f(\mathbf{h}_l)$ 的连续极限是 ODE，其数值求解（Euler 法）就是残差连接。$e^{At}$ 的谱（特征值）控制信息流。

5. **Cayley-Hamilton → 矩阵幂的简化**
   - $A$ 满足自己的特征方程：$p(A)=0$。→ 高次幂 $A^k$ 可降阶为低次多项式。**ML**：分析 RNN 的长期依赖 $\prod W$ 时，用 Cayley-Hamilton 降阶。

---

## 🆕 2024-2026 最新研究（线代理论在 ML 的前沿）

1. **Neural ODE / 深度均衡模型的稳定性分析（2024-2025）**
   - 深度均衡模型（DEQ）找不动点 $\mathbf{h}^*=f(\mathbf{h}^*)$，收敛性要求 Jacobian $J_f$ 的谱半径 $<1$。这正是 Jordan 形式 + 谱理论的直接应用。⚠️ 非线性系统的全局稳定性证明仍是开放问题。

2. **谱定理与正交初始化在 LLM 训练稳定性中的复兴（2024-2026）**
   - MuP（最大更新参数化）等理论用特征值尺度分析来预测模型可扩展性。正交权重（酉算子）保证 $\|Wh\|=\|h\|$，是稳定训练的理论工具。

3. **低秩微调（LoRA/QLoRA）的谱理论基础（2023-2026）**
   - LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）与 QLoRA（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）的低秩更新依赖"权重增量的有效秩低"。谱定理 + 奇异值理论是证明"小秩够用"的数学根基。

📌 **下一步**：→ [MATH 115 Real Variable](../math115_real_variable/)
