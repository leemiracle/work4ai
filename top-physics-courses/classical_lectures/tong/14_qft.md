# David Tong · Quantum Field Theory（量子场论）导读笔记

> Tong 系列第 14 本 | 难度 ★★★（研究生核心）| 配合：L11 量子场论 | **有视频！**

## §0 基本信息
- **作者**：David Tong（Cambridge，研究生 Part III 课程）
- **难度**：★★★（需要量子力学 + 经典场论 + 狭义相对论 + 复变函数）
- **篇幅**：约 155 页
- **链接**：davidtong.org/teaching/quantum-field-theory/ **（配有完整视频讲座！这是难得的免费 QFT 视频课）**
- **配合项目**：L11 量子场论
- **中文参考**：Peskin & Schroeder 中译本 / Zee《Quantum Field Theory in a Nutshell》

## §1 一句话定位
**现代物理的通用语言**——QFT 把量子力学、狭义相对论和场论融合，是粒子物理、凝聚态和弦论的共同基础。Tong 的版本以**正则量子化**为主线（区别于 Zee 的路径积分优先），配视频，是自学者首选。

## §2 前置知识（必须真会，不是"知道"）
- **量子力学**（Tong 06 全部 + 12 微扰论）：算符/态/测量/谐振子代数。如果你不会用产生湮灭算符 $a, a^\dagger$ 解谐振子，先回去学。
- **经典力学**（Tong 04 拉氏/哈氏）：拉格朗日量 $\mathcal{L}$、共轭动量 $\pi = \partial\mathcal{L}/\partial\dot{\phi}$、Hamiltonian。
- **狭义相对论**（Tong 02 后半）：四维记号 $x^\mu$、不变量 $p_\mu p^\mu = m^2$、张量指标升降。
- **经典场论**（Tong 05 电磁学）：麦克斯韦场作为场的范例。
- **复变函数**：围道积分（算 Feynman 传播子）、$\epsilon$ 极移技巧。
- **建议但非必须**：群论（SU(2), SU(3)）、路径积分概念。

> **铁律**：QFT 的难点不在"新概念"，而在"老概念的高密度组合"。前置不牢，必崩。

## §3 讲义全景（章节地图）

Tong 用**正则量子化**主线（先经典场→量子化→相互作用→Feynman图→Dirac场→QED）：

| 章 | 主题 | 核心问题 | 难点 |
|----|------|---------|------|
| 1 | 经典场论 | 场的拉氏量和守恒流 | Noether 定理 |
| 2 | 自由标量场（Klein-Gordon）| 怎么把场"量子化"？ | 产生湮灭算符 + 真空 |
| 3 | 相互作用场 | 粒子怎么散射？ | 相互作用绘景 + S 矩阵 |
| 4 | Feynman 图 | 散射振幅的图形计算 | Wick 定理 + 符号约定 |
| 5 | Dirac 场（旋量） | 费米子的量子场论 | γ 矩阵 + 反对易 |
| 6 | 量子电动力学（QED） | 电磁相互作用的 QFT | 规范固定 + 光子传播子 |
| 7 | 规范场（非阿贝尔） | Yang-Mills 理论预告 | 非阿贝尔自相互作用 |
| 8 | 重整化（如果含） | 消除无穷大 | 维度正规化 + 跑动耦合 |
| 9 | 对称性（如果含） | 全局/局域/离散对称 | Wilson 算符 |

## §4 核心章节拆解（深化版）

### §4.1 经典场论（第 1 章）—— 场的拉氏量与守恒律

**核心思想**：把粒子力学的拉格朗日方法推广到场。

