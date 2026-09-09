# 体系结构实验室（真机观测 × 算子工程）

> **定位**：真机体系结构与算子工程实验室——在飞腾 D3000/D3000M（FTC862，ARMv8.2-a，4 FVU）真机上，
> 走通"**PMU/微架构观测 → 体系结构实验 → NEON 算子优化推到理论峰值**"的完整链：
> 测量基础设施（计时/PMU/Perfetto）→ ISA/流水线/存储层次/乱序真机实验（Lab00-07）
> → GEMM/卷积/量化/Attention 算子优化（kernel-opt-lab）→ 多视角分析与专家审查（lens/Expert/Lenses）。
> 非教学模拟环境的纸上体系结构：每个数字都来自 perf stat / PMU / 秒表级实测，可重跑。

---

## 入库说明（2026-09-09）

- 本目录由 `C:\workspace\体系结构` 下**两个独立 git 仓库**并入（kernel-opt-lab、体系结构实验）。
  **git 历史不随迁**——复制时一律排除 `.git/`，源目录未动、未修改；如需提交历史回源目录查。
- **弃收清单**：
  - `kernel-opt-lab/.opencode/`（60M AI 工具运行时）；
  - `体系结构实验/.opencode/`（61M 同上）；
  - `体系结构实验/gpu-mode-resources/`（108M，533 文件）——**外部资源快照堆**：GPU MODE 社区（原 CUDA MODE，聚焦 GPU 编程/kernel 性能优化/MLSys 的开源社区）公开资料的爬取整理快照，纯外部资料、非本库原创代码，且全部可自 GitHub `gpu-mode` 组织与 gpumode.com 重新获取，故不搬；其内容精华已由 [`体系结构实验/背景知识/GPU_Mode资源全览.md`](体系结构实验/背景知识/GPU_Mode资源全览.md)（社区全景/讲座目录/竞赛/working groups 深度综述）承载；
  - 两库 `.git/` 历史与 `.githooks/`（git 钩子基础设施，属源仓库运维件）；
  - `体系结构实验/` 下 15 个空运行时目录（analytics/android-*/cache/codegen/collaboration/custom-templates/learning/memory/predictive/prompt-library/swarm/templates）与 `.pytest_cache/`；
  - `体系结构实验/` 根级 **3 份过程性审计报告仍不迁**（删源前留档说明）：`md检查报告.md`、`实验诊断与修复计划.md`、`审计报告.md`——一次性过程产物，结论已固化进各文档修订，非资产本体；其 README 中的引用已降级纯文本。另 `POLICY-COMPLIANCE.md` 在两源库中均不存在（AUTONOMY-STATEMENT 的引用为源库固有死链，维持降级）。
- **依赖随迁**：`体系结构实验/common/`（Makefile.inc/bench.h/pmu.h/perf 脚本——Lab00-07 与 Expert_04/05 的 Makefile 均 `include ../../common/Makefile.inc` 或 `-I../../common`，不随迁则不可编译）与 `体系结构实验/isa_reference/`（18 个 md / 755 条 A64 指令，Lab01 README 直接链入）一并入库；`duel_validator.py` 因 [`CODE_INDEX.md`](体系结构实验/CODE_INDEX.md) 引用随迁。
- **补充迁移（同日二次并入，防删源丢失）**：`View_01~05` 五个视角目录（35 文件）+ 根级 6 份文档——[`README.md`](体系结构实验/README.md)（项目主入口/改造宪法）、[扩展专题.md](体系结构实验/扩展专题.md)、[领域资源库.md](体系结构实验/领域资源库.md)、[战略锚点.md](体系结构实验/战略锚点.md)、[改造蓝图与写作规范.md](体系结构实验/改造蓝图与写作规范.md)、[Expert升级指南.md](体系结构实验/Expert升级指南.md)——整迁至原相对位置，首次并入时降级的 117 条指向上述文件的引用已全部恢复为活链接（kernel-opt-lab 侧 3 条改指 `../../体系结构实验/`，其余原位复活）。

