# David Tong · Kinetic Theory（动理论/非平衡统计）导读笔记

> Tong 系列第 16 本 | 难度 ★★★（研究生）| 配合：L05 非平衡统计

## §0 基本信息
- **作者**：David Tong（Cambridge，研究生 Part III）
- **难度**：★★★（需要统计物理 + 偏微分方程）
- **篇幅**：约 100 页
- **链接**：davidtong.org/teaching/kinetic-theory/
- **配合项目**：L05 热力学与统计物理（非平衡部分）

## §1 一句话定位
**非平衡统计力学**——从微观碰撞推导宏观输运方程，理解时间箭头和布朗运动。

## §2 前置知识
- 必须会：统计物理（07 的系综 + 配分函数）、偏微分方程、经典力学（碰撞/散射）
- 建议会：概率论、随机过程基础

## §3 讲义全景（章节地图）

| 章 | 主题 | 核心问题 |
|----|------|---------|
| 1 | Liouville 方程 | 相空间中的概率分布怎么演化？|
| 2 | BBGKY 层级 | 从多体到少体的约化 |
| 3 | Boltzmann 方程 | 碰撞的统计效应 |
| 4 | H 定理 | 为什么熵总是增加？|
| 5 | 输运系数 | 粘性/热导/扩散怎么算？|
| 6 | 随机过程 | Langevin 方程和布朗运动 |
| 7 | 线性响应 | Kubo 公式 |

## §4 核心章节拆解（深化版）

### §4.1 Liouville 方程 —— 相空间流的可逆性

**核心概念**：$N$ 粒子系统的相空间概率密度 $\rho(\mathbf{q}^N, \mathbf{p}^N, t)$ 服从 Liouville 方程。

**Liouville 方程**（从哈密顿方程推导）：
$$\frac{\partial \rho}{\partial t} = \{H, \rho\} = -\sum_i \left(\dot{q}_i \frac{\partial \rho}{\partial q_i} + \dot{p}_i \frac{\partial \rho}{\partial p_i}\right)$$

等价于 $\frac{d\rho}{dt} = 0$（沿轨迹的全导数为零）。

**Liouville 定理**：相空间体积在哈密顿流下保持不变——概率密度像不可压缩流体。

**直觉图像**：相空间中的概率"流体"像不可压缩的水一样流动——它可以拉伸、折叠，但**永远不能压缩**。一小团相空间点在演化中保持体积不变。

**反直觉点**：Liouville 方程是**时间可逆的**——如果 $\rho(q,p,t)$ 是解，那么 $\rho(q,-p,-t)$ 也是解。但宏观上熵只增不减——这就是"不可逆性悖论"（irreversibility paradox），是统计力学最深刻的谜题。

---

### §4.2 BBGKY 层级 —— 层层递进的约化

**核心概念**：从 $N$ 粒子分布到单粒子分布的层级约化。Bogoliubov–Born–Green–Kirkwood–Yvon hierarchy。

**约化分布函数**：
$$f_1(\mathbf{p}_1) = \int dq_2 \cdots dq_N \, \rho, \quad f_2(\mathbf{p}_1, \mathbf{p}_2) = \int dq_3 \cdots dq_N \, \rho$$

**BBGKY 层级**（显式形式）：$f_1$ 的方程涉及 $f_2$，$f_2$ 的方程涉及 $f_3$……无穷链条。第一级的精确方程为：
$$\frac{\partial f_1}{\partial t} + \{H_1, f_1\} = \int d^3x_2\, d^3p_2\, \{V_{12}, f_{12}\}$$
其中 $f_{12} = f_2(\mathbf{x}_1, \mathbf{p}_1, \mathbf{x}_2, \mathbf{p}_2, t)$ 是两粒子联合分布。第二级 $f_2$ 的方程右边会出现 $f_3$（三粒子分布），依此类推——这就是 **BBGKY 塔**。

**截断方式**（这是关键近似）：
- $f_2 \approx f_1 f_1$（分子混沌 / Stosszahlansatz）→ **Boltzmann 方程**
- $f_2 \approx f_1 f_1 +$ 平均场 → **Vlasov 方程**

