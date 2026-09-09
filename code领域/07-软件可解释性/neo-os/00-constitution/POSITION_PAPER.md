# Position Paper · Formal Explainability for Arbitrary Complex Software

> **状态**：🟡 占位（v0.1，Phase 1 数据填充后投稿）
> **目标会议**：SOSP / OSDI（系统）/ NeSy / POPL（神经符号）/ ACL（蒸馏）
> **日期**：2026-08-05
> **作者**：Neo-OS

---

## 一、问题（The Gap）

所有重要软件（Linux/Blink/LLVM/PostgreSQL/K8s）都成长为巨型工程，造成**领域信息差**：只有少数内部人真懂，外部人被术语墙挡住。这是基础软件创新的结构性瓶颈。

现有方案各有死角：
- **AIOps（Datadog/Dynatrace）**：事后因果图，无形式化保证，plausible hallucination
- **observability（eBPF/DTrace）**：只采集 what，不解释 why
- **形式化（seL4）**：20 人年级成本，无法泛化到任意软件
- **LLM 解释**：会幻觉，无 ground truth 接地

**无人做过**：把任意复杂软件的行为，翻译成**可证明的英文解释**。

---

## 二、洞察（The Insight）

**软件栈的本质是人脑认知的 IR**。LLM + world model 让我们可以抛弃这些 IR，重新让事件直达人脑——60 年来第一次。

Neo-OS 的三重新颖性（不可替代三角）：
1. **commit-distilled 语义**：从软件历史蒸馏领域世界模型——无人做过
2. **形式化可证明**：Lean4 验证因果规则——唯一压过 Dynatrace 因果图
3. **trace-native 接地**：事件发生时解释（告警前）——唯一实时

---

## 三、方法（The Method）

### 四层架构
```
L3   English Interface  ← 三层讲解 × 17视角 × 费曼门（work4ai 方法论运行时化）
L2.5 Formal Rules      ← Lean4 因果规则（soundness 保证）
L2   World Model       ← commit 蒸馏的 7B 领域模型（本机常驻）
L1   Event Ontology    ← 一切皆 (event, cause) 对（eBPF + 硬件 trace）
```

### 五原子（领域无关解释原语）
Event / State / Causality / Invariant / DecisionPoint——定义里**无任何领域概念**。引擎只对五原子编程，每个领域提供薄 adapter（<20%）。

### 神经符号闭环（AlphaProof 范式在系统软件的落地）
```
commit 历史 → L2 蒸馏规则（神经，广覆盖，会幻觉）
          → L2.5 Lean4 验证（符号，绝不撒谎）
          → 通过则输出（★★★ 可证明），否则降级（★★ 软规则 / ★ LLM 直觉）
```

---

## 四、实证（The Evidence，v1.1 已验证）

| 假设 | 验证 | 数据 |
|------|------|------|
| commit 能蒸馏因果三元组 | ✅ Raft 域 N=89 | root_cause **97%**、fix 100%、完整三元组 39%（symptom 瓶颈）|
| kernel C commit 可蒸馏 | ✅ kernel N=3（cgit webfetch）| root_cause 100%、完整三元组 66.7%、置信度 0.97 |
| LLM 抽取 precision 可接受 | ✅ 基线 73-93% | 15 样本定性（待资深工程师确认）|
| 形式化能表达真实 OS 规则 | ✅ C2 spinlock×preempt | 5 定理 sorry=0（3 零公理），超过 omega |
| 形式化能表达分布式规则 | ✅ Phase 1 Raft committedMono | sorry=0，对齐 dsyme 716T |
| 属性级粒度可行（非 seL4 20 人年）| ✅ Cedar 范式 | 数周级，5+2 条规则 |

---

## 五、贡献（Contributions）

1. **第一个 commit-distilled 系统世界模型**：把软件 git 历史作为 (事件,因果) 语料
2. **神经符号 trace 解释架构**：Lean4 验证的因果规则 + 三级置信度
3. **CTC（Cognitive Token Cost）度量**：可证伪的可解释性量化
4. **五原子领域无关内核**：N=2（Raft + PostgreSQL）验证 adapter <20%

---

## 六、诚实边界（Honest Limits）

- **Ashby 必要变异度律**：解释器复杂度 ≥ 系统复杂度，Neo-OS 是**有损压缩器**非"打破一切信息差"
- **Kolmogorov 不可计算**：完美解释不可达，CTC 有理论下限 O(K(系统))
- **形式化只保证已写规则**：规则集完备性是 epistemic gap（对抗层 v0 实证：Inv 1/5 判别力）

---

## 七、论文点（Three Paper-Grade Points）

1. **Linux commit history as training corpus for system world models**（SOSP/OSDI/ACL）
   - C1 Raft 域 N=89 + kernel N=3 真实数据
2. **Neuro-symbolic trace explanation with formal soundness**（NeSy/POPL）
   - C2 spinlock×preempt + Phase 1 Raft + 对抗层（R5§6 命门实证）
3. **Cognitive Token Cost: democratizing complex software**（CHI/CSCW）
   - CTC 度量 + Bloom 2-sigma 对标

---

## 八、下一步（填数据 → 投稿）

- [ ] C1 扩到 N=1000（fetch_kernel_commits.py 批量 cgit）
- [ ] C1 precision 资深工程师标注（Raft 域 Jepsen+dsyme 双 ground truth）
- [ ] Phase 1 完整 prototype（Raft 域，复用 dsyme 716T）
- [ ] 用户研究（CTC 度量实证，≥3 工程师）
- [ ] 第二域 PostgreSQL（验证 adapter <20%）

---

*本 position paper 作为 Neo-OS 学术定位锚。Phase 1 数据就绪后扩写投稿。*
