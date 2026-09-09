# Neo-OS · 架构设计（DESIGN）

> 版本 v2.0。本文档定义 Neo-OS 的技术架构：四层技术栈、五原子内核、薄 adapter 契约、跨域原语。

---

## 一、四层技术栈

### L0 · Hardware Layer
- **x86**：Intel PT（perf AUX，snapshot 模式）
- **ARM64**：CoreSight TRBE + ETE
- **RISC-V**：N-Trace（自定义 pipeline）
- **NPU/GPU**：PMU 计数器 + 厂商 trace（多数闭源，需补偿）
- 设计原则：**硬件作为加速器，纯软件（eBPF）优先保证可移植**

### L1 · Event Ontology Layer（事件本体，OS 的根）
- **常态采集**：eBPF（CO-RE + libbpf），覆盖 syscall/tracepoint/kprobe，开销 1-3%
- **异常放大**：硬件 PT/ETM snapshot，eBPF 检测异常时触发 100-500ms 窗口
- **因果骨架**：OTel Span Context（trace_id 跨层传播）+ 单机 vector clock
- **语义化**：IR 规则引擎（binary → semantic event），输出 JSONL
- **事件格式**（LLM-friendly）：
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

### L2 · System World Model Layer（核心创新）
- **基座**：Qwen2.5-Coder-7B（代码理解强 + 中文友好 + 开源）
- **训练目标**（三层）：
  - 主：**因果/干预式**（do-calculus，利用系统世界可干预独特红利）
  - 辅：预测式 next-event（JEPA 风 latent 预测，VICReg 防 collapse）
  - 界面：生成式解释（DreamerV3 风想象 rollout → 英文）
- **训练语料构成**：
  - Linux commits 60%（Tier 1/2/3 分层，见 E05）
  - Crash reports 20%（kernel oops, syzkaller）
  - 合成数据 15%（注入 bug → trace → 已知原因）
  - 教科书 5%（OSTEP, Red Book）
- **蒸馏方法**：QLoRA（NF4 4bit 基座）+ 每域 LoRA adapter + LIMA 式 1000 条精挑 + DPO 对齐
- **部署**：本机 GPU 7B（vLLM/SGLang）+ INT4 量化 + 云端 fallback（low-confidence 时）

### L2.5 · Formal Rule Layer（soundness 保证）
- **形式化语言**：Lean4（可执行规范 + NeSy 工具链全在此）
- **粒度**：属性/不变式级（Cedar 范式），不做全代码验证
- **规则来源**：LLM 归纳 + Lean4 验证（通过则保留，否则丢弃）
- **不完备性兜底**：三级置信度
  - ★★★ 可证明（Lean4 verified）
  - ★★ 软规则（高置信但不形式化）
  - ★ LLM 直觉（标注低置信）
- **耦合架构**：双向——LLM 给候选因果链，规则约束每步，输出经验证版本

### L3 · English Interface Layer
- **方法论内核**：三层讲解 × 17 视角护栏 × 费曼质量门（继承 work4ai）
  - 三层：直觉（比喻）→ 数学（规则）→ trace 证据
  - 17 视角：自动启发式扫描（第一性原理/布鲁姆/图尔敏/红队/系统论/...）
  - 费曼门：F1 外行复述 / F2 卡壳自曝 / F3 术语黑名单 / F4 回炉记录
- **交互模式**：异常被动推送 + 按需主动问答
- **可信度呈现**：文本 + citation（每句可溯源到 trace 段）+ confidence
- **语言**：英文 v1，中文 v2

---

## 二、五原子内核（领域无关）

引擎只针对五原子编程，**严禁泄露领域假设**：

```
Event {
  t: Timestamp
  location: DomainLocation   // 领域插件定义"location"指什么
  cause: CausalityEdge?
  payload: Payload
}

State {
  t: Timestamp
  snapshot: DomainState
  location: DomainLocation
}

Causality {
  cause: EventId | StateId
  effect: EventId | StateId
  mechanism: String          // 因果机制描述
  confidence: ★★★|★★|★
}

Invariant {
  assertion: FormalAssertion // Lean4 表达式
  anchor: FormalAnchor       // spec/rfc/tla+/类型规则
  status: Verified|Violated|Unknown
}

DecisionPoint {
  branch_taken: BranchId
  alternatives: [Branch]
  rationale: String
}
```

