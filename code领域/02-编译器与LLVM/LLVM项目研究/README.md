# LLVM 项目研究

> 🎉 **项目完工（2026-07-07）**：**第一期 25 视角全部完成（18 Expert + 7 Lens）+ 第二期 6 专题全部完成**，总产出 **~2.0MB / ~65 万字**，全部 Expert 达深度型（9 个 ≥80KB），5 个服务器命脉级断层全部承载，E18 飞腾特异性锚点实测 5 清单完成。git commit 链：`8a0f11b` → `fbda9af` → `97dbaec`。
>
> 一套针对 **LLVM 编译器 umbrella 项目（22 子项目）**的多专家深度剖析，
> 参照姊妹项目 `../体系结构实验/`（`../体系结构实验/`）（飞腾 D3000M）的"23 专家 + 9 透镜"范式，
> 把 LLVM 切成 **18 个专家视角 + 7 个异质思维透镜**，覆盖前端/中端/后端/Target 矩阵/工具链/运行时/治理全价值链。
>
> **本项目不是 LLVM 版维基百科**——每个视角必过"特异性测试 v2.0"：
> **代码级实例（引用 OpenXiangShan/llvm-project 真实代码） + 飞腾工程实证（phytium_repos 45 目录） + 对偶判断（vs GCC/Cranelift/MLIR）**，三选一必满足。

---

## 0. 项目定位

| 维度 | 本项目 | 姊妹项目（飞腾 D3000M） |
|------|--------|-------------------------|
| 主角 | LLVM 编译器 umbrella（22 子项目） | 飞腾 D3000M 芯片（FTC862） |
| 范式 | 领域通用指南 + 飞腾为案例 | 芯片特异剖析 |
| 视角 | 18 Expert + 7 Lens | 23 Expert + 9 Lens |
| 时间尺度 | 5-15 年（LLVM 演进周期） | 5-10 年（芯片生命周期） |
| 飞腾角色 | 案例锚点之一 | 主角 |
| 总规模 | ~65 万字（25 视角 + 6 第二期专题，全部深度型） | ~32 万字 |

**两者完全不重复**：飞腾项目谈"这颗芯片被 LLVM 怎么编译"，本项目谈"LLVM 这个 umbrella 的领域全貌，飞腾作为案例之一"。

---

## 1. 视角矩阵（18 专家 + 7 透镜）

### 1.1 18 专家视角（按 LLVM 价值链四轴）

#### 轴一·补全编译价值链（7 个 P0）

| # | 专家 | 一句话定位 | 状态 |
|:-:|------|-----------|:----:|
| 01 | [**Clang 前端**](./Expert_01_Clang_Frontend/) | C/C++/ObjC/Sema/AST/静态分析 | ✅ |
| 02 | [**LLVM IR 设计**](./Expert_02_LLVM_IR_Design/) | SSA/undef/poison/类型系统/内存模型 | ✅ |
| 03 | [**Pass 框架**](./Expert_03_Pass_Framework/) | Legacy PM → New PM 10 年迁移史 | ✅ |
| 04 | [**中端优化**](./Expert_04_Middle_End_Opt/) | GVN/SCCP/InstCombine + Polly + MLIR 融合 | ✅ |
| 05 | [**代码生成**](./Expert_05_CodeGen_SelectionDAG_GlobalISel/) | SelectionDAG + GlobalISel + TableGen | ✅ |
| 06 | [**寄存器分配与调度**](./Expert_06_RegAlloc_Scheduler/) | Greedy/Basic/Fast/PBQP + MISched + MC | ✅ |
| 07 | [**自动向量化**](./Expert_07_Auto_Vectorization/) | Loop Vec + SLP + Vector Predication | ✅ |

#### 轴二·Target 后端矩阵（4 个 P0）

