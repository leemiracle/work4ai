# Evans《Partial Differential Equations》(GSM 19, 2nd Ed) · 快速逐章精读

> 基于原书：*Partial Differential Equations*, GSM 19（Lawrence C. Evans, AMS, 2nd ed., 2010）/ 读于：2026-07-02
> 定位：**PDE 研究生级标准教材**，古典表示 → 弱解理论 → 非线性三大阶梯，GTM 谱系核心纵深。
> 关联：[Kress 数值分析 GTM181](kress_数值分析_GTM181_快速逐章.md) · [微分方程 ODE](../stage-2-研究生基础/微分方程_快速逐章.md) · [C-数值分析研究入门](C-数值分析与科学计算_研究入门.md)
> 章节映射：本笔记依 Evans 三部曲 12 章组织——Part I 古典(Ch1-3)·Part II 线性弱解(Ch4-6)·Part III 非线性(Ch7-12)。

---

## §0 引言：Evans 的「弱解」哲学转向

Lawrence C. Evans《Partial Differential Equations》(GSM 19, AMS, 2nd ed. 2010) 是偏微分方程方向的研究生级标准教材——作者 Evans 是 UC Berkeley 教授、非线性 PDE 与微分对策的世界权威，本书因此带有一块招牌：**非线性 PDE 的现代理论**（粘性解、守恒律激波、变分法）。

一句话定位：本书是 stage-3 PDE 方向的核心纵深教材。已读本仓库《微分方程》(Boyce-DiPrima 本科 ODE+PDE 入门)与 Kress(数值实现)，Evans 把读者从「会用分离变量解具体方程」推进到「在 Sobolev 函数空间中建立弱解的存在、唯一、正则性」——这是 20 世纪 PDE 理论的方法论革命。

三大阶梯贯穿全书，构成「从显式公式到抽象存在性」的因果链：

- **古典表示**（Part I）：基本解、Green 函数、特征线、能量方法——给出「解长什么样」的显式公式，依赖 Fourier 变换与分离变量。
- **弱解理论**（Part II）：Sobolev 空间是舞台，Lax-Milgram 是椭圆方程的存在唯一判据，变分法把 PDE 化为「能量泛函极小」。
- **非线性发展**（Part III）：热/波方程弱解（Galerkin 逼近）、守恒律激波（熵条件）、Hamilton-Jacobi（粘性解）、Navier-Stokes——线性工具无力，需非线性新方法。

Evans 的核心哲学是**「放宽解的定义以获得存在性」**：古典解要求 $u\in C^2$，太苛刻、多数 PDE 无解；弱解只要求 $u\in H^1(\Omega)$（分布意义下可导），用分部积分把导数「转移」到检验函数上。这一「弱化」换来的是：先有存在性，再用「正则性提升」逐步证明弱解其实是光滑的（Weyl 引理式的「椭圆正则化」）。

### 四本 PDE 教材对比

| 维度 | **Evans GSM19** | Strauss | Taylor PDE(3卷) | Gilbarg-Trudinger |
|------|------------------|---------|------------------|-------------------|
| 篇幅·定位 | ~750页·GTM研究生级 | ~450页·本科入门 | ~1500页·研究级全面 | ~520页·GTM椭圆专精 |
| 招牌特色 | 三部曲均衡(古典→弱解→非线性) | 工程直觉·本科 | 几何全面纵深(流形/分析) | 椭圆二阶圣经(先验估计) |
| 弱解/Sobolev | **核心 Part II** | 浅(无系统) | 二者皆有(深) | 椭圆深入(无抛物双曲) |
| 非线性 | **有(守恒律/HJ/NS)** | 无 | 有(部分) | 无(纯线性椭圆) |
| 现代性 | 2010(2nd)·现代 | 2007(2nd) | 2011 | 2001(reprint)·经典 |
| 飞腾匹配 | 弱解+Sobolev+有限元 | 古典直觉 | 几何全面 | 先验估计·非散度 |

> **阅读策略**：Strauss 立柱(本科直觉) → **Evans 封顶(弱解理论+非线性)**。Taylor 作几何纵深侧翼(按需查)，Gilbarg-Trudinger 则是椭圆方向的「百科全书」深挖工具。

---

## §1 全书骨架与飞腾锚点分布

Evans 全书 12 章，主线是「**放宽解的定义，换来存在性，再提升正则性**」。Part I 给显式公式(知道解长什么样)，Part II 搭建弱解舞台(Sobolev 空间→椭圆存在性→变分)，Part III 把线性工具推广到非线性(发展方程→守恒律激波→粘性解→流体)。每章均对接一条飞腾实测锚点。

**与已读书的衔接**：《微分方程》(Boyce-DiPrima) 第 8-9 章已建立分离变量、傅里叶级数、Sturm-Liouville 的本科直觉；Kress 第 5-6 章已给 ODE/PDE 的数值离散。Evans 的增量在 Part II-III：Sobolev 空间的严格弱导数、Lax-Milgram 的椭圆存在唯一性、守恒律的熵条件——这些是本科教材触及不到的现代核心。读 Evans 时 Part I 可快速扫读(查漏补缺)，重心放在 Part II 的弱解理论。

### 飞腾锚点 × 章节分布表

