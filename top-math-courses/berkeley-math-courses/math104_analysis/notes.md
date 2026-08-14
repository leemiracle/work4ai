# Berkeley MATH 104 · 章节笔记（Ross *Elementary Analysis*）

> **教材**：Ross, *Elementary Analysis: The Theory of Calculus* (2nd ed, Springer, 2013)
> **一手核实**：ISBN 978-1461462705；Berkeley 官方推荐入门教材
> **特色**：比 Rudin 友好得多，循序渐进，是实分析**最佳起点**

---

# 费曼三层讲透：微积分的严格基础

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **ε-δ 极限** | **"无限迫近游戏"**：你给出目标精度 ε，我给出迫近距离 δ |
| **上确界** | **"够得到的天花板"**：最小上界——再低一点就够不到了 |
| **完备性** | **"数轴没有缝隙"**：Cauchy 列（自己越来越紧凑的序列）一定到达终点 |
| **一致连续** | **"统一标准的放大镜"**：不管看哪里，同样的放大倍数（δ）就够 |
| **可积** | **"面积可以被逼近"**：上和与下和的差距可以任意小 |

---

## 🧮 数学层（Ross 核心内容）

### ε-δ 极限 ★

$$\lim_{n \to \infty} s_n = s \iff \forall \epsilon > 0, \exists N, \forall n > N: |s_n - s| < \epsilon$$

**Ross 的教学法**：先讲序列极限（ε-N），再讲函数极限（ε-δ），循序渐进。

### 单调收敛定理

$$s_n \text{ 递增有上界} \implies s_n \text{ 收敛}$$

这是上确界原理的直接推论——Ross 把它作为核心工具。

### Bolzano-Weierstrass

$\mathbb{R}$ 中每个有界序列有收敛子序列。

### 4 种收敛模式预告（Ross 后续课程需要）

$$L^p \Rightarrow \text{依概率} \Rightarrow \text{依分布}; \quad \text{a.s.} \Rightarrow \text{依概率}$$

Ross 只讲确定性序列收敛，但为后续 Berkeley Math 218（概率论）打基础。

---

## 💻 代码层

```python
import numpy as np
# ε-δ 验证: lim 1/n = 0
for eps in [0.1, 0.01, 1e-6]:
    N = int(1/eps) + 1
    print(f"ε={eps} → N={N} → |1/N-0|={1/N:.2e} {'✓' if 1/N < eps else '✗'}")
# 单调收敛: s_n = (1+1/n)^n → e
s = [(1+1/n)**n for n in range(1,1001)]
print(f"s_1000 = {s[-1]:.8f}, e = {np.e:.8f}")
```

---

## ⚠️ 不足层

| 局限 | 说明 |
|---|---|
| **只做 $\mathbb{R}$** | 不做度量空间（Rudin 做 $\mathbb{R}^n$） |
| **Riemann 积分** | 不涉及 Lebesgue |
| **证明较温和** | 严格度低于 Rudin/MAT 215 |

---

## 🚀 应用层

| Ross 概念 | ML 对应 |
|---|---|
| ε-δ 极限 | 数值稳定性 |
| 单调收敛定理 | loss 单调下降的收敛 |
| Taylor 定理 | Newton 法优化 |
| 一致连续 | Lipschitz 条件 |

---

## Ross 章节概览

| 章 | 内容 | 重点 |
|---|---|---|
| 1-2 | 引言、$\mathbb{R}$ 简介 | 实数公理 |
| 3-4 | 序列、子序列 | ε-N 定义、Bolzano-Weierstrass ★ |
| 5-7 | 级数、收敛判别 | 比值、根值、积分判别 |
| 8-10 | 连续性 | ε-δ、一致连续、介值定理 |
| 11-12 | 可导性 | MVT、Taylor ★ |
| 13-15 | Riemann 积分 | Darboux 和、微积分基本定理 |
| 16-17 | 函数序列 | 一致收敛 ★ |
| 18-19 | 级数展开 | 幂级数、Taylor 级数 |
| 20-21 | 度量空间（可选） | 预告 Rudin |

---

## 与 work4ai 交叉

- **讲透激活函数**：Ch 8-12 连续与可导
- **讲透优化器**：Ch 11-12 MVT + Taylor
- **讲透泛化**：Ch 16-17 一致收敛
