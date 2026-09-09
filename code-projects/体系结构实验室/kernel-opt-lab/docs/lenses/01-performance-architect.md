# 视角 1：资深性能架构师（Performance Architect）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（calm-emerald-otter），扮演 15+ 年经验、曾设计 Apple/Qualcomm/华为麒麟算子库的资深性能架构师
> **方法**：read-only 深度审查 `src/` + `analysis/` + `docs/` 全部代码

---

我现在已经掌握了全局情况。我的 grep 命令证实了代码中不存在 `__builtin_prefetch`、`posix_memalign`、线程亲和性（thread affinity）、非临时存储（non-temporal stores）或大页（hugepage）支持——这些内容仅在文档中作为"TODO"被提及。以下是针对该架构的分析报告。

## 1. 视角定位（Performance Architect）

我关注的是**微架构资源的实际利用率**：FVU/LSU/ROB 是否被打满、寄存器是否溢出、cache hierarchy 的复用是否最优、load latency 是否被 ILP 隐藏、多核时 shared resource（L3/DRAM 控制器/TLB）是否成为隐形瓶颈。我不是看"算法对不对"，而是看"这条 `vfmaq_laneq` 在 pipeline 里到底等了几拍"。下面所有建议都基于 D3000 的 4 FVU / 32 NEON reg / L2=512K / L3 双段拓扑的硬约束。

## 2. 当前项目的 8 个盲区（性能架构师视角）

1. **零软件预取（prefetch）** — 全代码库无 `__builtin_prefetch`/`prfm`（grep 确认只在 docs 当 TODO 提）。`gemm_f32_v5_mr8` 内循环每次 12 个 `vld1q`（8a+4b），D3000 LSU 2 load/cyc → 6 cyc 光 load，而 32 FMLA 在 4 FVU 下 8 cyc——load 已成隐性瓶颈，但 51% backend stall 说明 latency 没被隐藏。**没有 prefetch distance 概念**。

2. **宏内核参数空间完全未探索** — `gemm_tune.c`/`autotune.c` 只 sweep **MR∈{1,2,4,8}**，**没有 NR、没有 KC、没有 MC/NC**（Goto & VdG 三层 blocking 的核心）。NR=4（当前）意味着 B 复用只有 MR=8 次；NR=16 能让 B 复用翻 4 倍、A 复用不变。这是单核还能再榨 10-20% 的最大杠杆。

3. **FP16 "MR=8 反而慢" 的诊断是错的** — 代码注释归因于"`vfmaq_laneq_f16` 单 instr 吞吐 <4/cyc"。真正原因更可能是**寄存器溢出**：MR=8 FP16 = 8(c) + 8(a) + 1(bm) = 17 reg，加上 lane-broadcast form 编译器需临时寄存器，溢栈到 L1。**没有 disassembly 验证**（`objdump -d` 数 `str q` 指令），这是诊断 FP16 性能的第一步。

4. **零 cache-line 对齐** — 所有 GEMM 源码用裸 `malloc`（`gemm_f32.c:158`、`gemm_s8.c:163`、`gemm_f16.c:218`、`multicore.c:98`）。只有 `lens-roofline.c:37` 用了 `posix_memalign`。D3000 上未对齐 `vld1q` 可能走慢路径或 alignment trap。

5. **8 核效率 57% 的归因不完整** — README 说是"L3 双段限制"，但真正嫌疑：(a) 无 thread affinity（`OMP_PROC_BIND`/`GOMP_CPU_AFFINITY` 都没设），核间迁移踢飞 L1/L2；(b) B_blk=4MB 跨 8 核共享读，L3 容量竞争；(c) C 输出 4MB 全是 **write-allocate store**，没用 non-temporal `stnp` 绕过 cache；(d) 热降频未被 PMU 剥离——57% 里有几个百分点是 2.5→2.2GHz？

6. **PMU Lens 用的是通用事件** — `PERF_COUNT_HW_CACHE_*` 粒度太粗。FTC862 有 raw PMU event 能区分 **LSU stall reason**（wait on L1 miss vs L2 miss vs DTLB walk）、**FVU utilization**（FMLA issued / FVU busy cycle）。没有这些，"后端 stall 51%" 只是一句废话，定位不到 root cause。

7. **TLB pressure 完全没量化** — B_blk=4MB / 4KB page = 1024 页，远超 L1 dTLB（典型 64 entry）。`lens-pmu.c` 没采 `DTLB_WALK`，也没试 `madvise(MADV_HUGEPAGE)` / 2MB hugepage 把 TLB entry 压到 2 个。

