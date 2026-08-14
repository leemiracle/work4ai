# 资源清单 §01 · 数学成熟度（P0 — 你的最大短板）

> **为什么这是 P0**：你 human 记忆自评"数学 0"。物理到研究生级以上，数学是命门——GR 靠微分几何，粒子物理靠群论与李代数，QFT 靠泛函分析，拓扑物相靠代数拓扑。Boas 级数学方法只够本科入门。
>
> **本文档**：把"物理研究级数学"拆成 9 个子方向，给教材表 + 与 `top-math-courses` 和 `top-physics-courses` 的双向映射 + 12/24/36 月计划。
>
> **配套**：[EXPERT_PATH_2026.md §4.1](../EXPERT_PATH_2026.md)

---

## §1 物理研究的数学地图（一图看清）

```
                物理研究级数学
                     │
        ┌────────────┼────────────┐
   连续数学(分析)   离散数学(代数)   几何
        │            │            │
   复分析          线性代数       微分几何 ← GR/粒子/规范场
   实分析          抽象代数       黎曼几何
   泛函分析 ← QFT  群论 ← 粒子    辛几何 ← 哈密顿力学
   PDE ← 场论     李代数 ← 规范   复几何 ← 弦理论
   变分法 ← 拉氏   表示论 ← 粒子   代数拓扑 ← 拓扑物相
        │            │            │
        └────────────┼────────────┘
                     │
               数值/计算/概率
                     │
            数值分析  概率论  统计  随机过程
            (做模拟)  (统计力/量子测量/噪声)
```

**核心洞察**：物理用的数学**不是纯数学家的版本**——物理学家用数学"算出物理"，不追求数学严谨性的最大一般性。所以：
- 物理微分几何：Nakahara（物理系标配），不是 Lee 三部曲（数学系）
- 物理群论：Cornwell / Georgi，不是 Humphreys（数学系）
- 物理泛函：Reed & Simon（数学物理圣经，但物理学家只读 vol1），不是 Rudin

---

## §2 你已有的金矿：`top-math-courses/` 9 校

**先挖这里，再补物理专用数学。** `top-math-courses` 已有 30 课零基础→研究入门路径（见该目录 `UNIFIED_ROADMAP.md`）。摘要：

| 阶段 | 课 | 你能用在哪 |
|------|----|----------|
| 阶段 0（基础 4 课）| MIT 18.01/18.02/18.06/18.03 | 所有物理的入门地基 |
| 阶段 1（本科基础 6 课）| Axler LADR / 概率 / 实分析入门 / 复分析 | 力学、电磁、量子基础 |
| 阶段 2（本科核心 6 课）| Rudin / Artin 抽代 / Munkres 拓扑 / 测度论 | QFT、统计、GR |
| 阶段 3（应用 6 课）| Durrett 概率 / Trefethen 数值线代 / Boyd 凸优化 / 信息论 | 统计物理、计算物理、AI for Physics |
| 阶段 4（研究生 6 课）| 测度论 / 泛函 / 随机过程 | 凝聚态、量子测量、噪声 |

**优先级建议**：物理学习者，把 `top-math-courses` 的重点放在 **阶段 0-2**（地基+核心），阶段 3 选学（概率/数值线代/信息论），阶段 4 按需（泛函分析 QFT 用到再补）。

---

## §3 物理专用数学教材表（按方向，9 大块）

> 每本给：难度（★越多越难）/ 给谁 / 为什么 / 配合物理哪个主题

### 3.1 综合数学方法（本科物理用）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Boas** *Mathematical Methods in the Physical Sciences* | ★★ | 物理本科入门 | 全球物理系标配，覆盖广，例题多 | 项目 L06 |
| **Arfken** *Mathematical Methods for Physicists* | ★★ | Boas 替代 | 更全但更干，参考书性质 | L06 |
| **Riley, Hobson & Bence** *Mathematical Methods for Physics and Engineering* | ★★ | Cambridge 系 | 最厚最全（1300+页），习题多 | L06 |
| **Butkov** *Mathematical Physics* | ★★ | 老派经典 | 补充视角 | - |

**建议**：Boas 一本通吃本科。难点章节（特殊函数/积分变换）配 Riley Hobson Bence 查。

