# Hartshorne《代数几何》(GTM52) · 快速逐章精读

> 基于原书:`Algebraic Geometry`, GTM 52 (Robin Hartshorne, 1977, Springer) / 读于:2026-07-02
> 定位:**现代概形代数几何圣经**,Grothendieck 概形理论的权威教科书,最难自学书之一。
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言:Hartshorne 是什么,为什么读它

Robin Hartshorne 的《Algebraic Geometry》(GTM 52, 1977) 是**现代概形代数几何的圣经**,也是 Grothendieck 概形理论最权威的教科书。
Hartshorne 用五章带读者走完一条语言升级之路:先在第 1 章用经典「代数簇」(多项式方程的零点集)建立几何直觉,
再在第 2 章把这些簇「升级」为概形($\mathrm{Spec}\,R$ 配上结构层 $\mathcal{O}_X$),第 3 章用凝聚层上同调 $H^i(X,\mathcal{F})$ 制造计算工具,
第 4-5 章用 Riemann-Roch 定理完成曲线与曲面的双有理分类。顶峰是 Serre 对偶定理与 Riemann-Roch 定理。

**这是数学里最难自学的书之一**。它需要充分前置:抽象代数(群环域)、交换代数(理想、局部化、Noether 环——本仓库已读 Atiyah-MacDonald)、
同调代数(导出函子、$\mathrm{Ext}$、谱序列——本仓库已读 Weibel)、点集拓扑。本仓库还读了 Lang 代数与 Mac Lane 范畴论。
Hartshorne 是这些工具的**几何综合**:交换代数变成「仿射概形的局部坐标」,同调代数变成「度量几何对象缺失信息的尺子」。

**读它的意义**:现代代数数论的两大顶峰——Wiles 证明费马大定理(用椭圆曲线 + 概形)、算术几何的 Langlands 纲领——
都建立在这本书的地基上;几何表示论、模空间理论、镜像对称也都以概形语言为母语。

对比四本主流教材:

| 书 | 风格 | 严格性 | 适合谁 |
|---|---|---|---|
| **Hartshorne (GTM52, 1977)** | 高度浓缩、习题即正文、抽象到顶,5 章直奔概形+上同调 | ★★★★★ | 有交换代数+同调代数底子、立志走代数数论/几何方向者 |
| **Shafarevich《基础代数几何》** | 经典簇语言起手、几何图画得足、叙事温柔,两卷 | ★★★★ | 先用它建直觉,再攻 Hartshorne |
| **Ravi Vakil《The Rising Sea/FOOTPRINTS》** | 对话式、层层铺垫、800+ 页处处讲动机,讲义体 | ★★★★☆ | 自学首选,把 Hartshorne 每个跳跃都补上 |
| **Qing Liu《代数几何与算术曲线》** | 直接走算术概形、含非代数闭域与 $\mathrm{Spec}\,\mathbb{Z}$ | ★★★★ | 想做数论方向、关心算术曲线者 |

**「如何不死在 Hartshorne 上」**:绝不裸读。先用 Shafarevich 第 1 卷或 Vakil 讲义把第 1 章的簇直觉和第 2 章的层语言吃透,再进 Hartshorne 的习题地狱。
Hartshorne 的习题占了全书信息量的至少一半,「只读定理不刷题」等于没读。

---

## §1 全书 5 章 + 附录骨架一览(飞腾锚点分布)

| 章 | 标题 | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| **Ch1** | Varieties 代数簇 | 仿射/射影簇、Nullstellensatz、非异点、完全交 | **matmul 15×[V03]** |
| **Ch2** | Schemes 概形 | 层、$\mathrm{Spec}\,R$、分离/真、Kähler 微分 | **TLB 4.81×[E04]** ⭐主力 |
| **Ch3** | Cohomology 上同调 | 层上同调、Čech、Serre 对偶、Riemann-Roch | **Schmidt 正交化** |
| **Ch4** | Curves 曲线 | 亏格、RR 曲线、椭圆曲线群律、Hurwitz | **FP16 3.81×[L01]** |
| **Ch5** | Surfaces 曲面 | 相交数 $(C.D)$、RR 曲面、K3、极小模型 | **UDOT 16.9×[E05]** |
| **附录A** | 同调代数 | 导出函子、$\mathrm{Ext}$、谱序列速览 | **GEMM 9.45G[Lab05]** |
| **附录B** | 超越方法 | GAGA 证明、Stein 簇、解析拓扑 | **Iron Law<2%[Lab00]** |
| **附录C** | 计算工具 | Gröbner 基等计算专题(略) | 分支预测[Lab02] |

