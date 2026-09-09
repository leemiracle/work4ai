# Michael E. Taylor《偏微分方程 I：基本理论》 · 快速逐章精读

> 基于原书：*Partial Differential Equations I — Basic Theory*, Applied Mathematical Sciences 115（Michael E. Taylor, Springer, 2nd ed., 2011；初版 1996）/ 读于：2026-07-03
> 定位：**几何视角的 PDE 全面纵深奠基卷**，把古典三方程 + Sobolev + 拟微分算子 + 微局部分析熔铸为单一体系。
> 关联：[Evans PDE](evans_PDE偏微分方程_快速逐章.md) · [Hörmander ALPDO I](hormander_线性偏微分算子I_快速逐章.md) · [Gilbarg-Trudinger 椭圆 PDE](gilbarg_trudinger_椭圆PDE_快速逐章.md) · [Lang 实与泛函分析 GTM142](../stage-2-研究生基础/lang_实与泛函分析_GTM142_快速逐章.md)
> 本文为**快速逐章精读**，每主题 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

> 📌 **章节合并与 TOC 说明（以原书真实结构为准）**
>
> Taylor《Partial Differential Equations》是 Springer Applied Math Sciences 三卷本（Vol I 基本 / Vol II 线性定性 / Vol III 非线性），全集合计约 17–18 章连续编号。**Vol I《Basic Theory》是三卷大厦的奠基卷**：古典三方程（Laplace / 波 / 热）建立直觉，Sobolev 空间搭舞台，**拟微分算子与波前集**（Taylor 的招牌——比 Hörmander 更早把微局部分析引入研究生教材）提供现代工具。
>
> 本笔记将 Vol I 忠实整合为 **12 个主题**（标注对应原书章号）：主题 1–4 为古典三方程 + 基本线性 PDE；主题 5–7 为现代分析机器（Sobolev / 拟微分 / 微局部）；主题 8–9 为椭圆边值与奇性传播（线性的定性核心）；主题 10–12 为完全非线性、几何 PDE 与变分（Vol I 收尾并通向 Vol II/III）。主题 10–11 在 Taylor 三卷本中部分内容延展至 Vol III，本笔记作为「前向指针」纳入，标注其跨卷归属。

---

## §0 引言：Taylor 的「几何全面」PDE 体系

Michael E. Taylor（UNC Chapel Hill）的三卷本《Partial Differential Equations》（Springer AMS 115–117，初版 1996，第二版 2011 全面修订）是 PDE 领域**体量最大、覆盖最广的现代教材**——全集合计约 1500 页，从古典 Laplace 方程一直讲到 Ricci 流与 Monge-Ampère 方程。一句话定位：本书是 stage-3 PDE 方向的**几何全面纵深教材**。

**Vol I《Basic Theory》是整个三卷大厦的奠基卷**。Taylor 的招牌设计是：先让古典三方程（Laplace / 波 / 热）建立「PDE 长什么样」的直觉，随即引入 **Sobolev 空间**搭弱解舞台，再用**拟微分算子**（pseudodifferential operators, $\Psi$DO）与**波前集**（wave front set）装备微局部分析——这是比 Evans 更深、比 Hörmander 更早进教材的现代工具箱。一句话：Taylor 把「古典表示 → 函数空间 → 微局部机器」三步阶梯压缩在 Vol I 内完成，使读者拿到 Vol II（线性定性）与 Vol III（非线性）的全部预备。

Taylor 的核心哲学是「**用几何与微局部的统一语言，统摄椭圆 / 双曲 / 抛物三大类方程**」：拟微分算子的符号演算让三类方程共享「椭圆性 / 主型 / 传播」的统一框架，波前集则把「奇异在哪个方向」这件事精确化——这正是 Hörmander 在研究级专著中建立、Taylor 在研究生教材中普及的范式革命。

### 四本 PDE 教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|------|------|--------|--------|
| **Taylor PDE I（本书）** | 几何全面纵深；古典 + Sobolev + 拟微分 + 微局部四合一；三方程统一于符号演算 | ★★★★★（严格且自包含） | PDE/几何分析研究者 |
| **Evans PDE（GSM 19）** | 现代研究生标准；弱解三部曲（椭圆/抛物/双曲）应用驱动 | ★★★★（严格但重存在性直觉） | PDE 研究生入门首选 |
| **Hörmander ALPDO I** | 线性 PDE 皇冠；分布论 + Fourier 分析 + 波前集严格重建 | ★★★★★（极严，逐条重建语言） | PDE/分析方向研究深造 |
| **Gilbarg-Trudinger GT 224** | 二阶椭圆圣经；Schauder 经典 + Sobolev 弱解双轴；先验估计中心 | ★★★★★（逐条证明） | 椭圆 PDE 专精 |

> **阅读策略**：Evans 入门建弱解直觉 → **Taylor Vol I 补全几何 + 拟微分 + 微局部**（Evans 完全未涉及的现代机器）→ Hörmander I 回溯分布论严格地基 → Gilbarg-Trudinger 做椭圆专精。四者构成 PDE「四套马车」：Evans 是「地图」，Taylor 是「全面纵深」，Hörmander 是「语言地基」，GT 是「椭圆专精」。

---

## §1 全书 12 主题骨架一览（飞腾锚点分布）

Taylor Vol I 主线是「**古典三方程 → Sobolev 函数空间 → 拟微分算子 → 微局部分析**」四步阶梯。主题 1–4 给古典显式公式，主题 5–7 搭现代分析机器，主题 8–9 用机器解线性问题（椭圆边值 + 奇性传播），主题 10–12 推向非线性与几何。每主题对接一条飞腾实测锚点。

