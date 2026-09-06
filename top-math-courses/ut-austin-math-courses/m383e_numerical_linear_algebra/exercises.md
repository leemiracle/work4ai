# UT Austin M 383E · 习题集（精选 + 解题思路）

> **来源**：Trefethen & Bau *Numerical Linear Algebra* 课后习题 + 自编

---

## 第 1 章 · QR 分解

### Q1.1（基础）
用修正 Gram-Schmidt 对 $A = \begin{pmatrix} 1 & 1 \\ 0 & 1 \\ 0 & 0 \end{pmatrix}$ 做 QR 分解。

<details><summary>解</summary>

$k=0$: $r_{00} = \|a_0\| = 1$, $q_0 = (1,0,0)^T$。
$k=1$: $r_{01} = q_0^T a_1 = 1$。$v = a_1 - r_{01}q_0 = (0,1,0)^T$, $r_{11} = 1$, $q_1 = (0,1,0)^T$。

$$Q = \begin{pmatrix} 1 & 0 \\ 0 & 1 \\ 0 & 0 \end{pmatrix}, \quad R = \begin{pmatrix} 1 & 1 \\ 0 & 1 \end{pmatrix}$$

验证 $QR = A$ ✓。注意 $A$ 已基本正交，QR 恰好 = $A$。
</details>

### Q1.2（中等）
解释为什么经典 Gram-Schmidt（CGS）在数值上不稳定，而修正 Gram-Schmidt（MGS）稳定。

<details><summary>解</summary>

**CGS**：$r_{jk} = q_j^T a_k$（始终用原始 $a_k$）。
**MGS**：$r_{jk} = q_j^T v_k$，其中 $v_k$ 已减去之前所有 $q_j$ 分量。

CGS 的问题：当 $a_k$ 几乎在 $\text{span}(q_0,\dots,q_{k-1})$ 中时，$a_k$ 与 $v_k$ 的舍入误差导致 $q_k$ 与前面 $q_j$ 的正交性丢失（$\|Q^TQ - I\| \gg \epsilon$）。

MGS 通过"逐步减去分量"避免了这种误差积累。**但 MGS 也不是完全向后稳定**——Householder QR 才是工业首选。

**ML 关联**：PyTorch `torch.linalg.qr` 用 Householder。
</details>

### Q1.3（中等）
Householder 反射 $H = I - 2vv^T/(v^Tv)$。证明 $H$ 是正交对称矩阵，且能把任意向量 $x$ 反射到 $\pm\|x\|e_1$。

<details><summary>解</summary>

**对称**：$H^T = I - 2vv^T/(v^Tv) = H$。
**正交**：$H^TH = (I - 2\frac{vv^T}{v^Tv})^2 = I - 4\frac{vv^T}{v^Tv} + 4\frac{v(v^Tv)v^T}{(v^Tv)^2} = I$。

要把 $x$ 反射到 $\alpha e_1$：$Hx = x - 2\frac{v^Tx}{v^Tv}v = \alpha e_1$。取 $v = x - \alpha e_1$，$\alpha = -\text{sign}(x_1)\|x\|$（选符号避免相消）。
</details>

---

## 第 2 章 · 条件数与稳定性

### Q2.1（基础）
$A = \text{diag}(10^6, 1)$ 的条件数是多少？解 $Ax = b$ 时最多损失几位有效数字？

<details><summary>解</summary>

$\kappa(A) = 10^6/1 = 10^6$。约损失 $\log_{10}(10^6) = 6$ 位有效数字（双精度有 ~16 位，剩 ~10 位）。

**ML 关联**：Hessian 病态导致梯度下降震荡——见 [Stanford CME 364A](../../stanford-math-courses/cme364A_convex_optimization/) 条件数实验。
</details>

### Q2.2（中等）
证明最小二乘正规方程 $A^TA\hat{x} = A^Tb$ 的条件数是 $\kappa(A)^2$，因此不推荐。

<details><summary>解</summary>

$A^TA$ 的特征值是 $\sigma_i^2$（$A$ 的奇异值平方）。$\kappa(A^TA) = \sigma_{\max}^2/\sigma_{\min}^2 = \kappa(A)^2$。

若 $\kappa(A) = 10^8$，正规方程损失 16 位 → 完全失效，而 QR 解法只损失 8 位。

**ML 关联**：`np.linalg.lstsq` 不用正规方程而用 SVD/QR。
</details>

### Q2.3（中等）
Hilbert 矩阵 $H_{ij} = 1/(i+j-1)$ 是著名的病态矩阵。$H_{5}$ 和 $H_{10}$ 的条件数约多少？

<details><summary>解</summary>

$\kappa(H_5) \approx 4.8 \times 10^5$，$\kappa(H_{10}) \approx 1.6 \times 10^{13}$。

$H_{15}$ 的 $\kappa \sim 10^{17}$ 已超出双精度范围 → 数值上等于奇异矩阵。最小二乘拟合高次多项式 = 解 Hilbert 系统，故高次多项式拟合数值灾难。
</details>

### Q2.4（开放）
"向后稳定的算法解良态问题一定准确"——这句话对吗？给出反例或证明。

<details><summary>解</summary>

