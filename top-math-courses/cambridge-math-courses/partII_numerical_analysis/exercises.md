# Cambridge Part II NA · 习题集

### Q1（基础）
CG 的 Chebyshev 收束界中，条件数 $\kappa = 10^4$ 时，要将误差减小 100 倍需要几步？

<details><summary>解</summary>

收束因子 $\rho = \frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1} \approx \frac{99}{101} \approx 0.98$。

$100 \cdot \rho^k < 1$ → $k > \ln(100)/\ln(1/0.98) \approx 228$ 步。

**ML 关联**：深度网络 Hessian 的条件数大 → 训练慢（二阶方法/预处理的价值）。
</details>

### Q2（中等）
证明 Jacobi 预处理（$M = \text{diag}(A)$）总能减小条件数（或至少不增大）。

<details><summary>解</summary>

$M^{-1}A$ 归一化对角线为 1。对 SPD 矩阵，Jacobi 预处理后特征值集中在 1 附近。但**不总是**减小条件数（有反例）。更好的是块 Jacobi / 不完全 Cholesky。
</details>

### Q3（中等）
谱方法 vs 有限元：对解析解的 PDE，哪种精度更高？

<details><summary>解</summary>

谱方法：指数收敛 $O(e^{-cn})$（Chebyshev 展开）。
有限元（$p$ 阶）：代数收敛 $O(h^p)$。

**解析解 → 谱方法远优**。但间断解 → 谱方法 Gibbs 现象，FEM 更鲁棒。
</details>

### Q4（开放）
Fourier Neural Operator (FNO) 如何用神经网络学习 PDE 解算子？

<details><summary>提示</summary>

FNO (Li et al. 2021)：输入函数 → FFT → 频域线性变换 → IFFT → 非线性激活。本质是**可微的谱方法**，用 NN 学频域系数。

优势：参数共享、可泛化到不同分辨率。与 FEM 互补：FNO 快但不精确，FEM 精确但慢。
</details>

### Q5（开放）
预处理技术如何应用于深度学习的二阶优化（K-FAC）？

<details><summary>提示</summary>

K-FAC (Martens & Grosse)：用 Kronecker 分解近似 Fisher 信息矩阵 $F \approx A \otimes B$，$F^{-1} \approx A^{-1} \otimes B^{-1}$。

这本质是**块预处理**：把大矩阵的逆分解为小矩阵 Kronecker 积的逆。类似不完全 Cholesky 的思想。
</details>
