# Lawrence C. Evans, Ronald F. Gariepy《测度论与函数的细性质》 · 快速逐章精读

> 基于原书：`Measure Theory and Fine Properties of Functions`, Lawrence C. Evans & Ronald F. Gariepy, CRC Press, 1992（revised printing 2015）/ 全 6 章
> 读于：2026-07-03 / stage-2 研究生基础 · 几何测度论 + 函数空间主线
> 定位：**几何测度论（GMT）的「工程友好」入口**——以「函数有多光滑」为核心问题，把 Radon 测度、Hausdorff 维数、面积/共面积公式、Sobolev/BV 函数、Lipschitz 可微性织成一张「细性质」之网。
> 本文为**快速逐章精读**（忠于原书 6 章真实结构），每章 1 个飞腾锚点 🟢/🟡 + 1 个关键定理 + 1 道自测题。

---

## §0 引言：Evans-Gariepy 是什么，为什么读它

Evans（UC Berkeley，PDE 大师）与 Gariepy 的这本书，标题里那个「**Fine Properties of Functions**」是全书灵魂。多数测度论教材（Folland/Royden/Halmos）把测度当作目的本身——建立抽象理论后便收手；Evans-Gariepy 则把测度论当作**工具**，服务于一个更具体的问题：**「粗糙的函数（Sobolev、BV、Lipschitz）到底有多光滑？在哪些点上可微？边界有多规则？」** 这正是「细性质」(fine properties) 的含义。

全书的叙事极具 Evans 个人风格——**定理导向、可手算、工程落地**。它的核心工具链是五件套：

- ① **覆盖定理**（Vitali、Besicovitch）——把「用小球盖住集合」变成精确的测度估计；
- ② **Hausdorff 测度与维数**——给分形与非整数维集合「称重」；
- ③ **面积公式与共面积公式**——Lipschitz 映射下如何换元、如何切片算体积；
- ④ **Sobolev 与 BV 函数**——弱导数与有界变差的函数空间，是 PDE 与变分法的语言；
- ⑤ **Rademacher 与 Federer 定理**——Lipschitz 函数 a.e. 可微、集合有限周界的刻画。

这五件工具环环相扣，最终服务于 PDE 正则性理论与变分法中的极小曲面问题。

与 Mattila《Geometry of Sets and Measures》（纯几何测度论，偏研究级）相比，Evans-Gariepy 更亲民、覆盖面更广（含 Sobolev/BV，Mattila 几乎不碰函数空间）；与 Folland/Royden（经典实分析，停在 $L^p$）相比，本书从「测度」直接冲向「函数的几何细性质」，是连接抽象测度论与 PDE/变分法的关键桥梁。它是 Evans《Partial Differential Equations》（GTM19，已做）的直接理论后盾——PDE 书里那些 Sobolev 嵌入、迹定理、BV 结构定理的证明细节，都藏在这本书里。

**建议读法**：先通 Folland/Royden 的 Ch 1-4（测度+积分+$L^p$）建立抽象基础 → 精读 Evans-Gariepy Ch 1（Radon 测度+覆盖定理）→ Ch 2-3（Hausdorff+面积公式）→ Ch 4-6（Sobolev/BV/可微性，全书 payoff）。

**前置与衔接**：读本书需要 Folland/Royden 的抽象测度论基础（σ-代数、Carathéodory、Lebesgue 积分、$L^p$）+ 多元微积分（Jacobian、换元）+ 基础泛函（弱导数的分布语言）。本书本身是 Evans《PDE》(GTM19)、极小曲面理论、$\Gamma$-收敛、图像处理（全变差去噪）的直接前置。与 Federer《Geometric Measure Theory》（GMT 圣经，符号极重）相比，Evans-Gariepy 是其「可读版」——同样的核心定理（面积公式、BV 结构、Rademacher），但证明可手算、符号可忍受。

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|:-:|---|
| **Evans-Gariepy**《测度论与细性质》 | 测度=工具，服务「函数有多光滑」，可手算，PDE/变分导向 | ★★★★ | 想把测度论接到 PDE/几何/变分法的应用型研究生 ⭐ |
| **Folland**《Real Analysis》 | 现代技巧+全景最广，抽象测度→泛函→Fourier→拓扑群 | ★★★★★ | 想要「现代分析百科全书」的研究生（已做） |
| **Royden**《实分析》 | 分析视角，先 $\mathbb{R}$ 上 Lebesgue 再抽象，渐进教学 | ★★★★ | 分析/泛函方向，偏好 concrete→abstract（已做） |
| **Mattila**《Geometry of Sets and Measures》 | 纯几何测度论研究级，密度/投影/正则性，密度高 | ★★★★★ | GMT 研究者，Federer《GMT》的友好替代 |

> 🟢 事实可作锚点：Radon-Nikodym、Hausdorff 维数、Besicovitch 覆盖、面积公式、Sobolev 嵌入、Gauss-Green、Rademacher、Federer 定理均为严格定理。
> 🟡 类比（「维数=分辨率」「覆盖=地址翻译」「可微=局部线性化」）仅供直觉，**绝不在严格证明中引用**。

