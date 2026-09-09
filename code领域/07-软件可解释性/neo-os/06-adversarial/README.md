# Neo-OS · 对抗层 v0（Adversarial Layer v0）

> **状态**：v0 跑通，实证发现已在 SpinlockPreempt 上验证
> **日期**：2026-08-05
> **设计依据**：[ADVERSARIAL_LAYER_DESIGN.md](../01-decisions/ADVERSARIAL_LAYER_DESIGN.md) v1.1（注：v2.0 已出，见下警告）
> **方法论来源**：arXiv:2606.01794（Tridirectional Discriminating-Power）

---

## ⚠️ 重要校正（Oracle Review 后，2026-08-05）

### 校正 1：v0 定位（Oracle A1）

本原型是**方法论验证 + 工具链就绪**，**不是生产对抗层**。

- 它在**手工** SpinlockPreempt 上跑，**测的是手工者的规则敏感性**，不是 L2 蒸馏管线的规则可信度
- 价值：验证对抗层方法可行（发现规则盲点）+ 工具链就绪（model.py + attacker.py 可复用）
- **生产对抗层推迟到 Phase 1.5**：等 C1 蒸馏出第一条真正从 commit 来的规则

### 校正 2：F5 重新解读（schedule no-op）

v0 发现的「3 盲点」需重新解读。Oracle Review F5 指出：v1 模型的 `step schedule = s`（no-op）测不到 sleep 持锁死锁，**把模型盲点误报为规则盲点**。

| 边界 | v0 判定 | F5 后重新解读 |
|------|--------|-------------|
| B1a（preemptEnable pc≥1）| 🟥 盲点 | ⚠️ 模型盲点（Nat 饱和掩盖下溢）|
| B1b（配对纪律）| ✅ 判别力 | ✅ 真 rule sensitivity（保留）|
| B2a（schedule pc=0）| 🟥 盲点 | 🟥 **假盲点**（schedule 是 no-op，F5）|
| B2b（schedule ¬lockHeld）| 🔵 冗余 | 🔵 冗余（Inv 间接覆盖）|
| B3（lockRelease 持有性）| 🟥 盲点 | ⚠️ 待 v2 模型重测 |

**修复**：SpinlockPreempt v2 已扩展 schedule 语义（加 `deadlocked : Bool` 字段，持锁 schedule 进入死锁态）。v0 需在 v2 模型上重跑才有意义。

详见 [ORACLE_REVIEW.md](../02-research/deep/ORACLE_REVIEW.md) F5 + [ORACLE_REVIEW_RESPONSE.md](../02-research/deep/ORACLE_REVIEW_RESPONSE.md) §4.6。

---

## 以下为 v0 原始报告（保留作历史记录，含上述校正前的解读）

---

## 一、v0 是什么

对抗层的第一道实现（Attacker Agent v0），用**纯 Python 模拟** SpinlockPreempt 语义（不依赖 lake/Lean4），跑 tridirectional 判别力评估。

**核心机制**（v1.1 修正后，借鉴 arXiv:2606.01794）：
- **不做随机 fuzzing**，而是手工定义 5 个安全关键语义边界
- 每个边界构造 minimal-diff mutant safe（去掉单一条件）
- 用揭示性 trace 测试 Inv 在 mutant 下是否仍保持
- tridirectional：正例（成立）/ 边界（mutant）/ 冗余（被间接覆盖）

---

## 二、怎么跑

```bash
cd 06-adversarial
python3 model.py       # 先跑模型自测（对照 Lean4 已验证结果）
python3 attacker.py    # 跑 tridirectional 判别力报告
```

无外部依赖（纯 Python 标准库）。

---

## 三、🟥 v0 的核心实证发现

### 发现 1：现有 Inv 只对 1/5 安全边界有判别力

| 边界 | 描述 | 判定 | 含义 |
|------|------|------|------|
| **B1a** | preemptEnable 要求 pc≥1（防下溢）| 🟥 盲点 | Inv 没检查 pc 下溢（Nat 饱和掩盖）|
| **B1b** | preemptEnable 持锁时须留 pc≥2（配对纪律）| ✅ 判别力 | Inv 捕捉到了（对应现有 `pair_discipline_is_necessary`）|
| **B2a** | schedule 要求 pc=0（不可 atomic 调度）| 🟥 盲点 | Inv 没编码 schedule 约束 |
| **B2b** | schedule 要求 ¬lockHeld（不可持锁调度）| 🔵 冗余 | Inv 的「持锁→pc≥1」间接覆盖（schedule 要 pc=0，矛盾）|
| **B3** | lockRelease 要求 lockHeld=true（不可释放未持有）| 🟥 盲点 | Inv 第二子句 vacuously true（lockHeld=false 时）|