| # | 专家 | 一句话定位 | 状态 |
|:-:|------|-----------|:----:|
| 08 | [**AArch64 后端**](./Expert_08_AArch64_Backend/) | ⭐ 飞腾直接命脉（FTC86x 调度模型） | ✅ |
| 09 | [**x86 后端**](./Expert_09_x86_Backend/) | 性能标杆对照（lea/AVX-512/Intel-AMD 分裂） | ✅ |
| 10 | [**RISC-V 后端**](./Expert_10_RISCV_Backend/) | 国产对偶（RVV/香山/玄铁） | ✅ |
| 11 | [**GPU/异构后端**](./Expert_11_GPU_Heterogeneous_Backend/) | ⭐ 服务器命脉级断层：AMDGPU/NVPTX/BPF 对齐债 | ✅ |

#### 轴三·工具链与运行时（4 个）

| # | 专家 | 一句话定位 | 状态 |
|:-:|------|-----------|:----:|
| 12 | [**LLD + BOLT**](./Expert_12_LLD_BOLT/) | 链接器 + 后链接优化 | ✅ |
| 13 | [**LLDB 调试器**](./Expert_13_LLDB_Debugger/) | LLDB vs GDB | ✅ |
| 14 | [**Sanitizers + JIT**](./Expert_14_CompilerRT_Sanitizers_JIT/) | ASan/MSan/CFI + ORC JIT | ✅ |
| 15 | [**C++ 运行时栈**](./Expert_15_Runtimes_libcxx/) | libcxx/libcxxabi/libunwind/openmp | ✅ |

#### 轴四·宏观与生态（3 个）

| # | 专家 | 一句话定位 | 状态 |
|:-:|------|-----------|:----:|
| 16 | [**Flang Fortran**](./Expert_16_Flang_Fortran/) | HPC 现代化（f18/FIR/MLIR） | ✅ |
| 17 | [**治理与 License**](./Expert_17_Governance_License/) | Apache 2.0 w/ LLVM Exception / 社区公司化 | ✅ |
| 18 | [**⭐ 飞腾/国产化适配收口**](./Expert_18_Phytium_Adaptation/) | phytvm fork diff + phytium_repos 45 目录实证 + 国产 CPU 厂商 LLVM fork 对照 | ✅ |

### 1.2 7 异质思维透镜（[`Lenses/`](./Lenses/)）

| 透镜 | 范式 | 一句话定位 | 锐度 |
|----|------|----------|:--:|
| [Lens_01 历史学家](./Lenses/Lens_01_Historian.md) | 历史模式匹配 | GCC→LLVM→MLIR 兴衰周期 | 🟢最高 |
| [Lens_02 破坏式创新](./Lenses/Lens_02_Christensen.md) | Christensen | LLVM 起步比 GCC 慢但模块化颠覆 | 🟢最高 |
| [Lens_03 供应链分析师](./Lenses/Lens_03_SupplyChain.md) | 依赖地图 | 每个 Target 后端哪个公司养着 | 🟢最高 |
| [Lens_04 经济学家](./Lenses/Lens_04_Economist.md) | 平台经济学 | LLVM IR 是多边平台 | 🟡中高 |
| [Lens_05 反垄断学者](./Lenses/Lens_05_Antitrust.md) | 平台垄断 | LLVM/Clang 是否新垄断 | 🟡中高 |
| [Lens_06 教育学家](./Lenses/Lens_06_Educator.md) | 教学法 | LLVM 帮了还是害了编译教育 | 🟠中 |
| [Lens_07 国产化战略家](./Lenses/Lens_07_China_Localization.md) | 自主可控 | 谁能摆脱 LLVM/GCC 依赖 | 🟢高 |

---

## 2. 五个"服务器命脉级断层"（对标飞腾"无 BF16/I8MM/SVE"战略伤疤）

| # | 断层 | 必接 Expert |
|:-:|------|----------|
| ① | **GPU/异构后端对齐债**（AMDGPU/NVPTX/BPF 谁养着） | E11 |
| ② | **MLIR 与 LLVM core 的融合裂痕** | E04 + MLIR |
| ③ | **编译器供应链安全**（miscompilation CVE、xz utils） | E14 + E17 |
| ④ | **New PM vs Legacy PM 10 年迁移债** | E03 |
| ⑤ | **Linux 内核 GCC→Clang 迁移**（2024-2026 真在进行） | E18 + E17 |

