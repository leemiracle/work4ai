# Neo-OS · 对抗层设计（L2.5 Adversarial Layer）v2.0

> **版本**：v2.0（2026-08-05，基于 [ORACLE_REVIEW.md](../02-research/deep/ORACLE_REVIEW.md) 全面校正）
> **判决**：CONDITIONAL-GO（oracle 给 NO-GO on v1.1，本 v2.0 满足 C-1 到 C-6）
> **变更摘要**（v1.x → v2.0）：
> - **砍**：三道防线架构（Oracle/Attacker/Analyst）→ 因 F1（oracle 回归）/F2（同管线失能）/S6（Analyst YAGNI）
> - **换**：provenance tag（S4）+ Fixes: 链主力 normative signal（S5）+ 手工 rule sensitivity（F3 诚实命名）
> - **改**：★★★ 重新定义（F6，要求人工审计）+ TL;DR 重写（F1，oracle 重新分布命门）+ schedule 语义扩展（F5，已实现）
> - **删**：Lean4 confidence attribute（I5）/ Attack-to-Property 闭环（I4）/ 错误引用（I1）
> **服务命门**：council C2 验收 + 项目宪法第二条（形式化规约）

---

## 一、TL;DR（v2.0，回应 Oracle F1）

**v1.x（错）**：「Neo-OS 明确否认 trace 是 ground truth——正确性必须来自独立 oracle。」

**v2.0（对）**：

> **Neo-OS 否认任何单一来源（trace 或 oracle）是 ground truth。可信度来自多个错误模式去相关的来源之间的一致性。oracle 不逃出命门，它重新分布命门。**

三条核心结论：

1. **「证的不是错规则」是真问题**（Oracle S1 肯定）。在系统域，被证明的是「trace 保持 Inv」，不是「Inv 编码了正确行为」。这是 Lean4 soundness 之外的语义层问题（distilled rule ≠ axiom），与数学 benchmark 污染无关（I1 校正）。

2. **v1.x 的三道防线是「制造声称-验证差距的机器」**（Oracle F2/F6）。Oracle Agent 与 L2 同一条 autoformalization 管线，错误正相关；★★★「三方通过」在错误正相关时是最强假信号。**v2.0 砍掉三道防线，换 provenance tag**。

3. **真正的 normative signal 是 Fixes: 链**（Oracle S5）。fix commit 把描述性 trace 转规范性信号（fix 定义「正确」），比 kernel 文档错误模式更去相关。这是 v2.0 的主力可信度来源。

---

## 二、问题陈述（保留，但删 I1 错误引用）

### 2.1 核心威胁：trace 固化 bug

R5 §6 的根本难点，在系统域：

```
        L2 蒸馏                  L2.5 形式化              L3 输出
trace ──────────► 候选规则 R ──────────► 证明 R 成立 ──────────► 「可证明的解释」
   ▲                                              │
   │                                              ▼
   └──── 但如果 trace 来自 buggy kernel ◄────────┘
            则 R 可能固化 bug            解释披着 soundness 外衣
                                         却编码了错误行为
```

**这是系统域对 AlphaProof 范式的根本修正**：数学域里证明成立 = 对（ground truth 是数学真理）；系统域里证明成立 ≠ 对（ground truth 是「正确行为」，但 trace 可能不含正确行为）。

**注意**（I1 校正）：这个问题**不需要**引用 atp-checkers/miniF2F-v2/ProofGate 等数学 benchmark 污染论文支持。那些论文讲的是「benchmark 题目泄漏到训练集」，不是「Lean4 证出来的定理可能错」。在数学域 Lean4 kernel 是 sound 的。系统域问题自己成立，理由是「distilled rule ≠ axiom」。

### 2.2 v0 实证的重新解读（F5 校正）

`../06-adversarialattacker.py` v0 跑出的「Inv 只 1/5 判别力」需重新解读：

