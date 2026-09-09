# Views — Kernel-Lab 视角矩阵

> 不再是"单一优化工程师视角"。
> 本项目把**同一台飞腾 D3000（FTC862 / 4 FVU）上的算子优化**切成 **三层视角**：
> 技术维度（可执行 lens）→ 专家角色（书面审查）→ 异质思维（战略判断）。
>
> **护城河**：对一颗具体芯片算子性能的密集实测剖析 + 多视角交叉验证，不是通用优化教程。

---

## 0. 为什么要三层视角

| 层 | 回答什么 | 强项 | 弱项 |
|----|---------|------|------|
| **技术 lens**（可执行）| "瓶颈在哪？compute 还是 memory bound？" | 有 PMU/Roofline 实证 | 只看局部，不见森林 |
| **专家 lens**（书面）| "这个领域的专家会怎么决策？" | 深度，领域知识 | 易同质化（都是从业者）|
| **异质透镜**（战略）| "国产算力优化这件事，历史/VC/Christensen 怎么看？" | 跳出框架，命运判断 | 不直接产出代码 |

**三者对偶**：技术 lens 是"测量"，专家 lens 是"判断"，异质透镜是"跳出当前框架的全局审视"。
冲突时（如性能 vs 安全），记录在 §4 对偶矩阵，不掩盖。

---

## 1. 层 1：技术维度 lens（`analysis/`，可执行）

> 跑 `make lens && make analyze`，输出到 [`results/lenses/`](./results/lenses/)。

| Lens | 视角 | 程序 | 关键产出 |
|------|------|------|---------|
| **Roofline** | compute/memory bound 分类 | [`analysis/lens-roofline.c`](./analysis/lens-roofline.c) | 算子在 roofline 哪条线上 |
| **PMU** | 微架构 IPC/cache/branch/stall | [`analysis/lens-pmu.c`](./analysis/lens-pmu.c) | L1D miss / branch MPKI / backend stall |
| **Thermal** | 热设计 + DVFS 降频 | [`analysis/lens-thermal.c`](./analysis/lens-thermal.c) | 持续满载后是否降频 |
| **Precision** | FP16/INT8 误差分布 | [`analysis/lens-precision.c`](./analysis/lens-precision.c) | 量化精度损失是否可接受 |
| **Latency** | p50/p90/p99 长尾 | [`analysis/lens-latency.c`](./analysis/lens-latency.c) | 尾延迟（实时推理关键）|

---

## 2. 层 2：专家角色 lens（`docs/lenses/`，书面审查）

> 10 个领域专家对项目的审查报告。详见 [`docs/lenses/LENS-INDEX.md`](./docs/lenses/LENS-INDEX.md)。

| # | 角色 | 报告 | 一句话发现 |
|:-:|------|------|-----------|
| 1 | 性能架构师 | [`01`](./docs/lenses/01-performance-architect.md) | 零 prefetch / 宏参数未探索 / 多核 57% 误诊 |
| 2 | 算法科学家 | [`02`](./docs/lenses/02-algorithm-scientist.md) | BF16 缺席 / FP16 累加 bug / 距 Llama-7B 差 90% |
| 3 | OS/Runtime | [`03`](./docs/lenses/03-os-runtime-expert.md) | MC×NC 分块缺失（已修 +52%）/ hugepage / 绑核 |
| 4 | 编译器专家 | [`04`](./docs/lenses/04-compiler-expert.md) | PhyGCC/clang/gcc 零横评 / fast-math 未测 |
| 5 | 硬件专家 | [`05`](./docs/lenses/05-hardware-engineer.md) | 4 FVU 结构 / L3 双段 DynamIQ / Spec store bypass |
| 6 | 教育者 | [`06`](./docs/lenses/06-developer-advocate.md) | 缺 TUTORIAL+VISUAL+COMMON-PITFALLS 三件套 |
| 7 | DevOps/SRE | [`07`](./docs/lenses/07-sre.md) | CI 跑 Graviton 不是 D3000 / 零 perf-gate |
| 8 | QA | [`08`](./docs/lenses/08-qa.md) | 覆盖率 0.006% / 零 property testing |
| 9 | 安全 | [`09`](./docs/lenses/09-security.md) | malloc 零 NULL check（已修）/ NaN 链路 |
| 10 | 应用集成 | [`10`](./docs/lenses/10-integration.md) | 全仓 0 个 .h（已加 kernel_lab.h）|

---

## 3. 层 3：异质思维透镜（`Lenses/`，战略判断）

> 借用自姊妹项目「体系结构实验」，用**非从业者**的眼睛看"国产算力优化这件事"。
> 这些透镜不直接产出代码，但回答"为什么做、做给谁、能不能成"。

