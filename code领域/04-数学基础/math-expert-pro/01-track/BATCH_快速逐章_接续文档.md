# 快速逐章笔记批量生产 · 接续文档

> 创建：2026-07-02（暂停时点）
> 用途：**下次重启 opencode 后，说一句「继续批量生产快速逐章笔记，照接续文档」即可无缝接续。**
> 本文件是自包含的：任务定义 + 当前进度 + 未完成清单 + 标准模板 + 飞腾锚点池 + 风格规范 + 执行方式 + 已知坑，全部都在这里。

---

## 0. 一句话接续指令（下次直接说这句）

> **「继续批量生产快速逐章笔记，照 `01-track/BATCH_快速逐章_接续文档.md`，从『未完成清单』顶部往下做。」**

AI 看到这句后，应：
1. 读本文件 §3 未完成清单顶部
2. 按 §6 执行方式（每批 ≤ 5 个 task 并行 subtask）
3. 按 §4 标准模板 + §5 飞腾锚点池 + §7 风格规范 写 prompt
4. 每批完成后，把已完成的从 §3 划掉、移到 §2 已完成清单
5. 持续循环直到 §3 清空，或用户喊停

---

## 1. 任务定义

为 `/home/lwz/文档/书/数学经典/` 下的数学经典书，批量生成「快速逐章精读」笔记，落盘到 `math-expert-pro/01-track/stage-{1,2,3}-*/` 对应目录。

**每本笔记的标准产出**：定位 + 章节骨架表（含飞腾锚点）+ 每章（核心概念 / 飞腾锚点 / 关键定理 LaTeX / 自测题）+ 思想主线 + 交叉引用。目标行数 280–440 行/本。

**本质**：基于经典教材的**已知章节结构**（PDF 多为扫描版，无法提取文本，靠公知目录）+ 项目**飞腾 D3000M 锚点**特色，重构认知地图。不是逐字精读，是建立全书骨架。

---

## 2. 当前进度（截至 2026-07-03 更新）

**已完成：119 个文件**（含快速逐章 + 简版合集）+ 5 本新增约 1701 行

### 2026-07-03 新增 23 本（本日四批累计）
**批一（5 本，1701 行）**：
- Feller《概率论》卷一（stage-3，280 行，组合直觉派概率）
- Bertsekas《凸优化理论》（stage-3，398 行，对偶中心化）
- Mohri《机器学习理论基础》2ed（stage-3，370 行，PAC+Rademacher 双轴，真实 TOC 17 章）
- Schölkopf-Smola《学习核方法》（stage-3，360 行，RKHS 统一框架）
- Kelley《一般拓扑》GTM27（stage-2，293 行，网/滤子 + 一致结构）

**批二（6 本，1910 行）**：
- Willard《一般拓扑》（stage-2，338 行，10 章，介于 Munkres 与 Kelley 之间）
- Neukirch《代数数论》（stage-3，281 行，7 章，类形成抽象类域论）
- Kobayashi-Nomizu《微分几何基础》卷 I（stage-2，320 行，7 章，联络中心化）
- Janusz《代数数域》（stage-3，296 行，8 章，零基础亲民入门）
- Williams《概率与鞅》（stage-3，343 行，15 章，鞅中心化概率）
- Nesterov《凸优化算法引论》（stage-3，332 行，5 章，NAG/复杂度下界）

**批三（6 本，2142 行）—— 填补候选方向缺口**：
- Trefethen-Bau《数值线代》（stage-3，440 行，12 主题，SIAM 经典，数值方向）
- Demmel《应用数值线代》（stage-3，302 行，6 章，数值方向）
- Bishop & Bishop《深度学习：基础与概念》2024（stage-3，353 行，真实 TOC 20 章，PRML 升级版）
- Shreve《随机分析金融 II》（stage-3，335 行，11 章，Itô 微积分金融出口）
- MacWilliams-Sloane《纠错码理论》（stage-3，369 行，4 部分 14 主题，MacWilliams 恒等式顶峰，信息论方向）
- Vapnik《统计学习理论》（stage-3，343 行，16 章，VC 维/SRM 原典，ML 理论源头）

