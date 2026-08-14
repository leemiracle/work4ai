# Cambridge Part IB · 费曼三层讲透：数值分析

> **教材**：Süli & Mayers, *An Introduction to Numerical Analysis* ★
> **特色**：Cambridge Part IB——**严格的误差分析 + 插值 + 求积 + ODE 收敛性证明**

---

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **插值误差** | "插值多项式在已知点精确，在未知点靠外推" |
| **Gauss 求积** | "不是等距选点，而是最优选点"——Chebyshev 节点 |
| **RK 方法阶条件** | "用 Taylor 展开匹配更高阶项"——Butcher 树 |
| **收束阶** | "$p$ 阶方法 = 误差 $O(h^p)$"——halving $h$ 减小误差 $2^p$ 倍 |

> **一句话总结**：Cambridge IB NA = **"数值方法 + 严格证明"**。与 [M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/) 的线代部分互补，本课侧重**插值/求积/ODE 的严格误差分析**。

---

## 🧮 数学层

### 1. 插值误差定理 ★

对 $n+1$ 点 Lagrange 插值 $p_n(x)$：
$$f(x) - p_n(x) = \frac{f^{(n+1)}(\xi)}{(n+1)!}\prod_{i=0}^{n}(x - x_i)$$

**Runge 现象**：等距节点高次插值在边界处发散。解决：Chebyshev 节点 $x_k = \cos(\frac{(2k+1)\pi}{2(n+1)})$。

### 2. Gauss 求积 ★

$n$ 点 Gauss 求积精确到 $2n-1$ 次多项式：
$$\int_{-1}^{1} f(x)\,dx \approx \sum_{k=1}^n w_k f(x_k)$$

节点 $x_k$ 是 Legendre 多项式 $P_n(x)$ 的根。

### 3. ODE 收敛性 ★★

$p$ 阶单步法：局部截断误差 $O(h^{p+1})$，全局误差 $O(h^p)$。

**Dahlquist 等价定理**：单步法收敛 ⟺ 相容（局部误差 → 0）+ 零稳定。

**绝对稳定性**：对 $\dot{y} = \lambda y$，$|R(h\lambda)| \leq 1$（$R$ = 稳定性函数）。

### 4. 多步法（Linear Multistep Methods）

Adams-Bashforth（显式）/ Adams-Moulton（隐式）/ BDF（stiff）。

**Dahlquist 阶障碍**：零稳定 + $p$ 阶的显式多步法最多 $p \leq 2$（A-稳定隐式）。

---

## 💻 代码层

```python
import numpy as np

# Gauss-Legendre 求积 (2点: 精确到3次多项式)
x_gauss = np.array([-1/np.sqrt(3), 1/np.sqrt(3)])
w_gauss = np.array([1.0, 1.0])
# ∫f dx ≈ Σ w_k f(x_k)

# 验证: ∫x³ dx from -1 to 1 = 0
val = sum(w * x**3 for w, x in zip(w_gauss, x_gauss))
print(f"2点Gauss求积 ∫x³ = {val:.6f} (精确值=0)")

# RK4 稳定性函数
def rk4_stability(hlam):
    z = hlam
    return 1 + z + z**2/2 + z**3/6 + z**4/24

# 显式 Euler 稳定性函数
def euler_stability(hlam):
    return 1 + hlam

# 绘制稳定区 |R(z)| ≤ 1
z = np.linspace(-4, 2, 500)
# ... (验证 RK4 比 Euler 稳定区大得多)
```

---

## ⚠️ 不足层
- 严格证明对工程师偏理论，实践中常用库即可
- 多步法的启动需要初始步（单步法不需要）
- A-稳定显式方法不存在（Dahlquist 障碍）

---

## 🔬 应用层
1. **Gauss 求积 → 贝叶斯积分 / 物理仿真**
2. **RK4 → RL 环境动力学 / Neural ODE**
3. **稳定性分析 → 深度网络训练（stiff 梯度流）**
4. **Chebyshev 插值 → 谱方法**（高精度 PDE 求解）

---

## 🆕 2024-2026
- **高阶 Neural ODE**：用 RK4 / Diffrax 替代 Euler，提升连续网络精度
- **自适应步长**：JAX 中的 DOP853 / Dormand-Prince
- **可微求积**：自动微分 + Gauss 求积 → 可微物理

---

## 交叉引用
- [Cambridge Part II NA](../../cambridge-math-courses/partII_numerical_analysis/) — 高级续集（Krylov/谱方法）
- [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/) — 线代数值方法
- [Stanford CME 108](../../stanford-math-courses/cme108_scientific_computing/) — 类似覆盖面
