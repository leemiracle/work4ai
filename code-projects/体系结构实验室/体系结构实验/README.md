# 计算机体系结构实验项目

> 一套面向**飞腾 D3000/D3000M（FTC663/FTC862, ARMv8-A）**真机的体系结构实验，
> 系统化覆盖三本经典教材与 csdiy 推荐课程的核心知识点。
> 每个实验都用 `perf` / `PhyTune` / PMU 计数器**直接观测硬件行为**，
> 而不是停留在"取指-译码-执行-访存-写回"的背诵。
>
> **本项目不只是"perf 工程师视角"**——通过 **23 个顶级专家视角 + 9 个异质思维透镜**，
> 同一台飞腾 D3000M 被切成互补切面：从 ISA 理论、RTL、物理设计、工艺、封装、
> EDA、DFT、固件、OS、分布式、RAS，到 AI 定位、地缘战略、绿色计算、开源生态，
> 再到历史学家 / Christensen / 供应链 / VC 的异质审视。详见 [`Views.md`](./Views.md)。

---

## 0. 视角矩阵（23 专家 + 9 异质思维透镜）

本项目把飞腾 D3000M 切成 **23 个顶级专家视角**（覆盖 ISA→工艺→封装→固件→OS→分布式→RAS→AI 定位→地缘→绿色→开源全价值链）+ **9 个非从业者异质思维透镜**（历史学家 / Christensen / 供应链 / 经济 / 未来 / 人类学 / VC / 反垄断 / 伦理）。

👉 **完整矩阵、三轴体系、分层图、对偶验证、阅读建议**见 [`Views.md`](./Views.md)（项目导航中枢）。

**快速入口**：
- **原 12 专家**：[E01科学家](./Expert_01_Scientist/) · [E02架构](./Expert_02_Architect/) · [E03硬件](./Expert_03_HW_Designer/) · [E04 OS](./Expert_04_OS_Kernel/) · [E05 AI推理](./Expert_05_AI_Inference/) · [E06政策](./Expert_06_Standards_Policy/) · [E07商业](./Expert_07_Business/) · [E08数值](./Expert_08_Numerics/) · [E09建模](./Expert_09_Performance_Model/) · [E10分布式](./Expert_10_Distributed/) · [E11编译](./Expert_11_Compiler_Research/) · [E12安全](./Expert_12_Security_CISO/)
- **新增 11 专家**：[E13物理设计](./Expert_13_VLSI_Physical/) · [E14工艺](./Expert_14_Process_Manufacturing/) · [E15封装Chiplet](./Expert_15_Package_Chiplet/) · [E16 EDA](./Expert_16_EDA_Toolchain/) · [E17 DFT硅后](./Expert_17_DFT_PostSilicon/) · [E18固件](./Expert_18_Firmware_Boot/) · [E19地缘](./Expert_19_Geostrategy/) · [E20绿色](./Expert_20_Green_Compute/) · [E21 AI定位](./Expert_21_AI_Positioning/) · [E22开源生态](./Expert_22_OpenSource_Ecosystem/) · [E23 RAS](./Expert_23_Server_RAS/)
- **9 异质透镜**：[`Lenses/`](./Lenses/)（历史 / Christensen / 供应链 / 经济 / 未来 / 人类学 / VC / 反垄断 / 伦理）

**改造宪法**（视角清单 / 质量门槛 / 写作纪律）：[`改造蓝图与写作规范.md`](./改造蓝图与写作规范.md) ｜ **质量审计**：`审计报告.md`

**入门路径**：零基础 → [`Nand2Tetris/`](./Nand2Tetris/)（教学 HDL 造 Hack CPU）→ [`DDCA/`](./DDCA/)（工业 Verilog 造 MIPS CPU，可综合到 FPGA）；学生 → [Expert_01](./Expert_01_Scientist/) → [Expert_03](./Expert_03_HW_Designer/)；工程师 → [Expert_11](./Expert_11_Compiler_Research/) → [Expert_04](./Expert_04_OS_Kernel/)；想破思维定式 → [`Lenses/`](./Lenses/)。

**辅助工具视角**：[`View_01_Compiler`](./View_01_Compiler/) / [`View_02_Security`](./View_02_Security/) / [`View_03_Perf`](./View_03_Perf/) / [`View_04_History`](./View_04_History/) / [`View_05_CrossArch`](./View_05_CrossArch/)。

**对偶验证**：[`duel_validator.py`](./duel_validator.py) 用 5 个实验交叉检验多视角结论（4 一致 + 1 性能-安全冲突）。

**可运行代码总索引**：[`CODE_INDEX.md`](./CODE_INDEX.md) 列出全部可跑程序 + 命令 + 飞腾实测数据表。

---

## 0.5 项目思想地图（5 层结构）

本项目按 **5 层**组织，每层回答一个不同的问题：

