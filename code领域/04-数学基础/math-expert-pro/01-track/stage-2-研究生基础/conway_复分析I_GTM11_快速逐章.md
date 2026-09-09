# Conway《单复变函数I》(GTM11) · 快速逐章精读

> 基于原书:Functions of One Complex Variable I, GTM11(John B. Conway, 2nd Ed, 1978) / 读于:2026-07-02
> 定位:**研究生复分析标准教材**,最现代最系统最平衡,GTM 模范读物。
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言:Conway 是什么,为什么读它

John B. Conway 的《Functions of One Complex Variable I》(Springer GTM 11)自 1973 年初版、
1978 年修订为流传至今的第二版以来,一直是**英语世界研究生复分析的标准教材**。它的气质
与 Ahlfors 截然相反:Ahlfors 用几何图像讲故事,Conway 则把复分析建成一座**公理化系统**——
从复数域的代数结构出发,经幂级数、Cauchy 理论、调和函数、解析延拓,直到 Runge 定理与
Riemann 映射,层层递进、处处自洽。Conway 的标志是**用正规族(normal families)证明
Riemann 映射定理**——干净、现代、可教,这是它区别于古典教材的最大特色;另一标志是
独立成章的**调和函数**理论,把 Poisson 核、Dirichlet 问题、次调和函数讲透。

本仓库已精读 Ahlfors(几何直觉圣经)、Gamelin(现代代数味)、钟玉泉(中文标准教材)。
Conway 是第四座山——**最现代、最系统、最平衡**:它补上 Ahlfors 缺的严格骨架、Gamelin
跳过的调和函数专章、钟玉泉没有的 Runge/Montel 全景。四山并读,同一批定理会显出四种面貌。

| 书 | 风格 | 严格性 | 适合谁 |
|:-:|------|:------:|--------|
| Conway GTM11 | 现代系统、正规族证明、调和函数专章、自洽渐进 | 极严格、公理化、习题精 | 欲建完整研究生骨架、自学查漏 |
| Ahlfors《Complex Analysis》 | 几何直觉、古典单复变、球面图景驱动 | 严格但偏直觉叙述 | 想获得几何洞察、读「原典」者 |
| Gamelin《Complex Analysis》 | 现代代数工具、Riemann 面/多复变入门 | 严格、抽象、代数味 | 喜代数味、工程与理论兼顾 |
| Stein–Shakarchi《Complex Analysis》 | 流畅现代、图文并茂、习题精炼 | 严格、直观兼顾 | 想要「Princeton 风」清新教材者 |

**读 Conway 的正确姿势**:重点不是算题(钟玉泉够算),也不是追几何灵感(那是 Ahlfors),
而是**搭一座能自洽运转的理论大厦**——特别留意 Conway 三大招牌:① 幂级数优先定义解析性
(第 2 章);② 正规族证 Riemann 映射(第 7 章);③ Runge 定理与 Mittag-Leffler 的近似观
(第 8 章)。读懂 Conway,你就握住了现代复分析的「工程蓝图」。

---

## §1 全书 8 章骨架一览(飞腾锚点分布)

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
| 1 | 复数系(域/共轭/球面/拓扑) | 复数域、代数封闭、Riemann 球面、弦度量、连通性 | **GEMM 9.45G[Lab05]** |
| 2 | 复函数的解析性 | 幂级数、Cauchy–Riemann、全纯、初等函数、支割线 | **分支预测[Lab02]** |
| 3 | 亚纯函数与奇点 | 线积分、Goursat、Cauchy 定理/公式、Laurent、留数、幅角原理 | **UDOT 16.9×[E05]** |
| 4 | 调和函数 | 中值性质、Poisson 核、Schwarz 反射、Harnack、Dirichlet、次调和 | **Schmidt 正交化** |
| 5 | 解析延拓与全纯覆盖 | 延拓、单值性定理、γ 函数、Riemann ζ、覆盖面 | **TLB 4.81×[E04]** |
| 6 | 共形映射 | Möbius、Schwarz 引理、Riemann 映射、Schwarz–Christoffel、整函数增长 | **matmul 15×[V03]** |
| 7 | 正规族与 Riemann 映射证明 | Ascoli–Arzelà、Montel 定理、Riemann 映射严格证、Hurwitz | **FP16 3.81×[L01]** |
| 8 | Runge 定理与近似 | 多项式/有理近似、射线、Mittag-Leffler、Weierstrass 因子分解 | **Iron Law<2%[Lab00]** |

