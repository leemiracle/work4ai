# 桥接注记：遗忘地板 e\*=f/(r+f) 在 TTT Fast Weights 上的形式

> 交叉创新探索 · 2026-08-26 | 连接：讲透Loop E5（循环经济学定律）× 2602.21204/2608.21308（TTT 架构前沿）
> 地位：**可检验预言**——给出 TTT fast weight 稳态的标度律，E4 实验直接验证

## 一、命题（循环定律的架构投影）

讲透Loop E5 证明：有遗忘的学习循环收敛到误差地板 $e^* = \frac{f}{r+f}$（$r$=学习率，$f$=遗忘率）——稳态由遗忘决定，与初始误差无关。

**投影到 TTT**：fast weight $W_t$ 的更新规则（LaCT/E2-TTT 通用形式）：

$$W_{t+1} = (1-\gamma)\,(W_t - \eta\, g_t)$$

其中 $\gamma$ 是 weight decay（遗忘），$\eta$ 是内环学习率，$g_t$ 是带噪梯度。设目标 $W^*$ 在局部近似固定、梯度噪声方差 $\sigma^2$（Hessian $A\succeq \lambda I$）。

**推论（稳态标度律）**：fast weight 偏差的稳态二阶矩满足

$$\lim_{t\to\infty}\mathbb{E}\|W_t - W^*\|^2 \;\approx\; \frac{\eta^2\sigma^2}{2\gamma} + O(\text{目标漂移}^2)$$

**证明骨架**（照搬 E5 的不动点论证）：每步噪声注入 $\eta^2\sigma^2$，衰减因子 $(1-\gamma)^2$，几何级数求和 $\Rightarrow \eta^2\sigma^2 \sum_k (1-\gamma)^{2k} = \frac{\eta^2\sigma^2}{1-(1-\gamma)^2} \approx \frac{\eta^2\sigma^2}{2\gamma}$。这正是 $e^*=\frac{f}{r+f}$ 的连续极限形态：**$f\leftrightarrow\gamma$，$r\leftrightarrow\eta$，分子是"注入"分母是"排出"**。

## 二、三个可检验预言

1. **范数标度**：固定 $\eta$，稳态 $\|W\|$ 或偏差 $\propto \gamma^{-1/2}$（二阶矩）——**09 章实验 E4 正是测这个**（γ 扫描 → 稳态范数）；
2. **学习率-衰减比不变量**：同样稳态可由 $(\eta, \gamma)$ 与 $(c\eta, c\gamma)$ 近似达到（分子 $\eta^2$ 分母 $\gamma$ 不变量是 $\eta^2/\gamma$）——解释了为什么 TTT 实践中 lr 和 decay 必须联合调；
3. **无衰减必爆**：$\gamma\to 0$ 时稳态发散（除非 $\sigma\to 0$）——**遗忘不是 bug 是有界性前提**。E2-TTT 的三因子核 $\mathcal{K}^W_t = \eta_t\,\tilde\beta_t\,R_t$ 里 $R_t$（decay 存活因子）被精确保留，恰是这个数学的工程化签名：**遗忘因子必须进闭式核，否则 chunk 化不收敛**。

## 三、双向价值（飞轮记账）

- **Loop→架构**：循环经济学的定律直接给出架构调参的标度律（本注记）；
- **架构→Loop**：TTT 是"遗忘地板"最好的架构实验台（$f$ 可直接扫描）——讲透Loop E5 的曲线可以在这里重跑一遍（γ 扫描 = f 扫描）；
- **S 级候选 C1 的对照**：C1（E≥n+λ₁−α）也是"压缩界的稳态"型不等式——TTT 稳态范数与能量界的类比（谱方法统一收口）值得记为 open 观察。

## 四、诚实边界

- 线性化+固定目标假设：真实序列非平稳（$W^*$ 漂移），漂移项进地板（E5 原式已含此项的定性版本）；
- 二阶近似只在 $\eta\lambda \ll 1$ 时成立（小步长）；
- E4 实验用固定随机 token 流（平稳），验证的是纯噪声地板项——漂移项的验证需要非平稳序列任务（后续实验）。