| 层次 | 文档 | 回答的问题 |
|------|------|-----------|
| **① 思想母题层（横向）** | [`背景知识/Great_Ideas_体系结构思想.md`](./背景知识/Great_Ideas_体系结构思想.md) | **为什么**会有这些设计？（抽象/局部性/并行/流水线/预测/存储层次/可靠性/接口/能效/可扩展性 十大思想） |
| **① 思想母题层（纵向）** | [`背景知识/处理器分层模型.md`](./背景知识/处理器分层模型.md) | 从 App 到硅片**中间有几层抽象**？（应用 / OS+ABI / ISA / 微架构 / 物理 五层契约栈，含 IBM S/360 历史、跨 ISA 兼容性矫正、QEMU vs Gem5 辨析）|
| **② 实验观测层（自上而下）** | [`Lab00`–`Lab07`](.) | 在飞腾 D3000M 上**怎么观测**？（perf + PMU 计数器） |
| **② 自下而上构建层（与 Lab 对偶）** | [`Nand2Tetris/`](./Nand2Tetris/) + [`DDCA/`](./DDCA/) | **自己造一台计算机**：Nand2Tetris 用教学 HDL（Hack ISA），DDCA 用工业 Verilog（MIPS，可综合到 FPGA）|
| **③ 专家视角层** | [`Expert_01`–`Expert_23`](.) | 不同角色**怎么看**？（ISA→工艺→封装→固件→OS→分布式→RAS→AI） |
| **④ 异质透镜层** | [`Lenses/Lens_01`–`Lens_09`](./Lenses/) | **换个角度**怎么看？（历史/Christensen/供应链/经济/未来/人类学/VC/反垄断/伦理） |
| **⑤ 事实锚点层** | [`战略锚点.md`](./战略锚点.md) | 飞腾的**核心事实**权威定义（避免 22 篇 Expert 重复铺陈） |

> **新读者建议**：先读 ①（十分钟建立全局观：横向看 [`Great_Ideas`](./背景知识/Great_Ideas_体系结构思想.md) + 纵向看 [`处理器分层模型`](./背景知识/处理器分层模型.md)，形成"思想 × 层次"十字骨架）→ 再按 §3 路线图进 ②；想多角度深入进 ③；想破思维定式进 ④；查证事实进 ⑤。
>
> **四种 CPU 学习路径互补**：
> - **[`Nand2Tetris`](./Nand2Tetris/)**（教学级自下而上）：从 Nand 一路造到俄罗斯方块——**亲手构建一台教学 CPU（Hack）+ 完整工具链 + OS**
> - **[`DDCA`](./DDCA/)**（工业级自下而上）：ETH Zurich Mutlu + Harris & Harris，用 **工业 Verilog** + **MIPS** + **可综合到 FPGA**——比 Nand2Tetris 工程化高一个量级
> - **[`Lab00`–`Lab07`](./Lab00_测量基础设施/)**（自上而下）：用 perf 观测真实工业 CPU（飞腾 D3000M）
> - **[`Capstone/cpu_simulator`](./Capstone/cpu_simulator/)**（中间抽象）：用 Python 模拟 RV32I 5 级流水线

---

## 1. 项目定位

| 维度 | 本项目 | MIT 6.172（已完成） |
|------|--------|---------------------|
| 视角 | **自下而上**：硬件如何工作 | 自上而下：如何让代码跑得快 |
| 主要教材 | Patterson RISC-V / 姚永斌超标量 / CAQA | Leiserson 讲义 |
| 核心问题 | "流水线/Cache/分支预测**到底是什么**？" | "为什么这段代码慢、怎么优化？" |
| 工具用法 | perf/PMU 用于**观测概念** | perf/PMU 用于**优化决策** |
| 关系 | **互补**：硬件理解→优化直觉 | 互补：优化经验→硬件提问 |

两者**完全不重复**：6.172 教你写快代码，本项目教你看懂硬件在干什么。

---

## 2. 与三本书 + csdiy 课程的映射表

### 📘 书 1：Patterson & Hennessy《计算机组成与设计：硬件/软件接口 RISC-V 版（第2版）》
*入门级，机械工业出版社 2023，豆瓣 8.7*

| 章节 | 主题 | 对应实验 |
|------|------|---------|
| Ch1 | 性能、功率、成本、Amdahl 定律 | Lab00 |
| Ch2 | 指令集（RV32I）、汇编、调用约定 | Lab01 |
| Ch3 | 计算机算术（整数/浮点） | Lab01.5 |
| Ch4 | **流水线**、冒险、分支预测 | Lab02 |
| Ch5 | **存储层次**、Cache、虚拟存储 | Lab03 |
| Ch6 | 并行处理器、GPU、DSA | Lab05 |

### 📕 书 2：姚永斌《超标量处理器设计》
*进阶级，清华大学出版社 2014，豆瓣 9.6（CPU 设计类目第一）*

