# David Gilbarg, Neil S. Trudinger《二阶椭圆偏微分方程》(GTM 224) · 快速逐章精读

> 基于原书：*Elliptic Partial Differential Equations of Second Order*, Grundlehren der math. Wissenschaften 224（David Gilbarg & Neil S. Trudinger, Springer, 2nd ed., 1983 / 2001 reprint）/ 读于：2026-07-03
> 定位：**二阶椭圆 PDE 的「圣经」**，以「Schauder 经典 + Sobolev 弱解」双轴统一椭圆理论，从调和函数到拟线性方程的全谱覆盖。
> 关联：[Evans PDE](evans_PDE偏微分方程_快速逐章.md) · [Hörmander ALPDO I](hormander_线性偏微分算子I_快速逐章.md) · [Folland 实分析](../stage-2-研究生基础/folland_实分析_快速逐章.md) · [Reed-Simon I](../stage-2-研究生基础/reed_simon_数学物理方法I_快速逐章.md)
> 本文为**快速逐章精读**，每主题 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

> 📌 **章节合并说明**：原书第二版（2001 reprint）共 **16 章**。本笔记合并为 **10 个主题**（Ch 1–2 合并、Ch 5–6 合并、Ch 10–11 合并、Ch 12–13 合并、Ch 14–16 合并），保留原书章节号以便回溯。每主题标注对应原章节。

---

## §0 引言：椭圆 PDE 圣经的「双轴统一」

二阶椭圆偏微分方程是数学物理的核心语言——Laplace 方程描述电势与稳定温度场，Poisson 方程描述引力势，极小曲面方程描述肥皂膜形状。David Gilbarg（斯坦福）与 Neil Trudinger（ANU）合著的本书（Springer GTM 224，初版 1977，第二版 1983，2001 重印增补 Krylov-Safonov 理论）被公认为**二阶椭圆 PDE 领域的圣经**——它不是某一类技巧的汇编，而是用两条独立而互补的主轴把整个二阶椭圆理论统一起来。

**双轴之一：Schauder 经典框架（Ch 2–6）**。从 Laplace 方程的调和函数出发，经最大值原理、Newton 位势、Hölder 空间 $C^{k,\alpha}$，抵达 **Schauder 估计**——用系数与右端的 Hölder 范数控制解的 $C^{2,\alpha}$ 范数。这套理论要求系数 Hölder 连续，给出「经典解」的全套先验估计。

**双轴之二：Sobolev 弱解框架（Ch 7–9, 12–13）**。从 $W^{k,p}$ 空间出发，经弱解定义，抵达两条顶峰结果：**De Giorgi-Nash-Moser 正则性**（散度型方程弱解自动 Hölder 连续，系数只需有界可测！——Schauder 做不到）与 **Calderón-Zygmund $W^{2,p}$ 估计**（非散度型方程强解的二阶导数估计）。第二版新增 **Krylov-Safonov Harnack 不等式**（非散度型弱解），补全了双轴。

两条轴线在 Ch 10–11 的非线性方法（Schauder / Leray-Schauder 不动点）处汇合，最终通向 Ch 14–16 的拟线性方程与方程组。一句话：GT 用「经典 Hölder + 弱解 Sobolev」两把钥匙，打开了二阶椭圆 PDE 的大门。

### 四本 PDE / 分析教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|------|------|--------|--------|
| **GT 224（本书）** | 椭圆 PDE 全谱「圣经」；经典 Schauder + 弱解 Sobolev 双轴；先验估计中心 | ★★★★★（逐条定理给完整证明） | 椭圆 PDE / 几何分析研究者 |
| **Evans PDE（GSM 19）** | 现代研究生标准；弱解三部曲（椭圆/抛物/双曲）应用驱动 | ★★★★（严格但重存在性直觉） | PDE 研究生入门首选 |
| **Hörmander ALPDO I** | 线性 PDE 皇冠；分布论 + Fourier 分析 + 波前集严格重建 | ★★★★★（极严，逐条重建语言） | PDE/分析方向研究深造 |
| **Han-Lin《椭圆 PDE》** | 精炼现代讲义（Courant/AMS）；直奔正则性与先验估计，证明干净 | ★★★★（简洁但非自包含） | 已入门者快速复习椭圆理论 |

> **阅读策略**：Evans PDE 入门建立弱解直觉 → **GT 224 做椭圆专精**（补全 Schauder 全谱 + DGNM/CZ 顶峰）→ Hörmander I 回溯分布论严格地基。三者构成 PDE「三套马车」：Evans 是「地图」，GT 是「椭圆专精」，Hörmander 是「语言地基」。

---

## §1 全书 10 主题骨架一览（飞腾锚点分布）

GT 全书主线是「**两条独立轴线 + 非线性汇合 + 拟线性应用**」。主题 1–4 是 Schauder 经典轴，主题 5–7 是 Sobolev 弱解轴，主题 8 汇合非线性方法，主题 9–10 推向拟线性与方程组。每主题对接一条飞腾实测锚点。