---

## §1 全书 6 章骨架一览（飞腾锚点分布）

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | General Measure Theory（一般测度论） | Radon 测度、Carathéodory、覆盖定理（Vitali/Besicovitch）、微分、Radon-Nikodym | **TLB 4.81×[E04]** |
| 2 | Hausdorff Measure（Hausdorff 测度） | Hausdorff 测度 $\mathcal{H}^s$、Hausdorff 维数、密度定理、可求长集 | **FP16 3.81×[L01]** |
| 3 | Area and Coarea Formulas（面积与共面积公式） | Lipschitz 映射、Jacobian、面积公式、共面积公式、换元 | **matmul 15×[V03]** |
| 4 | Sobolev Functions（Sobolev 函数） | 弱导数、$W^{k,p}$、磨光逼近、Sobolev 嵌入、迹、Poincaré | **UDOT 16.9×[E05]** |
| 5 | BV Functions and Sets of Finite Perimeter（BV 与有限周界集） | 有界变差、有限周界、约化边界、Gauss-Green、等周不等式 | **Iron Law<2%[Lab00]** |
| 6 | Differentiability and Approximation（可微性与逼近） | Rademacher 定理、Whitney 延拓、逼近可微、Federer 刻画 | **分支预测[Lab02]** |

**三条主线**：

1. **覆盖与微分主线**——覆盖定理(Ch 1) → Radon 测度微分(Ch 1) → Lipschitz 可微(Ch 6)，用「小球覆盖」驱动「逐点微分」；
2. **几何测度主线**——Hausdorff 测度(Ch 2) → 面积/共面积公式(Ch 3)，给「不规则集合与映射」称重换元；
3. **函数空间主线（全书 payoff）**——Sobolev(Ch 4) → BV/有限周界(Ch 5) → 可微性刻画(Ch 6)，回答「粗糙函数有多光滑」。

---

### 第 1 章 · General Measure Theory（一般测度论）

- **核心**：全书地基。从 Carathéodory 外测度构造出发，聚焦 $\mathbb{R}^n$ 上的 **Radon 测度**（Borel 正则 + 紧集有限测度），这是几何测度论的标准工作对象。两大**覆盖定理**是本章引擎：

  - **Vitali 覆盖定理**——不相交小球族逼近，$1/2^k$ 缩放，要求球的缩放比可控；
  - **Besicovitch 覆盖定理**——更强大：$\mathbb{R}^n$ 中任意有界球族可拆成至多 $N(n)$ 个不相交子族覆盖中心点集，**不依赖球的缩放比**。

  覆盖定理直接推出 **Radon 测度的微分理论**：极限 $\lim_{r\to0}\frac{\mu(B(x,r))}{\nu(B(x,r))}$ a.e. 存在且等于 Radon-Nikodym 导数 $d\mu/d\nu$。**Lebesgue 微分定理**（$\frac1{|B_r|}\int_{B(x,r)}f\to f(x)$ a.e.）是其直接推论。本章还建立 Lebesgue 分解（$\mu=\mu_{ac}+\mu_s$）与 Hahn/Jordan 分解。

- **飞腾锚点**：**TLB 4.81×[E04]** —— Borel σ-代数由开集逐层生成（开集 $\to$ Borel $\to$ Radon 正则化），Radon 测度用紧集从内、开集从外逼近，如同 **TLB 多级页表分层寻址**：越底层覆盖越大。
  - 🟢事实：Borel σ-代数层级生成与 Radon 正则性（$\mu(E)=\sup_{K\subset E}\mu(K)=\inf_{U\supset E}\mu(U)$）是测度论标准结论；Besicovitch 覆盖把任意有界球族拆成 $\leq N(n)$ 族不相交集，$N(n)$ 只依赖维数。
  - 🟡类比：覆盖定理用小球「寻址」每个点，如同 TLB 缓存合法地址翻译；微分定理是「逐点查询测度密度」。

- **关键定理**：**Besicovitch 覆盖定理 + Radon-Nikodym 定理** ——
  $$\mathbb{R}^n\text{ 中有界球族 }\mathcal{F}\ \Rightarrow\ \exists\ \text{至多 }N(n)\text{ 个不相交子族 }\mathcal{F}_1,\dots,\mathcal{F}_{N(n)}\ \text{覆盖中心点集};$$
  $$\nu\ll\mu\ (\sigma\text{-有限})\ \Leftrightarrow\ \exists!\ f=\frac{d\nu}{d\mu}\in L^1(\mu),\quad \nu(E)=\int_E f\,d\mu.$$
  - Besicovitch 覆盖是几何测度论的「瑞士军刀」，比 Vitali 更强（不要求球缩放到固定比例）；Radon-Nikodym 把「绝对连续测度」变成「带密度的积分」。

- **自测**：用 Besicovitch 覆盖推出 Lebesgue 微分定理（$\frac1{|B_r|}\int_{B(x,r)}f\to f$ a.e.）；区分 $\nu\ll\mu$（绝对连续）与 $\nu\perp\mu$（互相奇异），给 Lebesgue 分解 $\mu=\mu_{ac}+\mu_s$ 的具体例子。