| 章节 | 主题 | 对应实验 |
|------|------|---------|
| Ch1 | 超标量概览、顺序/乱序 | Lab02 + Lab04 |
| Ch2 | Cache、多端口、Victim Cache | Lab03 |
| Ch3 | 虚拟存储、TLB、Page Walk | Lab03 |
| Ch4 | **分支预测**（2-bit/全局/竞争/TAGE） | Lab02 |
| Ch5 | 指令集体系（RISC/CISC/MIPS/ARM） | Lab01 |
| Ch6 | 指令解码 | Lab04（专题） |
| Ch7 | **寄存器重命名**（ROB/ARF/PRF 三种方案） | Lab04 |
| Ch8 | **发射**（集中式 vs 分布式、唤醒-选择电路） | Lab04 |
| Ch9 | 执行、旁路网络、Cluster、Memory Disambiguation | Lab02 + Lab04 |
| Ch10 | 提交、ROB、异常处理 | Lab04 |
| Ch11 | **真实案例：Alpha 21264** | Capstone-A（论文精读 + 飞腾对比） |

### 📗 书 3：Hennessy & Patterson《Computer Architecture: A Quantitative Approach (5th)》
*高级，Morgan Kaufmann 2011，豆瓣 9.6（圣经）*

| 章节 | 主题 | 对应实验 |
|------|------|---------|
| Ch1 | **量化方法论**（CPU 时间公式、Amdahl/Gustafson、Iron Law） | Lab00 |
| Ch2 | 存储层次（Cache、Consistency、Prefetch） | Lab03 |
| Ch3 | **ILP 与其利用**（Tomasulo、ROB、Speculation） | Lab02 + Lab04 |
| Ch4 | DLP（Vector/SIMD/GPU） | Lab05 |
| Ch5 | TLP（多处理器、一致性、同步） | Lab05 |
| Ch6 | WSC 仓库级计算机 | Capstone-C |
| App A | 指令集原则 | Lab01 |
| App B | 存储层次复习 | Lab03 |
| App C | 流水线基础 | Lab02 |
| App J | 计算机算术 | Lab01.5 |

### 🎓 csdiy.wiki 推荐课程（补充）

| 课程 | 价值 | 何时穿插 |
|------|------|---------|
| **Nand2Tetris** | 从 NAND 门到俄罗斯方块，零门槛 | 如对硬件完全陌生，Lab00 前可选做 → [`Nand2Tetris/`](./Nand2Tetris/)（本项目已集成 12 个 project 导读）|
| **ETHz DDCA (Mutlu)** | Harris & Harris Verilog 实战，**可综合到 FPGA** | Nand2Tetris 后进阶 → [`DDCA/`](./DDCA/)（本项目已集成 9 个 Lab 导读）|
| **CMU 15-213 CSAPP** | Bryant 的体系/系统全景 | Lab01/Lab03 的深读参考 |
| **UCB CS61C** | RISC-V + C→汇编→CPU + 并行优化 Numpy | Lab01/Lab02/Lab05 |
| **ETHz CA (Onur Mutlu)** | 前沿研究级体系结构 | Lab04 之后的研究性阅读 |

---

## 3. 阶段路线图（建议按顺序，但可灵活）

```
                    ┌──────────────────────────────────────┐
   阶段 0 (1 周)    │ Lab00 测量基础设施 + 架构探测           │ ← 工具链建立
                    │   "你必须先有度量衡，才能做实验"          │   (Iron Law)
                    └──────────────────────────────────────┘
                                      ↓
                    ┌──────────────────────────────────────┐
   阶段 1 (1-2 周)  │ Lab01 ISA 与汇编 + ARMv8.x 扩展         │ ← 书1 Ch2 + v8.2-v8.4
                    │   fp16/UDOT/FCMLA/LSE/AES 全实测        │
                    └──────────────────────────────────────┘
                                      ↓
                    ┌──────────────────────────────────────┐
   阶段 2 (2 周)    │ Lab02 流水线、ILP、分支预测、LSE         │ ← 书1 Ch4 + 书2 Ch1/4
                    │   LSE 原子 vs LL/SC（v8.1）             │
                    └──────────────────────────────────────┘
                                      ↓
                    ┌──────────────────────────────────────┐
   阶段 3 (2 周)    │ Lab03 存储层次（Cache/虚拟存储/NUMA）   │ ← 书1 Ch5 + 书2 Ch2/3
                    │   pointer chasing 实测 cache 边界       │
                    └──────────────────────────────────────┘
                                      ↓
                    ┌──────────────────────────────────────┐
   阶段 4 (2-3 周)  │ Lab04 超标量乱序核心机制                  │ ← 书2 Ch6-10（全书核心）
                    │   rename_capacity 反推 PRF              │
                    └──────────────────────────────────────┘
                                      ↓
                    ┌──────────────────────────────────────┐
   阶段 5 (1-2 周)  │ Lab05 SIMD/NEON 与多核并行               │ ← 书3 Ch4/5 + CS61C Proj4
                    │   GEMM 五步优化（fp32）                  │
                    └──────────────────────────────────────┘
                                      ↓
                    ┌──────────────────────────────────────┐
   阶段 6 (1-2 周)  │ Lab06 内存模型与并发（ARM 特色）          │ ← Sorin et al. 圣经
                    │   ARM RCpc 重排实测 + dmb 代价           │
                    └──────────────────────────────────────┘
                                      ↓
                    ┌──────────────────────────────────────┐
   阶段 7 (1 周)    │ Lab07 密码学专题（飞腾杀手级）            │ ← 国密合规 + TLS
                    │   AES/SHA/SM3/SM4/CRC32 全套             │
                    └──────────────────────────────────────┘
                                      ↓
                    ┌──────────────────────────────────────┐
   阶段 8 (4-8 周)  │ Capstone（三个并行做）                   │ ← 综合应用
                    │   A. 论文：Alpha 21264 vs 飞腾          │
                    │   B. 自写 RV32I 模拟器                  │
                    │   C. 工作负载刻画（如 llama.cpp）       │
                    └──────────────────────────────────────┘
```

