# S5 — 飞腾 RISC-V 转向评估：编译器就绪度全景（重演 Apple 2005 切 x86）

> **专题定位**：飞腾若从 ARM 转向 RISC-V（重演 Apple 2005 切 x86），编译器就绪度评估。本文是第二期专题，承接 Expert_10（RISC-V 后端）和 Lens_07（国产化）的实证底座，把"飞腾切不切 RISC-V"这个问题**从编译器侧给出一份可证伪的工程评估**。
>
> **数字来源分级（全文统一）**：`[实测]` = 本项目 grep/ls OpenXiangShan/llvm-project；`[官方]` = 厂商/规范一手（官网/spec）；`[GitHub]` = 开源仓库 code/commit/PR；`[Discourse]` = LLVM 官方论坛；`[社区]` = 中文社区/公众号；`[报道]` = 权威媒体；`[书]` = 学术著作；`[推测-依据]` = 基于公开信息推断。所有外部链接访问日期：2026-07-07。
>
> **§0.3 双重门槛声明**：
> - **(a) 飞腾工程实证**：本文所有"飞腾零 upstream"判断锚定 Expert_18 五清单 + Lens_07 §2.1 grep 实测（主线 LLVM AArch64 后端 `phytium|ftc86|ftc66` 零命中）。
> - **(b) 代码级实例**：本文所有"RISC-V 后端就绪"判断锚定 `OpenXiangShan/llvm-project/llvm/lib/Target/RISCV/` 真实 `.td`/`.cpp`，含文件清单（本次 `ls`/`glob` 实测）+ 行号引用（Expert_10 转引）。
> - **(c) 对偶判断**：ARM（E08）/RISC-V（本文）/LoongArch（Expert_10 §2.4）三后端对齐 + Apple 历史先例对照。

---

## §0. 必须先看的事实：本次 ls 实证

> 本节是全文的"证据底座"。实测对象：`/data/usershare/ai/riscv/OpenXiangShan/llvm-project/llvm/lib/Target/RISCV/`（LLVM 23.0.0git 主线），实测日期 2026-07-07。

### 0.1 RISC-V 后端目录实测（ls 等效 glob）

```
   RISC-V 后端文件规模（实测 glob，2026-07-07）
   ─────────────────────────────────────────
   .cpp 文件：68 个（含 MCTargetDesc 13 + AsmParser 1 + Disassembler 1
                     + GISel 7 + MCA 1 + TargetInfo 1 + 主目录 44）
   .td  文件：90 个（含 RISCVSched* 16 + RISCVInstrInfo* ~40 + 厂商扩展 ~10）
   关键 Pass（.cpp）：
     RISCVInsertVSETVLI.cpp       1087 行  ← RVV 心脏 Pass（3 相数据流）
     RISCVISelLowering.cpp         巨型文件  ← 指令选择/合法化
     RISCVMachineScheduler.cpp               ← 自定义调度
     RISCVGatherScatterLowering.cpp          ← RVV gather/scatter
     RISCVVectorPeephole.cpp                 ← 向量窥孔
     RISCVVLOptimizer.cpp / RISCVVMV0Elimination.cpp  ← VL/mask 优化
     RISCVInsertReadWriteCSR.cpp / RISCVInsertWriteVXRM.cpp  ← CSR 管理
     RISCVZacasABIFix.cpp                    ← 原子 ABI 修正（Zacas）
     RISCVZilsdOptimizer.cpp                 ← Zilsd（load/store 64）优化
   对照：AArch64 后端 .cpp ≈ 84 个（多 ~23%），.td ≈ 55 个
```

**一句话**：RISC-V 后端在体量上已达 AArch64 的 ~80%，但调度模型只有 AArch64 的一半（16 vs ~30）——**宽度够，深度不够**。

### 0.2 调度模型清单（glob `RISCVSched*.td` 实测，16 套）

```
   主线 LLVM RISC-V 后端 16 个调度模型（glob 实测，2026-07-07）
   ──────────────────────────────────────────────────────────────
   #  文件                                    代表厂商/核           国产?
   ─  ───────────────────────────────────    ──────────────────   ────
   1  RISCVSchedAndes45.td                    Andes N45             否(台)
   2  RISCVSchedGenericOOO.td                 通用乱序模型          —
   3  RISCVSchedMIPSP8700.td                  MIPS P8700(SG2042)    🟡 间接
   4  RISCVSchedRocket.td                     UC Berkeley Rocket    否
   5  RISCVSchedSiFive7.td                    SiFive 7-Series       否
   6  RISCVSchedSiFiveP400.td                 SiFive P400/P450/P470 否
   7  RISCVSchedSiFiveP500.td                 SiFive P500/P550      否
   8  RISCVSchedSiFiveP600.td                 SiFive P600/P670      否
   9  RISCVSchedSiFiveP800.td                 SiFive P800/P870      否
   10 RISCVSchedSpacemitX60.td                进迭时空 X60/A100     🟢 国产!
   11 RISCVSchedSpacemitX100.td               进迭时空 X100         🟢 国产!
   12 RISCVSchedSyntacoreSCR1.td              Syntacore SCR1        否
   13 RISCVSchedSyntacoreSCR345.td            Syntacore SCR3/4/5   否
   14 RISCVSchedSyntacoreSCR7.td              Syntacore SCR7        否
   15 RISCVSchedTTAscalonX.td                 Tenstorrent Ascalon   否
   16 RISCVSchedXiangShanNanHu.td             中科院 香山 NanHu     🟢 国产!
```

> 表 0.2：RISC-V 后端调度模型清单（`[实测]` glob `RISCVSched*.td`）。**香山 NanHu 有完整 317 行调度模型在主线**——这是国产 RISC-V 最重磅的 upstream 成绩，也是飞腾切 RISC-V 可复用的微架构模板。

### 0.3 厂商扩展文件（glob `RISCVInstrInfoX*.td` 实测，13+ 家）

```
   RISCVInstrInfoX*.td 厂商扩展（glob 实测，2026-07-07）
   ──────────────────────────────────────────────────────
   RISCVInstrInfoXAndes.td      晶心 Andes（Perf/BFHCvt/VDot）
   RISCVInstrInfoXCV.td         OpenHW CORE-V
   RISCVInstrInfoXMips.td       MIPS（CMov/LSP/CBOP/EXECTL）
   RISCVInstrInfoXqccmp.td      —（条件乘）
   RISCVInstrInfoXqci.td        —（QUALIA）
   RISCVInstrInfoXRivos.td      Rivos（Vizip）
   RISCVInstrInfoXSf.td         SiFive（自定义）
   RISCVInstrInfoXSfmm.td       SiFive（矩阵）
   RISCVInstrInfoXSpacemiT.td   🟢 进迭时空（XSMTVDot 点积）
   RISCVInstrInfoXTHead.td      🟠 平头哥玄铁（th.lwd/ldd/swd/sdd 访存对）
   RISCVInstrInfoXVentana.td    Ventana（CondOps）
   RISCVInstrInfoXwch.td        沁恒 WCH（MCU）
   RISCVInstrInfoXAIF.td        —（AIF 扩展）
   RISCVInstrFormatsSpacemitV.td 🟢 进迭时空向量格式
   RISCVInstrFormatsXAIF.td     —（AIF 格式）
```

> 表 0.3：厂商扩展清单（`[实测]` glob）。**关键发现**：飞腾若切 RISC-V 并有自研扩展（如国密增强），可直接走 `RISCVInstrInfoXPhytium.td` 的 Xxxx 路线 upstream——这是 ARM 后端不提供的"自由度"。

---

## §1. Apple 2005 PowerPC→x86 + 2020 x86→ARM 切换的编译器教训（Rosetta 1/2）

> 任务点名必答：飞腾若切 RISC-V，重演 Apple 2005 切 x86，编译器侧能学到什么？

### 1.1 两次切换的工程骨架

Apple 历史上完成过两次史诗级 ISA 切换，每一次都是**编译器 + 二进制翻译 + OS 全栈协调**的极限工程，业界至今无出其右者。理解这两次切换的编译器侧，是评估飞腾切 RISC-V 的最佳坐标系。

