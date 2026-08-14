# Cambridge Part IB NA · 习题集

### Q1（基础）
证明 2 点 Gauss-Legendre 求积对 3 次多项式精确。

<details><summary>解</summary>

节点 $x_k = \pm 1/\sqrt{3}$, $w_k = 1$。验证 $\int_{-1}^1 x^3 dx = 0$，$\sum w_k x_k^3 = (-1/\sqrt{3})^3 + (1/\sqrt{3})^3 = 0$ ✓。

一般地，$n$ 点 Gauss 求积精确到 $2n-1$ 次。
</details>

### Q2（中等）
Runge 现象：对 $f(x) = 1/(1+25x^2)$，等距 11 点插值的最大误差出现在哪里？

<details><summary>解</summary>

误差在区间边界 $|x| \approx 0.9$ 附近最大，可达 $\sim 1.9$（而函数值 $\leq 1$）！Chebyshev 节点下最大误差 $\sim 0.1$。

**ML 关联**：高阶多项式拟合不稳定 → 用低阶或正则化。
</details>

### Q3（中等）
RK4 对 $\dot{y} = \lambda y$ 的绝对稳定区比显式 Euler 大多少？

<details><summary>解</summary>

Euler: $|1 + z| \leq 1$ → 圆盘 $|z+1| \leq 1$（实轴上 $(-2, 0)$）。
RK4: $|1 + z + z^2/2 + z^3/6 + z^4/24| \leq 1$ → 实轴上约 $(-2.78, 0)$。

RK4 的实稳定区比 Euler 宽 $\approx 39\%$。
</details>

### Q4（开放）
Dahlquist 阶障碍说什么？为什么 A-稳定的显式多步法不存在？

<details><summary>提示</summary>

Dahlquist 第二障碍：A-稳定多步法的阶 $p \leq 2$。隐式梯形法（$p=2$）是 A-稳定中最精确的。

显式方法不可能 A-稳定，因为稳定性函数是多项式（$|p(z)| \leq 1$ 对所有 $\text{Re}(z) < 0$ 不可能成立）。
</details>

### Q5（开放 — ML）
Neural ODE 用 Euler 法 vs RK4，训练效果差异？

<details><summary>提示</summary>

RK4 精度更高（$O(h^4)$ vs $O(h)$），但每步代价 4 倍。Chen 2018 用 "dopri5"（自适应 RK）。实践：精度 vs 计算量的权衡取决于问题 stiffness。

⚠️ 具体性能数据需查 Diffrax 文档和最新 Neural ODE 论文。
</details>
