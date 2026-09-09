# Harvard Math 112 · 章节笔记（Rudin / Pugh）

> **教材**：Rudin *Principles* 或 Pugh *Real Mathematical Analysis*
> **特色**：Harvard 标准实分析（不像 Math 55 极端），度量空间导向

---

# 费曼三层讲透：度量空间上的分析

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **度量空间** | **"有尺子的世界"**：一切分析都基于距离函数 $d$ |
| **ε-δ 连续** | **"不管你多挑剔，我都能满足"**——客户给 ε，我给 δ |
| **完备性** | **"空间没有洞"**：Cauchy 列到达终点，不会悬空 |
| **紧致性** | **"无处可逃"**：有界+闭 = 所有序列有收敛子列 |
| **一致收敛** | **"整条曲线一起逼近"**：sup 范数 → 0 |

---

## 🧮 数学层

### 度量空间 $(X, d)$

开球 $B_r(p) = \{q : d(p,q) < r\}$。开集/闭集、收敛、Cauchy 列、完备性。

### ε-δ 连续（度量空间版）

$$f: (X, d_X) \to (Y, d_Y) \text{ 在 } p \text{ 连续} \iff \forall \epsilon > 0, \exists \delta > 0: d_X(x,p) < \delta \Rightarrow d_Y(f(x), f(p)) < \epsilon$$

### 4 种收敛模式（Harvard 112 预告 Math 114）

$$L^p \Rightarrow \text{依概率} \Rightarrow \text{依分布}; \quad \text{a.s.} \Rightarrow \text{依概率}$$

### 紧致集上的连续函数
- 取得最值（极值定理）
- 一致连续
- 像 tight（紧致的连续像是紧致的）

### 一致收敛与连续/可积/可导

| 性质 | 逐点 | 一致 |
|---|---|---|
| 连续性 | ❌ | ✅ |
| 可积交换 | ❌ | ✅ |
| 可导交换 | ❌ | 需导数列一致收敛 |

---

## 💻 代码层

```python
import numpy as np
# 度量空间: 不同的距离函数
x, y = 1.0, 3.0
print(f"d_1 = |x-y| = {abs(x-y)}")
print(f"d_2 = sqrt(sum x_i^2) = {np.sqrt((x-y)**2)}")
print(f"d_∞ = max|x_i-y_i| = {max(abs(x-y))}")
# 度量空间完备性: Cauchy 列在 R 中收敛
s = np.cumsum([1/(k*(k+1)) for k in range(1,1001)])
print(f"Cauchy 列 s_1000 = {s[-1]:.10f} → 1 (完备)")
```

---

## ⚠️ 不足层
- 度量空间有限维 → 泛函分析（Math 114）处理无穷维
- Riemann 积分 → Math 114 做 Lebesgue

---

## 🚀 应用层

| 概念 | ML 对应 |
|---|---|
| ε-δ 连续 | ReLU 连续不可微 |
| 紧致+连续 | loss 最小值存在 |
| 一致连续 | Lipschitz 条件 → GAN |
| 一致收敛 | 泛化保证 |
| Stone-Weierstrass | UAT |

---

## 章节概览

| 章 | 内容 | 关键 |
|---|---|---|
| 1 | 度量空间 | 开集/闭集、完备性 |
| 2 | 紧致性 ★ | Heine-Borel、Bolzano-Weierstrass |
| 3 | 连续性 | ε-δ、一致连续 |
| 4 | 微分 | MVT、Taylor |
| 5 | Riemann 积分 | Darboux 和 |
| 6 | 函数序列 ★ | 一致收敛、Arzelà-Ascoli |
| 7 | 特殊函数 | 幂级数、Stone-Weierstrass |
