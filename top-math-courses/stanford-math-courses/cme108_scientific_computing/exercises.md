# Stanford CME 108 · 习题集

### Q1（基础）
IEEE 754 双精度下，计算 $\epsilon_{\text{machine}}$ 并解释为何 $1 + \epsilon/2 = 1$。

<details><summary>解</summary>

52 位尾数 → $\epsilon = 2^{-52} \approx 2.22 \times 10^{-16}$。$1 + \epsilon/2$ 的舍入结果回到 1（被截断到 52 位尾数）。这是浮点"吸收"的根源。

**ML 关联**：fp16 下 $\epsilon \approx 10^{-3}$，大梯度 + 小更新可能被吸收 → 需 mixed precision。
</details>

### Q2（中等）
Runge 函数 $f(x) = 1/(1+25x^2)$ 在 $[-1,1]$ 上等距 $n$ 点插值，$n=5$ 和 $n=15$ 哪个误差更大？

<details><summary>解</summary>

$n=15$ 误差更大！Runge 现象：等距高次插值在边界处振荡加剧。

解决：用 Chebyshev 节点（$x_k = \cos((2k-1)\pi/(2n))$）或样条插值。
</details>

### Q3（中等）
证明隐式 Euler 法对 $\dot{y} = \lambda y$（$\text{Re}(\lambda) < 0$）无条件稳定。

<details><summary>解</summary>

$y_{n+1} = y_n + h\lambda y_{n+1}$ → $y_{n+1} = y_n / (1 - h\lambda)$。放大因子 $|1/(1-h\lambda)| < 1$ 当 $\text{Re}(\lambda) < 0$，对任意 $h > 0$。✓

**ML 关联**：Neural ODE 中 stiff 动力学需要隐式求解器。
</details>

### Q4（开放）
Neural ODE（Chen 2018）如何将数值 ODE 求解与深度学习结合？

<details><summary>提示</summary>

将 ResNet 的离散层 $\dot{h} = f(h,t)$ 连续化，用 ODE solver 做前向。反向传播用伴随法（adjoint method）避免存储中间状态，内存 $O(1)$。
</details>

### Q5（开放）
混合精度训练中，fp16 的 $\epsilon \approx 10^{-3}$ 对梯度更新的影响？

<details><summary>提示</summary>

fp16 范围 $[6 \times 10^{-8}, 65504]$。小梯度乘以学习率可能被下溢为 0 → 梯度缩放（loss scaling）：放大 loss，保持梯度在表示范围内，更新前再缩回。
</details>
