---
card_id: MATH-DISCOVERY-ENGINE
title: 数学发现引擎 × 组合爆炸——AI(模型) × Agent(手段) × 数学(森林) 的研究循环
universe: top-math-courses
burke:
  场景: 从学习循环升级为研究循环（AI 当主角，数学知识当搜索空间）
  主体: 多模型 × 多手段 × 知识森林，人定方向
  能动: 进化循环四步——变异（算子+LLM 提议）→ 选择（验证级联）→ 遗传（知识卡）→ 调度（四象限）
  行动: 组合爆炸式生成猜想/证明/构造，机器验证过滤，幸存者固化回森林
  目的: 产出机器可验证的新数学事实（恒等式/不等式/引理/证明），逐步逼近研究级发现
  张力: 生成爆炸 vs 验证预算；自治深度 vs 验证层级（RSI 边界）
  弧线: 每个幸存发现 = 森林新节点 + 下一轮生成的先验
status: running (T1 已点火)
refs:
  - 学习循环前身: MATH_LOOP_ENGINE.md（七阶段/五 reward/R1-R5——本引擎复用其全部零件）
  - 循环设计学: ../讲透Loop/（五件套/验证阶梯/三守卫——本引擎的外循环规格）
  - 先例六系统: papers 见 §四（全部 2026 一手核实）
  - T1 实验: loops/experiments/discovery_T1_graph_conjectures.py
updated: 2026-08-26
---

# MATH_DISCOVERY_ENGINE：三轴组合爆炸研究循环

> **本文档是什么**：MATH_LOOP_ENGINE 的研究升级——学习循环（人学数学）装上发现循环（AI 产数学）。回答三个问题：**组合什么**（三轴清单）、**怎么爆**（进化四步）、**爆出什么算数**（验证级联 + 诚实分级）。

## 〇、愿景公式与物理基础

$$\text{发现引擎价值} = \underbrace{\text{生成多样性}}_{\text{模型×手段×对象}} \times \underbrace{\text{验证便宜度}}_{\text{reward 级联}} \times \underbrace{\text{记忆复利}}_{\text{知识卡回灌}}$$

成立条件是**验证不对称性**（查 < 做，讲透Loop Ch03）：生成侧可以狂野爆炸（组合不完是资产），因为验证侧足够便宜（Lean/穷举/SymPy 秒级裁决）；幸存者写入记忆成为下一轮生成的先验（复利）。**若验证与生成同贵，爆炸立即变负债**——这是选战场的第一判据（数学恰好是验证最便宜的领域，形式真理零 grounding 成本，讲透Loop Ch08）。

## 一、三轴清单（全部现有库存，无新采购）

| 轴 | 库存 | 角色 |
|----|------|------|
| **模型** | DeepSeek-Prover-V2-7B（本地 DCU）/ Qwen2.5-0.5B（本地）/ glm-4-flash（便宜 API）/ glm-5.3（强 API）/ 异构互判 | 不同先验的提议者；异构组合当独立验证器 |
| **手段** | Lean4+Mathlib（L5）/ SymPy+mpmath（L4 符号）/ 穷举+区间（L4 数值）/ OEIS+LMFDB（识别）/ delegation（oracle/debugger/fixer 并行）/ 进化采样（Elo+P-UCB，Nexus 制）/ schedule_job+RESUME（循环原语） | 从形式证明到群体搜索的全谱手段 |
| **数学** | 知识森林（30 锚点卡×R1-R5）/ 问题池（OEIS 开放猜想、formal-conjectures 的 Erdős Lean 形式化、Mathlib 未覆盖角）/ 讲透X 深挖单元 | 供给知识件 + 需求侧问题 |

## 二、引擎架构：进化循环四步