- **拉氏密度** $\mathcal{L}(\phi, \partial_\mu\phi)$（注意是密度，作用量 $S = \int d^4x \, \mathcal{L}$）
- **Euler-Lagrange 方程**（对场）：
$$\partial_\mu \left(\frac{\partial\mathcal{L}}{\partial(\partial_\mu\phi)}\right) - \frac{\partial\mathcal{L}}{\partial\phi} = 0$$
- **Klein-Gordon 场**：$\mathcal{L} = \frac{1}{2}\partial_\mu\phi\,\partial^\mu\phi - \frac{1}{2}m^2\phi^2$，运动方程 $(\Box + m^2)\phi = 0$
- **共轭动量**：$\pi(x) = \partial\mathcal{L}/\partial\dot{\phi} = \dot{\phi}$
- **Hamiltonian 密度**：$\mathcal{H} = \pi\dot{\phi} - \mathcal{L} = \frac{1}{2}\pi^2 + \frac{1}{2}(\nabla\phi)^2 + \frac{1}{2}m^2\phi^2$

**Noether 定理（QFT 的灵魂）**：每个连续对称性 → 一个守恒流。
- 时间平移 → 能量守恒
- 空间平移 → 动量守恒
- 内部 U(1)（$\phi \to e^{i\alpha}\phi$）→ 荷守恒（如电荷）

**守恒流公式**：$j^\mu = \frac{\partial\mathcal{L}}{\partial(\partial_\mu\phi)}\,\delta\phi$，满足 $\partial_\mu j^\mu = 0$

**直觉图像**：场像一张绷紧的橡皮膜。拉氏量描述膜的"弹性"。Noether 定理说：如果膜在某个方向拉伸均匀（对称），就有相应的"守恒量"。

**反直觉点**：Noether 定理的深刻之处在于——**守恒律不是实验发现的规律，是对称性的数学必然**。能量守恒因为时间平移不变（宇宙今天和明天一样）。

---

### §4.2 自由标量场的量子化（第 2 章）—— QFT 的核心魔术

**核心问题**：怎么把一个经典场变成量子场？

**步骤**（正则量子化）：
1. **平面波展开**：解 Klein-Gordon 方程，通解是平面波叠加
$$\phi(\mathbf{x},t) = \int \frac{d^3p}{(2\pi)^3} \frac{1}{\sqrt{2E_\mathbf{p}}} \left(a_\mathbf{p} e^{-ipx} + a_\mathbf{p}^\dagger e^{ipx}\right)$$
其中 $E_\mathbf{p} = \sqrt{|\mathbf{p}|^2 + m^2}$。$a_\mathbf{p}, a_\mathbf{p}^\dagger$ 是待定的系数。

2. **量子化（对易关系）**：模仿谐振子，令
$$[a_\mathbf{p}, a_\mathbf{q}^\dagger] = (2\pi)^3 \delta^{(3)}(\mathbf{p}-\mathbf{q})$$
这把 $a, a^\dagger$ 解释为**产生/湮灭算符**。

3. **粒子诞生**：$a_\mathbf{p}^\dagger|0\rangle = |\mathbf{p}\rangle$（一个动量为 $\mathbf{p}$ 的粒子态）

4. **Hamiltonian**：
$$H = \int \frac{d^3p}{(2\pi)^3} \, E_\mathbf{p} \, a_\mathbf{p}^\dagger a_\mathbf{p} + \int d^3p \, E_\mathbf{p} \cdot \frac{1}{2}\delta^{(3)}(0)$$
**第二项是无穷大**——真空能量发散！这是 QFT 的第一个"无穷大危机"。

**真空能量与 Casimir 效应**：
- 表面看，真空能量无穷大是灾难
- 但只有**能量差**可观测。两块平行金属板间的真空能量密度比外部低 → **Casimir 力**（1948 预言，1997 实验验证）
- 真空不空，它在**涨落**

**Fock 空间**：多粒子态 $|p_1, p_2, \ldots\rangle = a_{p_1}^\dagger a_{p_2}^\dagger \cdots |0\rangle$。QFT 自然描述**可变粒子数**的系统（区别于固定 N 的量子力学）。