---

## 子库一：[`kernel-opt-lab/`](kernel-opt-lab/README.md) —— D3000 算子优化实验室（v1.0）

168 文件 / 4.0 MB。**把 D3000 算子推到理论峰值**的工作目录：`src/` 20 个 C 算子（GEMM FP32/INT8/FP16、Winograd 卷积 F(2,3)/F(4,4)/INT8、NEON Flash Attention、多核 flat/MC×NC 分块、手写汇编微内核）+ `analysis/` 5 个可执行技术 lens（Roofline/PMU/Thermal/Precision/Latency）+ 现代 Makefile（make/lens/analyze/test/bench）+ `isa_reference/` 755 条 A64 指令深度参考 + `common/` 计时与 PMU 基础设施 + `docs/`（安装/瓶颈分析/最优参数表/Perfetto 教程/FTC862 PMU 规范/csdiy 深展开）+ `Lenses/` 9 个异质思维透镜 + `results/` 实测基线与 bench 报告。
核心成果：**4 核 MC×NC 分块 GEMM 143 GFLOPS（92% 效率）**，FP32 单核 39.45 GFLOPS（98.6% of 40），INT8 77.74 GOPS（97.2%），Winograd F(4,4) 21.5× vs Direct，NEON Flash Attention 8 核 16×。
导航：[README](kernel-opt-lab/README.md) ｜ [CODE_INDEX](kernel-opt-lab/CODE_INDEX.md) ｜ [学习路径](kernel-opt-lab/学习路径.md) ｜ [项目宪法](kernel-opt-lab/项目宪法.md)。

## 子库二：[`体系结构实验/`](体系结构实验/README.md) —— 体系结构教学实验场（23 专家视角体系）

293 文件 / 6.5 MB。以飞腾 D3000M 真机为标本的体系结构实验：`Lab00-07`（35 个 C 文件——测量基础设施/ISA 与汇编/流水线与 ILP/存储层次/超标量乱序/并行与 SIMD/内存模型与并发/密码学专题，perf/PMU 真机观测）、`View_01~05` 五视角工具集（编译器对比/安全 POC/性能工程三板斧/历史/跨架构，6 个 C 文件可运行）、`DDCA/` 九个 Verilog lab（rtl/tb，8 个 .v）、`Capstone/`（RV32I 五级流水线模拟器 Python 实现 + 工作负载刻画 + Alpha 21264 研究）、`Nand2Tetris/`（12 个项目导览文档）、`Expert_01~23` 23 个专家人格 md（其中 6 个含可运行代码/脚本）、`Lenses/` 9 个异质透镜、`Views.md` 视角矩阵、[`CODE_INDEX.md`](体系结构实验/CODE_INDEX.md) 可运行代码总索引、`背景知识/`（Great Ideas/处理器分层模型/GPU MODE 全览/概念）、根级治理文档（[README](体系结构实验/README.md)/[战略锚点](体系结构实验/战略锚点.md)/[改造蓝图与写作规范](体系结构实验/改造蓝图与写作规范.md)/[扩展专题](体系结构实验/扩展专题.md)/[领域资源库](体系结构实验/领域资源库.md)/[Expert升级指南](体系结构实验/Expert升级指南.md)）。
核心实测：issue width 4-wide、L1D 64KB@1.61ns→DRAM 130ns 全层级延迟、UDOT INT8 16.9×、TLB 2M 大页 4.81×。

---

## 代码资产索引（逐可运行单元）

> 硬件标注：**真机** = 需飞腾 D3000/D3000M（FTC862，ARMv8.2-a+fp16+dotprod）+ Linux（perf/taskset；PhyGCC 12.3.2 优先，系统 gcc 回退）；
> **无需真机** = 任何 x86/ARM 机器可跑（Python/iverilog/浏览器）。

