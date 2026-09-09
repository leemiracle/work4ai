# Arnold《经典力学的数学方法》(GTM60, 2nd Ed) · 快速逐章精读

> 基于原书:*Mathematical Methods of Classical Mechanics* (V. I. Arnold, GTM60, 2nd ed., Springer, 1989) / 齐民友中译本
> 读于:2026-07-02 / stage-3 研究方向 · 经典力学几何化主桥梁
> 定位:**几何化经典力学的圣经**,Newton 方程 → 变分原理 → Hamilton 正则 → 辛几何,微分形式与辛几何为现代物理数学奠基。
> 本文为**快速逐章精读**(按主题重组为 11 单元),每章 1 个飞腾锚点 🟢/🟡 + 1 个关键定理 + 1 道自测题。
> 前置:本仓库已读 Lee《光滑流形》GTM218、Petersen《黎曼几何》GTM171、do Carmo、Milnor《从可微观点看拓扑》。

---

## §0 引言:Arnold GTM60 是什么,为什么读它

Vladimir I. Arnold(1937-2010,俄罗斯数学学派巨匠)是二十世纪最有影响力的几何分析学家之一。
他以 **KAM 定理**(Kolmogorov-Arnold-Moser,可积系统在小扰动下大部分不变环面存活)、**奇点理论**(catastrophe theory 的分类)与**辛拓扑**(Arnold 猜想)闻名于世。
他的《Mathematical Methods of Classical Mechanics》(GTM60,第 2 版 1989)是**几何化经典力学的标准范本**,也是**辛几何入门的最佳教材**。

Arnold 从一个极简的物理事实——Newton 第二定律 $m\ddot{\mathbf x}=\mathbf F$——出发,
经由**变分原理**(Lagrange)与 **Legendre 变换**(Hamilton),抵达**辛流形**上的**正则方程**与**积分不变量**,把力学彻底重写为**微分几何的语言**。
他的招牌是「**几何优先,计算其次**」:拒绝把力学当作向量方程的堆砌,而坚持把相空间(phase space)视为**辛流形** $(M^{2n},\omega)$,Hamilton 流是保辛结构的微分同胚。
Arnold 名言:「数学教育的一项严重缺陷是,代数与微积分代替了几何,于是学生们既看不见也摸不着数学」——本书正是对此的回应。

这一视角直接催生了现代**辛拓扑**(symplectic topology)与**几何力学**(geometric mechanics)。
全书三部分十章:Part I Newton 力学(实验事实 + 运动方程),Part II Lagrange 力学(变分原理 + 流形上的力学 + 振动),
Part III Hamilton 力学(微分形式 + 辛流形 + 正则形式 + 摄动 + Anosov 定理),另有约 30 个著名附录(KAM、Kepler 拓扑、Maslov 指数、Arnold 猜想等)。
本文按主题重组为 **2 Part 11 单元**(Part I = Ch1-4 含 Newton 与变分过渡,Part II = Ch5-11 含 Hamilton 与辛几何高潮)。

本仓库已精读 **Lee《光滑流形》GTM218**(切空间 / 形式 / Stokes / de Rham / Lie 群 / 辛流形引论 ch22)、
**Petersen/do Carmo**(黎曼几何,测地线 = 自由粒子)、**Milnor《从可微观点看拓扑》**(Morse 理论)。
GTM60 是 Lee GTM218 §22(辛流形引论)的**纵深展开**:Arnold 把 Lee 的辛几何骨架注入物理血肉,
展示微分形式如何「自然地」描述力学定律——功 $=$ $1$-形式的积分,辛形式 $=$ 力学的灵魂。

| 维度 | **Arnold GTM60** | Abraham-Marsden | Goldstein | Landau 卷 1 |
|---|---|---|---|---|
| 风格·学派 | **几何化**,俄罗斯学派,辛几何优先 | 无穷维力学,范畴论味,极抽象 | 物理直觉,标准教科书 | 物理学派,极简最高纲领 |
| 篇幅·年代 | ~500 页,1989(2nd) | ~800 页,1978 | ~600 页,1950(经典) | ~170 页,1976 |
| 严格度 | 高(流形 + 形式必备) | **极高**(无穷维流形) | 中(计算导向) | 低(直觉驱动) |
| 辛几何 | **核心主线**(Part III 五章) | 核心但更抽象 | 仅正则变换章 | 隐含(不显式) |
| 适合谁 | 有几何基础、想贯通力学的读者 ⭐ | 职业几何力学家 | 物理系本科生 | 物理直觉型读者 |

> 🟢 事实可作锚点:Euler-Lagrange 方程、Hamilton 正则方程、Darboux 定理、Liouville 定理均为严格定理。
> 🟡 类比(「相空间=辛流形」「作用量=路径积分」)仅供直觉,**绝不在严格证明中引用**。

---

## §1 全书骨架一览(11 单元,飞腾锚点分布)

原书三部分十章(本文按主题重组为 2 Part 11 单元):Part I(Ch1-4 Newton 力学含变分过渡)与 Part II(Ch5-11 Hamilton 力学含辛几何高潮)。
飞腾锚点从 8 选 1 池中分散,其中 matmul⭐(Ch7/8)、Schmidt⭐(Ch6/10)、GEMM⭐(Ch4/11)各重复一次——
重复处语义自然(Ch7/8 同为变换、Ch6/10 同涉正交对偶、Ch4/11 同属辛结构)。

