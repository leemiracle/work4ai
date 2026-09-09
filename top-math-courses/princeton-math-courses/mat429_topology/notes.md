# Princeton MAT 429 · 章节笔记（Munkres *Topology*）

> **教材**：Munkres *Topology*（全本）；补充 Hatcher *Algebraic Topology* Ch.0
> **特色**：Princeton 拓扑课程——点集拓扑严格化 + 代数拓扑入门

---

# 费曼三层讲透：拓扑学

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **拓扑空间** | **"橡皮几何"**：可以拉伸、弯曲，但不能撕裂或粘合 |
| **同胚** | **"拓扑等价"**：咖啡杯 ≅ 甜甜圈 |
| **紧致性** | **"有限信息确定全部"**：有限子覆盖 |
| **商空间** | **"粘合等价类"**：把正方形对边粘起来 → 圆柱 / Möbius 带 / 环面 |
| **基本群** | **"数洞的代数方法"**：$S^1$ 有一个洞 → $\pi_1 = \mathbb{Z}$ |
| **覆叠空间** | **"多值函数的几何化"**：$\mathbb{R} \to S^1$ 是万有覆叠 |

---

## 🧮 数学层

### 拓扑公理

$(X, \tau)$: $\emptyset, X \in \tau$; 任意并封闭; 有限交封闭。

### 连续 + 同胚

$f: X \to Y$ **连续** $\iff$ 开集原像开。

$f$ **同胚** $\iff$ 双射 + 连续 + 逆连续。拓扑等价。

### 紧致性 ★★★

每个开覆盖有有限子覆盖。

- **Heine-Borel**: $\mathbb{R}^n$ 中 $\iff$ 有界+闭
- **Tychonoff**: 紧致空间的任意积紧致（$\iff$ 选择公理）
- **紧致 + 连续**: 像 tight, 取最值, 一致连续

**ML 应用**: $\{\theta : \|\theta\| \leq R\}$ 紧致 → loss 最小值存在。

### 分离公理 $T_0$ — $T_4$

Hausdorff ($T_2$): 任意两点有不相交开邻域。

**Urysohn 引理**: $T_4$ 中不相交闭集可用连续函数分离。

### 商拓扑

$X/\sim$: 等价类的集合, $\pi: X \to X/\sim$ 自然投影。

$U \subset X/\sim$ 开 $\iff \pi^{-1}(U)$ 开。

**例子**: $[0,1]/\{0 \sim 1\} \cong S^1$; $[0,1]^2/\text{对边粘合} \cong$ 环面/圆柱/Möbius/Klein 瓶。

### 基本群 ★★

$\pi_1(X, x_0)$: 基于 $x_0$ 的环路同伦类, 群运算 = 环路拼接。

| 空间 | $\pi_1$ |
|---|---|
| $\mathbb{R}^n$ | $0$ (可缩) |
| $S^1$ | $\mathbb{Z}$ |
| $S^n$ ($n \geq 2$) | $0$ |
| 环面 $T^2$ | $\mathbb{Z}^2$ |

### 覆叠空间

$p: E \to B$ 覆叠映射: 每点有均匀覆叠邻域。

$\mathbb{R} \to S^1$, $t \mapsto e^{2\pi i t}$ 是万有覆叠。

$\pi_1(B) / p_*(\pi_1(E)) \cong$ 覆叠变换群。

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt

# 商空间: 正方形粘合成环面
fig, axes = plt.subplots(1, 3, figsize=(12, 4))

# 正方形
u = np.linspace(0, 1, 50)
v = np.linspace(0, 1, 50)
U, V = np.meshgrid(u, v)
axes[0].pcolormesh(U, V, np.sin(2*np.pi*U) * np.cos(2*np.pi*V), cmap='coolwarm')
axes[0].set_title("[0,1]² → 环面 T²")

# 环面嵌入 R³
theta = 2 * np.pi * U  # (2, π) × (2, π)
phi = 2 * np.pi * V
R, r = 2, 1
X = (R + r * np.cos(phi)) * np.cos(theta)
Y = (R + r * np.cos(phi)) * np.sin(theta)
Z = r * np.sin(phi)
axes[1].remove()
ax3d = fig.add_subplot(132, projection='3d')
ax3d.plot_surface(X, Y, Z, cmap='coolwarm', alpha=0.8)
ax3d.set_title("环面 T²")

# 基本群: S¹ 的环路
t = np.linspace(0, 1, 100)
for n in [1, 2, 3]:
    axes[2].plot(np.cos(2*np.pi*n*t), np.sin(2*np.pi*n*t), label=f'缠绕数={n}')
axes[2].set_title("π₁(S¹) = ℤ")
axes[2].legend()
axes[2].set_aspect('equal')
plt.tight_layout()
plt.savefig("topology_demo.png", dpi=100)
print("拓扑演示已保存")
```

---

## ⚠️ 不足层
- 点集拓扑扎实但代数拓扑只入门（基本群）
- 不涉及同调群/上同调（需研究生课）

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| 紧致性 | 参数空间正则化 → 极值存在 |
| 同胚 | 数据流形 = 低维拓扑空间 |
| 商空间 | 等变网络 / 对称性约化 |
| 基本群 | TDA: 数据中"洞"的检测 |
| 覆叠空间 | 多值函数 / 离散对称性 |

---

## 章节概览（Munkres）

| 章 | 内容 | 关键 |
|---|---|---|
| 2-3 | 拓扑空间 | 开集、连续映射 |
| 4-5 | 连通性 / 紧致性 ★★ | Tychonoff |
| 6 | 度量空间 | Baire 定理 |
| 7 | 分离公理 | Urysohn 引理 |
| 9 | 基本群 ★★ | $\pi_1(S^1) = \mathbb{Z}$ |
| 11 | 覆叠空间 | 万有覆叠 |
| 13 | 分类定理 | 曲面分类 |