**总时长估算**：每周 8 小时投入，约 **14-20 周**完成 Lab00-Lab07；
Capstone 三个并行约 8 周。

---

## 4. 实验目录结构

```
体系结构实验/
├── README.md                       ← 本文件（路线图 + 映射表）
├── 扩展专题.md                     ← ARMv8.x 扩展特性总览（含关键指令索引，必读）
├── isa_reference/                  ← **A64 指令级深度参考**（基于 ARM ARM DDI 0487G.b）
│   ├── README.md                   ← 总索引（按版本/Lab 两种导航）
│   ├── intrinsic_mapping.md        ← 指令 → C/C++ intrinsic 速查表（必读工具）
│   ├── deep_dive_core.md           ← 6 条核心指令算法层深度专题（AESE/SHA256H/UDOT/SM3SS1/SM4E/FCMLA）
│   ├── a64_base_overview.md        ← A64 350 条基础指令分类地图 + 索引（含按首字母拆分）
│   ├── a64_base_a_to_g.md          ← 基础指令 A-G 部分（89 条详解）
│   ├── a64_base_h_to_p.md          ← 基础指令 H-P 部分（126 条详解）
│   ├── a64_base_q_to_z.md          ← 基础指令 Q-Z 部分（135 条详解）
│   ├── a64_system_instructions.md  ← DMB/DSB/DC/IC/AT/TLBI + option 详表
│   ├── v8.0_asimd.md               ← NEON 267 条 SIMD/FP 指令（索引）
│   ├── v8.0_asimd_a_to_g.md        ← NEON 指令 A-G 部分（79 条）
│   ├── v8.0_asimd_h_to_p.md        ← NEON 指令 H-P 部分（40 条）
│   ├── v8.0_asimd_q_to_z.md        ← NEON 指令 Q-Z 部分（148 条）
│   ├── v8.0_crypto.md              ← AES/SHA1/SHA256/PMULL (15 条)
│   ├── v8.0_crc32.md               ← CRC32 硬件加速
│   ├── v8.1_lse.md                 ← LSE 原子 (55 条)
│   ├── v8.1_rdm.md                 ← SQRDMLAH/SH (4 条)
│   ├── v8.1_lor.md                 ← LDLAR/STLLR (6 条)
│   ├── v8.1_lrcpc.md               ← LDAPR RCpc load-acquire (3 条)
│   ├── v8.2_fp16.md                ← FP16 标量+NEON (68 条)
│   ├── v8.2_ras_cvap.md            ← RAS (ESB) + DC CVAP
│   ├── v8.3_fcma.md                ← FCMLA/FCADD 复数 (3 条)
│   ├── v8.3_misc.md                ← LRCPC2/JSConv/PAuth (25 条)
│   ├── v8.4_dotprod.md             ← UDOT/SDOT int8 点积 (4 条)
│   ├── v8.4_sha3_sha512.md         ← SHA3/SHA512 (8 条)
│   ├── v8.4_sm3_sm4.md             ← 国密 SM3/SM4 (9 条)
│   ├── v8.5_misc.md                ← v8.5+ BTI/FlagM/MTE/WFxT 等
│   └── v8.x_unsupported.md         ← SVE/BF16/I8MM/FHM 不支持说明 + 替代方案
├── common/                         ← 全体实验共用的基础设施
│   ├── bench.h                     ← 高精度计时 + 统计
│   ├── pmu.h                       ← perf_event_open 简易包装（修了 exclude_idle 坑）
│   ├── Makefile.inc                ← 通用编译规则
│   ├── perf_stat_run.sh            ← sudo perf stat wrapper（飞腾受限模式）
│   └── run_template.sh             ← perf 包装脚本模板
├── Lab00_测量基础设施/             ← ✅ 4 实验全跑通
│   ├── README.md
│   └── src/ (arch_probe, null_loop, amdahl_law, iron_law)
├── Lab01_ISA与汇编/                ← ✅ 7 实验跑通（含 ARMv8.2+ 扩展）
│   ├── README.md
│   └── src/ (c_to_asm, isa_features, fp16_perf, dot_product,
│            fcmla_complex, disasm_diff.sh)
├── Lab02_流水线与ILP/              ← ✅ 3 实验跑通
│   ├── README.md
│   └── src/ (data_hazards, branch_predict, loop_unroll, ooo_magic, lse_vs_llsc)
├── Lab03_存储层次/                 ← ✅ cache 边界/line/关联度/false sharing/TLB
│   ├── README.md
│   └── src/ (cache_sizes, cache_line, associativity, false_sharing, tlb_hugepage)
├── Lab04_超标量乱序/               ← ✅ 反推 ROB/LDQ/重命名/推测
│   ├── README.md
│   └── src/ (rename_capacity, rob_size, load_store_spec)
├── Lab05_并行与SIMD/               ← ✅ NEON/GEMM 全栈
│   ├── README.md
│   └── src/ (neon_intrinsics, auto_vectorize, gemm_full_stack)
├── Lab06_内存模型与并发/           ← ✅ 屏障代价 + store-store/MP 重排
│   ├── README.md
│   └── src/ (mem_order_cost, store_store_reorder, message_passing)
├── Lab07_密码学专题/               ← ✅ AES/SHA/SM3/SM4/CRC32
│   ├── README.md
│   └── src/ (aes_test, sha_compare, sm_test, crc_test)
│
├── Expert_01_Scientist/            ← 首席科学家（论文-设计映射 + open problems）
├── Expert_02_Architect/            ← 资深架构师（PPA 决策 + 下一代推演）
├── Expert_03_HW_Designer/          ← 硬件设计（RTL/IP集成/die对标）🔁深化
├── Expert_04_OS_Kernel/            ← 操作系统（软硬协同 + syscall/页表）
├── Expert_05_AI_Inference/         ← AI 推理（CPU/NPU/GPU 边界）
├── Expert_06_Standards_Policy/     ← 标准政策（国内信创/标准博弈）🔁深化
├── Expert_07_Business/             ← 商业经济（IP授权/周期/BOM）🔁深化
├── Expert_08_Numerics/             ← 数值分析（FP 正确性 + Kahan）
├── Expert_09_Performance_Model/    ← 性能建模（Roofline + CPI 栈）
├── Expert_10_Distributed/          ← 分布式（DC TCO/板级/CXL）🔁深化
├── Expert_11_Compiler_Research/    ← 编译器研究（IR/Pass/调度）
├── Expert_12_Security_CISO/        ← 首席安全官（威胁模型 + 信任根）
├── Expert_13_VLSI_Physical/        ← 🆕 VLSI 物理设计（综合/P&R/STA/签核）
├── Expert_14_Process_Manufacturing/← 🆕 工艺制造（14nm诚实定位/良率，含yield_model.py）
├── Expert_15_Package_Chiplet/      ← 🆕 封装与 Chiplet（UCIe/CoWoS/HBM）
├── Expert_16_EDA_Toolchain/        ← 🆕 EDA 工具方法学（DC/PT/OpenROAD）
├── Expert_17_DFT_PostSilicon/      ← 🆕 DFT + 硅后 Bringup（含test_cost_model.py）
├── Expert_18_Firmware_Boot/        ← 🆕 固件启动链（UEFI/TF-A/SBSA）
├── Expert_19_Geostrategy/          ← 🆕 半导体地缘战略（出口管制/供应链地图）
├── Expert_20_Green_Compute/        ← 🆕 绿色计算（PUE/每瓦性能/ESG）
├── Expert_21_AI_Positioning/       ← 🆕 AI 算力定位（无BF16/I8MM战略伤疤）
├── Expert_22_OpenSource_Ecosystem/ ← 🆕 开源芯片+国产软件栈（RISC-V/麒麟/达梦）
├── Expert_23_Server_RAS/           ← 🆕 服务器 RAS（ECC/MCA/可靠性）
├── Lenses/                         ← 🆕 9 异质思维透镜（历史/Christensen/供应链/经济/未来/人类学/VC/反垄断/伦理）
│
├── View_01_Compiler/               ← 编译器工具（-O0..-Ofast 实测）
├── View_02_Security/               ← 安全工具（Flush+Reload POC）
├── View_03_Perf/                   ← 性能工具（待补充）
├── View_04_History/                ← 历史资料（待补充）
├── View_05_CrossArch/              ← 横向数据（待补充）
│
└── Capstone/                       ← ✅ 三个综合项目全部完成
    ├── README.md
    ├── alpha_21264_study/          ← ✅ A. 论文精读 + 飞腾对比
    │   ├── README.md
    │   ├── notes.md                ← Kessler 1999 论文精读笔记
    │   ├── arch_diagram.md         ← 21264 微架构 mermaid 图（5 张）
    │   ├── comparison.md           ← 21264 vs D3000M 对比（数据自动采集）
    │   └── collect_lab_data.py     ← 一键重跑 Lab 反推实验
    ├── cpu_simulator/              ← ✅ B. RV32I 5 级流水线周期精确模拟器
    │   ├── README.md
    │   ├── rv32i_sim.py            ← 700 行完整 RV32I + forwarding/stall/预测器
    │   ├── assembler.py            ← 迷你 RV32I 汇编器（伪指令 + 标签）
    │   ├── run_all_and_report.py   ← 自动报告生成器
    │   ├── report.md               ← 自动生成的实验报告
    │   ├── test_progs/             ← 7 个测试程序（带 @expect 自验证）
    │   └── tests/test_rv32i.py     ← 77 个 pytest 测试（0.17s 跑完）
    └── workload_characterization/  ← ✅ C. 工作负载刻画（GEMM + zstd）
        ├── README.md
        ├── driver.sh               ← perf stat 自动采集
        ├── collect.py              ← 报告生成器
        ├── profile_report.md       ← 9 个工作负载实测数据
        ├── recommendations.md      ← 5 条具体优化建议
        └── data/                   ← 原始 perf 数据
```