- **历史/动机**：Besicovitch（1919）在研究长度问题时发明这套覆盖技术，远早于它在测度微分中的应用。Radon-Nikodym（1913）的「测度求导」思想，在 $\mathbb{R}^n$ 上由覆盖定理赋予精确的「逐点微分」含义——这是从抽象到具体的关键一步。

---

### 第 2 章 · Hausdorff Measure（Hausdorff 测度）

- **核心**：本章给「不规则集合」(分形、低维曲面)精确称重。**Hausdorff 测度**定义为
  $$\mathcal{H}^s(E)=\lim_{\delta\to0}\inf\left\{\sum_i(\mathrm{diam}\,U_i)^s:\ E\subset\bigcup_i U_i,\ \mathrm{diam}\,U_i\leq\delta\right\},$$
  用直径 $\leq\delta$ 的覆盖取下确界——它是 Lebesgue 测度的推广：$\mathcal{H}^n=$ Lebesgue 测度（至多差常数 $\omega_n/2^n$）。

  关键现象是**相变**：对固定 $E$，$s<\dim_H E$ 时 $\mathcal{H}^s(E)=\infty$，$s>\dim_H E$ 时 $\mathcal{H}^s(E)=0$，临界值即 **Hausdorff 维数** $\dim_H E=\inf\{s:\mathcal{H}^s(E)=0\}$。Cantor 集维数 $\log2/\log3\approx0.63$，Koch 雪花 $\approx1.26$。

  **密度定理**：$\Theta^s(E,x)=\lim_{r\to0}\frac{\mathcal{H}^s(E\cap B(x,r))}{(2r)^s}$ 在 $\mathcal{H}^s$-a.e. $x\in E$ 上存在。**可求长集**（rectifiable）：$\mathcal{H}^1$-有限且可被 Lipschitz 像覆盖，是几何测度论的核心对象。

- **飞腾锚点**：**FP16 3.81×[L01]** —— Hausdorff 维数 $s$ 是度量集合所需的「分辨率档」：$s$ 越高需要的覆盖越细，如同 **FP16/32/64** 是数值精度的三档——低维分形用 $\mathcal{H}^s$（$s<1$）才「称得出重量」。
  - 🟢事实：Hausdorff 测度的相变现象（$s$ 跨过 $\dim_H$ 时测度从 $\infty$ 跳到 $0$）是严格定理；Cantor 三分集维数 $=\log2/\log3$ 可手算验证。
  - 🟡类比：Hausdorff 维数=「集合的内在分辨率需求」，整数维用 Lebesgue 测度（FP64 高精度），分数维需专用测度（切换精度档）。

- **关键定理**：**Hausdorff 维数与密度定理** ——
  $$\dim_H E=\inf\{s:\mathcal{H}^s(E)=0\}=\sup\{s:\mathcal{H}^s(E)=\infty\};\qquad \Theta^{*s}(E,x)=\limsup_{r\to0}\frac{\mathcal{H}^s(E\cap B(x,r))}{\omega_s r^s}.$$
  - 维数是集合的「指纹」；密度 $\Theta^s$ 在可求长集上 a.e. $=1$，在纯不可求长集上 a.e. $<1$，是可求长性的判据。

- **自测**：手算 Cantor 三分集的 Hausdorff 维数 $=\log2/\log3$（每步删 $1/3$ 留 $2$ 段，$2(1/3)^s=1$）；说明 Koch 曲线维数 $=\log4/\log3\approx1.26$。

- **历史/动机**：Hausdorff（1918）为度量「非整数维集合」发明这套测度，Carathéodory 随即推广。Besicovitch 是分形几何的先驱，他证明 Cantor 集的维数 $\log2/\log3$——这是「集合可以不是整数维」的第一个严格例子，颠覆了「维数=自由度」的直觉。

---

### 第 3 章 · Area and Coarea Formulas（面积与共面积公式）

- **核心**：本章处理「Lipschitz 映射下如何换元、如何切片」。

  **面积公式**（Area Formula）：$f:\mathbb{R}^n\to\mathbb{R}^m$（$n\leq m$）Lipschitz 时，Jacobian $Jf=\sqrt{\det(Df^TDf)}$ a.e. 有定义（Rademacher，Ch 6），且
  $$\int_{\mathbb{R}^n}g(f(x))\,Jf(x)\,dx=\int_{\mathbb{R}^m}g(y)\,\mathcal{H}^{n-m}\text{-计数的 }f^{-1}(y)\,d\mathcal{H}^m(y),$$
  即 $\int g\,Jf\,dx=\sum_{y}g(y)\#f^{-1}(y)$——Jacobian 加权后等于按像点计数。这是多元换元公式的 Lipschitz 版（不要求 $C^1$，只需 Lipschitz + Rademacher）。

  **共面积公式**（Coarea Formula）：$f:\mathbb{R}^n\to\mathbb{R}^m$（$n\geq m$）Lipschitz 时，
  $$\int_{\mathbb{R}^n}g(x)\,Jf(x)\,dx=\int_{\mathbb{R}^m}\left(\int_{f^{-1}(y)}g\,d\mathcal{H}^{n-m}\right)dy,$$
  即「体积分 = 对每个切片的面积分再对水平集参数积分」。共面积公式是 Fubini 的几何推广（水平集切片），是变分法、极小曲面、$\Gamma$-收敛的核心工具。

