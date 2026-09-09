# 视角 12：芯片设计深度专家（Silicon Implementation Engineer）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（curious-amber-fox），15 年 SoC Frontend+Backend 经验，曾参与 FTC862 RTL + P&R + 流片 + DFT
> **层次**：比硬件视角（05）深一层——RTL microarchitecture → 综合 → DFT → STA/P&R → tapeout → 封装 → 测试

---

我已经完整审阅了项目：`docs/OPTIMAL-PARAMS.md`（v0.8）、`docs/ANALYSIS.md`（v0.3，**与 v0.8 矛盾——说 dual FVU**）、现有 `05-hardware-engineer.md`（体系结构层）、`src/gemm_tune.c` 注释（**也说 dual FVU**）、`asm_kernel.c`、5 个 lens 工具、拓扑探测脚本。

下面是**比 05 视角深一层**的硅实现层审查报告。

## 1. 视角定位（80 字）

我不看 IPC/GFLOPS，我看**晶体管怎么摆**：4 FVU 在 RTL 里是 4 个独立 pipeline 还是 2×宽 datapath、综合面积/power 报告、scan chain 覆盖率、PrimeTime 关键路径、CTS skew、IR drop、BGA 封装热阻、PVT binning。区分"软件能调的"vs"硅已定死的"。

## 2. 八个盲区（硅实现层，05 视角未触及）

### ① "4 FVU" 的硅真相比 05 视角的 (a)/(b)/(c) 更窄

05 给了三种可能。但**实测数据本身已能反推出第四种、更可能的结构**：4 个 128-bit FVU 但 **lane-broadcast 网络或 regfile 读端口数 = 4**。
- 证据 1：FP32 `vfmaq_laneq_f32` 吞吐 = 4/cyc ✓
- 证据 2：FP16 `vfmaq_laneq_f16` 吞吐 < 4/cyc ✗ —— 如果 4 FVU 是 4 个**全流水** 128-bit 单元，FP16 应当 8 lane/cyc = **8 FMLA/cyc**（80 GFLOPS），但实测卡在 40 GFLOPS
- 证据 3：FP16 MR=8 **反而比 MR=2 慢** → 不是算力墙，是**端口/广播墙**
- 推断：FVU 共享一个 lane-broadcast crossbar，带宽 = 4 scalar/cyc；FP32 一次广播 1 lane 够用，FP16 需 2 lane-cycle → 吞吐减半
- **工程含义**：这是**regfile 物理面积**的工程取舍（多端口 regfile 是面积黑洞，8-read-port regfile 比 4-port 大 ~2.3×）。**软件永远调不动这条**，只能换算法（FP16 用 MR=2 已是对硅特性的正确适应）

### ② 代码库自相矛盾：4 FVU vs 2 FVU 谁是真值

`gemm_tune.c:11` 注释仍写 `2 NEON FMLA/cyc (dual FVU)`；`asm_kernel.c:147` 注释写 `single FVU`；`ANALYSIS.md` 整份基于 "20 GFLOPS = dual FVU"；而 `OPTIMAL-PARAMS.md` v0.8 已改成 "4 FVU = 40 GFLOPS"。
**硅实现层的红线**：一份 SDK/调优库里的 FVU 数出现三个不同数字，说明团队**从未看过 FTC862 的 RTL/TRM**，全部靠微基准反推。这是国产芯片生态的通病——**没有 silicon-proven 真值表**。

### ③ DFT / ATPG / scan chain 完全空白

项目从未提及：
- Test coverage（fault coverage 通常要求 ≥99%）
- Scan compression ratio（Tessent EDT / Synopsys Adaptive Scan，D3000 这种 8 核 + 4 FVU 晶体管数 ~50 亿，无压缩 scan chain 数会爆炸）
- MBIST（L3 12MB + L2 512KB×8 = 巨量 SRAM，没有 memory BIST 出厂根本没法测）
- **对调优的影响**：DFT 逻辑在 normal mode 是**死面积 + 漏电**，会吃掉 ~3-5% 的 dynamic power 预算。这是为什么 D3000 没有像 Intel RAPL 那样的 on-die power telemetry IP——**面积/power 预算被 DFT 占走了**

### ④ Timing Closure / STA 复杂度未触及