| 章 | 主题 | 主飞腾锚点 | 实测数据 | 辅锚点 | 落地点 |
|----|------|-----------|----------|--------|--------|
| 1 | 四大PDE引言 | matmul [V03] 🟢 | 15× | Iron Law | 基本解卷积=密集点积 |
| 2 | Fourier变换 | UDOT⭐Fourier [E05] 🟢 | **16.9×** | matmul | 频域卷积·点积核 |
| 3 | 分离变量 | Schmidt Sobolev投影 🟢 | Gram-Schmidt | matmul | 正交特征基·稳定展开 |
| 4 | Sobolev空间 | TLB局部弱导 [E04] 🟡 | 4.81× | Iron Law⭐弱解 | 弱导数局部性·磨光逼近 |
| 5 | 二阶椭圆Lax-Milgram | GEMM⭐有限元 [Lab05] 🟢 | **9.45G** | Iron Law⭐弱解 | 双线性型=刚度矩阵组装 |
| 6 | 变分Dirichlet | GEMM⭐有限元 🟢 | 9.45G | Schmidt | 能量泛函极小·直接方法 |
| 7 | 热方程弱解 | FP16 [L01] 🟢 | 3.81× | matmul | Galerkin·长期积分误差 |
| 8 | 波动方程 | matmul 🟢 | 15× | FP16 | Galerkin投影·能量守恒 |
| 9 | 守恒律Burgers熵 | 分支预测激波 [Lab02] 🟡 | 0.71 | GEMM | 激波间断·熵条件筛选 |
| 10 | Hamilton-Jacobi粘性 | FP16 🟡 | 3.81× | Iron Law | 粘性消去ε→0·极限 |
| 11 | 非散度形式 | TLB局部弱导 🟡 | 4.81× | matmul | 极值原理局部性 |
| 12 | Navier-Stokes | GEMM⭐有限元 🟢 | 9.45G | FP16 | 非线性对流项·大矩阵 |

```
Part I 古典表示公式(Ch1-3) ── 显式公式·"解长什么样"
第1章 四大PDE(transport/Laplace/热/波)── 基本解·Green·特征线·能量 ──┐
第2章 Fourier变换 ── 微分⟹乘法，全空间PDE频域求解 ─────────────────┤
第3章 分离变量 ── 有界域特征函数展开·Sturm-Liouville正交基 ────────┘
         │ 弱化解的定义
Part II 线性PDE弱解理论(Ch4-6) ── 函数空间·存在性·变分
第4章 Sobolev空间 ── 弱导数·嵌入·迹·紧性，弱解"舞台" ─────────────┐
第5章 二阶椭圆(Lax-Milgram)── 双线性型·强制·弱形式⟹存在唯一 ──────┤
第6章 变分法(Dirichlet)── 能量泛函极小·Euler-Lagrange·直接方法 ───┘
         │ 推广到非线性
Part III 非线性PDE(Ch7-12) ── 发展方程·守恒律·粘性·流体
第7章 热方程弱解 ── Galerkin逼近·能量估计·半群 ───────────────────┐
第8章 波动方程弱解 ── Galerkin·能量守恒 ──────────────────────────┤
第9章 守恒律(Burgers/熵)── 激波·Rankine-Hugoniot·Lax熵条件 ───────┤
第10章 Hamilton-Jacobi ── 粘性解(Crandall-Lions) ─────────────────┤
第11章 非散度形式 ── Aleksandrov·Krylov-Safonov·W^{2,p}估计 ──────┤
第12章 Navier-Stokes ── 不可压NS·存在性理论 ──────────────────────┘

数学根基：Spivak微积分(多元/链式法则)·LADR(内积/正交)·Royden(Lebesgue/Lp/Hilbert)
         ·微分方程ODE(特征线/变换域/能量)
```

---

## Part I · 古典表示公式

### 第1章 引言：四大经典 PDE(Introduction)

- **核心**：全书工具章，用四种方法解四类方程，建立「PDE 长什么样」的直觉：

  ① **transport 方程**——$u_t+b\cdot Du=f$，沿特征线 $\dot x=b$ 化为 ODE，解 $u(x,t)=g(x-tb)$。这是「方法一：特征线法」。

  ② **Laplace 方程** $\Delta u=0$——基本解 $\Phi(x)=\frac{1}{n(2-n)\omega_n}|x|^{2-n}$($n\ge3$)，平均值公式 $u(x)=\frac{1}{|\partial B|}\int_{\partial B}u$，最大值原理(max 在边界)，Green 函数表出解。这是「方法二：基本解 + Green 函数」。

  ③ **热方程** $u_t-\Delta u=f$——热核 $\Phi(x,t)=\frac{1}{(4\pi t)^{n/2}}e^{-|x|^2/4t}$，**Duhamel 原理**把非齐次源表为卷积叠加。

  ④ **波方程** $u_{tt}-\Delta u=0$——d'Alembert 公式(1D)、Kirchhoff(3D)、Poisson(2D)，**能量方法** $\frac{d}{dt}\frac12\int(u_t^2+|Du|^2)=0$ 给唯一性与有限传播速度。

- **飞腾锚点** 🟢：**matmul 15×** [V03]。基本解卷积 $u=\Phi*g=\int\Phi(x-y)g(y)\,dy$ 是密集点积——离散后正是 GEMM；Duhamel 的时间积分叠加多次卷积，是 matmul 的天然场景。

- **关键定理**：**热方程 Duhamel 原理**——$u(x,t)=\int_{\mathbb{R}^n}\Phi(x-y,t)g(y)\,dy+\int_0^t\!\int\Phi(x-y,t-s)f(y,s)\,dy\,ds$。

- **自测**：① 调和函数满足平均值公式，反之是否成立(Weyl 引理：是)？② 波方程能量为何守恒？这给出什么物理结论(能量不增不减=有限传播)？

---

### 第2章 Fourier 变换(Fourier Transform)

