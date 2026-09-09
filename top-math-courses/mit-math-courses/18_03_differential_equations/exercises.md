# MIT 18.03 · 精选习题

> 2 道基础 + 3 道中等 + 2 道开放题（连接 ML）

---

## 基础题

### Q1（可分离变量 ODE）

求解 $\frac{dx}{dt} = -2x$，初始条件 $x(0) = 3$。

> **提示**：分离变量后积分。这是**指数衰减**的标准形式。
>
> **答案**：$x(t) = 3e^{-2t}$。

### Q2（二阶 ODE）

求解 $\ddot{x} + 4\dot{x} + 5x = 0$，$x(0) = 1$，$\dot{x}(0) = 0$。描述解的物理行为。

> **提示**：特征方程 $r^2 + 4r + 5 = 0$。
>
> **答案**：$r = -2 \pm i$，$x(t) = e^{-2t}(\cos t + 2\sin t)$。欠阻尼振荡，振幅以 $e^{-2t}$ 衰减。

---

## 中等题

### Q3（线性系统与特征值）

对 $\dot{\mathbf{x}} = A\mathbf{x}$，其中 $A = \begin{pmatrix}0 & 1\\-2 & -3\end{pmatrix}$：
(a) 求 $A$ 的特征值
(b) 判断原点的稳定性
(c) 画出大致相图

> **提示**：$\text{tr}(A) = -3$，$\det(A) = 2$。
>
> **答案**：(a) $\lambda = -1, -2$。(b) 两个负实特征值 → 稳定节点（吸引子）。(c) 轨迹沿特征向量方向趋近原点。

### Q4（Euler 法计算）

对 $\dot{x} = x - t$，$x(0) = 0$，用 Euler 法（步长 $h = 0.5$）计算 $x(1)$ 的近似值。与解析解 $x(t) = t + 1 - e^t$ 比较。

> **提示**：$x_{n+1} = x_n + h(x_n - t_n)$，$t_0=0, t_1=0.5, t_2=1.0$。
>
> **答案**：$x_1 = 0 + 0.5(0 - 0) = 0$；$x_2 = 0 + 0.5(0 - 0.5) = -0.25$。解析值 $x(1) = 1 + 1 - e \approx -0.718$。Euler 误差较大（$h$ 太大）。

### Q5（Laplace 变换解 ODE）

用 Laplace 变换求解 $\ddot{x} + x = \delta(t)$（$x(0) = \dot{x}(0) = 0$），即冲激响应。

> **提示**：$\mathcal{L}\{\ddot{x}\} = s^2 X(s)$，$\mathcal{L}\{\delta(t)\} = 1$。
>
> **答案**：$s^2 X + X = 1$ → $X = 1/(s^2+1)$ → $x(t) = \sin t$（单位脉冲激励下的振荡响应）。

---

## 开放题（连接 ML）

### Q6（ResNet = Euler 离散化的 Neural ODE）

ResNet 的残差块定义为 $\mathbf{h}_{l+1} = \mathbf{h}_l + f_\theta(\mathbf{h}_l)$。
(a) 说明这是哪个 ODE 的 Euler 离散化（步长 $h=1$）？
(b) 如果用 RK4 代替 Euler，"网络结构"会怎样变化？
(c) 连续化（Neural ODE）相比离散 ResNet 有什么优势和劣势？

> **提示**：(a) $\dot{\mathbf{h}} = f_\theta(\mathbf{h})$。(b) RK4 每步需要 4 次评估 $f$（类似 4 个子层）。(c) 优势：内存 $O(1)$（adjoint），可变深度；劣势：训练慢（需 ODE solver 反复求值）。
>
> **答案要点**：(a) $\frac{d\mathbf{h}}{dt} = f_\theta(\mathbf{h}(t))$，$\Delta t = 1$。 (b) 一个"RK4 层"= 4 次 $f$ 评估 + 加权组合。 (c) Neural ODE 内存恒定但 wall-clock 更慢，精度 vs 速度可调。

### Q7（Mamba SSM 的离散化）

Mamba 的连续状态空间模型 $\dot{\mathbf{h}}(t) = A\mathbf{h}(t) + B\mathbf{x}(t)$。
(a) 用前向 Euler 离散化（步长 $\Delta$），写出离散递推式
(b) 特征值条件：$A$ 的特征值满足什么条件时，离散系统 $\mathbf{h}_k$ 稳定？
(c) 解释为什么 Mamba 在初始化时要把 $A$ 设为对角矩阵且特征值为负（HiPPO 初始化）

> **提示**：(a) $\mathbf{h}_{k+1} = (I + \Delta A)\mathbf{h}_k + \Delta B\mathbf{x}_k$。(b) $(I+\Delta A)$ 的特征值模 $<1$。(c) 负特征值 → 连续系统稳定 → 离散后仍稳定（长程记忆）。
>
> **答案要点**：(a) Euler：$\mathbf{h}_{k} \approx (I+\Delta A)\mathbf{h}_{k-1} + \Delta B\mathbf{x}_k$。（Mamba 实际用 ZOH：$\bar{A} = e^{\Delta A}$。） (b) $|1 + \Delta\lambda_i| < 1$，即 $-2/\Delta < \lambda_i < 0$。 (c) 对角 $A$ 简化 $e^{\Delta A}$ 计算；负特征值保证衰减记忆，利于建模长序列。
