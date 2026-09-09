# 改造蓝图与写作规范（LLVM 项目宪法 v1.0）

> 本文件是"LLVM 项目研究"视角体系建设的**最高决策文档**。
> 所有 Expert 与 Lens 都必须遵循此处的清单、门槛、模板、纪律。
> 制定于 2026-07-07，整合了 oracle 战略评审（`oracle战略评审.md`）的全部修正。
> **姊妹项目**：`../体系结构实验/改造蓝图与写作规范.md`（`../体系结构实验/改造蓝图与写作规范.md`）（飞腾 D3000M 项目宪法 v1.0）

---

## 0. 一条战略忠告（最高原则）

> **项目护城河 = LLVM 作为编译器基础设施的领域通用深度剖析，飞腾 phytium_repos / phytvm 作为案例锚点之一（而非全部）。**

### 0.1 路线判定（oracle 评审的核心结论）

LLVM **不是飞腾的芯片**。强行套飞腾项目的"芯片特异剖析"范式（删芯片名后不能读成通用教科书）会逼出大量伪造特异性。本项目的正确路线是 **Expert升级指南.md** 已经指明的方向：

> "用户指出 Expert 太'就飞腾论飞腾'，应升级为**该领域的通用专家指南**——飞腾作为案例锚点而非全部。"

**本项目天然就是"领域通用指南"**，飞腾 phytium_repos 45 目录是案例池。

### 0.2 战略级发现（必须诚实处理，对应宪法 §4.3 反软文精神）

> ⚠️ **`opt-npu/ncsdk/common/phytvm/src/target/llvm/codegen_arm.cc` 是 vanilla Apache TVM upstream 代码**，文件头部明确写"This is used as an example on how to override behavior llvm code generator for specific target"。
>
> **这不是飞腾深度自研的 LLVM 后端**。`phytvm` 是 Apache TVM 的完整 fork，LLVM target 部分是通用桥接代码。飞腾的真正定制在别处（最可能在 `src/target/opt/`、NPU 自定义 target kind、或 `contrib/` 目录，需在 E18 Phytium Adaptation 中做完整 diff 确认）。

**这个发现的意义**：飞腾对 LLVM 的贡献是**工程消费**（在 45 个 OS/嵌入式发行版里用 LLVM/Clang 做了什么裁剪、什么适配、遇到什么坑），不是**自研定制**。这个差异决定了路线 B 是唯一正确的路线。

### 0.3 特异性测试 v2.0（替代飞腾项目宪法 §0 的"芯片特异测试"）

> **LLVM 项目特异性测试**：删掉飞腾/phytium_repos/phytvm 后，若该文读得通 → 判定失败。
> **或者**：若该文只是翻译 LLVM 官方文档/README，无任何"代码级实例 + 工程教训 + 对偶判断" → 判定失败。

**双重门槛**：每个 Expert/Lens 必须满足以下**至少一项**：
- **(a) 飞腾工程实证**：引用 phytium_repos / OpenXiangShan 里真实的 recipe/patch/config/代码片段
- **(b) 代码级实例**：引用 OpenXiangShan/llvm-project 里真实的 `.td`/`.cpp`/Pass 代码片段（不是 README 翻译）
- **(c) 对偶判断**：给出"如果换 GCC/Cranelift/MLIR 会怎样"的对比判断

**理由**：LLVM 太通用，必须用"代码实例 + 工程教训 + 对偶判断"三件套替代"芯片实测"作为特异性来源。

---

## 1. 22 子项目优先级矩阵（核心交付物）

LLVM monorepo 有 22 个子项目（见 `OpenXiangShan/llvm-project/`），若每个都做 8000+ 字 Expert，总规模 ≈ 22 万字，**必然规模失控 + 通用化失焦**。切分依据三条：
1. 是否过 §0.3 特异性测试 v2.0
2. 是否在飞腾工程实战里出现过（phytium_repos 45 目录是否真实用到）
3. 是否是 LLVM 价值链的承重墙