| 主题 | 原章 | 标题 | 核心概念 | 飞腾锚点 |
|:----:|:----:|------|---------|:--------:|
| 1 | Ch 1–2 | 椭圆方程分类与 Laplace 方程 | 一致椭圆条件 · 均值定理 · Harnack | UDOT 16.9×⭐ 🟢 |
| 2 | Ch 3 | 最大值原理 | 弱/强最大值 · Hopf 引理 · 比较原理 | 分支预测 🟡 |
| 3 | Ch 4 | Poisson 方程与 Newton 位势 | 基本解 · 位势表示 · 奇异积分先声 | matmul 15× 🟢 |
| 4 | Ch 5–6 | Hölder 空间与 Schauder 估计 | $C^{k,\alpha}$ · **Schauder 内/边界估计** · 连续性方法 | Iron Law<2%⭐ 🟡 |
| 5 | Ch 7 | Sobolev 空间 | $W^{k,p}$ · **嵌入定理** · 迹 · Poincaré | Schmidt 🟡 |
| 6 | Ch 8 | 广义解与正则性 | 弱解 · **De Giorgi-Nash-Moser** · 散度型 Harnack | TLB 4.81×⭐ 🟢 |
| 7 | Ch 9 | 强解 · Calderón-Zygmund | $W^{2,p}$ · **CZ 分解** · 奇异积分 $L^p$ 有界 | FP16 3.81×⭐ 🟡 |
| 8 | Ch 10–11 | 非线性方法与不动点 | Schauder 不动点 · **Leray-Schauder 度** | GEMM 9.45G 🟢 |
| 9 | Ch 12–13 | 弱解最大值与 Harnack | **ABP 估计** · **Krylov-Safonov Harnack** | UDOT 16.9×⭐ 🟢（复用） |
| 10 | Ch 14–16 | 拟线性方程与方程组 | 梯度估计 · 极小曲面 · **de Giorgi 反例** | TLB 4.81×⭐ 🟡（复用） |

```
Schauder 经典轴（系数 Hölder 连续 ⟹ 经典解 C^{2,α}）
主题1 椭圆分类+Laplace ── 一致椭圆·均值定理·Harnack ─────────────┐
主题2 最大值原理 ─────── 弱/强最大值·Hopf 引理·比较原理 ──────────┤
主题3 Poisson+Newton ── 基本解 Γ=|x|^{2-n}·位势表示·奇异积分先声 ─┤
主题4 Hölder+Schauder ── C^{k,α}·Schauder 估计·连续性方法（存在性）┘
         ╳ 双轴汇合
Sobolev 弱解轴（系数有界可测 ⟹ 弱解自动 C^α）
主题5 Sobolev 空间 ────── W^{k,p}·嵌入 W^{k,p}↪C^{m,α}·迹·Poincaré ─┐
主题6 广义解+DGNM ────── 弱解·De Giorgi-Nash-Moser 正则性·散度Harnack┤
主题7 强解+CZ ────────── W^{2,p}·Calderón-Zygmund 分解·奇异积分 L^p ──┘
         ╳
主题8 非线性方法 ──────── Schauder 不动点·Leray-Schauder 度（线性⟹拟线性）
主题9 弱解最大值+Harnack ─ ABP 估计·Krylov-Safonov Harnack（非散度型）
主题10 拟线性+方程组 ──── 梯度估计·极小曲面·de Giorgi 反例（方程组障碍）

数学根基：Folland 实分析(测度/Lp) · Reed-Simon I(算子/Hilbert)
         ·Hörmander I(分布论) · Evans PDE(弱解直觉)
```

---

### 主题 1 · 椭圆方程分类与 Laplace 方程（Ch 1–2）

- **核心**：GT 的起点是把「二阶椭圆方程」统一成一个抽象对象：

  $$Lu = a^{ij}(x)D_{ij}u + b^i(x)D_i u + c(x)u = f(x)$$

  配**一致椭圆条件** $a^{ij}(x)\xi_i\xi_j \ge \lambda|\xi|^2$（$\lambda>0$）。Laplace 方程 $\Delta u=0$ 是一切的原型。本章用**均值定理**（球面上积分均值 = 中心值）推出调和函数的整套经典性质：

  ① **解析性**——调和函数自动实解析（局部幂级数展开）。
  ② **Liouville 定理**——$\mathbb{R}^n$ 上有界调和函数必常数。
  ③ **Harnack 第一不等式**——正调和函数在紧集上上下有界 $\sup_K u\le C\inf_K u$。

  GT 把 Laplace 方程当作「标尺」——后续所有估计都先在 Laplace 上验证，再推广到变系数。
- **飞腾锚点** 🟢：**UDOT 16.9×⭐** [E05]。均值定理 $u(x)=\frac{1}{|\partial B_R|}\int_{\partial B_R(x)}u\,dS$ 是**球面上的点积累加求和**——离散后每个 $x$ 处是一次内积（权重积分），飞腾 INT8 UDOT 点积指令对批量均值求和加速 16.9×。这是全书最强的「数学↔硬件」匹配：均值 = 点积求和。标 🟢（事实：均值定理本质就是加权求和）。
- **关键定理**：**均值定理**——$u$ 调和 $\Leftrightarrow$ 对所有球 $B_R(x)\Subset\Omega$，

  $$u(x)=\frac{1}{n\omega_n R^{n-1}}\int_{\partial B_R(x)}u\,dS.$$

  **Harnack 不等式**：$u\ge0$ 调和 $\Rightarrow \sup_{B_R}u\le C\inf_{B_R}u$（$C=C(n)$）。
- **自测**：① 验证 $u(x)=|x|^{2-n}$ 在 $\mathbb{R}^n\setminus\{0\}$ 调和（$n\ge3$）。② 用均值定理证明调和函数必解析（均值 = 多项式卷积 ⟹ 实解析）。

---

### 主题 2 · 最大值原理（Ch 3）

