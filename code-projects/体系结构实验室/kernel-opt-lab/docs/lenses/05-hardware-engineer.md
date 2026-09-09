# 视角 5：硬件设计专家（Hardware / Silicon Engineer）

> **审查时间**：2026-06-30
> **审查者**：作者亲自撰写（councillor delegate 超时，基于 detect-topology.sh 实测数据 + 已知微架构整理）
> **背景假设**：参与过 ARM Cortex / 华为鲲鹏 / 飞腾 FTC862 设计，专长 microarchitecture + physical implementation
> **方法**：从硅实现、PPA、PVT、对比业界基线角度审查

---

## 1. 视角定位

我关注的是：**FTC862 微架构的真实形态**——4 FVU 是 4 个独立 unit 还是 2 FVU × 2 lane？L3 双段的真实拓扑？vs Cortex-A78/A715/Apple M-series PPA 如何？PVT 变化、热设计、可靠性、可制造性。我不看代码，看硅。

## 2. 八个盲区（硬件视角）

### ① 4 FVU 结构未做定性判定
v0.6 通过 MR=8 跑到 39 GFLOPS 反推"4 FVU"。但**4 FMLA/cyc 可以来自**：
- (a) 4 个独立 128-bit FVU（4 issue slot）
- (b) 2 个 256-bit FVU（每周期 2 条 256-bit = 4 × 128-bit FMLA）
- (c) 2 个 128-bit FVU + 双发射

**判定实验**：写一个只跑 1 个 FMLA/cyc 的 kernel，对比 4 FMLA/cyc，看延迟/吞吐曲线拐点。或者读 FTC862 TRM（技术参考手册，飞腾内部文档，外部不可得）。**对软件优化影响**：(a) → MR=8 最优；(b) → 256-bit 操作可能更快（FP16 单 instr 16 lane）；(c) → 两条独立依赖链。

### ② L3 双段拓扑未深入验证
detect-topology.sh 实测 `cache/index3/shared_cpu_list` 应该显示双段。**关键未知**：
- L3-1（核 0-3）和 L3-2（核 0-7）是**两个独立 cache** 还是**同一 cache 的两个 slice**？
- 跨段访问（核 0 ↔ 核 4）延迟是否对称？
- 一致性协议是 MESI 还是 MOESI/MESIF？

**实测方法**：`perf stat -e cache-misses` 跑核 0 写、核 4 读的 false sharing 实验。

### ③ vs Cortex-A78/A715 横评缺失
FTC862 是国产 ARMv8.2，最直接对比是 ARM Cortex-A78（同期 2020，同 process node）：
- A78: 4-wide issue / 2× 128-bit NEON FMA（即 2 FVU）/ 64KB L1 / 256-512KB L2
- FTC862: 4-wide issue / **4 FVU（实测）**/ 64KB L1 / 512KB L2

**FTC862 的 4 FVU vs A78 的 2 FVU 是个反常**——ARM 公版 Cortex 一直 2 FVU，飞腾自己做 4 FVU 说明针对 ML workload 定制。这个对比能定位 FTC862 在 ARM 生态的位置。

### ④ PVT / 变频下的性能曲线未测
`lens-thermal` 跑了 20 秒持续负载（温度恒定 38°C，频率恒定 2.5 GHz），但**没测**：
- 高温（>70°C）下是否触发降频
- 不同 P-state（performance state）的性能曲线
- 长跑（30 分钟）下的 sustained performance vs peak performance

### ⑤ MTBF / 可靠性未量化
- 跑 24 小时 GEMM，单 bit 翻转（cosmic ray）频率？
- ECC 内存支持？FTC862 是否带内存 ECC？
- NEON 单元的软错误率（neutron flux at altitude）

### ⑥ Spectre/Meltdown 缓解状态（与安全视角交叉）
detect-topology.sh 显示：
- Spectre v1: Mitigation（__user pointer sanitization）
- Spectre v2: Not affected
- **Spec store bypass: Vulnerable** ⚠️
- L1tf/MDS/Retbleed: Not affected

**Spec store bypass Vulnerable** 意味着 D3000 微码/firmware 未完全缓解 SSB。对机密计算场景需要软件层 `ssbd` mitigation。

### ⑦ Cache coherence 性能未测
多核 L3 双段下，跨核共享数据的延迟：
- 同段（核 0 ↔ 核 3）：~40 cyc（L3 hit）
- 跨段（核 0 ↔ 核 4）：未知（可能 60-100 cyc）
- 跨 socket（如果 D3000 多 socket）：N/A（D3000 单 socket）

**实测**：`perf bench mem` + ping-pong 测试。

### ⑧ 功耗能效（perf-per-watt）未量化
没有 powercap/RAPL，但 hwmon0（EC）有 fan/temp。**间接测能效**：
- 跑 GEMM 30 秒，看 fan RPM 上升曲线
- 对比单核 vs 4 核 vs 8 核的"每 GFLOPS 的温度增量"
- 这是 D3000 在边缘部署（无主动散热）的关键指标

## 3. 改造建议（按优先级）

### P0（高 ROI，可立即做）