| 子项目 | 优先级 | 处置 | 理由 |
|--------|:----:|------|---------------------|
| **llvm** (core) | **P0** | 拆为多个 Expert（E02 IR / E03 Pass / E04 中端 / E05 CodeGen / E06 RegAlloc / E07 AutoVec） | IR/Pass/CodeGen 是 LLVM 心脏 |
| **clang** | **P0** | 独立 Expert（E01 Clang Frontend） | C/C++ 前端，飞腾代码起点 |
| **mlir** | **P0** | 独立章节（合并进 E04 中端 + 战略断层章节） | AI 推理框架底座，飞腾 NPU 命脉 |
| **lld** | **P0** | 独立 Expert（E12 LLD + BOLT） | 默认链接器，FreeBSD/Android/飞腾嵌入式都用 |
| **compiler-rt** | **P0** | 独立 Expert（E14 Sanitizers + JIT） | ASan/MSan/CFI，飞腾服务器 RAS 命脉 |
| **clang-tools-extra** | P1 | 合并进 E01 Clang | 工具，不是独立学科 |
| **flang** + flang-rt | P1 | 独立 Expert（E16 Flang，第二期） | HPC/科学计算命脉 |
| **lldb** | P1 | 独立 Expert（E13 LLDB） | 调试器，飞腾开发者体验 |
| **bolt** | P1 | 合并进 E12 | 反馈优化，独立但小 |
| **orc-rt** + llvm JIT | P1 | 合并进 E14 | JIT 命脉 |
| **polly** | P2 | 合并进 E04 中端 | 多面体优化，研究意义大 |
| **offload** + libsycl | P2 | 合并进 E11 GPU/异构后端 | OpenMP target / SYCL |
| **libclc** | P3 | **只索引**（领域资源库） | OpenCL C 运行时，小众 |
| **libc** | P3 | **只索引** | LLVM libc 仍在早期 |
| **libcxx** + libcxxabi + libunwind | P2 | 独立 Expert（E15 C++ 运行时栈） | C++ ABI 命脉 |
| **llvm-libgcc** | P3 | **只索引** | GCC 兼容层 |
| **openmp** | P2 | 合并进 E15 或 E11 | OpenMP runtime |
| **runtimes** + cross-project-tests | P3 | **只索引** | 元构建 |

### 收口结论

**22 子项目 → 收敛到 15 个核心 Expert + 3 个第二期 Expert + 7 个 Lens + 5 个"只索引"条目**。
- **独立成 Expert（15+3）**：见 §3
- **合并进其它 Expert（5 类）**：clang-tools-extra→E01；bolt→E12；polly→E04；offload+libsycl→E11；openmp→E15
- **只索引（5 个）**：libclc / libc / llvm-libgcc / runtimes / cross-project-tests —— 在 `领域资源库_LLVM.md` 里各写一段定位 + 入口链接

---

## 2. 护城河（路线 B 的具体支撑）

### 2.1 四类飞腾特异性锚点的诚实评估

| 锚点候选 | 用户原认知 | 实测核实（oracle） | 强度 |
|---------|---------|---------|:----:|
| 飞腾自研 NPU TVM LLVM 后端 | ⭐ 强护城河 | `codegen_arm.cc` 是 **vanilla Apache TVM upstream** | 🔴 虚 |
| e2000-android11 / ft2004-android10 LLVM 精简版 | 中 | Android NDK 裁剪版（Google 维护为主） | 🟠 待查 |
| 飞腾用 LLVM 给 FTC862 做的定制 | 中 | 主线 LLVM **无 FTC86x 调度模型**（E11 已点破） | 🟡 反向锚点 |
| Yocto recipe / FreeBSD ports | 弱 | 真实工程产物 | 🟢 实 |
| **phytium_repos 45 目录的 OS/固件生态** | 用户未提 | **最强护城河**：飞腾在 Linux/Yocto/Buildroot/Android/FreeBSD/NuttX/FreeRTOS/seL4/Zephyr/OpenHarmony/OpenEuler 全栈用 LLVM/Clang | 🟢 强 |

### 2.2 真正的护城河

