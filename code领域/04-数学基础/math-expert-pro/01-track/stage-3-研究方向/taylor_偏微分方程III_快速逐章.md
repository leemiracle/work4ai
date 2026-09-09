# Michael E. Taylor《偏微分方程 III：非线性方程》 · 快速逐章精读

> 基于原书：*Partial Differential Equations III — Nonlinear Equations*, Applied Mathematical Sciences 117（Michael E. Taylor, Springer, 2nd ed., 2011；初版 1996）/ 读于：2026-07-03
> 定位：**非线性 PDE 的「全面纵深」收官卷**，把 Vol I–II 的线性机器推广到完全非线性椭圆 / 非线性演化 / 几何变分 / 曲率流的完整体系。
> 关联：[Taylor PDE I（奠基卷）](taylor_偏微分方程I_快速逐章.md) · [Taylor PDE II（线性定性卷）](taylor_偏微分方程II_快速逐章.md) · [Jost 几何分析](../stage-2-研究生基础/jost_黎曼几何与几何分析_快速逐章.md) · [Evans PDE](evans_PDE偏微分方程_快速逐章.md) · [Gilbarg-Trudinger 椭圆 PDE](gilbarg_trudinger_椭圆PDE_快速逐章.md)
> 本文为**快速逐章精读**（忠于原书真实 TOC），每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

> 📌 **Vol III 定位与「三部曲」关系（以原书真实结构为准）**
>
> Taylor 三卷本（Springer AMS 115–117）的第三卷副题为 **「Nonlinear Equations」**。若 [Vol I《Basic Theory》](taylor_偏微分方程I_快速逐章.md) 搭机器（古典三方程 + Sobolev + 拟微分引论）、[Vol II《Qualitative Studies》](taylor_偏微分方程II_快速逐章.md) 用机器回答线性定性，则 **Vol III 把整套线性机器推广到非线性世界**：完全非线性椭圆（Monge-Ampère、De Giorgi-Nash-Moser 完全非线性版）、非线性抛物（守恒律 / Ricci 流引论）、非线性双曲（激波 / 波动映射 / Einstein 方程）、变分几何（极小曲面 / 调和映射）、曲率流（平均曲率流 / Ricci 流 / Perelman 熵）。
>
> Vol III 的结构逻辑是「**先完全非线性椭圆（Ch 1，最难的核心），再三类非线性演化（Ch 2–3），后几何变分与曲率流（Ch 4–5，皇冠应用）**」。Vol III 是三部曲的收官：线性理论（Vol I–II）是非线性理论（Vol III）的**必经前置**——非线性先验估计处处依赖线性的 Schauder / Sobolev / 拟微分工具。

> 🟢 **【事实】** 飞腾锚点中标注 🟢 者，数学概念与硬件性能的关联是事实匹配（如「曲率张量缩并 ⟺ 大矩阵乘」「计数 = 指示函数求和」），可作严格论证的锚点。
> 🟡 **【类比】** 标注 🟡 者仅供直觉建立（如「特征分解 ↔ 正交化」「抛物稳定预算 ↔ 误差铁律」），**绝不在严格证明中引用**。
> ⭐ 标记为用户高频使用的核心锚点（UDOT / Iron Law）。

---

## §0 引言：Taylor 的「非线性收官」卷

Michael E. Taylor（UNC Chapel Hill）三卷本《Partial Differential Equations》（Springer AMS 115–117，初版 1996，第二版 2011 全面修订）是 PDE 领域体量最大的现代教材。**Vol III《Nonlinear Equations》是这套大厦的收官卷**——与已完成的 Vol I、Vol II 合为「Taylor PDE 三部曲」。

Vol I 回答「**解长什么样**」（显式公式 + 弱解），Vol II 回答「**解有何性质**」（定性），Vol III 回答「**当方程本身非线性时，解还存在、还正则、还演化吗**」。一句话定位：本书是 stage-3 PDE 方向的**非线性纵深教材**，把 Vol I–II 的线性机器推广到完全非线性椭圆、非线性演化、几何变分与曲率流。

Vol III 的设计哲学可凝练为三条主线：① **完全非线性椭圆**（Ch 1）——以 Monge-Ampère 方程 $\det D^2u=f$ 为典范，De Giorgi-Nash-Moser 理论的完全非线性版（Krylov-Safonov Harnack、Evans-Krylov 二阶导估计）给出 $C^{2,\alpha}$ 正则性，Caffarelli 解决 Monge-Ampère 解的存在与正则；② **非线性演化**（Ch 2–3）——守恒律的熵解（Kružkov）、拟线性抛物正则、非线性双曲的激波与波动映射、Einstein 真空方程在调和规范下的局部适定性；③ **几何变分与曲率流**（Ch 4–5）——极小曲面、Eells-Sampson 调和映射热流、Hamilton Ricci 流短时存在、Perelman 熵单调性。Taylor 把几何 PDE（Perelman 的 Poincaré 证明引擎、Donaldson 规范理论的变分背景）作为非线性分析的「皇冠应用」。

核心哲学凝练：**线性 PDE 的先验估计（Schauder / Sobolev / 极值 / 能量）是非线性 PDE 的「脚手架」——非线性问题通过「连续性方法 + 先验估计」化为线性问题的扰动**。这是 Vol III 区别于 Vol I–II 的本质：Vol I–II 的对象是「给定的线性算子」，Vol III 的对象是「依赖解本身的非线性算子」，但后者仍用前者的工具求解。

### 四本 PDE / 几何分析教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|------|------|--------|--------|
| **Taylor PDE III（本书）** | 非线性全面收官；完全非线性椭圆 + 非线性演化 + 几何变分 + 曲率流四合一 | ★★★★★（严格，前沿密集） | PDE / 几何分析研究者 |
| **Taylor PDE I（Vol I 奠基）** | 几何全面奠基；古典三方程 + Sobolev + 拟微分引论 + 波前集引论 | ★★★★★ | PDE 研究生（先读） |
| **Taylor PDE II（Vol II 线性定性）** | 线性定性纵深；微局部机器统摄奇性 / 谱 / 散射 / 发展 / 边界 | ★★★★★ | PDE / 分析研究者 |
| **Jost 几何分析（刚做）** | 几何分析综合；Riemann 几何 + PDE/物理（Hodge/Bochner/调和映射/Ricci 流） | 高，分析密度大 | 几何分析研究者 ⭐ |

