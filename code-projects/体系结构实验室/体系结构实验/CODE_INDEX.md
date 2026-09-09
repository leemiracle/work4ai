# 可运行代码索引

> 23 专家视角 + 9 异质思维透镜 + Capstone + View 工具集，**所有可运行程序与关键 artifact** 的统一入口。
> 每个程序都附"做什么 / 跑法 / 预期输出"。
> E13-23 为改造蓝图新增；其中 E14/E17 有独立可运行脚本，E18/E20/E23 的探测脚本内嵌于 README，E13/15/16/19/21/22 为纯分析型（无代码 artifact）。

---

## A. 实验员视角（Lab00-Lab07）

| 程序 | 路径 | 命令 |
|------|------|------|
| arch_probe | [`Lab00_测量基础设施/src/arch_probe.c`](./Lab00_测量基础设施/src/) | `taskset -c 0 ./arch_probe` |
| null_loop | [`Lab00_测量基础设施/src/null_loop.c`](./Lab00_测量基础设施/src/) | `taskset -c 0 ./null_loop` |
| cache_sizes | [`Lab03_存储层次/src/cache_sizes.c`](./Lab03_存储层次/src/) | `taskset -c 0 ./cache_sizes` |
| rename_capacity | [`Lab04_超标量乱序/src/rename_capacity.c`](./Lab04_超标量乱序/src/) | `taskset -c 0 ./rename_capacity` |
| gemm_full_stack | [`Lab05_并行与SIMD/src/gemm_full_stack.c`](./Lab05_并行与SIMD/src/) | `taskset -c 0 ./gemm_full_stack` |

---

## B. Capstone 综合项目

### B.1 RV32I 5 级流水线模拟器（Python）
| 文件 | 用途 | 命令 |
|------|------|------|
| [`Capstone/cpu_simulator/rv32i_sim.py`](./Capstone/cpu_simulator/rv32i_sim.py) | 模拟器 | `python3 Capstone/cpu_simulator/rv32i_sim.py` |
| [`Capstone/cpu_simulator/assembler.py`](./Capstone/cpu_simulator/assembler.py) | 迷你汇编器 | `python3 Capstone/cpu_simulator/assembler.py` |
| [`Capstone/cpu_simulator/tests/test_rv32i.py`](./Capstone/cpu_simulator/tests/test_rv32i.py) | pytest 77 测试 | `pytest Capstone/cpu_simulator/tests/ -v` |
| [`Capstone/cpu_simulator/run_all_and_report.py`](./Capstone/cpu_simulator/run_all_and_report.py) | 自动报告 | `python3 Capstone/cpu_simulator/run_all_and_report.py -o report.md` |

### B.2 工作负载刻画
| 文件 | 命令 |
|------|------|
| [`Capstone/workload_characterization/driver.sh`](./Capstone/workload_characterization/driver.sh) | `bash Capstone/workload_characterization/driver.sh` |
| [`Capstone/workload_characterization/collect.py`](./Capstone/workload_characterization/collect.py) | `python3 Capstone/workload_characterization/collect.py 'data/*.perf'` |

### B.3 Lab 反推数据
| 文件 | 命令 |
|------|------|
| [`Capstone/alpha_21264_study/collect_lab_data.py`](./Capstone/alpha_21264_study/collect_lab_data.py) | `python3 Capstone/alpha_21264_study/collect_lab_data.py --md` |

---

## C. 23 专家视角的可运行代码

### Expert_03_HW_Designer — Verilog RTL 骨架
| 文件 | 内容 | 需要 |
|------|------|------|
| [`Expert_03_HW_Designer/rtl/alu.v`](./Expert_03_HW_Designer/rtl/alu.v) | 10 条 RV32I ALU | iverilog/yosys 仿真 |
| [`Expert_03_HW_Designer/rtl/forwarding_unit.v`](./Expert_03_HW_Designer/rtl/forwarding_unit.v) | 流水线 forwarding 单元 | 同上 |
| [`Expert_03_HW_Designer/rtl/two_bit_predictor.v`](./Expert_03_HW_Designer/rtl/two_bit_predictor.v) | 2-bit 饱和预测器 | 同上 |
| [`Expert_03_HW_Designer/rtl/tb_alu.v`](./Expert_03_HW_Designer/rtl/tb_alu.v) | ALU testbench | `iverilog -o tb_alu tb_alu.v alu.v && vvp tb_alu` |