**批四（6 本，2158 行）—— 候选方向纵深补强**：
- Boucheron-Lugosi-Massart《集中不等式》（stage-3，333 行，真实 TOC 15 章，浓度现象四路线统一）
- Richardson-Urbanke《现代编码理论》（stage-3，330 行，10 章，5G LDPC/Turbo/BP 译码）
- Borwein-Lewis《凸分析与非线性优化》（stage-3，536 行，9 章，泛函视角凸分析，与 Bertsekas/Nesterov 形成三角）
- Feller《概率论》卷二（stage-3，339 行，19 章，从离散升级到测度+扩散）
- Warner《流形与李群基础》GTM94（stage-2，300 行，6 章，流形+李群+表示一站式）
- Lee《黎曼流形引论》GTM176（stage-2，320 行，11 章，Lee 三件套合龙）

**项目阶段完成度**：
- **§3A 9 本全部清空 ✅**
- **§3B 各候选方向均 ≥ 2 本 ✅**：概率随机过程 4 本 / 优化理论 3 本 / ML 理论 5 本 / 数值分析 2 本 / 信息论 3 本 / 数论 4 本 / 几何拓扑 8+ 本
- **达到文档「做完边界」(§3A 9 + §3B 各方向 2-3 ≈ 25-30 本) ✅**

### stage-1-本科核心（19 个）
- **快速逐章（14 本）**：数学天书中的证明、应用组合数学、apostol数学分析、apostol微积分卷二、brualdi组合数学、halmos有限维向量空间、hoffman_kunze线性代数、lay线性代数、rosen离散数学、rudin_pma、strang线性代数、tao分析I、tao分析II、thomas微积分
- **简版合集（5 个，覆盖 18 本科普/入门/教辅）**：科普与工具书、普林斯顿入门读本三册、丘维声代数与几何三册、数学思维与学习方法三册、组合专题与中文教辅

### stage-2-研究生基础（53 个快速逐章）
从大学数学走向现代数学、代数学引论、泛函分析、复变函数入门、复分析、矩阵分析、李代数表示论、图论、微分方程、微分几何、严加安测度论讲义、ahlfors复分析、artin代数、atiya_macdonald、bott_tu微分形式GTM82、conway复分析I(GTM11)、conway复分析II(GTM159)、do_carmo黎曼几何、dummit、eisenbud交换代数GTM150、flajolet_sedgewick解析组合学、folland实分析、fulton代数拓扑GTM153、fulton_harris表示论、guillemin_pollack微分拓扑、hall李群李代数、halmos测度论GTM18、hatcher代数拓扑、hirsch微分拓扑GTM33、hungerford代数GTM73、jacobson基础代数I、lang复分析GTM103、lee光滑流形引论GTM218、lee拓扑流形GTM202、milnor从可微观点看拓扑、munkres代数拓扑引论、munkres全章、petersen黎曼几何GTM171、pugh实数学分析、reed_simon数学物理方法I、rotman群论入门GTM148、royden全20章、rudin泛函分析、rudin_real_complex、serre有限群线性表示GTM42、spivak流形上的微积分、stanley计数组合学卷一、stein_shakarchi泛函分析、stein_shakarchi复分析、stein_shakarchi实分析、stein_shakarchi_Fourier分析、walter常微分方程GTM182

### stage-3-研究方向（44 个快速逐章）
概率与计算、姜启源数学模型、数理金融、数学建模、数值方法、线性规划、apostol解析数论、arnold经典力学的数学方法GTM60、atiyah_K理论、billingsley概率与测度、bishop_PRML、C-数值分析、cover_thomas信息论、D-凸优化、durrett概率论、E-信息论GTM134、evans_PDE偏微分方程、goodfellow深度学习、griffiths_harris代数几何原理、hartshorne代数几何、hastie统计学习基础ESL、ireland_rosen数论GTM84、isaacs有限群理论、karatzas_shreve随机计算GTM113、kress数值分析GTM181、lang代数、lang代数数论GTM110、mackay信息论推理与学习、mac_lane范畴论、murphy机器学习概率视角、nocedal_wright数值优化、rotman同调代数、russell_norvig人工智能AIMA、serre局部域GTM67、shalev_shwartz理解机器学习、shiryaev概率GTM95、silverman椭圆曲线GTM106、silverman椭圆曲线II_GTM151、sutton_barto强化学习、tenenbaum解析概率数论、vakil代数几何TheRisingSea、vershynin高维概率、wainwright高维统计、weibel同调代数