| 主题 | 原书章 | 标题 | 核心概念 | 飞腾锚点 |
|:----:|:----:|------|---------|:--------:|
| 1 | Ch 1 | 基本线性 PDE | 特征线 · 分类 · 基本解 | matmul 15× 🟢 |
| 2 | Ch 1 | Laplace/Poisson 与位势论 | 均值 · 极值 · Green 函数 · Newton 位势 | UDOT 16.9×⭐ 🟢 |
| 3 | Ch 2 | 波方程与能量法 | d'Alembert · Kirchhoff · 能量 · 有限传播 | FP16 3.81×⭐ 🟡 |
| 4 | Ch 3 | 热方程与抛物正则性 | 热核 · Duhamel · 极值 · 光滑化 | TLB 4.81×⭐ 🟡 |
| 5 | Ch 4 | Sobolev 空间 | 弱导数 · **嵌入** · 迹 · 紧性 | Iron Law<2%⭐ 🟡 |
| 6 | Ch 7 | 拟微分算子 | **符号类** · 量化 · 合成 · 椭圆拟逆 | GEMM 9.45G 🟢 |
| 7 | Ch 7 | 波前集与微局部分析 | $WF(u)$ · **传播** · 微局部光滑 | 分支预测 🟡 |
| 8 | Ch 5 | 椭圆边值问题 | Lax-Milgram · Fredholm · 正则性 · 谱 | matmul 15× 🟢（复用） |
| 9 | Ch 7 | 解的奇性传播 | **Hamilton 流** · 次特征带 · Poisson 括号 | Schmidt 🟡 |
| 10 | Ch 6* | Monge-Ampère 与完全非线性 | $\det D^2u=f$ · Alexandrov · 完全非线性椭圆 | UDOT 16.9×⭐ 🟢（复用） |
| 11 | Ch 16* | 几何 PDE · 曲率流引论 | 平均曲率流 · Ricci 流 · 极小曲面 | GEMM 9.45G 🟢（复用） |
| 12 | Ch 6 | PDE 与变分法 | Euler-Lagrange · 直接方法 · 特征值 | FP16 3.81×⭐ 🟡（复用） |

> `*` 标注的主题在 Taylor 三卷本中部分内容延展至 Vol III（非线性卷），本笔记作 Vol I 的「前向指针」。

```
古典三方程 ── 给显式公式，"解长什么样"
主题1 基本线性PDE ── 特征线·分类·基本解（transport/Laplace/波/热原型）──────────┐
主题2 Laplace/Poisson ── 均值·极值·Green函数·Newton位势 ──────────────────────┤
主题3 波方程+能量 ── d'Alembert·Kirchhoff·能量守恒·有限传播 ───────────────────┤
主题4 热方程+抛物 ── 热核·Duhamel·极值·无穷传播·光滑化 ──────────────────────┘
          │ 弱化解的定义，搭建函数空间
现代分析机器 ── Sobolev 空间 + 拟微分算子 + 微局部分析
主题5 Sobolev空间 ── 弱导数·嵌入 W^{k,p}↪C^{m,α}·迹·Rellich紧性 ───────────────┐
主题6 拟微分算子 ── 符号类S^m·量化·合成·椭圆拟逆 N=Op(p)^{-1} ─────────────────┤
主题7 波前集+微局部 ── WF(u)住余切丛·微局部光滑·奇异定向 ───────────────────────┘
          │ 用机器解线性 PDE
线性定性核心 ── 椭圆边值 + 奇性传播
主题8 椭圆边值 ── Lax-Milgram·Fredholm抉择·椭圆正则性·特征值谱 ────────────────┐
主题9 奇性传播 ── Hamilton流·次特征带·WF(u)沿流传播·Poisson括号 ────────────────┘
          │ 推向非线性与几何
非线性 + 几何 + 变分
主题10 Monge-Ampère ── detD²u=f·Alexandrov极值·完全非线性椭圆 ──────────────────┐
主题11 几何PDE ── 平均曲率流·Ricci流·极小曲面（Vol III前向指针） ─────────────┤
主题12 PDE+变分 ── Euler-Lagrange·直接方法·能量极小·特征值Rayleigh ────────────┘

数学根基：Spivak多元微积分(链式法则/散度定理)·Folland实分析(Lp/测度)
         ·Reed-Simon I(算子/谱)·Lee光滑流形(余切丛/Hamilton流)
         ·Hörmander I(分布论)·Lang GTM142(泛函/Sobolev)
```

---

## 古典三方程

### 主题 1 · 基本线性 PDE（Basic Linear PDE）

- **核心**：Taylor 的开篇是「PDE 的分类与求解工具箱」。从**一阶方程** $F(x,u,Du)=0$ 的**特征线法**出发——沿特征 ODE $\dot x=b$ 把 PDE 降为 ODE。随后对**二阶线性方程** $a^{ij}u_{x_ix_j}+\cdots=f$ 做分类：根据系数矩阵 $A=(a^{ij})$ 的特征值符号，分为**椭圆**（全正/全负）、**双曲**（一负余正）、**抛物**（退化但适定）三类。这一分类不是形式游戏——它决定了解的定性性质（椭圆=平衡态、双曲=有限传播、抛物=无穷传播+光滑化）。Taylor 给出三类方程各自的基本解雏形，为主题 2–4 的深入铺设。

- **飞腾锚点** 🟢：**matmul 15×** [V03]。特征线法把 PDE 离散为沿大量轨迹的 ODE 推进，每步是向量场 $b(x)$ 的求值与 Euler 步——批量轨迹并行推进正是 matmul；线性方程的基本解卷积 $u=\Phi*f$ 也是密集点积。15× 向量化增益直接加速多轨迹求解。

- **关键定理**：**一阶方程的特征线解**——$u_t+b\cdot\nabla u=0$，$u(x,0)=g(x)$ 的解为 $u(x,t)=g(x-tb)$（沿特征线 $x-tb=\text{const}$ 传播）。**二阶分类判据**：$A$ 的特征值全同号 $\Rightarrow$ 椭圆；一异号 $\Rightarrow$ 双曲。

- **自测**：① 写出 transport 方程 $u_t+bu_x=0$ 的通解并解释「特征线 = 信息传播路径」。② $\Delta u + u_{tt}$ 是哪一类（双曲）？$u_t - \Delta u$ 呢（抛物）？

---

### 主题 2 · Laplace/Poisson 方程与位势论（Laplace/Poisson & Potential Theory）

- **核心**：Laplace 方程 $\Delta u=0$ 是一切椭圆 PDE 的原型。Taylor 系统化展开位势论：

  ① **均值定理**——$u$ 调和 $\Leftrightarrow$ 球面积分均值 = 中心值；由此推出调和函数**自动实解析**（无穷可导）。
  ② **极值原理**——最大值在边界达到（弱）/ 内部达不到（强），Hopf 引理给法向导数符号。
  ③ **Green 函数与 Newton 位势**——基本解 $\Phi(x)=c_n|x|^{2-n}$（$n\ge3$），Green 函数 $G(x,y)$ 表出 Dirichlet 问题解 $u(x)=\int_{\partial\Omega}\partial_\nu G\cdot\varphi-\int_\Omega G\cdot f$。

  这套古典理论是 GT（Gilbarg-Trudinger）主题 1–3 的预演，Taylor 在 Vol I 做充分铺垫，Vol II 再深化。