> **飞腾整个国产化软件栈对 LLVM/Clang 的工程消费**（phytium_repos 45 目录）+ **主线 LLVM 对 FTC86x 的"无调度模型"反向锚点** + **OpenXiangShan/llvm-project 完整 monorepo 的代码级实例**。

这三者构成本项目不可替代的素材库。

---

## 3. 18 Expert 清单（15 核心 + 3 第二期）

### 3.1 轴一·补全编译价值链（7 个 P0）

| # | 目录名 | 定位 | 关键 LLVM 锚点 | 阶段 |
|:-:|------|------|----------------|:--:|
| 01 | `Expert_01_Clang_Frontend` | Clang 前端（C/C++/ObjC/Sema/AST/静态分析） | Clang AST vs GCC GENERIC、PhyCC 用 LLVM 13、phytium_repos Android NDK 的 Clang | C |
| 02 | `Expert_02_LLVM_IR_Design` | LLVM IR 设计与语义（SSA/undef/poison/类型系统/内存模型） | undef vs poison 演进、LangRef、miscompilation CVE 史 | C |
| 03 | `Expert_03_Pass_Framework` | Pass 框架（Legacy PM → New PM 迁移） | 10 年迁移史、opt -passes=、analysis invalidation | C |
| 04 | `Expert_04_Middle_End_Opt` | 中端优化（GVN/SCCP/InstCombine/SROA/LICM/LoopUnroll + Polly + MLIR） | 2026 边际收益、Polly 为何没进 -O3、MLIR 融合裂痕（战略断层） | F |
| 05 | `Expert_05_CodeGen_SelectionDAG_GlobalISel` | 指令选择与合法化（SelectionDAG + GlobalISel + TableGen） | GlobalISel 覆盖率、AArch64.td 实例、Legalize 对"无 SVE"的约束 | C |
| 06 | `Expert_06_RegAlloc_Scheduler` | 寄存器分配 + 指令调度 + MC layer | Greedy/Basic/Fast/PBQP、Pre/Post-RA Sched、MISched、飞腾 31 寄存器红利 | C |
| 07 | `Expert_07_Auto_Vectorization` | 自动向量化（Loop Vec + SLP + VP） | Loop Vec cost model、Vector Predication、SLP 覆盖率、对偶 GCC tree-vectorizer | C |

### 3.2 轴二·Target 后端矩阵（4 个 P0）

| # | 目录名 | 定位 | 关键锚点 | 阶段 |
|:-:|------|------|----------|:--:|
| 08 | `Expert_08_AArch64_Backend` | ARM/AArch64 后端（飞腾直接命脉） | ⭐ **主线 LLVM 无 FTC86x 调度模型**、AArch64.td 清单、PhyGCC vs LLVM 对照 | D |
| 09 | `Expert_09_x86_Backend` | x86 后端（性能标杆对照） | lea 7 种用途、AVX-512 vs SVE mask、Intel/AMD 调度分裂 | D |
| 10 | `Expert_10_RISCV_Backend` | RISC-V 后端（国产对偶） | RVV 可变长向量、香山/玄铁/算能调度模型、ARM vs RISC-V 工程成熟度 | D |
| 11 | `Expert_11_GPU_Heterogeneous_Backend` | GPU/异构后端（⭐ 服务器命脉级断层：对齐债） | AMDGPU/NVPTX/BPF/SPIR-V 后端、谁养着谁、飞腾 NPU 编译路线 | D |

### 3.3 轴三·工具链与运行时（3 个 P0 + 1 个 P1）

| # | 目录名 | 定位 | 关键锚点 | 阶段 |
|:-:|------|------|----------|:--:|
| 12 | `Expert_12_LLD_BOLT` | 链接器（LLD）+ 后链接优化（BOLT） | ELF/COFF/MachO/WASM、ThinLTO vs Full LTO、BOLT 反馈优化 | E |
| 13 | `Expert_13_LLDB_Debugger` | 调试器（LLDB） | LLDB vs GDB、DWARF 解析、expression evaluator、嵌入式 RTOS 覆盖 | E |
| 14 | `Expert_14_CompilerRT_Sanitizers_JIT` | Sanitizers + compiler-rt + ORC JIT | ASan shadow memory 在 ARM64 NUMA、MSan libc intercept、CFI 开销、ORC JIT（V8/PG/MySQL） | E |
| 15 | `Expert_15_Runtimes_libcxx` | C++ 运行时栈（libcxx/libcxxabi/libunwind/openmp/offload） | libcxx vs libstdc++ ABI、C++ 异常零开销、libunwind vs libgcc_s、OpenMP 多核扩展 | E |