- **飞腾锚点**：**matmul 15×[V03]** —— Jacobian $Jf=\sqrt{\det(Df^TDf)}$ 是微分 $Df$（$m\times n$ 矩阵）的奇异值之积，面积/共面积公式本质是**线性变换的体积放大率**的积分版——$Df$ 把单位立方体拉伸成超椭球，体积比为 $|\det|$（满秩时）。
  - 🟢事实：面积公式 $\int g\,Jf=\int g\,\#f^{-1}$ 是多元换元的严格推广，Lipschitz + Rademacher（a.e. 可微）保证 $Jf$ a.e. 有定义；$Df^TDf$ 的特征值是奇异值平方，$Jf$ 是其乘积。
  - 🟡类比：面积公式 = matmul 的非线性版（$y=f(x)$ 局部用 $Df$ 线性化，体积放大 $=|\det Df|$）；共面积公式 = 「按行求和」的几何版。

- **关键定理**：**面积公式与共面积公式** ——
  $$\text{Area}(n\leq m):\ \int_A g(f(x))\,J_n f\,dx=\int_{\mathbb{R}^m}g(y)\,\mathcal{H}^0(A\cap f^{-1}(y))\,d\mathcal{H}^m(y);$$
  $$\text{Coarea}(n\geq m):\ \int_A g\,J_m f\,dx=\int_{\mathbb{R}^m}\int_{A\cap f^{-1}(y)}g\,d\mathcal{H}^{n-m}\,dy.$$
  - 面积公式用于「参数化曲面求面积」(Lipschitz 图)，共面积公式用于「按水平集分解体积分」(变分法、等周不等式证明)。

- **自测**：用面积公式验证 $f:\mathbb{R}^2\to\mathbb{R}^2$，$f(x)=Ax$（$A$ 可逆）时 $\int g(Ax)|\det A|\,dx=\int g(y)\,dy$（经典换元）；用共面积公式说明 $f(x)=|x|$ 时 $\int_{\mathbb{R}^n}g\,dx=\int_0^\infty\int_{\partial B_r}g\,d\mathcal{H}^{n-1}\,dr$（球坐标分解）。

---

### 第 4 章 · Sobolev Functions（Sobolev 函数）

- **核心**：本章是 PDE 与变分法的语言基础。

  **弱导数**：$Du=g$ 若 $\int u\,\partial_i\varphi=-\int g\varphi$（$\forall\varphi\in C_c^\infty$，分部积分无边界项）。**Sobolev 空间** $W^{k,p}(\Omega)=\{u:\|D^\alpha u\|_{L^p}<\infty,\ |\alpha|\leq k\}$。**磨光逼近**（mollifier $\eta_\varepsilon*u$）证明 $C^\infty$ 在 $W^{k,p}$（$p<\infty$）中稠密——弱导数是「光滑化极限」。

  核心是 **Sobolev 嵌入定理**：$u\in W^{1,p}$（$1\leq p<n$）$\Rightarrow u\in L^{p^*}$，$p^*=\frac{np}{n-p}$（临界指标），$\|u\|_{L^{p^*}}\leq C\|\nabla u\|_{L^p}$；$p>n$ 时 $u$ Hölder 连续（Morrey 不等式）；$p=n$ 时 $u\in\mathrm{BMO}$（John-Nirenberg）。

  **Poincaré 不等式**（$\|u-u_\Omega\|_{L^p}\leq C\,\mathrm{diam}(\Omega)\|\nabla u\|_{L^p}$）控制函数振荡。**迹定理**：$u\in W^{1,p}$ 在边界 $\partial\Omega$ 上有良定义的迹 $Tu\in L^p(\partial\Omega)$。

- **飞腾锚点**：**UDOT 16.9×[E05]** —— 弱导数定义 $\int u\,\partial_i\varphi=-\int g\varphi$ 是对偶配对（积分=加权求和极限），本质是 **UDOT 点积累加**的连续版；Sobolev 嵌入 $\|\nabla u\|_{L^p}\to\|u\|_{L^{p^*}}$ 是积分不等式的缩并估计。
  - 🟢事实：弱导数通过分部积分定义（对偶配对 $\int u\partial_i\varphi$），$W^{1,p}\hookrightarrow L^{p^*}$ 嵌入是严格不等式；磨光逼近 $\eta_\varepsilon*u\to u$ 在 $W^{k,p}$ 中收敛。
  - 🟡类比：弱导数=「平均化的导数」（磨光后再求导），UDOT 累加是其离散实现；Sobolev 嵌入=「梯度可控则函数本身可控」的能量估计。