**21 个可运行 binary**，覆盖 ISA/流水线/存储/超标量/并行/内存模型/密码学。

**ISA 文档体系**：[`isa_reference/`](./isa_reference/) 下 18 个深度 md 文件，从 ARM ARM DDI 0487G.b（8696 页）原书提取 755 个 A64 指令条目，按 HWCAP 扩展分组（v8.0-v8.5+），每个指令含助记符/汇编模板/Decode 伪代码/Operation 伪代码/飞腾实测性能/陷阱。总索引在 [`isa_reference/README.md`](./isa_reference/README.md)。

---

## 5. 实验的统一格式

每个 Lab 的 README 都按相同结构组织，便于系统化推进：

```
## 0. 学习目标（一句话能说清）
## 1. 对应教材与课程（明确指出书-章节）
## 2. 核心概念速览（直觉 → 关键公式 → 一张图）
## 3. 实验列表（每个子实验包含）
   ### 3.x.1 现象
   ### 3.x.2 假设（你猜会怎样？先写下）
   ### 3.x.3 实验代码（可运行的最小骨架）
   ### 3.x.4 运行方法（编译、运行、采样命令）
   ### 3.x.5 预期结果（数据表格）
   ### 3.x.6 解释（为什么是这个结果）
   ### 3.x.7 缺陷与陷阱（实验设计本身的局限）
   ### 3.x.8 扩展思考（链接到更深内容）
## 4. 学完应该掌握的检查清单（自测）
## 5. 参考文献（带页码的精确定位）
```