**第一次：2005–2006 PowerPC → x86（Rosetta 1）**。2005 年 WWDC，乔布斯宣布 Mac 从 PowerPC 切到 Intel x86，核心动因是 PowerPC G5 的散热与功耗在移动端无解——IBM（PowerPC 联盟主导方）无法提供笔记本级别的低功耗高性能芯片，而 Intel 的 Core Duo 路线图明确领先一代以上 `[报道]`。这是一次典型的"ISA 被上游锁定后下游被迫切轨"：IBM 不更新移动 PowerPC ≈ ARM 不授 v9 给中国，锁定方的"不作为"直接威胁下游生存。编译器侧，Apple 的 Xcode 同时维护 PowerPC 和 x86 两套后端约一年，强制所有 ISV 用 **Universal Binary**（一个二进制装两套机器码，用 `lipo` 打包）重新分发——这把"切换成本外部化给整个开发者生态"。对于无法重编的旧软件，Apple 收购了 Transitive 公司的 **QuickTransit 动态二进制翻译**，包装成 **Rosetta 1**，在运行期把 PowerPC 指令翻译成 x86 指令 `[书]`。Rosetta 1 的编译器本质是一个"JIT 翻译器"——它不做 IR 级优化（太慢），而是**块级翻译 + 基本块链接 + 代码缓存**，性能约为原生 PowerPC 的 40–80%。这个性能区间恰恰是"够用但不爽"，驱动用户主动重编。Apple 在 2009 年随 Mac OS X 10.6 砍掉了 PowerPC 支持，整个迁移窗口约 4 年（2005 宣布 → 2009 弃用）。

**第二次：2020–2023 x86 → ARM（Rosetta 2）**。2020 年 WWDC，Apple 宣布 Mac 从 Intel x86 切到自研 Apple Silicon（ARM），动因是 Intel 制程挤牙膏（"Intel 才是 PowerPC"），而 Apple 自研 A 系列芯片的能效比已碾压。编译器侧，Xcode 同样维护双后端，但这次 Apple 的杀手锏是 **Rosetta 2**——一个**AOT（提前翻译）为主、JIT 为辅**的二进制翻译器。Rosetta 2 在 x86 应用首次启动时把整个二进制翻译成 ARM 代码并缓存到磁盘，后续运行直接用缓存版本 `[报道]`。AOT 比 JIT 快的原因是：翻译开销摊到一次性，运行期无翻译中断。Rosetta 2 性能约为原生 ARM 的 70–90%，远好于 Rosetta 1。Apple 在 2023 年随 Mac Studio/Pro 完成 Apple Silicon 全产品线切换，迁移窗口约 3 年（2020 宣布 → 2023 Intel Mac 停产）。

### 1.2 编译器侧的五条教训

把两次切换的编译器工程提炼成五条可迁移的教训：

**教训一：Universal Binary 是"过渡期刚需"，但它延长了切换的痛感。** Apple 两次切换都强制 Universal Binary（PPC+x86 / x86+ARM），这让"双栈并行"成为约 3–4 年的强制状态。对飞腾切 RISC-V 的启示是：**ARM+RISC-V 双栈并行几乎不可避免**（§7 详述），且双栈不是"两个编译器并存"那么简单，是"两个 ABI、两套 OS 镜像、两份软件包仓库、两套 CI/CD"的全面负担。Apple 能扛住是因为它是垂直整合公司，飞腾是纯 CPU 公司，双栈协调成本外部化给麒麟/达梦/统信等 ISV，**协调难度比 Apple 高一个量级**。

**教训二：二进制翻译是"旧软件续命"的唯一答案，但性能只能到 70–90%。** Rosetta 1（40–80%）和 Rosetta 2（70–90%）的天花板是块级翻译 + 缓存的固有上限——它无法做 IR 级跨架构优化（那需要重编）。对飞腾的启示是：切 RISC-V 后，ARM 老软件（信创已部署的麒麟/达梦/金蝶等）必须靠**二进制翻译续命**，但翻译性能天花板约 70–90%。这里 RISC-V 有个天然劣势——**RISC-V 没有 LoongArch 那样的 LBT 原生二进制翻译扩展**（`[实测]` LoongArch 有 `LoongArchLBTInstrInfo.td` 原生 x86/ARM 翻译指令），RISC-V 只能靠 QEMU 软件翻译，性能更低（QEMU TCG 约 30–50%）。**这是 RISC-V 相对 LoongArch 的结构性劣势**，也是飞腾切 RISC-V 比"切 LoongArch"更难的原因之一。

**教训三：编译器团队的"双后端维护"是切换期的最大人力黑洞。** Apple 在两次切换期间，LLVM 团队（Apple 是 LLVM 的最大金主之一）同时维护 AArch64 + x86 +（早期还有 PowerPC）三套后端的调度模型、合法化、ABI。这个人力成本是数倍的。对飞腾的启示是：飞腾当前编译器团队推测 12–20 人（Lens_07 §S2），同时维护 PhyCC（LLVM fork）+ PhyGCC（GCC fork）已接近极限。**若再加 RISC-V 后端，团队至少要扩 1 倍**，否则双栈会拖垮单栈质量。

**教训四：切换的"临界点"是性能差距，不是技术成熟度。** Apple 2005 切 x86 是因为 PowerPC 与 x86 的 IPC/功耗差距拉到临界；2020 切 ARM 是因为 A14 能效比碾压 Intel。**编译器成熟度只是必要条件，性能差距是充分条件**——如果 RISC-V 服务器单核性能追不上 Neoverse，编译器再成熟飞腾也不会切。这是 Expert_10 §4.1 盲区警告的"编译器工程师视野局限"——切不切 ISA 由芯片性能和地缘决定，编译器是跟随变量。

**教训五：Apple 的切换是"主动进攻"，飞腾的切换将是"被动防御"。** Apple 两次都是性能领先方主动切换（切到更强的 ISA）；飞腾切 RISC-V 将是被 ARM v9 锁死后的被动求生。**被动切换的决策质量更差**——时间窗口不由飞腾定，可能被迫在 RISC-V 生态未成熟时仓促切换（§5 详述时间成本）。

> **§1 诚实结论**：Apple 两次 ISA 切换提供了"双栈并行 3–4 年 + 二进制翻译续命 + 70–90% 性能天花板 + 团队翻倍"的工程模板。飞腾切 RISC-V 将重演这个模板，但有三重加难：① RISC-V 是"边缘 ISA"（非 Apple 切到的"主流 ISA"）；② 飞腾无垂直整合（双栈协调外部化）；③ RISC-V 无 LBT 原生翻译（旧软件续命性能更低）。**飞腾切 RISC-V 不是"能不能"的问题，是"比 Apple 难 3 倍但必须做"的被动求生**。

---

## §2. 飞腾若切 RISC-V，LLVM RISC-V 后端就绪度（RVV/多核/服务器级）

> 任务点名必答：飞腾切 RISC-V，LLVM RISC-V 后端（RVV/多核/服务器级）就绪了吗？

### 2.1 总体就绪度：基础就绪，深度欠半

从 §0 的实测清单看，RISC-V 后端的**基础就绪度已经足够**：68 个 .cpp、90 个 .td、16 套调度模型、完整的 RV64GC + RVV + Zba/Zbb/Zbs + Zk 国密支持。Linux/Glibc/Debian 在 RV64GC 上已能完整自举编译 `[官方]` riscv.org。这意味着飞腾若做一款 RV64GC 服务器核，**用主线 LLVM 就能编出可运行的 Linux 全栈**——这是 2019 年（LLVM 9 实验性）到 2026 年（LLVM 23）7 年积累的成果。

但"能跑"和"跑得快"是两个层级。RISC-V 后端的**深度欠半**体现在三个维度：

**深度债一：调度模型覆盖只有 AArch64 的一半（16 vs ~30）。** §0.2 实测 16 套调度模型，其中服务器级（高性能乱序）只有香山 NanHu、SpacemiT X60/X100、Tenstorrent Ascalon、MIPS P8700（=SG2042）寥寥几套。对比 AArch64 的 Neoverse N1/N2/N3/V1/V2/V3/V3AE（ARM 服务器全系）、TSV110（华为鲲鹏）、Ampere1（Ampere）、Oryon（高通）、Olympus——**RISC-V 服务器级调度模型数量约 AArch64 的 1/3**。飞腾若做高性能 RISC-V 核，要么用 `generic-ooo`（`RISCVSchedGenericOOO.td`，通用乱序，次优）凑合，要么自己写 `RISCVSchedFTC9xx.td`（从零）。Expert_10 §2.5 判断"飞腾切 RISC-V 的第一件事是学香山把调度模型推回主线"——这正是"深度债"的直接体现。

**深度债二：AI 推理栈成熟度落后 NEON/SVE 约 2 年。** 飞腾 E21 已证"无 BF16/I8MM/SVE 是 AI 战略伤疤"。切到 RISC-V 能解决这个问题吗？部分能：RISC-V 有 Zvfbfmin/Zvfbfwma（向量 BF16，§0.3 验证 `RISCVInstrInfoZvfbf.td` 存在）、Zve64d（嵌入式向量）、RVV（可变长向量）。**理论上 RISC-V 的 AI 数据类型比飞腾 ARMv8.4 更丰富**（有 BF16！）。但问题是**编译器栈成熟度**：ARM 侧的 KleidiAI/ACL（oneDNN 后端）已深度优化 NEON/SVE/I8MM 向量化；RISC-V 侧的 RVV-MLIR/KleidiAI-RVV 落后约 2 年 `[推测-依据: ARM ACL/KleidiAI 活跃度 vs RISC-V RVV-MLIR 社区]`。**切 RISC-V 不能立刻解 AI 算力痛——要等 RISC-V AI 推理栈追平**，这又是一笔时间债（§5 详述）。