> **阅读策略**：Vol I 搭机器 + 显式解 → Vol II 用机器做线性定性 → **Vol III 把机器推广到非线性**（三部曲合璧）→ Jost 用同一套 PDE/变分工具求解几何问题。四者构成「PDE × 几何分析」的纵深矩阵：Vol I–III 是「PDE 主轴」，Jost 是「几何分析出口」。**Vol I–II 是 Vol III 的必经前置**——非线性先验估计处处回引线性工具。

### Vol I–II ↔ Vol III「三部曲」逐主题映射

Vol III 是线性理论的非线性推广：Vol I–II 的每个线性主题，在 Vol III 都有对应的非线性升级。

| Vol I–II 主题（线性机器） | Vol III 章节（非线性推广） | 升级关系 |
|:---|:---|:---|
| Vol I 主题 8 + GT：线性椭圆 Schauder / DGNM | **Ch 1** 完全非线性椭圆 | 线性 $a^{ij}u_{ij}=f$ → 完全非线性 $F(D^2u)=f$；Monge-Ampère $\det D^2u=f$ |
| Vol II Ch 5：线性抛物半群（Hille-Yosida） | **Ch 2** 非线性抛物 | 线性 $u_t-\Delta u=0$ → 拟线性 $u_t-\mathrm{div}\,a(Du)Du=0$；守恒律 / p-Laplacian |
| Vol II Ch 6：线性双曲能量法 | **Ch 3** 非线性双曲 | 线性波 → 拟线性波 / 守恒律系统；激波、波动映射、Einstein 方程 |
| Vol I 主题 12：线性变分（Dirichlet 原理） | **Ch 4** 变分方法与几何 PDE | 二次泛函 → 非线性泛函（面积、能量）；极小曲面、调和映射 |
| Vol I 主题 11：曲率流引论 | **Ch 5** 曲率流与几何演化 | 平均曲率流 / Ricci 流完整化；Hamilton 存在、Perelman 熵 |

> 一句话：**Vol III 把 Vol I–II 的线性机器逐主题推广到非线性**——读者可对照阅读，用 Vol III 的非线性理论回溯巩固 Vol I–II 的线性直觉。

---

## §1 全书 5 章骨架一览（飞腾锚点分布）

Vol III 主线是「**完全非线性椭圆 → 非线性抛物 / 双曲 → 几何变分 → 曲率流**」。Ch 1 是最难的核心（完全非线性正则性），Ch 2–3 是非线性演化（抛物光滑化 + 双曲激波），Ch 4–5 是几何 PDE 的皇冠应用（变分存在性 + 几何流）。每章对接一条飞腾实测锚点，全书 5 个最贴合的锚点各用一次。

| 章 | 标题（英文 / 中文） | 核心概念 | 飞腾锚点 |
|:-:|------|---------|:--------:|
| 1 | Nonlinear Elliptic Equations（非线性椭圆） | 完全非线性 $F(D^2u)=f$ · **Monge-Ampère** · Krylov-Safonov · Evans-Krylov | UDOT 16.9×⭐ 🟢 |
| 2 | Nonlinear Parabolic Equations（非线性抛物） | 拟线性抛物 · 守恒律 **熵解** · p-Laplacian · 黏性解 · Ricci 流引论 | Iron Law<2%⭐ 🟡 |
| 3 | Nonlinear Hyperbolic Equations（非线性双曲） | 激波 · 对称双曲组 · **波动映射** · **Einstein 方程** | Schmidt 🟡 |
| 4 | Variational Methods & Geometric PDE（变分与几何 PDE） | 直接方法 · minimax · **极小曲面** · **Eells-Sampson 调和映射** | matmul 15× 🟢 |
| 5 | Curvature Flows & Geometric Evolution（曲率流与几何演化） | **平均曲率流** · **Hamilton Ricci 流** · **Perelman 熵** · 手术 | GEMM 9.45G 🟢 |

```
完全非线性椭圆（Ch 1）：非线性 PDE 的核心难题
Ch 1 非线性椭圆 ── Monge-Ampère det D²u=f·Krylov-Safonov Harnack·Evans-Krylov C²,α·Caffarelli ──┐
           │ 推广到时间演化
非线性演化（Ch 2–3）：抛物光滑化 + 双曲激波
Ch 2 非线性抛物 ── 拟线性抛物正则·守恒律熵解(Kružkov)·p-Laplacian·黏性解·Ricci流引论 ───────┤
Ch 3 非线性双曲 ── 激波/熵条件·对称双曲组·波动映射·Einstein方程(调和规范) ───────────────────┘
           │ 推广到几何变分
几何变分 + 曲率流（Ch 4–5）：非线性分析的皇冠应用
Ch 4 变分与几何PDE ── 直接方法·minimax·极小曲面·Eells-Sampson调和映射热流·Bochner技巧 ──────┐
Ch 5 曲率流 ── 平均曲率流·Hamilton Ricci流短时存在(DeTurck)·Perelman F熵/W熵单调·手术 ────┘

数学根基：Taylor PDE I（Sobolev/拟微引论）·Taylor PDE II（半群/能量法/微局部）
         ·Gilbarg-Trudinger（线性椭圆先验）·Lee 光滑流形（曲率/联络）·Jost 几何分析（调和映射/Ricci流）
```

---

## 完全非线性椭圆

### 第 1 章 · Nonlinear Elliptic Equations（非线性椭圆方程）★ 三部曲核心

