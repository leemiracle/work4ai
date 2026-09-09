# Neo-OS · L2.5 Formal Rule Layer

> **Soundness 保证层**——Lean4 形式化的因果规则，保证解释无幻觉。LLM 输出经规则过滤，证明不了的标"低置信度"。
>
> 权威 spec：[`00-constitution/DESIGN.md`](../../00-constitution/DESIGN.md) §一 L2.5 节

---

## 状态：🟢 C2 命门已达标（Phase 0 完成 → Phase 1 待扩规则集）

C2 council 验收：**非平凡 Lean4 规则可证，sorry 清零**。

| 规则集 | Lean4 文件 | sorry 状态 | 命门 |
|---|---|---|---|
| 5 toy 不变式（V11）| `formal-seed/Main.lean` | ✅ 0 | V11 语法可行 |
| **spinlock×preempt v2** | `formal-seed/NeoOsFormalSeed/SpinlockPreempt.lean` | ✅ 0 | **C2 语义可行**（omega 无能为力）|
| **Raft ElectionSafety** | `formal-seed/NeoOsFormalSeed/RaftElection.lean` | ✅ 0 | 对齐 dsyme RE5 |
| **Raft committedMono** | `formal-seed/NeoOsFormalSeed/RaftRules.lean` | ✅ 0 | 对齐 dsyme hcommitted_mono |
| **Raft LogMatching** | `formal-seed/NeoOsFormalSeed/RaftLogMatching.lean` | ✅ 0 | 零公理 |
| **DistilledRules 48 条** | `formal-seed/NeoOsFormalSeed/DistilledRules.lean` | — | L2 蒸馏产物 |

详细验证报告：[`formal-seed/VERIFICATION.md`](./formal-seed/VERIFICATION.md)

---

## 当前实现

### [`formal-seed/`](./formal-seed/) — Lean4 项目

```
formal-seed/
├── lakefile.toml              # Lean4 lib: NeoOsFormalSeed
├── lean-toolchain             # leanprover/lean4:v4.21.0
├── Main.lean                  # 入口（5 toy 不变式 + 主定理 soundExplanation_acyclic）
├── NeoOsFormalSeed.lean       # lib 根（导入所有子模块）
└── NeoOsFormalSeed/
    ├── Basic.lean             # 基础类型
    ├── SpinlockPreempt.lean   # C2 命门（5 定理 sorry=0）
    ├── RaftRules.lean         # Raft committedMono
    ├── RaftElection.lean      # Raft ElectionSafety（disjoint 推导）
    ├── RaftLogMatching.lean   # Raft LogMatching
    └── DistilledRules.lean    # L2 蒸馏的 48 条规则
```

### 验证

```bash
cd 04-layers/l2_5-formal-rules/formal-seed
lake build    # ✅ 通过
# 检查 sorry
# echo '#print axioms NeoOs.Inv_preserved_over_trace' | lake env lean
# 应输出 [propext, Quot.sound]（Lean core），无 sorryAx
```

---

## 与上下游的契约

| 方向 | 契约 |
|---|---|
| **上游输入** | L2 蒸馏规则（`data/l2_distilled_rules*.lean`）→ 形式化验证（通过则保留，否则丢弃）|
| **下游输出** | 已验证规则 → [`l3-explain/`](../l3-explain/) Intuition/Formal/Trace 三层讲解的 Formal 层 |

---

## 三级置信度（DESIGN.md L2.5 节）

- **★★★ 可证明**（Lean4 verified）— 当前所有 Raft/spinlock 规则
- **★★ 软规则**（高置信但不形式化）— Phase 1 待积累
- **★ LLM 直觉**（标注低置信）— Phase 1 待积累

---

## Phase 1 升级路线

1. **扩规则集**：从 6 + 48 → 数百条（接 L1 真实 trace 归纳）
2. **autoformalize 闭环**：LLM 给候选规则 → Lean4 验证 → 通过则入 DistilledRules
3. ** Cedar 范式补充**：运行时策略审计（与 Lean4 静态证明分层，规则 ID 共享，见 [CONSTITUTION.md](../../00-constitution/CONSTITUTION.md) §深度洞察）
4. **LeanDojo/ReProver** 集成：LLM 辅助证明，降形式化成本

**反 Hurd 红线**（CONSTITUTION.md 附录）：
- ❌ 不用 RL 学习 Lean4 规则作基座
- ❌ 不做全代码验证（seL4 20 人年级成本）
- ✅ Cedar 范式（属性级 + 运行时监督）

---

## 引用

- work4ai 理论弹药：[`03-methodology/from-work4ai.md`](../../03-methodology/from-work4ai.md) §B（讲透控制论/因果推断/符号主义）
- 深度调研：[`02-research/deep/R2-lean4-os-verification-sota.md`](../../02-research/deep/R2-lean4-os-verification-sota.md)
- 第一域决策：[`01-decisions/FIRST_DOMAIN_DECISION.md`](../../01-decisions/FIRST_DOMAIN_DECISION.md)