**分子混沌假设**（正式表述）：Stosszahlansatz 假定
$$f_2(\mathbf{p}_1, \mathbf{p}_2, t) \approx f_1(\mathbf{p}_1, t)\cdot f_1(\mathbf{p}_2, t) \quad \textbf{在碰撞之前}$$
但**不**假定碰撞之后仍然成立。碰撞会建立短程关联，但下一次碰撞前这关联又已衰减。这种"碰撞前独立、碰撞后关联"的**时间不对称**假设，正是 BBGKY 链条被截断、时间箭头被引入的数学位置。

**直觉图像**：要知道一个粒子的行为，需要两个粒子的关联；要知道两个粒子的关联，需要三个粒子的信息——像一个永远打不开的俄罗斯套娃。

**反直觉点**：截断处正是不可逆性进入的地方——通过假设 $f_2 \approx f_1 f_1$（碰撞前不相关），我们**打破了时间反演对称性**。可逆的微观定律 + 不可逆的近似 = 宏观时间箭头。

---

### §4.3 Boltzmann 方程 —— 碰撞的统计效应

**核心概念**：单粒子分布函数 $f(\mathbf{x}, \mathbf{p}, t)$ 的演化方程。

**Boltzmann 方程**：
$$\frac{\partial f}{\partial t} + \frac{\mathbf{p}}{m} \cdot \nabla_x f + \mathbf{F} \cdot \nabla_p f = C[f]$$

**碰撞积分**（二元弹性碰撞）：
$$C[f_1] = \int d^3p_2 \, d\Omega \, |v_1 - v_2| \frac{d\sigma}{d\Omega} \left[f_1' f_2' - f_1 f_2\right]$$

**完整记号**（用跃迁率 $W$）：等价地把碰撞项写成
$$C[f] = \int d^3p_2\, d^3p_1'\, d^3p_2'\, W(\mathbf{p}_1,\mathbf{p}_2|\mathbf{p}_1',\mathbf{p}_2')\,[f_1' f_2' - f_1 f_2]$$
其中 $W$ 是跃迁率（来自 Fermi 黄金法则 / 散射截面）。能量和动量守恒 $\delta(E_1'+E_2'-E_1-E_2)\,\delta^3(\mathbf{p}_1'+\mathbf{p}_2'-\mathbf{p}_1-\mathbf{p}_2)$ 限制着积分。

"$f'f' - ff$" 结构：**增益项**（散射进入 $p_1$）减去**损失项**（散射离开 $p_1$）。

**分子混沌**（Stosszahlansatz）：碰撞前速度不相关：$f_2(\mathbf{p}_1, \mathbf{p}_2) = f_1(\mathbf{p}_1) f_1(\mathbf{p}_2)$。

**平衡态推导**：$C[f_{eq}] = 0$ 要求**细致平衡** $f_1' f_2' = f_1 f_2$。两边取对数：
$$\ln f_1' + \ln f_2' = \ln f_1 + \ln f_2$$
这说明 $\ln f$ 是**碰撞不变量**——在碰撞中守恒的量的线性组合。弹性碰撞的不变量只有粒子数、动量、动能，所以
$$\ln f = a + \mathbf{b}\cdot\mathbf{p} + c\, p^2 \quad\Longrightarrow\quad f_{eq} = n \left(\frac{m}{2\pi k_B T}\right)^{3/2} e^{-p^2/2mk_BT}$$
即 **Maxwell-Boltzmann 分布**（在质心系中 $\mathbf{b}=0$，$a,c$ 由 $n,T$ 定）。

**直觉图像**：碰撞随机化动量 → 驱动系统趋向 Maxwell-Boltzmann 分布。碰撞项是一个"工厂"，源源不断地生产熵。

**反直觉点**：分子混沌假设通过假定碰撞前（而非碰撞后）的独立性，打破了时间反演对称性。这种不对称性就是**时间箭头的微观起源**。

---

### §4.4 H 定理 —— 从可逆到不可逆

**核心概念**：Boltzmann 定义的 $H$ 函数只减不增。

**$H$ 函数**：$$H[f] = \int f \ln f \, d^3p$$

Boltzmann 用 Boltzmann 方程证明了 $\frac{dH}{dt} \leq 0$。这意味着熵 $S = -k_B H + \text{const}$ 只增不减——**热力学第二定律从微观定律推导出来！**

