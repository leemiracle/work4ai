# MIT 18.01 · 精选习题

> 2 道基础 + 3 道中等 + 2 道开放题（连接 ML）

---

## 基础题

### Q1（极限计算）

用极限定义或等价变形求：

$$\lim_{x \to 0} \frac{e^x - 1 - x}{x^2}$$

> **提示**：这是 0/0 型，可用 Taylor 展开或 L'Hôpital。
>
> **答案**：$\frac{1}{2}$

### Q2（链式法则）

设 $y = \sigma(3w^2 + 2w + 1)$，其中 $\sigma(z) = \frac{1}{1+e^{-z}}$。求 $\frac{dy}{dw}$ 在 $w = 1$ 处的值。

> **提示**：$\frac{dy}{dw} = \sigma'(z)\cdot z'(w)$，其中 $\sigma'(z) = \sigma(z)(1-\sigma(z))$。
>
> **答案**：$z(1) = 6$，$\sigma(6) \approx 0.9975$，$z'(1) = 8$，所以 $\frac{dy}{dw} \approx 0.9975 \times 0.0025 \times 8 \approx 0.01995$

---

## 中等题

### Q3（最优化与梯度下降）

对 $f(x) = x^4 - 4x^2 + 1$：
(a) 求所有临界点并分类（极大/极小）
(b) 从 $x_0 = 1$ 出发，学习率 $\eta = 0.1$，写出梯度下降前 3 步的值

> **提示**：(a) $f'(x) = 4x^3 - 8x = 4x(x^2 - 2)$；用二阶导判别。
> (b) $x_{t+1} = x_t - 0.1 \cdot f'(x_t)$。
>
> **答案**：(a) $x = 0$（极大，$f''(0)=-8<0$），$x = \pm\sqrt{2}$（极小，$f''=\frac{16}{}\sqrt{2}>0$）。 (b) $f'(1) = 4-8 = -4$，$x_1 = 1-0.1(-4) = 1.4$；$f'(1.4) \approx 4(2.744)-11.2 \approx -0.224$，$x_2 \approx 1.422$；$x_3 \approx 1.413$（趋向 $\sqrt{2}\approx 1.414$）。

### Q4（Taylor 展开应用）

用 $e^x$ 的 3 阶 Taylor 多项式（在 $a=0$ 处）近似计算 $e^{0.1}$，并给出误差的上界估计。

> **提示**：$e^x \approx 1 + x + x^2/2 + x^3/6$；余项 $R_3 = \frac{e^c}{24}x^4$，$0 < c < x$。
>
> **答案**：$e^{0.1} \approx 1 + 0.1 + 0.005 + 0.0001\overline{6} \approx 1.1051\overline{6}$；真值 $e^{0.1}\approx 1.10517$；误差 $< \frac{e^{0.1}}{24}(0.1)^4 \approx 4.6 \times 10^{-6}$。

### Q5（积分与概率）

概率密度 $p(x) = c \cdot e^{-x}$（$x \geq 0$）：
(a) 求 $c$ 使其归一化
(b) 计算期望 $E[X] = \int_0^\infty x\,p(x)\,dx$

> **提示**：(a) $\int_0^\infty c e^{-x}\,dx = c$；(b) 分部积分。
>
> **答案**：(a) $c = 1$（标准指数分布）。 (b) $E[X] = 1$。

---

## 开放题（连接 ML）

### Q6（链式法则 → 反向传播推导）

一个两层网络：$z = w_2 \cdot \text{ReLU}(w_1 \cdot x + b_1) + b_2$，损失 $L = (z - y)^2$。给定 $x, y, w_1, b_1, w_2, b_2$ 的具体值，用链式法则推导 $\frac{\partial L}{\partial w_1}$ 的完整表达式，并解释为什么这叫"反向"传播。

> **提示**：$\frac{\partial L}{\partial w_1} = \frac{\partial L}{\partial z}\cdot\frac{\partial z}{\partial h}\cdot\frac{\partial h}{\partial a}\cdot\frac{\partial a}{\partial w_1}$，其中 $h=\text{ReLU}(a)$，$a = w_1 x + b_1$。"反向"指的是从损失 $L$（输出端）逐层向 $w_1$（输入端）回溯局部导数。
>
> **答案要点**：$\frac{\partial L}{\partial w_1} = 2(z-y)\cdot w_2 \cdot \mathbb{1}[w_1 x + b_1 > 0]\cdot x$。

### Q7（Newton 法 vs 梯度下降）

对 $f(x) = x^2$（最简单凸函数），从 $x_0 = 10$ 出发：
(a) 梯度下降（$\eta = 0.1$）需要多少步使 $|x| < 0.01$？
(b) Newton 法（$x_{n+1} = x_n - f'(x_n)/f''(x_n)$）需要多少步？
(c) 解释为什么 Newton 法"一步到最小值"——这对深度学习意味着什么？

> **提示**：(a) $x_{n} = 0.8\,x_{n-1}$，几何衰减；(b) $f''(x) = 2$，$x_1 = x_0 - 2x_0/2 = 0$。
>
> **答案要点**：(a) $\lceil\log(0.01/10)/\log(0.8)\rceil \approx 38$ 步。 (b) **1 步**。 (c) Newton 法利用二阶信息（$f''$）直接跳到极值点；但深度学习损失函数维数极高（数亿参数），计算/存储 Hessian $f''$ 不可行，所以实际用一阶方法（SGD/Adam）。
