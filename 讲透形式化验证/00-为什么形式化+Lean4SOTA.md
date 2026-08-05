# 00 · 为什么形式化 + Lean4 SOTA（2024-2026）

> 本章建立全系列地基。三件事：① 形式化验证**到底验证什么**（不是"测一遍"而是"数学证明"）；② 为什么 **Lean4** 在 2024-2026 成了定理证明器的新宠；③ 从 seL4（11 人年）到 Atmosphere（20 秒）的演化，以及你必须警惕的"**验证剧场**"陷阱。
>
> 配套：[`讲透神经符号/00`](../讲透神经符号/00-神经符号循环为什么是新范式.md)（AlphaProof 式闭环）+ [`讲透RL/04`](../讲透RL/04-RL与形式证明.md)（RL 证定理）

---

## 一、形式化验证到底验证什么

### 1.1 测试 vs 形式化

| 方法 | 给你的保证 | 成本 |
|------|-----------|------|
| 单元测试 | "我测过的 case 都过了" | 低 |
| 模糊测试（fuzzing）| "我随机试了 1 亿次没崩" | 中 |
| **形式化验证** | "**对所有可能输入，性质 P 永远成立**"（数学证明）| **极高** |

> 🎯 **一句话**：测试只能"证明 bug 存在"（找到的），永远不能"证明 bug 不存在"。**形式化验证是唯一能证明"某类 bug 不可能发生"的方法**——因为它穷尽所有情况做了数学证明。

### 1.2 形式化验证的产物：定理

形式化验证的产出不是测试报告，而是**定理**（theorem）。例如：

```lean
-- seL4 风格：调度保持内核不变式
theorem schedule_preserves_kernelInvariant
    (s s' : SystemState)
    (hInv : kernelInvariant s)
    (hStep : schedule s = .ok s') :
    kernelInvariant s' := by
  ...
```

这个定理说：**对任意状态 s，只要 s 满足内核不变式，调用 schedule 后的新状态 s' 也满足**。这是对所有可能的 s 的数学断言，不是测试。

### 1.3 为什么这么贵：proof-to-code 比

形式化验证的核心成本指标是 **proof-to-code ratio**——证明代码 / 被验证代码的比例：

| 项目 | proof-to-code | 含义 |
|------|--------------|------|
| seL4（2009）| **20:1** | 1 行 C 代码要 20 行证明 |
| CertiKOS | 14.9:1 | 1 行要 15 行 |
| **Atmosphere（2025）** | **3.32:1** | 1 行只要 3.3 行 ⭐ |

> 📌 **演化趋势**：从 20:1 到 3.32:1 是 6 倍效率提升。形式化验证正从"11 人年证明 8.7K 行"进入"工程实用"阶段——这是 2024-2026 最重要的变化。

---

## 二、seL4：黄金标准与它的代价

### 2.1 seL4 是什么

seL4（SOSP 2009，Klein et al.）是**人类第一个完整形式化验证的 OS 微内核**：

| 维度 | 数字 |
|------|------|
| 验证范围 | 功能正确性（refinement）+ 完整性 + 机密性 + 二进制正确性 |
| C 代码 | 8.7K LoC |
| 证明代码 | 200K+ LoC Isabelle/HOL |
| 人年 | ~20（含安全证明）|
| proof-to-code | 20:1 |
| 验证器 | Isabelle/HOL（不是 Lean4）|

### 2.2 seL4 验证的是什么

seL4 的核心是 **refinement proof**——三层抽象逐层精化：

```
抽象规范（abstract spec，数学描述内核应做什么）
    ↓ 证明 refinement
设计规范（design spec，更细的算法描述）
    ↓ 证明 refinement
C 代码实现（实际编译执行的代码）
    ↓ 证明 C→二进制正确性
二进制（实际跑的机器码）
```

每一层都证明"下层忠实实现了上层"。最终结论：**二进制忠实执行了抽象规范**。

### 2.3 seL4 的边界（必须诚实声明）

