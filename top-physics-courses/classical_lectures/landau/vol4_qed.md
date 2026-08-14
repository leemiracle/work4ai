
# Landau · Vol 4《量子电动力学》导读笔记

> Landau 系列第 04 本 | 难度 ★★★★★ | 配合：L11 量子场论

## §0 基本信息
- **作者**：V. B. Berestetskii, E. M. Lifshitz, L. P. Pitaevskii
- **年份 / 版本**：第 2 版（1982 英译）
- **难度**：★★★★★（10 卷中最难的几本之一）
- **篇幅**：约 450 页
- **配合项目**：L11 量子场论

## §1 一句话定位
**QED 的标准参考书**——协变微扰论、费曼图、辐射理论的完整处理。Landau 本人不仅写了这套教材的方法论基础，还在 1954-56 年与 Abrikosov、Khalatnikov 证明了 QED 有 **Landau 极点**——这是他对 QFT 的核心贡献之一。

## §2 前置知识
- 必须会：Landau Vol 2（经典场论）+ Vol 3（量子力学）+ 狭义相对论的协变表述
- 建议会：群论基础（Lorentz 群表示）、复变函数（围道积分）

## §3 讲义全景（章节地图）

| 章 | 标题 | 核心问题 |
|----|------|---------|
| 1-2 | 光子和相对论性粒子 | QED 的基本对象 |
| 3-4 | 狄拉克方程 | 相对论性电子 |
| 5-6 | 精确解与库仑势 | 精确vs微扰 |
| 7-8 | 散射的协变微扰论 | S 矩阵 |
| 9-10 | 不变振幅与费曼图 | 费曼规则 |
| 11-12 | 辐射 | 光子辐射 |
| 13-14 | 辐射修正 | 真空极化、自能 |
| 15-16 | 高阶修正 | 重整化 |

## §4 核心章节拆解（深化版）

### §4.1 光子与相对论性粒子（第 1-2 章）

**光子**：无质量、自旋 1 的玻色子。
- 只有**两种**物理偏振态（左旋/右旋圆偏振），而非 3 个——规范不变性消去了纵向极化
- 光子没有静止参考系（$m=0$），所以不能用通常的自旋量子化

**光子产生/湮灭算符**：
$$A_\mu(x) = \sum_{\mathbf{k},\lambda}\frac{1}{\sqrt{2\omega V}}\left(a_{\mathbf{k}\lambda}e_{\mu}^{(\lambda)}e^{-ikx} + a^\dagger_{\mathbf{k}\lambda}e_{\mu}^{(\lambda)*}e^{ikx}\right)$$

$\lambda = 1,2$ 为两个物理偏振，$e_\mu^{(\lambda)}$ 为偏振矢量。

**相对论性粒子的量子描述——Klein-Gordon 方程**：
$$(\Box + m^2)\phi = 0, \qquad \Box = \partial_\mu\partial^\mu$$

**KG 方程的困难**：概率密度不正定（$\rho$ 可以为负），负能量解无法自然解释。这促使 Dirac 寻找一阶方程。

**反直觉点**：光子只有 2 个偏振态（而非 3 个自旋投影），是因为无质量粒子的偏振由**螺旋度**（自旋在动量方向的投影）描述，只有 $\pm 1$ 两个值。这与有质量粒子的 $2s+1$ 个自旋态不同。

---

### §4.2 Dirac 方程（第 3 章）★ 核心基础

**Dirac 方程**（一阶相对论性波动方程）：
$$(i\gamma^\mu\partial_\mu - m)\Psi = 0$$

**$\gamma$ 矩阵满足 Clifford 代数**：
$$\{\gamma^\mu, \gamma^\nu\} = 2\eta^{\mu\nu}\mathbf{1}$$

$\gamma^\mu$ 是 $4\times 4$ 矩阵，$\Psi$ 是 4 分量 Dirac 旋量。

**Dirac 旋量的物理分解**：4 分量 = 2 自旋 × 正能/负能：
- $u_s(p)$：正能解（电子，$s = \uparrow, \downarrow$）
- $v_s(p)$：负能解重新诠释为**正电子**（反粒子）

**自由粒子 Hamiltonian**：
$$\hat{H} = \boldsymbol{\alpha}\cdot\hat{\mathbf{p}} + \beta m, \quad \alpha^i = \gamma^0\gamma^i, \quad \beta = \gamma^0$$

