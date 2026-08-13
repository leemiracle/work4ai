# 讲义手册 — 经典物理讲义详细指南（David Tong 为核心）

> **为什么有这一份**：[08_lectures_and_courses.md](08_lectures_and_courses.md) 给了概览。本文档展开到**可执行**——每本讲义覆盖什么、难度几星、怎么读、读完能干什么、配合项目哪一章。
>
> **核心**：David Tong 讲义（23 本，**2026-08-13 webfetch 核实**自 davidtong.org/teaching/）。他是**当代自学者最该用的资源**——免费、全面、清晰、配习题。
>
> **配套**：[08_lectures_and_courses.md](08_lectures_and_courses.md)（概览）+ [00_popular_science.md](00_popular_science.md)（科普起点）

---

## §0 为什么 David Tong 是"当代费曼"

### 他本人
- **David Tong**，Cambridge 大学 DAMTP 教授（理论物理）
- 研究方向：弦理论、规范场论、凝聚态（量子霍尔）
- **教学**：他的讲义被全球物理学生公认为"当代最好的物理讲义"

### 他的讲义的 5 个不可替代之处

1. **完全免费**——23 本 PDF 全开放，不收一分钱
2. **覆盖全面**——从本科一年级力学到高级研究生弦理论，**整个理论物理课程体系**
3. **写得极清晰**——直觉 + 严谨 + 幽默（和费曼同款风格）
4. **每本配习题 + 解答**——可做题，不是只读
5. **部分有视频**（如 QFT）——可以跟着录像学

### 一句话
> **Tong 之于 21 世纪自学者 = 费曼之于 20 世纪物理系。** 他把整个理论物理课程免费给你，写得好到让你想读。

---

## §1 David Tong 23 本讲义完整目录（已核实）

> 来源：davidtong.org/teaching/（2026-08-13 webfetch）
> 每本都在 davidtong.org/teaching/<slug>/ 下，免费 PDF

### 难度梯度图（先看清全景）

```
入门（一年级本科）─────────────────────────────────
  Dynamics and Relativity  ★
  Vector Calculus          ★
  
核心（高年级本科）─────────────────────────────────
  Classical Dynamics       ★★     (拉氏/哈氏)
  Electromagnetism         ★★     (麦克斯韦全套)
  Quantum Mechanics        ★★     (薛定谔方程)
  Statistical Physics      ★★     (统计力学+热力学)
  Solid State Physics      ★★     (能带/费米面/声子)
  Fluid Mechanics          ★★     (Navier-Stokes)
  Cosmology                ★★     (膨胀宇宙)
  Mathematical Biology     ★★     (种群/反应扩散)
  Topics in QM             ★★★    (原子/散射/基础)
  
研究生入门（第一年研究生）─────────────────────────
  General Relativity       ★★★    (微分几何+引力)
  Quantum Field Theory     ★★★    (正则量子化,有视频)
  Statistical Field Theory ★★★    (相变+重整化群)
  Kinetic Theory           ★★★    (非平衡统计)
  The Standard Model       ★★★    (标准模型数学结构)
  String Theory            ★★★    (玻色弦+CFT)
  Quantum Hall Effect      ★★★    (前半本 ★★)
  Supersymmetric QM        ★★★    (联系几何)
  Supersymmetric Field Theory ★★★
  Gauge Theory             ★★★★   (拓扑+强耦合)
  
高级研究生 ─────────────────────────────────────────
  Solitons and D-Branes    ★★★★★  (TASI 暑期学校级)
  
特殊（科普级，零数学门槛）─────────────────────────
  Particle Physics         ★      (只需高中数学!CERN 暑期学校)
```

---

## §2 Tong 讲义逐本详解

### §2.1 入门级（一年级本科，物理零基础起步）

#### 📘 Dynamics and Relativity（动力学与相对论）
- **覆盖**：牛顿力学 + 狭义相对论
- **难度**：★（一年级）
- **章节要点**：牛顿定律 / 守恒律 / 轨道力学 / 振子 / 刚体入门 / 狭义相对论（洛伦兹变换 / $E=mc^2$）
- **读完能干什么**：能用牛顿定律解任何经典力学问题；理解时间膨胀和长度收缩
- **配合项目**：L01 力学 + L07 狭义相对论
- **链接**：davidtong.org/teaching/dynamics-and-relativity/
- **为什么必读**：**这是你物理学习的第 1 本**。比 Taylor 教材更直觉，比 Feynman 更系统。