---

## 3. 未完成清单（下次从这里顶部往下做）

### 3A. 上次 abort 的 9 本 —— ✅ 2026-07-03 全部清空

全部 9 本已完成：Feller I / Kelley / Willard / Neukirch / Bertsekas / Mohri / Schölkopf-Smola / Kobayashi-Nomizu I / Janusz。

### 3B. 待做候选（按方向分组，GTM 丛书 271 本的精选子集）

**已完成（按方向累计本数）**：
- 概率随机过程（3）：Feller I ✅ / Williams ✅ / billingsley（pre-batch）
- 优化理论（2）：Bertsekas ✅ / Nesterov ✅
- ML 理论（4）：Mohri ✅ / Schölkopf-Smola ✅ / hastie ESL（pre）/ murphy（pre）
- 数值分析（0）：**缺口方向**
- 信息论（2）：cover_thomas（pre）/ macwilliams ✅（369 行，补编码理论）
- 数论（4）：Neukirch ✅ / Janusz ✅ / silverman（pre）/ ireland_rosen（pre）
- 几何拓扑（6+）：Kobayashi-Nomizu I ✅ + munkres/hatcher/lee × 2/do_carmo/spivak 等多本

- **批三派发中（5 本剩余，MacWilliams 已完成）**：
- Trefethen 数值线代（数值分析）
- Demmel 数值线代（数值分析）
- Bishop 深度学习 2023（ML 理论深化）
- Shreve 随机分析金融 II（概率/金融应用）
- ~~MacWilliams 码理论（信息论/编码）~~ ✅ 369 行（信息论方向补编码理论，MacWilliams 恒等式顶峰）
- Vapnik 统计学习理论（ML 理论源头）

**2026-07-03 新增（单本）**：
- **Warner《流形与李群基础》GTM94**（stage-2，301 行，7 章+延伸，§3B 几何/拓扑方向深化。「微分流形+李群+紧李群表示」一站式桥梁，与 Kobayashi-Nomizu 卷I（联络中心化）正交互补。关键定理：Stokes/de Rham/Peter-Weyl/Weyl 特征公式/Lie 三定理。AI 锚点：等变神经网络）

**剩余候选**（后续可选）：

**概率/随机过程**：~~Williams 概率与鞅~~（✅已做）/ Feller 卷二、Breiman 概率论、Loève GTM45-46、Revuz-Yor 连续鞅、Karlin-Taylor 随机过程、Karatzas-Shreve GTM113（pre）

**数论/算术几何**：Washington 割圆域 GTM83、Koblitz 椭圆曲线与模形式 GTM97、Cassels-Fröhlich 代数数论、Marcus 代数数域、Silverman-Tate 椭圆曲线有理点、Serre 算术教程(Course in Arithmetic)

**代数/同调**：Jacobson 基础代数II、Lang 实与泛函分析 GTM142、Lam 模与环讲义 GTM189、Rotman 高等现代代数、Bourbaki 代数

**几何/拓扑**：~~Warner 流形与李群基础 GTM94~~（✅2026-07-03 已做 301 行）、Spivak 微分几何 5 卷、Kobayashi-Nomizu 卷II、Helgason 对称空间、Lawson-Michelsohn 自旋几何、Lee 黎曼流形 GTM176、Jost 黎曼几何与几何分析

**分析/PDE**：选 Hormander 线性 PDE、Taylor PDE 三卷、Gilbarg-Trudinger 椭圆 PDE