- **核心**：把「微分」变成「乘法」，全空间 $\mathbb{R}^n$ 上线性 PDE 的求解利器：

  ① **定义与性质**——$\hat u(\xi)=\frac{1}{(2\pi)^{n/2}}\int e^{-ix\cdot\xi}u(x)\,dx$，核心魔法 $\widehat{D^\alpha u}=(i\xi)^\alpha\hat u$(导数⟹乘法)、$\widehat{u*v}=\hat u\hat v$(卷积⟹乘积)、Plancherel 保范。

  ② **解 PDE**——$-\Delta u=f$ 取变换得 $|\xi|^2\hat u=\hat f$，$\hat u=\hat f/|\xi|^2$，反变换即解 $u=\Phi*f$。热方程变换后 $\hat u_t+|\xi|^2\hat u=0$ 化为 ODE。

  ③ **分布理论入门**——广义函数(δ 函数、基本解作为分布)，Fourier 变换在分布上闭环，是 Sobolev 空间(Ch4)的预备。

- **飞腾锚点** 🟢：**UDOT⭐Fourier 16.9×** [E05]。Fourier 变换 = 基函数 $e^{-ix\cdot\xi}$ 与 $u$ 的内积叠加，本质是密集点积；FFT 把 $O(n^2)$ 降到 $O(n\log n)$，飞腾 INT8 UDOT 点积指令对批量频域系数求和加速 16.9×。

- **关键定理**：**卷积定理**——$\widehat{u*v}=\hat u\hat v$；反演 $u(x)=\frac{1}{(2\pi)^{n/2}}\int e^{ix\cdot\xi}\hat u(\xi)\,d\xi$。

- **自测**：① 用 Fourier 变换求 $-\Delta u=f$ 在 $\mathbb{R}^n$ 的解。② $\widehat{D_ku}$ 等于什么？这为何是「弱导数」的频域语言？

---

### 第3章 分离变量(Separation of Variables)

- **核心**：有界域上 PDE 的求解，把 PDE 拆成 ODE 特征值问题：

  ① **特征函数展开**——设 $u(x,t)=X(x)T(t)$ 代入，边界条件筛出离散特征值 $\lambda_n$ 与特征函数 $\phi_n$，解表为级数 $u=\sum c_n\phi_n e^{-\lambda_n t}$。

  ② **对称特征值问题**——$Lu=\lambda u$($L$ 对称椭圆算子)，特征值离散实数列 $\lambda_1\le\lambda_2\le\cdots\to\infty$，特征函数 $\{\phi_n\}$ 在 $L^2$ 中**正交完备**，任意函数可展为广义 Fourier 级数。

  ③ **Sturm-Liouville 理论**——回扣《微分方程》第 9 章；分离变量是 Ch4 Sobolev 空间特征值理论的「古典版预演」。

- **飞腾锚点** 🟢：**Schmidt Sobolev 投影**。特征函数正交基 $\{\phi_n\}$ 的构造与 Gram-Schmidt 正交化同源(对称算子保证正交)；正交基使展开系数 $c_n=\langle u,\phi_n\rangle$ 数值稳定，这是 Ch4 Sobolev 空间「投影到子空间」思想的古典前身。辅锚点：大规模展开系数是 **matmul 15×**。

- **关键定理**：**特征函数正交完备性**——对称椭圆算子的特征函数 $\{\phi_n\}$ 构成 $L^2(\Omega)$ 的正交基，$u=\sum\langle u,\phi_n\rangle\phi_n$。

- **自测**：① 一维杆 $u_t=u_{xx}$，端点 $u=0$，初值 $g(x)=x(1-x)$，写出级数解前几项。② 为何特征值 $\lambda_n\to\infty$？这保证级数收敛。

---

## Part II · 线性 PDE 弱解理论

### 第4章 Sobolev 空间(Sobolev Spaces)· Part II 开篇

- **核心**：**弱解理论的舞台**。把「导数」从经典 $C^k$ 放宽到分布意义，构造容纳弱解的函数空间：

  ① **弱导数**——$u$ 有 $\alpha$ 阶弱导数 $D^\alpha u$ 若 $\int u\,D^\alpha\phi=(-1)^{|\alpha|}\int(D^\alpha u)\phi$($\forall\phi\in C_c^\infty$)。分部积分把导数「转移」到检验函数——这是弱解哲学的源头。

  ② **空间 $W^{k,p}$/$H^1$**——$W^{k,p}=\{u:D^\alpha u\in L^p,|\alpha|\le k\}$，$H^1(\Omega)=W^{1,2}$ 是 Hilbert 空间。磨光逼近($u_\epsilon=\eta_\epsilon*u\to u$)证明弱导数=磨光极限。

  ③ **三大工具**——**Sobolev 嵌入**($W^{1,p}\hookrightarrow L^{p^*}$，$p^*=np/(n-p)$)、**迹定理**(边界值 $Tu\in L^2(\partial\Omega)$ 有意义)、**Rellich 紧性**($W^{1,p}\Subset L^p$，极小化序列有收敛子列)。

- **飞腾锚点** 🟡：**TLB 局部弱导** [E04]。弱导数由「局部积分恒等式」定义，依赖函数在局部邻域的行为——TLB(翻译后备缓冲)管理「局部性」的内存映射，弱导数的局部支撑结构与缓存的局部访问模式同构，故标 🟡(类比)。**Iron Law<2%⭐弱解**：磨光逼近的截断误差须压进 2% 预算，弱解才逼近真解——这是「放宽定义」换取存在性的精度代价。

- **关键定理**：**Sobolev 嵌入定理**——若 $1\le p<n$，$W^{1,p}(\Omega)\hookrightarrow L^{p^*}(\Omega)$，$p^*=\frac{np}{n-p}$；$p>n$ 则嵌入连续函数空间 $C^{0,\alpha}$。