8. **SVE / 更宽 vector 零探索** — `-march=armv8.2-a+fp16+dotprod` 没 `+sve`。FTC862 是否有 SVE 未知（需 `mrs ID_AA64PFR0_EL1` 探测），但即便无 SVE2，`LD1RQ`（128-bit 加载+广播）比 `vld1q`+`vdupq` 序列省指令——INT8 v5_mr8 里 8 次 `vdupq_lane_s32` 是纯浪费。

## 3. 改造建议（D3000 具体可执行）

### P0（最高杠杆，1-2 天可落地）

- **P0.1 GEMM 内核加 software prefetch**。在 `gemm_f32_v5_mr8` 的 k-loop 起始处插：
  ```c
  __builtin_prefetch(&b[(k+8)*4], 0, 1);      // b 流式，距离=8×16B=128B
  __builtin_prefetch(&A[(i+0)*K+k+16], 0, 0); // a，距离按 KC 调
  ```
  prefetch distance 由实测 L2 latency × issue rate 反推（D3000 L2 ~10 cyc，8 FMLA/cyc-tile → dist≈8）。预期 +5-8% FP32。

- **P0.2 引入 NR 维 + KC blocking**。把当前 `jb += 1（NR=4）` 改 `jb += 4（NR=16）`，同一次 k-loop 累加 16 列 C。寄存器：8(c)×4(j-group)=32→超，故 MR×NR 组合要在 32 reg 内搜：MR=8/NR=4（当前）、MR=4/NR=8、MR=8/NR=4+双缓冲。同时加 KC=256 外层 K-blocking，让 A_panel 16KB 钉死 L1。预期单核再 +10-15%。

- **P0.3 所有 malloc 换对齐 + hugepage**：
  ```c
  posix_memalign((void**)&A, 64, M*K*4);
  madvise(A, M*K*4, MADV_HUGEPAGE);
  ```
  一行改动，消除 alignment fault + TLB miss。C 矩阵初始化用 `DC ZVA`（`asm("dc zva, %0"::"r"(ptr))`）替代 `vdupq+store`，省 read-for-ownership。

### P1（中等杠杆）

- **P1.1 多核三件套**：(a) `OMP_PROC_BIND=close` + `GOMP_CPU_AFFINITY="0-7"` 钉核；(b) C store 改 non-temporal：内联 `asm volatile("stnp q0, q1, [%0]"::"r"(ptr))`；(c) `schedule(static)` 改 `schedule(guided, 4)` 避免 i-tile 过小导致 B_blk 复用断裂。目标把 8 核从 57% → 75%+。

- **P1.2 FP16 重诊**：先 `objdump -dS bin/gemm_f16 | grep -c 'str.*q'` 数 spill。若 >0，把 MR=8 降到 MR=4 NR=8（同算力同寄存器，换 broadcast 路径）。再用 raw PMU（FTC862 `FP_INST_RETIRED` / `NEON_CYCLES`）算真实 FVU 利用率，别靠 lane 吞吐推断。

- **P1.3 INT8 去 `vdupq_lane`**。`gemm_s8_v5_mr8:103-110` 的 8 次 `vdupq_lane_s32(a2,0)` 是 8 条指令浪费。用 `vdupq_laneq_s32` 一次或换 `SDOT` lane 形式 `vdotq_laneq_s32(c, b, a, 0)`（ARMv8.4），省 4-6 instr/iter。

### P2（深度优化，长线）

- **P2.1 双缓冲（software pipelining）**：k-loop 拆成 `load a_next/b_next → fma(c,a_cur,b_cur) → rotate`。把 LSU 和 FVU 真正并发，目标 IPC 从 1.43 → 2.0+。手写汇编或 `__asm__ goto` 块，编译器难自动生成。
- **P2.2 SVE 探测 + 对比 lens**：`mrs x0, ID_AA64PFR0_EL1` 查 SVE 字段，若有则 `-march=armv8.6-a+sve2` 重编，`whilelo`/`ld1rqw` 重写 GEMM。
- **P2.3 Winograd F(4,4) 多核化 + 数据布局**：当前单核。多核时 V 变换（per-tile）天然并行，但 U=gGgGᵀ（per-channel）要避免 8 核重读。pack U 到 NC/8 channel-block。

## 4. 关键洞察（最该补的 3 件事）

