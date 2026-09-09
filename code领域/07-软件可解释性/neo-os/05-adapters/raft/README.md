# Neo-OS · Raft adapter（第一域）

> **第一域 = Raft 共识**（已锁定，详见 [`FIRST_DOMAIN_DECISION.md`](../../01-decisions/FIRST_DOMAIN_DECISION.md)）。
>
> 三重 ground truth：Jepsen 21 issue + dsyme 716 定理 + Ongaro TLA+。

---

## 状态：🟢 语料已蒸馏 + 形式化锚点已接 + Phase 1 待完整集成

### 已完成（Phase 0）

| 项 | 文件 | 状态 |
|---|---|---|
| etcd/Raft commit 抽取 | [`04-layers/l2-world-model/data/etcd_c1_results.jsonl`](../../04-layers/l2-world-model/data/etcd_c1_results.jsonl) | ✅ N=89, root_cause 97% |
| 抽取报告 | [`04-layers/l2-world-model/data/raft_extraction_report.md`](../../04-layers/l2-world-model/data/raft_extraction_report.md) | ✅ |
| Lean4 ElectionSafety | [`04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftElection.lean`](../../04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftElection.lean) | ✅ sorry=0（对齐 dsyme RE5）|
| Lean4 committedMono | [`04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftRules.lean`](../../04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftRules.lean) | ✅ sorry=0（对齐 dsyme hcommitted_mono）|
| Lean4 LogMatching | [`04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftLogMatching.lean`](../../04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftLogMatching.lean) | ✅ sorry=0 |
| L3 三层讲解（4 规则）| [`04-layers/l3-explain/explanations.md`](../../04-layers/l3-explain/explanations.md) | ✅ ElectionSafety/committedMono/spinlock/logMatching |

---

## 三重 ground truth

| 来源 | 性质 | 用途 |
|---|---|---|
| **Jepsen 21 issue** | 真实 bug 报告（带因果真值）| canonical_QA 评估集 |
| **dsyme 716 定理**（2026-04，[`github.com/dsyme/raft-lean-squad`](https://github.com/dsyme/raft-lean-squad)）| 完整 Lean4 形式化 | formal_anchors 锚点 |
| **Ongaro TLA+ spec** | Raft 论文作者的形式规范 | ontology 权威定义 |

---

## adapter 五件套（DESIGN.md §一）

| 契约 | Raft 具体内容 | 状态 |
|---|---|---|
| `trace_source` | etcd/Raft log + Jepsen 失败注入 trace | ⏳ Phase 1 |
| `ontology` | TLA+ state machine：Leader/Follower/Candidate + term/vote/log | 🟢 |
| `world_corpus` | etcd git history 401 commit → 89 抽取（Raft 域）+ Raft paper + dsyme 注释 | 🟢 |
| `formal_anchors` | dsyme 716 定理 + Ongaro TLA+ + 本仓库 3 Lean4 证明 | 🟢 |
| `canonical_QA` | Jepsen 21 issue + 教科书 13 题 | ⏳ Phase 1 |

---

## Phase 1 集成 TODO

按 [`00-constitution/ROADMAP.md`](../../00-constitution/ROADMAP.md) Gate G1-G5：

1. **G1 adapter<20% 特化**：把 [`04-layers/l2-world-model/c1_pipeline/`](../../04-layers/l2-world-model/c1_pipeline/) 在 Raft 域的特化代码隔离成 `raft/trace_source.py` 等模块，证明 <20%
2. **G2 五原子零修改**：把 Raft ontology（Leader/Follower/...）映射到 Event/State/Causality/Invariant/DecisionPoint，证明五原子定义零修改
3. **G3 形式化非平凡**：当前 3 Raft 定理已 sorry=0，扩到 5-10 条覆盖 ElectionSafety + LogMatching + StateMachineSafety
4. **G4 蒸馏验证**：从 etcd commit 抽取的规则 ≥50% 在 dsyme 716 定理中有对应（验证 L2 蒸馏质量）
5. **G5 用户价值**：≥3 位 SRE 在 Jepsen 失败场景下用 Neo-OS 解释，准确率 vs 文档基线

---

## 引用

- 决策记录：[`01-decisions/FIRST_DOMAIN_DECISION.md`](../../01-decisions/FIRST_DOMAIN_DECISION.md)
- 形式化锚点：[`04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftRules.lean`](../../04-layers/l2_5-formal-rules/formal-seed/NeoOsFormalSeed/RaftRules.lean)
- 蒸馏语料：[`04-layers/l2-world-model/data/raft_extraction_report.md`](../../04-layers/l2-world-model/data/raft_extraction_report.md)