**直觉图像**：场像海洋。平静的海面 = 真空。一个波 = 一个粒子。两个波 = 两个粒子。粒子不是"小球"，是**场的振动**。

**反直觉点 1**：粒子数不守恒。高能碰撞可以"创造"粒子（$e^+e^- \to \mu^+\mu^-$）——因为场一直都在，只是能量转移激发了新的振动模式。

**反直觉点 2**：真空有结构。真空不是"什么都没有"，是场的**最低能态**，充满量子涨落。这是 Hawking 辐射、Unruh 效应的根源。

---

### §4.3 相互作用与 S 矩阵（第 3 章）—— 粒子怎么散射

**核心问题**：自由场好解，加了相互作用怎么办？

**相互作用绘景**（Interaction Picture）：
- 把 Hamiltonian 分成 $H = H_0 + H_{int}$
- $H_0$ 自由场（能精确解），$H_{int}$ 相互作用（小，做微扰）
- 态随 $H_{int}$ 演化，算符随 $H_0$ 演化

**时间演化算符**（Dyson 系列）：
$$U(t,t_0) = T\exp\left(-i\int_{t_0}^t dt' \, H_{int}(t')\right)$$
$T$ 是**编时算符**（按时间排序）——这看似无害，但导致 Feynman 图的出现。

**S 矩阵**（Scattering matrix）：$S = U(\infty, -\infty)$，描述"从无穷远过去到无穷远未来"的演化。

**跃迁振幅**：$\langle f | S | i \rangle$ = 从初态 $|i\rangle$ 到末态 $|f\rangle$ 的概率幅。实验测的散射截面正比于 $|\langle f|S|i\rangle|^2$。

**直觉图像**：两个粒子从远方来，相互作用一下（散射），飞向远方。S 矩阵编码"进来什么，出去什么"。

---

### §4.4 Feynman 图（第 4 章）—— QFT 的"发明"

**核心魔术**：把 Dyson 系列的每一项画成图，计算变成**画图+读图**。

**Wick 定理**：把编时乘积分解为"正规乘积 + 收缩"。收缩 $\langle 0|T\phi(x)\phi(y)|0\rangle$ 就是**Feynman 传播子** $D_F(x-y)$。

**Feynman 传播子**（动量空间）：
$$\tilde{D}_F(p) = \frac{i}{p^2 - m^2 + i\epsilon}$$
那个 $i\epsilon$ 看似多余，实际规定了**因果性**（粒子向前传播，反粒子向后）。

**Feynman 规则**（对 $\phi^4$ 理论 $\mathcal{L}_{int} = -\frac{\lambda}{4!}\phi^4$）：
- 内线（传播子）：$\frac{i}{p^2-m^2+i\epsilon}$
- 顶点：$-i\lambda$
- 外线：$1$
- 动量守恒：每个顶点 $\delta^{(4)}(\sum p)$
- 积分未定圈动量

**树图 vs 圈图**：
- **树图**（无圈）：有限，经典极限
- **圈图**（有圈）：**紫外发散**（积分到无穷大动量）→ 需要重整化

**散射振幅计算**（例子：$\phi^4$ 理论的 2→2 散射，树图）：
$$i\mathcal{M} = -i\lambda, \quad |\mathcal{M}|^2 = \lambda^2$$
$$\frac{d\sigma}{d\Omega} = \frac{\lambda^2}{64\pi^2 s}$$
（$s$ 是质心系能量平方）

**直觉图像**：Feynman 图是"粒子碰撞的故事"。线 = 粒子传播，顶点 = 相互作用发生。复杂的图 = 更高阶的量子修正。

**反直觉点 1**：Feynman 图不是"真实发生的物理过程"。它是**数学展开的图形编码**。同一个过程有无数个图（树图+1圈+2圈+...），加起来才是真实振幅。

**反直觉点 2**：反粒子 = 粒子向后时间传播。Feynman 的天才洞察：负能量解重新解释为"正能量的反粒子向后跑"。

---