#### 📘 Vector Calculus（矢量微积分）
- **覆盖**：梯度/散度/旋度/积分定理（高斯/斯托克斯）
- **难度**：★（一年级）
- **读完能干什么**：看懂麦克斯韦方程的微分形式
- **配合项目**：L02 电磁学 + L06 数学方法
- **链接**：davidtong.org/teaching/vector-calculus/
- **为什么必读**：电磁学的前置。$\nabla$ 不熟，电磁学白学。

---

### §2.2 核心本科级（高年级，物理四大支柱）

#### 📘 Classical Dynamics（经典动力学）
- **覆盖**：拉格朗日力学 + 哈密顿力学 + 刚体
- **难度**：★★（高年级）
- **章节要点**：最小作用量原理 / 欧拉-拉格朗日方程 / 诺特定理（对称↔守恒）/ 哈密顿方程 / 刚体（欧拉角/陀螺）
- **读完能干什么**：用拉氏方程解任何力学问题；理解"为什么能量/动量/角动量守恒"
- **配合项目**：L01 进阶 + L08 量子的前置
- **链接**：davidtong.org/teaching/classical-dynamics/
- **为什么必读**：拉氏/哈氏是**量子力学的语言**。不学这个，量子力学的算符形式看不懂。

#### 📘 Electromagnetism（电磁学）
- **覆盖**：麦克斯韦方程全套 + 相对论形式 + 介质中的电磁
- **难度**：★★（高年级）
- **章节要点**：静电/静磁 / 感应 / 麦克斯韦方程 / 电磁波 / 辐射 / 相对论形式（电磁张量）/ 介质
- **读完能干什么**：从麦克斯韦方程推光速；理解电磁场张量 $F_{\mu\nu}$
- **配合项目**：L02 电磁学
- **链接**：davidtong.org/teaching/electromagnetism/
- **对比**：与 Purcell（Berkeley Vol 2）互补。Purcell 从相对论讲，Tong 从方程讲。

#### 📘 Quantum Mechanics（量子力学）
- **覆盖**：薛定谔方程为主的第一课
- **难度**：★★（高年级）
- **章节要点**：薛定谔方程 / 一维问题（势阱/势垒/谐振子）/ 氢原子 / 自旋 / 角动量 / 微扰论
- **读完能干什么**：解氢原子能级；理解自旋 1/2
- **配合项目**：L08 量子入门 + L09 量子中级
- **链接**：davidtong.org/teaching/quantum-mechanics/
- **为什么必读**：比 Griffiths 更直觉，比 Sakurai 更友好。**首选量子入门**。

#### 📘 Statistical Physics（统计物理）
- **覆盖**：统计力学 + 热力学 + 经典气/量子气/相变
- **难度**：★★（高年级）
- **章节要点**：热力学四定律 / 熵 / 系综（微正则/正则/巨正则）/ 经典气体 / 量子气体（玻色/费米）/ 相变
- **读完能干什么**：推麦克斯韦-玻尔兹曼分布；理解玻色-爱因斯坦凝聚
- **配合项目**：L05 统计力学
- **链接**：davidtong.org/teaching/statistical-physics/
- **为什么必读**：统计是 **AI for Physics 的根基**（Hopfield/Hinton 都从这里来）。

#### 📘 Solid State Physics（固体物理）
- **覆盖**：能带 / 费米面 / 声子 / 磁场中粒子
- **难度**：★★（高年级）
- **章节要点**：晶体结构 / 倒格子 / 能带论 / 费米面 / 声子 / 量子霍尔效应入门
- **读完能干什么**：解释为什么金属导电、绝缘体不导电
- **配合项目**：L12 凝聚态
- **链接**：davidtong.org/teaching/solid-state-physics/

#### 📘 Fluid Mechanics（流体力学）
- **覆盖**：Euler / Navier-Stokes / 波 / 稳定性 / 湍流
- **难度**：★★（高年级）
- **配合项目**：L20 流体（项目专门化）
- **链接**：davidtong.org/teaching/fluid-mechanics/

#### 📘 Cosmology（宇宙学）
- **覆盖**：膨胀宇宙 / 热历史 / 结构形成
- **难度**：★★（高年级）
- **配合项目**：L14 宇宙学
- **链接**：davidtong.org/teaching/cosmology/