| 透镜 | 范式 | 在算子优化项目里的追问 | 锐度 |
|----|------|---------------------|:--:|
| [Lens_01 历史学家](./Lenses/Lens_01_Historian.md) | 历史模式匹配 | 国产算子库（如本项目）能否复刻 cuBLAS/MKL 的生态崛起路径？ | 🟢最高 |
| [Lens_02 破坏式创新者](./Lenses/Lens_02_Christensen.md) | Christensen | 边缘算力（D3000）是不是被高端 GPU"性能过度供给"留下的低端颠覆窗口？ | 🟢最高 |
| [Lens_03 供应链分析师](./Lenses/Lens_03_SupplyChain.md) | 依赖地图 | 算子优化的"卡脖子"在哪（编译器/库/工具链）？| 🟢高 |
| [Lens_04 经济学家](./Lenses/Lens_04_Economist.md) | 产业经济 | 自研算子库的规模效应/网络效应阈值？| 🟡中高 |
| [Lens_05 未来学家](./Lenses/Lens_05_Futurist.md) | 技术赌注 | D3000 无 SVE/BF16，在 2026+ AI 算力图景里还能撑多久？| 🟠中 |
| [Lens_06 人类学家](./Lenses/Lens_06_Anthropologist.md) | 组织社会学 | 信创迁移中，算子库的"不可见基础设施"角色 | 🟠中 |
| [Lens_07 VC 投资人](./Lenses/Lens_07_VC.md) | 下注判断 | 投不投"基于 D3000 的国产推理引擎"？| 🟢高 |
| [Lens_08 反垄断学者](./Lenses/Lens_08_Antitrust.md) | 平台经济 | CUDA/cuDNN 垄断租金 vs 国产算子库的必需设施机会 | 🟡中高 |
| [Lens_09 科技伦理学者](./Lenses/Lens_09_Ethics.md) | 双用途审视 | 国产算力优化的军民两用维度 | 🟠中 |

> **注**：异质透镜原文针对"飞腾芯片整体命运"，在算子优化项目里我们关注的是"算子库/推理引擎"这个子集。每个透镜顶部有"Kernel-Lab 适配说明"。

---

## 4. 对偶验证矩阵（核心机制：同一问题问两个视角）

| 现象 | 视角 1 | 视角 2 | 对偶结论 |
|------|--------|--------|---------|
| 多核只有 57% 效率 | 技术 lens-PMU（L3 双段）| 专家 03-OS（flat vs tiled）| ✅ 一致，MC×NC 分块是解 |
| FP16 MR=8 反而慢 | 专家 02-算法（累加 bug）| 技术 lens-precision（精度）| ⚠️ 算法 bug + 硬件吞吐双重原因 |
| 安全 vs 性能 | 专家 09-安全（NULL check）| 技术 lens-latency（防 check 开销）| ⚠️ 冲突：安全检查有微小开销，但必须做 |
| 国产算子库能不能成 | 专家 02-算法（技术差距）| Lens_01-历史（追赶者命运）| ⚠️ 局部技术最优 vs 周期宿命 |
| D3000 做 AI 推理 | 专家 02-算法（无 BF16）| Lens_05-未来（技术赌注）| ⚠️ 工程债 vs 不可逆缺硬件 |
| 自研算子库价值 | 专家 10-集成（库化）| Lens_07-VC（下注）| ✅ 一致，库化是生态门槛 |

---

## 5. 阅读建议（按背景）

### 优化工程师（写算子的人）
技术 lens（`make analyze`）→ 专家 01 架构师 → 专家 02 算法 → 专家 03 OS → [`项目宪法.md`](./项目宪法.md) §7 实验纪律

### 想理解"为什么这么优化"
专家 05 硬件（4 FVU）→ [`扩展专题.md`](./扩展专题.md)（NEON/UDOT/FP16）→ [`isa_reference/`](./isa_reference/) → 技术 lens-PMU

### 国产算力决策者
专家 02 算法（BF16 缺席）+ Lens_02 Christensen + Lens_07 VC + Lens_03 供应链

### 想破思维定式（异质透镜串读）
Lens_01 历史 → Lens_02 Christensen → Lens_07 VC → Lens_05 未来

---

## 6. 三层视角的协同工作流

```
   ┌─────────────────────────────────────────────────────────┐
   │ 异质透镜 Lenses/   "国产算子优化该不该做、做给谁"          │ 战略层
   │ (历史/Christensen/VC/未来)                               │ (不产出代码)
   └─────────────────────────────────────────────────────────┘
                              ↓ 指明方向
   ┌─────────────────────────────────────────────────────────┐
   │ 专家 lens docs/lenses/  "这个领域专家怎么决策"             │ 判断层
   │ (架构师/算法/OS/编译器/硬件/教育/SRE/QA/安全/集成)         │ (书面报告)
   └─────────────────────────────────────────────────────────┘
                              ↓ 给出具体建议
   ┌─────────────────────────────────────────────────────────┐
   │ 技术 lens analysis/    "瓶颈在哪、优化有没有效"            │ 测量层
   │ (Roofline/PMU/Thermal/Precision/Latency)                │ (可执行)
   └─────────────────────────────────────────────────────────┘
                              ↓ 验证落地
   ┌─────────────────────────────────────────────────────────┐
   │ src/ 算子实现    "GEMM/Conv/Attention 实际代码"            │ 实现层
   │ (18 个 Makefile 目标)                                    │ (C 代码)
   └─────────────────────────────────────────────────────────┘
```

**信息流**：异质透镜定方向 → 专家 lens 出建议 → 技术 lens 量化验证 → src/ 实现 → 技术 lens 回测 → 专家 lens 复审 → 异质透镜重估命运。