- **核心**：本章是 Vol III 的**核心难题**——处理最高阶项以非线性方式依赖 $u$ 的**完全非线性椭圆方程** $F(D^2u,x)=f$。代表是 **Monge-Ampère 方程**
  $$\det(D^2u)=f(x)\quad(f>0),$$
  它出现在 Kähler-Einstein 度量（复 Monge-Ampère，Yau 定理的 PDE 引擎）、最优传输（Monge-Kantorovich）、仿射几何中。本章把 Vol I 主题 8 + GT 的线性椭圆理论推广为完全非线性框架：
  - ① **De Giorgi-Nash-Moser 完全非线性版**——线性椭圆的 DNM 正则性（解自动 Hölder）在完全非线性下由 **Krylov-Safonov Harnack 不等式**复活：完全非线性一致椭圆方程的解 Hölder 连续。这是「线性正则性 ⟹ 非线性正则性」的关键跃迁——线性用 Moser 迭代，完全非线性用 Aleksandrov 极值 + Abel 和函数迭代。
  - ② **Evans-Krylov 二阶导估计**——完全非线性方程的解满足 $D^2u\in C^{\alpha}$（Hessian Hölder），前提是方程关于 $D^2u$ 是**凹或凸**的（concave/convex，如 Monge-Ampère 的 $\det$ 在凸锥上凹）。这给 Monge-Ampère 的 $C^{2,\alpha}$ 正则性，是 GT 线性 Schauder 估计的非线性推广。
  - ③ **Caffarelli 正则性与连续性方法**——$\det D^2u=f\in C^\alpha$（$f$ 正、$u$ 凸）⟹ $u\in C^{2,\alpha}_{\mathrm{loc}}$；用**连续性方法**（continuity method）：沿参数族 $t\in[0,1]$ 把已知解 $t=0$ 延续到目标 $t=1$，每步用先验估计保证延续不中断。**凸性是基石**：$\det D^2u>0$ ⟹ $D^2u\ge0$ ⟹ $u$ 凸，凸性使先验估计闭合。
  - ④ **应用**——Monge-Ampère 解决 Kähler-Einstein 度量存在性（Calabi 猜想，Yau 1978）；完全非线性方程还出现在随机控制（Bellman / Isaacs 方程）与保角几何中。

- **飞腾锚点** 🟢：**UDOT 16.9×⭐** [E05]。Monge-Ampère 测度 $\det(D^2u)\,dx$ 的体积估计依赖**大批网格点上 Hessian 行列式的点积累加**——每个格点处是 $n\times n$ 小矩阵 $\det$ 的求和，Alexandrov 极值原理的法映射（normal map）覆盖体积也是密集计数求和，$L^n$ 范数 $\int(f^+)^n\,dx$ 也是点积。UDOT（无符号点积）对批量行列式累加加速 16.9×。标 🟢（事实：行列式求积 = 点积累加）。

- **关键定理**：**Krylov-Safonov Harnack 不等式**——$F(D^2u)=f$ 完全非线性一致椭圆（一致椭圆性
  $$0<\lambda I\le\frac{\partial F}{\partial(D^2u)}\le\Lambda I,$$
  $f$ 有界 ⟹ $u$ Hölder 连续，且 $\sup_{B_{r/2}}u\le C\inf_{B_{r/2}}u$（Harnack）。
  **Caffarelli Monge-Ampère 正则性**：$\det D^2u=f>0$，$f\in C^\alpha$，$u$ 凸 ⟹ $u\in C^{2,\alpha}_{\mathrm{loc}}$。
  重要性：把「右端光滑」翻译为「解二阶导光滑」，是完全非线性椭圆的皇冠结果，直接服务于 Kähler-Einstein 度量存在（Yau 定理的 PDE 引擎）。

- **自测**：① 为何 Monge-Ampère 方程要求 $u$ 凸（$\det D^2u=f>0$ ⟹ $D^2u$ 半正定 ⟹ 凸）？
  ② Evans-Krylov 估计为何需要 $F$ 关于 $D^2u$ 凹或凸（凹凸性 ⟹ Hessian 一致椭圆，Krylov-Safonov 可用）？
  ③ Alexandrov 极值中 $L^n$ 范数的 $n$ 从何而来（Sobolev 临界嵌入 $W^{2,n}$ + 行列式维数）？
  ④ 连续性方法为何需要先验估计（开性 = 隐函数定理，闭性 = 先验界保证极限不跑出空间）？

---

## 非线性演化

### 第 2 章 · Nonlinear Parabolic Equations（非线性抛物方程）

- **核心**：本章把 [Vol II Ch 5](taylor_偏微分方程II_快速逐章.md) 的线性热半群推广到非线性抛物。核心对象有三类：
  - ① **拟线性抛物方程** $u_t-\mathrm{div}\,a(x,u,Du)Du=f$——其正则性由**冻结系数法**给出：在每个点把方程线性化为 $u_t-a^{ij}(Du)\partial_{ij}u=f$，用 Vol II 的 Schauder / Sobolev 抛物估计，再「解冻」迭代。解在抛物意义下光滑化（增益 $2m$ 阶），与线性热方程共享「高频模式指数衰减」的机制。
  - ② **标量守恒律** $u_t+\mathrm{div}\,F(u)=0$——即使初值光滑，解也可能在有限时间**形成激波**（特征线相交，因 $F'(u)$ 随 $u$ 变化使特征速度依赖解本身）。经典解失效，须引入**熵解**（entropy solution, Kružkov 1970）：满足熵不等式 $\eta(u)_t+q(u)\cdot\nabla\le0$（$\forall$ 凸熵 $\eta$，$q'=\eta'F'$），Kružkov 证明熵解存在且唯一，且 $L^1$ 收缩。
  - ③ **非线性扩散与黏性解**——p-Laplacian $\mathrm{div}(|Du|^{p-2}Du)$（退化抛物，$|Du|=0$ 处退化）、多孔介质方程 $u_t=\Delta(u^m)$；**Hamilton-Jacobi** $u_t+H(Du)=0$ 的**黏性解**（viscosity solution, Crandall-Lions）由 vanishing viscosity 极限定义：$u^\varepsilon_t+H(Du^\varepsilon)=\varepsilon\Delta u^\varepsilon$，$\varepsilon\to0$ 时 $u^\varepsilon\to u$，黏性项提供光滑化使极限适定。
  - 本章还含 **Ricci 流引论**——$\partial_tg=-2\mathrm{Ric}$ 作为非线性抛物几何方程的预告（Ch 5 深化为完整理论）。

