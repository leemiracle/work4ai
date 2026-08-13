# Princeton MAT 322 · 偏微分方程 精读笔记

> **教材**：Strauss, *Partial Differential Equations: An Introduction*；进阶 Evans, *PDE*
> **参考**：[math.princeton.edu/undergraduate](https://www.math.princeton.edu/undergraduate)

---

## 〇、费曼直觉层：PDE 到底在研究什么？

### 一句话直觉

> **PDE = 描述"变化的变化"的方程——物理定律的数学语言。**

ODE（常微分方程）描述一个量如何随时间变化。PDE 描述一个量如何**同时**随多个变量（时间+空间）变化。

**三个典范 PDE**：
| PDE | 直觉 | ML 对应 |
|---|---|---|
| **热方程** $u_t = \Delta u$ | 浓度平滑化：高浓度流向低浓度 | **扩散模型** ★ |
| **波方程** $u_{tt} = c^2 \Delta u$ | 扰动以速度 $c$ 传播 | 物理模拟 AI |
| **拉普拉斯方程** $\Delta u = 0$ | 达到平衡：处处平均 | 图半监督学习 |

### 热方程的直觉

想象滴一滴墨水进水里。最初墨水集中在一个点。随时间推移，墨水**扩散**开来，浓度越来越均匀。

数学上：$u(x,t)$ = 时刻 $t$ 在位置 $x$ 的墨水浓度。
$$\frac{\partial u}{\partial t} = D \frac{\partial^2 u}{\partial x^2}$$

- 左边：浓度随时间的变化率
- 右边：浓度的"曲率"（凸的地方浓度下降，凹的地方上升）
- $D$：扩散系数

**关键结论**：热方程的解就是**高斯卷积**！$u(x,t) = \int G(x-y, t) u_0(y) dy$，其中 $G$ 是热核（高斯函数）。这就是为什么扩散模型叫"扩散"——它们在数学上就是热方程的随机版本。

---

## 一、数学层：核心定义与定理

### 1.1 三大典范 PDE

**热方程**（扩散方程）：
$$u_t = \alpha^2 \Delta u = \alpha^2 (u_{xx} + u_{yy} + u_{zz})$$

**波方程**：
$$u_{tt} = c^2 \Delta u$$

**拉普拉斯/泊松方程**：
$$\Delta u = 0 \quad (\text{Laplace}), \qquad \Delta u = f \quad (\text{Poisson})$$

其中 $\Delta = \sum_i \frac{\partial^2}{\partial x_i^2}$ 是**拉普拉斯算子**。

### 1.2 分离变量法 ★

**核心思想**：假设解可以分解 $u(x,t) = X(x)T(t)$，将 PDE 化为两个 ODE。

**热方程在 $[0,L]$ 上的分离变量**：
$$u(x,t) = X(x)T(t) \implies X T' = \alpha^2 X'' T \implies \frac{T'}{\alpha^2 T} = \frac{X''}{X} = -\lambda$$

- $X'' + \lambda X = 0$ + 边界条件 → **Sturm-Liouville 特征值问题**
- $T' = -\lambda\alpha^2 T \implies T(t) = e^{-\lambda\alpha^2 t}$

**解**：
$$u(x,t) = \sum_{n=1}^{\infty} B_n \sin\frac{n\pi x}{L}\, e^{-(n\pi\alpha/L)^2 t}$$

**关键观察**：高频项（大 $n$）衰减更快 → 热方程**平滑**了高频信息。

### 1.3 Fourier 级数 ★

任何"合理"的周期函数可以展开为正弦/余弦级数：
$$f(x) = \frac{a_0}{2} + \sum_{n=1}^{\infty}\left(a_n\cos\frac{n\pi x}{L} + b_n\sin\frac{n\pi x}{L}\right)$$

$$a_n = \frac{1}{L}\int_{-L}^L f(x)\cos\frac{n\pi x}{L}dx, \quad b_n = \frac{1}{L}\int_{-L}^L f(x)\sin\frac{n\pi x}{L}dx$$

