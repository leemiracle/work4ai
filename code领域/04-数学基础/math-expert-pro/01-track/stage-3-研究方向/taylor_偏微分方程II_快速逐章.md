# Michael E. Taylor《偏微分方程 II：线性方程的定性研究》 · 快速逐章精读

> 基于原书：*Partial Differential Equations II — Qualitative Studies of Linear Equations*, Applied Mathematical Sciences 116（Michael E. Taylor, Springer, 2nd ed., 2011；初版 1996）/ 读于：2026-07-03
> 定位：**线性 PDE 的「定性研究」纵深卷**，用微局部机器回答奇性 / 谱 / 散射 / 发展 / 边界五大定性问题。
> 关联：[Taylor PDE I](taylor_偏微分方程I_快速逐章.md)（双子·奠基卷） · [Hörmander ALPDO I](hormander_线性偏微分算子I_快速逐章.md) · [Gilbarg-Trudinger 椭圆 PDE](gilbarg_trudinger_椭圆PDE_快速逐章.md) · [Evans PDE](evans_PDE偏微分方程_快速逐章.md) · [Lang 实与泛函分析 GTM142](../stage-2-研究生基础/lang_实与泛函分析_GTM142_快速逐章.md)
> 本文为**快速逐章精读**，每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

> 📌 **Vol II 定位与「双子」关系（以原书真实结构为准）**
>
> Taylor 三卷本（AMS 115–117）的第二卷副题为 **「Qualitative Studies of Linear Equations」**。若 [Vol I《Basic Theory》](taylor_偏微分方程I_快速逐章.md) 的任务是「**搭机器**」（古典三方程给直觉、Sobolev 空间搭舞台、拟微分算子与波前集做引论），则 **Vol II 的任务是「用机器回答定性问题」**：解的奇异在何处、如何传播？算子的谱有何渐近规律？远场散射如何刻画？扩散与双曲方程的长期行为如何？边界如何影响正则性？
>
> Vol II 的结构逻辑是「**先深挖机器，再四路应用**」：Ch 1–2 把 Vol I 仅作引论的拟微分算子与波前集展开为**完整符号演算**（含 Vol I 未深论的 $L^2$ 有界性 Calderón-Vaillancourt 定理、Gårding 不等式、奇性传播定理）；Ch 3–8 是四路定性应用——谱理论（Weyl 定律）、散射理论（Lax-Phillips）、扩散（Hille-Yosida 半群 + Friedrichs 扩张）、双曲（能量法）、流形微局部（Egorov 定理）、边值问题（Lopatinski-Shapiro / ADN）。**Vol I 与 Vol II 合为「Taylor PDE 双子」**。

> 🟢 **【事实】** 飞腾锚点中标注 🟢 者，数学概念与硬件性能的关联是事实匹配（如「拟微分算子作用 ⟺ 矩阵向量乘」「计数 = 指示函数求和」），可作严格论证的锚点。
> 🟡 **【类比】** 标注 🟡 者仅供直觉建立（如「Hamilton 流追踪 ↔ 正交化投影」「抛物 CFL 条件 ↔ 误差预算」），**绝不在严格证明中引用**。
> ⭐ 标记为用户高频使用的核心锚点（UDOT / Iron Law / TLB / FP16）。

---

## §0 引言：Taylor 的「定性研究」纵深卷

Michael E. Taylor（UNC Chapel Hill）三卷本《Partial Differential Equations》（Springer AMS 115–117，初版 1996，第二版 2011 全面修订）是 PDE 领域体量最大的现代教材。**Vol II《Qualitative Studies of Linear Equations》是这套大厦的定性分析纵深卷**——与刚完成的 Vol I 合为「双子」。

Vol I 回答「**解长什么样**」（显式公式 + 弱解存在性 + 正则性），Vol II 回答「**解有何性质**」。一句话定位：本书是 stage-3 PDE 方向的**定性分析纵深教材**，把微局部机器（拟微分算子 + 波前集 + Hamilton 流）用作统摄一切线性 PDE 定性性质的统一语言。

Vol II 的设计哲学可凝练为：**Ch 1–2 先把 Vol I 的引论深化为完整机器**——象征类 $S^m_{\rho,\delta}$、合成 / 伴随 / $L^2$ 有界性（Calderón-Vaillancourt）、Gårding 不等式、椭圆拟逆、波前集传播定理（Hörmander 1970 巅峰）；**Ch 3–8 再四路应用**这同一套机器。谱理论用波前集微局部刻画导出 Weyl 定律 $N(\lambda)\sim C\lambda^{n/2}$；散射理论用波算子把入 / 出射态对接为酉散射矩阵 $S$；扩散与双曲用半群（Hille-Yosida）与能量法分别给抛物光滑化与有限传播；流形微局部用 Egorov 定理保证主符号在典范变换下不变；边值问题用 Lopatinski-Shapiro 条件把「内部椭圆性」推广到「边界椭圆性」。

核心哲学凝练为一句话：**微局部分析（拟微分算子 + 波前集 + Hamilton 流）是统摄一切线性 PDE 定性性质的统一语言**——奇性传播、谱渐近、散射矩阵、边界正则性，全部能用「符号在余切丛上的行为」来刻画。这正是 Hörmander 在研究级专著中建立、Taylor 在研究生教材中推广的范式革命。

「定性」（qualitative）一词的精确含义值得强调：它不追求解的**显式公式**（那是 Vol I 古典部分的任务），而追求解的**性质刻画**——奇异在哪、谱如何分布、远场如何散射、长期如何发展、边界如何约束。这两类问题的方法论截然不同：显式公式依赖 Fourier 变换与基本解，定性刻画依赖算子代数（象征演算）与几何动力学（Hamilton 流）。Vol II 的历史意义在于：它把 Hörmander 1970 年的奇性传播定理（20 世纪线性 PDE 最深的成果之一）从研究专著引入研究生教材，使「微局部定性分析」成为可教学的体系。

### 四本 PDE 教材对比

| 书 | 风格 | 严格性 | 适合谁 |
|------|------|--------|--------|
| **Taylor PDE II（本书）** | 定性研究纵深；拟微分 + 波前集完整展开后四路应用；微局部统摄 | ★★★★★（严格且自包含） | PDE / 几何分析研究者 |
| **Taylor PDE I（Vol I 奠基）** | 几何全面奠基；古典三方程 + Sobolev + 拟微分引论 + 波前集引论；搭机器 | ★★★★★ | PDE 研究生（先读） |
| **Hörmander ALPDO I** | 线性 PDE 皇冠；分布论 + Fourier + 波前集严格重建（语言地基） | ★★★★★（极严，逐条重建） | PDE / 分析研究深造 |
| **Gilbarg-Trudinger GT 224** | 二阶椭圆圣经；Schauder 经典 + Sobolev 弱解双轴；先验估计中心 | ★★★★★（逐条证明） | 椭圆 PDE 专精 |