### Expert_04_OS_Kernel — syscall/TLB 测量（飞腾本机可跑）
| 文件 | 测什么 | 命令 |
|------|------|------|
| [`Expert_04_OS_Kernel/src/syscall_bench.c`](./Expert_04_OS_Kernel/src/syscall_bench.c) | 各 syscall 真实延迟 | `make -C Expert_04_OS_Kernel run` |
| [`Expert_04_OS_Kernel/src/tlb_cost.c`](./Expert_04_OS_Kernel/src/tlb_cost.c) | 4K vs 2M 大页 | 同上（实测 4.81× 加速）|

### Expert_05_AI_Inference — INT8 算力（飞腾本机可跑）
| 文件 | 测什么 | 命令 |
|------|------|------|
| [`Expert_05_AI_Inference/src/int8_gemm_udot.c`](./Expert_05_AI_Inference/src/int8_gemm_udot.c) | UDOT INT8 GEMM | `make -C Expert_05_AI_Inference run`（实测 16.9× 加速）|

### Expert_09_Performance_Model — Roofline 模型
| 文件 | 用途 | 命令 |
|------|------|------|
| [`Expert_09_Performance_Model/roofline_d3000m.py`](./Expert_09_Performance_Model/roofline_d3000m.py) | 生成 Roofline PNG | `python3 Expert_09_Performance_Model/roofline_d3000m.py` |
| [`Expert_09_Performance_Model/roofline_d3000m.png`](./Expert_09_Performance_Model/roofline_d3000m.png) | 生成的 Roofline 图 | 直接看 |

### Expert_14 — 良率与 good-die 推测模型（独立脚本，飞腾本机可跑）
| 文件 | 用途 | 命令 |
|------|------|------|
| [`Expert_14_Process_Manufacturing/yield_model.py`](./Expert_14_Process_Manufacturing/yield_model.py) | Poisson/Murphy/Bose-Einstein 三模型算 14nm/7nm 良率、good die/晶圆、裸 die 成本 | `python3 Expert_14_Process_Manufacturing/yield_model.py` |

### Expert_17 — 量产测试成本与 DPPM 逃逸模型（独立脚本，飞腾本机可跑）
| 文件 | 用途 | 命令 |
|------|------|------|
| [`Expert_17_DFT_PostSilicon/test_cost_model.py`](./Expert_17_DFT_PostSilicon/test_cost_model.py) | ATE/handler 机时成本 → 每颗测试成本 + DPPM 逃逸率 + TC 敏感性分析 | `python3 Expert_17_DFT_PostSilicon/test_cost_model.py` |

### Expert_18 / E20 / E23 — 内嵌于 README 的探测脚本（非独立文件）
> 这 3 个脚本以代码块形式内嵌在各自 README 里，未存为独立文件。跑法 = 复制代码块存为同名文件后执行（飞腾本机）。

| 脚本 | 内嵌位置 | 用途 | 跑法 |
|------|---------|------|------|
| `boot_chain_probe.sh` | [Expert_18 §2.11](./Expert_18_Firmware_Boot/README.md) | 捞出 BL1→BL31→UEFI→GRUB→内核 整条启动链证据，验证信任链推测图 | 存 `.sh` 后 `bash boot_chain_probe.sh` |
| `energy_probe.sh` | [Expert_20 §2.10](./Expert_20_Green_Compute/README.md) | 探 cpufreq/cpuidle/DVFS 档位，粗测满载/空载功耗比与每瓦性能（PPW） | 存 `.sh` 后 `bash energy_probe.sh` |
| `ras_probe.c` | [Expert_23 §2.11](./Expert_23_Server_RAS/README.md) | 验证 FEAT_RAS 存在性 + `ESB` 指令可执行性 + ESB 延迟粗测（对标 ~10–50 cyc） | `gcc -O2 -o ras_probe ras_probe.c && ./ras_probe` |

### 纯分析型 Expert（无可运行代码 artifact）
> Expert_13_VLSI_Physical、Expert_15_Package_Chiplet、Expert_16_EDA_Toolchain、Expert_19_Geostrategy、Expert_21_AI_Positioning、Expert_22_OpenSource_Ecosystem —— 这 6 个视角为纯分析/战略型，其"可验证性"体现在**量化对标表与图表**（非代码）。E19 的核心 artifact 是 [`Lenses/Lens_03_SupplyChain.md`](./Lenses/Lens_03_SupplyChain.md) 的 11 节点供应链依赖图（见 §H）。