---

## 3. 项目目录结构

```
LLVM项目研究/
├── 改造蓝图_LLVM.md              ← 本项目宪法（视角清单/门槛/纪律）
├── README.md                     ← 本文件
├── Views_LLVM.md                 ← 18 Expert + 7 Lens 矩阵导航
├── 领域资源库_LLVM.md             ← 共享资源（含 5 个"只索引"子项目 + 网络资源）
├── oracle战略评审.md              ← oracle 战略评审报告（项目宪法依据）
├── CODE_INDEX_LLVM.md            ← 可运行代码/artifact 索引
├── 审计报告_LLVM.md               ← 质量审计
│
├── Expert_01_Clang_Frontend/     ← Clang 前端
├── Expert_02_LLVM_IR_Design/     ← LLVM IR 设计
├── Expert_03_Pass_Framework/     ← Pass 框架
├── Expert_04_Middle_End_Opt/     ← 中端优化 + MLIR
├── Expert_05_CodeGen_*/          ← SelectionDAG/GlobalISel/TableGen
├── Expert_06_RegAlloc_Scheduler/ ← 寄存器分配 + 调度
├── Expert_07_Auto_Vectorization/ ← 自动向量化
├── Expert_08_AArch64_Backend/    ← ⭐ 飞腾命脉
├── Expert_09_x86_Backend/        ← x86 后端
├── Expert_10_RISCV_Backend/      ← RISC-V 后端（国产对偶）
├── Expert_11_GPU_*/              ← ⭐ 异构债断层
├── Expert_12_LLD_BOLT/           ← 链接器 + 后链接优化
├── Expert_13_LLDB_Debugger/      ← 调试器
├── Expert_14_CompilerRT_*/       ← Sanitizers + JIT
├── Expert_15_Runtimes_libcxx/    ← C++ 运行时栈
├── Expert_16_Flang_Fortran/      ← Flang（第二期）
├── Expert_17_Governance_License/ ← 治理 License
├── Expert_18_Phytium_Adaptation/ ← ⭐ 飞腾收口（B 阶段先行）
│
├── Lenses/                       ← 7 异质思维透镜
├── Views/                        ← 工具集笔记
├── isa_reference/                ← ISA 参考引用（链接到飞腾项目）
└── common/                       ← 共用基础设施
```

---

## 4. 本地资源素材池（不可替代的写作素材）

| 资源 | 路径 | 用途 |
|------|------|------|
| LLVM monorepo（22 子项目全） | `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/` | 代码级实例素材库 |
| 飞腾 OS/固件/嵌入式生态 | `/data/usershare/ai/飞腾/phytium_repos/` | 飞腾工程实证素材库（45 目录） |
| 飞腾 NPU SDK（TVM fork） | `/data/usershare/ai/飞腾/phytium_repos/opt-npu/ncsdk/common/phytvm/` | E18 必做 diff |
| Yocto LLVM recipe | `/data/usershare/ai/飞腾/phytium_repos/phytium-linux-yocto/.../llvm/` | E12/E17 实证 |
| Android 11 LLVM | `/data/usershare/ai/飞腾/phytium_repos/e2000-android11-device/external_llvm-project/` | E17/E18 实证 |
| FreeBSD LLVM ports | `/data/usershare/ai/飞腾/phytium_repos/freebsd/contrib/llvm-project/` | E12/E17/E18 实证 |

---

## 5. 写作纪律（宪法 §7 摘要）

每个 Expert/Lens 强制：
1. **数字来源分级**：`[实测]`/`[官方]`/`[报告]`/`[社区]`/`[Discourse]`/`[HN/Reddit]`/`[GitHub commit]`/`[推测-依据]`
2. **强制"盲区与反方"段**：敢说这一视角看不见什么、会误导什么（反软文）
3. **强制对偶链接段**：指明与其他视角的一致/冲突
4. **必过 §0.3 特异性测试 v2.0**：飞腾工程实证 OR 代码级实例 OR 对偶判断，至少一项
5. **质量门槛**：Expert≥8000字/≥15参考/≥1对标表/≥3图表；Lens≥4500字/≥8参考

