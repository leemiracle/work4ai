# D+C 调研笔记 —— 对抗层实施的实现指南

> **元数据** | 日期：2026-08-05 | 服务于 [ADVERSARIAL_LAYER_DESIGN.md](../../01-decisions/ADVERSARIAL_LAYER_DESIGN.md) v1.1 修正
> **D 来源**：arXiv:2606.01794（Tridirectional Discriminating-Power，已 webfetch HTML 核实）
> **C 来源**：seL4/l4v README + ITPEval（arXiv:2607.19407，已 websearch 核实）

---

## 一、D — Minimal-Diff Mutant 策略细节（从 arXiv:2606.01794 提炼）

### 1.1 核心方法论：手工语义导向，非随机 fuzzing

论文的关键立场（§1.3 + §5.5）：

> "A single hand-constructed minimal-diff mutant is a principled choice over an operator-derived corpus — a security-critical semantic regression test specifically optimized for formal specification boundary detection, distinct from the random syntactic perturbations automated mutation operators typically produce."

**翻译**：单个手工构造的 minimal-diff mutant 优于算子生成的语料库——它是**安全关键语义回归测试**，专为形式化规约边界检测优化，区别于自动变异算子通常产生的随机语法扰动。

**对 Neo-OS Attacker Agent 的直接修正**：v1.0 设计的「4 类随机突变算子（swap/delete/insert/perturb）」**不够**——那是 fuzzing。真正的 minimal-diff 方法论要求：

1. **语义导向选择突变点**：不是随机选事件位置，而是选**安全关键语义边界**（如 spinlock 持有区间内的 schedule、preempt 配对边界）
2. **单一差异原则**：每个 mutant 只改一处安全关键语义，其余完全相同（signature/control flow/API）
3. **可区分性假设**：mutant 在 code-shape 层与原版不可区分，只在 body-semantics 层不同——这是规则必须捕捉的

### 1.2 Tridirectional 判别力结构（论文核心贡献）

arXiv:2606.01794 的判别力量化是 **tridirectional**（三方向），非二元：

| 方向 | trace 性质 | 期望规则行为 | Neo-OS 对应 |
|------|----------|-----------|-----------|
| **正例**（positive）| 已验证正确的运行 | 规则成立 | Lean4 已证 `Inv_preserved_over_trace` |
| **反例**（negative）| 已知 bug trace（如 DAO 2016 攻击）| 规则**否决** | 历史 bug commit 蒸馏的违规 trace |
| **边界**（boundary）| minimal-diff mutant | 规则**否决** | Attacker 生成的单差异 mutant |

**判别力谓词**（discriminating power predicate，§5.1）：

一个规则 R 有判别力 ⟺ R 在正例上成立 ∧ R 在反例上否决 ∧ R 在边界（minimal-diff）上否决。

**关键洞察**：边界方向是判别力的真正体现——「pattern recognition 在 structural-adjacency boundary 退化」。随机 fuzzing 测不出这个；只有 minimal-diff 能。

### 1.3 flashLoanVulnerable 构造细节（§5.5，可迁移模式）

论文的 boundary case 构造（§2.4 + §5.5）：

```
flashLoan（safe，production）          flashLoanVulnerable（mutant，手工）
─────────────────────────              ─────────────────────────
相同：                                  差异（单处安全关键）：
- 函数签名                              body fails to engage the guard
- callback interface (IFlashLoanReceiver)  pattern's body invariant correctly
- 控制流形状                            at the callback boundary,
- surface API                           leaving a reentrancy window
- CEI ordering（checks-effects-         其余完全相同
  interactions）形状
```

**可迁移到 Neo-OS spinlock+preempt 的模式**：

| spinlock 正确版（production）| spinlock mutant（手工 minimal-diff）|
|-------------------------------|-------------------------------------|
| `safe(preemptEnable): pc≥1 ∧ (lockHeld→pc≥2)` | `safe'(preemptEnable): pc≥1`（漏掉 lockHeld→pc≥2）|
| 其余 5 事件 safe 完全相同 | 其余完全相同 |
| Inv 成立 | Inv 在 ⟨1,true⟩→preemptEnable→⟨0,true⟩ 违反 |

