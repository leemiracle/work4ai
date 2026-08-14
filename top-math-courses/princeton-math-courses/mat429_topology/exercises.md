# Princeton MAT 429 · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（开集）
证明有限拓扑空间中所有集合都是紧致的。

<details><summary>解</summary>
有限集的任何开覆盖已经是有限覆盖（最多 $|X|$ 个元素）。所以有限集紧致。
</details>

### Q2 ⭐⭐（紧致性）
证明 $[0, 1]^\mathbb{N}$（可数无穷维立方体）在积拓扑中紧致。

<details><summary>解</summary>
$[0,1]$ 紧致（Heine-Borel）。由 **Tychonoff 定理**，紧致空间的任意积紧致 → $[0,1]^\mathbb{N}$ 紧致。

**注意**: 这里必须用**积拓扑**，而非箱拓扑（box topology）。

**ML 关联**: 无限维参数空间（如函数空间）的紧致性——RKHS 中有界集的弱紧致性。
</details>

### Q3 ⭐⭐（商空间）
证明把 $[0,1]$ 的两端粘合（$0 \sim 1$）后得到的商空间同胚于 $S^1$。

<details><summary>解</summary>
定义 $f: [0,1] \to S^1$, $t \mapsto e^{2\pi i t}$。$f(0) = f(1)$，所以 $f$ 诱导商空间上的连续双射 $\bar{f}: [0,1]/\{0 \sim 1\} \to S^1$。$[0,1]$ 紧致 → 商空间紧致 → $S^1$ Hausdorff → $\bar{f}$ 是同胚。
</details>

### Q4 ⭐⭐（基本群）
计算环面 $T^2 = S^1 \times S^1$ 的基本群。

<details><summary>解</summary>
$\pi_1(X \times Y) \cong \pi_1(X) \times \pi_1(Y)$。所以 $\pi_1(T^2) = \pi_1(S^1) \times \pi_1(S^1) = \mathbb{Z} \times \mathbb{Z} = \mathbb{Z}^2$。

**ML 关联**: 环面有两个独立"洞"→ 数据流形中拓扑特征的分类。
</details>

### Q5 ⭐⭐⭐（开放：TDA 与持续同调）
解释持续同调如何用基本群/同调群来分析点云数据的形状。

<details><summary>解（思路）</summary>
1. **Vietoris-Rips 复形**: 对点云 $\{x_i\}$ 和参数 $\epsilon$，若 $d(x_i, x_j) < \epsilon$ 则连接 → 随 $\epsilon$ 增大形成复形 $VR_\epsilon$。
2. **同调群**: 计算 $H_0$（连通分量）、$H_1$（环/洞）、$H_2$（空腔）随 $\epsilon$ 变化。
3. **持续图**: 每个拓扑特征有 birth $\epsilon_b$ 和 death $\epsilon_d$；$(\epsilon_b, \epsilon_d)$ 远离对角线 = 显著特征。
4. **应用**: 蛋白质折叠分析、脑功能网络、神经网络表示空间分析。

**工具**: GUDHI (Python), Ripser (C++)。
</details>

### Q6 ⭐⭐⭐（开放：等变神经网络与商拓扑）
解释等变神经网络为什么涉及商拓扑 $X/G$。

<details><summary>解（思路）</summary>
**目标**: 设计对群 $G$（如旋转、排列）等变的网络：$f(g \cdot x) = g \cdot f(x)$。

**商拓扑视角**:
1. 商空间 $X/G$ = 轨道空间（每个等价类 $= G$-轨道）。
2. 等变函数 $f$ 诱导商空间上的函数 $\bar{f}: X/G \to Y/G$。
3. 网络设计 = 在商拓扑上定义连续映射。

**例子**:
- **DeepSets** ( permutation 等变): $\mathbb{R}^{n \times d} / S_n$（商掉对称群）
- **GNN**: 图上的商结构
- **SO(3) 等变网络**: $\mathbb{R}^3 / SO(3)$（商掉旋转群）

**数学**: 商拓扑的连续性 = $f^{-1}(U)$ 开 in $X/G$ $\iff$ $\pi^{-1}(f^{-1}(U))$ 开 in $X$。
</details>