**Parseval 定理**：$\int |f|^2 = \sum |a_n|^2 + |b_n|^2$（能量守恒——时域和频域能量相等）。

### 1.4 热核与基本解 ★

热方程 $u_t = \Delta u$ 在 $\mathbb{R}^n$ 上的**基本解**（热核）：
$$G(x,t) = \frac{1}{(4\pi t)^{n/2}} e^{-|x|^2/(4t)}, \quad t > 0$$

解的**卷积表示**：
$$u(x,t) = \int_{\mathbb{R}^n} G(x-y, t)\, u_0(y)\, dy = (G(\cdot, t) * u_0)(x)$$

**直觉**：热方程的解 = 初始条件与高斯核的卷积。时间越大，高斯越宽（方差 $\propto t$），解越平滑。

### 1.5 最大值原理 ★

**定理**：热方程 $u_t = \Delta u$ 在有界区域 $\Omega \times [0,T]$ 上的解，其最大值出现在**初始时刻 $t=0$ 或边界 $\partial\Omega$** 上。

**推论**：内部不会自发产生新极值——热量只能从边界/初始条件传入。

**ML 意义**：扩散过程不会"创造"新信息，只会平滑/混合——这保证了扩散模型前向过程的良定性。

### 1.6 特征线法（一阶 PDE）

对一阶 PDE $a(x,y)u_x + b(x,y)u_y = f$，**特征线**是 ODE 系统：
$$\frac{dx}{ds} = a(x,y), \quad \frac{dy}{ds} = b(x,y), \quad \frac{du}{ds} = f(x,y)$$

沿特征线，PDE 化为 ODE。

### 1.7 Green 函数

泊松方程 $\Delta u = f$ 的解：$u(x) = \int G(x,y) f(y) dy$

- $G(x,y)$ = 点源 $y$ 在 $x$ 处产生的场
- $n=2$: $G \sim \frac{1}{2\pi}\ln|x-y|$（对数势）
- $n=3$: $G \sim -\frac{1}{4\pi|x-y|}$（牛顿势）

---

## 二、代码层：热方程数值模拟

```python
import numpy as np
import matplotlib.pyplot as plt

# 有限差分法解热方程 u_t = D * u_xx
L, T = 1.0, 0.1
Nx, Nt = 100, 5000
dx, dt = L/Nx, T/Nt
D = 0.01
alpha = D * dt / dx**2  # 稳定性条件: alpha < 0.5
assert alpha < 0.5, f"不稳定: alpha={alpha}"

x = np.linspace(0, L, Nx+1)
u = np.zeros(Nx+1)
u[Nx//2 - 5:Nx//2 + 5] = 1.0  # 初始: 中心一个脉冲

snapshots = [u.copy()]
for n in range(Nt):
    u_new = u.copy()
    u_new[1:-1] = u[1:-1] + alpha * (u[2:] - 2*u[1:-1] + u[:-2])
    u = u_new
    if n % 1000 == 0:
        snapshots.append(u.copy())

for i, snap in enumerate(snapshots):
    plt.plot(x, snap, label=f't={i*T/len(snapshots):.3f}')
plt.xlabel('x'); plt.ylabel('u'); plt.legend()
plt.title('热方程: 脉冲扩散 → 高斯')
plt.savefig('heat_equation_diffusion.png', dpi=150)
plt.show()
```

### 与高斯卷积的验证

```python
# 热方程解 = 高斯卷积初始条件
from scipy.ndimage import gaussian_filter1d
u0 = np.zeros(Nx+1); u0[Nx//2 - 5:Nx//2 + 5] = 1.0
sigma_t = np.sqrt(2 * D * T) / dx  # 热核的方差 ~ sqrt(2Dt)
u_gaussian = gaussian_filter1d(u0, sigma=sigma_t)
# u_gaussian ≈ 数值解 at t=T
```

---

## 三、与 ML 的联系 ★（PDE 的核心 ML 价值）

### 3.1 扩散模型 = 随机热方程 ★

