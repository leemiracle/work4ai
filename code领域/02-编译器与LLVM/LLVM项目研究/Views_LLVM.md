# LLVM 项目研究 — 18 专家视角 + 7 异质思维透镜矩阵

> 不再是"飞腾版编译器"，也不止于"LLVM 教程"。
> 本项目把 **LLVM umbrella 项目（22 子项目）** 切成 **18 个顶级专家视角** + **7 个非从业者异质思维透镜**，
> 覆盖从前端 Clang/Flang 到 IR/Pass/CodeGen/RegAlloc/Target 矩阵/工具链/运行时/治理的**完整价值链与思维维度**。
>
> **护城河**：LLVM 作为编译器基础设施的领域通用深度剖析，飞腾 phytium_repos 45 目录作为案例锚点之一（而非全部）。
> 每个视角必过"特异性测试 v2.0"——**代码级实例 OR 飞腾工程实证 OR 对偶判断**，三选一必满足。

---

## 0. 为什么要"专家视角 + 异质透镜"

- **专家视角**回答"这个领域的首席从业者会怎么想这个问题"——深度，但易同质化（LLVM 项目同质化风险尤甚：所有专家都可能是"编译器工程师"）。
- **异质透镜**用历史学家/经济学家/反垄断学者等**非从业者**的眼睛看 LLVM——破"首席从业者"的思维定式。
- **两者对偶**：专家视角是"局部最优"，异质透镜是"跳出当前框架的全局审视"。

---

## 1. 18 专家视角全景

### 1.1 轴一·补全编译价值链（7 个 P0，"全"）

| # | 专家角色 | 一句话定位 | 关键 LLVM 锚点 | 阶段 |
|:-:|---------|-----------|--------------|:--:|
| 1 | [**Clang 前端**](./Expert_01_Clang_Frontend/) | C/C++/ObjC/Sema/AST/静态分析 | Clang AST vs GCC GENERIC、PhyCC LLVM 13 | C |
| 2 | [**LLVM IR 设计**](./Expert_02_LLVM_IR_Design/) | SSA/undef/poison/类型系统/内存模型 | undef→poison 演进、LangRef、miscompilation CVE | C |
| 3 | [**Pass 框架**](./Expert_03_Pass_Framework/) | Legacy PM → New PM 10 年迁移 | opt -passes=、analysis invalidation | C |
| 4 | [**中端优化**](./Expert_04_Middle_End_Opt/) | GVN/SCCP/InstCombine + Polly + MLIR 融合 | 2026 边际收益、Polly 为何没进 -O3 | F |
| 5 | [**代码生成**](./Expert_05_CodeGen_SelectionDAG_GlobalISel/) | SelectionDAG + GlobalISel + TableGen | GISel 覆盖率、AArch64.td 实例 | C |
| 6 | [**寄存器分配与调度**](./Expert_06_RegAlloc_Scheduler/) | Greedy/Basic/Fast/PBQP + MISched + MC | 飞腾 31 寄存器红利、Pre/Post-RA Sched | C |
| 7 | [**自动向量化**](./Expert_07_Auto_Vectorization/) | Loop Vec + SLP + Vector Predication | VP 扩展、对偶 GCC tree-vectorizer | C |

### 1.2 轴二·Target 后端矩阵（4 个 P0，"深"）

| # | 专家角色 | 一句话定位 | 关键锚点 | 阶段 |
|:-:|---------|-----------|---------|:--:|
| 8 | [**AArch64 后端**](./Expert_08_AArch64_Backend/) | ⭐ **飞腾直接命脉** | 主线 LLVM 无 FTC86x 调度模型 | D |
| 9 | [**x86 后端**](./Expert_09_x86_Backend/) | 性能标杆对照 | lea 7 用途、AVX-512 mask、Intel-AMD 分裂 | D |
| 10 | [**RISC-V 后端**](./Expert_10_RISCV_Backend/) | 国产对偶 | RVV 可变长、香山/玄铁调度模型 | D |
| 11 | [**GPU/异构后端**](./Expert_11_GPU_Heterogeneous_Backend/) | ⭐ **服务器命脉级断层** | AMDGPU/NVPTX/BPF 对齐债 | D |

### 1.3 轴三·工具链与运行时（4 个，"链"）