| 边界 | v0 判定 | v2.0 重新解读 |
|------|--------|-------------|
| B1a（preemptEnable pc≥1）| 🟥 盲点 | ⚠️ 模型盲点（Nat 饱和掩盖下溢）|
| B1b（配对纪律）| ✅ 判别力 | ✅ 真 rule sensitivity（保留）|
| B2a（schedule pc=0）| 🟥 盲点 | 🟥 **模型盲点冒充规则盲点**（schedule 是 no-op，F5）|
| B2b（schedule ¬lockHeld）| 🔵 冗余 | 🔵 冗余（Inv 间接覆盖）|
| B3（lockRelease 持有性）| 🟥 盲点 | ⚠️ 待 F5 扩展后重测 |

**结论**：v0 的「Inv 只 1/5 判别力」**部分是模型缺陷冒充**。SpinlockPreempt v2 已扩展 schedule 语义（加 deadlocked 字段），消除了 F5。

---

## 三、v2.0 架构：provenance + Fixes: 链 + 手工 rule sensitivity

### 3.1 v1.x 砍掉的部分（Oracle F1/F2/S6）

| v1.x 组件 | 状态 | 理由 |
|-----------|------|------|
| ❌ Oracle Agent（LLM 形式化文档）| 砍 | F2：与 L2 同管线，错误正相关 |
| ❌ Attacker 自动化 | 降级 | F3/F5：保留作方法论原型，不作生产层 |
| ❌ Analyst（综合置信度）| 砍 | S6：在前两道失能时综合噪声 |
| ❌ Attack-to-Property 闭环 | 砍 | I4：无收敛保证，可能无限膨胀 |
| ❌ Lean4 confidence attribute | 砍 | I5：定理 timeless vs 置信度 empirical，范畴错误 |
| ❌ 数学 benchmark 污染引用 | 砍 | I1：引用错位 |

### 3.2 v2.0 保留/新增的部分

#### 3.2.1 Provenance Tag（S4，核心）

每条规则带 provenance tag，**不压缩成单一置信度数字**，让 L3 读者自己解读：

```json
{
  "rule_id": "spinlock_preempt_pair_discipline",
  "lean4_theorem": "NeoOs.SpinlockPreempt.Inv_preserved_over_trace",
  "provenance": {
    "source_commits": ["abc123", "def456"],       // 蒸馏来源 commit
    "matched_docs": ["Documentation/locking/spinlocks.rst"],
    "source_count": 2,                             // 独立源数
    "fixes_chain": true,                           // 是否来自 Fixes: 链
    "human_audited": false,                        // 是否人工审计
    "lean4_proven": true,                          // Lean4 证明状态
    "axiom_record": ["propext", "Quot.sound"]      // 公理依赖
  }
}
```

**关键设计**：provenance 是**事实记录**，不是**可信度判断**。L3 输出层据此组织措辞，但不把多源一致性等价于「正确」。

#### 3.2.2 Fixes: 链作主力 normative signal（S5）

fix commit 的独特价值（v2.0 提升 oracle (e) 从 ★★ 到 ★★★★）：

- **描述性 → 规范性转换**：普通 commit 描述「系统做了什么」；fix commit 描述「系统**应该**做什么」（fix 定义了正确）
- **错误模式去相关**：fix commit 修复的 bug，与 kernel 文档（共享作者/传统）**错误模式更去相关**
- **因果链接明确**：`Fixes:` 标签提供 commit → bug → 正确行为的因果链

**v2.0 机制**：c1_pipeline.py 已抽取 `(symptom, root_cause, fix)` 三元组。`fix` 字段是规范性信号的源头——它是「正确行为」的操作定义。

#### 3.2.3 手工 Rule Sensitivity（F3 诚实命名）

保留 `pair_discipline_is_necessary` 风格的**手工**反例定理，不自动化：

