# Nocedal-Wright《数值优化》(2nd Ed) · 快速逐章精读

> 基于原书：*Numerical Optimization*（Jorge Nocedal & Stephen J. Wright, Springer, 2nd Ed, 2006）/ 读于：2026-07-02
> 定位：**数值优化最权威现代教材**（NW，CMU/Argonne），从无约束到约束到全局/网络优化全谱系，ML 训练（梯度下降/Adam/L-BFGS）与运筹的核心算法圣经。
> 三源 = 原书理论 × 已读 D-凸优化(Boyd 理论) × 飞腾 D3000M（实践锚点）
> 关联：[D-凸优化 Boyd](D-凸优化_快速逐章.md) · [线性规划](线性规划_快速逐章.md) · [Kress 数值分析](kress_数值分析_GTM181_快速逐章.md) · [研究入门](D-优化理论_研究入门.md)

---

## §0 引言：Nocedal-Wright 是「Boyd 的算法实现版」

Jorge Nocedal（CMU/西北大学，L-BFGS 发明者）与 Stephen J. Wright（Argonne/Wisconsin，内点法权威）合著的《Numerical Optimization》是**数值优化领域的标准研究生教材**——与 Boyd《凸优化》正交互补：**Boyd 讲「优化问题长什么样」**（凸性识别、对偶、建模），**Nocedal 讲「算法怎么真正算出来」**（线搜索、信赖域、拟牛顿、SQP 的迭代细节与收敛性证明）。

一句话定位：本书是 stage-3 方向 D（优化理论）的**算法实现核心教材**。
已读本仓库 [D-凸优化](D-凸优化_快速逐章.md)(Boyd)，本书从「凸的理论保证」推进到「任意可微优化的算法工程」——**不再假设凸性**，必须直面「牛顿方向可能非下降」「信赖域半径需动态调整」「全局最优不可保证」等 Boyd 避而不谈的算法工程现实。

全书的灵魂贯穿三个层次，构成一条从「无约束」到「约束」到「全局」的递进主线：
① **无约束**（第 3-9 章）：线搜索 vs 信赖域两大框架，CG/拟牛顿两大加速器，
这是 **ML 训练（Adam/L-BFGS）的直接源头**；
② **约束**（第 12-18 章）：KKT 条件 + 罚函数/SQP/内点法，这是**机器人控制、约束训练的算法根基**；
③ **全局/组合**（第 13-14、19 章）：单纯形/分支定界/元启发式，这是**运筹与混合整数的世界**。

飞腾锚点把抽象收敛率钉到工程肉身：**Iron Law <2%** [Lab00]（浮点收敛误差的「铁律」）直接对应第 3/4 章收敛性判据；**matmul 15×** [V03]（Hessian 阵运算）对应牛顿/BFGS 的矩阵开销；**分支预测** [Lab02] 对应线搜索的分支跳转。优化算法多为 🟢（事实锚点），因为收敛性定理可严格验证。

### 四本优化教材对比

| 维度 | **Nocedal-Wright** | Boyd 凸优化 | Bertsekas 凸优化 | Sundaram 最优理论 |
|------|-------------------|-------------|-----------------|-------------------|
| 定位 | **算法实现**（全谱系） | 凸建模与理论 | 凸分析纵深 | 最优性理论 |
| 篇幅·层级 | ~650 页·研究生算法级 | ~700 页·研究生建模级 | ~500 页·研究纵深 | ~350 页·理论导论 |
| 招牌特色 | **L-BFGS + 信赖域 + SQP** | 建模识别 + 内点 | 对偶 + 算法证明 | KKT 理论框架 |
| 约束处理 | **罚函数/SQP/内点全谱系** | 仅凸内点 | 凸 + 对偶 | 仅理论 |
| 凸性假设 | **不假设凸**（核心区别） | 全程凸 | 全程凸 | 凸 + 非凸理论 |
| 飞腾匹配 | 收敛率 × Hessian × 分支 | 建模（Roofline） | 对偶证明 | 理论（无实现） |

> **阅读策略**：Boyd 建模（凸世界） → **Nocedal 算法（打破凸假设的工程现实）** → Bertsekas/Sundaram 理论锐化。

---

## §1 全书骨架（19 章 · 飞腾锚点分布）

| 部分 | 章节 | 主题 | 飞腾锚点 |
|------|------|------|----------|
| **I 地基** | 第 1 章 | 引言·问题分类 | Iron Law ⭐ |
| | 第 2 章 | 优化基础·最优性条件 | matmul ⭐ |
| **II 无约束** | 第 3 章 | 线搜索·Wolfe 条件 | 分支预测 |
| | 第 4 章 | 信赖域·子问题 | Iron Law ⭐ |
| | 第 5 章 | 共轭梯度 CG | Schmidt 正交化 |
| | 第 6 章 | 拟 Newton·BFGS/DFP/SR1 | matmul ⭐ |
| | 第 7 章 | 大规模无约束·L-BFGS | TLB |
| | 第 8 章 | 计算导数·AD/有限差分 | FP16 |
| | 第 9 章 | 无导数方法·坐标下降 | 分支预测 |
| **III 最小二乘** | 第 10 章 | 最小二乘·Gauss-Newton | UDOT ⭐ |
| | 第 11 章 | 非线性方程组 | Iron Law ⭐ |
| **IV 约束理论+LP** | 第 12 章 | 约束理论·KKT/二阶充分 | matmul ⭐ |
| | 第 13 章 | 线性规划·单纯形/内点 | GEMM |
| | 第 14 章 | 网络组合·最短路/最大流 | 分支预测 |
| **V 约束算法** | 第 15 章 | 二次规划·活动集/内点 | GEMM |
| | 第 16 章 | 罚函数·增广 Lagrangian | Iron Law ⭐ |
| | 第 17 章 | SQP·序列二次规划 | UDOT ⭐ |
| | 第 18 章 | 内点法·原始对偶 | TLB |
| **VI 全局** | 第 19 章 | 全局优化·分支定界/元启发式 | 分支预测 |

