# 连续但处处不可导：Weierstrass 怪物

> 这个反例点破的「以为万能」认知偏差：以为「连续函数几乎处处可导」是常态。
> Lakatos 框架定位：原始猜想 = 「连续 ⇒ 几乎处处可导」；反例 = Weierstrass 函数；逼迫的 lemma-incorporation = 一致收敛条件 + 几何直觉永久降级。

## 构造与定义

1872 年，Karl Weierstrass 向柏林数学学会报告了下面这个函数：

$$
W(x) = \sum_{n=0}^{\infty} a^n \cos(b^n \pi x)
$$

参数满足：$0 < a < 1$，$b$ 为正奇数。Weierstrass 原始证明用的条件是

$$
ab > 1 + \frac{3\pi}{2}.
$$

后来 G. H. Hardy（1916）将条件精简为 $ab \geq 1$，即**振幅衰减速度 $a$ 不足以压制频率 $b$ 的震荡**——这是「处处不可导」的本质条件。

## 为什么它是反例

### 处处连续（一致收敛 + 连续极限）

由 Weierstrass M-判别法：

$$
\left| a^n \cos(b^n \pi x) \right| \leq a^n, \qquad \sum_{n=0}^{\infty} a^n = \frac{1}{1-a} < \infty \;\;(0<a<1).
$$

故级数在 $\mathbb{R}$ 上**一致收敛**。每一项 $a^n \cos(b^n \pi x)$ 是连续函数，连续函数列的一致极限仍连续。所以 $W(x)$ 在 $\mathbb{R}$ 上处处连续。

### 处处不可导（关键条件 $ab > 1$）

证明思路：固定 $x_0$，对每个 $m \in \mathbb{N}$，构造序列 $h_m \to 0$，使得差商

$$
\left| \frac{W(x_0 + h_m) - W(x_0)}{h_m} \right| \to \infty.
$$

具体取 $h_m = \frac{1 - x_0 \text{ 的小数部分相关的奇偶调整}}{2 b^m}$（标准证明细节见 Stein-Shakarchi 或 Royden），关键用到：

- 低频部分（$n \leq m$）的差商被放大 $b^m$ 倍；
- 高频部分（$n > m$）的差商有界且被三角恒等式控制；
- 当 $ab > 1$ 时，低频放大主导，差商发散。

**结论**：$W$ 在 $x_0$ 处不可导。$x_0$ 是任取的，故处处不可导。

## 它破坏了哪个直觉

19 世纪主流直觉是「**连续函数除了个别点外都可导**」。Bolzano（约 1830）甚至构造过一个「连续但不可导」的例子但未发表；Riemann 的学生也讨论过类似函数。但 Weierstrass 是第一个给出**严格证明**的人，而且是一举证明「处处不可导」这个最极端版本。

Charles Hermite 据说惊呼：

> 「我怀着恐惧转向这令人怜悯的怪物 (this distressing monster)。」

Henri Poincaré 也说这类函数「折磨着眼睛」。

**直觉被打碎**：「连续」和「光滑」是两回事；光滑根本不是连续的常态。

## 它逼迫理论如何改进（Lakatos lemma-incorporation）

1. **几何直觉被永久降级**：从此任何基于「画图能看出来的」论证都不可信，只有 $\varepsilon$-$\delta$ 才算数。这是分析严格化的真正起点。

2. **一致收敛概念被推上前台**：Cauchy 曾错误认为「连续函数级数收敛则和连续」。Weierstrass 怪物的存在说明这必须加「**一致收敛**」条件。Stokes 与 Seidel（1847–1848）独立提出一致收敛概念，正是被这类反例所逼。

3. **Baire 范畴定理揭示真相**：后来 Baire（1899）证明：连续函数空间 $C[0,1]$ 中，**处处可导函数是第一纲集（meager，"瘦集合"）**；处处连续处处不可导的函数反而是「典型」——第二纲集（comeager）。可导才是稀有特例，不可导才是常态。

$$
\{ f \in C[0,1] : f \text{ 在某点可导} \} \text{ 是第一纲集；其补集是第二纲集（"典型"的连续函数）.}
$$

这彻底颠覆了「连续函数几乎处处可导」的直觉——它不仅在逻辑上错，在「典型性」意义上也完全反了。

## 可视化/代码验证思路

用 numpy 截断前 $N$ 项画图：

```python
import numpy as np
import matplotlib.pyplot as plt

def weierstrass(x, a=0.5, b=11, N=50):
    return sum(a**n * np.cos(b**n * np.pi * x) for n in range(N))

x = np.linspace(0, 1, 100000)
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for ax, N in zip(axes.flat, [5, 20, 50, 200]):
    ax.plot(x, weierstrass(x, N=N), lw=0.3)
    ax.set_title(f'N = {N}')
plt.tight_layout()
plt.show()
```

观察：随 $N$ 增大曲线越来越「毛刺」；放大任何一段都粗糙（**自相似**——这正是分形的萌芽，Hausdorff 维数 $= \log b / \log(1/a)$）。

## 推荐深入阅读

- Stein & Shakarchi《Fourier Analysis》第 3 章——给出 Hardy 条件 $ab \geq 1$ 的完整证明。
- Royden《Real Analysis》第 6 章——Baire 范畴定理与「典型连续函数处处不可导」的严格推导。
- Imre Lakatos《Proofs and Refutations》——本反例所遵循的「证明-反驳」方法论母本。
- math-expert `05-history/01-无穷之争-芝诺到勒贝格.md`——Weierstrass 怪物在分析严格化史中的位置。
- YouTube：Mathologer *The darkest problem in all of mathematics* 与 3Blue1Brown 分形系列——可视化直觉。
