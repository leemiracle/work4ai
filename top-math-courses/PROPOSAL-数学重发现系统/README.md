# PROPOSAL：数学重发现系统（Math Rediscovery System）
> ⚠️ **状态更新 2026-08-28**：本 proposal 已被 [../MATH_AGENT_HARNESS.md](../MATH_AGENT_HARNESS.md) 吸收取代——发现引擎本体见 [../MATH_DISCOVERY_ENGINE.md](../MATH_DISCOVERY_ENGINE.md)（已运行 T1-T4b）。本文档降级为历史参考：13 发现算子与 RediscoveryBench 协议已被 harness 卡 §三吸收。

> **一句话**：融合知识探索机制（检索/类比/反例/多样性）与搜索-压缩-验证循环，以「重发现已知顶会级数学成果」为评测协议的 math agent 系统。
> **创建**：2026-08-28 ｜ **状态**：纲领 v1.0（P0 已启动）
> **依托**：math-expert-pro（八重视角知识体系）+ 讲透Lean4数学/实分析 + coding plan 基础设施 + ai-agent-book 实验框架

---

## 1. 理论基础：数学发现的算子学

### 1.1 总框架（修正版 Polya 循环）

$$\text{数学} = \underbrace{\text{展开}}_{\text{ENUMERATE/VARY}} + \underbrace{\text{压缩}}_{\text{COMPRESS/ABSTRACT}} + \underbrace{\text{探边}}_{\text{STRETCH/NEGATE}} + \underbrace{\text{翻译}}_{\text{TRANSLATE/ANALOGIZE}} + \underbrace{\text{验证}}_{\text{PROVE}}$$

五种运动螺旋上升，非单向"具体→抽象"。核心修正（相对经典 Polya 框架）：
1. **证明是发现的引擎而非终点**（Lakatos《证明与反驳》）：证明尝试→局部卡点→反例→概念barrelling→更精细定理；
2. **边界探索（stretching）**：在 (假设强度, 结论强度) 平面上找精确边界——发现的产出常常不是新定理而是精确化的边界；
3. **横向类比**：跨域结构匹配，最好的类比是"部分类比"——断裂点就是新数学的位置（Montgomery-Dyson 时刻）；
4. **死胡同的正面价值**：DEAD-END-MAP（边界的负空间测绘，五次方程→Galois）；
5. **Multiples 现象是重发现的科学史依据**（Merton）：多重独立发现是常态→发现是结构空间成熟度（Zeitgeist）的函数→时间切片知识库 = 可控 ready 度的实验装置。

### 1.2 发现算子库（13 算子，可计算接口）

| 算子 | 输入→输出 | AI 实现 | 历史案例 |
|---|---|---|---|
| ENUMERATE | 问题→解空间 | 约束求解/采样 | Euler 桥→图论 |
| VARY | 解→邻域解 | 参数扰动 | 方程变形 |
| **STRETCH** | 定理→(最弱假设,最强结论)边界 | 边界二分搜索 | 素数定理误差项史 |
| **NEGATE** | 猜想→反例 | 反例搜索器 | Weierstrass 函数；Frey 曲线 |
| PROVE-PROBE | 猜想→证明卡点→概念修正 | Lean proof state 分析 | Lakatos 循环 |
| **TRANSLATE** | 问题A域→B域 | 跨域词典（依赖图对齐） | 解析几何 |
| **ANALOGIZE** | 结构A↔B 同构+断裂点 | 子图匹配+断裂检测 | Montgomery-Dyson |
| COMPRESS | 实例集→最短描述 | MDL/程序合成 | FunSearch 哲学（Kolmogorov 先验） |
| SYMMETRIZE | 状态空间→群作用→不变量 | computational invariant theory | Galois/Noether |
| GENERALIZE/SPECIALIZE | 定理↔上下移动 | 约束增删 | Lp 空间 |
| **DUALIZE** | 对象↔对偶 | 范畴对偶自动化 | Pontryagin 对偶 |
| **QUESTION-GEN** | 结构→好问题集 | Graffiti 式猜想生成 | Hilbert 23 问 |
| **DEAD-END-MAP** | 失败轨迹→边界负空间 | 记忆层账本 | 五次方程 300 年→Galois |

（加粗 = 相对用户 12 层框架的增量算子；12 层框架见对话记录，本表是其可计算化。）

## 2. 系统架构：五层

```
⑤ 反思层：world rehearsal（脑内彩排）· 类比案例库 · 探索策略进化（AlphaEvolve search mode）
④ 记忆层：探索轨迹账本（DEAD-END-MAP 持久化）· recall ledger · 经验提炼
③ 验证层：Lean kernel（完美 grounding）· 数值验证 · 反例检索（NEGATE 主场）
② 探索层：发现算子库调度——island 模型（类比岛/边界岛/反例岛各绑定算子组合）
          · diversity 选择（MMR/DPP）· bandit 预算分配（算子粒度）
① 知识层：时间切片知识库（重建"成果发现前的世界"）· 依赖图（Matlas 式拓扑展开）
          · slogan 化检索 · L0/L1/L2 层次（OpenViking 经验迁移）
```