| # | 专家角色 | 一句话定位 | 关键锚点 | 阶段 |
|:-:|---------|-----------|---------|:--:|
| 12 | [**LLD + BOLT**](./Expert_12_LLD_BOLT/) | 链接器 + 后链接优化 | ThinLTO、BOLT PGO 反向 | E |
| 13 | [**LLDB 调试器**](./Expert_13_LLDB_Debugger/) | LLDB vs GDB | DWARF 解析、嵌入式 RTOS | E |
| 14 | [**Sanitizers + JIT**](./Expert_14_CompilerRT_Sanitizers_JIT/) | ASan/MSan/CFI + ORC JIT | shadow memory NUMA、V8/PG/MySQL JIT | E |
| 15 | [**C++ 运行时栈**](./Expert_15_Runtimes_libcxx/) | libcxx/libcxxabi/libunwind/openmp | libcxx vs libstdc++ ABI、libunwind 战争 | E |

### 1.4 轴四·宏观与生态（3 个，"大"）

| # | 专家角色 | 一句话定位 | 关键锚点 | 阶段 |
|:-:|---------|-----------|---------|:--:|
| 16 | [**Flang Fortran**](./Expert_16_Flang_Fortran/) | HPC 现代化（f18/FIR/MLIR） | gfortran 差距、国产量子/气象/CFD | F |
| 17 | [**治理与 License**](./Expert_17_Governance_License/) | Apache 2.0 w/ LLVM Exception / 公司化 | 6 月 release vs GCC 年度、commit 份额 | F |
| 18 | [**⭐ 飞腾/国产化收口**](./Expert_18_Phytium_Adaptation/) | phytvm diff + phytium_repos 45 目录实证 | ⚠️ vanilla TVM 误判纠正 + 国产 CPU LLVM fork 对照 | **B（先行）** |

---

## 2. 7 异质思维透镜（[`Lenses/`](./Lenses/)）

> 破"编译器工程师同质化"。每个用非从业者的眼睛看 LLVM，给出命运预测/下注判断。

| 透镜 | 范式 | 核心框架 | 锐度 | 阶段 |
|----|------|---------|:--:|:--:|
| [Lens_01 历史学家](./Lenses/Lens_01_Historian.md) | 历史模式匹配 | GCC→LLVM→MLIR 兴衰周期；预测 MLIR 是否颠覆 LLVM core | 🟢最高 | A |
| [Lens_02 破坏式创新者](./Lenses/Lens_02_Christensen.md) | Christensen | LLVM 起步比 GCC 慢但模块化颠覆；Cranelift 是否重演 | 🟢最高 | A |
| [Lens_03 供应链分析师](./Lenses/Lens_03_SupplyChain.md) | 依赖地图 | 每个 Target 后端哪个公司养着（Apple/AMD/NVIDIA/ARM/Huawei） | 🟢最高 | A |
| [Lens_04 经济学家](./Lenses/Lens_04_Economist.md) | 平台经济学 | LLVM IR 是多边平台（前端+后端双边），网络效应/锁定 | 🟡中高 | F |
| [Lens_05 反垄断学者](./Lenses/Lens_05_Antitrust.md) | 平台垄断 | LLVM/Clang 在 C/C++ 是否新垄断？Rust/CUDA 依赖 | 🟡中高 | F |
| [Lens_06 教育学家](./Lenses/Lens_06_Educator.md) | 教学法 | LLVM 帮了还是害了编译教育（Kaleidoscope/CS 241） | 🟠中 | F |
| [Lens_07 国产化战略家](./Lenses/Lens_07_China_Localization.md) | 自主可控 | 飞腾/华为/龙芯/申威/海光谁能摆脱 LLVM/GCC 依赖 | 🟢高 | A |

---

## 3. 四轴视角体系

```
轴一·补全编译价值链（"全"）
  Clang(E01) → IR(E02) → Pass(E03) → 中端+MLIR(E04)
            → CodeGen(E05) → RegAlloc+Sched(E06) → AutoVec(E07)

轴二·Target 后端矩阵（"深"）
  AArch64(E08) ⭐飞腾命脉   |   x86(E09) 标杆   |   RISC-V(E10) 国产对偶
  GPU/异构(E11) ⭐断层

轴三·工具链与运行时（"链"）
  LLD+BOLT(E12)   |   LLDB(E13)   |   Sanitizers+JIT(E14)   |   C++运行时栈(E15)

轴四·宏观与生态（"大"）
  Flang(E16)   |   治理(E17)   |   ⭐ 飞腾/国产化收口(E18)
```

---

## 4. 五个"服务器命脉级断层"（对标飞腾"无 BF16/I8MM/SVE"）