| 章 | 标题(主题重组) | 核心概念 | 飞腾锚点 |
|---|---|---|---|
| 1 | 实验事实(原书 Ch1) | Galileo 相对性 / Galileo 群 / Newton 定律 | FP16 |
| 2 | 运动方程 Newton(原书 Ch2) | 保守力 / 角动量 / Kepler 问题 / 守恒律 | 分支预测⭐ |
| 3 | 变分原理(原书 Ch3) | 变分法 / Euler-Lagrange / Hamilton 原理 | Iron Law⭐作用量 |
| 4 | Liouville 定理(原书 Ch4-5 桥) | 相流保体积 / 流形上的 Lagrange 力学 | GEMM⭐辛矩阵 |
| 5 | 微分形式(原书 Ch6) | 外代数 / 外微分 $d^2=0$ / Stokes | TLB⭐局部坐标 |
| 6 | 辛流形(原书 Ch7) | 辛形式 $\omega=\sum dp\wedge dq$ / Darboux | Schmidt⭐辛正交 |
| 7 | Hamilton 正则方程(原书 Ch8) | $\dot q=\partial H/\partial p,\ \dot p=-\partial H/\partial q$ | matmul⭐变换 |
| 8 | Legendre 变换(原书 Ch8 §38 桥) | $H=p\dot q-L$ / $L\leftrightarrow H$ 对偶 | matmul⭐变换 |
| 9 | 作用量(原书 Ch9 + 附录) | 作用量泛函 / 作用-角变量 / Hamilton-Jacobi | UDOT⭐作用量积分 |
| 10 | 对偶原理(原书 Ch8 §46 + 附录) | Huygens 原理 / Maupertuis / 光学-力学类比 | Schmidt⭐辛正交 |
| 11 | 积分不变量(原书 Ch8 §40) | Poincaré-Cartan 不变量 / 辛体积 | GEMM⭐辛矩阵 |

**主线**:(1) **Newton→Lagrange**——从 $m\ddot x=F$ 到变分原理 $\delta S=0$,力→路径,坐标依赖→坐标无关;
(2) **Lagrange→Hamilton**——Legendre 变换把二阶 ODE 化为一阶辛系统,切丛→余切丛;
(3) **Hamilton→辛几何**——正则方程 $=$ 辛流形上的 Hamilton 向量场,积分不变量 $=$ 辛结构的不变量,物理→几何。

---

## 第一篇 · Newton 力学

### 第 1 章 · 实验事实

- **核心**:力学的经验基础。Newton 时空观:绝对时间 + 欧氏空间 $\mathbb R^3$。
  **Galileo 相对性原理**:在所有惯性系中力学定律相同。**Galileo 群** $G$ $=$ 空间平移 + 时间平移 + 旋转 + Galileo 推进(boost)$\mathbf v\to\mathbf v+\mathbf u$。
  Newton 方程 $m\ddot{\mathbf x}=\mathbf F(\mathbf x,\dot{\mathbf x},t)$ 在 $G$ 下不变——这预设力的变换律。
  三定律(惯性 / $F=ma$ / 作用反作用)是 Galileo 群协变的经验事实。Arnold 在此把「经验」几何化为「对称群」,为 Noether 定理(Ch3)埋下伏笔。
- **飞腾锚点**:**FP16** —— 实验测量总带有限精度,从 FP16 数据(有限精度)到 Newton 定律(无限精度模型)是抽象跳跃。
  🟢事实:Galileo 群在低速($v\ll c$)下精确,相对论修正是「FP16→FP64」的精度升级(Lorentz 群取代 Galileo 群);
  🟡类比:实验事实是数学公理的经验输入,如同训练数据是模型参数的输入。
- **关键定理**:**Galileo 群的 Newton 方程不变性**。
  $$g\in G:\ (\mathbf x,t)\mapsto(A\mathbf x+\mathbf u\,t+\mathbf b,\ t+s),\qquad m\ddot{\mathbf x}=\mathbf F\ \xrightarrow{\ g\ }\ m\ddot{\mathbf x}'=\mathbf F'.$$
- **自测**:写出 Galileo 推进 $\mathbf x'=\mathbf x+\mathbf u\,t$ 下速度与加速度的变换;说明为何 Newton 第二定律在推进下形式不变(力的变换律是什么?),再说明 Lorentz 推进下 Newton 方程为何「不再」形式不变。

---

### 第 2 章 · 运动方程 Newton

- **核心**:Newton 方程的求解与守恒律。**保守力** $\mathbf F=-\nabla U$ 给出**能量守恒** $E=T+U$。
  **角动量** $\mathbf L=\mathbf r\times m\dot{\mathbf r}$ 在中心力场($\mathbf F\parallel\mathbf r$)下守恒。
  **Kepler 问题**($U=-k/r$):轨道是圆锥曲线,由能量正负区分椭圆 / 抛物 / 双曲——Arnold 用纯几何方法推导,无需冗长计算。
  三体问题不可积——Poincaré 首先发现其混沌性,这是确定性系统中复杂行为的起源。
  守恒律的源头是**对称性**——时间平移→能量,旋转→角动量,空间平移→动量(Noether 定理的物理前驱)。
- **飞腾锚点**:**分支预测⭐分支空间** —— Newton 方程是确定性 ODE,给定初值可预测整条轨道(分支预测成功)。
  🟢事实:混沌系统(三体)使轨道对初值指数敏感——分支预测器失效,正 Lyapunov 指数使远期预测不可行;
  🟡类比:轨道的「分支空间」是相空间中的积分曲线,初值离散化后的误差传播如同分支预测的代价。