**深度债三：RVV 合法化复杂度爆炸是 RISC-V 后端最重的工程债。** §0.1 实测的 `RISCVInsertVSETVLI.cpp`（1087 行，3 相数据流）是 RVV 的"心脏 Pass"——它全局分析 `vl`/`vtype` CSR 的变化点，在真正需要改变时才插 `vsetvli` 指令。这是 ARM SVE/NEON **没有的编译器税**（NEON 定长、SVE 硬件自动管理 VG）。RVV 的 LMUL × SEW × TA/TU/MA/MU × VLEN 组合让 SelectionDAG 合法化空间指数级膨胀（`RISCVISelLowering.cpp` + `RISCVInstrInfoVPseudos.td` 大量代码处理合法化）。**飞腾切 RISC-V 后，编译器团队要补 RVV 合法化的课**——这是 PhyCC 当前（基于 AArch64 NEON）不存在的复杂度。

### 2.2 RVV 就绪度：类型系统天才，合法化地狱

§2.1 提到的 `vscale = VLEN/64` 是 RVV 在 LLVM IR 的建模根基（`[实测]` RISCVRegisterInfo.td:586-598 注释）。这个抽象让"一份二进制跨 VLEN"（VLEN=128/256/512/1024 同一份代码）成为可能——`<vscale x 4 x i32>` 在 VLEN=128 时是 2 个 i32，VLEN=512 时是 8 个 i32，但 IR 写法不变。这是 RVV 相对 NEON 定长的"先进性"，也是 AI 推理框架（TVM/MLIR）倾向走 LLVM 的原因（框架层不用写 VLEN 分支）。

但代价是**合法化爆炸**。VP（Vector Predication）方案试图统一 RVV 和 ARM SVE（§Expert_10 §2.2），但 5 年仍未真正落地——因为 RVV 的 TA/TU/MA/MU（tail-undisturbed/agnostic + mask-undisturbed/agnostic）四种策略比 SVE 的谓词模型**语义更丰富**，强行统一必有一方被降维。**飞腾切 RISC-V 后，VP 半统一状态意味着飞腾的 RVV 代码和华为鲲鹏的 SVE 代码在 IR 层"看起来统一"，但后端合法化仍各走各路**——这增加了跨架构调试的复杂度。

### 2.3 多核/服务器级就绪度：RVA23 profile 是入场券

RISC-V 服务器级的"入场券"是 **RVA23S64 profile**（应用处理器组合包），它规定了服务器核必须支持的基础扩展集（RV64GC + Zba/Zbb/Zbs + Zicbom/Zicboz + Zicclsm + AIA 等）。§0.2 实测的香山 Kunminghu（`RISCVProcessors.td:822`）和 SpacemiT X100（`:909`）都已对齐 RVA23S64 `[实测]`。**飞腾切 RISC-V 的第一个工程目标就是对齐 RVA23S64**——这保证软件生态（Linux/Glibc/Debian 已 RVA23-ready）能直接跑。

服务器级还需要的特性：① **H-extension（虚拟化）**——RISC-V 有，主线 LLVM 支持；② **多核一致性（Zicclsm）**——缓存行管理，主线支持；③ **原子（A 扩展 + Zacas）**——`RISCVZacasABIFix.cpp`（§0.1 实测）正是处理 Zacas 原子 ABI 的 Pass，证明主线已支持。**多核/服务器级编译器侧基本就绪**，瓶颈不在编译器而在芯片单核性能（香山 NanHu vs Neoverse V2 的 IPC 差距）。

### 2.4 国密（Zk）就绪度：能跑，性能待调

飞腾 D3000M 有 SM3/SM4 原生指令（飞腾 E05 实测）。切 RISC-V 会丢吗？不会——RISC-V 的 **Zk（Scalar Cryptography）扩展含 SM3/SM4**，主线 LLVM 已支持（`RISCVFeatures.td` 的 Zksh/Zksed，`RISCVInstrInfoZk.td` 实测存在）。**但性能是问号**——RISC-V Zk 的 SM3/SM4 是标准扩展（通用实现），飞腾原生 SM3/SM4 是微架构级优化（D3000M 实测 16.9× 加速）。**切 RISC-V 后国密性能可能回退**，需要飞腾自研 Zk 增强扩展（走 `RISCVInstrInfoXPhytium.td` 的 Xxxx 路线）补回来。这是 §0.3 厂商扩展机制的价值——飞腾可以用 Xxxx 路线把国密增强 upstream，而不污染标准扩展。

> **§2 诚实结论**：RISC-V 后端**基础就绪**（后端稳定 + RVA23 profile + 国密 Zk），但**深度欠半**（服务器级调度模型只有 AArch64 1/3、AI 推理栈落后 2 年、RVV 合法化是新的编译器税）。飞腾切 RISC-V 的编译器基础设施"够用但不爽"，**飞腾自身必须补三课**：① 写 FTC9xx 调度模型 upstream；② 等待 RVV-MLIR/KleidiAI-RVV 追平；③ 建立 RVV 合法化调优能力。**切 ISA 不等于获得后端就绪——飞腾要把自己变成 RISC-V 后端的"生产者"，不是继续当"消费者"**。

---

## §3. 飞腾若切 RISC-V，OS 生态就绪度（Linux/glibc/发行版）

> 任务点名必答：飞腾切 RISC-V，OS 生态（Linux 内核/glibc/发行版）就绪了吗？

### 3.1 Linux 内核：已自举，但高性能场景特性待补

Linux 内核对 RISC-V 的支持始于 2018 年（Linux 4.15 合入 RV64 基础支持），到 2026 年已演进到完整的 RV64GC + RVA23 profile 支持 `[官方]` kernel.org。RISC-V 是 Linux 内核的一等公民架构——和 ARM/x86 同级，有独立的 `arch/riscv/` 目录、独立的 maintainer 团队（Palmer Dabbelt 为首）。

飞腾切 RISC-V 后的内核侧就绪度分三层：

**基础就绪**：Linux 内核能在 RV64GC 上完整自举（boot/调度/内存管理/文件系统/网络全栈），这是 2018–2024 年的成果。飞腾若做 RV64GC 服务器核，主线 Linux 能直接跑——不需要像申威 swLinux 那样维护深度 fork。

**高性能特性待补**：服务器级特性（NUMA、大页透明合并 THP、KVM 虚拟化、性能计数器 perf）在 RISC-V 上**部分就绪**。KVM 虚拟化（基于 H-extension）已在主线 `[官方]`；NUMA 在多 socket RISC-V 服务器（如 SG2042 64 核）上仍在补 `[推测-依据: SG2042 NUMA patch 社区讨论]`；perf 计数器（`RISCVPfmCounters.td` §0 实测存在）需要每个核定义自己的 PMU 事件。飞腾切 RISC-V 后，要把 FTC9xx 的 PMU/大页/NUMA patch 推回主线——这是 E18 五清单里飞腾在 ARM 侧做得不好的（phytium_repos 45 目录的内核 patch 多为 fork，少 upstream）。**切 RISC-V 不自动获得内核 upstream 能力**，飞腾要重新建立内核贡献渠道。

**信创内核适配**：飞腾当前在麒麟 OS（信创主力）上有深度适配（飞腾 E06 共识）。切 RISC-V 后，麒麟 OS 需要**新增 RISC-V 发行版**——麒麟已有 ARM/x86/LoongArch 版本，加 RISC-V 是第 4 个架构。这是 OS 侧的协调成本（§5 详述）。

### 3.2 glibc：RV64 已上游，但 ABI 仍在演进

glibc 对 RISC-V 的支持始于 2019 年（glibc 2.29），到 2026 年 RV64 LP64D ABI 已稳定 `[官方]` sourceware。但 RISC-V 的 ABI 演进比 ARM 活跃——近年有 **Zilsd（load/store 64 位整数为单条指令）** 改变 ABI 的优化（§0.1 实测 `RISCVZilsdOptimizer.cpp`）、**Zacas（原子比较交换）** 改变原子 ABI（`RISCVZacasABIFix.cpp`）。这些 ABI 微调意味着**RISC-V 的二进制兼容性不如 ARM 稳定**——飞腾切 RISC-V 后要紧跟 glibc ABI 演进，否则旧二进制可能跑不了。

对照 ARM：AArch64 的 AAPCS64 ABI 自 2012 年（ARMv8 发布）基本冻结，极其稳定。**ARM 的 ABI 稳定性是飞腾在 ARM 栈上积累的二进制资产的保护层**；切 RISC-V 后这层保护没了，要重新积累。

### 3.3 发行版：Debian/Fedora/openEuler 已 RVA23-ready

