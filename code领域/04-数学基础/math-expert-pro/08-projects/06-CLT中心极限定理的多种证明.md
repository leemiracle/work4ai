# 中心极限定理（CLT）的多种证明

> 为什么这个结论值得用多种方式证明：中心极限定理（Central Limit Theorem）是概率论的「中心」——它解释了为什么正态分布无处不在：任意分布（只要方差有限）的独立和标准化后都趋向正态。200 多年来，它被至少 5 条路径反复证明——二项逼近、特征函数、矩方法、Lindeberg 替换、Stein 方法——每一条都揭示「正态性」的不同侧面，最后一条还能给出机器学习里迫切需要的收敛速率。

## 结论陈述

设 $X_1,X_2,\ldots$ 是独立同分布（i.i.d.）随机变量，$\mathbb E[X_i]=\mu$，$\text{Var}(X_i)=\sigma^2\in(0,\infty)$。令 $S_n=X_1+\cdots+X_n$。则标准化部分和依分布收敛于标准正态：
$$\frac{S_n-n\mu}{\sigma\sqrt n}\ \xrightarrow{\ d\ }\ \mathcal N(0,1) \quad (n\to\infty).$$

换句话说：**只要方差有限，无论原始分布多么奇怪（偏态、离散、重尾到二阶矩为止），独立求和后的标准化结果一律趋向钟形曲线**。这正是「正态分布无处不在」的数学根源。

**历史脉络（一条贯穿 200 年的主线）**：

| 年份 | 人物 | 贡献 |
| --- | --- | --- |
| 1733 | Abraham de Moivre | 首次对 $p=1/2$ 的二项分布写出正态极限（路径 1 雏形） |
| 1812 | Pierre-Simon Laplace | 推广到任意 $p$，CLT 之名渐显 |
| 1900–1901 | Lyapunov | 用特征函数给出第一版严格一般证明（路径 2 前身） |
| 1922 | Jarl W. Lindeberg | 替换法 + 最一般 Lindeberg 条件（路径 4） |
| 1920s | Paul Lévy | 系统化特征函数 + 连续定理（路径 2 标准化） |
| 1941–1942 | Berry / Esseen | 收敛速率 $O(1/\sqrt n)$（路径 5 的核心定理） |
| 1972 | Charles Stein | Stein 方法，把速率证明系统化（路径 5） |

下面给出 **5 条** 思路迥异的证法——分别用组合逼近、调和分析、矩计数、替换法、 Stein 方法攻下同一个结论。

---

## 路径 1：de Moivre–Laplace（二项分布特例，de Moivre 1733 / Laplace 1812）

**思路**：最早期形式。$S_n\sim\text{Bin}(n,p)$（$n$ 次独立伯努利试验之和，$\mu=np$，$\sigma^2=np(1-p)$）。用 Stirling 公式直接估计点概率。

**关键步骤**：

1. 对点概率用 Stirling 公式 $n!\sim\sqrt{2\pi n}(n/e)^n$ 展开：
$$\mathbb P(S_n=k)=\binom{n}{k}p^k(1-p)^{n-k},\quad k=np+x\sqrt{np(1-p)}.$$
2. 取对数后在 $k=np$ 附近 Taylor 展开，二次项主导，高阶项在中心区域（$x=O(1)$，即 $k$ 离 $np$ 约 $O(\sqrt n)$）趋于零。
3. 得到**局部极限定理**：
$$\sqrt{np(1-p)}\cdot\mathbb P(S_n=k)\ \xrightarrow{n\to\infty}\ \frac{1}{\sqrt{2\pi}}e^{-x^2/2}.$$
4. 右端正是标准正态密度。把离散概率对 $x$ 求和逼近为积分，即得分布函数收敛。$\square$

**美学**：⭐⭐⭐ 朴素、初等，但仅对二项分布成立。