**这正是现有 `pair_discipline_is_necessary` 反例定理做的事**——但论文的方法论把它**系统化**：不是手工一个，而是 Attacker Agent 自动生成一类「单安全关键差异」mutant。

### 1.4 D 对 Attacker Agent v1.0 设计的修正

| v1.0 设计 | v1.1 修正（基于 D）|
|-----------|------------------|
| 4 类随机突变算子（swap/delete/insert/perturb）| **语义导向 minimal-diff**：识别安全关键语义边界，每 mutant 改一处 |
| mutant_survival_rate 单一指标 | **tridirectional 判别力**：正例成立率 + 反例否决率 + 边界否决率 |
| 随机生成 n_mutants | **手工 + LLM 混合**：手工定义语义边界类，LLM 在每类内生成具体 mutant |
| 无 ground truth bug trace | **纳入历史 bug commit** 作反例方向（接 c1_pipeline 的 bug-fix trace）|

---

## 二、C — Oracle 来源可行性矩阵

### 2.1 seL4 spec 现状（github.com/seL4/l4v，已核实）

seL4 的形式化栈**全部是 Isabelle/HOL**：

| spec 层 | 内容 | 形式 |
|---------|------|------|
| `spec/abstract/` | functional abstract specification | Isabelle/HOL |
| `spec/sep-abstract/` | separation kernel spec | Isabelle/HOL |
| `spec/haskell/` | Haskell model（与 C 同步）| Haskell → Isabelle（自动）|
| `spec/capDL/` | capability distribution | Isabelle/HOL |
| `tools/c-parser/` | C → Simpl（Isabelle）| 自动翻译 |
| `tools/autocorres/` | C → higher-level Isabelle functions | 自动抽象 |

**结论**：seL4 spec **无 Lean4 版本**。要用需 Isabelle→Lean4 翻译。

### 2.2 Isabelle→Lean4 翻译可行性（ITPEval，arXiv:2607.19407）

ITPEval 是首个跨 ITP 翻译 benchmark（Lean4/Rocq/Isabelle/HOL Light），关键发现：

| 指标 | 数值 | 含义 |
|------|------|------|
| statement translation pass@1 | **29.1%** | LLM 把 Isabelle 定理翻译到 Lean4，仅 29% 能 type-check |
| proof translation pass@1 | **10.5%** | 完整证明翻译更难 |
| controlled theorems proof pass@1 | 29.7% | 自包含 axiomatized 文件 |
| ecosystem theorems proof pass@1 | **5.2%** | 真实库依赖（library mismatch 是最大失败源）|
| Lean4 BEq 语义等价 | **54%** | 即使 type-check 通过，仅 54% 语义等价（type-checking 高估语义保真）|

**结论**：**无可靠的 Isabelle→Lean4 自动翻译工具**。LLM 翻译 pass@1 仅 29%，语义等价仅 54%。直接用 seL4 Isabelle spec 作 Oracle **工程成本极高**（需手工翻译 + 语义保真验证）。

### 2.3 Oracle 来源决策矩阵

| 来源 | 可信度 | Lean4 现成？ | 工程成本 | 覆盖面 | 决策 |
|------|--------|------------|---------|--------|------|
| seL4 Isabelle spec | ★★★★★ | ❌（需翻译，pass@1 29%）| 极高（人月级）| 窄（微内核）| **长期目标**（v2+）|
| **seLe4n Lean4 spec** | ★★★★ | ✅（已是 Lean4）| 低（引用）| 中（调度/IPC/VSpace）| **v1 候选**（谨慎，单作者无评审）|
| **kernel 文档** | ★★★★ | ❌（NL→Lean4 靠 LLM）| 中（LLM + 验证）| 广 | **v0 已选**（现实可行）|
| dsyme Raft Lean4（716T）| ★★★★★ | ✅ | 低（引用）| Raft 域专 | **v1 候选**（若第一域=Raft）|
| 多版本一致性 | ★★★ | N/A（数据驱动）| 中 | 中 | v1+ 补充 |
| commit 投票 + Fixes: | ★★ | N/A | 低（已有 c1_pipeline）| 海 | **v0 补充信号** |