**ML/AI 深化**：Bengio 深度学习论文集、LeCun 深度学习、Murphy 概率ML新两卷2022、Boucheron 集中不等式、Bühlmann 统计学习

**优化/数值**：~~Nesterov 凸优化算法~~（✅已做）/ 选 Borwein 凸分析、Demmel 数值线代、Trefethen 数值线代（批三中）

**信息论/编码**：选 MacWilliams 码理论（批三中）、Richardson-Urbanke 现代编码理论、Csiszár 信息论与编码

---

## 4. 标准模板（照此结构，每本一份）

```
# {作者}《{书名}》(GTMxx) · 快速逐章精读

> 基于原书:{原文名}, {版次}({作者}, {年份})/ 读于:{日期}
> 定位:**{一句话定位}**, {第二句特色}。
> 本文为**快速逐章精读**,每章 1 个飞腾锚点 + 1 个关键定理 + 1 道自测题。

---

## §0 引言:{书名}是什么,为什么读它(约 350 字)
（含 4 列对比表：书|风格|严格性|适合谁，列本书 + 3 本同类）

---

## §1 全书 N 章骨架一览(飞腾锚点分布)
| 章 | 标题 | 核心概念 | 飞腾锚点 |
|:-:|------|---------|---------|
（N 行）

---

### 第 1 章 · {英文章名}({中文})
- **核心**:(80-120 字,讲本章概念逻辑串联)
- **飞腾锚点**:**XXX** —— (60 字,数学↔硬件真实关联)
- **关键定理**:**XXX**:(LaTeX 陈述)。简述重要性。
- **自测**:(1-2 题,具体可做)

---
（第 2-N 章同格式）

---

## §9 全书思想主线(约 200 字)
（讲贯穿全书的主线 + 与已读教材呼应）

## §10 与本仓库其他笔记的交叉引用
（列 4-6 条：与已读的 X/Y/Z 对比 + AI/工程锚点 3-5 条）
```

**简版合集**（多本合并到一个文件）：每本 50-70 行，结构简化为「定位 + 章节骨架表 + 阅读建议」，适合科普/入门/教辅类。

---

## 5. 飞腾锚点池（每章选 1 个，全书分散用，必须带具体数字）

项目 AI 锚点法核心：把数学概念锚定到飞腾 D3000M 国产 CPU 实测性能。

| 锚点 | 数字 | 适用数学概念 |
|------|------|------|
| **FP16 3.81×[L01]** | 3.81× | 浮点精度/数值范围/有限表示 |
| **Iron Law<2%[Lab00]** | <2% | 误差控制铁律（性能=指令数×CPI×时钟）|
| **分支预测[Lab02]** | 0.71 vs 3.14 | 条件分支/模式识别/路径选择 |
| **UDOT 16.9×[E05]** | 16.9× | 无符号点积累加（求和/积分/期望）|
| **matmul 15×[V03]** | 15× | 矩阵乘法/线性变换 |
| **GEMM 9.45G[Lab05]** | 9.45 GFLOPS | 高维矩阵吞吐 |
| **TLB 4.81×[E04]** | 4.81× | 内存局部性/分层寻址（局部↔整体）|
| **Schmidt 正交化** | — | 投影/最小二乘/正交分解 |

**使用纪律**：🟢【事实】可作证明锚点；🟡【类比】仅直觉，不可在严格证明中引用。每个锚点都要写清「数学概念↔硬件性能」的真实关联。

---

## 6. 执行方式（关键经验）

### 并行 subtask 数量
- **每批 ≤ 5 个 task 并行 subtask**（general 类型），最稳。
- **6 个偶尔可行**。
- **≥ 7 个高概率 abort**（2026-07-02 多次验证：8-10 个常触发 `Tool execution aborted`，且常连锁 abort 同批全部）。
- abort 后：重做即可（同一 prompt 重派通常成功）。

