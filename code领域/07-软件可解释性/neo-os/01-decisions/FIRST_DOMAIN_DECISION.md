# Neo-OS · 第一域选型决策（FIRST_DOMAIN_DECISION）

> **决策**：✅ **第一域 = Raft 共识**（分布式系统）
> **第二域候选**：PostgreSQL 查询规划器（Phase 3 第二个，验证通用性）
> **日期**：2026-08-05
> **回应**：council C3（锁定单一域，推荐数据库/分布式而非 OS kernel）

---

## 一、决策摘要（一句话）

> **选 Raft，因为它有"三重 ground truth"——Ongaro TLA+ 锚点 + Jepsen 21 issue 因果真值语料 + dsyme/raft-lean-squad 716 定理已证形式化基座——这让 Neo-OS 的 commit 蒸馏 precision 验证（council C1）有了所有领域里最强的对齐目标。**

---

## 二、⚠️ 诚实修正：ROUND3 R3-3 的"Lean4 Raft 零空白"声称是错的

ROUND3 R3-3 曾声称"Lean4 Raft 形式化是公开空白（gh-grep 零命中）"。**经核实，此声称错误**。2026 年已有多个 Lean4 Raft 形式化项目：

| 项目 | 规模 | 状态 | 核实日期 |
|------|------|------|---------|
| **`dsyme/raft-lean-squad`** | 716-769 theorems / 79 Lean files / **0 sorry** | ✅ 端到端 `fullProtocolStep_safe`（EL7）已证，Lean 4.30-rc2 | 2026-04-28 |
| **`neutron-build/neutron`** | `Aeneas/Raft.lean` / 70 theorems / 0 sorry | ✅ log-matching + election-safety 风格性质 | 2026-02-25 |

**gh-grep 零命中的原因**：这些项目用 `RaftReachable` / `ClusterState` / `FVSquad.RaftElection` 等命名，而非 `inductive RaftState` / `namespace Raft`。命名差异导致 grep 漏报——这是项目宪法"声称-验证差距校正"的又一个实例。

**修正后的含义**：Raft 不是"形式化空白可补的学术机会"，而是**已有现成形式化基座可复用**。这反而让 Raft 更适合第一域（形式化风险最低）。

---

## 三、两候选九维度对比（核实后）

| 维度 | Raft 共识 | PostgreSQL 规划器 | 占优 |
|------|-----------|------------------|------|
| **1. 形式化锚点** | TLA+（Ongaro 单一权威 spec）+ **dsyme 716T 已证** | 关系代数（成熟，但 PG 特定逻辑需自建）| **Raft**（锚点 + 已证基座）|
| **2. Lean4 基座** | ✅ dsyme/raft-lean-squad 可直接复用 | ❌ 关系代数 Lean4 库少，需自建 | **Raft** |
| **3. 黄金语料** | Jepsen 21 issue（**带因果真值**）| pgsql-hackers 邮件列表（需挖因果）| **Raft**（因果密度高）|
| **4. 商业化/付费意愿** | SRE 团队（开源文化，付费弱）| DBA（预算明确，付费强）| **PostgreSQL** |
| **5. 因果封闭性** | 高（状态机封闭，消息驱动）| 中（跨优化器/执行器/存储多层）| **Raft** |
| **6. 五原子适配** | 极清晰（见 §四）| 需更多抽象（plan node/event 映射）| **Raft** |
| **7. scope 可控** | 小（Ongaro spec ~500 行 TLA+）| 大（src/backend/optimizer/ 数十万行）| **Raft** |
| **8. Neo-OS 增量价值** | 蒸馏规则对齐 dsyme 已证定理（神经符号闭环现成）| 需先建形式化基座才能对齐 | **Raft** |
| **9. 形式化风险** | 低（dsyme 铺路，复用 716T）| 中（关系代数 Lean4 自建）| **Raft** |

**结论**：Raft 在 9 维度中 **8 个占优**，PostgreSQL 仅在商业化（维度 4）更强。

---

## 四、Raft 五原子对应（领域插拔契约预演）

| 五原子 | Raft 对应 | Neo-OS 解释原语 |
|--------|----------|----------------|
| **Event** | RequestVote / AppendEntries / VoteResponse / ElectionTimeout | "发生了什么"（RPC + timeout）|
| **State** | currentTerm / votedFor / log[] / commitIndex / state | "此刻在哪"（节点状态机）|
| **Causality** | leader → follower AppendEntries；quorum ACK → commit | "为什么导致它"（消息因果）|
| **Invariant** | ElectionSafety / LeaderCompleteness / StateMachineSafety（dsyme RE5/RSS1 已证）| "本该/本不该怎样"（三大安全）|
| **DecisionPoint** | election timeout 触发选举 / log mismatch 拒绝 Append | "本可走另一条路"（分叉点）|

**判据满足**：五原子定义里**无任何 Raft 特定概念泄露**——Event/State/Causality/Invariant/DecisionPoint 是领域无关原语，Raft 只是填充。这正是 Neo-OS "领域无关内核 + 薄 adapter" 的验证点（council G1/G2）。

---

## 五、为什么 Raft 的"三重 ground truth"是 C1 的最强武器