### 2.4 Oracle Agent 路线图（v1.1 修正）

| 版本 | Oracle 来源 | 预期 oracle_alignment 精度 |
|------|-----------|--------------------------|
| **v0**（Day 2）| kernel 文档（spinlocks.rst）+ Fixes: 信号 | ~0.6-0.7（LLM 形式化文档有噪声）|
| **v1**（Phase 1 末）| + seLe4n Lean4 spec（调度/锁不变式直接引用）+ dsyme Raft（若域匹配）| ~0.8 |
| **v2+**（Phase 2+）| + seL4 Isabelle spec（手工翻译关键模块）+ 多版本投票 | ~0.9 |

**关键决策**：v0 不依赖 seL4 Isabelle spec（成本太高）；v1 评估 seLe4n spec 层（已是 Lean4，省翻译）；seL4 Isabelle 作为长期研究目标。

---

## 三、对 ADVERSARIAL_LAYER_DESIGN.md 的 v1.1 修正清单

基于 D+C，设计文档需以下修正（用 edit 标注 v1.1）：

1. **§3.2 Attacker Agent**：从「4 类随机突变」升级为「语义导向 minimal-diff + tridirectional 判别力」（借鉴 arXiv:2606.01794）
2. **§3.1 Oracle Agent**：明确 v0（kernel 文档）/ v1（seLe4n + dsyme）/ v2+（seL4 Isabelle）路线图；记录 Isabelle→Lean4 翻译成本（ITPEval pass@1 29%）
3. **§6 实施路线 Day 1**：mutator 实现从「随机 4 类」改为「手工定义语义边界类 + LLM 生成具体 mutant」
4. **§7 验收标准**：判别力指标从「mutant_survival_rate ≤ 0.2」改为「tridirectional：正例成立 + 反例否决 + 边界否决」

---

## 四、📌 下一步（进入 A+B）

### A（Day 1，Attacker v0 实现）的具体调整

基于 D 的修正，Attacker v0 实现应：

1. **先手工定义 spinlock+preempt 的语义边界类**（不随机）：
   - 边界类 1：preemptEnable 的 lockHeld 条件（现有 `pair_discipline_is_necessary` 已示范）
   - 边界类 2：schedule 的 preemptCount=0 条件
   - 边界类 3：lockRelease 的 lockHeld=true 前置
   - 边界类 4：事件顺序敏感性（lockAcquire 必须在 preemptDisable 之后/之前？）
2. **每类用 LLM 生成 3-5 个具体 mutant**（在 SpinlockPreempt.lean 的 safe/Inv 上做最小修改）
3. **tridirectional 评估**：
   - 正例：现有 `Inv_preserved_over_trace` 在正确 trace 上成立（已证）
   - 反例：从 c1_pipeline 的 LOCK_SYNC 类 bug commit 蒸馏违规 trace
   - 边界：上述 minimal-diff mutant
4. **输出判别力报告**：规则在三类上的成立/否决矩阵

### B（并行，oracle review）

委派 `@oracle` 对**修正后的 v1.1 设计**做独立深度 review，重点问：
- 语义导向 minimal-diff 是否真能覆盖 spinlock+preempt 的所有安全关键边界？
- Oracle v0 用 kernel 文档 + LLM 形式化，引入的新幻觉如何控制？
- tridirectional 判别力是否有更优的量化方式？

---

*D+C 调研完成。设计文档将据此做 v1.1 修正；A 的实现指南已具体到「手工语义边界类 + LLM 生成 mutant」。*