- **关键定理**：**Sobolev 嵌入定理 + Poincaré 不等式** ——
  $$u\in W^{1,p}(\mathbb{R}^n),\ 1\leq p<n\ \Rightarrow\ u\in L^{p^*},\ p^*=\frac{np}{n-p},\ \|u\|_{L^{p^*}}\leq C\|\nabla u\|_{L^p};$$
  $$u\in W^{1,p}(\Omega),\ \Omega\ \text{有界 Lipschitz}\ \Rightarrow\ \|u-u_\Omega\|_{L^p}\leq C\,\mathrm{diam}(\Omega)\|\nabla u\|_{L^p}\ (\text{Poincaré}).$$
  - Sobolev 嵌入是 PDE 正则性理论的基石（$p^*$ 临界指标决定解的「光滑升级」），Poincaré 不等式是变分法存在性证明的核心。

- **自测**：验证 $u(x)=|x|^{-\alpha}\in W^{1,p}(B_1)$ 当且仅当 $\alpha<\frac{n}{p}-1$（用临界指标判断奇性）；用 Poincaré 说明 $W^{1,p}_0(\Omega)$ 中 $\|u\|_{L^p}\leq C\|\nabla u\|_{L^p}$（零边界无常数项）。

---

### 第 5 章 · BV Functions and Sets of Finite Perimeter（BV 函数与有限周界集）

- **核心**：本章把 Sobolev 推到极限——$W^{1,1}$ 的「边界」是 **BV（有界变差）**空间。

  $u\in\mathrm{BV}(\Omega)$ 若分布导数 $Du$ 是**有限 Radon 测度**（不只是 $L^1$ 函数），即总变差 $|Du|(\Omega)<\infty$。BV 函数可有跳跃（阶跃函数 $u=\chi_E$ 是 BV，$Du$ 集中在边界）。集合 $E$ 有**有限周界**（finite perimeter）若 $\chi_E\in\mathrm{BV}$，其周界 $P(E)=|D\chi_E|(\Omega)$。

  **约化边界**（reduced boundary）$\partial^*E$ 是「有确切外法向量」的边界点集。**De Giorgi 结构定理**：$\partial^*E$ 可求长（$\mathcal{H}^{n-1}$-有限），且 $D\chi_E=-\nu_E\,\mathcal{H}^{n-1}\lfloor\partial^*E$（导数=法向量 × 面积测度）。

  **Gauss-Green 定理**（散度定理的 BV 版）：$\int_E\mathrm{div}\,\varphi=-\int_{\partial^*E}\varphi\cdot\nu_E\,d\mathcal{H}^{n-1}$。**等周不等式**：$P(E)\geq n\omega_n^{1/n}|E|^{(n-1)/n}$（球取等），是 BV 理论的招牌应用。

- **飞腾锚点**：**Iron Law<2%[Lab00]** —— BV 函数的导数 $Du$ 是测度（可能有原子/奇异部分），总变差 $|Du|(\Omega)<\infty$ 是**误差可控**的精确表述——「变差有界」即「振荡总量被夹住」，如同 Iron Law 性能=指令数×CPI×时钟的预算约束。
  - 🟢事实：$Du$ 是有限 Radon 测度（BV 定义），De Giorgi 结构定理 $D\chi_E=-\nu_E\mathcal{H}^{n-1}\lfloor\partial^*E$ 是严格结论；等周不等式 $P(E)\geq n\omega_n^{1/n}|E|^{(n-1)/n}$ 可证。
  - 🟡类比：BV=「总变差有预算的函数」（如同 Iron Law 的误差预算），阶跃函数的变差集中在跳跃点（原子测度）；有限周界集=「边界不太破碎的集合」。

- **关键定理**：**De Giorgi 结构定理 + Gauss-Green + 等周不等式** ——
  $$\partial^*E\ \text{可求长},\quad D\chi_E=-\nu_E\,\mathcal{H}^{n-1}\lfloor\partial^*E;\qquad \int_E\mathrm{div}\,\varphi=-\int_{\partial^*E}\varphi\cdot\nu_E\,d\mathcal{H}^{n-1};$$
  $$P(E)\geq n\omega_n^{1/n}|E|^{(n-1)/n}\quad(\text{球取等}).$$
  - De Giorgi 定理把「BV 函数的导数」几何化为「约化边界 × 法向量 × 面积测度」；等周不等式是 BV 理论与几何的交汇点。

- **自测**：说明 $\chi_{B_1(0)}\in\mathrm{BV}(\mathbb{R}^n)$ 且 $P(B_1)=\mathcal{H}^{n-1}(\partial B_1)=n\omega_n$（球取等）；构造一个集合使 $\partial E\neq\partial^*E$（提示：加一个「尖刺」测度零但拓扑边界变大的部分）。

- **历史/动机**：De Giorgi（1950s）为研究极小曲面问题发明「有限周界集」语言——他把「集合的边界」从拓扑概念升级为测度论概念（约化边界 $\partial^*E$），使散度定理（Gauss-Green）能推广到「边界不光滑」的集合。Caccioppoli 先驱性地用「周界」概念，De Giorgi 与 Federer 各自独立完善了整套 BV 理论。等周不等式是其最优美的应用。