**阅读路径建议**:Ch1(直觉)→ Ch2(语言升级,最劝退,务必配 Vakil)→ Ch3(计算引擎)→ Ch4(分类样板)→ Ch5(分类进阶)。
附录 A 随时回查(与 Weibel 互参),附录 B 在读 Ch3 GAGA 时回看。**切勿跳过习题**:Hartshorne 习题 III.4-III.5、IV.1、IV.4 是全书精华。

**难度分布**:Ch1 ★★★(经典,重直觉)、Ch2 ★★★★★(抽象跳升,劝退高发)、Ch3 ★★★★(技术密集)、Ch4 ★★★(Ch3 后较顺)、Ch5 ★★★★(相交理论需练手)。

---

### 第 1 章 · Varieties(代数簇)

- **核心**:第 1 章用「经典语言」打开代数几何——一个代数簇就是一组多项式方程的公共零点集 $V(I)\subseteq\mathbb{A}^n$。
  Hilbert 零点定理把几何(簇)与代数(理想)焊死;$V$ 与 $I$ 是一对 Galois 联系。
  每个仿射簇配一个坐标环 $A(Y)=k[x_1,\dots,x_n]/I(Y)$,仿射簇的全部几何都编码在这环里(态射 ↔ 环同态)。
  射影簇搬到 $\mathbb{P}^n$ 上,配齐次理想与分次坐标环 $S(Y)$;射影簇必紧(完备,complete)。
  接着定义正则函数(处处局部为分式)、态射、有理函数域 $K(Y)$;用 Jacobi 矩阵判别非异点(光滑点);
  二次/三次曲线曲面给出大量「看得见」的例子。函数域维数 $\dim Y=\mathrm{tr.deg}_k K(Y)$。
  这一章是后面概形抽象的**几何地基**,务必先在这里积累直觉。

- **各节速览**:
  - I.1 仿射簇:$V(I)$、$I(Y)$、坐标环、Zariski 拓扑。
  - I.2 射影簇:$\mathbb{P}^n$、齐次化、分次环、射影 Nullstellensatz。
  - I.3 态射:正则函数、同构、坐标环同态。
  - I.4 有理函数:函数域 $K(Y)$、有理映射、双有理等价。
  - I.5 非异簇:切空间、Jacobi 判据、光滑点集开且稠。
  - I.6 非异曲线:DVR、局部环是赋值环。
  - I.7-8 相交维数、完全交、代数簇的合理性判据。
  - I.9-13 二次/三次曲面、扭三次曲线、分类实例。

- **飞腾锚点**:**matmul 15×[V03]** —— 射影空间 $\mathbb{P}^n$ 用齐次坐标 $[x_0:\dots:x_n]$,射影变换/非齐次化/双有理变换都是矩阵作用。
  - 🟢事实:3D 渲染管线的投影矩阵就是 $\mathbb{P}^3$ 齐次坐标变换(齐次除法还原);坐标环 $A(Y)$ 是对簇点的「矩阵化代数编码」。
  - 🟡类比:齐次坐标多塞一个 $x_0$ 当「缩放缓冲」,恰似 matmul 把点坐标批量线性变换;射影变换群 $PGL_{n+1}$ 作用 = 可逆矩阵作用模标量。

- **关键定理**:**Hilbert 零点定理(Nullstellensatz)**($k=\bar{k}$):
  $$I(V(J))=\sqrt{J},\qquad V(J)=\emptyset\;\Longleftrightarrow\;1\in J$$
  弱形式(空集 ⟺ 理想含 1),强形式(取零点再还原 = 取根式)。这是「几何 ↔ 代数字典」的总开关,后面所有翻译都靠它。