### §4.5 Dirac 场（第 5 章）—— 费米子的 QFT

**Dirac 方程**（描述自旋 1/2 粒子，如电子）：
$$(i\gamma^\mu\partial_\mu - m)\psi = 0$$
$\gamma^\mu$ 是 4×4 矩阵（Dirac 矩阵），$\psi$ 是 4 分量旋量。

**Dirac 矩阵的代数**（Clifford 代数）：$\{\gamma^\mu, \gamma^\nu\} = 2\eta^{\mu\nu}$

**拉氏量**：$\mathcal{L} = \bar{\psi}(i\gamma^\mu\partial_\mu - m)\psi$，其中 $\bar{\psi} = \psi^\dagger\gamma^0$

**量子化（关键差异）**：费米子用**反对易关系**
$$\{a_\mathbf{p}, a_\mathbf{q}^\dagger\} = (2\pi)^3\delta^{(3)}(\mathbf{p}-\mathbf{q})$$
（不是玻色子的对易 $[a,a^\dagger]$）

**Pauli 不相容原理的 QFT 起源**：反对易 → 同一态不能有两个相同费米子（$a^\dagger_\mathbf{p}a^\dagger_\mathbf{p}|0\rangle = 0$）。**Pauli 原理不是假设，是 QFT + 自旋统计定理的必然**。

**反粒子的预言**：Dirac 方程有负能量解。Dirac 最初解释为"质子"（错），后来理解为**正电子**（反电子）。1932 年 Anderson 实验发现正电子——QFT 的第一个胜利。

**直觉图像**：旋量是"带自旋的场"。电子有两个自旋态，正电子也有两个，共 4 个分量。

**反直觉点**：自旋统计定理（玻色子整数自旋用对易，费米子半整数自旋用反对易）在非相对论量子力学里**无法证明**，只有 QFT + 狭义相对论 + 局域性能证明它。这是 QFT 比量子力学更深的标志。

---

### §4.6 QED（第 6 章）—— 最成功的物理理论

**QED 拉氏量**：
$$\mathcal{L} = -\frac{1}{4}F_{\mu\nu}F^{\mu\nu} + \bar{\psi}(i\gamma^\mu D_\mu - m)\psi$$
其中 $D_\mu = \partial_\mu + ieA_\mu$ 是**协变导数**，$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$。

**规范不变性**（U(1)）：$\psi \to e^{-i\alpha(x)}\psi$, $A_\mu \to A_\mu + \partial_\mu\alpha$。拉氏量不变。

**规范固定**：光子传播子依赖规范选择。Feynman 规范（$\partial_\mu A^\mu = 0$）下：
$$\tilde{D}_{F,\mu\nu}(k) = \frac{-i\eta_{\mu\nu}}{k^2 + i\epsilon}$$

**QED Feynman 规则**：
- 电子线：$\frac{i(\gamma^\mu p_\mu + m)}{p^2 - m^2 + i\epsilon}$
- 光子线：$\frac{-i\eta_{\mu\nu}}{k^2 + i\epsilon}$
- 顶点：$-ie\gamma^\mu$

**电子-缪子散射（e⁻μ⁻ → e⁻μ⁻）**：树图振幅
$$i\mathcal{M} = (-ie\gamma^\mu)_{ij} \frac{-i\eta_{\mu\nu}}{q^2} (-ie\gamma^\nu)_{kl}$$

**QED 的精度**：电子的反常磁矩
$$a_e = \frac{g-2}{2} = \frac{\alpha}{2\pi} + \cdots \approx 0.00115965218$$
理论与实验符合到 **12 位有效数字**——这是物理学最精确的预测。

**跑动耦合常数**：$\alpha(Q^2)$ 随能量变化。QED 的 $\alpha$ 在高能变大（屏蔽减弱）——QED 不是真正可重整化的（Landau 极点）。

**直觉图像**：QED 把"电磁力"重新描述为"交换光子"。两个电子排斥 = 一个虚光子在他们之间传递。

