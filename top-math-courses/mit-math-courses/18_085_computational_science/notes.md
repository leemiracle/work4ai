# MIT 18.085 · 费曼三层讲透：计算科学与工程

> **教材**：Strang, *Computational Science and Engineering* (2007) ★
> **视频**：[OCW Strang 18.085](https://ocw.mit.edu/courses/18-085-computational-science-and-engineering-i-fall-2008/)
> **特色**：Strang 的应用数学——**图拉普拉斯 / FFT / 有限元**，用线代统一

---

## 🧠 直觉层

| 概念 | 比喻 |
|---|---|
| **差分（finite difference）** | "用离散格点近似连续导数"——$\frac{du}{dx} \approx \frac{u_{i+1}-u_i}{\Delta x}$ |
| **边值问题离散化** | "把微分方程变成矩阵方程 $Au=f$"——PDE → 线代 |
| **图拉普拉斯 $L = D - A$** | "图的'二阶导'"——度矩阵减邻接矩阵，描述图上的扩散 |
| **FFT** | "把 $O(n^2)$ 的 DFT 加速到 $O(n\log n)$"——分治的胜利 |
| **有限元（FEM）** | "把连续域切成小片，每片用简单函数近似"——分段多项式 |
| **Krylov 子空间** | "用 $\{b, Ab, A^2b,\dots\}$ 逼近 $A^{-1}b$"——迭代法根基 |

> **一句话总结**：**18.085 = "用线代统一应用数学"**。Strang 的核心洞见：**微分方程 = 矩阵方程，差分 = 矩阵，图拉普拉斯 = 二阶差分矩阵**。

---

## 🧮 数学层

### 1. 差分矩阵 ★

**一阶差分**（forward）：
$$\frac{u_{i+1} - u_i}{\Delta x} \approx u'(x_i) \quad \Leftrightarrow \quad D_+ = \frac{1}{\Delta x}\begin{pmatrix} -1 & 1 & & \\ & -1 & 1 & \\ & & \ddots & \ddots \end{pmatrix}$$

**二阶差分**（centered）：
$$\frac{u_{i+1} - 2u_i + u_{i-1}}{\Delta x^2} \approx u''(x_i) \quad \Leftrightarrow \quad D_2 = \frac{1}{\Delta x^2}\begin{pmatrix} -2 & 1 & & \\ 1 & -2 & 1 & \\ & \ddots & \ddots & \ddots \end{pmatrix}$$

> **这是所有二阶 PDE（热方程、波方程、Laplace）离散化的核心矩阵**。

### 2. 边值问题 → 矩阵方程 ★★

泊松方程 $-u'' = f$，边界 $u(0) = u(1) = 0$。离散化：

$$-\frac{u_{i+1} - 2u_i + u_{i-1}}{\Delta x^2} = f_i$$

矩阵形式：$K\mathbf{u} = \mathbf{f}$，$K$ 是三对角正定矩阵（$K = D_2$ 带边界）。

**Strang 的洞见**：$K$ 就是**刚度矩阵**（stiffness matrix），$K\mathbf{u} = \mathbf{f}$ 是所有 FEM 的核心方程。

### 3. 图拉普拉斯 ★★★

对图 $G = (V, E)$：
$$L = D - A$$
- $D$：度矩阵（对角）
- $A$：邻接矩阵

**性质**：
- $L$ 半正定，$\mathbf{1}^T L \mathbf{1} = 0$（连通图的最小特征值）
- $L = B^T B$（$B$ = 关联矩阵 / incidence matrix）
- **第二小特征值 $\lambda_2$（Fiedler 值）** = 图的"连通性"度量

**ML 关联**：
- **谱聚类**：用 $L$ 的特征向量分割图
- **GNN**：图拉普拉斯正则化（$L$ 是图上的"拉普拉斯算子"）
- **Diffusion models on graphs**：热扩散在图上的推广

### 4. 傅里叶矩阵与 FFT ★★

$$F_n = \begin{pmatrix} \omega^{jk} \end{pmatrix}_{j,k=0}^{n-1}, \quad \omega = e^{-2\pi i/n}$$

**DFT**：$\hat{\mathbf{u}} = F_n \mathbf{u}$，代价 $O(n^2)$。

**FFT**（Cooley-Tukey）：分治
$$F_{2n} = \begin{pmatrix} I & D \\ I & -D \end{pmatrix}\begin{pmatrix} F_n & 0 \\ 0 & F_n \end{pmatrix}P$$

代价 $O(n\log n)$。

**ML 关联**：
- **卷积 = 频域乘法**：$\text{conv}(a,b) = \text{IFFT}(\text{FFT}(a) \cdot \text{FFT}(b))$
- CNN 的快速实现

### 5. 有限元（FEM）入门

**弱形式**：找 $u \in V$ s.t. $\int u'v' = \int fv$, $\forall v \in V$。

**离散**：取有限维子空间 $V_h$（分段线性），基函数 $\phi_i$。

$$\sum_j u_j \int \phi_j' \phi_i' = \int f\phi_i \quad \Rightarrow \quad K\mathbf{u} = \mathbf{f}$$

**ML 关联**：神经网络的函数空间视角——NN 是另一种"基函数逼近"。

### 6. Krylov 子空间迭代法

$$\mathcal{K}_k(A, b) = \text{span}\{b, Ab, A^2b, \dots, A^{k-1}b\}$$

CG / GMRES 在 $\mathcal{K}_k$ 中找近似解。详见 [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/notes.md) 第 5 节。

**ML 关联**：attention 的线性近似用 Krylov 思想。

---

## 💻 代码层

```python
import numpy as np
import matplotlib.pyplot as plt

# 图拉普拉斯: 谱聚类示例
def spectral_clustering(W, k):
    """W = 相似度矩阵, k = 簇数"""
    D = np.diag(W.sum(axis=1))
    L = D - W  # 图拉普拉斯
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    # 用前 k 个特征向量做 k-means
    features = eigenvectors[:, :k]
    # ... k-means on features
    return features

# 差分法解泊松方程 -u'' = f
n = 100; dx = 1.0 / (n + 1)
x = np.linspace(0, 1, n + 2)
f = np.sin(np.pi * x[1:-1])  # 源项
# 三对角矩阵 K (二阶差分)
K = np.diag(-2*np.ones(n)) + np.diag(np.ones(n-1), 1) + np.diag(np.ones(n-1), -1)
K /= -dx**2  # 注意符号
u = np.linalg.solve(K, f)
u_full = np.concatenate([[0], u, [0]])  # 加边界
# 解析解: u(x) = sin(πx)/π²
u_exact = np.sin(np.pi * x) / np.pi**2
print(f"最大误差: {np.max(np.abs(u_full - u_exact)):.6f}")

# FFT 验证: 卷积 = 频域乘积
a = np.random.randn(1024); b = np.random.randn(1024)
conv_direct = np.convolve(a, b)
conv_fft = np.fft.ifft(np.fft.fft(a, 2048) * np.fft.fft(b, 2048)).real
print(f"FFT 卷积误差: {np.max(np.abs(conv_direct - conv_fft[:len(conv_direct)])):.2e}")
```

---

## ⚠️ 不足层

| 局限 | 说明 |
|---|---|
| **低阶差分精度低** | 一阶差分 $O(\Delta x)$，需高阶格式或 FEM |
| **显式方法对 stiff PDE 不稳定** | 热方程显式需 $\Delta t \leq \Delta x^2 / 2$（CFL 条件）|
| **FEM 网格生成复杂** | 3D 不规则区域网格生成是工程难题 |
| **谱聚类对大图慢** | 特征分解 $O(n^3)$，需近似（Lanczos）|
| **FFT 要求信号长度 2 的幂** | 非 2 幂需 zero-padding 或混合 FFT |

---

## 🔬 应用层

1. **图拉普拉斯 → 谱聚类 / GNN 正则化**
2. **FFT → CNN 卷积加速**
3. **Krylov → attention 线性近似**
4. **泊松方程 → 图半监督学习**（Zhu-Ghahramani-Lafferty 2003）
5. **热方程 → diffusion model 的 PDE 根基**，见 [ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/) 和 [Princeton MAT 322 PDE](../../princeton-math-courses/mat322_pde/)

---

## 🆕 2024-2026 最新研究

- **GNN 与图拉普拉斯**：ChebNet / GCN = 图上的谱卷积，与 FFT 深度联系
- **神经 PDE 求解器**：用 PINN（物理信息神经网络）解 PDE，与传统 FEM 互补
- **Diffusion on graphs**：图上的 score-based 生成
- **线性 attention**：用 Krylov / 核技巧把 attention 从 $O(n^2)$ 降到 $O(n)$

---

## 📚 章节结构对照（Strang CSE）

| 章 | 主题 | 重要性 |
|---|---|---|
| 1 | A=CR 与四个子空间复习 | ★ |
| 2 | **差分矩阵与一阶/二阶差分** | ★★★ |
| 3 | **边值问题离散化** | ★★★ |
| 4 | **图拉普拉斯** | ★★★ |
| 5 | FFT | ★★ |
| 6 | 有限元入门 | ★★ |
| 7 | Krylov 迭代法 | ★★ |

---

## 与 work4ai 讲透系列的交叉

- **讲透 GNN**：第 4 章（图拉普拉斯）+ 谱聚类
- **讲透 CNN**：第 5 章（FFT = 卷积加速）
- **讲透 diffusion**：第 3 章（热方程离散化）→ [ETH 401-3651 SDE](../../eth-math-courses/e401_3651_numerical_sde/)
- **讲透 attention 加速**：第 7 章（Krylov）→ [UT Austin M 383E](../../ut-austin-math-courses/m383e_numerical_linear_algebra/)