#### 📘 Mathematical Biology（数学生物学）
- **覆盖**：种群动力学 / 反应扩散 / Fokker-Planck
- **难度**：★★（高年级）
- **特色**：跨学科，与你的 AI 兴趣相关（神经网络/种群动力学同源）
- **链接**：davidtong.org/teaching/mathematical-biology/

#### 📘 Topics in Quantum Mechanics（量子力学专题）
- **覆盖**：原子物理 / 散射理论 / 量子基础
- **难度**：★★★（高年级/研究生入门）
- **特色**：含量子基础（诠释/测量问题）—— 很少教材认真讲这块
- **配合项目**：L09 量子中级进阶
- **链接**：davidtong.org/teaching/topics-in-quantum-mechanics/

---

### §2.3 研究生入门级（理论物理核心）

#### 📘 General Relativity（广义相对论）
- **覆盖**：测地线 + 微分几何 + 引力 + 应用
- **难度**：★★★（研究生第一年）
- **章节要点**：弯曲时空中的测地线 / 张量 / 度规 / 联络曲率 / 爱因斯坦方程 / 史瓦西黑洞 / 宇宙学
- **读完能干什么**：算史瓦西解；理解 GPS 相对论修正
- **配合项目**：L10 广义相对论
- **链接**：davidtong.org/teaching/general-relativity/
- **对比**：与 Carroll *Spacetime and Geometry* 同级，Tong 更友好

#### 📘 Quantum Field Theory（量子场论）⭐ **有视频！**
- **覆盖**：标量场 / Dirac 场 / 矢量场的正则量子化
- **难度**：★★★（研究生第一年）
- **章节要点**：Klein-Gordon 场 / Dirac 场 / 电磁场 / 费曼图 / QED / 重整化入门
- **读完能干什么**：算一个费曼图（散射振幅）
- **配合项目**：L11 QFT
- **链接**：davidtong.org/teaching/quantum-field-theory/（**含视频录像**）
- **为什么必读**：**QFT 入门首选**。比 Peskin 友好，比 Zee 严谨。还有免费视频。

#### 📘 Statistical Field Theory（统计场论）
- **覆盖**：相变 + 临界现象 + 重整化群
- **难度**：★★★（研究生第一年）
- **特色**：重整化群的最佳入门（Wilson 的伟大思想）
- **配合项目**：L11 QFT 的统计视角
- **链接**：davidtong.org/teaching/statistical-field-theory/

#### 📘 Kinetic Theory（动力论）
- **覆盖**：非平衡统计力学 / Boltzmann 方程 / 随机过程 / 线性响应
- **难度**：★★★（研究生）
- **特色**：非平衡态——大多数统计教材只讲平衡，这本补非平衡
- **链接**：davidtong.org/teaching/kinetic-theory/

#### 📘 The Standard Model（标准模型）
- **覆盖**：标准模型的数学结构 / 强弱力 / 自发破缺 / 反常
- **难度**：★★★（研究生）
- **配合项目**：L13 粒子物理
- **链接**：davidtong.org/teaching/standard-model/

#### 📘 String Theory（弦理论）
- **覆盖**：玻色弦 + 共形场论（CFT）基础
- **难度**：★★★（研究生第一年）
- **配合项目**：L22 弦理论
- **链接**：davidtong.org/teaching/string-theory/

#### 📘 Quantum Hall Effect（量子霍尔效应）
- **覆盖**：前半量子力学级（整数量子霍尔）/ 后半场论级（Chern-Simons/CFT）
- **难度**：★★★（分两半）
- **特色**：拓扑物相的入门最佳
- **配合项目**：L12 凝聚态进阶 + L24 拓扑物理
- **链接**：davidtong.org/teaching/quantum-hall-effect/

#### 📘 Supersymmetric Quantum Mechanics（超对称量子力学）
- **覆盖**：联系几何（Morse 理论 / Atiyah-Singer 指标定理）
- **难度**：★★★（研究生）
- **链接**：davidtong.org/teaching/supersymmetric-quantum-mechanics/

#### 📘 Supersymmetric Field Theory（超对称场论）
- **覆盖**：N=1 超对称 in d=3+1
- **难度**：★★★（研究生）
- **链接**：davidtong.org/teaching/supersymmetric-field-theory/