council C1 要求 commit 蒸馏 precision ≥0.7，**需要 ground truth 标注**。Raft 提供所有领域里最强的三重 ground truth：

```
        Jepsen 21 issue                dsyme/raft-lean-squad 716T
        （运行时因果真值）              （形式化已证定理）
              │                              │
              │  Neo-OS L2 蒸馏              │  Neo-OS L2.5 对齐
              ▼                              ▼
        从 Raft commit 蒸馏 ────→ 因果规则 ────→ 对齐 dsyme 已证不变式
        (symptom, root_cause, fix)            (ElectionSafety 等)
              │                              │
              └──────── precision 验证 ───────┘
                    （双重 ground truth 交叉验证）
```

- **Jepsen 21 issue**：每个 issue 有 Jepsen 团队的根因分析（运行时因果真值），是蒸馏 symptom/root_cause 的 gold label
- **dsyme 716T**：已证定理（ElectionSafety RE5 / raftReachable_safe RT2 等）是蒸馏 Invariant 规则的形式化 ground truth
- **Ongaro TLA+**：spec 是 Causality/DecisionPoint 的权威定义

PostgreSQL 只能靠**人工标注**（DBA 专家），因果密度低、成本高、subjective。**Raft 的 precision 验证成本最低、可信度最高。**

---

## 六、推荐与理由（最终判词）

**第一域 = Raft 共识。** 理由排序：

1. **三重 ground truth**（最强理由）：Jepsen + dsyme + Ongaro 让 C1 precision 验证有所有领域最强的对齐目标，**大幅降低 council C1 的执行成本与可信度**。
2. **形式化风险最低**：dsyme 716T 是现成基座，Neo-OS L2.5 复用而非从零建。Neo-OS 增量 = 神经符号蒸馏对齐已证定理（AlphaProof 范式在分布式领域的落地）。
3. **因果封闭 + scope 小**：Raft 状态机封闭，Ongaro spec ~500 行，**最快验证 Neo-OS pipeline 端到端**（反 Hurd：第一域要快验证）。
4. **五原子对应极清晰**：直接满足 council G1/G2（adapter 薄 + 五原子零修改）。
5. **学术 paper-grade**：神经符号蒸馏 × 形式化对齐 = NeurIPS/NeSy/POPL 论文点。

**第二域 = PostgreSQL 规划器**（Phase 3 第二个）：
- 验证通用性（关系代数 vs TLA+ 的形式化基座差异正好检验"adapter <20%"）
- 接商业化（DBA 付费意愿强，Phase 4 后商业落地）

---

## 七、风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| Raft 商业化较远（SRE 开源文化）| 中 | Phase 1-3 学术 + 开源双轨；Phase 4 后 PostgreSQL 接商业 |
| dsyme 716T 是 Rust 实现验证，非 spec 验证 | 低 | Neo-OS 对齐 Ongaro TLA+ spec（更抽象），dsyme 作 Rust 落地的 correspondence 证据 |
| Jepsen 21 issue 样本量小（precision 统计置信度）| 中 | 扩到 etcd/raft-rs/TiKV commit（Raft 实现族），样本扩到 1000+ |
| 第一域选分布式而非 OS kernel，"OS 解释器"初心偏移 | 低 | CONSTITUTION 第一条不变：kernel C commit 仍是长期核心靶子；Raft 是"先验证 pipeline 再攻 kernel"的 council 策略，非放弃 OS |

---

## 八、与 ROADMAP / C2 / C1 的联动

- **ROADMAP Phase 1**（OS prototype）→ **修订**：第一域 prototype 改为 Raft（而非 Linux+eBPF）。Linux+eBPF 移到 Phase 2+ 作为"情怀域"。
- **C2（已通过）**：spinlock+preempt 非平凡规则已证（C2 范式）。Raft 域的形式化复用 dsyme 716T，Neo-OS 增量是蒸馏对齐。
- **C1（进行中）**：kernel clone 进行中，但 **Raft 域的 C1 precision 验证更强**（Jepsen+dsyme 双 ground truth）。kernel commit 蒸馏仍做（CONSTITUTION 第一条），但 Raft commit（etcd/raft-rs）作为 C1 的**补充验证域**，precision 可双重交叉验证。

---

## 九、决策签署

| 项 | 值 |
|----|-----|
| 第一域 | **Raft 共识**（etcd-raft / raft-rs / TiKV Raft 实现族）|
| 形式化基座 | dsyme/raft-lean-squad（复用 716T）|
| 因果语料 | Jepsen 21 issue + Raft 实现 commit |
| 形式化锚点 | Ongaro TLA+ spec |
| 第二域候选 | PostgreSQL 规划器（Phase 3）|
| 决策日期 | 2026-08-05 |
| 决策依据 | council C3 + 九维度对比 + 三重 ground truth + 反 Hurd（快验证）|

---

*本决策锁定 Neo-OS 第一域。Phase 1 prototype 改为 Raft 域。回 CONSTITUTION.md 三条初心做最终检验：第一域选 Raft 不违反任何一条初心（kernel 仍是长期靶子，Raft 是验证 pipeline 的策略选择）。*