### A. kernel-opt-lab —— 算子与 lens（C，`make` 或单目标，全部需真机）

| # | 名称 | 语言/源 | 入口 | 做什么 | 已知实测 |
|---|------|---------|------|--------|---------|
| 1 | gemm_f32 | C [`src/gemm_f32.c`](kernel-opt-lab/src/gemm_f32.c) | `make gemm_f32` | FP32 GEMM v5（MR=8，4 FVU 全开） | **39.45 GFLOPS（98.6% of 40）** |
| 2 | gemm_s8 | C [`src/gemm_s8.c`](kernel-opt-lab/src/gemm_s8.c) | `make gemm_s8` | INT8 GEMM v5（vdotq 点积） | **77.74 GOPS（97.2% of 80）** |
| 3 | gemm_f16 | C [`src/gemm_f16.c`](kernel-opt-lab/src/gemm_f16.c) | `make gemm_f16` | FP16 GEMM（v4_dual MR=2 最优） | 39.01 GFLOPS（78% of 50）⚠️ MR=8 反而更慢 |
| 4 | gemm_tune | C [`src/gemm_tune.c`](kernel-opt-lab/src/gemm_tune.c) | `make gemm_tune` | MR×NR×KC 自动调参 | 输出最优参数表 |
| 5 | gemm_autotune | C [`src/gemm_autotune.c`](kernel-opt-lab/src/gemm_autotune.c) | `gcc -O3 src/gemm_autotune.c -lm`（未挂 Makefile） | 进阶自动调优 | — |
| 6 | gemm_mr8_verify | C [`src/gemm_mr8_verify.c`](kernel-opt-lab/src/gemm_mr8_verify.c) | `make gemm_mr8_verify` | 三数据类型 MR=8 正确性验证 | 全 PASS |
| 7 | bench_gemm | C [`src/bench_gemm.c`](kernel-opt-lab/src/bench_gemm.c) | `make bench_gemm` | 原版主基准（raw throughput） | 基线对照 |
| 8 | conv_benchmark | C [`src/conv_benchmark.c`](kernel-opt-lab/src/conv_benchmark.c) | `make conv_benchmark` | 3×3/1×1/depthwise 卷积对比 | im2col 6.3× vs Direct |
| 9 | conv_winograd | C [`src/conv_winograd.c`](kernel-opt-lab/src/conv_winograd.c) | `make conv_winograd` | Winograd F(2×2,3×3) | 14.8× vs Direct |
| 10 | conv_winograd_f44 | C [`src/conv_winograd_f44.c`](kernel-opt-lab/src/conv_winograd_f44.c) | `make conv_winograd_f44` | ⭐ Winograd F(4×4,3×3) | **21.5× vs Direct（26.19 等效 GFLOPS）** |
| 11 | conv_winograd_int8 | C [`src/conv_winograd_int8.c`](kernel-opt-lab/src/conv_winograd_int8.c) | `gcc -O3 … -lm`（未挂 Makefile） | INT8 Winograd | — |
| 12 | conv_sizes | C [`src/conv_sizes.c`](kernel-opt-lab/src/conv_sizes.c) | `make conv_sizes` | 尺寸扫描 32→224 | roofline 拟合 |
| 13 | conv_dispatcher | C [`src/conv_dispatcher.c`](kernel-opt-lab/src/conv_dispatcher.c) | `make conv_dispatcher` | 按尺寸自动策略选择（OpenMP） | 自适应分发 |
| 14 | attention | C [`src/attention.c`](kernel-opt-lab/src/attention.c) | `make attention` | Naive vs scalar Flash 基线 | 154.2 ms @N=1024 |
| 15 | attention_neon | C [`src/attention_neon.c`](kernel-opt-lab/src/attention_neon.c) | `make attention_neon` | ⭐ NEON Flash + 多核 Flash（OpenMP） | **单核 6.58× / 8 核 16×（9.6 ms）** |
| 16 | multicore | C [`src/multicore.c`](kernel-opt-lab/src/multicore.c) | `make multicore` | OpenMP flat 多核扩展性 | 8 核 ~170 GFLOPS（57%，L3 双段限制） |
| 17 | multicore_tiled | C [`src/multicore_tiled.c`](kernel-opt-lab/src/multicore_tiled.c) | `make multicore_tiled` | ⭐ MC×NC 分块多核（OpenMP） | **4 核 143 GFLOPS（92.4% 效率）** |
| 18 | multicore_winograd | C [`src/multicore_winograd.c`](kernel-opt-lab/src/multicore_winograd.c) | `make multicore_winograd` | 多核 Winograd（OpenMP） | — |
| 19 | multicore_winograd_f44 | C [`src/multicore_winograd_f44.c`](kernel-opt-lab/src/multicore_winograd_f44.c) | `make multicore_winograd_f44` | 多核 F(4,4) Winograd（OpenMP） | — |
| 20 | asm_kernel | C [`src/asm_kernel.c`](kernel-opt-lab/src/asm_kernel.c) | `make asm_kernel` | 手写 inline asm 微内核（对照编译器） | — |
| 21 | lens-roofline | C [`analysis/lens-roofline.c`](kernel-opt-lab/analysis/lens-roofline.c) | `make lens` → `./bin/lens-roofline` | compute/memory bound 分类 | results/lenses/ 报告 |
| 22 | lens-pmu | C [`analysis/lens-pmu.c`](kernel-opt-lab/analysis/lens-pmu.c) | 同上 | 微架构 IPC/cache/branch 计数 | 同上 |
| 23 | lens-thermal | C [`analysis/lens-thermal.c`](kernel-opt-lab/analysis/lens-thermal.c) | 同上 | 热设计 + DVFS 降频证据 | 满载 49°C@2.2GHz |
| 24 | lens-precision | C [`analysis/lens-precision.c`](kernel-opt-lab/analysis/lens-precision.c) | 同上 | FP16/INT8 误差分布 | — |
| 25 | lens-latency | C [`analysis/lens-latency.c`](kernel-opt-lab/analysis/lens-latency.c) | 同上 | p50/p90/p99 长尾分布 | — |