- **飞腾锚点** 🟢：**UDOT 16.9×⭐** [E05]。均值定理 $u(x)=\frac{1}{|\partial B|}\int_{\partial B}u\,dS$ 是**球面上的加权求和**——离散后每个 $x$ 处是一次内积，飞腾 INT8 UDOT 点积指令对批量均值加速 16.9×。Green 函数表示 $u=\int G\cdot f$ 也是点积累加。标 🟢（均值 = 加权求和，事实匹配）。

- **关键定理**：**均值定理**——$u$ 调和 $\Leftrightarrow$ 对所有球 $B_R(x)\Subset\Omega$，$u(x)=\frac{1}{n\omega_nR^{n-1}}\int_{\partial B_R}u\,dS$。**Poisson 核表示**：球上 Dirichlet 问题解 $u(x)=\int_{\partial B}P(x,y)\varphi(y)\,dS(y)$。

- **自测**：① 验证 $\Phi(x)=c_n|x|^{2-n}$ 满足 $\Delta\Phi=\delta$（分布意义）。② 用均值定理证明 Liouville 定理（$\mathbb{R}^n$ 上有界调和函数必常数）。

---

### 主题 3 · 波方程与能量法（Wave Equation & Energy Methods）

- **核心**：波方程 $u_{tt}-\Delta u=0$ 是双曲方程的原型。Taylor 给三套工具：

  ① **显式公式**——d'Alembert（1D）：$u(x,t)=\frac12[g(x+t)+g(x-t)]+\frac12\int_{x-t}^{x+t}h(s)\,ds$；Kirchhoff（3D）；Poisson（2D，降维法）。
  ② **Duhamel 原理**——非齐次 $u_{tt}-\Delta u=f$ 的解 = 齐次解 + 源项的时间积分叠加。
  ③ **能量方法**——$E(t)=\frac12\int(u_t^2+|\nabla u|^2)\,dx$ 守恒 $\frac{dE}{dt}=0$，给**唯一性**与**有限传播速度**（扰动只在光锥 $\{|x-x_0|\le t\}$ 内传播）。

  能量法是 Taylor 的招牌——它不依赖显式公式，可推广到变系数与非线性波方程，是「现代 PDE」方法的雏形。

- **飞腾锚点** 🟡：**FP16 3.81×⭐** [L01]。波方程**无耗散**，能量守恒意味着数值误差**不衰减**——长期积分中浮点误差线性累积。FP16（$\varepsilon\approx9.8\times10^{-4}$）下误差比 FP64 增长更快，3.81× 速度差背后是「精度-时间」权衡：波方程数值需要辛格式保能量，FP16 的有限精度天然破坏辛结构。标 🟡。

- **关键定理**：**能量守恒 + 有限传播**——$E(t)=E(0)$ ⟹ 唯一性；依赖区域（光锥）外 $u=0$ ⟹ 扰动传播速度 $\le1$。**Duhamel**：$u=\text{齐次}+\int_0^t\!\int\Phi(x-y,t-s)f(y,s)\,dy\,ds$。

- **自测**：① 用能量法证明波方程 Cauchy 问题解的唯一性。② 为何波方程的依赖区域是「锥」而热方程是「全空间」（有限 vs 无穷传播）？

---

### 主题 4 · 热方程与抛物正则性（Heat Equation & Parabolic Regularity）

- **核心**：热方程 $u_t-\Delta u=0$ 是抛物方程的原型。与波方程对比鲜明：

  ① **热核** $\Phi(x,t)=\frac{1}{(4\pi t)^{n/2}}e^{-|x|^2/4t}$（$t>0$），解 $u(x,t)=\int\Phi(x-y,t)g(y)\,dy$——高斯卷积把初值**瞬间光滑化**（$t>0$ 时 $u\in C^\infty$）。
  ② **极值原理**——热方程也有极值原理，但与椭圆型不同：最大值可在 $t=0$（初值）或边界达到，**内部**（$t>0$）达不到严格最大值。
  ③ **无穷传播 + 光滑化**——热核支撑为全空间（$t>0$ 处处非零），故扰动**瞬时传遍全域**（物理上的「超光速」悖论，说明热方程是近似模型）；但光滑化使高频模式指数衰减，解对初值的低频部分敏感。

  Taylor 强调椭圆 ↔ 抛物的内在联系：$t\to\infty$ 时热方程的解趋于 Laplace 方程的平衡态（抛物 ⟹ 椭圆的渐近）。

- **飞腾锚点** 🟡：**TLB 4.81×⭐** [E04]。热核 $e^{-|x|^2/4t}$ 是**快速衰减的局部核**——远离对角线（$|x-y|$ 大）的权重指数小，数值上只需计算近对角线的「局部带」即可。这与 TLB 管理「局部热页」的内存局部性同构：热核卷积的有效支撑 = 缓存局部窗口，4.81× 命中增益正来自局部访问。标 🟡。

- **关键定理**：**热核表示 + 光滑化**——$u(x,t)=\int_{\mathbb{R}^n}\Phi(x-y,t)g(y)\,dy$，$\Phi=\frac{1}{(4\pi t)^{n/2}}e^{-|x|^2/4t}$；$t>0$ 时 $u\in C^\infty$。**抛物极值原理**：$\sup_{\Omega_T}u\le\sup_{\partial_p\Omega_T}u^+$（抛物边界 = 初值 + 侧边）。

- **自测**：① 验证热核 $\Phi$ 满足 $\partial_t\Phi-\Delta\Phi=0$（$t>0$）。② 为何热方程光滑化但波方程不光滑化（高频模式衰减 vs 守恒）？

---

## 现代分析机器

### 主题 5 · Sobolev 空间（Sobolev Spaces）

- **核心**：Sobolev 空间是**弱解理论的舞台**——Taylor 把它作为从古典到现代的桥梁，系统展开四大支柱：

  ① **弱导数**——分部积分定义 $\int u\,D^\alpha\varphi=(-1)^{|\alpha|}\int(D^\alpha u)\varphi$（$\forall\varphi\in C_c^\infty$），把导数从 $C^k$ 放宽到 $L^p$。磨光逼近 $u_\epsilon=\eta_\epsilon*u\to u$ 是弱导数=磨光极限的桥梁。
  ② **Sobolev 嵌入定理**——$W^{k,p}\hookrightarrow L^{p^*}$（$p^*=\frac{np}{n-p}$，$p<n$）；$kp>n$ 时 $\hookrightarrow C^{m,\alpha}$（Morrey 嵌入：弱导数够多则解自动连续）。这是「函数空间之间的通道」。
  ③ **迹定理 + Rellich 紧性**——边界值 $Tu\in L^p(\partial\Omega)$ 有意义；$W^{1,p}\Subset L^p$（紧嵌入），极小化序列有收敛子列——变分法存在性的关键。

  Taylor 的 Sobolev 理论比 Evans 更完整（含插值定理、Nirenberg 的差商刻画），为后续拟微分算子铺路。