### 3.2 复分析（场论/量子散射/格林函数必备）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Needham** *Visual Complex Analysis* | ★★ | **强烈推荐入门** | 几何直觉最强，读完会"看见"复数 | 电磁/量子 |
| **Brown & Churchill** *Complex Variables* | ★ | 工程友好 | 标准教材 | - |
| **Ahlfors** *Complex Analysis* | ★★★ | 数学经典 | 第一本复分析 Fields 奖教材 | 进阶 |
| **Gamelin** *Complex Analysis* | ★★ | Berkeley 185 | 拓扑视角 | - |

**建议**：先 Needham（爱不释手），再 Gamelin 或 Ahlfors 做严谨补充。**留数定理计算实积分**是物理必杀技（解格林函数、散射振幅、回路积分）。

### 3.3 微分几何（GR/粒子/规范场必备，**物理命门**）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Nakahara** *Geometry, Topology and Physics* | ★★★ | **物理学家必读圣经** | 从流形到纤维丛到规范场，物理应用导向 | L10 GR / L11 QFT |
| **Carroll** *Spacetime and Geometry* ch1-3 | ★★★ | 配合 GR 学 | GR 教材里最好的几何附录 | L10 |
| **Frankel** *The Geometry of Physics* | ★★★ | 物理应用最全 | 从电磁到 Yang-Mills 到拓扑，物理例子丰富 | L02/L10/L11 |
| **Schutz** *Geometrical Methods of Mathematical Physics* | ★★ | 入门友好 | 比较浅，适合先读 | L10 前置 |
| **Lee** *Riemannian Manifolds* | ★★★★ | 数学系 | 严谨补充（可选）| 深入 |

**建议**：Schutz 先读（2 周速通）→ Carroll ch1-3（配合 GR）→ Nakahara（终身参考书）。**Frankel 是物理例子的金矿**，遇到具体物理问题查这里。

### 3.4 李群与李代数（粒子物理/规范场必备）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Cornwell** *Group Theory in Physics* vol 1-3 | ★★★ | **物理系标配** | 最系统的物理群论，SO(3)/SU(2)/SU(3) 全覆盖 | L09/L13 |
| **Georgi** *Lie Algebras in Particle Physics* | ★★★ | Harvard 课程 | 从粒子物理视角讲，应用导向 | L13 |
| **Tung** *Group Theory in Physics* | ★★ | 入门友好 | 习题多 | 先读 |
| **Cahn** *Semi-Simple Lie Algebras and Their Representations*（在线免费）| ★★★ | 粒子方向 | 在线精品 | L13 |
| **Jones** *Groups, Representations and Physics* | ★★ | 入门 | 简洁 | - |

**建议**：Tung 入门 → Cornwell 系统学 → Georgi/Cahn 做粒子物理应用。

### 3.5 泛函分析（QFT 严格化、量子力学数学基础）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Reed & Simon** *Methods of Modern Mathematical Physics* vol 1-4 | ★★★★ | **数学物理圣经** | 量子力学的严格数学基础，物理学家读 vol1 即可 | L11 QFT |
| **Kreyszig** *Introductory Functional Analysis* | ★★★ | 入门友好 | 标准入门教材 | 先读 |
| **Rudin** *Functional Analysis* | ★★★★ | 数学经典 | 严谨但难 | 进阶 |
| **Ballentine** *Quantum Mechanics: A Modern Development* | ★★★ | 物理教材 | 把量子力学的数学基础讲清楚的物理书 | L09 |

**建议**：物理学家**不需要**读全套 Reed & Simon。读 Kreyszig 入门 + Ballentine（物理视角）+ Reed&Simon vol1 选章（Hilbert 空间、谱定理、自伴算子）即可。

### 3.6 代数拓扑（拓扑物相、弦理论）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Nakahara** ch3-4（同伦/同调）| ★★★ | 物理学家 | Nakahara 里就够物理用 | L12 拓扑物相 |
| **Nash & Sen** *Topology and Geometry for Physicists* | ★★★ | 物理专用 | 同伦/同调/纤维丛，物理例子 | L12 |
| **Munkres** *Topology* | ★★ | 拓扑入门 | 点集拓扑标准 | 基础 |
| **Hatcher** *Algebraic Topology*（在线免费）| ★★★★ | 数学经典 | 同伦/同调的现代经典，免费 | 进阶 |