---

### 第 1 章 · 复数系(域/共轭/球面/拓扑)

- **核心**:本章把 $\mathbb{C}$ 建成**代数封闭域**并赋予几何与拓扑。线索是:
  $\mathbb{R}\,[i]/(i^2+1)$ $\to$ 复数域 $\mathbb{C}=\{x+iy\}$ $\to$ 定义共轭 $\bar z$、
  模 $|z|$、极式 $z=re^{i\theta}$(幅角 $\theta$ 多值)。关键一跃是**球面表示**:球极投影
  把平面紧化,补进唯一 $\infty$,得 Riemann 球面 $\hat{\mathbb{C}}=\mathbb{C}\cup\{\infty\}$,
  并用**弦度量**(chordal metric)度量球面距离。章末铺设点集拓扑:开闭集、连通集、曲线(路径)、
  单连通区域的直觉——为第 3 章 Cauchy 定理的同伦版备好舞台。Conway 把域、几何、拓扑三件
  事讲得干净利落,是全书「地基」。
- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— 复数域 $\mathbb{C}$ 是二维实向量空间,复数乘法
  $(a+bi)(c+di)$ 等价于实 $2\times2$ 矩阵 $\begin{pmatrix}a&-b\\b&a\end{pmatrix}$ 的乘法,
  共轭即转置,模即矩阵行列式的平方根。
  🟢事实:复运算在飞腾上以 GEMM 高吞吐批量执行,FFT/DFT 的复蝶形运算底层正是此类矩阵乘。
  🟡类比:把 $\mathbb{C}$ 当作「带旋转的二维网格」,矩阵乘就是它的硬件化身。
- **关键定理**:**代数基本定理**(在此陈述,严格证明留待第 3 章 Liouville 定理):任意非常数
  复系数多项式 $p(z)$ 在 $\mathbb{C}$ 中有根,等价地 $\mathbb{C}$ 是**代数封闭域**——它保证
  复数域「大小刚好」,既不再扩张也不缺根。
- **Conway 特色**:本章把域代数、球面几何、点集拓扑**三件事一次性铺好**——多数教材把它们
  散落到不同章,Conway 却让第 1 章成为后续一切的地基:弦度量让 $\hat{\mathbb C}$ 成自然度量
  空间,连通性/曲线定义直接喂给第 3 章的同伦版 Cauchy 定理。这种「地基先行」是 Conway 系统
  感的源头,也是它比 Ahlfors(几何叙事)更利落之处。
- **自测**:① 求方程 $z^5=1$ 的全部根(5 次单位根),并写出它们在单位圆上的位置。
  ② 证明平行四边形恒等式 $|z+w|^2+|z-w|^2=2(|z|^2+|w|^2)$。
  ③ 在弦度量下,$z$ 与 $1/\bar z$ 是否为 Riemann 球面上的对径点?简述理由。

---

### 第 2 章 · 复函数的解析性(幂级数/全纯/Cauchy–Riemann/初等函数)

- **核心**:Conway 的招牌是**幂级数优先**:先严格定义幂级数 $\sum a_n(z-a)^n$ 与收敛半径
  (根值法/比值法),再称在其收敛盘内级数和为「解析」(analytic)。随后证明解析 $\Leftrightarrow$
  复可导(全纯 holomorphic)$\Leftrightarrow$ 满足 **Cauchy–Riemann 方程**
  $\dfrac{\partial f}{\partial\bar z}=0$(即 $u_x=v_y,\ u_y=-v_x$)。初等函数悉数登场:
  $e^z$、$\sin z$、$\cos z$、双曲函数,以及难点——**多值函数** $\log z$(因 $e^z$ 以
  $2\pi i$ 为周期,$\log$ 有无穷多值)、幂 $z^\alpha=e^{\alpha\log z}$。为取单值须切
  **支割线**(branch cut),这把幅角的多值性正式化为「选一支」的操作。