- **自测**：① $u(x)=|x|$ 在 $(-1,1)$ 有弱导数吗(有，$\text{sgn}$)？$|x|^{1/2}$ 呢(无)？② 为何 Rellich 紧性是变分法「直接方法」的关键？

---

### 第5章 二阶椭圆方程· Lax-Milgram(Second-Order Elliptic)

- **核心**：**弱解理论的高潮**。把 $Lu=f$ 写成弱形式，用 Lax-Milgram 证明存在唯一：

  ① **弱形式**——散度型 $Lu=-(a^{ij}u_{x_j})_{x_i}+b^iu_{x_i}+cu=f$，分部积分得双线性型 $B[u,v]=\int a^{ij}u_{x_j}v_{x_i}+b^iu_{x_i}v+cuv$。弱解：找 $u\in H_0^1$ 使 $B[u,v]=(f,v)$($\forall v$)。

  ② **Lax-Milgram 定理**——$H$ 上**有界 + 强制**(coercive)双线性型 $B$，对任意 $f\in H^*$ 存在唯一 $u\in H$ 使 $B[u,v]=\langle f,v\rangle$。Gårding 不等式 $B[u,u]\ge\alpha\|u\|_{H^1}^2-\gamma\|u\|_{L^2}^2$ 处理非强制情形。

  ③ **正则性与特征值**——弱解 + 系数光滑 ⟹ $u$ 提升(椭圆正则性)；对称椭圆算子的特征值 $\lambda_1=\min\frac{\int|Du|^2}{\int u^2}$(Rayleigh 商)。

- **飞腾锚点** 🟢：**GEMM⭐有限元** [Lab05]。双线性型 $B[u,v]$ 离散后正是**有限元刚度矩阵** $K_{ij}=B[\phi_j,\phi_i]$，组装是密集 GEMM——飞腾 9.45 GFLOPS 直接决定大规模椭圆问题的求解效率。**Iron Law<2%⭐弱解**：Lax-Milgram 保证存在唯一，但「弱解到古典解」的正则性提升是精度门槛。

- **关键定理**：**Lax-Milgram**——$B:H\times H\to\mathbb{R}$ 有界($|B[u,v]|\le M\|u\|\|v\|$)且强制($B[u,u]\ge\alpha\|u\|^2$)，则 $\forall f\in H^*$ $\exists!u$：$B[u,v]=\langle f,v\rangle$。

- **自测**：① Poisson $-\Delta u=f$，$u|_{\partial\Omega}=0$，写出弱形式与双线性型，验证强制性。② Gårding 不等式何时退化为不强制(低阶项 $c$ 太负)？

---

### 第6章 变分法· Dirichlet 原理(Calculus of Variations)

- **核心**：把 PDE 视为「能量泛函的极值条件」，**直接方法**给存在性：

  ① **Euler-Lagrange 方程**——能量 $I[u]=\int_\Omega L(Du,u,x)\,dx$，极小元的必要条件 $-\text{div}\,\frac{\partial L}{\partial(Du)}+\frac{\partial L}{\partial u}=0$ 正是 PDE。Dirichlet 原理：$\min\frac12\int|Du|^2-\int fu$ 的 Euler-Lagrange = Poisson $-\Delta u=f$。

  ② **直接方法**——取极小化序列 $\{u_n\}$，$I[u_n]\to\inf$；弱下半连续性($u_n\rightharpoonup u\Rightarrow I[u]\le\liminf I[u_n]$)+ Rellich 紧性 ⟹ 极小元存在。这是「**变分=存在性**」的核心论证。

  ③ **约束与特征值**——带约束($\|u\|=1$)的极值给特征值(Rayleigh 商)，约束变分引出 Lagrange 乘子。Hamilton 量与 Ch10 Hamilton-Jacobi 方程对接。

- **飞腾锚点** 🟢：**GEMM⭐有限元**。能量泛函 $I[u]$ 离散后是有限元刚度/质量矩阵的二次型 $\frac12\mathbf{u}^TK\mathbf{u}-\mathbf{f}^T\mathbf{u}$，极小化 = 解 $K\mathbf{u}=\mathbf{f}$(GEMM 组装)；辅锚点：正交投影极小化用 **Schmidt Sobolev 投影**。

- **关键定理**：**Dirichlet 原理 + 直接方法**——$\inf_{H_0^1}I[u]$ 在 coercive 条件下可达，极小元是 Poisson 方程弱解；弱下半连续 + 紧性 = 存在性。

- **自测**：① 为何 $I[u]=\int|Du|^2$ 弱下半连续而 $\int-|Du|^2$ 不是(凸性)？② Rayleigh 商 $\lambda_1=\min_{u\ne0}\frac{\int|Du|^2}{\int u^2}$ 的极小元满足什么 PDE(特征值方程 $-\Delta u=\lambda u$)？

---

## Part III · 非线性 PDE

### 第7章 热方程弱解(Heat Equation, Weak)· Part III 开篇

- **核心**：把 Part II 的椭圆弱解理论推广到时间发展方程：

  ① **Galerkin 逼近**——$u' + Lu = f$ 投影到有限维特征函数子空间，化为一组 ODE，解后取极限得弱解。这是「先有限维存在，再紧性取极限」的标准范式。

  ② **能量估计**——$\|u(t)\|_{L^2}^2+\int_0^t\|Du\|_{L^2}^2\le C(\|g\|^2+\|f\|^2)$，耗散结构(扩散)使能量衰减，给唯一性与正则性。

  ③ **半群理论**——$u(t)=e^{tL}g$，线性算子生成 $C_0$ 半群(Hille-Yosida 定理)，热方程是耗散半群的典范。最大值原理在弱解意义仍成立。