```
┌─ ① 变异 GENERATE ────────────────────────────────────────────┐
│   发现算子库（R1-R5 定理级化，见 §三）× LLM 提议 × 组合枚举      │
│   产出：猜想 / 证明草稿 / 构造（程序）—— 不要求对，要求多样      │
├─ ② 选择 SELECT ──────────────────────────────────────────────┤
│   验证级联（便宜→贵）：数值穷举 → 符号恒等 → Lean 0 sorry       │
│   级联早停：便宜层挂掉的不进贵层（FAR 的 cascade 思想）          │
├─ ③ 遗传 INHERIT ─────────────────────────────────────────────┤
│   幸存者 → 知识卡（含 PartialProof/Obstruction 失败卡，MMAT 制）│
│   高分个体进 population，Elo 采样当下一轮 prompt（Nexus 制）    │
├─ ④ 调度 SCHEDULE ────────────────────────────────────────────┤
│   四象限（自顶/自底 × BFS/DFS）：                              │
│   问题池 BFS（FAR 式扫文献） / 攻坚 DFS（Nexus 式单题）         │
│   森林 BFS（MLE 点亮） / 固化 DFS（讲透X/mathlib PR）          │
│   外循环规格与守卫：讲透Loop 12 问（cap/熔断/独立验证全套）      │
└─ 人的位置：方向设定（验证层级顶端之上）+ 终审（blocked 升级口）─┘
```

## 三、发现算子库（生成侧的语法）

| 算子 | 操作 | 森林级先例 → 定理级用法 |
|------|------|----------------------|
| **分解** | 目标→子目标链（跨度控制） | Prover 蒸馏规律①=ToMap 学术结论（Decomposer 是全管线瓶颈） |
| **综合** R2 | 结构叠加（群×拓扑=Lie 群） | 不变量配对穷举（T1 的 9×9×… 模板） |
| **类比** R5 | 不变量迁移（同调：拓扑→代数→QFT） | "X 在领域 A 的定理，搬到领域 B 还成立吗"——LLM 提议+穷举快筛 |
| **逆问题** R4 | 求↔给互换 | 已知必要条件 → 问充分性；恒等式 → 反解常数（Ramanujan Machine 制） |
| **公理反问** R1 | 删/弱化假设 | 定理去条件后穷举找反例（反例也是产出） |
| **数值启发** | 算→猜→验 | 序列→OEIS 反查→SymPy 确认→Lean（五 reward 级联的发现方向） |

## 四、六系统先例（2026 一手核实，挂 papers 纪律）

| 系统 | arXiv | 战果 | 借鉴 |
|------|-------|------|------|
| AlphaProof Nexus | 2605.22763 | 9/353 Erdős + 44/492 OEIS，几百美元/题 | 进化采样+Elo；basic agent（生成-验证交替）可复现 Erdős 级 |
| FAR | 2608.16977 | 5245 论文→6453 候选→77 人工审→15 真 | 问题选择是第一瓶颈；级联过滤省验证预算 |
| MECA | 2607.27709 | 机制为中心造猜想，35/100 被独立 prover 解决 | 猜想与机制联合精炼（防 ill-posed） |
| MMAT | 2607.04394 | 三 agent 闭环，2 月解 11 开放问题 | Obstruction 卡：死路也是知识 |
| ReasFlow | 2607.14178 | 知识卡驱动，5 篇完整论文 | declarative+procedural 双卡——work4ai 知识卡宇宙同构 |
| ToMap | 2607.11307 | +19% 全证明形式化 | 瓶颈在 Decomposer（与 Prover 蒸馏独立同结论） |

## 五、三档试点