**建议**：Munkres 点集拓扑（基础）→ Nakahara ch3-4（物理应用）→ Hatcher（深入，可选）。

### 3.7 表示论（粒子物理、凝聚态）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Sternberg** *Group Theory and Physics* | ★★★ | 物理应用 | 物理系表示论 | L13 |
| **Fulton & Harris** *Representation Theory* | ★★★★ | 数学经典 | 紧李群表示论圣经 | 进阶 |
| **Simon** *Representations of Finite and Compact Groups* | ★★★ | 入门友好 | Oxford 课程 | 先读 |

**建议**：Simon 入门 → Sternberg 物理应用 → Fulton & Harris（数学方向才需要）。

### 3.8 变分法与经典力学数学（拉氏/哈氏力学基础）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Gelfand & Fomin** *Calculus of Variations* | ★★ | **经典力学的数学根基** | 最小作用量原理的严格数学 | L01 |
| **Goldstein** *Classical Mechanics* ch2,8,10 | ★★ | 物理教材 | 拉氏/哈氏/正则变换 | L01 |
| **Arnol'd** *Mathematical Methods of Classical Mechanics* | ★★★ | 数学物理经典 | 用微分流形讲力学，深刻 | L01 进阶 |
| **Marsden & Ratiu** *Introduction to Mechanics and Symmetry* | ★★★★ | 现代视角 | 辛几何力学 | 进阶 |

**建议**：Gelfand & Fomin（薄、清晰、必读）→ Goldstein → 想深入读 Arnol'd（数学美）。

### 3.9 PDE 与特殊函数（场论、波、量子）

| 教材 | 难度 | 给谁 | 为什么 | 配合 |
|------|------|------|--------|------|
| **Strauss** *Partial Differential Equations* | ★★ | 入门 | PDE 标准教材 | L02/L03/L08 |
| **Evans** *Partial Differential Equations* | ★★★★ | 数学经典 | 严谨 | 进阶 |
| **Arfken** ch11-13（特殊函数）| ★★ | 物理用 | 勒让德/贝塞尔/厄米特/拉盖尔 | L09 氢原子 |
| **Andrews** *Special Functions of Mathematics for Engineers* | ★★ | 工程友好 | 特殊函数大全 | - |

**建议**：Strauss 学方法 + Arfken/RHB 查特殊函数。氢原子要懂球谐函数、拉盖尔多项式。

---

## §4 双向映射表（数学 ↔ 物理主题）

> 学某个物理主题前，应该先学哪部分数学？

### 4.1 物理主题 → 数学先修

| 物理主题（项目 L#）| 必备数学 | 推荐数学教材章节 |
|------|---------|----------------|
| L01 力学 | 变分法 + ODE + 线代 | Gelfand & Fomin 全 + Boas ch7,12 |
| L02 电磁学 | 矢量微积分 + PDE + 张量 | Boas ch3,10 + Strauss ch1-4 |
| L03 波与光学 | PDE + 傅里叶分析 + 复变 | Boas ch14,15 + Needham |
| L04 热力学 | ODE + 偏导 | Boas ch4,6 |
| L05 统计力学 | 概率 + 组合 + 信息论 | Pitman 概率 + Cover&Thomas ch2 |
| L06 数学方法 | （本身就是数学）| Boas 全本 |
| L07 狭义相对论 | 线代（张量）+ 洛伦兹群 | Boas ch3,7 + Tung ch4 |
| L08 量子入门 | 线代（Hilbert 空间）+ 复变 + ODE | Axler LADR + Needham + Boas |
| L09 量子中级 | 群论 SO(3)/SU(2) + 特殊函数 + 泛函入门 | Cornwell ch1-6 + Arfken ch12 + Kreyszig ch1-4 |
| L10 GR | **微分几何**（命门）+ 张量 | Nakahara ch5-7 + Carroll ch1-3 |
| L11 QFT | 泛函 + 群论 SU(3) + 复变 + 路径积分 | Reed&Simon vol1 + Cornwell vol2 |
| L12 凝聚态 | 群论（晶体对称）+ 统计 + 拓扑入门 | Cornwell + Kittel ch1-2 + Nash&Sen |
| L13 粒子 | 群论 SU(3)/李代数 + 表示论 | Georgi + Sternberg |
| L14 宇宙学 | GR + 概率 + 数值 | Carroll + Pitman |
| L15 计算物理 | 数值分析 + 线代 + 编程 | Trefethen&Bau + Giordano |

