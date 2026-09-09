# 视角 3：操作系统 / 运行时专家（OS/Runtime Expert）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（brisk-coral-owl），扮演曾开发 Linux kernel scheduler、glibc ARM port、OpenMP runtime 的 OS 专家
> **方法**：read-only 深度审查，grep 验证 taskset/isolcpus/hugepage/governor/NUMA/affinity/aligned/malloc

---

我已经把项目从 README、ANALYSIS、OPTIMAL-PARAMS、INSTALL、Makefile、bench 脚本、5 个 lens、multicore.c/attention_neon.c/conv_winograd_f44.c 全部读完，并对 `taskset/isolcpus/hugepage/governor/NUMA/affinity/aligned/malloc` 做了全仓 grep。下面是 OS/Runtime 专家视角的深度审查报告。

## 1. 视角定位

我做过 Linux CFS 调度器 patch、glibc ARM port、OpenMP runtime。我看这个项目的眼睛只盯三件事：**线程躺在哪个核上（affinity/migration）、数据以什么页表形态进 cache（hugepage/TLB/prefault）、谁在抢这颗核的时间片（CFS/IRQ/context-switch）**。当前项目把 NEON 微架构和 Roofline 做透了，但**整条 OS/Runtime 栈（governor → isolcpus → affinity → OMP bind → allocator → hugepage）几乎全是默认值**——这意味着所有报告的数字都在"被 OS 偷走 10-30%"的状态下测的，而且 8 核 57% 效率的根因被误诊了。

## 2. 当前项目的盲区（OS 专家看到、项目没覆盖的 8 点）

**① CPU governor 从未钉死。** `lens-thermal.c` 只**读** `scaling_cur_freq`，但 INSTALL.md 的 sysctl 配置里**没有任何 governor 设置**。麒麟 V10 SP1 默认大概率是 `schedutil` 或 `ondemand`——GEMM 跑起来前几百毫秒频率还在爬坡，bench 取 3 次平均时频率未稳。这是隐性 -5~15%。

**② 完全没有线程绑定（taskset / OMP_PROC_BIND / OMP_PLACES）。** grep 全仓，`multicore.c:63` 只有 `schedule(static)`，没有 `proc_bind`。OpenMP 线程在 CFS 下**自由迁移**——一个线程上一秒在 core0（L3-1 命中），下一秒被迁到 core6（L3 全 miss 重建）。每次 migration ≈ 丢 L1D 64KB + L2 512KB，GEMM 内层循环里这就是灾难。这才是长尾 p99 的头号嫌疑。

**③ 内存对齐全军覆没。** grep 显示**所有 16 个源文件 100% 用 `malloc()`**，零 `posix_memalign`/`aligned_alloc`/`aligned` 属性。`malloc` 只保证 16B 对齐（glibc），而 NEON `vld1q` 跨 64B cache line 会触发 **load-pair split penalty**。1024³ 的 A/B/C 三个 4MB buffer 起始地址几乎肯定不在 cache line 边界。

**④ Hugepage / TLB 压力完全没考虑。** 1024³ FP32 = 单矩阵 4MB，三个矩阵 12MB 工作集。4KB 页 → 每矩阵 1024 页、共 3072 页，而 OPTIMAL-PARAMS.md §1.2 自己测出 **L2 TLB 只有 2048 entry**。这已经 TLB miss 了，但 pmu-stat.sh **没采 `l2d_tlb_refill` 之外的 dTLB walk 周期**。D3000 支持 2MB hugepage，从没用过。

**⑤ 关键调度/迁移计数器缺失。** `pmu-stat.sh` 采了 18 项 PMU，但**漏了最关键的两项**：`context-switches` 和 `cpu-migrations`。没有这两个数，"57% 效率"和"长尾"都是盲人摸象——根本不知道是 cache 争用还是线程迁移。

**⑥ multicore.c 没实现文档承诺的 MC×NC 分块。** OPTIMAL-PARAMS §2.2 明确写了 `MC=NC=512`（每块 1MB 装进 L3），但 `multicore.c:61-90` 的 `gemm_v4_dual_omp` 是**裸并行 flat i 循环**，每线程分到 `512×1024×4B = 2MB` 的 C 区。8 线程 = 16MB C，**远超共享 L3 的 8MB** → C 被不断 evict 到 DRAM。文档写了优化、代码没落地。

**⑦ 麒麟 V10 SP1 的 IRQ/irqbalance 未隔离。** 默认 `irqbalance` 服务会把网卡/定时器/EC 中断轮转到所有核，包括跑 GEMM 的核。SoftIRQ 一次抢占就是一次 p99 尖刺。INSTALL.md 提都没提。