---

### 第 6 章 · Differentiability and Approximation（可微性与逼近）

- **核心**：本章是全书的「可微性总收尾」，回答「粗糙函数到底在哪可微」。

  **Rademacher 定理**：$f:\mathbb{R}^n\to\mathbb{R}^m$ Lipschitz $\Rightarrow$ $f$ a.e. 可微（$\mathbb{R}^n$ 上 Lebesgue a.e.）。这是「Lipschitz $\Rightarrow$ 可微」的严格陈述，面积/共面积公式（Ch 3）依赖它定义 Jacobian。

  **Whitney 延拓定理**：闭集 $A$ 上的「相容 jets」（满足 Taylor 余项条件）可延拓成 $C^1$ 函数——这是「逐点信息 $\to$ 全局光滑函数」的桥梁。

  **逼近可微性**（approximate differentiability）：去掉零测集后可微，比经典可微更弱但足够做积分换元。**Federer 定理**（全书高潮之一）：集合 $E$ 有有限周界 $\Leftrightarrow$ 其特征函数的「逼近导数」行为良好，把 Ch 5 的 BV 与 Ch 6 的可微性缝合。

  本章还涉及 **Whitney 分解**（把开集分解成二进方体的标准技术）与 **Lusin 型逼近**（Lipschitz 函数可用 $C^1$ 函数逼近到任意精度，去掉小测度集）。

- **飞腾锚点**：**分支预测[Lab02]** —— Rademacher 定理说 Lipschitz 函数在「绝大多数点」（a.e.）可微——例外点是零测集的「罕见事件」，如同 **分支预测器**假设错误路径罕见（命中 0.71 vs 失误 3.14 周期）。
  - 🟢事实：Rademacher 定理（Lipschitz $\Rightarrow$ a.e. 可微）是严格结论；Whitney 延拓定理（相容 jets $\to$ $C^1$ 延拓）是严格结论。
  - 🟡类比：可微点=「局部线性化成功」的点（主路径），不可微点=「线性化失败」的罕见分支；Federer 定理=「有限周界集在逼近意义下边界规则」，是分支判定（周界有限 vs 无限）。

- **关键定理**：**Rademacher 定理 + Federer 定理** ——
  $$f:\mathbb{R}^n\to\mathbb{R}^m\ \text{Lipschitz}\ \Rightarrow\ f\ \text{在 }\mathbb{R}^n\text{ 上 Lebesgue-a.e. 可微};$$
  $$E\ \text{有限周界}\ \Leftrightarrow\ \text{特征函数 }\chi_E\ \text{逼近可微且逼近导数结构良好 (Federer)}.$$
  - Rademacher 是几何测度论的基石（保证 Lipschitz 映射的 Jacobian a.e. 有定义）；Federer 定理把 BV（Ch 5）与可微性（Ch 6）缝合，是「细性质」理论的集大成。

- **自测**：用 Rademacher 说明 $f(x)=|x|$ 在 $\mathbb{R}$ 上 a.e. 可微（除 $x=0$）；说明 Cantor 函数 Lipschitz（否——它只是连续 BV）从而 Rademacher 不直接适用，但它是「奇异函数」的典型。

---

## §8 全书脉络一览（红线串联）

> §1 骨架表按「学什么」排列，本表按「为什么」排列，集中对照核心定理与飞腾锚点。

| 章 | 性质层级 | 核心定理 | 飞腾/工程锚点 |
|:-:|---|---|---|
| 1 | 测度地基 | Besicovitch 覆盖 + Radon-Nikodym + Lebesgue 微分 | TLB 4.81× Borel 层级 |
| 2 | 集合称重 | Hausdorff 维数 + 密度定理 | FP16 3.81× 分辨率档 |
| 3 | 映射换元 | 面积公式 + 共面积公式 | matmul 15× Jacobian 缩并 |
| 4 | 函数空间 I | Sobolev 嵌入 + Poincaré + 迹 | UDOT 16.9× 弱导数对偶配对 |
| 5 | 函数空间 II | De Giorgi 结构 + Gauss-Green + 等周 | Iron Law<2% 变差预算 |
| 6 | 可微性收尾 | Rademacher + Whitney + Federer | 分支预测 a.e. 可微 |

**三条红线**：

1. **覆盖与微分红线**——覆盖定理(Vitali/Besicovitch, Ch 1) $\to$ Radon 测度微分(Radon-Nikodym, Ch 1) $\to$ Lipschitz 可微(Rademacher, Ch 6)。「用小球覆盖」驱动「逐点微分」。
2. **几何测度红线**——Hausdorff 测度/维数(Ch 2) $\to$ 面积/共面积公式(Ch 3)。给「不规则集合与 Lipschitz 映射」称重换元。
3. **函数空间红线（payoff）**——Sobolev $W^{k,p}$(Ch 4) $\to$ BV/有限周界(Ch 5) $\to$ 可微性 + Federer 刻画(Ch 6)。回答「粗糙函数有多光滑、在哪可微、边界多规则」。

