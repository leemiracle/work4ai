# 病态填充空间曲线：Peano 与 Hilbert 的维数破坏者

> 这个反例点破的「以为万能」认知偏差：以为「曲线必是一维」。
> Lakatos 框架定位：原始猜想 = 「连续映射保持维数 / 曲线 = 1 维对象」；反例 = Peano 曲线；逼迫的改进 = 拓扑维数严格化 + Hausdorff 维数引入。

## 构造与定义

1890 年，Giuseppe Peano 给出第一个**填充空间的曲线**——一个连续满射

$$
f: [0,1] \to [0,1]^2, \quad \text{使 } f([0,1]) = [0,1]^2 \text{（填满整个正方形）}.
$$

Peano 的原始构造是**解析公式**（用三进制展开编码）。1891 年，David Hilbert 给出了更几何化的迭代构造，今天称为 **Hilbert 曲线**：

**迭代思路**：

1. 第 $1$ 步：把单位正方形分 $4 = 2^2$ 个小格，曲线依次穿过每格中心，形成「凹」字形。
2. 第 $n$ 步：分 $4^n$ 个小格，曲线依次穿过每格中心，每一步缩小尺度。
3. $n \to \infty$ 时，曲线连续地逼近一个极限 $f$，且像稠密于正方形。

**关键定理**：$[0,1]$ 紧致，$[0,1]^2$ Hausdorff；连续映射的像是紧致（闭）；稠密 + 闭 $=$ 全集。故

$$
f([0,1]) = [0,1]^2.
$$

即 Hilbert 曲线**满射到整个正方形**——这就是「填充空间」的含义。

## 为什么它是反例

### 连续映射不保持维数

直觉里「曲线 = 一维对象」「正方形 = 二维对象」，一维不可能塞满二维。Peano/Hilbert 曲线打破这一点：

> **存在连续满射 $f: [0,1] \twoheadrightarrow [0,1]^d$ 对任何 $d \geq 1$**（高维 Peano 曲线也存在）。

### 不是单射（必非一一）

Peano 曲线**不是单射**——这是必然的。如果 $f$ 是一一的，则 $f: [0,1] \to [0,1]^2$ 是连续双射；由于 $[0,1]$ 紧致、$[0,1]^2$ Hausdorff，$f$ 自动是**同胚**。但这不可能：

> 去掉 $[0,1]$ 的内点（如 $1/2$），结果不连通（两段）；去掉 $[0,1]^2$ 的任意点，结果仍连通。同胚保持这种拓扑性质，矛盾。

所以 Peano 曲线必然「自我相交无穷多次」。

## 它破坏了哪个直觉

**「曲线必是一维」**——这一直觉有两层：

1. **「曲线 = 线」的几何直觉**：直观上「画一条线」总是 1 维细丝。Peano 曲线让"线"塞满"面"。
2. **「连续映射保持维数」的拓扑直觉**：人们以为维数是拓扑不变量。Peano 曲线证明：**拓扑维数对连续像不保持**——这是维数理论必须解决的危机。

更深一层：这件事说明 **「连续」远比「直观连续」宽泛**。一条"几何上很好看"的曲线和一条"塞满正方形"的怪物的拓扑定义是同一个——都是 $[0,1] \to X$ 的连续映射。要区分它们，必须引入更精细的维数概念。

## 它逼迫理论如何改进

1. **维数理论的严格化**：Hurewicz-Wallman（1948）等发展了**拓扑维数（covering dimension / 大归纳维数 / 小归纳维数）**的严格理论。结论：拓扑维数是**拓扑不变量**（同胚保持），但对**一般连续像**不一定保持——除非加上「闭映射」或「度量空间 + 有限维」等额外条件。

2. **Hausdorff 维数的引入**：Hausdorff（1918）引入更精细的**Hausdorff 维数** $\dim_H$：

$$
\dim_H([0,1]^d) = d, \quad \dim_H(\text{Peano 曲线像}) = 2.
$$

Hausdorff 维数对 Lipschitz 映射保持单调，但对一般连续映射可以增加。**Peano 曲线像的 Hausdorff 维数 $= 2$**，与正方形本身相同——它"真的是二维的"。

3. **分形几何的催生**：Peano 曲线是 Mandelbrot「分形」概念的前驱之一——一个对象有非整数或"超出直观"的 Hausdorff 维数。Mandelbrot（1975+）正式建立分形几何。

4. **计算机科学的意外应用**：Hilbert 曲线在数据库与图像处理中用于**空间填充索引**——把 2D 数据映射到 1D 序列时，Hilbert 曲线比简单扫描更好地**保持局部性**（相邻 2D 点在 1D 序列中也大致相邻）。这是 Google 的 S2、PostGIS 的 Hilbert 索引等的核心思想。

## 可视化/代码验证思路

```python
import numpy as np
import matplotlib.pyplot as plt

def hilbert_curve(order):
    """生成 order 阶 Hilbert 曲线的点序列"""
    n = 2 ** order
    pts = []
    for d in range(n * n):
        # d -> (x, y) via Hilbert mapping
        x, y, t = d, 0, 1
        while t < n:
            rx = 1 & (x // 2)
            ry = 1 & (x // 2)
            if ry == 0:
                if rx == 1:
                    x = t - 1 - x
                    y = t - 1 - y
                x, y = y, x
            x += t * rx
            y += t * ry
            t *= 2
        pts.append((x / (n-1), y / (n-1)))
    return np.array(pts)

fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, order in zip(axes, [1, 2, 4, 7]):
    pts = hilbert_curve(order)
    ax.plot(pts[:, 0], pts[:, 1], lw=0.3)
    ax.set_title(f'order = {order}, N = {len(pts)}')
plt.tight_layout()
plt.show()
```

观察：order 越大，曲线越"稠密地"覆盖正方形。order $= 7$ 时已看不出空隙。

## 推荐深入阅读

- Hans Sagan《Space-Filling Curves》（1994）——主题专著，从 Peano 到现代统一处理。
- Stein & Shakarchi《Real Analysis》第 1 章（练习）——严格证明 Hilbert 曲线满射。
- Mandelbrot《The Fractal Geometry of Nature》（1982）——分形几何与 Peano 曲线的传承关系。
- Hilbert 1891 原文（*Über die stetige Abbildung einer Linie auf ein Flächenstück*）——历史文献。
- math-expert `05-history/`（待建）—— Cantor 与维数危机的历史脉络。