**DDPM**（Ho et al. NeurIPS 2020, [2006.11239](https://arxiv.org/abs/2006.11239) ✅）的前向过程：
$$dx = -\frac{1}{2}\beta(t) x\, dt + \sqrt{\beta(t)}\, dW_t$$

这是热方程的**随机版本**（加入布朗运动 $dW_t$）。数据分布被逐步"加热"（加噪）直到变成纯高斯。

反向过程（生成）= **逆向热流**——从噪声恢复数据。详见 [ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/) 和 [Oxford C8.1 SDE](../../oxford-math-courses/partC_c8_1_sde/)。

### 3.2 分数匹配 = 对数密度的梯度

Score-based 模型（Song et al. 2021, [2011.13456](https://arxiv.org/abs/2011.13456) ✅）：
$$\nabla_x \log p_t(x) = -\frac{x - \sqrt{\bar\alpha_t} x_0}{1 - \bar\alpha_t}$$

分数函数 = Fokker-Planck 方程中漂移项的核心——PDE 与生成模型的桥梁。

### 3.3 图拉普拉斯 → 半监督学习

图上的拉普拉斯矩阵 $L = D - A$（度矩阵 - 邻接矩阵）是连续拉普拉斯算子的**离散化**。

**标签传播**（Zhu & Ghahramani 2002）：$\frac{dF}{dt} = -LF$ → 已知标签沿图扩散到未知节点。

### 3.4 PDE 神经网络（PINN）

**Physics-Informed Neural Networks**（Raissi et al. 2019, [physics-informed deep learning](https://www.sciencedirect.com/science/article/pii/S0021999118307125) ✅）：用神经网络 $u_\theta(x,t)$ 近似 PDE 解，损失函数中加入 PDE 残差：
$$\mathcal{L} = \|u_\theta - u_{data}\|^2 + \lambda\|u_t - \Delta u_\theta\|^2$$

---

## 四、不足层与边界

1. **经典 PDE 理论偏线性**：热/波/拉普拉斯都是线性的。ML 中的 PDE（如 PINN 的非线性方程）需要非线性 PDE 理论（弱解、Sobolev 空间）——这超出本课范围。
2. **边界条件至关重要**：Dirichlet/Neumann/Robin 边界条件的选择深刻影响解。ML 中通常考虑全空间 $\mathbb{R}^n$，边界条件被吸收进核卷积表示。
3. **高维 PDE 很难**：$n > 3$ 时，经典 PDE 理论的工具（Sobolev 嵌入定理等）变得微妙。而 ML 中的扩散在几百到几千维空间中运作——这需要完全不同的概率方法（不是经典 PDE 分析）。

---

## 五、应用层速查

| 应用 | PDE 工具 | 效果 |
|---|---|---|
| **扩散模型** | 热方程 + SDE | DDPM/Score-based 生成 |
| **图半监督** | 离散拉普拉斯 | 标签传播 |
| **PINN** | PDE 残差损失 | 用 NN 解 PDE |
| **图像处理** | 热方程 = 高斯模糊 | 各向异性扩散去噪 |
| **流体模拟** | Navier-Stokes | 物理 AI |

---

## 六、推荐路径

1. **Strauss 第 1-5 章**：三大 PDE + 分离变量 + Fourier 级数 → **核心**
2. **Strauss 第 7 章**：最大值原理 → **理解扩散模型的关键**
3. **跳过**：高阶 Sobolev 空间理论（除非做 PINN）
4. **交叉**：[ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)（随机版热方程 → 扩散模型）

---

## 术语对照

| 英文 | 中文 |
|---|---|
| Heat equation | 热方程/扩散方程 |
| Wave equation | 波方程 |
| Laplace equation | 拉普拉斯方程 |
| Laplacian $\Delta$ | 拉普拉斯算子 |
| Separation of variables | 分离变量法 |
| Fourier series | 傅里叶级数 |
| Heat kernel | 热核（高斯函数）|
| Maximum principle | 最大值原理 |
| Green's function | 格林函数 |
| Method of characteristics | 特征线法 |
| Sturm-Liouville | 施图姆-刘维尔理论 |
| Well-posedness | 适定性（Hadamard）|