### 3.4 轴四·宏观与生态（1 P0 + 2 P1）

| # | 目录名 | 定位 | 关键锚点 | 阶段 |
|:-:|------|------|----------|:--:|
| 16 | `Expert_16_Flang_Fortran` | Flang Fortran 现代化（f18/FIR/MLIR） | PGI/NVIDIA 重写、gfortran 差距、HPC 国产化（量子/气象/CFD） | F |
| 17 | `Expert_17_Governance_License` | LLVM 治理、License 与社区 | Apache 2.0 with LLVM Exception 演变、6 月 release vs GCC 年度、公司化（Apple/Google/AMD/NVIDIA/ARM/Huawei commit 份额） | F |
| 18 | `Expert_18_Phytium_Adaptation` | ⭐ **飞腾/国产化适配收口**（路线 B 的命脉） | phytvm fork diff（纠正 vanilla TVM 误判）、phytium_repos 45 目录 LLVM/Clang patch 盘点、主线 LLVM FTC86x 调度模型源码确认、国产 CPU 厂商 LLVM fork 生态对照（飞腾/华为/龙芯/申威） | **B（先行）** |

---

## 4. 7 异质思维透镜（`Lenses/`）

> 破"编译器工程师同质化"。LLVM 项目最大的同质化风险是"所有专家都是编译器工程师，都从代码看"。透镜必须用**非编译器从业者**的眼睛。

| 文件 | 范式 | 核心框架 | 锐度 | 阶段 |
|----|------|---------|:--:|:--:|
| `Lenses/Lens_01_Historian.md` | 历史学家 | GCC 1987→LLVM 2000→Clang 2007→MLIR 2019 兴衰周期；预测 MLIR 是否会颠覆 LLVM core | 🟢最高 | A |
| `Lenses/Lens_02_Christensen.md` | 破坏式创新 | LLVM 起步比 GCC 慢但**模块化+可复用**——典型低端颠覆；Cranelift/MLIR 是否在重演 | 🟢最高 | A |
| `Lenses/Lens_03_SupplyChain.md` | 供应链分析师 | 每个 Target 后端是哪个公司养着的（Apple/AMD/NVIDIA/ARM/Huawei）依赖图 | 🟢最高 | A |
| `Lenses/Lens_04_Economist.md` | 经济学家 | LLVM IR 作为**多边平台**（前端 Clang/Flang/Rust + 后端 Target 双边），网络效应/锁定 | 🟡中高 | F |
| `Lenses/Lens_05_Antitrust.md` | 反垄断学者 | LLVM/Clang 在 C/C++ 是否形成新垄断？Rust/CUDA 依赖 | 🟡中高 | F |
| `Lenses/Lens_06_Educator.md` | 教育学家 | LLVM 作为编译教学素材（Kaleidoscope/CS 241/龙书 vs LLVM）——帮了还是害了编译教育？ | 🟠中 | F |
| `Lenses/Lens_07_China_Localization.md` | 国产化战略家 | 编译器自主可控——飞腾/华为/龙芯/申威/海光谁能摆脱 LLVM/GCC 依赖？ | 🟢高 | A |

---

## 5. 五个"服务器命脉级断层"（对标飞腾项目的"无 BF16/I8MM/SVE"战略伤疤）

LLVM 项目的"断层"= 哪些缺失让 LLVM 在某个关键生产场景**跑不了/跑不稳/跑不安全**。