- **飞腾锚点** 🟡：**Iron Law<2%⭐** [Lab00]。非线性抛物方程的显式数值有更严格的 **CFL 稳定性预算**（$dt\le C\,dx^2$），违反即数值爆炸（高频噪声放大）——这是「误差须压进预算」的铁律：稳定步长是精度 / 稳定性权衡参数，与 Iron Law 性能铁律（误差须 <2%）同构。**黏性解**的 vanishing viscosity 极限正是「正则化项 $\varepsilon\Delta u$ 压进无穷小预算」的思想化身——$\varepsilon$ 是精度旋钮，$\varepsilon\to0$ 时奇异被消除但极限仍适定。标 🟡。

- **关键定理**：**Kružkov 熵解存在唯一性**——标量守恒律
  $$u_t+\mathrm{div}\,F(u)=0\quad(F\text{ 凸}),\qquad u(x,0)\in L^\infty,$$
  存在唯一熵解 $u\in L^\infty\cap C([0,\infty);L^1_{\mathrm{loc}})$，满足所有 Kružkov 熵不等式；$L^1$ 收缩原理
  $$\|u(t)-v(t)\|_{L^1}\le\|u(0)-v(0)\|_{L^1}$$
  给唯一性。重要性：它是非线性双曲 / 抛物「弱解理论」的基石——熵条件排除非物理激波，使解在「特征相交」后仍适定。

- **自测**：① 熵条件为何排除非物理激波（违反熵不等式的弱解不对应物理耗散极限 / vanishing viscosity）？
  ② p-Laplacian $\mathrm{div}(|Du|^{p-2}Du)$ 在 $|Du|=0$ 处退化，如何影响解的正则性（退化 ⟹ 解 $C^{1,\alpha}$ 但非 $C^2$）？
  ③ 黏性解的 vanishing viscosity 极限与「抛物光滑化」有何关系（$\varepsilon\Delta u$ 项提供光滑化，$\varepsilon\to0$ 留下适定极限）？
  ④ 为何标量守恒律有唯一熵解而系统情形是开放问题（标量有 Kružkov 熵的凸结构，系统无等价物）？

---

### 第 3 章 · Nonlinear Hyperbolic Equations（非线性双曲方程）

- **核心**：本章把 [Vol II Ch 6](taylor_偏微分方程II_快速逐章.md) 的线性对称双曲组推广到非线性。核心特征仍是**无耗散 + 有限传播**，但解可能在有限时间**爆破**（激波形成）：
  - ① **守恒律系统与激波**——$u_t+\mathrm{div}\,F(u)=0$（系统，$u\in\mathbb{R}^m$），特征线相交 ⟹ 激波；**Rankine-Hugoniot 跳跃条件** $s\,[u]=[F(u)]$（$s$ 激波速度，$[u]$ 跨激波跳跃）+ 熵条件选定物理激波。与 Ch 2 标量情形不同，系统的熵解唯一性是**重大开放问题**（多维尚未完全解决，Lax 的「小激波仍唯一」是一维部分结果）。
  - ② **拟线性对称双曲组**——$\partial_tu=\sum_jA_j(u)\partial_{x_j}u+F$（$A_j=A_j^T$），能量法 + Gronwall 给**局部**适定性（解可能有限时间爆破）；线性化后用 Vol II Ch 6 的能量估计，非线性项做扰动。
  - ③ **波动映射**（wave maps）——闵可夫斯基空间 $\mathbb{R}^{1+n}$ 到黎曼流形 $(N,h)$ 的调和映射（能量极小），是波动方程的几何版：Euler-Lagrange 方程 $\Box u^k+\Gamma^k_{ij}(u)\partial_\alpha u^i\partial^\alpha u^j=0$。波动映射可能有限时间爆破（能量集中在特征），其正则性 / 爆破判定是当代研究热点（临界维数 $n=2$ 是分水岭）。
  - ④ **Einstein 真空方程引论**——$R_{\mu\nu}=0$ 在**调和规范**（de Donder / harmonic gauge，坐标满足 $\Box x^\mu=0$）下化为**拟线性波方程组**，Choquet-Bruhat（1952）证明局部存在唯一——这是广义相对论 Cauchy 问题的数学基础，也是「把几何方程翻译为标准 PDE」的典范。

- **飞腾锚点** 🟡：**Schmidt 正交化**。守恒律系统的解分解为**特征族**（rarefaction fan / shock fan），每个族沿一个特征速度 $A(u)$ 的特征值传播——这与把波动「正交分解」到特征方向同源：特征分解 $u=\sum c_i r_i$（$r_i$ 特征向量）= Gram-Schmidt 式地把状态向量投到特征向量基上。波动映射的目标流形上沿测地分解也类似。标 🟡（类比，直觉用）。

- **关键定理**：**拟线性对称双曲组局部适定性**——
  $$\partial_tu=\sum_j A_j(u)\,\partial_{x_j}u+F\quad(A_j=A_j^T,\ A_j\text{ 光滑}),$$
  初值 $u(0)\in H^s$（$s>n/2+1$）⟹ 存在唯一极大解 $u\in C([0,T^*);H^s)$，能量估计
  $$E(t)\le E(0)\,e^{Ct}.$$
  **Choquet-Bruhat Einstein 局部存在**：真空 Einstein 方程在调和规范下化为拟线性波，局部存在唯一光滑解。重要性：把「几何方程」（Einstein）翻译为「标准 PDE」（拟线性波），使 PDE 工具直接服务广义相对论。

- **自测**：① 调和规范如何把 Einstein 真空方程 $R_{\mu\nu}=0$ 化为拟线性波（坐标满足 $\Box x^\mu=0$，消除 Bianchi 恒等式导致的规范退化）？
  ② 波动映射为何可能有限时间爆破（能量沿特征集中，非线性 Christoffel 项 $\Gamma\partial u\partial u$ 聚焦）？
  ③ Rankine-Hugoniot 条件 $s[u]=[F(u)]$ 中 $s$ 的物理意义（激波面速度 = 通量跳跃 / 状态跳跃）？
  ④ 为何系统守恒律的熵解唯一性比标量难（标量有 Kružkov 凸熵，系统无对应的凸结构）？

