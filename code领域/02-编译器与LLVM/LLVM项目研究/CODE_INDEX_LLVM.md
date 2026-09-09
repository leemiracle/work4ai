# 可运行代码 / Artifact 索引（LLVM 项目研究）

> 18 Expert + 7 Lens + 6 第二期专题 + E18 实测清单，**所有可运行程序/真实 grep 数据/工程实证** 的统一入口。
> 本项目代码实证来自两条源：① OpenXiangShan/llvm-project（22 子项目 monorepo）② 飞腾 phytium_repos（45 目录国产化实证池）。
> **总产出 ~2.0MB / ~65 万字（2026-07-07 完工）**。

---

## A. E18 飞腾特异性锚点实测（5 个清单，**路线 B 护城河地基**）

| 清单 | 路径 | 核心结论 |
|------|------|---------|
| phytvm fork diff | [`Expert_18_Phytium_Adaptation/phytvm_diff_findings.md`](./Expert_18_Phytium_Adaptation/phytvm_diff_findings.md) | ⚠️ `codegen_arm.cc` 是 vanilla Apache TVM（oracle §0.3 已澄清）；飞腾真实定制在 contrib/phytium + 外部 npu_compiler/gpu_compiler 二进制，**完全绕过 LLVM codegen** |
| phytium_repos LLVM patches | [`Expert_18_Phytium_Adaptation/phytium_repos_llvm_patches.md`](./Expert_18_Phytium_Adaptation/phytium_repos_llvm_patches.md) | 45 仓库**零飞腾 LLVM/Clang patch**，全是上游发行版（Android 12/Yocto 13.0.1/Buildroot 9.0.1/FreeBSD 19.1.7） |
| 主线 LLVM FTC86 源码确认 | [`Expert_18_Phytium_Adaptation/主线LLVM_FTC86_源码确认.md`](./Expert_18_Phytium_Adaptation/主线LLVM_FTC86_源码确认.md) | LLVM 23.0 全树 grep `FTC86\|Phytium` **零命中**；34 个 AArch64 调度模型无飞腾（华为有 TSV110） |
| 飞腾 SDK LLVM 版本矩阵 | [`Expert_18_Phytium_Adaptation/飞腾SDK_LLVM版本矩阵.md`](./Expert_18_Phytium_Adaptation/飞腾SDK_LLVM版本矩阵.md) | 6 大 OS 全用上游 LLVM，版本 9.0.1→19.1.7 跨 5 年碎片化；默认工具链除 FreeBSD 外全是 GCC |
| 国产 CPU 厂商 LLVM 生态 | [`Expert_18_Phytium_Adaptation/国产CPU厂商_LLVM_fork_生态.md`](./Expert_18_Phytium_Adaptation/国产CPU厂商_LLVM_fork_生态.md) | 三档分化：龙芯 LoongArch 主线 / 华为毕昇+TSV110+openEuler / 平头哥玄铁 C910 → **飞腾最末档，纯消费者** |

### E18 三条最关键工程实证（写进所有 Expert 的飞腾实证段）
1. **phytvm NPU/GPU 编译绕过 LLVM**（走外部 npu_compiler/gpu_compiler 二进制）——飞腾编译器创新在 LLVM 之外
2. **主线 LLVM 23.0 + 飞腾 45 公开仓库 = 零飞腾 LLVM 痕迹**——飞腾不自研 LLVM fork
3. **华为有毕昇+TSV110+主线贡献，龙芯有主线后端，飞腾三者皆无**——飞腾是国产 CPU 中编译器投入最浅的

---

## B. 18 Expert 视角（按完成状态）

### ✅ 已完成（18 个全完成，全部深度型 ≥50KB）