> **阅读策略**：Vol I 搭机器 + 显式解 → **Vol II 用机器做定性研究**（双子合璧）→ Hörmander I 回溯分布论严格地基 → GT 做椭圆专精。四者构成 PDE「四套马车」：Vol I 是「奠基」，Vol II 是「定性纵深」，Hörmander 是「语言地基」，GT 是「椭圆专精」。

### Vol I ↔ Vol II 「双子」逐章映射

Vol I 与 Vol II 的关系是「**引论 → 完整理论 + 定性应用**」：Vol I 给概念种子，Vol II 让它长成完整机器并四路应用。

| Vol I 主题（引论 / 种子） | Vol II 章节（完整 / 应用） | 升级关系 |
|:---|:---|:---|
| 主题 6 拟微分算子（引论） | **Ch 1** 伪微分算子（完整） | 象征类 → $L^2$ 有界性（C-V）+ Gårding + 椭圆拟逆 |
| 主题 7 波前集（引论） + 主题 9 奇性传播 | **Ch 2** 波前集与传播（完整） | $WF$ 定义 → 传播定理（Hörmander 1970）+ Poisson 括号 |
| 主题 8 椭圆边值（谱的引子） | **Ch 3** 谱理论（Weyl 定律） | 特征值存在 → 谱渐近 $N(\lambda)\sim C\lambda^{n/2}$ + 聚类 |
| 主题 3 波方程（显式公式） | **Ch 4** 散射理论 | Kirchhoff 公式 → 波算子 + 散射矩阵 $S$ |
| 主题 4 热方程（显式公式） | **Ch 5** 扩散方程（半群） | 热核卷积 → Hille-Yosida 半群 + Friedrichs 扩张 |
| 主题 3 波方程（能量法） | **Ch 6** 双曲方程 | 能量守恒 → 对称双曲组能量估计 + 有限传播 |
| 主题 6–7（$\mathbb{R}^n$ 微局部） | **Ch 7** 流形微局部 | $\mathbb{R}^n$ 符号 → 不变主符号 + Egorov 定理 |
| 主题 8 椭圆边值（Lax-Milgram） | **Ch 8** 边值问题 | 弱解存在 → Lopatinski-Shapiro + Calderón 投影 |

> 一句话：**Vol I 的每个主题，在 Vol II 都有对应章节的「升级版」**——读者可对照阅读，用 Vol II 的完整理论回溯巩固 Vol I 的直觉，或用 Vol I 的显式例子验证 Vol II 的抽象定理。

---

## §1 全书 8 章骨架一览（飞腾锚点分布）

Vol II 主线是「**深挖微局部机器 → 四路定性应用**」。Ch 1–2 是确定性机器（拟微分算子的完整符号演算 + 波前集传播定理），Ch 3–4 是谱与散射（频域渐近），Ch 5–6 是发展方程（抛物 / 双曲），Ch 7–8 是流形与边界（几何化推广）。每章对接一条飞腾实测锚点，全书 8 锚点各用一次、相邻不重复。

| 章 | 标题（英文 / 中文） | 核心概念 | 飞腾锚点 |
|:-:|------|---------|:--------:|
| 1 | Pseudodifferential Operators（伪微分算子） | 象征类 $S^m_{\rho,\delta}$ · 合成 · 伴随 · **$L^2$ 有界性** · Gårding | GEMM 9.45G 🟢 |
| 2 | Wave Front Sets & Propagation（波前集与奇性传播） | $WF(u)$ · **Hamilton 流** · 次特征带 · 传播定理 | Schmidt 🟡 |
| 3 | Spectral Theory（谱理论） | **Weyl 定律** $N(\lambda)\sim C\lambda^{n/2}$ · 谱聚类 · 本征函数 | UDOT 16.9×⭐ 🟢 |
| 4 | Scattering Theory（散射理论） | 波算子 · **散射矩阵** $S$ · Lax-Phillips · 渐近完备 | matmul 15× 🟢 |
| 5 | Diffusion Equations（扩散方程） | 热半群 · **Hille-Yosida** · **Friedrichs 扩张** · 抛物正则 | Iron Law<2%⭐ 🟡 |
| 6 | Hyperbolic Equations（双曲方程） | 能量估计 · 有限传播 · 对称双曲组 · 唯一性 | FP16 3.81×⭐ 🟡 |
| 7 | Microlocal Analysis on Manifolds（流形微局部） | 不变主符号 · **Egorov 定理** · 余切丛算子代数 | 分支预测 🟡 |
| 8 | Boundary Problems（边值问题） | **Lopatinski-Shapiro** · ADN · Calderón 投影 · 层位势 | TLB 4.81×⭐ 🟡 |

```
确定性机器（Ch 1–2）：把 Vol I 的引论深化为完整理论
Ch 1 伪微分算子 ── 象征类S^m_{ρ,δ}·合成/伴随·L²有界(C-V)·Gårding·椭圆拟逆 ────┐
Ch 2 波前集+传播 ── WF(u)住余切丛·Hamilton流·次特征带·奇性沿流传播 ──────────────┘
          │ 用机器回答「频域定性」
频域定性（Ch 3–4）：谱渐近 + 散射
Ch 3 谱理论 ── Weyl定律 N(λ)~Cλ^{n/2}·谱聚类·本征函数凝聚 ──────────────────────┐
Ch 4 散射理论 ── 波算子W±·酉散射矩阵S·Lax-Phillips·渐近完备 ────────────────────┘
          │ 用机器回答「时间发展」
发展方程（Ch 5–6）：抛物光滑化 + 双曲有限传播
Ch 5 扩散方程 ── 热半群e^{tΔ}·Hille-Yosida生成·Friedrichs扩张·抛物正则 ────────┐
Ch 6 双曲方程 ── 能量估计·对称双曲组(Friedrichs)·有限传播·唯一性 ──────────────┘
          │ 用机器回答「几何化与边界」
几何 + 边界（Ch 7–8）：流形不变性 + 边界椭圆性
Ch 7 流形微局部 ── 不变主符号·Egorov定理·典范变换保算子代数·Hodge ──────────────┐
Ch 8 边值问题 ── Lopatinski-Shapiro·ADN补充条件·Calderón投影·层位势 ────────────┘

数学根基：Taylor PDE I（Sobolev/拟微引论）·Hörmander I（分布论）
         ·Lang GTM142（谱定理/半群/紧算子）·Lee光滑流形（余切丛/Hamilton流）
```