| 档 | 内容 | 成本 | 验证 | 状态 |
|----|------|------|------|------|
| **T1** | TxGraffiti-mini：n≤7 全枚举图 × 9 不变量 × 4 模板族 → 幸存不等式 | 零 API | 穷举 | ✅ |
| **T1.5/T2** | 地毯式：图论升级（+谱/Zagreb/直径 18 不变量）+ 整数序列域 + 数学预筛 + 文献查证 | 零 API + 4 次 websearch | 穷举+随机 10k+文献 | ✅ **产出 S 级候选 C1**（见下） |
| **T4/T4b** | AI 数学域：矩阵不等式（log域，埋雷 8/8+det 恒等式独立发现）+ 熵锥（E3 校准 100% Shannon；E4 三层过滤 2820→378→0 真候选=扫描挖不到 non-Shannon，需符号推理） | 零 API | LP+反例库 | ✅ 完成（详见 [loops/experiments/discovery_T4_results_card.md](loops/experiments/discovery_T4_results_card.md)） |
| **T2.5** | **C1 攻坚（③ 裁决锁定）**：(a)✅ 文献深查确认 open（E±λ1±α 组合文献空白；SDP 线走 χf/Hoffman 方向非加项）→ (b)✅ **121,196 图零违反**（含结构族/切换带；K_n 取等 gap=-2e-14；17.1% 图上强于已知界）→ (c)🔥 Lean 形式化（本地 Mathlib v4.14 全量构建中，C1 陈述已写：`/tmp/opencode/C1lean/C1lean.lean`，证明路径四案见注释） | 本地 | Lean 0 sorry | 🔥 (c) 进行中 |
| **T3** | 完整四象限：FAR-lite 问题池 + 交叉匹配 + 攻坚 + 固化 | agent 编排 | 五件套+三守卫 | 待启 |

## 六、T2 地毯式搜索结果（2026-08-26，S 级发现）

**两域漏斗**：图论 26 万检查→4471 幸存→3 真候选；序列域 3 千检查→0 真候选。186 条已知 rediscover 作校准。详见 [loops/experiments/discovery_T2_carpet_search.md](loops/experiments/discovery_T2_carpet_search.md)。

**S 级候选 C1**：$\mathcal{E}(G) \geq n + \lambda_1 - \alpha$——
- 证据：n≤7 全枚举 + n=8..11 随机图 10,000 张零违反 + 星族 n=8..15 全过；
- 价值：Fajtlowicz/Graffiti 1980s 猜想 E≥2(n-α) 于 2026 刚被证明（2607.19817+等号图 2608.04367），**C1 在 19% 随机图与全部星族上严格强于它**，且不被蕴含——40 年猜想战场的直接延长线；
- 引擎叙事：Graffiti 是 TxGraffiti 的前身——**本引擎与目标定理同门**，机器猜想传统的 2026 延续。

**A/B 级**：γ+μ₁≤n+λ₁（λ₁<2 图族开放区域）；γ+μ₁≤n+μ（Brand-Seifter 插值）。

**四条引擎教训**：① dummy filtering 仍是主瓶颈（80% 幸存是已知对的线性组合——需"已知不等式组合闭包"检测器）② 价值在**跨族交叉**（谱×组合）——单族内部已被 30-40 年机器猜想扫净 ③ 查证即校准（rediscover 计数=引擎可信度）④ 浮点不变量的 tight 判定需改分位数贴边度。

## 六·旧、T1 结果（2026-08-26，discovery_T1_graph_conjectures.py）

- 穷举 1253 图（n≤7 全部）× 9 不变量（n/m/Δ/δ/ω/α/χ/γ/μ 全精确计算）× 4 模板族 ≈ 260 万次候选检查，秒级；
- **验收通过**：Nordhaus-Gaddum 和式（χ+α≤n+1）与积式（α·χ≥n）被 rediscover；伪命题 ω·α≥n 被 C5 正确拒收——引擎的接受与拒收双通路都被验证；
- 幸存者分层：已知/定义 flagged + **tight unflagged 候选**（等号可达且无已知标记）= 查文献与 Lean 形式化的工作清单（结果 json：`loops/experiments/discovery_T1_results.json`）；
- 诚实边界：n≤7 穷举 = 强证据**不是证明**；unflagged ≠ 新定理，是"值得查"。

## 七·RL、Agent 技术注入（T3 实验线，2026-08-26）