#### 📘 Gauge Theory（规范理论）
- **覆盖**：QFT 的拓扑 + 强耦合部分
- **难度**：★★★★（研究生，需路径积分基础）
- **特色**：QFT 的"有趣部分"——拓扑解/瞬子/Theta真空
- **链接**：davidtong.org/teaching/gauge-theory/

---

### §2.4 高级研究生

#### 📘 Solitons and D-Branes（孤立子与 D 膜）
- **覆盖**：超对称规范理论中的孤立子 + D 膜
- **难度**：★★★★★（TASI 暑期学校级，最高）
- **链接**：davidtong.org/teaching/solitons/
- **注意**：这是 Tong 最难的讲义，需要先读 String Theory + Gauge Theory

---

### §2.5 特殊：科普级（零数学门槛）

#### 📘 Particle Physics（粒子物理）⭐ **只需高中数学！**
- **覆盖**：粒子物理 + QFT 的科普详细版
- **难度**：★（**只需高中数学**）
- **特色**：CERN 暑期学校讲座，**最不数学**的 Tong 讲义
- **用法**：**物理小白的第 1 本 Tong**（比 Dynamics and Relativity 还易）。读完能"看懂"粒子物理新闻。
- **链接**：davidtong.org/teaching/particle-physics/
- **强烈推荐**：如果你完全零基础，从这本开始（再读 Dynamics and Relativity）

---

## §3 David Tong 的 3 条阅读路径

### 路径 A：本科快速通道（12-18 月，建立完整物理直觉）

```
1. Particle Physics (科普级, 先建立兴趣)
2. Dynamics and Relativity (牛顿+SR)
3. Vector Calculus (前置)
4. Electromagnetism (麦克斯韦)
5. Classical Dynamics (拉氏/哈氏)
6. Quantum Mechanics (薛定谔)
7. Statistical Physics (统计)
8. Solid State Physics (凝聚态)
```

**产出**：相当于 Cambridge 物理系本科毕业水平（理论部分）。

### 路径 B：理论物理深钻（24-36 月，到研究生）

路径 A + 以下：
```
9. Topics in QM
10. General Relativity
11. Quantum Field Theory (有视频!)
12. Statistical Field Theory
13. Gauge Theory
14. String Theory
```

**产出**：能读现代理论物理论文。

### 路径 C：AI for Physics（你的方向，12-18 月）

```
1. Particle Physics (科普)
2. Dynamics and Relativity
3. Quantum Mechanics
4. Statistical Physics (★ AI 的根基)
5. Solid State Physics (★ 材料方向)
6. Kinetic Theory (非平衡, ML 相关)
7. Mathematical Biology (网络/动力学)
```
然后跳到 [ai_for_physics/](../ai_for_physics/)。

**产出**：能用物理直觉做 AI for Physics 研究。

---

## §4 费曼物理学讲义（FLP）详细

### 基本信息
- **作者**：Richard Feynman（Caltech）
- **年份**：1961-1963
- **免费在线**：feynmanlectures.caltech.edu（3 卷全文 + 录音）
- **中译本**：上海科学技术出版社（3 卷）

### 3 卷结构 + 必读章节

#### 卷 1：力学、热、辐射（约 600 页）
**必读章节**：
- §1-1 原子假说（"如果物理学消失，留一句话：物质由原子组成"）
- §4 能量守恒（Denis 积木——见 [08 §8 示范](08_lectures_and_courses.md)）
- §9 爱因斯坦相对论
- §10-12 动量守恒 / 旋转动力学 / 力的相对性
- §15 狭义相对论
- §39 气体动理论（统计入门）

#### 卷 2：电磁与物质（约 600 页）
**必读章节**：
- §1 电磁学的直觉（"圆圈套圆圈"）
- §13 静磁学
- §18 麦克斯韦方程
- §20 麦克斯韦方程在自由空间（光 = 电磁波）
- §25 电动力学相对论形式

#### 卷 3：量子力学（约 400 页）
**必读章节**：
- §1-3 量子行为（双缝实验，**至今最好的量子入门**）
- §5 自旋 1/2（Stern-Gerlach，**自旋在前位置在后**）
- §8-9 薛定谔方程
- §12 氢原子

### 怎么读 FLP
- **不求一次懂**：每年重读一卷
- **配合做题教材**：Morin 力学 / Griffiths 量子
- **先读故事感强的章节**：§1-1, §4, 卷3§1-3
- **听录音**（feynmanlectures.caltech.edu 有原音）

---

## §5 Susskind "理论最小"系列详细

