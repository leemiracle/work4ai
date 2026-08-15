# 物理 · Neural Operators 深挖（FNO / DeepONet）

> **博士级**：FNO 和 DeepONet 的数学 + 应用。

## 一、为什么需要 Neural Operator

**PINN**：参数化解（一个网络解一个 PDE）。
**Neural Operator**：学**算子**——一族 PDE 的解。

形式：$\mathcal{G}: a(x) \mapsto u(x)$，输入系数函数 $a$，输出解 $u$。

## 二、DeepONet（Lu 2021）

### 2.1 架构

基于 Chen 1995 **Universal Approximation Theorem for Operators**。

```
branch net: 处理输入函数 a 的采样点
trunk net: 处理输出坐标 y
输出: G(a)(y) = Σ_k branch_k(a) · trunk_k(y)
```

### 2.2 数学

$$\mathcal{G}(a)(y) \approx \sum_{k=1}^p b_k(a) \cdot t_k(y)$$

### 2.3 优势 / 劣势

- ✅ 理论基础强
- ❌ 需要传感器位置固定

## 三、Fourier Neural Operator（Li 2021）

### 3.1 核心：频域卷积

PDE 的算子大多在频域稀疏（高频快速衰减）。

**FNO 层**：

```
v_{t+1} = σ(W v_t + K(v_t))
              ↑
         频域卷积
```

**K(v)**：

1. **FFT**：$v \to \hat{v}$
2. 截断高频（保留 $k_{max}$ 模式）
3. 学习频率权重
4. **IFFT**：回到空间域

### 3.2 数学

$$\mathcal{K}(\phi)(v) = \mathcal{F}^{-1}(R_\phi \cdot \mathcal{F}(v))$$

其中 $R_\phi$ 是可学习频率权重矩阵。

### 3.3 优势

- ✅ 分辨率无关（train 低分辨率，test 高分辨率）
- ✅ 比 CNN 快 1000×
- ✅ 通用性

## 四、性能对比

| 方法 | Burgers 误差 | Darcy 误差 | Navier-Stokes（长时）|
|---|---|---|---|
| FCN | 1.5e-2 | 5e-2 | 失败 |
| PINN | — | — | 失败（stiff）|
| DeepONet | 1e-3 | 1e-2 | 中 |
| FNO | **5e-4** | **8e-3** | 好 |
| Factorized FNO | 类似 | 类似 | 更快 |

## 五、应用案例

### 5.1 天气预报（FourCastNet）

NVIDIA 用 FNO 做全球天气预报——比经典数值快 1000×。

### 5.2 多孔介质（地下水流）

油田模拟 / 核废料处理。

### 5.3 设计优化

机翼设计 / 反应堆设计。

## 六、当前前沿

- **Factorized FNO**（2D/3D 高效）
- **Geometry-aware NO**（弯曲域）
- **Physics-Informed NO**（PINN + NO 混合）
- **Operator Transformer**（结合注意力）

## 七、博士级练习

1. 实现 FNO（PyTorch 50 行）
2. 在 Burgers 方程对比 PINN
3. 研究截断频率对精度影响

## 八、关键引用

- Li 2021 *ICLR* FNO
- Lu 2021 *DeepONet*（多论文）
- Kovachki 2023 综述 *Neural Operators*