- **自测**:
  1. 在 $\mathbb{A}^2_{\mathbb{R}}$ 与 $\mathbb{A}^2_{\mathbb{C}}$ 上分别画出 $V(y^2-x^3)$;用 Jacobi 判据指出尖点 $(0,0)$ 是奇点。
  2. 扭三次曲线(twisted cubic)$C=\{(t,t^2,t^3)\}\subseteq\mathbb{A}^3$,证明 $I(C)=(y-x^2,\,z-x^3)$,并判断 $C$ 是否为完全交(complete intersection)。
  3. 求 $V(x^2+y^2+z^2-1)\subseteq\mathbb{P}^2_{\mathbb{C}}$ 的维数与次数,并说明它 $\cong\mathbb{P}^1$。

---

### 第 2 章 · Schemes(概形)

- **核心**:第 2 章完成「语言升级」——把簇推广为概形。先定义**层**(sheaf):给每个开集 $U$ 配一个 $\mathcal{F}(U)$(局部数据),
  满足粘合公理(局部一致即可拼成全局)。**仿射概形** $\mathrm{Spec}\,R$ 以素理想集合为底,赋予 Zariski 拓扑(闭集 = $V(I)$),
  再装上结构层 $\mathcal{O}_{\mathrm{Spec}\,R}$,其茎(stalk)$\mathcal{O}_{X,\mathfrak{p}}\cong R_{\mathfrak{p}}$(局部化)。
  **概形** = 局部同胚于某 $\mathrm{Spec}\,R$ 的局部环空间。随后区分既约(reduced,无幂零)、正规(normal,整闭)、既约不可约(integral);
  用对角态射定义**分离**(separated,= Hausdorff 的代数版本)与**真**(proper,= 紧致的代数版本)。
  凝聚层(quasi-coherent / coherent)是概形上「好」的层;**除子**(Cartier / Weil)刻画函数的零极点。
  Kähler 微分 $\Omega_{X/Y}$ 给出导子的通用对象,是非异性的代数判据。这一章抽象度跳升,是全书最劝退的关口。

- **各节速览**:
  - II.1 层:预层、层、层化、茎。
  - II.2 概形:$\mathrm{Spec}\,R$、结构层、概形定义。
  - II.3 基本性质:既约、不可约、整、Noether、维数。
  - II.4 分离与真:对角态射、真映射(紧的代数化)。
  - II.5 模层:拟凝聚、凝聚层,仿射上 $\widetilde{M}$。
  - II.6 除子:Cartier 除子(局部方程)与 Weil 除子(余维 1 子簇)。
  - II.7 射影空间:$\mathcal{O}(1)$、扭转层、$\mathrm{Proj}$ 构造。
  - II.8 微分:$\Omega_{X/Y}$、Kähler 微分、光滑/非分歧判据。

- **飞腾锚点**:**TLB 4.81×[E04]** ⭐本章主力 —— 概形的核心是**局部性**:茎(stalk)= 一个点的局部数据,
  仿射开覆盖给局部坐标,$\mathrm{Spec}\,R$ 按素理想分层。这与 TLB「靠局部性提速」同构。
  - 🟢事实:CPU 的 TLB 缓存页表,把虚拟地址的局部翻译加速 4.81×;层把全局问题切片成茎的局部问题,再粘合。
  - 🟡类比:地址翻译切片成页(局部)再拼全局地址,正如层用开覆盖的局部截面拼全局截面;仿射开覆盖 = 页表。

- **关键定理**:**仿射全局截面定理**:对仿射概形 $X=\mathrm{Spec}\,R$,
  $$\Gamma(X,\mathcal{O}_X)\cong R,\qquad \mathcal{O}_{X,\mathfrak{p}}\cong R_{\mathfrak{p}}$$
  即「仿射概形 = 环的忠实几何镜像」,全局截面能完整复原环。非仿射概形才有「真正丢失的全局信息」(由上同调度量)。

- **自测**:
  1. $\mathrm{Spec}\,k[x,y]/(xy)$ 是否既约?是否不可约?画出它的素理想示意图(两条坐标轴相交)。
  2. $\mathrm{Spec}\,\mathbb{Z}$ 有多少个闭点?其泛点(generic point)对应哪个素理想?
  3. 验证态射 $\mathbb{A}^1_k\to\mathrm{Spec}\,k$ 是分离且真的;而 $\mathbb{A}^1_k\to\mathbb{A}^1_k$ 的开浸入是真的吗?

---