| # | Expert | 字数 | 核心判断 |
|:-:|--------|------|---------|
| 01 | [Clang 前端](./Expert_01_Clang_Frontend/README.md) | 59KB | Clang AST vs GCC GENERIC；CSA 性能爆炸债；C++20/23/26 + PAC/BTI/MTE；飞腾实际押 GCC 而非 Clang |
| 02 | [LLVM IR 设计](./Expert_02_LLVM_IR_Design/README.md) | 52KB/~12000字 | undef→poison 演进；miscompilation CVE 史；Alive2 是 LLVM Pass 验证金标准 |
| 03 | [Pass 框架](./Expert_03_Pass_Framework/README.md) | 60KB/627行 | New PM 10 年迁移债（断层 ④）；飞腾卡在 LLVM 13"中端新、后端旧"撕裂期 |
| 04 | [中端优化+MLIR](./Expert_04_Middle_End_Opt/README.md) | 62KB | MLIR 48 方言（实测）；断层 ② MLIR-core 融合裂痕 |
| 05 | [CodeGen SelectionDAG/GlobalISel](./Expert_05_CodeGen_SelectionDAG_GlobalISel/README.md) | 70KB | GlobalISel 覆盖率；AArch64.td 实例；飞腾无 SVE 的 Legalize 约束 |
| 06 | [RegAlloc+Scheduler](./Expert_06_RegAlloc_Scheduler/README.md) | 76KB | 四种 RegAlloc + Greedy 源码剖析；MISched；ML RegAlloc MLGO；飞腾 31 寄存器红利 |
| 07 | [自动向量化](./Expert_07_Auto_Vectorization/README.md) | 66KB | Vector Predication（VP）；飞腾无 SVE 的向量化天花板 |
| 08 | [AArch64 后端](./Expert_08_AArch64_Backend/README.md) | 60KB | ⭐ 主线 LLVM 无 FTC86x 调度模型；34 个调度模型清单；华为 TSV110 upstream 案例 |
| 09 | [x86 后端](./Expert_09_x86_Backend/README.md) | 87KB | LEA 7 用途深度；AVX-512 vs SVE；Intel-AMD 调度分裂；APX；commit 份额 |
| 10 | [RISC-V 后端](./Expert_10_RISCV_Backend/README.md) | 56KB | RVV 可变长；国产 RISC-V LLVM 生态（香山/玄铁/SG2042） |
| 11 | [GPU/异构后端](./Expert_11_GPU_Heterogeneous_Backend/README.md) | 68KB | ⭐ 断层 ① AMDGPU/NVPTX/BPF 对齐债；飞腾 NPU 绕过 LLVM |
| 12 | [LLD+BOLT](./Expert_12_LLD_BOLT/README.md) | 80KB | LLD ELF 架构；BOLT Meta 实证；mold/wild 冲击；ThinLTO |
| 13 | [LLDB 调试器](./Expert_13_LLDB_Debugger/README.md) | 90KB | LLDB vs GDB；DWARF 5/6；expression evaluator；嵌入式 RTOS 调试 |
| 14 | [Sanitizers+JIT](./Expert_14_CompilerRT_Sanitizers_JIT/README.md) | 71KB | ⭐ 断层 ③ ASan shadow + CFI + xz utils + ORC JIT + SanCov |
| 15 | [C++ 运行时栈](./Expert_15_Runtimes_libcxx/README.md) | 62KB | libcxx vs libstdc++ ABI；libunwind vs libgcc_s 战争 |
| 16 | [Flang](./Expert_16_Flang_Fortran/README.md) | 84KB | FIR 深度；OpenMP lowering；Intel ifx 对照；Fortran 标准进度 |
| 17 | [治理 License](./Expert_17_Governance_License/README.md) | 104KB | ⭐ 断层 ⑤ Linux 内核 GCC→Clang；公司 commit 份额；Apache 2.0 演变 |
| 18 | [飞腾收口](./Expert_18_Phytium_Adaptation/README.md) | 59KB + 5清单 | ⭐ 飞腾纯消费者；NPU 编译绕过 LLVM；华为 CANN 对照；六家国产 CPU 中最末档 |

### 🎉 第二期 6 专题（全部 ≥57KB）

| # | 专题 | 字数 | 承载 |
|:-:|------|:----:|------|
| S1 | [MLIR AI 编译器全景](./Second_Phase/S1_MLIR_AI_Compilers.md) | 61KB | 断层 ② 深化（48 方言 + StableHLO/IREE/torch-mlir/Mojo） |
| S2 | [飞腾商业版编译器深挖](./Second_Phase/S2_Phytium_Commercial_Compilers.md) | 67KB | 路线 B 飞腾案例（PhyCC/PhyGCC 闭源推测） |
| S3 | [LLVM 安全审计](./Second_Phase/S3_LLVM_Security_Audit.md) | 64KB | 断层 ③ 深化（miscompilation CVE + Alive2 + xz utils + AI 审 PR） |
| S4 | [国产 CPU 编译器研发投入量化](./Second_Phase/S4_China_CPU_Compiler_Investment.md) | 57KB | Lens_07 深化（六家厂商对照） |
| S5 | [飞腾 RISC-V 转向评估](./Second_Phase/S5_Phytium_RISCV_Transition.md) | 60KB | Lens_01/07 深化（Apple 类比 + trigger 矩阵） |
| S6 | [LLVM 编译器战争史 30 年](./Second_Phase/S6_Compiler_Wars_History.md) | 82KB | Lens_01/02 深化（GCC→LLVM→MLIR→Mojo） |

---

## C. 7 异质思维透镜

### ✅ 已完成（7 个全完成）

| 透镜 | 字数 | 核心判断 |
|------|------|---------|
| [Lens_01 历史学家](./Lenses/Lens_01_Historian.md) | 54KB | Carlota Perez 长波 + Kuhn 范式；MLIR 48 方言实测；飞腾纯消费者 |
| [Lens_02 Christensen](./Lenses/Lens_02_Christensen.md) | 38KB / 12000 字 | LLVM 颠覆 GCC 是混合颠覆；MLIR 是潜伏 disruptive；Cranelift 卡在 JIT niche |
| [Lens_03 供应链分析师](./Lenses/Lens_03_SupplyChain.md) | 44KB | Target 后端公司化养育地图；单点失败风险 |
| [Lens_04 经济学家](./Lenses/Lens_04_Economist.md) | 42KB | LLVM IR 多边平台；网络效应/锁定效应 |
| [Lens_05 反垄断学者](./Lenses/Lens_05_Antitrust.md) | 32KB / 9500 字 | Areeda 必需设施四要件；GCC→LLVM 垄断转移；CUDA vs LLVM |
| [Lens_06 教育学家](./Lenses/Lens_06_Educator.md) | 33KB | Kaleidoscope 教程；LLM 能否写 Pass |
| [Lens_07 国产化战略家](./Lenses/Lens_07_China_Localization.md) | 57KB / 7000 字 | 飞腾编译器自主度最低；华为/龙芯/平头哥对照 |