**揭示**：正态分布最早就是作为二项分布的极限「被发现」的，而非凭空定义。de Moivre 1733 年首次写下正态密度的公式，正是为了逼近二项系数——这是正态分布的「诞生证书」。

**注记**：此法的现代延伸是 **Edgeworth 展开**——保留 Taylor 展开中的三阶、四阶项，得到对正态极限的「修正项」，从而刻画 $T_n$ 与 $\mathcal N$ 的偏差大小。它正是路径 5 Berry–Esseen 定理的「精度升级版」前身。

---

## 路径 2：特征函数 + Lévy 连续定理（现代标准证法，Lévy 1920s）

**思路**：最干净、最普适的现代证法。标准化 $Y_i=(X_i-\mu)/\sigma$（$\mathbb E Y_i=0,\text{Var}=1$），令 $T_n=\frac1{\sqrt n}\sum_{i=1}^n Y_i$。用特征函数（傅里叶变换）把「求和」化为「乘积」。

**关键步骤**：

1. 独立变量的特征函数相乘：
$$\varphi_{T_n}(t)=\mathbb E[e^{itT_n}]=\prod_{i=1}^n\varphi_{Y_i}(t/\sqrt n)=\varphi_Y(t/\sqrt n)^n.$$
2. 对 $\varphi_Y$ 在 0 处 Taylor 展开（这里用到二阶矩存在，且 $\mathbb E Y=0,\mathbb E Y^2=1$）：
$$\varphi_Y(u)=1+iu\,\mathbb E Y-\frac{u^2}{2}\mathbb E Y^2+o(u^2)=1-\frac{u^2}{2}+o(u^2).$$
3. 代入 $u=t/\sqrt n$，再用 $\lim_{n\to\infty}(1+a_n/n)^n=e^a$（当 $a_n\to a$）：
$$\varphi_{T_n}(t)=\left(1-\frac{t^2}{2n}+o(1/n)\right)^n\ \xrightarrow{n\to\infty}\ e^{-t^2/2}.$$
4. 后者正是 $\mathcal N(0,1)$ 的特征函数。由 **Lévy 连续定理**（特征函数逐点收敛 $\Rightarrow$ 分布弱收敛）得 $T_n\xrightarrow{d}\mathcal N(0,1)$。$\square$

**美学**：⭐⭐⭐⭐⭐ 一页纸证完最一般 i.i.d. CLT，优雅至极。

**揭示**：特征函数把「卷积（求和）化为乘积」，把「分布收敛」化为「函数逐点收敛」——是概率论与调和分析的交汇点。整个现代极限理论都建立在这个翻译之上。

**注记**：Lévy 连续定理的「逆向」方向（分布弱收敛 $\Rightarrow$ 特征函数逐点收敛）是平凡的；真正需要证的是「正向」，即从特征函数收敛反推分布收敛，这里的关键是 **tightness（紧性）**——保证极限不会「逃到无穷」。这正是「$\sigma^2\in(0,\infty)$」中「$<\infty$」部分的用武之地。

---

## 路径 3：矩方法（method of moments）

**思路**：假设 $X_i$ 的所有矩都存在（比 CLT 需要的二阶矩**强**）。直接计算 $T_n$ 的各阶矩，证明它们收敛到正态的矩。

**关键步骤**：

1. 计算 $T_n=\frac1{\sqrt n}\sum Y_i$ 的 $k$ 阶矩 $\mathbb E[T_n^k]=n^{-k/2}\sum_{i_1,\ldots,i_k}\mathbb E[Y_{i_1}\cdots Y_{i_k}]$。
2. 由于 $Y_i$ 独立且均值零，凡有某个下标只出现一次的项期望为零。剩下「每个下标至少出现两次」的项。
3. 组合计数（用 Stirling 数）证明：
   - **奇数阶矩** $\mathbb E[T_n^{2m+1}]\to 0$；
   - **偶数阶矩** $\mathbb E[T_n^{2m}]\to(2m-1)!!=1\cdot3\cdot5\cdots(2m-1)$，正是标准正态的 $2m$ 阶矩。