- **关键定理**:**能量守恒 + Kepler 第三定律**。
  $$\mathbf F=-\nabla U\ \Longrightarrow\ \frac{d}{dt}\!\left(\frac{m|\dot{\mathbf x}|^2}{2}+U\right)=0;\qquad T^2\propto a^3\ \text{(Kepler 第三定律)}.$$
- **自测**:对 Kepler 势 $U=-k/r$,总能量 $E<0$ 时半长轴 $a=-k/(2E)$;圆轨道的周期 $T=2\pi\sqrt{a^3/k}$,由此推出 Kepler 第三定律 $T^2\propto a^3$。

---

### 第 3 章 · 变分原理

- **核心**:力学的**变分重构**——Arnold 的第一个几何升级。给定 Lagrange 量 $L(q,\dot q,t)=T-V$,定义**作用量** $S[\gamma]=\int_{t_0}^{t_1}L\,dt$。
  **Hamilton 原理**(驻定作用量原理):真实路径使 $S$ 取驻定值 $\delta S=0$。对 $S$ 变分得 **Euler-Lagrange 方程** $\frac{d}{dt}\frac{\partial L}{\partial\dot q_i}-\frac{\partial L}{\partial q_i}=0$。
  这把 Newton 的 $F=ma$ 从「力」翻译为「几何」——路径在位形空间 $Q$ 中「自然弯曲」,坐标无关。
  变分法基础(等周问题、最速降线 brachistochrone)为历史前驱。
  **Noether 定理**:每一个连续对称变换对应一个守恒量——这是 Ch2 对称性直觉的严格化,也是二十世纪理论物理(规范场论)的基石。
- **飞腾锚点**:**Iron Law⭐作用量** —— Hamilton 驻定作用量原理 $\delta S=0$ 是物理学的「宪法」,所有运动方程都从它导出,是一条铁律。
  🟢事实:$\delta S=0$ 是严格变分定理,与 Fermat 光学原理、Einstein 引力方程同源;
  🟡类比:作用量 $S$ 是路径空间的「损失函数」,真实路径是「梯度为零」的极值,与机器学习的损失最小化直觉同构。
- **关键定理**:**Euler-Lagrange 方程**(Hamilton 原理的推论)。
  $$\delta S=\delta\int_{t_0}^{t_1}L(q,\dot q,t)\,dt=0\ \Longrightarrow\ \frac{d}{dt}\frac{\partial L}{\partial\dot q_i}-\frac{\partial L}{\partial q_i}=0,\quad i=1,\ldots,n.$$
- **自测**:取 $L=\frac12 m\dot q^2-U(q)$,验证 Euler-Lagrange 给出 Newton 方程 $m\ddot q=-U'(q)$;再取球摆 $L=\frac12 ml^2(\dot\theta^2+\dot\varphi^2\sin^2\theta)-mgl(1-\cos\theta)$,写出 $\theta$ 的运动方程。

---

### 第 4 章 · Liouville 定理

- **核心**:**位形空间是流形** $Q$——约束系统(如球面摆)的位形在 $S^2$ 上,不是 $\mathbb R^3$。
  Lagrange 量在**切丛** $TQ$ 上定义($\dot q\in T_qQ$),广义坐标在流形上取值。
  引入**相空间** $T^*Q$(余切丛)。Hamilton 方程的流保持相空间体积——这是 **Liouville 定理**:
  Hamilton 流 $\Phi_t:T^*Q\to T^*Q$ 保 **Liouville 测度** $\omega^n=\prod_i dp_i\wedge dq_i$。
  推论:相流不可压缩,这是统计力学(微正则系综)的基础。
  Arnold 在此把 Newton 力学「抬」到流形上(原书 Ch4-5:Lagrangian on manifolds + 小振动 / 正则模式),
  为 Part II 的辛几何铺路——Liouville 体积保持是辛结构的第一个「免费回报」。
- **飞腾锚点**:**GEMM⭐辛矩阵** —— Hamilton 流保体积等价于辛矩阵(行列式 $=1$),辛群 $Sp(2n)$ 自动保 Liouville 体积。
  🟢事实:辛矩阵 $M$ 满足 $M^TJM=J$($J=\begin{psmallmatrix}0&I\\-I&0\end{psmallmatrix}$ 为标准辛矩阵),$\det M=1$ 自动成立,故 Liouville 体积保持是辛约束的免费推论;
  🟡类比:辛变换是「保辛结构的 GEMM」,比一般线性变换多一层结构约束,如同保正交变换比一般 matmul 多了 $Q^TQ=I$。
- **关键定理**:**Liouville 定理**(相空间体积保持)。
  $$\Phi_t^*\!\left(\prod_{i=1}^n dp_i\wedge dq_i\right)=\prod_{i=1}^n dp_i\wedge dq_i;\qquad \mathrm{div}(X_H)=\sum_i\!\left(\frac{\partial\dot q_i}{\partial q_i}+\frac{\partial\dot p_i}{\partial p_i}\right)=0.$$
- **自测**:验证谐振子 $H=\frac12(p^2+\omega^2 q^2)$ 的 Hamilton 流 $\Phi_t$ 保相空间面积;再说明 Liouville 定理为何排除了「相空间体积收缩到一点」的耗散系统(如阻尼振子不属于 Hamilton 系统)。

---

## 第二篇 · Lagrangian 与 Hamiltonian