---

# Part I · 地基（第 1-2 章）

---

## 第 1 章 · Introduction 引言（PP.1-18）

- **核心**：定义**优化问题**标准形 $\min f(x)$ s.t. 约束，
  按约束分**无约束 / 等式约束 / 不等式约束**，按函数分**线性 / 非线性 / 凸 / 非凸**。
  给出全书分类法与算法选择树。强调「优化 = 连续空间搜索」vs「组合优化 = 离散搜索」的根本区别。
  非线性优化的残酷现实：**没有全局保证**（非凸时），算法只能保证收敛到「稳定点」$\nabla f=0$。
  全书围绕「如何高效找稳定点」「如何把约束化为无约束」「如何逼近全局」三大问题展开。
- **飞腾锚点**：**Iron Law <2% [Lab00]**（收敛误差铁律）🟢。
  所有收敛性证明都假设「浮点精确」，但 Iron Law 说累积误差 >2% 就破坏收敛判据。
  停止判据 $\|\nabla f\|<\epsilon$ 中，$\epsilon$ 不能小于机器精度 $\epsilon_{\text{mach}}$，
  否则 Iron Law 违约——停止判据是「数值精度」与「算法理论」的握手处。
- **关键概念**：**全局最优 vs 局部最优**（非凸不等）；
  **凸性**保证局部即全局（[D-凸优化] 的核心承诺）；**平滑性**（$C^2$）保证牛顿法可用。
- **自测**：非凸优化的「全局最优」为何不可保证？给一个多局部极小的例子。
  （提示：$f(x)=x^4-4x^2$，$x=\pm\sqrt{2}$ 都是局部极小，$x=0$ 是局部极大。）

---

## 第 2 章 · Fundamentals of Unconstrained Optimization 优化基础（PP.19-46）

- **核心**：建立**最优性条件**——一阶 $\nabla f(x^\ast)=0$（稳定点）；
  二阶 $\nabla^2 f(x^\ast)\succeq 0$（局部极小必要），正定 $\nabla^2 f(x^\ast)\succ0$（充分）。
  定义**方向导数** $D_p f=\nabla f^\top p$ 与**下降方向**（$D_p f<0$）。
  引入**算法框架**：选方向 $p_k$ + 选步长 $\alpha_k$，$x_{k+1}=x_k+\alpha_k p_k$。
  收敛率：**线性**（$r<1$）/ **超线性**（比 $\to0$）/ **二次**（每步位数翻倍）。
- **飞腾锚点**：**matmul 15× [V03]**（Hessian 矩阵）🟢。
  二阶条件需 Hessian $\nabla^2 f\in\mathbb{R}^{n\times n}$，$n=10^4$ 时占 400GB 不可行
  ——这是牛顿法大规模下「算不动」的根源，催生第 6-7 章拟牛顿/L-BFGS。
  matmul 15× 让中等规模（$n\sim10^3$）Hessian 运算可向量化加速。
- **关键定理**：**Taylor 展开** $f(x+p)=f(x)+\nabla f^\top p+\frac12 p^\top\nabla^2 f\,p+O(\|p\|^3)$
  ——牛顿法 $p=-[\nabla^2 f]^{-1}\nabla f$ 就是对二阶 Taylor 取最优。
  收敛率层级：二次（牛顿）> 超线性（BFGS）> 线性（最速下降/CG）。
- **自测**：稳定点 $\nabla f=0$ 一定是极小值吗？
  （否：$f(x)=x^3$，$x=0$ 稳定但非极值（拐点）；$f(x)=-x^2$，$x=0$ 稳定但是极大。）

---

# Part II · 无约束优化方法（第 3-9 章）⭐⭐⭐ ML 训练核心

---

## 第 3 章 · Line Search Methods 线搜索法（PP.30-65）⭐⭐⭐

- **核心**：**两大框架之一**。给定下降方向 $p_k$（最速下降 $-\nabla f$ 或牛顿 $-[\nabla^2f]^{-1}\nabla f$），
  沿该方向搜步长 $\alpha_k$ 使 $f(x_k+\alpha p_k)$ 充分下降。
  **Armijo/回溯条件**：$f(x_k+\alpha p_k)\le f(x_k)+c_1\alpha\nabla f_k^\top p_k$（保证下降）；
  **Wolfe 条件**：加曲率条件 $\nabla f(x_k+\alpha p_k)^\top p_k\ge c_2\nabla f_k^\top p_k$（步长不太小）。
  最速下降对强凸二次 Z 字形收敛（线性率，与条件数 $\kappa$ 相关）。
- **飞腾锚点**：**分支预测 [Lab02]**（线搜索分支）🟢。
  回溯线搜索是典型的**条件分支循环**：试 $\alpha=1$，不满足 Armijo 则 $\alpha\leftarrow\rho\alpha$ 重试，
  循环次数数据依赖——分支预测器命中率低，线搜索有不可预测延迟。
  AI 锚点：**Adam 优化器**的步长自适应是「数据驱动的线搜索」。
- **关键定理**：**Zoutendijk 定理**——若 $\cos\theta_k$ 有下界 + Wolfe 条件，
  则 $\sum_k\cos^2\theta_k\|\nabla f_k\|^2<\infty$，即 $\|\nabla f_k\|\to0$（收敛基石）。
- **自测**：为什么「精确线搜索」（每步最优 $\alpha$）很少用？
  （提示：精确需解一维 $\min_\alpha$，本身就是优化问题；回溯只需 2-3 次求值，性价比远优。）

---

## 第 4 章 · Trust-Region Methods 信赖域法（PP.66-100）⭐⭐⭐

