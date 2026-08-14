# UT Austin M 365C · 章节笔记（Rudin *PMA* / Abbott）

> **教材**：Rudin *Principles* Ch.1-5 或 Abbott *Understanding Analysis*
> **特色**：UT Austin 本科实分析——度量空间 + 多变量分析入门

---

# 费曼三层讲透：实分析（UT Austin 版）

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **度量空间** | **"有尺子的空间"**：一切分析基于距离 $d$ |
| **完备性** | **"没有洞"**：Cauchy 列收敛 |
| **紧致性** | **"有界+闭"**（有限维）→ 序列有收敛子列 |
| **ε-δ 连续** | **"精度可控"**：ε 给目标, δ 给策略 |
| **一致收敛** | **"整条曲线同时逼近"** |

---

## 🧮 数学层

### 度量空间基础

$(X, d)$: 开球 $B_r(p) = \{q : d(p,q) < r\}$。开集 = 开球的并。

### 完备性 ★★

$\mathbb{R}$ 完备: Cauchy 列 $\Rightarrow$ 收敛列。

**不完备例子**: $\mathbb{Q}$（$1, 1.4, 1.41, 1.414, ...$ 是 $\mathbb{Q}$ 中 Cauchy 列但收敛到 $\sqrt{2} \notin \mathbb{Q}$）。

### 紧致性 ★★★

**Bolzano-Weierstrass**: $\mathbb{R}^n$ 中有界序列有收敛子列。

**Heine-Borel**: $S \subset \mathbb{R}^n$ 紧致 $\iff$ 有界 + 闭。

**紧致 + 连续**: $\Rightarrow$ 取最值 (极值定理), 一致连续。

**ML 核心**: $\{\theta : \|\theta\| \leq R\}$ 紧致 → loss 最小值存在 → 优化良定义。

### 连续函数 ★

ε-δ 定义 → 度量空间版。

**IVT**: $f$ 连续, $f(a) < 0 < f(b)$ → $\exists c: f(c) = 0$。

### 可微 + Taylor

$f'(c) = \lim_{h\to0} \frac{f(c+h)-f(c)}{h}$

**MVT**: $\exists c: f'(c) = \frac{f(b)-f(a)}{b-a}$

**ML 应用**: MVT → 梯度路径可达性；Taylor → 牛顿法。

### 序列与级数

| 收敛 | 判别 |
|---|---|
| 正项级数 | 比较、比值、根值、积分 |
| 一般级数 | 绝对收敛 → 收敛 |
| 交错 | Leibniz: $a_n \searrow 0$ |
| 幂级数 | $R = 1/\limsup|c_n|^{1/n}$ |

### 函数序列 ★

一致收敛: $\sup |f_n - f| \to 0$

$f_n \rightrightarrows f$ + $f_n$ 连续 → $f$ 连续

$f_n \rightrightarrows f$ + 可积 → $\int f_n \to \int f$

$f_n' \rightrightarrows g$ + $f_n(x_0)$ 收敛 → $f_n \to f$ 可微, $f' = g$

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt

# 紧致性: [0,1] 紧致 vs (0,1) 不紧致
# 序列 1/n 在 (0,1) 中无收敛子列 (极限 0 ∉ (0,1))
seq = np.array([1/n for n in range(1, 50)])
print(f"序列 1/n 的前5项: {seq[:5]}")
print(f"极限 = 0")
print(f"0 ∈ [0,1]? {0 >= 0 and 0 <= 1}  → [0,1] 紧致")
print(f"0 ∈ (0,1)? {0 > 0 and 0 < 1}    → (0,1) 不紧致")

# 极值定理: 连续函数在紧致集上取最值
x = np.linspace(-1, 1, 100)
f = x**2 + 1  # 连续
print(f"\nf(x) = x² + 1 on [-1,1]")
print(f"min f = {min(f):.4f} at x=0")
print(f"max f = {max(f):.4f} at x=±1")
print("紧致集上连续函数取最值 ✓")

# 一致收敛演示
fig, ax = plt.subplots(figsize=(8, 4))
for n in [1, 2, 5, 20]:
    fn = np.exp(-n * x**2)  # 逐点→0 (x≠0), 一致→0? No (sup=1 at x=0)
    ax.plot(x, fn, label=f'n={n}')
ax.set_title("exp(-nx²): 逐点→0 但不一致 (sup=1)")
ax.legend()
plt.tight_layout()
plt.savefig("uniform_convergence.png", dpi=100)
```

---

## ⚠️ 不足层
- 只做度量空间入门 → 研究生 M 381C 做测度论
- 不做 Lebesgue 积分 → M 381C
- 拓扑空间概念不做（M 367K 概率 / 独立拓扑课）

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| 紧致 + 连续 | 参数正则化 → 极值存在 |
| ε-δ 连续 | ReLU 分析（连续不可微） |
| MVT | 优化路径可达性 |
| 一致收敛 | 泛化保证 |
| 幂级数 | softmax / 特征展开 |
| Weierstrass M-判别 | Fourier 级数收敛 |

---

## 章节概览

| 章 | 内容 | 关键 |
|---|---|---|
| 1 | 实数 | 完备性 ★★ |
| 2 | 度量空间 | 开集/闭集 |
| 3 | 紧致性 ★★★ | Heine-Borel、极值定理 |
| 4 | 连续性 | ε-δ、IVT |
| 5 | 可微 | MVT、Taylor |
| 6 | 序列/级数 | 判别法 |
| 7 | 函数序列 ★ | 一致收敛 |