**反直觉点**：QED 如此成功，但它**不是终极理论**——它有 Landau 极点问题（极高能下耦合发散）。这暗示需要更深的理论（如电弱统一 / 大统一）。

---

### §4.7 非阿贝尔规范场（第 7 章）—— Yang-Mills 预告

**推广**：U(1)（电磁）→ SU(N)（非阿贝尔）

**Yang-Mills 拉氏量**：
$$\mathcal{L} = -\frac{1}{4}F^a_{\mu\nu}F^{a\mu\nu}, \quad F^a_{\mu\nu} = \partial_\mu A^a_\nu - \partial_\nu A^a_\mu + gf^{abc}A^b_\mu A^c_\nu$$

**关键差异**：$f^{abc}$（结构常数）非零 → 规范玻色子**自身带荷** → 胶子可以发射胶子（三胶子/四胶子顶点）。

**渐近自由**（Gross/Politzer/Wilczek 1973，2004 诺奖）：QCD 的耦合在高能**变弱**（与 QED 相反）。这解释了为什么强相互作用在短距离"弱"（可微扰），在长距离"强"（禁闭）。

→ 详见 [17_standard_model.md](17_standard_model.md) 和 [22_gauge_theory.md](22_gauge_theory.md)。

---

## §5 必做习题（具体）

| 题 | 内容 | 为什么必做 |
|----|------|----------|
| 2.1 | 推导 Klein-Gordon 场的 Hamiltonian | 验证能量正定 |
| 2.3 | 计算 $[H, a_\mathbf{p}^\dagger]$ | 理解 $a^\dagger$ 创造能量 $E_\mathbf{p}$ 的粒子 |
| 3.2 | 推导 $\phi^4$ 理论的 Feynman 规则 | 第一次自己"发明"Feynman 图 |
| 4.1 | 计算 $\phi^4$ 的 2→2 散射树图振幅 | 第一个散射截面 |
| 5.4 | 验证 Dirac 方程的平面波解 | 理解 u/v 旋量 |
| 6.1 | 计算 e⁻μ⁻ 散射的 $|\mathcal{M}|^2$ | QED 的核心计算 |
| 7.2 | 验证 QED 的 Ward 身份 $q_\mu\mathcal{M}^\mu = 0$ | 规范不变性的物理后果 |

**Tong 的习题表**在讲义末尾，配部分解答。建议**至少做完上表 7 题**才算入门。

## §6 读完后你应该能
- [ ] 推导 Klein-Gordon 场的量子化（平面波展开 + 对易关系）
- [ ] 解释为什么真空有能量（Casimir 效应）
- [ ] 用 Feynman 规则算 $\phi^4$ 的 2→2 散射树图
- [ ] 解释为什么费米子用反对易（自旋统计定理）
- [ ] 算 QED 电子-缪子散射的 $|\mathcal{M}|^2$
- [ ] 解释跑动耦合常数和渐近自由

## §7 与项目的映射
- **直接对应**：L11 量子场论
- **前置**：[06_quantum_mechanics.md](06_quantum_mechanics.md) + [05_electromagnetism.md](05_electromagnetism.md) + [04_classical_dynamics.md](04_classical_dynamics.md)
- **后续**：[17_standard_model.md](17_standard_model.md)（标准模型）/ [15_stat_field_theory.md](15_stat_field_theory.md)（凝聚态视角）/ [22_gauge_theory.md](22_gauge_theory.md)（拓扑）

## §8 延伸阅读
- **读完 Tong →** Peskin & Schroeder（标准教材，习题多）
- **路径积分视角 →** Zee *QFT in a Nutshell*（直觉优先，与 Tong 互补）
- **严谨数学 →** Weinberg *The Quantum Theory of Fields* vol 1-3（最权威但难）
- **凝聚态视角 →** Tong 自己的 [15_stat_field_theory.md](15_stat_field_theory.md)
- **历史 →** Schweber *QED and the Men Who Made It*（Feynman/Schwinger/Tomonaga/朝永的故事）
- **视频**：Tong 的 QFT 录像（讲义页面有链接）+ Sidney Coleman 的传奇讲座（Stanford，YouTube 有部分）