**判别率：1/5 = 20%**（目标 ≥80%，未达标）

### 发现 2：直接印证 R5 §6 命门

R5 §6 警告：「Lean4 自验证 ≠ 规则正确」。v0 的实证：

> 现有 `Inv_preserved_over_trace` 主定理 sorry 清零，`#print axioms` 仅 propext + Quot.sound（数学级可靠）。**但 Inv 本身只捕捉了 5 个安全边界中的 1 个**。如果 L2 蒸馏出这个 Inv，Lean4 会给它盖上「soundness」章，但它对 3/5 真实 bug 视而不见。

**这就是「trace 固化 bug → 完美证明错误规则」的具体形态**：不是 Inv 错了，而是 Inv **过窄**——它只编码了「持锁时 pc≥1」，漏了 schedule/lockRelease/preemptEnable-pc-lower-bound 的约束。

### 发现 3：3 个盲点 → Attack-to-Property 新 Inv 子句候选

| 盲点 | 建议 Inv 扩展 |
|------|-------------|
| B1a（preemptEnable pc≥1）| 扩展 Inv 加入 `preemptCount` 单调性约束，或建模真实 kernel 的 `int`（非 Nat）语义 |
| B2a（schedule pc=0）| 扩展 Inv 加入 `schedule 只在 pc=0 时发生` 的时序约束（需 richer 状态机）|
| B3（lockRelease 持有性）| 扩展 Inv 加入 `lockRelease 前置 lockHeld=true` 的状态依赖 |

### 发现 4：1 个冗余边界 = Inv 设计的意外红利

B2b（schedule ¬lockHeld）在 Inv 约束下无法独立触发——因为 Inv 的「持锁→pc≥1」+ schedule 的 pc=0 要求 = 矛盾，所以持锁时 schedule 会被 pc=0 挡住。**这说明 Inv 的设计有意外的覆盖红利**，值得在论文中标注。

---

## 四、v0 的方法论价值

1. **量化 Inv 完备性**：从「sorry 清零 = 可靠」升级到「判别率 20% = 不完备」
2. **系统化盲点发现**：手工反例定理（`pair_discipline_is_necessary`）只发现 1 个盲点边界；v0 系统化发现 3 个 + 1 个冗余
3. **实证 R5 §6 命门**：不再是逻辑推断，是 SpinlockPreempt 上的实测数据
4. **Attack-to-Property 的具体输入**：3 个盲点直接给出 Inv 扩展建议

---

## 五、v0 的局限

1. **Python 模拟 vs Lean4 语义差异**：Nat 饱和减法掩盖了 B1a 的下溢 bug（真实 kernel int 可负）
2. **手工边界类**：5 个边界是人工定义，可能漏掉其他安全关键语义
3. **未跨 Lean4 交叉验证**：v0 纯 Python，未调 lake 确认 mutant 在 Lean4 的行为一致
4. **未接 c1_pipeline**：反例方向（negative）暂用手工状态，未从真实 bug commit 蒸馏

---

## 六、下一步（v1）

1. **扩展 Inv**：基于 3 个盲点的 Attack-to-Property 建议，构造 Inv' 并重新跑判别力（目标 ≥80%）
2. **Lean4 交叉验证**：用 `lean4_checker.py` 调 lake，确认 mutant 在 Lean4 的行为与 Python 一致
3. **LLM 生成边界类**：用 GLM 从 kernel 文档自动发现更多安全关键语义边界
4. **接 c1_pipeline**：反例方向从 LOCK_SYNC 类 bug commit 蒸馏违规 trace
5. **Oracle Agent v0**：用 kernel 文档（spinlocks.rst）给 Inv 打 oracle_alignment 分数

---

## 七、文件结构

```
.
├── README.md          ← 本文件（v0 实验报告）
├── model.py           ← SpinlockPreempt Python 语义模型（1:1 映射 Lean4）
└── attacker.py        ← Attacker Agent v0（语义边界 + mutant + tridirectional eval）
```

---

*v0 的核心价值不是「跑通」，而是**实证暴露了 Inv 的不完备性**——这把 R5 §6 的命门从逻辑推断变成可量化的工程问题。*