### 第 3 章 · Cohomology(凝聚层上同调)

- **核心**:第 3 章制造「计算工具」。整体截面函子 $\Gamma(X,-)$ 左正合不右正合,其右导出函子就是层上同调 $H^i(X,\mathcal{F})=R^i\Gamma$。
  **Čech 上同调**用开覆盖 $\{U_i\}$ 的交错复形 $\check{C}^\bullet(\mathfrak{U},\mathcal{F})$ 计算,在仿射开覆盖下与导出函子上同调一致(Leray 定理)。
  **Serre 仿射消失定理**:仿射概形上凝聚层的 $H^i=0\,(i>0)$——这是「仿射 = 无上同调障碍」的判据(逆也成立,Serre 判据)。
  接着有限性定理(射影簇上凝聚层上同调是有限维 $k$-向量空间)、**Hilbert 多项式**($\chi(\mathcal{F}(n))$ 是 $n$ 的多项式,给出维数与次数)。
  **GAGA**(Serre)说:复数域上,代数凝聚层 = 解析凝聚层,且上同调同构。
  **Serre 对偶定理**给出 $H^i\leftrightarrow H^{n-i}$ 的对偶(用典范层 $\omega_X$)。顶峰 **Riemann-Roch 定理**把 Euler 示性数 $\chi(\mathcal{F})$ 表为相交数。
  这一章是抽象到计算的桥梁,也是后两章分类的发动机。

- **各节速览**:
  - III.1 导出函子回顾:内射分解、右导出 $R^iF$。
  - III.2 层上同调:$\Gamma$ 左正合,$H^i=R^i\Gamma$。
  - III.3 Čech 上同调:交错复形、与导出函子一致。
  - III.4 仿射消失定理(Serre):仿射 + 凝聚 ⟹ $H^{>0}=0$。
  - III.5 有限性:射影簇上 $H^i$ 有限维。
  - III.6 Hilbert 多项式:$\chi(\mathcal{F}(n))$ 多项式,给 $\dim/\deg$。
  - III.7 GAGA:代数层 ↔ 解析层范畴等价。
  - III.8 Serre 对偶:$H^i\cong H^{n-i}(\,\cdot^\vee\otimes\omega_X)^\vee$。
  - III.9 Riemann-Roch:Euler 示性数 = 相交多项式。

- **飞腾锚点**:**Schmidt 正交化** —— Serre 对偶把 $H^i(X,\mathcal{F})$ 对偶到 $H^{n-i}(X,\mathcal{F}^\vee\otimes\omega_X)^\vee$,
  是「配对/投影」的极致,如 Schmidt 正交化把向量投到正交补。
  - 🟢事实:Serre 对偶给出维数相等 $\dim H^i=\dim H^{n-i}$,迹映射 $H^n(\omega_X)\cong k$ 是「内积」。
  - 🟡类比:典范层 $\omega_X$ 扮演「内积/度量」的角色,让上同调群两两对偶;Schmidt 正交化用内积找正交基,Serre 对偶用 $\omega_X$ 找对偶群。

- **关键定理**:**Serre 对偶定理**(射影 $n$ 维光滑簇 $X$ 上凝聚层 $\mathcal{F}$):
  $$H^i(X,\mathcal{F})\;\cong\;H^{n-i}(X,\,\mathcal{F}^\vee\otimes\omega_X)^\vee$$
  其中 $\omega_X=\Omega^n_X$ 是典范层(余切层最高次楔幂)。当 $i=0$ 给出 $\Gamma(\mathcal{F})\cong\mathrm{Ext}^{n}(\mathcal{F},\omega_X)^\vee$。

- **自测**:
  1. 计算 $H^0(\mathbb{P}^1,\mathcal{O}(d))$ 与 $H^1(\mathbb{P}^1,\mathcal{O}(d))$ 对所有 $d\in\mathbb{Z}$,验证 $\chi(\mathcal{O}(d))=d+1$。
  2. 写出 Hilbert 多项式为什么能同时给出 $\dim X$ 与 $\deg X$(提示:首项系数)。
  3. GAGA 在什么意义上让你「用解析方法算代数上同调」?为何这对**仿射**簇不成立?

---

### 第 4 章 · Curves(代数曲线)