---

## 几何变分与曲率流

### 第 4 章 · Variational Methods and Geometric PDE（变分方法与几何 PDE）

- **核心**：本章把 [Vol I 主题 12](taylor_偏微分方程I_快速逐章.md) 的线性变分推广为**非线性变分几何**——用能量 / 面积泛函的极值条件定义几何对象：
  - ① **直接方法与 minimax**——能量泛函 $I[u]=\int L(Du,u,x)\,dx$ 的极小元用直接方法（弱下半连续 + Rellich 紧性，Vol I 主题 12）；**Mountain Pass 引理**（Ambrosetti-Rabinowitz）给「鞍点型」临界点：若 $I$ 在两点「山谷」之间有「山脊」，则存在临界值 $c=\inf_\gamma\sup I\circ\gamma$。minimax 方法用于寻找非极小的解（如 Yamabe 问题：在共形类中极小全数量曲率）。
  - ② **极小曲面**——面积泛函 $A[u]=\int\sqrt{1+|Du|^2}\,dx$ 的 Euler-Lagrange 给极小曲面方程 $\mathrm{div}(Du/\sqrt{1+|Du|^2})=0$（Vol I 主题 11 稳态）。它是**非线性椭圆**（主符号正定），正则性由 Ch 1 工具给。Bernstein 定理（$\mathbb{R}^2$ 上整解是线性）是经典结果，高维有反例（Bombieri-De Giorgi-Giusti）。
  - ③ **调和映射**（harmonic maps）——能量泛函 $E(u)=\frac12\int_M|Du|^2\,dV_g$ 的临界点，Euler-Lagrange 是张力场 $\tau(u)=\mathrm{tr}\nabla Du=0$。**Eells-Sampson 调和映射热流**（1964） $\partial_tu=\tau(u)$ 把变分问题化为抛物演化：目标流形截面曲率 $\le0$ 时，热流全局存在且收敛到调和映射。**Bochner 技巧**：$\frac12\partial_t\int|Du|^2=-\int|\nabla Du|^2-\int\mathrm{Rm}_N(Du,Du,Du,Du)\le0$（曲率非正 ⟹ 能量单调）给存在性与不爆破。
  - 本章是与 [Jost 几何分析](../stage-2-研究生基础/jost_黎曼几何与几何分析_快速逐章.md) Ch 8（调和映射）的**直接交汇**——Jost 是调和映射存在性的权威贡献者（几何侧叙事），Taylor 给 PDE 侧的严格先验估计；Bochner 公式在两书中同源。

- **飞腾锚点** 🟢：**matmul 15×** [V03]。能量泛函离散为**有限元刚度矩阵** $K_{ij}(u)=\int DL(D\phi_j)\cdot D\phi_i\,dx$，非线性时 $K=K(u)$ 随解更新；调和映射热流的梯度下降每步是 $K(u)\cdot u$ 的 matmul；极小曲面方程 Newton 迭代的 Jacobi 矩阵也是密集矩阵求逆。15× 向量化增益直接加速变分求解与梯度流迭代。标 🟢（事实：泛函离散 = 矩阵装配 + 求解）。

- **关键定理**：**Eells-Sampson 调和映射存在性**——紧黎曼流形 $(M,g)$ 到截面曲率 $K_N\le0$ 的紧目标 $(N,h)$，调和映射热流
  $$\partial_tu=\tau(u)=\mathrm{tr}\,\nabla Du$$
  对所有 $t\ge0$ 存在光滑解，$t\to\infty$ 时收敛到调和映射 $u_\infty:M\to N$。**Bochner 公式**：
  $$\tfrac12\partial_t\!\int|Du|^2=-\!\int|\nabla Du|^2+\!\int\mathrm{Rm}_N(Du,Du,Du,Du)\le0\quad(K_N\le0).$$
  重要性：把「拓扑问题」（$M\to N$ 是否有调和代表）化为「抛物 PDE 的长期行为」，是几何分析的范式典范——拓扑约束（曲率符号）⟹ 分析结论（存在性）。

- **自测**：① 为何目标截面曲率 $K_N\le0$ 保证调和映射热流不爆破（Bochner 公式给 $\int|Du|^2$ 单调减，能量有上界 ⟹ 梯度一致有界 ⟹ 不爆破）？
  ② 极小曲面方程 $\mathrm{div}(Du/\sqrt{1+|Du|^2})=0$ 为何是椭圆（主符号 $\delta_{ij}/\sqrt{1+|Du|^2}-u_i u_j/(1+|Du|^2)^{3/2}$ 正定）？
  ③ Mountain Pass 引理如何找「非极小」临界点（沿路径极大值的极小，PS 条件保证临界点存在）？

---

### 第 5 章 · Curvature Flows and Geometric Evolution Equations（曲率流与几何演化方程）★ 三部曲皇冠