### 第 5 章 · 微分形式

- **核心**:Part II 的数学工具章(原书 Ch6)。**外形式**(exterior forms):$\mathbb R^n$ 上反对称多重线性泛函。
  **外微分** $d:\Omega^k\to\Omega^{k+1}$ 满足 $d^2=0$。**楔积** $\wedge$ 反交换($\alpha\wedge\beta=(-1)^{kl}\beta\wedge\alpha$)。
  **Stokes 定理** $\int_M d\omega=\int_{\partial M}\omega$ 统一一切积分定理。**Poincaré 引理**:局部闭 $=$ 恰当。
  Arnold 用形式语言重写力学——功 $\int\mathbf F\cdot d\mathbf r$ 是 $1$-形式的积分,辛形式 $\omega=\sum dp_i\wedge dq_i$ 是 $2$-形式,
  **Poincaré-Cartan $1$-形式** $\theta=p\,dq-H\,dt$ 是力学的「联络」。本章为 Lee GTM218 ch11/ch14(已精读)的物理应用。
- **飞腾锚点**:**TLB⭐局部坐标** —— 微分形式在局部坐标卡中计算,如同 TLB 分页寻址。
  🟢事实:$k$-形式在坐标 $x^i$ 下展开为 $\omega=\sum\omega_{i_1\cdots i_k}\,dx^{i_1}\wedge\cdots\wedge dx^{i_k}$,局部用 $\mathbb R^n$ 寻址,卡间用转移函数拼接(Lee ch11 已精读);
  🟡类比:形式是坐标无关的,但计算须「分页」到局部坐标,如同 TLB 把虚拟地址翻译为物理地址。
- **关键定理**:**Stokes 定理**(流形上的微积分基本定理)。
  $$\int_M d\omega=\int_{\partial M}\omega,\qquad d^2=0\ \Longleftrightarrow\ \partial^2=\varnothing.$$
- **自测**:在 $\mathbb R^3$ 中验证 $\omega=F_1\,dx+F_2\,dy+F_3\,dz$ 的 Stokes 给出 $\oint_C\mathbf F\cdot d\mathbf r=\iint_S(\nabla\times\mathbf F)\cdot d\mathbf S$(经典 Stokes);再说明 $d^2=0$ 的意义是「边界的边界为零」。

---

### 第 6 章 · 辛流形

- **核心**:全书的高潮(原书 Ch7)。**辛流形** $(M^{2n},\omega)$:$\omega$ 是闭($d\omega=0$)且非退化($\omega^n\ne0$)的 $2$-形式。
  余切丛 $T^*Q$ 自带**标准辛结构** $\omega=\sum dp_i\wedge dq_i$。
  **Darboux 定理**:任何辛流形局部都有坐标使 $\omega=\sum dp_i\wedge dq_i$——辛流形「局部平坦」,没有局部不变量
  (与黎曼曲率本质不同!这是辛几何与黎曼几何的根本差异——Petersen 的 $R_{ijkl}$ 在辛几何中没有对应物)。
  **Lagrangian 子流形**:$\omega|_L=0$ 且 $\dim L=n$,是辛流形的「极小子流形」。**辛同胚**(symplectomorphism)保 $\omega$。
  Arnold 在此把 Hamilton 力学完全「几何化」——力学 $=$ 辛几何。
- **飞腾锚点**:**Schmidt⭐辛正交** —— 辛流形有**辛正交补**($V^\perp$ 关于 $\omega$ 定义),辛基(Darboux)类似 Schmidt 正交基。
  🟢事实:Darboux 定理说辛形式局部可标准化为 $\sum dp_i\wedge dq_i$,类似 Schmidt 把内积标准化为 $\delta_{ij}$;
  辛正交补满足 $\dim V+\dim V^\perp=2n$,但 $V\cap V^\perp\ne\varnothing$ 可能(Lagrangian 子流形),与欧氏正交补本质不同;
  🟡类比:辛基是「成对坐标 $(p_i,q_i)$」的标准化,每对像一个谐振子的相平面。
- **关键定理**:**Darboux 定理**(辛流形局部平坦,无曲率)。
  $$(M^{2n},\omega)\ \text{辛流形}\ \Longrightarrow\ \forall\,p\in M,\ \exists\ \text{局部坐标使}\ \omega=\sum_{i=1}^n dp_i\wedge dq_i.$$
- **自测**:验证 $T^*\mathbb R^n=\mathbb R^{2n}$ 上 $\omega=\sum dp_i\wedge dq_i$ 满足 $d\omega=0$ 且 $\omega^n\ne0$;再说明 Darboux 定理为何意味着辛流形「没有曲率」(对比 Petersen 黎曼流形的局部不变量 $R_{ijkl}$)。

---

### 第 7 章 · Hamilton 正则方程

- **核心**:**Hamilton 正则方程**把 Lagrange 的二阶 ODE 化为**一阶辛系统**。
  给定 Hamilton 量 $H(q,p,t)$,正则方程为 $\dot q_i=\partial H/\partial p_i$,$\dot p_i=-\partial H/\partial q_i$。
  几何上,定义 **Hamilton 向量场** $X_H$ 满足 $i_{X_H}\omega=dH$(即 $\omega(X_H,\cdot)=dH(\cdot)$)。
  Hamilton 流 $\Phi_t$ 是辛流形上的**辛同胚**(保 $\omega$,故保 Liouville 体积,Ch4)。
  能量守恒:$dH/dt=\partial H/\partial t$($H$ 不显含 $t$ 时守恒)。**正则变换**(canonical transformation)= 辛同胚,可用生成函数编码。
  **相空间** $=$ 余切丛 $T^*Q$ $=$ 辛流形,Hamilton 力学完全在辛流形上运行——Newton 的二阶向量方程最终化为一阶辛流。