| # | 断层 | 命脉级别 | 必接 Expert | 对标飞腾 |
|:-:|------|:------:|----------|---------|
| ① | **GPU/异构后端对齐债**（AMDGPU/NVPTX/BPF 每个由不同公司养，质量参差） | 🟢最高 | E11 | 飞腾"AI 算力定位"战略伤疤 |
| ② | **MLIR 与 LLVM core 的融合裂痕**（独立 dialect 生态，与 LLVM IR 二元） | 🟢最高 | E04 + MLIR 章节 | 飞腾"无 SVE 向量化天花板" |
| ③ | **编译器供应链安全**（miscompilation CVE、xz utils 教训、Alive2/CompCert 对比） | 🟢最高 | E14 + E17 | 飞腾"服务器 RAS" |
| ④ | **New PM vs Legacy PM 的 10 年迁移债** | 🟢高 | E03 | 飞腾"PhyGCC rebase 落后" |
| ⑤ | **Linux 内核 GCC→Clang 迁移**（2024-2026 真在进行，国产化内核编译命脉） | 🟢最高 | E18 + E17 | 飞腾"ARM v9 不授" |

**理由**：这 5 个都满足"服务器命脉级"——丢了一个，LLVM 在某关键场景就跑不了/跑不稳/跑不安全。

---

## 6. 失败模式预警（这个项目最容易怎么翻车）

| # | 失败模式 | 危险度 | 表现 | 预防措施 |
|:-:|---------|:----:|------|---------|
| **F1** | 规模失控 | 🔴🔴🔴 | 22 子项目全做 8000 字 Expert，总 22 万字，半成品堆积 | §1 收口 15+3 Expert + 5 索引，硬上限 16 万字 |
| **F2** | 通用化失焦（过不了 §0.3 v2.0） | 🔴🔴🔴 | 写成 LLVM 教科书，删飞腾后读得通 | §0.3 双重门槛：飞腾工程实证 OR 代码级实例 OR 对偶判断 |
| **F3** | README 翻译 | 🔴🔴 | 每个子项目抄官方 README/Doxygen | 强制引用 OpenXiangShan/llvm-project 真实代码片段（行号、`.td`/`.cpp`） |
| **F4** | 忽略飞腾工程实战 | 🔴🔴 | 本地有 phytium_repos 45 目录 + phytvm fork，却只写通用 LLVM | E18 必须是 P0 且先行（阶段 B），每个轴一/二/三专家都要有飞腾实证段 |
| **F5** | 重复 E11 已写内容 | 🔴🔴 | 飞腾项目 E11 已经写了 PhyGCC + Pass pipeline + RegAlloc | E11 内容降为本项目的 ARM 后端案例段，**不重写**，只引用 |
| **F6** | 误判护城河 | 🔴🔴 | 把 phytvm codegen_arm.cc 当飞腾自研 LLVM 后端 | §0.2 已诚实指出是 vanilla TVM，E18 必须先做完整 diff 确认 |
| **F7** | 透镜后置 | 🟡 | 把透镜放最后 | 宪法已修正：透镜先行（A 阶段） |
| **F8** | 盲区段缺失 | 🟡 | 不写"盲区与反方" | §4.3 强制，审计报告扫 |
| **F9** | 数字不分级 | 🟡 | `[推测]` 不标依据 | §4.3.1 强制 8 级标签 |
| **F10** | 三连环教训重演 | 🟡 | auto_continue 未开 / 误信假审计 / 单源不交叉验证 | 项目记忆块已记录的前次教训 |

---

## 7. 质量门槛（沿用飞腾项目宪法 §4）

### 7.1 Expert 硬性下限

| 维度 | 下限 |
|------|------|
| 字数 | ≥ 8000 字（深度型 ≥ 12000） |
| 参考文献 | ≥ 15 条，其中 ≥ 5 条论文/标准/官方文档 |
| 量化对标表 | ≥ 1 张（PPA / benchmark / 性能 / commit 份额） |
| 图表 | ≥ 3 张（ASCII / 表格，鼓励代码片段） |
| 可运行/可验证 artifact | 技术类尽量有（diff / 脚本 / 引用代码行号） |
| **§0.3 特异性测试 v2.0** | ✅ **必过**（双重门槛至少一项） |