- **核心**：最大值原理是椭圆方程「**边界决定全局**」的严格化身，也是后续先验估计与比较原理的基石。三步递进：

  ① **弱最大值原理**——$c\le0$ 时 $\sup_\Omega u\le\sup_{\partial\Omega}u^+$：解的最大值不出边界。
  ② **强最大值原理**——除非 $u$ 恒常数，否则内部取不到严格最大值。
  ③ **Hopf 边界引理**——边界最大值点的外法向导数严格正。

  Hopf 引理是把内部信息与边界条件连接的关键——它把「在边界达到极值」强化为「法向导数有固定符号」，从而推导出比较原理与唯一性。
- **飞腾锚点** 🟡：**分支预测** [Lab02]。最大值原理的判定本质是**符号 yes/no 分类**——$u$ 在边界 vs 内部何处取最大、$\partial u/\partial\nu$ 正负如何，是一连串条件分支。分支预测器的可预测分支（0.71 CPI）vs 误预测（3.14 CPI）对应「常数解（平凡最大值）」与「非常数解（Hopf 严格不等式）」的分野。标 🟡（类比）。
- **关键定理**：**Hopf 引理**——若 $u\in C^2(\Omega)\cap C^1(\bar\Omega)$ 在 $x_0\in\partial\Omega$ 处达到严格最大值，且 $\Omega$ 在 $x_0$ 满足内部球条件，则

  $$\frac{\partial u}{\partial\nu}(x_0)>0$$

  （$\nu$ 为外法向）。
- **自测**：① 用 Hopf 引理证明 Dirichlet 问题 $\Delta u=f$，$u|_{\partial\Omega}=\varphi$ 的解唯一。② 弱最大值原理为何要求 $c\le0$（$c>0$ 时举反例 $u=\sin x$ 在 $(0,\pi)$ 上）。

---

### 主题 3 · Poisson 方程与 Newton 位势（Ch 4）

- **核心**：Newton 位势是 Laplace 基本解

  $$\Gamma(x-y)=\frac{1}{n(2-n)\omega_n}|x-y|^{2-n}\quad(n\ge3),$$

  它是 Poisson 方程 $-\Delta u=f$ 的「解算子」：$u(x)=\int_\Omega\Gamma(x-y)f(y)\,dy$。本章的核心难题是**位势的可微性**——$u=\Gamma*f$ 何时有二阶连续导数？对 $D_{ij}u$ 形式求导得到**奇异积分** $\int D_{ij}\Gamma(x-y)f(y)\,dy$（核在 $y=x$ 有 $|x-y|^{-n}$ 奇异），其收敛性需要精细分析——这正是 Ch 9（Calderón-Zygmund）的先声。GT 先在 $f\in C^\alpha_c$ 下证明 $D_{ij}u$ Hölder 连续（Schauder 局部版的预备）。
- **飞腾锚点** 🟢：**matmul 15×** [V03]。Newton 位势 $u(x)=\int\Gamma(x-y)f(y)\,dy$ 离散后是**密集核矩阵** $\Gamma_{ij}=\Gamma(x_i-y_j)$ 乘以向量 $f$——正是 matmul。对 $N$ 个源点、$M$ 个场点，计算量 $O(NM)$，飞腾 matmul 15× 向量化增益直接加速。标 🟢（位势积分 ⟺ 矩阵向量乘）。
- **关键定理**：**Newton 位势正则性**——$f\in C_c^\alpha(\mathbb{R}^n)$（$0<\alpha<1$）$\Rightarrow$ $D_{ij}u$ 存在且满足

  $$\|D_{ij}u\|_{C^\alpha(B_R)}\le C\|f\|_{C^\alpha}.$$

  （$i,j$ 任意；这是 CZ 奇异积分 $L^p$ 理论的 Hölder 先声。）
- **自测**：① 显式验证 $-\Delta(\Gamma*f)=f$（对 $f\in C_c^\infty$，用分布意义）。② 位势 $u(x)=\int_{B_1}\Gamma(x-y)\,dy$ 在 $x=0$ 处二阶导数为何存在但「勉强」连续（奇异积分的临界性）？

---

### 主题 4 · Hölder 空间与 Schauder 估计（Ch 5–6）★ Schauder 经典轴核心

- **核心**：本章是 Schauder 经典框架的顶点。Ch 5 定义 **Hölder 空间** $C^{k,\alpha}(\bar\Omega)$——$k$ 阶导数 Hölder 连续（指数 $\alpha\in(0,1)$），配插值范数成为 Banach 空间。Ch 6 推出**全书最核心的先验估计——Schauder 估计**：

  $$\|u\|_{C^{2,\alpha}}\le C(\|u\|_{C^0}+\|f\|_{C^\alpha}).$$

  Schauder 估计的本质是「**系数与右端的正则性传递给解**」——$f\in C^\alpha$ 且 $a^{ij}\in C^\alpha$ 则 $u\in C^{2,\alpha}$，增益两阶导数。配合**边界估计**（球上 + 边界展平）与**连续性方法**（continuity method：沿参数族 $t\in[0,1]$ 从已知解延拓），GT 给出 Dirichlet 问题的存在唯一性。这是「先验估计 ⟹ 存在性」的典范范式。