**自旋 1/2 自动出现**：Dirac 方程自然预言自旋 $1/2$——旋量在旋转下按 SU(2) 变换，自旋算符 $\hat{\mathbf{S}} = \frac{1}{2}\hat{\boldsymbol{\Sigma}}$（$\Sigma^i = \frac{1}{2}\epsilon^{ijk}\sigma^{jk}$）。

**螺旋度**：$\hat{h} = \hat{\boldsymbol{\Sigma}}\cdot\hat{\mathbf{p}}/|\mathbf{p}|$。无质量费米子的螺旋度是好量子数（左旋 vs 右旋）。

**反直觉点**：负能态被重新诠释为反粒子——这不是数学把戏。正电子在 1932 年被 Anderson 发现，证实了 Dirac 的预言。反粒子的存在是**相对论 + 量子力学的必然**。

---

### §4.3 电磁场中的 Dirac 粒子（第 4-5 章）

**最小耦合**：$\partial_\mu \to D_\mu = \partial_\mu + ieA_\mu$（协变导数）

**带电粒子在 Coulomb 场中**：
- 精确能级（不考虑辐射修正）：
$$E_{n,j} = mc^2\left[1 + \frac{(Z\alpha)^2}{\left(n - \delta_j\right)^2}\right]^{-1/2}$$
其中 $\delta_j = j + \frac{1}{2} - \sqrt{(j+\frac{1}{2})^2 - (Z\alpha)^2}$

- 这给出了氢原子的**精细结构**（比 Bohr 模型精确，但不含 Lamb 移动）

**Klein 佯谬**：超强电场（$Z\alpha \sim 1$）下，Dirac 方程预言真空产生电子-正电子对（Schwinger 机制的前身）。

**反直觉点**：Dirac 方程在 Coulomb 场中的精确解已经包含了自旋-轨道耦合和相对论修正——不需要微扰论。

---

### §4.4 协变微扰论与 S 矩阵（第 7-8 章）★ 全卷核心

**S 矩阵**（散射矩阵）：
$$S_{fi} = \langle f|S|i\rangle, \qquad S = T\exp\left(-i\int_{-\infty}^{\infty} H_{int}(t)\,dt\right)$$

$T$ 为编时算符（按时间排列算符乘积）。

**跃迁概率**：
$$dw = 2\pi|M_{fi}|^2\delta(E_f - E_i)\,d\nu_f$$

$\delta(E_f - E_i)$ 保证能量守恒，$M_{fi}$ 为**不变振幅**（Lorentz 不变量）。

**散射截面**：
$$d\sigma = \frac{1}{4\sqrt{(p_1\cdot p_2)^2 - m_1^2 m_2^2}}|M_{fi}|^2\,d\Phi$$

**不变相空间**（Lorentz 不变的末态体积元）：
$$d\Phi = (2\pi)^4\delta^{(4)}\!\left(\sum p\right)\prod_f \frac{d^3p_f}{(2\pi)^3 2E_f}$$

**直觉图像**：S 矩阵编码"进来什么，出去什么"。散射截面 = $|振幅|^2 \times$ 相空间因子。

**反直觉点**：散射问题不需要知道碰撞的时间细节——只需知道渐近态（远过去和远未来）和相互作用的总效果。

---

### §4.5 Feynman 图与 QED 规则（第 9-10 章）

**QED 拉氏量**：
$$\mathcal{L} = -\frac{1}{4}F_{\mu\nu}F^{\mu\nu} + \bar{\psi}(i\gamma^\mu D_\mu - m)\psi$$

$D_\mu = \partial_\mu + ieA_\mu$，$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$。

**规范不变性**（U(1)）：$\psi \to e^{-i\alpha(x)}\psi$，$A_\mu \to A_\mu + \frac{1}{e}\partial_\mu\alpha$。

**QED Feynman 规则**：
| 元素 | 表达式 |
|------|--------|
| 电子传播子 | $S_F(p) = \frac{i(\gamma^\mu p_\mu + m)}{p^2 - m^2 + i\epsilon}$ |
| 光子传播子 | $D_{\mu\nu}(k) = \frac{-i\eta_{\mu\nu}}{k^2 + i\epsilon}$（Feynman 规范）|
| 顶点 | $-ie\gamma^\mu$ |
| 外线（电子）| $u_s(p)$ / $\bar{u}_s(p)$ |
| 外线（光子）| $e_\mu^{(\lambda)}$ |