配套：`make analyze` 一键跑全套 lens 生成报告（[`kernel-opt-lab/scripts/`](kernel-opt-lab/scripts/)：build/test/bench-all/analyze-all/run-perfetto/pmu-stat/detect-topology/runtime-tune 8 脚本；[`kernel-opt-lab/common/`](kernel-opt-lab/common/README.md) bench.h/pmu.h/perf_stat_run.sh；[`kernel-opt-lab/perfetto/`](kernel-opt-lab/perfetto/) trace 配置 → ui.perfetto.dev 可视化）。

### B. 体系结构实验 —— Lab00-07 真机观测（C，各 `Lab*/src/Makefile`，需真机 + taskset/perf）

| Lab | Makefile 目标 | 做什么 / 已知实测 |
|-----|--------------|------------------|
| [Lab00 测量基础设施](体系结构实验/Lab00_测量基础设施/) | arch_probe / null_loop / amdahl_law / iron_law | CPUID/拓扑探测；空循环 IPC（**issue width 4-wide**，ALU 端口 2/cyc）；Amdahl/铁律验证 |
| [Lab01 ISA 与汇编](体系结构实验/Lab01_ISA与汇编/) | c_to_asm / isa_features / fp16_perf / dot_product / fcmla_complex / calling_conv / basic_math | C→汇编对照；ISA 特性探测；**FP16 vs FP32 SIMD 3.81×**；UDOT/FCMLA 点积；调用约定 |
| [Lab02 流水线与 ILP](体系结构实验/Lab02_流水线与ILP/) | data_hazards / branch_predict / lse_vs_llsc / loop_unroll / ooo_magic | 数据冒险/分支预测代价；LSE vs LL/SC 原子；循环展开收益 |
| [Lab03 存储层次](体系结构实验/Lab03_存储层次/) | cache_sizes / cache_line / associativity / false_sharing / tlb_hugepage | 逐层测出 **L1D 64KB@1.61ns → L2 512KB@4.78ns → L3 8MB@14ns → DRAM 130ns**；伪共享代价 |
| [Lab04 超标量乱序](体系结构实验/Lab04_超标量乱序/) | rename_capacity / rob_size / load_store_spec | **重命名拐点 n≥12 饱和 IPC≈3.45**（发射带宽限制而非 PRF）；ROB 容量探测 |
| [Lab05 并行与 SIMD](体系结构实验/Lab05_并行与SIMD/) | gemm_full_stack / neon_intrinsics / auto_vectorize | GEMM 五步优化全栈（NEON FP32 峰 9.45 GFLOPS）；intrinsics vs 自动向量 |
| [Lab06 内存模型与并发](体系结构实验/Lab06_内存模型与并发/) | mem_order_cost / store_store_reorder / message_passing | 内存序代价；store-store 重排观测；消息传递 |
| [Lab07 密码学专题](体系结构实验/Lab07_密码学专题/) | crc_test / aes_test / sha_compare / sm_test | **CRC32 硬件 vs 软件 14.26×**；AES/SHA/国密 SM 指令实测 |

