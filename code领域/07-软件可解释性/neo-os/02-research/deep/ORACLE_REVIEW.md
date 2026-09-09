# Oracle 架构 Review · 对抗层设计 v1.1

> **Reviewer**：独立架构 reviewer（@oracle，GLM-5.1）| **日期**：2026-08-05
> **对象**：`ADVERSARIAL_LAYER_DESIGN.md` v1.1 + `DC-prep-notes.md` + `SpinlockPreempt.lean` + `../../06-adversarial`（attacker.py v0 实证）
> **立场**：找漏洞是使命，不客气。每条「你错了」都给理由。
> **判决**：**NO-GO（v1.1 如设计）→ CONDITIONAL-GO（A1 方案）**

---

## 致命问题（必须修，否则 v0 会主动伤害项目）

### F1. Oracle 回归（infinite regress）——设计根本没有逃出命门

**你错了**，当 TL;DR 第 3 条说「Neo-OS 明确否认 trace 是 ground truth——正确性必须来自独立 oracle」。这句话的潜台词是「oracle 是 ground truth」，**但 oracle 不是**。

| Oracle 候选 | 谁验证它正确？ | 真实可信度 |
|---|---|---|
| seL4 Isabelle spec | seL4 团队**手写**的抽象规约。证明只断言「C refines spec」，**不断言「spec 满足用户意图」** | spec 可能编码错误意图，与 trace 同病 |
| kernel 文档 | 已知有大量过时/错误文档 | 与「buggy kernel」共享同一群作者、同一套传统，**错误模式高度相关** |
| seLe4n（v1 候选）| **单作者、3 star、无同行评审** | 引用它做 oracle = 把未审计的形式化当真理，**比无 oracle 更危险** |
| LLM 把文档转 Lean4 | 与 L2 蒸馏**完全相同的 autoformalization 管线** | 见 F2 |

§8.3 提到 Ashby，但把它框成「残余风险」是粉饰。真实情况：oracle 把「证错规则」的问题原封不动搬到「证错 oracle」这一层。**oracle 的价值不在于「正确」，而在于「与 trace 的错误模式去相关」**。

**修复方向**：TL;DR 第 3 条改成：

> 「Neo-OS 否认**任何单一来源**（trace 或 oracle）是 ground truth。可信度来自**多个错误模式去相关的来源之间的一致性**，而非来自某个『独立 oracle』。oracle 不逃出命门，它**重新分布**命门。」

★★★ 不再意味着「已验证正确」，而是「多源去相关一致」。

### F2. Oracle v0 与它要审计的 L2 是**同一条管线**——结构性失能

L2 蒸馏：`LLM(commit_text) → Lean4 规则 R`
Oracle v0：`LLM(doc_text) → Lean4 断言 → 与 R 对齐`

**这是同一种操作**（NL→Lean4 autoformalization）跑两次。autoformalization 错位率 15-20% **对两者同样适用**，且错误**正相关**（共享 LLM、共享 kernel 话语传统）。

`grind` 验证「断言可证」，**不是「断言匹配文档语义」**。vacuously true 的断言（如 `∀ s, True → Inv s`）能 type-check、能被 grind 证、能「对齐」任何 R——然后 Oracle_alignment=1.0，★★★。

**ITPEval 发现：type-check pass ≠ 语义等价，仅 54% BEq**。这正是 Oracle v0 的失败模式。**Oracle v0 在结构上不比它要审计的对象更可信**。

**修复方向**：v0 砍掉 Oracle Agent。见替代方案 A1。

### F3. 「mutant trace」与「mutant rule」概念混淆——方法论与引用论文对不上

设计里有两套「mutant」，没区分：
- **§3.2 mutators 表**：swap/delete/insert/perturb **事件**（trace mutation）
- **DC-prep-notes + 现有 `pair_discipline_is_necessary`**：把 `safe` 改成 `safe'`（**rule mutation**）

arXiv:2606.01794 的 Tridirectional mutate 的是**合约代码**。在 Neo-OS 抽象层里，「合约代码」对应不到任何单一对象——你只能 mutate rule 或 trace，**两者都不是论文方法论的忠实迁移**。

**修复方向**：明确选 **rule sensitivity analysis**（mutate safe/Inv，测哪些条件必要），诚实命名，不叫「discriminating power」。

### F4. 现有主定理陈述假设 `OK s es`——无法直接喂 mutant trace

```lean
theorem Inv_preserved_over_trace :
    ∀ (s : S) (es : List Ev), OK s es → Inv s → Inv (final s es)
```

这个定理要求 `OK s es`（trace 满足 safe）。Attacker 想生成「持锁区间插入 schedule」的 mutant trace——这种 trace **不是 OK**。`lean4_check(rule_R, m)` 怎么跑？

- 选项 A：丢掉 `OK` 假设 → 命题对任意 es 是假的（`lockRelease` 不持锁就打破 Inv）→ 所有 mutant「否决」= 假阳性
- 选项 B：只生成「仍 OK 的 mutant」→ 测不到真正危险的 trace
- 选项 C：定义新谓词、新定理 → 重新设计