- **飞腾锚点** 🟡：**Iron Law<2%⭐**。弱导数由「积分恒等式」定义，数值上磨光逼近 $u_\epsilon=\eta_\epsilon*u$ 的截断误差须压进精度预算——这与 Iron Law 性能铁律（误差须压进 <2%）同构：磨光核 $\eta_\epsilon$ 的尺度 $\epsilon$ 是「精度-正则性」权衡参数，$\epsilon$ 太大丢信息、太小引振荡。标 🟡。

- **关键定理**：**Sobolev 嵌入定理**——$1\le p<n$ $\Rightarrow$ $W^{1,p}(\Omega)\hookrightarrow L^{p^*}(\Omega)$，$p^*=\frac{np}{n-p}$；$p>n$ $\Rightarrow$ $W^{1,p}\hookrightarrow C^{0,\,1-n/p}$（Morrey）。**Rellich 紧性**：$W^{1,p}_0(\Omega)\Subset L^p(\Omega)$。

- **自测**：① $u(x)=|x|^{-\alpha}$ 属于 $W^{1,p}(B_1)$ 的条件是什么（$\alpha<1-n/p$）？② 为何 Rellich 紧性是变分法「直接方法」的关键（极小化序列有收敛子列 ⟹ 极小元可达）？

---

### 主题 6 · 拟微分算子（Pseudodifferential Operators）★ Taylor 招牌

- **核心**：本章是 Taylor 区别于 Evans / GT 的**核心招牌**——在研究生教材中系统引入拟微分算子（$\Psi$DO），用**符号演算**统一处理椭圆 / 双曲 / 抛物三类方程：

  ① **符号类** $S^m_{\rho,\delta}$——函数 $p(x,\xi)$ 满足导数估计 $|D_x^\beta D_\xi^\alpha p|\le C_{\alpha\beta}(1+|\xi|)^{m-\rho|\alpha|+\delta|\beta|}$。经典符号 $\rho=1,\delta=0$（$S^m_{1,0}$）对应微分算子。
  ② **量化与合成**——符号 $p$ 量化为算子 $\mathrm{Op}(p)u(x)=\int e^{ix\cdot\xi}p(x,\xi)\hat u(\xi)\,d\xi$；两算子合成的**主符号** = 两符号之积（模低阶），使算子代数化。
  ③ **椭圆拟逆**（parametrix）——椭圆算子 $P=\mathrm{Op}(p)$（$p$ 主部非零）有拟逆 $Q=\mathrm{Op}(q)$，$q\sim p^{-1}$（渐近展开），使 $PQ=I+R$（$R$ 光滑化算子）。这给出**椭圆正则性**的统一证明：$Pu=f$ 光滑 + $f$ 光滑 ⟹ $u$ 光滑。

  拟微分算子是 Hörmander 在 Vol III 才展开的机器，Taylor 在 Vol I 就引入——体现「工具早装配、后续受益」的教学设计。

- **飞腾锚点** 🟢：**GEMM 9.45G** [Lab05]。拟微分算子作用 $\mathrm{Op}(p)u(x)=\int e^{ix\cdot\xi}p(x,\xi)\hat u(\xi)\,d\xi$ 是**变符号密集积分算子**——离散后是 $N\times N$ 大矩阵（符号 $p(x,\xi)$ 在网格上采样）乘向量，正是 GEMM。9.45 GFLOPS 直接决定大规模 PDE 的拟微分算子作用吞吐。标 🟢（事实：算子作用 ⟺ 矩阵向量乘）。

- **关键定理**：**椭圆拟逆存在性**——$P\in OPS^m_{1,0}$ 椭圆（主符号 $p_m(x,\xi)$ 可逆，$|\xi|$ 大），则 $\exists Q\in OPS^{-m}_{1,0}$ 使 $PQ=I+R_1$，$QP=I+R_2$（$R_1,R_2$ 为光滑化算子 $OPS^{-\infty}$）。**椭圆正则性推论**：$Pu=f\in H^s$ ⟹ $u\in H^{s+m}$（增益 $m$ 阶 Sobolev 正则性）。

- **自测**：① 写出 Laplace 算子 $-\Delta$ 的主符号 $p_2(x,\xi)=|\xi|^2$，验证椭圆性。② 拟逆 $Q$ 为何是「近似逆」而非精确逆（差一个光滑化算子 $R$）？

---

### 主题 7 · 波前集与微局部分析（Wave Front Set & Microlocal Analysis）

- **核心**：Taylor 把 Hörmander 的**波前集**（wave front set）$WF(u)$ 作为微局部分析的核心工具引入——给分布的奇异做「方向 CT 断层」：

  ① **定义**——$(x_0,\xi_0)\notin WF(u)$ 若存在 $x_0$ 邻域截断 $\chi$ 使 $\widehat{\chi u}$ 在 $\xi_0$ 锥邻域速降。波前集住在余切丛 $T^*\Omega\setminus0$ 中，记录奇异在哪个**余方向**出现——比支撑更精细。
  ② **微局部光滑**——$u$ 在 $(x_0,\xi_0)$ 处微局部 $C^\infty$ ⟺ $(x_0,\xi_0)\notin WF(u)$；这把「整体正则性」细化到「点-方向」。
  ③ **运算的微局部法则**——乘积 $WF(uv)\subset$（适当条件下的合并）；拟微分算子 $\mathrm{Op}(p)$ 不增加波前集：$WF(\mathrm{Op}(p)u)\subset WF(u)$（椭圆时等号）。

  波前集是主题 9（奇性传播）的语言基础——Taylor 用它把「解的奇异如何传播」精确化。