**核心原则**：每个实验都要 **先写假设 → 再跑代码 → 后解释**。
这是体系结构研究的标准范式（CAQA Ch1 的 "Fallacies and Pitfalls"）。

---

## 6. 工具链与依赖

### 必备
| 工具 | 用途 | 飞腾平台检查命令 |
|------|------|-----------------|
| `gcc` / `kpgcc` | 编译（带 `-mcpu=ftc663/ftc86x`） | `which gcc kpgcc` |
| `aarch64-linux-gnu-as` | 汇编器 | `as --version` |
| `aarch64-linux-gnu-objdump` | 反汇编查看 | `objdump -d a.out` |
| `perf` | PMU 计数器、采样 | `perf --version` |
| `taskset` / `numactl` | 绑核 / NUMA | `which taskset numactl` |

### 强烈推荐（飞腾环境已有）
| 工具 | 用途 | 路径 |
|------|------|------|
| **PhyTune topdown-tool** | ARM 官方 Top-Down 分析 | `/opt/phytune/.../topdown/topdown-tool` |
| **PhyTune pmu_ftc8/6.sh** | 处理器核 PMU 采集 | `/opt/phytune/.../hwpmu/` |
| **PhyTune dutpro** | 微架构微基准套件 | `/opt/phytune/.../dutpro/` |
| **datop** | DAMON 数据访问监控 | `/opt/phytune/.../fs-datop/datop` |

### 可选
| 工具 | 用途 | 何时需要 |
|------|------|---------|
| Valgrind Cachegrind | cache 模拟（不受硬件限制） | Lab03 对照实验 |
| LLVM-MCA | 静态指令调度分析 | Lab02/Lab04（飞腾未必支持，可换用 LLVM 编译） |
| gem5 | 周期精确模拟器 | Capstone-B |
| Verilator | Verilog 仿真 | Capstone-B（如选 FPGA 路线） |