发现循环的 RL 形式化（与讲透Loop Ch08 IMPROVE 算子同构）：

| RL 概念 | 发现引擎对应 | 实现档位 |
|---------|-------------|---------|
| episode | 一轮发现（选臂→生成→级联验证→reward） | T3 ✅ |
| 策略 π | 臂选择分布 | UCB1（Nexus P-UCB 极简版）✅ |
| 动作空间 | 臂=（不变量族对×模板）窄 48 / 不变量级宽 624 | 双档对照 ✅ |
| reward | 0.3·tier/3 + 0.5·tight + 0.2·novelty（富信号，FunSearch 教训） | ✅ |
| 课程学习 | 级联验证 n5→n7→随机 n8-10 | ✅（=curriculum：便宜课先上） |
| 经验回放 | Obstruction 记忆（死区避开） | ✅ 简版 |
| 进化采样 | 候选级 parent 邻域（Nexus Elo 制） | ⬜ 下一步 |

**T3 双空间对照结论（discovery_T3_rl_engine.py）**：
- 窄 48 臂：UCB 8 vs uniform 11 金标——**探索非瓶颈时 bandit 无优势**（早期噪声 Q 反而误导）；
- 宽 624 臂：UCB 13 vs 9、到 5 金标 5 轮 vs 9 轮——**空间贫瘠化后学习价值显现**（≈2 倍加速）；
- **Goodhart 现场演示**：reward 未编码"跨族价值"，agent 涌向 ×基础（n/m）平庸高分区——修法：reward 加跨族深度项 / LLM critic（MECA 制）/ 候选级进化（Nexus 制）。

**T2+ 跨分支扫描结论（discovery_T2plus_crossbranch.py）**：
- 域C 数论×图论：χ(D(n))=Ω(n) 埋雷 FAIL——**埋雷者（人）的定理本身错了**（除子 Hasse 图恒二部 χ=2，引擎算对了）：验证不对称性连人都防，埋雷验收双向工作；
- 域C2 真候选：**ω(n) ≤ γ(X_n) ≤ 2ω(n)**（单位元凯莱图支配数被素因子个数双边夹）；
- 域D 代数×数论：卷积闭包 22 命中/56 未命中（1*λ=平方指示等已知恒等式在表外被独立撞上）；未命中样本的 p^k 值序列 = 闭式猜想素材（接 OEIS 反查）；
- 工程坑实录：eps 表 off-by-one（[1]+[0] 把幺元放 n=0）、稠密图精确 χ 回溯爆炸（贪心+ω 夹逼通道修复）、τ 剪枝。

## 八、诚实边界（引擎的三条宪法）

1. **发现分级**：T1 产出机器验证的小事实（真但小）；T2 是开放猜想的新证明（有先例可循）；Erdős 级需前沿模型+重算力——本地 7B 的合理地盘是 T1/T2；
2. **RSI 边界**（2607.07663）：bounded self-refinement 安全区内运转（猜想→验证→再猜想收敛循环）；"自动设定研究方向"在验证层级顶端之上——**方向归人，执行归机器**；
3. **成本宪法**（讲透Loop Ch11）：每档试点先写 X/Y 账（成本上限 vs 预期产出），Nexus 参考价几百美元/题，本地档必须显著低于此。

## 挂网

- 上游：[MATH_LOOP_ENGINE.md](MATH_LOOP_ENGINE.md)（学习循环——本引擎的 L1-L4 内件）、[../讲透Loop/](../讲透Loop/)（循环设计学——外循环规格与守卫）
- **总纲**：[BIDIRECTIONAL_FLYWHEEL.md](BIDIRECTIONAL_FLYWHEEL.md)（本引擎=飞轮的 AI→Math 环；引擎自举台账在总纲 §三）
- 下游：loops/experiments/（试点实验线）、Prover harness（T2 攻坚手）
- 更新协议：每档试点点火/收官刷新 §五 §六；先例表新条目必须先过 papers 纪律（ID 现场核实）