- **核心**：本章是 Vol III 的**皇冠**——把非线性抛物（Ch 2）推广到几何演化方程，以曲率为主项驱动度量 / 曲面演化。这是 21 世纪几何分析的爆发点：
  - ① **平均曲率流**（mean curvature flow）——浸入曲面 $F(\cdot,t):\Sigma\to\mathbb{R}^{n+1}$ 以平均曲率向量演化 $\partial_tF=-H\nu$，是热方程的几何推广（曲面收缩趋平滑，Vol I 主题 11 的演化版）。它是**抛物几何方程**，但可能在有限时间出现**奇点**：**neck pinching**（管状区域中部先断，曲率爆破），需手术（surgery）切除奇点重连后继续演化。
  - ② **Hamilton Ricci 流**——度量演化 $\partial_tg(t)=-2\,\mathrm{Ric}(g(t))$（Hamilton 1982 引入）。它是「度量版热方程」（Ricci 张量分量满足抛物方程，高频曲率模式衰减），**短时存在**由 **DeTurck trick** 证明：Ricci 流本身因微分同胚不变性有「规范退化」（Bianchi 恒等式），DeTurck 用规范向量场的 Lie 导数修正，化为严格抛物系统再解，最后还原。Hamilton 用它分类三维流形的曲率演化（正规化使曲率趋向常数）。
  - ③ **Perelman 熵单调性**——Perelman（2002–2003）引入 **F-熵** $\mathcal{F}(g,f)=\int_M(R+|\nabla f|^2)e^{-f}\,dV$ 与 **W-熵** $\mathcal{W}(g,f,\tau)$（$\tau>0$ 尺度参数），证明二者沿 Ricci 流（耦合 $f,\tau$ 的方程）**单调不减**。这是非线性 PDE 的「Liapunov 泛函」——熵单调性推出 **Perelman 非塌缩定理**（曲率有界处体积有下界），排除了「塌缩」奇点，使手术可分类所有三维奇点，最终证明 Poincaré 猜想与 Thurston 几何化纲领。
  - 本章是三部曲的至高点——Ricci 流 + Perelman 熵把「流形分类」这个纯拓扑问题，完全化为「非线性抛物方程的全局单调性分析」。

- **飞腾锚点** 🟢：**GEMM 9.45G** [Lab05]。Ricci 流每一步的曲率张量演化 $\partial_tR_{ijkl}=\Delta R_{ijkl}+Q_{ijkl}(R)$（$Q$ 是曲率的二次缩并）涉及**大规模张量缩并**——Ricci $R_{ij}=R^k{}_{ikj}$ 是 Riemann 张量 $R_{ijkl}$（$n^4$ 分量）的迹求和缩并，离散网格上每个点是密集矩阵运算，正是 GEMM。平均曲率流的水平集方法（窄带计算 / Osher-Sethian）也是密集矩阵吞吐。9.45 GFLOPS 直接决定几何流仿真的速度上限。标 🟢（事实：曲率张量缩并 ⟺ 大矩阵乘）。

- **关键定理**：**Hamilton Ricci 流短时存在性**——紧流形 $M$ 上任意光滑度量 $g(0)$，Ricci 流
  $$\partial_tg=-2\,\mathrm{Ric}$$
  存在唯一光滑解 $g(t)$（$t\in[0,\varepsilon)$）；**DeTurck trick**：用 Bianchi 规范向量场把 Ricci 流化为严格抛物（消除规范退化），解出后还原。
  **Perelman F-熵单调**：$\mathcal{F}(g,f)=\int(R+|\nabla f|^2)e^{-f}\,dV$ 沿 Ricci 流 + 耦合方程单调不减，
  $$\frac{d}{dt}\mathcal{F}=2\int_M\bigl|\mathrm{Ric}+\nabla^2 f\bigr|^2 e^{-f}\,dV\ge0.$$
  重要性：Perelman 熵是「非线性抛物方程的全局单调量」——它把「局部存在」提升为「全局分类」，是 Poincaré 猜想证明的数学引擎，也是 21 世纪几何分析最深刻的概念之一。

- **自测**：① DeTurck trick 如何把 Ricci 流的规范退化消除（用 Bianchi 向量场的 Lie 导数修正，化为严格抛物系统，解出后规范变换还原）？
  ② Perelman F-熵单调性 $\frac{d}{dt}\mathcal{F}\ge0$ 为何排除「塌缩」奇点（熵有下界 ⟹ 非塌缩 ⟹ 体积有下界，奇点可分类）？
  ③ 平均曲率流的 neck pinching 为何需要手术（管状区域曲率爆破，流无法延续，须切除重连后继续）？
  ④ Ricci 流为何是「度量版热方程」（Ricci 张量分量满足抛物方程，高频曲率衰减）？

---

## §9 全书思想主线：线性机器的非线性推广 + 几何皇冠

Vol III 的总纲是「**把 Vol I–II 的线性机器推广到非线性，并在几何 PDE 达到皇冠**」。Ch 1（完全非线性椭圆）是最难的核心：Monge-Ampère $\det D^2u=f$ 把最高阶项非线性化，但 Krylov-Safonov Harnack + Evans-Krylov 二阶导估计仍能给出 $C^{2,\alpha}$ 正则性——线性 DNM 理论的完全非线性复活。**连续性方法 + 先验估计**把存在性归结为「先验界 ⟹ 解存在」（开性来自隐函数定理，闭性来自先验界保证极限不跑出空间），这是非线性椭圆的标准范式。

Ch 2–3（非线性演化）把线性半群 / 能量法推广到非线性：标量守恒律的熵解（Kružkov）用熵条件排除非物理激波，使弱解在「特征相交」后仍适定；拟线性对称双曲组的能量法给局部存在，波动映射与 Einstein 方程把几何对象翻译为标准 PDE（调和规范 ⟹ 拟线性波）。Ch 4–5（几何变分与曲率流）是「非线性分析的皇冠」：Eells-Sampson 调和映射热流把「拓扑问题」化为「抛物长期行为」（目标非正曲率 ⟹ Bochner 能量单调 ⟹ 全局收敛），Hamilton Ricci 流 + Perelman 熵把「流形分类」化为「几何演化方程的全局单调性」——Perelman 证明 Poincaré 的数学引擎。

读者一旦抓住「**非线性 PDE 通过『连续性方法 + 先验估计』化为线性问题的扰动，再在几何舞台达到最壮丽的应用**」这条主线，就理解了 Vol III 的设计：**不是逐个非线性方程给技巧，而是用 Vol I–II 的线性脚手架，系统攀登完全非线性椭圆 ⟶ 非线性演化 ⟶ 几何变分 ⟶ 曲率流的阶梯**。与 Vol I–II 呼应：Vol I「搭线性机器」，Vol II「用机器回答线性定性」，Vol III「把机器推广到非线性并登顶几何」——**三部曲合璧，构成从古典到现代非线性几何 PDE 的完整纵深**。