**反 Hurd 铁律**：在第二个领域跑通前，不把"内核"当既成事实。永远从 N=2 提取，不从 N=1 泛化。

---

## 三、薄 Adapter 契约

```typescript
interface DomainAdapter {
  // 1. 事件接入器：读现有 trace 工具输出，绝不自造 tracer
  trace_source: {
    ingest(): AsyncIterable<Event>
    // strace/eBPF | CDP | opt remarks | EXPLAIN | OTel | tcpdump
  }

  // 2. 命名本体：领域词汇表
  ontology: {
    location_meaning: "fd" | "DOM node" | "SSA value" | "table" | "span" | ...
    event_types: Enum
    state_schema: Schema
  }

  // 3. 世界语料：权威历史文本
  world_corpus: {
    commits: Commit[]
    specs: Spec[]           // POSIX | HTML/CSS/WGSL | RFC | SQL std | TLA+
    docs: Doc[]
  }

  // 4. 形式锚点：可机检参照
  formal_anchors: {
    invariants: Lean4Theorem[]
    postconditions: Contract[]
    rfc_must: RFCSection[]
  }

  // 5. 典型问题集：该域 top-K 追问
  canonical_QA: {
    questions: QA[]
    benchmarks: Benchmark[]
  }
}
```

**核心约束**：adapter 必须薄（<20% 代码）。若 >60%，说明抽象泄漏，回内核修正。

### Cookbook：要解释一个新领域（如 Django），需要什么

| 步骤 | 内容 |
|------|------|
| trace_source | OTel + ORM log + 模板渲染日志 → 统一 Event 流 |
| ontology | URL→view→serializer→ORM→SQL 生命周期；middleware 顺序 |
| world_corpus | Django 官方文档 + 源码 + WSGI/ASGI 规范 |
| formal_anchors | HTTP 状态码语义；queryset 惰性求值契约 |
| canonical_QA | "为何 N+1 query""为何 middleware 顺序错""为何没用索引" |

产物全是"喂料"，不含一行解释逻辑。

---

## 四、跨域原语：转换流水线视角

**最值钱的迁移**：每个复杂系统都有内部表示在反复变换；**可解释性 = 让每一次变换都可读**。

| 领域 | 转换流水线 |
|------|-----------|
| 编译器 | source → AST → IR → (N pass) → 机器码 |
| 浏览器 | HTML → DOM → layout tree → paint tree → GPU 命令 |
| GPU | shader 源 → SPIR-V → ISA；render graph → draw calls |
| 分布式 | request → spans → 因果图 |
| 数据库 | SQL → 解析树 → 逻辑计划 → 物理计划 → 执行 |

引擎内置「变换链」原子：任何 trace 可解读为"表示 R 在 t 经变换 T 变成 R'"。

---

## 五、性能预算（<3%）

| 组件 | 开销 | 策略 |
|------|------|------|
| eBPF 常态采集 | 1-3% | syscall + tracepoint + 应用 span |
| OTel 采样 | <1% | 1% 采样率 |
| 硬件 PT snapshot | 0%（非常态）| 异常触发 100-500ms |
| 因果 token 传播 | <0.1% | trace_id 注入 |
| Vector clock | <0.5% | per-CPU |
| **总计** | **<3%** | 生产可常开 |

六条设计原则（来自 work4ai GPU 系列）：绝不物化全量 / 分页消除碎片 / 增量不回扫 / 识别 memory-bound / 通信-计算重叠 / 多后端自适应。

---

## 六、安全与隐私

- **trace 含 PII/密钥**：差分隐私 + 污点分析 + 本地推理（零数据出境）
- **LLM 幻觉防线**：神经符号分层 + 强制 citation + 形式化过滤
- **TCB 边界**：明确形式化保证止于何处（硬件层 TLB/缓存/DMA 仍 TCB）

---

*架构版本 v2.0。详见 [EXPANDED_KNOWLEDGE.md](../02-research/EXPANDED_KNOWLEDGE.md) 第二编技术地基。*