### 基本信息
- **作者**：Leonard Susskind（Stanford）
- **形式**：YouTube 录像 + 书（同名）
- **定位**：科普→教材的**桥梁**（比科普深，比教材浅）

### 系列清单（每本/每个录像）

| 书 | 主题 | 难度 |
|----|------|------|
| **The Theoretical Minimum: What You Need to Know to Start Doing Physics** | 经典力学 | ★★ |
| **Quantum Mechanics: The Theoretical Minimum** | 量子 | ★★ |
| **Special Relativity and Classical Field Theory** | 相对论+经典场 | ★★ |
| **General Relativity: The Theoretical Minimum** | 广义相对论 | ★★★ |
| **Statistical Mechanics: The Theoretical Minimum** | 统计 | ★★★ |
| **Cosmology**（即将/已出）| 宇宙学 | ★★★ |

### 用法
- 看完科普（[00_popular_science.md](00_popular_science.md)）后，用 Susskind 过渡
- 每本配 Stanford YouTube 录像（搜 "Susskind Theoretical Minimum"）
- 读完再进 Tong / Griffiths

---

## §6 MIT OCW Walter Lewin 详细

### 基本信息
- **作者**：Walter Lewin（MIT，已故）
- **特色**：物理演示教学巅峰（亲自摆钟/放电/吊钢丝）
- **获取**：ocw.mit.edu + YouTube（搜 "Walter Lewin"）

### 核心课

#### 8.01 Classical Mechanics（力学，1999 版）
- 35 讲录像
- 演示：单摆 / 旋转 / 碰撞 / 流体
- **必看**：Lewin 用自己的身体做实验（吊钢丝证明钟摆周期）
- 名言："测量 = 物理"

#### 8.02 Electricity and Magnetism（电磁，2002 版）
- 演示：静电 / 磁铁 / 电磁感应 / 等离子
- **必看**：Lewin 让特斯拉线圈在讲台上放电

#### 8.03 Vibrations and Waves（振动与波）
- 较少人知道，但同样精彩

### 注意
- Lewin 因丑闻被 MIT 部分撤下，但录像在 YouTube 广泛流传
- **他的教学价值不因个人行为而减**

---

## §7 Berkeley Physics Course 5 卷详细

### 基本信息
- **年代**：1960-1970s（与 FLP 同时代）
- **特色**：比 Feynman 系统比教材直觉

### 5 卷详解

| 卷 | 标题 | 作者 | 配合项目 | 特色 |
|----|------|------|---------|------|
| **Vol 1** | Mechanics | Kittel/Knight/Ruderman | L01 | 经典力学，Berkeley 风格 |
| **Vol 2** | Electricity and Magnetism | **Purcell** | L02 | **必读**——从相对论讲电磁，磁 = 电的相对论效应 |
| **Vol 3** | Waves | Crawford | L03 | 振动与波，配实验 |
| **Vol 4** | Quantum Physics | Wichmann | L08 | 量子，概念导向 |
| **Vol 5** | Statistical Physics | **Reif** | L05 | **研究生级**，统计力学最深教材之一 |

### 特别推荐：Purcell Vol 2
- **核心思想**：磁场是电场的相对论效应。一个运动电荷的磁场 = 静止参考系中电场的变形
- **读完**：你**一次**理解电与磁的统一，且直接通向狭义相对论
- **被奉为**：电磁学教材的黄金标准

### 特别推荐：Reif Vol 5
- 比 Kittel & Kroemer 更深更全
- 研究生级统计力学的标准参考

---

## §8 Landau-Lifshitz 理论物理教程 10 卷详细

### 基本信息
- **作者**：Lev Landau + Evgeny Lifshitz（苏联学派）
- **地位**：研究生圣经
- **特色**：最简洁（Landau 从不浪费一字）+ 直觉极强 + 难

### 10 卷

| 卷 | 标题 | 主题 | 难度 |
|----|------|------|------|
| 1 | Mechanics | 经典力学（拉氏视角）| ★★★ |
| 2 | The Classical Theory of Fields | 经典场论（电磁+相对论）| ★★★★ |
| 3 | Quantum Mechanics: Non-Relativistic Theory | 非相对论量子 | ★★★★ |
| 4 | Quantum Electrodynamics | QED | ★★★★★ |
| 5 | Statistical Physics Part 1 | 统计（上）| ★★★★ |
| 6 | Fluid Mechanics | 流体 | ★★★★ |
| 7 | Theory of Elasticity | 弹性 | ★★★ |
| 8 | Electrodynamics of Continuous Media | 连续介质电动力学 | ★★★★ |
| 9 | Statistical Physics Part 2 | 统计（下，凝聚态）| ★★★★★ |
| 10 | Physical Kinetics | 物理动力论 | ★★★★ |

