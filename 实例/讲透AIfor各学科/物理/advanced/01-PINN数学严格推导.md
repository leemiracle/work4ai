# 物理 · PINN 数学严格推导

> **博士级**：PINN 的核心思想 + 数学严格化 + 失败模式。

## 一、PINN 的核心思想

经典数值方法（FEM/FDM）：离散化 PDE。
**PINN**：把 PDE 作为 loss，神经网络参数化解。

## 二、数学形式

### 2.1 一般 PDE

$$\mathcal{N}[u(x)] = 0, \quad x \in \Omega$$
$$u(x) = g(x), \quad x \in \partial\Omega$$

### 2.2 PINN 损失

神经网络 $u_\theta(x)$ 近似解。loss：

$$\mathcal{L}(\theta) = \underbrace{\frac{1}{N_r}\sum_i |\mathcal{N}[u_\theta(x_i)]|^2}_{\mathcal{L}_{PDE}} + \lambda \underbrace{\frac{1}{N_b}\sum_j |u_\theta(x_j) - g(x_j)|^2}_{\mathcal{L}_{BC}}$$

- $\mathcal{L}_{PDE}$：内部点 PDE 残差
- $\mathcal{L}_{BC}$：边界条件
- 自动微分（autograd）算 $\mathcal{N}[u_\theta]$

## 三、收敛性理论

### 3.1 NTk 视角

PINN 在无限宽极限近似线性模型（**Neural Tangent Kernel**）：

$$u_\theta(x) \approx u_{\theta_0}(x) + \langle \nabla_\theta u, \Theta^{-1} r \rangle$$

其中 $\Theta$ 是 NTK。

### 3.2 误差分解

$$\|u - u_\theta\| \leq \underbrace{\epsilon_{approx}}_{\text{网络容量}} + \underbrace{\epsilon_{opt}}_{\text{优化}} + \underbrace{\epsilon_{gen}}_{\text{泛化}}$$

## 四、失败模式

| 失败 | 原因 | 解药 |
|---|---|---|
| **stiff PDE** | 多尺度 | causal training / Fourier feature |
| **尖锐边界层** | 梯度消失 | hp-VPINN |
| **优化局部最小** | loss landscape 复杂 | curriculum / 多 start |

## 五、关键变体

- **VPINN**：变分形式（弱解）
- **hp-VPINN**：多域
- **SA-PINN**：自适应权重
- **PINN-SR**：稀疏回归发现 PDE

## 六、博士级练习

1. 推导 PINN 在 Burgers 方程上的 loss
2. 实现 PINN 解 1D 热传导（PyTorch 50 行）
3. 分析 PINN 在 stiff PDE 上的失败（数值实验）

## 关键引用

- Raissi 2019 *J Comput Phys*
- Karniadakis 2021 *Nat Rev Phys* 综述
- Wang 2022 NTK 视角