| # | 断层 | 必接 Expert | 对标飞腾 |
|:-:|------|----------|---------|
| ① | **GPU/异构后端对齐债** | E11 | 飞腾"AI 算力定位" |
| ② | **MLIR 与 LLVM core 融合裂痕** | E04 + MLIR | 飞腾"无 SVE 向量化天花板" |
| ③ | **编译器供应链安全** | E14 + E17 | 飞腾"服务器 RAS" |
| ④ | **New PM 10 年迁移债** | E03 | 飞腾"PhyGCC rebase 落后" |
| ⑤ | **Linux 内核 GCC→Clang 迁移** | E18 + E17 | 飞腾"ARM v9 不授" |

---

## 5. "对偶验证"矩阵（核心机制：同一问题问两个视角）

| 现象 | 视角1 | 视角2 | 对偶结论 |
|------|------|------|---------|
| MLIR 是否颠覆 LLVM core | E04 中端（融合） | Lens_01 历史（兴衰周期） | ⚠️ 工程融合 vs 历史周期 |
| 飞腾 FTC86x 调度缺失 | E08 AArch64（工程） | Lens_07 国产化（自主可控） | ⚠️ 工程补丁 vs 战略断层 |
| LLVM vs GCC 商业战 | E17 治理（社区） | Lens_05 反垄断（平台） | ✅ 互补 |
| 飞腾用 LLVM 还是 GCC | E18 飞腾收口（实证） | Lens_07 国产化（战略） | ✅ 工程跟随战略 |
| Rust 是否威胁 LLVM | E11 GPU/异构（共存） | Lens_02 Christensen（颠覆） | ⚠️ 共生 vs 颠覆 |
| GPU 后端腐烂风险 | E11（对齐债） | Lens_03 供应链（公司撤退） | ✅ 一致 |
| 编译器供应链安全 | E14 Sanitizers（防御） | Lens_05 反垄断（平台脆弱） | ✅ 一致 |
| New PM 迁移拖延 | E03 Pass（工程债） | Lens_04 经济（迁移成本） | ⚠️ 工程债 vs 经济理性 |

---

## 6. 阅读建议（按背景）

### 想看"LLVM 全产业链"
E01 Clang → E02 IR → E03 Pass → E05 CodeGen → E06 RegAlloc → E08 AArch64 → E12 LLD → E14 Sanitizers

### 国产化决策者
E18 Phytium + E08 AArch64 + Lens_07 国产化 + Lens_03 供应链 + E17 治理

### AI 时代定位
E04 中端 + MLIR 章节 + E11 GPU 异构债 + Lens_02 Christensen + 飞腾 E21 AI 定位（姊妹项目）

### 破思维定式（异质透镜串读）
Lens_01 历史 → Lens_02 Christensen → Lens_03 供应链 → Lens_07 国产化 → Lens_05 反垄断

### 研究员/PhD
E02 IR + E03 Pass + E11 GPU 异构债 + E14 Sanitizers + 全部对偶段 + 各视角参考文献

### 编译器工程师实战
E01 Clang + E03 Pass + E05 CodeGen + E06 RegAlloc + E07 AutoVec + E08 AArch64

---

## 7. 项目目录结构（与宪法 §11 一致）

```
LLVM项目研究/
├── 改造蓝图_LLVM.md          ← 项目宪法（视角清单/门槛/纪律）
├── README.md                 ← 项目入口
├── Views_LLVM.md（本文件）   ← 视角矩阵导航
├── 领域资源库_LLVM.md         ← 共享资源（含 5 索引 + 网络资源）
├── oracle战略评审.md          ← 战略评审报告（宪法依据）
├── CODE_INDEX_LLVM.md        ← artifact 索引
├── 审计报告_LLVM.md           ← 质量审计
│
├── Expert_01..18_*/           ← 18 专家视角
├── Lenses/                    ← 7 异质思维透镜
├── Views/                     ← 工具集笔记
├── isa_reference/             ← ISA 参考引用（飞腾项目）
└── common/                    ← 共用基础设施
```

---

## 8. 写作纪律（宪法 §7 摘要）

每个 Expert/Lens 强制：
1. **数字来源分级**：8 级标签
2. **强制"盲区与反方"段**：反软文
3. **强制对偶链接段**：指明与其他视角一致/冲突
4. **必过 §0.3 特异性测试 v2.0**：代码实例 OR 飞腾实证 OR 对偶判断
5. **质量门槛**：Expert≥8000字/≥15参考/≥1对标表/≥3图表；Lens≥4500字/≥8参考

📌 深度样板：飞腾项目 Expert_11_Compiler_Research（610+ 行）

---

📌 **下一步**：从 [Expert_18 Phytium Adaptation](./Expert_18_Phytium_Adaptation/)（B 阶段先行）或 [Lenses/](./Lenses/)（A 阶段透镜）开始。