📌 深度样板：飞腾项目 Expert_11（编译器研究，610+ 行）
📌 反面教材（已规避）：把每个子项目写成 README 翻译（F3 失败模式）

---

## 6. 阶段路线图

```
阶段 A (1-2 天)  ┤ 透镜先行（破死板）—— Lens_01/02/03/07               │ 4 并行
                  └──────────────────────────────────────────────────┘
                                  ↓
阶段 B (1-2 天)  ┤ 特异性锚点实测（路线 B 地基）—— E18 + phytvm diff   │ 2-3 并行
                  └──────────────────────────────────────────────────┘
                                  ↓
阶段 C (3-5 天)  ┤ 价值链核心 —— E01-E07                                │ 7 并行
                  └──────────────────────────────────────────────────┘
                                  ↓
阶段 D (2-3 天)  ┤ Target 矩阵 —— E08-E11                              │ 4 并行
                  └──────────────────────────────────────────────────┘
                                  ↓
阶段 E (2-3 天)  ┤ 工具链运行时 —— E12-E15                             │ 4 并行
                  └──────────────────────────────────────────────────┘
                                  ↓
阶段 F (2-3 天)  ┤ 宏观长尾 —— E16/E17 + Lens_04/05/06                 │ 5 并行
                  └──────────────────────────────────────────────────┘
                                  ↓
阶段 G (1 天)    ┤ 全局整合 —— Views/CODE_INDEX/README/资源库/审计     │ 自做
                  └──────────────────────────────────────────────────┘
```

**总时长估算**：每个阶段 1-5 天，全流程约 **12-20 天**（auto_continue 持续推进）。

---

## 7. 如何开始

### 写作者（专家/透镜作者）

```bash
# 1. 先读宪法
cat 改造蓝图_LLVM.md

# 2. 读 oracle 评审（理解为什么这样切）
cat oracle战略评审.md

# 3. 读对应飞腾项目 Expert（避免重复）
cat ../体系结构实验/Expert_11_Compiler_Research/README.md

# 4. 探查本地资源
ls /data/usershare/ai/riscv/OpenXiangShan/llvm-project/<子项目>/
ls /data/usershare/ai/飞腾/phytium_repos/

# 5. 按 Expert 模板（宪法 §8）起草
```

### 阅读者

入门路径：
- **想看 LLVM 全貌** → [`Views_LLVM.md`](./Views_LLVM.md) → [`领域资源库_LLVM.md`](./领域资源库_LLVM.md)
- **想看飞腾特异** → [E08 AArch64](./Expert_08_AArch64_Backend/) → [E18 Phytium Adaptation](./Expert_18_Phytium_Adaptation/)
- **想破思维定式** → [`Lenses/`](./Lenses/)（历史/Christensen/供应链/国产化）
- **研究员/PhD** → E02 IR / E03 Pass / E11 GPU 异构债 + 各视角参考文献

---

## 8. 与飞腾项目的协同（不重复原则）

| 飞腾项目已有 | 本项目处置 |
|------------|----------|
| 飞腾 Expert_11_Compiler_Research（PhyGCC + Pass pipeline + RegAlloc） | **引用为 E08 AArch64 的飞腾案例段**，不重写 |
| 飞腾 View_01_Compiler（-O0..-Ofast 实测） | 引用为 E07 AutoVec / E06 RegAlloc 的实测来源 |
| 飞腾 Lab00-07（ISA/Cache/Pipeline 实测） | 引用为 E08 AArch64 的实测锚点 |
| 飞腾 isa_reference/ | 引用为 E08 AArch64 的 ISA 参考 |
| 飞腾 领域资源库.md | 部分通用资源（教材/顶会/分析机构）直接引用 |

📌 **下一步**：直接进入 [`改造蓝图_LLVM.md`](./改造蓝图_LLVM.md)（项目宪法）或 [`Views_LLVM.md`](./Views_LLVM.md)（视角矩阵导航）。