### B2. 体系结构实验 —— View 视角工具集（C，各 Makefile，View_01~03 需真机）

| 单元 | 语言/源 | 入口 | 做什么 / 已知实测 |
|------|---------|------|------------------|
| 编译器对比 | C [`View_01_Compiler/`](体系结构实验/View_01_Compiler/) | `make -C View_01_Compiler compare`（另有 vectorize 报告） | -O0..-Ofast 实测 [`src/opt_compare.c`](体系结构实验/View_01_Compiler/src/)；向量化成败报告 |
| 安全 POC | C [`View_02_Security/`](体系结构实验/View_02_Security/) | `make -C View_02_Security run` | Flush+Reload cache 时序攻击（cache_timing）；常时间编程对比（constant_time） |
| 性能三板斧 | C [`View_03_Perf/`](体系结构实验/View_03_Perf/) | `make -C View_03_Perf run` | 矩阵乘 8 步优化（**实测 15×**，matmul_evolution）；伪共享（**实测 2×**）；分支模式 IPC |
| 历史/跨架构视角 | 文档 [`View_04_History/`](体系结构实验/View_04_History/) ｜ [`View_05_CrossArch/`](体系结构实验/View_05_CrossArch/) | — | 两个文档型视角目录（x86/ARM/RISC-V 谱系对照），无可运行代码 |

### C. 体系结构实验 —— Capstone 综合项目（Python，无需真机）

| 单元 | 语言/源 | 入口 | 做什么 |
|------|---------|------|--------|
| RV32I 五级流水线模拟器 | Python [`Capstone/cpu_simulator/rv32i_sim.py`](体系结构实验/Capstone/cpu_simulator/rv32i_sim.py) | `python3 rv32i_sim.py` | 取指→译码→执行→访存→写回逐级模拟，含冒险/转发 |
| 迷你汇编器 | Python [`Capstone/cpu_simulator/assembler.py`](体系结构实验/Capstone/cpu_simulator/assembler.py) | `python3 assembler.py` | 汇编 → RV32I 机器码 |
| 模拟器测试 | Python [`Capstone/cpu_simulator/tests/`](体系结构实验/Capstone/cpu_simulator/tests/) | `pytest tests/ -v` | **77 个测试**全过 |
| 自动报告 | Python [`Capstone/cpu_simulator/run_all_and_report.py`](体系结构实验/Capstone/cpu_simulator/run_all_and_report.py) | `python3 run_all_and_report.py -o report.md` | 跑全部测试程序生成报告 |
| 工作负载刻画 | Shell/Python [`Capstone/workload_characterization/`](体系结构实验/Capstone/workload_characterization/) | `bash driver.sh`（需真机 perf） | perf 采样→collect.py 汇总指令混合比 |
| Lab 反推数据 | Python [`Capstone/alpha_21264_study/collect_lab_data.py`](体系结构实验/Capstone/alpha_21264_study/collect_lab_data.py) | `python3 … --md` | 汇总 Lab 实测对标 Alpha 21264 |

