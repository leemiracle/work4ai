# Harvard Math 131 · 习题集

> **分级**：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放

---

### Q1 ⭐（开集/闭集）
在标准拓扑下，$(0, 1) \cup (2, 3)$ 是 $\mathbb{R}$ 的开集吗？是连通的吗？

<details><summary>解</summary>
**开**: 是两个开区间的并 → 开集 ✓
**连通**: 不连通。$(0,1)$ 和 $(2,3)$ 是两个非空分离开集。
</details>

### Q2 ⭐⭐（紧致性）
$S = \{0\} \cup \{1/n : n \in \mathbb{N}\}$ 在 $\mathbb{R}$ 中紧致吗？

<details><summary>解</summary>
**有界** ($\subset [0,1]$) ✓ + **闭** (包含极限点 0) ✓ → 由 Heine-Borel 紧致 ✓。

**ML 关联**：离散点集 + 极限点构成紧致集——数据流形的理想化模型。
</details>

### Q3 ⭐⭐（连续映射）
$f: \mathbb{R} \to \mathbb{R}$, $f(x) = x^2$。$f^{-1}((-1, 4)) = ?$ 验证开集原像是开集。

<details><summary>解</summary>
$f^{-1}((-1,4)) = \{x : x^2 < 4\} = (-2, 2)$。开集 ✓。
</details>

### Q4 ⭐⭐⭐（开放：紧致性与神经网络泛化）
解释为什么权重衰减 $\|\theta\|^2 \leq R$ 使 loss 最小值存在，以及这与泛化的关系。

<details><summary>解</summary>
1. $\{\theta : \|\theta\|^2 \leq R\}$ 是 $\mathbb{R}^d$ 中的闭球 → 有界 + 闭 → **紧致**（Heine-Borel）。
2. Loss $L(\theta)$ 连续（神经网络是连续映射，交叉熵/MSE 连续）。
3. 紧致集上连续函数取最小值 → $\inf L = \min L$，最小值存在。
4. **泛化**: 紧致假设空间 → 覆盖数有限 → 泛化界 $O(\sqrt{d \log R / n})$。

**深层**: 权重衰减不只是正则化技巧——它从拓扑上保证了优化的良定义性。
</details>

### Q5 ⭐⭐（基本群）
计算 $\pi_1(S^1)$。

<details><summary>解（思路）</summary>
$\pi_1(S^1) \cong \mathbb{Z}$，生成元是绕一圈的环路。缠绕数 $n \in \mathbb{Z}$ 分类所有环路的同伦类。

**ML 关联**: 持续同调 (TDA) 用拓扑不变量分析数据形状。
</details>

### Q6 ⭐⭐⭐（开放：TDA 与机器学习）
解释持续同调如何用于分析神经网络的 loss landscape 形状。

<details><summary>解（思路）</summary>
1. **Loss landscape** 是高维空间上的标量场 $L: \mathbb{R}^d \to \mathbb{R}$。
2. 对每个阈值 $\alpha$，取下水平集 $L^{-1}((-\infty, \alpha])$，计算同调群 $H_0$（连通分量）、$H_1$（洞）。
3. **持续图**: 跟踪拓扑特征（洞/空腔）随 $\alpha$ 变化的生命周期。
4. 长寿命特征 = loss landscape 的真实结构（如多个局部极小值的连通性）。
5. 应用：分析 mode collapse in GANs、差分隐私的扰动影响。

**工具**: GUDHI, Ripser, scikit-tda。
</details>
