# neo-os 知识桥梁 —— 与本知识库的映射

> 本文件记录 **neo-os 项目**（`../neo-os`，通用复杂软件可解释性基础设施）与 **work4ai 知识库**（本项目）的知识关系。
>
> **关系一句话**：work4ai 是**方法论的源头**（"直觉→数学→代码→不足→应用"讲透范式 × 费曼门 × 17 视角）；neo-os 是**方法论的下游应用**（L3 英文接口明确"继承 work4ai 方法论"）。但 neo-os 在立项探索中产出了大量 work4ai 体系里**缺失或薄弱的通用 AI 知识**——本文件索引这些知识的回流。
>
> **neo-os 立项目标**（背景）：用事件本体（L1）+ commit 蒸馏 world model（L2）+ Lean4 形式化规则（L2.5）+ 英文输出（L3），把任意复杂软件（OS / 浏览器 / 编译器 / 数据库 / 分布式）的行为翻译成**可证明的英文解释**。

---

## 一、知识回流的判定原则

neo-os 的产物分两类，**只有"通用 AI 知识"才回流** work4ai：

| 类别 | 例子 | 是否回流 |
|------|------|---------|
| ✅ **通用 AI/系统知识**（SOTA 调研、论文精读、方法论）| RL+形式证明 SOTA、Lean4 OS 验证、神经符号闭环 | **回流**（改写成讲透体）|
| ❌ **项目管理产物**（立项/评审/路线图）| CONSTITUTION、COUNCIL、ROADMAP、POSITION | 不回流（是 neo-os 项目档案）|
| ❌ **工程原型/数据**（代码、实验 jsonl）| prototype/*.py、prototype/data/*.jsonl | 不回流（是 neo-os 工程产物）|

**改写纪律**：neo-os 是"探索报告体"（TL;DR + SOTA 表 + 对项目的启示），work4ai 是"讲透体"（直觉→数学→代码→局限→应用 + 费曼门）。回流时**必须改写不是搬运**——去掉 neo-os 项目特定内容（命门/council/C1-C4），保留核心知识（SOTA、原理、数字、arXiv ID），加上讲透包装。

---

## 二、已回流的通用知识（gap 全表）

下表列出 neo-os 有的通用知识 → work4ai 现状 → 回流后的位置。🔴 = 高 gap（work4ai 完全空白且是 2025-2026 前沿），🟡 = 中 gap。

| neo-os 源文件 | 主题 | work4ai 原状 | gap | 回流到 |
|--------------|------|-------------|-----|--------|
| `explorations/rl/02a-rl-formal-proof.md` | RL + 形式证明（AlphaProof 谱系）| 讲透RL 仅 00-03 基础 | 🔴 | [`讲透RL/04-RL与形式证明.md`](./讲透RL/04-RL与形式证明.md) |
| `explorations/rl/05-paper-limit-of-rlvr.md` | **RLVR 的极限**（pass@k 反转，NeurIPS 2025 Oral）| ❌ 完全无 | 🔴 | [`讲透RL/05-RLVR的极限.md`](./讲透RL/05-RLVR的极限.md) |
| `explorations/rl/02c-rl-systems.md` | RL + 系统软件（MLGO/AlphaEvolve/Cold-RL）| ❌ 完全无 | 🟡 | [`讲透RL/06-RL与系统软件.md`](./讲透RL/06-RL与系统软件.md) |
| `docs/research/R2-lean4-os-verification-sota.md` | **Lean4 形式化 OS 验证 SOTA**（seL4/Verus/Atmosphere/seLe4n/Veil）| ❌ **完全无新主题** | 🔴 | [`讲透形式化验证/00-为什么形式化+Lean4SOTA.md`](./讲透形式化验证/00-为什么形式化+Lean4SOTA.md) |
| `docs/research/R5-neuro-symbolic-loop-sota.md` | **神经符号闭环 SOTA**（AlphaProof/Delta-Prover/KVerus/VERISPECGEN）| ❌ **完全无新主题** | 🔴 | [`讲透神经符号/00-神经符号循环为什么是新范式.md`](./讲透神经符号/00-神经符号循环为什么是新范式.md) |

### 待回流（本轮未做，留给后续）

| neo-os 源文件 | 主题 | 建议回流位置 | 优先级 |
|--------------|------|-------------|--------|
| `docs/research/R4-ai-software-explainability-landscape.md` | AI 软件可解释性竞品全景 | `讲透可解释性/`（现有 README+00，深化用）| 🟡 |
| `docs/research/LEAN4_REWARD_BENCH.md` | FormalRewardBench 论文（专门 prover 评估证明最差 24.4%）| `讲透形式化验证/01-形式化奖励的陷阱.md` | 🟡 |
| `explorations/rl/02b-rl-scientific-discovery.md` | RL + 科学发现（GNoME/AI-Scientist 去偏见）| `讲透RL/07-RL与科学发现.md` | 🟢 |
| `explorations/rl/06-pass-k-experiment-design.md` | pass@k 实验设计 | 并入 `讲透RL/05` 的实验章节 | 🟢 |
| `explorations/rl/04-rl-as-math-direction.md` | RL 作数学方向（三大支柱的应用熔炉）| `讲透RL/` 综述篇 | 🟢 |

---

## 三、neo-os 完整资产清单（备忘）

### 回流了（5 份核心知识 → 5 个讲透文件）
见上表。

### 未回流（项目管理 + 工程，留 neo-os 自用）

**立项/评审类**（neo-os 项目档案）：
- `CONSTITUTION.md`（三条初心）、`COUNCIL_FINAL_REVIEW.md`、`ORACLE_REVIEW.md` / `ORACLE_REVIEW_RESPONSE.md`
- `POSITION.md` / `POSITION_PAPER*.md`、`ROADMAP.md`、`FIRST_DOMAIN_DECISION.md`
- `NEXT_STEPS.md`、`LOCAL_ASSETS.md`、`BREADTH_DEPTH_ANALYSIS.md`
- `ADVERSARIAL_LAYER_DESIGN.md`、`PROVENANCE_DESIGN.md`
- `EXPANDED_KNOWLEDGE.md`、`ROUND3_EXPLORATION.md`（立项探索，部分含通用知识但偏项目语境）
- `RESEARCH_QUESTIONS.md`

**工程原型类**（neo-os 工程产物）：
- `prototype/c1_pipeline/`（commit 蒸馏 pipeline）
- `prototype/adversarial-layer/`（对抗层）
- `prototype/formal-seed/`（Lean4 种子，含 SpinlockPreempt/RaftRules）
- `prototype/l3/`（L3 解释引擎）
- `prototype/pass-k-experiment/`（pass@k 实验）
- `prototype/data/*.jsonl`（实验数据）

---

## 四、跨项目概念对照

neo-os 的某些概念在 work4ai 里有对应讲透，便于交叉学习：

| neo-os 概念 | work4ai 对应 | 备注 |
|------------|-------------|------|
| L3 英文接口（三层讲解 × 17 视角 × 费曼门）| 本项目根目录方法论 | neo-os L3 明确"继承 work4ai" |
| L2 world model（commit 蒸馏 7B）| [`讲透基础模型`](./讲透基础模型/) + [`讲透复用权重`](./讲透复用权重/) | 蒸馏 + 持续学习 |
| L2.5 Lean4 形式化规则 | [`讲透形式化验证`](./讲透形式化验证/)（本轮新建）| Lean4 + 形式方法 |
| C1 commit 蒸馏（root_cause 抽取）| [`讲透RL/06`](./讲透RL/06-RL与系统软件.md)（active learning）| 数据采样的 RL 视角 |
| RL 用于规则/证明 | [`讲透RL/04`](./讲透RL/04-RL与形式证明.md) + [`讲透RL/05`](./讲透RL/05-RLVR的极限.md) | RL 能力边界 |
| 神经符号闭环（AlphaProof 式）| [`讲透神经符号`](./讲透神经符号/)（本轮新建）| LLM + Lean4 自我博弈 |
| GRPO（DeepSeek-R1）| [`讲透RL/03-RLHF-DPO-GRPO`](./讲透RL/03-RLHF-DPO-GRPO.md) | 已有，是 04/05 的前置 |

---

## 五、方法论纪律（每次回流都要念）

1. **改写不是搬运**：neo-os 探索报告体 → work4ai 讲透体（直觉→数学→代码→局限→应用）
2. **去项目化**：去掉命门/council/C1-C4/对 Neo-OS 的启示等 neo-os 专属内容
3. **保留可信度标注**：arXiv ID 一手核实（✅）/ 二手（⚠️）/ 推断（⚡）必须保留，这是 work4ai 的来源纪律
4. **加配套链接**：每个回流文件要链回 work4ai 相关系列（如讲透RL 04 要链回 03 GRPO）
5. **尊重费曼门**：核心声称要能被"戳穿自以为懂"——保留反方证据、数字、失败模式

---

## 六、neo-os 项目快速索引（供 work4ai 读者深入）

- **Gitee 仓库**：https://gitee.com/leemiracle/neo-os
- **本地路径**：`../neo-os`（相对于本项目）
- **立项时间**：2026-08
- **当前状态**：v1.1 立项包完成，命门初步验证（Raft 域 commit 蒸馏达标 + Lean4 种子 sorry 清零）
- **核心纪律**："深度上专精，方法上通用。永远 N=2 提取，N=1 不泛化。"
- **必读（按顺序）**：`CONSTITUTION.md` → `POSITION.md` → `DESIGN.md` → `EXPANDED_KNOWLEDGE.md` → `ROADMAP.md`

---

*本桥梁文件随 neo-os 探索进展与 work4ai 回流进度持续更新。最近一次更新见 git log。*