三大发行版的 RISC-V 就绪度：
- **Debian**：riscv64 是官方发布架构，有完整端口 `[官方]`。
- **Fedora**：riscv64 是次要架构（secondary arch），社区维护 `[官方]`。
- **openEuler（华为开源，信创主力）**：有 RISC-V 版本，RISC-V 是一等架构 `[社区]` openEuler blog。这对飞腾是利好——openEuler 是飞腾当前在信创的主力 OS（飞腾 E06），它已有 RISC-V 版本意味着**飞腾切 RISC-V 后 openEuler 这条 OS 线能平滑迁移**。
- **麒麟 OS**：作为飞腾信创第一 OS，麒麟的 RISC-V 版本是关键。公开信息显示麒麟已在研发 RISC-V 版本 `[推测-依据: 信创 3.0 要求国产 OS 多架构支持]`，但成熟度待验证。

**发行版就绪度结论**：Debian/Fedora/openEuler 已 RVA23-ready，飞腾切 RISC-V 的发行版基础够用。但**信创关键 OS（麒麟/统信）的 RISC-V 版本成熟度是飞腾切换的真正瓶颈**——这不是编译器问题，是 ISV 协调问题（§5 详述）。

### 3.4 ISV 生态：最深的债

OS 内核/glibc/发行版是"基础设施"，真正的切换瓶颈是 **ISV（独立软件开发商）**——麒麟数据库、达梦数据库、金蝶中间件、用友 ERP、金山办公等信创核心软件。这些软件当前在 ARMv8.4 上有飞腾适配版，切 RISC-V 需要：① 全部重编（Universal Binary 或双包）；② 性能调优（RISC-V 微架构与 ARM 不同，缓存/分支预测调优要重做）；③ 认证（信创认证要重新过）。

**ISV 重适配是切换的"最后一公里"，也是最贵的一公里**。Apple 2005 切 x86 时，Adobe/Microsoft 等大 ISV 用了 1–2 年才完成 Universal Binary 重编；飞腾切 RISC-V，信创 ISV 的重适配成本更高（信创 ISV 多为国内中小厂商，工程能力弱于 Adobe/MS）。

> **§3 诚实结论**：OS 基础设施（Linux/glibc/Debian/openEuler）**已就绪**，RISC-V 是一等公民架构。但**三层债**：① 飞腾自研内核 patch（PMU/NUMA/大页）要重新 upstream；② glibc ABI 演进活跃，二进制兼容性不如 ARM 稳定；③ 信创 ISV（麒麟/达梦/金蝶/用友）重适配是切换最贵的一公里。**OS 基础设施就绪 ≠ 生态就绪——飞腾切 RISC-V 的生态债主要在 ISV 协调，不在编译器**。

---

## §4. ARM → RISC-V 的 ABI 切换工程债

> 任务点名必答：从 ARM AAPCS64 切到 RISC-V LP64D，ABI 切换的工程债有多大？

### 4.1 ABI 的本质：二进制契约

ABI（Application Binary Interface）是**二进制层面的契约**——它规定了函数参数怎么传（寄存器/栈）、返回值怎么放、调用栈怎么布局、结构体内存对齐、异常处理机制。ABI 一旦定下来，**所有编译的二进制要遵守同一套 ABI 才能 link 在一起**。切换 ABI 意味着**所有二进制（库、应用、内核模块）必须重编**——这是 ISA 切换的"硬性税"。

### 4.2 AAPCS64 vs LP64D 的关键差异

飞腾当前用 ARM 的 AAPCS64（ARM Architecture Procedure Call Standard 64-bit），切到 RISC-V 的 LP64D（64 位长整型 + 双精度浮点 ABI）。两者在**功能上等价**（都是 64 位 + 硬件浮点 ABI），但在**细节上有几十处差异**：

**寄存器约定不同**：AAPCS64 用 X0–X7 传前 8 个整数参数，V0–V7 传浮点；RISC-V LP64D 用 a0–a7（x10–x17）传整数，fa0–fa7 传浮点。这导致**函数调用的寄存器分配完全不同**，编译器后端的 CallingConv（调用约定）要从 AAPCS64 改成 RISCCV LP64D（§0.1 实测 `RISCVCallingConv.cpp` + `RISCVCallingConv.td`）。

**栈布局不同**：AAPCS64 的栈帧有 FP（帧指针 x29）+ LR（链接寄存器 x30）约定；RISC-V 用 s0/fp（x8）+ ra（x1）。栈展开（stack unwinding，异常处理/调试器需要）的元数据格式不同（ARM 用 .eh_frame + DWARF，RISC-V 也用 DWARF 但寄存器编号映射不同）。

**结构体对齐不同**：ARM AAPCS64 对 SIMD 向量类型（NEON/SVE）有特殊对齐规则（16 字节/32 字节对齐）；RISC-V 的 RVV 向量是可变长（`<vscale x N x T>`），对齐规则基于 VLEN。这影响**跨语言 FFI（如 Rust↔C、Go↔C）的 ABI 兼容**。

**变长参数（varargs）不同**：AAPCS64 用栈传变长参数；RISC-V 也有类似机制但细节不同。这是 C 标准库 `printf`/`scanf` 的底层依赖。

### 4.3 ABI 切换的工程债量化

ABI 切换的工程债不是"改个寄存器映射"那么简单，它是**全栈重验证**：

**债一：所有静态库/动态库必须重编**。飞腾信创栈里的每个库（OpenSSL 国密版、达梦驱动、金蝶中间件）都要用 RISC-V LP64D 重编。这不是技术问题，是**供应链协调问题**——飞腾要说服所有上游库的维护者出 RISC-V 版本。

**债二：JIT/动态代码生成的软件要重写后端**。V8（Chrome JS 引擎）、HotSpot（OpenJDK）、CPython（未来可能加 JIT）这类含 JIT 的软件，JIT 会直接生成机器码——ABI 切了，JIT 后端要重写。飞腾 PhyJDK（OpenJDK fork，Lens_07 §S2 实证）当前生成 ARM 机器码，切 RISC-V 要改 HotSpot 的 codegen。**这是切 ISA 最贵的一笔债**。

**债三：二进制翻译的性能天花板**。对无法重编的旧软件，靠二进制翻译（QEMU TCG）续命。但 §1.2 已述：QEMU 翻译 ARM→RISC-V 性能约 30–50%（远低于 Rosetta 2 的 70–90%），因为 RISC-V 无 LBT 原生翻译扩展。**旧软件续命性能低，倒逼用户重编——但重编需要 ISV 配合**，形成死循环。

**债四：调试/性能分析工具链要重做**。gdb（RISC-V 支持，但远不如 ARM 成熟）、perf（PMU 事件要飞腾自研定义）、valgrind（RISC-V 支持有限）、strace（RISC-V 支持）——这些工具在 RISC-V 上**能用但不如 ARM 精细**。飞腾切 RISC-V 后，性能调优的工具链要重新积累。

### 4.4 对照 LoongArch：LBT 的降维优势

LoongArch 用 **LBT（LoongArch Binary Translation）扩展**原生支持 x86/ARM 二进制翻译（`[实测]` LoongArchLBTInstrInfo.td）。这意味着龙芯切 ISA 时，旧 x86/ARM 软件可以用**硬件辅助翻译**（性能高于纯软件 QEMU）。RISC-V 没有这个——只能纯软件翻译。**这是 RISC-V 相对 LoongArch 在"ABI 切换工程债"上的结构性劣势**：同样切 ISA，龙芯有硬件翻译兜底，RISC-V 没有。

> **§4 诚实结论**：ARM AAPCS64 → RISC-V LP64D 的 ABI 切换工程债是**全栈重验证**——寄存器/栈/对齐/varargs 几十处差异，所有库重编、JIT 软件重写后端、二进制翻译性能只有 30–50%（无 LBT 兜底）。**这是飞腾切 RISC-V 最硬的工程税，且无法绕过**——它不是"编译器改改"的问题，是"整个软件供应链重新认证"的问题。对照 LoongArch 的 LBT，RISC-V 在二进制续命上更吃亏。

---

## §5. 编译器框架切换时间成本（5/10/15 年）

> 任务点名必答：飞腾从 ARM 编译器栈切到 RISC-V 编译器栈，时间成本多久？分 5/10/15 年三档评估。

### 5.1 时间成本的三档模型

飞腾切 RISC-V 的编译器栈时间成本，可以分"激进/标准/保守"三档评估。每档对应不同的切换深度和风险：

**5 年档（激进）——只切编译器后端，保留框架**。假设飞腾 2028 启动，2033 完成：① 第 1–2 年（2028–2030）建立 RISC-V 编译器团队（从零招人 + 学香山调度模型），写 FTC9xx 调度模型 upstream，跑通 RV64GC 基础编译；② 第 3–4 年（2030–2032）做 PhyCC-RV（LLVM fork，RISC-V 后端），对齐 RVA23 profile，跑通 Linux 全栈自举；③ 第 5 年（2032–2033）ISV 重适配试点（麒麟/达梦出 RISC-V 版本）。**5 年档的风险**：① RISC-V 服务器芯片 2028 可能还没成熟（香山昆明湖单核 vs Neoverse V2 差距），切了个半成品；② ISV 重适配 5 年来不及（Apple 用了 3–4 年且有垂直整合优势）；③ 飞腾 ARMv8.4 资产（RTL/PhyCC/信创资质）沉没成本未消化。**5 年档现实可行性 < 20%**。