- **诚实命名**：不叫「discriminating power」（暗示测 bug），叫「rule sensitivity analysis」（测规则形式必要性）
- **对象明确**：mutate 的是 safe/Inv 定义（rule mutation），不是 trace（trace mutation）
- **价值**：证明规则的某个条件是必要的（去掉则 Inv 不保持）

SpinlockPreempt v2 有两个反例定理：
- `pair_discipline_is_necessary`（v1 保留）：无配对纪律则 Inv 不保持
- `schedule_held_violates_Inv`（v2 新增）：持锁 schedule 进入 deadlocked，违反 Inv

### 3.3 ★★★ 重新定义（F6）

**v1.x（错）**：★★★ = Lean4 证明 + Oracle alignment ≥ 0.7 + Mutant survival ≤ 0.2

**v2.0（对）**：

| 等级 | 条件 | L3 输出策略 |
|------|------|-----------|
| **★★★** | Lean4 证明（sorry 清零）+ **provenance ≥ 3 源去相关一致** + **至少 1 源人工审计** | 「可证明的解释」+ 标注 provenance |
| **★★** | Lean4 证明 + provenance ≥ 2 源（部分去相关）| 「软规则」+ 标注 provenance |
| **★** | Lean4 证明（无 provenance 或单源）| 「形式证明级」+ 明确标注「未经独立验证，请谨慎」|

**关键**：★★★ **必须有人工审计**。不再有「自动 ★★★」——三方错误正相关时「自动一致」恰恰是最强假信号。

---

## 四、schedule 语义扩展（F5 已实现）

SpinlockPreempt v2（2026-08-05）已修复 F5：

```lean
structure S where
  preemptCount : Nat
  lockHeld     : Bool
  deadlocked   : Bool   -- v2 新增

-- step schedule 持锁时进入 deadlocked（真实 kernel：sleep 持锁 → 死锁）
| Ev.schedule => if s.lockHeld 
    then { preemptCount := s.preemptCount, lockHeld := s.lockHeld, deadlocked := true } 
    else s

-- Inv v2 加入 ¬deadlocked
def Inv (s : S) : Prop :=
  s.preemptCount ≥ 0 ∧ (s.lockHeld = true → s.preemptCount ≥ 1) ∧ s.deadlocked = false
```

**验证状态**（`#print axioms`）：
- `step_preserves_Inv`：[propext, Quot.sound] ✅
- `Inv_preserved_over_trace`：[propext, Quot.sound] ✅
- `pair_discipline_is_necessary`：**零公理依赖** ✅
- `schedule_held_sets_deadlock`：**零公理依赖** ✅（v2 新增）
- `schedule_held_violates_Inv`：**零公理依赖** ✅（v2 新增）

**意义**：模型现在能表达「持锁 schedule → deadlocked → 违反 Inv」这个 spinlock 最核心 bug 类。对抗层不再把模型盲点误报为规则盲点（F5 已消除）。

---

## 五、v0 定位（回应 Oracle A1）

`../06-adversarial` v0 的定位：

> ⚠️ **v0 = 方法论原型 + 工具链就绪，不是生产对抗层**。
> - 它在手工 SpinlockPreempt 上跑，**测的是手工者的规则敏感性，不是 L2 蒸馏管线的规则可信度**
> - 价值：验证对抗层方法可行（发现规则盲点）+ 工具链就绪（model.py + attacker.py 可复用）
> - **生产对抗层推迟到 Phase 1.5**：等 C1 蒸馏出第一条真正从 commit 来的规则

---

## 六、实施路线（v2.0 简化）

### Phase 1（与 C1 对齐）

1. **C1 真实抽取**（council 最高优先）：kernel commit 蒸馏，产出真实规则
2. **Provenance tag 设计**：规则带 (source_commits, matched_docs, source_count, fixes_chain, human_audited)
3. **Fixes: 链 normative signal**：c1_pipeline.py 的 `fix` 字段作规范性信号源