- **核心**：**两大框架之二**。在信赖域 $\|p\|\le\Delta$ 内**整体近似**：
  $\min_p\ m_k(p)=f_k+\nabla f_k^\top p+\frac12p^\top B_kp$ s.t. $\|p\|\le\Delta$（$B_k\approx\nabla^2 f_k$）。
  根据**实际/预测下降比** $\rho_k=\frac{f(x_k)-f(x_k+p_k)}{m_k(0)-m_k(p_k)}$ 动态调半径：
  $\rho$ 接近 1 则扩大 $\Delta$，$\rho$ 小则缩小。
  **Cauchy 点**（沿最速下降到边界）保证全局收敛，无需精确解子问题。
- **飞腾锚点**：**Iron Law <2% [Lab00]**（收敛误差）🟢。
  核心判据 $\rho_k=\frac{\text{实际下降}}{\text{预测下降}}$ 是两浮点数之比，
  下降量小时 $\rho_k$ 被**浮点噪声**支配——Iron Law 的 <2% 会污染 $\rho_k$ 符号判断，
  导致错误扩大/缩小信赖域。接近最优时 $\rho_k$ 振荡而非稳定趋于 1。
- **关键定理**：**信赖域全局收敛定理**——每步取 Cauchy 点（或更优）$\Rightarrow\liminf\|\nabla f_k\|=0$。
  信赖域**不需线搜索就保证收敛**，且 $B$ 不正定时自动限步长——**对非凸更鲁棒**。
- **自测**：信赖域比线搜索「鲁棒」在哪？
  （提示：线搜索在 $p$ 非下降方向时失败（Hessian 不正定）；信赖域限步长 $\|p\|\le\Delta$ 自动处理不正定 $B$。）

---

## 第 5 章 · Conjugate Gradient Methods 共轭梯度法（PP.101-128）⭐⭐

- **核心**：求解 $Ap=b$（$A$ 大型稀疏正定）的 **Krylov 子空间迭代法**，不需存 $A^{-1}$。
  **共轭方向**：$p_i^\top Ap_j=0$（$i\ne j$，$A$-正交）。对二次 $f=\frac12x^\top Ax-b^\top x$，
  CG 最多 $n$ 步精确收敛（精确算术）；有限精度下 ~$O(\sqrt\kappa)$ 步。
  **Fletcher-Reeves / Polak-Ribière** 推广到非二次。优势：**每步只需 $Ap_k$**，内存 $O(n)$。
- **飞腾锚点**：**Schmidt 正交化(QR 分解)** 🟢。
  CG 的共轭性 $p_i^\top Ap_j=0$ 是「$A$-内积下的正交化」——
  本质是对 Krylov 子空间 $\{b,Ab,A^2b,\ldots\}$ 做 **Gram-Schmidt 正交化**
  （以 $A$-内积 $\langle u,v\rangle_A=u^\top Av$）。
  三条递推公式是对 Schmidt 正交化的精巧递归，避免存储历史方向——这是 CG 省内存的精髓。
- **关键算法**：**CG 迭代**——$\alpha_k=\frac{r_k^\top r_k}{p_k^\top Ap_k}$，$x_{k+1}=x_k+\alpha_kp_k$，
  $r_{k+1}=r_k-\alpha_k Ap_k$，$\beta_k=\frac{r_{k+1}^\top r_{k+1}}{r_k^\top r_k}$，$p_{k+1}=r_{k+1}+\beta_kp_k$。
  误差界：$\|x_k-x^\ast\|_A\le2\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^k\|x_0-x^\ast\|_A$。
- **自测**：CG 为什么对条件数 $\kappa$ 敏感？预条件子作用？
  （提示：$\kappa$ 大则因子接近 1、收敛慢。预条件 $M^{-1}A$ 降等效 $\kappa$——选 $M\approx A$ 但易分解。）

---

## 第 6 章 · Quasi-Newton Methods 拟牛顿法（PP.129-164）⭐⭐⭐

- **核心**：牛顿法需 $\nabla^2 f$（$O(n^2)$ 存储 + $O(n^3)$ 分解），最速下降只用一阶（线性收敛）。
  **拟牛顿法**用**割线方程** $B_{k+1}s_k=y_k$（$s=x_{k+1}-x_k$，$y=\nabla f_{k+1}-\nabla f_k$）
  递推近似 Hessian 逆 $H_k\approx[\nabla^2 f_k]^{-1}$，**不需二阶导**却达**超线性收敛**。
  三大变体：**BFGS**（$H$ 更新，最鲁棒，默认）、**DFP**（$B$ 更新，常逊于 BFGS）、
  **SR1**（对称秩一，不保正定，适用信赖域/非凸）。
- **飞腾锚点**：**matmul 15× [V03]**（Hessian 矩阵）🟢。
  BFGS 更新 $H_{k+1}=(I-\rho sy^\top)H_k(I-\rho ys^\top)+\rho ss^\top$ 涉及矩阵-矩阵乘（matmul）。
  $n=10^3$ 时每步 ~$10^9$ FLOP——matmul 15× 向量化把每步成本压到可接受范围。
  AI 锚点：**BFGS 是中等规模（$n<10^4$）无约束优化的黄金标准**（SciPy `minimize(BFGS)`）。
- **关键定理**：**BFGS 超线性收敛定理**——$f$ 二阶连续可微、Hessian 正定 Lipschitz、
  Wolfe 线搜索 $\Rightarrow$ 超线性收敛 $\lim\frac{\|x_{k+1}-x^\ast\|}{\|x_k-x^\ast\|}=0$。
- **自测**：BFGS 比牛顿法好在哪、差在哪？
  （好：不需 $\nabla^2f$、$H$ 恒正定保下降；差：仅超线性非二次、$O(n^2)$ 存储大规模不可行→第 7 章。）

---

## 第 7 章 · Large-Scale Unconstrained Optimization 大规模无约束（PP.165-194）⭐⭐⭐