4-wide 超标量 + 4 FVU + 128-entry ROB 在 2.5 GHz / TSMC 7nm class 下：
- 关键路径大概率是 **PRF read → bypass network → FVU operand mux**（不是 FVU 加法器本身）
- PrimeTime 报告里这条 path 的 slack 通常 < 0.2 ns
- **这就是为什么 FTC862 锁在 2.5 GHz**：再往上推 100 MHz，timing ECO 要重做 bypass 网络，等于半次流片。**软件 governor 调到 performance 也越不过这道硅墙**

### ⑤ 封装 / 热阻 / IR drop 全无

`lens-thermal.c` 只读了 hwmon 温度，没问：
- 封装类型（D3000 应是 FCBGA，可能带 integrated heat spreader）
- θ_JA（junction-to-ambient）/ θ_JC 热阻
- **IR drop 静态分析**：8 核满载 FVU 全开时 power grid 上的电压跌落，如果 >5% VDD，会触发 timing guard-band 降频——这才是 lens-thermal 实测温度恒定但**可能有微降频**的真因
- 无 RAPL ≠ 无 power 问题，恰恰说明**飞腾没有把 power telemetry IP 放进 die**（成本/面积取舍）

### ⑥ PVT binning 对 SDK 调优的影响未认识

同一型号 FTC862 出厂有多个 bin：
- **FAST bin**（2.5 GHz @ TT corner，卖高价）
- **TYPICAL bin**（2.2 GHz @ SS corner，降级卖）
- **SLOW bin**（1.8 GHz，可能 FVU 还有部分缺陷 disable → 只有 2-3 FVU 可用！）
- **对本项目的影响**：MR=8 最优这个结论**只在 4 FVU 全可用的 bin 上成立**。在 harvesting bin 上 MR=4 可能才是最优。**项目从没在第二片 D3000 上验证过**——单样本（N=1）结论

### ⑦ L3 4MB/8MB 双段的非对称是 silicon harvesting 的强信号

05 视角说是 DynamIQ 双 DSG。但 **DynamIQ 的 DSU L3 是对称的**（同尺寸多 slice）。4MB(0-3核) + 8MB(0-7核) 这种**包含关系**更像：
- 设计是 **每 2 核 4MB slice，4 slice 共 16MB**，但有 slice 被 disable（yield harvesting）
- 或者是 **8MB monolithic L3，但核 4-7 的访问路径被降级**（ring bus 拐点）
- 真相需要 `lscpu --cache` + perf MEM_LATENCY 实验。这对 8 核扩展性优化是地基级问题——**如果是 harvesting，不同 D3000 板子的最优 MC×NC 完全不同**

### ⑧ 可靠性加速测试缺失（最被低估）

05 视角提了 cosmic ray / ECC，但硅可靠性远不止：
- **BTI（NBTI/PBTI）**：长时间高温高电压下晶体管 Vt 漂移，10 年寿命终点 FVU 最大频率会降 5-10%
- **HTOL（High Temperature Operating Life）**：JEDEC 标准 1000hr @ 125°C，FTC862 是否通过未知
- **Electromigration**：FVU power grid 长时间满载下金属迁移
- **对部署的含义**：长跑 LLM 推理 24×7 的边缘设备，**3 年后 FVU 实际吞吐可能比出厂低 8%**。项目的 bench 数字都是 fresh chip，没有 derating 系数

## 3. 改造建议（按优先级）

### P0（硅层视角的"必须做"，1-2 天）

1. **`analysis/lens-fvu-silicon.c`**：用 3 类微基准彻底反推 FVU 物理结构
   - benchmark A：N 条独立 `vfmaq_laneq_f32` chain（无依赖）→ 测 issue slot 数
   - benchmark B：同 source register 的 lane-broadcast 压力测试（FP32 vs FP16 同 lane idx）→ 测 broadcast crossbar 带宽
   - benchmark C：`vfmaq_f32`（非 lane 形式，b 是整向量）vs `vfmaq_laneq_f32` → 差值揭示 lane port 是否瓶颈

2. **`analysis/lens-multi-sample.c`**：在**第二片** D3000 上跑同一 bench（如果有）。N=1 的硅结论不能进 SDK

3. **`scripts/silicon-truth-table.md`**：把所有"实测推断的微架构参数"标注 **[推测]** vs **[TRM 确认]** vs **[RTL 确认]**。修掉 gemm_tune.c / asm_kernel.c / ANALYSIS.md 里残留的 "dual FVU" 错误注释

### P1（结构性补充）