### 每个 subtask 的 prompt 结构（紧凑版约 150-250 字即可）
1. 书名 + 目标输出绝对路径
2. 章节结构（我提供已知目录）
3. 「模板照本仓库 {某本已做笔记}」+ §0 对比表 4 列要求
4. 飞腾锚点池（每章选 1，分散）
5. 风格规范一句话（纯中文术语英文 / LaTeX / 🟢🟡标注 / 引号「」 / 行数区间）
6. 返回要求：(a)路径 (b)wc -l (c)对比表 (d)锚点列表。**不返回整篇**（节省上下文）。

### 工作流
1. 从 §3 未完成清单选 ≤ 5 本
2. 为每本写一个 task subtask（并行派发）
3. 等返回 → 验证落盘（`wc -l`）
4. 把完成的从 §3 划掉，加到 §2
5. 重复直到 §3 清空或用户喊停

---

## 7. 风格规范（务必遵守）

1. **纯中文**，技术术语/书名/人名保留英文（Cauchy、Riemann、Galois、Hilbert 等）
2. LaTeX：行内 `$...$`，行间 `$$...$$`
3. 每章「核心」段落写**概念逻辑串联**，不是名词罗列
4. 飞腾锚点讲清「数学↔硬件」真实关联，标注 🟢事实 / 🟡类比
5. 自测题要**具体可做**（给具体函数/具体群/具体积分），不是「理解本章」
6. §0 对比表必须 4 列：书 | 风格 | 严格性 | 适合谁，含本书 + 3 本同类
7. 引号用「」，不是 ""
8. 全文目标行数：正式快速逐章 280-440 行；简版合集 250-380 行

---

## 8. 已知坑（避坑指南）

1. **PDF 多为扫描版**（DuXiu/Adobe Image Conversion），`pdftotext` 提取不到文本。不要纠结于读 PDF——经典教材的章节结构是公知知识，直接用。
2. **并行 subtask 超过 ~6 个会 abort**。每批严格 ≤ 5 个。
3. **章节结构要核对真实目录**：子代理有时会按"教学逻辑重组"偏离原书章节号。在 prompt 里强调「忠于原书真实 TOC，若有重组需标注对应原章节号」。
4. **锚点池只有 8 个**：章数 > 8 时允许合理复用（同一锚点隔几章再用，标注不同角度），但相邻章不要重复。
5. **简版合集**用于多本性质相近的书合并（科普/入门/教辅），避免文件爆炸。正式研究生教材单独成篇。
6. **AI 锚点法映射表**见 `10-personal/02-AI锚点法-数学落到工程.md`（数学概念↔AI/工程出口的完整映射）。

---

## 9. 用户画像（驱动所有决策）

- Python 工程级 / PyTorch 入门 / **数学零基础补课** / 喜可视化·历史动机·工程落地·难题
- 纯中文（技术术语英文）
- 学习风格：**直觉 → 公式 → 代码 → 不足/缺陷 → 应用场景**
- 每周 10-20h
- 目标：6-8 年达「应用数学研究型工程师」研究入门级
- 研究方向候选（stage-2 末锁定）：ML 理论 / 概率随机过程 / 数值分析 / 优化理论 / 信息论

**因此**：ML/AI/概率/优化/信息论方向的书优先级最高（贴合候选方向）；纯数学经典（代数几何/数论）做骨架即可。

---

## 10. 接续校验清单（下次重启后先做这个）

重启 opencode 后，AI 应先执行：

1. `ls /home/lwz/文档/书/数学经典/math-expert-pro/01-track/stage-*/ | grep "快速逐章"` → 确认 114 个文件仍在
2. 读本文件 §3 未完成清单顶部
3. 选 ≤ 5 本，按 §6 派 subtask
4. 每批完成后更新 §2/§3
5. 循环

**判断"做完"的边界**：§3A 的 9 本做完 + §3B 各方向核心 2-3 本做完（约 25-30 本），即可认为"数学经典/ 精选覆盖完成"。GTM 271 本全做无必要（大量冷门专题与 5 个候选方向无关）。

---

> 📌 本文档是**自包含**的接续手册。下次只需说 §0 那句话，AI 读完本文件就能无缝继续。无需重新摸索任务定义、模板、锚点池、坑。