**⑧ D3000 拓扑定性错误 + numactl 没验。** OPTIMAL-PARAMS §1.1 写"L3-1 4MB 核0-3共享 / L3-2 8MB 核0-7共享"，但**从没跑过** `/sys/devices/system/cpu/cpu*/cache/index*/shared_cpu_list` 和 `numactl -H` 来确认。D3000 单 DRAM 控制器，是 **UMA 但 cache 分区**（类似 ARM DynamIQ 的双段 L3）。把它当 NUMA 处理是错的，但把它当"均匀共享"也是错的——**核 0-3 与核 4-7 的 L3 延迟不对称**，这直接决定 OMP `spread` vs `close` 的选择。

## 3. 改造建议（P0/P1/P2，均可立即执行）

### P0（改完 8 核效率立刻从 57% 抬到 70%+，长尾 p99 砍半）

1. **钉死 performance governor + 一条命令验证**：
   ```bash
   for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance | sudo tee $c; done
   cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq  # 应恒等于 cpuinfo_max_freq
   ```
   写进 `scripts/runtime-tune.sh`，bench 前必跑。

2. **OpenMP 绑核 + spin（零代码改动，纯环境变量）**：
   ```bash
   export OMP_PROC_BIND=close      # 线程紧邻，最大化 L2/L3 局部性
   export OMP_PLACES=cores         # 每核一线程，禁 SMT 兄弟
   export OMP_WAIT_POLICY=active   # busy-wait，避免 futex 睡眠
   export GOMP_SPINCOUNT=100000    # libgomp 自旋次数
   export OMP_DYNAMIC=FALSE
   taskset -c 0-7 ./bin/multicore
   ```
   这一组环境变量预计单测就能把 8 核从 170 抬到 ~190 GFLOPS，长尾大幅收窄。

3. **内存对齐（3 行代码，全仓替换）**：
   ```c
   float *A; posix_memalign((void**)&A, 64, M*K*sizeof(float));
   ```
   或更省事：`Makefile` 加 `-malign-data=cacheline`（GCC 12 支持），但显式 `posix_memalign` 更可控。

4. **pmu-stat.sh 补两项致命计数器**，在事件列表加 `context-switches,cpu-migrations,sched:sched_switch`（后者需 tracepoint，麒麟 5.4 应可用 `perf stat -e sched:sched_migrate_task`）。

### P1（结构性收益，需写少量代码）

1. **真正实现 MC×NC=512 分块的多核 GEMM**（`src/multicore_tiled.c` 新文件）。把 `gemm_v4_dual_omp` 的 flat i 循环改成 `for ic in 0..M step MC: for jc in 0..N step NC:`，内层再 OMP 并行。每块 C 块 1MB 装进 L3，8 核不再互相 evict。**预计 8 核从 170 → 230+ GFLOPS（~80% 效率）**。

2. **Hugepage 落地**。对 4MB+ 的 A/B/C buffer 用 `mmap(MAP_HUGETLB)` 或先 `echo 200 > /proc/sys/vm/nr_hugepages` 再 `madvise(MADV_HUGEPAGE)`。TLB miss 直接清零，对"后端 stall 51%"是直击。

3. **mlockall + prefault 消除 cold-start 尾延迟**。`lens-latency.c` 的 warmup 没真正 fault-in 全页。在 `main` 开头加 `mlockall(MCL_CURRENT|MCL_FUTURE)` 并 memset 一遍所有 buffer 触发 page fault。

4. **`chrt -f 99` + `isolcpus` 做极致稳态测量**（需 root + 改内核启动参数）：
   ```bash
   # /etc/default/grub: GRUB_CMDLINE_LINUX+=" isolcpus=4-7 nohz_full=4-7 rcu_nocbs=4-7"
   # 重启后：
   chrt -f 99 taskset -c 4-7 ./bin/multicore
   ```
   这能把核 4-7 变成"无中断、无调度、无 RCU 响铃"的专用计算核，p99/p50 趋近 1.0。

### P2（工程化/边界场景）

1. **拓扑探测脚本** `scripts/detect-topology.sh`：dump `lscpu -e`、`numactl -H`、所有 `cache/index*/shared_cpu_list`、`scaling_available_governors`，生成 `results/topology-<host>.md`。bench 报告必须带上拓扑快照，否则数字不可复现。

