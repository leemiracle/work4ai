# Neo-OS · 领域 adapter 层（05-adapters/）

> **薄 adapter 契约**——每个领域提供五件套（trace_source / ontology / world_corpus / formal_anchors / canonical_QA），**adapter 只翻译，不负责任何解释逻辑**。
>
> 权威 spec：[`00-constitution/DESIGN.md`](../00-constitution/DESIGN.md) §一"领域插拔 adapter"节

---

## 反 Hurd 纪律（CONSTITUTION.md）

> **"深度上专精，方法上通用。永远 N=2 提取，N=1 不泛化。"**

Phase 3 才扩展到第二域。当前 **`raft/` 是第一域，验证完才开第二域**（Gate G1-G5 在 [`00-constitution/ROADMAP.md`](../00-constitution/ROADMAP.md) Phase 3）。

---

## 第一域：Raft（已锁定）

详见 [`01-decisions/FIRST_DOMAIN_DECISION.md`](../01-decisions/FIRST_DOMAIN_DECISION.md) 九维度对比。

**为什么是 Raft**：
- 形式化锚点：TLA+（Ongaro 单一权威）+ dsyme 716 定理（已证 ground truth）
- 黄金语料：Jepsen 21 issue（带因果真值）
- 因果封闭性：高（状态机封闭，跨抽象层少）

详见 [`raft/`](./raft/)。

---

## adapter 五件套契约（DESIGN.md）

每个 adapter 必须提供：

| 契约 | 内容 | Raft 第一域状态 |
|---|---|---|
| `trace_source` | eBPF/OTel trace 来源 | ⏳ Phase 1 |
| `ontology` | 领域事件本体（映射到五原子）| 🟢 TLA+ state machine |
| `world_corpus` | commit/spec/docs 语料 | 🟢 etcd/Raft 89 commit 已蒸馏 |
| `formal_anchors` | TLA+/Lean4 形式锚点 | 🟢 dsyme 716 定理 + Ongaro TLA+ |
| `canonical_QA` | 标准问答对（评估用）| ⏳ Phase 1 |

**约束**：adapter 必须 <20% 工作量是"特化"，>80% 复用内核（Gate G1）。

---

## 候选第二/三域（锁抽屉，Phase 3 才评估）

按 [`01-decisions/FIRST_DOMAIN_DECISION.md`](../01-decisions/FIRST_DOMAIN_DECISION.md) Raft vs PostgreSQL 对比，PostgreSQL 列为第二域候选。

[`00-constitution/ROADMAP.md`](../00-constitution/ROADMAP.md) Phase 3 候选：
- PostgreSQL 查询规划器（关系代数锚点）
- LLVM 编译器（ORE remarks，[`LOCAL_ASSETS.md`](../02-research/LOCAL_ASSETS.md) 提到本地有 llvm/ 源码）
- 浏览器（Blink）
- GPU 驱动（Vulkan/Mesa）

**禁止**：在 Raft 完整 Phase 1 验证前讨论这些（反 Hurd）。