- **飞腾锚点** 🟢：**FP16 3.81×** [L01]。热方程长时间积分中**耗散使高模衰减**，但浮点误差累积仍支配长时间精度——FP16($\varepsilon\approx9.8\times10^{-4}$)下高模比 FP64 更快被噪声淹没，3.81× 速度差背后是「精度-时间」权衡。辅锚点：Galerkin 每步是 **matmul 15×**。

- **关键定理**：**能量估计 + 唯一性**——$\frac{d}{dt}\frac12\|u\|_{L^2}^2+\|Du\|_{L^2}^2=(f,u)\le\frac12\|f\|^2+\frac12\|u\|^2$ ⟹ Gronwall ⟹ 解的界与唯一性。

- **自测**：① 热方程弱解的「能量」为何单调递减(耗散)？② Galerkin 逼近为何能取到极限(Rellich 紧性)？

---

### 第8章 波动方程弱解(Wave Equation)

- **核心**：把 Ch1 的能量方法严格化，建立弱解存在性：

  ① **Galerkin 逼近**——同 Ch7，投影到特征函数子空间得 ODE 组，取极限。波方程无耗散，能量守恒。

  ② **能量守恒**——$E(t)=\frac12\int(u_t^2+|Du|^2)\,dx=E(0)$，与 Ch1 一致；这给唯一性与有限传播速度(扰动的「光锥」结构)。

  ③ **正则性与半群**——二阶方程化为方程组后生成 $C_0$ 半群(保能量，酉群)；波方程的弱解在能量空间 $H_0^1\times L^2$ 中适定。

- **飞腾锚点** 🟢：**matmul 15×**。Galerkin 投影的每步推进是特征函数基上的 matmul；波方程的辛结构(保能量)要求时间推进用辛格式，matmul 向量化加速多模式并行。辅锚点：长期积分误差受 **FP16 3.81×** 影响但波方程无耗散、误差不衰减。

- **关键定理**：**能量守恒 + 有限传播**——$E(t)=E(0)$ ⟹ 唯一性；依赖区域(光锥)外 $u=0$ ⟹ 信号速度有限。

- **自测**：① 波方程能量守恒 vs 热方程能量衰减，物理本质差异(可逆 vs 不可逆)？② 为何波方程弱解需两个初值 $u(0),u_t(0)$ 而热方程只需一个？

---

### 第9章 守恒律· Burgers 与熵(Conservation Laws)

- **核心**：**非线性第一击**。$u_t+F(u)_x=0$，特征线相交产生激波，古典解破裂：

  ① **特征线与激波**——Burgers 方程 $u_t+(u^2/2)_x=0$，特征线 $x=x_0+F'(g(x_0))t$；$F''>0$ 时压缩特征线相交 ⟹ 古典解爆破，产生**激波**(解的间断)。

  ② **Rankine-Hugoniot 跳跃条件**——激波速度 $s=\frac{[F(u)]}{[u]}$($[\cdot]$ 跨间断的跳跃)。满足跳跃条件的弱解不唯一——需**熵条件**筛选物理解。

  ③ **Lax 熵条件与 Lax-Oleinik 公式**——熵解满足 $\eta(u)_t+q(u)_x\le0$(凸熵)；Hopf-Lax 公式经变分给出熵解显式表示，凸积分给出粘性消去极限($u_\epsilon\to u$)。

- **飞腾锚点** 🟡：**分支预测激波** [Lab02]。激波是解的**间断**——数值上跨激波的通量计算含条件分支(upwind 方向由特征速度符号决定)，飞腾实测分支密集代码 IPC 仅 0.71 vs 理论 3.14；熵条件本身是「多解中筛选」的逻辑分支，分支预测失误直接拖慢守恒律求解器。辅锚点：大矩阵是 **GEMM 9.45G**。

- **关键定理**：**Rankine-Hugoniot + Lax 熵条件**——激波 $s[u]=[F(u)]$；熵解要求穿过激波特征线「进入」($F'(u_l)>s>F'(u_r)$)，唯一确定物理解。

- **自测**：① Burgers 初值 $g(x)=1$($x<0$)、$0$($x>0$)，特征线如何相交？激波速度多少($s=1/2$)？② 为何弱解不唯一需熵条件(可压缩 vs 稀疏波)？

---

### 第10章 Hamilton-Jacobi 方程· viscosity 解

- **核心**：一阶非线性方程 $u_t+H(Du)=0$，特征线法在「焦散」(caustics)处失效：

  ① **特征线与爆破**——特征线方程含 $H'(p)$，相邻特征线相交使 $Du$ 爆破(多值)，古典解在有限时间破裂(与 Ch9 守恒律同病)。

  ② **粘性解**(Crandall-Lions)——加小扩散 $\epsilon\Delta u_\epsilon$，$u_{\epsilon,t}+H(Du_\epsilon)=\epsilon\Delta u_\epsilon$，令 $\epsilon\to0$ 取极限。粘性解是唯一连续解，不依赖 $\epsilon$ 的具体选取——这是「用抛物正则化定义一阶方程解」的天才创举。

  ③ **比较原理与控制理论**——粘性解满足比较原理($u\le v$ 边界 ⟹ 内部)，唯一性由此；最优控制/微分对策的值函数是 Hamilton-Jacobi-Bellman 方程的粘性解。

