# Cambridge Part IB Analysis & Topology · 章节笔记

> **教材**：Cambridge Tripos IB lecture notes + Rudin *PMA* Ch.2-7 + Sutherland *Introduction to Metric and Topological Spaces*
> **特色**：多变量分析 + 度量空间 + 拓扑入门——Cambridge IB 的核心分析课

---

# 费曼三层讲透：度量空间与拓扑

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **度量空间** | **"有尺子的世界"**：一切分析基于 $d(x,y)$ |
| **紧致性** | **"无处可逃"**：有界+闭（有限维） |
| **一致收敛** | **"整条曲线同时逼近"** |
| **压缩映射** | **"每次都拉近"**：$d(Tx,Ty) < d(x,y)$ |
| **拓扑空间** | **"有近邻概念但没尺子"**：度量空间的抽象 |
| **连通性** | **"一整块"**：不能分成不相交的开集 |

---

## 🧮 数学层

### 度量空间 $(X, d)$

$d$: 正定 + 对称 + 三角不等式。

**完备化**: $\mathbb{Q}$ 在 $|\cdot|$ 下 → 完备化 $\mathbb{R}$。

### 紧致性 ★★

等价定义（度量空间）:
1. 每个开覆盖有有限子覆盖
2. 每个序列有收敛子列（Bolzano-Weierstrass 性质）
3. 完备 + 完全有界

**Heine-Borel**: $\mathbb{R}^n$ 中 $\iff$ 有界+闭。

**紧致 + 连续**: → 取最值（极值定理）→ 一致连续。

### 一致收敛 ★

$f_n \rightrightarrows f$ on $S$: $\sup_{x \in S} |f_n(x) - f(x)| \to 0$

| 操作 | 逐点 | 一致 |
|---|---|---|
| 保持连续 | ❌ | ✅ |
| 可积换序 | ❌ | ✅ |
| 可微换序 | ❌ | 需 $f_n'$ 一致收敛 |

**Weierstrass M-判别法**: $|f_n(x)| \leq M_n$, $\sum M_n < \infty$ → $\sum f_n$ 一致收敛。

### 压缩映射原理 ★★

$(X, d)$ 完备, $T: X \to X$ 压缩 ($d(Tx,Ty) \leq q \cdot d(x,y)$, $q < 1$) → **唯一不动点**。

迭代: $x_{n+1} = T(x_n) \to x^*$, $d(x_n, x^*) \leq \frac{q^n}{1-q} d(x_1, x_0)$。

**ML 应用**: $\theta_{k+1} = \theta_k - \eta \nabla L(\theta_k)$ 是压缩映射 $\iff$ $\eta L_{lip} < 1$。

### 拓扑空间 $(X, \tau)$

$\tau$: 任意并 + 有限交封闭。

**连续** = 开集原像开。

**商空间** $X/\sim$: 等价类 → 新空间。

### 连通性

$X$ 连通 $\iff$ 不能写成两个非空分离开集的并。

**ML 应用**: loss landscape 连通性 → 局部极小值之间的路径。

### 多变量分析速成

- Jacobian 矩阵 + 链式法则
- 反函数定理: $\det J \neq 0$ → 局部可逆
- 隐函数定理: $F(x,y) = 0$ + $\partial F/\partial y \neq 0$ → $y = g(x)$

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt

# 压缩映射: Newton 法求 sqrt(2)
def newton_sqrt():
    x = 2.0  # 初始值
    history = [x]
    for _ in range(10):
        x = 0.5 * (x + 2.0 / x)  # T(x) = (x + 2/x)/2
        history.append(x)
    return history

hist = newton_sqrt()
print("Newton 法收敛到 sqrt(2):")
for i, x in enumerate(hist):
    err = abs(x - np.sqrt(2))
    print(f"  x_{i} = {x:.10f}, 误差 = {err:.2e}")

# 一致收敛 vs 逐点收敛
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
x = np.linspace(0, 1, 200)
for n in [1, 5, 10, 50]:
    axes[0].plot(x, x**n, label=f'n={n}')
axes[0].set_title("x^n: 逐点→0 但不一致 (sup=1/4)")
axes[0].legend()

for n in [1, 5, 10, 50]:
    axes[1].plot(x, x**n / n, label=f'n={n}')
axes[1].set_title("x^n/n: 一致→0 (sup=1/n→0)")
axes[1].legend()
plt.tight_layout()
plt.savefig("convergence_demo.png", dpi=100)
print("\n收敛模式对比已保存")
```

---

## ⚠️ 不足层
- 不做 Lebesgue 积分（Part II Measure & Probability）
- 拓扑只入门（Part II Algebraic Topology）
- 泛函分析在 Part II

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| 紧致 + 连续 | 参数正则化 → 极值存在 |
| 一致收敛 | 泛化保证 |
| 压缩映射 | SGD 收敛速率 |
| 反函数定理 | Normalizing Flows |
| 链式法则 | 反向传播 |
| 商空间 | 等变网络 |

---

## 章节概览

| 章 | 内容 | 关键 |
|---|---|---|
| 1 | 度量空间 | 完备性、完备化 ★ |
| 2 | 紧致性 ★★ | Heine-Borel、极值定理 |
| 3 | 一致收敛 | Weierstrass M-判别法 |
| 4 | 压缩映射 ★★ | Banach 不动点 |
| 5 | 拓扑空间 | 连续 = 原像开 |
| 6 | 连通性 | 路径连通 |
| 7 | 多变量分析 | Jacobian、反/隐函数定理 |