### 怎么读
- **本科先读卷 1**（力学，用拉格朗日——比 Goldstein 简洁深刻）
- **研究生卷卷啃**：每卷配现代教材对比读（如卷 3 配 Sakurai）
- **不要入门就读**——会绝望（太简洁）

---

## §9 Dirac / Pauli / Sommerfeld 讲义详细

### 📘 Dirac *The Principles of Quantum Mechanics*
- **作者**：Paul Dirac（1933 诺奖）
- **特色**：bra-ket 记号的诞生地。极简、极美。
- **名言**："美比真更重要"
- **难度**：★★★★
- **必读**：读了他，你才理解量子力学的"数学美"

### 📘 Dirac *Lectures on Quantum Mechanics*（Yeshiva 讲座）
- 比 *Principles* 短，更聚焦
- 含 Dirac 对量子约束系统的处理（先驱）

### 📘 Pauli *Lectures on Physics*（6 卷）
- **作者**：Wolfgang Pauli（1945 诺奖）
- **6 卷**：电动力学 / 光学 / 量子 / 热力学 / 波动 / 力学
- **特色**：泡利刻薄、精确、深刻
- **MIT 访问时整理**（1950s）

### 📘 Sommerfeld *Lectures on Theoretical Physics*（6 卷）
- **作者**：Arnold Sommerfeld
- **地位**："未拿诺奖的最伟大物理学家"
- **特色**：培养了海森堡/泡利/贝特等诺奖学生
- **风格**：物理直觉 + 数学严谨的典范

---

## §10 整合阅读路径（所有资源串起来）

### 阶段 1：科普→公式过渡（月 1-6）
- 看 **MIT Lewin 8.01**（视觉直觉）
- 读 **Susskind 经典力学**（桥梁）
- 读 **Tong Particle Physics**（科普级，建立兴趣）

### 阶段 2：本科核心（月 7-24）
- 读 **Tong Dynamics and Relativity**（第 1 本严谨）
- 配合 **Berkeley Vol 1**（力学）
- 读 **Tong Electromagnetism**
- 配合 **Berkeley Vol 2 (Purcell)**（电磁，相对论视角）
- 读 **Tong Classical Dynamics**（拉氏/哈氏）
- 读 **Tong Quantum Mechanics**
- 配合 **Feynman 卷 3**（量子直觉）
- 读 **Tong Statistical Physics**
- 配合 **Berkeley Vol 5 (Reif)**（统计深化）

### 阶段 3：研究生（月 25-48）
- 读 **Tong General Relativity**
- 配合 **Carroll Spacetime and Geometry**
- 读 **Tong QFT**（看视频！）
- 配合 **Peskin** 做题
- 读 **Landau 卷 1-3**（重读经典，研究生视角）

### 阶段 4：前沿（月 49+）
- 读 **Tong String Theory / Gauge Theory / Solitons**
- 读 **Dirac Principles**（量子力学的数学美）
- 选定方向深读

---

## §11 一个反直觉的建议

> **不要同时读多本讲义。**
>
> 很多人收藏了 Feynman + Tong + Landau + Berkeley 全套，结果每本读 10 页就放下。
>
> **正确做法**：每个主题**只选 1 本主读**（其他做参考）。
> - 力学：Tong Dynamics and Relativity
> - 电磁：Purcell (Berkeley Vol 2)
> - 量子：Tong QM + Feynman 卷 3（双主）
> - 统计：Tong Statistical Physics
> - GR：Tong GR + Carroll
> - QFT：Tong QFT（首选）
>
> **读完一本，再开下一本。** 物理学不是比谁读得多，是比谁读得透。

---

**完成日期**：2026-08-13
**核实**：David Tong 讲义清单已 webfetch davidtong.org/teaching/ 核实（23 本）
**配套**：[08_lectures_and_courses.md](08_lectures_and_courses.md)（概览）+ [00_popular_science.md](00_popular_science.md)（科普起点）+ [EXPERT_PATH_2026.md](../EXPERT_PATH_2026.md)