**读法建议**：第一遍精读 Ch 1（覆盖定理是全书引擎）+ Ch 4（Sobolev 嵌入，PDE 前置）；第二遍死磕 Ch 3（面积/共面积，全书技术枢纽）+ Ch 5（BV/有限周界，变分法核心）；Ch 2/6 按需查阅。全书精读约 60-90 小时（每周 10-20h，6-9 周）。

---

## §9 全书思想主线（约 200 字）

Evans-Gariepy 全书有一条贯穿的灵魂：**「用测度论的工具刻画函数的细（fine）性质——它有多光滑、在哪可微、边界有多规则」**。这条主线沿三层展开：

**第一层（Ch 1）测度地基**：Radon 测度 + 覆盖定理（Vitali/Besicovitch）→ 测度微分（Radon-Nikodym、Lebesgue 微分）。覆盖定理是全书引擎——「用小球盖住集合」精确地转化为测度估计。

**第二层（Ch 2-3）几何测度**：Hausdorff 测度给分形称重（Ch 2），面积/共面积公式处理 Lipschitz 映射下的换元与切片（Ch 3）。这两章把「不规则集合与映射」纳入可计算框架。

**第三层（Ch 4-6）函数空间 payoff**：Sobolev 函数（Ch 4，弱导数 + 嵌入）→ BV/有限周界（Ch 5，测度值导数 + 约化边界）→ 可微性刻画（Ch 6，Rademacher + Federer）。这三章是全书的「细性质」收束——粗糙函数（Sobolev/BV/Lipschitz）在「绝大多数点」上有好的性质（可微、有法向量、有迹），例外点集是零测的。

与 Folland/Royden 的区别：它们停在 $L^p$（函数空间的第一站），Evans-Gariepy 从 $L^p$ 继续冲向 Sobolev/BV/Lipschitz（「粗糙但仍有结构」的函数）；与 Mattila 的区别：Mattila 是纯 GMT（集合与测度的几何），Evans-Gariepy 把 GMT 与函数空间（Sobolev/BV）缝合，是 PDE 与变分法工作者的必备工具箱。本书是 Evans《PDE》(GTM19) 的理论后盾——PDE 书里引用的 Sobolev 嵌入、迹定理、BV 结构定理，证明细节都在这里。

---

## §10 与本仓库其他笔记的交叉引用

- **与 Folland《Real Analysis》对比**（stage-2，已做）：Folland Ch 1-3（测度+积分+RN）$\approx$ Evans-Gariepy Ch 1 前半；Folland Ch 4（$L^p$）是 Evans-Gariepy Ch 4（Sobolev）的前置。**差异**：Folland 覆盖泛函/Fourier/拓扑群全景但**不碰 Sobolev/BV/Hausdorff**；Evans-Gariepy 从 Radon 测度直接冲向函数的细性质，是 Folland Ch 4 之后的「几何+PDE 方向」。建议：Folland 先读建立抽象测度论基础 $\to$ Evans-Gariepy 学 Sobolev/BV 的几何测度论视角。

- **与 Royden《实分析》对比**（stage-2，已做）：Royden Ch 1-8（$\mathbb{R}$ 上 Lebesgue）+ Ch 9-12（一般测度）$\approx$ Evans-Gariepy Ch 1；Royden Ch 6（微分与积分，AC 函数）是 Evans-Gariepy Ch 5-6（BV + 可微性）的 $\mathbb{R}^1$ 前身。**差异**：Royden 停在「一维绝对连续=FTC 成立」，Evans-Gariepy 推到 $\mathbb{R}^n$ 的 BV/有限周界/Rademacher。建议：用 Royden Ch 6 的「AC 函数」直觉理解 Evans-Gariepy Ch 5 的「BV 函数」（一维 BV = AC + 跳跃）。

- **与 Halmos《Measure Theory》GTM18 对比**（stage-2，已做）：Halmos 是纯抽象测度论（无几何/PDE），Evans-Gariepy 是「$\mathbb{R}^n$ 上的具体测度 + 函数细性质」。建议：Halmos 补抽象严格性，Evans-Gariepy 补几何与 PDE 应用。

- **与 Evans《Partial Differential Equations》GTM19 对比**（stage-3，已做）：GTM19 大量使用 Sobolev 空间（Ch 5-6）、迹定理、Poincaré 不等式、BV 函数——这些工具的**严格证明**在 Evans-Gariepy Ch 4-5。建议：读 GTM19 时手边备 Evans-Gariepy 作参考，遇到 Sobolev 嵌入/迹定理的细节就回查。