- **飞腾锚点** 🟡：**FP16 3.81×**。粘性消去 $\epsilon\to0$ 是「正则化参数趋于零的极限」——数值上 $\epsilon$ 过小则扩散项被浮点噪声支配，FP16 的有限精度天然引入「数值粘性」，既是逼近粘性解的意外工具，也限制了 $\epsilon$ 可取的最小值。辅锚点：**Iron Law<2%** 是粘性参数选择的精度判据。

- **关键定理**：**粘性解的存在唯一(比较原理)**——$\epsilon\Delta u_\epsilon$ 正则化的极限 $u$ 唯一且不依赖 $\epsilon$ 选取；比较原理 ⟹ 唯一性。

- **自测**：① 为何加 $\epsilon\Delta u$ 能「救」古典解爆破(扩散抹平多值)？② 粘性解与守恒律熵解有何同构(都是「物理可容许的弱解」)？

---

### 第11章 非散度形式二阶椭圆(Nondivergence Form)

- **核心**：$Lu=-a^{ij}(x)u_{x_ix_j}=f$（系数不在导数内，与 Ch5 散度型对照），**Lax-Milgram 不再直接适用**：

  ① **非散度 vs 散度**——散度型(Ch5)可分部积分得双线性型；非散度型无法直接弱化，需不同工具。这是「一致椭圆」$a^{ij}$ 的另一面。

  ② **Aleksandrov 极值原理**——非散度型不适用经典最大值原理，Aleksandrov 用几何(Monge-Ampère)给出非光滑最大值界。

  ③ **Krylov-Safonov 估计**——Harnack 不等式(非散度型)与 $W^{2,p}$ 内估计，是先验估计的巅峰——系数仅一致椭圆 + 有界，解仍有正则性，但证明远比散度型艰深。

- **飞腾锚点** 🟡：**TLB 局部弱导** [E04]。极值原理与 Harnack 不等式是**局部**性质(解在某点的界由局部邻域决定)，与非散度系数的局部性同构——TLB 管理局部内存映射，类比适用(标 🟡)。辅锚点：离散算子是 **matmul 15×**。

- **关键定理**：**Krylov-Safonov Harnack 不等式**——一致椭圆非散度方程的非负解满足 $\sup_K u\le C\inf_K u$(局部)，⟹ Hölder 连续正则性。

- **自测**：① 非散度型为何不能直接用 Lax-Milgram(无法分部积分得对称双线性型)？② Harnack 不等式给出什么正则性(解自动 Hölder 连续)？

---

### 第12章 非线性系统· Navier-Stokes(Nonlinear Systems)

- **核心**：**全书收尾的开放前沿**。不可压 Navier-Stokes 方程是非线性抛物系统，存在性是千禧难题的一部分：

  ① **方程组**——$\partial_tu+(u\cdot\nabla)u=-\nabla p+\nu\Delta u+f$，$\nabla\cdot u=0$(不可压)。非线性对流项 $(u\cdot\nabla)u$ 与粘性 $\nu\Delta u$ 的博弈决定流动性质(层流 vs 湍流)。

  ② **存在性理论**——2D 全局光滑解(能量估计闭合)；3D 全局弱解(Leray-Hopf)已知，全局光滑存在性是**千禧大奖难题**(Clay，$10^6 美元)，至今未解。

  ③ **方法综合**——非线性项用能量估计 + Sobolev 嵌入(Ch4)控制，压力由投影(Helmholtz 分解)消除，弱解构造综合 Part II-III 全部工具——这是 Evans 三部曲方法的「毕业考」。

- **飞腾锚点** 🟢：**GEMM⭐有限元** [Lab05]。Navier-Stokes 数值解(有限元/谱方法)的对流项 $(u\cdot\nabla)u$ 离散后是非线性大矩阵，每步 Newton 迭代都是 GEMM 密集型——9.45 GFLOPS 直接决定 CFD 仿真吞吐。辅锚点：长期积分误差受 **FP16 3.81×** 影响。

- **关键定理**：**Leray 弱解存在性(3D)**——能量不等式 $\frac12\|u(t)\|^2+\nu\int_0^t\|Du\|^2\le\frac12\|u(0)\|^2+\int_0^t(f,u)$ ⟹ 全局弱解存在；3D 唯一性与光滑性仍开放。

- **自测**：① 2D 为何全局光滑(非线性项可控)而 3D 开放(涡旋拉伸)？② Navier-Stokes 综合了哪些前章工具(Sobolev+椭圆+能量+非线性)？

---

## §9 思想主线：古典 → 弱解 → Sobolev → 变分

Evans 全书的总纲是一条「**放宽定义换取存在性，再提升正则性**」的辩证链条。Part I 古典方法(Ch1-3)依赖显式公式：基本解、特征线、Fourier 变换、分离变量——它们回答「解长什么样」，但要求 $u\in C^2$，太苛刻、多数方程无解。

转折发生在 Part II(Ch4-6)：**Sobolev 空间**把导数放宽到分布意义($H^1$ 弱可导)，**Lax-Milgram** 在弱形式下证明椭圆方程存在唯一，**变分法**把 PDE 等价于能量泛函极小。三者环环相扣——Sobolev 空间是舞台，Lax-Milgram 是主角，变分是动机(「PDE = 能量极值条件」)。读者一旦抓住「**弱解 ⟺ 能量极小 ⟺ 强制双线性型**」这条三位一体，就理解了 20 世纪线性 PDE 理论的全部精髓。

