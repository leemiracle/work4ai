# Neo-OS · 四层架构实现（04-layers/）

> **本目录是 Neo-OS 的工程实现核心**——把 [`00-constitution/DESIGN.md`](../00-constitution/DESIGN.md) 的四层架构物化为可运行原型。
>
> 严格按架构语义组织：每个子目录对应一层，**目录名就是架构名**。

---

## 四层映射

| 目录 | 层 | 状态 | Phase |
|---|---|---|---|
| [`l1-event-ontology/`](./l1-event-ontology/) | **L1 Event Ontology** | ⚠️ 设计占位（无代码）| Phase 1 |
| [`l2-world-model/`](./l2-world-model/) | **L2 System World Model** | 🟢 C1 命门已达标（sglang+Raft+kernel 三域）| Phase 0/1 |
| [`l2_5-formal-rules/`](./l2_5-formal-rules/) | **L2.5 Formal Rules** | 🟢 C2 命门已达标（spinlock+Raft 3 定理 sorry=0）| Phase 0/1 |
| [`l3-explain/`](./l3-explain/) | **L3 English Interface** | 🟢 prototype 跑通（4 规则三层讲解）| Phase 0/1 |

L0（Hardware）暂无代码，由 L1 的 eBPF + 硬件 PT adapter 覆盖（Phase 1 才接入）。

---

## 与架构 spec 的对应

权威 spec：[`00-constitution/DESIGN.md`](../00-constitution/DESIGN.md) §一（四层技术栈）+ §二（五原子内核）。

每层 README 自描述该层的：
- 职责（一句话）
- 当前实现（具体文件 + 验证状态）
- 接上下游的契约（输入/输出）
- 引用 DESIGN.md 的对应章节
- 下一步（具体 TODO）

---

## 五原子（领域无关，跨四层）

引擎只针对五原子编程——**严禁泄露 OS/领域假设**。详见 DESIGN.md §二。

| 原子 | 回答 |
|---|---|
| Event | 发生了什么？ |
| State | 此刻在哪？ |
| Causality | 为什么导致它？ |
| Invariant | 本该/本不该怎样？ |
| Decision Point | 本可走另一条路？ |

---

## 当前命门状态（2026-08-05）

- ✅ **C1**（commit 蒸馏，→ L2）：sglang N=100(62%) + etcd/Raft N=89(97%) + kernel N=145(100%)
- ✅ **C2**（非平凡 Lean4 规则，→ L2.5）：spinlock×preempt v2 + Raft ElectionSafety/committedMono/LogMatching
- 🟢 **L3 prototype**：4 规则三层讲解输出（GLM-4-plus 生成）
- ⏳ **L1**：Phase 1 待实现（eBPF + Intel PT）
- ⏳ **trace-native 升级**：L3 当前用构造示例，Phase 1 接 eBPF 真实 trace

详见 [`00-constitution/COUNCIL_FINAL_REVIEW.md`](../00-constitution/COUNCIL_FINAL_REVIEW.md) C1-C4 + [`03-methodology/trace-native-upgrade.md`](../03-methodology/trace-native-upgrade.md)。