- **AI 锚点**（数学 ↔ 工程）：
  - 🟢 **Sobolev 嵌入 = 正则性升级**：$W^{1,p}\hookrightarrow L^{p^*}$ 说明「梯度可控则函数本身可控」——神经网络损失景观中，参数梯度的 $L^p$ 界直接给出函数值的界（泛化误差估计的 PDE 视角）。
  - 🟢 **BV = 稀疏变差**：BV 函数的导数是测度（可有原子），类比 $\ell^1$ 稀疏信号——全变差去噪（ROF 模型 $\min\|u-f\|^2+\lambda\|Du\|_{TV}$）直接用 BV 理论，图像处理的数学根基。
  - 🟡 **Hausdorff 维数 = 数据本征维数**：流形学习估计数据集的内在维数，本质是 Hausdorff 维数的统计估计；分形数据（如金融市场 tick 数据）维数 $\neq$ 欧氏维数。
  - 🟡 **Rademacher = Lipschitz 网络可微**：Lipschitz 神经网络（Wasserstein GAN 的判别器约束）a.e. 可微（Rademacher），保证梯度下降有定义；Lipschitz 常数控制对抗鲁棒性。
  - 🟡 **共面积公式 = 水平集分解**：共面积公式把体积分拆成水平集面积分，类比神经网络激活值的「等高线分析」——理解模型在哪层「切片」上信息最密集。

---

## §11 自测答案要点（供核对）

1. **Ch 1** Besicovitch 覆盖比 Vitali 强在不依赖球的缩放比；$\nu\ll\mu$ 例：$\nu(E)=\int_E f\,d\mu$（$f\in L^1$），$\nu\perp\mu$ 例：$\delta_0\perp$ Lebesgue（$\{0\}$ 的 Lebesgue 测度为 0）。
2. **Ch 2** Cantor 集：每步留 $2^k$ 段、每段长 $3^{-k}$，$2^k\cdot(3^{-k})^s=1\Rightarrow 2\cdot3^{-s}=1\Rightarrow s=\log2/\log3$ ✓。Koch 曲线：每步 $4^k$ 段、每段长 $3^{-k}$，$4\cdot3^{-s}=1\Rightarrow s=\log4/\log3$ ✓。
3. **Ch 3** 面积公式：$f(x)=Ax$，$Jf=|\det A|$，$\int g(Ax)|\det A|\,dx=\int g(y)\,dy$ ✓（经典换元）。共面积：$f(x)=|x|$，$Jf=1$，水平集 $f^{-1}(r)=\partial B_r$（$n-1$ 维球面），$\int g\,dx=\int_0^\infty\int_{\partial B_r}g\,d\mathcal{H}^{n-1}\,dr$ ✓（球坐标）。
4. **Ch 4** $u=|x|^{-\alpha}$：$|Du|\sim|x|^{-\alpha-1}$，$\int_{B_1}|x|^{(-\alpha-1)p}\,dx$ 收敛 $\Leftrightarrow$ $(-\alpha-1)p+n>0$ $\Leftrightarrow$ $\alpha<\frac np-1$ ✓。$W^{1,p}_0$：$u_\Omega=0$（零边界），Poincaré 退化为 $\|u\|_{L^p}\leq C\|\nabla u\|_{L^p}$ ✓。
5. **Ch 5** $\chi_{B_1}$：$D\chi_{B_1}=-\nu\,\mathcal{H}^{n-1}\lfloor\partial B_1$，$P(B_1)=\mathcal{H}^{n-1}(\partial B_1)=n\omega_n$，$|B_1|=\omega_n$，等周 $n\omega_n\geq n\omega_n^{1/n}\omega_n^{(n-1)/n}=n\omega_n$ 取等 ✓。$\partial E\neq\partial^*E$：给球加一条「刺」（线段），$\mathcal{H}^{n-1}$ 测度为 0 但拓扑边界变大。
6. **Ch 6** $f=|x|$ Lipschitz（常数 1），除 $x=0$ 外可微 ✓。Cantor 函数**不 Lipschitz**（它连续、BV、$F'=0$ a.e. 但 $F$ 不恒常数，是「奇异函数」），Rademacher 不适用；它是分布导数为奇异测度的典型。

---

## 三条红线回顾

1. **覆盖与微分红线**：覆盖定理(Vitali/Besicovitch, Ch 1) $\to$ Radon 测度微分(Radon-Nikodym, Ch 1) $\to$ Lipschitz 可微(Rademacher, Ch 6)。
2. **几何测度红线**：Hausdorff 测度/维数(Ch 2) $\to$ 面积/共面积公式(Ch 3)。
3. **函数空间红线（payoff）**：Sobolev $W^{k,p}$(Ch 4) $\to$ BV/有限周界(Ch 5) $\to$ 可微性 + Federer 刻画(Ch 6)。

> 与本仓库衔接：Evans-Gariepy Ch 1 对应 `folland_实分析_快速逐章` Ch 1-3 + `royden_全20章` Ch 9-11；Ch 4（Sobolev）是 `evans_PDE偏微分方程_快速逐章` 的直接前置；Ch 5（BV）与 `royden` Ch 6（一维 AC/FTC）互为低维-高维对照。建议先读 Folland/Royden 建立测度论基础，再用 Evans-Gariepy 学 Sobolev/BV 的几何测度论视角，最后接 Evans《PDE》GTM19 做 PDE 应用。
