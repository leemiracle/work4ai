# Stanford CME 108 · 费曼三层讲透：科学计算导论

> **教材**：Heath, *Scientific Computing: An Introductory Survey*（修订版）
> **教授**：Eric Darve
> **特色**：Stanford 工程学院计算基础课——**误差分析 / 插值 / 数值积分 / ODE / 稀疏矩阵**

---

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **浮点误差** | "计算机只能存有限位小数"——$0.1 + 0.2 \neq 0.3$ |
| **插值** | "在已知点之间画一条平滑曲线"——多项式/样条 |
| **数值积分** | "用矩形/梯形/辛普森法估算面积"——quadrature |
| **ODE 求解** | "一小步一小步往前走"——Euler / RK4 |
| **稀疏矩阵** | "大部分元素是 0 的矩阵"——只存非零元 |

> **一句话总结**：CME 108 = **"从连续数学到离散计算的桥梁"**。核心：**误差传播分析 + 稳定性 + 精度与效率的权衡**。

---

## 🧮 数学层

### 1. 浮点数与误差传播 ★

IEEE 754 双精度：$\epsilon_{\text{machine}} \approx 2.2 \times 10^{-16}$（52 位尾数）。

**前向误差** vs **后向误差**：
- 前向：$\|\hat{x} - x\| / \|x\|$（计算结果的误差）
- 后向：$\hat{x}$ 是否是某个"扰动问题"的精确解？（→ M 383E 第 III 部分）

**误差传播**：$f(x+\delta) \approx f(x) + f'(x)\delta$ → 相对误差 $\approx |f'/f| \cdot |\delta/x|$。

### 2. 插值

**Lagrange 插值**：$p(x) = \sum_i y_i \prod_{j \neq i} \frac{x - x_j}{x_i - x_j}$。

**样条插值**：分段三次多项式，$C^2$ 连续，更稳定（避免 Runge 现象）。

### 3. 数值积分（quadrature）

**Newton-Cotes**：梯形法（$O(h^2)$）、辛普森法（$O(h^4)$）。

**Gauss 求积**：$n$ 点精确到 $2n-1$ 次多项式（最优选点）。

### 4. ODE 数值解 ★★

**初值问题** $\dot{y} = f(t, y)$:

| 方法 | 公式 | 精度 | 稳定区 |
|---|---|---|---|
| Euler | $y_{n+1} = y_n + hf(t_n,y_n)$ | $O(h)$ | $\|1 + h\lambda\| \leq 1$ |
| RK4 | 四阶 Runge-Kutta | $O(h^4)$ | 更大 |
| 隐式 Euler | $y_{n+1} = y_n + hf(t_{n+1},y_{n+1})$ | $O(h)$ | **无条件稳定** |

**Stiff 方程**：需要隐式方法（A-稳定），如 BDF / 隐式 Euler。

### 5. 稀疏矩阵与迭代法

稀疏存储（CSR/CSC）+ 迭代求解（CG / GMRES），详见 [M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/notes.md)。

---

## 💻 代码层

```python
import numpy as np

# Runge 现象: 等距插值在高次时不稳定
def lagrange_interp(x, y, xq):
    n = len(x); result = np.zeros_like(xq)
    for i in range(n):
        L = np.ones_like(xq)
        for j in range(n):
            if i != j: L *= (xq - x[j]) / (x[i] - x[j])
        result += y[i] * L
    return result

# RK4 vs Euler
def rk4(f, y0, t):
    y = np.zeros((len(t), len(y0))); y[0] = y0
    for i in range(len(t)-1):
        h = t[i+1] - t[i]; k1 = f(t[i], y[i])
        k2 = f(t[i]+h/2, y[i]+h*k1/2); k3 = f(t[i]+h/2, y[i]+h*k2/2)
        k4 = f(t[i]+h, y[i]+h*k3)
        y[i+1] = y[i] + h*(k1 + 2*k2 + 2*k3 + k4)/6
    return y

# 测试: 简谐振子 y'' + y = 0
f = lambda t, y: np.array([y[1], -y[0]])
t = np.linspace(0, 10, 1000); y0 = [1.0, 0.0]
sol = rk4(f, y0, t)
print(f"RK4 误差: {np.max(np.abs(sol[:,0] - np.cos(t))):.2e}")
```

---

## ⚠️ 不足层
- 浮点误差在深层网络中积累（梯度爆炸/消失的数值根源）
- 高阶多项式插值不稳定（Runge 现象），需样条
- 显式 ODE 解法对 stiff 问题效率极低

---

## 🔬 应用层
1. **RK4 → 物理引擎 / 动力学仿真** → RL 环境设计
2. **数值积分 → 贝叶斯推断**（MCMC 中的 quadrature）
3. **稀疏矩阵 → 大规模推荐系统**
4. **误差分析 → 混合精度训练**（fp16/bf16 的数值稳定性）

---

## 🆕 2024-2026
- **混合精度计算**：Tensor Core 的矩阵乘精度分析
- **神经 ODE**（Chen 2018）：用 ODE solver 做连续深度网络
- **可微物理**：自动微分 + 数值求解器 → JAX/Diffrax

---

## 交叉引用
- [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/) — 线代部分深入
- [MIT 18.085](../../mit-math-courses/18_085_computational_science/) — 差分/PDE/FEM