**形式证明**（关键步骤）：
$$\frac{dH}{dt} = \int d^3p_1\, (1 + \ln f_1)\, \frac{\partial f_1}{\partial t} = \int d^3p_1\, (1+\ln f_1)\, C[f_1]$$
利用碰撞积分在对称性（交换 $1\leftrightarrow 2$、碰撞前 $\leftrightarrow$ 碰撞后）下的不变性，可以重写为对称形式：
$$\frac{dH}{dt} = \frac{1}{4}\int d^3p_1\, d^3p_2\, d\Omega\, |v_1-v_2|\frac{d\sigma}{d\Omega}\,(f_1'f_2' - f_1f_2)\ln\frac{f_1'f_2'}{f_1f_2} \leq 0$$
最后的不等号成立，是因为对任意 $x,y>0$ 恒有 $(x-y)\ln(x/y) \geq 0$（令 $x=f_1'f_2'$，$y=f_1f_2$）。这个优雅的证明**只用到了 $x\ln x$ 的凸性**！等号当且仅当 $f_1'f_2'=f_1f_2$（细致平衡，即平衡态）时成立。

**Loschmidt 佯谬**：微观定律时间可逆，但 $dH/dt \leq 0$——矛盾？解决：H 定理是**统计性的**，不是绝对的。熵可以减小，但概率 $\sim e^{-N}$（$N \sim 10^{23}$）。

**Zermelo 佯谬**：Poincaré 回归说系统最终回到初始态 → H 必然增加。解决：回归时间 $\sim e^N$ 天文数字般巨大。

**直觉图像**：墨水滴入水中——它扩散（H 减小）。反向播放：墨水重新聚集——物理上可能，但需要荒谬特殊的初始条件。

**反直觉点**：时间箭头来自**概率**，而不是基本定律。宇宙的低熵初始态（大爆炸）才是时间箭头的最终原因。

---

### §4.5 输运系数 —— 微观到宏观的桥梁

**核心概念**：从 Boltzmann 方程推导宏观输运系数。

**Chapman-Enskog 展开**：在 Knudsen 数（$Kn = \ell/L$ = 平均自由程/宏观尺度）小的情况下展开 $f = f^{(0)} + f^{(1)} + \cdots$。

- **零阶**：局域平衡（带局域 $T(\mathbf{x},t)$, $n(\mathbf{x},t)$, $\mathbf{u}(\mathbf{x},t)$ 的 Maxwell-Boltzmann）
- **一阶**：给出 Navier-Stokes 方程及输运系数

**硬球结果**：
$$\eta = \frac{5}{16}\frac{\sqrt{\pi m k_B T}}{\pi d^2}, \quad \kappa = \frac{75}{64}\frac{k_B\sqrt{\pi m k_B T}}{\pi d^2}, \quad D = \frac{3}{8}\frac{\sqrt{\pi k_B T/m}}{n d^2}$$

**惊人结果**：$\eta$ 与**密度无关**（低密度极限下）！

**直觉图像**：输运 = 分子携带动量/能量/粒子跨越宏观距离。分子越多 = 载流子越多，但平均自由程越短——**精确抵消**。

**反直觉点**：理想气体的粘性随温度**升高**而增大（与液体相反！）——因为更快分子输运更多动量，尽管平均自由程更短。

---

### §4.6 Langevin 方程与布朗运动 —— 涨落与耗散

**核心概念**：用随机力描述热涨落。

**Langevin 方程**（布朗粒子）：
$$m\dot{v} = -\gamma v + \xi(t), \quad \langle \xi(t) \rangle = 0, \quad \langle \xi(t)\xi(t')\rangle = 2D\delta(t-t')$$

**涨落-耗散定理**（Einstein 关系）：$D = \gamma k_B T / m$——摩擦系数和噪声强度被锁在一起！

**推导**：稳态下能量均分 $\langle v^2\rangle = k_B T/m$。从 Langevin 方程：$\langle v^2\rangle = D/(\gamma\tau)$，其中 $\tau = m/\gamma$。等价：$D = k_B T / m \cdot \tau = k_B T/\gamma$。Einstein 关系：$D = \mu k_B T$（$\mu = 1/\gamma$ 为迁移率）。

