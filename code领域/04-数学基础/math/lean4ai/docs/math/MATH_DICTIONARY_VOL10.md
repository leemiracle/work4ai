# 数学知识词典 - 第十卷：拓扑群、李群与微分方程
## Mathematics Subject Dictionary - Volume 10: Topological Groups, Lie Groups and ODEs

**MSC分类**: 22-XX, 34-XX  
**版本**: 2.1  
**更新日期**: 2025-03-26  

---

## 目录

1. [22-XX 拓扑群与李群 (Topological Groups, Lie Groups)](#22-xx-拓扑群与李群-topological-groups-lie-groups)
2. [34-XX 常微分方程 (Ordinary Differential Equations)](#34-xx-常微分方程-ordinary-differential-equations)

---

## 22-XX 拓扑群与李群 (Topological Groups, Lie Groups)

### 定义 I.22.1 (拓扑群 / Topological Group)

**定义**: **拓扑群** $G$ 是一个群，同时是拓扑空间，使得群运算

$$\mu: G \times G \to G, \quad (x, y) \mapsto xy$$
$$\iota: G \to G, \quad x \mapsto x^{-1}$$

是连续映射。若拓扑是Hausdorff的，称 $G$ 为 **Hausdorff拓扑群**。

**基本性质**:
- 左平移 $L_g: x \mapsto gx$ 和右平移 $R_g: x \mapsto xg$ 是同胚
- 逆映射 $\iota$ 是同胚
- 单位元 $e$ 的邻域系决定整个拓扑

---

### 定义 I.22.2 (李群 / Lie Group)

**定义**: **李群** $G$ 是一个光滑流形，同时是一个群，使得群运算 $\mu$ 和 $\iota$ 是光滑映射。

**等价定义**: 李群是光滑流形上的群结构，使得乘法 $(g, h) \mapsto gh^{-1}$ 光滑。

**经典例子**:
- $(\mathbb{R}^n, +)$：加法群
- $(\mathbb{C}^\times, \times)$：非零复数乘法群
- $GL_n(\mathbb{R})$：一般线性群
- $SL_n(\mathbb{R})$：特殊线性群（行列式为1）
- $O(n), SO(n)$：正交群，特殊正交群
- $U(n), SU(n)$：酉群，特殊酉群
- $Sp(n)$：辛群

---

### 定义 I.22.3 (李代数 / Lie Algebra)

**定义**: **李代数** $\mathfrak{g}$ 是域 $\mathbb{F}$ 上的向量空间，配备双线性映射

$$[\cdot, \cdot]: \mathfrak{g} \times \mathfrak{g} \to \mathfrak{g}$$

满足：
1. **反对称性**: $[X, Y] = -[Y, X]$
2. **Jacobi恒等式**: $[X, [Y, Z]] + [Y, [Z, X]] + [Z, [X, Y]] = 0$

**李群的李代数**: 李群 $G$ 在单位元处的切空间 $T_e G$，配备李括号

$$[X, Y] = \left.\frac{d}{dt}\right|_{t=0} (dL_{\exp(tX)})_e Y$$

等价地，通过左不变向量场的交换子定义。

---

### 定理 22.1 (指数映射 / Exponential Map)

**定理**: 设 $G$ 是李群，$\mathfrak{g}$ 是其李代数。**指数映射**

$$\exp: \mathfrak{g} \to G, \quad X \mapsto \gamma_X(1)$$

其中 $\gamma_X$ 是满足 $\gamma_X(0) = e$，$\dot{\gamma}_X(0) = X$ 的单参数子群，具有以下性质：
1. $\exp$ 是光滑映射
2. $\exp(0) = e$
3. $(d\exp)_0 = \text{id}: \mathfrak{g} \to T_e G$
4. $\exp$ 在 $0$ 附近是局部微分同胚
5. $\exp(tX) = \gamma_X(t)$（对所有 $t$）

---

### 定理 22.2 (Baker-Campbell-Hausdorff公式 / BCH Formula)

**定理**: 在 $\exp$ 的局部逆的坐标下，群乘法由

$$\exp(X) \exp(Y) = \exp\left(X + Y + \frac{1}{2}[X,Y] + \frac{1}{12}[X,[X,Y]] - \frac{1}{12}[Y,[X,Y]] + \cdots\right)$$

给出，其中级数只涉及李括号的迭代组合。

**意义**: 李群在单位元附近的群结构完全由李代数的括号结构决定。

---

### 定义 I.22.4 (单参数子群 / One-Parameter Subgroup)

**定义**: 李群 $G$ 的 **单参数子群** 是光滑群同态

$$\gamma: \mathbb{R} \to G$$

**性质**: 对任意 $X \in \mathfrak{g}$，$\gamma_X(t) = \exp(tX)$ 是单参数子群，且所有单参数子群都有此形式。

---

### 定理 22.3 (李对应 / Lie Correspondence)

**定理**: 在以下对应下，李群与李代数之间存在密切联系：

| 李群 $G$ | 李代数 $\mathfrak{g}$ |
|----------|----------------------|
| 李子群 | 李子代数 |
| 正规子群 | 理想 |
| 李群同态 | 李代数同态 |
| 覆盖空间 | 中心扩张 |

**精确陈述**: 
1. 李群同态 $\phi: G \to H$ 完全由 $(d\phi)_e: \mathfrak{g} \to \mathfrak{h}$ 决定
2. 单连通李群由其李代数唯一确定
3. 连通李群的中心 = $\mathfrak{g}$ 的中心的指数

---

### 定义 I.22.5 (伴随表示 / Adjoint Representation)

**定义**: 李群 $G$ 的 **伴随表示** $\text{Ad}: G \to GL(\mathfrak{g})$ 定义为

$$(\text{Ad}_g)(X) = \left.\frac{d}{dt}\right|_{t=0} (g \exp(tX) g^{-1})$$

李代数的 **伴随表示** $\text{ad}: \mathfrak{g} \to \mathfrak{gl}(\mathfrak{g})$ 定义为

$$(\text{ad}_X)(Y) = [X, Y]$$

**关系**: $(d\text{Ad})_e = \text{ad}$

---

### 定义 I.22.6 ( Killing形式 / Killing Form)

**定义**: 李代数 $\mathfrak{g}$ 的 **Killing形式** 是双线性型

$$B(X, Y) = \text{tr}(\text{ad}_X \circ \text{ad}_Y)$$

**性质**:
1. 对称性: $B(X, Y) = B(Y, X)$
2. 结合性: $B([X, Y], Z) = B(X, [Y, Z])$
3. $\text{Ad}$-不变性: $B(\text{Ad}_g X, \text{Ad}_g Y) = B(X, Y)$

**定理** (Cartan判别法): 有限维李代数 $\mathfrak{g}$ 是半单的当且仅当其Killing形式非退化。

---

### 定义 I.22.7 (紧李群 / Compact Lie Group)

**定义**: 李群 $G$ 是 **紧李群**，如果作为拓扑空间它是紧的。

**例子**:
- $SO(n)$, $SU(n)$, $Sp(n)$（紧）
- $GL_n(\mathbb{R})$, $SL_n(\mathbb{R})$（非紧）

**Peter-Weyl定理**: 设 $G$ 是紧李群。则 $L^2(G)$ 分解为有限维不可约表示的直和。

---

### 定理 22.4 (紧李群的结构 / Structure of Compact Lie Groups)

**定理**: 设 $G$ 是连通紧李群。则：
1. $G$ 的李代数 $\mathfrak{g}$ 有分解 $\mathfrak{g} = \mathfrak{z} \oplus [\mathfrak{g}, \mathfrak{g}]$，其中 $\mathfrak{z}$ 是中心
2. $G = (T \times G_{ss})/\Gamma$，其中 $T$ 是环面，$G_{ss}$ 是半单紧李群，$\Gamma$ 是有限群
3. $G$ 的通用覆盖 $\tilde{G} = \mathbb{R}^n \times G_1 \times \cdots \times G_k$，其中 $G_i$ 是单连通单李群

---

### 定义 I.22.8 (根系统 / Root System)

**定义**: 欧氏空间 $V$ 中的 **根系统** $\Phi$ 是满足以下条件的有限向量集：
1. $\Phi$ 有限，$0 \notin \Phi$，$\text{span}(\Phi) = V$
2. 对任意 $\alpha \in \Phi$，$s_\alpha(\Phi) = \Phi$（反射不变性），其中 $s_\alpha(x) = x - \frac{2(x,\alpha)}{(\alpha,\alpha)}\alpha$
3. 对任意 $\alpha, \beta \in \Phi$，$\frac{2(\beta,\alpha)}{(\alpha,\alpha)} \in \mathbb{Z}$（晶体学条件）

**根系与李代数**: 半单复李代数 $\mathfrak{g}$ 的根系 $\Phi(\mathfrak{g}, \mathfrak{h})$ 由关于Cartan子代数 $\mathfrak{h}$ 的根空间分解给出。

---

### 定理 22.5 (复半单李代数的分类 / Classification of Complex Semisimple Lie Algebras)

**定理**: 复半单李代数由其Dynkin图完全分类。不可约情况对应：
- **经典李代数**: $A_n (n \geq 1)$, $B_n (n \geq 2)$, $C_n (n \geq 3)$, $D_n (n \geq 4)$
- **例外李代数**: $G_2$, $F_4$, $E_6$, $E_7$, $E_8$

**与李群的对应**:
| 李代数 | 对应李群 |
|--------|----------|
| $A_n$ | $SL_{n+1}(\mathbb{C})$ |
| $B_n$ | $SO_{2n+1}(\mathbb{C})$ |
| $C_n$ | $Sp_{2n}(\mathbb{C})$ |
| $D_n$ | $SO_{2n}(\mathbb{C})$ |

---

### 定义 I.22.9 (表示 / Representation)

**定义**: 李群 $G$ 的 **（有限维）表示** 是群同态

$$\pi: G \to GL(V)$$

其中 $V$ 是有限维复向量空间。

**李代数表示**: 李代数 $\mathfrak{g}$ 的表示是李代数同态

$$\rho: \mathfrak{g} \to \mathfrak{gl}(V)$$

**微分对应**: $(d\pi)_e = \rho$

---

### 定理 22.6 (最高权定理 / Highest Weight Theorem)

**定理**: 设 $\mathfrak{g}$ 是复半单李代数。则：
1. 不可约有限维表示与支配整最高权 $\lambda$ 一一对应
2. 每个不可约表示 $V_\lambda$ 有权空间分解 $V_\lambda = \bigoplus_{\mu} V_\mu$
3. 权 $\mu$ 的重数由Kostant公式或Freudenthal公式给出

**Weyl特征标公式**:

$$\text{ch}(V_\lambda) = \frac{\sum_{w \in W} \epsilon(w) e^{w(\lambda + \rho)}}{\sum_{w \in W} \epsilon(w) e^{w(\rho)}}$$

其中 $W$ 是Weyl群，$\rho = \frac{1}{2}\sum_{\alpha > 0} \alpha$。

---

### 定义 I.22.10 (齐性空间 / Homogeneous Space)

**定义**: 设 $G$ 是李群，$H$ 是闭子群。**齐性空间** $G/H$ 是左陪集空间，配备商拓扑和唯一的流形结构使得投影 $G \to G/H$ 是光滑淹没。

**例子**:
- $SO(n)/SO(n-1) \cong S^{n-1}$
- $SL_n(\mathbb{R})/SO(n) \cong$ 正定对称矩阵空间
- $GL_n(\mathbb{C})/U(n) \cong$ 正定Hermite矩阵空间

---

### 定理 22.7 (齐性空间上的不变测度 / Invariant Measures on Homogeneous Spaces)

**定理**: 设 $G$ 是局部紧群，$H$ 是闭子群。$G/H$ 上存在 $G$-不变测度当且仅当

$$|\det(\text{Ad}_h)|_G = |\det(\text{Ad}_h)|_H, \quad \forall h \in H$$

**特例**: 若 $G$ 紧或 $H$ 紧，不变测度总存在。

---

### 定义 I.22.11 (局部紧Abel群 / Locally Compact Abelian Group)

**定义**: **局部紧Abel群** (LCA群) 是同时是局部紧拓扑空间和Abel群的拓扑群。

**Pontryagin对偶定理**: LCA群 $G$ 的对偶 $\hat{G}$（连续特征群）满足 $\hat{\hat{G}} \cong G$。

---

### 参考文献 (22-XX)
1. Helgason, S., *Differential Geometry, Lie Groups, and Symmetric Spaces*, AMS, 2001
2. Knapp, A.W., *Lie Groups Beyond an Introduction*, Birkhäuser, 2002
3. Humphreys, J.E., *Introduction to Lie Algebras and Representation Theory*, Springer, 1972
4. Bourbaki, N., *Lie Groups and Lie Algebras*, Springer
5. Sepanski, M.R., *Compact Lie Groups*, Springer, 2007
6. Folland, G.B., *A Course in Abstract Harmonic Analysis*, CRC, 1995

---

## 34-XX 常微分方程 (Ordinary Differential Equations)

### 定义 I.34.1 (常微分方程 / Ordinary Differential Equation)

**定义**: **$n$阶常微分方程** 是形如

$$F(x, y, y', y'', \ldots, y^{(n)}) = 0$$

的方程，其中 $F: D \subset \mathbb{R}^{n+2} \to \mathbb{R}$ 是给定函数。

**一阶方程组**: $n$阶方程等价于一阶方程组

$$\mathbf{y}' = \mathbf{f}(x, \mathbf{y})$$

其中 $\mathbf{y} = (y, y', \ldots, y^{(n-1)})^T \in \mathbb{R}^n$。

---

### 定理 34.1 (存在唯一性定理 / Existence and Uniqueness Theorem)

**定理** (Picard-Lindelöf): 设 $\mathbf{f}: D \subset \mathbb{R} \times \mathbb{R}^n \to \mathbb{R}^n$ 连续且关于 $\mathbf{y}$ 满足Lipschitz条件：

$$\|\mathbf{f}(x, \mathbf{y}_1) - \mathbf{f}(x, \mathbf{y}_2)\| \leq L\|\mathbf{y}_1 - \mathbf{y}_2\|$$

则初值问题

$$\mathbf{y}' = \mathbf{f}(x, \mathbf{y}), \quad \mathbf{y}(x_0) = \mathbf{y}_0$$

在某个区间 $|x - x_0| < h$ 上存在唯一解。

**证明**: Picard迭代 $\mathbf{y}_{n+1}(x) = \mathbf{y}_0 + \int_{x_0}^x \mathbf{f}(t, \mathbf{y}_n(t)) dt$ 收敛到唯一解。 □

---

### 定义 I.34.2 (向量场与积分曲线 / Vector Fields and Integral Curves)

**定义**: 光滑流形 $M$ 上的 **向量场** $X$ 是截面 $X: M \to TM$。**积分曲线** 是满足

$$\dot{\gamma}(t) = X(\gamma(t))$$

的曲线 $\gamma: I \to M$。

**流**: 向量场 $X$ 生成 **流** $\phi_t: M \to M$，使得

$$\frac{d}{dt}\bigg|_{t=0} \phi_t(p) = X(p)$$

---

### 定理 34.2 (流的性质 / Properties of Flows)

**定理**: 设 $X$ 是 $M$ 上的完备向量场。则：
1. $\phi_0 = \text{id}_M$
2. $\phi_{t+s} = \phi_t \circ \phi_s$（群性质）
3. $t \mapsto \phi_t(p)$ 是 $X$ 过 $p$ 的积分曲线
4. $\phi_t$ 是微分同胚

**Lie导数**: 对于函数 $f$，

$$(\mathcal{L}_X f)(p) = \left.\frac{d}{dt}\right|_{t=0} f(\phi_t(p)) = X_p(f)$$

---

### 定义 I.34.3 (自治系统 / Autonomous System)

**定义**: **自治系统** 是不显含自变量的微分方程组

$$\frac{d\mathbf{y}}{dt} = \mathbf{f}(\mathbf{y})$$

**平衡点**: 满足 $\mathbf{f}(\mathbf{y}_0) = 0$ 的点 $\mathbf{y}_0$。

**相图**: 解曲线在相空间 $\mathbb{R}^n$ 中的图像。

---

### 定理 34.3 (线性化与稳定性 / Linearization and Stability)

**定理**: 考虑自治系统 $\dot{\mathbf{y}} = \mathbf{f}(\mathbf{y})$，$\mathbf{f}(\mathbf{y}_0) = 0$。设 $A = D\mathbf{f}(\mathbf{y}_0)$。则：

1. **渐近稳定**: 若 $A$ 的所有特征值有负实部，则 $\mathbf{y}_0$ 渐近稳定
2. **不稳定**: 若 $A$ 有特征值有正实部，则 $\mathbf{y}_0$ 不稳定
3. **临界情形**: 若 $A$ 有零实部特征值但无正实部特征值，需更高阶分析

**注**: 这给出了平衡点局部稳定性的线性化判据。

---

### 定义 I.34.4 (Lyapunov函数 / Lyapunov Function)

**定义**: 设 $\mathbf{y}_0$ 是 $\dot{\mathbf{y}} = \mathbf{f}(\mathbf{y})$ 的平衡点。**Lyapunov函数** 是定义在 $\mathbf{y}_0$ 邻域 $U$ 上的函数 $V: U \to \mathbb{R}$，满足：
1. $V(\mathbf{y}_0) = 0$，$V(\mathbf{y}) > 0$ 当 $\mathbf{y} \neq \mathbf{y}_0$
2. $\dot{V}(\mathbf{y}) = \nabla V \cdot \mathbf{f}(\mathbf{y}) \leq 0$ 当 $\mathbf{y} \in U$

---

### 定理 34.4 (Lyapunov稳定性定理 / Lyapunov Stability Theorem)

**定理**: 设 $\mathbf{y}_0$ 是平衡点，$V$ 是Lyapunov函数。
1. **稳定性**: 若 $\dot{V} \leq 0$，则 $\mathbf{y}_0$ 稳定
2. **渐近稳定性**: 若 $\dot{V} < 0$（$\mathbf{y} \neq \mathbf{y}_0$），则 $\mathbf{y}_0$ 渐近稳定

**LaSalle不变性原理**: 若 $\dot{V} \leq 0$，则轨道趋于 $\{\mathbf{y} : \dot{V}(\mathbf{y}) = 0\}$ 的最大不变子集。

---

### 定义 I.34.5 (极限环 / Limit Cycle)

**定义**: **极限环** 是孤立的闭轨道（周期解），即存在邻域不含其他闭轨道。

**稳定性**:
- **稳定极限环**: 附近轨道趋于它
- **不稳定极限环**: 附近轨道远离它
- **半稳定极限环**: 一侧稳定，一侧不稳定

---

### 定理 34.5 (Poincaré-Bendixson定理 / Poincaré-Bendixson Theorem)

**定理**: 设 $\dot{\mathbf{y}} = \mathbf{f}(\mathbf{y})$ 是 $\mathbb{R}^2$ 上的自治系统，$\mathbf{f} \in C^1$。若轨道 $\gamma$ 有界且不趋于平衡点，则 $\gamma$ 的 $\omega$-极限集是周期轨道。

**应用**: 平面系统如果有界区域不含平衡点且有轨道进入，则必有极限环。

---

### 定义 I.34.6 (二维系统的指标 / Index of Planar Systems)

**定义**: 向量场 $\mathbf{f}$ 沿闭曲线 $C$ 的 **指标** (Poincaré索引) 是

$$I_C(\mathbf{f}) = \frac{1}{2\pi} \oint_C d\theta$$

其中 $\theta = \arg(f_1 + if_2)$。

**孤立平衡点的指标**: 若 $\mathbf{y}_0$ 是孤立平衡点，则

$$I(\mathbf{y}_0) = \lim_{r \to 0} I_{\partial B_r(\mathbf{y}_0)}(\mathbf{f})$$

**性质**: 闭轨道内部平衡点指标之和 = 1。

---

### 定义 I.34.7 (分岔 / Bifurcation)

**定义**: 依赖参数 $\mu$ 的系统 $\dot{\mathbf{y}} = \mathbf{f}(\mathbf{y}, \mu)$ 在 $\mu = \mu_0$ 处发生 **分岔**，如果系统的相图拓扑结构在 $\mu_0$ 处发生变化。

**基本分岔类型**:

1. **鞍结分岔** (Saddle-Node): 平衡点产生/消失
   $$\dot{x} = \mu - x^2$$

2. **跨临界分岔** (Transcritical): 稳定性交换
   $$\dot{x} = \mu x - x^2$$

3. **叉形分岔** (Pitchfork): 对称性破缺
   $$\dot{x} = \mu x - x^3$$

4. **Hopf分岔**: 平衡点失稳，产生极限环

---

### 定理 34.6 (Hopf分岔定理 / Hopf Bifurcation Theorem)

**定理**: 设 $\dot{\mathbf{y}} = \mathbf{f}(\mathbf{y}, \mu)$，$\mathbf{f}(\mathbf{0}, \mu) = 0$。设线性化 $A(\mu) = D\mathbf{f}(\mathbf{0}, \mu)$ 有一对复特征值 $\lambda(\mu) = \alpha(\mu) \pm i\omega(\mu)$，满足：
1. $\alpha(0) = 0$，$\omega(0) > 0$
2. $\alpha'(0) \neq 0$（横截性）
3. $A(0)$ 无其他零实部特征值

则存在 $\mu_0$ 的邻域，使得当 $\mu$ 在 $\mu_0$ 某一侧时，有周期解从平衡点分岔出来。

---

### 定义 I.34.8 (线性系统 / Linear Systems)

**定义**: **线性系统** 是形如

$$\dot{\mathbf{y}} = A(t)\mathbf{y} + \mathbf{b}(t)$$

的方程组，其中 $A(t)$ 是 $n \times n$ 矩阵，$\mathbf{b}(t)$ 是向量。

**齐次线性系统**: $\dot{\mathbf{y}} = A(t)\mathbf{y}$

**常数系数**: $\dot{\mathbf{y}} = A\mathbf{y}$

---

### 定理 34.7 (线性系统的基本矩阵 / Fundamental Matrix of Linear Systems)

**定理**: 设 $\Phi(t)$ 是 $\dot{\mathbf{y}} = A(t)\mathbf{y}$ 的 **基本矩阵**（列向量是 $n$ 个线性无关解）。则：
1. 通解: $\mathbf{y}(t) = \Phi(t)\mathbf{c}$，$\mathbf{c} \in \mathbb{R}^n$
2. $\det\Phi(t) = \det\Phi(t_0) \exp\left(\int_{t_0}^t \text{tr}\,A(s) ds\right)$（Liouville公式）

**常数变易法**: 非齐次方程的解

$$\mathbf{y}(t) = \Phi(t)\Phi^{-1}(t_0)\mathbf{y}_0 + \Phi(t)\int_{t_0}^t \Phi^{-1}(s)\mathbf{b}(s) ds$$

---

### 定理 34.8 (常系数线性系统 / Constant Coefficient Linear Systems)

**定理**: 对于 $\dot{\mathbf{y}} = A\mathbf{y}$（$A$ 常矩阵）：

1. **若 $A = PDP^{-1}$ 可对角化**:

$$\mathbf{y}(t) = P e^{Dt} P^{-1}\mathbf{y}_0 = P \begin{pmatrix} e^{\lambda_1 t} & & \\ & \ddots & \\ & & e^{\lambda_n t} \end{pmatrix} P^{-1}\mathbf{y}_0$$

2. **一般情况**: $\mathbf{y}(t) = e^{At}\mathbf{y}_0$，其中

$$e^{At} = \sum_{k=0}^\infty \frac{(At)^k}{k!}$$

**Jordan标准形**: 可用Jordan分解化简计算。

---

### 定义 I.34.9 (Floquet理论 / Floquet Theory)

**定义**: **周期线性系统** $\dot{\mathbf{y}} = A(t)\mathbf{y}$，$A(t+T) = A(t)$。

**Floquet定理**: 基本矩阵有形式

$$\Phi(t) = P(t) e^{Bt}$$

其中 $P(t+T) = P(t)$ 周期，$B$ 是常数矩阵。

**特征乘数**: $e^{BT}$ 的特征值 $\rho_i$。

**特征指数**: 满足 $e^{\mu_i T} = \rho_i$ 的 $\mu_i$。

**稳定性**: 当且仅当所有 $|\rho_i| < 1$（或 $\text{Re}(\mu_i) < 0$）时渐近稳定。

---

### 定义 I.34.10 (Sturm-Liouville问题 / Sturm-Liouville Problem)

**定义**: **Sturm-Liouville问题** 是二阶线性微分方程

$$-(p(x)y')' + q(x)y = \lambda w(x)y, \quad a \leq x \leq b$$

配合边界条件

$$\alpha_1 y(a) + \alpha_2 y'(a) = 0, \quad \beta_1 y(b) + \beta_2 y'(b) = 0$$

其中 $p(x) > 0$，$w(x) > 0$。

**自伴算子**: 微分算子 $L[y] = -(py')' + qy$ 在加权内积 $\langle f, g \rangle = \int_a^b fgw\, dx$ 下自伴。

---

### 定理 34.9 (Sturm-Liouville特征值理论 / Sturm-Liouville Eigenvalue Theory)

**定理**: 正则Sturm-Liouville问题有：
1. 可数无穷多个实特征值 $\lambda_1 < \lambda_2 < \cdots$，$\lambda_n \to \infty$
2. 每个特征值是简单的（一维特征空间）
3. 特征函数 $\{\phi_n\}$ 关于权 $w$ 正交
4. 特征函数完备：$\{f \in L^2_w[a,b]\}$ 可展为Fourier级数 $f = \sum c_n \phi_n$

**振荡定理**: 第 $n$ 个特征函数 $\phi_n$ 在 $(a,b)$ 内恰有 $n-1$ 个零点。

---

### 定义 I.34.11 (边值问题 / Boundary Value Problems)

**定义**: **边值问题** (BVP) 是微分方程配合边界条件（而非仅初值）。

**两点边值问题**:

$$y'' = f(x, y, y'), \quad a < x < b$$
$$\alpha y(a) + \beta y'(a) = \gamma, \quad \delta y(b) + \epsilon y'(b) = \eta$$

**Green函数**: 线性边值问题的解可通过Green函数 $G(x, \xi)$ 表示：

$$y(x) = \int_a^b G(x, \xi) f(\xi) d\xi + \text{边界项}$$

---

### 定理 34.10 (Green函数的构造 / Construction of Green's Function)

**定理**: 对于 $Ly = y'' + p(x)y' + q(x)y = f(x)$，边界条件 $y(a) = y(b) = 0$，Green函数为：

$$G(x, \xi) = \begin{cases}
\frac{y_1(x) y_2(\xi)}{W(\xi)}, & a \leq x < \xi \\
\frac{y_1(\xi) y_2(x)}{W(\xi)}, & \xi < x \leq b
\end{cases}$$

其中 $y_1$ 满足左边界条件，$y_2$ 满足右边界条件，$W = y_1 y_2' - y_1' y_2$ 是Wronsky行列式。

**性质**:
1. $G$ 连续，$\frac{\partial G}{\partial x}$ 在 $x = \xi$ 有跳跃 $1$
2. $LG = 0$（$x \neq \xi$）
3. $G(a, \xi) = G(b, \xi) = 0$

---

### 定义 I.34.12 (奇异扰动 / Singular Perturbation)

**定义**: **奇异扰动问题** 包含小参数 $\epsilon$：

$$\epsilon y'' + p(x)y' + q(x)y = 0$$

当 $\epsilon \to 0$ 时，方程阶数降低，产生 **边界层**（boundary layer）。

**匹配渐近展开**:
- 外部解：设 $\epsilon = 0$，求 $y_{\text{out}}$
- 内部解：在边界层附近引入伸缩变量 $\xi = x/\epsilon^\alpha$
- 匹配：$y_{\text{in}} \to y_{\text{out}}$（中间区域）

---

### 定理 34.11 (稳定性理论 / Stability Theory)

**定理** (Lyapunov第二方法的推广): 考虑 $\dot{\mathbf{y}} = \mathbf{f}(\mathbf{y})$，$\mathbf{f}(\mathbf{0}) = 0$。若有正定函数 $V$ 使得 $\dot{V} \leq -cV$（$c > 0$），则原点 **指数稳定**：

$$\|\mathbf{y}(t)\| \leq \|\mathbf{y}(0)\| e^{-ct/2}$$

**逆Lyapunov定理** (Massera, Kurzweil): 若原点渐近稳定且 $\mathbf{f} \in C^k$，则存在 $C^k$ 类Lyapunov函数。

---

### 定义 I.34.13 (Hamilton系统 / Hamiltonian Systems)

**定义**: **Hamilton系统** 是形如

$$\dot{q}_i = \frac{\partial H}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial H}{\partial q_i}$$

的方程组，其中 $H(q, p, t)$ 是 **Hamilton函数**。

**性质**:
1. **能量守恒**: 若 $H$ 不显含 $t$，则 $H$ 沿解是常数
2. **Liouville定理**: 相空间体积守恒
3. **辛结构**: 流 $\phi_t$ 保持辛形式 $\omega = \sum_i dq_i \wedge dp_i$

---

### 定理 34.12 (KAM理论 / Kolmogorov-Arnold-Moser Theory)

**定理**: 考虑近可积Hamilton系统

$$H(I, \theta, \epsilon) = H_0(I) + \epsilon H_1(I, \theta)$$

其中 $I \in \mathbb{R}^n$，$\theta \in \mathbb{T}^n$。若：
1. $H_0$ 满足非退化条件 $\det(\partial^2 H_0/\partial I^2) \neq 0$
2. 扰动 $\epsilon$ 足够小
3. Diophantine条件：频率 $\omega = \nabla H_0$ 满足 $|\omega \cdot k| \geq \gamma |k|^{-\tau}$（$k \in \mathbb{Z}^n \setminus \{0\}$）

则大多数不变环面在小扰动下保持（只是变形）。

**意义**: 可积系统的大部分"正则"行为在小扰动下保持。

---

### 参考文献 (34-XX)
1. Coddington, E.A., Levinson, N., *Theory of Ordinary Differential Equations*, McGraw-Hill, 1955
2. Hirsch, M.W., Smale, S., Devaney, R.L., *Differential Equations, Dynamical Systems, and an Introduction to Chaos*, Academic Press, 2012
3. Perko, L., *Differential Equations and Dynamical Systems*, Springer, 2001
4. Hartman, P., *Ordinary Differential Equations*, SIAM, 2002
5. Arnold, V.I., *Mathematical Methods of Classical Mechanics*, Springer, 1989
6. Wiggins, S., *Introduction to Applied Nonlinear Dynamical Systems and Chaos*, Springer, 2003

---

## Lean4 代码示例

本节提供与李群、李代数和常微分方程相关的 Lean4 代码示例。

### 1. 李代数基础

```lean4
-- 李代数的定义
import Mathlib.Algebra.Lie.Basic

-- 李代数满足反对称性和Jacobi恒等式
example (R : Type*) [CommRing R] (L : Type*) [AddCommGroup L] [Module R L]
    [LieAlgebra R L] (x y z : L) :
    ⁅x, y⁆ = -⁅y, x⁆ := by
  exact lie_skew x y

-- Jacobi 恒等式
example (R : Type*) [CommRing R] (L : Type*) [AddCommGroup L] [Module R L]
    [LieAlgebra R L] (x y z : L) :
    ⁅x, ⁅y, z⁆⁆ + ⁅y, ⁅z, x⁆⁆ + ⁅z, ⁅x, y⁆⁆ = 0 := by
  exact lie_lie_assoc_anti x y z
```

### 2. 一般线性群的李代数

```lean4
-- 矩阵李代数
import Mathlib.Algebra.Lie.Matrix
import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup

-- 一般线性群的李代数是矩阵代数，李括号为交换子
-- ⁅A, B⁆ = AB - BA

-- 交换子的性质
example (n : Type*) [Fintype n] (A B : Matrix n n ℝ) :
    ⁅A, B⁆ = A * B - B * A := by
  simp [Matrix.lie_def]
```

### 3. 特殊线性群与特殊线性李代数

```lean4
-- 特殊线性群 SL(n)
import Mathlib.LinearAlgebra.Matrix.SpecialLinearGroup

-- SL(n, R) 的李代数是迹为零的矩阵
-- sl_n = {A : Matrix n n R | A.trace = 0}

-- 迹的线性性
example (n : Type*) [Fintype n] (A B : Matrix n n ℝ) :
    (A + B).trace = A.trace + B.trace := by
  exact Matrix.trace_add A B
```

### 4. 正交群与特殊正交群

```lean4
-- 正交群
import Mathlib.LinearAlgebra.Matrix.SpecialLinearGroup
import Mathlib.LinearAlgebra.Matrix.Symmetric

-- O(n) = {A : Matrix n n R | Aᵀ A = I}
-- SO(n) = {A : O(n) | A.det = 1}

-- 正交矩阵保持内积
-- 对于 A ∈ O(n)，⟨Ax, Ay⟩ = ⟨x, y⟩
```

### 5. 指数映射

```lean4
-- 矩阵指数
import Mathlib.LinearAlgebra.Matrix.Exponential

-- 矩阵指数的定义
-- exp(A) = Σ_{k=0}^{∞} A^k / k!

-- 指数的基本性质
example (n : Type*) [Fintype n] (A : Matrix n n ℝ) :
    Matrix.exp 0 = 1 := by
  exact Matrix.exp_zero

-- 指数与迹的关系 (对于小矩阵)
-- det(exp(A)) = exp(tr(A))
```

### 6. 单参数子群

```lean4
-- 单参数子群
-- γ(t) = exp(tA) 是满足 γ(s+t) = γ(s)γ(t) 的群同态

-- 矩阵指数的群性质
example (n : Type*) [Fintype n] (A : Matrix n n ℝ) (s t : ℝ) :
    Matrix.exp (A * (s + t)) = Matrix.exp (A * s) * Matrix.exp (A * t) := by
  rw [Matrix.exp_mul_eq_exp_add]
  -- 需要 A 是可交换的矩阵
```

### 7. 伴随表示

```lean4
-- 伴随表示
import Mathlib.Algebra.Lie.Basic

-- Ad_g(X) = g X g^{-1}
-- ad_X(Y) = [X, Y]

-- ad 与李括号的关系
example (R : Type*) [CommRing R] (L : Type*) [AddCommGroup L] [Module R L]
    [LieAlgebra R L] (x y : L) :
    ⁅x, y⁆ = (LieAlgebra.ad R L) x y := by
  rfl
```

### 8. 常微分方程存在唯一性

```lean4
-- Picard-Lindelöf 定理
import Mathlib.Analysis.ODE.PicardLindelof

-- 初值问题 y' = f(x, y), y(x₀) = y₀
-- 若 f 关于 y 满足 Lipschitz 条件，则存在唯一解

-- 局部存在性
example {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    {f : ℝ → E → E} {x₀ : ℝ} {y₀ : E}
    (hlip : ∀ x ∈ Set.Ioo (x₀ - ε) (x₀ + ε), LipschitzOnWith K (f x) (ball y₀ δ))
    (hcont : ContinuousOn (fun p : ℝ × E => f p.1 p.2) (Set.Ioo (x₀ - ε) (x₀ + ε) ×ˢ ball y₀ δ)) :
    ∃ sol : ℝ → E, sol x₀ = y₀ ∧ ∀ x ∈ Set.Ioo (x₀ - h) (x₀ + h), HasDerivAt sol (f x (sol x)) x := by
  -- 使用 Picard-Lindelof 存在性定理
  sorry
```

### 9. 线性常微分方程

```lean4
-- 线性系统 y' = A y
import Mathlib.LinearAlgebra.Matrix.Exponential

-- 解为 y(t) = exp(tA) y₀

-- 常系数线性系统的解
example (n : Type*) [Fintype n] (A : Matrix n n ℝ) (y₀ : Matrix n n ℝ) (t : ℝ) :
    ∃ y : ℝ → Matrix n n ℝ, y 0 = y₀ ∧ ∀ s : ℝ, HasDerivAt y (A * y s) s := by
  -- y(s) = exp(sA) y₀
  use fun s => Matrix.exp (s • A) * y₀
  constructor
  · simp [Matrix.exp_zero]
  · intro s
    -- 需要证明导数
    sorry
```

### 10. Hamilton 系统

```lean4
-- Hamilton 方程
-- dq/dt = ∂H/∂p
-- dp/dt = -∂H/∂q

-- 简谐振子 H(q, p) = p²/2 + kq²/2
-- dq/dt = p
-- dp/dt = -kq

-- 辛结构保持
-- Hamilton 流保持辛形式 ω = dq ∧ dp
```

### 11. Sturm-Liouville 问题

```lean4
-- Sturm-Liouville 算子
-- L[y] = -(p(x)y')' + q(x)y = λw(x)y

-- 自伴性质
-- ⟨Ly₁, y₂⟩_w = ⟨y₁, Ly₂⟩_w

-- 特征值的实性
-- 自伴算子的特征值都是实数
```

### 12. 稳定性分析

```lean4
-- Lyapunov 稳定性

-- 线性化的稳定性判据
-- 若 A 的所有特征值有负实部，则原点渐近稳定

-- 矩阵稳定性
def IsStableMatrix (A : Matrix n n ℂ) : Prop :=
  ∀ λ : ℂ, Matrix.Eigenvalue A λ → λ.re < 0

-- Hurwitz 稳定性判据
-- 通过特征多项式的系数判断稳定性
```

### 13. 极限环与分岔

```lean4
-- Poincaré-Bendixson 定理 (示意性)
-- 在 ℝ² 中，有界轨道若不趋于平衡点，则趋于周期轨道

-- Hopf 分岔条件
-- 当特征值穿过虚轴时产生极限环
-- Re(λ(μ)) 在 μ = μ₀ 处变号
```

### 14. 向量场与流

```lean4
-- 向量场与流的关系
import Mathlib.Geometry.Manifold.VectorBundle.SmoothSection

-- 向量场生成流
-- d/dt φ_t(p) = X(φ_t(p))

-- 流的群性质
-- φ_{t+s} = φ_t ∘ φ_s
```

### 15. 齐性空间

```lean4
-- 齐性空间 G/H
-- 例如：Sⁿ⁻¹ = SO(n)/SO(n-1)

-- 球面作为齐性空间
-- S² = SO(3)/SO(2)
```

### 说明

上述代码展示了 Mathlib4 中李群、李代数和常微分方程的主要内容：

1. **李代数**: Mathlib 提供了完整的李代数理论，包括李括号、Jacobi 恒等式等
2. **矩阵群**: 支持一般线性群、特殊线性群、正交群等
3. **矩阵指数**: 提供了矩阵指数的定义和基本性质
4. **ODE 理论**: 包含 Picard-Lindelöf 存在唯一性定理
5. **稳定性**: 可定义矩阵稳定性和 Lyapunov 函数

---

## 跨领域联系

### 与泛函分析的联系
- **李群** = Banach李群的无穷维推广
- **半单李代数** = 算子代数的结构理论
- **表示论** = 调和分析的基础

### 与微分几何的联系
- **李群** = 具有群结构的光滑流形
- **指数映射** = 测地线的类比
- **齐性空间** = 对称空间

### 与动力系统的联系
- **流** = 向量场生成的动力系统
- **稳定性** = Lyapunov理论
- **分岔** = 参数变化下的结构改变

### 与数学物理的联系
- **Hamilton系统** = 经典力学
- **李群** = 规范场论
- **KAM理论** = 近可积系统的稳定性

### 与数论的联系
- **代数群** = 模形式的自守表示
- **李代数** = Langlands纲领

---

## 本卷统计

| 类别 | 数量 |
|------|------|
| **定义** | 26 |
| **定理** | 12 |
| **参考文献** | 12+ |
| **MSC二级分类** | 2 |

---

## 版本信息

**创建日期**: 2025-03-26  
**版本**: 2.1  
**总大小**: ~25K  
**MSC覆盖**: 22-XX, 34-XX

---

*"李群是连续对称性的数学实现，而微分方程是变化规律的精确描述。"  
—— Hermann Weyl*