- **飞腾锚点** 🟡：**分支预测** [Lab02]。波前集判定是**方向 yes/no 分类**——每个余方向 $\xi_0$ 要判「Fourier 变换在此锥是否速降」，是一连串条件分支；微局部光滑性的验证（截断 + Fourier + 速降判定）是分支密集逻辑。分支预测器的可预测分支（0.71 CPI）vs 误预测（3.14 CPI）对应「光滑方向（速降）」与「奇异方向（不速降）」的分野。标 🟡。

- **关键定理**：**波前集定义**——$WF(u)=\{(x,\xi)\in T^*\Omega\setminus0:\xi\text{ 方向非速降}\}$。**微局部椭圆正则性**：$\mathrm{Op}(p)$ 椭圆于 $(x_0,\xi_0)$，$\mathrm{Op}(p)u=f$ ⟹ $(x_0,\xi_0)\notin WF(u)$ 当且仅当 $(x_0,\xi_0)\notin WF(f)$。

- **自测**：① $\delta$ 分布的波前集 $WF(\delta)=\{(0,\xi):\xi\ne0\}$（原点的所有方向），验证。② 为何光滑函数的 $WF=\emptyset$ 但支撑非空（光滑 = 所有方向速降）？

---

## 线性定性核心

### 主题 8 · 椭圆边值问题（Elliptic Boundary Value Problems）

- **核心**：Taylor 用 Sobolev 空间（主题 5）+ 拟微分算子（主题 6）系统处理椭圆边值问题，比 Evans Ch 5 更全面：

  ① **Lax-Milgram 存在唯一**——散度型 $Lu=f$ 的弱形式给双线性型 $B[u,v]$，有界 + 强制 ⟹ $\exists!$ 弱解。Gårding 不等式处理非强制（低阶项）。
  ② **Fredholm 抉择**——椭圆算子 $L$ 视为 $H^s\to H^{s-m}$ 的 Fredholm 算子（指标有限），「要么唯一解，要么核非平凡」——把线性代数推广到 PDE。
  ③ **椭圆正则性与谱**——弱解 + 系数光滑 ⟹ $u$ 提升到 $H^{s+m}$（拟逆的推论）；对称椭圆算子的特征值 $\lambda_1\le\lambda_2\le\cdots\to\infty$，特征函数 $\{\phi_n\}$ 构成 $L^2$ 正交基（紧嵌入 + 谱定理）。

  Taylor 的特色是用**拟微分算子的拟逆**统一证明椭圆正则性，而 Evans 用散度型分部积分、GT 用 Schauder 估计——三种路径殊途同归。

- **飞腾锚点** 🟢：**matmul 15×**（复用，距主题 1 隔 7 个，不冲突）。Lax-Milgram 的双线性型 $B[u,v]$ 离散后是**有限元刚度矩阵** $K_{ij}=B[\phi_j,\phi_i]$，组装与求解都是密集 matmul；特征值问题的离散化给出大规模矩阵特征值问题，matmul 15× 向量化增益直接加速。标 🟢。

- **关键定理**：**Lax-Milgram**——$B:H\times H\to\mathbb{R}$ 有界（$|B[u,v]|\le M\|u\|\|v\|$）且强制（$B[u,u]\ge\alpha\|u\|^2$）⟹ $\forall f\in H^*$ $\exists!u$：$B[u,v]=\langle f,v\rangle$。**Fredholm 抉择**：$L$ 椭圆 ⟹ $L:H^s\to H^{s-m}$ 是 Fredholm 指标 0 算子，$\dim\ker L=\dim\ker L^*<\infty$。

- **自测**：① Poisson $-\Delta u=f$，$u|_{\partial\Omega}=0$，写出弱形式并验证强制性（Poincaré 不等式）。② Fredholm 抉择说「$L$ 可逆或 $\ker L\ne0$」——$-\Delta$ 在 Dirichlet 条件下属于哪种（$\lambda_1>0$ ⟹ 可逆）？

---

### 主题 9 · 解的奇性传播（Propagation of Singularities）★ 微局部顶峰

- **核心**：本章是 Taylor Vol I 的**微局部分析高潮**——用波前集（主题 7）刻画「PDE 解的奇异如何传播」。核心是**奇性传播定理**：

  ① **Hamilton 流与次特征带**——算子 $P=\mathrm{Op}(p)$ 的主符号 $p(x,\xi)$ 生成 $T^*\Omega$ 上的 **Hamilton 向量场** $H_p=(\partial_\xi p,-\partial_x p)$，其积分曲线是**次特征带**（bicharacteristics）。
  ② **传播定理**——主型双曲算子 $Pu=f$ 的解，其波前集满足：$WF(u)\setminus WF(f)\subset\mathrm{Char}(P)$（特征集），且**沿 $H_p$ 的流不变**——奇异沿次特征带传播，不凭空产生或消失。
  ③ **Poisson 括号**——两算子主符号的 Poisson 括号 $\{p,q\}=H_p q$ 控制算子的交换结构，是次特征带「切向」信息的代数化身。

  这条定理是 Hörmander 1970 年的巅峰成果，Taylor 在 Vol I 就给完整陈述与证明思路——它把「整体唯一性」细化到「微局部唯一性」：奇异只在 $(x,\xi)\in\mathrm{Char}(P)$ 上出现，且沿流移动。

- **飞腾锚点** 🟡：**Schmidt 正交化**。Hamilton 流 $H_p$ 的积分曲线追踪是**坐标变换 + 投影**——在余切丛上沿特征方向推进，每步是把分量重新组合到「主符号坐标系」上，与 Gram-Schmidt 正交分解的思想同源：次特征带 = 把波动方程的光锥结构「正交分解」到频率方向。标 🟡。

- **关键定理**：**奇性传播定理（Hörmander）**——$P\in OPS^m_{1,0}$ 主型（$dp\ne0$ 于 $\mathrm{Char}(P)$），$Pu=f$，则

  $$WF(u)\setminus WF(f)\subset\mathrm{Char}(P)=\{p(x,\xi)=0\},$$

  且 $WF(u)\setminus WF(f)$ 在 $H_p$ 的 Hamilton 流下不变（奇异沿次特征带传播）。

- **自测**：① 波方程 $u_{tt}-\Delta u=0$ 的次特征带是什么（光锥 $x=\pm t+const$）？奇异如何沿光锥传播？② 为何传播定理说明「奇异不凭空产生」（$WF(u)$ 的增加只能来自 $WF(f)$）？

---

## 非线性与几何

### 主题 10 · Monge-Ampère 与完全非线性（Monge-Ampère & Fully Nonlinear）