### D. 体系结构实验 —— DDCA 数字设计（Verilog，iverilog/yosys 仿真无需真机；Lab_09 需 FPGA 板）

九个 lab（[`DDCA/`](体系结构实验/DDCA/README.md) Lab_01 基础→Lab_09 Capstone FPGA），12 份 md 讲义 + 8 个 .v：Lab_02 组合逻辑（rtl）、Lab_03 ALU（rtl+tb_alu）、Lab_05 单周期 MIPS（4 个 rtl）、Lab_06 流水线 MIPS（rtl）；对照 [`Expert_03_HW_Designer/rtl/`](体系结构实验/Expert_03_HW_Designer/)（alu/forwarding_unit/two_bit_predictor + tb_alu，10 条 RV32I ALU）。

### E. 体系结构实验 —— Nand2Tetris（12 个项目导览，纯文档）

[`Nand2Tetris/`](体系结构实验/Nand2Tetris/README.md) Project_01 布尔逻辑 → Project_12 OS，12 份项目 README 导览（**练习导向写作，未含实现代码**，hdl/py/jack 由读者完成）；配 tools/bibliography。

### F. 体系结构实验 —— Expert 可运行件（飞腾本机为主）

| 单元 | 语言/源 | 入口 | 做什么 / 已知实测 | 硬件 |
|------|---------|------|------------------|------|
| syscall/TLB 测量 | C [`Expert_04_OS_Kernel/`](体系结构实验/Expert_04_OS_Kernel/) | `make -C Expert_04_OS_Kernel run` | 各 syscall 真实延迟；**TLB 4K vs 2M 大页 4.81×** | 真机 |
| INT8 UDOT GEMM | C [`Expert_05_AI_Inference/`](体系结构实验/Expert_05_AI_Inference/) | `make -C Expert_05_AI_Inference run` | UDOT INT8 GEMM | 真机（**实测 16.9×**） |
| 浮点精度演示 | C [`Expert_08_Numerics/src/`](体系结构实验/Expert_08_Numerics/src/) | `make -C Expert_08_Numerics/src compare` | -O0..fast 变体下 Kahan 求和是否被 -ffast-math 破坏 | 真机（armv8.4 编译） |
| Roofline 模型 | Python [`Expert_09_Performance_Model/roofline_d3000m.py`](体系结构实验/Expert_09_Performance_Model/roofline_d3000m.py) | `python3 …` | 生成 D3000M Roofline PNG | 无需真机 |
| 良率/成本模型 | Python [`Expert_14_Process_Manufacturing/yield_model.py`](体系结构实验/Expert_14_Process_Manufacturing/yield_model.py) | `python3 …` | Poisson/Murphy/Bose-Einstein 良率、good die、裸 die 成本（14nm Murphy 63.1%/$14.3，推测值） | 无需真机 |
| 测试成本/DPPM | Python [`Expert_17_DFT_PostSilicon/test_cost_model.py`](体系结构实验/Expert_17_DFT_PostSilicon/test_cost_model.py) | `python3 …` | ATE 机时→每颗测试成本 + DPPM 逃逸（$0.69/~500，推测值） | 无需真机 |
| 内嵌探测脚本 ×3 | Shell/C（Expert_18/20/23 README §内代码块） | 复制存盘后运行 | 启动链取证 / 能效 PPW / FEAT_RAS+ESB 探测 | 真机 |
| 对偶验证 | Python [`duel_validator.py`](体系结构实验/duel_validator.py) | `python3 duel_validator.py` | 5 个实验交叉检验多视角一致性 | 混合 |