### 7.2 Lens 硬性下限

| 维度 | 下限 |
|------|------|
| 字数 | ≥ 4500 字 |
| 框架引用 | 明确使用 named framework |
| LLVM 命运判断 | 必须给出具体预测/下注 |
| 对偶 | 指出该透镜与从业者视角的冲突点 |

### 7.3 三条制度性纪律（强制）

1. **数字来源分级制**：所有数字必须标 `[实测]` / `[官方文档]` / `[第三方报告]` / `[社区]` / `[推测-依据]` / `[GitHub commit]` / `[Discourse]` / `[HN/Reddit]`。
2. **"盲区/弱点"诚实段强制**：每个 Expert 必须有一节"这一视角的盲区与反方"——敢说这一视角看不见什么、会误导什么。**杜绝软文。**
3. **对偶链接强制**：每个 Expert/Lens 必须有"与其他视角对偶"段，指明一致/冲突。

---

## 8. Expert 写作模板（统一结构）

```markdown
# Expert_XX — <角色名>视角

> **角色定位**：这位专家是谁、在什么岗位、做什么决策（1 段）
> **核心思维模型**：他怎么分析问题（1 段，named framework）

## 1. 看 LLVM 的 N 个核心问题（8-12 个，尖锐）
## 2. 具体分析（过特异性测试 v2.0：代码级实例 + 飞腾实证 + 对偶判断）
   - 2.1 ...（含量化对标表 + 代码片段）
   - 2.2 ...（含图表）
## 3. 设计决策评估（LLVM 哪些决策认可 / 哪些该改 / 飞腾工程教训）
## 4. 这一视角的盲区与反方（诚实段，强制）
## 5. 与其他视角对偶（一致 / 冲突，强制）
## 6. 参考文献（≥15，分级标注）
## 7. 延伸阅读（项目内引用 + 外部）
## § 领域方法论与资源（不只 LLVM，给所有该领域从业者）—— 通用资源引用 领域资源库_LLVM.md
```

### Lens 写作模板

```markdown
# Lens_0X — 用 <范式> 的眼睛看 LLVM

> **范式**：named framework
> **为什么从业者看不见**：这个透镜破解了什么同质化

## 1. 这个范式的核心逻辑（1 节）
## 2. 用它看 LLVM（3-5 个尖锐判断）
## 3. 对 LLVM 命运的具体预测/下注（强制可证伪）
## 4. 这个透镜与从业者视角的冲突（对偶）
## 5. 参考文献
## § 范式方法论与资源（通用化）
```

---

## 9. 执行阶段（A→G）

> **关键修正**：透镜先行（破死板）+ 阶段 B 改为"特异性锚点实测"（路线 B 的地基）。

| 阶段 | 内容 | 并行度 |
|:--:|------|:----:|
| **A** | 破死板：Lens_01 历史 / Lens_02 Christensen / Lens_03 供应链 / Lens_07 国产化 | 4 并行 |
| **B** | 特异性锚点实测（护城河）：E18 Phytium Adaptation + phytvm fork 完整 diff + phytium_repos 45 目录 LLVM/Clang patch 盘点 + 主线 LLVM FTC86x 调度模型源码确认 | 2-3 并行 |
| **C** | 价值链核心：E01 Clang / E02 IR / E03 Pass / E04 中端 / E05 CodeGen / E06 RegAlloc / E07 AutoVec | 7 并行 |
| **D** | Target 矩阵：E08 AArch64 / E09 x86 / E10 RISC-V / E11 GPU 异构债 | 4 并行 |
| **E** | 工具链与运行时：E12 LLD+BOLT / E13 LLDB / E14 Sanitizers+JIT / E15 C++ 运行时栈 | 4 并行 |
| **F** | 宏观与长尾：E16 Flang / E17 治理 + Lens_04 经济 / Lens_05 反垄断 / Lens_06 教育 | 5 并行 |
| **G** | 全局整合：Views_LLVM.md / CODE_INDEX_LLVM.md / README.md / 领域资源库_LLVM.md / 审计报告.md | 自做 |