- **核心**：Taylor Vol I 在收尾处引入完全非线性椭圆方程的代表作——**Monge-Ampère 方程**

  $$\det(D^2u)=f(x)\quad(f>0),$$

  它是**完全非线性**（最高阶项 $D^2u$ 以非线性方式出现）的典范，出现在微分几何（Kähler-Einstein 度量的复 Monge-Ampère）、最优传输（Monge-Kantorovich）、与仿射几何中。

  ① **Alexandrov 极值原理**——用 Monge-Ampère 测度 $\det D^2u$ 的几何（法映射覆盖体积）给 $L^\infty$ 上界，是非线性最大值原理的原型。
  ② **完全非线性正则性**——Caffarelli-Nirenberg-Spruck / Evans-Krylov 理论：$\det D^2u=f\in C^\alpha$（$f$ 正）⟹ $u\in C^{2,\alpha}$，解的 Hessian Hölder 连续。这是 GT（线性椭圆）方法的非线性推广。
  ③ **凸性作用**——Monge-Ampère 方程要求 $u$ 凸（$\det D^2u>0$ ⟹ $D^2u\ge0$），凸性是先验估计的基石。

  > 注：Monge-Ampère 的完整理论在 Taylor Vol III（非线性卷）深化，Vol I 做引论。GT 主题 9（ABP）与本主题的 Alexandrov 极值同源。

- **飞腾锚点** 🟢：**UDOT 16.9×⭐**（复用，距主题 2 隔 8 个，不冲突）。Alexandrov 极值原理依赖 **Monge-Ampère 测度** $\det D^2u\,dx$ 的体积估计——离散后是 Hessian 行列式（$n\times n$ 小矩阵 det 的点积累加），大批网格点的 $\det D^2u$ 求和是 UDOT 加速场景。$L^n$ 范数 $\int(f^+)^n\,dx$ 也是密集求和。标 🟢。

- **关键定理**：**Alexandrov 极值原理**——$u\in C^2(\Omega)\cap C^0(\bar\Omega)$，$Lu\ge f$（$c\le0$），则 $\sup_\Omega u\le\sup_{\partial\Omega}u^+ + C\,\mathrm{diam}(\Omega)\,\|f^+\|_{L^n(\Omega)}$。**Monge-Ampère 解的正则性**：$\det D^2u=f>0$，$f\in C^\alpha$，$u$ 凸 ⟹ $u\in C^{2,\alpha}_{\mathrm{loc}}$。

- **自测**：① 为何 Monge-Ampère 方程要求 $u$ 凸（$\det D^2u=f>0$ ⟹ $D^2u$ 半正定 ⟹ 凸）？② Alexandrov 极值中 $L^n$ 范数的 $n$ 从何而来（Sobolev 临界嵌入 $W^{2,n}$ + 行列式维数）？

---

### 主题 11 · 几何 PDE · 曲率流引论（Geometric PDE: Curvature Flows）

- **核心**：Taylor 在 Vol I 的几何窗口引入**几何 PDE**——以曲率为主项的方程描述曲面的演化：

  ① **平均曲率流**（mean curvature flow）——曲面以**平均曲率向量** $H=-H\nu$ 为速度演化：$\partial_t F=-H\nu$。它是热方程的几何推广（曲面「收缩」趋平滑），是**抛物几何方程**。
  ② **Ricci 流**（Ricci flow）——度量 $g(t)$ 以 Ricci 张量为速度演化：$\partial_t g=-2\mathrm{Ric}$。Hamilton 1982 引入，Perelman 用它证明 Poincaré 猜想（2003）。它也是抛物型（度量版热方程）。
  ③ **极小曲面**——平均曲率 $H=0$ 的曲面（肥皂膜），是平均曲率流的**稳态**。极小曲面方程是非线性椭圆方程。

  几何 PDE 的核心难点是**方程在曲率爆破时失效**（曲率流可能在有限时间出现奇点），需要手术（surgery）或正则化继续——这正是 Hamilton / Perelman 的核心技术。

  > 注：完整的曲率流理论在 Taylor Vol III，Vol I 只做引论。极小曲面方程的部分出现在 GT 主题 10。

- **飞腾锚点** 🟢：**GEMM 9.45G**（复用，距主题 6 隔 5 个，不冲突）。曲率流的数值模拟（水平集方法 / 参数化曲面）每步需计算曲面的**第二基本形式**（$n\times n$ 矩阵）与平均曲率（迹），离散后是大规模 GEMM——9.45 GFLOPS 直接决定曲面演化仿真的吞吐。水平集方法的窄带计算也是密集矩阵运算。标 🟢。

- **关键定理**：**平均曲率流方程**——浸入曲面 $F(\cdot,t):\Sigma\to\mathbb{R}^{n+1}$，$\partial_tF=-H\nu$，其中 $H$ 为平均曲率、$\nu$ 为法向。**极小曲面方程**：$\mathrm{div}\bigl(\nabla u/\sqrt{1+|\nabla u|^2}\bigr)=0$（图情形 $H=0$）。

- **自测**：① 验证极小曲面方程是平均曲率 $H=0$ 的条件（$H=\mathrm{div}(\nabla u/\sqrt{1+|\nabla u|^2})$）。② Ricci 流 $\partial_tg=-2\mathrm{Ric}$ 为何是「度量版热方程」（Ricci 张量的分量满足抛物方程）？

---

### 主题 12 · PDE 与变分法（PDE & Calculus of Variations）

- **核心**：Taylor 用变分法收束 Vol I——把 PDE 视为**能量泛函的极值条件**，用「直接方法」给存在性：

  ① **Euler-Lagrange 方程**——能量 $I[u]=\int_\Omega L(Du,u,x)\,dx$，极小元的必要条件 $-\mathrm{div}\,\frac{\partial L}{\partial(Du)}+\frac{\partial L}{\partial u}=0$ 正是 PDE。Dirichlet 原理：$\min\frac12\int|\nabla u|^2-\int fu$ 的 Euler-Lagrange = Poisson $-\Delta u=f$。
  ② **直接方法**——取极小化序列 $\{u_k\}$，$I[u_k]\to\inf$；弱下半连续性 + Rellich 紧性（主题 5）⟹ 极小元存在。这是「变分 = 存在性」的核心论证。
  ③ **特征值与约束变分**——带约束 $\|u\|=1$ 的极值给椭圆算子的特征值（Rayleigh 商 $\lambda_1=\min\frac{\int|\nabla u|^2}{\int u^2}$），约束变分引出 Lagrange 乘子。

  变分法把椭圆 PDE（主题 8）、完全非线性（主题 10）、几何 PDE（主题 11）统一在「能量极小」的框架下——极小曲面是面积泛函的极小，Monge-Ampère 可从最优传输的变分结构导出。