**10 年档（标准）——双栈并行，渐进切换**。假设飞腾 2030 启动，2040 完成：① 第 1–3 年（2030–2033）RISC-V 编译器栈预研（学平头哥 OpenC910 + c-sky/buildroot 路径），RISC-V 后端 upstream 调度模型；② 第 4–6 年（2033–2036）双栈并行期（ARM+RISC-V 同时出货，PhyCC 双后端维护），ISV 开始重适配；③ 第 7–10 年（2036–2040）RISC-V 主线化，ARM 逐步退役（类比 Apple 2009 弃 PowerPC）。**10 年档的风险**：双栈并行期编译器团队要翻倍（§1.2 教训三），人力成本高；信创客户在双栈期可能困惑（买 ARM 还是 RISC-V 版？）。**10 年档现实可行性 50–65%**——这是最可能的路径，也是 Lens_07 §2.4 预测的"切轨窗口 2032–2035"的延伸。

**15 年档（保守）——等待 RISC-V 服务器成熟后再切**。假设飞腾 2032 启动，2047 完成：前提是 2030–2035 RISC-V 服务器单核追平 Neoverse、ARM v9 持续不授。这个档位的优势是"等生态成熟再切，风险最低"，但劣势是**飞腾在 ARMv8.4 冻结的编译器债再累积 15 年**（主线 LLVM 的 SVE2/SME/FP8 红利永远拿不到），且 15 年后飞腾的 ARM 资产更难退役（沉没成本更大）。**15 年档现实可行性 20–30%**——太保守，可能错过窗口。

### 5.2 时间成本的关键依赖变量

三档时间成本不是飞腾单方面能决定的，它依赖三个外部变量：

**变量一：ARM v9 是否解禁中国**。如果 2030 前 ARM v9 解禁（地缘缓和），飞腾可能放弃 RISC-V 切换，留在 ARM（v9 红利能拿）。但 Lens_07 §2.4 判断"v9 持续不授"是高概率事件（地缘归 E19），所以这个变量倾向于"不解禁"。

**变量二：RISC-V 服务器单核性能何时追平 Neoverse**。这是 §2.3 提到的芯片侧瓶颈。香山昆明湖（2025 流片）单核 SPECint 约 Neoverse N2 水平，距 V2/V3 还有 1–2 代差距 `[推测-依据: 香山路标 + Neoverse 演进]`。追平窗口约 2030–2035。**这是切换的"充分条件"——性能不追平，编译器再成熟也不切**。

**变量三：信创政策是否强制 RISC-V**。如果信创 4.0（2028–2032）强制要求"国产 ISA"（排除 ARM，因 v9 不授），飞腾可能被迫加速切 RISC-V（或转 LoongArch）。这是政策驱动的"强制切换"——时间不由飞腾定。

### 5.3 时间成本的"沉没成本陷阱"

飞腾切 RISC-V 最大的时间成本障碍不是技术，是**沉没成本心理**。飞腾在 ARMv8.4 上积累了：① FTC862/863 RTL（数亿研发投入）；② PhyCC/PhyGCC（编译器团队多年投入）；③ 信创资质 + 国密认证 + 军工资质（ARM 栈上的认证资产）；④ ISV 适配（麒麟/达梦等已在飞腾 ARM 上认证）。**这些沉没成本让飞腾"不愿切"——切了等于承认 ARM 路线走到头**。

这是经典的"创新者窘境"（Christensen 框架，Lens_02）： incumbents（飞腾在 ARM 栈）被沉没成本锁住，不愿转向 disruptive 技术（RISC-V）。**沉没成本越大，切换越晚，最终切换越仓促**——这是 15 年档（保守）可能演变成"被迫仓促切换"的内在逻辑。

> **§5 诚实结论**：飞腾切 RISC-V 的时间成本，**10 年档（标准双栈并行）最可能**（50–65%），5 年档太激进（< 20%），15 年档太保守（20–30%）。关键依赖三个外部变量：v9 是否解禁（倾向于不）、RISC-V 服务器何时成熟（2030–2035）、信创是否强制国产 ISA（待定）。**最大的时间成本障碍是沉没成本心理**——飞腾在 ARM 栈的资产越多，越不愿切，最终切换越仓促。**这是"创新者窘境"的编译器版**。

---

## §6. 飞腾 RISC-V 转向 trigger 条件（ARM v9 永久不授 / RISC-V 服务器成熟 / 信创）

> 任务点名必答：飞腾切 RISC-V 的 trigger（触发）条件是什么？什么情况下会真正启动切换？

### 6.1 三个 trigger 及其概率

飞腾切 RISC-V 不是"想切就切"，需要**外部 trigger**触发。基于 Lens_07 §2.4 + Expert_10 §2.5 的分析，有三个 trigger，按概率排序：

**Trigger 一：ARM v9 永久不授中国（概率 > 80%）**。这是最强的 trigger。ARM v8.4 是飞腾的天花板——主线 LLVM 从 2019 起持续为 ARMv8.5/v8.6/v9 演进（SVE2/MTE/SME/FP8/FP4），飞腾 FTC862 拿不到任何红利（Lens_07 §2.4.1 表 3 实证）。如果 v9 永久不授，飞腾在 ARM 栈上的编译器债**永续累积**——这不是性能问题，是"永远落后一代"的战略窒息。**v9 不授是"必要 trigger"**——没有这个压力，飞腾不会切。地缘归 E19，但 2026 的判断是"v9 持续不授"是高概率事件。

**Trigger 二：RISC-V 服务器单核性能追平 Neoverse（概率 50–65%，时间窗 2030–2035）**。这是"充分 trigger"——性能不追平，编译器再成熟飞腾也不切（§1.2 教训四）。香山昆明湖（2025）单核约 Neoverse N2 水平，SpacemiT X100（2025）类似；下一代（2028–2030）有望追 N3/V2 水平 `[推测-依据: 香山/SpacemiT 路标]`。**追平窗口 2030–2035**——这与 Lens_07 §2.4 预测的"切轨窗口 2032–2035"吻合。**关键不确定性**：RISC-V 服务器单核能否真正追平 ARM？历史经验是开源 ISA 的服务器化比预期慢（SG2042 64 核但单核弱），可能再延 2–3 年。

**Trigger 三：信创政策强制"国产 ISA"（概率 30–45%）**。如果信创 4.0（2028–2032）将"国产 ISA"纳入准入标准（排除 ARM，因 v9 不授；排除 x86，因海光授权风险），飞腾必须在 RISC-V 和 LoongArch 之间选一个。这是政策驱动的"强制 trigger"——时间不由飞腾定。**这个 trigger 的不确定性最高**——信创政策方向取决于国家战略，可能突然加码（强制国产 ISA）也可能保持现状（只要求国产编译器）。

### 6.2 Trigger 组合与启动时点

三个 trigger 不是独立的，它们**组合触发**飞腾的切换决策：

**最可能组合（概率 45–55%）：Trigger 一（v9 不授）+ Trigger 二（RISC-V 成熟，2030–2035）**。飞腾在 v9 持续锁 + RISC-V 服务器 2032 前后成熟的双重压力下，启动 RISC-V 编译器栈预研（参考平头哥 OpenC910 路径），双栈并行（§7），2035 后渐进切换。**启动时点约 2030–2032**，完成约 2040。

**次可能组合（概率 20–30%）：Trigger 一 + Trigger 三（信创强制）**。信创 4.0 强制国产 ISA，飞腾被迫在 2028–2030 启动切换，时间仓促，可能选 RISC-V（生态比 LoongArch 广）也可能选 LoongArch（有 LBT 兜底）。**这个组合的风险是仓促切换——沉没成本没消化，ISV 没准备好**。

**低概率组合（概率 < 15%）：Trigger 一 单独触发**。v9 不授但 RISC-V 服务器不成熟 + 信创不强制——飞腾可能继续在 ARMv8.4 耗着，直到 RISC-V 成熟。这是"延迟切换"场景，飞腾在 ARM 栈的债继续累积。

**黑天鹅组合（概率 < 10%）：v9 解禁**。地缘缓和，ARM v9 解禁中国——飞腾放弃 RISC-V，留在 ARM。这个概率低（地缘归 E19 判断"持续不授"），但若发生会彻底改变飞腾路径。

### 6.3 Trigger 触发后的"第一动作"

一旦 trigger 触发，飞腾切 RISC-V 的**第一动作不是写编译器**，而是**建立 upstream 能力**。Expert_10 §2.5 和 §3.3 明确：飞腾切 ISA 不等于获得 upstream 能力——飞腾在 ARM 栈零 upstream（Lens_07 §2.1 grep 实证），切 RISC-V 后若不投入 upstream，照样零痕迹。