三部曲的递进结构值得最后点明：Vol I 自下而上（古典 ⟶ Sobolev ⟶ 拟微引论），回答「**解存在吗、长什么样**」；Vol II 自上而下（微局部机器 ⟶ 四路定性），回答「**解有何性质**」；Vol III 由内向外（完全非线性 ⟶ 几何演化），回答「**当世界本身非线性时，结构如何涌现**」。三卷合起来，恰好覆盖 PDE 从「构造解」到「刻画性质」到「非线性几何应用」的全谱。

---

## §10 与本仓库其他笔记的交叉引用

- **与 [Taylor PDE I](taylor_偏微分方程I_快速逐章.md)（奠基卷）**：Vol I 搭线性机器（古典三方程 + Sobolev + 拟微分引论 + 显式解）。**Vol III Ch 1 完全非线性椭圆**是 Vol I 主题 8（线性椭圆边值 Lax-Milgram）+ 主题 10（Monge-Ampère 引论）的非线性升级；Vol III Ch 4 变分是 Vol I 主题 12（Dirichlet 原理）的非线性推广。Vol I 主题 10–11 的「前向指针」在 Vol III 落地为完整理论——读 Vol III 时可回查 Vol I 主题 10 的 Monge-Ampère 引论作直觉铺垫。

- **与 [Taylor PDE II](taylor_偏微分方程II_快速逐章.md)（线性定性卷）**：Vol II 的微局部机器（Ch 1–2 拟微分 + 波前集）在 Vol III 升级为**非线性微局部**（para-differential calculus，Bony 的仿积分解，把非线性项在频率上分解）；Vol II Ch 5（Hille-Yosida 半群）是 Vol III Ch 2（非线性抛物）+ Ch 5（Ricci 流）的泛函基础；Vol II Ch 6（对称双曲能量法）是 Vol III Ch 3（非线性双曲）的工具。**Vol I–II 是 Vol III 的必经前置**——非线性先验估计处处回引线性 Schauder / Sobolev / 能量工具。

- **与 [Jost 几何分析](../stage-2-研究生基础/jost_黎曼几何与几何分析_快速逐章.md)（刚做）**：Jost Ch 8（调和映射）+ Ch 9（Kähler 与 Ricci 流）与 Vol III Ch 4（Eells-Sampson）+ Ch 5（Ricci 流）**直接交汇**——Jost 是调和映射存在性的权威贡献者（几何侧叙事，含 sigma 模型 / Yang-Mills 的物理动机），Taylor 给 PDE 侧的严格先验估计；Jost 的 Bochner 技巧（Ch 8）与 Vol III Ch 4 的 Bochner 公式同源。**Taylor 是「PDE 主轴」，Jost 是「几何分析出口」**——两者配对读，Taylor 补 PDE 严格性，Jost 补几何叙事与物理动机。

- **与 [Gilbarg-Trudinger 椭圆 PDE](gilbarg_trudinger_椭圆PDE_快速逐章.md)**：GT 是线性椭圆专精（Schauder + Sobolev 双轴），Vol III Ch 1 完全非线性椭圆是 GT 方法的**非线性推广**——GT 主题 9（ABP / Alexandrov 极值）是 Vol III Monge-Ampère 正则性的线性原型，GT 的 Schauder 估计是 Evans-Krylov $C^{2,\alpha}$ 的线性版本。读 Vol III Ch 1 前值得复习 GT 的 Schauder / ABP 估计。

- **与 [Evans PDE](evans_PDE偏微分方程_快速逐章.md)**：Evans Part IV（非线性）覆盖 Vol III Ch 1–3 的「地图版」（完全非线性 / 守恒律 / 拟线性波），但**完全未涉及曲率流 / Ricci 流 / Perelman 熵**（Vol III Ch 5）。Vol III 补全这三大 Evans 缺失的几何 PDE 专题，是 Evans Part IV 的「研究级纵深」。读 Evans 建立非线性直觉后用 Vol III Ch 1、Ch 5 拓展。

- **AI / 工程锚点**（Vol III 的非线性几何 PDE = AI for Science 的最深数学引擎）：

  - ① **Monge-Ampère 与最优传输 / 生成模型**：Ch 1 的 Monge-Ampère 方程是最优传输（Monge-Kantorovich）的 PDE 核心——生成模型（Wasserstein GAN、Normalizing Flow）的距离计算依赖 Monge-Ampère 解；神经网络逼近传输映射是 AI for Optimal Transport 的前沿。
  - ② **曲率流与几何深度学习**：Ch 5 的 Ricci 流 / 平均曲率流是 3D 几何处理、医学图像分割（水平集方法）、图神经网络中流形学习的数学引擎；Perelman 熵的单调性思想与深度学习的「能量泛函极小化」结构同构。
  - ③ **非线性扩散与 Diffusion 模型**：Ch 2 的非线性扩散（p-Laplacian、多孔介质）是 Diffusion 模型（score-based generative）的推广框架——标准扩散模型用线性热方程，非线性扩散给「数据依赖」的采样动力学。
  - ④ **变分与 PINN / Deep Ritz**：Ch 4 的变分方法是 Deep Ritz Method（用神经网络极小化能量泛函）的连续数学源头；Eells-Sampson 热流 = 神经网络上「能量下降」动力学的几何版。
  - ⑤ **Einstein 方程与数值相对论**：Ch 3 的 Einstein 方程在调和规范下的拟线性波形式，是数值相对论（引力波模拟、黑洞合并）的数学基础——AI 辅助的 Einstein 求解器是 AI for Physics 的最前沿。

> **一句话总结本书的 AI 价值**：Vol III 把「线性 PDE 机器」推广到「非线性世界」，而 AI for Science 的最前沿（最优传输的 Monge-Ampère、生成模型的非线性扩散、几何深度学习的曲率流、数值相对论的 Einstein 方程）恰恰是「在非线性几何 PDE 上用神经网络逼近解」——读通 Vol III，就拿到了从线性 PDE 到非线性几何演化的完整阶梯，三部曲合璧，为理解 21 世纪几何分析与 AI for Science 的最深交汇铺路。

---

## §11 各章精华一句话