**经典过程的树图计算**：
- **Compton 散射**（$\gamma + e^- \to \gamma + e^-$）：两个树图（s 道和 u 道），→ Klein-Nishina 公式
- **电子-缪子散射**（$e^-\mu^- \to e^-\mu^-$）：t 道光子交换
- **Bhabha 散射**（$e^+e^- \to e^+e^-$）：s 道 + t 道

**Klein-Nishina 公式**（Compton 散射微分截面）：
$$\frac{d\sigma}{d\Omega} = \frac{r_e^2}{2}\left(\frac{\omega'}{\omega}\right)^2\left(\frac{\omega'}{\omega} + \frac{\omega}{\omega'} - \sin^2\theta\right)$$

$r_e = e^2/(mc^2)$ 为经典电子半径。低能极限（$\omega \ll mc^2$）回到 Thomson 散射。

**反直觉点 1**：Feynman 图不是"真实发生的物理过程"。它是 Dyson 级数展开的图形编码——同一个过程有无数个图（树图 + 1 圈 + 2 圈 + …），加起来才是精确振幅。

**反直觉点 2**：反粒子 = 粒子向**后**传播。Feynman 的洞察：负能量解重新解释为"正能量的反粒子在时间中倒退"。

---

### §4.6 辐射修正与重整化（第 13-15 章）

**圈图修正的来源**：树图只是一阶近似。更高阶的图包含**闭合圈**（虚粒子圈），导致紫外发散。

**三类基本发散**：
1. **真空极化**（光子自能圈）：虚 $e^+e^-$ 对屏蔽电荷 → 电荷重整化
2. **电子自能**（电子自能圈）：虚光子修正电子质量和波函数 → 质量重整化
3. **顶点修正**：顶点处的辐射修正

**电子反常磁矩**（$g-2$）：
$$a_e = \frac{g-2}{2} = \frac{\alpha}{2\pi} + \text{(higher orders)} \approx 0.00115965218$$

Schwinger 1948 年计算了第一阶修正 $\alpha/2\pi$。理论与实验符合到 **12 位有效数字**——物理学最精确的预测。

**Lamb 移动**：氢原子 $2S_{1/2}$ 和 $2P_{1/2}$ 能级的微小差异（Dirac 方程预言它们简并）。来自真空极化 + 电子自能修正。

**跑动耦合常数**：有效电荷随能量变化
$$\alpha(Q^2) = \frac{\alpha(0)}{1 - \frac{\alpha(0)}{3\pi}\ln(Q^2/m^2e^2)}$$

高能时 $\alpha$ 变大（屏蔽减弱）——但增大有极限。

**Landau 极点**（Landau-Abrikosov-Khalatnikov, 1954-56）：在极高能标 $\Lambda_L$ 处，QED 耦合发散：
$$\Lambda_L \sim m_e \exp\left(\frac{3\pi}{2\alpha}\right) \sim 10^{286}\,\text{eV}$$

这意味着 QED 在极高能不自洽——不是终极理论。Landau 对此极为不满，甚至质疑 QFT 本身的有效性。这个问题后来由 **QCD 的渐近自由**（Gross, Politzer, Wilczek 1973）给出了出路——非阿贝尔理论在高能变弱而非变强。

**反直觉点 1**：QED 的重整化物理上极度成功（$10^{-12}$ 精度），但**数学上不严格**——微扰级数是渐近展开（不是收敛级数），圈图积分无穷大。

**反直觉点 2**：Landau 极点表明 QED 不是终极理论。但 Landau 本人因此对 QFT 持悲观态度——他认为 QFT 需要根本性改变。历史证明他部分正确（QCD 解决了某些问题），但 QFT 框架本身 survived。

## §5 关键推导与思考题

| # | 内容 | 为什么重要 |
|---|------|----------|
| 1 | 验证 Dirac 方程平面波解 $u_s(p)$, $v_s(p)$ | 理解费米子和反费米子态 |
| 2 | 推导 Compton 散射的 Klein-Nishina 公式 | QED 标志性结果 |
| 3 | 计算电子 $g-2$ 的 Schwinger 一阶修正 $\alpha/(2\pi)$ | 最精确物理理论的验证 |
| 4 | 理解真空极化对电荷的屏蔽效应 | 跑动耦合常数的起源 |
| 5 | 画出并计算 $e^+e^- \to \mu^+\mu^-$ 的树图 | QED 核心计算练习 |
| 6 | 理解 Landau 极点的物理含义 | QED 的根本局限性 |
| 7 | 推导 Lamb 移动的定性起源 | 精细结构修正 |

## §6 读完后你应该能
- [ ] 写出 QED 的拉氏量并解释规范不变性
- [ ] 用 Feynman 规则计算树图散射截面
- [ ] 理解 Dirac 方程如何预言自旋 1/2 和反粒子
- [ ] 解释真空极化和跑动耦合常数
- [ ] 理解重整化的物理意义和 Landau 极点
- [ ] 欣赏 QED 作为"最精确物理理论"的地位及其局限

## §7 与项目的映射
- **直接对应**：L11 量子场论
- **本科/研究生入门**：先用 [../tong/14_qft.md](../tong/14_qft.md) 学基础，再查 Landau Vol 4 做参考
- **进阶**：Peskin & Schroeder（更现代的 QFT 教材）

## §8 延伸阅读
- **Tong 14** *QFT*（免费，有视频，更友好）
- **Peskin & Schroeder** *An Introduction to QFT*（标准现代教材）
- **Weinberg** *The Quantum Theory of Fields*（更全面但更难）
- **Schwaber** *QED and the Men Who Made It*（历史：Feynman/Schwinger/Tomonaga）

## §9 学习建议
- **节奏**：20+ 周（极难）
- **怎么读**：**不要用 Landau Vol 4 当第一本 QFT 教材**。先学 Tong 或 Peskin，再把 Landau 当参考
- **陷阱**：符号体系老旧（CGS 度量符号约定等），需要转换
- **Landau 与 QFT**：Landau 自己在 1954-56 年（与 Abrikosov、Khalatnikov）证明了 QED 的 Landau 极点——耦合在极高能发散。这使他对 QFT 框架产生怀疑。1962 年车祸后他无法继续研究，这个问题的最终解决（QCD 渐近自由, 1973）他没有看到。Vol 4 后续修订由 Lifshitz 和 Pitaevskii 完成。
- **关键洞察**：**QED 是物理学最精确的理论（$10^{-12}$），但它有 Landau 极点——不是终极理论。Landau 本人发现了这个局限。**

## §10 常见误区（深化新增）

### 🕳️ 误区 1：负能海真实存在
- ❌ "真空充满负能电子海"
- ✅ Dirac 海是历史图像。现代观点：正电子是独立粒子，费米子场的量子化自然产生反粒子，不需要"海"。

### 🕳️ 误区 2：虚粒子"真的存在"
- ❌ "虚粒子是寿命极短的粒子"
- ✅ 虚粒子是**数学项**——传播子的内部线，不满足质壳条件 $p^2 = m^2$（离壳）。它们不可观测，是微扰展开的中间步骤。

### 🕳️ 误区 3：Feynman 图是真实物理过程
- ❌ "电子真的在画这些线"
- ✅ Feynman 图是**微扰展开的图形编码**。同一个过程有无数个图，加起来才是精确振幅。单个图没有物理意义。

### 🕳️ 误区 4：重整化是"藏无穷大的把戏"
- ❌ "重整化只是把无穷大吸收进重新定义的参数"
- ✅ Wilson 的重整化群观点：重整化揭示了**物理随尺度变化**的深刻结构（不同尺度有不同的有效理论）。这是物理洞察，不是数学把戏。

### 🕳️ 误区 5：QED 是终极理论
- ❌ "QED 如此精确，它是最终的电磁理论"
- ✅ QED 有 **Landau 极点**（极高能耦合发散），无法容纳引力，无法解释暗物质。Landau 本人发现了这个局限——QED 不是终点。

## §11 与其他 QFT/QED 教材的对比（深化新增）

| 教材 | 风格 | 适合谁 | vs Landau |
|------|------|--------|-----------|
| **Berestetskii-Lifshitz-Pitaevskii** | 协变微扰论经典、详尽 | 参考级 | — |
| **Peskin & Schroeder** | 标准现代、友好 | 研究生主读 | 比 Landau 友好现代 |
| **Weinberg** | 最严谨最深 | 进阶参考 | 难，Landau 的进阶 |
| **Srednicki** | 逻辑独特（先 spin 1/2） | 换视角 | 章节顺序不同 |
| **Schwartz** | 现代友好 | 研究生 | 与 Peskin 类似难度 |
| **Tong 14** | 免费有视频、最友好 | 入门 | 比 Landau 友好得多 |

**建议组合**：**Tong 14（入门）→ Peskin（主读做题）→ Landau Vol 4（经典参考+Landau 极点）**

---

**完成日期**：2026-08-13（深化版 v2）
**配套**：[README.md](README.md) + [tong/14_qft.md](../tong/14_qft.md)