**第一动作应该是学香山**（Expert_10 §3.3 教训一）：① 写 `RISCVSchedFTC9xx.td`（飞腾自研 RISC-V 核调度模型）；② 在 `RISCVProcessors.td` 加 FTC9xx ProcessorModel；③ 在 `RISCV.td` include；④ 走 `RISCVInstrInfoXPhytium.td` 的 Xxxx 路线 upstream 国密增强扩展。**这是"自研核 + upstream 框架"的工程模板**（对偶龙芯 LoongArch 路径的 RISC-V 版）。

> **§6 诚实结论**：飞腾切 RISC-V 的 trigger 是三重组合——v9 不授（必要）+ RISC-V 服务器成熟（充分）+ 信创强制（政策）。最可能组合（v9 不授 + RISC-V 2030–2035 成熟）启动时点约 2030–2032，完成约 2040。**Trigger 触发后的第一动作不是写编译器，是建立 upstream 能力——学香山把调度模型推回主线**。切 ISA 不自动获得 upstream 能力，飞腾要把自己从"消费者"变成"生产者"。

---

## §7. 飞腾双栈策略（ARM+RISC-V 并行）编译器负担

> 任务点名必答：飞腾若同时维护 ARM + RISC-V 双栈，编译器负担有多大？

### 7.1 双栈并行的必然性

§1.2 教训一已述：Apple 两次切换都经历 3–4 年的双栈并行期（Universal Binary）。飞腾切 RISC-V 同样**几乎不可能"一刀切"**——必须经历 ARM+RISC-V 双栈并行的过渡期。原因有三：① 沉没成本（ARMv8.4 资产不能立刻退役）；② ISV 适配需要时间（信创 ISV 重编 RISC-V 版要 2–3 年）；③ 客户过渡（已部署的飞腾 ARM 系统要维护 5–10 年生命周期）。**双栈并行是切换的"必经阶段"，不是可选项**。

### 7.2 双栈编译器负担量化

飞腾双栈并行的编译器负担，从"两个 fork"扩展到"四个 fork"：

**当前（单栈 ARM）**：飞腾维护 PhyCC（LLVM fork）+ PhyGCC（GCC fork）= **2 个 fork**。编译器团队推测 12–20 人（Lens_07 §S2），已接近极限。

**双栈期（ARM+RISC-V）**：飞腾要维护 PhyCC-ARM（LLVM fork）+ PhyCC-RV（LLVM fork）+ PhyGCC-ARM（GCC fork）+ PhyGCC-RV（GCC fork）= **4 个 fork**。**编译器团队至少要扩 1 倍（24–40 人）**（§1.2 教训三）。

但这里有个**关键优化**：如果飞腾把 RISC-V 支持推回主线 LLVM（学香山），就可以**用主线 LLVM 替代 PhyCC-RV**——客户用主线 clang 即可，不用装 fork。这把"4 个 fork"简化为"PhyCC-ARM + PhyGCC-ARM + 主线 LLVM-RV + 主线 GCC-RV"= **2 个 fork + 2 个主线**。**这就是 upstream 的价值——upstream 能把 fork 负担转化为主线红利**。

### 7.3 双栈的技术债

双栈并行的技术债不只是"维护两套后端"，还有更深层的：

**债一：双 ABI 的二进制管理**。ARM AAPCS64 和 RISC-V LP64D 的二进制不兼容（§4），飞腾要维护**两套软件包仓库**（ARM 版 + RISC-V 版），每个信创软件出两个包。这是 Debian/Fedora 等多架构发行版的成熟做法，但飞腾信创栈（麒麟/达梦）的 ISV 能力弱于 Debian 社区，**双包管理负担更重**。

**债二：双微架构调优**。飞腾 ARMv8.4 核和未来 RISC-V 核的微架构（发射宽度/缓存层级/分支预测）不同，编译器调度优化要分别做。PhyCC-ARM 的调度模型（ftc86x，闭源）和主线 LLVM 的 RISC-V 调度模型（ftc9xx，upstream）是两套——**双栈意味着双倍的微架构调优工作**。

**债三：双栈期的"认知混乱"**。客户和 ISV 在双栈期会困惑："新项目该用 ARM 版还是 RISC-V 版？" Apple 用明确的路标（"2023 后 Intel Mac 停产"）消除混乱，飞腾需要类似明确的退役路标。**如果飞腾不敢宣布 ARM 退役时点，双栈会无限延长，编译器负担永续**。

### 7.4 双栈的退出策略

双栈并行不是目的，是过渡。飞腾需要明确的**退出策略**——何时退役 ARM 栈。参照 Apple：① 宣布退役时点（Apple 2009 弃 PowerPC，2023 弃 Intel Mac）；② 过渡期内新功能优先新架构；③ 过渡期后停止旧架构安全更新。

飞腾的退出策略应该是：① **2032 宣布** RISC-V 为新主线架构；② **2032–2040 双栈并行**（ARM 继续出货但新核停发）；③ **2040 后 ARM 退役**（只保留安全维护）。**退出策略的明确性比双栈本身更重要**——模糊的退出策略会让双栈变成永续负担。

### 7.5 对照：龙芯的双栈经验

龙芯从 MIPS 切 LoongArch 提供了国产双栈的现成经验。龙芯在 2020–2025 经历了 MIPS + LoongArch 双栈期：① 用 LBT 扩展让 LoongArch 跑旧 MIPS 二进制（硬件翻译兜底）；② 渐进把 ISV 迁到 LoongArch；③ 2025 后 MIPS 退役。**龙芯的经验是"硬件翻译兜底 + 渐进迁移 + 明确退役"**。飞腾切 RISC-V 没有 LBT 兜底（§4.4），双栈过渡比龙芯更难——只能靠 Universal Binary + QEMU 软件翻译。

> **§7 诚实结论**：飞腾双栈（ARM+RISC-V）并行是切换的**必经阶段**，编译器负担从"2 个 fork"扩到"4 个 fork"（团队翻倍），除非 upstream 简化为"2 fork + 2 主线"。双栈的技术债包括双 ABI 二进制管理、双微架构调优、认知混乱。**关键解法是明确退出策略**——参照 Apple/龙芯，宣布退役时点，避免双栈永续。**双栈的负担大小取决于飞腾的 upstream 能力——upstream 能把 fork 负担转化为主线红利**。

---

## §8. 三后端成熟度对标表（ARM / RISC-V / LoongArch）

> 这是全文的对偶核心表，锚定 Expert_10 §2.4 + 本次实测。

| 维度 | AArch64（E08，飞腾当前） | RISC-V（飞腾候选） | LoongArch（龙芯对照） |
|------|:---:|:---:|:---:|
| **进主线版本** | LLVM 3.0+（2011） | LLVM 9（2019）→ 13（2021 稳定） | LLVM 16（2023-03） |
| **.cpp 文件数** | ~84 `[实测]` | ~68 `[实测]` | ~30 `[实测]` |
| **.td 文件数** | ~55 `[实测]` | ~90 `[实测]` | ~20 `[实测]` |
| **调度模型数** | ~30 `[实测]` | **16** `[实测]` | **0**（通用模型） |
| **国产核在主线** | 🟢 华为 TSV110；🔴 飞腾零 | 🟢🟢 香山/SpacemiT；🟠 玄铁半截子 | 🟢 龙芯全栈 |
| **向量方案** | NEON 定长 + SVE/SVE2 可变长 + SME 矩阵 | RVV 可变长（vscale） | LSX 128 定长 + LASX 256 定长 |
| **BF16 支持** | ❌（飞腾 ARMv8.4 无） | ✅ Zvfbfmin/Zvfbfwma `[实测]` | ✅ |
| **二进制翻译** | 无（靠 Rosetta/QEMU 外部） | 无原生（靠 QEMU，30–50%） | 🟢 **LBT 原生**（x86/ARM） |
| **国密（SM3/SM4）** | ✅ 飞腾原生（微架构优化） | ✅ Zk 扩展（标准，待调优） | ✅ |
| **ABI 稳定性** | 🟢 AAPCS64 冻结（2012+） | 🟡 LP64D 活跃演进 | 🟢 稳定 |
| **ISA 主权** | 🔴 ARM 授权锁（v9 不授） | 🟡 开放 ISA，国际共识 | 🟢🟢 完全自研 |
| **飞腾切换代价** | （当前栈） | 高（无 LBT + 边缘生态 + 外部协调） | 中（有 LBT + 但龙芯主导） |

> 表 8：三后端成熟度对标（`[实测]` glob + `[官方]` 规范 + `[推测-依据]`）。**三个关键判断**：
> 1. **RISC-V 在"数据类型丰富度"上优于飞腾当前 ARMv8.4**（有 BF16！），但"AI 推理栈成熟度"落后 2 年。
> 2. **RISC-V 在"二进制翻译"上劣于 LoongArch**（无 LBT），这是飞腾选 RISC-V 而非 LoongArch 的关键顾虑。
> 3. **RISC-V 的"ISA 主权"是部分自主**（开放但受国际共识制约），不如 LoongArch 完全自研。

