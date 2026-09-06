# ETH 401-3904 · 费曼三层讲透：凸优化（ETH 版）

> **教材**：Boyd & Vandenberghe, *Convex Optimization* ★；Bubeck, *Convex Optimization: Algorithms and Complexity* (2015)
> **关联**：与 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/) 同类，ETH 版更侧重算法复杂度理论

> 本课的核心数学（凸集/凸函数/KKT/对偶/算法）与 Stanford CME 364A 完全一致，详见 [CME 364A notes.md](../../stanford-math-courses/cme364A_convex_optimization/notes.md)。本笔记聚焦 **ETH 特色：算法复杂度理论（Bubeck 视角）**。

---

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **凸优化** | "碗底一定在最底部"——局部最优 = 全局最优 |
| **Bubeck 复杂度** | "任何一阶算法在凸问题上都有信息论下界"——你不可能比 GD 更聪明 |
| **Oracle 模型** | "算法只能问两个问题：这点的梯度是多少？这点的函数值是多少？" |

> **ETH 特色**：Bubeck 用**信息论复杂度**证明：$L$-平滑凸函数上，任何一阶方法的迭代复杂度下界 $\Omega(L/\epsilon)$。GD 恰好达到这个下界——**GD 已经是最优的**。

---

## 🧮 数学层（Bubeck 的复杂度下界）

### 一阶 Oracle 模型

算法在每个查询点 $x_k$ 只能获得：
- **梯度 oracle**：$\nabla f(x_k)$
- **函数值 oracle**：$f(x_k)$

### GD 的迭代复杂度

$L$-平滑凸函数：$f(x_k) - f^\star \leq \frac{L\|x_0 - x^\star\|^2}{2k}$

要达 $\epsilon$ 精度需 $k = O(L/\epsilon)$ 步。

### 复杂度下界（Nesterov 2004, Bubeck 2015）★★

**定理**：对任何只使用 $k$ 次一阶 oracle 的算法，存在 $L$-平滑凸函数 $f$ 使得：
$$f(x_k) - f^\star \geq \frac{L\|x_0 - x^\star\|^2}{32(k+1)^2} \cdot c$$

（具体常数版本见 Nesterov *Introductory Lectures*）

> **推论**：$k = \Omega(1/\epsilon)$ 步才能达 $\epsilon$ 精度。**GD 的 $O(1/k)$ 收敛率是最优的**（不用加速的话）。

### Nesterov 加速：突破到 $O(1/k^2)$

$$y_k = x_k + \frac{k-1}{k+2}(x_k - x_{k-1})$$
$$x_{k+1} = y_k - \frac{1}{L}\nabla f(y_k)$$

收敛：$f(x_k) - f^\star \leq O(L/k^2)$。**Nesterov 加速达到一阶方法的信息论下界**。

### 强凸场景

$m$-强凸 + $L$-平滑（$\kappa = L/m$）：
- GD：$O(\kappa \log(1/\epsilon))$（线性收敛）
- Nesterov 加速：$O(\sqrt{\kappa}\log(1/\epsilon))$——**平方根加速**
- 下界：$\Omega(\sqrt{\kappa})$——Nesterov 最优

### 非光滑凸（次梯度法）

$f$ 凸但不可微（如 $\ell_1$ 范数）：
$$x_{k+1} = x_k - \eta_k g_k, \quad g_k \in \partial f(x_k)$$

收敛 $O(1/\sqrt{k})$——**比光滑慢**。可用 smoothing 技巧（Nesterov 2005）恢复 $O(1/k)$。

---

## 💻 代码层

```python
import numpy as np

def nesterov_accelerated_grad(grad_f, x0, L, n_iter=200):
    """Nesterov 加速梯度下降: O(1/k^2) vs GD 的 O(1/k)"""
    x = x0.copy(); x_prev = x0.copy()
    trajectory = [x.copy()]
    for k in range(1, n_iter + 1):
        y = x + (k - 1) / (k + 2) * (x - x_prev)
        x_prev = x.copy()
        x = y - (1.0 / L) * grad_f(y)
        trajectory.append(x.copy())
    return np.array(trajectory)

# 凸二次函数: 比较 GD vs Nesterov
A = np.diag([10.0, 1.0]); L = 10.0
grad_f = lambda x: A @ x
x0 = np.array([5.0, 5.0])
traj_nes = nesterov_accelerated_grad(grad_f, x0, L, n_iter=100)
# GD 对比...
```

---

## ⚠️ 不足层

| 局限 | 说明 |
|---|---|
| **复杂度下界假设确定 oracle** | 随机 oracle（SGD）有不同界 |
| **Nesterov 加速对噪声敏感** | SGD + 动量的理论更微妙 |
| **非凸无下界保证** | 深度学习的非凸优化，复杂度理论尚不完善 |
| **高阶方法代价高** | 牛顿法 $O(n^3)$，立方正则化 $O(n^3)$ |

---

## 🔬 应用层

1. **Nesterov 加速 → PyTorch `SGD(momentum, nesterov=True)`**
2. **Adam 的收敛保证（Reddi 2018 AMSGrad 修复，[1804.04825](https://arxiv.org/abs/1804.04825) ✅）**
3. **分布式优化的通信复杂度下界**
4. **RLHF 的凸化（DPO）**：见 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/)

---

## 🆕 2024-2026 最新研究

- **Schedule-Free Optimization**（Defazio 2024）：无需调学习率调度的加速方法
- **机器学习的 oracle 复杂度**：差分隐私约束下的下界
- **分布凸优化的 lower bound**：通信 vs 本地计算权衡

---

## 📚 参考结构

| 来源 | 章节 |
|---|---|
| Boyd & Vandenberghe | 凸集/凸函数/KKT/对偶（与 CME 364A 共享）|
| Bubeck (2015) | 第 3-4 章：一阶方法复杂度 |
| Nesterov (2018) | 第 2 章：加速方法 |

详见 [Stanford CME 364A notes.md](../../stanford-math-courses/cme364A_convex_optimization/notes.md) 的 KKT / SVM / 梯度下降完整推导。