`lean4_check` 在设计里被当作透明调用，**实际不存在这个 API**。

**修复方向**：写 Attacker 之前，先**重新陈述定理**为不依赖 OK 的形式，例如 `preserves_Inv (es : List Ev) (s : S) : Prop := Inv s → Inv (final s es)`。

### F5. 模型本身测不到最重要的 spinlock bug 类——`schedule` 是 no-op

```lean
| Ev.schedule => s   -- step schedule 不改状态
```

`schedule` 对状态**完全无影响**。「持锁时不能 schedule」的危险**只编码在 `safe` 里**，没编码在 `step` 语义里。

后果：Attacker 生成「持锁区间插入 schedule」的 mutant。trace 跑过 `final`，状态不变，**Inv 自然保持**。设计标记为「规则盲点」——但这是**模型盲点**，不是规则盲点。

**对抗层在当前模型上跑，会把模型缺陷误报为规则缺陷**。最阴险的失败模式：你以为在测规则，实际在测模型的语义覆盖度，而且不知道。

**修复方向**：先**扩展 `step` 语义**，让 schedule 持锁时进入「bad state」（新增 `deadlocked : Bool` 字段，或用 `Option S`）。

### F6. 相关错误能让错误规则拿 ★★★（最致命失败模式）

四条路径，全部现实：
1. Oracle 与 trace 共享同一误解（F1）
2. Mutant 类不覆盖真实 bug（F5）
3. seLe4n 错了（F1）
4. Oracle 断言 vacuously true（F2）

**关键洞察**：★★★ 定义是「三方都通过」。三方**都通过**在「三方错误正相关」时恰恰是最强的错误信号。当前设计把「三方一致」当可信度证据，但**没有量化三方的错误相关性**。

**修复方向**：★★★ 必须额外要求「至少一个来源经过**人工审计**」或「来源错误模式**已知去相关**」。否则 ★★★ 不颁发。

---

## 重要问题（应该修）

### I1. 引用越界——数学 benchmark 论文不支持系统域论点

§2.1 说「三份独立审计证明『Lean4 自验证 ≠ 规则正确』」。**你错了**。这些论文是关于**数学 benchmark 污染**（题目泄漏到训练集），**不是**「Lean4 证出来的定理可能错」。在数学域 Lean4 kernel 是 sound 的。

系统域问题（trace 固化 bug）**不需要这些引用支持**——它自己就成立，理由是「distilled rule ≠ axiom」。

**修复**：删掉这段引用，改成直接论证。

⚠️ **额外警告**：DC-prep-notes 引用的 arXiv:2606.01794 / 2604.10392 / 2607.19407 全是 2026 年极新论文。记忆铁律：「arXiv ID 错误率 30-50%」。**这些 ID 应在落盘前 webfetch 核实**。

### I2. OS 场景与 Solidity 本质差异——minimal-diff 可能失效

Solidity：单线程、离散状态机、漏洞类 crisp、mutant = 代码 diff。
spinlock+preempt：真并发，但模型是 `List Ev`（**已丢并发维度**）。

minimal-diff 前提是「单语义差异可孤立」。在 Solidity 成立，在 `List Ev` 线性模型**部分成立**（压扁丢了你最该测的东西）。

**修复**：承认「我们在 toy 线性模型上借用 Solidity 方法论，结论适用范围受限」。

### I3. LLM 生成「单差异」mutant——没有强制机制

设计说「手工边界类 + LLM 生成 mutant」。LLM 倾向多处修改。无 AST-level diff 计数，「单差异」前提无法保证。

**修复**：实现 mutant 验证器——AST diff，只接受 changed_nodes == 1。

### I4. Attack-to-Property 闭环——无收敛保证，可能无限膨胀

§3.3 闭环：failed mutant → 新规则 R' → 又失败 → 又生 R''……**无删除/合并/收敛机制**。规则库单调增长，过拟合已知攻击。

**修复**：加规则库预算 + 定期合并 + 删被蕴含的弱规则。或**砍掉闭环**——v0 只做单向测试。

### I5. Lean4 confidence attribute 是范畴错误

定理（timeless 数学事实）vs 置信度（empirical、可变）是**不同范畴**。自定义 attribute 需要 handler，会污染定理陈述可读性。

**修复**：置信度**只放 JSON sidecar**。删掉 Lean4 attribute。

### I6. 20 个 mutant 在 6 事件模型上——证据过薄

边界类上界很小（4-6 类）。每类 3-5 mutant 大部分等价。统计 survival_rate 在 n=5 上**没意义**。

**修复**：v0 追求**语义边界覆盖度**（覆盖率 X/8），不是 mutant 数量。

### I7. 阈值无根据

oracle_alignment ≥ 0.7、mutant_survival ≤ 0.2——**从哪来的**？没论证。

**修复**：标注「v0 占位阈值，待 N≥10 条规则后校准」。

### I8. 时间线乐观 2x

Day 1 实际是 Day 2-3（F4/F5 的 setup）。

---

## 建议（可考虑）

### S1（POSITIVE）. 核心直觉是对的

