# Stanford CME 364A · 费曼三层讲透：凸优化

> **教材**：Boyd & Vandenberghe, *Convex Optimization* (Cambridge, 2004) — **免费 PDF** ★
> **一手核实**：[web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf) ✅
> **视频**：[Boyd ENGR108 全套](https://www.youtube.com/playlist?list=PL3940CE95F3B87249) ✅
> **配套库**：CVXPY [cvxpy.org](https://cvxpy.org)

---

# 费曼三层讲透：凸优化到底在研究什么？

## 🧠 直觉层（1 句话比喻）

| 概念 | 比喻 |
|---|---|
| **凸集** | **"碗的内壁"**——集合里任两点连线仍藏在碗里，永不凸出 |
| **凸函数** | **"碗底一定在最底部"**——弦永远在图像上方，局部最小 = 全局最小 |
| **凸优化问题** | **"在碗里找最低点"**——只要在碗内，随便怎么滚都能到底 |
| **拉格朗日函数** | **"把约束罚成目标的一部分"**——$\mathcal{L}(x,\lambda)=f+\lambda g$，用乘子把"不许越界"变成"越界要付代价" |
| **对偶问题** | **"从碗外面看碗底"**——给原问题找一个永远 $\leq$ 原解的下界，强对偶时两者相等 |
| **KKT 条件** | **"拉格朗日乘子 + 互补松弛"**——驻点 + 约束激活时乘子才非零，最优解的"通关密码" |
| **梯度下降** | **"蒙眼下山，每步朝最陡方向"**——$\theta_{k+1}=\theta_k-\eta\nabla f$ |
| **牛顿法** | **"用碗的曲率一次跳到底"**——$\theta_{k+1}=\theta_k-(\nabla^2 f)^{-1}\nabla f$，二阶信息一步抵多步 |
| **对偶间隙** | **"原问题与对偶问题的差距"**——凸问题 Slater 条件下为 0 |

> **一句话总结**：**凸优化 = "碗底一定在最底部"**。只要问题凸，梯度下降/牛顿法保证收敛到全局最优。深度学习之所以难，正是因为损失函数**非凸**——有无数个局部碗底。

---

## 🧮 数学层（核心定义 + 定理 + LaTeX）

### 1. 凸集（Convex Sets）

**定义**：$C \subseteq \mathbb{R}^n$ 是凸集，若
$$\forall x, y \in C, \forall \theta \in [0,1]: \quad \theta x + (1-\theta)y \in C$$

**几何**：集合中任两点的线段全在集合内。

**保凸运算**：
- 交集：$C_1 \cap C_2$ 凸（**最重要的性质**——许多可行域是约束的交集）
- 仿射变换：$AC + b$ 凸
- 透视变换、分式线性变换保凸

**重要凸集例子**：
| 凸集 | 定义 |
|---|---|
| 超平面 | $\{x : a^Tx = b\}$ |
| 半空间 | $\{x : a^Tx \leq b\}$ |
| 范数球 | $\{x : \|x\|_p \leq r\}$ |
| 椭球 | $\{x : (x-x_c)^T P^{-1}(x-x_c) \leq 1\}$ |
| 多面体 | $\{x : Ax \preceq b\}$（有限个半空间交集）|
| 正半定锥 | $\mathbb{S}^n_+ = \{X \in \mathbb{S}^n : X \succeq 0\}$ |

### 2. 凸函数（Convex Functions）

**定义**：$f: \mathbb{R}^n \to \mathbb{R}$ 是凸函数，若 $\text{dom}\, f$ 凸且
$$\forall x, y \in \text{dom}\, f, \forall \theta \in [0,1]: \quad f(\theta x + (1-\theta)y) \leq \theta f(x) + (1-\theta)f(y)$$

**一阶条件**（$f$ 可微）★：
$$f(y) \geq f(x) + \nabla f(x)^T (y - x) \quad \forall x, y$$

> **直觉**：凸函数的切平面永远是全局下界（"托底"）。

**二阶条件**（$f$ 二阶可微）★：
$$\nabla^2 f(x) \succeq 0 \quad \forall x \in \text{dom}\, f$$

> **直觉**：Hessian 半正定 = 处处"碗状"。

**保凸运算**：
- 非负加权和：$\alpha f + \beta g$ 凸（$\alpha,\beta \geq 0$）
- 逐点取上确界：$\sup_{i} f_i(x)$ 凸
- 仿射复合：$f(Ax+b)$ 凸
- 期望：$f(x) = \mathbb{E}_\xi[g(x,\xi)]$ 凸（**SGD 的理论根基**）

**经典凸函数**：
- $f(x) = x^p$（$p \geq 1$ 或 $p \leq 0$）
- $f(x) = e^{ax}$、$f(x) = -\log x$、$f(x) = x\log x$
- 范数：$\|x\|_p$ 凸
- $f(X) = \log\det X$（在 $\mathbb{S}^n_{++}$ 上凹）

### 3. 凸优化问题

$$\min_{x} f_0(x) \quad \text{s.t.} \quad f_i(x) \leq 0,\ i=1,\dots,m; \quad h_i(x) = 0,\ i=1,\dots,p$$

**凸优化问题**要求：$f_0, f_i$ 凸，$h_i$ 仿射。

**关键结论**★：
- **局部最优 = 全局最优**
- 最优集凸
- 若 $f_0$ 严格凸 → 最优解唯一

**标准形式问题**：
| 问题 | 形式 |
|---|---|
| **LP** | $\min c^Tx$ s.t. $Gx \preceq h$ |
| **QP** | $\min \frac12 x^T P x + q^T x$ s.t. $Gx \preceq h$（$P \succeq 0$）|
| **QCQP** | $f_0, f_i$ 均为二次型 |
| **SOCP** | $\|A_i x + b_i\|_2 \leq c_i^T x + d_i$ |
| **SDP** | $\min c^Tx$ s.t. $F_0 + \sum x_i F_i \succeq 0$ |

### 4. 拉格朗日对偶（Duality）★★★

**拉格朗日函数**：
$$\mathcal{L}(x, \lambda, \nu) = f_0(x) + \sum_{i=1}^m \lambda_i f_i(x) + \sum_{i=1}^p \nu_i h_i(x)$$

其中 $\lambda_i \geq 0$（不等式约束乘子），$\nu_i \in \mathbb{R}$（等式约束乘子）。

**对偶函数**：
$$g(\lambda, \nu) = \inf_{x} \mathcal{L}(x, \lambda, \nu)$$

**对偶问题**：
$$\max_{\lambda \succeq 0, \nu} g(\lambda, \nu)$$

**弱对偶**：$g(\lambda, \nu) \leq p^\star$（永远成立，对偶永远给下界）

**强对偶**（凸问题 + **Slater 条件**）：$d^\star = p^\star$
> Slater 条件：存在严格可行点 $\exists x: f_i(x) < 0, h_i(x) = 0$（相对内点非空）

### 5. KKT 条件 ★★★（最优性的充要条件）

凸问题 + Slater 条件下，$x^\star$ 最优 $\iff$ 存在 $\lambda^\star, \nu^\star$ 满足：

$$\nabla f_0(x^\star) + \sum_i \lambda_i^\star \nabla f_i(x^\star) + \sum_i \nu_i^\star \nabla h_i(x^\star) = 0 \quad \text{(平稳性)}$$
$$f_i(x^\star) \leq 0, \quad h_i(x^\star) = 0 \quad \text{(原问题可行)}$$
$$\lambda_i^\star \geq 0 \quad \text{(对偶可行)}$$
$$\lambda_i^\star f_i(x^\star) = 0 \quad \text{(互补松弛) ★}$$

> **互补松弛的直觉**：约束没激活（$f_i < 0$）时，乘子必须为 0（"约束没顶用，乘子也别说话"）；约束激活（$f_i = 0$）时，乘子才可能非零。

### 6. SVM 的完整推导（KKT 的标志性应用）★★★

**SVM 原问题**（硬间隔）：
$$\min_{w,b} \frac12 \|w\|^2 \quad \text{s.t.} \quad y_i(w^T x_i + b) \geq 1,\ i=1,\dots,n$$

**拉格朗日函数**：
$$\mathcal{L}(w,b,\alpha) = \frac12\|w\|^2 - \sum_{i=1}^n \alpha_i\left[y_i(w^T x_i + b) - 1\right], \quad \alpha_i \geq 0$$

**对 $w, b$ 求驻点**：
$$\nabla_w \mathcal{L} = w - \sum_i \alpha_i y_i x_i = 0 \implies \boxed{w^\star = \sum_i \alpha_i y_i x_i}$$
$$\frac{\partial \mathcal{L}}{\partial b} = -\sum_i \alpha_i y_i = 0 \implies \sum_i \alpha_i y_i = 0$$

**代回得对偶问题**：
$$\max_\alpha \sum_i \alpha_i - \frac12 \sum_{i,j} \alpha_i \alpha_j y_i y_j \underbrace{x_i^T x_j}_{K_{ij}} \quad \text{s.t.} \quad \alpha_i \geq 0,\ \sum_i \alpha_i y_i = 0$$

**互补松弛**：$\alpha_i^\star[y_i(w^Tx_i+b)-1]=0$
- $\alpha_i > 0$ → 该样本恰在间隔边界上 → **支持向量**
- $\alpha_i = 0$ → 该样本对分类面无贡献

**核技巧**：把 $x_i^T x_j$ 换成 $K(x_i, x_j) = \phi(x_i)^T\phi(x_j)$，无需显式计算 $\phi$。常用核：高斯 RBF $K = e^{-\gamma\|x-x'\|^2}$。

**决策函数**：
$$f(x) = \text{sign}\left(\sum_{i:\alpha_i>0} \alpha_i y_i K(x_i, x) + b\right)$$

### 7. 算法：梯度下降、牛顿法、拟牛顿

#### 梯度下降（GD）

$$x_{k+1} = x_k - \eta_k \nabla f(x_k)$$

**收敛速率**（$f$ 凸，$L$-平滑 $\nabla^2 f \preceq LI$）：
$$f(x_k) - f^\star \leq \frac{\|x_0 - x^\star\|^2}{2\eta k} \quad \text{(固定步长 } \eta = 1/L\text{)}$$

→ $O(1/k)$ 收敛（次线性）。**强凸**（$mI \preceq \nabla^2 f$）时**线性收敛** $O((1-m/L)^k)$。

#### 随机梯度下降（SGD）

$$x_{k+1} = x_k - \eta_k \nabla f_{i_k}(x_k), \quad i_k \text{ 随机}$$

$\mathbb{E}[\nabla f_{i_k}] = \nabla f$（无偏）。收敛 $O(1/\sqrt{k})$（方差导致变慢），但**每步代价 $O(1)$** vs GD 的 $O(n)$。

#### 牛顿法

$$x_{k+1} = x_k - [\nabla^2 f(x_k)]^{-1} \nabla f(x_k)$$

**收敛速率**：**二次收敛**（近最优解时误差平方级下降）——$O(\log\log(1/\epsilon))$。

**代价**：每步 $O(n^3)$（求逆 Hessian），不适合 $n$ 大。

#### 拟牛顿（BFGS）

用低秩更新近似 Hessian 逆：$H_{k+1} = H_k + \text{rank-2 correction}$，每步 $O(n^2)$，超线性收敛。

#### L-BFGS

只存最近 $m$ 步的 $(s_k, y_k)$，内存 $O(mn)$——大尺度优化标配。

### 8. 内点法（Interior Point）

障碍法（Barrier Method）：
$$\min t f_0(x) - \sum_i \log(-f_i(x)) \quad (\text{去掉不等式约束，用障碍函数罚})$$

逐步增大 $t$，每步用牛顿法。对凸问题，**多项式时间**收敛。

---

## 💻 代码层（numpy 实现）

### 手写梯度下降 + 收敛速率验证

```python
import numpy as np
import matplotlib.pyplot as plt

def gradient_descent(grad_f, x0, lr=0.01, n_iter=1000):
    """朴素梯度下降，返回轨迹"""
    x = x0.copy()
    trajectory = [x.copy()]
    for _ in range(n_iter):
        x = x - lr * grad_f(x)
        trajectory.append(x.copy())
    return np.array(trajectory)

# 凸二次函数 f(x) = 0.5 x^T A x，A 正定
A = np.array([[2.0, 0.5], [0.5, 1.0]])
grad_f = lambda x: A @ x
x_star = np.zeros(2)

traj = gradient_descent(grad_f, np.array([5.0, 5.0]), lr=0.1, n_iter=100)
errors = np.linalg.norm(traj - x_star, axis=1)

plt.semilogy(errors); plt.xlabel('iteration'); plt.ylabel('||x_k - x*||')
plt.title('Gradient descent on convex quadratic: linear convergence'); plt.grid(True)
plt.savefig('gd_convergence.png', dpi=100); plt.show()
```

### SVM 对偶求解（凸二次规划）

```python
def svm_dual_solve(X, y, K_fn=None):
    """SVM 对偶问题: max sum(alpha) - 0.5 sum_ij alpha_i alpha_j y_i y_j K_ij
       s.t. alpha >= 0, sum alpha_i y_i = 0
       用 scipy 的 QP 求解器（这里用 SMO 简化版示意）
    """
    n = len(y)
    if K_fn is None:
        K = X @ X.T  # 线性核
    else:
        K = K_fn(X, X)
    # 这里用 cvxpy 一行求解（凸 QP）
    import cvxpy as cp
    alpha = cp.Variable(n)
    objective = cp.Maximize(cp.sum(alpha) - 0.5 * cp.quad_form(
        cp.multiply(alpha, y), cp.psd_wrap(K)))
    constraints = [alpha >= 0, alpha @ y == 0]
    cp.Problem(objective, constraints).solve()
    alpha_val = alpha.value
    w = ((alpha_val * y)[:, None] * X).sum(axis=0)  # w = sum alpha_i y_i x_i
    sv = alpha_val > 1e-6  # 支持向量
    return w, alpha_val, sv
```

### 牛顿法 vs 梯度下降收敛对比

```python
def newton_method(grad_f, hess_f, x0, n_iter=50, tol=1e-12):
    x = x0.copy()
    traj = [x.copy()]
    for _ in range(n_iter):
        g = grad_f(x)
        if np.linalg.norm(g) < tol: break
        x = x - np.linalg.solve(hess_f(x), g)  # 避免显式求逆
        traj.append(x.copy())
    return np.array(traj)

# 对比: 二次函数上 Newton 二次收敛, GD 线性收敛
A = np.array([[10.0, 2.0], [2.0, 3.0]])
grad_f = lambda x: A @ x
hess_f = lambda x: A
x0 = np.array([8.0, -6.0])

gd_traj = gradient_descent(grad_f, x0, lr=0.03, n_iter=500)
nt_traj = newton_method(grad_f, hess_f, x0, n_iter=20)

plt.semilogy(np.linalg.norm(gd_traj, axis=1), label='GD (linear)')
plt.semilogy(np.linalg.norm(nt_traj, axis=1), label='Newton (quadratic)')
plt.legend(); plt.xlabel('iter'); plt.ylabel('||x_k||'); plt.grid(True)
plt.savefig('newton_vs_gd.png', dpi=100); plt.show()
```

---

## ⚠️ 不足层（局限）

| 局限 | 说明 |
|---|---|
| **非凸时对偶间隙 > 0** | 深度学习损失非凸，KKT 只是必要条件不是充分，SGD 卡局部最小 |
| **牛顿法代价 $O(n^3)$** | 大模型（$n \sim 10^9$）不可行，只能用一阶（SGD/Adam） |
| **Slater 条件可能不成立** | 退化凸问题（如等式约束主导）需用相对内点版 |
| **强凸假设脆弱** | 实际问题常仅凸不强凸，收敛速率从线性退化为次线性 |
| **SGD 方差** | $O(1/\sqrt{k})$ 收敛慢，需 mini-batch / variance reduction (SVRG, SAGA) |
| **条件数 $\kappa$ 大时收敛慢** | GD 收敛速率依赖 $\kappa = L/m$，病态问题需预条件 |
| **整数约束不凸** | 组合优化需松弛 + 分支定界，见 [ETH 401-3901](../../eth-math-courses/e401_3901_linear_combinatorial_optimization/) |

---

## 🔬 应用层（ML 公式级对应）

### 1. SVM = 凸二次规划 + KKT ★

见上文第 6 节完整推导。`sklearn.svm.SVC` 内部就是解这个凸 QP。

### 2. Lasso / Ridge = 带正则的凸优化

$$\min_w \frac{1}{2n}\|Xw - y\|^2 + \lambda \|w\|_1 \quad \text{(Lasso, 凸)}$$
$$\min_w \frac{1}{2n}\|Xw - y\|^2 + \frac{\lambda}{2}\|w\|_2^2 \quad \text{(Ridge, 强凸)}$$

Lasso 的 $\ell_1$ 项导致稀疏解（KKT 互补松弛在 $w_i = 0$ 处给出软阈值）。

### 3. 逻辑回归 = 凸优化

$$\min_w \sum_i \log(1 + \exp(-y_i w^T x_i)) + \frac{\lambda}{2}\|w\|^2$$

损失凸（logistic loss 是凸函数的复合），加 $\ell_2$ 正则后强凸 → 线性收敛。

### 4. SGD = 随机凸优化

经验风险最小化 $f(w) = \frac1n \sum_i \ell(w; x_i, y_i)$，SGD 每步随机抽一个 $i$：
$$w_{k+1} = w_k - \eta_k \nabla \ell(w_k; x_{i_k}, y_{i_k})$$

### 5. Adam = RMSProp + 动量（[1412.6980](https://arxiv.org/abs/1412.6980) ✅）

$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t \quad \text{(一阶矩)}$$
$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2 \quad \text{(二阶矩)}$$
$$\hat{m}_t = m_t/(1-\beta_1^t), \quad \hat{v}_t = v_t/(1-\beta_2^t) \quad \text{(偏差校正)}$$
$$\theta_{t+1} = \theta_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon}$$

> Adam 本质是**对每个参数自适应步长的拟牛顿近似**——用 $v_t$ 估计对角 Hessian。

### 6. RLHF 的偏好优化 = 凸化（2024-2026 热点）

DPO（Direct Preference Optimization, [2305.18290](https://arxiv.org/abs/2305.18290) ✅）把 RLHF 的非凸问题转化为**凸的分类损失**：
$$\mathcal{L}_{\text{DPO}} = -\log\sigma\left(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta\log\frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)$$

### 7. SDP 用于聚类 / 社区检测

半监督聚类松弛成 SDP：$\max \text{Tr}(CX)$ s.t. $X \succeq 0$, $X_{ii}=1$。

---

## 📚 章节结构对照（Boyd & Vandenberghe）

| 章 | 主题 | 重要性 |
|---|---|---|
| 2 | Convex sets | ★★ |
| 3 | Convex functions | ★★★ |
| 4 | Convex optimization problems | ★★★ |
| 5 | Duality | ★★★ |
| 9 | Unconstrained minimization (GD, Newton) | ★★★ |
| 10 | Equality constrained minimization | ★★ |
| 11 | Interior point methods | ★★ |

---

## 与 work4ai 讲透系列的交叉

- **讲透优化器（SGD/Adam/Lion）**：第 9 章 + 第 5 章对偶
- **讲透 SVM**：第 5 章 KKT 完整推导
- **讲透正则化（L1/L2）**：第 3 章凸函数 + 第 4 章凸问题
- **讲透 RLHF/DPO**：凸化技巧