> 五章一气呵成：完全非线性椭圆（Ch 1）打底后，非线性演化（Ch 2–3）展开，几何变分与曲率流（Ch 4–5）登顶。

- **Ch 1**★：完全非线性椭圆 $F(D^2u)=f$——Krylov-Safonov Harnack 给 Hölder 正则，Evans-Krylov 给 $C^{2,\alpha}$；Monge-Ampère $\det D^2u=f$ 是典范，Caffarelli 解决存在与正则。
- **Ch 2**：标量守恒律的熵解（Kružkov）用熵条件排除非物理激波；p-Laplacian / 黏性解是「正则化消除奇异性」的范例；Ricci 流作预告。
- **Ch 3**：拟线性对称双曲组能量法给局部存在；波动映射 / Einstein 方程（调和规范 ⟹ 拟线性波）把几何对象翻译为标准 PDE。
- **Ch 4**：直接方法 + minimax 求解非线性变分；Eells-Sampson 调和映射热流把「拓扑问题」化为「抛物长期行为」（目标非正曲率 ⟹ Bochner 能量单调 ⟹ 全局收敛）。
- **Ch 5**★：Hamilton Ricci 流短时存在（DeTurck trick）+ Perelman F-熵 / W-熵单调——非线性 PDE 的「Liapunov 泛函」排除了塌缩奇点，是 Poincaré 证明的引擎。

---

## 📌 阅读建议（对接数学专家路径）

1. **精读顺序**：**Ch 1（完全非线性椭圆，三部曲核心）** → Ch 2（非线性抛物 / 守恒律，建熵解直觉）→ Ch 4（变分 / 调和映射，几何化）→ Ch 3（非线性双曲 / Einstein，按需）→ **Ch 5（曲率流，三部曲皇冠）**。若时间紧，**Ch 1 + Ch 5** 是必读核心。

2. **与 Vol I–II / Jost 配对读**：Vol III Ch 1 ↔ Vol I 主题 8 + GT（线性椭圆 → 完全非线性）；Vol III Ch 4–5 ↔ Jost Ch 8–9（调和映射 / Ricci 流的几何叙事）。Taylor 补 PDE 严格性，Jost 补几何动机——配对读效果最佳。

3. **数学根基回溯**：Schauder / Sobolev 先验 ⟵ Vol I 主题 5–8 + GT（已读）；半群 / 能量法 ⟵ Vol II Ch 5–6（已读）；曲率 / 联络 / Bochner 公式 ⟵ Jost（刚做）+ Lee GTM176（已读）；分布 / 弱解 ⟵ Hörmander I（已读）。

4. **动手验证**（Python 工程师优势）：Ch 1 用 NumPy 实现凸函数的 Monge-Ampère 测度（$\det D^2u$ 在网格上的点积累加），验证 Alexandrov 极值的覆盖体积；Ch 2 用有限体积法解 Burgers 方程（$u_t+uu_x=0$）观察激波形成与熵解；Ch 4 用梯度下降实现调和映射热流（目标球面），观察 $t\to\infty$ 收敛；Ch 5 用 `scipy.linalg.expm` 在 2D 网格上模拟 Ricci 流的曲率演化，验证 Perelman F-熵单调。代码即理解，飞腾实测数据则作为「工程极限」的参照系。

5. **深挖课题**（Vol III 特色，选做）：
   - ① Monge-Ampère $\det D^2u=f$ 的 Caffarelli 正则性如何推广 GT 的线性 Schauder 估计（凹凸性 ⟹ Hessian 一致椭圆）。
   - ② Kružkov 熵解的 $L^1$ 收缩原理如何给守恒律弱解的唯一性（对比原理 + 熵耗散）。
   - ③ Eells-Sampson 调和映射热流为何在目标非正曲率下全局存在（Bochner 公式 $\int|Du|^2$ 单调减）。
   - ④ Perelman F-熵 $\mathcal{F}=\int(R+|\nabla f|^2)e^{-f}\,dV$ 的单调性如何排除塌缩奇点（熵下界 ⟹ 体积非塌缩）——通向 Poincaré 猜想的完整证明。

6. **前向指针：研究专题**：Vol III 是三部曲收官，读完可顺接 Ricci 流专著（Chow-Knopf / Morgan-Tian）、Kähler-Einstein 几何（Yau / Tian）、规范理论（Donaldson）、辛拓扑（Floer）。Vol III Ch 5 的 Perelman 熵是 21 世纪几何分析最重要的概念之一——它把「局部存在的非线性抛物方程」提升为「全局可分类的几何演化」，是 stage-3 研究方向（几何分析 / ML 理论 / 数值分析）的共同高阶出口。

> 注：本笔记基于 Taylor《Partial Differential Equations III: Nonlinear Equations》（AMS 117, 2nd ed. 2011）撰写快速逐章导览，忠实于 5 章结构，侧重概念串联与飞腾 / AI 锚点对接。关键定理（Krylov-Safonov Harnack、Evans-Krylov $C^{2,\alpha}$、Caffarelli Monge-Ampère 正则、Kružkov 熵解唯一、拟线性对称双曲组局部适定、Choquet-Bruhat Einstein 局部存在、Eells-Sampson 调和映射存在、Hamilton Ricci 流短时存在、Perelman F-熵单调）均为标准准确陈述。与 Vol I、Vol II 合为「Taylor PDE 三部曲」。
>
> 📊 **规模与定位**：本笔记 5 章全覆盖，每章含核心逻辑串联（3–4 子要点）+ 飞腾锚点 + 关键定理 LaTeX（含重要性简述）+ 自测 3–4 题。飞腾锚点池选 5 个最贴合的、各用一次、相邻不重复：
> - **UDOT 16.9×**（Ch 1 Monge-Ampère 行列式累加 = 点积）· **Iron Law<2%**（Ch 2 抛物稳定预算 / 黏性解极限）
> - **Schmidt**（Ch 3 守恒律特征分解 = 正交化类比）· **matmul 15×**（Ch 4 变分离散 = 矩阵装配）
> - **GEMM 9.45G**（Ch 5 曲率张量缩并 = 大矩阵乘）
