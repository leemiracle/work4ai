# neo-os 知识桥梁 —— 与本知识库的双向映射

> 本文件记录 **neo-os 项目**（`../neo-os`，通用复杂软件可解释性基础设施）与 **work4ai 知识库**（本项目）的**双向**知识关系。
>
> **关系一句话**：work4ai 是**方法论的源头**（"直觉→数学→代码→不足→应用"讲透范式 × 费曼门 × 17 视角）；neo-os 是**方法论的下游应用 + 反向回馈者**。neo-os 在立项探索中产出了 work4ai 缺失的前沿知识（→ 回流 work4ai），并把 work4ai 的"代码实证层"升级为"trace 实证层"（→ 回馈 work4ai 方法论）。
>
> **neo-os 立项目标**：用事件本体（L1）+ commit 蒸馏 world model（L2）+ Lean4 形式化规则（L2.5）+ 英文输出（L3），把任意复杂软件（OS / 浏览器 / 编译器 / 数据库 / 分布式）的行为翻译成**可证明的英文解释**。
>
> **neo-os 2026-08-05 重组**：仓库按数字编号目录重组（00-constitution / 01-decisions / 02-research / 03-methodology / 04-layers / 05-adapters / 06-adversarial / 07-experiments / 90-archive）。本文件的路径映射已同步。

---

## 〇、双向桥梁（核心）