「证的不是错的规则」是真问题，且**正确识别为系统域 vs 数学域的根本差异**。这个 insight 是整个设计最有价值的部分，应保留并突出。修复方向是**重新框定**（F1）而非**抛弃**。

### S2（POSITIVE）. 优先级判断正确，但应更激进

Day 1 先做 Attacker 后做 Oracle——理由正确。结合 F2，更激进：**v0 完全砍掉 Oracle**。

### S3（POSITIVE）. seL4 Isabelle 决策正确

但应更彻底：作为「研究展望」提一句即可，不要在路线图给 v2+ 槽位。

### S4. provenance 替代 correctness 🟥

不要声称规则「已验证正确」。每条规则标 **provenance**：来自哪些 commit、匹配哪些文档段落、几源一致、是否人工审计过。让 L3 读者**自己解读** provenance。这与项目宪法「每条声称标验证等级」一致，且**不引入 oracle 回归**。

### S5. 「Fixes: 链」是真正的金矿，被低估了 🟥

oracle (e)「commit 投票 + Fixes: 链」标 ★★，但它是**最有系统域特色的 normative signal**：fix commit 把描述性 trace 转成规范性信号（fix 定义了「正确」）。比 kernel 文档**错误模式更去相关**。应提到 ★★★★，作 v0 主力 oracle。

### S6. 三道防线有冗余——Analyst 是 YAGNI 候选

Analyst 核心逻辑是加权函数。在前两道防线都失能时（F1/F2/F4），Analyst 综合的是噪声。**v0 砍掉 Analyst**。

---

## 替代方案

### A1（推荐）. Provenance-only v0，对抗层推迟到 Phase 1.5

**v0**：
1. 规则带 provenance tag（commits、docs、source count、人工审计 flag）——S4
2. 保留 `pair_discipline_is_necessary` 风格**手工 rule sensitivity mutant**（不自动化）
3. **砍掉** Oracle Agent、Attacker 自动化、Analyst、Attack-to-Property 闭环
4. Fixes: 链作主 normative signal（S5）

**何时重建对抗层**：等有了 ≥1 条**真正从 commit 蒸馏出来**的规则。**在手工规则上跑对抗层，测的是手工者，不是蒸馏管线**——最深的 YAGNI：**你还没东西可测**。

### A2. 两层而非三层

Oracle + 报告，砍掉 Attacker 和 Analyst。Oracle 用 **Fixes: 链 + 多版本一致性**（去相关源），不用 LLM 形式化文档（避免 F2）。

### A3. 先修模型，再谈对抗

F5 揭示模型测不到核心 bug。**先扩展 SpinlockPreempt.lean**：schedule 持锁时进入 bad state，加并发维度。

---

## 总判决

**NO-GO（v1.1 如设计）→ CONDITIONAL-GO（A1 方案）**

### NO-GO 理由

v1.1 **会主动伤害项目的认识论诚实使命**：
1. Oracle v0 与 L2 同构（F2）——审计者不比被审计者可信，★★★ 是假信号
2. 模型测不到核心 bug（F5）——对抗层把模型盲点误报为规则盲点
3. lean4_check 接口不存在（F4）——Day 1 计划无法执行
4. 相关错误给错误 ★★★（F6）——最致命失败模式无缓解

项目核心卖点依赖「每条声称标真实验证等级」。**当前 v1.1 制造看起来更严格、实际相关性不比 L2 强的「验证层」**，把无知伪装成知识，**抬高 CTC 而非降低**。违反宪法第三条。

### CONDITIONAL-GO 条件

1. **C-1（必须）**：采用 A1，v0 砍掉 Oracle Agent，provenance-only
2. **C-2（必须）**：webfetch 核实四个 arXiv ID（I1）
3. **C-3（必须）**：修复 F4——重新陈述定理或明确 mutant 只测 rule sensitivity
4. **C-4（应该）**：修复 F5——扩展 step schedule 语义，或明确标注模型局限
5. **C-5（应该）**：重写 TL;DR 第 3 条（F1）——oracle 重新分布命门
6. **C-6（应该）**：砍掉 Lean4 confidence attribute（I5）
7. **C-7（可考虑）**：砍掉 Attack-to-Property 闭环（I4）

---

## 附：预设反驳回应

| 你可能说 | oracle 回应 |
|---|---|
| 「v0 就是要简化」 | v0 简化 OK，但 v0 不能**制造假信号**。F2/F6 的 ★★★ 是假信号 |
| 「Oracle 多源投票能去相关」 | 能，但 v0 只有 kernel 文档单源。单源不去相关 |
| 「pair_discipline_is_necessary 已证明 mutant 有价值」 | 它证明了**手工 rule sensitivity** 有价值。没证明**自动化三层对抗**有价值 |
| 「Ashby 我们承认了」 | §8.3 承认残余风险，但没承认 **Oracle 层本身有同一问题**（F1）|
| 「我们要发表论文，需要新意」 | 真新意是「trace ≠ GT」insight（S1，保留）。三道防线是包装，且包装破了。**砍包装、突出 insight** 更有学术价值 |

---

*本 review 由 @oracle 产出，主 agent 落盘。如需针对 F1/F4/F6 展开更深论证，告知即可。*