4. 若极限分布被矩唯一决定（满足 **Carleman 条件** $\sum_{k\geq 1}(m_{2k})^{-1/2k}=+\infty$，正态分布满足此条件），则 $T_n\xrightarrow{d}\mathcal N$。$\square$

**美学**：⭐⭐⭐ 直接、组合味浓，但需要额外假设。

**揭示**：正态分布的所有矩由前两阶完全决定（$m_{2k}=(2k-1)!!$），这是它「被两个参数刻画」的深层原因。缺点：需要「所有矩存在」这个额外假设，不如特征函数法一般（反例：对数正态分布的矩不满足 Carleman 条件）。

**一个具体的演算**：取 $k=4$，唯一幸存的非零项是「下标成对」的配对——共 3 种配对方式（$\{1,2\}\{3,4\}$、$\{1,3\}\{2,4\}$、$\{1,4\}\{2,3\}$），每项贡献 $\frac{1}{n^2}$，故 $\mathbb E[T_n^4]=3\cdot n(n-1)\cdot\frac1{n^2}\to 3=3!!$，正是 $\mathcal N(0,1)$ 的四阶矩。这就是「配对」组合学在背后工作。

---

## 路径 4：Lindeberg 替换（Jarl Waldemar Lindeberg, 1922）

**思路**：最具洞察力的证法。把 $X_i$ 一个一个「替换」成同均值同方差的高斯 $G_i$，证明替换前后分布几乎不变。

**关键步骤**：

1. 设 $T_n=\frac1{\sqrt n}\sum_{i=1}^n Y_i$，对照 $T_n'=\frac1{\sqrt n}\sum_{i=1}^n G_i$（其中 $G_i$ 独立、$\mathcal N(0,1)$）。后者每项独立高斯，和显然 $\sim\mathcal N(0,1)$。
2. 一次替换 $Y_i\to G_i$ 对任意良行为检验函数 $h$ 的影响：用 Taylor 展开到三阶，差被 $\frac{1}{n^{3/2}}\mathbb E|Y_i|^3$ 控制。
3. $n$ 次替换累计误差 $O(1/\sqrt n)\to 0$。所以 $T_n$ 与 $T_n'$ 同极限，即 $\mathcal N(0,1)$。$\square$
4. 这套论证给出最一般的 **Lindeberg 条件**（不必同分布，对三角阵列成立）：
$$\frac1{s_n^2}\sum_{i=1}^n\mathbb E\left[Y_i^2\,\mathbf 1_{\{|Y_i|>\varepsilon s_n\}}\right]\xrightarrow{n\to\infty}0,\quad \forall\varepsilon>0\quad(s_n^2=\sum_{i=1}^n\sigma_i^2).$$
   Lindeberg 条件 $\Rightarrow$ CLT，且蕴含「没有单一项占主导」（**Feller 条件** $\max_i\sigma_i^2/s_n^2\to 0$）。

**美学**：⭐⭐⭐⭐⭐ 极具构造性，洞察深刻。

**揭示**：正态分布是「在替换下唯一稳定的极限」——这是「为什么是正态」的最深答案。任何「温和的」（无主导项的）独立和，其极限只能是正态，别无选择。

**为什么只展开到三阶**：检验函数 $h$ 的一阶、二阶项在替换时被「同均值、同方差」的设定精确抵消（这就是为何要选 $G_i$ 与 $Y_i$ 同前两阶矩），残差从三阶起，故速率由三阶矩 $\mathbb E|Y|^3$ 主导。这个观察直接预告了路径 5 中 Berry–Esseen 常数 $\rho=\mathbb E|Y|^3/\sigma^3$ 的登场。

---

## 路径 5：Stein 方法（Charles Stein, 1972）

**思路**：唯一能给出**显式收敛速率**的证法。用刻画正态的微分方程作为「距离尺子」。