- **核心**：当 $n>10^4$（深度学习/科学计算），BFGS 的 $O(n^2)$ 存储不可行。
  **L-BFGS**（Limited-memory BFGS）：只存最近 $m$ 组 $(s_i,y_i)$（$m=5\sim20$），
  通过**双循环递推**隐式计算 $H_k\nabla f_k$（不显式存 $H_k$），存储 $O(mn)$ 而非 $O(n^2)$。
  这是**大模型全批量训练/科学计算大规模优化的主力算法**。
  **信赖域 L-BFGS**：L-BFGS 近似嵌入信赖域（信赖域牛顿-CG），适合稀疏/非凸。
- **飞腾锚点**：**TLB 4.81× [E04]**（稀疏 Hessian）🟢。
  $(s_i,y_i)$ 向量序列顺序访问，TLB 缺失惩罚大 $m$——4.81× 提升来自对齐缓存行/页。
  科学计算 Hessian 常稀疏（PDE 离散化），稀疏存储 + L-BFGS 是「内存墙」下唯一方案。
  AI 锚点：**L-BFGS 是大模型全批量微调标准优化器**（比 Adam 内存友好）。
- **关键算法**：**L-BFGS 双循环递推**——从 $H_0^{(k)}=\gamma_k I$ 出发
  （$\gamma_k=\frac{s_{k-1}^\top y_{k-1}}{y_{k-1}^\top y_{k-1}}$ 自适应缩放），
  向前/向后各乘 $m$ 次 $(I-\rho_i y_i s_i^\top)$，实现 $H_k\nabla f_k$ 而不存 $H_k$。收敛率：线性。
- **自测**：L-BFGS 的 $m$ 太小/太大各有什么后果？
  （太小：近似差收敛慢；太大：内存/成本增加收益递减。经验 $m=5\sim20$，多数 $m=10$ 足够。）

---

## 第 8 章 · Calculating Derivatives 计算导数（PP.195-220）

- **核心**：优化算法需 $\nabla f$ 和 $\nabla^2 f$，但手算易错、黑箱无解析导数。
  ① **有限差分**：$\frac{\partial f}{\partial x_i}\approx\frac{f(x+he_i)-f(x)}{h}$，
  截断 $O(h)$ vs 舍入 $O(\epsilon/h)$，最优 $h\sim\sqrt\epsilon$。
  ② **自动微分（AD）**：对计算图精确传播链式法则，**零截断误差**，
  前向模式（$n$ 次得 Jacobian）/反向模式（1 次得梯度）。
  ③ **复步法**：$f'(x)\approx\text{Im}[f(x+ih)]/h$，避免减法相消，精度近机器精度。
- **飞腾锚点**：**FP16 3.81× [L01]**（数值精度）🟢。
  有限差分致命弱点是「截断 vs 舍入」权衡——FP16 精度 $\epsilon\sim10^{-3}$，
  最优 $h\sim0.03$ 太大，梯度误差 ~3% 直接违反 Iron Law <2%。
  **低精度训练不能用有限差分**，必须用 AD（精确，不受精度限制）。
  AI 锚点：**PyTorch autograd = AD 反向模式** = backprop 的工业实现。
- **关键概念**：**前向 AD**（正向传播切线，$n$ 次得 Jacobian）
  vs **反向 AD / backprop**（逆向传播伴随，1 次得梯度，需 $O(\text{深度})$ 存储）。
  深度学习选反向因 $f:\mathbb{R}^n\to\mathbb{R}$（$n$ 大输出少），反向只需 1 次遍历。
- **自测**：为什么反向 AD 比 forward AD 适合神经网络？
  （提示：NN 是 $f:\mathbb{R}^n\to\mathbb{R}$（$n$ 亿参数），前向需 $n$ 次，反向只需 1 次——差 $n$ 倍。）

---

## 第 9 章 · Derivative-Free Optimization 无导数方法（PP.221-248）

- **核心**：当 $\nabla f$ 不可得（黑箱/实验/昂贵仿真），用**函数值**直接搜索。
  ① **坐标下降**：轮流沿各轴一维搜索（简单但非轴对齐问题极慢）。
  ② **模式搜索**（Hooke-Jeeves）：固定模式试探邻域，接受改进方向。
  ③ **Nelder-Mead 单纯形法**：$n+1$ 顶点，反射/扩展/外收缩/内收缩操作演化。
  无导数法**收敛慢、无强理论保证**，但黑箱场景无可替代。
- **飞腾锚点**：**分支预测 [Lab02]** 🟢。
  坐标下降/模式搜索核心是「试探 $2n$ 方向，接受最优」——**数据依赖分支**：
  哪个方向改进就跳哪，预测器无法预测。Nelder-Mead 反射/收缩决策同理（4 种操作选择）。
  AI 锚点：**贝叶斯优化（BO）**是无导数优化现代版，用高斯过程代理 + 采集函数（EI/UCB）。
- **关键概念**：无导数法**收敛率远逊于梯度法**——
  $n$ 维需 $O(n)$ 次求值才估计一个梯度方向。函数求值昂贵时应改用代理模型（BO/Kriging）。
- **自测**：Nelder-Mead 为什么在高维（$n>10$）失效？
  （提示：$n+1$ 顶点覆盖 $\mathbb{R}^n$ 信息太少，退化严重；反射/收缩启发式高维下近随机游走。$n\le5$ 可靠。）

---

# Part III · 非线性最小二乘与方程组（第 10-11 章）

---

## 第 10 章 · Least-Squares Problems 最小二乘问题（PP.249-280）⭐⭐

- **核心**：$\min\frac12\|r(x)\|^2=\frac12\sum r_i(x)^2$（$r$ 残差）。
  梯度 $\nabla f=J^\top r$（$J$ Jacobian），Hessian $\nabla^2 f=J^\top J+\sum r_i\nabla^2 r_i$。
  **Gauss-Newton（GN）**：丢弃二阶项，用 $J^\top J\approx\nabla^2f$——残差小（好拟合）时精确，
  **不需二阶导**且 $J^\top J$ 恒半正定。
  **Levenberg-Marquardt（LM）**：GN + 阻尼 $(J^\top J+\lambda I)p=-J^\top r$，
  $\lambda$ 大趋最速下降，$\lambda$ 小趋 GN——**曲线拟合/相机标定的工业标准**。