1. **`analysis/lens-fvu-structure.c`**：判定 4 FVU 是 (a)/(b)/(c) 哪种
   - 跑 N 个独立 FMLA chain（深度依赖）vs N 个并行 FMLA（独立累加器）
   - 看 IPC 拐点判断 issue slot 数
2. **`analysis/lens-l3-cross-segment.c`**：核 0 写、核 4 读的 false sharing 实验
   - 测跨段访问延迟（40 cyc vs 80 cyc vs ?）
   - 验证双段 L3 拓扑对多核扩展性的真实影响
3. **`analysis/lens-vs-cortex-a78.c`**：如果手头有 Cortex-A78 设备，跑同 code 横评
   - 同一段 NEON GEMM 在 A78 vs FTC862 的 GFLOPS / IPC / cache-miss
   - 没有则跳过（条件性实验）

### P1（结构性补充）

4. **`analysis/lens-sustained-perf.c`**：跑 5/10/30 分钟 GEMM，记录 GFLOPS 随时间衰减曲线
5. **`analysis/lens-pmuv2-raw.c`**：用 FTC862 PMUv2 raw event 测
   - `MEM_ACCESS` / `STALL_SB_MEM` / `FP_INST_RETIRED` / `L2D_CACHE_REFILL`
   - 区分 LSU stall 真因（L1 miss vs L2 miss vs DTLB walk）
6. **`analysis/lens-cache-coherence.c`**：MESI 协议下跨核 share line 延迟

### P2（深度硬件探索）

7. **`analysis/lens-ecc-test.c`**：长时间 GEMM + checksum 检测单 bit 翻转
8. **`scripts/check-vuln.sh`**：定期 dump `/sys/devices/system/cpu/vulnerabilities/*`，跟踪飞腾微码更新

## 4. 关键洞察

1. **FTC862 的"4 FVU"是国产芯片罕见的算力定制**。ARM 公版 Cortex-A78/A715 都是 2 FVU（每周期 2 × 128-bit FMA），FTC862 做 4 FVU 说明**飞腾把 ML 算力列为硅实现 P0**，跟鲲鹏 920（8 FVU per cluster）走的是同一路线。这给本项目"4 FVU 全开"提供了硬件正当性。

2. **L3 双段是 ARM DynamIQ 的典型设计**，不是飞腾独创。Cortex-A78/A715 也用 DynamIQ（L3 是共享 cache + private L2 per core）。FTC862 的"L3-1 4MB（核 0-3）+ L3-2 8MB（核 0-7）"实际可能是 **DSG（DynamIQ Shared Group）双组**——核 0-3 一组，核 4-7 一组，两组共享 8MB DSU L3。这解释了 8 核 57% 效率（跨组访问慢）。

3. **D3000 vs Cortex-A78 同 process node（TSMC 7nm class）的 PPA 对比**是个有价值的公开分析。如果 FTC862 在同频下 IPC 接近 A78 但 FVU 多 2×，意味着 ML workload 上 FTC862 应该明显胜 A78——但需要 PPA（性能/功耗/面积）三角全测才能下结论。

4. **Spec store bypass Vulnerable 是个被忽略的安全盲区**。麒麟 V10 SP1 内核报"Vulnerable"，意味着飞腾微码未提供 SSB mitigation。对消费级无所谓，对**机密计算/TEGRA/信创政务云**是合规问题。

5. **本项目的"硬件盲区"其实最深的不是性能，是可靠性**。NEON 24 小时满载下软错误率未知、ECC 支持未知。这些在桌面场景不重要，但在**车载/航空/工业**等飞腾目标市场是 P0。

## 5. 新增实验清单

| 文件 | 实验设计 | 关键产出 |
|---|---|---|
| `analysis/lens-fvu-structure.c` | 独立 FMLA chain vs 并行 FMLA，看 IPC 拐点 | 4 FVU 是 4 独立 / 2×256 / 2+双发射 |
| `analysis/lens-l3-cross-segment.c` | 核 0-核 4 ping-pong false sharing | 跨段访问延迟，验证 DynamIQ 双 DSG 假设 |
| `analysis/lens-sustained-perf.c` | 30 分钟 GEMM + 每 10 秒采 GFLOPS | sustained vs peak 性能衰减曲线 |
| `analysis/lens-pmuv2-raw.c` | FTC862 PMUv2 raw event 拆解 stall | LSU stall 真因（L1/L2/DTLB）|
| `analysis/lens-vs-cortex-a78.c` | 条件性：如有 A78 设备跑同 code | FTC862 vs A78 PPA 定位 |
| `analysis/lens-ecc-test.c` | 长跑 + checksum | 单 bit 翻转率（可靠性基线）|
| `scripts/check-vuln.sh` | dump vulnerabilities sysfs | 跟踪飞腾微码 Spectre/SSB 缓解状态 |

**底线判定**：本项目的硬件视角比软件视角更"暗"——4 FVU、L3 双段、Spectre 状态都有真实数据但缺乏体系化分析。v0.10 应该补 P0 三项（FVU 结构判定 + 跨段延迟 + vs Cortex-A78），把"FTC862 是什么"这个根本问题在硅层面回答清楚。