- **飞腾锚点**:**matmul⭐变换** —— Hamilton 方程 $\dot z=J\nabla H$($z=(q,p)$,$J$ 为辛矩阵)中 $J\nabla H$ 是矩阵-向量乘法,Hamilton 流是「辛旋转」。
  🟢事实:辛矩阵 $J=\begin{psmallmatrix}0&I\\-I&0\end{psmallmatrix}$,$J^2=-I$,$\dot z=J\nabla H$ 是标准线性变换(matmul),$\Phi_t=\exp(tX_H)$ 保辛结构;
  🟡类比:Hamilton 流是「保辛结构的 matmul」,正则变换 $=$ 辛矩阵作用,与自然梯度法中保黎曼度量的变换同构。
- **关键定理**:**Hamilton 正则方程 + Hamilton 流保辛**。
  $$\dot q_i=\frac{\partial H}{\partial p_i},\quad \dot p_i=-\frac{\partial H}{\partial q_i};\qquad \Phi_t^*\omega=\omega\ \text{(Hamilton 流保辛形式)}.$$
- **自测**:对谐振子 $H=\frac{p^2}{2m}+\frac12 kq^2$,写出正则方程并解出 $q(t)=A\cos(\omega t+\varphi)$($\omega=\sqrt{k/m}$);再验证 Hamilton 流 $\Phi_t$ 保辛面积 $\omega=dp\wedge dq$。

---

### 第 8 章 · Legendre 变换

- **核心**:连接 Lagrange 与 Hamilton 的**桥梁**。**Legendre 变换** $H(q,p)=p_i\dot q^i-L(q,\dot q)$,
  其中 $p_i=\partial L/\partial\dot q^i$(广义动量)。这要求**正则性**:Hessian $\partial^2L/\partial\dot q^i\partial\dot q^j$ 非退化(可反解 $\dot q=\dot q(q,p)$)。
  几何上,Legendre 变换是从**切丛** $TQ$(Lagrange 的 $(q,\dot q)$)到**余切丛** $T^*Q$(Hamilton 的 $(q,p)$)的微分同胚。
  凸性条件下 Legendre 变换**对合**(双重变换回到自身:$L^{**}=L$),这是凸分析的核心工具,
  也连接 Fenchel 对偶、热力学(内能↔自由能)与机器学习(SVM 对偶)。退化情形(相对论粒子 $L$ 关于 $\dot q$ 线性)需约束 Hamiltonian 处理。
- **飞腾锚点**:**matmul⭐变换** —— Legendre 变换是从 $(q,\dot q)$ 到 $(q,p)$ 的换基,如同 matmul 换坐标系。
  🟢事实:$p=\partial L/\partial\dot q$ 是切丛到余切丛的纤维导数(切空间 $\to$ 余切空间),实现上是 Jacobian 变换;
  🟡类比:Legendre 变换像「从速度坐标切到动量坐标」,两者通过能量 $H=p\dot q-L$ 对偶,与 SVM 中原问题-对偶问题的 Fenchel 对偶同构。
- **关键定理**:**Legendre 变换的对合性**(凸性条件下)。
  $$p_i=\frac{\partial L}{\partial\dot q^i},\qquad H(q,p)=p_i\dot q^i-L(q,\dot q);\qquad L=H^{**}\ \text{(双重 Legendre 回到自身)}.$$
- **自测**:对 $L=\frac12 m\dot q^2-U(q)$,算 $p=m\dot q$,$H=p^2/(2m)+U$,验证 $H=p\dot q-L$;再说明当 $L$ 关于 $\dot q$ 线性($L=\alpha\dot q$)时 Legendre 变换退化(为何 Hessian 奇异?)。

---

### 第 9 章 · 作用量

- **核心**:作用量的多面性。**作用量泛函** $S=\int L\,dt$ 的驻定值给出真实路径(Ch3)。
  **Hamilton 主函数** $S(q,t)$ 满足 **Hamilton-Jacobi 方程** $\partial S/\partial t+H(q,\partial S/\partial q)=0$——把 $2n$ 个 ODE 化为一个 PDE。
  **作用量-角变量** $(I,\varphi)$:完全可积系统($n$ 个独立守恒量,即 $n$ 个对合的首次积分)可变换为 $I_i=\text{const}$,$\dot\varphi_i=\omega_i(I)$,
  解在**不变环面** $T^n$ 上准周期运动。这是 **KAM 定理**(Kolmogorov-Arnold-Moser)的舞台:小扰动下大多数不变环面存活(仅被有理频率的极薄环面破裂)。
  **生成函数** $S(q,Q,t)$ 编码正则变换——辛几何的「坐标变换工具」,也是 Hamilton-Jacobi 理论的核心。
- **飞腾锚点**:**UDOT⭐作用量积分** —— 作用量 $S=\int L\,dt$ 是沿路径的时间积分(累加),正如 UDOT 是沿向量的点积累加。
  🟢事实:$S=\int_{t_0}^{t_1}L\,dt$ 离散化为 $\sum_i L_i\Delta t$(逐点求值 $+$ 累加),实现上等同 UDOT 点积指令的路径积分版本;
  🟡类比:作用量是「路径的分数」,最优路径是「分数驻定」的极值,与强化学习中沿轨迹的回报累积同构。