- **飞腾锚点**：**UDOT 16.9× [E05]**（梯度点积）🟢。
  GN 核心运算 $J^\top r$（Jacobian 转置乘残差）是一连串**点积** $\sum_j J_{ji}r_j$——
  UDOT 向量化直接加速每步。残差范数 $\|r\|^2=r^\top r$ 也是点积。
  AI 锚点：**LM 是 SLAM、Bundle Adjustment、相机标定（OpenCV `calibrateCamera`）的核心**。
- **关键算法**：**Levenberg-Marquardt**——解 $(J^\top J+\lambda I)p=-J^\top r$ 求方向，
  根据实际/预测下降比调 $\lambda$。残差大时 $\sum r_i\nabla^2r_i$ 主导，GN 失效，需通用牛顿。
- **自测**：Gauss-Newton 何时等价牛顿法？何时失效？
  （提示：残差 $r_i(x^\ast)\approx0$ 时 $\sum r_i\nabla^2r_i\approx0$，GN=牛顿二次收敛；残差大时二阶项主导，LM 阻尼修复。）

---

## 第 11 章 · Nonlinear Equations 非线性方程组（PP.281-302）

- **核心**：求 $F(x)=0$（$F:\mathbb{R}^n\to\mathbb{R}^n$）。
  ① **牛顿法** $x_{k+1}=x_k-J_k^{-1}F_k$（局部二次收敛，需 Jacobi 逆）。
  ② **不精确牛顿（Newton-Krylov）**：CG/GMRES 近似解 $J_kp=-F_k$，适合大型稀疏。
  ③ **Broyden 方法**：拟牛顿版，割线近似 Jacobi，不需算 $J$。
  ④ **连续法/同伦法**：从易解 $F_0$ 连续变形到 $F$，**扩大收敛域**。
  桥梁：$F(x)=0\iff\min\|F(x)\|^2$（化为第 10 章最小二乘）。
- **飞腾锚点**：**Iron Law <2% [Lab00]**（收敛误差）🟢。
  牛顿法停止判据 $\|F_k\|<\epsilon$——Jacobi 近奇异时，浮点误差使 $\|F_k\|$ 在 $\epsilon_{\text{mach}}^{1/2}$
  附近**振荡**而非单调下降，造成「假收敛」。连续法对病态问题更鲁棒，但路径追踪仍受精度限制。
- **关键定理**：**牛顿法局部收敛定理**——$J(x^\ast)$ 非奇异，初值足够近 $\Rightarrow$ 二次收敛。
  收敛域有限是核心缺陷（初值不好可能发散/收敛到错误根）——全局策略见第 3-4 章和连续法。
- **自测**：非线性方程组的牛顿法与第 2 章优化的牛顿法有何异同？
  （提示：优化求 $\nabla f=0$ 即 $F=\nabla f$，$J=\nabla^2f$（Hessian 对称半正定保下降）；纯方程组 $J$ 无此结构。）

---

# Part IV · 约束优化理论与线性规划（第 12-14 章）

---

## 第 12 章 · Theory of Constrained Optimization 约束优化理论（PP.315-348）⭐⭐⭐

- **核心**：$\min f(x)$ s.t. $c_i(x)\le0$,$h_i(x)=0$ 的最优性理论。
  **一阶必要（KKT）**：$\nabla f+\sum\lambda_i\nabla c_i+\sum\nu_i\nabla h_i=0$，$c_i\le0$，$\lambda_i\ge0$，
  $\lambda_ic_i=0$（互补松弛）。**LICQ**（活跃约束 Jacobi 行满秩）保证乘子唯一。
  **二阶充分**：切空间投影 Hessian $Z^\top\nabla^2_{xx}\mathcal{L}Z\succ0$ $\Rightarrow$ 严格局部最优。
- **飞腾锚点**：**matmul 15× [V03]**（Hessian 矩阵）🟢。
  二阶充分条件需检查**投影 Hessian** $Z^\top\nabla^2_{xx}\mathcal{L}Z$ 正定性——
  $Z$ 构造（约束 Jacobi 零空间 QR/SVD）和投影 $Z^\top(\cdot)Z$ 涉及 matmul。
  LICQ 检验 = 约束 Jacobi 行满秩 = 秩判定。AI 锚点：**KKT 是所有约束算法（第 15-18 章）的停止判据**。
- **关键定理**：**KKT 一阶必要**——LICQ 下 $x^\ast$ 局部最优 $\Rightarrow$ 存在唯一 $(\lambda^\ast,\nu^\ast)$ 满足 KKT 四条。
  **二阶充分**：KKT + 投影 Hessian 正定 $\Rightarrow$ 严格局部最优。
  与 [D-凸优化第 5 章] 区别：Boyd 凸下 KKT **充要**，NW 非凸下仅**必要**。
- **自测**：互补松弛 $\lambda_ic_i=0$ 的经济直觉？
  （提示：$\lambda_i$=影子价格——约束不活跃（$c_i<0$）资源不稀缺、$\lambda_i=0$；活跃（$c_i=0$）才有正价格。）

---

## 第 13 章 · Linear Programming 线性规划（PP.349-384）⭐⭐

- **核心**：$\min c^\top x$ s.t. $Ax\le b, x\ge0$。
  ① **单纯形法**（Dantzig 1947）沿多面体顶点迭代（选进基/出基=沿边走），实践极快但最坏指数。
  ② **内点法**（Karmarkar 1984）多项式复杂度，沿中心路径逼近。
  **对偶理论**：对偶 $\max b^\top y$ s.t. $A^\top y\le c$，**强对偶恒成立**（LP 特有）。
  LP 是凸优化最简特例（与 [线性规划]、[D-凸优化第 4-5 章] 衔接）。