---

## D. View 工具集（飞腾本机可跑）

### View_01_Compiler — 编译器对比
| 程序 | 用途 | 命令 |
|------|------|------|
| `src/opt_compare.c` | -O0..-Ofast 实测 | `make -C View_01_Compiler compare` |
| `Makefile` 向量化报告 | 看 vectorize 成败 | `make -C View_01_Compiler vectorize` |

### View_02_Security — 安全 POC
| 程序 | 用途 | 命令 |
|------|------|------|
| `src/cache_timing.c` | Flush+Reload cache 时序 | `make -C View_02_Security run` |
| `src/constant_time.c` | 常时间编程对比 | 同上 |

### View_03_Perf — 性能工程师工具
| 程序 | 用途 | 命令 |
|------|------|------|
| `src/matmul_evolution.c` | 矩阵乘 8 步优化 | `make -C View_03_Perf run`（实测 15× 加速）|
| `src/false_sharing.c` | 多核 false sharing | 同上（实测 2× 加速）|
| `src/branch_patterns.c` | 分支模式 IPC | 同上 |

---

## E. 对偶验证（综合）

| 文件 | 用途 | 命令 |
|------|------|------|
| [`duel_validator.py`](./duel_validator.py) | 5 个实验交叉检验多视角 | `python3 duel_validator.py` |

---

## F. 一键全套测试

```bash
# 跑全部可运行程序，验证项目健康
cd 体系结构实验

# 1. Lab 实测（需要 taskset + perf）
taskset -c 0 Lab00_测量基础设施/src/arch_probe
taskset -c 0 Lab00_测量基础设施/src/null_loop
taskset -c 0 Lab03_存储层次/src/cache_sizes
taskset -c 0 Lab04_超标量乱序/src/rename_capacity

# 2. Capstone 模拟器
python3 -m pytest Capstone/cpu_simulator/tests/ -v     # 77 个测试
python3 Capstone/cpu_simulator/run_all_and_report.py -o /tmp/r.md

# 3. Expert 可运行程序
make -C Expert_04_OS_Kernel run                          # syscall + TLB
make -C Expert_05_AI_Inference run                       # INT8 UDOT
python3 Expert_09_Performance_Model/roofline_d3000m.py   # Roofline
# 3b. 新增 Expert 推测模型（纯 Python，无需特权/硬件）
python3 Expert_14_Process_Manufacturing/yield_model.py   # 良率/good die/裸die成本
python3 Expert_17_DFT_PostSilicon/test_cost_model.py     # 测试成本/DPPM 逃逸

# 4. View 工具
make -C View_01_Compiler compare                         # -O 对比
make -C View_02_Security run                             # 安全 POC
make -C View_03_Perf run                                 # 矩阵乘优化

# 5. 对偶验证
python3 duel_validator.py

# 6. 新增 Expert 内嵌探测脚本（需飞腾本机；从对应 README §X 复制代码块存盘后运行）
#    Expert_18 §2.11 boot_chain_probe.sh  → bash boot_chain_probe.sh   (启动链取证)
#    Expert_20 §2.10 energy_probe.sh      → bash energy_probe.sh       (能效/PPW 画像)
#    Expert_23 §2.11 ras_probe.c          → gcc -O2 -o ras_probe ras_probe.c && ./ras_probe  (RAS 能力探测)
```

---

## G. 飞腾 D3000M 实测关键数据汇总

| 数据 | 实测值 | 来源 |
|------|------|------|
| Issue Width | 4-wide | Lab00/null_loop IPC=4.00 |
| ALU 端口 | 2/cycle | Lab00/null_loop IPC=2.00 |
| L1 D-Cache | 64KB/4-way @ 1.61 ns | Lab03/cache_sizes |
| L2 Cache | 512KB/8-way @ 4.78 ns | Lab03 |
| L3 Cache | 8MB shared @ 14 ns | Lab03 |
| DRAM | 130 ns | Lab03 |
| 寄存器重命名拐点 | n≥12 saturate IPC≈3.45（发射带宽，非 PRF）| Lab04 |
| FP16 vs FP32 SIMD | 3.81× | Lab01/fp16_perf |
| CRC32 硬件 vs 软件 | 14.26× | Lab07/crc_test |
| NEON FP32 GEMM peak | 9.45 GFLOPS | Lab05/gemm_full_stack |
| **UDOT INT8 加速** | **16.9×** | Expert_05/int8_gemm_udot |
| **TLB 2M vs 4K** | **4.81×** | Expert_04/tlb_cost |
| **matmul 优化 0→最优** | **15×** | View_03/matmul_evolution |

