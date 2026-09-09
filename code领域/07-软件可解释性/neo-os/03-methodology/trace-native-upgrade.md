# trace-native-upgrade.md · work4ai 方法论的 Neo-OS 升级

> **Neo-OS 唯一的方法论原创贡献**：
> 把 work4ai 的"代码实证层"升级为"**trace 实证层**"——让每条解释具备**可证伪性**，
> 区别于 LLM 的 plausible hallucination。

---

## 一、work4ai 原版：代码实证层（retrospective）

work4ai 三层讲解宪法（[`../work4ai/README.md`](../../work4ai/README.md) §六）：

```
直觉层（Intuition）  →  数学层（Math）  →  代码实证层（Code）
   1 句话比喻             关键公式 + 推导       可运行的最小 Python/PyTorch 示例
```

**代码实证层的特性**：
- ✅ 不凭记忆——每个结论用 bash 跑出来验证（loss/梯度/维度）
- ✅ 数字是真跑出来的，不是猜的
- ⚠️ **但是**：代码实证是 **retrospective**——事后构造示例验证结论
- ⚠️ 代码是"为了讲清楚而构造的玩具"，**不是真实运行流的快照**

这在 AI 知识库场景**足够**——讲透注意力机制，构造一个最小 attention 矩阵跑给你看就行。

---

## 二、Neo-OS 场景：为什么代码实证不够

Neo-OS 的目标是**解释真实软件的运行时行为**——不是讲清楚概念，是**回答"这台机器上为什么发生了这件事"**。

| 维度 | work4ai 代码实证 | Neo-OS trace 实证 |
|---|---|---|
| 数据来源 | 事后构造示例 | **eBPF/Intel PT 真实采集的运行时事件** |
| 时间锚 | 无（教学示例） | **纳秒级时间戳**（happens-before 严格偏序） |
| 可证伪 | 否（构造示例只能展示现象） | **是**（trace 是 ground truth，可与解释对照） |
| 噪声 | 无（理想化示例） | **大量**（生产 trace 含调度噪声/并发干扰）|
| 因果方向 | 教学概念→示例 | **真实事件→解释**（归纳而非演绎） |

**关键差异**：trace 是 **ground truth**。如果 L3 解释说"X 导致 Y"，但 trace 显示 X 在 Y 之后发生，**解释就破产**。这种**可证伪性**是 work4ai 代码实证层不具备的。

---

## 三、升级设计：trace 实证层（trace-native）

### 3.1 三层结构对照

```
work4ai 原版                          Neo-OS 升级版
─────────────                        ─────────────
直觉层（Intuition）                    直觉层（Intuition）           ← 不变
    1 句话比喻                            1 句话比喻

数学层（Math）                        形式化层（Formal）            ← 升级
    关键公式 + 推导                       Lean4 不变式 + 数学含义

代码实证层（Code）                    ★ Trace 实证层（Trace） ★    ← 核心升级
    可运行示例                            eBPF/PT 真实 trace 片段
                                         + 时间戳因果序
                                         + 状态快照
```

### 3.2 Trace 实证层的最小契约

每条 trace 证据必须包含：

```typescript
interface TraceEvidence {
  events:       TraceEvent[]    // 真实采集的事件序列（带 ts 纳秒戳）
  causalChain:  CausalEdge[]    // 因果边（每条边可回溯到 trace 段）
  stateSnapshot: StateSnap      // 关键状态快照
  violated:     boolean         // 是否违反规则（用于反例解释）
  provenance: {
    source:     "eBPF" | "Intel PT" | "Arm CoreSight"
    spanId:     string           // OTel span，跨层追溯
    rawTraceId: string           // 原始 trace 文件 ID（可调取完整上下文）
  }
}
```

### 3.3 可证伪性 = Neo-OS 的护城河

```
LLM 输出（candidate explanation）
       │
       ▼
   ┌──────────────────────┐
   │  L2.5 Lean4 形式化   │  ← 检查因果无环、不变式满足
   └──────────────────────┘
       │ filter
       ▼
   ┌──────────────────────┐
   │  L1 Trace 实证复核   │  ← ★ 把每条因果边对回真实 trace
   └──────────────────────┘
       │ verify
       ▼
   通过 → ★★★ 可证明解释
   失败 → 标"低置信度"，降级为软规则或丢弃
```

**核心承诺**：Neo-OS 输出的每条解释，**每句话都可点击展开 trace 段**——读者可独立验证。

这与 work4ai 的"代码可跑给你看"是同一种精神（不凭嘴说），但落地强度提升一个数量级：**从"事后构造的示例"到"真实运行流的快照"**。

---

## 四、继承的不变与变

| 维度 | 不变（继承 work4ai） | 变（Neo-OS 升级） |
|---|---|---|
| **认识论立场** | 不凭记忆，实证至上 | 不变 |
| **三层结构** | 直觉→数学→证据 | 直觉→形式化→trace（结构不变，第三层语义升级） |
| **费曼门** | F1 外行复述 / F2 卡壳自曝 / F3 术语黑名单 / F4 回炉 | 不变（L3 输出仍要过 F1-F4） |
| **17 视角护栏** | 第一性原理 / 布鲁姆 / 图尔敏 / 红队 / 系统论 / ... | 不变 |
| **证据性质** | 代码实证（retrospective） | **trace 实证（real-time ground truth）** |
| **可证伪性** | 弱（示例可重跑但不可证伪解释） | **强**（trace 可与解释对照，矛盾即破产） |
| **目标读者** | 学习者（理解概念） | 工程师（理解本机发生了什么） |

---

## 五、Phase 1 prototype 现状与差距

**已实现**（[`04-layers/l3-explain/`](../04-layers/l3-explain/)）：
- ✅ 三层结构输出（Intuition / Formal / Trace evidence）
- ✅ Formal 层接 L2.5 Lean4 规则
- ⚠️ Trace 层是 **GLM 构造的示例**，非真实 eBPF 采集（标记为局限）

**Phase 1 完整路线**：
1. 接 [`04-layers/l1-event-ontology/`](../04-layers/l1-event-ontology/) 的 eBPF trace → Trace evidence 用真实采集
2. 实现 trace 复核探针（lean_trace_check）：把 L3 输出的因果链对回 trace 段
3. 费曼门 F1-F4 + 17 视角护栏自动化
4. CTC 度量实证（对标 Bloom 2-sigma，≥3 工程师用户研究）

---

## 六、为什么这是 Neo-OS 的 paper-grade 贡献

这是三个研究点（[00-constitution/RESEARCH_QUESTIONS.md](../01-decisions/RESEARCH_QUESTIONS.md)）中**最具 Neo-OS 独特性的**：

> **Neuro-symbolic trace explanation with formal soundness**（NeurIPS/NeSy/POPL）
>
> 核心命题：把 work4ai 三层讲解方法论运行时化，用 trace 实证替换代码实证，
> 让 LLM 解释具备数学（Lean4）+ 经验（trace）双重可证伪性。

work4ai 给了方法论（三层 + 费曼 + 17 视角），Neo-OS 给了**运行时落地 + 可证伪升级**。
前者是知识库，后者是基础设施——**两者通过本目录建立引用契约**。

---

*本文件是 Neo-OS 对 work4ai 方法论的**唯一原创贡献声明**。
任何"Neo-OS 创新点"的声称，必须能回到本文件指出"哪些是继承、哪些是升级、哪些是新创"。*