- **飞腾锚点**：**GEMM 9.45G [Lab05]**（大规模 LP）🟢。
  工业 LP（供应链/调度）约束矩阵 $A$ 可达 $10^6\times10^6$（稀疏），
  单纯形/内点法核心都是**稀疏矩阵运算**——GEMM 内核吞吐决定 CPLEX/Gurobi 速度。
  AI 锚点：**OR-Tools / Gurobi / COPT 的 LP 引擎**底层是优化后的稀疏 GEMM + 分解。
- **关键算法**：**单纯形法**——选进基（$\bar c_j<0$）/出基（最小比值主元），沿边到更优顶点，
  直到 $\bar c_j\ge0$（最优）。**原始对偶内点**——$\min c^\top x-\mu\sum\log(b_i-a_i^\top x)$，$\mu\to0$。
- **自测**：单纯形为什么「最坏指数但实践多项式」？
  （提示：Klee-Minty 构造走遍 $2^n$ 顶点；但平均 $O(n)$ 步——Spielman-Teng 平滑分析（2001）证明随机扰动后期望多项式。）

---

## 第 14 章 · Network and Combinatorial Optimization 网络与组合优化（PP.385-420）

- **核心**：图上优化。**最短路**（Dijkstra $O(E+V\log V)$/Bellman-Ford $O(VE)$）、
  **最大流**（Ford-Fulkerson 增广路径/推-重标 $O(V^2E)$）、**最小费用流**、**网络单纯形**。
  **指派/运输问题**是网络流特例。组合优化（TSP/排班）NP-hard，需整数规划+分支定界（第 19 章）。
  网络问题因**全单模性**整数解自动满足，LP 松弛即精确解。
- **飞腾锚点**：**分支预测 [Lab02]** 🟢。
  图遍历（DFS/BFS/Dijkstra 优先队列）核心是「访问邻居 + 条件判断（已访问？更优？）」——
  分支密集且数据依赖（图结构不规则→缓存/分支均不友好）。
  AI 锚点：**GNN 消息传递 = 网络优化的可微版**；**物流调度（美团/滴滴）= 最短路/指派落地**。
- **关键概念**：**全单模性（TU）**——$A$ 每个方子阵行列式 $\in\{-1,0,1\}$
  $\Rightarrow$ LP 顶点自动整数。网络问题 $A$=关联矩阵恒 TU，可精确求解无需整数规划——图结构的免费午餐。
- **自测**：网络单纯形为什么比通用单纯形快？
  （提示：网络 LP 基矩阵=生成树，基变换只需 $O(V)$ 树操作（加/删边）vs 通用 $O(V^3)$ 主元。）

---

# Part V · 约束非线性优化算法（第 15-18 章）⭐⭐⭐

---

## 第 15 章 · Quadratic Programming 二次规划（PP.421-472）

- **核心**：$\min \frac12x^\top Qx+c^\top x$ s.t. $Ax\le b$。QP 是约束优化「最小非平凡问题」，
  也是 **SQP（第 17 章）每步的子问题**。
  ① **等式 QP**：KKT 系统 $\begin{bmatrix}Q&A^\top\\A&0\end{bmatrix}\begin{bmatrix}x\\\lambda\end{bmatrix}=-\begin{bmatrix}c\\b\end{bmatrix}$ 直接解。
  ② **不等式 QP**：**活动集法**（猜活跃约束，解等式 QP，调整）或**内点法**。
  $Q\succeq0$ 凸 QP（全局最优），$Q$ 不定非凸 QP（NP-hard）。
- **飞腾锚点**：**GEMM 9.45G [Lab05]** 🟢。
  QP 核心是解 KKT 系统（不定对称鞍点阵），大 QP 需稀疏分解（LDL$^\top$/Schur 补）+ 迭代精化。
  GEMM 加速因子化和回代。AI 锚点：**SVM 训练=凸 QP**；**MPC=每步解 QP**（自动驾驶/机器人核心）。
- **关键算法**：**活动集法**——维护活跃集 $\mathcal{W}$，每步解等式 QP 得方向 $p$；
  可行则走、否则算最大步长加入阻断约束；乘子负则移除约束。最坏指数但实践快。
- **自测**：为什么非凸 QP（$Q$ 不定）是 NP-hard？
  （提示：非凸 QP 可编码布尔约束 $x_i(1-x_i)=0\Rightarrow x_i\in\{0,1\}$，归约到整数规划 NP-complete。）

---

## 第 16 章 · Penalty and Augmented Lagrangian 罚函数与增广 Lagrangian（PP.473-514）

- **核心**：把约束优化转化为无约束问题。
  ① **二次罚函数**：$\min f+\frac\mu2\|c^+\|^2$，$\mu\to\infty$ 逼真约束——但**病态**（$\kappa\sim\mu$）。
  ② **增广 Lagrangian（ALM）**：$L_A=f+\lambda^\top c+\frac\mu2\|c\|^2$，
  同时优化 $x$ 和更新 $\lambda\leftarrow\lambda+\mu c$——**$\mu$ 不需趋于无穷**，$\lambda$ 收敛到真实乘子，避免病态。
  ③ **精确罚函数**（$\ell_1$ 罚 $\mu\|c^+\|_1$）有限 $\mu$ 即精确但不可微。
- **飞腾锚点**：**Iron Law <2% [Lab00]**（收敛误差）🟢。
  二次罚 $\mu\to\infty$ 使 $\kappa\sim\mu\to\infty$，线性系统误差 $\sim\kappa\epsilon_{\text{mach}}$ 爆炸
  ——Iron Law 限定 $\mu$ 上限（$\mu\epsilon<2\%$）。ALM 的 $\lambda$ 更新分担「逼真」压力，
  $\mu$ 保持适中，**从根本上避免 Iron Law 违约**——这是 ALM 取代纯罚函数的工程动机。
- **关键算法**：**增广 Lagrangian（ALM/Hestenes-Powell）**——
  内层无约束解 $\min_x L_A(x,\lambda;\mu)$；外层 $\lambda^+\leftarrow\lambda+\mu c$，必要时增 $\mu$。
  AI 锚点：ALM 是**约束训练（如 PINN 物理信息神经网络）的标准框架**。