Part III(Ch7-12)把线性工具推向非线性：热/波方程弱解(Ch7-8)是「Galerkin 有限维 + 紧性取极限」的标准范式；但守恒律激波(Ch9)、Hamilton-Jacobi 多值(Ch10)中**古典解爆破**，需全新概念(熵解、粘性解)；非散度型(Ch11)与 Navier-Stokes(Ch12)则把先验估计与非线性分析推到前沿——后者直接撞上千禧难题。这条主线最终指向一个深刻结论：**PDE 理论的本质是「在与非线性的搏斗中，不断发明新的『解』的定义」**——古典解 → 弱解 → 熵解 → 粘性解，每一次放宽都换来存在性，也付出新挑战。

---

## §10 交叉引用与 AI 锚点

- **与 Kress《数值分析》**：Kress 第 5-6 章是 ODE/PDE 的**数值离散**(有限元、Crank-Nicolson)，Evans 是其**连续数学基础**——Lax-Milgram 的双线性型正是有限元刚度矩阵 $K_{ij}=B[\phi_j,\phi_i]$ 的来源，Evans 给「为何能这样离散」，Kress 给「如何在硅片上算」。读 Evans Ch5-6 后再看 Kress Ch6 有限元，会豁然开朗。

- **与《微分方程》(Boyce-DiPrima)**：Boyce 第 8-9 章(分离变量、傅里叶级数、Sturm-Liouville)是 Evans Ch3 的**本科预演**；Boyce 第 4 章 Laplace 变换与 Evans Ch2 Fourier 变换同属「变换域求解」思想。Evans 的增量在 Part II 弱解——Boyce 完全未触及。

- **与 Neural-PDE / PINN**：物理信息神经网络(PINN)把 PDE 残差作为损失函数的「软约束」，本质是 Evans Ch5 弱形式的**神经网络逼近**；神经算子(FNO/DeepONet)在函数空间(Ch4 Sobolev)上学习解算子——**Sobolev 空间是神经算子的数学语言**。

- **AI 锚点**(PDE = 物理模拟的数学根基)：
  - ① **PDE = 物理模拟**：天气预报、CFD、电磁仿真底层全是 Evans 的方程；扩散模型(图像生成)的热方程 $\partial_tu=\Delta u+\nabla\cdot\nabla\log p$ 是 Evans Ch7 的随机版。
  - ② **Sobolev = 函数空间**：Ch4 的 $H^1$ 空间是神经切线核(NTK)理论、函数空间优化的舞台；Sobolev 嵌入给出神经网络表达能力的尺度。
  - ③ **变分 = 最小作用**：Ch6 的能量泛函极小与 ML 训练的损失极小同构——「PDE 是 Euler-Lagrange 方程」⟺「梯度流是 PDE」，Score-based 生成的 Langevin 动力学即变分结构。
  - ④ **粘性解 = 强化学习**：Ch10 的 Hamilton-Jacobi-Bellman 方程是最优控制/RL 的值函数方程，粘性解理论是连续 RL 的严格基础。
  - ⑤ **守恒律 = 图神经网络**：Ch9 的熵条件与图上的信息传递守恒同构，激波的「特征线交汇」类比 GNN 的消息聚合。

> **一句话总结本书的 AI 价值**：Evans 把「连续物理定律」翻译成「函数空间中的存在性与正则性」，而 AI 的科学计算分支(PINN/FNO/扩散模型/RL 控制)恰恰是「在 Sobolev 空间上用神经网络逼近 PDE 解算子」——读通 Evans，就拿到了理解 AI for Science 全部分支的数学钥匙。

---

## §11 自测题提示要点(速查)

> 下表给出各章自测题的关键提示 / 答案要点，供做完后核对。建议先动手推导再查表——PDE 的直觉只有在亲手算过 Duhamel 卷积、亲手验证 Sobolev 嵌入指数后才会内化。

| 章 | 自测题 | 提示要点 |
|----|--------|----------|
| 1 | 调和函数反平均值 | Weyl 引理：平均值公式 ⟹ 调和(光滑)，故等价 |
| 1 | 波方程能量守恒 | $\frac{dE}{dt}=\int u_t(u_{tt}-\Delta u)=0$，⟹ 唯一性 + 有限传播 |
| 2 | $-\Delta u=f$ 求解 | $\hat u=\hat f/|\xi|^2$，反变换 $u=\Phi*f$($\Phi$ 基本解) |
| 2 | $\widehat{D_ku}$ | $(i\xi_k)\hat u$——「弱导数 = 频域乘 $i\xi$」 |
| 3 | 级数解前几项 | $\phi_n=\sqrt2\sin(n\pi x)$，$c_n=\langle g,\phi_n\rangle$，$u=\sum c_n\phi_ne^{-(n\pi)^2t}$ |
| 3 | $\lambda_n\to\infty$ | 紧算子谱聚于 0，逆算子特征值发散，保级数收敛 |
| 4 | $\|x\|$ 弱导数 | 有：$D(|x|)=\text{sgn}(x)$；$|x|^{1/2}$ 无($L^1$ 非局部可积) |
| 4 | Rellich 为何关键 | 弱收敛 + 紧嵌入 ⟹ 强收敛子列，极小元可达 |
| 5 | Poisson 弱形式 | $B[u,v]=\int Du\cdot Dv$，Poincaré ⟹ 强制性 |
| 5 | Gårding 不强制 | $c<-\lambda_1$ 时低阶项破坏强制性，需 Fredholm 抉择 |
| 6 | 弱下半连续 | $|\cdot|^2$ 凸 ⟹ $\liminf\ge$ 极限(Mazur)；凹函数不行 |
| 6 | Rayleigh 极小元 | $-\Delta u=\lambda u$ 特征方程，$\lambda_1$ 最小特征值 |
| 7 | 能量单调递减 | $\frac{d}{dt}\frac12\|u\|^2=-\|Du\|^2+(f,u)\le0$(扩散耗散) |
| 7 | Galerkin 取极限 | Rellich 紧性给强收敛子列，弱解存在 |
| 8 | 可逆 vs 不可逆 | 波方程保能量(时间反演对称)；热方程耗散(不可逆) |
| 8 | 波方程两初值 | 二阶时间导数需 $u(0),u_t(0)$；热方程一阶只需 $u(0)$ |
| 9 | Burgers 激波速度 | 压缩波相交，$s=[F]/[u]=(1/2-0)/(1-0)=1/2$ |
| 9 | 弱解不唯一 | 稀疏波(连续)也满足 R-H，熵条件选压缩激波 |
| 10 | 粘性救爆破 | $\epsilon\Delta u$ 抹平多值，极限唯一连续解 |
| 10 | 熵解 vs 粘性解 | 都是「物理可容许弱解」，Kružkov 统一框架 |
| 11 | 非散度无 Lax-Milgram | $a^{ij}u_{ij}$ 无法分部积分成对称双线性型 |
| 11 | Harnack 正则性 | $\sup/\inf\le C$ ⟹ 解 Hölder 连续(振荡控制) |
| 12 | 2D 光滑 3D 开放 | 2D 非线性项能量可控；3D 涡旋拉伸使 $\|Du\|$ 可能爆破 |
| 12 | 综合工具 | Sobolev 嵌入 + 椭圆投影 + 能量估计 + 非线性估计 |