**Ornstein-Uhlenbeck 过程**：Langevin 方程是 OU 过程，给出速度自关联函数
$$\langle v(t)v(0)\rangle = \frac{k_BT}{m}\,e^{-|t|/\tau}, \quad \tau = \frac{m}{\gamma}$$
**扩散常数**（Green-Kubo 形式）：
$$D = \int_0^\infty \langle v(t)v(0)\rangle\, dt = \frac{k_BT}{m}\cdot\tau = \frac{k_BT}{m\gamma}$$
这就是从第一性原理导出的 **Einstein 关系**。**均方位移**分两个区间：
$$\langle x^2(t)\rangle = \begin{cases} (k_BT/m)\, t^2 & t \ll \tau \text{（弹道区，自由粒子）}\\ 2Dt & t \gg \tau \text{（扩散区，随机游走）}\end{cases}$$

**直觉图像**：同样的分子碰撞同时产生摩擦（系统性拖曳）和噪声（随机踢击）——它们是一枚硬币的两面。

**反直觉点**：涨落-耗散定理意味着你**不能只有摩擦而无噪声**。任何在温度 $T$ 下的耗散系统，都**必然**有精确确定的涨落幅度。

---

### §4.7 线性响应与 Kubo 公式 —— 平衡关联决定非平衡响应

**核心概念**：系统对外部微扰的响应可以用平衡关联函数表达。

**微扰**：弱外场 $F(t)$ 耦合到观测量 $A$：$H = H_0 - F(t)A$。