---

## D. 五个服务器命脉级断层（对标飞腾"无 BF16/I8MM/SVE"）

| # | 断层 | 承载 Expert | 状态 |
|:-:|------|----------|:----:|
| ① | GPU/异构后端对齐债 | E11 | ✅ |
| ② | MLIR-core 融合裂痕 | E04 | ✅ |
| ③ | 编译器供应链安全 | E14 | ✅ |
| ④ | New PM 10 年迁移债 | E03 | ✅ |
| ⑤ | Linux 内核 GCC→Clang 迁移 | E17 | ✅ |

---

## E. 一键全套验证（grep 命令汇总）

```bash
# 验证主线 LLVM 无飞腾（E18 实证）
grep -rn "FTC86\|Phytium" /data/usershare/ai/riscv/OpenXiangShan/llvm-project/llvm/ 2>/dev/null
# 预期：零命中

# 验证华为 TSV110 在主线（E08 实证）
grep -rn "TSV110\|tsv110" /data/usershare/ai/riscv/OpenXiangShan/llvm-project/llvm/lib/Target/AArch64/ 2>/dev/null

# 验证 phytvm codegen_arm.cc 是 vanilla TVM（oracle §0.3）
head -20 /data/usershare/ai/飞腾/phytium_repos/opt-npu/ncsdk/common/phytvm/src/target/llvm/codegen_arm.cc
# 预期：ASF License + "this is used as an example"

# 验证 MLIR 48 方言（Lens_01 实测）
ls /data/usershare/ai/riscv/OpenXiangShan/llvm-project/mlir/include/mlir/Dialect/ | wc -l

# 验证 New PM 仍在迁移（E03 实证）
ls -la /data/usershare/ai/riscv/OpenXiangShan/llvm-project/llvm/lib/IR/LegacyPassManager.cpp
# 预期：仍 1734 行，未删
```

---

## F. 飞腾工程实证数据汇总（E18 实测产出）

| 数据 | 值 | 来源 |
|------|-----|------|
| 主线 LLVM 23.0 FTC86 命中数 | **0** | E18 实测 |
| phytium_repos 45 目录飞腾 LLVM patch | **0** | E18 实测 |
| phytvm codegen_arm.cc | **vanilla Apache TVM** | oracle §0.3 |
| 飞腾 NPU 编译路径 | **绕过 LLVM**（外部 npu_compiler 二进制） | E18 实测 |
| Yocto LLVM 版本 | 13.0.1（New PM 默认版） | E18 实测 |
| FreeBSD LLVM 版本 | 19.1.7 | E18 实测 |
| Android 11 LLVM 版本 | 12（NDK 裁剪） | E18 实测 |
| Buildroot LLVM 版本 | 9.0.1 | E18 实测 |
| 飞腾默认工具链 | **GCC**（PhyGCC 10.3.2）；LLVM 次要 | E18 实测 |
| AArch64 调度模型总数 | **34 个** | E08 实测 |
| 华为在主线 LLVM | **有**（tsv110 在 AArch64Processors.td:833/1544） | E08+E18 实测 |
| 龙芯 LoongArch 在主线 | **有**（LLVM 18+，22.x 还在加 LA32） | Lens_07 实测 |
| 平头哥玄鉄 C910 在主线 | **fork**（未完全 upstream） | Lens_07 实测 |
| 飞腾在主线 LLVM | **零贡献**（既无后端也无调度模型） | E18 实测 |

---

## G. 文档型 artifact（项目骨架）

| 文件 | 角色 | 规模 |
|------|------|------|
| [`改造蓝图_LLVM.md`](./改造蓝图_LLVM.md) | 项目宪法 v1.0 | 12 章 / 路线 B + 18 Expert + 7 Lens + 5 断层 + 10 失败模式 |
| [`README.md`](./README.md) | 项目入口 | 与飞腾项目对偶定位 |
| [`Views_LLVM.md`](./Views_LLVM.md) | 视角矩阵导航 | 18 Expert + 7 Lens 四轴体系 |
| [`领域资源库_LLVM.md`](./领域资源库_LLVM.md) | 共享资源库 | 12 章（顶会/工具/教材/标准/中文社区/英文社区/视频/数据/22 子项目/飞腾专属/刷新机制） |
| [`oracle战略评审.md`](./oracle战略评审.md) | 战略评审存档 | 宪法依据 |
| [`CODE_INDEX_LLVM.md`](./CODE_INDEX_LLVM.md)（本文件） | artifact 索引 | — |

---

📌 **下一步**：等剩余 9 个 Expert/Lens 完成 → 写审计报告 → 更新 Views/README → git commit。