- **关键定理**:**Hamilton-Jacobi 方程 + 作用量-角变量**。
  $$\frac{\partial S}{\partial t}+H\!\left(q,\frac{\partial S}{\partial q}\right)=0;\qquad I_i=\frac{1}{2\pi}\oint_{\gamma_i}p\,dq,\quad \dot I_i=0,\ \dot\varphi_i=\omega_i(I).$$
- **自测**:对谐振子 $H=\frac12(p^2+\omega^2 q^2)$,算作用量 $I=H/\omega$(总能量除以频率),写出角变量 $\varphi=\omega t+\varphi_0$;再说明 Hamilton-Jacobi 方程如何把 $2n$ 个 ODE「打包」为一个 PDE。

---

### 第 10 章 · 对偶原理

- **核心**:**力学与光学的深层对偶**——Arnold 最具诗意的章节。
  **Huygens 原理**:波前的新位置是旧波前每点发出的子波的包络。Arnold 展示 Huygens 原理等价于**变分原理**:粒子轨道与波前传播对偶。
  **Maupertuis 原理**:在固定能量 $E$ 下,真实路径使**约化作用量** $\int p\,dq$ 驻定($\delta\int p\,dq=0$)。
  **光学-力学类比**:Fermat 原理(光走时间最短的路径)与 Maupertuis 原理结构相同——力学是「波长远极短的波动光学」。
  Hamilton-Jacobi 方程是**程函方程**(eikonal),$S$ 是波的相位,$\hbar\to0$ 的准经典极限回到 Newton 轨道——Schrödinger 方程是 Hamilton-Jacobi 的「量子化」。
- **飞腾锚点**:**Schmidt⭐辛正交** —— 力学(粒子轨道,正交于等作用量面)与光学(波前,正交于光线)的「正交对偶」。
  🟢事实:Hamilton-Jacobi 中 $p=\partial S/\partial q$,粒子动量正交于等作用量面 $S=\text{const}$(梯度正交于等值面);波前与光线正交;
  🟡类比:力学-光学对偶像「粒子与波的正交分解」,量子力学中由 de Broglie 波长统一,$\lambda=h/p\to0$ 回到经典极限。
- **关键定理**:**Maupertuis 原理 + 光学-力学类比**。
  $$\delta\int_{\gamma}p\,dq=0\ \text{(固定能量}\ E);\qquad \text{Fermat}\ \delta\int n\,ds=0\ \longleftrightarrow\ \text{Maupertuis}\ \delta\int\sqrt{2m(E-V)}\,ds=0.$$
- **自测**:写出 Snell 定律(折射)从 Fermat 原理的推导;再说明为何 $E\to\infty$ 时力学轨道趋近直线(自由粒子),等价于「折射率均匀」。

---

### 第 11 章 · 积分不变量

- **核心**:**Poincaré 积分不变量**:在辛流形 $(M^{2n},\omega)$ 上,$\omega$ 的幂 $\omega^k$($k=1,\ldots,n$)在 Hamilton 流下不变。
  一阶不变量 $\oint_\gamma p\,dq$(Poincaré 相对积分不变量)在**正则变换**(辛同胚)下保持。
  **Poincaré-Cartan $1$-形式** $\theta=p\,dq-H\,dt$ 在扩展相空间上定义,其外微分 $d\theta=\omega-dH\wedge dt$ 给出**接触结构**(contact structure)。
  Arnold 将这些不变量与 Liouville 定理(Ch4,$\omega^n$ 的不变性)统一:辛结构 $\omega$ 本身就是**最基本的积分不变量**。
  此框架直接通向**辛拓扑**——**Arnold 猜想**:Hamilton 辛同胚的不动点数 $\ge\sum\dim H^k(M)$(Morse 不等式的辛推广);
  以及 **Gromov 非挤压定理**(辛球不能被挤压到更细的柱)。
- **飞腾锚点**:**GEMM⭐辛矩阵** —— Poincaré 积分不变量在辛变换下保持,是辛矩阵保「辛面积」的直接推论。
  🟢事实:辛同胚 $f$ 满足 $f^*\omega=\omega$,故 $\oint_\gamma p\,dq=\int_D\omega=\int_{f(D)}\omega=\oint_{f(\gamma)}p\,dq$——积分不变量是辛结构(GEMM 保结构)的积分表述;
  🟡类比:辛面积 $\int\omega$ 如同矩阵行列式(体积),辛变换保行列式 $=1$,故保辛面积,与 SVD 中保体积的正交变换同构。
- **关键定理**:**Poincaré 相对积分不变量**。
  $$\oint_\gamma\sum_i p_i\,dq_i\ \text{在正则变换下不变};\qquad f^*\omega=\omega\ \Longrightarrow\ \int_D\omega^k=\int_{f(D)}\omega^k,\quad k=1,\ldots,n.$$
- **自测**:验证谐振子 $\oint pdq=2\pi E/\omega$($E$ 为能量),在正则变换 $(q,p)\to(Q,P)$ 下不变;再说明 Arnold 猜想为何要求「辛同胚」而非一般微分同胚(辛结构提供了额外约束)。

---

## §8 附录一览:Arnold 的「宝藏」

GTM60 第 2 版附有约 **30 个附录**,每一篇都是独立的小论文,浓缩了 Arnold 对某专题的独到视角。以下列出与 11 章主线关联最密的附录,供选读导航:

- **附录 1-3**:Kepler 问题拓扑 / 三体问题 / 刚体——经典力学的深度案例,对接 Ch2。
- **附录 4-5**:Lie 群与力学 / 约束系统——对称性的几何处理,对接 Ch1/Ch4。
- **附录 6-7**:正则变换 / 生成函数——正则形式论的工程细节,对接 Ch7。
- **附录 8-9**:Hamilton-Jacobi / 变分原理——作用量的深度展开,对接 Ch9。
- **附录 10-11**:周期运动 / 不变环面与 KAM——Arnold 本人的核心贡献,对接 Ch9(KAM 定理)。
- **附录 12**:拓扑分析与牛顿引力势的拓扑——Arnold 对势函数拓扑的洞察,对接 Ch2。
- **附录 13**:Maupertuis 原理与光学——力学-光学对偶的完整论述,对接 Ch10。
- **附录 14-15**:接触结构 / 辛拓扑引论——通向接触几何与 Gromov 理论,对接 Ch6/Ch11。
- **附录 16**:Maslov 指数——准经典近似的拓扑障碍,连接 Ch10(对偶)与 Ch11(不变量)。
- **附录 17-18**:波前 / Lagrange 映射——奇点理论(Arnold 另一核心贡献)在光学中的应用。
- **附录 19-20**:短程线流 / Morse 理论——Morse 不等式的辛几何版本,对接 Ch11(Arnold 猜想)。

> **建议**:第一遍读正文 10 章,暂跳附录;第二遍按主题选读附录(Ch9→附录 10-11 KAM,Ch11→附录 19-20 Morse/Arnold 猜想)。

---

## §9 全书思想主线:Newton → Lagrangian → Hamiltonian → 辛几何

Arnold GTM60 的主线是一条「**力学几何化**」的上升阶梯,把向量方程逐步重写为辛流形上的几何。

**第一阶 · Newton**(Ch1-2):力学从经验事实出发——Galileo 相对性原理 + Newton 三定律。$m\ddot{\mathbf x}=\mathbf F$ 是 $\mathbb R^3$ 中的向量方程,
守恒律(能量、角动量)从力的特殊对称性「附带」得到。Newton 语言依赖坐标选择,无法自然处理约束(如球面摆),
且把「力」当作原始概念——这是物理直觉最强但数学结构最浅的层次。

**第二阶 · Lagrangian**(Ch3-4):Hamilton 驻定作用量原理 $\delta S=0$ 把力学从「力」翻译为「路径」——位形空间 $Q$ 是**微分流形**,
Lagrange 量 $L=T-V$ 在切丛 $TQ$ 上,Euler-Lagrange 方程是**坐标无关**的变分方程。
约束(球面摆、刚体)自动成为「流形上的力学」。Noether 定理把守恒律与对称性严格链接——Arnold 几何视角的第一个回报:守恒不再是巧合,而是对称的必然。

**第三阶 · Hamiltonian**(Ch7-8):Legendre 变换把二阶 Lagrange 方程化为一阶 Hamilton 正则方程 $\dot z=J\nabla H$。
相空间从切丛切换到余切丛 $T^*Q$,自带辛结构 $\omega=\sum dp_i\wedge dq_i$。
Hamilton 方程现在是**辛流形上的一阶流**——Hamilton 向量场 $X_H$ 定义为 $i_{X_H}\omega=dH$,Hamilton 流保辛结构(故保 Liouville 体积,Ch4)。
这一步把力学从「位形空间的二阶 ODE」提升为「辛流形上的几何流」。

**第四阶 · 辛几何**(Ch5-6, 9-11):Arnold 的终极视角——力学 $=$ 辛流形上的几何。
Darboux 定理说辛流形「局部平坦」(无曲率!),但**全局辛拓扑**丰富(Arnold 猜想、Gromov 非挤压定理)。
积分不变量(Ch11)是辛结构 $\omega$ 的积分表述,Poincaré 不变量 $\oint pdq$ 是一切正则理论的基石。
Hamilton-Jacobi 理论(Ch9-10)揭示力学与光学的深层对偶——粒子与波在 Hamilton-Jacobi 方程中统一,Schrödinger 方程是它的「量子化」。

**一条铁律**:辛结构 $\omega$ 是「力学的灵魂」——Newton 方程、Lagrange 方程、Hamilton 方程都是 $\omega$ 的不同表达;
守恒律、积分不变量、辛流的不动点(Arnold 猜想)都是 $\omega$ 的推论。
Arnold 把这条链讲透:从 $F=ma$ 到辛拓扑,每一步都有动机、有几何图景、有物理血肉。

### 四条红线

1. **几何化红线**——Newton($\mathbb R^3$ 向量)→ Lagrange(流形 $Q$ 上的变分)→ Hamilton(辛流形 $T^*Q$ 上的流),每升一阶,几何结构更深一层,坐标依赖逐层减弱。
2. **对称性红线**——Galileo 群(Ch1)→ Noether 定理(Ch3)→ 正则变换 / 辛同胚(Ch7-8)→ KAM 不变环面(Ch9),对称性从「经验观察」升级为「守恒的数学保证」。
3. **对偶红线**——Lagrange ↔ Hamilton(Legendre,Ch8)→ 粒子 ↔ 波(光学-力学类比,Ch10)→ 经典 ↔ 量子(Hamilton-Jacobi,Ch9),每一对对偶都揭示力学的一个新面相。
4. **不变量红线**——能量守恒(Ch2)→ Liouville 体积(Ch4)→ 辛形式 $\omega$(Ch6)→ Poincaré 积分不变量(Ch11),不变量逐层深化,最终汇聚于辛结构 $\omega$。

