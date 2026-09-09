# Neo-OS · L1 Event Ontology Layer

> **OS 的根**——一切都是 `(event, cause)` 对。eBPF 常态采集 + 硬件 PT/ETM 异常放大，输出 LLM-friendly JSONL。
>
> 权威 spec：[`00-constitution/DESIGN.md`](../../00-constitution/DESIGN.md) §一 L1 节

---

## 状态：⚠️ Phase 1 待实现

当前是设计占位目录（无代码）。Phase 1 第一项工作就是接入 eBPF/Intel PT。

**为什么现在没代码**：Phase 0 聚焦"上游命门"（C1 commit 蒸馏 + C2 形式化粒度），这两个不依赖 L1 真实 trace。Phase 1 接 L1 真实采集后才能完成 trace-native 升级（见 [`03-methodology/trace-native-upgrade.md`](../../03-methodology/trace-native-upgrade.md)）。

---

## 设计契约（DESIGN.md L1 节摘要）

### 常态采集
- **工具**：eBPF（CO-RE + libbpf）
- **覆盖**：syscall / tracepoint / kprobe
- **开销目标**：1-3%

### 异常放大
- eBPF 检测异常 → 触发硬件 PT/ETM snapshot
- 窗口：100-500ms

### 因果骨架
- OTel Span Context（trace_id 跨层传播）
- 单机 vector clock

### 事件格式（LLM-friendly JSONL）

```json
{
  "ts": 1234567890.123,
  "tid": 42, "cpu": 3,
  "trace_id": "...", "span_id": "...", "parent_span_id": "...",
  "type": "syscall|sched|fs|net|hw|...",
  "event": "page_fault_major",
  "cause": "demand_paging",
  "payload": {...},
  "ctx_snapshot": {...}
}
```

---

## 与上下游的契约

| 方向 | 契约 |
|---|---|
| **上游输入** | L0 硬件 trace（Intel PT/Arm CoreSight）→ L1 IR 规则引擎语义化 |
| **下游输出** | JSONL 事件流 → L2 world model 用于预测/解释，L3 用于 trace 实证 |

---

## Phase 1 第一批 TODO（按 ROADMAP Gate G1-G5）

1. 选 eBPF 框架（候选：libbpf-rs / aya / cilium ebpf Go）
2. 实现 5 原子 → eBPF event 适配器（验证"领域无关"承诺）
3. 实现 trace_id 跨 syscall/sched/fs 传播（OTel Span Context）
4. 接 L3 `l3_explain.py` Trace evidence 层（替换 GLM 构造示例）
5. 测开销（<15% 是 council C4 指标）

**反 Hurd 纪律**：adapter 只读现有 eBPF 工具，不自造 tracer（[CONSTITUTION.md](../../00-constitution/CONSTITUTION.md) 附录 RL 铁律 3）。

---

## 参考

- eBPF 文档：本机 `/mnt/c/workspace/linux/Documentation/bpf/`（kernel 源码内）
- trace-native 升级设计：[`03-methodology/trace-native-upgrade.md`](../../03-methodology/trace-native-upgrade.md)
- 五原子 spec：[`00-constitution/DESIGN.md`](../../00-constitution/DESIGN.md) §二