---

## 7. 飞腾平台关键参数（实验时反复查阅）

> 来源：`飞腾腾锐D3000M数据手册V0.5.1.pdf`、PhyTune 配置文件、实测 `lscpu`

| 参数 | D3000M (FTC862) | D3000 (FTC663) | 备注 |
|------|-----------------|----------------|------|
| ISA | **ARMv8.4-A** | ARMv8.1-A | 实测全面 v8.4: LSE/FP16/UDOT/SM3/SM4/SHA3/SHA512 |
| 核数 | 8（单芯片） | 8（单芯片） | 多芯片可扩 |
| 频率 | **2500 MHz** (实测) | — | performance governor |
| L1 I-Cache | 64 KB, 4-way | 64 KB, 4-way | 私有（实测 256 sets）|
| L1 D-Cache | 64 KB, 4-way | 64 KB, 4-way | 私有（实测 256 sets）|
| L2 Cache | **512 KB**, 8-way | 512 KB, 8-way | **私有**（实测，数据手册标 1M 不符；1024 sets）|
| L3/SLC | **4 MB(核0-3) + 8 MB(核0-7)** 分级 | 8 MB | HNF 节点（实测分级共享）|
| Cache Line | 64 B | 64 B | 标准 |
| SIMD | NEON 128-bit | NEON 128-bit | V0-V31，32 个寄存器 |
| TLB | L1 48 entry + L2 2048 entry | 同上 | 支持 4K/64K/2M 页 |
| 内存控制器 | DDR4-3200，4 通道 | DDR4-3200 | 单芯片带宽 ~102 GB/s |
| 编译器 tune | `-mcpu=ftc86x` | `-mcpu=ftc66x` | PhyGCC 12.3.2 |

**这些参数将在 Lab00 通过 `arch_probe.c` 实测验证一遍**——书上的数字终究是数字，亲手测出来才叫掌握。

---

## 8. 实验纪律（避免掉坑）

借鉴 CAQA Ch1 的 "Fallacies and Pitfalls" 和 Mytkowicz 2009 论文 *"Producing Wrong Data Without Doing Anything Obviously Wrong"*：

1. **每次实验固定频率**：`cpupower frequency-set -g performance`，避免 DVFS 干扰
2. **每次实验绑单核**：`taskset -c 0`，避免调度器漂移
3. **关闭超线程**（如飞腾支持 SMT）：`/sys/devices/system/cpu/smt/control`
4. **跑足够多次取中位数**：单次结果几乎一定有偏差
5. **warmup + measured**：先跑一遍预热 Cache，再计时
6. **检查编译器有没有"作弊"**：用 `objdump -d` 看看 hot loop 还在不在
7. **数据对齐**：`posix_memalign`，64 字节对齐
8. **用 `volatile` 或 memory clobber 防止 DCE**：编译器会删掉"无副作用"的循环
9. **使用 PMU 时注意 multiplexing**：6 个硬件计数器不够时会分时
10. **永远先写假设再跑实验**：没有假设的"实验"只是 curiosity

---

## 9. 如何开始

```bash
# 1. 探测你的环境（确认硬件/工具链）
cd 体系结构实验/common
make arch_probe
./arch_probe

# 2. 阅读 Lab00 README
cd ../Lab00_测量基础设施/
cat README.md

# 3. 编译并运行第一个实验
make
./null_loop
```

**第一个里程碑**：完成 Lab00 的所有实验，能回答：
- 我的飞腾 D3000 真实 L1/L2/L3 大小是多少？关联度多少？
- 一个空循环每条指令需要多少 cycles？
- Amdahl 定律在我自己设计的并行加速实验里成立吗？

---

## 10. 与既有项目的协同

| 既有目录 | 关系 |
|---------|------|
| `CPU性能优化/` | 提供 PhyGCC、perf、PhyTune 使用经验，本项目复用 |
| `MIT6_172/` | 提供 Bentley 规则、缓存优化、并行算法视角，本项目**不重复**但引用 |
| `汇编/` | 提供基础 ARM64 汇编脚手架（01_hello ~ 05_syscall），Lab01 在此基础上深入 |
| `benchmarks/` | 已有的 GEMM/malloc/string 基准，Lab05 会复用 |

---

## 11. 已实测的关键数据汇总（飞腾 D3000M / FTC862 @ 2.5 GHz）

### 微架构参数
| 参数 | 实测值 | 反推实验 |
|------|--------|---------|
| Issue Width | **4-wide** | Lab00 null_loop IPC=4.00 |
| ALU 端口数 | **2/cycle** | Lab00 loop_add IPC=2.00 |
| **fmadd latency** | **4 cycles** | Lab02 dep_chain_1 |
| 寄存器重命名容量 | ≥ 50 PR | Lab04 rename_capacity |
| L1 D-Cache | 64KB / 4-way / **1.6 ns** | Lab03 cache_sizes |
| **L2 Cache** | **512KB / 8-way / 5-8 ns** | Lab03（与 6.172 报告"1MB"不符）|
| L3-1 | 4MB（核 0-3 共享） | Lab03 |
| L3-2 | 8MB（核 0-7 共享）/ 14 ns | Lab03 |
| DRAM | 130-140 ns | Lab03 |