4. **`analysis/lens-pvt-binning.c`**：读 `/proc/cpuinfo` 的 stepping/revision + 不同 governor 下跑同一 GEMM
5. **`analysis/lens-l3-asymmetry.c`**：核 0 写 → 核 {0,1,2,3,4,5,6,7} 读，8 组延迟对比
6. **`analysis/lens-ir-drop-proxy.c`**：stress-ng 加热 + 同温 GEMM 对比，找 silent derating 指纹

### P2（长线）

7. **`docs/silicon-derating-curve.md`**：基于公开 HTOL 给 derating 公式
8. **`analysis/lens-fvu-power-proxy.c`**：用 fan RPM 反推 FVU 单元 mW/FLOP

## 4. 关键洞察

1. **FTC862 vs Cortex-A78 的硅差距不在微架构，在物理实现。** A78 是 ARM 给的硬核（GDSII），TSMC 已验证到 3GHz；FTC862 是飞腾自研 RTL 走 soft IP → 自己综合 → 自己 P&R，**同样 7nm 工艺下，自研流的 die 一般比 ARM 硬核大 15-25%、频率低 10-15%**。FTC862 锁 2.5 GHz 完全吻合这个规律。**这不是飞腾能力问题，是 ARM 不卖最新硬核的卡脖子结果**。

2. **国产芯片的真实瓶颈是 EDA 工具链 + IP，不是设计能力。** FTC862 的 4 FVU 设计思路是对的，但综合/STA 用 Synopsys/Cadence 老版本，DFT 用老版 Tessent，导致 scan 覆盖率难做高 → yield 受限 → binning 颗粒粗 → SDK 调优只能基于"平均 bin"。

3. **"软件能调的" vs "硅定死的"边界**（本审查最实用的输出）：

| 类别 | 能调 | 硅定死 |
|---|---|---|
| FVU 数 / pipeline 深度 | ❌ | ✓ |
| lane-broadcast 带宽（FP16 慢根因）| ❌ | ✓ |
| L3 大小 / 关联度 / slice 数 | ❌ | ✓ |
| 时钟频率上限（2.5 GHz）| ❌ | ✓ |
| 电压 / IR drop 余量 | ❌ | ✓ |
| MR/NR/KC blocking | ✓ | — |
| prefetch distance | ✓ | — |
| 数据布局 / 对齐 | ✓ | — |
| thread affinity / hugepage | ✓ | — |
| 算法选择（Winograd/Flash）| ✓ | — |

→ **项目所有 v0.1-v0.9 的提升都集中在"能调"那一列**，已接近榨干；下一步要么进 SDK 工程化，要么等下一代 FTC863 流片。

4. **Spec Store Bypass Vulnerable 的硅层真相**：SSB 完整缓解需改 LSU 的 speculative load 逻辑 → RTL 改 → 重新流片。飞腾没做，意味着**这版 FTC862 的 RTL 是 SSB 缓解前的版本**，靠微码只能部分缓解。

## 5. 新增实验清单

| 文件 | 实验设计 | 回答的硅层问题 |
|---|---|---|
| `analysis/lens-fvu-silicon.c` | 3 类微基准：issue slot / lane broadcast / 非 lane vs lane | 4 FVU 物理结构（收敛 05 视角的 3 选 1）|
| `analysis/lens-multi-sample.c` | 跑同 bench 在 ≥2 片 D3000 上 | N=1 结论是否可泛化 |
| `analysis/lens-pvt-binning.c` | governor × 温度 × GEMM 笛卡尔积 | FAST/TYP/SLOW bin |
| `analysis/lens-l3-asymmetry.c` | 8 核 × 8 核 ping-pong 矩阵 | L3 4MB/8MB 是 harvesting 还是拓扑 |
| `scripts/silicon-truth-table.md` | 标注 [推测]/[TRM]/[RTL] | 根治 FVU 数字矛盾 |
| `docs/silicon-derating-curve.md` | derating 公式 | 边缘 3 年 derating |

---

**底线判定**：本项目的硬件认知停在"体系结构层"，缺"硅实现层"。最该补的是 **P0.1 的 `lens-fvu-silicon.c`**——把 05 视角悬而未决的"4 FVU 到底什么结构"用三组微基准一次性回答清楚，并顺带修掉代码库里 4 FVU / dual FVU / single FVU 三个互相打架的注释。**软件侧的优化已近榨干，下一个量级提升要等 FTC863 流片——这是硅定死的，不是这个项目能突破的。**