### 4.2 数学方向 → 服务哪些物理

| 数学方向 | 主要服务的物理 | 优先级（按你的方向）|
|---------|--------------|------------------|
| 线性代数 | 全部物理 | ★★★ 必学（你有 LADR）|
| 变分法 | 经典力学、拉氏场论 | ★★★ 必学 |
| 复分析 | 电磁散射、量子散射、格林函数 | ★★★ 必学 |
| 微分几何 | GR、规范场、弦论 | ★★★ 必学（走理论）|
| 群论/李代数 | 粒子物理、凝聚态 | ★★★ 必学（走理论/凝聚态）|
| 泛函分析 | QFT 严格化、量子基础 | ★★ 重要 |
| 代数拓扑 | 拓扑物相、弦论 | ★★ 重要 |
| 表示论 | 粒子物理 | ★★ 选学 |
| 概率/统计 | 统计物理、AI for Physics | ★★★ 必学（你有优势）|
| 数值分析 | 计算物理、AI for Physics | ★★★ 必学（你有优势）|

---

## §5 12/24/36 月数学学习计划

> 假设：每周 10-20h（与你 human 记忆一致），物理数学并行。

### 阶段 1（月 1-12）：本科物理数学地基

**目标**：能读懂 Griffiths/Sakurai 全部数学，能推麦克斯韦方程→光速。

| 月 | 数学 | 物理（并行）|
|----|------|------------|
| 1-2 | Boas ch7-8（ODE + 级数解）| L01 力学 |
| 3-4 | Boas ch3（矢量微积分）+ ch10（张量）| L02 电磁 |
| 5-6 | Needham《Visual Complex Analysis》前 6 章 | L03 波 |
| 7-8 | Axler《LADR》ch1-5（你已有 top-math-courses）| L04 热 + L05 统计 |
| 9-10 | Boas ch11-13（特殊函数）| L08 量子入门 |
| 11-12 | Gelfand & Fomin《变分法》全本 + Boas ch14（积分变换）| L07 相对论 |

**月 12 自检**：
- [ ] 用留数定理计算 $\int_0^\infty \frac{dx}{1+x^4}$
- [ ] 用欧拉-拉格朗日方程推出单摆方程
- [ ] 解释为什么 Sturm-Liouville 问题给出正交本征函数

### 阶段 2（月 13-24）：研究生数学门槛

**目标**：能读懂 Peskin QFT 前 3 章、Carroll GR 全本。

| 月 | 数学 | 物理（并行）|
|----|------|------------|
| 13-15 | Schutz《Geometrical Methods》全 + Nakahara ch5-6（流形/张量）| L10 GR 入门 |
| 16-18 | Nakahara ch7（度规/联络/曲率）+ Carroll ch2-3 | L10 GR 主体 |
| 19-21 | Tung《Group Theory》ch1-7（SO(3)/SU(2)）| L09 量子中级 |
| 22-24 | Cornwell vol1（群论系统）+ Kreyszig ch1-4（Hilbert 空间）| L11 QFT 入门 |

**月 24 自检**：
- [ ] 计算 Schwarzschild 度规的 Christoffel 符号
- [ ] 证明 SO(3) 与 SU(2)/Z₂ 同构
- [ ] 解释为什么氢原子的"偶然简并"对应 SO(4) 对称性

### 阶段 3（月 25-36）：研究级数学

**目标**：能读现代凝聚态/粒子论文的数学部分。

| 月 | 数学 | 物理（并行）|
|----|------|------------|
| 25-27 | Nakahara ch9-10（纤维丛/规范场）| L11 QFT / L13 粒子 |
| 28-30 | Cornwell vol2（李代数）+ Georgi《Lie Algebras》| L13 粒子 |
| 31-33 | Nash & Sen（拓扑）+ Nakahara ch3-4（同伦/同调）| L12 拓扑物相 |
| 34-36 | Reed & Simon vol1（Hilbert 空间/谱定理）选章 | 选定方向的数学深化 |