### Phase 1.5（等 C1 蒸馏规则）

4. **重跑对抗层 v1**：在 SpinlockPreempt v2（含 deadlocked）+ 蒸馏规则上跑
5. **Lean4 交叉验证**：写 lean4_checker.py，重新陈述定理（F4，不依赖 OK 的形式）
6. **手工 rule sensitivity 扩展**：为蒸馏出的每条规则手工构造反例定理

### Phase 2+（研究展望）

7. **多版本投票**：mainline vs stable vs longterm 一致性
8. **seL4 Isabelle spec**：作研究展望提一句，**不占路线图槽位**（Oracle S3，ITPEval 显示翻译成本极高）

---

## 七、与 LeVer / VERISPECGEN 的差异（v2.0 更新）

| 维度 | **Neo-OS v2.0** | LeVer (ACL 2026) | VERISPECGEN |
|------|----------------|------------------|-------------|
| **ground truth** | **否认任何单一来源**；provenance 多源去相关 | NL 需求（人写）| NL 需求（人写）|
| **核心机制** | **provenance tag + Fixes: 链** | 4-agent 闭环 | traceability map |
| **对抗** | 手工 rule sensitivity（不自动化）| Attacker agent | 对抗测试 |
| **置信度** | provenance 事实记录（不压缩）| 隐含 | 隐含 |
| **独特假设** | trace **和** oracle 都不是 GT | NL = GT | NL = GT |

**v2.0 的学术新意**（精简后更清晰）：
1. 明确否认任何单一来源是 ground truth（系统域对 AlphaProof 的认识论修正）
2. Fixes: 链作为描述性→规范性转换的独特信号（系统域独有，数学域不存在）
3. provenance 替代 correctness（不引入 oracle 回归）

---

## 八、风险与局限（v2.0 更新）

| # | 风险 | v2.0 应对 |
|---|------|----------|
| 1 | provenance 多源仍可能集体错误 | ★★★ 要求人工审计（最后一道防线）|
| 2 | Fixes: 链可能 fix 了错误方向 | 多 fix 交叉 + 人工审计 |
| 3 | 手工 rule sensitivity 覆盖不全 | 承认局限，Phase 1.5 用 LLM 辅助发现边界 |
| 4 | Ashby 必要变异度律 | 诚实立场：v2.0 大幅压低「证错规则」概率，但不归零 |

---

## 九、与三条初心的对齐

| 初心 | v2.0 的贡献 |
|------|------------|
| 第一条（commit 蒸馏）| Fixes: 链作 normative signal，强化「commit 是规范性语料」的定位 |
| 第二条（形式化规约）| schedule 语义扩展（F5）让 C2 真建模 spinlock 死锁；★★★ 重定义让 soundness 诚实 |
| 第三条（降 CTC）| provenance 让 L3 输出诚实标注证据来源——**避免披着 soundness 外衣的幻觉反而抬高 CTC** |

---

## 十、📌 下一步

### 已完成（v2.0）
- ✅ SpinlockPreempt v2（F5 修复，sorry 清零）
- ✅ oracle review + 回应（ORACLE_REVIEW.md + RESPONSE.md）
- ✅ 本设计文档 v2.0

### Phase 1 立即
1. **C1 真实抽取**（kernel commit）—— 所有后续的前置
2. **provenance tag 设计**——规则的证据来源记录
3. **Fixes: 链 normative signal**——c1_pipeline 的 fix 字段利用

### Phase 1.5（等 C1）
4. 重跑对抗层 v1（在 v2 模型 + 蒸馏规则上）
5. Lean4 交叉验证（F4 重新陈述定理）

---

*v2.0 作为对抗层设计的新基线。v1.x 的分析价值保留在 ORACLE_REVIEW.md；本文档是实施依据。初心校正回到 [CONSTITUTION.md](../00-constitution/CONSTITUTION.md)。*