- **自测**：ALM 比纯二次罚函数好在哪？
  （提示：纯罚需 $\mu\to\infty$ 致病态（Iron Law 违约）；ALM 乘子更新让中等 $\mu$ 即精确，避免病态。）

---

## 第 17 章 · Sequential Quadratic Programming 序列二次规划（PP.515-542）⭐⭐⭐

- **核心**：约束优化的「牛顿法」。每步解 **QP 子问题**（Lagrange 函数二次近似 + 约束线性化）：
  $\min_p \frac12p^\top\nabla^2_{xx}\mathcal{L}p+\nabla f^\top p$ s.t. $\nabla c_i^\top p+c_i=0$。
  QP 的解 $p$ 是搜索方向，乘子给出新 $\lambda$。**SQP = 对 KKT 系统施牛顿法**。
  加线搜索（$\ell_1$ 精确罚 merit function）或信赖域保全局收敛。
  拟牛顿近似 $\nabla^2_{xx}\mathcal{L}$（BFGS/SR1）避免二阶导。**SQP 是中等规模约束优化最强方法**。
- **飞腾锚点**：**UDOT 16.9× [E05]**（梯度点积）🟢。
  SQP 每步需 $\nabla f$ 和所有 $\nabla c_i$（约束 Jacobi），梯度评估成本高时 UDOT 向量化的点积直接加速。
  QP 子问题求解（活动集/内点）内部也大量点积（投影、对偶间隙 $\sum\lambda_ic_i$）。
  AI 锚点：**SQP 是机器人轨迹优化、航空航天、化工流程的工业标准**（SNOPT/filterSQP）。
- **关键算法**：**SQP 迭代**——① 解 QP 子问题（BFGS 近似 Hessian）得 $p_k,\lambda_{k+1}$；
  ② 线搜索（merit $\phi=f+\mu\|c^+\|_1$）得 $\alpha_k$；③ $x_{k+1}=x_k+\alpha_kp_k$。收敛率：超线性/二次。
- **自测**：SQP 与第 12 章 KKT 的关系？
  （提示：SQP=对 KKT 施牛顿法——QP 子问题 KKT=原问题 KKT 线性化，牛顿步=解线性化 KKT。）

---

## 第 18 章 · Interior-Point Methods for Nonlinear Programming 非线性内点法（PP.543-572）⭐⭐⭐

- **核心**：约束优化的「多项式复杂度」方法。对不等式 $c_i(x)\ge0$ 引入松弛 $s_i\ge0$ + 对数障碍
  $-\mu\sum\log s_i$，沿中心路径 $\mu\to0$ 逼近最优。
  **原始对偶法**同时迭代 $(x,s,\lambda)$，解扰动 KKT：
  $\nabla f-A^\top\lambda=0$，$S\Lambda e=\mu e$，$c(x)-s=0$。
  牛顿步解此非线性系统，$\mu$ 递减（$\mu_{k+1}=\sigma_k\mu_k$）。
  **多项式收敛**（凸情形），是 LP/SOCP/SDP/非线性约束的统一框架。
- **飞腾锚点**：**TLB 4.81× [E04]**（稀疏 Hessian）🟢。
  大规模内点法（IPOPT）每步解**稀疏 KKT 系统**
  $\begin{bmatrix}\nabla^2\mathcal{L}&0&A^\top\\0&\Sigma&A_{ineq}^\top\\A&A_{ineq}&0\end{bmatrix}\Delta=-r$
  ——稀疏分解（LDL$^\top$）TLB 局部性极强，4.81× 来自 nested dissection 排序。
  AI 锚点：**IPOPT 是开源约束优化之王**，广泛用于化工/电网/金融。
- **关键定理**：**中心路径存在性**——凸+Slater $\Rightarrow$ 中心路径 $(x(\mu),\ldots)$ 存在唯一光滑，
  $\mu\to0$ 时 $\to(x^\ast,\ldots)$。**多项式复杂度**：自协和 $O(\sqrt\nu\log(1/\epsilon))$ 步。
- **自测**：内点法 vs 活动集法（第 15 章）的区别？
  （提示：活动集「跳顶点」（离散切换，组合味）；内点「穿」内部沿中心路径平滑逼近（连续味，多项式）。）

---

# Part VI · 全局优化（第 19 章）

---

## 第 19 章 · Global Optimization 全局优化与混合整数（PP.573-606）

- **核心**：非凸优化的「终极困难」——找**全局**最优（而非局部稳定点）。
  ① **分支定界（Branch and Bound）**：递归分割可行域，松弛算下界，LB$\ge$UB 则剪枝——
  **整数规划/MIP 的标准算法**。
  ② **元启发式**：遗传算法（GA，选择/交叉/变异）、模拟退火（SA，Metropolis 接受）、
  粒子群（PSO）——**无理论保证但实践有效**。
  ③ **多起点法**：多个初值跑局部优化取最优。
  核心张力：**完整性（保证全局）vs 效率（NP-hard 不可避免）**。
- **飞腾锚点**：**分支预测 [Lab02]** 🟢。
  分支定界「分支」=递归二分决策树——每节点判断「剪枝 or 继续」，分支密集数据依赖。
  模拟退火 $P(\text{accept})=\min(1,e^{-\Delta f/T})$ 是随机分支。
  AI 锚点：**MIP=整数+连续变量**（供应链/选址/排班，Gurobi/CPLEX）；
  **NAS=组合优化的 ML 版**（搜索空间离散巨大）。
- **关键算法**：**分支定界**——① 松弛（$x_i\in\{0,1\}\to[0,1]$）解连续得 LB；
  ② LB$\ge$UB 则剪枝；③ 否则分支（$x_i=0$ vs $1$）递归。
  **模拟退火**——$\Delta f<0$ 接受，否则以 $e^{-\Delta f/T}$ 接受（允许爬山），$T\to0$ 退火。