### G. 已知实测数据速查（飞腾 D3000M，来源 [`体系结构实验/CODE_INDEX.md`](体系结构实验/CODE_INDEX.md) §G 与 [`kernel-opt-lab/results/baseline.md`](kernel-opt-lab/results/baseline.md)）

| 数据 | 实测值 | 来源 |
|------|--------|------|
| Issue Width | 4-wide | Lab00/null_loop IPC=4.00 |
| L1D/L2/L3/DRAM 延迟 | 1.61 / 4.78 / 14 / 130 ns | Lab03/cache_sizes |
| **4 核 MC×NC GEMM** | **143 GFLOPS（92.4%）** | kernel-opt-lab/multicore_tiled |
| FP32 单核 GEMM | 39.45 GFLOPS（98.6% of 40，4 FVU） | kernel-opt-lab/gemm_f32 |
| INT8 单核 GEMM | 77.74 GOPS（97.2% of 80） | kernel-opt-lab/gemm_s8 |
| Winograd F(4,4) | 21.5× vs Direct | kernel-opt-lab/conv_winograd_f44 |
| NEON Flash Attention | 单核 6.58× / 8 核 16× | kernel-opt-lab/attention_neon |
| FP16 vs FP32 SIMD | 3.81× | Lab01/fp16_perf |
| CRC32 硬件 vs 软件 | 14.26× | Lab07/crc_test |
| UDOT INT8 | 16.9× | Expert_05 |
| TLB 2M vs 4K | 4.81× | Expert_04/tlb_cost |
| matmul 优化 0→最优 | 15× | View_03/matmul_evolution |

---

## 与仓库关系

| 仓库位置 | 关系 |
|---------|------|
| [`../../top-cs-projects/`](../../top-cs-projects/) | 九校课程实践库。其中 **CMU 专课目录无 18-447（计算机体系结构）**，berkeley 侧仅有教学级的 [`topic3-arch/`](../../top-cs-projects/berkeley-cs-projects/topic3-arch/)——本库以飞腾真机实验 + 算子工程补上"体系结构动手层"这一档 |
| [`../../讲透计算机科学技术/`](../../讲透计算机科学技术/) | 学科谱系文档层（讲透计算机系统结构等六族）；本库是其**真机实证对应物**——谱系讲"是什么/为什么"，本库给"测出来/优化到" |
| `../../讲透高性能计算/README.md`（本地保留、未入公开仓） | HPC 物理层系列（Amdahl/Roofline/内存层级/混合精度）。该系列当前仅有 README 存根、篇目引用的文件未建，**其中引用的实验环节缺失——本库补位**：Lab00 的 amdahl_law/iron_law、lens-roofline、Lab05 GEMM 全栈即其 01/02/03/04 篇的可运行版本 |

## 使用入口

- 想看算子优化全貌 → [`kernel-opt-lab/README.md`](kernel-opt-lab/README.md) + [`CODE_INDEX.md`](kernel-opt-lab/CODE_INDEX.md)
- 想跑真机实验 → [`体系结构实验/README.md`](体系结构实验/README.md)（项目主入口/改造宪法）+ [`CODE_INDEX.md`](体系结构实验/CODE_INDEX.md)（含"一键全套测试"命令块）
- 想读视角/人格 → [`kernel-opt-lab/Views.md`](kernel-opt-lab/Views.md) 与 [`体系结构实验/Views.md`](体系结构实验/Views.md)；根级路线图见 [战略锚点](体系结构实验/战略锚点.md)/[改造蓝图与写作规范](体系结构实验/改造蓝图与写作规范.md)