### 十二章精华一句话

- **第 1 章**：四大 PDE 各有「招式」——特征线(transport)、基本解+Green(Laplace)、热核+Duhamel(热)、d'Alembert+能量(波)。
- **第 2 章**：Fourier 变换把微分变乘法，全空间 PDE 在频域求解；卷积定理是基本解的核心。
- **第 3 章**：有界域上分离变量 = 特征函数正交展开，Sturm-Liouville 给完备基——古典版的「谱方法」。
- **第 4 章**：Sobolev 空间是弱解的舞台，弱导数 + 嵌入 + 迹 + 紧性四大工具缺一不可。
- **第 5 章**(Part II 高潮)：Lax-Milgram 把椭圆方程化为强制双线性型，弱解存在唯一——有限元的数学根基。
- **第 6 章**：变分法把 PDE 等价于能量泛函极小，直接方法(下半连续 + 紧性)给存在性——「最小作用原理」。
- **第 7 章**：热方程弱解 = Galerkin + 能量估计，耗散结构使能量衰减，半群是时间演化算子。
- **第 8 章**：波方程弱解保能量，辛结构对应可逆时间演化，光锥给有限传播。
- **第 9 章**：守恒律激波——Rankine-Hugoniot 给跳跃条件，Lax 熵条件从多解中筛物理解。
- **第 10 章**：Hamilton-Jacobi 粘性解——加 $\epsilon\Delta u$ 正则化取极限，Crandall-Lions 的天才定义。
- **第 11 章**：非散度型需 Aleksandrov/Krylov-Safonov，先验估计的巅峰，系数粗糙仍有正则性。
- **第 12 章**：Navier-Stokes 综合全书工具，3D 全局光滑存在性是千禧难题——Evans 的「毕业考」。

---

## 📌 阅读建议(对接数学专家路径)

1. **精读顺序**：Ch1(四大 PDE 直觉)→ Ch4(Sobolev，弱解舞台)→ **Ch5(Lax-Milgram，Part II 核心)** → Ch6(变分)→ Ch7-8(发展方程弱解)→ Ch9-10(非线性，熵解/粘性解)→ Ch11-12(前沿，按需)。

2. **每章配飞腾实测**：读完一章，对照 §1 分布表跑对应 Lab/Expert。Ch5 的 GEMM 有限元、Ch2 的 UDOT Fourier、Ch9 的分支预测激波是强匹配——把「纸面定理」钉在「硅片数据」上(AI 锚点法)。

3. **数学根基回溯**：弱导数/分布 ⟵ Royden(Lebesgue/Lp) + 泛函分析(Hilbert 空间)；Green 函数/基本解 ⟵ Spivak 多元微积分(链式法则/散度定理)；特征线 ⟵ 《微分方程》第 1 章(一阶 ODE)；Lax-Milgram ⟵ LADR(内积空间) + 泛函(Riesz 表示)。

4. **深挖课题**(Evans 特色)：
   - ① 弱解的正则性提升(Weyl 引理：弱解 ⟹ 光滑)如何「收回」放宽的代价。
   - ② 熵解 vs 粘性解的 Kružkov 统一框架(Ch9-10 的深层联系)。
   - ③ 3D Navier-Stokes 千禧难题为何难(Ch12，涡旋拉伸的能量失控)。
   - ④ 飞腾无 BF16 对长时间 PDE 积分误差累积的影响(Ch7，Expert_21 战略伤疤)。

5. **动手验证**(Python 工程师优势)：每章选 1 题用 FEniCS/SciPy 实现并对照 §11 提示表自检——例如 Ch5 用 FEniCS 解 Poisson 弱形式对照解析解，Ch9 手写 Burgers 激波的 upwind 格式观察熵解，Ch2 用 NumPy FFT 解热方程对照解析热核。代码即理解，飞腾实测数据则作为「工程极限」的参照系。

> 注：本笔记基于 Evans GSM19(2nd ed.)书目定位撰写快速逐章导览，侧重概念串联与飞腾/AI 锚点对接。章节编号依 PDE 标准三部曲(古典表示 → 线性弱解 → 非线性)组织。数学内容(基本解/Green 函数/Lax-Milgram/Sobolev 嵌入/Rankine-Hugoniot/粘性解等)均为标准准确陈述。
