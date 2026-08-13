# MIT 18.085 · 习题集

---

### Q1.1（基础）
对二阶差分矩阵 $K_3 = \begin{pmatrix} 2 & -1 & 0 \\ -1 & 2 & -1 \\ 0 & -1 & 2 \end{pmatrix}$，求特征值和特征向量。

<details><summary>解</summary>

特征值：$\lambda_k = 2 - 2\cos(k\pi/4)$, $k=1,2,3$ → $\lambda = 2-\sqrt{2}, 2, 2+\sqrt{2}$。

特征向量：$\sin(jk\pi/4)$——**正弦函数的离散版**！

> 这是 **DST（离散正弦变换）** 的来源，也是谱方法的基础。
</details>

### Q1.2（中等）
用差分法离散化 $-u'' = \delta(x - 1/2)$（$u(0)=u(1)=0$），解释 $K^{-1}$ 的物理意义。

<details><summary>解</summary>

$K\mathbf{u} = \mathbf{e}_{n/2}$（源在中点）。$\mathbf{u} = K^{-1}\mathbf{e}_{n/2}$ = $K^{-1}$ 的第 $n/2$ 列。

**物理意义**：$K^{-1}$ 是**离散 Green 函数**——在点 $j$ 放单位源，在点 $i$ 的响应。连续极限下 $K^{-1}$ → Green 函数 $G(x,y) = \min(x,y)(1-\max(x,y))$。

**ML 关联**：核方法的核矩阵 = Green 函数（RKHS 理论）。
</details>

### Q1.3（中等 — 图拉普拉斯）
对完全图 $K_4$（4 个顶点，所有边相连），求图拉普拉斯 $L$ 的特征值。

<details><summary>解</summary>

$L = 3I - (J - I) = 4I - J$（$J$ = 全 1 矩阵）。特征值：$0$（对应 $\mathbf{1}$），$4, 4, 4$（三重）。

$\lambda_2 = 4 > 0$ → 图连通。完全图的代数连通性最大。

**ML 关联**：谱聚类用 $\lambda_2$ 衡量图的可分割性。
</details>

### Q1.4（开放）
为什么 FFT 把 $O(n^2)$ 的 DFT 降到 $O(n\log n)$？这对 CNN 意味着什么？

<details><summary>提示</summary>

FFT 利用 $F_{2n}$ 的分块结构（$F_{2n}$ = 偶数项 $F_n$ + 奇数项 $D F_n$），递归分治 → $T(n) = 2T(n/2) + O(n) = O(n\log n)$。

CNN 的大核卷积可用 FFT 加速：$\text{conv}(a,b) = \text{IFFT}(\text{FFT}(a)\cdot\text{FFT}(b))$。当核宽度 $> \log n$ 时 FFT 比直接卷积快。
</details>

### Q1.5（开放 — PDE & Diffusion）
热方程 $\partial_t u = \Delta u$ 的离散化与扩散模型的前向过程有何关系？

<details><summary>提示</summary>

热方程 $\partial_t u = \Delta u$ 的解是 $u(x,t) = (G_t * u_0)(x)$（高斯核卷积）。这等价于在数据上加高斯噪声——**正是 DDPM 前向过程的连续极限**。

$u(x, T)$（$T$ 大）→ 常数（"均匀化"），对应扩散模型的纯噪声。反向过程 = 求反向热方程（不适定问题，需 score 正则化）。

详见 [ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/) 和 [Princeton MAT 322 PDE](../../princeton-math-courses/mat322_pde/)。
</details>

### Q1.6（开放）
PINN（物理信息神经网络）与 FEM 相比有什么优劣？

<details><summary>提示</summary>

PINN 把 PDE 残差作为损失项，用神经网络 $u_\theta(x)$ 近似解。

优势：无需网格、高维问题可处理、逆问题（参数估计）方便。
劣势：训练慢、收敛无保证、精度不如 FEM。

2024 进展：PINN + 算子学习（DeepONet, Fourier Neural Operator）处理参数化 PDE。⚠️ 具体精度对比需查最新文献。
</details>