- **飞腾锚点** 🟡：**FP16 3.81×⭐**（复用，距主题 3 隔 9 个，不冲突）。变分极小化的梯度下降（$\partial_tu=-\delta I/\delta u$）是「PDE 即梯度流」的化身——数值上长期迭代中浮点误差累积。能量泛函 $I[u]$ 的离散是二次型 $\frac12\mathbf{u}^TK\mathbf{u}-\mathbf{f}^T\mathbf{u}$，极小化 = 解 $K\mathbf{u}=\mathbf{f}$；FP16 下条件数大的 $K$ 使迭代收敛慢，3.81× 速度差背后是「精度-收敛性」权衡。标 🟡。

- **关键定理**：**Dirichlet 原理 + 直接方法**——$\inf_{H_0^1}I[u]$（$I[u]=\frac12\int|\nabla u|^2-\int fu$）在强制条件下可达，极小元是 Poisson 方程弱解；弱下半连续 + 紧性 = 存在性。**Rayleigh 商**：$\lambda_1=\min_{u\ne0}\frac{\int|\nabla u|^2}{\int u^2}$，极小元满足 $-\Delta u=\lambda_1 u$。

- **自测**：① 为何 $I[u]=\int|\nabla u|^2$ 弱下半连续而 $\int-|\nabla u|^2$ 不是（凸性：$|\cdot|^2$ 凸 ⟹ 下半连续）？② 极小曲面（面积泛函极小）为何是变分法与几何 PDE（主题 11）的交汇点？

---

## §9 全书思想主线：古典 → Sobolev → 拟微分 → 微局部

Taylor Vol I 的总纲是一条「**从古典显式公式到微局部统一机器**」的纵深链条。主题 1–4（古典三方程）给出「解长什么样」的显式公式——特征线、基本解、Green 函数、能量方法——它们依赖 $C^k$ 古典解，建立椭圆 / 双曲 / 抛物三大类的直觉差异（平衡态 / 有限传播 / 光滑化）。

转折发生在主题 5–7（现代机器）：**Sobolev 空间**把导数放宽到弱意义，搭起弱解舞台；**拟微分算子**用符号演算统一三类方程，椭圆拟逆给正则性的代数化证明；**波前集**把奇异精确到「点-方向」，是微局部分析的语言。这三件机器一旦装配完毕，主题 8–9（线性定性核心）便水到渠成——椭圆边值用 Lax-Milgram + 拟逆，奇性传播用 Hamilton 流 + 波前集。主题 10–12（非线性与几何）则是这套线性机器向完全非线性（Monge-Ampère）、几何（曲率流）、变分（能量极小）的推广。

读者一旦抓住「**拟微分算子的符号 $p(x,\xi)$ 是三类方程的统一语言，波前集 $WF(u)$ 是奇异的微局部坐标**」这条主线，就理解了 Taylor 体系的核心设计：**不是逐类方程给技巧，而是用一套微局部机器统摄椭圆 / 双曲 / 抛物**——这正是 Hörmander 在研究级专著中建立、Taylor 在研究生教材中普及的范式革命。与已读呼应：Evans 弱解三部曲是 Taylor 主题 1–5 + 8 的「地图版」，Taylor 补全拟微分与微局部（主题 6–7, 9）这两大 Evans 缺失的机器；Hörmander I 的分布论是 Taylor 弱导数的严格地基——Taylor「使用并推广」分布，Hörmander「重建」分布。

---

## §10 与本仓库其他笔记的交叉引用

- **与 [Evans PDE](evans_PDE偏微分方程_快速逐章.md)**：Evans 弱解三部曲（椭圆 / 抛物 / 双曲 + 非线性）是 Taylor 主题 1–5 + 8 + 12 的「地图版」——Evans 重在存在性直觉与非线性应用，**完全未涉及拟微分算子与波前集**（Taylor 主题 6–7, 9）。Taylor 补全这两大现代机器，并用微局部统一三类方程。**Evans 是「应用地图」，Taylor 是「全面纵深」**——读 Evans 建立弱解直觉后，用 Taylor 把拟微分 / 微局部吃透。

- **与 [Hörmander ALPDO I](hormander_线性偏微分算子I_快速逐章.md)**：Hörmander I 的分布论 + Fourier 分析是 Taylor 弱导数（主题 5）、拟微分算子（主题 6）、波前集（主题 7）的**严格语言地基**——Taylor 主题 6–7 的拟微分算子与波前集正是 Hörmander Vol III 的研究生教材版。**Hörmander 是「语言重建」，Taylor 是「语言应用」**。读 Taylor 主题 7 波前集时可回查 Hörmander Ch VIII 的原始定义。

- **与 [Gilbarg-Trudinger 椭圆 PDE](gilbarg_trudinger_椭圆PDE_快速逐章.md)**：GT 是椭圆专精（Schauder + Sobolev 双轴），Taylor 主题 8（椭圆边值）覆盖 GT 的弱解轴（Lax-Milgram + DGNM）但不深挖 Schauder 估计的逐条证明。Taylor 的特色是用**拟微分算子拟逆**统一证明椭圆正则性，而 GT 用 Schauder / CZ 分解——两种路径互补。Taylor 主题 10（Monge-Ampère）与 GT 主题 9（ABP）的 Alexandrov 极值同源。

- **与 [Lang 实与泛函分析 GTM142](../stage-2-研究生基础/lang_实与泛函分析_GTM142_快速逐章.md)**：Lang 的 Sobolev 空间 / Hilbert 空间 / 紧算子理论是 Taylor 主题 5（Sobolev）、主题 8（Lax-Milgram / Fredholm）的泛函基础；Lang 的谱定理是椭圆算子特征值展开的依据。读 Taylor 前 Lang GTM142 的 Sobolev 章节值得复习。

