# Spivak 第 22 章 · Infinite Sequences · 精读笔记

> 基于原书第 22 章(PP.452-470)。Part IV 开端——无穷序列的严格理论。
> 原书:`Calculus (Spivak) 4th ed.` ch22 / 读于:2026-07-01

---

## §0 一句话

> **序列极限的 ε-定义:lim aₙ=l ⟺ ∀ε>0,∃N,∀n>N,|aₙ-l|<ε。与第 5 章函数极限同构,但下标离散——这是级数(第23章)的根基。**

---

## §1 序列极限定义(原书 PP.453-454)

### 定义
$\lim_{n\to\infty}a_n=l$ ⟺ $\forall\varepsilon>0,\exists N\in\mathbb{N},\forall n>N:|a_n-l|<\varepsilon$

> 与第 5 章 $\lim_{x\to\infty}f(x)$ 的区别:这里 $n$ 离散(自然数),那里 $x$ 连续。结构完全平行。

### 序列极限 ↔ 函数极限(原书 P.455)
$\lim a_n=l \iff \lim_{x\to\infty}f(x)=l$(其中 $f$ 是连接 $(n,a_n)$ 的折线)。
∴ 函数极限的定理(和/积/商)直接搬过来。

---

## §2 经典极限(原书 PP.453-455)

| 序列 | 极限 | 技巧 |
|------|------|------|
| $\sqrt{n}$ | 0 | $1/n<\varepsilon$ 取 $N>1/\varepsilon$ |
| $\sqrt{n+1}-\sqrt{n}$ | 0 | 有理化 $=\frac{1}{\sqrt{n+1}+\sqrt{n}}$ 或 MVT |
| $\frac{3n^3+7n^2+1}{4n^3-8n+63}$ | 3/4 | 上下除 $n^3$ |
| $a^n$($0<a<1$) | 0 | $\ln a<0\Rightarrow a^n=e^{n\ln a}\to0$ |

### 极限法则(原书 P.454)
$\lim a_n,\lim b_n$ 存在 ⟹ $\lim(a_n+b_n)=\lim a_n+\lim b_n$(和/积/商同理)。

---

## §3 重要定理(原书 PP.456-470,本章精华)

### 单调有界定理
**有界单调序列必收敛**。
- 依赖 **LUB**(第8章):单调增有上界 ⟹ 收敛到 $\sup$
- 又一次完备性的应用

### Cauchy 序列(原书 PP.460+)
$\{a_n\}$ 是 Cauchy 序列 ⟺ $\forall\varepsilon>0,\exists N,\forall m,n>N:|a_m-a_n|<\varepsilon$
**定理**:实数序列收敛 ⟺ Cauchy。
- 这是 $\mathbb{R}$ **完备性的序列刻画**(等价于 LUB)
- 预告第 29 章:用 Cauchy 序列**构造** $\mathbb{R}$

### 子序列与 Bolzano-Weierstrass
有界序列必有收敛子序列(B-W 定理)——依赖 LUB。

### Stolz 定理(序列版 L'Hôpital)
求 $a_n/b_n$ 极限的工具(分母单调增→∞)。

---

## §4 飞腾/Python 锚点
| 序列概念 | 工程 |
|---------|------|
| 极限 ε-定义 | 数值算法收敛判据(迭代何时停)|
| 单调有界→收敛 | 二分法/牛顿法的收敛保证(Expert_08)|
| Cauchy 序列 = 完备 | 浮点"伪 Cauchy"(有限精度下退化)|
| 子序列 | 采样/降采样 |

---

## §5 自测
1. 写出序列极限的 ε-定义,与函数极限对比。
2. 证 $\sqrt{n+1}-\sqrt{n}\to0$(两种方法:有理化 + MVT)。
3. 证:单调有界序列收敛(用 LUB)。
4. 为什么"Cauchy ⟺ 收敛"等价于 $\mathbb{R}$ 完备?

---

## 📌 下一步
第 23 章(无穷级数)+ 第 24 章(幂级数)+ 第 25-27 章(复分析)——把序列推向级数与复域。