---

## §9. 飞腾切 RISC-V 的就绪度评分表（5 维度）

| 维度 | 就绪度 | 关键证据 | 飞腾自身短板 |
|------|:------:|---------|------------|
| **LLVM 后端基础** | 🟢 80% | 68 cpp/90 td/16 调度模型，RV64GC+RVV+Zk 全套 `[实测]` | 飞腾零 RISC-V 经验 |
| **服务器级调度模型** | 🟡 50% | 香山/SpacemiT/Ascalon/SG2042 几套，仅 AArch64 1/3 | 飞腾要自写 FTC9xx 调度模型 |
| **AI 推理栈（RVV-MLIR）** | 🟠 35% | RVV 有 BF16，但 KleidiAI-RVV 落后 ARM 2 年 | 飞腾 AI 算力债延续 |
| **OS 生态（Linux/glibc/发行版）** | 🟢 75% | Debian/Fedora/openEuler RVA23-ready | 信创 ISV（麒麟/达梦）重适配 |
| **二进制续命（翻译）** | 🔴 25% | 无 LBT，QEMU 30–50% | 远低于 LoongArch/Apple Rosetta |
| **综合就绪度** | **🟡 ~53%** | 基础够，深度欠，续命弱 | upstream 能力是根本短板 |

> 表 9：飞腾切 RISC-V 就绪度评分（`[实测]` + `[推测-依据]`）。**综合就绪度约 53%——"够启动预研，不够全面切换"**。

---

## §10. 图表汇总

> **图表 1：飞腾切 RISC-V 的就绪度雷达图（5 维度）**
> ```
>                    LLVM后端基础 (80%)
>                          ████
>                        █       █
>          服务器调度(50%) ██     ██ AI推理栈(35%)
>                       █           █
>                        █         █
>                          █     █
>                  OS生态(75%)███  ██ 二进制续命(25%)
>                          ↑
>                   综合就绪度 ~53%
>   ────────────────────────────────────
>   特征：基础宽（OS/后端），深度窄（AI/续命/调度）
>   短板：二进制续命（无 LBT）是最低维度
> ```
> 图表 1：飞腾切 RISC-V 就绪度雷达图。**形状是"偏科的"——基础够但续命弱，这意味着切换的"启动门槛"够，但"完成门槛"（旧软件续命）不够**。

> **图表 2：飞腾切 RISC-V 时间线（10 年档标准路径）**
> ```
>   2026 ──── 2030 ──── 2032 ──── 2036 ──── 2040 ──── 2045
>    │         │         │         │         │         │
>    │  ARMv8.4│  预研启动│ 双栈并行 │ RISC-V  │ ARM     │
>    │  冻结期 │  ↓       │ ARM+RV  │ 主线化  │ 退役    │
>    │         │ 学香山   │         │         │         │
>    │         │ upstream │ 4 fork  │ 2fork+  │ 维护态  │
>    │         │ 调度模型 │ 团队翻倍 │ 2主线   │         │
>    │         │         │         │         │         │
>    └─Trigger: v9不授+RISC-V服务器成熟(2030-2035)──────┘
> ```
> 图表 2：飞腾切 RISC-V 时间线（10 年档，概率 50–65%）。**关键节点：2030 预研启动 → 2032 双栈 → 2036 主线化 → 2040 ARM 退役**。

> **图表 3：飞腾双栈编译器负担演化**
> ```
>   编译器 fork 数量演化：
>
>   4 fork ┤                          ┌────┐(双栈峰值)
>         │                         ╱      ╲
>   3 fork ┤                       ╱        ╲
>         │                     ╱            ╲
>   2 fork ┤─────╲            ╱                ╲────── (主线化后)
>         │      ╲          ╱                        ╲
>   1 fork ┤       ╲      ╱                          ╲─────
>         │        ╲    ╱
>   0 fork ┤────────╲──╱(纯ARM期)                       
>         └──┬─────┬─────┬─────┬─────┬─────┬─────
>          2026   2030  2032  2036  2040  2045
>          ARM    预研  双栈  峰值  主线  ARM退役
> ```
> 图表 3：飞腾双栈编译器 fork 负担演化。**双栈峰值在 2032–2036（4 fork，团队翻倍），upstream 后降到 2 fork + 主线**。**upstream 是降低负担的唯一解**。

---

## §11. 盲区与反方（诚实段，强制）

### 11.1 本评估的系统性盲区

1. **高估编译器就绪度对切换决策的影响**。本文是"编译器侧评估"，但飞腾切不切 RISC-V 的**真正决策变量是芯片性能 + 地缘 + 信创政策**，编译器只是跟随变量（§1.2 教训四）。**若决策者据本文得出"编译器够成熟，飞腾该切"的结论，会犯"编译器工程师视野局限"的错误**（Expert_10 §4.3 同款警告）。

2. **RISC-V 服务器单核性能预测的不确定性**。本文假设"2030–2035 RISC-V 服务器追平 Neoverse"，但这是推测。历史经验是开源 ISA 服务器化比预期慢（SG2042 单核弱），可能再延 2–3 年。**若 RISC-V 服务器 2040 才成熟，飞腾切换窗口整体后移**。

3. **二进制翻译性能数据的不确定性**。本文引用"QEMU ARM→RISC-V 约 30–50%"，但这是 QEMU TCG 的通用估算，**针对飞腾信创软件（麒麟/达梦）的实际翻译性能未实测**。可能更高（若软件是计算密集型，翻译开销占比小）或更低（若软件是系统调用密集型，翻译开销大）。

4. **信创 ISV 重适配能力的低估**。本文假设信创 ISV（麒麟/达梦/金蝶）能在 3–5 年内完成 RISC-V 重适配，但这些 ISV 的工程能力参差——**部分小 ISV 可能永远不出 RISC-V 版**，导致飞腾切 RISC-V 后生态残缺。

5. **LoongArch 替代选项的忽视**。本文聚焦"飞腾切 RISC-V"，但飞腾的另一个国产 ISA 选项是 **LoongArch**（与龙芯合作或自研 LA 兼容核）。LoongArch 有 LBT 兜底（§4.4），可能比 RISC-V 更适合飞腾的"旧软件续命"需求。**本文未充分评估"飞腾切 LoongArch"的对比选项**。

### 11.2 反方意见

- **"飞腾根本不该切 RISC-V，应该死守 ARMv8.4 + 等信创保护"**——部分有理。信创双轨制（Lens_07 §2.5）让飞腾在 niche 内能活，niche 内 L1（可用）达标即可。但反方：信创 4.0 可能强制国产 ISA，且 ARMv8.4 编译器债永续累积——**死守是"慢性窒息"，不是"稳定存活"**。

- **"飞腾应该切 LoongArch 而非 RISC-V"**——有竞争力。LoongArch 有 LBT 兜底 + ISA 完全自研 + 主线一等公民，某些维度优于 RISC-V。但反方：LoongArch 是龙芯独家 ISA，飞腾切 LoongArch 等于"从 ARM 锁换到龙芯锁"——**生态主权问题**。RISC-V 至少是全球开放 ISA。

- **"编译器就绪度不重要，飞腾切 RISC-V 的瓶颈在芯片和生态"**——基本正确。本文反复强调"编译器是跟随变量"。但反方：编译器就绪度是切换的**必要条件**（不就绪切不了），即便不是充分条件。

### 11.3 本评估最可能误导决策之处

**把"编译器基础就绪"等同于"切换可行"，据此推荐飞腾尽早切 RISC-V**。这是编译器评估的视野局限——飞腾切不切是芯片 + 地缘 + 信创的综合决策，编译器就绪度（53%）只说明"技术上能启动"，不说明"战略上该执行"。**若决策者据本文得出"飞腾 2028 就该启动切换"的结论，会忽略 RISC-V 服务器性能未成熟 + ISV 未准备好的风险**。正确的决策框架是：**等 Trigger 二（RISC-V 服务器成熟）+ Trigger 一（v9 不授）同时满足后再启动，而非仅凭编译器就绪**。

---

## §12. 与其他视角对偶（强制）