- **自测**：为什么全局优化「无免费午餐」（NFL）？
  （提示：Wolpert-Macready NFL（1997）：对所有函数取平均，任何两算法期望性能相同——没有万能优化器。出路=领域知识。）

---

## §9 思想主线：从无约束到约束到全局的三级火箭

全书贯穿着一条清晰的**递进主线**，可用「三级火箭」概括：

**第一级 · 无约束（第 3-9 章）**：两大框架——**线搜索**（沿方向搜步长，Wolfe 保收敛）与**信赖域**（球内整体近似，自适应调半径）——是所有优化的基石。两者之上叠加**加速器**：CG（$A$-共轭性，Krylov 正交化）、拟牛顿 BFGS（割线近似 Hessian 逆，超线性）、L-BFGS（限内存，大规模）。这一级是 **ML 训练的直接源头**：Adam 是自适应线搜索、L-BFGS 是大模型全批量微调主力。飞腾锚点密集覆盖：Iron Law（收敛误差）、matmul（Hessian 运算）、分支预测（线搜索分支）。

**第二级 · 约束（第 12-18 章）**：KKT 条件提供理论终点（一阶必要+二阶充分），算法上分三条路线——**罚函数/增广 Lagrangian**（化约束为无约束，$\lambda$ 乘子更新避免病态）、**SQP**（每步解 QP，KKT 的牛顿法，超线性）、**内点法**（中心路径+对数障碍，多项式复杂度）。这三者从不同角度逼近 KKT，是**机器人控制、约束训练、运筹优化**的算法根基。UDOT（梯度点积）和 GEMM（大规模 LP）锚定约束算法的工程成本。

**第三级 · 全局（第 19 章）**：当凸性被彻底打破，局部最优不再够用——分支定界提供**完整性的组合保证**（整数规划，松弛+剪枝），元启发式提供**启发式的实践效率**（无保证但有效）。这一级承认「NP-hard 不可解」的现实，用松弛+剪枝在精确与效率间求平衡。

三级的统一精神：**用局部信息（梯度/Hessian）做全局决策（最优/剪枝）**——无约束靠 Taylor 近似、约束靠 KKT 线性化、全局靠分支松弛。**优化的本质 = 用廉价局部模型驱动昂贵全局搜索**。

---

## §10 交叉引用与飞腾锚点速查

### 与路径其他书的交叉

| 本书概念 | 关联书/方向 | 接口 |
|:------|:------|:-----|
| 线搜索/信赖域/牛顿 | **[D-凸优化 Boyd] 第 9 章** | Boyd 讲凸的理论，NW 讲打破凸假设的算法工程 |
| KKT 条件（非凸必要） | **[D-凸优化] 第 5 章** | Boyd 凸 KKT 充要 vs NW 非凸 KKT 仅必要 |
| 单纯形/内点法 | **[线性规划] 全书** | Vaserstein 讲 LP 建模，NW 讲 LP 算法实现 |
| 有限差分/AD | **[Kress 数值分析 GTM181]** | 数值微分/自动微分的数值分析根基 |
| 共轭梯度 CG | **[Kress] 数值线代** | Krylov 子空间法的统一视角 |
| L-BFGS 大规模 | **ML 训练（Adam/L-BFGS）** | 大模型全批量微调的标准优化器 |
| 内点法多项式复杂度 | **[D-凸优化] 第 11 章** | Boyd 自协和分析 vs NW 原始对偶实现 |
| 分支定界/组合 | **[GKP 具体数学] 组合** | 离散优化的组合学根基 |

### AI 锚点（优化 = ML 训练核心）

| 算法 | AI/工程落地 |
|:------|:------|
| **L-BFGS**（第 7 章） | 大模型全批量微调主力（比 Adam 内存友好） |
| **Adam/SGD**（第 3 章延伸） | 自适应线搜索 = 深度学习训练引擎 |
| **Gauss-Newton/LM**（第 10 章） | SLAM、Bundle Adjustment、相机标定 |
| **SQP**（第 17 章） | 机器人轨迹优化、航空航天设计（SNOPT） |
| **内点法 IPOPT**（第 18 章） | 开源约束优化之王，化工/能源/金融 |
| **AD 反向模式**（第 8 章） | PyTorch autograd = backprop 的数学本质 |
| **分支定界/MIP**（第 19 章） | 供应链设计、神经架构搜索（NAS） |

### 飞腾锚点速查（每章 1 个，共 19 个）

| 锚点 | 章节 | 主题 |
|:------|:------|:------|
| **Iron Law <2% ⭐** | Ch1, 4, 11, 16 | 收敛误差铁律（引言/信赖域/方程组/罚函数） |
| **matmul 15× ⭐** | Ch2, 6, 12 | Hessian 矩阵运算（最优性/BFGS/KKT） |
| **分支预测** | Ch3, 9, 14, 19 | 数据依赖分支（线搜索/无导数/网络/分支定界） |
| **Schmidt 正交化** | Ch5 | CG 共轭性 = $A$-正交化 |
| **TLB 4.81×** | Ch7, 18 | 稀疏 Hessian/大规模 KKT（L-BFGS/内点法） |
| **FP16 3.81×** | Ch8 | 有限差分精度（AD 不受低精度影响） |
| **UDOT 16.9× ⭐** | Ch10, 17 | 梯度点积（Gauss-Newton/SQP） |
| **GEMM 9.45G** | Ch13, 15 | 大规模 LP/QP 的稀疏矩阵运算 |

---

> **下一步**：精读 NW 第 3-4 章（线搜索 vs 信赖域）+ 第 6-7 章（BFGS/L-BFGS，ML 训练源头）+ 第 12 章（KKT 约束理论枢纽）；研究选题「**飞腾低精度 L-BFGS 的收敛性退化与补偿**」——当割线方程被量化噪声打破，超线性收敛退化多少？能否用 Iron Law 误差补偿？衔接 [D-凸优化] 第 3 章锚点（凸性被噪声破坏）。