- **飞腾锚点**:**分支预测[Lab02]** —— 多值函数沿不同路径落到不同「叶」($\log z$ 绕原点
  一圈值增 $2\pi i$),取单值须判断路径是否绕过支点并选定幅角区间,正如分支预测器根据
  「历史」(绕支点的圈数/幅角累积)预判走哪一叶 Riemann 面。
  🟢事实:数值库实现 `clog` 时须显式选主值支(Arg ∈ $(-\pi,\pi]$),这是确定性的分支选择。
  🟡类比:支割线 = 流水线的「预定出口」,绕支点圈数 = 分支历史寄存器。
- **关键定理**:**Cauchy–Riemann 方程**——设 $f=u+iv$ 在开集 $\Omega$ 上有偏导,则 $f$ 全纯
  当且仅当
  $$\frac{\partial f}{\partial\bar z}=0\quad\Longleftrightarrow\quad u_x=v_y,\ \ u_y=-v_x$$
  这是「复可导一次即强约束」的微分化身,把 $f$ 的实虚部焊成一对调和共轭。
- **Conway 特色**:**幂级数优先**是 Conway 的招牌起手式——多数教材先定义「复可导」再证其等
  价于幂级数,Conway 反过来先立幂级数(纯代数/分析对象)再推出 Cauchy–Riemann,逻辑链条更
  短、更少依赖几何直觉。这让 $\dfrac{\partial f}{\partial\bar z}$ 算子自然登场,为后续全纯
  性的代数刻画铺路。
- **自测**:① 求主值 $\mathrm{Log}(-1)$ 及其全部值。
  ② 验证 $f(z)=e^z$ 满足 Cauchy–Riemann 方程。
  ③ 设 $f(z)=\bar z$,它处处不满足 Cauchy–Riemann 方程,试从「$\partial f/\partial\bar z$」
    的角度解释它为何「最反全纯」。

---

### 第 3 章 · 亚纯函数与奇点(积分/Cauchy 定理/Cauchy 公式/留数/幅角原理)

- **核心**:全书**计算引擎**。从路径(弧段)与线积分 $\int_\gamma f\,dz$ 起步,给出 Conway
  的招牌——**Goursat 定理**:对三角形 $T$,若 $f$ 全纯则 $\oint_{\partial T}f=0$,
  **且不假设 $f'$ 连续**(Goursat 的天才在于用细分绕过 $f'$ 的连续性)。由此推出 Cauchy
  定理(同伦版:$\gamma$ 在 $\Omega$ 内可缩则 $\oint_\gamma f=0$)与 **Cauchy 积分公式**
  $f(z)=\dfrac1{2\pi i}\oint_\gamma\dfrac{f(\zeta)}{\zeta-z}\,d\zeta$。局部性质:全纯 $\Rightarrow$
  无穷次可导 $\Rightarrow$ 可展 Taylor 级数。奇点分类经 **Laurent 级数**完成(可去/极点/
  本性)。**留数定理**把闭路积分化为留数求和,$\mathrm{Res}(f,a)=a_{-1}$;**幅角原理**用
  $\oint f'/f$ 数零点。本章是 Conway 全书最具计算杀伤力的核心。
- **飞腾锚点**:**UDOT 16.9×[E05]** —— Cauchy 积分公式是核函数 $\dfrac1{\zeta-z}$ 沿边界对
  $f(\zeta)$ 的**点积累加**,$f(z)=\sum_\text{边界}\dfrac{f(\zeta)\,\Delta\zeta}{\zeta-z}/(2\pi i)$,
  UDOT(无符号点积,加速 16.9×)的「核 × 值 → 求和」引擎正是这种结构的硬件化身:用核加权
  一圈边界采样,就重构出内部值。
  🟢事实:Cauchy 核的离散卷积是 Galerkin/边界元方法的数学原语,与点积累加器结构同构。