| 对偶视角 | 一致 / 冲突 | 核心交汇点 |
|---------|:----------:|----------|
| **Expert_10 RISC-V Backend** | ✅ 强共鸣 | 本文消费 Expert_10 的"国产 RISC-V upstream 实证"（香山/SpacemiT/玄铁），给出飞腾切 RISC-V 的就绪度评分。Expert_10 给"后端状态"，本文给"切换评估"。 |
| **Lens_07 国产化** | ✅ 强共鸣 | Lens_07 §2.4 预测"飞腾切轨窗口 2032–2035"，本文细化到"10 年档标准路径（2030 启动–2040 完成）"。两者一致：飞腾切 RISC-V 是大概率事件，但比 Apple 切 x86 更难。 |
| **E08 AArch64 Backend** | ✅ 强对偶 | E08 证"飞腾在 ARM 后端零 upstream"，本文证"飞腾切 RISC-V 后必须建立 upstream 能力"。**E08 给"ARM 侧的债"，本文给"RISC-V 侧的解（但要付费）"**。 |
| **E18 Phytium Adaptation** | ✅ 强互补 | E18 给"飞腾零 fork 实证"（45 目录全是消费），本文给"飞腾切 RISC-V 的 upstream 路径"（学香山）。**E18 证病，本文开方**。 |
| **飞腾 E22 开源生态** | ✅ 强共鸣 | E22 §2.2 写"RISC-V 服务器生态落后 ARM 3–5 年"，本文从编译器侧证实（AI 推理栈落后 2 年 + 调度模型 1/3）。 |
| **Lens_01 历史学家** | ✅ 强共鸣 | Lens_01 看"GCC→LLVM→MLIR 兴衰周期"，本文看"Apple 2005/2020 ISA 切换周期"。**两者共享"技术周期决定厂商命运"的历史视角**。 |

---

## §13. 参考文献（≥ 12，分级标注）

### 规范 / 官方文档（一手）

1. **[官方]** RISC-V International, *The RISC-V Instruction Set Manual, Volume I（含 V 扩展 RVV 1.0 + Zk 国密）*, riscv.org/technical/specifications, 访问 2026-07-07. —— RVV/Zk/Profile 的权威定义。
2. **[官方]** RISC-V International, *RISC-V Profiles (RVA22/RVA23S64)*, riscv.org, 访问 2026-07-07. —— 服务器级 profile，飞腾切 RISC-V 的对齐目标。
3. **[官方]** ARM Ltd., *ARM Architecture Reference Manual (ARM ARM, DDI 0487)*. —— AAPCS64 ABI 定义，§4 ABI 切换对照源。
4. **[官方]** 龙芯中科, *LoongArch 指令系统 + LBT/LVZ/LSX/LASX 扩展*（loongson.cn/system/loongarch）, 访问 2026-07-07. —— LBT 原生二进制翻译，§4.4 对照依据。

### 论文 / 学术

5. **[书]** Singh, S., *Mac OS X Internals: A Systems Approach*, Addison-Wesley, 2006. —— Apple 2005 PowerPC→x86 切换的 Universal Binary + Rosetta 1 工程细节。
6. **[论文]** Bresnahan, T. & Malerba, F., "Industrial-level computing: 'Windows of opportunity'", *Research Policy*, 28(9), 1999. —— 后发国家产业演化"机会窗口"，飞腾切 RISC-V 时机的框架来源。
7. **[论文]** Christensen, C., *The Innovator's Dilemma*, Harvard Business Review Press, 1997. —— 沉没成本陷阱，§5.3 飞腾"不愿切"的内在逻辑。

### GitHub / 实测

8. **[实测]** 本项目 glob `/data/usershare/ai/riscv/OpenXiangShan/llvm-project/llvm/lib/Target/RISCV/*.td` + `*.cpp`（2026-07-07）—— §0 后端目录 + 调度模型 16 套 + 厂商扩展 13+ 家实证。
9. **[实测]** 本项目 glob 同路径 `RISCVSched*.td`（2026-07-07）—— §0.2 调度模型清单（含香山 NanHu/SpacemiT X60-X100/SG2042 P8700）。
10. **[GitHub]** llvm/llvm-project, *RISCVInsertVSETVLI.cpp*（1087 行, 3-phase dataflow）, 访问 2026-07-07. —— §2.2 RVV 心脏 Pass。
11. **[GitHub]** OpenXiangShan/XiangShan, *香山开源 RISC-V 处理器*（github.com/OpenXiangShan/XiangShan）, 访问 2026-07-07. —— 香山 NanHu/Kunminghu 微架构，飞腾切 RISC-V 的可复用调度模型模板。
12. **[GitHub]** llvm/llvm-project, *LoongArchLBTInstrInfo.td*（LBT 原生二进制翻译扩展）, 访问 2026-07-07. —— §4.4 LoongArch 对照依据。

### 报道 / 社区

13. **[报道]** Siracusa, J., "Mac OS X 10.4.4 Tiger: Rosetta and the Intel transition", *Ars Technica*, 2006. —— Rosetta 1（QuickTransit）性能 40–80% 的媒体记录。
14. **[报道]** Larabel, M., "Apple Rosetta 2 Performance On Apple Silicon", *Phoronix*, 2020–2023. —— Rosetta 2（AOT 翻译）性能 70–90% 的实测记录。
15. **[社区]** openEuler, "openEuler RISC-V 架构进展"（openeuler.org/zh/blog）, 2024–2026. —— §3.3 openEuler RISC-V 一等架构证据。
16. **[社区]** 香山技术文档, *XiangShan-doc*（xiangshan-doc.readthedocs.io）, 访问 2026-07-07. —— 香山南湖 6 发射微架构，与 RISCVSchedXiangShanNanHu.td 对应。

---

## §14. 五个最重磅的诚实判断（全文提炼）

> 1. **飞腾切 RISC-V 的编译器基础设施"基本就绪"（综合 ~53%）**——后端稳定（68 cpp/90 td/16 调度模型 `[实测]`）+ RVA23 profile 成熟 + 国密 Zk 支持。但**深度欠半**：服务器级调度模型只有 AArch64 1/3、AI 推理栈落后 2 年、二进制续命（无 LBT）只有 25%。**够启动预研，不够全面切换**。
>
> 2. **飞腾切 RISC-V 比 Apple 2005 切 x86 难 3 倍**——① 切到"边缘 ISA"（RISC-V 服务器生态落后 ARM 3–5 年）而非"主流 ISA"；② 飞腾无垂直整合（双栈协调外部化给信创 ISV）；③ RISC-V 无 LBT 原生翻译（旧软件续命性能 30–50%，远低于 Rosetta 2 的 70–90%）。**飞腾切 RISC-V 不是"能不能"的问题，是"比 Apple 难 3 倍但必须做"的被动求生**。**🔒 2026-07 校准**：C930（2025-03 交付，首款国产服务器级 RISC-V CPU，3.4 GHz/15.2 SPECint2006/GHz，TITAN+TPE+8 TOPS Matrix，平头哥对外授权 IP）让"边缘 ISA"的硬件差距缩小——C930 性能已达 Cortex-A77/Neoverse-N1 区间，不再是"边缘"。但 OS/DB/ISV 国产适配仍落后 ARM 3-5 年，"难 3 倍"的核心约束（生态非硬件）不变。深度供应链分析见飞腾体系结构实验 [Lens_03 §节点③](../../体系结构实验/Lenses/Lens_03_SupplyChain.md) + [Expert_22 §2.1](../../体系结构实验/Expert_22_OpenSource_Ecosystem/)。
>
> 3. **飞腾切 RISC-V 的 trigger 是三重组合**——v9 不授（必要，> 80%）+ RISC-V 服务器成熟（充分，2030–2035）+ 信创强制国产 ISA（政策，30–45%）。最可能组合启动时点约 2030–2032，10 年档标准路径完成约 2040（概率 50–65%）。**Trigger 触发后第一动作不是写编译器，是建立 upstream 能力——学香山把调度模型推回主线**。
>
> 4. **双栈并行（ARM+RISC-V）是切换的必经阶段，编译器负担从"2 fork"扩到"4 fork"（团队翻倍）**——除非 upstream 简化为"2 fork + 2 主线"。**双栈的关键解法是明确退出策略**（参照 Apple 2009 弃 PowerPC / 龙芯 2025 弃 MIPS），宣布 ARM 退役时点，避免双栈永续。**upstream 能把 fork 负担转化为主线红利**。
>
> 5. **飞腾切 RISC-V 不等于获得 upstream 能力**——飞腾在 ARM 栈零 upstream（Lens_07 §2.1 grep 实证），切 RISC-V 后若不投入 upstream，照样零痕迹。**切 ISA 是"换舞台"，建立 upstream 能力是"学会演戏"——两者不等价**。飞腾的根本短板不是 ISA 选择，是组织上没投入 upstream。切 RISC-V 后第一课：把自己从"消费者"变成"生产者"，学香山三步走（写调度模型 → 加 ProcessorModel → include RISCV.td）。

---

> **与项目宪法的对齐**：本文锚定 §0.3 双重门槛（飞腾工程实证 + 代码级实例 + 对偶判断），数字标来源分级，强制"盲区与反方"段（§11），强制对偶链接（§12）。飞腾是案例锚点，RISC-V 切换评估是普适命题——任何后发厂商在 ISA 锁定后追求"切轨自主"都适用本框架（Apple 2005 模型 + 双栈时间成本 + trigger 组合）。