| 方向 | 桥梁文件 | 内容 |
|------|---------|------|
| **work4ai → neo-os**（方法论下行）| [`../neo-os/03-methodology/from-work4ai.md`](../neo-os/03-methodology/from-work4ai.md) | neo-os 那边维护的引用索引：work4ai 每个核心资产 → neo-os 哪一层 → 当前用途与状态（A-F 六类）|
| **work4ai → neo-os**（方法论升级）| [`../neo-os/03-methodology/trace-native-upgrade.md`](../neo-os/03-methodology/trace-native-upgrade.md) | neo-os 的**原创贡献**：把 work4ai "代码实证层"升级为"trace 实证层"（见 [§七](#七neo-os-给-work4ai-的原创回馈trace-native-升级)）|
| **neo-os → work4ai**（知识回流）| 本文件 | 索引 neo-os 探索产出 → work4ai 讲透文件（见 [§二](#二已回流的通用知识gap-全表)）|

> 📌 **关键**：neo-os 在 `03-methodology/` 显式建立了"方法论契约层"——结构本身就是契约（任何人 `ls 03-methodology/` 就懂 provenance）。本文件是 work4ai 这一侧的对应契约。

---

## 一、知识回流的判定原则

neo-os 的产物分两类，**只有"通用 AI 知识"才回流** work4ai：

| 类别 | 例子 | 是否回流 |
|------|------|---------|
| ✅ **通用 AI/系统知识**（SOTA 调研、论文精读、方法论）| RL+形式证明 SOTA、Lean4 OS 验证、神经符号闭环 | **回流**（改写成讲透体）|
| ❌ **项目管理产物**（立项/评审/路线图）| CONSTITUTION、COUNCIL、ROADMAP、POSITION | 不回流（是 neo-os 项目档案）|
| ❌ **工程原型/数据**（代码、实验 jsonl）| 04-layers/*/*.py、04-layers/.../data/*.jsonl | 不回流（是 neo-os 工程产物）|

**改写纪律**：neo-os 是"探索报告体"（TL;DR + SOTA 表 + 对项目的启示），work4ai 是"讲透体"（直觉→数学→代码→局限→应用 + 费曼门）。回流时**必须改写不是搬运**——去掉 neo-os 项目特定内容（命门/council/C1-C4），保留核心知识（SOTA、原理、数字、arXiv ID），加上讲透包装。

---

## 二、已回流的通用知识（gap 全表）

下表列出 neo-os 有的通用知识 → work4ai 现状 → 回流后的位置。🔴 = 高 gap（work4ai 完全空白且是 2025-2026 前沿），🟡 = 中 gap。**neo-os 路径已同步到 2026-08-05 重组后的结构**。

| neo-os 源文件（重组后路径） | 主题 | work4ai 原状 | gap | 回流到 |
|--------------|------|-------------|-----|--------|
| [`02-research/rl/02a-rl-formal-proof.md`](../neo-os/02-research/rl/02a-rl-formal-proof.md) | RL + 形式证明（AlphaProof 谱系）| 讲透RL 仅 00-03 基础 | 🔴 | [`讲透RL/04-RL与形式证明.md`](./讲透RL/04-RL与形式证明.md) |
| [`02-research/rl/05-paper-limit-of-rlvr.md`](../neo-os/02-research/rl/05-paper-limit-of-rlvr.md) | **RLVR 的极限**（pass@k 反转，NeurIPS 2025 Oral）| ❌ 完全无 | 🔴 | [`讲透RL/05-RLVR的极限.md`](./讲透RL/05-RLVR的极限.md) |
| [`02-research/rl/02c-rl-systems.md`](../neo-os/02-research/rl/02c-rl-systems.md) | RL + 系统软件（MLGO/AlphaEvolve/Cold-RL）| ❌ 完全无 | 🟡 | [`讲透RL/06-RL与系统软件.md`](./讲透RL/06-RL与系统软件.md) |
| [`02-research/deep/R2-lean4-os-verification-sota.md`](../neo-os/02-research/deep/R2-lean4-os-verification-sota.md) | **Lean4 形式化 OS 验证 SOTA**（seL4/Verus/Atmosphere/seLe4n/Veil）| ❌ **完全无新主题** | 🔴 | [`讲透形式化验证/00-为什么形式化+Lean4SOTA.md`](./讲透形式化验证/00-为什么形式化+Lean4SOTA.md) |
| [`02-research/deep/R5-neuro-symbolic-loop-sota.md`](../neo-os/02-research/deep/R5-neuro-symbolic-loop-sota.md) | **神经符号闭环 SOTA**（AlphaProof/Delta-Prover/KVerus/VERISPECGEN）| ❌ **完全无新主题** | 🔴 | [`讲透神经符号/00-神经符号循环为什么是新范式.md`](./讲透神经符号/00-神经符号循环为什么是新范式.md) |
| [`02-research/deep/LEAN4_REWARD_BENCH.md`](../neo-os/02-research/deep/LEAN4_REWARD_BENCH.md) | Lean4 作为 RL reward verifier 的速度可行性（实测 sub-second）| ❌ 无 | 🟡 | [`讲透形式化验证/01-Lean4作为RL奖励验证器.md`](./讲透形式化验证/01-Lean4作为RL奖励验证器.md) |
| [`02-research/deep/R4-ai-software-explainability-landscape.md`](../neo-os/02-research/deep/R4-ai-software-explainability-landscape.md) | AI 驱动的软件可解释性竞品全景（4类竞品 + 解释性幻觉71.2%）| 讲透可解释性 仅模型可解释性（00-01）| 🟡 | [`讲透可解释性/S1-AI驱动的软件可解释性.md`](./讲透可解释性/S1-AI驱动的软件可解释性.md) |

### 已评估结案（不回流，附理由）

| neo-os 源文件 | 主题 | 不回流理由 |
|--------------|------|-----------|
| [`02-research/rl/02b-rl-scientific-discovery.md`](../neo-os/02-research/rl/02b-rl-scientific-discovery.md) | RL + 科学发现（GNoME/AI-Scientist）| 🟢 边际价值中：核心洞察（GNoME/AlphaFold 本质不是 RL）已在 [`讲透RL/04`](./讲透RL/04-RL与形式证明.md) 提及；剩余是应用综述 |
| [`02-research/rl/06-pass-k-experiment-design.md`](../neo-os/02-research/rl/06-pass-k-experiment-design.md) | pass@k 实验设计 | 🟢 边际价值低：是**实验方案非知识**；核心 pass@k 反转论证已在 [`讲透RL/05`](./讲透RL/05-RLVR的极限.md) 完整覆盖 |
| [`02-research/rl/04-rl-as-math-direction.md`](../neo-os/02-research/rl/04-rl-as-math-direction.md) | RL 作数学方向评估 | 🟢 不适合回流：高度**个人化**（基于个人画像的方向建议），非通用知识 |

### 待回流（留给后续轮次）

> ✅ **暂无待回流项**——所有 🔴 高 gap 与 🟡 中 gap 已全部处理完毕（已回流 7 份 / 已评估结案 3 份）。剩余 🟢 低优先级见上"已评估结案"表。

---

## 三、费曼检验（质量门）

work4ai 的费曼门（F1 外行复述 / F2 卡壳自曝 / F3 术语黑名单 / F4 回炉记录）**不再单独保存 `.费曼检验.md`/`.多视角.md` 衍生文件**（2026-08-10 起整合政策，原版 md 即唯一版本——衍生文件经核查全是自动生成空壳，无原创内容）。如需对某文件做费曼自检，临时跑：

```bash
python3 费曼学习法/feynman-coach.py "主题" --rounds 3   # 3 角色连环追问，戳穿"自以为懂"
```

> 🚨 **铁律**：F2/F4 必须作者本人答——AI 代写 = 伪造费曼。详见 [`费曼学习法/`](./费曼学习法/)。

---

## 四、跨项目概念对照

neo-os 的概念在 work4ai 里有对应讲透，便于交叉学习（对照 neo-os 的 [`from-work4ai.md`](../neo-os/03-methodology/from-work4ai.md) A-F 六类映射）：

| neo-os 概念 | work4ai 对应 | 备注 |
|------------|-------------|------|
| L3 英文接口（三层讲解 × 17 视角 × 费曼门）| 本项目根目录方法论 + [`费曼学习法`](./费曼学习法/) | neo-os L3 明确"继承 work4ai"（[§七](#七neo-os-给-work4ai-的原创回馈trace-native-升级) 的升级）|
| L2 world model（commit 蒸馏 7B）| [`讲透基础模型`](./讲透基础模型/) + [`讲透复用权重`](./讲透复用权重/) + [`讲透微调`](./讲透微调/) | 蒸馏 + 持续学习 + 每域 adapter |
| L2.5 Lean4 形式化规则 | [`讲透形式化验证`](./讲透形式化验证/)（本轮新建）+ [`讲透符号主义`](./讲透符号主义/) + [`讲透因果推断`](./讲透因果推断/) | Lean4 + 形式方法 + 因果 |
| L1 事件本体（eBPF）| [`讲透分布式AI系统`](./讲透分布式AI系统/) + [`讲透GPU与系统级`](./讲透GPU与系统级/) + [`讲透KV Cache`](./讲透KVCache/) | trace 流式处理 + 增量计算 |
| L0 硬件（Intel PT）| [`讲透GPU与系统级`](./讲透GPU与系统级/) | FlashAttention / 量化 / CUDA |
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
6. **路径同步**：neo-os 路径会随其重组变化，本文件引用 neo-os 时用相对路径并标注重组日期

---

## 六、neo-os 项目快速索引（供 work4ai 读者深入）

- **Gitee 仓库**：https://gitee.com/leemiracle/neo-os
- **本地路径**：`../neo-os`（相对于本项目）
- **立项时间**：2026-08
- **仓库结构**（2026-08-05 重组后）：`00-constitution`（立项宪法）/ `01-decisions`（决策）/ `02-research`（研究：deep + rl）/ `03-methodology`（work4ai 契约）/ `04-layers`（四层原型）/ `05-adapters` / `06-adversarial`（对抗层）/ `07-experiments`（pass-k）/ `90-archive`
- **核心纪律**："深度上专精，方法上通用。永远 N=2 提取，N=1 不泛化。"
- **必读（按顺序）**：[`00-constitution/CONSTITUTION.md`](../neo-os/00-constitution/CONSTITUTION.md) → [`00-constitution/POSITION.md`](../neo-os/00-constitution/POSITION.md) → [`03-methodology/from-work4ai.md`](../neo-os/03-methodology/from-work4ai.md) → [`02-research/EXPANDED_KNOWLEDGE.md`](../neo-os/02-research/EXPANDED_KNOWLEDGE.md) → [`00-constitution/ROADMAP.md`](../neo-os/00-constitution/ROADMAP.md)

---

## 七、neo-os 给 work4ai 的原创回馈：trace-native 升级

**这是双向知识流的关键**——neo-os 不只是 work4ai 的下游，它对 work4ai 的方法论有**一项 paper-grade 的原创升级**（见 [`../neo-os/03-methodology/trace-native-upgrade.md`](../neo-os/03-methodology/trace-native-upgrade.md)）：

### 升级内容

把 work4ai 三层讲解的第三层"**代码实证层**"（retrospective，事后构造示例）升级为"**trace 实证层**"（real-time ground truth，真实运行流的快照）：

```
work4ai 原版                          neo-os 升级版
─────────────                        ─────────────
直觉层（Intuition）                    直觉层（Intuition）           ← 不变
数学层（Math）                        形式化层（Formal）            ← 升级（Lean4 不变式）
代码实证层（Code）                    ★ Trace 实证层（Trace） ★    ← 核心升级（eBPF 真实 trace）
```

### 为什么这对 work4ai 有启发

| 维度 | work4ai 代码实证 | neo-os trace 实证 | 启发 |
|------|----------------|------------------|------|
| 可证伪性 | 弱（示例可重跑但不可证伪解释）| **强**（trace 可与解释对照，矛盾即破产）| 解释可被现实推翻 |
| 数据来源 | 事后构造 | 真实采集 | 不凭构造 |
| 适用场景 | 教学（讲概念）| 运行时（解释本机发生了什么）| 互补 |

> 📌 **对 work4ai 的潜在应用**：work4ai 当前是知识库（讲概念，代码实证足够）。但如果未来要做"AI 解释真实系统"的方向（如讲透 Agent 调试、讲透 LLM 推理过程），**trace 实证层是比代码实证更强的证据形式**。neo-os 已经趟出这条路，work4ai 可按需借鉴。

### neo-os 自己的定位（诚实标注）

neo-os 的 trace-native 升级目前 **Phase 1 prototype 的 trace 层仍是 GLM 构造的示例，非真实 eBPF 采集**（neo-os 自己标记为局限）。真实 trace 接入是 Phase 1 路线的待办。所以这是**方向性贡献**，工程上尚未完全落地——work4ai 借鉴时需注意此边界。

---

## 八、未回流的 neo-os 资产（备忘）

### 立项/评审类（neo-os 项目档案，不回流）
`00-constitution/`（CONSTITUTION / COUNCIL_FINAL_REVIEW / DESIGN / POSITION / POSITION_PAPER / ROADMAP）、`01-decisions/`（ADVERSARIAL_LAYER_DESIGN / FIRST_DOMAIN_DECISION / PROVENANCE_DESIGN / RESEARCH_QUESTIONS）、`02-research/`（BREADTH_DEPTH_ANALYSIS / EXPANDED_KNOWLEDGE / LOCAL_ASSETS / ROUND3_EXPLORATION）、`02-research/deep/`（ORACLE_REVIEW* / SYNTHESIS / DC-prep-notes）、`NEXT_STEPS.md`、`README.md`、`90-archive/`

### 工程原型类（neo-os 工程产物，不回流）
`04-layers/l2-world-model/c1_pipeline/`（commit 蒸馏 pipeline）、`04-layers/l2_5-formal-rules/formal-seed/`（Lean4 种子，含 SpinlockPreempt/RaftRules）、`04-layers/l3-explain/`（L3 解释引擎）、`06-adversarial/`（对抗层）、`07-experiments/pass-k/`、`04-layers/.../data/*.jsonl`（实验数据）

---

*本桥梁文件随 neo-os 探索进展与 work4ai 回流进度持续更新。最近一次更新：2026-08-05（同步 neo-os 重组 + 加双向引用 + trace-native 回馈 + 费曼骨架）。*