### 关键设计决策
1. **时间切片防泄漏**：重发现 1994 年的成果，只暴露 ≤1993 年的知识状态（Matlas 式带年份 statements + 引用图遮断后继）；严格版 = cutoff 前模型 + cutoff 后成果。
2. **回应 OEIS 负结果**（朴素 arXiv 检索不提升数学发现）：flat RAG 无效 ≠ 结构化知识探索无效——差异化在依赖图导航/反例检索/多样性激励三者，这是可检验假设（P0 即验证）。
3. **重发现路径对照**：agent 探索轨迹 vs 历史真实发现路径的量化对比——"AI 数学直觉 vs 人类数学史"的独立科学产出。

## 3. Benchmark：RediscoveryBench-Math

| Tier | 目标 | 可行性证据 |
|---|---|---|
| T1 教科书级 | 经典定理重发现 | Self-Supervised Theorem Discovery（从公理自增长定理库） |
| T2 经典研究级 | 20 世纪重要引理/构造 | OEIS Open 44% @$200；AlphaEvolve 75% 重发现率 |
| T3 顶会级 | 2015-2025 论文核心引理 | Station 重构 Jacobian 反例；HorizonMath GPT-5.4 Pro 超 2 项 SOTA |

**评分四维**：重发现成功（kernel/数值/构造三类验证）· 路径相似度（vs 历史证明路径）· 发现效率（LLM 调用数/检索次数）· 知识利用率（检索是否改变探索方向——Lego-RL 式条件分布检测）。

**首批题目来源**：AlphaEvolve 问题库（67 题公开含验证代码）+ Formal Conjectures solved set（836）+ HorizonMath + 10 篇顶会论文核心引理（手工筛）。

## 4. 赛道坐标（2026-08 检索核实）

| 工作 | 与本系统的关系 |
|---|---|
| FIRE-Bench（arXiv:2602.02905） | 重发现评测范式已被验证（ML 实证域，F1<50）；**数学域空白** |
| Station（arXiv:2608.23691） | 多智能体开放世界已产出重发现孤立案例（Jacobian 反例/Takhanov-Yun 恒等式） |
| AlphaEvolve（arXiv:2506.13131 + 2511.02864） | 搜索引擎上限参考；search mode（进化搜索策略而非构造）是②层设计依据 |
| Formal Conjectures（arXiv:2605.13171） | 2615 Lean 4 形式化题库 + kernel 验证 = ③层基础设施 |
| OEIS Open（arXiv:2608.11941） | **负结果警示**：47.6 万篇 flat arXiv 检索无效 → 本系统差异化假设的靶子 |
| LeanSearch v2 / Lean Finder / LeanPremise | 知识层检索基线（premise selection 谱系） |
| Matlas（arXiv:2604.17484）/ 9M Theorem Search | 时间切片库的构建蓝图（依赖图拓扑展开 + slogan 化） |
| HorizonMath（arXiv:2603.15617） | generator-verifier gap 三分类（closed-form/optimization/construction）= 验证层协议 |

## 5. 实施路线

### P0（已启动，2026-08-28）
- [x] 理论框架定稿（发现算子库 13 算子）
- [x] 接入 math agent：math-expert-pro/.opencode/skill/math-discovery/（项目级 skill）
- [x] 可执行算子最小库（discovery_operators.py：ENUMERATE/STRETCH/NEGATE 可跑版）
- [ ] 最小验证 demo（具体数学探索案例跑通算子循环）
- [ ] P0 实验设计：AlphaEvolve 公开库挑 5 题 + 时间切片检索 + coding plan 跑搜索-验证闭环 → 检验"结构化检索是否打破 OEIS 负结果"（正负皆可发表）

### P1（3-6 月）
T1 教科书重发现 50 题 + 路径对照分析 → workshop 级产出（benchmark + 机制消融）。

### P2（6-18 月）
T2/T3 扩展 + 全算子消融（diversity/bandit/world rehearsal）→ 主会级：系统论文或"重发现成功率 as ready 度函数"的数学史量化论文。

## 6. 风险与诚实预期

1. T3 系统化重发现可能被证明当前模型不可行——但失败诊断本身有发表价值（FIRE-Bench 模式）；
2. 防泄漏协议无法彻底屏蔽参数记忆——需报告泄漏敏感性分析；
3. 算力差距（AlphaEvolve TPU 级）——Station 已证开源栈可行；T1/T2 不需要该量级（OEIS：$50-200/attempt）。

## 7. 资产连接

| 资产 | 用途 |
|---|---|
| math-expert-pro（461 会话知识体系） | 知识层种子 + 算子 skill 宿主 |
| 讲透Lean4数学/实分析 × Tao companion | 验证层 + "单人版重发现"工作流范本 |
| coding plan（8 模型 + embedding-3） | 探索循环的推理与检索底座 |
| ai-agent-book 实验框架（registry patch/横评/评测协议） | harness 层直接复用（Harbor 五条协议） |
| world-ai4sci-math 2200 篇 arXiv | 时间切片种子语料 |
| OpenViking L0/L1/L2 + android-demo 记忆三件套 | 知识层/记忆层架构蓝图 |