---

## 确定性机器

### 第 1 章 · Pseudodifferential Operators（伪微分算子）

- **核心**：本章把 [Vol I 主题 6](taylor_偏微分方程I_快速逐章.md) 仅作引论的拟微分算子展开为**完整符号演算**，是 Vol II 一切定性研究的工具基础。
  - ① **象征类** $S^m_{\rho,\delta}$——函数 $p(x,\xi)$ 满足 $|D_x^\beta D_\xi^\alpha p|\le C_{\alpha\beta}\langle\xi\rangle^{m-\rho|\alpha|+\delta|\beta|}$；经典类 $S^m_{1,0}$ 对应微分算子。
  - ② **量化与合成**——$p$ 量化为 $\mathrm{Op}(p)u(x)=\int e^{ix\cdot\xi}p(x,\xi)\hat u(\xi)\,d\xi$；两算子合成的主符号 = 两符号之积（模低阶），使算子代数化。
  - ③ **伴随**——$\mathrm{Op}(p)^*=\mathrm{Op}(p^*)$，主符号取复共轭，使算子代数关于对合封闭。
  - ④ **$L^2$ 有界性**（Calderón-Vaillancourt）与 **Gårding 不等式**（正主符号 ⟹ 算子「半正定」）——把「代数条件」（象征符号）翻译为「分析结论」（算子有界 / 强制）。
  - ⑤ **椭圆拟逆** $PQ=I+R$（$R$ 光滑化）——给椭圆正则性的代数化证明。

- **飞腾锚点** 🟢：**GEMM 9.45G** [Lab05]。拟微分算子作用 $\mathrm{Op}(p)u$ 是**变符号密集积分变换**——离散后是 $N\times N$ 大矩阵（符号在 Fourier 网格上采样）乘向量，正是 GEMM。Calderón-Vaillancourt 定理保证该「矩阵」的算子范数有界（$\le C\sup$ 有限阶导数），即 GEMM 的谱范数受控。9.45 GFLOPS 直接决定大规模 PDE 的拟微分算子作用吞吐。标 🟢（事实：算子作用 ⟺ 矩阵向量乘）。

- **关键定理**：**Calderón-Vaillancourt $L^2$ 有界性**——$p\in S^0_{\rho,\rho}$（$0<\rho\le1$）⟹ $\mathrm{Op}(p)$ 在 $L^2(\mathbb{R}^n)$ 上有界，且
  $$\|\mathrm{Op}(p)\|_{L^2\to L^2}\le C\sup_{|\alpha|,|\beta|\le N(n)}|D_\xi^\alpha D_x^\beta p|,$$
  即算子范数仅由**有限阶**（$N$ 依赖维数 $n$）象征导数控制。重要性：它把「零阶拟微分算子」纳入 $L^2$ 有界算子范畴，使象征演算的代数操作有分析的合法性——这是 Ch 2–8 一切估计的基石。**Gårding 不等式**：$\mathrm{Re}\,p\ge c|\xi|^m$（$|\xi|$ 大）⟹ $\mathrm{Re}\langle\mathrm{Op}(p)u,u\rangle\ge c'\|u\|_{H^{m/2}}^2-C\|u\|_{L^2}^2$。

- **自测**：① 写出 Laplace 算子 $-\Delta$ 的主符号 $p_2=|\xi|^2$，验证它满足 Gårding 条件。② Calderón-Vaillancourt 为何只需「有限阶」导数（提示：象征渐近展开截断后余项光滑化）？③ 验证 $\mathrm{Op}(p)\mathrm{Op}(q)$ 的主符号 $=(pq)_m$（主部之积）。

---

### 第 2 章 · Wave Front Sets and Propagation of Singularities（波前集与奇性传播）★ 微局部顶峰