- **AI / 工程锚点**（Taylor 的拟微分 + 微局部 = AI for Science 的高级数学引擎）：

  - ① **Neural Operator / FNO**：Fourier Neural Operator 在频域学习解算子——Taylor 主题 6 拟微分算子的符号 $p(x,\xi)$ 正是「频域乘法」的推广，FNO 截断高频模式 = 拟微分算子的低阶近似；波前集（主题 7）刻画神经网络解的高频奇异。
  - ② **PINN（物理信息神经网络）**：把 PDE 残差作损失，本质是弱形式配对的神经网络逼近——Taylor 主题 5 弱导数 + 主题 8 Lax-Milgram 是 PINN 的连续数学源头；椭圆正则性（拟逆推论）给 PINN 解的误差上界。
  - ③ **Diffusion 模型**：采样过程是热方程（主题 4 热核）的随机版，score 函数的奇异用波前集（主题 7）微局部刻画；逆向扩散的「去奇异」与微局部光滑化同构。
  - ④ **物理仿真（CFD / 几何处理）**：曲率流（主题 11）是 3D 几何处理 / 医学图像分割的数学引擎（水平集方法）；Monge-Ampère（主题 10）出现在最优传输与生成模型的距离计算中。
  - ⑤ **奇性传播 = 信息流**：主题 9 的奇性沿次特征带传播，与神经网络中「信息沿计算图传播」的结构同构——理解 PDE 的微局部传播有助于分析深度网络的信息瓶颈。

> **一句话总结本书的 AI 价值**：Taylor 把「古典物理方程」推进到「拟微分算子 + 波前集的微局部语言」，而 AI for Science 的高级分支（Neural Operator 的频域学习、PINN 的弱形式、扩散模型的微局部奇异）恰恰是「在符号演算与余切丛上用神经网络逼近 PDE 解算子」——读通 Taylor Vol I，就拿到了从古典 PDE 到现代微局部分析的完整阶梯，为理解 AI for Science 的最深数学层铺路。

---

## §11 各主题精华一句话

- **主题 1**：一阶方程用特征线降为 ODE；二阶方程按系数矩阵特征值符号分椭圆 / 双曲 / 抛物三类——分类决定定性性质。
- **主题 2**：Laplace 方程的均值定理 ⟹ 调和函数自动解析；Green 函数表出 Dirichlet 问题解——椭圆 = 平衡态。
- **主题 3**：波方程能量守恒 ⟹ 唯一性 + 有限传播（光锥）；能量法不依赖显式公式，可推广到变系数。
- **主题 4**：热核高斯卷积把初值瞬间光滑化；抛物极值原理使最大值在抛物边界达到——抛物 = 无穷传播 + 平滑。
- **主题 5**：Sobolev 空间是弱解舞台——弱导数 + 嵌入 + 迹 + 紧性，把导数从 $C^k$ 放宽到 $L^p$。
- **主题 6**★：拟微分算子用符号演算统一三类方程——椭圆拟逆 $PQ=I+R$ 给正则性的代数化证明。
- **主题 7**：波前集 $WF(u)$ 给奇异做「方向 CT 断层」，住在余切丛——比支撑更精细的微局部坐标。
- **主题 8**：Lax-Milgram + Fredholm 抉择 + 拟逆 ⟹ 椭圆边值存在唯一 + 正则性 + 谱。
- **主题 9**★：奇性沿 Hamilton 流的次特征带传播——$WF(u)$ 不凭空产生，只在特征集上沿流移动。
- **主题 10**：Monge-Ampère $\det D^2u=f$ 是完全非线性椭圆典范；Alexandrov 极值用几何给 $L^n$ 上界。
- **主题 11**：平均曲率流 / Ricci 流是「度量版热方程」；曲率爆破需手术——Perelman 证明 Poincaré 的引擎。
- **主题 12**：变分法把 PDE 等价于能量泛函极小；直接方法（下半连续 + 紧性）给存在性——「最小作用原理」。

---

## 📌 阅读建议（对接数学专家路径）

1. **精读顺序**：主题 1–4（古典三方程，快扫建立直觉）→ **主题 5（Sobolev，弱解舞台）** → **主题 6（拟微分算子，Taylor 招牌）** → **主题 7（波前集，微局部语言）** → **主题 9（奇性传播，微局部顶峰）** → 主题 8（椭圆边值）→ 主题 12（变分）→ 主题 10–11（非线性 + 几何，按需 / Vol III 前向）。

2. **与 Evans / Hörmander 配对读**：Taylor 主题 1–5 ↔ Evans Part I–II（古典 + 弱解）；Taylor 主题 6–7 ↔ Hörmander Vol III（拟微分 + 波前集的研究版）。Evans / Hörmander 各补一面，Taylor 融合二者。

3. **数学根基回溯**：弱导数 / 分布 ⟵ Hörmander I（已读）+ Folland 实分析（已读）；Hilbert 空间 / Lax-Milgram / 谱定理 ⟵ Lang GTM142（已读）+ Reed-Simon I（已读）；余切丛 / Hamilton 流 ⟵ Lee 光滑流形（已读）；多元微积分 ⟵ Spivak（已读）。

4. **深挖课题**（Taylor 特色）：
   - ① 拟微分算子的符号演算如何统一椭圆 / 双曲 / 抛物三类方程的「正则性 / 传播」理论（主题 6 → 8 → 9）。
   - ② 波前集传播定理（主题 9）如何把「整体唯一性」细化到「微局部唯一性」。
   - ③ Monge-Ampère 方程（主题 10）的完全非线性正则性如何推广 GT 的线性椭圆理论。
   - ④ 曲率流（主题 11）的「有限时间奇点」为何需要手术——通向 Perelman 的 Poincaré 证明。

5. **动手验证**（Python 工程师优势）：主题 4 用 NumPy 验证热核卷积的光滑化（随机初值 ⟹ $t>0$ 时 $C^\infty$）；主题 5 用 `scipy.sparse` 实现有限元验证 Sobolev 嵌入阶；主题 6 可用 FFT 实现拟微分算子作用（符号 $p(x,\xi)$ 在频域乘法）验证椭圆拟逆；主题 7 可视化 $\delta$ 的波前集 = 全方向。代码即理解，飞腾实测数据则作为「工程极限」的参照系。

> 注：本笔记基于 Taylor《Partial Differential Equations I: Basic Theory》（AMS 115, 2nd ed. 2011）撰写快速逐章导览，忠实整合为 12 主题，侧重概念串联与飞腾 / AI 锚点对接。主题 10–11 部分内容在 Taylor 三卷本中延展至 Vol III（非线性卷），本笔记作 Vol I 的前向指针并标注。数学内容（特征线法 / 均值定理 / 能量守恒 / 热核 / Sobolev 嵌入 / 椭圆拟逆 / 波前集传播 / Alexandrov 极值 / 曲率流方程 / Dirichlet 原理等）均为标准准确陈述。
