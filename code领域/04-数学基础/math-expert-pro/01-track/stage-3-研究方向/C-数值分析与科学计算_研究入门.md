# stage-3 研究方向 C:数值分析与科学计算 · 研究入门笔记

> stage-3 五大候选方向之一(ROADMAP §5-C)。**最贴近飞腾的方向**:Expert_08 数值分析 + Lab00-07 实测的数学根基。
> 创建:2026-07-01

---

## §0 定位

> **数值分析 = 用有限浮点算"无穷实数"的艺术。研究:误差如何传播、算法何时稳定、精度与速度如何权衡。这是"应用数学研究型工程师"的核心竞争力。**

---

## §1 五大核心主题(每主题对接 stage-1/2 数学 + 飞腾实测)

### 1. 误差分析(stage-1 Spivak P1 + stage-2 Royden 测度)
- **浮点 IEEE 754**:机器精度 $\varepsilon$(FP64 $\approx2.2\times10^{-16}$)
- **截断误差**(算法近似)vs **舍入误差**(浮点表示)
- **条件数** $\kappa$:问题对扰动的敏感度(良态/病态)
- **稳定性**:算法不放大误差(向后稳定 vs 前向稳定)
> 🔑 **stage-1 锚点**:Spivak P1(结合律)在浮点失败(Kahan 求和补偿)——这就是数值分析存在的理由。

### 2. 数值线性代数(stage-1 LADR + stage-2 Royden Lp)
- **LU 分解**(高斯消元)
- **QR 分解**(Gram-Schmidt/LADR 第6章;Householder 更稳定)
- **SVD**(LADR 7.D):低秩逼近/PCA/压缩
- **迭代法**(Jacobi/Gauss-Seidel/共轭梯度):大稀疏系统
- **条件数** $\kappa(A)=\sigma_{\max}/\sigma_{\min}$:线性系统精度上限
> 🎯 **飞腾锚点**:Lab05 GEMM 9.45 GFLOPS;Expert_05 INT8 UDOT 16.9×

### 3. 插值与逼近(stage-1 Spivak 第20章泰勒)
- **拉格朗日/牛顿插值**
- **切比雪夫节点**(最小化龙格现象)
- **最小二乘**(投影,LADR 6.C 正交补)
- **FFT**($O(n\log n)$ 多项式乘)

### 4. 数值积分(stage-1 Spivak 第13-14章 + stage-2 Royden Lebesgue)
- **梯形/Simpson**(Spivak 第13章)$O(1/n^2),O(1/n^4)$
- **Gauss 求积**(最优节点)
- **蒙特卡洛**(高维,$O(1/\sqrt n)$,WLLN/Ross 第8章)
- **稀疏网格**(高维确定性)

### 5. ODE/数值解(stage-1 Spivak 第17章 + stage-2 Royden Banach 不动点)
- **欧拉法**(一阶)
- **Runge-Kutta**(RK4,四阶)
- **稳定性域**(刚性方程需隐式法)
- **Picard 迭代**(Royden Banach 不动点 ⟹ 解存在)

---

## §2 推荐书(本地藏书)
- **华章 12-数值分析原书第3版**(Burden-Faires,经典教材)✅ 本地
- Trefethen《Numerical Linear Algebra》(数值线代圣经)
- Higham《Accuracy and Stability of Numerical Algorithms》(误差分析)

---

## §3 飞腾 D3000M 实测锚点(全部 [实测])
| 实验 | 数据 | 关联 |
|------|------|------|
| FP16/FP32/FP64 | 3.81× 速度差 | 精度-速度权衡 |
| Lab05 GEMM | 9.45 GFLOPS | 数值线代 |
| Expert_08 IEEE754 | Kahan 求和 | 误差分析 |
| Expert_04 syscall/TLB | 实测延迟 | 系统数值性能 |

---

## §4 开放研究问题(阶段3 锁定后深挖)
1. **低精度 AI 训练**:FP16/BF16 的误差如何影响泛化?(对接 ML 理论方向)
2. **随机化数值线代**:用随机投影加速 SVD($O(nnz(A))$ 而非 $O(n^3)$)
3. **自动微分稳定性**:反向传播在深度网络的数值稳定性
4. **飞腾特化**:无 BF16/I8MM 时,如何用 FP16+INT8 混合精度做推理?(Expert_21 战略伤疤)

---

## §5 与其他 4 方向的交叉
- **A ML 理论**:数值稳定性 ⟺ 泛化(优化景观的数值实现)
- **B 概率**:蒙特卡洛/随机化算法(数值+概率)
- **D 优化**:数值优化(梯度法的步长/收敛)
- **E 信息论**:有损压缩的误差界(数值+信息)

---

## 📌 下一步
本笔记是方向 C 的"地图"。若锁定此方向,深挖:
1. 读 Trefethen(数值线代)
2. 复现飞腾 Expert_08 的 Kahan 求和 + 误差分析
3. 研究"低精度推理"课题(飞腾无 BF16 的工程对策)