## §9 学习建议
- **节奏**：8-12 周（155 页，每周 15-20 页 + 做题）
- **怎么看视频**：Tong 的录像配合讲义，**每章先看视频再读 PDF**
- **陷阱**：
  - 不要跳过经典场论（第 1 章）——Noether 定理是后面所有对称性讨论的基础
  - Feynman 图的符号约定（$-i\lambda$ vs $+i\lambda$）容易搞错，对答案时检查
  - Dirac 矩阵的 $\gamma^0$ 是 Hermitian，$\gamma^i$ 是 anti-Hermitian——记错会全盘崩
  - 圈图发散不要被吓到——重整化在第 8 章（如果讲义含），先理解树图
- **关键洞察**：**QFT 的核心不是"新物理"，是"把已知的东西（量子+相对论+场）放一起"产生的涌现现象**（粒子数可变、真空涨落、反粒子、自旋统计）。这是 Anderson "More Is Different" 在基础物理的体现。

## §10 常见误区（深化新增）

### 🕳️ 误区 1：把 Feynman 图当"真实过程"
- ❌ "电子真的在画这些线"
- ✅ Feynman 图是**微扰展开的图形编码**，是数学工具。真实过程是整个振幅（所有图之和）。

### 🕳️ 误区 2：虚粒子"真的存在"
- ❌ "虚粒子是寿命短的粒子"
- ✅ 虚粒子是**数学项**，不满足 $E^2 = p^2 + m^2$（离壳）。它们不可观测。

### 🕳️ 误区 3：路径积分"更基本"
- ❌ "正则量子化是过时的，路径积分才是真理"
- ✅ 两者**等价**（在大多数理论里）。Tong 用正则是因为它更直观；Zee 用路径积分是因为它更优雅。都要会。

### 🕳️ 误区 4：重整化是"数学把戏"
- ❌ "重整化是把无穷大藏起来"
- ✅ Wilson 的重整化群观点：重整化揭示了**物理随尺度变化**的深刻结构（为什么不同尺度有不同有效理论）。这是物理洞察，不是把戏。

### 🕳️ 误区 5：QFT "完成"了
- ❌ "标准模型是终极理论"
- ✅ QFT 极其成功，但**无法容纳引力**，**无法解释暗物质/暗能量/中微子质量**。下一次革命还在等。

## §11 与其他 QFT 教材的对比（深化新增）

| 教材 | 风格 | 适合谁 | vs Tong |
|------|------|--------|---------|
| **Peskin & Schroeder** | 标准严谨，习题多 | 研究生主教材 | 比 Tong 更全更深，但更干 |
| **Zee** *QFT in a Nutshell* | 直觉优先，路径积分 | 想要"为什么"的人 | 与 Tong 互补（路径积分视角）|
| **Weinberg** vol 1-3 | 最严谨最深 | 进阶/参考 | 难，Tong 是它的入门 |
| **Srednicki** | 逻辑独特（先 spin 1/2）| 想换视角 | 章节顺序不同 |
| **Schwartz** *QFT and the Standard Model* | 现代友好 | 研究生 | 与 Tong 类似难度，更现代 |
| **Coleman**（录像/讲义）| 传奇教学 | 想看大师 | Stanford 录像珍贵 |

**建议组合**：**Tong（主读）+ Peskin（做题）+ Zee（直觉补充）** = QFT 自学三件套。

---

**完成日期**：2026-08-13（深化版 v2，从 142 行扩到 ~310 行）
**配套**：[tong/README.md](README.md) + [TEMPLATE.md](../TEMPLATE.md) + [ai_for_physics/](../../ai_for_physics/)