**月 36 自检**：
- [ ] 解释 Berry 相位的几何意义（纤维丛上的联络）
- [ ] 用表示论解释夸克的颜色 SU(3)
- [ ] 解释整数量子霍尔效应的拓扑不变量（Chern 数）

---

## §6 数学学法的 5 个反直觉建议

### 💡 1. 物理学家学数学：先算后证
- 数学系：定义→定理→证明
- 物理系：**先算一个例子→再回头理解定理**
- 例：学李代数前，先算 $[J_x, J_y] = i\hbar J_z$（角动量对易关系），再看数学结构。

### 💡 2. 教材搭配 > 单本精读
- 同一主题读 2 本不同视角的书，比读 1 本两遍深刻。
- 例：微分几何同时翻 Nakahara（物理）+ Schutz（直觉）+ Frankel（例子）。

### 💡 3. 用物理验证数学
- 学完一个数学工具，找一个物理应用算出来。
- 例：学完留数定理，去算一个静电场格林函数。学完群论，去分类氢原子能级。

### 💡 4. 不要被严谨性绑住
- 物理用的数学允许"物理严谨"（Dirac delta 函数、路径积分、重整化在数学严格化之前物理学家用了几十年）。
- **不要**为了追求数学严格而卡住物理学习。先会用，后理解。

### 💡 5. 做题是唯一标准
- "读懂 Nakahara" ≠ "会微分几何"。
- 每章做 5-10 道题（书后习题或自编：计算具体流形的曲率）。

---

## §7 与 `top-math-courses` 的协调（避免重复劳动）

你已经有的 `top-math-courses`（9 校数学）覆盖**纯数 + ML 理论**。本文档补充**物理专用数学**。两者关系：

| 方向 | 在哪学 | 备注 |
|------|-------|------|
| 微积分 / 线代 / ODE | `top-math-courses` 阶段 0 | 物理数学地基，不重复 |
| 实分析 / 抽代 / 测度论 | `top-math-courses` 阶段 1-2 | 选学（理论物理用）|
| 概率 / 数值 / 优化 / 信息论 | `top-math-courses` 阶段 3 | **与 AI for Physics 共用**，重点学 |
| **复分析（物理）**| **本文档 §3.2** + top-math 复分析 | Needham 视角 |
| **微分几何（物理）**| **本文档 §3.3** | top-math 没有物理几何 |
| **群论/李代数（物理）**| **本文档 §3.4** | top-math 抽代偏纯数 |
| **泛函分析（物理）**| **本文档 §3.5** + top-math 阶段 4 | Reed&Simon 视角 |
| **代数拓扑（物理）**| **本文档 §3.6** | top-math 拓扑偏点集 |

**建议节奏**：阶段 0-1（top-math）→ 本文档 §3.2/3.3/3.8（物理专用）→ 阶段 2-3（top-math）→ 本文档 §3.4/3.5/3.6（物理专用）。

---

## §8 工具与检查

### 数学软件（必装）
- **SymPy**（Python 符号计算）— 推导验证、解 ODE、化简表达式
- **Mathematica**（商业，学生版 ~$150）— 物理系标配，符号+数值+可视化一体
- **SageMath**（开源，免费）— Mathematica 替代
- **Lean4**（你已在用，law/neo-os 项目）— 形式化验证推导

### 自测题（每阶段结束做一遍，纸笔，不看资料）
1. 计算 $\int_{-\infty}^{\infty} \frac{\sin x}{x} dx$（留数定理）
2. 写出拉格朗日方程，并从牛顿第二定律推导之
3. 计算 2-球面 $S^2$ 的高斯曲率（微分几何）
4. 列出 SO(3) 的不可约表示（群论）
5. 证明厄米算子的本征值是实数（泛函）
6. 解释为什么甜甜圈和咖啡杯拓扑等价（拓扑）

---

**完成日期**：2026-08-13
**配套**：[EXPERT_PATH_2026.md](../EXPERT_PATH_2026.md) + [top-math-courses/UNIFIED_ROADMAP.md](../../top-math-courses/UNIFIED_ROADMAP.md) + [02_computational_toolchain.md](02_computational_toolchain.md)