- **飞腾锚点** 🟡：**Iron Law<2%⭐**。Schauder 估计 $\|u\|_{C^{2,\alpha}}\le C(\|u\|_{C^0}+\|f\|_{C^\alpha})$ 是一条**误差控制铁律**——常数 $C$ 衡量「输入正则性 ⟹ 输出正则性」的放大率，对应 Iron Law 的「性能 = 指令数 × CPI × 时钟」中 CPI 误差须压进 <2% 预算。$C$ 过大意味着数值不稳定（误差被放大），这正是 Schauder 估计作为「稳定性保证」的工程意义。标 🟡。
- **关键定理**：**Schauder 内估计**——$Lu=f$（$a^{ij}\in C^\alpha$ 一致椭圆），$\Omega'\Subset\Omega$ $\Rightarrow$

  $$\|u\|_{C^{2,\alpha}(\Omega')}\le C(\|u\|_{C^0(\Omega)}+\|f\|_{C^\alpha(\Omega)}),$$

  $C=C(n,\lambda,\Lambda,\Omega',\Omega)$。**全局边界估计** + 连续性方法 ⟹ Dirichlet 问题 $\exists!$ 解 $u\in C^{2,\alpha}(\bar\Omega)$。
- **自测**：① 连续性方法如何把 Schauder 估计（先验）转为存在性（后验）？（提示：$L_t=(1-t)\Delta+tL_0$，解集开 + 闭 ⟹ 全 $[0,1]$。）② 为何 Schauder 要求 $a^{ij}\in C^\alpha$ 而 DGNM（主题 6）不要求系数连续？

---

### 主题 5 · Sobolev 空间（Ch 7）

- **核心**：从经典 Hölder 框架切换到现代 Sobolev 框架——$W^{k,p}(\Omega)$ 定义为有 $k$ 阶**弱导数**（分布意义下分部积分成立）且 $L^p$ 可积的函数。本章三大支柱：

  ① **Sobolev 嵌入定理**——$W^{k,p}\hookrightarrow L^q$（$1/q=1/p-k/n$）；$kp>n$ 时 $\hookrightarrow C^{m,\alpha}$，即 **Morrey 嵌入**：弱导数足够多则解自动连续乃至 Hölder。
  ② **迹定理**——$W^{1,p}(\Omega)\to L^p(\partial\Omega)$，给边界值赋予意义。
  ③ **Poincaré 不等式**——$\|u-u_\Omega\|_{L^p}\le C\|\nabla u\|_{L^p}$，消去常数自由度。

  Sobolev 空间是后续弱解理论（主题 6–7）与散度型椭圆方程的函数空间基底。
- **飞腾锚点** 🟡：**Schmidt 正交化**。Sobolev 嵌入 $W^{k,p}\hookrightarrow L^q$ 的证明依赖**投影 / 平均化 / 局部坐标展平**——本质是把函数分量重新组合到「好的基」上，与 Gram-Schmidt 正交分解的思想同源：迹定理的投影到边界 = 向子空间投影；Morrey 嵌入的逐点估计来自「代表球上的平均 ⟹ 连续性」的投影论证。标 🟡（类比）。
- **关键定理**：**Morrey 嵌入定理**——$u\in W^{1,p}(\Omega)$，$p>n$ $\Rightarrow$ $u$ Hölder 连续（$u\in C^{0,\,1-n/p}$）。一般：

  $$kp>n\;\Rightarrow\;W^{k,p}\hookrightarrow C^{k-[n/p]-1,\;\alpha},\quad \alpha=[n/p]+1-n/p.$$
- **自测**：① 判定 $u(x)=|x|^{-\beta}$ 属于 $W^{1,p}(B_1)$ 的条件（答：$\beta<1-n/p$）。② 用 Poincaré 不等式证明 $W^{1,2}_0(\Omega)$ 中的 $\|\nabla u\|_{L^2}$ 与 $\|u\|_{W^{1,2}}$ 等价范数。

---

### 主题 6 · 广义解与 De Giorgi-Nash-Moser 正则性（Ch 8）★ 弱解轴核心

- **核心**：本章是 GT 弱解框架的**灵魂**。**弱解**定义为分部积分意义下满足

  $$\int_\Omega A\nabla u\cdot\nabla\varphi\,dx=0\quad(\forall\varphi\in C_c^1)$$

  的 $u\in W^{1,2}$。核心难题：系数矩阵 $A(x)$ 只**有界可测**（一致椭圆但不要求连续），弱解有多正则？**De Giorgi-Nash-Moser 定理**给出震惊数学界的结果——弱解**自动 Hölder 连续** $u\in C^\alpha_{\mathrm{loc}}$！这是 Schauder 框架（要求 $a^{ij}\in C^\alpha$）做不到的。方法是 De Giorgi 的「截断 + Caccioppoli 能量估计 + 迭代」，不依赖 Fourier 分析，是 GT 的招牌。配套的**散度型 Harnack 不等式**（$u\ge0$ 弱调和 ⟹ $\sup\le C\inf$）也在本章。
- **飞腾锚点** 🟢：**TLB 4.81×⭐** [E04]。DGNM 正则性的证明核心是**逐球的局部能量估计**（Caccioppoli 不等式 $\int_{B_r}|\nabla u|^2\le C/r^2\int_{B_{2r}}|u|^2$），每个球的估计独立于全局——这与 TLB 管理「局部页」的内存局部性同构：截断函数把全局弱形式限制到球 $B_r$（= 缓存页），4.81× 命中增益正来自局部访问。标 🟢（事实：Caccioppoli 估计就是局部化截断）。
- **关键定理**：**De Giorgi-Nash-Moser 正则性**——$A(x)$ 有界一致椭圆，$u\in W^{1,2}$ 弱解 $\mathrm{div}(A\nabla u)=0$ $\Rightarrow$ $u\in C^\alpha_{\mathrm{loc}}$（$\alpha=\alpha(n,\lambda/\Lambda)>0$）。**散度型 Harnack**：

  $$u\ge0\text{ 弱调和}\;\Rightarrow\;\sup_{B_R}u\le C\inf_{B_R}u.$$
- **自测**：① DGNM 为何比 Schauder「更强」（系数要求更低）？（提示：有界可测 $\supset$ Hölder 连续。）② Caccioppoli 估计中截断函数 $\eta$ 的选取为何关键（$\eta$ 在 $B_r$ 内为 1、$B_{2r}$ 外为 0 的过渡层控制误差）。

---

### 主题 7 · 强解与 Calderón-Zygmund（Ch 9）★ 弱解轴顶峰

- **核心**：强解 $u\in W^{2,p}$ 是「二阶导数 $L^p$ 存在」的解。本章顶峰是 **Calderón-Zygmund $W^{2,p}$ 估计**——非散度型方程 $Lu=f$（$a^{ij}$ 连续）满足 $\|D^2 u\|_{L^p}\le C\|f\|_{L^p}$（$1<p<\infty$）。证明工具是 **Calderón-Zygmund 分解**：

  把 $L^p$（或 $L^1$）函数分解成「好的」（小）+「坏的」（大但稀疏）二部份，对坏部份做二进方体分解。

  核心是**奇异积分算子** $Tf(x)=\mathrm{p.v.}\int K(x-y)f(y)\,dy$（核 $K$ 有 $|x|^{-n}$ 奇异，如 Riesz 变换）的 $L^p$ 有界性（$1<p<\infty$；$p=1,\infty$ 失败）。这把 Schauder 的 Hölder 估计「翻译」成 $L^p$ 语言。
- **飞腾锚点** 🟡：**FP16 3.81×⭐** [L01]。CZ 奇异积分的核 $|x-y|^{-n}$ 在 $y\to x$ 处奇异，数值上需主值截断（p.v.）——FP16（$\varepsilon\approx9.8\times10^{-4}$）下近奇异点的高频误差被放大，3.81× 速度差背后是「精度-截断半径」权衡。$p=1,\infty$ 失败对应「弱型估计」的精度边界（Marcinkiewicz 插值需 $1<p<\infty$）。标 🟡。
- **关键定理**：**CZ $W^{2,p}$ 估计**——$a^{ij}\in C^0$ 一致椭圆，$Lu=f\in L^p$，$u\in W_0^{2,p}(\Omega)$ $\Rightarrow$

  $$\|u\|_{W^{2,p}}\le C\|f\|_{L^p}\quad(1<p<\infty).$$

  **奇异积分 $L^p$ 有界性**：Riesz 变换 $R_j$ 在 $L^p$ 有界（$1<p<\infty$），$p=1,\infty$ 无界。
- **自测**：① 为何 CZ 分解对 $p=1$ 只能给出弱型（$L^{1,\infty}$）而非强 $L^1$？② Hilbert 变换（$n=1$ 的 Riesz 变换）在 $L^\infty$ 上无界——给出反例 $f=\mathrm{sgn}$。

---

### 主题 8 · 非线性方法与不动点定理（Ch 10–11）

- **核心**：本章是线性理论通向拟线性的**桥梁**。核心思路：把非线性方程的不动点化为线性算子的不动点。两大工具：

  ① **Schauder 不动点定理**——紧凸集 $K$ 到自身的连续映射 $T:K\to K$ 有不动点。直接给出半线性方程 $-\Delta u=g(x,u)$ 解的存在性（把线性解算子 $(-\Delta)^{-1}$ 与非线性项复合成 $T$）。
  ② **Leray-Schauder 度**——有限维 Brouwer 度的无穷维推广，给拓扑度理论：它度量「映射在区域内零点的代数个数」，满足同伦不变性（连续形变下度不变）。用于拟线性方程的存在性（先验界 ⟹ 度非零 ⟹ 解存在），是 Ch 14–15 拟线性理论的核心工具。
- **飞腾锚点** 🟢：**GEMM 9.45G** [Lab05]。不动点迭代 $u_{k+1}=T(u_k)$ 的每一步本质是求解一个线性椭圆方程（$-\Delta u_{k+1}=g(x,u_k)$），离散后是大矩阵求逆 / GEMM。大规模 PDE 的 Newton 迭代、拟线性方程的逐次线性化，每步吞吐由 9.45 GFLOPS GEMM 决定。标 🟢（事实：不动点迭代 ⟹ 线性求解 ⟹ GEMM）。
- **关键定理**：**Schauder 不动点定理**——$K\subset B$ 紧凸，$T:K\to K$ 连续 $\Rightarrow$

  $$\exists\,x\in K,\quad Tx=x.$$

  **Leray-Schauder 度**——紧扰动的恒等映射 $I-T$ 的拓扑度满足同伦不变性、区域可加性，度 $\ne0$ 则有不动点。
- **自测**：① 用 Schauder 不动点说明 $-\Delta u=\lambda e^u$（$\lambda>0$ 小）在 $u|_{\partial\Omega}=0$ 下有解的思路（提示：$T(v)=(-\Delta)^{-1}(\lambda e^v)$，找不变凸集）。② Leray-Schauder 度的「先验界 ⟹ 解存在」逻辑链是什么？

---

### 主题 9 · 弱解最大值原理与 Krylov-Safonov Harnack（Ch 12–13）★ 第二版新增

- **核心**：本章把最大值原理与 Harnack 不等式推广到**弱解**，是 GT 第二版（2001）的标志性增补。两大顶峰：

  ① **Alexandrov-Bakelman-Pucci（ABP）最大值原理**——用 Monge-Ampère 行列式 $\det D^2 u$ 给出 $L^\infty$ 上界 $\sup_\Omega u\le\sup_{\partial\Omega}u+C\|f^+\|_{L^n}$，$L^n$ 范数的出现是几何（凸性 / 法映射）的结晶，把线性最大值原理推进到非线性预备。
  ② **Krylov-Safonov Harnack 不等式**——**非散度型**方程 $a^{ij}(x)D_{ij}u=0$（$a^{ij}$ 仅一致椭圆 + 有界可测）弱解的 Harnack：$\sup_{B_R}u\le C\inf_{B_R}u$。这是 DGNM（散度型，主题 6）的非散度型对偶，补全了双轴——散度型有 DGNM，非散度型有 Krylov-Safonov，二者覆盖所有二阶椭圆方程。
- **飞腾锚点** 🟢：**UDOT 16.9×⭐** [E05]（复用，距主题 1 隔 7 个，不冲突）。Harnack 不等式 $\sup\le C\inf$ 的证明依赖**逐球振幅衰减的迭代**——每步是球上 $\sup/\inf$ 的点积比估计，离散后是加权求和（UDOT）。ABP 中 $L^n$ 范数 $\int(f^+)^n\,dx$ 也是点积累加。标 🟢。
- **关键定理**：**ABP 估计**——$Lu\ge f$（$c\le0$），$u\in C^2(\Omega)\cap C^0(\bar\Omega)$ $\Rightarrow$

  $$\sup_\Omega u\le\sup_{\partial\Omega}u^+ + C\,\mathrm{diam}(\Omega)\,\|f^+\|_{L^n(\Omega)}.$$

  **Krylov-Safonov Harnack**：$a^{ij}$ 一致椭圆有界可测，$u\ge0$ 弱解 $\Rightarrow \sup_{B_R}u\le C\inf_{B_R}u$。
- **自测**：① ABP 为何依赖 $L^n$ 而非 $L^\infty$ 或 $L^1$？（提示：$L^n$ 是 Sobolev 临界嵌入 $W^{2,n}$ 的指标，且与行列式 $\det D^2u$ 的几何维数匹配。）② Krylov-Safonov 与 DGNM 的区别（非散度型 vs 散度型）如何对应 $a^{ij}$ 的不同假设？

---

### 主题 10 · 拟线性方程与椭圆方程组（Ch 14–16）

- **核心**：GT 的终章把理论推向最难的拟线性与方程组。**拟线性椭圆方程**

  $$a^{ij}(x,u,\nabla u)D_{ij}u=b(x,u,\nabla u)$$

  系数依赖解与梯度。核心策略是「先控梯度 ⟹ 再提正则」：

  ① **梯度估计**——$\|\nabla u\|_{L^\infty}\le C$，用最大值原理 + Bernstein 技术。
  ② 梯度有界后系数 $a^{ij}(x,u,\nabla u)$ 可视为连续，退化回线性 Schauder/CZ 框架，得 $C^{2,\alpha}$ 正则性。

  两个典范：一致椭圆拟线性（极小曲面方程 $\mathrm{div}\bigl(\nabla u/\sqrt{1+|\nabla u|^2}\bigr)=0$）与平均曲率方程。**椭圆方程组**（Ch 16）则揭示障碍：单个方程的漂亮正则性在方程组中**部分失效**——**de Giorgi 反例**（1968）给出一个椭圆方程组，其弱解虽 Hölder 连续但**不是** $C^{1,\alpha}$，说明标量 DGNM 不能直接推广到向量。
- **飞腾锚点** 🟡：**TLB 4.81×⭐** [E04]（复用，距主题 6 隔 3 个，不冲突）。拟线性方程的梯度在边界层 / 内部急剧变化，数值上需要**自适应网格加密**（adaptive mesh refinement, AMR）——梯度大处加密，这与 TLB 管理「热页」的局部性同构：AMR 把计算资源集中到「高梯度页」，4.81× 命中增益正来自局部加密。de Giorgi 反例的「正则性失效」则对应「某些页无法缓存」的硬障碍。标 🟡。
- **关键定理**：**梯度估计**——拟线性一致椭圆方程 $a^{ij}(x,u,\nabla u)D_{ij}u=0$ 在适当结构条件下

  $$\|\nabla u\|_{L^\infty(\Omega')}\le C\quad(\Omega'\Subset\Omega),\text{ 从而 }u\in C^{2,\alpha}.$$

  **de Giorgi 反例**：$\exists$ 椭圆方程组 $-\mathrm{div}(A\nabla u)=0$（$u:\mathbb{R}^n\to\mathbb{R}^m$，$n\ge3$），弱解 $u\in C^\alpha$ 但 $u\notin C^{1,\alpha}$。
- **自测**：① 验证极小曲面方程 $\mathrm{div}\bigl(\nabla u/\sqrt{1+|\nabla u|^2}\bigr)=0$ 的均匀椭圆条件 $a^{ij}\xi_i\xi_j\ge\lambda|\xi|^2$（$\lambda$ 依赖 $|\nabla u|$，退化在 $|\nabla u|\to\infty$）。② de Giorgi 反例为何不与标量 DGNM 矛盾（方程组 vs 单方程的维数 $m$ 效应）？

---

## §9 全书思想主线：Schauder 经典 + Sobolev 弱解的「双轴统一」

GT 的总纲是「**用两条独立而互补的轴线，把整个二阶椭圆理论统一起来**」。两条轴各有「系数要求」与「正则性产出」：

- **Schauder 经典轴**（主题 1–4）：系数 Hölder 连续 $a^{ij}\in C^\alpha$ ⟹ 经典解 $u\in C^{2,\alpha}$。工具是最大值原理 + Hölder 空间 + Schauder 估计 + 连续性方法。产出是「光滑系数 ⟹ 光滑解」。

- **Sobolev 弱解轴**（主题 5–7, 9）：系数有界可测 $a^{ij}\in L^\infty$ ⟹ 弱解 $u\in C^\alpha$（DGNM 散度型 / Krylov-Safonov 非散度型）或 $u\in W^{2,p}$（CZ 强解）。工具是 Sobolev 空间 + 弱形式 + 奇异积分。产出是「粗糙系数 ⟹ 仍有一定正则性」。

两条轴的张力与互补是 GT 最深刻的设计：Schauder 要求高（$C^\alpha$ 系数）但产出高（$C^{2,\alpha}$ 解）；弱解轴要求低（$L^\infty$ 系数）但产出也低（$C^\alpha$ 解）。在主题 8（非线性方法）处两轴汇合——不动点方法把线性解算子（Schauder 或 Sobolev 框架）嵌入非线性映射，通向主题 10 的拟线性方程。全书的终极教训是：**椭圆 PDE 的正则性 = 系数正则性 × 方程结构**，双轴覆盖了从调和函数到极小曲面的全谱。

与已读呼应：Evans PDE 把弱解理论（GT 的轴二）当作「地图」快速带过，GT 在此深挖到 DGNM/CZ 顶峰；Hörmander I 的分布论是弱解定义（GT Ch 8）的严格地基——GT「使用」弱形式，Hörmander「重建」分布语言。三者构成 PDE「三套马车」。

---

## §10 与本仓库其他笔记的交叉引用

- **与 [Evans PDE](evans_PDE偏微分方程_快速逐章.md)**：Evans 把椭圆弱解理论（Schauder + Sobolev + 正则性）作为「椭圆 Ch 5–6」快速带过，重在三类型（椭圆/抛物/双曲）的统一地图；GT 专精椭圆，补全 Evans 未展开的 Schauder 全谱证明、DGNM 完整推导、Calderón-Zygmund 分解、Krylov-Safonov Harnack。**Evans 是「目录」，GT 是「专精」**——读 Evans 建立直觉后用 GT 补全严格性。

- **与 [Hörmander ALPDO I](hormander_线性偏微分算子I_快速逐章.md)**：Hörmander I 的分布论是 GT 弱解定义的严格地基——GT Ch 8 的弱解 $\int A\nabla u\cdot\nabla\varphi=0$ 是分布求导（Hörmander Ch III 分部积分）的直接应用；Newton 位势（GT Ch 4）= 分布卷积基本解（Hörmander Ch IV）。读 GT 前 Hörmander I 的分布论提供语言，但 GT 不需要波前集等高阶工具。

- **与 [Folland 实分析](../stage-2-研究生基础/folland_实分析_快速逐章.md)**：Folland 的 Lebesgue 积分、$L^p$ 空间、Hölder/Minkowski 不等式是 GT Ch 5（Hölder 空间）、Ch 7（Sobolev 空间）、Ch 9（CZ 分解）的测度论基础；奇异积分算子（GT Ch 9）的 $L^p$ 有界性证明直接调用 Folland 的极大函数与 Marcinkiewicz 插值。

- **与 [Reed-Simon I](../stage-2-研究生基础/reed_simon_数学物理方法I_快速逐章.md)**：Reed-Simon 的 Hilbert 空间算子理论、紧算子、谱定理是 GT 弱解存在性（Lax-Milgram）与不动点方法（紧算子的 Schauder 不动点）的泛函包装；特征函数展开（Laplace 特征值）连接 Reed-Simon 的谱理论与 GT 的先验估计。

- **AI / 工程锚点**（椭圆 PDE = AI for Science 的核心数学）：

  - ① **PINN（物理信息神经网络）**：把椭圆方程残差 $\|Lu-f\|$ 作损失，本质是弱形式配对的神经网络逼近——GT Ch 8 弱解定义是 PINN 的连续数学源头；Schauder 估计（GT Ch 6）给 PINN 解的误差上界（正则性 ⟹ 收敛率）。
  - ② **Neural Operator / DeepONet**：学习椭圆算子的解算子 $f\mapsto u=L^{-1}f$——Newton 位势（GT Ch 4）$u=\Gamma*f$ 是解算子的显式原型；CZ $W^{2,p}$ 估计（GT Ch 9）保证解算子的 $L^p$ 连续性（神经网络可逼近的条件）。
  - ③ **有限元方法（FEM）**：离散弱形式 $\int A\nabla u\cdot\nabla v=\int fv$——GT Ch 8 弱形式是 FEM 的连续源头；Sobolev 嵌入（GT Ch 7）给 FEM 收敛阶；UDOT 16.9× / GEMM 9.45G 正是 FEM 刚度矩阵的硬件加速。
  - ④ **最小曲面 / 几何变分**：极小曲面方程（GT Ch 16）是几何 PDE 的典范，拟线性梯度估计（GT Ch 14）保证肥皂膜形状的正则性；AI 生成 3D 曲面（如 Neural SDF）的正则性依赖椭圆先验估计。
  - ⑤ **物理仿真（CFD / 电磁 / 热）**：Laplace/Poisson 方程（GT Ch 2–4）是静电、稳态热、不可压势流的模型；GT 的先验估计是仿真收敛性 / 网格自适应（AMR）的理论保证。

> **一句话总结本书的 AI 价值**：GT 把「椭圆 PDE 的解如何依赖系数与数据」严格量化为「先验估计」（Schauder $C^{2,\alpha}$ / Sobolev $W^{2,p}$ / DGNM $C^\alpha$），而 AI for Science（PINN / Neural Operator / FEM）恰恰是「用神经网络逼近这些解算子」——读通 GT，就拿到了椭圆 PDE 数值与 AI 求解的理论底座（正则性 ⟹ 逼近率 ⟹ 收敛保证）。

---

## §11 各主题精华一句话

- **主题 1**：一致椭圆条件 + 均值定理是全书的「标尺」——Laplace 方程上验证一切再推广。
- **主题 2**：最大值原理是「边界决定全局」的严格化身，Hopf 引理连接内部与边界。
- **主题 3**：Newton 位势 $u=\Gamma*f$ 是 Poisson 方程的解算子，其可微性引出奇异积分（CZ 先声）。
- **主题 4**★：Schauder 估计 $\|u\|_{C^{2,\alpha}}\le C(\|u\|_{C^0}+\|f\|_{C^\alpha})$ 是经典轴核心——先验估计 ⟹ 存在性。
- **主题 5**：Sobolev 嵌入 $W^{k,p}\hookrightarrow C^{m,\alpha}$（$kp>n$）是弱解轴的函数空间基础。
- **主题 6**★：De Giorgi-Nash-Moser——有界可测系数 ⟹ 弱解自动 $C^\alpha$，Schauder 做不到的壮举。
- **主题 7**★：Calderón-Zygmund 分解 ⟹ 奇异积分 $L^p$ 有界 ⟹ 强解 $W^{2,p}$ 估计。
- **主题 8**：Schauder / Leray-Schauder 不动点把线性解算子嵌入非线性映射，通向拟线性。
- **主题 9**★：ABP + Krylov-Safonov 把最大值原理与 Harnack 推到非散度型弱解，补全双轴。
- **主题 10**：拟线性靠梯度估计 ⟹ 退化回线性；de Giorgi 反例揭示方程组正则性的障碍。

---

## 📌 阅读建议（对接数学专家路径）

1. **精读顺序**：主题 1–3（Laplace + 最大值 + 位势，快扫）→ **主题 4（Schauder 估计，经典轴核心）** → **主题 6（DGNM，弱解轴灵魂）** → **主题 7（CZ，弱解轴顶峰）** → 主题 5（Sobolev，按需查）→ 主题 9（ABP + Krylov-Safonov）→ 主题 8, 10（非线性 + 拟线性，应用层）。

2. **与 Evans 配对读**：Evans「椭圆 Ch 5–6」↔ GT 主题 4–7。Evans 给地图，GT 补全证明——读 Evans 建立「弱解三部曲」直觉后，用 GT 把 Schauder / DGNM / CZ 的完整证明吃透。

3. **数学根基回溯**：Hölder / Sobolev 空间 ⟵ Folland 实分析（已读）；弱形式 / 分布 ⟵ Hörmander I（刚读）；Hilbert 空间 / Lax-Milgram ⟵ Reed-Simon I（已读）。

4. **深挖课题**（GT 特色）：
   - ① Schauder 估计的「先验 ⟹ 存在性」范式如何成为现代 PDE 的标准方法（连续性方法）。
   - ② DGNM 为何不需要 Fourier 分析（De Giorgi 截断法的纯实分析威力）。
   - ③ Calderón-Zygmund 分解如何把「好-坏」二分法变成奇异积分 $L^p$ 有界的引擎。
   - ④ Krylov-Safonov 如何用「接触集 / 几何测度」把 Harnack 从散度型搬到非散度型。

5. **动手验证**（Python 工程师优势）：主题 3 用 NumPy 验证 Newton 位势 $u=\Gamma*f$ 的正则性（$f$ 随机 ⟹ $u$ 的二阶差分）；主题 4 用 `scipy.sparse` 实现有限元，验证 Schauder 估计的 $C^{2,\alpha}$ 收敛阶；主题 6 用随机矩阵 $A$（有界可测）验证 DGNM（弱解仍 $C^\alpha$）；主题 7 用 FFT 验证 Riesz 变换的 $L^p$ 有界性（$p=1,\infty$ 失败）。代码即理解，飞腾实测数据则作为「工程极限」的参照系。

> 注：本笔记基于 Gilbarg-Trudinger GT 224（2nd ed., 2001 reprint）真实 TOC（16 章合并为 10 主题）撰写快速逐章导览，侧重概念串联与飞腾 / AI 锚点对接。关键定理（均值定理、Hopf 引理、Schauder 估计、Sobolev 嵌入、DGNM 正则性、CZ $W^{2,p}$ 估计、ABP、Krylov-Safonov Harnack、de Giorgi 反例）均为标准准确陈述。
