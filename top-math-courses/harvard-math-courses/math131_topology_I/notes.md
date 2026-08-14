# Harvard Math 131 · 章节笔记（Munkres *Topology*）

> **教材**：Munkres *Topology*（前半部分）
> **特色**：点集拓扑——从度量空间抽象到一般拓扑空间

---

# 费曼三层讲透：点集拓扑核心

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **拓扑空间** | **"有'近邻'概念但没尺子"**——只知道开集，不量化距离 |
| **连续映射** | **"不撕裂开集"**：开集原像还是开集 |
| **紧致性** | **"无处可逃"**：任何开覆盖都有有限子覆盖 |
| **连通性** | **"不能分成两块"**：无法写成两个非空开集的分离并 |
| **商拓扑** | **"粘合空间"**：把等价类当成一个点 |
| **同伦** | **"可以连续变形"**：两根绳子能互相滑过去 |

---

## 🧮 数学层

### 拓扑空间 $(X, \tau)$

$\tau \subset \mathcal{P}(X)$ 满足：空集/全集 ∈ τ，任意并封闭，有限交封闭。

**例子**：
- 离散拓扑 $\tau = \mathcal{P}(X)$（最细）
- 平凡拓扑 $\tau = \{\emptyset, X\}$（最粗）
- 度量拓扑（由开球生成）

### 连续映射

$$f: (X, \tau_X) \to (Y, \tau_Y) \text{ 连续} \iff f^{-1}(U) \in \tau_X, \forall U \in \tau_Y$$

**等价条件**：开集原像开 / 闭集原像闭 / $\overline{f^{-1}(B)} \subset f^{-1}(\overline{B})$。

### 紧致性 ★★

**定义**：每个开覆盖有有限子覆盖。

**Heine-Borel**（度量空间）：$S \subset \mathbb{R}^n$ 紧致 $\iff$ 有界 + 闭。

**Tychonoff 定理** ★★★（等价于选择公理）：紧致空间的任意积紧致。

**ML 应用**：参数空间 $\{\theta : \|\theta\| \leq R\}$ 紧致 → loss 最小值存在。

### 连通性

$X$ 连通 $\iff$ 不能写成两个非空不相交开集的并。

**路径连通** $\Rightarrow$ 连通（反之不然：拓扑正弦曲线）。

### 分离公理

| 公理 | 条件 |
|---|---|
| $T_0$ | 任意两点中至少一个有不含另一个的开邻域 |
| $T_1$ | 每个单点集是闭集 |
| $T_2$ (Hausdorff) | 任意两点有不相交开邻域 |
| $T_4$ (Normal) | $T_1$ + 任意两个不相交闭集有不相交开邻域 |

**Urysohn 引理** ★：$T_4$ 空间中任意两个不相交闭集可用连续函数分离。

### 同伦与基本群

**同伦** $f \simeq g$：$H: X \times [0,1] \to Y$ 连续，$H(\cdot, 0) = f$, $H(\cdot, 1) = g$。

**基本群** $\pi_1(X, x_0)$：基于 $x_0$ 的环的同伦类。

**例子**：$\pi_1(S^1) = \mathbb{Z}$, $\pi_1(S^n) = 0$（$n \geq 2$）。

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt
# 紧致性演示: [0,1] 紧致 vs (0,1) 不紧致
# 在 (0,1) 中, 序列 1/n 没有极限 (0 不在空间内)
x = np.linspace(0.01, 0.99, 100)
# 但 1/n → 0, 而 0 ∉ (0,1) → 不完备 → 不紧致
seq = 1 / np.arange(1, 20)
print("序列 1/n:", seq[:5], "...")
print("极限 0 在 (0,1) 中?", 0 > 0 and 0 < 1)  # False → 不完备

# 同伦演示: 圆上的环路
theta = np.linspace(0, 2*np.pi, 100)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(np.cos(theta), np.sin(theta))
axes[0].set_title("S¹ 上的环路 (缠绕数=1)")
# 收缩到点
for r in np.linspace(0, 1, 5):
    axes[1].plot(r*np.cos(theta), r*np.sin(theta), alpha=0.5)
axes[1].set_title("同伦收缩 (在 R² 中)")
plt.tight_layout()
plt.savefig("homotopy_demo.png", dpi=100)
print("同伦演示已保存")
```

---

## ⚠️ 不足层
- Math 131 只做点集拓扑 + 基本群入门
- 代数拓扑（同调、上同调）需 Math 231br
- 微分拓扑需 Math 134

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| 紧致性 | 参数空间正则化 → 最值存在 |
| 连续映射 | 神经网络是连续映射 |
| 连通性 | loss landscape 连通性 |
| 商拓扑 | 等变网络 / 集合上的网络 |
| 同伦 | 持续同调 (TDA) → 数据形状分析 |
| 基本群 | 拓扑数据分析 (TDA) |

---

## 章节概览（Munkres）

| 章 | 内容 | 关键 |
|---|---|---|
| 2 | 拓扑空间 | 开集、基、子基 |
| 3 | 连续映射 | 原像开集 ★ |
| 4 | 连通性 | 路径连通、局部连通 |
| 5 | 紧致性 ★★ | Heine-Borel、Tychonoff |
| 6 | 度量空间 | 完备化、Baire 定理 |
| 7 | 分离公理 | Urysohn 引理 ★ |
| 9 | 基本群 ★ | $\pi_1(S^1) = \mathbb{Z}$ |