- **核心**:第 4 章是「分类成就」之一:用第 3 章工具完成光滑射影曲线的双有理分类。核心是曲线的 Riemann-Roch 定理。
  对除子 $D$ 与典范除子 $K_C$,$\ell(D)-\ell(K_C-D)=\deg D+1-g(C)$,其中 $g(C)=\ell(K_C)$ 是**亏格**(genus,拓扑洞数)。
  亏格是双有理不变量,把曲线分成三大类:$g=0$(有理曲线 $\cong\mathbb{P}^1$)、$g=1$(椭圆曲线)、$g\geq2$(一般曲线)。
  **Hurwitz 定理**给出覆盖的分歧公式 $2g(C)-2=\deg f\cdot(2g(C')-2)+\sum(e_P-1)$。
  $g=1$ 的椭圆曲线最精彩:Weierstrass 方程 $y^2=x^3+ax+b$(判别式 $\Delta\neq0$),其上的点构成一个 Abel 群
  (群律由「三点共线 ⟺ 相加为零」定义),这是密码学椭圆曲线(ECC)的数学源头。
  **典范嵌入**把非超椭圆曲线嵌入 $\mathbb{P}^{g-1}$;超椭圆曲线则是 $\mathbb{P}^1$ 的二重覆盖。

- **各节速览**:
  - IV.1 曲线的 Riemann-Roch:$\ell(D)-\ell(K_C-D)=\deg D+1-g$。
  - IV.2 Hurwitz 定理:分歧公式,Riemann-Hurwitz。
  - IV.3 曲线的嵌入:很丰除子给出嵌入,超椭圆判据。
  - IV.4 椭圆曲线:Weierstrass 方程、群律、$j$-不变量。
  - IV.5 典范嵌入:非超椭圆曲线 $\hookrightarrow\mathbb{P}^{g-1}$。
  - IV.6 分类:亏格 $g$ 的曲线模空间 $\mathcal{M}_g$(维数 $3g-3$)。

- **飞腾锚点**:**FP16 3.81×[L01]** —— 椭圆曲线上点的加法需要域运算(求逆、模逆),有限域 $\mathbb{F}_p$ 上椭圆曲线点乘是密码学核心,
  低精度运算天然适合 FP16 吞吐。
  - 🟢事实:椭圆曲线密码(ECC)的点加/倍点公式用有限域乘法 + 求逆,FP16 的 3.81× 吞吐直接加速批量点运算。
  - 🟡类比:群律「过两点的第三交点取负」是一组确定的多项式公式,适合流水线低精度计算;点乘 $nP$ = 反复加法,可 Montgomery 阶梯并行。

- **关键定理**:**Riemann-Roch 定理(曲线版)**:光滑射影曲线 $C$ 亏格 $g(C)$,除子 $D$:
  $$\ell(D)-\ell(K_C-D)=\deg D+1-g(C)$$
  取 $D=K_C$ 得 $\ell(K_C)=g$;取 $D=0$ 得 $\ell(0)=1$。当 $\deg D>2g-2$ 时 $\ell(K_C-D)=0$,故 $\ell(D)=\deg D+1-g$。

- **自测**:
  1. 对椭圆曲线 $C:y^2=x^3-x$ 在 $\mathbb{C}$ 上,验证 $g(C)=1$,并求典范除子 $K_C$ 的次数。
  2. 用群律在 $C:y^2=x^3+7$ 上,设 $P=(1,2)$,计算 $P+P=2P$(倍点公式)。
  3. Hurwitz:求 $\mathbb{P}^1\to\mathbb{P}^1$ 的 $d$ 重覆盖的分歧下界(Riemann-Hurwitz 给出 $\sum(e_P-1)\geq 2d-2$)。

---

### 第 5 章 · Surfaces(代数曲面)

- **核心**:第 5 章把分类推到二维——光滑射影曲面。核心是**相交理论**:两个除子 $C,D$ 的相交数 $(C.D)\in\mathbb{Z}$,
  是个双线性配对,$(C.D)=\deg(\mathcal{O}_X(C)\otimes\mathcal{O}_X(D))$。
  **爆破**(blow-up)在某点插入例外除子 $E$,满足 $E^2=(E.E)=-1$(Castelnuovo);$-1$ 曲线正是「可以被收缩」的曲线。
  曲面的 Riemann-Roch(Noether 形式):$\chi(\mathcal{O}_X(D))=\tfrac12 D(D-K_X)+\chi(\mathcal{O}_X)$,
  且 Noether 公式 $\chi(\mathcal{O}_X)=\tfrac1{12}(K_X^2+e(X))$。
  按 Kodaira 维数 $\kappa$ 与双有理等价类分类:**有理曲面**($\cong\mathbb{P}^2$ 的双有理像)、**直纹曲面**($\mathbb{P}^1$ 丛)、
  **K3 曲面**($K_X=0$,$\pi_1=0$,模空间 20 维)、一般型($\kappa=2$)。
  **极小模型程序**(MMP)的目标:每个曲面双有理等价类有唯一极小模型(无 $-1$ 曲线)。这是高维极小模型纲领的二维样板。

- **各节速览**:
  - V.1 曲面上的几何:相交数 $(C.D)$、双线性、自交 $C^2$。
  - V.2 直纹曲面:$\mathbb{P}^1$ 丛,亏格 $g$ 不变量。
  - V.3 单点变换(爆破):例外除子 $E$,$E^2=-1$,Castelnuovo 收缩判据。
  - V.4 曲面 Riemann-Roch:Noether 公式,统一代数 + 几何 + 拓扑。
  - V.5 有理曲面:$\mathbb{P}^2$ 及其爆破,极小模型 $\mathbb{P}^2$ 或 Hirzebruch 面 $\mathbb{F}_n$。

- **飞腾锚点**:**UDOT 16.9×[E05]** —— 相交数 $(C.D)$ 是「点积累加」:两条曲线在曲面上交于有限个点,
  计重数求和,恰如 UDOT(点积)把成对元素乘后累加。
  - 🟢事实:相交数定义为局部相交重数之和 $\sum_p (C\cdot D)_p$,是离散点积;UDOT 的乘加流水线 16.9× 直接对应批量计算。
  - 🟡类比:UDOT 把 $(C\cdot D)$ 的逐点贡献高效累加;$H^0$ 维数(有效除子空间)= 点积后的「强度」度量。

- **关键定理**:**Riemann-Roch 定理(曲面版,Noether)**:光滑射影曲面 $X$ 上除子 $D$:
  $$\chi(\mathcal{O}_X(D))=\frac12 D(D-K_X)+\chi(\mathcal{O}_X),\qquad \chi(\mathcal{O}_X)=\frac1{12}(K_X^2+e(X))$$
  其中 $e(X)=c_2(X)$ 是拓扑 Euler 示性数。这条把代数($D$)、几何($K_X$)、拓扑($e$)三者统一——是 Hartshorne 的「万物归一」时刻。

- **自测**:
  1. 在 $\mathbb{P}^2$ 上爆破一点得曲面 $X$,设 $E$ 为例外除子、$H$ 为某直线的拉回。计算 $E^2$、$(H.E)$、$H^2$。
  2. 证明 $E$ 是 $-1$ 曲线(Castelnuovo 判据:有理 + 自交 $-1$ ⟺ 可收缩)。
  3. K3 曲面满足 $K_X=0$,$e(X)=24$,推出其 $c_2=24$,与模空间维数 20 的关系。

---

### 附录 A · 同调代数(导出函子速览)

- **核心**:附录 A 给出第 3 章依赖的同调代数背景(与 Weibel 互补)。Abel 范畴(如 $R$-模范畴、凝聚层范畴)里,
  左正合函子 $F$ 的右导出函子 $R^iF$ 用内射分解定义;整体截面函子 $\Gamma$ 是左正合的,故 $H^i=R^i\Gamma$。
  $\mathrm{Ext}^i(M,N)$ 度量 $M$ 的扩张,$\mathrm{Tor}_i$ 度量张量的「非正合」。
  **谱序列**是把双复/滤过的同调逐页收敛到总同调的机器(「谱序列是同调代数的叶扇」),
  Čech → 导出函子的对比(Leray 谱序列)就靠它。这部分是 Weibel 第 2、3、5 章的浓缩版。

- **飞腾锚点**:**GEMM 9.45G[Lab05]** —— 谱序列是一张「多指标页 $E_r^{p,q}$」逐页翻转的高维计算,
  恰如 GEMM 处理高维矩阵吞吐。
  - 🟢事实:谱序列的 $E_r^{p,q}$ 是双指标阵列,每页做一次双线性求导 $d_r:E_r^{p,q}\to E_r^{p+r,q-r+1}$。
  - 🟡类比:GEMM 把 $C=AB$ 的高维张量吞吐流水化(9.45G MAC/s),谱序列把多指标同调页系统化,两者都是「批量处理高维结构」。

- **关键定理**:**导出函子长正合序列**:左正合 $F$,短正合 $0\to A\to B\to C\to 0$ 给出长正合
  $$0\to F(A)\to F(B)\to F(C)\to R^1F(A)\to R^1F(B)\to R^1F(C)\to R^2F(A)\to\cdots$$
  这是连接函子与上同调的通用工具——「断裂的正合列被导出函子续上」。

- **自测**:
  1. 用 $\mathrm{Ext}^1_{\mathbb{Z}}(\mathbb{Z}/2,\mathbb{Z})\cong\mathbb{Z}/2$ 解释扩张 $0\to\mathbb{Z}\to ?\to\mathbb{Z}/2\to0$ 有几个等价类。
  2. 写出第一象限谱序列 $E_2^{p,q}\Rightarrow H^{p+q}$ 的「收敛」含义(逐页取同调,极限给出目标)。

---

### 附录 B · 超越方法(GAGA 与解析拓扑)

- **核心**:附录 B 严格证明 GAGA(Serre 1956):在 $\mathbb{C}$ 上,射影代数簇 $X$ 的代数凝聚层范畴 $\cong$ 关联解析空间 $X^{an}$ 的解析凝聚层范畴,
  且上同调同构 $H^i(X,\mathcal{F})\cong H^i(X^{an},\mathcal{F}^{an})$。
  这让你**用复分析/拓扑工具算代数几何**:GAGA 后,代数簇上的全纯函数必为有理函数,射影簇的紧复流形结构忠实反映代数结构。
  还讲 **Stein 簇**(解析版的「仿射」,Cartan 定理 B:$H^i=0,\,i>0$),它是仿射消失定理的解析类比。

- **飞腾锚点**:**Iron Law<2%[Lab00]** —— GAGA 要求代数范畴与解析范畴「逐层逐对象」精确一致,误差必须为零,
  正如 Iron Law 把并行效率误差压在 2% 以内。
  - 🟢事实:GAGA 是范畴等价(严格一一对应,带函子的拟逆),不是近似;上同调维数完全相等。
  - 🟡类比:Iron Law 严控误差带保证「实测 ≈ 理论」,GAGA 保证「解析 ≈ 代数」零失真——两边都是「不容许偏差的对齐」。

- **关键定理**:**GAGA(Serre, 1956)**:对 $\mathbb{C}$ 上射影簇 $X$,函子 $\mathcal{F}\mapsto\mathcal{F}^{an}$ 给出凝聚层范畴的等价,且
  $$H^i(X,\mathcal{F})\cong H^i(X^{an},\mathcal{F}^{an})\quad\forall i$$
  推论:射影簇上的全纯函数必为多项式;解析子簇必为代数子簇。

- **自测**:
  1. GAGA 为何对**仿射**簇不成立?(提示:$\mathbb{A}^1_{\mathbb{C}}$ 上有非多项式的整全纯函数 $e^z$。)
  2. Stein 簇的 Cartan 定理 B($H^i=0,\,i>0$)与仿射概形的 Serre 消失定理如何类比?为何说 Stein = 解析仿射?

---

### 附录 C · 计算工具(专题,略)

- **核心**:附录 C 是计算代数几何的入门指针(Gröbner 基、消元理论),现代实现用 Macaulay2 / Singular / Sage / CoCoA。
  本快速精读从略,留作专题;计算代数几何与机器学习的代数方法(如代数统计)有交叉。
- **飞腾锚点**:**分支预测[Lab02]** —— Gröbner 基的 Buchberger 算法高度分支(反复判 S-多项式是否归约到零),分支预测友好。
  - 🟢事实:Buchberger 反复试除与归约,分支密集,流水线效率依赖分支预测命中率。

---

## §9 全书思想主线(约 220 字)

Hartshorne 的主线是**三步语言升级 + 两步分类成就**。
(1) **语言升级**:Ch1 用直观的代数簇(多项式零点)起步,Ch2 把簇抽象为概形($\mathrm{Spec}\,R$ + 结构层),让几何与数论统一——
$\mathrm{Spec}\,\mathbb{Z}$ 与 $\mathbb{P}^1_k$ 同居一族;(2) **计算工具**:Ch3 用凝聚层上同调度量「全局信息缺失」,
Serre 对偶 + Riemann-Roch 是顶峰,把 Euler 示性数表为相交数;(3) **分类成就**:Ch4 用 RR 完成曲线的双有理分类(亏格 $g$ 是不变量),
Ch5 用相交理论与 RR 完成曲面分类。贯穿全书的是 **Grothendieck 革命**:用概形与层把数论与几何焊死——
这正是 Wiles 证明费马大定理的底层语言(椭圆曲线 Ch4 + 概形 Ch2)。GAGA 则把代数与复分析对接。
全书与 Atiyah-MacDonald(局部化 = 仿射局部)、Weibel(导出函子 = 层上同调)、Lang/Mac Lane(范畴 = 层语言)构成完整工具链。

---

## §10 与本仓库其他笔记的交叉引用

- **vs Atiyah-MacDonald 交换代数**:Hartshorne Ch2 的「仿射概形 $\mathrm{Spec}\,R$」= A-M 第 1-3 章的理想、素谱、局部化的几何化;
  A-M 的 Noether 环 = Hartshorne 的 Noether 概形;A-M 的局部化 $R_{\mathfrak{p}}$ = Hartshorne 的茎 $\mathcal{O}_{X,\mathfrak{p}}$。
- **vs Weibel 同调代数**:Hartshorne Ch3 的层上同调 = Weibel 导出函子的特例($\Gamma$ 的右导出);
  Serre 对偶的 $\mathrm{Ext}$ = Weibel 第 3 章;谱序列(附录 A)= Weibel 第 5 章;Abel 范畴 = Weibel/Mac Lane。
- **vs Lang 代数 / Mac Lane 范畴论**:范畴、张量、正合列、函子是 Hartshorne 全书的语言底座;层 =「取值为 Abel 群的反变函子」。

**AI 锚点法(数学 ↔ 工程)**:
- **概形 = 数据类型的抽象推广** 🟢:$\mathrm{Spec}\,R$ 把「环」视为「空间」,像把一组数据类型(环)统一为几何对象来管理。
- **层 = 局部数据的粘合** 🟢:层公理「局部一致即全局可拼」与流形学习(manifold learning)的局部邻域拼成全局流形同构;$\mathcal{F}(U)$ = $U$ 上的局部特征。
- **上同调 = 数据缺失的度量** 🟢:$H^i(X,\mathcal{F})\neq0$ 表示「局部数据无法拼成全局」,恰似自编码器的重建误差衡量信息丢失;仿射消失定理 = 「无信息缺失的数据集」。
- **相交数 = 特征交互** 🟡:$(C.D)$ 度量两条曲线相交的「耦合强度」,类比特征工程中两特征的交互项强度。
- **椭圆曲线 = 密码学** 🟢:本仓库 W1 已做 RSA;椭圆曲线离散对数(ECDLP)是 ECC 密码基础,群律直接对应 Ch4。
- **代数簇 = 多项式方程组的解空间** 🟢:优化里的等式约束 $f_i(x)=0$ 的解集就是仿射簇,SMT 求解器解多项式约束即在求簇上的点。
- **Kähler 微分 $\Omega_{X/Y}$ = 自动微分** 🟡:$\Omega_{X/Y}$ 是导子的通用对象(线性化),与深度学习的 Jacobian/自动微分同构——都把几何「一阶展开」。
- **爆破 blow-up = 分辨率提升** 🟡:blow-up 在奇点处插入例外除子「细化」空间,类比超分辨率把低分辨率点展开成邻域。

---

> **纪律提示**:🟢事实可作锚点 / 🟡类比仅供直觉,绝不在严格证明中引用。Hartshorne 习题占信息量半数以上,「读定理不刷题」等于没读。
> Wildberger 构造主义对概形语言(尤其「无穷」与幂零)持保留,需标注其少数立场。