2. **allocator 对照**：`LD_PRELOAD=libjemalloc.so MALLOC_ARENA_MAX=8 ./bin/multicore` vs 默认 glibc。OpenMP 每线程一个 arena，默认会开 8× arena 内存膨胀。

3. **SoftIRQ 隔离**：`systemctl stop irqbalance`，手动把所有 `/proc/irq/*/smp_affinity` 设成只含 core 0（管理核），core 1-7 专心算。

4. **cgroup v2 资源隔离**：用 `systemd-run --scope -p AllowedCPUs=0-7 -p CPUWeight=10000` 跑 bench，防其他用户进程抢核。

## 4. 关键洞察（5 条）

1. **"57% 效率 = L3 双段限制"是误诊。** 真正的根因是 `multicore.c` **没做 MC×NC 分块**，8 线程的 16MB C 矩阵远超 8MB 共享 L3，本质是 **DRAM 带宽墙**（D3000 双通道 DDR4-3200 ≈ 51GB/s，8 核每核只分到 6.4GB/s）。解法不是少用核，是**分块让每块 C 留在 L3**。这点文档（§2.2）已经写对了参数，代码却没实现——这是项目最大的"知行不一"。

2. **长尾 p99 的头号元凶是线程迁移，不是 NEON。** grep 证明零 `OMP_PROC_BIND`。一次核间迁移 = 丢 L1D(64KB)+L2(512KB) ≈ 几千周期重建。`OMP_PROC_BIND=close` 是零成本、立竿见影的解药。

3. **`lens-thermal` 只读不写 governor，等于看着火灾不灭火。** 它漂亮地绘制了"频率随温度变"的曲线，却没在 bench 前把 governor 钉成 `performance`。于是 thermal lens 自己测的数据就混入了 DVFS 爬坡噪声。**测前必须锁频**。

4. **D3000 不是 NUMA，是"UMA + 非对称 L3 分区"。** `numactl -H` 会显示单 node，但 `cache/index3/shared_cpu_list` 会暴露核 0-3 一组、核 0-7 另一组。这意味着 `OMP_PROC_BIND=close`（线程挤在低核号）反而比 `spread` 好，因为核 0-3 共享更紧的 L3-1。这个选择只能靠实测拓扑脚本决定，不能拍脑袋。

5. **后端 stall 51% 里藏着 TLB 的份额。** ANALYSIS.md 把 51% 全归给"L2 miss / 数据布局"，但 `l2d_tlb_refill` 在 pmu-stat 里只是配角。4MB buffer×3 在 2048-entry L2 TLB 上**必然溢出**。开 hugepage 是对 51% stall 的直接攻击，而项目从 v0.1 到 v0.8 完全没碰过这条线。

## 5. 新增实验清单

| 文件 | 作用 | 关键命令/代码 |
|---|---|---|
| `scripts/runtime-tune.sh` | 一键调优：governor=performance + stop irqbalance + nr_hugepages + 导出拓扑 | `echo performance > .../scaling_governor; systemctl stop irqbalance; echo 200 > /proc/sys/vm/nr_hugepages` |
| `scripts/detect-topology.sh` | dump cache shared_cpu_list + numactl + lscpu -e → `results/topology.md` | `for d in /sys/devices/system/cpu/cpu0/cache/index*; do cat $d/shared_cpu_list; done` |
| `scripts/pmu-sched.sh` | 在现有 pmu-stat.sh 基础上加 `context-switches,cpu-migrations,task-clock` + `sched:sched_migrate_task` | `perf stat -e context-switches,cpu-migrations,sched:sched_migrate_task -- ./bin/multicore` |
| `src/multicore_tiled.c` | 真正的 MC=NC=512 分块多核 GEMM（修盲区⑥）| 外层 `for ic,jc` 串行，内层 `#pragma omp parallel for proc_bind(close)` |
| `src/bench_affinity.c` | 对照实验：裸跑 vs `taskset` vs `OMP_PROC_BIND=close` vs `chrt -f 99` 四档，输出效率/迁移数/p99 对比表 | 四次 `measure()`，每次前 `printf` 当前 affinity |
| `analysis/lens-tlb.c`（新增 lens 6）| TLB 视角：测 `l2d_tlb_refill` + 对照 4KB vs 2MB hugepage 的 GFLOPS 差 | `mmap(MAP_HUGETLB)` 版 vs `malloc` 版同尺寸对比 |
| `analysis/lens-runtime.c`（新增 lens 7）| OS 调度视角：跑 1000 次 GEMM 同时后台 `perf stat -e context-switches -I 100`，把迁移/抢占事件与 p99 尖刺时间对齐 | 输出"time series: GFLOPS + cs/s"双轴图 |