- **核心**：本章是 Vol II 的**微局部分析高潮**——把 [Vol I 主题 7](taylor_偏微分方程I_快速逐章.md) 的波前集深化为**完整的奇性传播理论**。
  - ① **波前集** $WF(u)\subset T^*\Omega\setminus0$ 记录奇异在哪个**余方向**出现——比支撑更精细（$\delta$ 的 $WF=\{(0,\xi):\xi\ne0\}$，原点全方向奇异）。
  - ② **Hamilton 流**——主符号 $p(x,\xi)$ 生成切向量场 $H_p=(\partial_\xi p,-\partial_x p)$，其积分曲线是**次特征带**（bicharacteristics），住在余切丛上。
  - ③ **传播定理**（Hörmander 1970 巅峰）——$Pu=f$ 的解，$WF(u)\setminus WF(f)\subset\mathrm{Char}(P)=\{p=0\}$，且沿 $H_p$ 流**不变**：奇异只在特征集上沿流移动、不凭空产生。这把「整体唯一性」细化到「微局部唯一性」。
  - ④ **Poisson 括号** $\{p,q\}=H_pq$ 控制算子交换结构——$\{p,q\ne0$ 表示两算子「横截」，是次特征带切向信息的代数化身。

- **飞腾锚点** 🟡：**Schmidt 正交化**。Hamilton 流 $H_p$ 的积分曲线追踪是**坐标变换 + 投影**——在余切丛上沿特征方向推进，每步把分量重新组合到「主符号坐标系」上，与 Gram-Schmidt 正交分解的思想同源：次特征带 = 把波动方程的光锥结构「正交分解」到频率方向。标 🟡（类比，直觉用）。

- **关键定理**：**奇性传播定理（Hörmander）**——$P=\mathrm{Op}(p)\in OPS^m_{1,0}$ 主型（$dp\ne0$ 于 $\mathrm{Char}(P)$），$Pu=f$，则
  $$WF(u)\setminus WF(f)\subset\mathrm{Char}(P)=\{p(x,\xi)=0\},$$
  且 $WF(u)\setminus WF(f)$ 在 $H_p$ 的 Hamilton 流下**不变**（奇异沿次特征带传播）。重要性：它精确预言了解在何处奇异、奇异如何传播——波方程的奇异沿光锥传播，椭圆方程无奇性传播（特征集为空）。这是 20 世纪线性 PDE 最深的定性结果之一。

- **自测**：① 波方程 $u_{tt}-\Delta u=0$ 的次特征带是什么（光锥 $x=\pm t+\mathrm{const}$）？奇异如何沿光锥传播？② 为何椭圆算子（如 $-\Delta$）无奇性传播（$\mathrm{Char}=\varnothing$ ⟹ $WF(u)=WF(f)$）？③ Poisson 括号 $\{p,q\}\ne0$ 为何意味着两算子「横截」（提示：$H_p$ 与 $H_q$ 线性无关）？

---

## 频域定性

### 第 3 章 · Spectral Theory（谱理论）

- **核心**：本章把微局部机器用于**椭圆算子的谱渐近**——回答「本征值如何分布」这一核心定性问题。紧流形 $M$ 上的 Laplace-Beltrami 算子 $\Delta$ 有离散谱 $0=\lambda_0\le\lambda_1\le\cdots\to\infty$（紧嵌入 + 谱定理）。Taylor 用波前集的微局部刻画导出：
  - ① **Weyl 定律**——本征值计数函数 $N(\lambda)=\#\{k:\lambda_k\le\lambda\}$ 满足 $N(\lambda)\sim C\,\mathrm{Vol}(M)\lambda^{n/2}$（$\lambda\to\infty$），常数 $C=(2\pi)^{-n}\omega_n$。本质是「**本征值计数 = 频率球内格点计数**」。
  - ② **谱聚类**——当 Hamilton 流**周期**时（如球面），本征值聚集成簇（簇间距 $\to0$）；当流**遍历**时，本征值服从随机矩阵统计（量子遍历）。
  - ③ **本征函数凝聚**——高频本征函数的 $L^2$ 质量分布由测地流决定：可积系统沿环面凝聚，混沌系统均匀铺开（量子唯一遍历性猜想，Shnirelman-Colin de Verdière-Zelditch）。

- **飞腾锚点** 🟢：**UDOT 16.9×⭐** [E05]。Weyl 定律 $N(\lambda)\sim C\lambda^{n/2}$ 的本质是**频率球 $\{|\xi|\le\sqrt{\lambda}\}$ 内的格点计数**——$N(\lambda)=\sum_k\mathbf{1}_{\lambda_k\le\lambda}$，即指示函数向量与全 1 向量的内积（点积累加），正是 UDOT（无符号点积）加速场景。大批频率网格上的计数求和直接受益于 16.9× 增益。标 🟢（事实：计数 = 指示函数求和 = 点积）。

- **关键定理**：**Weyl 谱渐近定律**——紧 $n$ 维流形 $M$ 上 Laplace 算子的本征值计数函数
  $$N(\lambda)\sim\frac{\omega_n}{(2\pi)^n}\,\mathrm{Vol}(M)\,\lambda^{n/2},\quad\lambda\to\infty,$$
  其中 $\omega_n$ 为 $n$ 维单位球体积。重要性：它给出「高频模式数正比于相空间体积」这一普适规律——本征值越密，频率球越大；体积越大，模式越多。**聚类定理**：若测地流周期，本征值聚集在周期轨道对应的频率处。

- **自测**：① 验证 Weyl 定律对 $\mathbb{T}^n$ 上 Laplacian 成立（$\lambda_k=|k|^2$，$N(\lambda)\approx$ 球 $\{|k|\le\sqrt\lambda\}$ 内整点数）。② 维数 $n$ 为何出现在指数 $n/2$（提示：频率空间维数 = 流形维数）？③ 为何球面 $S^2$ 上 Laplacian 的本征值成簇（测地流周期：大圆闭轨）？

---

### 第 4 章 · Scattering Theory（散射理论）

- **核心**：散射理论研究**远场渐近行为**——波方程的解在 $t\to\pm\infty$ 时如何分解为「自由传播」与「散射」两部分。
  - ① **波算子** $W_\pm$——把相互作用解 $u(t)=e^{-itH}u_0$ 与自由解 $e^{-itH_0}\phi$ 在 $t\to\pm\infty$ 时对接：$W_\pm\phi=\lim_{t\to\pm\infty}e^{itH}e^{-itH_0}\phi$（$H=H_0+V$ 含势，$H_0=-\Delta$ 自由）。
  - ② **渐近完备性**——$W_\pm$ 的像空间张成连续谱部分（$\mathrm{Ran}\,W_+=\mathrm{Ran}\,W_-=$ 连续谱子空间），意味着每个散射态都可被自由态逼近。
  - ③ **散射矩阵** $S=W_+^{-1}W_-$——把入射态映到出射态，是酉算子（能量守恒）。在频率壳上 $S(\xi)$ 是相位旋转 $e^{2i\delta(\xi)}$，相位偏移 $\delta(\xi)$ 编码散射体的全部信息。
  - ④ **Lax-Phillips 理论**——在「障碍物外的波动」几何框架下，用平移表示给散射矩阵的显式构造，把散射极点（resonance）与障碍几何联系起来。

- **飞腾锚点** 🟢：**matmul 15×** [V03]。散射矩阵 $S=W_+^{-1}W_-$ 是 $L^2$（能量空间）上的**酉算子**，把入射态映到出射态——离散化后是酉矩阵乘状态向量，正是 matmul。$S$ 在频率壳上的作用（相位旋转 $e^{2i\delta(\xi)}$）也是批量复数乘法。15× 向量化增益直接加速多频率散射计算。标 🟢（事实：酉算子作用 ⟺ 矩阵向量乘）。

- **关键定理**：**波算子存在性与完备性**——若 $V$（势）短程（$\|V\|(H_0+1)^{-1}$ 紧），则波算子 $W_\pm=\mathrm{s}\text{-}\lim_{t\to\pm\infty}e^{itH}e^{-itH_0}$ 存在且渐近完备（$\mathrm{Ran}\,W_\pm$ 张成连续谱子空间）。**散射矩阵酉性**：$S=W_+^{-1}W_-$ 是酉算子（能量守恒 ⟹ 保范）。重要性：完备性保证散射描述无信息丢失，酉性保证物理可观测。

- **自测**：① 为何散射矩阵 $S$ 必须酉（入射能量 = 出射能量 ⟹ 保范）？② 相位偏移 $\delta(\xi)=0$ 意味着什么（无散射，自由传播）？③ 逆散射如何从 $S(\xi)$ 反推势 $V$（提示：Gel'fand-Levitan-Marchenko 方程）？

---

## 发展方程

### 第 5 章 · Diffusion Equations（扩散方程）

- **核心**：本章把 [Vol I 主题 4](taylor_偏微分方程I_快速逐章.md) 的热方程深化为**半群理论框架**——把「热方程 = 由 $\Delta$ 生成的半群」抽象化。
  - ① **热半群** $e^{t\Delta}$——Laplace 算子生成**压缩半群**（$\|e^{t\Delta}u\|\le\|u\|$），$e^{t\Delta}u_0$ 给热方程 Cauchy 问题解，$t>0$ 时光滑化（高频模式 $e^{-t\lambda_k}$ 指数衰减）。
  - ② **Hille-Yosida 定理**——刻画「闭稠定算子 $A$ 生成压缩半群」的充要条件（预解式估计 $\|(\lambda I-A)^{-1}\|\le1/\lambda$），把 PDE 的适定性归结为**算子半群生成**。
  - ③ **Friedrichs 扩张**——非负对称算子（如散度型椭圆算子的弱形式）可扩张为**自伴算子**，保证谱定理适用、本征函数正交基存在。
  - ④ **抛物正则性**——$u_t+Lu=f$，$f\in H^s$ ⟹ $u\in H^{s+2m}$（增益 $2m$ 阶），解比右端光滑。半群框架适用于一般抛物方程与马尔可夫过程（Fokker-Planck / 扩散过程）。

- **飞腾锚点** 🟡：**Iron Law<2%⭐** [Lab00]。热半群 $e^{t\Delta}$ 是**压缩半群**（高频模式 $e^{-t\lambda_k}$ 指数衰减）——抛物方程数值稳定，但显式 Euler 有 **CFL 条件** $dt<dx^2/2$，违反即数值爆炸。这是「误差须压进预算」的铁律：稳定步长是精度 / 稳定性权衡参数，与 Iron Law 性能铁律（误差须 <2%）同构。隐式格式无条件稳定但每步需解线性系统。标 🟡。

- **关键定理**：**Hille-Yosida 定理**——闭稠定算子 $A$ 生成强连续压缩半群 $\{T(t)\}_{t\ge0}$ 当且仅当 $(0,\infty)\subset\rho(A)$（预解集）且 $\|(\lambda I-A)^{-1}\|\le1/\lambda$（$\lambda>0$）。重要性：它把「PDE 适定性」转化为「算子的预解式估计」——一个纯泛函条件，使抽象分析工具（谱理论）直接服务于 PDE 存在性。**Friedrichs 扩张**：稠定非负对称算子 $A$（$\langle Au,u\rangle\ge0$）存在自伴扩张 $A_F$，定义域含于形式域。

- **自测**：① 验证 $e^{t\Delta}$ 是压缩半群（$\|e^{t\Delta}u\|_{L^2}\le\|u\|_{L^2}$，因 $e^{-t\lambda_k}\le1$）。② 为何显式 Euler 解热方程需要 CFL 条件而隐式不需要（显式放大高频噪声）？③ Friedrichs 扩张为何对散度型椭圆算子必要（弱形式只给对称，需自伴才能用谱定理）？

---

### 第 6 章 · Hyperbolic Equations（双曲方程）

- **核心**：本章深化 [Vol I 主题 3](taylor_偏微分方程I_快速逐章.md) 的波方程为**一般双曲方程组理论**——核心特征是**无耗散 + 有限传播**。
  - ① **对称双曲组**（Friedrichs）——一阶方程组 $\partial_tu=\sum_j A_j(t,x)\partial_{x_j}u+F$，系数矩阵 $A_j$ 对称，可用能量法处理（非对称组需更强条件）。
  - ② **能量估计**——构造能量 $E(t)=\int|u|^2\,dx$，分部积分得 $\frac{dE}{dt}\le CE+F$ ⟹ **Gronwall 不等式**给 $E(t)\le(E(0)+\int|F|^2)e^{Ct}$，由此得唯一性与适定性。
  - ③ **有限传播速度**——扰动只在依赖区域（光锥 $\{|x-x_0|\le t\}$）内传播，与热方程的无穷传播对比鲜明：波方程的能量守恒使信息「不泄漏」，热方程的耗散使信息「瞬时弥漫」。
  - ④ **存在性与唯一性**——能量估计 + Galerkin 逼近给整体解；对称性是能量法的关键（保证边界项消失）。数值上双曲方程需保能量 / 辛格式。

- **飞腾锚点** 🟡：**FP16 3.81×⭐** [L01]。双曲方程**无耗散**，能量守恒意味着数值误差**不衰减**——长期积分中浮点误差线性累积。FP16（$\varepsilon\approx9.8\times10^{-4}$）下误差比 FP64 增长更快，3.81× 速度差背后是「精度-时间」权衡：双曲方程数值需要辛格式保能量，FP16 的有限精度天然破坏辛结构。标 🟡。

- **关键定理**：**对称双曲组的能量估计**——$\partial_tu=\sum_jA_j\partial_{x_j}u+F$（$A_j=A_j^T$）⟹ 存在 $C$ 使
  $$E(t)\le C\bigl(E(0)+\int_0^t\|F(s)\|_{L^2}^2\,ds\bigr)e^{Ct},\quad E(t)=\|u(\cdot,t)\|_{L^2}^2,$$
  由此得唯一性（$F=0,u(0)=0\Rightarrow u\equiv0$）。**有限传播**：依赖区域 $\{|x-x_0|\le t\}$ 外 $u=0$（扰动速度 $\le1$）。重要性：能量法不依赖显式公式，可推广到变系数与非线性波方程。

- **自测**：① 用能量法证明波方程 Cauchy 问题解的唯一性。② 为何双曲方程有限传播而热方程无穷传播（波 = 守恒，热 = 耗散光滑化）？③ 对称性条件 $A_j=A_j^T$ 在能量估计中起什么作用（保证分部积分边界项消失）？

---

## 几何与边界

### 第 7 章 · Microlocal Analysis on Manifolds（流形上的微局部分析）

- **核心**：本章把 Ch 1–2 的拟微分算子与波前集从 $\mathbb{R}^n$ **提升到流形** $M$ 上，建立坐标不变的微局部理论——保证微局部语言在几何 PDE 中不变地运作。
  - ① **不变主符号**——拟微分算子在流形上通过坐标卡局部定义，其主符号 $p_m\in C^\infty(T^*M\setminus0)$ 在余切丛上**坐标不变**（变换律由坐标变换的余切提升给出）。这是「主符号必须住在余切丛」的根本原因。
  - ② **Egorov 定理**——共轭 $\mathrm{Op}(p)$ 由 Fourier 积分算子（如双曲方程的解算子 $U(t)$）给出时，结果仍是拟微分算子，且主符号沿**典范变换**（$H_p$ 生成的辛同胚 $\Phi_t$）运输：$\sigma_{\mathrm{pr}}(U^{-1}\mathrm{Op}(q)U)=q_m\circ\Phi_t$。这把「解算子共轭」与「Hamilton 流运输」精确联系。
  - ③ **Hodge 理论**——流形上椭圆复形（de Rham 复形）的上同调由**调和形式**表示（Hodge 定理：每个上同调类有唯一调和代表），是指标理论（Atiyah-Singer）的先声。Taylor 在此为 Vol III 的指标理论埋下伏笔。

- **飞腾锚点** 🟡：**分支预测** [Lab02]。流形上的波前集 $WF(u)\subset T^*M\setminus0$ 在**每个点** $x\in M$ 记录哪些**余方向** $\xi$ 奇异——这是逐「点-方向」对的 yes/no 分类（Fourier 变换在此锥是否速降），分支密集逻辑；拟微分算子在流形上经坐标卡拼接，卡变换处的条件分支也类似。分支预测器可预测分支（0.71 CPI）vs 误预测（3.14 CPI）对应「光滑方向」与「奇异方向」的分野。标 🟡。

- **关键定理**：**主符号坐标不变性**——$\mathrm{Op}(p)$ 在坐标变换 $\kappa$ 下，主符号变换为 $p_m\circ\kappa'$（$\kappa'$ 为 $\kappa$ 的余切提升）。**Egorov 定理**：$U(t)$ 为 $\partial_tu=i\mathrm{Op}(p)u$ 的解算子，则 $U(t)^{-1}\mathrm{Op}(q)U(t)$ 仍是 $\Psi$DO，主符号为 $q_m\circ\Phi_t$（$\Phi_t$ 为 $H_p$ 的 Hamilton 流）。重要性：Egorov 定理保证微局部语言在「流形 + 几何方程」中不变，使 Ch 1–2 的 $\mathbb{R}^n$ 理论自动适用于弯曲时空、流形上的波 / 热方程。

- **自测**：① 为何主符号 $p_m(x,\xi)$ 必须住在余切丛 $T^*M$（而非切丛）？提示：余向量在坐标变换下的变换律。② Egorov 定理如何把「解算子共轭」与「Hamilton 流运输」联系起来？③ Hodge 定理为何说「每个 de Rham 上同调类有唯一调和代表」（椭圆算子的核有限维）？

---

### 第 8 章 · Boundary Problems（边值问题）

- **核心**：本章把 [Vol I 主题 8](taylor_偏微分方程I_快速逐章.md) 的椭圆边值推广为**完整的边界椭圆性理论**——把「内部椭圆性」推广到「边界椭圆性」。
  - ① **Lopatinski-Shapiro 条件**——边值问题 $\{P,B_1,\ldots,B_m\}$（$P$ 阶 $2m$，$m$ 个边界条件）Fredholm 的充要：对每个边界点，模型半空间问题（$P$ 的冻结系数 + $B_j$ 的主部）在 $L^2(\mathbb{R}^n_+)$ 中只有零解。即边界条件「正好够」消除半空间退化解。
  - ② **Agmon-Douglis-Nirenberg（ADN）**——把 Schauder / Sobolev 估计推广到椭圆组与边界，给 $C^{k,\alpha}$ 与 $W^{k,p}$ 正则性：满足补足条件 ⟹ 解的正则性提升 $2m$ 阶。
  - ③ **Calderón 投影**——用拟微分算子把边值问题约化为**边界上的拟微分方程**（$Bu|_{\partial\Omega}$ 满足 Calderón 投影的像），把高维内部问题降为低维边界问题。
  - ④ **层位势**——单层 / 双层位势把边值问题化为边界积分方程，未知量是边界密度（降维）。

- **飞腾锚点** 🟡：**TLB 4.81×⭐** [E04]。边值问题的作用集中在**边界** $\partial\Omega$（低一维子流形）——椭圆边界正则性、Calderón 投影、层位势全部「活在边界上」，是「局部」特征。这与 TLB 管理「局部热页」的内存局部性同构：边界是「缓存热」的局部窗口，层位势的有效支撑 = 缓存局部带。4.81× 命中增益正来自边界局部访问。标 🟡。

- **关键定理**：**Lopatinski-Shapiro 椭圆边界条件**——$\{P,B_1,\ldots,B_m\}$（$P$ 椭圆 $2m$ 阶）Fredholm 当且仅当：对每个边界点，模型半空间问题（$P$ 的冻结系数 + $B_j$ 的主部）在 $L^2(\mathbb{R}^n_+)$ 中只有零解。**ADN 正则性**：满足补足条件 ⟹ $\|u\|_{W^{k+2m,p}}\le C(\|Pu\|_{W^{k,p}}+\sum\|B_ju\|+\|u\|_{L^p})$。重要性：Lopatinski-Shapiro 是「内部椭圆性」的边界推广——主符号可逆保证内部正则，补足条件保证边界正则。

- **自测**：① Dirichlet 问题 $\{P,u|_{\partial\Omega}=g\}$ 为何满足 Lopatinski 条件（半空间上 $P$ 椭圆 + 边界值固定 ⟹ 唯一衰减解）？② 单层位势如何把 Dirichlet 问题化为边界积分方程（未知量 = 边界密度）？③ Neumann 问题（法向导数给定）为何也满足补足条件？

---

## §9 全书思想主线：微局部机器统摄线性 PDE 的定性性质

Vol II 的总纲是「**微局部机器统摄线性 PDE 的一切定性性质**」。Ch 1–2 把 Vol I 仅作引论的拟微分算子与波前集展开为完整理论：Calderón-Vaillancourt 给 $L^2$ 有界性（算子「矩阵」的范数受控），椭圆拟逆给正则性的代数化证明，奇性传播定理（Hörmander 1970 巅峰）把「整体唯一性」细化到「微局部唯一性」——奇异沿 Hamilton 流的次特征带传播，不凭空产生。

这套机器一旦定型，Ch 3–8 的四路应用便水到渠成：谱理论用波前集微局部刻画导出 Weyl 定律 $N(\lambda)\sim C\lambda^{n/2}$（本征值计数 = 频率球内格点计数）；散射理论用波算子把入 / 出射态对接为酉散射矩阵 $S$；扩散与双曲用半群（Hille-Yosida）与能量法分别给抛物光滑化与有限传播；流形微局部用 Egorov 定理保证主符号在典范变换下不变；边值问题用 Lopatinski-Shapiro 条件把「内部椭圆性」推广到「边界椭圆性」。

读者一旦抓住「**符号 $p(x,\xi)$ 在余切丛上的行为，刻画了线性 PDE 的一切定性性质**」这条主线，就理解了 Vol II 的设计：**不是逐个方程给技巧，而是用一套微局部语言统摄奇性、谱、散射、发展、边界**——这正是 Hörmander 建立而 Taylor 普及的范式革命。与 Vol I 呼应：Vol I「搭机器 + 给显式解」，Vol II「用机器回答定性问题」——双子合璧，构成从古典到微局部的完整纵深。

「双子」的互补结构值得最后点明：Vol I 自下而上（古典 → Sobolev → 拟微引论），回答「**解存在吗、长什么样**」；Vol II 自上而下（微局部机器 → 四路定性应用），回答「**解有何性质**」。两卷合起来，恰好覆盖线性 PDE 从「构造解」到「刻画性质」的全谱。读者若只读 Vol I，会停留在「能算显式解」但「不知解的定性行为」的阶段；若只读 Vol II，则缺少 Vol I 搭的 Sobolev / 拟微引论地基——**必须双子合璧**，方能完整理解现代线性 PDE 理论。

---

## §10 与本仓库其他笔记的交叉引用

- **与 [Taylor PDE I](taylor_偏微分方程I_快速逐章.md)（双子·奠基卷）**：Vol I 搭机器（古典三方程 + Sobolev + 拟微分引论 + 波前集引论 + 显式解），**Vol II 用机器做定性研究**。Vol II Ch 1–2 正是 Vol I 主题 6–7、9 的完整展开（Vol I 给概念引论，Vol II 给 Calderón-Vaillancourt / Gårding / 传播定理的完整理论）；Vol II Ch 5–6 深化 Vol I 主题 3–4（热 / 波方程从显式公式升级到半群 + 能量法框架）。**先读 Vol I 建立直觉，再用 Vol II 补全定性纵深**——双子配对效果最佳。

- **与 [Hörmander ALPDO I](hormander_线性偏微分算子I_快速逐章.md)**：Hörmander I 的分布论 + Fourier 分析是 Vol II Ch 1（拟微分算子）、Ch 2（波前集）的**严格语言地基**——Vol II 的拟微分算子与波前集传播定理正是 Hörmander 四卷全集 Vol III 的研究生教材版。**Hörmander 是「语言重建」，Taylor 是「语言应用 + 定性推广」**。读 Vol II Ch 2 传播定理时可回查 Hörmander Ch VIII 的波前集原始定义。

- **与 [Gilbarg-Trudinger 椭圆 PDE](gilbarg_trudinger_椭圆PDE_快速逐章.md)**：GT 是椭圆专精（Schauder + Sobolev 双轴），Vol II Ch 8（边值问题）覆盖 GT 的椭圆边界轴，但用**微局部方法**（Lopatinski-Shapiro + Calderón 投影）而非纯 Schauder 估计——两种路径互补。GT 给逐条先验估计（Schauder 内 / 边界估计），Taylor 给算子代数化的 Fredholm 判据（补足条件 ⟹ Fredholm）。此外，Vol II Ch 3 的 Weyl 定律在 GT 中只作背景提及，Taylor 给完整微局部证明——这是 GT 完全未覆盖的谱渐近专题。

- **与 [Evans PDE](evans_PDE偏微分方程_快速逐章.md)**：Evans 弱解三部曲是 Vol II Ch 5–6（扩散 / 双曲）的「地图版」——Evans 重存在性直觉，**完全未涉及谱渐近、散射、流形微局部**（Vol II Ch 3–4、7）。Vol II 补全这三大 Evans 缺失的现代专题。读 Evans Part II 后用 Vol II Ch 3–4、7 拓展定性视野。具体而言：Evans Ch 7（热方程弱解）对应 Vol II Ch 5（半群框架升级），Evans Ch 6–7（波方程能量法）对应 Vol II Ch 6（对称双曲组推广），但 Evans 的 Sobolev 弱解视角在 Vol II 升级为「算子半群 + 微局部」的统一框架——这是从「应用驱动」到「理论纵深」的跃迁。

- **与 [Lang 实与泛函分析 GTM142](../stage-2-研究生基础/lang_实与泛函分析_GTM142_快速逐章.md)**：Lang 的谱定理 / 紧算子 / Hilbert 空间理论是 Vol II Ch 3（Weyl 定律依赖紧算子谱）、Ch 5（Hille-Yosida 半群）的泛函基础。读 Vol II 前 Lang GTM142 的谱论与半群章节值得复习。

- **AI / 工程锚点**（Vol II 的微局部定性机器 = AI for Science 的高级数学引擎）：

  - ① **Neural Operator / FNO**：Fourier Neural Operator 在频域学习解算子——Vol II Ch 1 拟微分算子的象征 $p(x,\xi)$ 正是「频域乘法」的推广，FNO 截断高频 = 拟微分算子的低阶近似；Ch 2 波前集刻画神经网络解的高频奇异方向。
  - ② **PINN 谱方法**：用谱展开（Ch 3 Weyl 定律的本征函数基）逼近 PDE 解——PINN 在谱基上的系数学习与 Weyl 谱渐近直接相关，高频截断误差由象征演算（Ch 1）控制。
  - ③ **Diffusion 模型 + 微局部分析**：扩散模型的 score 函数奇异用波前集（Ch 2）微局部刻画；逆向扩散的「去奇异」与微局部光滑化（Ch 5 热半群）同构——这是 Vol II 的 Ch 2 + Ch 5 在生成模型中的交汇。
  - ④ **散射在量子化学 / 逆问题**：Ch 4 散射矩阵 $S$ 的相位偏移 $\delta(\xi)$ 编码散射体信息，是逆散射（医学成像 / 雷达）的数学核心；散射算子的神经网络逼近是 AI for Physics 的前沿。
  - ⑤ **边值问题与有限元**：Ch 8 的 Lopatinski-Shapiro 条件 + ADN 估计是有限元方法（FEM）边界处理的理论依据——机器学习的 PDE 求解器（如 Deep Ritz / PINN with boundary penalty）的收敛性证明依赖边界椭圆性。Calderón 投影把高维问题降为边界积分方程，与边界元法（BEM）直接对应。

> **一句话总结本书的 AI 价值**：Vol II 把「线性 PDE 的定性性质」全部纳入「微局部符号演算 + Hamilton 流」的统一语言，而 AI for Science 的高级分支（Neural Operator 的频域学习、PINN 的谱方法、扩散模型的微局部奇异）恰恰是「在余切丛上用神经网络逼近 PDE 的定性行为」——读通 Vol II，就拿到了从古典 PDE 到现代微局部定性分析的完整阶梯，为理解 AI for Science 的最深数学层铺路。

---

## §11 各章精华一句话

> 八章一气呵成：机器（Ch 1–2）搭好后，谱 / 散射 / 扩散 / 双曲 / 流形 / 边界六路定性应用各取所需。

- **Ch 1**：拟微分算子的完整符号演算——Calderón-Vaillancourt 给 $L^2$ 有界性，Gårding 不等式给正主符号 ⟹ 半正定，椭圆拟逆给正则性代数化证明。
- **Ch 2**★：奇性传播定理——$WF(u)$ 沿 Hamilton 流的次特征带传播，不凭空产生，只在特征集 $\{p=0\}$ 上移动。
- **Ch 3**：Weyl 谱渐近 $N(\lambda)\sim C\lambda^{n/2}$——本征值计数 = 频率球内格点计数；测地流周期 / 遍历决定谱聚类。
- **Ch 4**：波算子 $W_\pm$ 对接入 / 出射态，散射矩阵 $S=W_+^{-1}W_-$ 酉——相位偏移 $\delta(\xi)$ 编码散射体全部信息。
- **Ch 5**：Hille-Yosida 刻画半群生成，Friedrichs 扩张给自伴算子——热半群 $e^{t\Delta}$ 是压缩半群（高频指数衰减）。
- **Ch 6**：对称双曲组的能量估计 + 有限传播——双曲无耗散、扰动只在光锥内传播。
- **Ch 7**：主符号坐标不变（住余切丛），Egorov 定理保证解算子共轭保 $\Psi$DO 类、主符号沿 Hamilton 流运输。
- **Ch 8**：Lopatinski-Shapiro 条件把内部椭圆性推广到边界椭圆性；Calderón 投影把边值问题约化为边界拟微分方程。

---

## 📌 阅读建议（对接数学专家路径）

1. **精读顺序**：Ch 1（拟微分完整机器）→ Ch 2（奇性传播，微局部顶峰）→ **Ch 3（Weyl 定律，频域定性）** → Ch 5（Hille-Yosida 半群，泛函桥梁）→ Ch 6（双曲能量法）→ Ch 4（散射，按需）→ Ch 7（流形微局部，几何化）→ Ch 8（边值问题，按需）。

2. **与 Vol I / Hörmander 配对读**：Vol II Ch 1–2 ↔ Vol I 主题 6–7、9（引论 → 完整理论）；Vol II Ch 1–2 ↔ Hörmander Vol III（拟微分 + 波前集的研究版）。Vol I / Hörmander 各补一面，Vol II 融合并定性推广。

3. **数学根基回溯**：拟微分算子 / 波前集 ⟵ Vol I 主题 6–7 + Hörmander I（已读）；半群 / 谱定理 / 紧算子 ⟵ Lang GTM142（已读）+ Reed-Simon I（已读）；余切丛 / Hamilton 流 ⟵ Lee 光滑流形（已读）；椭圆边值 ⟵ Vol I 主题 8 + GT（已读）。

4. **动手验证**（Python 工程师优势）：Ch 1 用 FFT 实现拟微分算子作用（象征 $p(x,\xi)$ 频域乘法）验证 Calderón-Vaillancourt 的 $L^2$ 稳定性；Ch 3 用 NumPy 数 $\mathbb{T}^n$ 上 Laplacian 本征值验证 Weyl 定律 $N(\lambda)\sim C\lambda^{n/2}$；Ch 5 用 `scipy.linalg.expm` 实现热半群 $e^{t\Delta}$ 验证压缩性；Ch 6 用蛙跳格式验证波方程能量守恒与有限传播。代码即理解，飞腾实测数据则作为「工程极限」的参照系。

5. **深挖课题**（Vol II 特色，选做）：
   - ① Ch 2 奇性传播定理如何把「整体唯一性」细化到「微局部唯一性」——对比波方程（奇异沿光锥传播）与椭圆方程（无奇性传播，$\mathrm{Char}=\varnothing$）。
   - ② Ch 3 Weyl 定律的余项 $o(\lambda^{n/2})$ 如何改进——经典 $O(\lambda^{(n-1)/2})$（Avakumovic-Levitan）到 sharper 的 lattice-point 估计。
   - ③ Ch 5 Hille-Yosida 定理如何把「热方程适定性」归结为「Laplace 算子的预解式估计 $\|(\lambda+\Delta)^{-1}\|\le1/\lambda$」——泛函条件服务 PDE 存在性。
   - ④ Ch 7 Egorov 定理如何保证微局部语言在弯曲时空 / 流形上的波方程中不变运作——通向指标理论（Atiyah-Singer，Vol III）。

6. **前向指针：Vol III《Nonlinear Equations》（AMS 117）**：

   Taylor 三卷本的第三卷把 Vol I–II 的**线性机器**推广到**非线性 PDE**——完全非线性椭圆（Monge-Ampère）、非线性波 / 守恒律（激波、熵条件）、曲率流（Ricci 流、平均曲率流）、Hamilton-Jacobi（粘性解）。Vol II 的微局部工具（Ch 1–2）在 Vol III 升级为**非线性微局部分析**（Fourier 积分算子、para-differential calculus）。读 Vol II 后可按需选读 Vol III 的对应章节——**线性定性（Vol II）是非线性理论（Vol III）的必经前置**。

> 注：本笔记基于 Taylor《Partial Differential Equations II: Qualitative Studies of Linear Equations》（AMS 116, 2nd ed. 2011）撰写快速逐章导览，忠实于 8 章结构，侧重概念串联与飞腾 / AI 锚点对接。关键定理（Calderón-Vaillancourt $L^2$ 有界性、Gårding 不等式、奇性传播定理、Weyl 谱渐近 $N(\lambda)\sim C\lambda^{n/2}$、Hille-Yosida、Friedrichs 扩张、Egorov 定理、Lopatinski-Shapiro 条件）均为标准准确陈述。与 Vol I 合为「Taylor PDE 双子」。
>
> 📊 **规模与定位**：本笔记 8 章全覆盖，每章含核心逻辑串联（4–5 子要点）+ 飞腾锚点 + 关键定理 LaTeX（含重要性简述）+ 自测 2–3 题。飞腾锚点池 8 个与 8 章一一对应、相邻不重复：
> - **GEMM 9.45G**（Ch 1 拟微分算子作用 = 矩阵向量乘）· **Schmidt**（Ch 2 Hamilton 流追踪 = 正交化投影）
> - **UDOT 16.9×**（Ch 3 本征值计数 = 指示函数求和）· **matmul 15×**（Ch 4 散射矩阵 = 酉矩阵作用）
> - **Iron Law<2%**（Ch 5 抛物 CFL = 误差预算）· **FP16 3.81×**（Ch 6 双曲守恒 = 辛结构精度）
> - **分支预测**（Ch 7 波前集方向分类）· **TLB 4.81×**（Ch 8 边界局部性 = 缓存热页）