### 新增 Expert 推测数据（均 `[推测-依据]`，非实测/非官方，可由对应脚本重跑）

| 数据 | 推测值 | 来源（可重跑） |
|------|------|------|
| D3000M die 面积 | ~120 mm²（中位推测，8 核 4-wide OoO @14nm 级）| Expert_14/yield_model |
| 14nm 良率（Murphy, D0=0.4）| **63.1%** | Expert_14/yield_model |
| good die / 300mm 晶圆 | 314 颗 | Expert_14/yield_model |
| 裸 die 成本（14nm, $4500/晶圆）| **$14.3** | Expert_14/yield_model |
| 每颗量产测试成本 | **$0.69**（占信创售价 <0.1%，非成本大头）| Expert_17/test_cost_model |
| DPPM 逃逸（TC=99% + burn-in 筛 87.5%）| **~500**（vs Intel/AMD 服务器目标 <100）| Expert_17/test_cost_model |
| 单核每瓦性能 PPW（FP16 GEMM proxy）| **~3–4 GFLOPS/W**（落后 Graviton2/3 约 2–3 倍）| Expert_20/README §2.2 表 B |
| 单 CPU TDP | ~72W | Expert_20/README §2.2（E02 推测）|

📌 实测数字（上半表）均可由对应命令重跑生成，不依赖手工录入；下半表为 E14/E17/E20 的**推测模型产出**，依据链见各 Expert 的 README「盲区与反方」段——真实数据须功率计 + perf 现场实测。

---

## H. 异质思维透镜（`Lenses/`，9 个）

> 非"首席从业者"视角。每个透镜用一种**非从业者的眼睛**看飞腾，给出从业者给不出的洞察。
> 这些是**思维框架文档**（非可运行代码），每篇 ≥ 4000 字，含 named framework + 对飞腾命运的具体预测/下注 + 与从业者视角的冲突点。

| 文件 | 范式 | 一句话核心 |
|------|------|------|
| [`Lenses/Lens_01_Historian.md`](./Lenses/Lens_01_Historian.md) | 历史学家 | 从 4004→8086→ARM→Apple Silicon 的规律预测飞腾命运 |
| [`Lenses/Lens_02_Christensen.md`](./Lenses/Lens_02_Christensen.md) | 破坏式创新者 | Christensen 框架：RISC-V 是否作为低端颠覆 ARM？D3000M 给谁用 |
| [`Lenses/Lens_03_SupplyChain.md`](./Lenses/Lens_03_SupplyChain.md) | 供应链分析师 | 硅砂→机柜 11 节点依赖图，逐节点标卡脖子（**E19 核心 artifact 底图**）|
| [`Lenses/Lens_04_Economist.md`](./Lenses/Lens_04_Economist.md) | 经济学家 | 规模效应/网络效应/摩尔定律经济学/半导体周期 |
| [`Lenses/Lens_05_Futurist.md`](./Lenses/Lens_05_Futurist.md) | 未来学家 | 2035 图景（绑定具体技术赌注，禁科幻空谈）|
| [`Lenses/Lens_06_Anthropologist.md`](./Lenses/Lens_06_Anthropologist.md) | 人类学家 | 信创国产化对政府/国企 IT 组织的真实改变 |
| [`Lenses/Lens_07_VC.md`](./Lenses/Lens_07_VC.md) | VC 投资人 | "我是国资基金，投不投飞腾下一代？"下注判断 |
| [`Lenses/Lens_08_Antitrust.md`](./Lenses/Lens_08_Antitrust.md) | 反垄断学者 | ARM/NVIDIA+CUDA/Intel x86 平台垄断与反制 |
| [`Lenses/Lens_09_Ethics.md`](./Lenses/Lens_09_Ethics.md) | 科技伦理学者 | 军民两用审视、飞腾国防关联的伦理维度 |