---

## 10. 与飞腾项目的关系

### 10.1 不重复（避免 F5）

| 飞腾项目已有 | 本项目处置 |
|------------|----------|
| 飞腾 Expert_11_Compiler_Research（PhyGCC + Pass pipeline） | **降为本项目 E08 AArch64 的飞腾案例段**，引用不重写 |
| 飞腾 View_01_Compiler（-O0..-Ofast 实测） | 引用为 E07 AutoVec / E06 RegAlloc 的实测数据来源 |
| 飞腾 isa_reference/ | 引用为 E08 AArch64 的 ISA 锚点 |

### 10.2 互补

| 维度 | 飞腾项目 | LLVM 项目 |
|------|---------|----------|
| 主角 | 一颗芯片（D3000M） | 一个编译器 umbrella（LLVM） |
| 护城河 | 芯片实测 | 领域通用深度 + phytium_repos 案例 |
| 时间尺度 | 5-10 年（这颗芯片的生命周期） | 5-15 年（LLVM 的演进周期） |
| 飞腾角色 | 主角 | 案例锚点之一 |

---

## 11. 本地资源清单（写作素材池）

| 资源 | 路径 | 用途 |
|------|------|------|
| LLVM monorepo（完整 22 子项目） | `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/` | 代码级实例素材库（首选） |
| 飞腾 OS/固件/嵌入式生态（45 目录） | `/data/usershare/ai/飞腾/phytium_repos/` | 飞腾工程实证素材库 |
| 飞腾 NPU SDK（TVM fork） | `/data/usershare/ai/飞腾/phytium_repos/opt-npu/ncsdk/common/phytvm/` | ⚠️ E18 必做 diff 确认 |
| Yocto LLVM recipe | `/data/usershare/ai/飞腾/phytium_repos/phytium-linux-yocto/poky/meta/recipes-devtools/llvm/` | E12 LLD / E17 治理 实证 |
| Android 11 LLVM 精简版 | `/data/usershare/ai/飞腾/phytium_repos/e2000-android11-device/external_llvm-project/` | E17 / E18 实证 |
| FreeBSD LLVM ports | `/data/usershare/ai/飞腾/phytium_repos/freebsd/contrib/llvm-project/` | E12 LLD / E17 / E18 实证 |

---

## 12. 执行状态（2026-07-07 全部完工）

### ✅ 已完成（25/25 视角）
- **阶段 0**：摸清 5 个本地资源（4 个 LLVM fork/recipe/ports + 1 个 phytvm TVM 后端）
- **阶段 0**：吃透飞腾项目宪法/样板/资源库
- **阶段 0**：oracle 战略评审完成（`oracle战略评审.md`）
- **项目宪法 v1.0**（本文件）
- **阶段 A**：7 Lens 全部完成（历史/Christensen/供应链/经济/反垄断/教育/国产化）
- **阶段 B**：E18 特异性锚点实测完成（5 清单，发现 NPU 编译绕过 LLVM）
- **阶段 C**：7 Expert 全部完成（E01-E07）
- **阶段 D**：4 Expert 全部完成（E08-E11，承载断层 ①）
- **阶段 E**：4 Expert 全部完成（E12-E15）
- **阶段 F**：3 Expert 全部完成（E16/E17/E18，承载断层 ⑤）
- **阶段 G**：全局整合完成（CODE_INDEX/审计报告/Views/README 全更新）

### 🎉 项目完工
- 25 视角全部达标
- 总产出 ~1.34MB / ~44 万字
- 5 个服务器命脉级断层全部承载
- git commit: `872177d`（最终清理）← `a39bf5d`（README 完工横幅）← `9dbcf3f`（25/25 完成）← `8ab719c`（24/25）← `dc53cb6`（资源库 + 7 视角）

---

📌 **下一步**：按阶段 A→G 顺序并行执行。每个执行者必须先读本文件 + `oracle战略评审.md` + 对应的飞腾项目 Expert（如 E08 必读飞腾 Expert_11）。