**关键步骤**：

1. **Stein 特征**：$Z\sim\mathcal N(0,1)$ 当且仅当对一切良行为 $f$ 有 $\mathbb E[f'(Z)-Zf(Z)]=0$。
2. 构造 **Stein 方程**：对任意有界检验函数 $h$，
$$f'(w)-w\,f(w)=h(w)-\mathbb E[h(Z)].$$
3. 对任意目标 $W$，$W$ 与 $Z$ 的距离（如 Kolmogorov 距离）
$$\sup_x|\mathbb P(W\leq x)-\Phi(x)|\leq C_h\cdot\sup_f\big|\mathbb E[f'(W)-Wf(W)]\big|.$$
4. 把 $W=T_n=\frac1{\sqrt n}\sum Y_i$ 代入，通过 Taylor 估计此上界，得到 **Berry–Esseen 定理**（Berry 1941 / Esseen 1942）：
$$\sup_x\left|\mathbb P(T_n\leq x)-\Phi(x)\right|\leq\frac{C\,\mathbb E|Y_1|^3}{\sigma^3\sqrt n},\quad C\approx 0.4748\ (\text{Tyurin 2010 最佳已知上界}).$$
   收敛速率明确为 $O(1/\sqrt n)$。$\square$

**美学**：⭐⭐⭐⭐ 从「定性收敛」升级到「定量收敛」，工业级精度。

**揭示**：在机器学习与统计中，知道「$n$ 多大才够接近正态」至关重要——Stein 方法是定量概率的核心工具。它告诉我们：三阶矩 $\mathbb E|Y|^3$ 越大（尾部越重），收敛越慢；这就是重尾分布「拒绝正态化」的精确度量。

**ML 工程联系**：Batch Normalization 的理论依据就是「mini-batch 均值经标准化后近似正态」——但 Berry–Esseen 提醒我们：batch size $n$ 太小或激活值重尾时，逼近质量会按 $1/\sqrt n$ 退化。同理，bootstrap 置信区间的覆盖率误差、A/B 测试样本量的选择，都直接依赖这个 $O(1/\sqrt n)$ 速率。

---

## 各路径对比表

| 证法 | 适用条件 | 所需工具 | 深刻度 | 能否给收敛速率 | 揭示的本质 |
| --- | --- | --- | --- | --- | --- |
| 1 de Moivre–Laplace | 仅二项分布 | Stirling 公式 | ⭐⭐ | 否（仅定性） | 正态 = 二项的极限 |
| 2 特征函数 + Lévy | i.i.d.，二阶矩 | 傅里叶分析、连续定理 | ⭐⭐⭐⭐⭐ | 否 | 卷积化乘积、调和分析 |
| 3 矩方法 | i.i.d.，**所有矩** | 组合计数、Carleman | ⭐⭐⭐ | 否 | 正态由前两阶矩决定 |
| 4 Lindeberg 替换 | 独立（不必同分布） | Taylor、三角阵列 | ⭐⭐⭐⭐⭐ | 否（但可推广给速率） | 正态 = 替换下唯一稳定极限 |
| 5 Stein 方法 | i.i.d.，三阶矩 | Stein 方程、Berry–Esseen | ⭐⭐⭐⭐ | **是，$O(1/\sqrt n)$** | 定量化、ML 与统计的最爱 |

---

## 哪条路径最能揭示本质？为什么

- **若问「最简洁普适」**：**路径 2（特征函数）**——一页纸证完最一般 i.i.d. CLT，是所有概率论教材的标配。它把概率问题翻译成调和分析问题，是「两个分支缝合处」的典范。
- **若问「最深刻」**：**路径 4（Lindeberg 替换）**——它揭示「正态是替换下唯一稳定的极限」，并给出最一般的 Lindeberg 条件（不必同分布，只要没有单一项占主导）。Terence Tao 多次公开推崇此法，认为它「真正解释了为什么是正态」。
- **若问「最实用」**：**路径 5（Stein 方法）**——定量给出收敛速率 $O(1/\sqrt n)$，是机器学习、统计推断、抽样理论的最爱。知道「$n$ 多大才够」是工程落地的前提。

**对学习者**：先读**路径 1**（de Moivre–Laplace，历史起点）建立「正态 = 二项极限」的直觉，再用**路径 2**（特征函数）掌握现代标准武器，最后用**路径 5**（Stein 方法）补上定量维度。路径 4 留作「想真正理解为什么」时的深读材料。

反过来理解：5 条路径合起来才完整回答了「**为什么正态分布如此中心**」——它既是离散的组合极限（路径 1），又是调和分析的自然不动点（路径 2），又是矩序列的唯一解（路径 3），又是替换下的稳定吸引子（路径 4），又是可定量逼近的标准尺度（路径 5）。每一面都是它「无处不在」的一个理由。

**5 条路径的共同主线**：尽管工具迥异，它们都收敛到同一句关键——**「二阶矩主导，高阶项随 $n$ 增长被 $1/\sqrt n$ 消去」**。特征函数法里 Taylor 展开到二阶、矩方法里「下标必须配对」、Lindeberg 替换里「同前两阶矩抵消残差」、Stein 方法里 Berry–Esseen 常数 $\rho$——全是这同一句的不同侧面。看穿这一点，就理解了 CLT 的「骨架」：正态性 = 二阶信息 + 高阶遗忘。

**给 ML 从业者的一句话**：CLT 不只是定理，它是整个频率派统计（置信区间、假设检验、z-test、t-test、bootstrap）的地基，也是 BatchNorm、知识蒸馏温度缩放、变分推断中「假设后验近似正态」的理论借口。理解 CLT 的边界（什么时候不近似？重尾？强相关？小样本？）比记住它的结论更重要。

---

## 推荐深入阅读

- **Patrick Billingsley**《Probability and Measure》⭐ —— 特征函数证法的标准教材出处，第 5 章清晰严谨。
- **William Feller**《An Introduction to Probability Theory and Its Applications》Vol. II ⭐ —— Lindeberg 条件与三角阵列 CLT 的经典论述（路径 4 的圣经级出处）。
- **Terence Tao**《Topics in Random Matrix Theory》附录 ⭐ —— Lindeberg 替换的精妙演绎，Tao 自己极推崇此法，称之为「CLT 最有洞察力的证明」。
- **Sheldon Ross**《Probability Models》第 7 章 —— de Moivre–Laplace 定理的历史脉络与完整推导。
- **Chen, Goldstein & Shao**《Normal Approximation by Stein's Method》⭐ —— Stein 方法专著，Berry–Esseen 常数的系统讨论。
- **math-expert** `04-concepts/概率收敛-多表征.md` —— 依分布收敛等四种收敛（依概率、几乎必然、$L^p$、依分布）的对照与直观。

---

## 收尾：Thurston 五模态自检

读完本篇后，用 William Thurston 的「理解数学的五种模态」逐一自检 CLT：

1. **人类语言**：能否用一句话向非数学专业的朋友解释「为什么正态分布无处不在」？
2. **视觉/空间**：能否在脑中画出「独立变量求和 → 直方图逐渐变钟形」的动画？
3. **逻辑演绎**：能否默写出特征函数证法的 4 个关键步骤？
4. **过程/算法**：能否写一段 Python 代码（采样 $n$ 个均匀分布、标准化、重复万次、画直方图叠加正态密度）验证 CLT？
5. **跨域类比**：能否把 CLT 类比到物理学中的「中心极限 / 统计力学」（大量微观自由度的宏观量趋向高斯分布）或信息论中的「最大熵原理」（固定方差下正态是熵最大的分布）？

五项都能回答「是」，才算是把 CLT 从「记住结论」推进到「多维度占有」。