- **关键定理**:**Cauchy 积分公式**——设 $f$ 在 $\Omega$ 全纯,$\gamma$ 在 $\Omega$ 内绕 $z$ 一周,
  则
  $$f(z)=\frac1{2\pi i}\oint_\gamma\frac{f(\zeta)}{\zeta-z}\,d\zeta,\qquad
    f^{(n)}(z)=\frac{n!}{2\pi i}\oint_\gamma\frac{f(\zeta)}{(\zeta-z)^{n+1}}\,d\zeta$$
  它宣告「边界值决定内部一切」,是「局部决定整体」最锋利的表述,并免费送出无穷次可导。
- **Conway 特色**:**Goursat 定理的细分证法**是 Conway 的另一招牌——它证明 Cauchy 定理时
  **不假设 $f'$ 连续**,而用对三角形的逐次四等分把积分模压向一点,绕过了「全纯 $\Rightarrow$
  $f'$ 连续」这一当时尚未证明的事实。这一严格处理让 Cauchy 理论的逻辑基石完全自洽,是 Conway
  比 Ahlfors(默认 $f'$ 连续)更严谨之处。
- **自测**:① 用 Cauchy 公式计算 $\displaystyle\oint_{|z|=2}\frac{e^z}{z-1}\,dz$。
  ② 判定 $z=0$ 是 $f(z)=\sin(1/z)$ 的何种奇点,并求 $\mathrm{Res}(f,0)$。
  ③ 用留数定理计算 $\displaystyle\int_0^{2\pi}\frac{d\theta}{5+3\cos\theta}$
    (提示:令 $z=e^{i\theta}$ 化为单位圆围道)。

---

### 第 4 章 · 调和函数(中值/反射/Harnack/Dirichlet/次调和)

- **核心**:Conway 独立成章的**调和函数理论**,这是它区别于多数教材的亮点。调和函数 $u$
  满足 $\Delta u=0$。由 Cauchy 公式直接导出**中值性质**(mean value property):$u(a)$ 等于其
  圆周均值;由此推出**最大模原理**($u$ 非常数则在内部取不到最值)。**Poisson 核**
  $P_r(\theta)$ 把边界值「调和延拓」到圆盘内,给出 **Dirichlet 问题**(给定边界求调和函数)
  在圆盘上的显式解。**Schwarz 反射原理**把上半平面调和函数对称延拓过实轴。**Harnack 定理**
  保证单调调和序列收敛仍调和。最后引入**次调和**(subharmonic)函数,它是位势论与复分析的
  通用上包络工具。本章把「全纯 $\to$ 调和」的对偶关系彻底展开。
- **飞腾锚点**:**Schmidt 正交化** —— 给定调和 $u$,用 Cauchy–Riemann 求**调和共轭** $v$
  ($v_y=u_x,\ v_x=-u_y$)使 $f=u+iv$ 全纯,本质是沿 $\{(z-a)^n\}$ 基做投影分解;Laurent 展开把
  $f$ 投到正负幂「基底」上,正如 Schmidt 正交化把向量分解到正交基。
  🟢事实:Poisson 核 $P_r(\theta)=\dfrac{1-r^2}{1-2r\cos\theta+r^2}$ 是「带通滤波器」,圆盘
  调和延拓 = 边界 Fourier 模式的正交投影,数值上是正交分解。
  🟡类比:调和共轭 = 为已知「实部坐标」补上「虚部坐标」使向量落到全纯子空间。
- **关键定理**:**中值性质 / Poisson 公式**——$u$ 在圆盘 $|z|<R$ 调和 $\Leftrightarrow$ 对
  $|a|<r<R$ 有
  $$u(a)=\frac1{2\pi}\int_0^{2\pi}u(a+re^{i\theta})\,d\theta$$
  圆盘上 Dirichlet 问题的解由 Poisson 积分 $u(re^{i\theta})=\dfrac1{2\pi}\int P_r(\theta-t)u(e^{it})dt$ 给出。
- **Conway 特色**:**独立成章的调和函数理论**是 Conway 区别于多数教材的标志。Ahlfors 把
  调和函数分散嵌入共形映射章,Gamelin 一笔带过;Conway 却用完整一章把 Poisson 核、Dirichlet
  问题、Harnack、次调和讲成一个自洽系统,并严格建立「全纯 $\leftrightarrow$ 调和」的对偶
  桥梁。这让读者第一次看清:复分析不只是「全纯函数的学问」,也是「二维位势论的学问」。
- **自测**:① 求 $u(x,y)=x^2-y^2$ 的一个调和共轭 $v$,并写出对应的全纯函数 $f=u+iv$。
  ② 用最大模原理说明:若 $u$ 在有界域 $\Omega$ 调和且连续到边界,则 $u$ 在边界取最大值。
  ③ 写出单位圆盘 Dirichlet 问题的 Poisson 积分解,并解释 $P_r(\theta)$ 为何是「低通滤波器」。

---

### 第 5 章 · 解析延拓与全纯覆盖(延拓/单值性/γ 函数/Riemann ζ)

- **核心**:本章揭示全纯函数是「**由局部种子沿路径生长的生命体**」。从一个全纯函数元
  (germ)出发,沿路径逐点**解析延拓**。核心是**单值性定理**(Monodromy Theorem):在
  **单连通**区域内,若函数可沿任意路径延拓且路径间的连续变形不改变结果,则延拓给出
  **单值**全纯函数——这解释了为何 $\sqrt{z}$ 在去掉负实轴的平面单值、在穿孔平面则多值。
  全纯覆盖面把多值性的「叶」几何化。两大经典函数压轴:**Euler $\Gamma$ 函数**
  ($\Gamma(z)=\int_0^\infty t^{z-1}e^{-t}dt$,满足 $\Gamma(z+1)=z\Gamma(z)$、反射公式
  $\Gamma(z)\Gamma(1-z)=\pi/\sin\pi z$)与 **Riemann $\zeta$ 函数**
  ($\zeta(s)=\sum n^{-s}$,延拓到 $\mathbb{C}\setminus\{1\}$,函数方程连接 $s$ 与 $1-s$)。
- **飞腾锚点**:**TLB 4.81×[E04]** —— 解析延拓把「局部地址」(germ 在一点的幂级数)翻译成
  「全局地址」(整个区域的函数值),正如 TLB(Translation Lookaside Buffer,提速 4.81×)把
  虚拟地址翻译成物理全局地址;单值性定理保证在单连通域内这张「地址翻译表」无歧义,正如
  TLB 命中即确定唯一物理页。
  🟢事实:幂级数系数(Cauchy 估计)是「局部地址编码」,延拓即沿路径查表外推。
  🟡类比:多值函数的 Riemann 面 = 多级页表,绕支点换页。
- **关键定理**:**单值性定理(Monodromy Theorem)**——设 $\Omega$ 单连通,$f$ 的全纯 germ 可
  沿 $\Omega$ 内任一路径解析延拓,则延拓与路径无关,得到 $\Omega$ 上唯一的单值全纯函数。
  意义:在「无洞」区域里,局部信息无歧义地决定全局函数。
- **自测**:① 证明 $\Gamma(n+1)=n!$(对正整数 $n$)。
  ② 解释 $\sqrt{z}$ 在 $\mathbb{C}\setminus\{0\}$ 上为何不能定义成单值全纯函数,而去掉
    一条射线(如负实轴)后却可以。
  ③ 用反射公式 $\Gamma(z)\Gamma(1-z)=\pi/\sin\pi z$ 求 $\Gamma(1/2)$ 的值。

---

### 第 6 章 · 共形映射(Möbius/Schwarz 引理/Riemann 映射/Schwarz–Christoffel)

- **核心**:共形映射(保角 + 保向)是「柔性几何」。最核心的一族是 **Möbius 变换**
  $w=\dfrac{az+b}{cz+d}$($ad-bc\ne0$):它把圆/直线映成圆/直线、保交叉比,且精确对应
  $2\times2$ 矩阵。**Schwarz 引理**(单位圆盘自映射固定原点则 $|f(z)|\le|z|$、$|f'(0)|\le1$)
  是刚性之源。**Riemann 映射定理**给出惊人结论:任意单连通真子区域都与单位圆盘共形等价
  (存在性证在第 7 章用正规族完成)。**Schwarz–Christoffel 公式**把上半平面共形映到多边形,
  是工程(翼型、电磁场、地下水)的实用工具。章末用**级(order)与型(type)**刻画整函数增长,
  并触及超越整函数的 Picard 现象。
- **飞腾锚点**:**matmul 15×[V03]** —— Möbius 变换 $w=\dfrac{az+b}{cz+d}$ 精确对应矩阵
  $\begin{pmatrix}a&b\\c&d\end{pmatrix}$,两个 Möbius 变换的复合 = 矩阵乘法(加速 15×),
  逆变换 = 逆矩阵;共形映射的代数骨架即线性代数。
  🟢事实:Möbius 群 $PSL(2,\mathbb{C})$ 是 $SL(2,\mathbb{C})$ 模中心,其群运算即矩阵乘,
  在计算机图形的齐次坐标变换中直接调用 GEMM。
  🟡类比:Schwarz 引理的「收缩」= 谱范数 $\le1$ 的矩阵约束,共形 = 保角的线性近似。
- **关键定理**:**Schwarz 引理**——设 $f:\mathbb{D}\to\mathbb{D}$ 全纯且 $f(0)=0$,则
  $|f(z)|\le|z|$ 且 $|f'(0)|\le1$;等号成立($\exists\,z\ne0:\ |f(z)|=|z|$)当且仅当
  $f(z)=e^{i\theta}z$ 为旋转。它是「双曲几何刚性」的源头,推出大量唯一性定理。
- **Conway 特色**:本章把 **Möbius 变换的代数分类**(用不动点/交叉比)、**Schwarz–Christoffel
  公式**(上半平面到多边形的显式共形映射)与**整函数增长**三块内容整合,体现 Conway「几何 +
  代数 + 渐近」并重的平衡感。Möbius 群 $PSL(2,\mathbb{C})$ 的矩阵化是后续共形几何与物理(相对
  论 Möbius 群、共形场论)的入口。
- **自测**:① 求 Möbius 变换把上半平面 $\mathrm{Im}\,z>0$ 映成单位圆 $|w|<1$。
  ② 用 Schwarz 引理说明:何时 $|f'(0)|=1$ 取等,并描述取等函数的形态。
  ③ 设 $w=\dfrac{az+b}{cz+d}$,$ad-bc\ne0$,证明它把圆/直线仍映成圆/直线(提示:化圆方程)。

---

### 第 7 章 · 正规族与 Riemann 映射定理的证明(Ascoli–Montel)

- **核心**:本章是 Conway 全书的**方法论招牌**。**正规族**(normal family)是函数空间中的
  「紧致性」概念:一族函数称为正规的,若其任一序列都有紧一致收敛子列。工具是
  **Ascoli–Arzelà 定理**(等度连续 + 一致有界 $\Rightarrow$ 紧)。**Montel 定理**是复分析
  的引擎:局部一致有界的全纯函数族必正规——即「有界 $\Rightarrow$ 紧」。由此 Conway 给出
  **Riemann 映射定理的现代严格证明**:取极值化泛函的有界单叶函数,用 Montel 抽子列,验证
  极限达到目标(满射到圆盘)。另含 **Hurwitz 定理**(单叶函数列的极限仍单叶),保障极限过程
  不破坏单叶性。这套「有界族必紧 + 极值论证」是现代分析的标准范式。
- **飞腾锚点**:**FP16 3.81×[L01]** —— Montel 定理的核心假设是**一致有界**(函数值落在固定
  范围内),有界即得紧致性,正如 FP16 的**有限动态范围**(指数仅 5 位)天然约束了数值的「上
  界」——任何 FP16 计算都在一个固定带内,「有界」是它与生俱来的属性;有界族抽子列如同在有
  限精度档位间收敛。
  🟢事实:FP16 的最大表示值 $\approx65504$ 是硬上界,Montel 的「一致有界」与之同构——有界
  即存在紧子列。
  🟡类比:等度连续 = 函数族的「Lipschitz 带宽」,与浮点精度的「有效位带宽」相呼应。
- **关键定理**:**Montel 定理**——设 $\mathcal{F}$ 是开集 $\Omega$ 上的全纯函数族,若 $\mathcal{F}$
  在 $\Omega$ 的每个紧子集上一致有界(局部有界),则 $\mathcal{F}$ 是正规族(任一序列有紧一致
  收敛子列)。它把「逐点有界」升级为「序列紧」,是 Riemann 映射证明的发动机。
- **Conway 特色**:**用正规族证明 Riemann 映射定理**是 Conway 全书最大的方法论招牌。Ahlfors
  用极值长度/几何论证,Gamelin 偏代数;Conway 则走「Montel 抽子列 + 极值泛函 + Hurwitz 保单叶」
  的现代标准路线,干净、可教、可推广。这套范式日后直接通向全纯动力系统(迭代收敛)与多复变
  分析,是研究生必须掌握的「通用招式」。
- **自测**:① 用 Montel 定理说明:单位圆盘上一致有界的全纯函数列必有紧一致收敛子列。
  ② 简述 Conway 用正规族证 Riemann 映射定理的两步:极值泛函的取法 + Montel 抽子列与满射验证。
  ③ 用 Hurwitz 定理说明:单叶全纯函数列的紧一致极限若非常数,则仍单叶。

---

### 第 8 章 · Runge 定理与近似(多项式/有理近似/Mittag-Leffler)

- **核心**:全书的「**近似观**」收束章。**Runge 定理**:紧集 $K$ 上的全纯函数可用极点在
  $K$ 外的有理函数一致逼近;若 $\mathbb{C}\setminus K$ 连通,更可用**多项式**逼近。它把
  「全纯」彻底翻译成「可被简单函数逼近」,是数值与函数论的核心。其推论与对偶是
  **Mittag-Leffler 定理**:可指定任意离散极点集与主部,构造出对应的亚纯函数(亚纯函数的
  「部分分式分解」)。**Weierstrass 因子分解定理**则按指定零点构造整函数(整函数的「乘积
  分解」)。三者合起来表明:全纯/亚纯/整函数的奇点结构可被任意预设且函数唯一确定。章末触及
  **Picard 定理**(大 Picard:本质奇点附近函数取至多一个例外值外的所有值)。
- **飞腾锚点**:**Iron Law<2%[Lab00]** —— Runge 定理的本质是「**误差可控的逼近**」:对任意
  $\epsilon>0$,存在多项式/有理函数 $p$ 使 $\sup_K|f-p|<\epsilon$,这正是 Iron Law(误差须
  $<2\%$)的数学原型——把复杂目标分解到「主项 + 可控余项」,每一步逼近误差都有明确上界。
  🟢事实:Runge/Mittag-Leffler 的存在性证明用「主部之和」,余项控制是数值收敛的保证;实际
  数值逼近(Chebyshev/Padé)的误差预算正是 Iron Law 的工程化身。
  🟡类比:部分分式 = 把函数拆成「素因子」之和,逼近 = 在有限预算内截断这个无穷和。
- **关键定理**:**Runge 定理**——设 $K\subset\mathbb{C}$ 紧,$f$ 在含 $K$ 的开集上全纯,则对
  任意 $\epsilon>0$,存在极点在 $\mathbb{C}\setminus K$ 指定集的有理函数 $r$ 使
  $\sup_K|f-r|<\epsilon$;若 $\mathbb{C}\setminus K$ 连通,可取 $r$ 为多项式。它是
  「全纯 = 可被多项式逼近」的严格化,把抽象函数拉回可计算世界。
- **Conway 特色**:**Runge + Mittag-Leffler + Weierstrass 三定理并立**是 Conway 收束章的精华——
  Runge 管「逼近」(指定紧集上)、Mittag-Leffler 管「亚纯重构」(指定极点与主部)、Weierstrass
  管「整函数构造」(指定零点)。三者合奏表明:全纯世界的奇点结构可被任意预设,函数则由这些
  预设唯一决定。这是「结构决定函数」哲学的集大成,也是通向多复变与解析数论的桥梁。
- **自测**:① 用 Runge 定理说明:$\dfrac1{z-a}$($a\notin K$)在紧集 $K$ 上可用极点在 $a$
    同一连通分支的有理函数逼近。
  ② 写出 $\cot z$ 的 Mittag-Leffler 部分分式展开(主部为 $\dfrac1{z-n\pi}$)。
  ③ Runge 定理中「$\mathbb{C}\setminus K$ 连通」这一条件若去掉,为何多项式逼近可能失败?
    举一个反例思路。

---

## §9 全书思想主线

Conway 全书贯穿三条主线,层层递进、环环相扣。

**主线一·从局部到整体**:第 2 章幂级数定义「局部解析」,第 3 章 Cauchy 公式宣告「边界决定
内部」,第 5 章单值性定理保证「局部种子在无洞区域长成唯一全局函数」——全纯函数是被一个
局部 germ 完全决定的生命体。这是 Conway 系统大厦的主梁。

**主线二·有界即紧(正规族范式)**:第 6 章 Schwarz 引理给出「有界 $\Rightarrow$ 刚性」,
第 7 章 Montel 定理升级为「有界 $\Rightarrow$ 序列紧」,二者合力推出 Riemann 映射定理。
这套「有界 $\Rightarrow$ 紧 $\Rightarrow$ 极值可达」是现代分析的标准论证范式,是 Conway 区别
于古典教材的方法论核心。

**主线三·近似与分解**:第 4 章用 Poisson 核把边界值调和延拓(一种逼近),第 8 章 Runge 定理
把全纯函数逼成多项式、Mittag-Leffler 按指定极点重构亚纯函数——全纯世界的结构可被「简单
函数」任意逼近与分解。

三条主线在 Picard 定理会合:本质奇点的「取遍几乎所有值」既是局部奇性的极致(主线一),又
受整函数增长级约束(主线三),而其证明常借助正规族的紧性论证(主线二)。与已读教材呼应:
Ahlfors 给了同一批定理的几何图像,Gamelin 给了代数工具,钟玉泉给了计算训练——Conway 补上
了它们都欠缺的「**自洽系统骨架与现代论证范式**」。

---

## §10 与本仓库其他笔记的交叉引用

- **与 Ahlfors《Complex Analysis》对比**:同一批定理,两种气质。Ahlfors 用球面图景与解析
  延拓的几何图像讲故事,Conway 用幂级数与正规族的公理化框架建系统。建议 Ahlfors 当「地图」
  建直觉、Conway 当「蓝图」搭骨架。(本文件:`ahlfors_复分析_快速逐章.md`)
- **与 Gamelin《Complex Analysis》对比**:Gamelin 早引入 Riemann 面、层论等代数工具,适合
  工程导向;Conway 在第 5 章才触及覆盖面,更循序渐进。Conway 的调和函数专章是 Gamelin 所
  略。两本都是「现代味」,Conway 更平衡、Gamelin 更抽象。(本文件:`复分析_快速逐章.md`)
- **与钟玉泉《复变函数论》对比**:钟玉泉计算详尽、贴近中文考试,适合刷题熟练留数与积分;
  Conway 计算克制但证明骨架完整、Runge/Montel 全景为钟玉泉所无。先 Conway 搭架、后钟玉泉
  练手,互补无冗余。(本文件:`复变函数入门_快速逐章.md`)
- **与 Rudin《Real and Complex Analysis》对比**:Rudin 用测度论统一实分析与复分析,把 Cauchy
  公式嵌入 $H^p$ 空间与测度框架,泛函味浓;Conway 走「纯复」路线,先不引入测度,更利于
  建立复分析的独立直觉。读完 Conway 再读 Rudin 实复分析,可把「边界决定内部」与「测度决定
  积分」两种「整体决定」哲学缝合。(本仓库已精读:`rudin_real_complex_快速逐章.md`)
- **延伸阅读**:Stein–Shakarchi《Complex Analysis》——Princeton 教材,图文并茂、习题精炼,
  风格介于 Ahlfors(直觉)与 Conway(系统)之间,适合作为 Conway 的「友好对照本」。