seL4 **没有验证**的部分：
- ❌ 时序侧信道（timing side channel）
- ❌ DMA 假设（假设 DMA 配置正确）
- ❌ ~600 行汇编（启动代码）未验证
- ❌ 多核并发证明**仍在进行**（2026 仍未完成）

> 🟥 **铁律**：形式化验证的失败模式不是"证不出来"，而是"**验证边界之外的部分静默失败**"。seL4 诚实声明了边界，但很多项目不声明——见 [§六 验证剧场](#六验证剧场形式化最阴险的陷阱)。

---

## 三、Lean4：为什么成了新宠

### 3.1 定理证明器的世代

| 世代 | 代表 | 特点 |
|------|------|------|
| LCF 族 | Isabelle/HOL, Coq | 老牌，seL4 / CompCert 用 |
| **Lean4**（2013-）| Lean | **数学家友好 + 编程语言感 + mathlib 百万定理** |

### 3.2 Lean4 的三个杀手锏

**① mathlib**：开源数学库，~150 万行，覆盖从微积分到代数几何的现代数学。任何数学概念几乎都能 `import Mathlib.XXX` 直接用。

**② 类型论（Dependent Type Theory）**：Lean4 用构造演算（Calculus of Constructions）变种，**程序 = 证明，类型 = 命题**（Curry-Howard 同构）。写证明像写函数。

**③ 数学家的写作体验**：Lean4 的语法（特别是 tactic 模式）被设计成"数学家写证明草稿"的感觉，比 Coq 的 `intros; induction; simpl.` 更接近纸笔数学。这是为什么 2020 后大量数学家（包括 Fields 奖得主）涌入 Lean4——**Liquid Tensor Experiment**（Scholze 用 Lean4 验证他的凝态数学定理）是标志事件。

### 3.3 Lean4 在 OS 验证的现状（2026）

| 项目 | 验证范围 | 规模 | 状态 |
|------|---------|------|------|
| **seLe4n**（hatter6822）| 调度器/能力/IPC/VSpace/TLB/信息流不变式 | **6672 定理，0 sorry，209K LoC** | ⚡ 单作者，目标 Raspberry Pi 5，3 stars（极低曝光）|
| **lean4lean**（digama0）| Lean4 内核自身的元理论一致性 | ~155 定理 / 20 子系统 | 进行中 |
| **KLean**（PLOS 2025）| 内核扩展（BPF 替代）验证 | — | 学术 |
| **Veil**（CAV 2025）| 分布式协议转换系统 | 1704 LoC / 85 actions / 185 invariants | ✅ 可用 |

> 📌 **现状**：Lean4 端到端 OS 验证**只有一个项目（seLe4n），且极低曝光**。seL4 仍是黄金标准但用 Isabelle/HOL。**Lean4 OS 验证是真实存在但高度前沿的赛道，竞品极少**——这是蓝海，也是孤独。

---

## 四、2024-2026 的关键突破：Verus + Atmosphere

### 4.1 Verus（SOSP 2024）：用 Rust + SMT 验证系统

Verus（DOI:10.1145/3694715.3695952 ✅）的创新：用 **Rust 子集 + Z3 SMT solver**，让"写验证代码"变成"写带规格的 Rust"。

| 维度 | Verus |
|------|-------|
| 验证范围 | 分布式系统、OS 页表、NUMA 并发、crash-safe 存储、并发内存分配器 |
| 自动化 | 高（EPR 片段全自动；线性类型推理别名）|
| 局限 | Rust 子集；TCB 含 Z3；非线性算术需手工 |

### 4.2 Atmosphere（SOSP 2025）：20 秒验证全微内核

Atmosphere（DOI:10.1145/3731569.3764821 ✅）是 2025 最重要的系统验证进展：

| 维度 | Atmosphere |
|------|-----------|
| 验证范围 | 全功能微内核：进程/线程/动态内存/IPC/虚拟地址空间/IOMMU/容器隔离 |
| proof-to-code | **3.32:1**（seL4 是 20:1，6 倍提升）⭐ |
| 验证时间 | **<20 秒全量验证** |
| 人年 | **<2.5**（seL4 是 20，8 倍提升）|
| 局限 | big-lock 同步（非真正并发）；6K LoC 可执行码 |

> 🎯 **里程碑意义**：Atmosphere 把"形式化验证一个全功能微内核"从"20 人年"压到"<2.5 人年 + 20 秒验证"。这跨越了"可行性证明"到"工程实用"的门槛。**意味着"1-2 人周产非平凡规则"的预算在 SOTA 范围内是合理的**——前提是选对工具链。

---

## 五、`omega` 解不掉的边界（"非平凡"的精确定义）

在 Lean4 社区，"非平凡证明"有个精确判据：**`omega` 解不掉的就是非平凡**。理解这个判据是看懂 [讲透RL/04](../讲透RL/04-RL与形式证明.md) "C2 命门"的基础。

### 5.1 omega 是什么

`omega`（原名 `linarith`）是 Lean4 的**线性算术决策过程**（Presburger 算术）。它对 `Nat`/`Int` 上的 $<, \le, =, +, -, \text{常数} \times$ 完备：

```lean
-- omega 能解：纯线性算术
example (a b c : Int) (h1 : a < b) (h2 : b < c) : a < c := by omega  ✅
```

### 5.2 omega 解不掉的三类问题

| 类型 | 例子 | 为什么 |
|------|------|--------|
| **① 归纳结构** | trace/list 的递归 | omega 不是归纳证明器 |
| **② 非线性乘法** | 变量 × 变量 | Presburger 不含 |
| **③ 任意长度序列推理** | "对所有长度的 trace" | 需要对长度归纳 |

### 5.3 "trace 不变式 + induction on trace" 模式

这是系统验证最常见、omega 必败的模式。典型结构：

```lean
-- 1. 定义事件流为归纳类型
inductive EventTrace : SystemState → SystemState → Prop where
  | nil (s : SystemState) : EventTrace s s
  | cons (s₁ s₂ s₃ : SystemState)
      (hStep : step s₁ = .ok s₂)
      (hTail : EventTrace s₂ s₃) : EventTrace s₁ s₃

-- 2. 主定理：trace 保持不变式（必须 induction on trace）
theorem Inv_preserved_over_trace
    (s s' : SystemState)
    (hInit : inv s)
    (hTrace : EventTrace s s') :
    inv s' := by
  induction hTrace with
  | nil _ => exact hInit
  | cons _ s₂ _ hStep _ ih =>
    -- 此处 omega 无效：需调用单步引理
    exact ih (step_preserves_inv _ _ hStep)
```

> 🎯 **为什么 omega 解不掉**：`induction hTrace` 产生的归纳结构是高阶的（trace 是归纳类型，`cons` 引入递归假设 `ih`）。这是"语义验证非语法验证"的正解。

**开源范本**：seLe4n 的 `composedNonInterference_trace` 和 `dvr_trace_preserves_invariant` 都用这个 `induction hTrace with | nil => ... | cons ... ih => ...` 结构。

---

## 六、验证剧场：形式化最阴险的陷阱

形式化验证最危险的不是"证不出来"，而是"**验证边界之外的部分静默失败**"。两个 2026 的反面案例：

### 6.1 Lean4 内核漏洞 #14576（2026-07）

arXiv 一手核实 ✅：Lean4 内核的**嵌套归纳投影未检查结构名**，可构造 `0=1` 的**无公理伪证**（不用 sorry，不用任何 axiom）。

- **后果**：在 #14576 修复前，任何 Lean4 证明都可能是不健全的
- **教训**：**Lean4 内核本身也是软件，也可能有 bug**。光"Lean4 接受了证明"不足以保证健全性

### 6.2 Verification Theatre（IACR eprint 2026/192）

Kobeissi 审计 **libcrux**（Signal 用的 Rust 加密库）：13 个漏洞**逃出**了形式化验证——因为代码里用了 `lax` 属性，**静默接受所有证明**。

> 🟥 **铁律**：不要相信"已形式化验证"的声明，要问：
> - 验证了**什么性质**？（refinement？不变式？类型安全？）
> - 验证边界**之外**假设了什么？（DMA？时序？汇编？）
> - 用的什么验证器？版本？是否启用 `--trust=0`？
> - 是否有 `sorry` / axiom / `lax` 类逃生口？

### 6.3 CI 加固 checklist

防范上述陷阱的最小 checklist：
- [ ] `--trust=0`（禁用所有信任假设）
- [ ] `sorry` 扫描 gate（CI 里 grep `sorry`，有就 fail）
- [ ] 独立 checker 交叉核验（nanoda 或 lean4lean）
- [ ] 锁定 Lean4 版本 + mathlib 版本
- [ ] 显式声明验证边界（哪些验证了，哪些假设了）

---

## 七、形式化因果规则：未被占据的 niche

### 7.1 形式化的两层

| 层次 | 验证对象 | 代表 |
|------|---------|------|
| **形式化代码** | 代码忠实实现规范（refinement）| seL4, Atmosphere, CertiKOS |
| **形式化协议** | 协议转换系统的不变式 | Veil, IronFleet, Leslie |
| **形式化内核操作** | 单个内核操作保持不变式 | seLe4n |
| **形式化因果规则** ⚡ | 从事件流蒸馏的因果规则在 trace 上的保持性 | **无成熟竞品**（2026 蓝海）|

### 7.2 为什么"形式化因果规则"是新 niche

- 形式化 OS 社区（seL4/Verus/seLe4n）聚焦**代码层**，不涉及"从 world model 蒸馏规则"
- 神经符号社区（[讲透神经符号](../讲透神经符号/)）聚焦规则合成与约束，但不用 Lean4 做机器检查
- 因果推断社区不用定理证明器

> 📌 **蓝海**：**Lean4 形式化因果规则在事件 trace 上的保持性**——这个精确组合在公开文献中未见先例（⚡推断，基于公开文献穷举）。是研究前沿而非工程套用。

---

## 八、一句话总结

> 🎯 **三句话**：
> 1. **形式化验证是唯一能"证明某类 bug 不可能发生"的方法**——产出是定理不是测试报告；演化趋势是 proof-to-code 从 seL4 的 20:1 降到 Atmosphere 的 3.32:1，跨越"工程实用"门槛。
> 2. **Lean4 是新宠**（mathlib 百万定理 + 数学家友好 + Curry-Howard）；但 Lean4 端到端 OS 验证全球只有 seLe4n 一个项目（低曝光）——蓝海也孤独。
> 3. **验证剧场是头号陷阱**：Lean4 内核漏洞 #14576（无公理伪证）+ libcrux `lax` 静默接受 = "Lean 接受了证明"不足以保证健全性。必须 CI 加固（`--trust=0` + sorry gate + 独立 checker）。

📌 **下一步**：进入 [`讲透神经符号`](../讲透神经符号/) 看 AlphaProof 式"LLM 生成 + Lean4 验证"的闭环怎么把形式化验证和深度学习连起来，或 [`讲透RL/04`](../讲透RL/04-RL与形式证明.md) 看 RL 怎么（以及为什么不能）学形式化规则。

---

## 附：关键引用（arXiv/DOI 一手核实）

| 工作 | ID | 角色 |
|------|----|------|
| seL4 | SOSP 2009, Klein et al. | 黄金标准，20 人年 |
| Verus | DOI:10.1145/3694715.3695952 ✅ | SOSP 2024，Rust+SMT |
| **Atmosphere** | DOI:10.1145/3731569.3764821 ✅ | **SOSP 2025，3.32:1 + 20s** |
| CertiKOS | Ronghui Gu, Columbia | Coq 多处理器 OS |
| Veil | DOI:10.1007/978-3-031-98682-6_2 ✅ | CAV 2025，Lean4+SMT |
| seLe4n | github hatter6822/seLe4n | 唯一 Lean4 全 OS，6672 定理 |
| lean4lean | github digama0/lean4lean | Lean4 验证自身 |
| Lean4 #14576 | oss-security 2026-07 | 内核漏洞，无公理伪证 |
| Verification Theatre | IACR eprint 2026/192 ✅ | libcrux 13 漏洞逃验证 |
| Lean4 Omega.lean | github leanprover/lean4 | omega 实现 |