**读法建议**:第一遍精读 Ch1-3(Newton → 变分原理,物理直觉最密);第二遍死磕 Ch5-7(微分形式 → 辛流形 → 正则方程,全书灵魂,与 Lee GTM218 ch11/ch22 交叉);
第三遍选读 Ch9-11(作用量 → 对偶 → 积分不变量,通向 KAM 与辛拓扑)。全书精读约 80-120 小时(每周 10-20h,8-12 周)。

---

## §10 与本仓库其他笔记的交叉引用

- **Lee《光滑流形》GTM218**(stage-2):GTM60 Part II(Ch5-7)直接调用 Lee 的**微分形式**(ch11/ch14)、**Stokes 定理**(ch16)、**辛流形引论**(ch22)。
  Arnold 把 Lee 的「数学骨架」注入物理血肉。建议:Lee ch22 $\to$ Arnold Ch5-7,交叉对照辛形式 $\omega=\sum dp_i\wedge dq_i$ 的定义与 Darboux 定理——Lee 给定义,Arnold 给应用。
- **Petersen《黎曼几何》GTM171 / do Carmo**(stage-2):Arnold Ch2 的约束系统(球面摆)在 Petersen 的黎曼流形上运行,
  测地线是「自由粒子」的运动方程($L=\frac12|\dot\gamma|^2$,$\nabla_{\dot\gamma}\dot\gamma=0$)。
  Darboux 定理(Ch6)与黎曼曲率的对比是核心洞察:辛几何无曲率,黎曼几何有。建议:Petersen ch5(测地线)对照 Arnold Ch3 的变分原理——「测地线 $=$ 作用量驻定的曲线」。
- **Milnor《从可微观点看拓扑》**(stage-2):Arnold 的 Hamilton 流与 Morse 理论(Milnor ch2 临界点理论)在「流上的不动点」处交汇。
  **Arnold 猜想**(Hamilton 辛同胚不动点数 $\ge\sum\dim H^k$)是 Morse 不等式($c_\lambda\ge\beta_\lambda$)的辛推广。
  建议:Milnor ch2 $\to$ Arnold Ch11 附录(Arnold 猜想)——Morse 理论计数临界点,Arnold 猜想计数辛不动点。
- **Evans《PDE》**(stage-3):Arnold Ch9 的 **Hamilton-Jacobi 方程**是 Evans ch3(一阶 PDE / 特征线法)的核心例子。
  $\partial S/\partial t+H(q,\partial S/\partial q)=0$ 用特征线求解,特征线 $=$ Hamilton 轨道——PDE 的特征线就是力学轨道。建议:Evans ch3 $\leftrightarrow$ Arnold Ch9。
- **AI 锚点(飞腾 D3000M 映射)**:
  - **Galileo 群 = 等变性**(Ch1 FP16:物理定律的协变性 $=$ 神经网络的等变 / 协变架构,Galileo 推进 $\leftrightarrow$ 等变 CNN,旋转对称 $=$ 球面 CNN);
  - **变分原理 = 优化**(Ch3 Iron Law⭐:$\delta S=0$ $=$ 损失函数梯度为零,经典力学是路径空间的优化,与变分推断 / ELBO 同源);
  - **Legendre 对偶 = 对偶优化**(Ch8 matmul⭐:$L\leftrightarrow H$ 的 Legendre 变换 $=$ SVM / 强化学习的 Lagrange 对偶,凸优化 Fenchel 共轭);
  - **Hamilton 流 = 神经 ODE**(Ch7 matmul⭐:$\dot z=J\nabla H$ 是保结构 ODE,辛神经 ODE 用于保能量模拟,避免长期积分能量漂移);
  - **KAM = 扰动下的稳定性**(Ch9 UDOT⭐:小扰动下不变环面存活 $=$ adversarial training 的鲁棒性,数学上是 KAM 定理的测度估计);
  - **辛积分器 = 保结构数值**(Ch11 GEMM⭐:辛 Euler / Störmer-Verlet 保辛结构,分子动力学标准方法,与 Lee ch8 流的基本定理对接——辛积分器是 Lee ODE 理论的保结构特例)。

---

> **下一步**:沿 `01-track/stage-3` 精读 Arnold Ch1-3(Newton → 变分原理,物理直觉最密),遇关键概念查 `00-META/CONCEPT-INDEX` 中「导数 / 积分 / 优化」视角;
> Ch5-7(微分形式 → 辛流形 → 正则方程)死磕 Darboux 定理与 $i_{X_H}\omega=dH$,与 Lee GTM218 ch22(辛流形引论)交叉对照;
> Ch9-11(作用量 → 对偶 → 积分不变量)通向 KAM 定理与辛拓扑,选读附录(Arnold 猜想、Maslov 指数)。
> **实操验证**(建议用 Python/NumPy):
> - 用 `scipy.integrate.solve_ivp` 解 Kepler 问题(Ch2)→ 验证 $T^2\propto a^3$
> - 手写 Euler-Lagrange 方程求解双摆(Ch3)→ 验证混沌行为
> - 实现辛积分器 Störmer-Verlet 解谐振子(Ch11)→ 对比普通 RK4 的能量漂移