### ARMv8.x 特性（HWCAP 实测）
- ✅ v8.0: ASIMD, AES, SHA1, SHA2, PMULL, CRC32
- ✅ v8.1: ATOMICS(LSE), ASIMDRDM, LRCPC
- ✅ v8.2: FPHP, ASIMDHP（**FP16 SIMD 比 FP64 快 3.81×**）
- ⚠️ v8.3: FCMA（HWCAP 未报，可能内核老）
- ✅ v8.4: SHA3, SHA512, **SM3, SM4 国密**, ASIMDDP
- ❌ SVE / BF16 / I8MM

### 性能数据汇总（2026-07-02 修复后真机实测）
| 实验 | 关键结果 |
|------|---------|
| Lab00 null_loop | loop_volatile IPC=4.00（4-wide 实证）|
| Lab00 iron_law | T_pred vs T_med 误差 < 1%（freq=2.5GHz，PMU 可信）|
| Lab01 fp16_perf | FP16 SIMD 6.70 GFLOPS（vs FP64 1.73，3.88×）|
| Lab01 dot_product | **UDOT 14.73 GMACS（vs NEON v8.0 4.41×，v8.4 真测到）**|
| Lab01 basic_math | int div 10.4 cyc / fp add 2.0 / fp mul 3.0 / fp div 13.1（实测，非教科书值）|
| Lab02 dep_chain | cyc/op 完美线性下降（1:4.03, 2:2.03, 4:1.00, 8:0.51）|
| Lab02 branch_predict | 随机分支 IPC 0.71（vs 单调 3.14），miss 18.5% |
| Lab02 ooo_magic | **serial IPC 0.02（DRAM miss 300cyc）vs parallel 2.36，真展示乱序极限**|
| Lab02 LSE | 单线程 LSE 5.5 vs LL/SC 7.3 ns/op；**多核绑核修复后 4线程 LSE 82ns（真实争用）**|
| Lab03 cache_sizes | L1 1.6 / L2 7.98 / L3 135 / DRAM 141 ns（实测延迟）|
| Lab04 rename_capacity | n≥12 时 IPC saturate **3.45**（发射带宽上限，非 PRF）|
| Lab05 GEMM | 正确性校验✓；NEON fp32 11.0 GFLOPS（**55% fp32 peak**）；OMP 8核有效 |
| Lab06 store_reorder | **0 次重排/2M trials（跨核真实测量，飞腾 store-store 保守）**|
| Lab07 CRC32 | 硬件 vs 软件 table **18.98×** 加速 |
| Lab07 SM4 | **GB/T 32907 标准向量自检✓**（修复了轮函数公式错误）|

---

## 12. 待你确认的几个问题

为了让后续实验更贴合你的需求，建议回答（不强求）：

1. **时间预算**：每周可投入多少小时？（之前 AI 方向是 3h/周，但本项目似乎是工作相关）
2. **优先级**：6 个 Lab 你最想先深入哪 2 个？（如选 Lab02+Lab03，我会先把这两个的种子代码补齐）
3. **Capstone 偏好**：A 论文精读 / B 模拟器实现 / C 工作负载刻画，更想做哪个？
4. **FPGA 是否可及**：有 Basys 3 / Zynq 板子吗？（决定 Capstone-B 是否走 Verilog 路线）
5. **记录偏好**：实验报告想用什么格式？纯 Markdown / Markdown+图 / Jupyter notebook？

📌 **下一步**：直接进入 [`Lab00_测量基础设施/`](./Lab00_测量基础设施/)，那里有完整的可运行代码。

---

## 13. 开发与贡献（git hook + md 审计）

本项目用 git hook 自动守护文档质量。**clone 后请执行一次**：

```bash
git config core.hooksPath .githooks
```

之后每次 `git commit` 前，hook 会自动扫描 `.md` 文件的：
- **悬空链接**（`[..](./xxx)` 指向不存在的文件）
- **对偶不对称**（宪法 §4.3，[`Views.md`](./Views.md) §5 矩阵要求双向引用）

失败则阻止提交（明细见终端输出）；紧急可 `git commit --no-verify` 绕过。

手动跑完整审计（5 维度，< 1 秒）：

```bash
python3 scripts/md_audit.py              # 全量（链接/数字/门槛/格式/对偶）
python3 scripts/md_audit.py --links      # 只查链接
python3 scripts/md_audit.py --duels      # 只查对偶对称性
```

详见 `.githooks/README.md` 与 `md检查报告.md`。