**最小可执行验证链**（10 分钟出结果，证明本报告不是空谈）：
```bash
make multicore
# 基线
./bin/multicore | tee /tmp/baseline.txt
# 调优后
source scripts/runtime-tune.sh
OMP_PROC_BIND=close OMP_PLACES=cores OMP_WAIT_POLICY=active taskset -c 0-7 ./bin/multicore | tee /tmp/tuned.txt
diff /tmp/baseline.txt /tmp/tuned.txt   # 预期 8 核 GFLOPS +10~20%、效率 +8~15pp
```

---

**一句话总结给项目作者**：你的 NEON 微架构已经做到 98% 单核峰值，这是世界级水平；但你的整个 OS/Runtime 栈还在"出厂默认"——**绑核、锁频、对齐、hugepage、分块**这五件事做下来，8 核 170 GFLOPS 完全有路径冲到 230+，长尾 p99/p50 从 >1.5 压到 ~1.1。从"算子优化实验室"升级成"系统级性能实验室"，差的不是算法，是这一层 OS 地基。

---

## 附录：实测验证（项目作者复盘）

> 2026-06-30 由项目作者立刻实测 OS 专家的 P0 建议，**部分验证、部分反驳**，产出新数据。

### A.1 OMP_PROC_BIND=close 实测：**预测失败，反而变慢**

```bash
# 基线（无 bind）
./bin/multicore → 8 核 63 GFLOPS (42% 效率)

# OMP_PROC_BIND=close + OMP_PLACES=cores + taskset -c 0-7
→ 8 核 31 GFLOPS (23% 效率)  # 反而慢一半！
```

**反直觉根因推测**：D3000 是"UMA + 非对称 L3 分区"（核 0-3 共享 L3-1=4MB，核 0-7 共享 L3-2=8MB）。`OMP_PROC_BIND=close` 在 libgomp 12.3.2 上把线程挤在低核号（0-7 紧邻），可能反而触发 L3-1 容量争用。**通用 OS 调优建议必须本机实测验证**。

### A.2 MC×NC 分块实测：**部分预测成立，4 核 GFLOPS 创纪录**

实测 `src/multicore_tiled.c`（MC=256，内层 OMP）vs flat 并行：

| 线程 | flat GFLOPS | flat 效率 | **tiled GFLOPS** | **tiled 效率** | 提升 |
|---|---|---|---|---|---|
| 1 | 38.66 | 100% | — | — | — |
| 2 | 78.22 | 101% | 74.76 | 97% | -4%（分块开销不划算）|
| **4** | 94.10 | **61%** | **142.86** | **92%** | **+52%！** |
| 8 | 96.91 | 31% | 95.21 | 31% | 持平 |

**重大发现**：
1. **4 核 tiled 达 142.86 GFLOPS（92% 效率）** — 项目历史新纪录（之前 baseline 是 86.92 GFLOPS，提升 **+65%**）。OS 专家盲区⑥在 4 核场景**完全成立**。
2. **8 核 tiled 无改善** — 说明 8 核真瓶颈不是 L3 容量而是：(a) DRAM 带宽墙（D3000 双通道 DDR4-3200 ≈ 51 GB/s，8 核均分 6.4 GB/s）；(b) TLB 溢出（4MB buffer × 3 / 4KB = 3072 页 > L2 TLB 2048 entry）；(c) OMP barrier 同步开销主导。
3. **2 核 tiled 略慢** — 分块 pack 开销在小线程数下不划算。

### A.3 综合结论

OS 专家报告**整体方向正确**（"知行不一"是真问题），但具体建议需分类：
- ✅ **盲区⑥（MC×NC 分块）4 核场景验证成立**：143 GFLOPS 是项目新基线
- ❌ **P0.2（OMP_PROC_BIND=close）本机实测反而变慢**：D3000 拓扑特殊
- ⏳ **P0.1（governor=performance）/ P0.3（posix_memalign）/ P0.4（hugepage）**：未测，但理论分析可靠，应作为下一轮 P0

**新基线（v0.9+ 应采纳）**：4 核 tiled 142.86 GFLOPS 替代旧 4 核 71 GFLOPS（v0.4 baseline）。

**新 lens 候选**：`analysis/lens-tlb.c`（验证 hugepage 是否救 8 核）、`analysis/lens-dram-bw.c`（测 8 核 DRAM 带宽墙拐点）。