**线性响应**：
$$\delta\langle B(t)\rangle = \int_{-\infty}^t dt' \, \chi_{BA}(t-t') F(t')$$

**响应函数**（Kubo 公式 / 推迟格林函数）：
$$\chi_{BA}(t) = -\frac{i}{\hbar}\theta(t)\langle [B(t), A(0)]\rangle_{eq}$$

**电导率**：
$$\sigma(\omega) = \frac{1}{k_BT} \int_0^\infty dt \, e^{i\omega t} \langle J(t) J(0)\rangle_{eq}$$

**Kramers-Kronig 关系**：$\text{Re}\,\chi$ 和 $\text{Im}\,\chi$ 互为 Hilbert 变换（因果性约束）。

**直觉图像**：系统对踢击的响应取决于它的内部涨落谱——"自由时怎么晃"决定了"被推时怎么应"。

**反直觉点**：Kubo 公式把**非平衡性质**（输运系数）用**平衡关联函数**表达。你不需要解非平衡问题——只需测量平衡涨落！

## §5 必做习题（具体）

| 题 | 内容 | 为什么必做 |
|----|------|----------|
| 1.1 | 从哈密顿方程推导 Liouville 方程 | 理解相空间流的可逆性 |
| 2.3 | 验证 Maxwell-Boltzmann 分布是 Boltzmann 方程的平衡解 | 理解碰撞项的平衡条件 |
| 3.2 | 证明 H 定理 $dH/dt \leq 0$ | 从微观可逆定律导出宏观不可逆性 |
| 4.1 | Chapman-Enskog 展开推导理想气体粘性系数 | 理解输运系数的微观起源 |
| 5.3 | 从 Langevin 方程推导 Einstein 关系 $D = \mu k_BT$ | 涨落-耗散定理的核心实例 |
| 6.2 | 验证 Kubo 公式给出正确的直流电导率 | 非平衡性质 ← 平衡关联函数 |

## §6 读完后你应该能
- [ ] 写出 Liouville 方程并解释相空间体积不变
- [ ] 理解 BBGKY 层级和分子混沌假设
- [ ] 解释 H 定理和 Loschmidt 佯谬
- [ ] 从 Boltzmann 方程推导输运系数
- [ ] 解释涨落-耗散定理的物理意义
- [ ] 用 Kubo 公式计算简单系统的响应函数

## §7 与项目的映射
- **前置**：07_statistical_physics.md + 04_classical_dynamics.md
- **后续**：15_stat_field_theory.md（相变的场论处理用到平衡关联函数）
- **AI for Physics**：非平衡统计是理解扩散模型、生成模型的数学基础
- **对应**：L05 热力学与统计物理（非平衡部分）

## §8 延伸阅读
- 教材 → Kardar *Statistical Physics of Particles*（第 11-12 章涵盖动理论）
- 教材 → Huang *Statistical Mechanics*（第 4-5 章动理论详细）
- 深入 → Zubarev *Nonequilibrium Statistical Thermodynamics*
- 经典 → Kubo 的 1966 年 review（涨落-耗散定理）
- 科普 → Penrose *The Emperor's New Mind*（时间箭头的讨论）

## §9 学习建议
- **节奏**：4-6 周
- **怎么读**：核心是 Boltzmann 方程和 H 定理——理解时间箭头怎么从可逆微观定律中涌现
- **陷阱**：
  - 分子混沌假设是**近似**，不是精确原理——它引入了时间箭头
  - H 定理说"几乎总是"熵增，不是"绝对总是"——Poincaré 回归说系统最终会回到初始态（但需要 $10^{10^{23}}$ 年）
  - 涨落-耗散定理只适用于**近平衡**——远离平衡时需要更复杂的理论
- **关键洞察**：动理论的核心洞察是——**不可逆性从可逆微观定律中涌现**。这是统计物理最深刻的悖论和最优雅的解答。分子混沌假设 + 大数定律 → 时间箭头。理解了这一点，你就理解了为什么鸡蛋不能复原、为什么时间只朝一个方向流。

## §10 常见误区（深化新增）

### 🕳️ 误区 1：Liouville 方程导致熵增
- ❌ "Liouville 方程导致熵增"
- ✅ Liouville 方程完全时间可逆——熵增来自**分子混沌假设**（截断 BBGKY 层级时引入的近似）。Liouville 方程本身既不增加也不减少熵。

### 🕳️ 误区 2：H 定理说熵绝对只增不减
- ❌ "H 定理说熵绝对只增不减"
- ✅ H 定理是**统计性**的——熵可以减小，但概率为 $e^{-N}$（$N\sim 10^{23}$）。Poincaré 回复说系统最终会回到初始态，但需要 $10^{10^{23}}$ 年。

### 🕳️ 误区 3：理想气体粘性与密度成正比
- ❌ "理想气体粘性与密度成正比"
- ✅ Chapman-Enskog 给出 $\eta \propto \sqrt{T}/d^2$，与密度无关（密度增大 → 更多载流子，但平均自由程更短，**精确抵消**）。

### 🕳️ 误区 4：涨落和耗散是独立现象
- ❌ "涨落和耗散是独立现象"
- ✅ 涨落-耗散定理锁定两者——同一物理过程（分子碰撞）同时产生噪声和摩擦，比例为 $D = \gamma k_B T / m$。

### 🕳️ 误区 5：Kubo 公式需要解非平衡问题
- ❌ "Kubo 公式需要解非平衡问题"
- ✅ Kubo 把非平衡输运系数用**平衡关联函数**表达——只需平衡态的涨落谱。

## §11 跨教材对比（深化新增）

| 教材 | 风格 | 适合谁 | vs Tong |
|------|------|--------|---------|
| Kardar *Statistical Physics of Particles* | 现代简洁 | 研究生标准 | 第 11-12 章涵盖动理论 |
| Huang *Statistical Mechanics* | 经典全面 | 研究生 | 动理论章节更详细 |
| Landau & Lifshitz vol.10 *Physical Kinetics* | 物理直觉强 | 进阶参考 | 非平衡过程最全面 |
| Kubo, Toda, Hashitsume *Statistical Physics II* | 严谨系统 | 进阶 | 涨落-耗散最深入 |
| Reichl *Modern Statistical Mechanics* | 覆盖面广 | 研究生 | 非平衡统计全面 |
| Zwanzig *Nonequilibrium Statistical Mechanics* | 现代投影算子方法 | 进阶 | 与 Tong 互补 |

**建议组合**：**Tong（主读）+ Kardar（做题）+ Kubo/Toda/Hashitsume（涨落-耗散深入）** = 动理论学习三件套。

---

**完成日期**：2026-08-13（深化版 v2）
**配套**：[tong/README.md](README.md) + [TEMPLATE.md](../TEMPLATE.md) + [ai_for_physics/](../../ai_for_physics/)