**对**。向后稳定 + 良态 → 准确。

证明：向后稳定 $\Rightarrow \tilde{f}(x) = f(\tilde{x})$, $\|\tilde{x}-x\|/\|x\| = O(\epsilon_{\text{mach}})$。良态 $\Rightarrow \|f(\tilde{x})-f(x)\|/\|f(x)\| \leq \kappa \cdot O(\epsilon_{\text{mach}})$。两者结合 $\Rightarrow$ 总误差 $O(\kappa\epsilon_{\text{mach}})$，良态时 $\kappa$ 小 → 准确。

反例（说明两者都要）：良态问题 + 不稳定算法（CGS）→ 不准确；病态问题（Hilbert）+ 稳定算法 → 仍不准确。
</details>

---

## 第 3 章 · SVD 与应用

### Q3.1（基础）
$A = \begin{pmatrix} 3 & 0 \\ 0 & 2 \end{pmatrix}$ 的 SVD 是什么？最佳秩 1 近似是什么？

<details><summary>解</summary>

$A$ 已对角 → $U = I, \Sigma = \text{diag}(3,2), V = I$。

秩 1 近似：$A_1 = 3 \cdot e_1 e_1^T = \begin{pmatrix} 3 & 0 \\ 0 & 0 \end{pmatrix}$（保留最大奇异值）。

误差 $\|A - A_1\|_F = 2 = \sigma_2$（Eckart-Young）。
</details>

### Q3.2（中等）
用 SVD 推导最小二乘解 $\hat{x} = A^+ b$，并说明当 $A$ 秩亏时为何 SVD 唯一给出最小范数解。

<details><summary>解</summary>

$A = U\Sigma V^T$。$A^+ = V\Sigma^+U^T$（$\Sigma^+$ 把非零 $\sigma_i$ 取倒数，零保留）。

$\hat{x} = V\Sigma^+U^T b = \sum_{i:r} \frac{u_i^T b}{\sigma_i} v_i$。

秩亏时，$A$ 的零空间非平凡，最小二乘解不唯一。但 SVD 解**只在行空间投影**（不含零空间分量），故范数最小。

**ML 关联**：Ridge 回归 $\hat{x} = (A^TA + \lambda I)^{-1}A^Tb$ 是正则化的伪逆。
</details>

### Q3.3（开放）
LoRA 用 $W \approx BA$（$B: m\times r$, $A: r \times n$）近似全秩权重。从 SVD/Eckart-Young 角度分析 LoRA 的理论最优性。

<details><summary>提示</summary>

若训练后的 $W$ 的奇异值谱呈"长尾"（前 $r$ 个占主导），则 $W_r = U_r\Sigma_r V_r^T$ 是最佳秩 $r$ 近似。LoRA 的 $BA$ 可任意秩 $r$ 矩阵，故 SVD 给 $BA$ 的下界。

但 LoRA 实际训练时 $B, A$ 从随机初始化 SGD 更新，**不一定达到 SVD 最优**。实证：LoRA 在低秩适配任务上接近最优。详见 Hu et al. [2106.09685](https://arxiv.org/abs/2106.09685) ⚠️。
</details>

---

## 第 4 章 · 迭代法

### Q4.1（基础）
CG 解 $Ax = b$（$A$ 对称正定），$A = \text{diag}(4, 2, 1)$，最多几步收敛？

<details><summary>解</summary>

理论上 $n$ 步（$n=3$）精确收敛——CG 在 Krylov 子空间 $\mathcal{K}_n$ 中找精确解。

实际精度依赖 $\sqrt{\kappa} = \sqrt{4} = 2$ 步达 $\epsilon$（粗略估计）。
</details>

### Q4.2（中等）
解释预条件 $M^{-1}A$ 为何能加速 CG，并举一个预条件子的例子。

<details><summary>解</summary>

CG 收敛步数 $\sim \sqrt{\kappa(A)}$。若 $M \approx A$，则 $\kappa(M^{-1}A) \approx 1$ → 快速收敛。

预条件子例子：
- **对角预条件（Jacobi）**：$M = \text{diag}(A)$（Adam 的数学根基）
- **不完全 Cholesky**：$M = \tilde L \tilde L^T$（$\tilde L$ 是稀疏 Cholesky）
- **代数多网格（AMG）**：椭圆型 PDE 的标配

**ML 关联**：Adam 的 $v_t$ 就是对角预条件，$M = \text{diag}(\sqrt{v_t})$。
</details>

### Q4.3（开放）
GMRES 在非对称矩阵上每步最小化残差，但内存 $O(kn)$。重启策略（GMRES(m)）有什么权衡？

<details><summary>提示</summary>

GMRES(m) 每 $m$ 步重启，内存 $O(mn)$。但重启可能丢失收敛信息 → **停滞（stagnation）**。权衡：$m$ 大内存多但收敛好；$m$ 小内存省但可能不收敛。

替代：GCROT、GCRODR（带回收的 GMRES），BiCGSTAB（短递归但双倍矩阵-向量乘）。

**ML 关联**：attention 的非对称大矩阵求逆可能用 GMRES 变体（前沿研究）⚠️。
</details>