1. **"98% 峰值" 是被 K=1024 大算术强度掩盖的假象**。真正的 GEMM 工程价值在 **128-512 的中等尺寸**（conv im2col 后的真实 K），那里 prefetch + NR blocking 能拿 30%+，而项目完全没测。
2. **多核 57% 不是 L3 的锅，是工程没做**：无 affinity、无 non-temporal store、无 cache-aware partition。这是最便宜的提升（改环境变量 + 2 行 store 指令），却完全没碰。
3. **PMU Lens 停在"知道 stall 51%"，没到"知道为什么 stall"**。FTC862 raw event（如 `MEM_ACCESS`、`STALL_SB_MEM`、`FP_FIXED_CTR`）能区分 LSU vs FVU vs TLB，但全用通用 `CACHE_REFERENCES`。PMU lens 重写是 ROI 最高的诊断投资。

## 5. 新增实验/工具清单

| 文件 | 跑什么 | 回答的问题 |
|---|---|---|
| `analysis/lens-prefetch.c` | 同 GEMM kernel，sweep prefetch distance ∈{4,8,16,32} | D3000 L2 latency 下最优 prefetch 距离 |
| `analysis/lens-nr-kc.c` | MR×NR×KC 三维 sweep | 宏内核最优 blocking，补 Goto 三层 |
| `analysis/lens-raw-pmu.c` | `perf_event_open` raw config，采 FTC862 `STALL_SB_MEM`/`L2D_CACHE_REFILL`/`DTLB_WALK`/`FP_INST_RETIRED` | 51% stall 拆解到 root cause |
| `analysis/lens-tlb.c` | 4KB vs 2MB hugepage，`MADV_HUGEPAGE` on/off，采 DTLB_WALK | TLB 是否是大矩阵瓶颈 |
| `analysis/lens-multicore-deep.c` | 8 核 × {affinity on/off, stnp on/off, schedule static/guided} 笛卡尔积 | 57% 里 affinity/store/thermal 各占多少 |
| `analysis/lens-sve-probe.c` | `mrs ID_AA64PFR0_EL1` 解析 + 若有 SVE 跑 SVE GEMM 对比 NEON | D3000 是否支持 SVE，SVE 增益多少 |
| `analysis/lens-bank-conflict.c` | 不同 K stride 下 L2 带宽，找地址 hash 冲突拐点 | D3000 L2 bank/way 数，避免 stride |
| `analysis/lens-disasm-regpress.c` | `objdump -d` 数 FP16/FP32/INT8 三种 MR=8 的 `str q` spill 次数 | FP16 MR=8 慢的真因 |

**底线判断**：项目在"把 K=1024 FP32 推到 98%"这件事上做得很漂亮，但这恰恰是**最容易**的 case（算术强度 171，纯 compute-bound）。真正的算子库价值在中等尺寸、多核、混合精度的鲁棒性——而那里项目几乎空白。建议把重心从"刷峰值"转向"补 blocking + prefetch + 多核工程化"三件套，单核和 8 核都还有 15-30% 在桌上。

---

## 附录：P0.3 posix_memalign 实测验证（2026-06-30，作者复测）

按本报告 P0.3 建议把 `gemm_f32.c` 的 5 个 `malloc` 替换为 `posix_memalign(..., 64, ...)`：

| 实现 | GFLOPS | 结论 |
|---|---|---|
| malloc（基线）| 39.45 | 98.6% peak |
| **posix_memalign 64B** | **38.95** | **97.4% peak** |

**反直觉结果**： posix_memalign **没有提升，反而略低 1.3%**（在测量噪声范围内）。

**根因分析**：
1. glibc `malloc` 默认返回 16B 对齐指针，已满足 ARM NEON `vld1q` 的对齐要求（不要求 64B cache line 对齐）
2. D3000 的 NEON load unit **硬件原生处理 unaligned load**，无 alignment trap 慢路径
3. 跨 cache line 的 load penalty 在 4MB buffer 上概率较低（每 16B 一次 cache line 边界 = 1/4 概率），且被 4 FVU 计算时间掩盖

**修正建议**：
- posix_memalign 仍是好工程实践（hugepage 友好、为 SVE 128B 对齐做准备），**但不是 P0 性能提升手段**
- 本报告 P0.3 重新分级为 **P2**（工程整洁性）
- 真正的 P0 应该是 **prefetch** + **NR/KC blocking**（这两项未实测，仍可能是大提升）

**方法论教训**：所有"建议"必须本机实测验证。本 lens 框架的价值就在于：专家给假设，作者做实测，结果是 P0 / P1 / P2 的真实分级。
