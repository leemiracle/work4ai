# 不可数但测度为 0：Cantor 集

> 这个反例点破的「以为万能」认知偏差：以为「不可数 ⇒ 必有正体积/正测度」。
> Lakatos 框架定位：原始猜想 = 「集合的大小由"点数"决定」；反例 = Cantor 集；逼迫的改进 = 区分「基数」与「测度」两套独立的大小直觉。

## 构造与定义

Georg Cantor 于 1883 年引入这个集合，原是为理解集合论与基数的工具。

**迭代构造**：

- $C_0 = [0, 1]$
- $C_1$：从 $C_0$ 中删去中间三分之一开区间 $\left(\frac{1}{3}, \frac{2}{3}\right)$，剩 $\left[0, \frac{1}{3}\right] \cup \left[\frac{2}{3}, 1\right]$
- $C_{n+1}$：从 $C_n$ 的每个区间中删去中间三分之一开区间
- Cantor 集：$C = \bigcap_{n=0}^{\infty} C_n$

$$
C = \bigcap_{n=0}^{\infty} C_n
$$

## 为什么它是反例

### 测度为 0

第 $n$ 步后剩下 $2^n$ 个区间，每个长度 $3^{-n}$，总长度

$$
L_n = \left(\frac{2}{3}\right)^n \xrightarrow{n \to \infty} 0.
$$

Cantor 集 $C$ 被含于每个 $C_n$ 中，故

$$
m(C) \leq \lim_{n \to \infty} \left(\frac{2}{3}\right)^n = 0 \quad \Longrightarrow \quad m(C) = 0.
$$

**从测度看，Cantor 集"什么都没有"——但下面将看到它其实"充满"了点。**

### 不可数（基数 = 连续统 $2^{\aleph_0}$）

**三进制表示**是关键。任何 $x \in [0,1]$ 都有三进制小数展开 $x = \sum_{k=1}^{\infty} \frac{d_k}{3^k}$，其中 $d_k \in \{0, 1, 2\}$。

**定理**：$x \in C \iff$ 存在三进制展开只用数字 $0$ 和 $2$。

> 直觉：每一步删去的是「这一位是 1」的点。第一步删 $(1/3, 2/3)$ 对应三进制第一位是 1；第二步删去的是第二位是 1；以此类推。

于是 $C$ 与 $\{0, 2\}^{\mathbb{N}}$ 之间存在双射（每位是 0 或 2 的无穷序列），而 $|\{0, 2\}^{\mathbb{N}}| = 2^{\aleph_0}$。所以

$$
|C| = 2^{\aleph_0} = |\mathbb{R}|.
$$

**Cantor 集与整个实数轴"一样大"（按基数论），却测度为 0——这是反例的内核。**

### 性质总结

| 性质 | 是否满足 |
| --- | --- |
| 紧致 | ✅（闭且含于 $[0,1]$） |
| 完美 (perfect) | ✅（闭，每点是极限点） |
| 无处稠密 (nowhere dense) | ✅（闭集且不含任何开区间） |
| 全不连通 (totally disconnected) | ✅（任两点间存在不在 $C$ 中的点） |
| 自相似 | ✅ $C = \frac{1}{3}C \cup \left(\frac{1}{3}C + \frac{2}{3}\right)$ |
| Hausdorff 维数 | $\frac{\log 2}{\log 3} \approx 0.631$ |

## 它破坏了哪个直觉

**「不可数 ⇒ 必有正体积/正测度」**——这是关于"集合大小"的两个独立直觉的混淆：

- **基数（cardinality）**：集合里"有多少点"，纯集合论概念。
- **测度（measure）**：集合"占多大空间"，几何/拓扑概念。

Cantor 集证明：**这两者完全独立**。一个集合可以基数与 $\mathbb{R}$ 相同（不可数），但测度为 0（"什么都不占"）；反之也可以测度正、但内部空（见下面「胖 Cantor 集」）。

## 它逼迫理论如何改进

1. **测度论必须精细化**：Lebesgue 测度无法单纯用"基数"刻画集合大小，必须从开集覆盖、外测度等独立路径定义。

2. **「胖 Cantor 集」对照**：可以构造类似的迭代——每步删去中间区间，但删去的比例递减使剩余测度 $> 0$（例如 Smith-Volterra-Cantor 集，测度 $1/2$）。它**正测度但内部空**（无处稠密）。胖 Cantor 集是 Cantor 集的"对偶"——一个测度 0 但不可数，一个正测度但无内部。

3. **分形几何的诞生点**：Cantor 集是非整数 Hausdorff 维数的最简单例子（维数 $\log 2 / \log 3$），催生了 Mandelbrot 分形几何（1975+）。「维数可以是非整数」这一颠覆性想法，正源于 Cantor 集的研究。

4. **Baire 范畴 vs 测度的独立性**：Cantor 集**测度为 0 但非第一纲**（它本身就是无处稠密闭集，但作为单点不算 meager 的反例）。范畴与测度是两套「大小」直觉，Cantor 集是检验它们独立性的标准试金石（详见 06 篇）。

## 可视化/代码验证思路

```python
import numpy as np
import matplotlib.pyplot as plt

def cantor_set(depth=15):
    intervals = [(0.0, 1.0)]
    for _ in range(depth):
        nxt = []
        for a, b in intervals:
            cut = (b - a) / 3
            nxt.append((a, a + cut))
            nxt.append((b - cut, b))
        intervals = nxt
    return intervals

# 三进制判别法验证：x ∈ C ⟺ 三进制展开只用 0 和 2
def in_cantor(x, digits=30):
    for _ in range(digits):
        x *= 3
        if int(x) == 1:
            return False
        x -= int(x) if int(x) == 2 else 0
    return True
```

验证：采 $N=10^6$ 个均匀随机点，落在 $C$ 中的比例 $\approx 0$（与测度 0 一致）；但 $C$ 不可数。

## 推荐深入阅读

- Stein & Shakarchi《Real Analysis》第 1 章——Cantor 集的标准现代处理。
- Royden《Real Analysis》第 2 章——构造、性质、与不可数性的关系。
- Mandelbrot《The Fractal Geometry of Nature》（1982）——分形几何开山之作，Cantor 集是第一章起点。
- math-expert `05-history/01-无穷之争` 中 Cantor 集合论一段——历史背景。
- Wikipedia "Smith-Volterra-Cantor set"——胖 Cantor 集的对照反例。
