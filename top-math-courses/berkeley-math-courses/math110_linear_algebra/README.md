# UC Berkeley MATH 110 — Linear Algebra (Upper Division)

> **学校**：Berkeley
> **一手来源**：[math.berkeley.edu/courses](https://math.berkeley.edu/courses)

## 课程信息
- **编号**：MATH 110（upper division；区别于 lower division 的 MATH 54）
- **先修**：MATH 54 或同等
- **教材**：**Axler, *Linear Algebra Done Right* (4th ed, Springer, 2023, 免费 PDF)** ★
- **特色**：**本科线代最严格版本之一**——proof-based

## 教学大纲（Axler 4th ed）
1. Vector spaces
2. Finite-dimensional vector spaces
3. Linear maps
4. Polynomials
5. Eigenvalues, eigenvectors, invariant subspaces
6. Inner product spaces
7. Operators on inner product spaces
8. Operators on complex vector spaces
9. Operators on real vector spaces
10. Trace & determinant（重新定义，不通过置换）
11. **Spectral theorem** ★

## 与 ML 的关联
- **本科线代的标准严格训练**
- 谱定理 → PCA / 协方差
- 学完后：从纯数学视角理解 attention / 正交初始化

## 参考资源
- **教材（免费 PDF）**：[axler.net/LADR.html](https://axler.net/LADR.html)
- 视频：Axler 自录的 *Linear Algebra Done Right* 解说
- Princeton 对照：[MAT 217](../../princeton-math-courses/mat217_linear_algebra/)（同难度）
- MIT 对照：[MIT 18.700](../../mit-math-courses/)

## 学习建议
- **节奏**：每周 5-7 小时，12-14 周
- **配合 MIT 18.06**：MIT 教直觉，Berkeley 110 教证明

📌 **下一步**：→ [MATH 113 Abstract Algebra](../math113_abstract_algebra/) 或 [MATH 185 Complex Analysis](../math185_complex_analysis/)

---

## 📍 在数学全景中的位置

Berkeley 110（Axler）是线代从"工程师直觉"跨入"数学家严格"的**标准渡桥**。

```
直觉线代                    本课（严格线代 / Axler 风格）              后续数学
────────                    ──────────────────────────                  ────────
MIT 18.06 (Strang)  ──┐                                                抽象代数
UT Austin M 340L     ──┼──▶  Berkeley 110 (Axler LADR)  ──┬──▶  Berkeley 113 Abstract Algebra
ETH 401-0131        ──┘     ┃ 不用行列式定义特征值          │     Princeton MAT 345
Oxford Prelims M1   ──┘     ┃ invariant subspaces 出发      ├──▶  泛函分析 (无限维推广)
                       ┃ spectral theorem 严格证明          │     MIT 18.102 (Lax)
                       ┃                                    └──▶  数值线代 / 优化理论
                       ┃                                          UT Austin M 383E
                       └──▶  Princeton MAT 217 (同难度荣誉版)
```

- **前置**：一门入门线代（MIT 18.06 或 Berkeley 54），会基本矩阵运算即可。
- **本课独有**：Axler 的**"不用行列式"路线**——从向量空间→线性映射→算子→谱定理，全程不靠行列式定义特征值，而是从**不变子空间（invariant subspaces）**和**多项式**自然引出。这让谱定理的证明比传统教材干净得多。
- **后续**：(1) 抽象代数（把"向量空间"推广到"模"）；(2) 泛函分析（把有限维推广到无限维 Hilbert/Banach 空间）；(3) 数值线代（把存在性定理变成可计算算法）。

> 一句话：**18.06 教你"算"，110 教你"为什么算得通"——证明每个定理背后的结构。**

---

## 🔬 理论联系实际（公式级 ML/工程对应）

Axler 风格看似纯数学，但每个定理都是 ML 的隐形骨架：

1. **谱定理（Spectral Theorem）→ 自注意力的协方差几何**
   - 复谱定理：正规算子 $T$ 有正规矩阵表示 ⟺ $V$ 有 $T$ 的特征向量组成的**标准正交基**。
   - 实谱定理：自伴（对称）算子的特征值全实、特征向量可标准正交化：$S = \sum_i \lambda_i \mathbf{v}_i\mathbf{v}_i^T$。
   - **ML**：协方差矩阵 $\Sigma=\frac1n X^TX$ 自伴半正定 → 谱定理保证 PCA 的主轴存在且正交。Axler 的证明让你确信"PCA 永远可行"不是巧合而是定理。

2. **正定算子 → Mahalanobis 距离 / 高斯采样**
   - 正定算子 $T$（Axler 定义：$T=\sqrt{T^*T}$，自伴且 $\langle T\mathbf{v},\mathbf{v}\rangle\geq0$）。
   - **ML**：Mahalanobis 距离 $d^2=(\mathbf{x}-\mu)^T\Sigma^{-1}(\mathbf{x}-\mu)$；生成高斯样本 $\mathbf{x}=\mu+L\mathbf{z}$（$LL^T=\Sigma$，Cholesky = 正定算子的"平方根"）。

3. **投影（正交投影算子）→ 线性回归 / 注意力**
   - 正交投影 $P$ 满足 $P^2=P=P^*$。Axler 证明投影算子 ⟺ $V = \text{range}(P)\oplus\text{null}(P)$ 正交直和。
   - **ML**：最小二乘解 $\hat{\mathbf{x}}=A^+b$ 就是把 $b$ 投影到 $C(A)$；自注意力的 softmax 不是投影，但线性 attention 的核回归本质是投影。

4. **不变子空间 → LoRA 的子空间解释**
   - Axler 第 5 章：特征值来自 1 维不变子空间。若 $W$ 是 $T$ 的不变子空间，则 $T|_W$ 有特征值。
   - **ML**：LoRA 假设 $\Delta W$ 的"有效更新"集中在一个低维不变子空间（秩 $r$）内。110 教你的"不变子空间"语言，正是理解"为什么低秩更新够用"的数学框架。

5. **复化（complexification）→ 处理非对称矩阵**
   - 实算子在实空间可能无特征值，但复化后必有（代数基本定理）。Axler 用此优雅地证明实谱定理。
   - **ML**：神经网络动态系统（Neural ODE）的稳定性分析常需复特征值（振荡模式）。

---

## 🆕 2024-2026 最新研究（线代理论在 ML 的前沿）

1. **LoRA/QLoRA 的低秩数学需要谱定理 + 正定算子理论（2023-2026）**
   - LoRA（[arXiv:2106.09685](https://arxiv.org/abs/2106.09685)）与 QLoRA（[arXiv:2305.14314](https://arxiv.org/abs/2305.14314)）的低秩更新 $W=W_0+BA$，其有效性依赖"权重增量集中在低秩不变子空间"。Axler 第 5 章（不变子空间）+ 第 7 章（谱定理）正是证明"最优低秩子空间 = 前 $r$ 个奇异向量"的理论基础。

2. **正交初始化的谱理论复兴（2024-2025）**
   - 深度网络训练稳定性研究重新关注"正交权重矩阵"——即 Axler 第 7 章的酉算子/正交算子。用谱定理保证 $\|W\mathbf{x}\|=\|\mathbf{x}\|$（等距），防止梯度爆炸/消失。MPL（Mechanistic Interpretability）研究用正交基分解注意力头。

3. **不变子空间与持续学习（Continual Learning, 2024-2026）**
   - 避免灾难性遗忘的最新方法：为新任务在权重空间找一组**正交子空间**，使新学习不干扰旧知识。这正是 Axler 的"正交直和分解 $V=U\oplus U^\perp$"的直接工程化。⚠️ 该方向理论（子空间如何随训练漂移）仍在发展。

📌 **下一步**：→ [MATH 113 Abstract Algebra](../math113_abstract_algebra/) 或 [MATH 185 Complex Analysis](../math185_complex_analysis/)
